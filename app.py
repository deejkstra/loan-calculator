from typing import Optional, List

import decimal
from fastapi import FastAPI
from pydantic import condecimal
from sqlmodel import Field, Session, SQLModel, create_engine, select


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
    interest_payment: condecimal(max_digits=16, decimal_places=2) = Field(default=0)
    principal_payment: condecimal(max_digits=16, decimal_places=2) = Field(default=0)
    remaining_balance: condecimal(max_digits=16, decimal_places=2) = Field(default=0)


class LoanSummary(SQLModel):
    principal_payment: condecimal(max_digits=16, decimal_places=2) = Field(default=0)
    total_principal_payment: condecimal(max_digits=16, decimal_places=2) = Field(default=0)
    total_interest_payment: condecimal(max_digits=16, decimal_places=2) = Field(default=0)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/users', response_model=User)
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.get('/users', response_model=List[User])
def get_users():
    with Session(engine) as session:
        return session.exec(select(User)).all()


@app.post('/loans', response_model=Loan)
def create_loan(loan: Loan):
    with Session(engine) as session:
        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan


@app.get('/loans/{user_id}', response_model=List[Loan])
def get_loan(user_id: int):
    with Session(engine) as session:
        return session.exec(select(Loan).where(Loan.user_id == user_id)).all()


def _get_loan_schedule(loan: Loan):
    # https://www.thebalancemoney.com/loan-payment-calculations-315564
    def _get_monthly_payment(a, r, n):
        return a / ((((1 + r)**n) - 1) / (r * (1 + r)**n))

    # calculate loan schedule
    amortized_monthly_payment = _get_monthly_payment(
        a=loan.amount, 
        r=loan.annual_interest_rate / 12, 
        n=loan.monthly_payments)
    amount = loan.amount
    loan_schedules = []
    for m in range(loan.monthly_payments):
        interest_payment = amount * (loan.annual_interest_rate / 12)
        principal_payment = amortized_monthly_payment - interest_payment
        amount -= principal_payment
        schedule = LoanSchedule(
            month = m + 1,
            interest_payment = round(interest_payment, 2),
            principal_payment = round(principal_payment, 2),
            remaining_balance = round(amount, 2),
        )
        loan_schedules.append(schedule)
        
    return loan_schedules

@app.get('/loan_schedule/{loan_id}', response_model=List[LoanSchedule])
def get_loan_schedule(loan_id: int):
    with Session(engine) as session:
        loan = session.get(Loan, loan_id)
        return _get_loan_schedule(loan)
        

@app.get('/loan_summary/{loan_id}/{month}', response_model=LoanSummary)
def get_loan_summary(loan_id: int, month: int):
    with Session(engine) as session:
        loan = session.get(Loan, loan_id)
        schedule = _get_loan_schedule(loan)
        
        principal_payment = decimal.Decimal(0.0)
        total_principal_payment = decimal.Decimal(0.0)
        total_interest_payment = decimal.Decimal(0.0)

        # note - only doing it this way because order is not guaranteed
        for p in schedule:
            if p.month == month:
                principal_payment = p.principal_payment

            if p.month <= month:
                total_principal_payment += p.principal_payment
                total_interest_payment += p.interest_payment

        return LoanSummary(
            principal_payment=principal_payment,
            total_principal_payment=total_principal_payment,
            total_interest_payment=total_interest_payment,
        )

