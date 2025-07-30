import os
import pty
import subprocess
import sys
from typing import Dict, Any

def run_with_live_output(command):
    """Run command with live output using a PTY and write bytes directly."""
    master_fd, slave_fd = pty.openpty()
    
    process = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        text=False
    )
    
    os.close(slave_fd)
    
    out_stream = getattr(sys.__stdout__, "buffer", None)
    if out_stream is None:
        raise RuntimeError("No binary stdout stream available.")
    
    try:
        while True:
            output = os.read(master_fd, 1024 * 1024)
            if not output:
                break
            out_stream.write(output)
            out_stream.flush()
    except OSError:
        pass
    
    process.wait()
    return process.returncode

def start_init(
    model_path: str,
    dataset_path: str,
    recipe_path: str,
    run_id: str,
    run_dir: str,
    adapter_args: Dict[str, Any],
    train_args: Dict[str, Any],
    init_args: Dict[str, Any],
) -> int:
    """
    Start initialization with proper output handling.
    
    Args:
        model_path: Path to the model
        dataset_path: Path to the dataset
        recipe_path: Path to the recipe
        run_id: Unique identifier for the run
        run_dir: Directory for run outputs
        adapter_args: Arguments for adapter configuration
        train_args: Arguments for training configuration
        init_args: Arguments for initialization configuration
        
    Returns:
        int: Exit code from the initialization process
    """
    # Construct the path to the init script
    init_file_path = os.path.join(os.path.dirname(__file__), "run_init.py")
    
    # Build the command as a list for PTY/subprocess execution
    command_list = [
        "python",
        init_file_path,
        "--adapter-args", adapter_args.model_dump_json(),
        "--train-args", train_args.model_dump_json(),
        "--init-args", init_args.model_dump_json(),
        "--model-path", model_path,
        "--dataset-path", dataset_path,
        "--recipe-path", recipe_path,
        "--run-id", run_id,
        "--run-dir", run_dir,
    ]
    
    # Build the command string for IPython environment
    command_str = (
        f"python {init_file_path} "
        f"--adapter-args '{adapter_args.model_dump_json()}' "
        f"--train-args '{train_args.model_dump_json()}' "
        f"--init-args '{init_args.model_dump_json()}' "
        f"--model-path {model_path} "
        f"--dataset-path {dataset_path} "
        f"--recipe-path {recipe_path} "
        f"--run-id {run_id} "
        f"--run-dir {run_dir}"
    )
    
    # Check for IPython environment
    try:
        from IPython import get_ipython
        ipython = get_ipython()
    except ImportError:
        ipython = None
    
    if ipython is not None:
        print("Detected IPython/Colab. Running initialization using Notebook Environment.")
        ipython.system(command_str)
        return 0
    else:
        return run_with_live_output(command_list)

# Example usage
if __name__ == "__main__":
    # Example parameters - replace with actual values
    exit_code = start_init(
        model_path="/path/to/model",
        dataset_path="/path/to/dataset",
        recipe_path="/path/to/recipe",
        run_id="run123",
        run_dir="/path/to/run_dir",
        adapter_args={"adapter_key": "value"},
        train_args={"train_key": "value"},
        init_args={"init_key": "value"}
    )
    print("Initialization process exited with code:", exit_code)