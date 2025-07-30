from pydantic import BaseModel, Field, AfterValidator
from datetime import datetime
from typing import List, Annotated
from uuid import uuid4
from factory_sdk.dto.resource import is_valid_uuid
from typing import Optional


class NewProject(BaseModel):
    name: str


class Package(BaseModel):
    name: str
    version: str


class Device(BaseModel):
    name: str
    compute_capability: str
    total_memory: str
    multi_processor_count: str = Field(
        ..., description="Number of multiprocessors on the device"
    )


class CUDAInfo(BaseModel):
    version: str = Field(..., description="CUDA version from PyTorch")
    toolkit_version: Optional[str] = Field(
        None, description="CUDA toolkit version from nvcc"
    )
    driver_version: Optional[str] = Field(None, description="NVIDIA driver version")
    compute_capabilities: List[str] = Field(
        default_factory=list, description="Compute capabilities of available devices"
    )


class PythonInstallInfo(BaseModel):
    # executable_path: str = Field(..., description="Path to Python executable")
    # installation_prefix: str = Field(..., description="Python installation prefix")
    implementation: str = Field(
        ..., description="Python implementation (e.g., CPython)"
    )
    is_64bit: bool = Field(..., description="Whether Python is 64-bit")
    compiler: str = Field(..., description="Compiler used to build Python")
    build_flags: List[str] = Field(
        default_factory=list, description="Python build flags"
    )
    # paths: Dict[str, str] = Field(default_factory=dict, description="Important Python paths")


class Environment(BaseModel):
    python_info: PythonInstallInfo
    cuda_info: Optional[CUDAInfo] = None
    devices: List[Device] = Field(default_factory=list)
    packages: List[Package] = Field(default_factory=list)


class Integration(BaseModel):
    pass


class WandbLoggingIntegration(Integration):
    """Configuration for Weights & Biases tracking platform using environment variables."""

    api_key: str = Field(..., env="WANDB_API_KEY")
    username: str = Field(..., env="WANDB_USERNAME")
    project: str = Field(..., env="WANDB_PROJECT")
    job_type: Optional[str] = Field(None, env="WANDB_JOB_TYPE")
    run_group: Optional[str] = Field(None, env="WANDB_RUN_GROUP")
    tags: Optional[str] = Field(None, env="WANDB_TAGS")


class NeptuneLoggingIntegration(Integration):
    """Configuration for Neptune.ai tracking platform using environment variables."""

    api_token: str = Field(..., env="NEPTUNE_API_TOKEN")
    project: str = Field(..., env="NEPTUNE_PROJECT")


class IntegrationDict(BaseModel):
    wandb: Optional[WandbLoggingIntegration] = None
    neptune: Optional[NeptuneLoggingIntegration] = None


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    tenant: Annotated[str, AfterValidator(is_valid_uuid)]
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    #integrations: IntegrationDict = Field(default_factory=IntegrationDict)

class ProjectNameUpdate(BaseModel):
    name: str