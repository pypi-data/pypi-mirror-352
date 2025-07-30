import os
from typing import Dict, Union, Optional
from factory_sdk.fast.processes.process_runner import FactoryProcess, run_script


def start_merge(
    model_path: str,
    adapter_paths: Dict[str, str],
    output_dir: str,
    deployment_name: str = None,
    dtype: str = "float16",
    device: str = "auto",
    daemon: bool = False,
    working_dir: Optional[str] = None
) -> Union[int, FactoryProcess]:
    """
    Start a model merge process with proper output handling.
    
    Args:
        model_path: Path to the base model
        adapter_paths: Dictionary of adapter names to paths
        output_dir: Directory to save the merged model
        deployment_name: Name of the deployment (for logging)
        dtype: Data type for the merge ('float16', 'float32' or 'bfloat16')
        device: Device to use for merging ('cpu', 'cuda', 'auto')
        daemon: Whether to run as a daemon process
        working_dir: Working directory to run the script in
        
    Returns:
        Union[int, FactoryProcess]: If daemon=False, returns the exit code.
                                   If daemon=True, returns a FactoryProcess object.
    """
    # Construct the path to the merge.py file
    merge_script_path = os.path.join(os.path.dirname(__file__), "merge.py")
    
    # Create a name for logs if not provided
    if not deployment_name:
        # Use base model name as deployment name
        deployment_name = os.path.basename(model_path)
    
    # Create arguments dict
    args = {
        "model_path": model_path,
        "adapter_paths": adapter_paths,
        "output_dir": output_dir,
        "dtype": dtype,
        "device": device
    }
    
    # Set up environment variables
    env_vars = {}
    
    # Set CUDA device if using specific GPU
    if device.startswith("cuda:"):
        gpu_id = device.split(":")[-1]
        env_vars["CUDA_VISIBLE_DEVICES"] = gpu_id
    
    # Set up a custom log file for IPython daemon mode
    log_file = f"/tmp/merge_{deployment_name}.out"
    
    # Call the generic run_script function
    return run_script(
        script_path=merge_script_path,
        args=args,
        env_vars=env_vars,
        daemon=daemon,
        working_dir=working_dir,
        log_file=log_file
    )