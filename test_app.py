from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test():
    # test create user
    create_user_response = client.post('/users', json={'name': 'testuser'})
    assert create_user_response.status_code == 200

    # test create loan
    user_id = create_user_response.json()['id']
    create_loan_response = client.post('/loans', json={
        "user_id": user_id,
        "amount": 500_000,
        "annual_interest_rate": 0.06,
        "monthly_payments": 360
    })
    assert create_loan_response.status_code == 200

    # test get loans
    get_loans_response = client.get('/loans/%d' % user_id)
    assert get_loans_response.status_code == 200
    assert len(get_loans_response.json()) == 1

    # test loan schedule
    loan_id = get_loans_response.json()[0]['id']
    loan_schedule_response = client.get('/loan_schedule/%d' % loan_id)
    assert loan_schedule_response.status_code == 200

    loan_schedule = loan_schedule_response.json()
    assert len(loan_schedule) == 360
    assert loan_schedule[-1] == {
        "month": 360,
        "interest_payment": 14.91,
        "principal_payment": 2982.84,
        "remaining_balance": 0
    }

    # test loan summary
    month = 360
    loan_summary_response = client.get(
        '/loan_summary/%d/%d' % (loan_id, month))
    assert loan_summary_response.status_code == 200
    assert loan_summary_response.json() == {
        "principal_payment": 2982.84,
        "total_principal_payment": 499999.93,
        "total_interest_payment": 579190.97
    }

    # test create another user
    create_user2_response = client.post('/users', json={'name': 'testuser2'})
    assert create_user2_response.status_code == 200

    user2_id = create_user2_response.json()['id']

    # test loan share
    loan_share_response = client.post('/loan_share', json={
        "source_user_id": user_id,
        "target_user_id": user2_id,
        "loan_id": loan_id
    })
    assert loan_share_response.status_code == 200

    loan = loan_share_response.json()
    assert loan['user_id'] == user2_id
