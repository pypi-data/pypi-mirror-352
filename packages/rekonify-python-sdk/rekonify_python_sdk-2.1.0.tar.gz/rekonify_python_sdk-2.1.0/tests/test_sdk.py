from unittest.mock import patch

import pytest

from rekonify import RekonifyClient


@pytest.fixture
def client():
    return RekonifyClient(api_key='wH9tzaZH.V1dHWf90rZBNdeoQrj0sGwJRPEeCNDOfB8ZjKMlMGHE',
                          app_key='c5kusnhKRsW4CmziaufoTlqMQw8Cq3AtuIjGVur60BA')


@patch('requests.post')
def test_post_transaction(mock_post, client):
    mock_post.return_value.status_code = 202
    mock_post.return_value.json.return_value = {'details': 'Transaction Accepted for Recon'}

    from rekonify.models import Payer, Transaction
    payer: Payer = Payer(
        first_name='Jason',
        last_name='Bourne',
        email='threadstone@bourne.com',
        phone_number='0208365428',
        identity={
            'external_id': 'LT-123123'
        }
    )
    payload: Transaction = Transaction(
        type="PAY-IN",
        reference="REF-123131",
        amount='2.00',
        description='Payments for order #041312',
        transaction_date='2025-05-26T15:00:00',
        payer=payer
    )

    res = client.post_transaction(payload)
    assert res['detail'] == 'Transaction Accepted for Recon'


@patch('requests.post')
def test_post_bulk_transaction(mock_post, client):
    mock_post.return_value.status_code = 202
    mock_post.return_value.json.return_value = {'details': 'Accepted for processing'}

    from rekonify.models import Payer, Transaction
    payer: Payer = Payer(
        first_name='Jason',
        last_name='Bourne',
        email='threadstone@bourne.com',
        phone_number='0208365428',
        identity={
            'external_id': 'LT-123123'
        }
    )
    payload: Transaction = Transaction(
        type="PAY-IN",
        reference="REF-123131",
        amount='2.00',
        description='Payments for order #041312',
        transaction_date='2025-05-26T15:00:00',
        payer=payer
    )

    res = client.post_bulk_transactions([payload])
    assert res['detail'] == 'Accepted for processing'
