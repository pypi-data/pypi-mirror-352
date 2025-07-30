from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from pydantic import BaseModel
from typing import List


class PreprocessorMeta(FactoryResourceMeta):
    pass


class PreprocessorInitData(FactoryResourceInitData):

    def create_meta(self, tenant_name, project_name) -> PreprocessorMeta:
        return PreprocessorMeta(
            name=self.name,
            project=project_name,
            tenant=tenant_name,
            type="preprocessor",
        )


class PreprocessorRevision(FactoryResourceRevision):
    pass


class PreprocessorObject(BaseModel):
    meta: PreprocessorMeta
    revision: PreprocessorRevision


class Package(BaseModel):
    name: str
    version: str
    dependencies: List[str]


class PreprocessorCallObject(BaseModel):
    fn_name: str
    packages: List[Package]


class PreprocessorCode(BaseModel):
    code: str
    fn_name: str
