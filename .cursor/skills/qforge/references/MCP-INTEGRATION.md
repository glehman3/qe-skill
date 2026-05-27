# MCP Integration

## Primary Sources (Prioritized)
1. **GitHub PR's** - Main input source
2. **PRD's (Product Requirements Documents)** - Alternative to PR's for early-stage testing

## Using GitHub MCP Tools

| Tool | Purpose |
|------|---------|
| `mcp_github-mcp_search_repositories` | Validate repo names |
| `mcp_github-mcp_get_pull_request` | Get specific PR information |
| `mcp_github-mcp_list_pull_requests` | List PRs for repository-based test jams |
| `mcp_github-mcp_get_pull_request_files` | Understand scope of changes |
| `mcp_github-mcp_search_code` | Understand component context |
| `mcp_github-mcp_search_issues` | Find PRs associated with Jira tickets |

### Example: Search for PRs by Jira Ticket
```
mcp_github-mcp_search_issues with query: "[TICKET-ID] is:pr"
```

## Using Mabl MCP Tools (Optional Enhancement)

**When to Use Mabl MCP**:
- When generating test cases for features with existing Mabl tests
- To identify gaps in automated test coverage
- To suggest which test cases could be automated
- To reference existing test flows and scenarios
- To avoid duplicating existing automated tests

**Mabl MCP Integration**:
1. **Check for Existing Tests**:
   - Query Mabl for existing automated tests related to the component
   - Identify test coverage gaps
   - Reference existing test IDs in generated test cases

2. **Leverage Mabl Data**:
   - Review existing test scenarios to inform manual test case generation
   - Identify areas not covered by automation
   - Suggest automation opportunities for repetitive tests
   - Link related Mabl tests in test case notes

3. **Test Case Enhancement**:
   - Add "Mabl Test Reference" field when applicable
   - Mark test cases that could be automated
   - Suggest Mabl test creation for high-value scenarios
   - Include Mabl test URLs for reference

**Mabl Integration Workflow**:
1. Fetch PR details from GitHub (primary)
2. Extract component/feature information
3. Query Mabl for existing tests on that component (if available)
4. Generate test cases considering existing Mabl coverage
5. Note automation opportunities and gaps
6. Include Mabl test references where relevant

**Note**: Mabl integration is **optional** and should **not block** test jam creation if Mabl data is unavailable.

## Using Atlassian MCP for Jira (Optional)

**When to Use Atlassian MCP**:
- To fetch ticket details (description, ACs, comments)
- To query project metadata (components, issue types)
- To create Jira tickets from completed test jams
- To add comments or update existing tickets

**Setup** (one-time):

Add to `~/.cursor/mcp.json` under `"mcpServers"`:
```json
"atlassian-mcp-server": {
  "url": "https://mcp.atlassian.com/v1/mcp",
  "type": "http"
}
```

Then:
1. Restart Cursor
2. Go to **Settings → Tools & MCP**
3. Click **"Authenticate"** next to the Atlassian MCP server
4. Complete OAuth login in your browser

**Initialization** (required before any Jira calls):
```
# First, obtain cloudId for your Jira instance
resources = getAccessibleAtlassianResources()
cloudId = resources[0]["id"]  # e.g., "f4f7b1b7-a9c1-4eb7-97ba-e4842db0f223"
```

**Key Tools** (all require `cloudId` parameter):

| Tool | Purpose |
|------|---------|
| `getJiraIssue(cloudId, issueIdOrKey)` | Fetch ticket details by key (e.g., "TESTING-1512") |
| `searchJiraIssuesUsingJql(cloudId, jql)` | Search issues using JQL |
| `createJiraIssue(cloudId, projectKey, issueTypeName, summary, ...)` | Create new tickets |
| `getVisibleJiraProjects(cloudId)` | List available projects |
| `getJiraProjectIssueTypesMetadata(cloudId, projectIdOrKey)` | Get issue types for a project |
| `addCommentToJiraIssue(cloudId, issueIdOrKey, commentBody)` | Add comment to ticket |
| `editJiraIssue(cloudId, issueIdOrKey, fields)` | Update ticket fields |

**Migration from old Jira MCP**:

| Old Tool | New Tool | Notes |
|----------|----------|-------|
| `jira_search_issues` | `searchJiraIssuesUsingJql` | JQL syntax unchanged |
| `jira_create_issue` | `createJiraIssue` | `issueType` → `issueTypeName` |
| `get_project_metadata` | `getVisibleJiraProjects` + `getJiraProjectIssueTypesMetadata` | Split into two calls |

## Using Figma MCP Tools (Optional)

**When to Use Figma MCP**:
- To analyze design files for UI testing
- To extract component/flow information for test case generation
- For Risk Analysis (Feature 2) to understand UI constraints

## Error Handling

- If PR/Repo not found, ask user to verify the information
- If insufficient permissions, notify user and suggest alternatives
- If API rate limits hit, inform user and suggest waiting or reducing scope
- If Mabl MCP unavailable, proceed without it (it's optional)
- If Atlassian MCP unavailable, accept pasted ticket content instead
- If Figma MCP unavailable, continue without design analysis

## MCP Availability Matrix

| MCP | Feature 1 (Test Jam) | Feature 2 (Risk) | Feature 3 (Bug Tickets) | Feature 4 (Jira Import) |
|-----|---------------------|------------------|-------------------------|-------------------------|
| GitHub | **Required** | **Required** | N/A | N/A |
| Atlassian (Jira) | Optional | Optional | **Required** | **Required** |
| Google Drive | Optional* | Optional | Optional** | Optional** |
| Mabl | Optional | N/A | N/A | N/A |
| Figma | Optional | Optional | N/A | N/A |

*Feature 1: Google Drive MCP enables Google Sheets creation for test jams.
**Features 3 & 4: Google Drive MCP enables direct Google Sheets/Docs reading; if unavailable, PDF export is used.

## Setup Guides

- [FIRST-TIME-SETUP.md](../../../../qualityforge/setup/FIRST-TIME-SETUP.md)
- [MCP-SETUP.md](../../../../qualityforge/setup/MCP-SETUP.md)

Quick install for GitHub MCP:
```bash
codegen mcp install github-mcp:latest
```
