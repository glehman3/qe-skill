# Feature 1: Test Case/Jam Generation

*When user selects Option 1, proceed with this workflow*

---

## 🚨 CRITICAL FORMAT RULE - READ FIRST 🚨

**ABSOLUTE REQUIREMENT - NO EXCEPTIONS**:

### Pre-conditions, Test Steps, and Expected Results → **NUMBERED LISTS ONLY**

✅ **ALWAYS Use**:
```
1. First item
2. Second item
3. Third item
```

❌ **NEVER Use**:
```
- Bullet points  ← ❌ Causes Excel =NAME? errors
* Asterisks      ← ❌ Causes Excel =NAME? errors  
• Bullet symbols ← ❌ Causes Excel =NAME? errors
; Semicolons     ← ❌ Wrong format
```

**Why**: Cells starting with `-` cause Excel to display `=NAME?` errors

**Enforcement**: Automatic conversion via `enforce_numbered_lists()` function

**See**: [NUMBERED-LISTS-ONLY.md](../../../../qualityforge/NUMBERED-LISTS-ONLY.md) for visual guide

---

## MCP Verification (First Time / Diagnostic Check)

**BEFORE starting the interactive flow**, verify MCP availability:

1. **Check for GitHub MCP** (REQUIRED): Attempt to use `mcp_github-mcp_search_repositories` with a simple query (e.g., query="test", perPage=1)
   - If tool is NOT available or returns error: Display setup instructions and STOP
   - Setup guides: [FIRST-TIME-SETUP.md](../../../../qualityforge/setup/FIRST-TIME-SETUP.md) | [MCP-SETUP.md](../../../../qualityforge/setup/MCP-SETUP.md)
   - Quick setup: Configure GitHub MCP in Cursor Settings → MCP (see MCP-SETUP.md)
   - If available and working: Display "✅ GitHub MCP detected and ready"

2. **Check for Mabl MCP** (OPTIONAL): Verify if Mabl MCP tools are available
   - If NOT available: Continue without automation coverage analysis
   - If available: Display "✅ Mabl MCP detected - automation coverage analysis available"

3. **Check for Atlassian MCP** (OPTIONAL): Verify Jira integration
   - Call `getAccessibleAtlassianResources` to obtain `cloudId`
   - If error/unavailable: Display setup instructions (see below) and continue (ticket ingestion requires pasted content)
   - If available: Store `cloudId` for session; display "✅ Atlassian MCP detected - Jira integration available"

   **If Atlassian MCP not detected:**
   
   1. First, check if `~/.cursor/mcp.json` exists and whether `atlassian-mcp-server` is already configured
   2. Display and ask:
   ```
   ℹ️ Atlassian MCP not detected - Jira integration unavailable
   
   Would you like me to add the Atlassian MCP configuration to your mcp.json? (yes/no)
   ```
   
   **If user says yes:**
   - Read `~/.cursor/mcp.json`
   - Add to the `"mcpServers"` object:
     ```json
     "atlassian-mcp-server": {
       "url": "https://mcp.atlassian.com/v1/mcp",
       "type": "http"
     }
     ```
   - Write the updated file
   - Display:
     ```
     ✅ Added Atlassian MCP configuration to ~/.cursor/mcp.json
     
     Next steps:
     1. Restart Cursor (Cmd+Shift+P → "Developer: Reload Window")
     2. Go to Settings → Tools & MCP
     3. Click "Authenticate" next to atlassian-mcp-server
     4. Complete OAuth login in your browser
     5. Run /qforge again to use Jira integration
     ```
   
   **If user says no (or skip):**
   ```
   Continuing without Jira integration...
   (You can paste Jira ticket content manually when needed)
   ```

4. **Check for Figma MCP** (OPTIONAL): Verify if Figma MCP tools are available
   - If NOT available: Continue (risk analysis can still run without designs)
   - If available: Display "✅ Figma MCP detected - design ingestion available"

5. **Display Verification Summary**: Show MCP status and proceed

**Note**: Only verify on first use in session, when user asks, or if previous operation failed due to MCP issues. If verification test returns any result (even with warnings), proceed - the important thing is that the tool exists.

## Interactive Flow

When the user selects **Feature 1: Test Case/Jam Generation** (after MCP verification), guide them through this interactive process:

### Step 1: Welcome and Input Collection
Start with:
```
Let's create comprehensive test cases! 🎯

To get started, provide **any** of the following (one is enough):

📋 **Pull Request (PR)** (recommended)
- **PR URL(s)**: one or more PR URLs (comma-separated)
- **Example**: https://github.com/org/repo/pull/123

📦 **Repository**
- **Repository name**: org/repo
- **Example**: org/project

📄 **Product Requirements Document (PRD)**
- **PRD URL (required)**: link to the PRD document
- **PRD contents (required)**: paste the full PRD content

🎫 **Jira Ticket**
- **Jira URL or key** (e.g., PROJ-1234), or attach/export the ticket file and mention it with `@...`

Also include (optional):
- Any specific areas of focus or concerns
- Whether to check Mabl for existing test coverage (yes/no)
```

### Step 2: Gather Participant Information
After receiving the PR/Repo information:
```
Thank you for submitting those! 

How many participants will be part of this Test Jam?
```

### Step 3: Gather Additional Context
After receiving participant count:
```
Great! A few more questions to help create the best test cases:

1. Which test **category**(ies) should I create? (Be specific — I will ONLY generate the categories you list)
   
   Available types:
   - Functional Testing (core feature functionality)
   - UI/UX Testing (visual and interaction testing)
   - Integration Testing (cross-component interactions)
   - Regression Testing (ensure existing functionality isn't broken)
   - Performance Testing (load, response time, resource usage)
   - Security Testing (authentication, authorization, data protection)
   - Cross-Browser Testing (browser compatibility)
   - Accessibility Testing (WCAG compliance, screen readers)
   - API Testing (endpoint validation, error handling)
   - Mobile/Responsive Testing (device compatibility)
   
   Examples:
   - "functional" or "functional testing" → ONLY **Functional Testing** (Category)
   - "functional, regression" → ONLY **Functional Testing** + **Regression Testing** (Category)
   - "all" or "comprehensive" → ALL categories
   - "performance" → ONLY **Performance Testing** (Category)
   
   IMPORTANT:
   - These inputs map to the CSV **Category** column (Functional/Regression/etc).
   - The CSV **Type** column is the execution mode (Manual/Automated). For Test Jams, this is typically **Manual**.
   - For automated E2E tests, use `claude.md` in the playwright repository.

2. Are there any specific user flows or features that need extra attention?
3. What is the testing timeline/deadline?
4. Any specific devices, browsers, or environments to prioritize?
5. Should I check Mabl for existing automated test coverage? (yes/no)
   - If yes, I'll identify test coverage gaps and suggest automation opportunities
   - If no or Mabl unavailable, I'll proceed with standard test generation
```

## Analysis Requirements

### For PR-based Test Jams:
1. **Fetch PR Details** using MCP GitHub tools:
   - Get PR title, description, and labels
   - **Extract repository name** (org/repo) from PR URL
   - **Extract ticket ID** from PR title or description (e.g., TXPLAT-3858, MUL-4978)
   - Identify files changed and areas of code affected
   - Check for labels: `critical`, `high-priority`, `P0`, `P1`, `security`, `performance`
   - Analyze the PR comments for context and potential issues
   - Identify the component/feature being modified

2. **Prioritization Criteria**:
   - **Critical Priority**: PR's labeled as `critical`, `high-priority`, `P0`, or affecting security/authentication
   - **High Priority**: PR's affecting core user flows, payment systems, data integrity, or labeled `P1`
   - **Medium Priority**: PR's affecting secondary features, UI improvements, or performance
   - **Low Priority**: Minor bug fixes, cosmetic changes, or documentation

3. **Performance Testing**: Include performance test cases ONLY if user requested "performance" or "all" test types AND:
   - PR affects API endpoints
   - PR modifies database queries or data processing
   - PR changes rendering logic or component architecture
   - PR is labeled with `performance` or affects high-traffic areas

### For Repository-based Test Jams:
1. **Fetch Recent PR's** using MCP GitHub tools:
   - Query PR's merged in the last 4 weeks
   - **Extract repository name and ticket IDs** from each PR
   - Filter by priority labels and areas affected
   - Focus on the most critical changes first
   - Group test cases by PR when multiple PR's are included

2. **Priority Analysis**:
   - Identify PR's with `release`, `critical`, `high-priority` labels
   - Group PR's by component/feature area
   - Prioritize PR's affecting multiple areas of the codebase
   - Include performance testing scenarios ONLY if user requested "performance" or "all" test types

### For PRD-based Test Jams:
1. **Collect PRD Information**:
   - **PRD URL**: Must be provided by user
   - **PRD Contents**: Full text must be pasted by user
   - Both are required for proper test case generation

2. **Analyze PRD Content**:
   - **Extract PRD Title** from the document (first heading or title)
   - **Identify sections** within the PRD (e.g., "User Stories", "Acceptance Criteria", "Technical Requirements")
   - Extract feature requirements and acceptance criteria per section
   - Identify user flows and scenarios described in each section
   - Note technical requirements and constraints
   - Understand success metrics and KPIs

3. **Test Case Generation from PRD**:
   - Convert acceptance criteria into test cases **per PRD section**
   - Create test cases for each user flow described
   - Include edge cases and error scenarios
   - Add integration test cases for cross-system features
   - **Track which PRD section each test case comes from**

4. **PRD Test Case Naming Format**:
   - **Format**: `[PRD: PRD-Title] [Section-Name] Test Case Description`
   - **Example**: `[PRD: SMS Scheduling Feature] [User Stories] Verify user can schedule SMS for future delivery`
   - **Example**: `[PRD: Payment Integration] [Acceptance Criteria] Validate payment processing flow`
   - **Example**: `[PRD: Dashboard Redesign] [Technical Requirements] Test API response time under load`

5. **PRD Traceability**:
   - Include PRD URL in test case Pre-conditions or Notes
   - Reference specific PRD section in test case Objective
   - Format: "Based on PRD section: [Section Name] - [PRD URL]"
   - This allows testers to reference the original requirements

6. **Enhanced CSV Format for PRD-based Tests**:
   - Add **PRD Reference** column: `PRD: [Title] | Section: [Section Name] | URL: [PRD URL]`
   - See [csv-formats.md](../../../../qualityforge/templates/csv-formats.md) for complete format specifications

### For Jira-based Test Jams:
1. **Process Jira Ticket**:
   - Extract the Jira ticket ID from the provided file or URL (e.g., PROJ-1234, TXPLAT-3858)
   - Parse ticket content including:
     * Summary and description
     * Acceptance criteria
     * User stories
     * Technical requirements
     * Linked issues or dependencies
   - Extract Jira URL for traceability

2. **Auto-discover Related PRs**:
   - **If NO PRs are explicitly provided**, automatically search for PRs associated with the Jira ticket:
     * Use `mcp_github-mcp_search_issues` with query: `"[TICKET-ID] is:pr"` (e.g., `"PROJ-1234 is:pr"`)
     * Search across relevant repositories if known, or org-wide if not specified
     * Look for PRs with ticket ID in:
       - PR title (e.g., "PROJ-1234: Add new feature")
       - PR description/body
       - PR labels
       - Branch names
     * Include both open and merged PRs related to the ticket
   - **If PRs ARE explicitly provided**, use those PRs directly (no auto-search needed)
   - Notify user of discovered PRs: "Found X PRs associated with [TICKET-ID]"

3. **Combined Analysis**:
   - Analyze Jira ticket requirements as the primary source
   - Use discovered PRs to understand implementation details
   - Cross-reference Jira acceptance criteria with PR changes
   - Identify any gaps between Jira requirements and PR implementation

4. **Test Case Generation from Jira**:
   - Convert acceptance criteria into test cases
   - Create test cases for each user story
   - Include edge cases and error scenarios from description
   - Reference both Jira ticket AND related PRs in test cases

5. **Jira Test Case Naming Format**:
   - **Format**: `[TICKET-ID] Test Case Description`
   - **Example**: `[PROJ-1234] Verify user can complete checkout flow`
   - **Example**: `[TXPLAT-3858] Validate SMS webhook delivery`
   - If related PR is found, optionally add repo context: `[repo/name] [TICKET-ID] Test Case Description`

6. **Jira Traceability**:
   - Include Jira ticket URL in test case Pre-conditions or Notes
   - Reference specific acceptance criteria or user stories
   - Link related PRs discovered during auto-search
   - Format: "Based on Jira ticket: [TICKET-ID] - [Jira URL] | Related PRs: [PR URLs]"

### Mabl Integration (Optional):
1. **Query Existing Tests**:
   - Search Mabl for tests related to the component/feature
   - Review test coverage for the affected areas
   - Identify automated vs manual test gaps

2. **Enhance Test Cases with Mabl Data**:
   - Add "Automation Status" field: `Can be automated`, `Already automated in Mabl`, `Manual only`
   - Include Mabl test ID references when applicable
   - Note: `See Mabl test: [test-id] for automated coverage`
   - Suggest automation for repetitive or regression tests

3. **Coverage Gap Analysis**:
   - Identify areas not covered by existing Mabl tests
   - Prioritize manual testing where automation gaps exist
   - Recommend new Mabl test creation for high-value scenarios
   - Focus manual testing on exploratory and edge cases

## Test Case Generation

### Test Case Structure

**CSV Formats**: See [qualityforge/templates/csv-formats.md](../../../../qualityforge/templates/csv-formats.md) for detailed format specifications.

**Format Selection**:
- **Standard**: PR-based test jams (no Mabl)
- **Enhanced**: PR-based with Mabl integration
- **PRD**: PRD-based test jams
- **Full Enhanced**: PRD-based with Mabl integration

**Key Requirements**:
- All execution tracking columns (Status, Tester, Date Tested, Actual Results, Notes, Bug ID) must be initialized as **EMPTY/BLANK**
- Participants fill these during test execution
- Include appropriate optional columns (Automation Status, Mabl Reference, PRD Reference) based on test jam type

### Test Case Categories:

| Category | Focus |
|----------|-------|
| Functional Testing | Core feature functionality |
| UI/UX Testing | Visual and interaction testing |
| Integration Testing | Cross-component interactions |
| Regression Testing | Ensure existing functionality isn't broken |
| Performance Testing | Load, response time, resource usage |
| Security Testing | Authentication, authorization, data protection |
| Cross-Browser Testing | Browser compatibility |
| Accessibility Testing | WCAG compliance, screen readers |
| API Testing | Endpoint validation, error handling |
| Mobile/Responsive Testing | Device compatibility |

### CRITICAL: Category Filtering (STRICT ENFORCEMENT)

**MANDATORY RULE**: Generate test cases ONLY for the test category(ies) explicitly specified by the user in Step 3 (maps to CSV **Category** column).

**Filtering Logic**:
1. **Parse User Input**: From Step 3, question 1, extract the exact test type(s) the user requested
2. **Map to Categories**: Match their input to the categories in the table above
3. **Strict Generation**: Create test cases ONLY for the matched categories
4. **No Assumptions**: Do NOT add "related" or "recommended" test types unless explicitly requested

**Examples**:
- User says: "functional" or "functional testing"
  - Generate: Functional Testing test cases ONLY (Category column)
  - Do NOT generate: Regression, Performance, Security, or any other types

- User says: "functional, regression"
  - Generate: Functional Testing + Regression Testing test cases ONLY (Category column)
  - Do NOT generate: Performance, Security, or any other types

- User says: "all" or "comprehensive" or "all types"
  - Generate: ALL test types from the categories table

- User says: "performance"
  - Generate: Performance Testing test cases ONLY (Category column)
  - Do NOT generate: Functional, Regression, or any other types

**Validation Checkpoint**:
Before generating CSV files, verify:
1. List out the test type(s) the user requested
2. Confirm that EVERY test case in your generated list matches one of those types
3. Confirm that NO test cases exist for types that were NOT requested
4. If you find any test cases that don't match requested types, REMOVE them
5. **CRITICAL FORMAT ENFORCEMENT**: Pre-conditions, Test Steps, Expected Results MUST use NUMBERED LISTS
   - **RULE**: ALWAYS use numbered lists (1., 2., 3.)
   - **RULE**: NEVER use bullet points (-, *, •, +)
   - **RULE**: NEVER use semicolon-separated lists
   - **RULE**: NEVER use any other format
   - **ACTION**: Call `enforce_numbered_lists()` on all three fields for every test case
   - **VERIFY**: Every test case has numbered lists in all three fields
   - **WHY**: Bullet points cause Excel `=NAME?` errors - NO EXCEPTIONS

**Example Validation**:
```
User requested: "functional testing"
Generated test cases review:
- TC-001: Functional Testing 
- TC-002: Functional Testing 
- TC-003: Performance Testing == REMOVE - not requested
- TC-004: Functional Testing 
Final count: 3 Functional test cases (1 removed)

Formatting validation:
- Pre-conditions format: ✓ Numbered lists (1., 2., 3.)
- Test Steps format: ✓ Numbered lists (1., 2., 3.)
- Expected Results format: ✓ Numbered lists (1., 2., 3.)
- No bullet points (-) found: ✓ Pass
```

### Priority Levels:
- **Critical/P0**: Core functionality, security, data integrity
- **High/P1**: Important user flows, payment/billing, authentication
- **Medium/P2**: Secondary features, UI improvements
- **Low/P3**: Nice-to-have, cosmetic changes

### Test Case Requirements:
1. Each test case must include:
   - Unique Test ID (TC-001, TC-002, etc.)
   - Clear category and name **with PR context prefix**
   - Appropriate priority level
   - Test type (Manual, Automated, Manual + Automated) - **Column must be named "Type" not "Test Type"**
   - Component being tested
   - Clear objective
   - **Pre-conditions** (numbered list: 1., 2., 3. with newlines)
   - **Test Steps** (numbered list: 1., 2., 3. with newlines)
   - **Expected Results** (numbered list: 1., 2., 3. with newlines)
   - **Execution tracking columns** (Status, Tester, Date Tested, Actual Results, Notes, Bug ID)
     * **Important**: Initialize all execution tracking columns as EMPTY/BLANK
     * These are filled by participants during the test jam session
     * Do NOT pre-populate these fields

2. **CSV Generation Requirements**:
   - **MUST use Python's csv.writer** (not manual string formatting)
   - **MUST sanitize cells** to prevent formula injection
     * Prefix cells starting with `=`, `+`, `-`, `@`, `\t`, `\r` with single quote `'`
     * Prevents `#NAME?` errors in Excel/Google Sheets
   - **Multi-line content**: Keep newlines (`\n`) - csv.writer will quote cells automatically
   - **Formatting Standard**: Use numbered lists (1., 2., 3.) for Pre-conditions, Test Steps, and Expected Results
     * **CRITICAL**: NEVER use bullet points (`-`, `*`, `•`) - ONLY use numbered lists (`1.`, `2.`, `3.`)
     * **WHY**: Bullet points starting with `-` cause Excel `=NAME?` errors (Excel thinks `-` is a formula)
     * **Format examples** (content varies per test case):
       - **Pre-conditions**: `1. User is logged in\n2. Valid credentials available\n3. SMS credits > 10`
       - **Test Steps**: `1. Navigate to dashboard\n2. Click button\n3. Verify result`
       - **Expected Results**: `1. Page loads\n2. Button is visible\n3. Result displays`
     * Use numbered format structure - actual wording should match your specific test scenario
   - **Display in Excel/Sheets**: Multi-line fields appear as actual line breaks within cells
   - **Column 5**: Must be "Type" not "Test Type"
   - **Why**: Prevents formula injection + preserves natural multi-line formatting + consistent professional appearance

### Test Name Format with PR Context:
**Format**: `[repo-org/repo-name] [TICKET-ID] Test Case Name`

**Examples**:
- `[mctx/messaging-app] [TXPLAT-3858] SMS Send Success Flow`
- `[org/sms-service] [MUL-4978] SMS Dashboard Display - Chrome`
- `[org/project] [TXPLAT-3511] SMS Click Event Webhook`

**Extracting PR Context**:
1. **Repository**: Extract from PR URL
   - From: `https://github.com/org/messaging-app/pull/123`
   - Extract: `[mctx/messaging-app]`

2. **Ticket ID**: Extract from PR title or description
   - Look for patterns: TXPLAT-####, MUL-####, MCVULN-####, etc.
   - From PR title: "TXPLAT-3858: Add SMS webhook support"
   - Extract: `[TXPLAT-3858]`
   - If no ticket found in title, check PR description
   - If multiple tickets, use the primary one (first mentioned)
   - If no ticket found, use: `[NO-TICKET]`

**Application**:
- Prefix EVERY test case name with this format
- Apply to both master CSV and individual participant CSV files
- Makes it easy to trace test cases back to source PR
- Helps with test case organization and reporting

2. **Comprehensive Coverage** (within the user-selected test types):
   - Create test cases for happy paths
   - Include negative/edge cases
   - Add error handling scenarios
   - Include cross-browser tests ONLY if user requested "cross-browser" or "all" test types
   - Add accessibility tests ONLY if user requested "accessibility" or "all" test types
   - Include performance tests ONLY if user requested "performance" or "all" test types
   - **Remember**: Only generate test cases for the types the user explicitly requested

3. **Clarity and Detail**:
   - Steps should be explicit and actionable
   - Expected results should be measurable
   - Include specific values, URLs, or data when relevant
   - Reference specific UI elements or API endpoints

## Distribution Logic

### Splitting Test Cases:
1. **Calculate distribution**: `test_cases_per_participant = total_test_cases / num_participants`
2. **Smart distribution**:
   - If uneven division, distribute extra cases to early participants
   - Keep related test cases together when possible
   - Balance priority levels across participants
   - Consider grouping by category or component

### CSV Generation:
1. **Individual Files**: `testjam_participant_1.csv`, `testjam_participant_2.csv`, etc.
2. **Master File**: `testjam_all_test_cases.csv` - Contains ALL test cases in one file
3. **Output Location**: `test-jams/[session-name]/` (relative to repo root)
4. **Session Naming**: Use format: `YYYY-MM-DD_[repo-or-pr-name]`

### CSV Formatting Requirements

**CRITICAL: Use Python's csv.writer for bulletproof CSV generation**

See [CSV-GENERATION.md](CSV-GENERATION.md) for the complete implementation code and requirements.

Example structure:
```
test-jams/
  └── 2025-11-20_sms-features/
      ├── testjam_all_test_cases.csv      # Master file with ALL test cases
      ├── testjam_participant_1.csv       # Subset for participant 1
      ├── testjam_participant_2.csv       # Subset for participant 2
      ├── testjam_participant_3.csv       # Subset for participant 3
      └── test_jam_summary.md
```

**Important**: 
- Generate the master file FIRST with all test cases, then split them into individual participant files
- Always use Python's `csv.writer` for writing CSV files (never manual string formatting)
- Replace all `\n` newlines with ` | ` in Pre-conditions, Test Steps, and Expected Results BEFORE writing to CSV

## Summary Report

After generating CSV files, create a `test_jam_summary.md` with:

```markdown
# Test Jam Summary

**Date**: [Date]
**Focus**: [PR's or Repo]
**Participants**: [Number]
**Total Test Cases**: [Number]

## Overview
[Brief description of what's being tested]

## PR's/Changes Included
[List of PR's with titles and links]

## Critical Areas
[List of high-priority areas requiring focused testing]

## Test Case Distribution
- Participant 1: [X test cases] - Focus: [Area]
- Participant 2: [X test cases] - Focus: [Area]
- ...

## Testing Timeline
[Timeline information]

## Success Criteria
[What defines a successful test jam]

## Notes
[Any additional context or instructions]
```

## MCP Integration

See [MCP-INTEGRATION.md](MCP-INTEGRATION.md) for detailed MCP tool usage.

### Primary Sources (Prioritized):
1. **GitHub PR's** - Main input source
2. **PRD's (Product Requirements Documents)** - Alternative to PR's for early-stage testing

### Error Handling:
- If PR/Repo not found, ask user to verify the information
- If insufficient permissions, notify user and suggest alternatives
- If API rate limits hit, inform user and suggest waiting or reducing scope
- If Mabl MCP unavailable, proceed without it (it's optional)

## Best Practices

1. **Balance Coverage and Feasibility**: Don't create 500 test cases for a small PR
2. **Quality Over Quantity**: Focus on meaningful test scenarios
3. **Consider Testing Time**: Each test case should be completable in 5-15 minutes
4. **Include Setup Instructions**: Ensure pre-conditions are clear
5. **Add Context**: Reference specific code changes or issues when relevant
6. **Think Like a Tester**: What could break? What edge cases exist?
7. **Cross-Functional Perspective**: Consider product, engineering, and user viewpoints
8. **Leverage Existing Automation**: Check Mabl for existing coverage to avoid duplicate effort
9. **Identify Automation Opportunities**: Suggest which manual tests should become automated
10. **Prioritize Manual Testing**: Focus manual effort on areas not covered by automation

## Example Workflows

**Quick Reference**:
1. **PR-based with Mabl**: Analyze PR → Fetch PR details → Query Mabl coverage → Generate tests → Split across participants
2. **PRD-based**: Parse PRD sections → Extract requirements → Generate tests with PRD traceability → Link to requirements
3. **Repository-based**: Fetch recent merged PRs → Prioritize by impact → Generate comprehensive test coverage

## Output Format Selection

After generating test cases, ask the user how they would like to output them:

```
📤 Test Case Output Options

How would you like to output these test cases?

[A] CSV File (default)
    Export to spreadsheet format for test jams

[B] Jira Tickets
    Create test case tickets in a Jira project

[C] Both CSV and Jira
    Export CSV and also create Jira tickets

👉 Choice (A, B, or C):
```

### Option A: CSV Only (Default)
Proceed to standard CSV generation and Output Confirmation below.

### Option B or C: Jira Ticket Creation

If user selects B or C, guide them through Jira configuration:

#### Step 1: Jira Project
```
🎯 Jira Project Configuration

What Jira project should these test cases be created in?
Example: EEE, TXPLAT, TESTING

👉 Project key:
```

Verify project exists:
```python
projects = user-DAST-Orch-jira_search_issues(projectKeys=[project_key], maxResults=1)
```

#### Step 2: Epic Configuration
```
📁 Epic Configuration

How would you like to organize these test case tickets?

[A] Add to an existing epic
    Link all test cases to an epic that already exists

[B] Create a new epic containing these test cases
    I'll create a new epic first, then link all tickets to it

👉 Choice (A or B):
```

**Option A - Existing Epic:**
```
👉 Enter the existing epic key (e.g., EEE-10332):
```

**Option B - New Epic:**
```
📝 New Epic Details

1. Epic name/summary:
   Example: "Test Jam - Feature X - FY26 Q1"
   👉 Epic name:

2. Epic description (optional):
   👉 Description (or press Enter to skip):
```

#### Step 3: Assignee Configuration
```
👤 Assignee Configuration

Who should these test cases be assigned to?

[A] Assign to participants (round-robin)
    Distribute based on test jam participant allocation

[B] Specific user
    Assign all to one person

[C] Leave unassigned
    No assignee - can be assigned during sprint planning

👉 Choice (A, B, or C):
```

**Option A** uses the participant list from earlier, distributing tickets the same way as CSVs.

#### Step 4: Additional Labels
```
🏷️ Additional Labels

Default labels that will be applied:
- test-case
- QualityForge
⚠️ Note: Do not remove these default labels - they are used for reporting purposes.

Would you like to add any additional labels? (comma-separated)
Example: domain-auth, fy26-q1, test-jam

👉 Additional labels (or press Enter to skip):
```

#### Jira Ticket Format
For each test case, create a Task ticket:

**Summary**: `[{test_id}] {test_name}`

**Description** (Markdown format):
```markdown
## Test Case
{test_id}: {test_name}

## Pre-conditions
{pre_conditions}

## Test Steps
{test_steps}

## Expected Result
{expected_result}

---
*Created via QualityForge Test Jam Generation*
```

**Priority**: Based on test case priority field (or P3 default)

**Labels**: `test-case`, `QualityForge`, + user-specified labels

#### Jira Creation Progress
```
🚀 Creating test case tickets in Jira...

Creating epic: {epic_name}
✅ Epic created: {epic_key}

Creating test case tickets:
[████████████████████░░░░░░░░░░] 34/47

✅ {ticket_key}: [{test_id}] {test_name} → {assignee}
```

#### Jira Completion Summary
```
✅ Jira Tickets Created!

Epic: {epic_key} "{epic_name}"
  https://jira.example.com/browse/{epic_key}

Test Cases Created: {count}
  ✅ Successfully created: {success}
  ❌ Failed: {errors}

{if round_robin}
Assignment Distribution:
  - Participant 1: {count} tickets
  - Participant 2: {count} tickets
{/if}

View all tickets:
  JQL: project = {project_key} AND labels = "QualityForge" AND parent = {epic_key}
```

If Option C was selected (both CSV and Jira), continue to CSV output confirmation below.

---

## Output Confirmation

After generation, provide a summary:
```
✅ Test Cases Created Successfully!

📁 Location: test-jams/[session-name]/

📊 Summary:
- Total Test Cases: [X]
- Test Types Generated: [List ONLY the types that were generated, matching user's request]
- Test Types NOT Included: [List types that were NOT generated, if user didn't request them]
- Participants: [Y]
- Files Generated:
  - testjam_all_test_cases.csv ([X] test cases) ⭐ Master file
  - testjam_participant_1.csv ([Z] test cases)
  - testjam_participant_2.csv ([Z] test cases)
  - ...
  - test_jam_summary.md

✅ Validation Confirmed:
- All [X] test cases match the requested test type(s): [list types]
- No test cases were generated for unrequested types
- CSV generation: Used csv.writer with QUOTE_MINIMAL
- CSV formatting: Column 5 is "Type", multi-line content uses numbered lists (1., 2., 3.)
- All Pre-conditions, Test Steps, and Expected Results use NUMBERED LISTS (not bullet points)
- Formula injection prevention: All cells sanitized (no Excel =NAME? errors)
- All special characters (commas, quotes) handled automatically
- Quality gate: `python3 qualityforge/test_jam_quality_gate.py --test-jam [session-name]` (expect PASS)

🎯 Next Steps:
1. Review the test_jam_summary.md for overview
2. Use testjam_all_test_cases.csv for complete test plan reference
3. Distribute individual CSV files to participants
4. Brief participants on focus areas
5. Schedule test jam session
6. Track results and report findings

Need any adjustments? Just let me know!
```

---

## Step 5: Google Sheets Creation (Optional)

After CSVs are generated and validated, prompt the user:

```
📊 Google Sheets Creation

Would you like me to create a formatted Google Sheet for this test jam?
This creates a professional, ready-to-use spreadsheet matching the QCoE standard format.

The sheet will include:
- Cover page with test jam details and instructions
- Test Accounts tab (if accounts provided)
- Bug Tracking tab (ready for issue logging)
- Individual tabs for each participant ({num_participants} tabs)

👉 Create Google Sheet? (yes/no)
```

### If User Says Yes

**Step 5a: Participant Names**

```
👥 Participant Tab Names

How should the participant tabs be named?

[A] Use numbered tabs
    participant_1, participant_2, participant_3, ...

[B] Enter participant names
    I'll ask you to provide the names

👉 Choice (A or B):
```

If B:
```
Please enter the {num_participants} participant names (comma-separated):
Example: John Healy, Andre Pardue, Gregory Lehman

👉 Names:
```

**Step 5b: Create Spreadsheet**

Use MCP tools to create the formatted spreadsheet:

1. **Create spreadsheet** with `create_spreadsheet`:
   - Title: `{session_name} Test Jam`
   - Sheet names: `Cover`, `Test Accounts`, `Bug Tracking`, + participant tabs

2. **Write Cover sheet** with `sheets_write`:
   - Row 1: Test Jam title (bold, large, can include emoji)
   - Desired Outcomes section with yellow highlight
   - Key Links section (two-column layout)
   - Instructions section (numbered list)
   - Key for tabs section

3. **Write Test Accounts sheet** (if accounts provided during flow)

4. **Write Bug Tracking sheet** with headers:
   - ID, Bug Description, Jira Link, Priority, Status, Screenshot, Notes

5. **Write participant sheets** with test cases from CSV:
   - Load from `testjam_participant_{n}.csv`
   - Write headers + test case data
   - Add PREREQS rows where applicable

6. **Apply formatting** with `sheets_batch_update`:
   - Header formatting: blue background `#4A86E8`, white bold text
   - PREREQS row highlighting: yellow `#FFF2CC`
   - Alternating row colors: white / `#F3F3F3`
   - Borders: thin `#D9D9D9` on all cells
   - Column widths optimized for content
   - Text wrap enabled on content columns
   - Frozen header rows
   - Results dropdown with data validation: `NOT STARTED`, `IN PROGRESS`, `PASSED`, `FAILED`
   - Conditional formatting on Results column:
     - PASSED → Green background `#D9EAD3`
     - FAILED → Red background `#F4CCCC`
     - IN PROGRESS → Yellow background `#FFF2CC`
     - NOT STARTED → No color

### Formatting Specification (Match PDF Reference)

Based on the QCoE Test Jam standard format:

#### Cover Sheet Design

| Element | Specification |
|---------|---------------|
| Title | Row 1: Bold, large font (14pt), emoji allowed |
| Section Headers | Bold, background `#4A86E8` (blue), white text |
| "Desired Outcomes" | Yellow highlight `#FFF2CC` for content |
| "Key Links" | Two-column layout: labels left, values/links right |
| "Instructions" | Numbered list, normal formatting |
| "Key for tabs" | Bold labels, descriptive text |

#### Test Accounts Sheet

| Column | Width | Header Style |
|--------|-------|--------------|
| Account ID | 100px | Bold, `#4A86E8` background, white text |
| Plan | 80px | Same |
| Username | 200px | Same |
| Password | 100px | Same |
| Status | 80px | Same |
| Assignee | 120px | Same |

- Alternating row colors: white / `#F3F3F3`
- Borders: thin `#D9D9D9`

#### Bug Tracking Sheet

| Column | Header |
|--------|--------|
| ID | Test case ID that found the bug |
| Bug Description | Description of the issue |
| Jira Link | Link to created Jira ticket |
| Priority | P0/P1/P2/P3 |
| Status | Open/In Progress/Fixed/Won't Fix |
| Screenshot | Link to evidence |
| Notes | Additional context |

- Header row: Bold, `#4A86E8` background, white text
- Empty rows ready for data entry

#### Participant Test Case Sheets

| Column | Width | Notes |
|--------|-------|-------|
| ID | 80px | Test ID (TC-001, PREREQS, etc.) |
| Component | 150px | Component under test |
| Objective | 200px | Test objective |
| Conditions | 250px | Pre-conditions (numbered lists) |
| Steps to Test | 300px | Test steps (numbered lists) |
| Expected Results | 300px | Expected outcomes (numbered lists) |
| Tester | 100px | Pre-filled with participant name |
| Testing Evidence | 200px | Empty - tester fills in |
| Results | 100px | Dropdown: PASSED / FAILED / NOT STARTED / IN PROGRESS |

**Row Formatting:**
- PREREQS rows: Yellow background `#FFF2CC`, bold ID
- Regular test rows: Alternating white / `#F3F3F3`
- Header row: `#4A86E8` background, white bold text, frozen
- Text wrap enabled on all content columns
- Borders: thin `#D9D9D9` on all cells

### Success Output

```
✅ Google Sheet Created!

📊 Spreadsheet: {session_name} Test Jam
🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/

Tabs created:
- Cover (instructions and overview)
- Test Accounts (credentials if provided)
- Bug Tracking (ready for issue logging)
- {participant_1} ({X} test cases)
- {participant_2} ({X} test cases)
- ...

Formatting applied:
✅ Header styling (blue #4A86E8, white bold text)
✅ PREREQS rows highlighted (yellow #FFF2CC)
✅ Alternating row colors
✅ Results dropdown with conditional formatting
✅ Column widths optimized
✅ Text wrap enabled
✅ Header rows frozen

🎯 The spreadsheet is ready to share with participants!
```

### If User Says No

```
👍 Skipping Google Sheets creation.

Your CSVs are ready in: test-jams/{session-name}/
```

Continue to Accuracy Pass options.

---

### Optional: Accuracy Pass (Content Validity)

**Purpose**: Keep generation fast by default, but allow an optional post-generation pass to improve **accuracy** (AC coverage, consistency, specificity) without changing the formatting rules above.

**Prompt (immediately after generating the CSVs + Output Confirmation)**:
```
✅ Test Cases Created Successfully!

Before you export/share, do you want QualityForge to run an accuracy check for this test jam?

Choose accuracy level:
1. Skip (fastest) — no accuracy checks (current behavior)
2. Quick (recommended) — 10–20s automated heuristics, minimal/no questions
3. Thorough — Quick + agent-driven semantic AC↔test mapping, gap detection, and rubric scoring (1–3 min)

👉 Enter 1, 2, or 3:
```

#### Quick Accuracy Check (Option 2)

```
⚡ Quick Accuracy Check (10–20s)

What this checks:
- AC Coverage: do tests map to the Acceptance Criteria you provided?
- Completeness: pre-conditions / steps / expected results are present and verifiable
- Consistency: steps and expected results don't contradict pre-conditions

Running checks now...
```

**Important**: Use requirements/ACs already collected earlier in the flow (PRD content, Jira ticket ACs, PR description). Do NOT ask the user to re-paste this information. Only prompt when no ACs are available in session context (see the Fallback below).

**Implementation (default — ACs available in session context)**:

When ACs ARE in session context, write them to a temp file and run with `--acs-file` (preferred for any non-trivial AC text):

```bash
# 1. Write the ACs collected earlier (one per line, e.g., "AC1: ...") to a temp file
cat > /tmp/{session-name}_acs.txt <<'EOF'
AC1: ...
AC2: ...
EOF

# 2. Run the analyzer with the AC file
python3 qualityforge/test_jam_accuracy.py --test-jam {session-name} --mode quick --acs-file /tmp/{session-name}_acs.txt
```

For very short AC blobs you may inline with `--acs-text` instead:

```bash
python3 qualityforge/test_jam_accuracy.py --test-jam {session-name} --mode quick --acs-text "$(cat <<'EOF'
AC1: ...
AC2: ...
EOF
)"
```

**Fallback (only if no ACs are in session context)**:

```
I don't see explicit Acceptance Criteria (ACs) in what you provided.

To run AC coverage mapping, choose one:
1. Paste ACs now
2. Skip AC coverage mapping (still run completeness/consistency checks)

👉 Enter 1 or 2:
```

If the user picks "Skip", run without ACs:

```bash
python3 qualityforge/test_jam_accuracy.py --test-jam {session-name} --mode quick
```

**Output (always — report-only, does not modify CSVs)**:

```
📄 Accuracy Report Generated

Location:
- test-jams/{session-name}/test_jam_quality_report.json

Included:
- AC coverage matrix (AC → test IDs)
- Flagged tests with reasons
```

After Quick completes, proceed to **High-severity findings remediation** (below) before continuing to Step 6.

#### Thorough Accuracy Check (Option 3)

A real Quick + agent-driven semantic pass. Gives you semantic AC↔test mapping (with confidence), missing-scenario detection, and per-test rubric scores.

**Important**: Same AC sourcing rule as Quick — use ACs already in session context (PRD, Jira, PR). Do NOT ask the user to re-paste; only prompt as a Fallback when none are available.

**Runbook**:

1. **Run Quick first** (gets the heuristic baseline and the AC coverage matrix):

   ```bash
   python3 qualityforge/test_jam_accuracy.py --test-jam {session-name} --mode quick --acs-file /tmp/{session-name}_acs.txt
   ```

2. **Load the inputs** the agent needs for the semantic pass:
   - `test-jams/{session-name}/test_jam_quality_report.json` (Quick findings + counts)
   - `test-jams/{session-name}/testjam_all_test_cases.csv` and the per-participant CSVs
   - The ACs / PRD / Jira / PR context already collected earlier in the flow
   - The rubric: [`qualityforge/templates/TEST-CONTENT-RUBRIC.md`](../../../../qualityforge/templates/TEST-CONTENT-RUBRIC.md)
   - The output schema: [`qualityforge/templates/THOROUGH-REPORT-SCHEMA.md`](../../../../qualityforge/templates/THOROUGH-REPORT-SCHEMA.md)

3. **Agent semantic pass** — score every test against the rubric and produce:
   - **AC coverage matrix** with per-AC confidence (`high` / `medium` / `low`) and a one-line reasoning for each AC↔test link
   - **Coverage gaps**: missing negative / boundary / error-path / accessibility / permission scenarios (cite the AC or feature each gap relates to)
   - **Per-test rubric scores** (clarity, atomicity, verifiability, traceability, expected-result specificity)
   - **Recommendations** per finding: `rewrite` / `split` / `merge` / `regenerate`

4. **Merge with the Quick findings** and write the merged report to:

   `test-jams/{session-name}/test_jam_quality_report.json`

   extended with a top-level `"thorough"` block that conforms to `THOROUGH-REPORT-SCHEMA.md`. Preserve the existing Quick `findings` and `counts` so downstream steps (and the High-severity remediation flow below) keep working unchanged.

**Output summary**:

```
📊 Thorough Accuracy Report

AC Coverage (semantic):
- ACs analyzed: {R}
- Covered with high confidence: {Hc}/{R}
- Covered with medium confidence: {Mc}/{R}
- Not covered: {U}/{R}

Quality flags (Quick + Thorough):
- High severity: {H}
- Medium severity: {M}
- Low severity: {L}

Top scenario gaps:
- Missing negative coverage for: {Feature X}
- Missing boundary coverage for: {Field Y}
```

After Thorough completes, proceed to **High-severity findings remediation** (below) before continuing to Step 6.

#### High-severity findings remediation (runs after Quick or Thorough)

After either accuracy mode finishes, inspect `report["counts"]["high"]` and (when ACs were provided) `report["counts"]["ac_coverage_gaps"]`. If either is greater than zero, run this prompt **before** Step 6 / final summary:

```
⚠️ {N} high-severity content findings detected before export:
- {M} test cases missing Test Steps
- {K} test cases missing Expected Results
- {J} ACs without any covering test  (only shown if AC mapping ran)

How would you like to proceed?
1. Regenerate just the flagged test cases (recommended)
2. View details and continue manually
3. Continue without changes

👉 Enter 1, 2, or 3:
```

Use the `high_severity_test_ids(report)` helper from `qualityforge.test_jam_accuracy` to get the deduplicated list of Test IDs to act on:

```bash
python3 -c "
import json, sys
sys.path.insert(0, 'qualityforge')
from test_jam_accuracy import high_severity_test_ids
report = json.loads(open('test-jams/{session-name}/test_jam_quality_report.json').read())
print('\n'.join(high_severity_test_ids(report)))
"
```

**Option 1 — Targeted regeneration** (preserves IDs, participant assignment, and CSV ordering):

1. Call `high_severity_test_ids(report)` to get the list of flagged Test IDs.
2. For each flagged Test ID, regenerate ONLY that row using the original PRD / PR / Jira context already in session — preserving:
   - Test ID
   - Participant assignment (which `testjam_participant_*.csv` it lives in)
   - Category and Priority
3. Write the regenerated rows in-place:
   - Update the row in the matching `testjam_participant_*.csv`
   - Update the same row in `testjam_all_test_cases.csv`
   - Re-apply the same CSV formatting rules from earlier steps (numbered lists for Pre-conditions / Test Steps / Expected Results, formula-injection prefixing for cells starting with `=`, `+`, `-`, `@`, etc.)
4. Re-run the same Quick command from Step 5 to verify, then report the new counts to the user:

   ```
   ✅ Regenerated {N} test cases.
   - High severity remaining: {H'}
   - Medium severity remaining: {M'}
   ```

5. If `H' > 0`, surface the remaining high-severity findings to the user and ask whether to retry regeneration, view details, or continue.

**Option 2 — View details and continue manually**: print the per-finding details from `report["findings"]` (filtered to `severity == "high"`) so the user can fix them by hand later, then proceed to Step 6 without modifying CSVs.

**Option 3 — Continue without changes**: proceed straight to Step 6.

**Important**:
- The accuracy analyzer itself is still report-only. Targeted regeneration (Option 1) is the **only** path that mutates CSVs in this flow, and it only runs with the user's explicit consent.
- Step 6 (Coverage Map) and any post-accuracy share/distribution actions must wait until this remediation prompt has been offered (or skipped automatically because `high == 0` and `ac_coverage_gaps == 0`).

---

## Step 6: Test Coverage Map (Optional)

**Purpose**: After test cases are generated and validated, offer to create a formatted Test Coverage Map that maps requirements/acceptance criteria to test cases for traceability and gap analysis.

**Trigger**: After the accuracy check completes (or is skipped), present this option:

```
📊 Test Coverage Map (Optional)

Would you like me to generate a Test Coverage Map?

This creates a professional document that:
- Maps requirements/ACs to your test cases
- Identifies coverage gaps
- Calculates coverage metrics
- Provides a traceability matrix
- Exports as both Markdown and DOCX (with company branding)

👉 Generate coverage map? (yes/no):
```

### If User Says Yes

**Important**: Use requirements/ACs already collected earlier in the flow (from PRD, Jira ticket, or PR). Do NOT ask the user to re-paste this information.

**Sources for Requirements (in priority order)**:
1. **PRD content** - if user provided PRD in Step 1
2. **Jira ticket ACs** - if user provided Jira ticket
3. **PR description ACs** - if extractable from PR
4. **ACs provided during accuracy check** - if user pasted them in Step 5

**If no requirements are available in session context**:
```
⚠️ I don't have requirements/ACs in the current session context.

To generate a coverage map, please provide one of:
1. PRD content or URL
2. Jira ticket with acceptance criteria
3. List of requirements/ACs to map

👉 Paste requirements or enter 'skip' to cancel:
```

**If user enters 'skip'**:
```
👍 Skipping coverage map generation.

Your test jam is complete! Files are in: test-jams/{session-name}/

Need anything else?
```
Return to main flow - do NOT proceed with DOCX generation.

### Coverage Map Generation

1. **Extract requirements** from session context (PRD, Jira, PR, or accuracy check ACs)
2. **Load test cases** from `testjam_all_test_cases.csv` in the session folder
3. **Generate mapping** using the template at `qualityforge/templates/TEST-COVERAGE-MAP-TEMPLATE.md`
4. **Calculate metrics**:
   - Total requirements identified
   - Requirements with test coverage
   - Coverage percentage
   - Gap analysis
5. **Write the markdown file** to: `test-jams/{session-name}/test_coverage_map.md`
   - Use the template structure
   - Replace all `<placeholders>` with actual data
   - Ensure all tables are properly formatted markdown

### Output Files

Generate two files in the test jam session folder:

1. **`test_coverage_map.md`** - Markdown format with:
   - Coverage Metrics Summary
   - Requirements to Test Cases Matrix
   - Test Cases by Category breakdown
   - Coverage Gaps and Recommendations
   - Traceability Matrix

2. **`test_coverage_map.docx`** - Professional Word document with:
   - company branding (Avenir Next For company font)
   - Acme Platform colors (Peppercorn headers)
   - Properly formatted tables
   - Ready for upload to Google Docs/Sheets

### DOCX Generation

**Run the DOCX generator** after creating the markdown file:

```bash
# Navigate to qualityforge/risk and set up venv if needed
cd qualityforge/risk

# Create/activate virtual environment (reuse if exists)
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate

# Install python-docx if not already installed
pip install python-docx -q

# Generate DOCX from the test jam folder
# Replace {session-name} with actual session folder name (e.g., 2026-02-13_tx-domain-auth-entri)
python3 generate_risk_docx.py --coverage-only ../../test-jams/{session-name}
```

**Important Notes**:
- The `--coverage-only` flag ensures only the coverage map DOCX is generated
- The path `../../test-jams/{session-name}` is relative from `qualityforge/risk/`
- The venv in `qualityforge/risk/.venv` is shared across all coverage map generations
- If you get "module not found" errors, ensure you activated the venv first

The generator automatically:
- Detects this is a test jam folder (not a risk analysis folder)
- Finds `test_coverage_map.md` and converts it
- Applies company branding (font, colors)
- Creates properly formatted tables

### Success Output

```
✅ Test Coverage Map Generated!

📁 Location: test-jams/{session-name}/

📊 Coverage Summary:
- Total Requirements: {X}
- Covered by Tests: {Y}
- Coverage: {Y/X * 100}%
- Gaps Identified: {X-Y}

📄 Files Created:
- test_coverage_map.md (Markdown)
- test_coverage_map.docx (Word document with company branding)

The DOCX file is ready for upload to Google Docs or sharing with stakeholders.

🎯 Next Steps:
1. Review coverage gaps
2. Add test cases for uncovered requirements (if needed)
3. Share coverage map with stakeholders
4. Include in test jam documentation

Need any adjustments to the coverage map?
```

### Coverage Map Template Structure

The coverage map follows this structure (see `qualityforge/templates/TEST-COVERAGE-MAP-TEMPLATE.md`):

```markdown
# Test Coverage Map

## Coverage Metrics Summary
| Metric | Value |
|--------|-------|
| Total Requirements | X |
| Covered Requirements | Y |
| Coverage Percentage | Z% |
| Uncovered Requirements | A |

## Requirements to Test Cases Matrix
| Req ID | Requirement | Test Cases | Coverage |
|--------|-------------|------------|----------|
| REQ-001 | ... | TC-001, TC-002 | ✅ Covered |
| REQ-002 | ... | - | ❌ Gap |

## Test Cases by Category
| Category | Count | Requirements Covered |
|----------|-------|---------------------|
| Functional | X | REQ-001, REQ-003 |
| Regression | Y | REQ-002 |

## Coverage Gaps and Recommendations
[List requirements without test coverage and recommended actions]

## Traceability Matrix
[Full bidirectional mapping: Requirements ↔ Test Cases]
```
