# Transactions API

Work with live transactions, manage participants, and handle financial operations.

---

## Overview

!!! abstract "Transactions API Features"

    - **Transaction Management**: Get and update live transactions
    - **Participant Management**: Add and modify transaction participants
    - **Financial Operations**: Process payments and commission splits
    - **Document Management**: Generate reports and handle transaction documents

---

## Quick Start

```python
from rezen import RezenClient

client = RezenClient()

# Get transaction details
transaction = client.transactions.get_transaction("tx-12345")

# Add participant to existing transaction
participant = {
    "type": "LENDER",
    "first_name": "Bank",
    "last_name": "Officer",
    "company": "First National Bank"
}
client.transactions.create_participant(transaction_id, participant)
```

---

## Core Methods

### Transaction Operations

::: rezen.transactions.TransactionsClient.get_transaction
    options:
      show_source: false
      heading_level: 4

### Participant Management

::: rezen.transactions.TransactionsClient.create_participant
    options:
      show_source: false
      heading_level: 4

### Financial Operations

::: rezen.transactions.TransactionsClient.get_payment_info
    options:
      show_source: false
      heading_level: 4

::: rezen.transactions.TransactionsClient.get_money_transfers
    options:
      show_source: false
      heading_level: 4

### Document Operations

::: rezen.transactions.TransactionsClient.get_transaction_summary_pdf
    options:
      show_source: false
      heading_level: 4

---

## Usage Examples

!!! example "Transaction Management"

    === "Get Transaction"

        ```python
        transaction = client.transactions.get_transaction("tx-12345")
        print(f"Status: {transaction['status']}")
        print(f"Property: {transaction['property']['address']}")
        ```

    === "Add Participant"

        ```python
        lender = {
            "type": "LENDER",
            "first_name": "Sarah",
            "last_name": "Banker",
            "company": "Community Bank",
            "email": "sarah@communitybank.com"
        }

        response = client.transactions.create_participant(
            transaction_id,
            lender
        )
        ```

    === "Get Payment Info"

        ```python
        # Get payment information for an agent
        payment_info = client.transactions.get_payment_info(
            transaction_id,
            agent_id
        )

        print(f"Payment amount: {payment_info['amount']}")
        print(f"Payment status: {payment_info['status']}")
        ```

---

## Document Management

!!! info "Document Types"

    Available document operations include:

    - **Summary PDFs**: Generate transaction summary reports
    - **Document Lists**: Get all transaction-related documents
    - **Status Reports**: Track transaction progress

!!! example "Document Operations"

    ```python
    # Generate summary PDF
    pdf_data = client.transactions.get_transaction_summary_pdf(transaction_id)

    # Get money transfers
    transfers = client.transactions.get_money_transfers(transaction_id)
    for transfer in transfers:
        print(f"Transfer: {transfer['amount']} - Status: {transfer['status']}")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [:material-hammer-wrench: **Transaction Builder**](transaction-builder.md)

    Create new transactions from scratch

-   [:material-account-tie: **Agents API**](agents.md)

    Find agents to add to transactions

-   [:material-alert-circle: **Exceptions**](exceptions.md)

    Handle transaction-related errors

</div>
