from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class Shard(BaseModel):
    id: str
    num_samples: int


class Split(BaseModel):
    name: str
    num_samples: int
    features: Dict
    datasets_version: str
    shards: List[Shard]


class DatasetMeta(FactoryResourceMeta):
    pass


class DatasetInitData(FactoryResourceInitData):
    def create_meta(self, tenant_name, project_name) -> DatasetMeta:
        return DatasetMeta(
            name=self.name, project=project_name, tenant=tenant_name, type="dataset"
        )


class DatasetRevision(FactoryResourceRevision):
    pass


class DatasetObject(BaseModel):
    meta: DatasetMeta
    revision: str


class OODScores(BaseModel):
    train: List[float]
    test: List[float]


class OODConfig(BaseModel):
    num_neighbours: int
    max_samples: int
    text_embedding_model: str
    text_embedding_prefix: str
    image_embedding_model: Optional[str]


class ReducedEmbeddings(BaseModel):
    train2d: Any
    test2d: Any


class Embeddings(BaseModel):
    train: Any
    test: Any


class DatasetOODData(BaseModel):
    config: OODConfig
    distances: OODScores

    reduced_embeddings: Dict[str, ReducedEmbeddings]
    embeddings: Dict[str, Embeddings]
