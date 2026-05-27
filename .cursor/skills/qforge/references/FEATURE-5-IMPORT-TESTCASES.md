# Feature 5: Import Test Cases to Jira

*When user selects Option 5, proceed with this workflow*

---

## Overview

Import existing test cases from documents (Google Sheets, Google Docs, or PDF) into Jira as Task tickets. This feature reads test case data from your source, creates properly formatted Task tickets, and links them to an epic in your specified Jira project.

---

## MCP Verification

**Before starting the interactive flow**, verify MCP availability:

### Step 1: Check Jira MCP (REQUIRED)

Attempt to verify Jira access using DAST-Orch MCP:
```
Call: user-DAST-Orch-get_jira_user_info
```

- **If unavailable or error**: Display setup instructions and STOP
  ```
  ❌ Jira MCP not available
  
  Test case import requires Jira access via DAST-Orch MCP.
  
  Please ensure:
  1. DAST-Orch MCP is configured in Cursor
  2. You have authenticated with your SSO credentials
  
  Run /qforge again after setup is complete.
  ```
- **If available**: Display "✅ Jira MCP detected and ready"

### Step 2: Check Google Drive MCP (OPTIONAL)

Attempt to verify Google Sheets/Docs access:
```
Call: user-google-drive-mcp-sheets_get_metadata (with any test spreadsheet)
```

Or simply check if `user-google-drive-mcp-sheets_read` tool is available.

- **If available**: Set `GOOGLE_DRIVE_AVAILABLE = true`, display "✅ Google Drive MCP detected - can read Google Sheets/Docs directly"
- **If unavailable**: Set `GOOGLE_DRIVE_AVAILABLE = false`, display "ℹ️ Google Drive MCP not available - will use PDF export"

---

## Interactive Flow

### Step 1: Input Source

**If `GOOGLE_DRIVE_AVAILABLE = true`:**
```
📥 Import Test Cases to Jira

How would you like to provide your existing test cases?

[A] Google Sheet URL (recommended)
    I'll read test cases directly from your spreadsheet

[B] Google Doc URL
    I'll parse test cases from your document

[C] Drop in a PDF
    Drag and drop a PDF export into the chat

[D] Return to Main Menu

👉 Choice (A, B, C, or D):
```

**If `GOOGLE_DRIVE_AVAILABLE = false`:**
```
📥 Import Test Cases to Jira

ℹ️ Google Drive MCP is not available, so I'll need a PDF or local file.

Please provide your test cases in one of these formats:
- PDF export of your Google Sheet/Doc
- CSV file with test case data

You can either:
1. Drag and drop the file into the chat
2. Provide the full file path

👉 File path (or drag file here, or 'cancel' to return):
```

---

### Step 2: Collect Test Case Data

#### Option A: Google Sheet

```
📋 Google Sheet Input

Please provide the Google Sheet URL:
Example: https://docs.google.com/spreadsheets/d/1abc123.../edit

👉 Google Sheet URL:
```

After receiving URL, extract the spreadsheet ID:
```python
# Extract spreadsheet_id from URL
spreadsheet_id = extract_id_from_url(url)

# Get sheet names
sheets = user-google-drive-mcp-sheets_get_sheet_names(spreadsheet_id)
```

#### Step 2a: Tab Selection

Always display available tabs and ask which one(s) to process:

```
📑 Available tabs in this spreadsheet:

[1] Master Test Cases
[2] Sprint 42 Tests
[3] Regression Suite
[4] Archive

Which tab(s) would you like to import?
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

#### Option B: Google Doc

```
📄 Google Doc Input

Please provide the Google Doc URL:
Example: https://docs.google.com/document/d/1abc123.../edit

👉 Google Doc URL:
```

After receiving URL:
```python
# Extract document_id from URL
document_id = extract_id_from_url(url)

# Read the document content
content = user-google-drive-mcp-read_document(document_id)

# Parse test cases from document structure
test_cases = parse_test_cases_from_doc(content)
```

#### Option C: PDF/Local File

```
📄 PDF/Local File Input

Please drag and drop your file into the chat, or provide the path:
Example: /Users/you/Downloads/test_cases.pdf or @test_cases.pdf

👉 File:
```

Read and parse the PDF/CSV content. Extract tabular or structured data.

---

### Step 3: Column Detection

After reading the data, identify and confirm columns:

```
🔍 Analyzing test case data...

✅ Detected {count} test cases

Column mapping detected:
┌─────────────────┬────────────────────┐
│ Field           │ Mapped Column      │
├─────────────────┼────────────────────┤
│ Test ID         │ {detected_column}  │
│ Test Name       │ {detected_column}  │
│ Pre-conditions  │ {detected_column}  │
│ Test Steps      │ {detected_column}  │
│ Expected Result │ {detected_column}  │
│ Priority        │ {detected_column}  │
└─────────────────┴────────────────────┘

Does this mapping look correct? (yes/no/adjust)
```

If user says "adjust":
```
👉 Which field needs adjustment?
   1. Test ID
   2. Test Name
   3. Pre-conditions
   4. Test Steps
   5. Expected Result
   6. Priority

Enter field number and new column name (e.g., "2 Objective"):
```

---

### Step 4: Preview Test Cases

Display preview of test cases to be imported:

```
📋 Test Case Preview (showing 5 of {total})

┌────────┬─────────────────────────────────────┬──────────┐
│ ID     │ Test Name                           │ Priority │
├────────┼─────────────────────────────────────┼──────────┤
│ TC-001 │ Verify user login with valid creds  │ P1       │
│ TC-002 │ Verify password reset flow          │ P2       │
│ TC-003 │ Verify MFA enrollment               │ P1       │
│ TC-004 │ Verify session timeout behavior     │ P2       │
│ TC-005 │ Verify account lockout after fails  │ P1       │
└────────┴─────────────────────────────────────┴──────────┘

... and {remaining} more test cases

👉 Continue with all {total} test cases? (yes/no/filter):
```

If user says "filter":
```
How would you like to filter?

[A] By priority (e.g., "P1 only" or "P1,P2")
[B] By ID range (e.g., "TC-001 to TC-020")
[C] By keyword in name

👉 Filter option:
```

---

### Step 5: Jira Project Configuration

```
🎯 Jira Project Configuration

What Jira project should these test cases be created in?
Example: EEE, TXPLAT, TESTING

👉 Project key:
```

After receiving project key, verify it exists:
```python
# Verify project exists
projects = user-DAST-Orch-jira_search_issues(projectKeys=[project_key], maxResults=1)
```

If project found:
```
✅ Project verified: {project_key} ({project_name})
```

If project not found, ask to re-enter.

---

### Step 6: Epic Configuration

```
📁 Epic Configuration

How would you like to organize these test case tickets?

[A] Add to an existing epic
    Link all test cases to an epic that already exists

[B] Create a new epic containing these test cases
    I'll create a new epic first, then link all tickets to it

👉 Choice (A or B):
```

#### Option A: Existing Epic
```
👉 Enter the existing epic key (e.g., EEE-10332):
```

Verify the epic exists:
```python
epic = user-DAST-Orch-jira_search_issues(issueKeys=[epic_key])
```

If found, display confirmation:
```
🔍 Looking up epic...

✅ Found epic: {epic_key}
   "{epic_summary}"
   Status: {status}
   Current child issues: {child_count}

Test cases will be linked to this epic.
```

#### Option B: New Epic
```
📝 New Epic Details

1. Epic name/summary:
   Example: "Domain Auth Test Cases - Q1 2026"
   👉 Epic name:

2. Epic description (optional):
   👉 Description (or press Enter to skip):
```

Display confirmation:
```
✅ New epic will be created: "{epic_name}"
```

---

### Step 7: Assignee Configuration

```
👤 Assignee Configuration

Who should these test cases be assigned to?

[A] Specific user
    Assign all test cases to one person

[B] Round-robin across team
    Distribute evenly across multiple assignees

[C] Leave unassigned
    No assignee - can be assigned later

👉 Choice (A, B, or C):
```

#### Option A: Specific User
```
👉 Enter the username to assign all test cases to:
```

Verify user exists:
```python
# Verify user exists in Jira
user = user-DAST-Orch-get_jira_user_info()  # or search for specific user
```

```
✅ All test cases will be assigned to: {username}
```

#### Option B: Round-Robin
```
👥 Team Members for Round-Robin Assignment

Enter usernames (comma-separated):
Example: jsmith, mgarcia, kwilson

👉 Team members:
```

After receiving usernames:
```python
# Calculate distribution
team = [u.strip() for u in input.split(",")]
per_person = len(test_cases) // len(team)
remainder = len(test_cases) % len(team)
```

Display distribution:
```
✅ {total} test cases will be distributed across {count} assignees:
   - {user1}: {count1} tickets
   - {user2}: {count2} tickets
   - {user3}: {count3} tickets
```

#### Option C: Unassigned
```
ℹ️ Test cases will be created without assignees.
   They can be assigned later during sprint planning.
```

---

### Step 8: Additional Labels

```
🏷️ Additional Labels

Default labels that will be applied:
- test-case
- QualityForge
⚠️ Note: Do not remove these default labels - they are used for reporting purposes.

Would you like to add any additional labels? (comma-separated)
Example: domain-auth, fy26-q1, regression

👉 Additional labels (or press Enter to skip):
```

If user provides labels:
```python
labels = ["test-case", "QualityForge"]
if user_labels:
    labels.extend([label.strip() for label in user_labels.split(",") if label.strip()])
```

Display confirmation:
```
✅ Labels to apply:
   - test-case (default)
   - QualityForge (default)
   - {user_label_1}
   - {user_label_2}
   ...
```

---

### Step 9: Confirmation

```
📋 Ready to Import Test Cases to Jira

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Source: {google_sheet_url or pdf_path}
- Project: {project_key}
- Epic: {epic_key or "New → " + epic_name}
- Test cases to import: {count}
- Issue type: Task
- Labels: test-case, QualityForge{", " + additional_labels if additional_labels else ""}
- Assignee: {assignee or "Round-robin (" + team + ")" or "Unassigned"}

Each ticket will include:
- Summary: [{test_id}] {test_name}
- Description:
  • Pre-conditions
  • Test steps
  • Expected result
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 Import these test cases now? (yes/no):
```

---

### Step 10: Test Case Ticket Creation

For each test case, create a Task ticket:

#### Task Ticket Format

**Summary**: `[{test_id}] {test_name}`

**Description** (Markdown format - DAST-Orch converts to Jira ADF):
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
*Imported via QualityForge*
*Source: {source_file_or_url}*
```

#### Creation Loop

```python
created_tickets = []
assignment_index = 0

# Create epic first if Option B was selected
if create_new_epic:
    epic_result = user-DAST-Orch-jira_create_issue(
        projectKey=project_key,
        issueType="Epic",
        summary=epic_name,
        description=epic_description,
        epicName=epic_name  # Required for Epic type
    )
    epic_key = epic_result["key"]
    print(f"Creating epic: {epic_name}")
    print(f"✅ Epic created: {epic_key}\n")

print("Creating test case tickets:")

# Create each test case ticket
for i, test in enumerate(test_cases):
    # Determine assignee for round-robin
    assignee = None
    if assignment_mode == "specific":
        assignee = specific_user
    elif assignment_mode == "round_robin":
        assignee = team[assignment_index % len(team)]
        assignment_index += 1
    
    result = user-DAST-Orch-jira_create_issue(
        projectKey=project_key,
        issueType="Task",
        summary=f"[{test.id}] {test.name}",
        description=build_task_description(test),
        priority=test.priority or "P3: Low",
        labels=labels,
        assignee=assignee,
        parent=epic_key
    )
    
    created_tickets.append({
        "key": result["key"],
        "test_id": test.id,
        "summary": test.name,
        "assignee": assignee
    })
    
    # Display progress
    progress = int((i + 1) / len(test_cases) * 30)
    bar = "█" * progress + "░" * (30 - progress)
    print(f"\r[{bar}] {i + 1}/{len(test_cases)}", end="")
    print(f"\n✅ {result['key']}: [{test.id}] {test.name}" + (f" → {assignee}" if assignee else ""))
```

---

### Step 11: Completion Summary

```
✅ Import Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source File: {source}

{if new_epic}
Epic Created:
  {epic_key}: {epic_name}
  https://jira.example.com/browse/{epic_key}
{else}
Linked to Epic:
  {epic_key}: {epic_summary}
  https://jira.example.com/browse/{epic_key}
  (now has {new_child_count} child issues: {old_count} existing + {imported_count} new)
{/if}

Test Cases Imported: {total}
  ✅ Successfully created: {success_count}
  ❌ Failed: {error_count}

{if round_robin}
Assignment Distribution:
  - {user1}: {count1} tickets
  - {user2}: {count2} tickets
  - {user3}: {count3} tickets
{/if}

Labels Applied:
  {label_list}

View all imported tickets:
  JQL: project = {project_key} AND labels = "QualityForge" 
       AND labels = "test-case" AND parent = {epic_key}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Summary saved to: test-jams/{date}_import/import_summary.md

👉 Press Enter to return to main menu.
```

---

## Column Mapping Reference

The feature automatically detects common column names:

| Data Field | Common Column Names |
|------------|---------------------|
| Test ID | Test ID, Test Case ID, ID, TestID, TC ID, TC-ID, # |
| Test Name | Test Name, Objective, Title, Name, Test Case Name, Summary, Test Case |
| Pre-conditions | Pre-conditions, Preconditions, Conditions, Prerequisites, Pre-requisites, Setup |
| Steps | Steps to Test, Test Steps, Steps, Procedure, Actions |
| Expected Results | Expected Results, Expected, Expected Outcome, Expected Result |
| Priority | Priority, P0/P1/P2/P3, Severity |

---

## Error Handling

### Google Sheet/Doc Access Errors
```
❌ Unable to read Google Sheet/Doc

Error: {error_message}

Please check:
1. The URL is correct and complete
2. The document is shared with your Google account
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

### No Test Cases Found
```
⚠️ No test cases found in the provided source.

Please check:
1. The document contains test case data
2. Column headers are recognizable (see Column Mapping Reference)
3. Data rows exist below the header row

👉 Try again with a different source? (yes/no):
```

---

## Output Artifacts

After completion, the feature generates a summary file:

**Location**: `test-jams/{YYYY-MM-DD}_import/import_summary.md`

**Contents**:
```markdown
# Test Case Import Summary

- Date: {date}
- Source: {source_url_or_path}
- Project: {project_key}
- Epic: {epic_key}

## Created Tickets

| Ticket | Test ID | Summary | Assignee | Status |
|--------|---------|---------|----------|--------|
| EEE-9101 | TC-001 | Verify user login... | glehman | Created |
| EEE-9102 | TC-002 | Verify password reset... | jdoe | Created |

## Statistics
- Total test cases: {count}
- Tickets created: {created}
- Errors: {errors}

## Labels Applied
- test-case
- QualityForge
- {additional_labels}

## JQL Query
project = {project_key} AND labels = "QualityForge" AND parent = {epic_key}
```
