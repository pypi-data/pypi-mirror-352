from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum
from typing import List, Optional, Dict
import os


class Role(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


class TenantMember(BaseModel):
    id: str = Field(description="User ID")
    role: Role = Field(description="User role")

class EmailChangeRequest(BaseModel):
    """
    Request schema for initiating an email change process.
    """
    new_email: str

class EmailChangeVerify(BaseModel):
    """
    Schema for verifying and confirming an email change.
    """
    token: str


class UserInfo(BaseModel):
    id: str = Field(description="User ID", default_factory=lambda: str(uuid4()))
    username: str = Field(description="Username")
    firstname: str = Field(description="First Name")
    lastname: str = Field(description="Last Name")
    email: str = Field(description="Email")
    tenant: str = Field(description="Personal Tenant ID")


class LoginData(BaseModel):
    username: str = Field(description="Username")
    password: str = Field(description="Password")


class ResetPasswordData(BaseModel):
    email: str = Field(description="Email")


class FinishResetPasswordData(BaseModel):
    token: str = Field(description="Reset token")
    password: str = Field(description="New password")


class RegisterData(BaseModel):
    firstname: str = Field(description="First Name", min_length=1)
    lastname: str = Field(description="Last Name", min_length=1)
    email: str = Field(description="Email", min_length=1)


class FinishRegistrationData(BaseModel):
    token: str = Field(description="Verification token")
    username: str = Field(description="Username")
    password: str = Field(description="Password")
    questions: Dict[str, str] = Field(description="Background questions")


class SubscriptionLimits(BaseModel):
    max_storage: Optional[float] = Field(description="Max storage in GB")
    max_active_deployments: Optional[int] = Field(description="Max active deployments")
    max_tenants: Optional[int] = Field(description="Max tenants")


class SubscriptionUpdate(BaseModel):
    type: str = Field(description="Subscription type")
    return_to_tenant: Optional[str] = Field(description="Tenant ID to return to")


class Subscription(BaseModel):
    subscription_type: str = Field(description="Subscription type")
    deployment_type: str = Field(description="Deployment type")
    limits: SubscriptionLimits = Field(description="Subscription limits")
    update: Optional[SubscriptionUpdate] = Field(
        description="Subscription update (if any)"
    )


class TenantUsage(BaseModel):
    deployments: int = Field(description="Active deployments")
    storage: float = Field(description="Storage in GB")
    id: str = Field(description="Tenant ID")
    name: str = Field(description="Tenant name")


class AggregatedUsage(BaseModel):
    deployments: int = Field(description="Active deployments")
    storage: float = Field(description="Storage in GB")
    tenants: int = Field(description="Number of tenants")


class Usage(BaseModel):
    tenants: List[TenantUsage] = Field(description="Tenant usage")
    total: AggregatedUsage = Field(description="Total usage")

class UsernameUpdate(BaseModel):
    username: str

class SSOProvider(str, Enum):
    GOOGLE = "google"
    KEYCLOAK = "keycloak"

class OIDCProvider(BaseModel):
    name: str = Field(description="Provider name")
    client_id: str = Field(description="OAuth/OIDC client ID")
    client_secret: Optional[str] = Field(default=None, description="OAuth/OIDC client secret")
    discovery_url: str = Field(description="OIDC discovery URL (e.g. https://accounts.google.com/.well-known/openid-configuration)")
    scopes: List[str] = Field(default=["openid", "email", "profile"], description="OAuth scopes to request")
    icon: Optional[str] = Field(default=None, description="Provider icon name (for UI)")

class SSOLoginData(BaseModel):
    """Data for SSO login"""
    provider_name: str = Field(description="Name of the SSO provider")
    token: str = Field(description="Token from the SSO provider")
    token_type: str = Field(description="Token type (authorization_code, access_token, id_token)")

class SSOCallbackData(BaseModel):
    """Data for handling SSO callback"""
    provider_name: str = Field(description="Name of the SSO provider")
    code: str = Field(description="Authorization code from the provider")
    redirect_uri: str = Field(description="Redirect URI used in the authorization request")

class SSOConfig(BaseModel):
    providers: Dict[str, OIDCProvider] = Field(
        default_factory=dict,
        description="Dictionary of configured SSO providers"
    )

    @classmethod
    def from_env(cls, settings) -> "SSOConfig":
        """Create SSO config from environment variables with format:
        SSO_PROVIDER_{NAME}_{FIELD}=value"""
        providers = {}
        provider_secrets = {}
        
        # First pass: collect all secrets to validate providers
        for key, value in os.environ.items():
            if key.startswith("SSO_PROVIDER_") and value:
                _, _, provider_name, field = key.lower().split("_", 3)
                if field == "client_secret":
                    provider_secrets[provider_name] = value

        # Second pass: process providers, skipping those with test secrets
        for key, value in os.environ.items():
            if key.startswith("SSO_PROVIDER_") and value:
                # Parse provider name and field from key
                _, _, provider_name, field = key.lower().split("_", 3)
                
                # Skip this provider if it has a test secret
                if provider_name in provider_secrets and provider_secrets[provider_name].startswith("your-"):
                    continue
                
                # Initialize provider if not exists
                if provider_name not in providers:
                    providers[provider_name] = OIDCProvider(
                        name="",
                        client_id="",
                        discovery_url=""
                    )
                
                # Map fields to provider attributes
                provider = providers[provider_name]
                if field == "name":
                    provider.name = value
                elif field == "client_id":
                    provider.client_id = value
                elif field == "client_secret":
                    provider.client_secret = value
                elif field == "discovery_url":
                    provider.discovery_url = value
                elif field == "icon":
                    provider.icon = value

        # Remove any providers that don't have required fields
        providers = {
            name: provider 
            for name, provider in providers.items() 
            if provider.client_id and provider.discovery_url
        }
                
        return cls(providers=providers)
