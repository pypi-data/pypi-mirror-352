from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, Dict, List
from abc import abstractmethod
from uuid import UUID
from pydantic import AfterValidator
from typing import Annotated
from typing import Any


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns uuid_to_test is a valid UUID.
    -------

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    Correct
    >>> is_valid_uuid('c9bf9e58')
    Exception: Invalid UUID: c9bf9e58
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        raise ValueError(f"Invalid UUID: {uuid_to_test}")
    if not str(uuid_obj) == uuid_to_test:
        raise ValueError(f"Invalid UUID: {uuid_to_test}")
    return uuid_to_test


def is_valid_uuid_optional(uuid_to_test, version=4):
    if uuid_to_test is None:
        return None
    return is_valid_uuid(uuid_to_test, version)


class FactoryMetaState(str, Enum):
    INITIALIZED = "initialized"
    READY = "ready"
    FAILED = "failed"
    STALE = "stale"


class FactoryRevisionState(str, Enum):
    INITIALIZED = "initialized"
    READY = "ready"
    FAILED = "failed"
    STALE = "stale"


class FactoryResourceFileState(str, Enum):
    INITIALIZED = "initialized"
    UPLOADED = "uploaded"
    ABORTED = "aborted"


class FactoryResourceObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    updated_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    ready_at: Optional[float] = Field(default=None)
    failed_at: Optional[float] = Field(default=None)
    stale_at: Optional[float] = Field(default=None)


class FactoryResourceRevisionFile(BaseModel):
    id: Annotated[str, AfterValidator(is_valid_uuid)] = Field(
        default_factory=lambda: str(uuid4())
    )
    path: str
    upload_init_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    upload_expires_at: float
    upload_finished_at: Optional[float] = Field(default=None)
    upload_aborted_at: Optional[float] = Field(default=None)
    # 5GB
    max_upload_size: int = Field(default=5 * 1024 * 1024 * 1024)
    size: Optional[int] = Field(default=None)
    state: FactoryResourceFileState = Field(
        default=FactoryResourceFileState.INITIALIZED
    )


class FactoryResourceRef(BaseModel):
    id: Annotated[str, AfterValidator(is_valid_uuid)]
    revision: Annotated[str, AfterValidator(is_valid_uuid)]
    type: str


class NamedFactoryResourceRef(FactoryResourceRef):
    name: str


class FactoryResourceRevision(FactoryResourceObject):
    state: FactoryRevisionState = Field(default=FactoryRevisionState.INITIALIZED)
    fingerprints: Dict[str, str] = Field(default={})
    error_message: Optional[str] = Field(default=None)
    files: List[FactoryResourceRevisionFile] = Field(default=[])
    locked: bool = Field(default=False)
    dependencies: List[FactoryResourceRef] = Field(default=[])


class FactoryResourceMeta(FactoryResourceObject):
    name: str
    state: FactoryMetaState = Field(default=FactoryMetaState.INITIALIZED)
    last_revision: Annotated[Optional[str], AfterValidator(is_valid_uuid_optional)] = (
        Field(default=None)
    )
    project: Annotated[Optional[str], AfterValidator(is_valid_uuid_optional)] = Field(
        default=None
    )
    tenant: Annotated[str, AfterValidator(is_valid_uuid)]
    revisions: List[FactoryResourceRevision] = Field(default=[])
    type: str


class FactoryResourceInitData(BaseModel):
    name: str

    @abstractmethod
    def create_meta(
        self, tenant_name: str, project_name: Optional[str] = None
    ) -> FactoryResourceMeta:
        raise NotImplementedError()


class FactoryRevisionRef(BaseModel):
    object_id: Annotated[str, AfterValidator(is_valid_uuid)]
    revision_id: Annotated[str, AfterValidator(is_valid_uuid)]


class FileUploadInit(BaseModel):
    size: int
    hash: str


class FileUploadRef(BaseModel):
    upload_id: str
    upload_url: str
    upload_fields: Dict[str, Any]


class FileDownloadRef(BaseModel):
    download_url: str
    path: str


class FileDownloadRefs(BaseModel):
    files: List[FileDownloadRef]


class CompleteUploadRequest(BaseModel):
    fingerprint: str
