import gc
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from nebu import Message, Processor, processor
from nebu.config import GlobalConfig as NebuGlobalConfig
from nebu.containers.models import V1EnvVar
from nebu.errors import RetriableError
from nebu.processors.models import (
    V1Scale,
    V1ScaleDown,
    V1ScaleUp,
    V1ScaleZero,
)
from pydantic import BaseModel

from orign import V1TrainingStatus, find_latest_checkpoint

BASE_MODEL_ID = "unsloth/Qwen2.5-VL-72B-Instruct"
ADAPTER_DIR = "/nebu/cache/adapters"


class TrainingRequest(BaseModel):
    adapter: str
    dataset: str
    model: str = BASE_MODEL_ID
    max_length: int = 32_768
    epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_steps: int = 5
    logging_steps: int = 1
    save_steps: int = 5
    lora_alpha: int = 128
    lora_rank: int = 64
    lora_dropout: float = 0
    optimizer: str = "adamw_8bit"
    owner: Optional[str] = None
    labels: Optional[Dict[str, str]] = None


class TrainingResponse(BaseModel):
    loss: float
    train_steps_per_second: float
    train_samples_per_second: float
    train_runtime: float
    adapter: str
    adapter_uri: str


scale = V1Scale(
    up=V1ScaleUp(above_pressure=10, duration="5m"),
    down=V1ScaleDown(below_pressure=2, duration="10m"),
    zero=V1ScaleZero(duration="10m"),
)

setup_script = """
apt update
apt install -y git
pip install torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install trl peft transformers bitsandbytes sentencepiece accelerate orign
pip install -e git+https://github.com/pbarker/unsloth-zoo.git#egg=unsloth_zoo
pip install unsloth
pip install -e git+https://github.com/pbarker/unsloth-zoo.git#egg=unsloth_zoo
pip install huggingface_hub[hf_xet]
"""


def init():
    import gc

    from unsloth import FastVisionModel  # type: ignore # isort: skip
    import torch  # type: ignore  # type: ignore
    from nebu import Cache  # type: ignore
    from peft import LoraConfig, PeftModel  # type: ignore  # noqa: F401
    from unsloth_zoo.peft_utils import get_peft_regex  # type: ignore

    from orign import V1Adapter

    if "state" in globals():  # <-- already loaded by an earlier worker
        print("state already loaded by an earlier worker")
        return

    gc.collect()
    torch.cuda.empty_cache()  # os.environ.setdefault("MAX_PIXELS", "100352")

    os.makedirs(ADAPTER_DIR, exist_ok=True)

    @dataclass
    class TrainingState:
        base_model: FastVisionModel
        model_processor: Any
        base_model_id: str
        adapters: List[V1Adapter]
        cache: Cache

    print("Loading base model and tokenizer...")
    base_model, model_processor = FastVisionModel.from_pretrained(
        BASE_MODEL_ID,
        dtype=torch.bfloat16,
        load_in_4bit=False,
        max_seq_length=32_768,
        use_gradient_checkpointing="unsloth",
    )
    print("Base model and tokenizer loaded.")

    print("\nApplying initial PEFT setup with FastVisionModel.get_peft_model...")
    plumbed_model: PeftModel = FastVisionModel.get_peft_model(
        base_model,
        r=64,
        lora_alpha=128,
        lora_dropout=0.0,
        bias="none",
        finetune_vision_layers=True,
        finetune_language_layers=True,
        # target_modules is determined internally by Unsloth based on above flags
    )
    print(f"Type of model after get_peft_model: {type(plumbed_model)}")

    global G_INITIAL_TARGET_MODULES_PATTERN

    # --- Capture the target_modules from the "default" adapter ---
    if "default" in plumbed_model.peft_config:
        G_INITIAL_TARGET_MODULES_PATTERN = plumbed_model.peft_config[
            "default"
        ].target_modules
        print(
            "Captured initial target_modules pattern from 'default' adapter's config."
        )

        # Delete the default adapter since we'll manage our own adapters
        print("Deleting 'default' adapter created by get_peft_model.")
        plumbed_model.delete_adapter("default")
    else:
        print(
            "Warning: 'default' adapter not found. Attempting to generate target_modules pattern manually."
        )
        G_INITIAL_TARGET_MODULES_PATTERN = get_peft_regex(
            base_model,
            finetune_vision_layers=True,
            finetune_language_layers=True,
            finetune_attention_modules=True,
            finetune_mlp_modules=True,
        )
        print("Generated initial target_modules pattern (fallback).")

    if G_INITIAL_TARGET_MODULES_PATTERN is None:
        raise RuntimeError(
            "Could not determine initial target_modules pattern. Aborting."
        )

    plumbed_model.active_adapter = None
    print(
        f"Initial target_modules pattern to be reused: '{str(G_INITIAL_TARGET_MODULES_PATTERN)[:200]}...'"
    )

    global state
    state = TrainingState(
        base_model=plumbed_model,
        model_processor=model_processor,
        base_model_id=BASE_MODEL_ID,
        adapters=[],
        cache=Cache(),
    )


def add_or_load_adapter_for_model(
    model: "PeftModel",  # type: ignore # noqa: F821
    adapter_name: str,
    resume_training: bool,
) -> str:
    """
    Smart adapter management that:
    1. Uses set_adapter() for fast switching to already-loaded adapters
    2. Uses traditional add_adapter() for new adapters
    3. Uses hotswap_adapter() only when updating existing adapters with new weights
    """
    from peft import LoraConfig  # type: ignore  # noqa: F401

    # Check hotswap availability with detailed debugging
    hotswap_available = False
    hotswap_adapter = None
    try:
        from peft.utils.hotswap import hotswap_adapter  # type: ignore

        hotswap_available = True
        print(
            f"[Smart Adapter] hotswap_adapter successfully imported: {hotswap_adapter}"
        )
    except ImportError as e:
        print(f"[Smart Adapter] hotswap_adapter import failed: {e}")
    except Exception as e:
        print(
            f"[Smart Adapter] Unexpected error importing hotswap_adapter: {type(e).__name__}: {e}"
        )

    print(f"[Smart Adapter] Hotswap functionality available: {hotswap_available}")

    global G_INITIAL_TARGET_MODULES_PATTERN
    print(
        f"\n[Smart Adapter] Managing adapter: '{adapter_name}', resume: {resume_training}"
    )

    adapter_base_folder = os.path.join(ADAPTER_DIR, adapter_name)
    os.makedirs(adapter_base_folder, exist_ok=True)
    path_containing_adapter_files = os.path.join(adapter_base_folder, adapter_name)

    # Check if adapter is already loaded
    adapter_already_loaded = adapter_name in model.peft_config
    has_saved_weights = os.path.isdir(path_containing_adapter_files) and os.listdir(
        path_containing_adapter_files
    )

    print(
        f"[Smart Adapter] Adapter '{adapter_name}' already loaded: {adapter_already_loaded}"
    )
    print(f"[Smart Adapter] Has saved weights: {has_saved_weights}")

    # Add more detailed state debugging
    if adapter_already_loaded:
        print(
            f"[Smart Adapter] Current adapter config for '{adapter_name}': {model.peft_config[adapter_name]}"
        )
        if hasattr(model.peft_config[adapter_name], "target_modules"):
            print(
                f"[Smart Adapter] Target modules: {model.peft_config[adapter_name].target_modules}"
            )

    if has_saved_weights:
        print(
            f"[Smart Adapter] Saved weight files: {os.listdir(path_containing_adapter_files)}"
        )
        # Check if required files exist
        config_file = os.path.join(path_containing_adapter_files, "adapter_config.json")
        weights_file = os.path.join(
            path_containing_adapter_files, "adapter_model.safetensors"
        )
        print(f"[Smart Adapter] Config file exists: {os.path.exists(config_file)}")
        print(f"[Smart Adapter] Weights file exists: {os.path.exists(weights_file)}")

        if os.path.exists(config_file):
            try:
                import json

                with open(config_file, "r") as f:
                    config_data = json.load(f)
                print(
                    f"[Smart Adapter] Saved config target_modules: {config_data.get('target_modules', 'not found')}"
                )
                print(
                    f"[Smart Adapter] Saved config r: {config_data.get('r', 'not found')}"
                )
                print(
                    f"[Smart Adapter] Saved config lora_alpha: {config_data.get('lora_alpha', 'not found')}"
                )
            except Exception as e:
                print(f"[Smart Adapter] Failed to read config file: {e}")

    print(f"[Smart Adapter] Resume training flag: {resume_training}")
    print(f"[Smart Adapter] Model class: {model.__class__.__name__}")
    print(f"[Smart Adapter] Model device: {getattr(model, 'device', 'no device attr')}")

    if adapter_already_loaded and has_saved_weights and resume_training:
        # CASE 1: Adapter is loaded but we have newer weights to hotswap in
        print(
            f"[Smart Adapter] HOTSWAPPING: Updating existing adapter '{adapter_name}' with new weights"
        )
        print(f"[Smart Adapter] Hotswap source path: {path_containing_adapter_files}")
        print(f"[Smart Adapter] Hotswap target adapter: {adapter_name}")
        print(f"[Smart Adapter] Model device: {getattr(model, 'device', 'unknown')}")
        print(f"[Smart Adapter] Model type: {type(model)}")
        print(
            f"[Smart Adapter] Available files at source: {os.listdir(path_containing_adapter_files) if os.path.exists(path_containing_adapter_files) else 'path does not exist'}"
        )

        if not hotswap_available or hotswap_adapter is None:
            print(
                f"[Smart Adapter] Hotswap not available, falling back to traditional reload"
            )
            model.delete_adapter(adapter_name)
            return add_adapter_traditionally(
                model, adapter_name, resume_training, path_containing_adapter_files
            )

        try:
            # Add more detailed debugging before hotswap
            print(
                f"[Smart Adapter] Current adapter configs: {list(model.peft_config.keys())}"
            )
            print(f"[Smart Adapter] Current active adapters: {model.active_adapters}")

            # Hotswap requires an active adapter to replace
            if model.active_adapter != adapter_name:
                print(
                    f"[Smart Adapter] Setting adapter '{adapter_name}' as active before hotswap"
                )
                model.set_adapter(adapter_name)
                print(f"[Smart Adapter] Active adapter now: {model.active_adapters}")

            hotswap_start_time = time.time()
            hotswap_adapter(
                model,
                path_containing_adapter_files,
                adapter_name=adapter_name,
                torch_device="cuda" if hasattr(model, "device") else None,
            )
            hotswap_end_time = time.time()
            print(
                f"[Smart Adapter] Hotswap time taken: {hotswap_end_time - hotswap_start_time} seconds"
            )
            print(
                f"[Smart Adapter] Successfully hotswapped new weights into '{adapter_name}'"
            )
        except Exception as e:
            print(
                f"[Smart Adapter] Hotswap failed with detailed error: {type(e).__name__}: {str(e)}"
            )
            print(f"[Smart Adapter] Exception traceback:")
            import traceback

            traceback.print_exc()
            print(
                f"[Smart Adapter] Falling back to traditional reload due to hotswap failure"
            )
            # Fallback: delete and reload traditionally
            model.delete_adapter(adapter_name)
            return add_adapter_traditionally(
                model, adapter_name, resume_training, path_containing_adapter_files
            )

    elif adapter_already_loaded:
        # CASE 2: Adapter is already loaded, just switch to it (fastest!)
        print(
            f"[Smart Adapter] FAST SWITCH: Adapter '{adapter_name}' already loaded, using set_adapter()"
        )

    else:
        # CASE 3: New adapter, load it traditionally
        print(f"[Smart Adapter] NEW ADAPTER: Loading '{adapter_name}' traditionally")
        return add_adapter_traditionally(
            model, adapter_name, resume_training, path_containing_adapter_files
        )

    # Set the adapter as active
    model.set_adapter(adapter_name)
    print(f"[Smart Adapter] Active adapter set to: '{model.active_adapters}'")
    return adapter_base_folder


def add_adapter_traditionally(
    model: "PeftModel",  # type: ignore # noqa: F821
    adapter_name: str,
    resume_training: bool,
    path_containing_adapter_files: str,
) -> str:
    """Traditional adapter loading for new adapters"""
    from peft import LoraConfig  # type: ignore

    global G_INITIAL_TARGET_MODULES_PATTERN

    print(f"[Traditional] Adding new adapter '{adapter_name}'")
    new_lora_config = LoraConfig(
        r=64,
        lora_alpha=128,
        lora_dropout=1e-3,
        bias="none",
        target_modules=G_INITIAL_TARGET_MODULES_PATTERN,
    )

    try:
        model.add_adapter(adapter_name=adapter_name, peft_config=new_lora_config)
        print(f"[Traditional] Added adapter '{adapter_name}' successfully")
    except Exception as e:
        print(f"[Traditional] Error adding adapter '{adapter_name}': {e}")
        raise

    # Load weights if resuming and they exist
    if (
        resume_training
        and os.path.isdir(path_containing_adapter_files)
        and os.listdir(path_containing_adapter_files)
    ):
        print(
            f"[Traditional] Loading weights for '{adapter_name}' from {path_containing_adapter_files}"
        )
        try:
            model.load_adapter(
                path_containing_adapter_files, adapter_name, is_trainable=True
            )
            print(
                f"[Traditional] Successfully loaded weights for adapter '{adapter_name}'"
            )
        except Exception as e:
            print(f"[Traditional] Error loading weights: {e}")

    model.set_adapter(adapter_name)
    return os.path.dirname(path_containing_adapter_files)


def drop_adapter_from_model(model: "PeftModel", adapter_name_to_drop: str):  # type: ignore # noqa: F821
    import torch  # type: ignore

    print(f"\n[Adapter Management] Request to drop adapter: '{adapter_name_to_drop}'")

    # With smart management, we generally want to KEEP adapters loaded for fast switching
    # Only drop if we're running out of memory or explicitly requested
    print(
        f"[Adapter Management] Currently loaded adapters: {list(model.peft_config.keys())}"
    )
    print(f"[Adapter Management] Currently active: {model.active_adapters}")

    # For now, just deactivate the adapter but keep it loaded for fast switching later
    if adapter_name_to_drop in model.peft_config:
        print(
            f"[Adapter Management] Keeping adapter '{adapter_name_to_drop}' loaded but deactivating"
        )
        model.active_adapter = None
        print("[Adapter Management] Deactivated adapter - no active adapter")
    else:
        print(
            f"[Adapter Management] Adapter '{adapter_name_to_drop}' not found in loaded adapters"
        )

    # Optional: Could add memory pressure detection and selective dropping here
    # For example:
    # if memory_pressure_detected():
    #     print(f"[Adapter Management] Memory pressure detected, actually dropping '{adapter_name_to_drop}'")
    #     model.delete_adapter(adapter_name_to_drop)

    torch.cuda.empty_cache()
    gc.collect()
    print(f"[Adapter Management] Finished managing adapter '{adapter_name_to_drop}'.\n")


def train_lora_adapter(
    adapter_name_to_train: str,
    training_dataset: Any,
    num_epochs: int = 1,
    resume_from_saved_state: bool = False,
    checkpoint_path: Optional[str] = None,
):
    import json  # Added for reading trainer_state.json
    import os  # ensure os is imported locally if not already

    import torch  # type: ignore
    from trl import SFTConfig, SFTTrainer  # type: ignore
    from unsloth import FastVisionModel, is_bf16_supported  # type: ignore
    from unsloth.trainer import UnslothVisionDataCollator  # type: ignore

    global state

    print(
        f"\n--- Starting train_lora_adapter for adapter: '{adapter_name_to_train}' (Epochs: {num_epochs}, Resume: {resume_from_saved_state}) ---"
    )

    # Use smart adapter management
    start_adapter_time = time.time()
    adapter_base_save_folder = add_or_load_adapter_for_model(
        state.base_model,
        adapter_name_to_train,
        resume_from_saved_state or bool(checkpoint_path),
    )
    end_adapter_time = time.time()
    print(
        f"Time taken to load adapter: {end_adapter_time - start_adapter_time} seconds"
    )
    print(
        f"Adapter base save folder for '{adapter_name_to_train}': {adapter_base_save_folder}"
    )

    # The smart management ensures the correct adapter is active
    print(f"Training will use adapter: '{adapter_name_to_train}'")
    print(f"Currently active adapters: {state.base_model.active_adapters}")

    print("\nPreparing model for training with FastVisionModel.for_training...")
    model_ready_for_training = FastVisionModel.for_training(state.base_model)
    print("Model prepared for training.")

    print("\nModel's trainable parameters (on instance passed to SFTTrainer):")
    try:
        model_ready_for_training.print_trainable_parameters()
    except AttributeError:
        total_params = sum(p.numel() for p in model_ready_for_training.parameters())
        trainable_params = sum(
            p.numel() for p in model_ready_for_training.parameters() if p.requires_grad
        )
        print(
            f"trainable params: {trainable_params:,} || all params: {total_params:,} || trainable%: {100 * trainable_params / total_params:.4f}"
        )

    initial_learning_rate = 4e-4  # 5e-5
    print(f"Using initial learning_rate for SFTTrainer: {initial_learning_rate}")

    sft_config_args = SFTConfig(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        num_train_epochs=num_epochs,
        learning_rate=initial_learning_rate,
        optim="adamw_8bit",
        fp16=not is_bf16_supported(),
        bf16=is_bf16_supported(),
        save_strategy="epoch",
        save_total_limit=1,
        output_dir=f"./runs/{adapter_name_to_train}",
        logging_steps=1,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model_ready_for_training,
        tokenizer=state.model_processor,
        data_collator=UnslothVisionDataCollator(
            model_ready_for_training, state.model_processor, resize="max"
        ),
        train_dataset=training_dataset,
        args=sft_config_args,
    )

    # For SFTTrainer's resume_from_checkpoint:
    # If checkpoint_path is explicitly given, use it.
    # Else, if resume_from_saved_state is True, pass True to trainer.train() to load latest from output_dir.
    # Otherwise, no resume.
    sft_trainer_resume_arg = None
    if checkpoint_path:
        sft_trainer_resume_arg = checkpoint_path
        print(
            f"SFTTrainer will attempt to resume from EXPLICIT checkpoint path: '{sft_trainer_resume_arg}'"
        )
    elif resume_from_saved_state:
        sft_trainer_resume_arg = (
            True  # Let Trainer find the latest checkpoint in output_dir
        )
        print(
            f"SFTTrainer will attempt to resume from the latest checkpoint in its output_dir: {sft_config_args.output_dir}"
        )
    else:
        print(
            "SFTTrainer training from scratch (no SFTTrainer checkpoint specified or found for resume)."
        )

    # Check if the directory for SFTTrainer resume exists if a path was constructed (not True)
    if isinstance(sft_trainer_resume_arg, str) and not os.path.isdir(
        sft_trainer_resume_arg
    ):
        print(
            f"Warning: SFTTrainer resume path '{sft_trainer_resume_arg}' not found. Training from scratch."
        )
        sft_trainer_resume_arg = None  # Fallback to no resume

    print("\nInspecting SFT checkpoint for prior epoch count before training starts...")
    sft_checkpoint_dir_to_inspect = None
    if isinstance(sft_trainer_resume_arg, str) and os.path.isdir(
        sft_trainer_resume_arg
    ):
        sft_checkpoint_dir_to_inspect = sft_trainer_resume_arg
        print(
            f"SFTTrainer is configured to resume from explicit path: {sft_checkpoint_dir_to_inspect}"
        )
    elif sft_trainer_resume_arg is True:
        # SFTTrainer will look in sft_config_args.output_dir
        print(
            f"SFTTrainer is configured to resume from latest in output_dir: {sft_config_args.output_dir}"
        )
        # We need to find what SFTTrainer would find.
        # find_latest_checkpoint is imported from orign, which should be available.
        latest_sft_checkpoint_in_output_dir = find_latest_checkpoint(
            sft_config_args.output_dir
        )
        if latest_sft_checkpoint_in_output_dir:
            sft_checkpoint_dir_to_inspect = latest_sft_checkpoint_in_output_dir
            print(
                f"Found latest SFT checkpoint for inspection: {sft_checkpoint_dir_to_inspect}"
            )
        else:
            print(
                f"No SFT checkpoint found in {sft_config_args.output_dir} to inspect for prior epochs."
            )
    else:
        print(
            "SFTTrainer is not configured to resume from a checkpoint. No prior SFT epochs to report from trainer_state.json."
        )

    if sft_checkpoint_dir_to_inspect:
        trainer_state_path_to_inspect = os.path.join(
            sft_checkpoint_dir_to_inspect, "trainer_state.json"
        )
        print(
            f"Attempting to read SFT trainer state from: {trainer_state_path_to_inspect}"
        )
        if os.path.exists(trainer_state_path_to_inspect):
            try:
                with open(trainer_state_path_to_inspect, "r") as f:
                    sft_state_data = json.load(f)
                sft_epochs_completed = sft_state_data.get("epoch", 0.0)
                sft_global_step = sft_state_data.get("global_step", 0)
                print(
                    f"  >> SFT Checkpoint State: Epochs completed = {sft_epochs_completed}, Global steps = {sft_global_step}"
                )
            except Exception as e:
                print(
                    f"  >> Warning: Failed to read/parse SFT {trainer_state_path_to_inspect}: {e}"
                )
        else:
            print(f"  >> Warning: SFT {trainer_state_path_to_inspect} not found.")
    print("--- End of SFT Checkpoint Inspection ---")

    print("\nStarting SFTTrainer training...")
    trainer.train(resume_from_checkpoint=sft_trainer_resume_arg)
    print("SFTTrainer training finished.")

    # Save adapter weights - much simpler now that we train the actual adapter
    print(
        f"\nSaving adapter weights for '{adapter_name_to_train}' to base folder: {adapter_base_save_folder}"
    )
    model_ready_for_training.save_pretrained(adapter_base_save_folder)
    print("Adapter weights saved.")

    # With smart management, we keep the adapter loaded for fast future access
    print(
        f"[Smart Management] Keeping adapter '{adapter_name_to_train}' loaded for fast future access"
    )
    # Just deactivate for now
    drop_adapter_from_model(state.base_model, adapter_name_to_train)

    del trainer, model_ready_for_training
    torch.cuda.empty_cache()
    gc.collect()
    print(
        f"--- train_lora_adapter for adapter: '{adapter_name_to_train}' completed ---\n"
    )


def train_unsloth_sft(message: Message[TrainingRequest]) -> TrainingResponse:
    import gc
    import json
    import shutil

    import requests
    import torch  # type: ignore
    from chatmux import oai_to_unsloth
    from nebu import (
        Bucket,
        ContainerConfig,
        V1ResourceReference,
        is_allowed,
    )

    from orign import Adapter, Training, V1LoraParams

    global state
    if not hasattr(state, "base_model") or not hasattr(state, "model_processor"):
        raise RuntimeError(
            "Base model and processor not initialized. Ensure init() has run."
        )

    # First ensure CUDA cache is cleared
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    # Force garbage collection multiple times to ensure all tensors are released
    gc.collect()

    print("message", message)
    if not message.content:
        raise ValueError("No training request provided")
    training_request: TrainingRequest = message.content

    container_config = ContainerConfig.from_env()
    print("container_config", container_config)

    bucket = Bucket()

    print("determining adapter namespace and name...")
    adapter_parts = training_request.adapter.split("/")
    if len(adapter_parts) == 2:
        print("adapter_parts", adapter_parts)
        adapter_namespace = adapter_parts[0]
        adapter_name = adapter_parts[1]
    else:
        adapter_name = training_request.adapter
        if training_request.owner:
            print("owner", training_request.owner)
            adapter_namespace = training_request.owner
        else:
            print("no owner, using message.handle", message.handle)
            adapter_namespace = message.handle

    print("adapter_namespace", adapter_namespace)
    if not adapter_namespace:
        raise ValueError("Could not determine adapter namespace")

    # Define local and bucket paths
    # ADAPTER_DIR is global: /nebu/cache/adapters
    local_adapter_weights_dir_for_current_adapter = os.path.join(
        ADAPTER_DIR, adapter_name
    )
    # train_lora_adapter saves adapter weights into a subfolder named adapter_name within this
    actual_local_adapter_files_path = os.path.join(
        local_adapter_weights_dir_for_current_adapter, adapter_name
    )

    local_sft_runs_dir = f"./runs/{adapter_name}"

    # Bucket URIs
    adapter_weights_bucket_uri = f"{container_config.namespace_volume_uri}/adapters/{adapter_namespace}/{adapter_name}"
    sft_checkpoints_bucket_uri = f"{container_config.namespace_volume_uri}/sft_runs/{adapter_namespace}/{adapter_name}"

    if training_request.labels:
        training_labels = training_request.labels.copy()
    else:
        training_labels = {}
    training_labels["message_id"] = message.id
    training_labels["container_id"] = os.getenv("NEBU_CONTAINER_ID", "unknown")
    random_chars = secrets.token_hex(3)

    adapter_ref = V1ResourceReference(
        name=adapter_name,
        namespace=adapter_namespace,
        kind="Adapter",
    )
    print("adapter_ref: ", adapter_ref)

    training = None
    try:
        print("creating training with api_key", message.api_key)
        training = Training(
            name=adapter_name + "-" + random_chars,
            namespace=adapter_namespace,
            config_data=message.model_dump(),
            adapter=adapter_ref,
            labels=training_labels,
            unique_adapter_active=True,
            api_key=message.api_key,
        )
        print("\n >> marking initial training as running")
        training.update(status=V1TrainingStatus.RUNNING)
    except Exception as e:
        print(
            f"FATAL: Failed to create or update Training resource for {adapter_ref}: {e}  --- retrying..."
        )
        raise RetriableError(
            f"Failed to set up Training resource: {e}  --- retrying..."
        ) from e

    failure = False
    try:
        start_adapter_time = time.time()
        adapter_resource = None
        try:
            adapters_found = Adapter.get(
                adapter_namespace, adapter_name, api_key=message.api_key
            )
            if adapters_found:
                adapter_resource = adapters_found[0]
        except Exception:
            adapters_found = []  # noqa
        print("found adapter resource", adapter_resource)

        is_continue = False
        epochs_trained_so_far = 0
        sft_checkpoint_to_resume_from = (
            None  # This will be local_sft_runs_dir if resuming
        )

        if adapter_resource:
            print("Found existing adapter resource: ", adapter_resource)
            epochs_trained_so_far = adapter_resource.epochs_trained

            if not is_allowed(
                adapter_resource.metadata.owner, message.user_id, message.orgs
            ):
                raise ValueError("You are not allowed to train this existing adapter")

            # Sync adapter weights from bucket to local ADAPTER_DIR/adapter_name
            # train_lora_adapter expects them in ADAPTER_DIR/adapter_name/adapter_name
            print(
                f"Attempting to sync adapter weights from {adapter_weights_bucket_uri} to {actual_local_adapter_files_path}"
            )
            os.makedirs(
                actual_local_adapter_files_path, exist_ok=True
            )  # Ensure target dir exists for sync

            adapter_sync_start_time = time.time()
            try:
                bucket.sync(adapter_weights_bucket_uri, actual_local_adapter_files_path)
                print(f"Synced adapter weights to {actual_local_adapter_files_path}")
                is_continue = True
            except Exception as e:
                print(
                    f"Warning: Failed to sync adapter weights from {adapter_weights_bucket_uri}: {e}. May proceed without them if adapter is being created fresh by train_lora_adapter."
                )
            adapter_sync_end_time = time.time()
            print(
                f"Time taken to sync adapter weights: {adapter_sync_end_time - adapter_sync_start_time} seconds"
            )

            # Check if we have a specific checkpoint URI instead of a general SFT runs directory
            checkpoint_uri = adapter_resource.checkpoint_uri
            # If checkpoint URI points to a specific checkpoint (contains "/checkpoint-")
            if checkpoint_uri and "/checkpoint-" in checkpoint_uri:
                checkpoint_name = os.path.basename(checkpoint_uri)
                print(
                    f"Found specific checkpoint reference: {checkpoint_name} in {checkpoint_uri}"
                )

                # Create local directory for this specific checkpoint
                local_checkpoint_dir = os.path.join(local_sft_runs_dir, checkpoint_name)
                os.makedirs(local_checkpoint_dir, exist_ok=True)

                # Sync that specific checkpoint from bucket
                try:
                    print(
                        f"Syncing specific checkpoint from {checkpoint_uri} to {local_checkpoint_dir}"
                    )
                    sync_start_time = time.time()
                    bucket.sync(checkpoint_uri, local_checkpoint_dir)
                    sync_end_time = time.time()
                    print(
                        f"Time taken to sync specific checkpoint: {sync_end_time - sync_start_time} seconds"
                    )
                    print(f"Successfully synced checkpoint {checkpoint_name}")
                    sft_checkpoint_to_resume_from = local_checkpoint_dir
                    is_continue = True
                except Exception as e:
                    print(f"Failed to sync specific checkpoint: {e}")
                    is_continue = False
            else:
                # Fallback to old behavior in case checkpoint_uri is not a specific checkpoint
                print(
                    f"No specific checkpoint reference found in adapter. Will sync from general checkpoint directory: {checkpoint_uri}"
                )
                try:
                    bucket.sync(checkpoint_uri, local_sft_runs_dir)
                    # Look for latest checkpoint in the synced directory
                    latest_checkpoint = find_latest_checkpoint(local_sft_runs_dir)
                    if latest_checkpoint:
                        print(
                            f"Found latest checkpoint in synced directory: {latest_checkpoint}"
                        )
                        sft_checkpoint_to_resume_from = latest_checkpoint
                        is_continue = True
                    else:
                        print("No valid checkpoint found in synced directory")
                        is_continue = False
                except Exception as e:
                    print(f"Failed to sync from general checkpoint directory: {e}")
                    is_continue = False
        else:
            print(
                f"No existing Adapter resource found for {adapter_namespace}/{adapter_name}. This will be a new training."
            )
            # Clean up local directories for a fresh start if they exist from a failed previous run
            if os.path.exists(local_adapter_weights_dir_for_current_adapter):
                shutil.rmtree(local_adapter_weights_dir_for_current_adapter)
                print(
                    f"Cleaned up existing local adapter dir: {local_adapter_weights_dir_for_current_adapter}"
                )
            if os.path.exists(local_sft_runs_dir):
                shutil.rmtree(local_sft_runs_dir)
                print(f"Cleaned up existing local SFT runs dir: {local_sft_runs_dir}")
            os.makedirs(local_adapter_weights_dir_for_current_adapter, exist_ok=True)
            os.makedirs(local_sft_runs_dir, exist_ok=True)

        end_adapter_time = time.time()
        print(
            f"Time taken to download adapter: {end_adapter_time - start_adapter_time} seconds"
        )

        print("Downloading dataset")
        time_start_download = time.time()
        response = requests.get(training_request.dataset)
        response.raise_for_status()
        print(f"Downloaded dataset in {time.time() - time_start_download} seconds")

        lines = response.content.decode("utf-8").splitlines()
        time_start_convert = time.time()
        converted_dataset = [
            oai_to_unsloth(json.loads(line)) for line in lines if line.strip()
        ]
        print(f"Converted dataset in {time.time() - time_start_convert} seconds")
        print("dataset example", converted_dataset[:1])

        # Calculate the cumulative target number of epochs
        cumulative_target_epochs = epochs_trained_so_far + training_request.epochs
        print(
            f"Adapter '{adapter_name}': Has {epochs_trained_so_far} epochs trained. Requesting additional {training_request.epochs} epochs. Target cumulative epochs: {cumulative_target_epochs}."
        )
        print(
            f"Calling train_lora_adapter for '{adapter_name}'. Resume SFT: {is_continue}, SFT checkpoint path hint: {sft_checkpoint_to_resume_from}"
        )

        time_start_train = time.time()
        train_lora_adapter(
            adapter_name_to_train=adapter_name,
            training_dataset=converted_dataset,
            num_epochs=cumulative_target_epochs,  # Pass cumulative target epochs
            resume_from_saved_state=is_continue,  # For adapter weights loading
            checkpoint_path=sft_checkpoint_to_resume_from
            if is_continue
            else None,  # For SFTTrainer resume
        )
        print(
            f"train_lora_adapter completed in {time.time() - time_start_train} seconds"
        )

        # After training, sync artifacts to bucket
        # 1. Sync adapter weights
        # train_lora_adapter saves them to actual_local_adapter_files_path
        if os.path.exists(actual_local_adapter_files_path) and os.listdir(
            actual_local_adapter_files_path
        ):
            print(
                f"Syncing adapter weights from {actual_local_adapter_files_path} to {adapter_weights_bucket_uri}"
            )
            bucket.copy(actual_local_adapter_files_path, adapter_weights_bucket_uri)
            print("Synced adapter weights to bucket.")
        else:
            print(
                f"Warning: Local adapter files path {actual_local_adapter_files_path} is empty or does not exist after training. Cannot sync to bucket."
            )

        # 2. Sync SFT checkpoints
        # train_lora_adapter's SFTTrainer saves to local_sft_runs_dir
        if os.path.exists(local_sft_runs_dir) and os.listdir(local_sft_runs_dir):
            # Find the latest checkpoint directory
            latest_checkpoint = find_latest_checkpoint(local_sft_runs_dir)
            if latest_checkpoint:
                # Extract the checkpoint name (e.g., "checkpoint-132")
                latest_checkpoint_name = os.path.basename(latest_checkpoint)
                # Create a specific path for just the latest checkpoint
                latest_checkpoint_bucket_uri = (
                    f"{sft_checkpoints_bucket_uri}/{latest_checkpoint_name}"
                )

                print(
                    f"Syncing latest SFT checkpoint from {latest_checkpoint} to {latest_checkpoint_bucket_uri}"
                )
                bucket.copy(latest_checkpoint, latest_checkpoint_bucket_uri)
                print(f"Synced latest checkpoint ({latest_checkpoint_name}) to bucket.")

                # We'll use this specific checkpoint URI instead of the parent directory
                checkpoint_uri_for_adapter = latest_checkpoint_bucket_uri
            else:
                print(
                    f"Warning: Could not find a checkpoint directory in {local_sft_runs_dir}"
                )
                checkpoint_uri_for_adapter = sft_checkpoints_bucket_uri
        else:
            print(
                f"Warning: Local SFT runs directory {local_sft_runs_dir} is empty or does not exist after training. Cannot sync to bucket."
            )
            checkpoint_uri_for_adapter = sft_checkpoints_bucket_uri

        # Collect metrics from trainer_state.json in the local SFT runs directory
        training_metrics = {}
        trainer_state_path = None  # Initialize to None

        latest_checkpoint_dir = find_latest_checkpoint(local_sft_runs_dir)
        if latest_checkpoint_dir:
            trainer_state_path = os.path.join(
                latest_checkpoint_dir, "trainer_state.json"
            )
            print(f"Found latest checkpoint directory: {latest_checkpoint_dir}")
            print(f"Attempting to load trainer_state.json from: {trainer_state_path}")
        else:
            print(
                f"Warning: No checkpoint directory found in {local_sft_runs_dir}. Looking for trainer_state.json in the root of SFT runs dir as a fallback."
            )
            # Fallback to old behavior if no checkpoint dir is found, though less likely to succeed
            trainer_state_path = os.path.join(local_sft_runs_dir, "trainer_state.json")

        if trainer_state_path and os.path.exists(trainer_state_path):
            try:
                with open(trainer_state_path, "r") as f:
                    state_data = json.load(f)
                training_metrics = state_data
                print(f"Loaded training metrics from {trainer_state_path}")
                log_history = state_data.get("log_history", [])
                if log_history:
                    print(f"  Final log_history entry: {log_history[-1]}")
            except Exception as e:
                print(f"Warning: Failed to read/parse {trainer_state_path}: {e}.")
        else:
            print(f"Warning: {trainer_state_path} not found. Metrics will be empty.")

        # Update Adapter resource with the specific checkpoint URI
        final_epochs_trained = epochs_trained_so_far + training_request.epochs

        Adapter(
            name=adapter_name,
            namespace=adapter_namespace,
            model_uri=adapter_weights_bucket_uri,  # URI now points to the adapter weights in the bucket
            checkpoint_uri=checkpoint_uri_for_adapter,  # URI now points to the specific latest checkpoint
            owner=training_request.owner or message.user_id,  # type: ignore
            base_model=training_request.model,  # This is the original base model ID like "unsloth/Qwen2.5-VL-32B-Instruct"
            epochs_trained=final_epochs_trained,
            examples_trained=(
                adapter_resource.examples_trained if adapter_resource else 0
            )
            + len(converted_dataset),
            last_trained=int(time.time()),
            lora=V1LoraParams(
                r=training_request.lora_rank,
                alpha=training_request.lora_alpha,
                dropout=training_request.lora_dropout,
            ),
            labels=training_request.labels,
            api_key=message.api_key,
        )

        training.log(data=training_metrics)

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        # Extract metrics for TrainingResponse
        # Use .get() with defaults to avoid KeyError if metrics are missing
        final_loss = 0.0
        train_steps_per_second = 0.0
        train_samples_per_second = 0.0
        train_runtime = 0.0

        if training_metrics:
            log_history = training_metrics.get("log_history", [])
            if log_history:  # Get loss from the last step
                final_loss = log_history[-1].get(
                    "loss", log_history[-1].get("train_loss", 0.0)
                )

            # These specific keys might not be in log_history but directly in trainer_stats from SFTTrainer
            # train_lora_adapter doesn't directly return trainer_stats, so we rely on trainer_state.json
            # which might have slightly different structure for aggregated stats.
            # For now, let's use what's typically available or default to 0.
            train_steps_per_second = training_metrics.get(
                "train_steps_per_second", 0.0
            )  # This key might not exist directly
            train_samples_per_second = training_metrics.get(
                "train_samples_per_second", 0.0
            )  # This key might not exist
            train_runtime = training_metrics.get(
                "train_runtime", time.time() - time_start_train
            )  # Fallback to measured time

        return TrainingResponse(
            loss=final_loss,
            train_steps_per_second=train_steps_per_second,
            train_samples_per_second=train_samples_per_second,
            train_runtime=train_runtime,
            adapter=training_request.adapter,
            adapter_uri=adapter_weights_bucket_uri,  # Return the bucket URI for the adapter weights
        )
    except Exception as e:
        print(f"Error training unsloth: {e}")
        failure = True
        if training:
            print("\n >> marking training as failed due to exception")
            training.update(status=V1TrainingStatus.FAILED)
        # If an error occurs, we must still return a TrainingResponse or raise.
        # Raising the original error is often better for debugging.
        raise
    finally:
        print(
            f"finally block: training resource exists: {bool(training)}, failure: {failure}"
        )
        if training:
            if failure:
                if (
                    training.training.status != V1TrainingStatus.FAILED
                ):  # Avoid double update if already set
                    print("\n >> ensuring training is marked as FAILED in finally")
                    training.update(status=V1TrainingStatus.FAILED)
            else:
                if training.training.status != V1TrainingStatus.COMPLETED:
                    print("\n >> marking training as COMPLETED in finally")
                    training.update(status=V1TrainingStatus.COMPLETED)


def UnslothSFT(
    platform: str = "runpod",
    accelerators: List[str] = ["1:H100_SXM"],
    image: str = "public.ecr.aws/d8i6n0n1/orign/unsloth-trainer:324d8c6",  # "us-docker.pkg.dev/agentsea-dev/orign/unsloth-train:latest"
    scale: V1Scale = scale,
    namespace: Optional[str] = None,
    env: Optional[List[V1EnvVar]] = None,
    config: Optional[NebuGlobalConfig] = None,
    hot_reload: bool = True,
    debug: bool = False,
    min_replicas: int = 1,
    max_replicas: int = 4,
    name: Optional[str] = None,
    wait_for_healthy: bool = True,
) -> Processor[TrainingRequest, TrainingResponse]:
    decorate = processor(
        image=image,
        # setup_script=setup_script,
        accelerators=accelerators,
        platform=platform,
        scale=scale,
        namespace=namespace,
        env=env,
        init_func=init,
        # execution_mode="subprocess",
        config=config,
        hot_reload=hot_reload,
        debug=debug,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        name=name,
        wait_for_healthy=wait_for_healthy,
    )
    return decorate(train_unsloth_sft)
