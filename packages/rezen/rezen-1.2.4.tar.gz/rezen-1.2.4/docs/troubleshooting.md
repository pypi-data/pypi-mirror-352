# Troubleshooting Guide

Common issues, solutions, and debugging techniques for the ReZEN Python API client.

## 📋 Table of Contents

- [Authentication Issues](#authentication-issues)
- [Connection Problems](#connection-problems)
- [API Errors](#api-errors)
- [Data Validation Issues](#data-validation-issues)
- [Performance Problems](#performance-problems)
- [Common Error Messages](#common-error-messages)
- [Debugging Techniques](#debugging-techniques)
- [Environment Issues](#environment-issues)

---

## Authentication Issues

### Invalid API Key

**Symptoms:**
- `AuthenticationError: Invalid API key`
- 401 Unauthorized responses
- "Authentication failed" messages

**Solutions:**

```python
import os
from rezen import RezenClient
from rezen.exceptions import AuthenticationError

# 1. Verify API key is correct
api_key = os.getenv('REZEN_API_KEY')
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'NOT SET'}")

# 2. Test with explicit API key
try:
    client = RezenClient(api_key="your_actual_api_key_here")
    teams = client.teams.search_teams(page_size=1)
    print("✅ API key is valid")
except AuthenticationError as e:
    print(f"❌ API key invalid: {e}")
```

**Common Causes:**
- API key not set in environment variables
- Wrong API key (typos, old keys)
- API key revoked or expired
- Using staging key with production API or vice versa

### Environment Variable Not Found

**Error:** `REZEN_API_KEY environment variable not set`

**Solutions:**

```bash
# Check if environment variable is set
echo $REZEN_API_KEY

# Set environment variable (Linux/macOS)
export REZEN_API_KEY="your_api_key_here"

# Set environment variable (Windows)
set REZEN_API_KEY=your_api_key_here
```

**Python verification:**
```python
import os

api_key = os.getenv('REZEN_API_KEY')
if not api_key:
    print("❌ Environment variable not set")
    print("Set with: export REZEN_API_KEY='your_key'")
else:
    print(f"✅ Found API key: {api_key[:10]}...")
```

---

## Connection Problems

### Network Timeouts

**Symptoms:**
- `NetworkError: Connection timeout`
- Requests hanging indefinitely
- Intermittent connection failures

**Solutions:**

```python
from rezen import RezenClient
from rezen.base_client import BaseClient
import time

# 1. Increase timeout
BaseClient.DEFAULT_TIMEOUT = 60  # 60 seconds

# 2. Implement retry logic
def retry_request(func, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
                continue
            raise

# Usage
client = RezenClient()
teams = retry_request(lambda: client.teams.search_teams(page_size=10))
```

### SSL Certificate Issues

**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solutions:**

```python
import ssl
import requests
from urllib3.exceptions import InsecureRequestWarning

# WARNING: Only for development/testing
# Disable SSL verification (NOT recommended for production)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Or update certificates
# pip install --upgrade certifi
```

**Better solution - Update certificates:**
```bash
# Update certificates
pip install --upgrade certifi

# macOS specific
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Proxy Issues

**Error:** Connection fails behind corporate firewall

**Solutions:**

```python
import os
from rezen import RezenClient

# Set proxy environment variables
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'

# Or configure requests session directly
import requests
from rezen.base_client import BaseClient

class ProxyBaseClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.proxies = {
            'http': 'http://proxy.company.com:8080',
            'https': 'http://proxy.company.com:8080'
        }

# Use custom client
client = RezenClient()
client.teams._base_client = ProxyBaseClient()
```

---

## API Errors

### Rate Limiting

**Error:** `RateLimitError: Rate limit exceeded`

**Solutions:**

```python
from rezen.exceptions import RateLimitError
import time
import random

def rate_limited_request(func, *args, **kwargs):
    max_retries = 5
    base_delay = 1

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting {delay:.2f}s...")
                time.sleep(delay)
                continue
            raise e

# Usage
client = RezenClient()
teams = rate_limited_request(client.teams.search_teams, status="ACTIVE")
```

### Server Errors (5xx)

**Error:** `ServerError: Internal server error`

**Solutions:**

```python
from rezen.exceptions import ServerError
import time

def handle_server_errors(func, *args, **kwargs):
    max_retries = 3

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ServerError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                print(f"Server error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            # Log the error for investigation
            print(f"Server error after {max_retries} attempts: {e}")
            raise

# Usage
result = handle_server_errors(
    client.transaction_builder.create_transaction_builder
)
```

### Resource Not Found

**Error:** `NotFoundError: Resource not found`

**Common Causes & Solutions:**

```python
from rezen.exceptions import NotFoundError

# 1. Verify resource ID exists
def safe_get_transaction(client, transaction_id):
    try:
        return client.transactions.get_transaction(transaction_id)
    except NotFoundError:
        print(f"❌ Transaction {transaction_id} not found")

        # Try to find similar transactions
        try:
            builders = client.transaction_builder.get_transaction_builders(
                limit=10, from_offset=0, yenta_id="your_user_id"
            )
            print(f"Available transaction builders: {len(builders)}")
            for builder in builders[:3]:
                print(f"  - {builder.get('id')}")
        except Exception as e:
            print(f"Could not list transactions: {e}")
        return None

# 2. Verify team ID exists
def safe_get_team(client, team_id):
    try:
        return client.teams.get_team_without_agents(team_id)
    except NotFoundError:
        print(f"❌ Team {team_id} not found")

        # Search for similar teams
        teams = client.teams.search_teams(page_size=5)
        print(f"Available teams: {len(teams)}")
        for team in teams:
            print(f"  - {team.get('name')} ({team.get('id')})")
        return None
```

---

## Data Validation Issues

### Invalid Request Data

**Error:** `ValidationError: Invalid request parameters`

**Common Issues & Fixes:**

```python
from rezen.exceptions import ValidationError

# 1. Date format issues
def fix_date_formats():
    # ❌ Wrong formats
    bad_dates = [
        "2024/01/15",  # Should use hyphens
        "01-15-2024",  # Wrong order
        "2024-1-5",    # Missing zero padding
    ]

    # ✅ Correct format: YYYY-MM-DD
    good_date = "2024-01-15"

    return good_date

# 2. Missing required fields
def validate_buyer_data(buyer_data):
    required_fields = ['first_name', 'last_name', 'email']

    missing_fields = []
    for field in required_fields:
        if not buyer_data.get(field):
            missing_fields.append(field)

    if missing_fields:
        raise ValidationError(f"Missing required fields: {missing_fields}")

    # Email validation
    email = buyer_data.get('email')
    if email and '@' not in email:
        raise ValidationError(f"Invalid email format: {email}")

    return True

# Usage
buyer_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com"
}

try:
    validate_buyer_data(buyer_data)
    client.transaction_builder.add_buyer("tx-id", buyer_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Type Conversion Issues

**Error:** `TypeError: Object of type datetime is not JSON serializable`

**Solutions:**

```python
from datetime import datetime, date
import json

# 1. Convert dates to strings
def prepare_date_data(data):
    """Convert datetime objects to ISO format strings."""
    if isinstance(data, dict):
        return {k: prepare_date_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [prepare_date_data(item) for item in data]
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    return data

# Usage
transaction_data = {
    "closing_date": datetime(2024, 6, 15),
    "contract_date": date(2024, 5, 1)
}

# Convert before sending
clean_data = prepare_date_data(transaction_data)
# Now: {"closing_date": "2024-06-15T00:00:00", "contract_date": "2024-05-01"}
```

---

## Performance Problems

### Slow Response Times

**Symptoms:**
- API calls taking > 30 seconds
- Timeouts on large data requests
- Memory usage growing continuously

**Solutions:**

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(description):
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{description}: {elapsed:.2f}s")

# 1. Paginate large requests
def get_all_teams_paginated(client, page_size=50):
    all_teams = []
    page_number = 0

    while True:
        with timer(f"Page {page_number}"):
            teams = client.teams.search_teams(
                page_number=page_number,
                page_size=page_size
            )

        if not teams:
            break

        all_teams.extend(teams)
        page_number += 1

        # Add small delay to avoid rate limiting
        time.sleep(0.1)

    return all_teams

# 2. Use smaller page sizes for initial testing
def debug_slow_request(client):
    # Start with small request
    with timer("Small request (5 items)"):
        teams = client.teams.search_teams(page_size=5)

    # Gradually increase if needed
    with timer("Medium request (50 items)"):
        teams = client.teams.search_teams(page_size=50)
```

### Memory Issues

**Symptoms:**
- `MemoryError` on large datasets
- Python process memory growing continuously

**Solutions:**

```python
import gc
from typing import Iterator, Dict, Any

def process_teams_in_batches(client, batch_size=100) -> Iterator[Dict[str, Any]]:
    """Process teams in batches to avoid memory issues."""
    page_number = 0

    while True:
        try:
            teams = client.teams.search_teams(
                page_number=page_number,
                page_size=batch_size
            )

            if not teams:
                break

            # Yield each team individually
            for team in teams:
                yield team

            # Clean up
            del teams
            gc.collect()

            page_number += 1

        except Exception as e:
            print(f"Error processing page {page_number}: {e}")
            break

# Usage
processed_count = 0
for team in process_teams_in_batches(client):
    # Process one team at a time
    print(f"Processing team: {team.get('name')}")
    processed_count += 1

    if processed_count % 100 == 0:
        print(f"Processed {processed_count} teams")
```

---

## Common Error Messages

### "Transaction not found"

**Possible Causes:**
1. Transaction ID is wrong
2. Transaction was deleted
3. Using staging vs production IDs
4. Transaction hasn't been created yet

**Debug Steps:**
```python
def debug_transaction_not_found(client, transaction_id):
    print(f"Debugging transaction: {transaction_id}")

    # 1. Check transaction ID format
    if not transaction_id or len(transaction_id) < 10:
        print("❌ Transaction ID seems too short")
        return

    # 2. List available transactions
    try:
        builders = client.transaction_builder.get_transaction_builders(
            limit=10, from_offset=0, yenta_id="your-user-id"
        )
        print(f"Available transaction builders: {len(builders)}")

        for builder in builders:
            builder_id = builder.get('id')
            if builder_id and transaction_id in builder_id:
                print(f"✅ Found similar ID: {builder_id}")

    except Exception as e:
        print(f"Error listing transactions: {e}")
```

### "Invalid enum value"

**Error:** `ValueError: 'INVALID_STATUS' is not a valid TeamStatus`

**Solution:**
```python
from rezen import TeamStatus, AgentStatus

# ❌ Wrong - using string
teams = client.teams.search_teams(status="ACTIVE")

# ✅ Correct - using enum
teams = client.teams.search_teams(status=TeamStatus.ACTIVE)

# ❌ Wrong - typo in enum
agents = client.agents.search_active_agents(status="ACTIV")

# ✅ Correct - proper enum
agents = client.agents.search_active_agents(status=AgentStatus.ACTIVE)

# Check available enum values
print("Available team statuses:", [s.value for s in TeamStatus])
print("Available agent statuses:", [s.value for s in AgentStatus])
```

### "Connection refused"

**Possible Causes:**
1. Wrong base URL
2. Network connectivity issues
3. Firewall blocking requests
4. Service temporarily down

**Debug Steps:**
```python
import requests

def debug_connection_issues():
    # 1. Test basic connectivity
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        print("✅ Internet connection working")
    except Exception as e:
        print(f"❌ Internet connection issue: {e}")
        return

    # 2. Test ReZEN API endpoints
    base_urls = [
        "https://yenta.therealbrokerage.com/api/v1",
        "https://production-api.rezen.com"  # Example
    ]

    for url in base_urls:
        try:
            response = requests.get(f"{url}/health", timeout=10)
            print(f"✅ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

debug_connection_issues()
```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging
from rezen import RezenClient

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create client
client = RezenClient()

# All HTTP requests/responses will now be logged
teams = client.teams.search_teams(page_size=5)
```

### Request/Response Inspection

```python
import json
from rezen.base_client import BaseClient

class DebugClient(BaseClient):
    def _request(self, method, endpoint, **kwargs):
        # Log request details
        print(f"\n🔍 REQUEST: {method} {self.base_url}/{endpoint}")
        if kwargs.get('params'):
            print(f"   Params: {kwargs['params']}")
        if kwargs.get('json_data'):
            print(f"   Data: {json.dumps(kwargs['json_data'], indent=2)}")

        # Make the request
        response = super()._request(method, endpoint, **kwargs)

        # Log response details
        print(f"✅ RESPONSE: {len(json.dumps(response)) if response else 0} bytes")

        return response

# Use debug client
from rezen.teams import TeamsClient

debug_teams_client = TeamsClient()
debug_teams_client.__class__ = type('DebugTeamsClient', (DebugClient,), {})

teams = debug_teams_client.search_teams(status="ACTIVE", page_size=2)
```

### Performance Profiling

```python
import cProfile
import pstats
from io import StringIO

def profile_api_calls():
    # Create a profiler
    pr = cProfile.Profile()

    # Start profiling
    pr.enable()

    # Your API calls here
    client = RezenClient()
    teams = client.teams.search_teams(page_size=50)
    agents = client.agents.search_active_agents(page_size=20)

    # Stop profiling
    pr.disable()

    # Print results
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()

    print(s.getvalue())

profile_api_calls()
```

---

## Environment Issues

### Virtual Environment Problems

**Symptoms:**
- `ModuleNotFoundError: No module named 'rezen'`
- Wrong Python version
- Package conflicts

**Solutions:**

```bash
# 1. Verify virtual environment is activated
which python
which pip

# 2. Check if rezen is installed
pip list | grep rezen

# 3. Reinstall in clean environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
pip install rezen

# 4. Verify installation
python -c "import rezen; print(rezen.__version__)"
```

### Python Version Issues

**Error:** `SyntaxError` or `ImportError` related to Python version

**Check and fix:**

```bash
# Check Python version
python --version

# ReZEN requires Python 3.7+
# If using older version, upgrade:

# macOS with Homebrew
brew install python@3.9

# Ubuntu/Debian
sudo apt update
sudo apt install python3.9

# Windows - download from python.org

# Use specific Python version
python3.9 -m venv venv
source venv/bin/activate
pip install rezen
```

### Package Conflicts

**Error:** Version conflicts between dependencies

**Solutions:**

```bash
# 1. Check for conflicts
pip check

# 2. Create clean environment
pip freeze > old_requirements.txt
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate

# 3. Install only what you need
pip install rezen
pip install -r your_app_requirements.txt

# 4. If still conflicts, pin versions
pip install 'requests>=2.25.0,<3.0.0'
pip install 'urllib3>=1.26.0,<2.0.0'
```

---

## Getting Help

### Collect Debug Information

When reporting issues, include this information:

```python
import sys
import platform
import requests
import rezen

def collect_debug_info():
    print("=== Debug Information ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"ReZEN version: {rezen.__version__}")
    print(f"Requests version: {requests.__version__}")

    # Check API connectivity
    try:
        client = rezen.RezenClient()
        teams = client.teams.search_teams(page_size=1)
        print("✅ API connectivity: Working")
    except Exception as e:
        print(f"❌ API connectivity: {e}")

    # Check environment
    import os
    api_key = os.getenv('REZEN_API_KEY')
    print(f"API key set: {'Yes' if api_key else 'No'}")

    print("========================")

collect_debug_info()
```

### Support Channels

- **Documentation**: [API Reference](api-reference.md)
- **Examples**: [Usage Examples](examples.md)
- **GitHub Issues**: Create an issue with debug information
- **Email Support**: support@rezen.com

---

**💡 Pro Tip:** Always test with the smallest possible data set first, then scale up. This helps isolate whether issues are related to data size, specific values, or configuration problems.
