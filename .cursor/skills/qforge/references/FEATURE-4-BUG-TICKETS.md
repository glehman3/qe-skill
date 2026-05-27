# Feature 4: Bug Ticket Creation from Test Results

*When user selects Option 4, proceed with this workflow*

---

## Overview

Create Jira bug tickets from completed test results (Google Sheets or PDF export). This feature reads test execution data, identifies failed tests, and generates properly formatted bug tickets in your specified Jira project.

---

## MCP Verification

**Before starting the interactive flow**, verify MCP availability:

### Step 1: Check Jira MCP (REQUIRED)

Attempt to verify Jira access using Atlassian MCP bundle MCP:
```
Call: user-atlassian-mcp-get_jira_user_info
```

- **If unavailable or error**: Display setup instructions and STOP
  ```
  ❌ Jira MCP not available
  
  Bug ticket creation requires Jira access via Atlassian MCP bundle MCP.
  
  Please ensure:
  1. Atlassian MCP bundle MCP is configured in Cursor
  2. You have authenticated with your SSO credentials
  
  Run /qforge again after setup is complete.
  ```
- **If available**: Display "✅ Jira MCP detected and ready"

### Step 2: Check Google Drive MCP (OPTIONAL)

Attempt to verify Google Sheets access:
```
Call: user-google-drive-mcp-sheets_get_metadata (with any test spreadsheet)
```

Or simply check if `user-google-drive-mcp-sheets_read` tool is available.

- **If available**: Set `GOOGLE_SHEETS_AVAILABLE = true`, display "✅ Google Drive MCP detected - can read Google Sheets directly"
- **If unavailable**: Set `GOOGLE_SHEETS_AVAILABLE = false`, display "ℹ️ Google Drive MCP not available - will use PDF export"

---

## Interactive Flow

### Step 1: Input Source

**If `GOOGLE_SHEETS_AVAILABLE = true`:**
```
📊 Bug Ticket Creation from Test Results

How would you like to provide your test results?

[A] Google Sheet URL (recommended)
    I'll read the sheet directly

[B] PDF Export
    Export your Google Sheet as PDF and provide the file path

[C] Return to Main Menu

👉 Choice (A, B, or C):
```

**If `GOOGLE_SHEETS_AVAILABLE = false`:**
```
📊 Bug Ticket Creation from Test Results

ℹ️ Google Drive MCP is not available, so I'll need a PDF export of your test results.

Please export your Google Sheet as PDF:
1. Open your Google Sheet
2. File → Download → PDF (.pdf)
3. Save the file locally

👉 Provide the path to your PDF file (or 'cancel' to return):
```

---

### Step 2: Collect Test Results

#### Option A: Google Sheet

```
📋 Google Sheet Input

Please provide the Google Sheet URL:
Example: https://docs.google.com/spreadsheets/d/1abc123.../edit

👉 Google Sheet URL:
```

After receiving URL, extract the spreadsheet ID and read the data:
```python
# Extract spreadsheet_id from URL
# URL format: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit...
spreadsheet_id = extract_id_from_url(url)

# Get sheet names
sheets = user-google-drive-mcp-sheets_get_sheet_names(spreadsheet_id)
```

#### Step 2a: Tab Selection

Always display available tabs and ask which one(s) to process:

```
📑 Available tabs in this spreadsheet:

[1] Test Cases
[2] Sprint 42 Results
[3] Regression Suite
[4] Archive

Which tab(s) would you like to process?
- Enter tab number(s): e.g., "1" or "1,2,3" or "all"

👉 Tab selection:
```

If user selects multiple tabs:
```python
# Process each selected tab
all_test_data = []
for tab_name in selected_tabs:
    data = user-google-drive-mcp-sheets_read(spreadsheet_id, sheet_name=tab_name)
    all_test_data.extend(parse_test_data(data))
    print(f"  ✅ Read {len(data)} rows from '{tab_name}'")

print(f"\n📊 Total: {len(all_test_data)} test cases from {len(selected_tabs)} tab(s)")
```

If user selects single tab:
```python
# Read the selected sheet data
data = user-google-drive-mcp-sheets_read(spreadsheet_id, sheet_name=selected_tab)
```

#### Option B: PDF Export

```
📄 PDF Export Input

Please provide the path to your PDF file:
Example: /Users/you/Downloads/test_results.pdf or @test_results.pdf

👉 PDF file path:
```

Read and parse the PDF content. Extract tabular data from the PDF.

---

### Step 3: Column Detection

After reading the data, identify columns:

```
📋 Column Detection

I found these columns in your test results:
[List all column names]

Let me confirm the mapping:

1. Which column indicates PASS/FAIL status?
   Detected: "{auto_detected_column}" 
   👉 Press Enter to confirm, or type a different column name:

2. What values indicate a FAILED test? (comma-separated)
   Default: fail, failed, failure
   👉 Press Enter for default, or type custom values:
```

---

### Step 4: Preview Failed Tests

Scan for failed tests and display preview:

```
📊 Test Results Summary

Total test cases: {total}
Passed: {passed}
Failed: {failed}
Skipped/Other: {other}

Failed tests to create bug tickets for:
| # | Test ID | Test Name/Objective |
|---|---------|---------------------|
| 1 | TC-001  | User login fails... |
| 2 | TC-015  | Payment processing... |
| 3 | TC-023  | Export button not... |
...

👉 Proceed with creating {failed} bug tickets? (yes/no):
```

If no failed tests found:
```
✅ No failed tests found!

All {total} test cases passed. No bug tickets to create.

👉 Press Enter to return to main menu.
```

---

### Step 5: Jira Project Configuration

```
🎯 Jira Project Configuration

1. What Jira project should these bugs be created in?
   Example: HELIX, PROJ, TESTING
   👉 Project key:
```

After receiving project key, verify it exists:
```python
# Verify project exists
projects = user-atlassian-mcp-jira_search_issues(projectKeys=[project_key], maxResults=1)
```

If project not found, ask to re-enter.

---

### Step 6: Epic Configuration

```
📁 Epic Configuration

How would you like to organize these bug tickets?

[A] Add to an existing epic
    Link all bugs to an epic that already exists

[B] Create a new epic containing these bugs
    I'll create a new epic first, then link all bugs to it

[C] No epic - create standalone tickets
    Bugs will be created in the project without epic linkage

👉 Choice (A, B, or C):
```

#### Option A: Existing Epic
```
👉 Enter the existing epic key (e.g., HELIX-10332):
```

Verify the epic exists:
```python
epic = user-atlassian-mcp-jira_search_issues(issueKeys=[epic_key])
```

If found, display confirmation:
```
✅ Found epic: {epic_key}
   "{epic_summary}"

Bugs will be linked to this epic.
```

#### Option B: New Epic
```
📝 New Epic Details

1. Epic name/summary:
   Example: "Pre-release Bug Fixes - Feature X"
   👉 Epic name:

2. Epic description (optional):
   👉 Description (or press Enter to skip):
```

The epic will be created before the bugs.

#### Option C: No Epic
```
ℹ️ No epic selected

Bug tickets will be created as standalone issues in project {project_key}.
They can be linked to an epic manually later if needed.
```

---

### Step 6b: Additional Labels (Optional)

```
🏷️ Additional Labels

Default labels that will be applied:
- pre-release
- QualityForge

Would you like to add any additional labels? (comma-separated)
Example: tx-domain-auth, fy26-q1, regression

👉 Additional labels (or press Enter to skip):
```

If user provides labels, add them to the default list. Store as:
```python
labels = ["pre-release", "QualityForge"]
if user_labels:
    labels.extend([label.strip() for label in user_labels.split(",") if label.strip()])
```

---

### Step 7: Confirmation & Creation

```
📋 Ready to Create Bug Tickets

Summary:
- Project: {project_key}
- Epic: {epic_key or "New: " + epic_name or "None (standalone)"}
- Bug tickets to create: {count}
- Priority: P3: Low
- Labels: pre-release, QualityForge{", " + additional_labels if additional_labels else ""}

Each bug ticket will include:
- Summary: Test case title/objective
- Description:
  • Pre-conditions
  • Steps to test
  • Expected outcome vs Actual outcome

👉 Create these bug tickets now? (yes/no):
```

---

### Step 8: Bug Ticket Creation

For each failed test, create a bug ticket:

#### Bug Ticket Format

**Summary**: `[{test_id}] {test_name_or_objective}`

**Description** (Markdown format - Atlassian MCP bundle converts to Jira ADF):
```markdown
## Test Case
{test_id}: {test_name_or_objective}

## Pre-conditions
{pre_conditions_from_test_case}

## Steps to Reproduce
{steps_to_test_from_test_case}

## Expected Result
{expected_results_from_test_case}

## Actual Result
{actual_results_if_available}
(or "Test failed - see notes for details" if no actual result provided)

## Additional Notes
{notes_or_evidence_from_test_case}

---
*Created via QualityForge Bug Ticket Creation*
*Source: {google_sheet_url_or_pdf_path}*
```

#### Creation Loop

```python
created_tickets = []

# Create epic first if Option B was selected
if create_new_epic:
    epic_result = user-atlassian-mcp-jira_create_issue(
        projectKey=project_key,
        issueType="Epic",
        summary=epic_name,
        description=epic_description,
        epicName=epic_name  # Required for Epic type
    )
    epic_key = epic_result["key"]
    print(f"✅ Created epic: {epic_key}")

# Create each bug ticket
for test in failed_tests:
    result = user-atlassian-mcp-jira_create_issue(
        projectKey=project_key,
        issueType="Bug",
        summary=f"[{test.id}] {test.name}",
        description=build_bug_description(test),
        priority="P3: Low",
        labels=["pre-release", "QualityForge"],
        parent=epic_key  # If epic selected
    )
    created_tickets.append({
        "key": result["key"],
        "test_id": test.id,
        "summary": test.name
    })
    print(f"  ✅ Created: {result['key']}")
```

---

### Step 9: Completion Summary

```
✅ Bug Ticket Creation Complete!

📊 Summary:
- Project: {project_key}
- Epic: {epic_key} ({"existing" or "newly created" or "none"})
- Bug tickets created: {count}

📋 Created Tickets:
| Ticket | Test ID | Summary |
|--------|---------|---------|
| HELIX-11500 | TC-001 | User login fails when... |
| HELIX-11501 | TC-015 | Payment processing error... |
| HELIX-11502 | TC-023 | Export button not responding... |

🔗 Links for Slack/Docs:
- [HELIX-11500](https://jira.example.com/browse/HELIX-11500) - User login fails when...
- [HELIX-11501](https://jira.example.com/browse/HELIX-11501) - Payment processing error...
- [HELIX-11502](https://jira.example.com/browse/HELIX-11502) - Export button not responding...

{if epic_key}
📁 Epic: [{epic_key}](https://jira.example.com/browse/{epic_key})
{/if}

👉 Need anything else? Run /qforge to return to the main menu.
```

---

## Column Mapping Reference

The feature automatically detects common column names:

| Data Field | Common Column Names |
|------------|---------------------|
| Test ID | Test ID, Test Case ID, ID, TestID, TC ID |
| Test Name | Test Name, Objective, Title, Name, Test Case Name |
| Pre-conditions | Pre-conditions, Preconditions, Conditions, Prerequisites |
| Steps | Steps to Test, Test Steps, Steps, Procedure |
| Expected Results | Expected Results, Expected, Expected Outcome |
| Actual Results | Actual Results, Actual, Actual Outcome, Result |
| Status | Status, Results, Outcome, Test Result, Pass/Fail |
| Notes | Notes, Testing Evidence, Evidence, Comments |

---

## Error Handling

### Google Sheet Access Errors
```
❌ Unable to read Google Sheet

Error: {error_message}

Please check:
1. The URL is correct and complete
2. The sheet is shared with your Google account
3. You have at least "Viewer" access

👉 Try a different URL, or use PDF export instead? (url/pdf/cancel):
```

### Jira Creation Errors
```
⚠️ Error creating ticket for {test_id}

Error: {error_message}

Options:
[R] Retry this ticket
[S] Skip and continue with remaining tickets
[A] Abort (keep tickets already created)

👉 Choice:
```

### No Failed Tests
```
✅ Great news - no failed tests found!

All {total} test cases in your results have passing status.
No bug tickets need to be created.

👉 Press Enter to return to main menu.
```

---

## Output Artifacts

After completion, the feature generates a summary file:

**Location**: `test-jams/{YYYY-MM-DD}_bug-tickets/bug_creation_summary.md`

**Contents**:
```markdown
# Bug Ticket Creation Summary

- Date: {date}
- Source: {google_sheet_url or pdf_path}
- Project: {project_key}
- Epic: {epic_key or "None"}

## Created Tickets

| Ticket | Test ID | Summary | Status |
|--------|---------|---------|--------|
| HELIX-11500 | TC-001 | User login fails... | Created |
| HELIX-11501 | TC-015 | Payment processing... | Created |

## Statistics
- Total failed tests: {count}
- Tickets created: {created}
- Errors: {errors}
```
