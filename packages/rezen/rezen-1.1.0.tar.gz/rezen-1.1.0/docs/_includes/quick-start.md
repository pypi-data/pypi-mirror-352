```bash
pip install rezen
```

```python
from rezen import RezenClient

# Initialize client
client = RezenClient()

# Search for teams
teams = client.teams.search_teams(status="ACTIVE")

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