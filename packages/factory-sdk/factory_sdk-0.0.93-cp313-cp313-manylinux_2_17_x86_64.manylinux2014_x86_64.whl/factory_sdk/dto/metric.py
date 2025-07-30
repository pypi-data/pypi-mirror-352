from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from pydantic import BaseModel


class MetricMeta(FactoryResourceMeta):
    pass


class MetricInitData(FactoryResourceInitData):
    def create_meta(self, tenant_name, project_name) -> MetricMeta:
        return MetricMeta(name=self.name, project=project_name, tenant=tenant_name)


class MetricRevision(FactoryResourceRevision):
    pass


class MetricObject(BaseModel):
    meta: MetricMeta
    revision: MetricRevision


class MetricCallObject(BaseModel):
    callable: str


class MetricCode(BaseModel):
    code: str
    fn_name: str
