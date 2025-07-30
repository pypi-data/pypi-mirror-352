from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from pydantic import BaseModel
from typing import List


class DatasetRef(BaseModel):
    meta: str
    revision: str


class RecipeRevision(FactoryResourceRevision):
    pass


class RecipeMeta(FactoryResourceMeta):
    revisions: List[RecipeRevision] = []


class RecipeInitData(FactoryResourceInitData):

    def create_meta(self, tenant_name, project_name) -> RecipeMeta:
        return RecipeMeta(
            name=self.name, project=project_name, tenant=tenant_name, type="recipe"
        )


class RecipeObject(BaseModel):
    meta: RecipeMeta
    revision: str

    def get_revision(self):
        revisions = self.meta.revisions
        revisions = [revision for revision in revisions if revision.id == self.revision]
        if len(revisions) == 0:
            raise Exception("Revision not found")

        return revisions[0]


class Package(BaseModel):
    name: str
    version: str
    dependencies: List[str]


class PreprocessorCallObject(BaseModel):
    fn_name: str
    packages: List[Package]
