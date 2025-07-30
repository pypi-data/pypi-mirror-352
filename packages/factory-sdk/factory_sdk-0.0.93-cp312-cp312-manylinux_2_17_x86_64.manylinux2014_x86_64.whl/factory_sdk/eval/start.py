import os
import json
import pty
import subprocess
import sys

def run_with_live_output(command):
    """
    Run a command with live output using a PTY (works well in standard terminals).
    """
    master_fd, slave_fd = pty.openpty()
    
    process = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        text=True
    )
    
    os.close(slave_fd)
    
    try:
        while True:
            output = os.read(master_fd, 1024*1024)
            if not output:
                break

            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write(output)
            else:
                sys.stdout.write(output.decode())
            sys.stdout.flush()
    except OSError:
        pass  # PTY may be closed when process ends
    
    process.wait()
    return process.returncode

def start_eval(
    eval_dir,
    eval_args,
    model_paths,
    adapter_paths,
    dataset_path,
    recipe_path,
    client_params,
    eval_name,
):
    """
    Start evaluation by constructing the command and executing it.
    
    If an IPython environment is detected (e.g. in Google Colab), we use its system
    command (via `get_ipython().system()`) because PTY-based live output might not work.
    Otherwise, we use a PTY-based approach for live output.
    """
    # Construct the path to the run.py file (adjust if necessary)
    run_file_path = os.path.join(os.path.dirname(__file__), "run.py")
    
    # Build the command as a list for the subprocess/PTY method
    command_list = [
        "deepspeed",
        run_file_path,
        "--eval_dir", eval_dir,
        "--model_paths", json.dumps(model_paths),
        "--adapter_paths", json.dumps(adapter_paths),
        "--dataset_path", dataset_path,
        "--recipe_path", recipe_path,
        "--client_params", json.dumps(client_params),
        "--eval_name", eval_name,
        "--eval_args", eval_args.model_dump_json(),
    ]
    
    # Build the command string for an IPython environment (shell-based)
    command_str = (
        f"deepspeed {run_file_path} "
        f"--eval_dir {eval_dir} "
        f"--model_paths '{json.dumps(model_paths)}' "
        f"--adapter_paths '{json.dumps(adapter_paths)}' "
        f"--dataset_path {dataset_path} "
        f"--recipe_path {recipe_path} "
        f"--client_params '{json.dumps(client_params)}' "
        f"--eval_name {eval_name} "
        f"--eval_args '{eval_args.model_dump_json()}'"
    )
    
    # Try to detect if we're running inside an IPython environment
    try:
        from IPython import get_ipython
        ipython = get_ipython()
    except ImportError:
        ipython = None
    
    if ipython is not None:
        # Running in IPython/Colab: use its system command
        print("Detected IPython/Colab. Running command using Notebook Environment.")
        ipython.system(command_str)
        # Note: ipython.system does not return an exit code, so we return 0 by default
        return 0
    else:
        # Not in IPython: use the PTY-based execution for live output
        return run_with_live_output(command_list)

# Example usage:
if __name__ == "__main__":
    class DummyArgs:
        def model_dump_json(self):
            return '{"param": "value"}'
    
    exit_code = start_eval(
        eval_dir="/path/to/eval_dir",
        eval_args=DummyArgs(),
        model_paths=["/path/to/model1", "/path/to/model2"],
        adapter_paths=["/path/to/adapter1"],
        dataset_path="/path/to/dataset",
        recipe_path="/path/to/recipe",
        client_params={"key": "value"},
        eval_name="my_eval"
    )
    print("Process exited with code:", exit_code)
