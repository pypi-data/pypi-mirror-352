import os
import pty
import subprocess
import sys
import json
import shlex
import threading
import time
import tempfile
import signal
from typing import Dict, List, Union, Optional, Any


class FactoryProcess:
    """
    A class representing a factory deployment process.
    Provides methods to monitor, control and get status information about the process.
    """
    
    def __init__(self, process, thread=None, return_code_path=None, log_file=None, pid=None, ipython_mode=False):
        """
        Initialize the FactoryProcess object.
        
        Args:
            process: The subprocess.Popen object or None if in ipython mode
            thread: The output reader thread if applicable
            return_code_path: Path to the file storing the return code
            log_file: Path to the log file if using nohup in ipython mode
            pid: Process ID
            ipython_mode: Whether this is running in IPython/Colab environment
        """
        self.process = process
        self.thread = thread
        self.return_code_path = return_code_path
        self.log_file = log_file
        self.pid = pid
        self.ipython_mode = ipython_mode
        self._is_running = True
        
    def is_running(self) -> bool:
        """
        Check if the process is still running.
        
        Returns:
            bool: True if the process is still running, False otherwise
        """
        if not self._is_running:
            return False
            
        if self.ipython_mode:
            # In IPython mode, we need to check the process differently
            if self.pid is None:
                return False
                
            try:
                # Send signal 0 to check if process exists
                os.kill(self.pid, 0)
                return True
            except OSError:
                self._is_running = False
                return False
        else:
            # Standard process check
            if self.process is None:
                return False
                
            ret_code = self.process.poll()
            if ret_code is None:
                return True
            else:
                self._is_running = False
                return False
    
    def get_return_code(self) -> Optional[int]:
        """
        Get the return code of the process if it has completed.
        
        Returns:
            Optional[int]: The return code if the process has completed, None otherwise
        """
        if self.is_running():
            return None
            
        if self.ipython_mode:
            # In IPython mode, we can't easily get the return code
            return None
            
        # For normal processes, get from process object
        if self.process is not None:
            return self.process.returncode
            
        # Try reading from the file
        if self.return_code_path and os.path.exists(self.return_code_path):
            try:
                with open(self.return_code_path, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, FileNotFoundError):
                pass
                
        return None
    
    def terminate(self, timeout: int = 5) -> bool:
        """
        Terminate the process gracefully first, then forcefully if needed.
        
        Args:
            timeout: Number of seconds to wait for graceful termination before killing
            
        Returns:
            bool: True if the process was terminated, False otherwise
        """
        if not self.is_running():
            return True
            
        if self.ipython_mode:
            if self.pid is not None:
                try:
                    os.kill(self.pid, signal.SIGTERM)
                    # Wait for process to terminate
                    for _ in range(timeout):
                        time.sleep(1)
                        try:
                            os.kill(self.pid, 0)
                        except OSError:
                            # Process has terminated
                            self._is_running = False
                            return True
                            
                    # If we're here, the process didn't terminate gracefully
                    try:
                        os.kill(self.pid, signal.SIGKILL)
                        self._is_running = False
                        return True
                    except OSError:
                        pass
                except OSError:
                    # Process doesn't exist
                    self._is_running = False
                    return True
        else:
            if self.process is not None:
                self.process.terminate()
                try:
                    # Wait for the process to terminate
                    self.process.wait(timeout=timeout)
                    self._is_running = False
                    return True
                except subprocess.TimeoutExpired:
                    # Process didn't terminate gracefully, kill it
                    self.process.kill()
                    self.process.wait()
                    self._is_running = False
                    return True
                
        return False
    
    def wait(self, timeout: Optional[float] = None) -> Optional[int]:
        """
        Wait for the process to complete.
        
        Args:
            timeout: Maximum time to wait in seconds, or None to wait indefinitely
            
        Returns:
            Optional[int]: Return code if process completed, None if timed out
        """
        if self.ipython_mode:
            # In IPython mode, we need to poll
            if timeout is not None:
                end_time = time.time() + timeout
                while time.time() < end_time:
                    if not self.is_running():
                        return self.get_return_code()
                    time.sleep(0.5)
                return None
            else:
                # No timeout, poll indefinitely
                while self.is_running():
                    time.sleep(0.5)
                return self.get_return_code()
        else:
            if self.process is not None:
                try:
                    return_code = self.process.wait(timeout=timeout)
                    self._is_running = False
                    return return_code
                except subprocess.TimeoutExpired:
                    return None
            return self.get_return_code()
    
    def __str__(self) -> str:
        """String representation of the FactoryProcess"""
        status = "running" if self.is_running() else "completed"
        if not self.is_running():
            return_code = self.get_return_code()
            status += f" (return code: {return_code})"
        return f"FactoryProcess(pid={self.pid}, status={status})"
    
    def __repr__(self) -> str:
        """Detailed representation of the FactoryProcess"""
        return self.__str__()


def run_with_live_output(command, daemon=False):
    """Helper function to run command with live output using a PTY"""
    master_fd, slave_fd = pty.openpty()
    
    # Create a temporary file to store the return code
    return_code_path = None
    if daemon:
        return_code_file = tempfile.NamedTemporaryFile(delete=False)
        return_code_path = return_code_file.name
        return_code_file.close()
    
    process = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        text=True
    )
    
    os.close(slave_fd)
    
    def output_reader():
        try:
            while True:
                output = os.read(master_fd, 1024 * 1024)
                if not output:
                    break

                if hasattr(sys.stdout, "buffer"):
                    sys.stdout.buffer.write(output)
                else:
                    sys.stdout.write(output)
                sys.stdout.flush()
        except OSError:
            pass  # The PTY may close when the process ends
        
        # If daemon mode, write the return code to file when process completes
        if daemon and return_code_path:
            process.wait()
            with open(return_code_path, 'w') as f:
                f.write(str(process.returncode))
    
    # Start output reader in a thread
    reader_thread = threading.Thread(target=output_reader)
    reader_thread.daemon = daemon  # Make the thread daemon if requested
    reader_thread.start()
    
    if not daemon:
        # Wait for the thread to complete if not in daemon mode
        reader_thread.join()
        process.wait()
        return process.returncode
    else:
        # Return a FactoryProcess object
        return FactoryProcess(
            process=process,
            thread=reader_thread,
            return_code_path=return_code_path,
            pid=process.pid
        )


def start_deployment(
        deployment_dir: str,
        deployment_args: Any,
        model_path: str,
        adapter_paths: List[str],
        recipe_paths: List[str],
        client_params: Dict[str, Any],
        deployment_name: str,
        deployment_structure: Dict[str, Any],
        daemon: bool = False
) -> Union[int, FactoryProcess]:
    """
    Start deployment with proper output handling.
    
    Args:
        deployment_dir: Directory for the deployment
        deployment_args: Arguments for the deployment
        model_path: Path to the model
        adapter_paths: List of paths to adapters
        recipe_paths: List of paths to recipes
        client_params: Parameters for the client
        deployment_name: Name of the deployment
        deployment_structure: Structure of the deployment
        daemon: Whether to run as a daemon process
        
    Returns:
        Union[int, FactoryProcess]: If daemon=False, returns the exit code.
                                   If daemon=True, returns a FactoryProcess object.
    """
    # Construct the path to the run.py file
    run_file_path = os.path.join(os.path.dirname(__file__), "run.py")

    from factory_sdk.fast.args import encrypt_param

    # Build the base command as a list (for PTY/subprocess execution)
    command_list = [
        "python",
        run_file_path,
        "--deployment_dir", deployment_dir,
        "--model_path", model_path,
        "--adapter_paths", json.dumps(adapter_paths),
        "--client_params", encrypt_param(json.dumps(client_params)),
        "--deployment_name", deployment_name,
        "--deployment_args", deployment_args.model_dump_json(),
        "--recipe_paths", json.dumps(recipe_paths),
        "--trust-remote-code",
        "--deployment_structure", json.dumps(deployment_structure)
    ]
    
    # Build the command string for an IPython environment.
    command_str = " ".join(shlex.quote(arg) for arg in command_list)
    
    # Check if we're running in an IPython environment.
    try:
        from IPython import get_ipython
        ipython = get_ipython()
    except ImportError:
        ipython = None
        
    if ipython is not None and not daemon:
        # IPython environment doesn't support daemon mode well
        print("Detected IPython/Colab environment. Running command using Notebook Environment:")
        ipython.system(command_str)
        # ipython.system doesn't return an exit code, so return 0 by default.
        return 0
    elif ipython is not None and daemon:
        # For daemon mode in IPython, we need a different approach
        print("Detected IPython/Colab environment with daemon=True. Using background execution.")
        
        log_file = f"/tmp/deployment_{deployment_name}.out"
        # Use nohup to run in background
        bg_command = f"nohup {command_str} > {log_file} 2>&1 & echo $!"
        pid_output = ipython.getoutput(bg_command)
        
        try:
            # Try to extract PID from the output
            pid = int(pid_output[-1].strip())
            print(f"Started daemon process with PID: {pid}")
            
            # Return a FactoryProcess object
            return FactoryProcess(
                process=None,
                log_file=log_file,
                pid=pid,
                ipython_mode=True
            )
        except (ValueError, IndexError):
            print("Warning: Could not determine PID of daemon process")
            return FactoryProcess(
                process=None,
                log_file=log_file,
                ipython_mode=True
            )
    else:
        # Use the PTY-based execution for live output.
        result = run_with_live_output(command_list, daemon=daemon)
        return result


# Example usage:
if __name__ == "__main__":
    # Dummy deployment_args for demonstration
    class DummyDeploymentArgs:
        def model_dump(self):
            return {
                "learning_rate": 0.001,
                "batch_size": 32,
                "use_gpu": True,
                "verbose": False,
            }
            
        def model_dump_json(self):
            return json.dumps(self.model_dump())
    
    # Example with daemon=False (synchronous)
    print("Starting synchronous deployment...")
    exit_code = start_deployment(
        deployment_dir="/path/to/deployment_dir",
        deployment_args=DummyDeploymentArgs(),
        model_path="/path/to/model",
        adapter_paths=["/path/to/adapter1", "/path/to/adapter2"],
        recipe_paths=["/path/to/recipe"],
        client_params={"key": "value"},
        deployment_name="my_deployment",
        deployment_structure={"key": "value"},
        daemon=False
    )
    print(f"Synchronous deployment process exited with code: {exit_code}")
    
    # Example with daemon=True (asynchronous)
    print("\nStarting daemon deployment...")
    process = start_deployment(
        deployment_dir="/path/to/deployment_dir",
        deployment_args=DummyDeploymentArgs(),
        model_path="/path/to/model",
        adapter_paths=["/path/to/adapter1", "/path/to/adapter2"],
        recipe_paths=["/path/to/recipe"],
        client_params={"key": "value"},
        deployment_name="daemon_deployment",
        deployment_structure={"key": "value"},
        daemon=True
    )
    
    print(f"Daemon process info: {process}")
    
    # Example of checking status after some time
    print("\nWaiting for 3 seconds to check status...")
    time.sleep(3)
    
    print(f"Is process still running? {process.is_running()}")
    print(f"Current return code: {process.get_return_code()}")
    
    # Example of terminating the process
    print("\nTerminating process...")
    process.terminate()
    print(f"Process terminated. Is still running? {process.is_running()}")
    print(f"Final return code: {process.get_return_code()}")