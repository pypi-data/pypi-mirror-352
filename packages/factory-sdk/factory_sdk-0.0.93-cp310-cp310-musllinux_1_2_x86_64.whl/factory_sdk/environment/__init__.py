from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
import platform
import sys
import os
import subprocess
import sysconfig
from pydantic import BaseModel, Field
import torch
from factory_sdk.dto.project import (
    Package,
    Device,
    CUDAInfo,
    Environment,
    PythonInstallInfo,
    Project,
)
from rich.console import Console
from rich.traceback import install
from rich.panel import Panel

install(show_locals=True)
console = Console()


class EnvironmentError(Exception):
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.details = details or {}
        super().__init__(f"Environment Error: {message}\nDetails: {self.details}")
        console.print(
            Panel(f"[red]{message}[/red]\n{self.details}", border_style="red")
        )


class EnvironmentClient:
    def __init__(self, client: Any = None):
        self.client = client
        self.name = None
        self.system = platform.system().lower()

    def with_name(self, name: str) -> "EnvironmentClient":
        if not name or not isinstance(name, str):
            raise EnvironmentError("Invalid environment name", {"provided_name": name})
        self.name = name
        return self

    def _get_python_install_info(self) -> PythonInstallInfo:
        try:
            paths = {
                "stdlib": sysconfig.get_path("stdlib"),
                "site_packages": sysconfig.get_path("purelib"),
                "scripts": sysconfig.get_path("scripts"),
                "data": sysconfig.get_path("data"),
            }

            build_flags = []
            config_flags = sysconfig.get_config_vars()

            if config_flags.get("ABIFLAGS"):
                build_flags.append(f"ABI: {config_flags['ABIFLAGS']}")
            if config_flags.get("SOABI"):
                build_flags.append(f"SO ABI: {config_flags['SOABI']}")
            if hasattr(sys, "orig_argv"):
                build_flags.extend(
                    [f"Flag: {flag}" for flag in sys.orig_argv if flag.startswith("-")]
                )

            return PythonInstallInfo(
                executable_path=sys.executable,
                installation_prefix=sys.prefix,
                implementation=platform.python_implementation(),
                is_64bit=sys.maxsize > 2**32,
                compiler=platform.python_compiler(),
                build_flags=build_flags,
                paths=paths,
            )
        except Exception as e:
            raise EnvironmentError(
                "Failed to get Python installation info",
                {"error": str(e), "type": type(e).__name__},
            )

    def _run_command(self, cmd: List[str], timeout: int = 30) -> Optional[str]:
        try:
            use_shell = self.system == "windows"
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                shell=use_shell if use_shell else False,
                env=dict(os.environ, PATH=os.getenv("PATH", "")) if use_shell else None,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            return None

        except subprocess.TimeoutExpired:
            raise EnvironmentError(
                "Command timed out", {"command": cmd, "timeout": timeout}
            )
        except Exception as e:
            raise EnvironmentError(
                "Command execution failed", {"command": cmd, "error": str(e)}
            )

    def _get_python_version(self) -> str:
        try:
            return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        except Exception as e:
            raise EnvironmentError("Failed to get Python version", {"error": str(e)})

    def _get_cuda_info(self) -> Tuple[Optional[CUDAInfo], List[Device]]:
        if not torch.cuda.is_available():
            return None, []

        try:
            cuda_info = CUDAInfo(version=torch.version.cuda, compute_capabilities=[])

            devices = []
            compute_capabilities = []

            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                compute_cap = f"{props.major}.{props.minor}"
                compute_capabilities.append(compute_cap)

                device = Device(
                    name=props.name,
                    compute_capability=compute_cap,
                    total_memory=f"{props.total_memory / (1024**3):.2f}GB",
                    multi_processor_count=str(props.multi_processor_count),
                )
                devices.append(device)

            cuda_info.compute_capabilities = compute_capabilities

            try:
                nvcc_output = self._run_command(["nvcc", "--version"])
                if nvcc_output:
                    import re

                    toolkit_match = re.search(r"release (\S+),", nvcc_output)
                    if toolkit_match:
                        cuda_info.toolkit_version = toolkit_match.group(1)
            except Exception:
                pass

            try:
                nvidia_smi_cmd = [
                    "nvidia-smi",
                    "--query-gpu=driver_version",
                    "--format=csv,noheader",
                ]
                if self.system == "windows":
                    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
                    nvidia_smi = (
                        Path(program_files)
                        / "NVIDIA Corporation"
                        / "NVSMI"
                        / "nvidia-smi.exe"
                    )
                    if nvidia_smi.exists():
                        nvidia_smi_cmd[0] = str(nvidia_smi)

                driver_output = self._run_command(nvidia_smi_cmd)
                if driver_output:
                    cuda_info.driver_version = driver_output.splitlines()[0].strip()
            except Exception:
                pass

            return cuda_info, devices

        except Exception as e:
            raise EnvironmentError("Failed to get CUDA information", {"error": str(e)})

    def _get_pip_freeze_packages(self) -> List[Package]:
        packages = []

        pip_commands = [
            [sys.executable, "-m", "pip", "freeze"],
            ["pip3", "freeze"],
            ["pip", "freeze"],
        ]
        if self.system == "windows":
            pip_commands.append(["py", "-m", "pip", "freeze"])

        for cmd in pip_commands:
            output = self._run_command(cmd)
            if not output:
                continue

            for line in output.splitlines():
                try:
                    if not line or line.startswith("#"):
                        continue

                    if "==" in line:
                        name, version = line.split("==", 1)
                    elif "@" in line:
                        name = line.split("@")[0]
                        version = "git"
                    elif " @ " in line:
                        name = line.split(" @ ")[0]
                        version = "local"
                    else:
                        continue

                    name = name.strip().strip("\"'")
                    version = version.strip().strip("\"'")

                    if name and version:
                        packages.append(Package(name=name, version=version))

                except Exception:
                    pass

            if packages:
                break

        if not packages:
            try:
                import pkg_resources

                for pkg in pkg_resources.working_set:
                    packages.append(Package(name=pkg.key, version=pkg.version))
            except Exception:
                pass

        return packages

    def freeze(self) -> Environment:
        try:
            if not self.name:
                raise EnvironmentError("Environment name is required")

            python_info = self._get_python_install_info()
            cuda_info, devices = self._get_cuda_info()
            packages = self._get_pip_freeze_packages()

            environment = Environment(
                name=self.name,
                python_info=python_info,
                cuda_info=cuda_info,
                devices=devices,
                packages=packages,
            )

            project = self.client.get(
                f"projects/{self.client._project.id}",
                response_class=Project,
                scope="tenant",
            )
            project.environments[self.name] = environment

            self.client.put(
                f"projects/{self.client._project.id}",
                project,
                response_class=Project,
                scope="tenant",
            )

            return environment

        except EnvironmentError:
            raise
        except Exception as e:
            raise EnvironmentError(
                "Unexpected error while freezing environment",
                {"error": str(e), "type": type(e).__name__},
            )
