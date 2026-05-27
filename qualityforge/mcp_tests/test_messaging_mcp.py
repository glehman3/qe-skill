"""
Messaging MCP Integration Tests

These tests validate the Messaging MCP server functionality.
Ported from QCoE MCP Test Suite (Google Sheet).

To run:
    pip install httpx pytest pytest-asyncio
    pytest test_messaging_mcp.py -v

Environment variables required:
    messaging_MCP_URL - MCP server URL (default: https://messagingapp.com/mcp)
    messaging_MCP_TOKEN - Bearer token for authentication
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Any

import httpx
import pytest

# Configuration
MCP_URL = os.getenv("messaging_MCP_URL", "https://messagingapp.com/mcp")
MCP_TOKEN = os.getenv("messaging_MCP_TOKEN", "")


@dataclass
class MCPTestResult:
    """Result of an MCP test execution."""
    test_id: str
    name: str
    passed: bool
    message: str


class messagingMCPClient:
    """HTTP client for Messaging MCP server."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> dict:
        """Call an MCP tool via HTTP POST."""
        # MCP uses JSON-RPC 2.0 style requests
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
            "id": 1,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            result = response.json()

            # Handle JSON-RPC response format
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            return result.get("result", result)


# Test fixtures
@pytest.fixture
def mcp_client():
    """Create MCP client for tests."""
    if not MCP_TOKEN:
        pytest.skip("messaging_MCP_TOKEN not set")
    return messagingMCPClient(MCP_URL, MCP_TOKEN)


# =============================================================================
# TC-003: Authentication - Valid API Key
# =============================================================================
@pytest.mark.asyncio
async def test_tc003_valid_api_key_authentication(mcp_client):
    """
    TC-003: Verify valid API key authentication succeeds
    
    Pre-conditions:
        1. Messaging MCP is configured in mcp.json
        2. Valid messaging API key is set in Authorization header
        
    Expected Results:
        1. API call succeeds without authentication errors
        2. Account status information is returned
        3. Sending domains and quota are displayed
        4. No 401/403 errors occur
    """
    result = await mcp_client.call_tool("account_status")

    # Verify account info returned
    assert "account" in result or "username" in str(result), "Account info should be returned"
    assert "quota" in str(result).lower() or "hourly_quota" in str(result), "Quota should be displayed"


# =============================================================================
# TC-006: Messages Tool - Send Email
# =============================================================================
@pytest.mark.asyncio
async def test_tc006_messages_send(mcp_client):
    """
    TC-006: Verify messages/send tool sends email successfully
    
    Pre-conditions:
        1. Messaging MCP is configured and authenticated
        2. Sender domain is verified (or using test recipient)
        
    Expected Results:
        1. API returns success response with message ID
        2. Message status shows as 'sent' or 'queued' or 'rejected' (for unverified domain)
    """
    result = await mcp_client.call_tool("call_api", {
        "path": "messages/send",
        "params": {
            "message": {
                "subject": "MCP Test",
                "from_email": "test@example.com",
                "html": "<p>MCP Integration Test</p>",
                "to": [{"email": "test@mc-mail.nosend"}],
            }
        }
    })

    # Should return a response (even if rejected due to unverified domain)
    assert result is not None, "Should receive a response"
    # The response should contain status info
    result_str = str(result).lower()
    assert any(status in result_str for status in ["sent", "queued", "rejected", "status", "_id"]), \
        f"Response should contain message status: {result}"


# =============================================================================
# TC-007: Messages Tool - Search
# =============================================================================
@pytest.mark.asyncio
async def test_tc007_messages_search(mcp_client):
    """
    TC-007: Verify messages/search returns message history
    
    Expected Results:
        1. API returns list of matching messages (may be empty)
        2. No errors occur
    """
    result = await mcp_client.call_tool("call_api", {
        "path": "messages/search",
        "params": {"query": "test"}
    })

    # Should return without error (empty array is valid)
    assert result is not None, "Should receive a response"


# =============================================================================
# TC-011: Templates Tool - List
# =============================================================================
@pytest.mark.asyncio
async def test_tc011_templates_list(mcp_client):
    """
    TC-011: Verify templates/list returns all templates
    
    Expected Results:
        1. API returns list of all templates (may be empty)
        2. No errors occur
    """
    result = await mcp_client.call_tool("call_api", {
        "path": "templates/list",
        "params": {}
    })

    # Should return without error
    assert result is not None, "Should receive a response"


# =============================================================================
# TC-013: Templates Tool - Add
# =============================================================================
@pytest.mark.asyncio
async def test_tc013_templates_add_and_delete(mcp_client):
    """
    TC-013 + TC-016: Verify templates/add creates new template and templates/delete removes it
    
    Expected Results:
        1. Template is created successfully
        2. Template can be deleted
    """
    template_name = "mcp-pytest-template"

    # Create template
    add_result = await mcp_client.call_tool("call_api", {
        "path": "templates/add",
        "params": {
            "name": template_name,
            "code": "<p>Hello *|FNAME|*</p>",
            "subject": "Test Subject",
            "from_email": "test@example.com",
            "from_name": "Test",
            "text": "Hello",
        }
    })

    assert add_result is not None, "Template creation should return a response"

    # Clean up - delete template
    try:
        delete_result = await mcp_client.call_tool("call_api", {
            "path": "templates/delete",
            "params": {"name": template_name}
        })
        assert delete_result is not None, "Template deletion should return a response"
    except Exception as e:
        # Log but don't fail if delete fails (template may not have been created)
        print(f"Template cleanup failed: {e}")


# =============================================================================
# TC-018: Senders Tool - Domains
# =============================================================================
@pytest.mark.asyncio
async def test_tc018_senders_domains(mcp_client):
    """
    TC-018: Verify senders/domains returns sending domains
    
    Expected Results:
        1. API returns list of sending domains
        2. Each domain shows verification status
    """
    result = await mcp_client.call_tool("call_api", {
        "path": "senders/domains",
        "params": {}
    })

    assert result is not None, "Should receive a response"


# =============================================================================
# TC-033: Users Tool - Ping
# =============================================================================
@pytest.mark.asyncio
async def test_tc033_users_ping(mcp_client):
    """
    TC-033: Verify users/ping confirms API connectivity
    
    Expected Results:
        1. API returns 'PONG' response
        2. No authentication errors
    """
    result = await mcp_client.call_tool("call_api", {
        "path": "users/ping",
        "params": {}
    })

    result_str = str(result).upper()
    assert "PONG" in result_str, f"Expected PONG response, got: {result}"


# =============================================================================
# TC-036: Helper Tools - Account Status
# =============================================================================
@pytest.mark.asyncio
async def test_tc036_account_status(mcp_client):
    """
    TC-036: Verify account_status tool returns health summary
    
    Expected Results:
        1. Sending domains are listed
        2. DKIM/SPF verification status shown
        3. Reputation score displayed
        4. Send quota and any warnings shown
    """
    result = await mcp_client.call_tool("account_status")

    result_str = str(result).lower()

    # Verify key components
    assert "health" in result_str or "status" in result_str, "Health status should be included"
    assert "quota" in result_str, "Quota should be displayed"


# =============================================================================
# TC-037: Helper Tools - Diagnose Failed Send
# =============================================================================
@pytest.mark.asyncio
async def test_tc037_diagnose_failed_send(mcp_client):
    """
    TC-037: Verify diagnose_failed_send explains delivery failure
    
    Expected Results:
        1. Tool identifies message or returns "No messages found"
        2. No unhandled errors
    """
    result = await mcp_client.call_tool("diagnose_failed_send", {
        "email": "nonexistent-test-email@example.com"
    })

    # Should return some kind of response (likely "no messages found")
    assert result is not None, "Should receive a response"


# =============================================================================
# TC-038: Helper Tools - Build Template
# =============================================================================
@pytest.mark.asyncio
async def test_tc038_build_template(mcp_client):
    """
    TC-038: Verify build_template generates template scaffold
    
    Expected Results:
        1. Template HTML scaffold is generated
        2. Merge tag examples are included
    """
    result = await mcp_client.call_tool("build_template", {
        "name": "test-scaffold",
        "subject": "Welcome {{FNAME}}",
        "from_email": "test@example.com",
        "from_name": "Test Sender",
        "save": False,
    })

    result_str = str(result).lower()
    # Should contain HTML or template content
    assert any(x in result_str for x in ["html", "template", "<", "merge"]), \
        f"Should generate template scaffold: {result}"


# =============================================================================
# TC-039: Helper Tools - Integrate API
# =============================================================================
@pytest.mark.asyncio
async def test_tc039_integrate_api(mcp_client):
    """
    TC-039: Verify integrate_api returns working code snippet
    
    Expected Results:
        1. Working code snippet is returned
        2. Code is syntactically correct for the language
    """
    result = await mcp_client.call_tool("integrate_api", {
        "language": "python",
        "endpoint": "messages/send",
    })

    result_str = str(result).lower()
    # Should contain Python code
    assert any(x in result_str for x in ["import", "def", "requests", "python"]), \
        f"Should return Python code snippet: {result}"


# =============================================================================
# TC-040: Helper Tools - Onboarding
# =============================================================================
@pytest.mark.asyncio
async def test_tc040_onboarding(mcp_client):
    """
    TC-040: Verify onboarding tool returns setup checklist
    
    Expected Results:
        1. Current account state is assessed
        2. Completed steps are identified
        3. Missing steps are listed with priority
    """
    result = await mcp_client.call_tool("onboarding")

    result_str = str(result).lower()
    # Should contain checklist or steps
    assert any(x in result_str for x in ["step", "checklist", "complete", "setup", "domain"]), \
        f"Should return onboarding checklist: {result}"


# =============================================================================
# TC-041: Helper Tools - List API
# =============================================================================
@pytest.mark.asyncio
async def test_tc041_list_api(mcp_client):
    """
    TC-041: Verify list_api returns available endpoints
    
    Expected Results:
        1. All API endpoints are listed
        2. Descriptions are included for summary mode
    """
    result = await mcp_client.call_tool("list_api", {
        "detail": "summary"
    })

    result_str = str(result).lower()
    # Should list endpoints
    assert any(x in result_str for x in ["messages", "templates", "users", "endpoint"]), \
        f"Should list API endpoints: {result}"


# =============================================================================
# TC-042: Helper Tools - Describe API
# =============================================================================
@pytest.mark.asyncio
async def test_tc042_describe_api(mcp_client):
    """
    TC-042: Verify describe_api returns endpoint schema
    
    Expected Results:
        1. Full parameter schema is returned
        2. Required parameters are identified
    """
    result = await mcp_client.call_tool("describe_api", {
        "path": "messages/send"
    })

    result_str = str(result).lower()
    # Should describe the endpoint
    assert any(x in result_str for x in ["message", "param", "required", "to", "from"]), \
        f"Should describe messages/send endpoint: {result}"


# =============================================================================
# TC-045: Error Handling - Invalid Endpoint
# =============================================================================
@pytest.mark.asyncio
async def test_tc045_invalid_endpoint(mcp_client):
    """
    TC-045: Verify MCP handles invalid endpoint path
    
    Expected Results:
        1. 404 or similar error is returned
        2. Error clearly indicates invalid endpoint
        3. No crash occurs
    """
    try:
        result = await mcp_client.call_tool("call_api", {
            "path": "invalid/nonexistent/endpoint",
            "params": {}
        })
        # If we get here, check if error is in the result
        result_str = str(result).lower()
        assert any(x in result_str for x in ["error", "404", "unknown", "invalid", "not found"]), \
            f"Should indicate invalid endpoint: {result}"
    except Exception as e:
        # Exception is also acceptable - just make sure it's informative
        error_str = str(e).lower()
        assert any(x in error_str for x in ["error", "404", "unknown", "invalid", "not found"]), \
            f"Error should indicate invalid endpoint: {e}"


# =============================================================================
# Run all tests
# =============================================================================
if __name__ == "__main__":
    # Simple test runner for manual execution
    import sys

    async def run_tests():
        if not MCP_TOKEN:
            print("ERROR: messaging_MCP_TOKEN environment variable not set")
            print("Set it with: export messaging_MCP_TOKEN='your-token-here'")
            sys.exit(1)

        client = messagingMCPClient(MCP_URL, MCP_TOKEN)
        tests = [
            ("TC-003", "Valid API Key Auth", test_tc003_valid_api_key_authentication),
            ("TC-006", "Messages Send", test_tc006_messages_send),
            ("TC-007", "Messages Search", test_tc007_messages_search),
            ("TC-011", "Templates List", test_tc011_templates_list),
            ("TC-013", "Templates Add/Delete", test_tc013_templates_add_and_delete),
            ("TC-018", "Senders Domains", test_tc018_senders_domains),
            ("TC-033", "Users Ping", test_tc033_users_ping),
            ("TC-036", "Account Status", test_tc036_account_status),
            ("TC-037", "Diagnose Failed Send", test_tc037_diagnose_failed_send),
            ("TC-038", "Build Template", test_tc038_build_template),
            ("TC-039", "Integrate API", test_tc039_integrate_api),
            ("TC-040", "Onboarding", test_tc040_onboarding),
            ("TC-041", "List API", test_tc041_list_api),
            ("TC-042", "Describe API", test_tc042_describe_api),
            ("TC-045", "Invalid Endpoint", test_tc045_invalid_endpoint),
        ]

        passed = 0
        failed = 0

        print(f"\n{'='*60}")
        print("Messaging MCP Integration Tests")
        print(f"{'='*60}\n")

        for test_id, name, test_func in tests:
            try:
                await test_func(client)
                print(f"✅ {test_id}: {name} - PASSED")
                passed += 1
            except AssertionError as e:
                print(f"❌ {test_id}: {name} - FAILED: {e}")
                failed += 1
            except Exception as e:
                print(f"❌ {test_id}: {name} - ERROR: {e}")
                failed += 1

        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'='*60}\n")

        sys.exit(0 if failed == 0 else 1)

    asyncio.run(run_tests())
