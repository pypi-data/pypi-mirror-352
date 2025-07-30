import os
import pty
import subprocess
import sys
import json

def run_with_live_output(command):
    """Run command with live output using a PTY and write bytes directly."""
    master_fd, slave_fd = pty.openpty()
    
    # Ensure the child process writes raw bytes.
    process = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        text=False  # Output will be in bytes.
    )
    
    os.close(slave_fd)
    
    # Use the original stdout's binary stream.
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
        pass  # The PTY may close when the process ends
    
    process.wait()
    return process.returncode

def start_training(
    model_path,
    model_id,
    model_revision,
    dataset_path,
    recipe_path,
    recipe_id,
    recipe_revision,
    run_path,
    client_params,
    adapter_name,
):
    """
    Start training with proper output handling.
    
    If an IPython environment is detected (e.g. in Colab), use its system
    command to execute the command string. Otherwise, use a PTY-based approach
    for live output of raw bytes.
    """
    # Construct the path to the run.py file (adjust if needed)
    run_file_path = os.path.join(os.path.dirname(__file__), "run.py")
    
    # Build the command as a list (for PTY/subprocess execution)
    command_list = [
        "deepspeed",
        run_file_path,
        "--model_path", model_path,
        "--dataset_path", dataset_path,
        "--recipe_path", recipe_path,
        "--run_path", run_path,
        "--client_params", json.dumps(client_params),
        "--adapter_name", adapter_name,
        "--recipe_id", recipe_id,
        "--recipe_revision", recipe_revision,
        "--model_id", model_id,
        "--model_revision", model_revision,
    ]
    
    # Build the command string for an IPython environment
    command_str = (
        f"deepspeed {run_file_path} "
        f"--model_path {model_path} "
        f"--dataset_path {dataset_path} "
        f"--recipe_path {recipe_path} "
        f"--run_path {run_path} "
        f"--client_params '{json.dumps(client_params)}' "
        f"--adapter_name {adapter_name} "
        f"--recipe_id {recipe_id} "
        f"--recipe_revision {recipe_revision} "
        f"--model_id {model_id} "
        f"--model_revision {model_revision}"
    )
    
    # Try to detect if we're running inside an IPython environment
    try:
        from IPython import get_ipython
        ipython = get_ipython()
    except ImportError:
        ipython = None
    
    if ipython is not None:
        print("Detected IPython/Colab. Running command using Notebook Environment.")
        ipython.system(command_str)
        # ipython.system does not return an exit code, so we return 0 by default.
        return 0
    else:
        # Not in IPython: use the PTY-based execution for live output.
        return run_with_live_output(command_list)

# Example usage:
if __name__ == "__main__":
    # Dummy values for demonstration; replace with actual parameters as needed.
    exit_code = start_training(
        model_path="/path/to/model",
        model_id="model123",
        model_revision="v1.0",
        dataset_path="/path/to/dataset",
        recipe_path="/path/to/recipe",
        recipe_id="recipe456",
        recipe_revision="v2.0",
        run_path="/path/to/run_dir",
        client_params={"key": "value"},
        adapter_name="my_adapter"
    )
    print("Process exited with code:", exit_code)
