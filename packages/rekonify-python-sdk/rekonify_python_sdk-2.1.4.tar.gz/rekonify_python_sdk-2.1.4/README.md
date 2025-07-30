# 🔁 Rekonify Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/rekonify?color=blue)](https://pypi.org/project/rekonify-python-sdk/)
[![License](https://img.shields.io/pypi/l/rekonify?color=green)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/rekonify)](https://pypi.org/project/rekonify-python-sdk/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/rekonify/rekonify-python-sdk/tests.yml?branch=main)](https://github.com/Frndz-org/rekonify-python-sdk/actions)
[![Downloads](https://static.pepy.tech/personalized-badge/rekonify?period=month&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/rekonify)

**Rekonify Python SDK** is the official Python client for interacting with the [Rekonify API](https://rekonify.com) — a
platform that automates financial data ingestion, reconciliation, and rule-based matching across diverse systems.

This SDK provides both **synchronous** and **asynchronous** interfaces for ingesting transactions, identifying
customers, and managing reconciliation workflows.

---

## 🚀 Features

- 🔐 API key authentication
- 🔁 Transaction ingestion (pay-in / payout)
- ⚖️ Reconciliation rule management
- ⚡ Sync and async support
- 🧩 Easy to integrate into any Python app or workflow

---

## 📦 Installation

```bash
pip install rekonify-python-sdk9
```

---

## Usage

```python
from rekonify import RekonifyClient

from rekonify.models import Payer, Transaction

client = RekonifyClient(api_key="your_api_key", app_key="your_app_key")

payer: Payer = Payer(
    first_name='John',
    last_name='Doe',
    email='johndoe@example.com',
    phone_number='0231112312',
    identity={
        'external_id': 'LT-123123'  # Identifier
    }
)

payload: Transaction = Transaction(
    type="PAY-IN",  # PAY-IN or PAYOUT
    reference="REF-123131",
    amount='2.00',
    description='Payments for order #041312',
    transaction_date='2025-05-26T15:00:00',
    payer=payer
)

res = client.post_transaction(payload)

print(res)
```
