from typing import Literal

from pydantic import BaseModel, EmailStr


class Payer(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    identity: dict


class Transaction(BaseModel):
    reference: str
    type: Literal["PAY-IN", "PAYOUT"]
    amount: str
    description: str
    transaction_date: str
    payer: Payer
