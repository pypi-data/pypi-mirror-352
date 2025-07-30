from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional


class PaymentType(str, Enum):
    TRIAL = "trial"
    PAYED = "billed"


class PaymentCurrency(str, Enum):
    EUR = "EUR"


class PaymentStatus(str, Enum):
    OPEN = "open"
    CANCELED = "canceled"
    PENDING = "pending"
    AUTHORIZED = "authorized"
    EXPIRED = "expired"
    FAILED = "failed"
    PAID = "paid"
    CREDITED = "credited"


class PaymentInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user: str = Field()
    tenant: str = Field()
    currency: PaymentCurrency = Field()
    value: float = Field()
    checkout_url: str = Field()
    status: PaymentStatus = Field(default=PaymentStatus.OPEN)
    created_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    updated_at: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    type: PaymentType = Field(default=PaymentType.PAYED)
    expires_at: Optional[str] = Field(default=None)

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()


class InitPayment(BaseModel):
    currency: PaymentCurrency = Field(default=PaymentCurrency.EUR)
    value: float = Field(gt=0)
