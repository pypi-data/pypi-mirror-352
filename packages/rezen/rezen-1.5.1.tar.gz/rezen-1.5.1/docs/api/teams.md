# Teams API

Search and manage team information with comprehensive filtering and sorting capabilities.

---

## Overview

!!! abstract "Teams API Capabilities"

    - **Search Teams**: Find teams with advanced filtering options
    - **Team Details**: Get comprehensive team information
    - **Flexible Sorting**: Sort results by various criteria
    - **Pagination**: Handle large result sets efficiently

---

## Quick Start

```python
from rezen import RezenClient
from rezen.enums import TeamStatus, SortDirection

client = RezenClient()

# Simple team search
teams = client.teams.search_teams(status="ACTIVE", limit=10)

# Advanced search with enums
teams = client.teams.search_teams(
    status=TeamStatus.ACTIVE,
    sort_direction=SortDirection.DESC,
    page_size=50
)
```

---

## API Methods

### Search Teams

::: rezen.teams.TeamsClient.search_teams
    options:
      show_source: false
      heading_level: 4

!!! example "Search Examples"

    === "Basic Search"

        ```python
        teams = client.teams.search_teams(
            status="ACTIVE",
            limit=20
        )
        ```

    === "Advanced Filtering"

        ```python
        from rezen.enums import TeamStatus, SortField, SortDirection

        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            name="Sales Team",
            sort_by=[SortField.NAME, SortField.CREATED_AT],
            sort_direction=SortDirection.ASC,
            page_size=50
        )
        ```

### Get Team Details

::: rezen.teams.TeamsClient.get_team_without_agents
    options:
      show_source: false
      heading_level: 4

---

## Parameters Reference

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page_number` | `Optional[int]` | Page number (default: 0) |
| `page_size` | `Optional[int]` | Results per page (default: 20) |
| `sort_direction` | `Optional[SortDirection]` | ASC or DESC |
| `sort_by` | `Optional[List[SortField]]` | Fields to sort by |
| `team_id` | `Optional[str]` | Filter by team UUID |
| `name` | `Optional[str]` | Filter by team name |
| `search_text` | `Optional[str]` | General search text |
| `status` | `Optional[TeamStatus]` | ACTIVE or INACTIVE |
| `created_at_start` | `Optional[str]` | Date filter start (YYYY-MM-DD) |
| `created_at_end` | `Optional[str]` | Date filter end (YYYY-MM-DD) |
| `team_type` | `Optional[TeamType]` | Team type filter |

---

## Complete Examples

!!! example "Comprehensive Team Search"

    ```python
    from rezen import RezenClient
    from rezen.enums import TeamStatus, TeamType, SortDirection, SortField

    def comprehensive_team_search():
        client = RezenClient()

        # Search with multiple criteria
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            team_type=TeamType.PLATINUM,
            sort_by=[SortField.NAME, SortField.CREATED_AT],
            sort_direction=SortDirection.DESC,
            page_size=25,
            created_at_start="2024-01-01",
            created_at_end="2024-12-31"
        )

        print(f"Found {len(teams)} teams")
        for team in teams:
            print(f"Team: {team['name']} - Status: {team['status']}")

        return teams
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [:material-account-tie: **Agents API**](agents.md)

    Search and manage agent information

-   [:material-hammer-wrench: **Transaction Builder**](transaction-builder.md)

    Create transactions with team members

-   [:material-code-braces: **Data Types**](data-types.md)

    Learn about team-related enums and types

</div>
