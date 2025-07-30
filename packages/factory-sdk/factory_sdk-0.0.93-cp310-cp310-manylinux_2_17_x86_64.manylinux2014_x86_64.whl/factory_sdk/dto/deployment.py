from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import Field
from factory_sdk.fast.deployment.metrics.parser import VLLMStats

class DeploymentArgs(BaseModel):
    """Arguments for vLLM engine."""
    port: Optional[int] = 9000
    quantization_bits: Optional[int] = 4
    dtype: Optional[str] = "auto"
    max_seq_len_to_capture: Optional[int] = 1024
    max_seq_len: Optional[int] = 1024
    max_batched_tokens: Optional[int] = 4096
    max_memory_utilization: Optional[float] = 0.8
    swap_space: int = 4
    # Add field for arbitrary vLLM arguments
    vllm_args: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DeploymentMetrics(BaseModel):
    created_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    updated_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    data: VLLMStats

class DeploymentAnalytics(BaseModel):
    created_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    updated_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    shift_detection: Dict[str,Any]


class Deployment(BaseModel):
    id: str
    created_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    updated_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    name: str
    tenant: str
    project: str

    metrics:Dict[str,DeploymentMetrics] = Field(default_factory=dict)
    analytics:Dict[str,DeploymentAnalytics] = Field(default_factory=dict)

class DeploymentInit(BaseModel):
    name: str

    # -------------------------------------------------------------------
# Additional DTOs for updates
# -------------------------------------------------------------------
class DeploymentUpdate(BaseModel):
    name: Optional[str] = None



class DeploymentCombinedUpdate(BaseModel):
    metrics: Optional[VLLMStats] = None
    shift_detection: Optional[Dict[str, Dict[str, Any]]] = None
    deployment_structure: Optional[List[Dict[str, Any]]] = None

class KeystoneDeploymentUpdate(BaseModel):
    id:str
    tenant:str
    project:str
    data:DeploymentCombinedUpdate


class DeploymentMetricsUpdate(BaseModel):
    data: VLLMStats


class DeploymentAnalyticsUpdate(BaseModel):
    shift_detection: Dict[str, Any]