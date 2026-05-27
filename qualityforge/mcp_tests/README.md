# Messaging MCP Integration Tests

Automated tests for the Messaging MCP (Model Context Protocol) server. These tests validate that the MCP layer correctly proxies messaging API calls and that helper tools work as expected.

## Test Coverage

Tests ported from the QCoE MCP Test Suite:

| Test ID | Component | Description |
|---------|-----------|-------------|
| TC-003 | Authentication | Valid API key authentication |
| TC-006 | Messages | messages/send endpoint |
| TC-007 | Messages | messages/search endpoint |
| TC-011 | Templates | templates/list endpoint |
| TC-013 | Templates | templates/add and templates/delete |
| TC-018 | Senders | senders/domains endpoint |
| TC-033 | Users | users/ping connectivity check |
| TC-036 | Helper Tools | account_status tool |
| TC-037 | Helper Tools | diagnose_failed_send tool |
| TC-038 | Helper Tools | build_template tool |
| TC-039 | Helper Tools | integrate_api tool |
| TC-040 | Helper Tools | onboarding tool |
| TC-041 | Helper Tools | list_api tool |
| TC-042 | Helper Tools | describe_api tool |
| TC-045 | Error Handling | Invalid endpoint handling |

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

### With pytest (recommended)

```bash
export messaging_MCP_TOKEN="your-token-here"
pytest test_messaging_mcp.py -v
```

### Direct execution

```bash
export messaging_MCP_TOKEN="your-token-here"
python test_messaging_mcp.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `messaging_MCP_TOKEN` | Bearer token for MCP authentication | (required) |
| `messaging_MCP_URL` | MCP server URL | `https://messagingapp.com/mcp` |

## Adding New Tests

Each test follows this structure:

```python
@pytest.mark.asyncio
async def test_tcXXX_description(mcp_client):
    """
    TC-XXX: Test title
    
    Pre-conditions:
        1. ...
        
    Expected Results:
        1. ...
    """
    result = await mcp_client.call_tool("tool_name", {"param": "value"})
    assert "expected" in str(result)
```

## Contributing to messaging-tests

These tests can be contributed to the [mctx/messaging-tests](https://github.com/mctx/messaging-tests) repository. To do so:

1. Copy this module to `messaging-tests/common/mcp/`
2. Add MCP configuration to their settings
3. Update their runner to optionally execute MCP tests
4. Open a PR with documentation

## Related Resources

- [Messaging MCP Server](https://messagingapp.com/mcp)
- [QCoE MCP Test Suite](https://docs.google.com/spreadsheets/d/1OwdsZEMWRS2hsweWGv546V14l4QhxV-KnIxjnBrsYSM)
- [messaging-tests repo](https://github.com/mctx/messaging-tests)
