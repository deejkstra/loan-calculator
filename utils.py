from models import Loan, LoanSchedule


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
            month=m + 1,
            interest_payment=round(interest_payment, 2),
            principal_payment=round(principal_payment, 2),
            remaining_balance=round(amount, 2),
        )
        loan_schedules.append(schedule)

    return loan_schedules
