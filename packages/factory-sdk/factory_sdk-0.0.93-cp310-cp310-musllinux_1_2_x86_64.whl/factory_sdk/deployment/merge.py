import os
import json
import sys
import shutil
import argparse
from glob import glob
from rich.progress import Progress
from factory_sdk.utils.model import load_model_for_evaluation
from transformers import AutoConfig
import torch


def merge_adapter(model_path, adapter_paths, output_dir, dtype="float16", device="auto"):
    """
    Merge the adapter into the base model and save to output directory.
    
    Args:
        model_path: Path to the base model
        adapter_paths: Dictionary of adapter names to paths
        output_dir: Directory to save the merged model
        dtype: Data type for the merge ('float16', 'float32' or 'bfloat16')
        device: Device to use for merging ('cpu', 'cuda', 'auto')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert dtype string to torch dtype
        if dtype == "float16":
            torch_dtype = torch.float16
        elif dtype == "float32":
            torch_dtype = torch.float32
        elif dtype == "bfloat16":
            torch_dtype = torch.bfloat16
        else:
            torch_dtype = torch.float16
            print(f"Warning: Unsupported dtype '{dtype}', using float16 instead")
        
        # Ensure adapter_paths is a dictionary
        if isinstance(adapter_paths, str):
            try:
                adapter_paths = json.loads(adapter_paths)
            except json.JSONDecodeError:
                print("Error: adapter_paths must be a JSON dictionary or a Python dict")
                return False
        
        # Get the first adapter for now (only one supported in many architectures)
        if len(adapter_paths) != 1:
            print(f"Warning: Only one adapter is fully supported. Using first of {len(adapter_paths)}")
        
        adapter_name = list(adapter_paths.keys())[0]
        adapter_path = adapter_paths[adapter_name]
        
        print(f"Loading model from {model_path}")
        print(f"Loading adapter from {adapter_path}")
        print(f"Using {dtype} precision on {device}")
        
        # Check model architecture
        cfg = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        architectures = cfg.architectures if hasattr(cfg, "architectures") else []
        
        if not architectures:
            print("Warning: No architecture found in model config")
        else:
            print(f"Model architecture: {architectures[0]}")
        
        # Load model with adapter
        model_instance = load_model_for_evaluation(
            model_path,
            adapter_path,
            bnb_config=None,
            dtype=torch_dtype,
            device=device
        )
        
        # Merge adapter
        print("Merging adapter with base model...")
        model = model_instance.model.merge_and_unload()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy non-weight files from model_path to output_dir
        files = glob(f"{model_path}/*")
        print(f"Copying model files to {output_dir}")
        
        with Progress() as progress:
            task = progress.add_task("Copying model files", total=len(files))
            for file in files:
                # Skip weights files
                if file.endswith(".safetensors") or file.endswith(".bin") or file.endswith(".index.json"):
                    progress.update(task, advance=1)
                    continue
                
                # Copy other files (tokenizer, config, etc.)
                shutil.copy(file, output_dir)
                progress.update(task, advance=1)
        
        # Save merged model
        print(f"Saving merged model to {output_dir}")
        model.save_pretrained(output_dir, safe_serialization=False)
        
        print("Model merge completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during model merge: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge adapter into base model")
    parser.add_argument("--args", type=str, help="JSON string with all arguments")
    
    # Individual arguments (used if --args is not provided)
    parser.add_argument("--model_path", type=str, help="Path to the base model")
    parser.add_argument("--adapter_paths", type=str, help="JSON dictionary of adapter names to paths")
    parser.add_argument("--output_dir", type=str, help="Directory to save the merged model")
    parser.add_argument("--dtype", type=str, default="float16", help="Data type for merge (float16, float32, bfloat16)")
    parser.add_argument("--device", type=str, default="auto", help="Device to use for merging")
    
    args = parser.parse_args()
    
    # Check if all args are in a JSON string
    if args.args:
        try:
            params = json.loads(args.args)
            model_path = params.get("model_path")
            adapter_paths = params.get("adapter_paths")
            output_dir = params.get("output_dir")
            dtype = params.get("dtype", "float16")
            device = params.get("device", "auto")
        except json.JSONDecodeError:
            print("Error: Could not parse JSON args")
            sys.exit(1)
    else:
        # Use individual arguments
        model_path = args.model_path
        adapter_paths = args.adapter_paths
        try:
            if adapter_paths:
                adapter_paths = json.loads(adapter_paths)
        except json.JSONDecodeError:
            print("Error: adapter_paths must be a valid JSON string")
            sys.exit(1)
        output_dir = args.output_dir
        dtype = args.dtype
        device = args.device
    
    # Validate required arguments
    if not model_path:
        print("Error: model_path is required")
        sys.exit(1)
    if not adapter_paths:
        print("Error: adapter_paths is required")
        sys.exit(1)
    if not output_dir:
        print("Error: output_dir is required")
        sys.exit(1)
    
    # Run the merge
    success = merge_adapter(model_path, adapter_paths, output_dir, dtype, device)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)