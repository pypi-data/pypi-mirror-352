# Transaction Builder API

Create and manage transaction builders with full participant and property management capabilities.

---

## Overview

!!! abstract "Transaction Builder Workflow"

    The Transaction Builder API allows you to:

    - **Create** new transaction builders for various types of real estate transactions
    - **Configure** property details, participants, and financial information
    - **Manage** buyers, sellers, agents, and other transaction participants
    - **Submit** completed transactions for processing

---

## Quick Start

=== ":material-rocket-launch: Basic Transaction"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Step 1: Create transaction builder
    response: Dict[str, Any] = client.transaction_builder.create_transaction_builder()
    transaction_id: str = response['id']

    # Step 2: Add participants
    buyer_data: Dict[str, Any] = {
        "type": "BUYER",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com"
    }
    client.transaction_builder.add_buyer(transaction_id, buyer_data)

    # Step 3: Add property information
    location_data: Dict[str, Any] = {
        "address": "123 Main Street",
        "city": "Anytown",
        "state": "CA",
        "zipCode": "90210"
    }
    client.transaction_builder.update_location_info(transaction_id, location_data)

    # Step 4: Submit transaction
    client.transaction_builder.submit_transaction(transaction_id)
    ```

=== ":material-home: Listing Builder"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Create listing builder instead of transaction
    response: Dict[str, Any] = client.transaction_builder.create_transaction_builder(
        builder_type="LISTING"
    )
    listing_id: str = response['id']

    # Configure listing-specific details
    seller_data: Dict[str, Any] = {
        "type": "SELLER",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@email.com"
    }
    client.transaction_builder.add_seller(listing_id, seller_data)
    ```

---

## Core Transaction Management

### Create Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.create_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! example "Create Different Builder Types"

    === "Transaction Builder"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Standard transaction builder
        response: Dict[str, Any] = client.transaction_builder.create_transaction_builder()
        print(f"Transaction ID: {response['id']}")
        ```

    === "Listing Builder"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Listing-specific builder
        response: Dict[str, Any] = client.transaction_builder.create_transaction_builder(
            builder_type="LISTING"
        )
        print(f"Listing ID: {response['id']}")
        ```

### Get Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.get_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! tip "Response Structure"

    The transaction builder response includes:

    - **Basic Information**: ID, type, status, creation date
    - **Participants**: All buyers, sellers, agents, and other participants
    - **Property Details**: Location, pricing, and property information
    - **Financial Data**: Commission splits and payment information

### Submit Transaction

::: rezen.transaction_builder.TransactionBuilderClient.submit_transaction
    options:
      show_source: false
      heading_level: 4

!!! warning "Submission Requirements"

    Before submitting, ensure:

    - [ ] At least one participant is added
    - [ ] Property location is specified
    - [ ] Required financial information is complete
    - [ ] All mandatory fields are populated

### Delete Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.delete_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! danger "Deletion Warning"

    This operation is irreversible. Ensure you have backups of any critical data before deletion.

---

## Participant Management

### Buyers

=== ":material-account-plus: Add Buyer"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_buyer
        options:
          show_source: false
          heading_level: 5

    **Required Buyer Fields:**

    | Field | Type | Description |
    |-------|------|-------------|
    | `type` | `str` | Must be "BUYER" |
    | `first_name` | `str` | Buyer's first name |
    | `last_name` | `str` | Buyer's last name |
    | `email` | `str` | Valid email address |

    **Optional Buyer Fields:**

    | Field | Type | Description |
    |-------|------|-------------|
    | `phone` | `str` | Phone number |
    | `company` | `str` | Company name |
    | `address` | `str` | Mailing address |

    !!! example "Complete Buyer Example"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        buyer_data: Dict[str, Any] = {
            "type": "BUYER",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-123-4567",
            "company": "Doe Enterprises",
            "address": "456 Business Ave, Business City, BC 12345"
        }

        response: Dict[str, Any] = client.transaction_builder.add_buyer(transaction_id, buyer_data)
        ```

### Sellers

=== ":material-account-minus: Add Seller"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_seller
        options:
          show_source: false
          heading_level: 5

    !!! example "Seller Configuration"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        seller_data: Dict[str, Any] = {
            "type": "SELLER",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@email.com",
            "phone": "+1-555-987-6543"
        }

        response: Dict[str, Any] = client.transaction_builder.add_seller(transaction_id, seller_data)
        ```

### Agents & Co-Agents

=== ":material-account-tie: Add Co-Agent"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_co_agent
        options:
          show_source: false
          heading_level: 5

    **Agent Roles:**

    !!! info "Available Agent Roles"

        - `BUYERS_AGENT`: Represents the buyer
        - `SELLERS_AGENT`: Represents the seller
        - `LISTING_AGENT`: Lists the property
        - `DUAL_AGENT`: Represents both parties

    !!! example "Co-Agent Examples"

        === "Buyer's Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            co_agent_data: Dict[str, Any] = {
                "agent_id": "agent-uuid-here",
                "role": "BUYERS_AGENT"
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
            ```

        === "Seller's Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            co_agent_data: Dict[str, Any] = {
                "agent_id": "seller-agent-uuid",
                "role": "SELLERS_AGENT"
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
            ```

### Other Participants

=== ":material-account-multiple: Add Participant"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_participant
        options:
          show_source: false
          heading_level: 5

    **Participant Types:**

    | Type | Description |
    |------|-------------|
    | `INSPECTOR` | Property inspector |
    | `APPRAISER` | Property appraiser |
    | `LENDER` | Mortgage lender |
    | `TITLE_COMPANY` | Title company representative |
    | `ATTORNEY` | Legal counsel |
    | `CONTRACTOR` | Contractor or repair specialist |

    !!! example "Service Provider Examples"

        === "Property Inspector"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            inspector_data: Dict[str, Any] = {
                "type": "INSPECTOR",
                "first_name": "Mike",
                "last_name": "Inspector",
                "company": "Quality Inspections Inc",
                "phone": "+1-555-INSPECT",
                "email": "mike@qualityinspections.com"
            }
            client.transaction_builder.add_participant(transaction_id, inspector_data)
            ```

        === "Mortgage Lender"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            lender_data: Dict[str, Any] = {
                "type": "LENDER",
                "first_name": "Sarah",
                "last_name": "Banker",
                "company": "First National Bank",
                "phone": "+1-555-LOANS",
                "email": "sarah.banker@firstnational.com"
            }
            client.transaction_builder.add_participant(transaction_id, lender_data)
            ```

---

## Property & Location Details

### Location Information

::: rezen.transaction_builder.TransactionBuilderClient.update_location_info
    options:
      show_source: false
      heading_level: 4

!!! example "Property Location Examples"

    === "Residential Property"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        location_data: Dict[str, Any] = {
            "address": "123 Maple Street",
            "city": "Springfield",
            "state": "CA",
            "zipCode": "90210",
            "county": "Los Angeles",
            "unit": "Unit 2A",  # For condos/apartments
            "subdivision": "Maple Grove"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
        ```

    === "Commercial Property"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        location_data: Dict[str, Any] = {
            "address": "456 Business Blvd",
            "city": "Commerce City",
            "state": "TX",
            "zipCode": "75201",
            "county": "Dallas",
            "building_name": "Commerce Center",
            "floor": "15th Floor"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
        ```

### Pricing & Dates

::: rezen.transaction_builder.TransactionBuilderClient.update_price_and_date_info
    options:
      show_source: false
      heading_level: 4

**Key Date Fields:**

| Field | Format | Description |
|-------|--------|-------------|
| `contract_date` | `YYYY-MM-DD` | Date contract was signed |
| `closing_date` | `YYYY-MM-DD` | Expected closing date |
| `inspection_date` | `YYYY-MM-DD` | Property inspection date |
| `appraisal_date` | `YYYY-MM-DD` | Appraisal completion date |

!!! example "Pricing Information"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    price_date_data: Dict[str, Any] = {
        "purchase_price": 750000,
        "earnest_money": 15000,
        "down_payment": 150000,
        "loan_amount": 600000,
        "contract_date": "2024-02-01",
        "closing_date": "2024-03-15",
        "inspection_date": "2024-02-10",
        "appraisal_date": "2024-02-20"
    }

    client.transaction_builder.update_price_and_date_info(
        transaction_id,
        price_date_data
    )
    ```

### Title Information

::: rezen.transaction_builder.TransactionBuilderClient.update_title_info
    options:
      show_source: false
      heading_level: 4

!!! example "Title Company Details"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    title_data: Dict[str, Any] = {
        "title_company": "Premier Title Co",
        "title_contact": "Sarah Johnson",
        "title_phone": "+1-555-789-0123",
        "title_email": "sarah@premiertitle.com",
        "title_address": "789 Title Lane, Title City, TC 54321",
        "policy_number": "PT-2024-001234"
    }

    client.transaction_builder.update_title_info(transaction_id, title_data)
    ```

---

## Financial Management

### Commission Splits

::: rezen.transaction_builder.TransactionBuilderClient.update_commission_splits
    options:
      show_source: false
      heading_level: 4

!!! example "Commission Split Examples"

    === "Equal Split"

        ```python
        from typing import Dict, List, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        commission_data: List[Dict[str, Any]] = [
            {
                "agent_id": "buyer-agent-uuid",
                "split_percentage": 50.0,
                "commission_amount": 15000
            },
            {
                "agent_id": "seller-agent-uuid",
                "split_percentage": 50.0,
                "commission_amount": 15000
            }
        ]

        client.transaction_builder.update_commission_splits(
            transaction_id,
            commission_data
        )
        ```

    === "Unequal Split"

        ```python
        from typing import Dict, List, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        commission_data: List[Dict[str, Any]] = [
            {
                "agent_id": "listing-agent-uuid",
                "split_percentage": 60.0,
                "commission_amount": 18000
            },
            {
                "agent_id": "buyer-agent-uuid",
                "split_percentage": 40.0,
                "commission_amount": 12000
            }
        ]

        client.transaction_builder.update_commission_splits(
            transaction_id,
            commission_data
        )
        ```

### Commission Payers

::: rezen.transaction_builder.TransactionBuilderClient.add_commission_payer
    options:
      show_source: false
      heading_level: 4

**Payer Types:**

| Type | Description |
|------|-------------|
| `SELLER` | Seller pays commission |
| `BUYER` | Buyer pays commission |
| `BOTH` | Split between buyer and seller |

!!! example "Commission Payer Configuration"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    payer_data: Dict[str, Any] = {
        "payer_type": "SELLER",
        "commission_rate": 6.0,  # 6% commission
        "flat_fee": False  # Percentage-based, not flat fee
    }

    client.transaction_builder.add_commission_payer(transaction_id, payer_data)
    ```

---

## Query & Search Operations

### List Transaction Builders

::: rezen.transaction_builder.TransactionBuilderClient.get_transaction_builders
    options:
      show_source: false
      heading_level: 4

!!! example "Advanced Filtering"

    === "Basic Pagination"

        ```python
        builders = client.transaction_builder.get_transaction_builders(
            limit=20,
            from_offset=0
        )

        print(f"Found {len(builders)} transaction builders")
        for builder in builders:
            print(f"ID: {builder['id']}, Status: {builder['status']}")
        ```

    === "User-Specific Search"

        ```python
        # Get builders for specific user
        user_builders = client.transaction_builder.get_transaction_builders(
            limit=50,
            from_offset=0,
            yenta_id="user-uuid-here",
            builder_type="TRANSACTION"
        )
        ```

    === "Listing Builders Only"

        ```python
        # Get only listing builders
        listings = client.transaction_builder.get_transaction_builders(
            limit=25,
            from_offset=0,
            builder_type="LISTING"
        )
        ```

---

## Error Handling

!!! warning "Common Validation Errors"

    **Missing Required Fields:**
    ```python
    from rezen.exceptions import ValidationError

    try:
        # Missing required email field
        buyer_data = {
            "type": "BUYER",
            "first_name": "John",
            "last_name": "Doe"
            # email field missing!
        }
        client.transaction_builder.add_buyer(transaction_id, buyer_data)
    except ValidationError as e:
        print(f"Validation failed: {e.invalid_fields}")
    ```

!!! info "Best Practices"

    - **Validate Data**: Check required fields before API calls
    - **Handle Duplicates**: Check for existing participants before adding
    - **Save Progress**: Regularly save transaction state
    - **Error Recovery**: Implement retry logic for network issues

---

## Complete Workflow Example

!!! example "End-to-End Transaction Creation"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError
    import logging

    def create_complete_transaction():
        """Create a complete transaction with all participants and details."""

        try:
            client = RezenClient()

            # Step 1: Create transaction builder
            print("Creating transaction builder...")
            response = client.transaction_builder.create_transaction_builder()
            transaction_id = response['id']
            print(f"✅ Created transaction: {transaction_id}")

            # Step 2: Add buyer
            print("Adding buyer...")
            buyer_data = {
                "type": "BUYER",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-123-4567"
            }
            client.transaction_builder.add_buyer(transaction_id, buyer_data)
            print("✅ Added buyer")

            # Step 3: Add seller
            print("Adding seller...")
            seller_data = {
                "type": "SELLER",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@email.com",
                "phone": "+1-555-987-6543"
            }
            client.transaction_builder.add_seller(transaction_id, seller_data)
            print("✅ Added seller")

            # Step 4: Add property location
            print("Setting property location...")
            location_data = {
                "address": "123 Dream House Lane",
                "city": "Paradise",
                "state": "CA",
                "zipCode": "90210",
                "county": "Los Angeles"
            }
            client.transaction_builder.update_location_info(transaction_id, location_data)
            print("✅ Set property location")

            # Step 5: Set pricing and dates
            print("Setting pricing and dates...")
            price_data = {
                "purchase_price": 850000,
                "earnest_money": 17000,
                "contract_date": "2024-02-01",
                "closing_date": "2024-03-15"
            }
            client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
            print("✅ Set pricing and dates")

            # Step 6: Add service providers
            print("Adding service providers...")
            inspector_data = {
                "type": "INSPECTOR",
                "first_name": "Mike",
                "last_name": "Inspector",
                "company": "Quality Inspections Inc",
                "phone": "+1-555-INSPECT"
            }
            client.transaction_builder.add_participant(transaction_id, inspector_data)
            print("✅ Added inspector")

            # Step 7: Submit transaction
            print("Submitting transaction...")
            submit_response = client.transaction_builder.submit_transaction(transaction_id)
            print("✅ Transaction submitted successfully!")

            return {
                "success": True,
                "transaction_id": transaction_id,
                "submit_response": submit_response
            }

        except RezenError as e:
            logging.error(f"ReZEN API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": transaction_id if 'transaction_id' in locals() else None
            }
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Run the example
    result = create_complete_transaction()
    if result["success"]:
        print(f"🎉 Transaction {result['transaction_id']} created successfully!")
    else:
        print(f"❌ Failed to create transaction: {result['error']}")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [:material-handshake: **Transactions API**](transactions.md)

    Work with live transactions and manage ongoing deals

-   [:material-account-group: **Teams API**](teams.md)

    Search and manage team information

-   [:material-account-tie: **Agents API**](agents.md)

    Find and manage agent information

-   [:material-file-document: **Examples**](../examples.md)

    See more practical usage examples

</div>
