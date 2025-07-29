```bash
pip install rezen
```

```python
from rezen import RezenClient

# Initialize main client
client = RezenClient()

# Search for active teams
teams = client.teams.search_teams(status="ACTIVE")

# Search for agents in California
agents = client.agents.search_active_agents(state_or_province=["CALIFORNIA"])

# Create a transaction
response = client.transaction_builder.create_transaction_builder()
transaction_id = response['id']

# Add property details
client.transaction_builder.update_location_info(transaction_id, {
    "address": "123 Main Street",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "90210"
})

# Use Directory API for vendor management through main client
vendors = client.directory.search_vendors(
    page_number=0,
    page_size=20,
    roles=["TITLE_ESCROW", "LENDER"]
)
