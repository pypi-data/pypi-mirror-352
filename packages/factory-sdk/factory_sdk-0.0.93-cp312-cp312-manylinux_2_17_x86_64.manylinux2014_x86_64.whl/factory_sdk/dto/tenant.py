from pydantic import BaseModel, Field
from uuid import uuid4
from factory_sdk.dto.user import TenantMember, Role
from typing import List
from enum import Enum


class TenantType(str, Enum):
    USER = "user"
    TEAM = "team"


class TenantInit(BaseModel):
    name: str


class TenantWallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant: str = Field()
    balance: int = Field(default=0)


class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    members: List[TenantMember] = Field(min_length=1)
    type: TenantType = Field(default=TenantType.USER)

    def is_owner(self, user_id: str):
        for member in self.members:
            if member.id == user_id and member.role == "owner":
                return True
        return False

    def has_member(self, user_id: str):
        for member in self.members:
            if member.id == user_id:
                return True
        return False

    def add_member(self, user_id: str, role: Role):
        self.members.append(TenantMember(id=user_id, role=role))


class AddMemberRequest(BaseModel):
    username: str
