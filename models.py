from typing import Optional
from pydantic import condecimal
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    amount: int
    annual_interest_rate: float
    monthly_payments: int


class LoanSchedule(SQLModel):
    month: int
    interest_payment: condecimal(
        max_digits=16, decimal_places=2) = Field(default=0)
    principal_payment: condecimal(
        max_digits=16, decimal_places=2) = Field(default=0)
    remaining_balance: condecimal(
        max_digits=16, decimal_places=2) = Field(default=0)


class LoanSummary(SQLModel):
    principal_payment: condecimal(
        max_digits=16, decimal_places=2) = Field(default=0)
    total_principal_payment: condecimal(
        max_digits=16, decimal_places=2) = Field(default=0)
    total_interest_payment: condecimal(
        max_digits=16, decimal_places=2) = Field(default=0)
