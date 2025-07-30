from pydantic import BaseModel,Field
from typing import Optional
from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)

class EvalArgs(BaseModel):
    batch_size: int = 8
    accumulation_steps: int = 128
    dtype: str = Field("fp16", description="The dtype to use for training")
    attention_implementation: str = Field(
        "fa2", description="The attention implementation to use for training"
    )
    num_beams: int=1
    max_samples: Optional[int]=None
    quantization_bits: Optional[int] = Field(
        4, description="The number of bits to use for quantization"
    )
    max_new_tokens: int = 1024

class EvaluationMeta(FactoryResourceMeta):
    pass

class EvaluationInitData(FactoryResourceInitData):
    def create_meta(self, tenant_name, project_name) -> EvaluationMeta:
        return EvaluationMeta(
            name=self.name, project=project_name, tenant=tenant_name, type="evaluation"
        )
    
class EvaluationRevision(FactoryResourceRevision):
    pass



class EvaluationObject(BaseModel):
    meta: EvaluationMeta
    revision: str
