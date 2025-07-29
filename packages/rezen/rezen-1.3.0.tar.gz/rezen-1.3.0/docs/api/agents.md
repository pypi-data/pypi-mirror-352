# Agents API

Comprehensive agent search, network management, and detailed information retrieval.

---

## Overview

!!! abstract "Agents API Features"

    - **Agent Search**: Find agents with advanced filtering
    - **Network Management**: Access sponsor trees and downlines
    - **Contact Information**: Get agent details by email or ID
    - **Geographic Filtering**: Search by location and region

---

## Quick Start

```python
from rezen import RezenClient
from rezen.enums import Country, StateOrProvince, AgentSortField

client = RezenClient()

# Basic agent search
agents = client.agents.search_active_agents(name="John", limit=10)

# Geographic search
agents = client.agents.search_active_agents(
    country=[Country.UNITED_STATES],
    state_or_province=[StateOrProvince.CALIFORNIA]
)
```

---

## Core Methods

### Search Active Agents

::: rezen.agents.AgentsClient.search_active_agents
    options:
      show_source: false
      heading_level: 4

### Get Agent by Email

::: rezen.agents.AgentsClient.get_agents_by_email
    options:
      show_source: false
      heading_level: 4

### Get Agents by IDs

::: rezen.agents.AgentsClient.get_agents_by_ids
    options:
      show_source: false
      heading_level: 4

### Network Hierarchy

::: rezen.agents.AgentsClient.get_sponsor_tree
    options:
      show_source: false
      heading_level: 4

::: rezen.agents.AgentsClient.get_down_line_agents
    options:
      show_source: false
      heading_level: 4

---

## Search Examples

!!! example "Advanced Agent Search"

    === "Geographic Search"

        ```python
        from rezen.enums import Country, StateOrProvince

        # Search California agents
        agents = client.agents.search_active_agents(
            country=[Country.UNITED_STATES],
            state_or_province=[StateOrProvince.CALIFORNIA],
            page_size=50
        )
        ```

    === "Sorted Results"

        ```python
        from rezen.enums import AgentSortField, AgentSortDirection

        agents = client.agents.search_active_agents(
            sort_by=[AgentSortField.LAST_NAME, AgentSortField.FIRST_NAME],
            sort_direction=AgentSortDirection.ASC,
            page_size=25
        )
        ```

---

## Network Management

!!! info "Agent Hierarchy"

    The ReZEN platform supports agent network hierarchies with sponsor trees and downlines.

!!! example "Network Analysis"

    ```python
    # Get agent's sponsor tree
    sponsor_tree = client.agents.get_sponsor_tree("agent-uuid")

    # Get first-tier downline
    downline = client.agents.get_down_line_agents(
        agent_id="agent-uuid",
        tier=1,
        status_in=["ACTIVE"]
    )
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [:material-account-group: **Teams API**](teams.md)

    Manage team information and memberships

-   [:material-hammer-wrench: **Transaction Builder**](transaction-builder.md)

    Add agents to transactions

-   [:material-book-open: **Directory API**](directory.md)

    Access additional agent directory services

</div>
