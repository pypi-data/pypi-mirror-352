# Aliyah Python SDK

Python SDK for AI Agent Management and Compliance. Monitor, manage, and ensure compliance for your AI agents.

## Installation

```bash
pip install aliyah-sdk
```

## Quick Start

```python
from aliyah import AliyahClient

# Initialize client with your API key
client = AliyahClient("your_api_key")

# Create an agent
agent = client.agents.create("My Agent")
print(f"Created agent: {agent.name} (ID: {agent.id})")

# Verify agent is sending traces (wait for first session)
if client.agents.wait_for_session(agent.id, timeout=60):
    print("✅ Agent verified and sending traces!")
else:
    print("⏳ No traces received yet")

# Monitor sessions
sessions = client.sessions.list(limit=10)
print(f"Found {len(sessions)} sessions")

# Generate compliance report
report = client.compliance.generate_report(agent_id=agent.id)
print(f"Report generated: {report.get('view_url', 'N/A')}")

# Check for compliance issues
tickets = client.tickets.list(status="open")
if tickets:
    print(f"⚠️ {len(tickets)} open compliance issues")
else:
    print("✅ No open compliance issues")
```

## Agent Instrumentation

**Note**: For agent instrumentation and tracing, use the separate `ops` package. This SDK is for management and monitoring.

```bash
# Install the ops package for agent instrumentation
pip install ops

# In your agent code:
import ops as ao
ao.init(api_key="your_key", exporter_endpoint="https://aliyah-b9b7.onrender.com/v1/traces")
# Your agent code here - automatically traced
```

## API Reference

### Agent Management

```python
# Create agent
agent = client.agents.create("Agent Name", agent_type="custom")

# List agents
agents = client.agents.list()

# Get agent details
agent = client.agents.get(agent_id)

# Check for sessions (verification)
status = client.agents.check_sessions(agent_id)

# Wait for first session (polling)
connected = client.agents.wait_for_session(agent_id, timeout=60)

# Delete agent
client.agents.delete(agent_id)

# Get agent status and health
status = client.agents.get_status(agent_id)
health = client.agents.get_health(agent_id)
```

### Session Management

```python
# List sessions
sessions = client.sessions.list(limit=10, load_all=True)

# Get session details
details = client.sessions.get_details(session_id)

# Get LLM call details
call = client.sessions.get_llm_call(call_id)

# Get agent events
events = client.sessions.get_agent_events(
    agent_id=123,
    event_type="tool_usage",
    start_time="2024-01-01T00:00:00"
)
```

### Compliance Management

```python
# Evaluate session for compliance
result = client.compliance.evaluate_session(session_id, sync=True)

# Get evaluated sessions
sessions = client.compliance.get_evaluated_sessions(
    start_date=datetime(2024, 1, 1),
    agent_id=agent_id
)

# Generate compliance report
report = client.compliance.generate_report(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    agent_id=agent_id,
    sync=True
)

# List all reports
reports = client.compliance.list_reports()

# Download report
content = client.compliance.download_report(report_id)
with open("report.pdf", "wb") as f:
    f.write(content)

# Get compliance status data
status_data = client.compliance.get_status_report_data(agent_id=123)
```

### Ticket Management

```python
# List tickets with filters
tickets = client.tickets.list(
    status="open",
    priority="high",
    agent_id=123,
    limit=50
)

# List my assigned tickets
my_tickets = client.tickets.list_my_tickets(status="in_progress")

# Get detailed ticket information
ticket = client.tickets.get(ticket_id)

# Update ticket
updated = client.tickets.update(
    ticket_id,
    status="in_progress",
    priority="high",
    external_system="jira",
    external_ticket_id="PROJ-123"
)

# Reassign ticket
reassigned = client.tickets.reassign(
    ticket_id,
    assignee_id=456,
    reason="Better expertise match"
)

# Get ticket statistics
stats = client.tickets.get_stats()
print(f"Total: {stats.total}, Open: {stats.open}")

# Get available assignees
assignees = client.tickets.get_assignees()

# Integrate with external systems
result = client.tickets.integrate_external(
    ticket_id,
    system="jira",
    project_key="COMP",
    issue_type="Bug"
)

# Delete ticket (admin only)
client.tickets.delete(ticket_id)
```

## Utility Functions

```python
from aliyah import quick_agent_setup, verify_agent_connection, get_agent_summary

# Quick setup: create client and agent in one call
client, agent = quick_agent_setup("your-api-key", "My Agent")

# Verify agent connection
if verify_agent_connection(client, agent.id):
    print("Agent is connected!")

# Get comprehensive agent summary
summary = get_agent_summary(client, agent.id)
print(f"Agent has {summary['session_count']} sessions")
print(f"Open tickets: {len(summary['open_tickets'])}")
```

## Error Handling

```python
from aliyah import (
    AliyahError,
    AuthenticationError,
    AgentNotFoundError,
    SessionNotFoundError,
    TicketNotFoundError,
    ReportGenerationError,
    RateLimitError
)

try:
    agent = client.agents.get(999)
except AgentNotFoundError:
    print("Agent not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except AliyahError as e:
    print(f"API error: {e}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
    if e.response:
        print(f"Response: {e.response}")
```

## Configuration

### Environment Variables

```bash
# Optional: Set API key via environment (not needed if passed to client)
export ALIYAH_API_KEY="your_api_key"
```

### Custom Configuration

```python
# Custom client configuration
client = AliyahClient(
    api_key="your_key",
    base_url="https://your-custom-domain.com/api/v1"
)

# Test connection
if client.test_connection():
    print("✅ Connected to Aliyah API")
else:
    print("❌ Connection failed")
```

## Complete Example

```python
from aliyah import AliyahClient, get_agent_summary
from datetime import datetime, timedelta

def monitor_agents():
    """Complete example of agent monitoring workflow"""
    
    # Initialize client
    client = AliyahClient("your_api_key")
    
    # Get all agents
    agents = client.agents.list()
    print(f"Monitoring {len(agents)} agents...")
    
    for agent in agents:
        print(f"\n=== {agent.name} (ID: {agent.id}) ===")
        
        # Get comprehensive summary
        summary = get_agent_summary(client, agent.id)
        
        if summary.get('error'):
            print(f"❌ Error: {summary['error']}")
            continue
            
        # Print status
        if summary['has_sessions']:
            print(f"✅ Active - {summary['session_count']} sessions")
            if summary['last_session']:
                print(f"   Last seen: {summary['last_session']}")
        else:
            print("⚠️  No sessions detected")
        
        # Check for compliance issues
        if summary['open_tickets']:
            print(f"⚠️  {len(summary['open_tickets'])} open compliance issues:")
            for ticket in summary['open_tickets'][:3]:  # Show first 3
                print(f"   - {ticket.title} [{ticket.priority}]")
        else:
            print("✅ No compliance issues")
    
    # Generate organization-wide compliance report
    print("\n=== Generating Compliance Report ===")
    week_ago = datetime.now() - timedelta(days=7)
    
    try:
        report = client.compliance.generate_report(
            start_date=week_ago,
            sync=True
        )
        if report.get('success'):
            print(f"✅ Report generated: {report.get('view_url', 'Ready')}")
        else:
            print("⚠️  Report generation failed")
    except Exception as e:
        print(f"❌ Report error: {e}")
    
    # Get overall ticket stats
    print("\n=== Overall Ticket Statistics ===")
    stats = client.tickets.get_stats()
    print(f"Total tickets: {stats.total}")
    print(f"Open: {stats.open}, In Progress: {stats.in_progress}")
    print(f"Resolved: {stats.resolved}")

if __name__ == "__main__":
    monitor_agents()
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black aliyah/
isort aliyah/

# Type checking
mypy aliyah/
```

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://docs.aliyah.com
- Issues: https://github.com/aliyah/aliyah-python-sdk/issues
- Email: support@aliyah.com