from typing import List

import decimal
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, select, create_engine
from models import User, Loan, LoanSchedule, LoanSummary, Share
from utils import _get_loan_schedule


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


@app.post('/loan_share', response_model=Loan)
def share_loan(data: Share):
    with Session(engine) as session:
        loan = session.get(Loan, data.loan_id)
        if not loan.user_id == data.source_user_id:
            raise HTTPException(status_code=404, detail="Item not found")
        loan.user_id = data.target_user_id
        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan
