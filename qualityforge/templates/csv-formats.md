# CSV Format Templates

This document defines the CSV formats used for different test jam types.

## Format Selection Guide

| Test Jam Type | Use This Format |
|---------------|-----------------|
| PR-based (standard) | Standard Format |
| PR-based + Mabl integration | Enhanced Format (Mabl) |
| PRD-based | PRD Format |
| PRD-based + Mabl | Full Enhanced Format |
| **Test Account Creation** | **Test Account Format** |

---

## Standard Format (PR-based with Execution Tracking)

**Use for**: Regular PR-based test jams without Mabl integration

**CSV Header**:
```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
```

**Example Row** (note: in actual CSV, use newlines between numbered items - shown as `\n` below):
```csv
TC-001,Functional Testing,[nova-corp/helix-api] [HELIX-2847] SMS Send Success Flow,P0,Manual,SMS Service,Verify SMS can be sent successfully,"1. User is logged in\n2. SMS credits available\n3. Valid phone number","1. Navigate to SMS dashboard\n2. Click 'Send SMS'\n3. Enter valid phone number\n4. Enter message text\n5. Click 'Send'","1. SMS is sent successfully\n2. Confirmation message appears\n3. Credit balance decrements",,,,,
```

**How it displays in Excel/Sheets:**
- Pre-conditions, Test Steps, and Expected Results all show as numbered lists with line breaks
- **CRITICAL**: MUST use numbered lists (1., 2., 3.) - NEVER use bullet points (-, *, •)
- **WHY**: Bullet points starting with `-` cause Excel `=NAME?` formula errors
- Format example (content varies per test case):
  ```
  1. User is logged in
  2. SMS credits available
  3. Valid phone number
  ```
- Use numbered structure - actual wording should match your specific test scenario

---

## Completed Test Jam Export (Execution Tracking Filled)

**Use for**: Post-test-jam CSV exports where execution tracking columns are filled in

**Expected Columns**:
- Same as Standard Format (includes Status/Tester/Date Tested/Actual Results/Notes/Bug ID)
- Optional: `Testing Evidence` column (if you add screenshots/links during execution)

**Status/Results values**:
- Use `Fail`/`FAIL` (or `Failed`) to mark failed tests
- The completed test jam workflow will scan for failures and draft Jira tickets

**Artifact detection**:
- If `Testing Evidence` or `Notes` includes links (e.g., Google Drive), the tool will flag that artifacts were present and should be attached manually in Jira

---

## Enhanced Format (with Mabl integration + Execution Tracking)

**Use for**: PR-based test jams with Mabl automation coverage analysis

**CSV Header**:
```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,Automation Status,Mabl Reference,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
```

**Additional Columns**:
- **Automation Status**: `Already Automated` | `Can Be Automated` | `Manual Only` | `N/A`
- **Mabl Reference**: Mabl test ID or URL (e.g., `mabl-test-12345` or `See Mabl test: SMS-001`)

**Example Row** (note: in actual CSV, use newlines between numbered items - shown as `\n` below):
```csv
TC-001,Functional Testing,[nova-corp/helix-api] [HELIX-2847] SMS Send Success Flow,P0,Manual,SMS Service,Verify SMS can be sent successfully,"1. User is logged in\n2. SMS credits available","1. Navigate to SMS dashboard\n2. Click 'Send SMS'\n3. Enter details\n4. Click 'Send'","1. SMS sent successfully\n2. Confirmation appears",Can Be Automated,See Mabl test: SMS-SEND-001,,,,
```

---

## PRD Format (PRD-based + Execution Tracking)

**Use for**: Test cases generated from Product Requirements Documents

**CSV Header**:
```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,PRD Reference,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
```

**Additional Column**:
- **PRD Reference**: Format: `PRD: [Title] | Section: [Section Name] | URL: [PRD URL]`

**Example Row** (note: in actual CSV, use newlines between numbered items - shown as `\n` below):
```csv
TC-001,Functional Testing,[PRD: SMS Scheduling] [User Stories] Verify user can schedule SMS,P0,Manual,SMS Service,Test scheduling feature from PRD user stories,"1. User logged in\n2. SMS credits available","1. Navigate to SMS dashboard\n2. Click 'Schedule SMS'\n3. Select future date/time\n4. Enter details\n5. Click 'Schedule'","1. SMS scheduled for future delivery\n2. Scheduled time displayed\n3. Confirmation message shown",PRD: SMS Scheduling | Section: User Stories | URL: https://confluence.example.com/display/HELIX/SMS-Scheduling,,,,,
```

---

## Full Enhanced Format (PRD + Mabl + Execution Tracking)

**Use for**: PRD-based test jams with Mabl automation coverage analysis

**CSV Header**:
```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,Automation Status,Mabl Reference,PRD Reference,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
```

**Combines**: All additional columns from Enhanced and PRD formats

---

## Test Account Format (Test Account Creation Data)

**Use for**: Generating test accounts for test case execution via Test Tools UI

**Purpose**: This CSV provides all necessary information for testers to quickly create test accounts using the Test Tools application without having to figure out what data to enter.

**CSV Header**:
```csv
Test Case ID,Account Purpose,Shard,Creation Date,Creation Time,Manual Activation,Entry Point,A/B Test Experimental,Email,Username,Password,First Name,Last Name,Address,Address 2,City,State,Zipcode,Country,Sending Domain,Company Name,Company Domain,Feature Flags,Subscription Plan,Account Status,Created By,Date Created,Notes
```

**Example Rows**:
```csv
TC-001,SMS Send Success Testing,us-east,12/19/2025,02:00 PM,No,Default,Off,qa.test+sms_test@example.com,test_account_sms01,Generated123!,QA,Tester,405 N Angier Ave NE,,Atlanta,GA,30308,USA,example.com,QA SMS Testing,https://example.com,feature_sms_enabled,Basic (500 seats) + messaging add-on,Active,John Doe,12/19/2025,SMS requires paid plan (Basic minimum) with messaging add-on purchased separately
TC-002,Email Campaign Testing,us-east,12/19/2025,02:05 PM,No,Default,Off,qa.test+email_test@example.com,test_account_email01,SecurePass456!,Email,Tester,123 Main St,,San Francisco,CA,94102,USA,example.com,QA Email Testing,https://example.com,,Pro (2500 seats),Active,Jane Smith,12/19/2025,Pro plan for advanced email features and automation capabilities
```

### Test Account Column Definitions

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| **Test Case ID** | Links to test case requiring this account | Yes | `TC-001` |
| **Account Purpose** | What this account will be used for | Yes | `SMS Send Success Testing` |
| **Region** | Server shard for account creation | Yes | `us-east`, `us-west`, `eu-west` |
| **Creation Date** | Date to create account | Yes | `12/19/2025` |
| **Creation Time** | Time to create account | Yes | `02:00 PM` |
| **Manual Activation** | Whether manual activation needed | Yes | `Yes`, `No` |
| **Signup Source** | Account entry point setting | Yes | `Default` |
| **A/B Test Experimental** | Flag for A/B test experiments | Yes | `On`, `Off` |
| **Email** | Login email address | Yes | `qa.test+test@example.com` |
| **Username** | Account username | Yes | `test_account_sms01` |
| **Password** | Account password | Yes | `Generated123!` |
| **First Name** | Account holder first name | Yes | `QA` |
| **Last Name** | Account holder last name | Yes | `Tester` |
| **Address** | Street address line 1 | Yes | `405 N Angier Ave NE` |
| **Address 2** | Street address line 2 | No | `Apt 4B` |
| **City** | City name | Yes | `Atlanta` |
| **State** | State/province code | Yes | `GA`, `CA`, `NY` |
| **Zipcode** | Postal/ZIP code | Yes | `30308` |
| **Country** | Country name | Yes | `USA`, `Canada` |
| **Sending Domain** | Domain for sending | Yes | `example.com` |
| **Company Name** | Company/organization name | Yes | `QA SMS Testing` |
| **Company Domain** | Company website URL | Yes | `https://example.com` |
| **Feature Flags** | Comma-separated feature flags | No | `feature_sms_enabled, feature_api_v3` |
| **Subscription Plan** | Initial subscription plan tier | Yes | `Basic (500 seats) + messaging add-on`<br>⚠️ **Must match feature requirements!** |
| **Account Status** | Current account status | No | `Active`, `Pending`, `Created` |
| **Created By** | Person who created account | No | `John Doe` |
| **Date Created** | Actual creation date | No | `12/19/2025` |
| **Notes** | Additional information | No | Free text notes |

### Usage Workflow

1. **Generation**: Test jam generator creates this CSV alongside test case CSVs
2. **Distribution**: Participants receive both test cases AND test account CSVs
3. **Account Creation**: Participants navigate to Test Tools UI
4. **Data Entry**: Participants copy/paste values from CSV into test tools form
5. **Execution**: Participants use created accounts to execute test cases
6. **Tracking**: Participants fill in "Created By" and "Date Created" columns

### Best Practices

- **One Account Per Test Case**: Each critical test case should have a dedicated account
- **Descriptive Purpose**: Make "Account Purpose" clear and specific
- **Email Aliases**: Use `+` notation for easy filtering (e.g., `user+sms_test@example.com`)
- **Feature Flags**: Only include flags actually needed for the test
- **Password Security**: Store passwords securely; change after test jam
- **Account Cleanup**: Document account cleanup process after testing
- **⚠️ Subscription Plan Validation**: ALWAYS verify plan supports features being tested
  - See [feature-to-plan-mapping.md](./feature-to-plan-mapping.md) for complete matrix
  - Common mistakes: Starter plan for SMS, Basic for automation
  - Document plan selection rationale in Notes column

### File Naming Convention

- Test account files: `testjam_test_accounts.csv` (all participants)
- Or per-participant: `testjam_participant_N_accounts.csv`

### Integration with Test Cases

Link test accounts to test cases via **Test Case ID** column:
- Test case `TC-001` requires account `TC-001` from test accounts CSV
- Pre-conditions in test case CSV can reference: "Use account TC-001"
- Ensures traceability between accounts and tests

### ⚠️ Subscription Plan Validation (CRITICAL)

**Before generating test account CSV, validate Subscription Plan selection:**

| Feature Being Tested | Minimum Required Plan | Add-ons Needed |
|---------------------|----------------------|----------------|
| SMS (text messages) | Basic | + messaging add-on |
| MMS (picture messages) | Pro | + messaging add-on |
| Marketing Automation | Pro | None |
| AI Features (AI Assistant) | Pro | None |
| Predictive Segmentation | Pro | None |
| A/B Testing (2 variants) | Basic | None |
| Custom HTML Templates | Enterprise | None |
| Basic Email | Free | None |

**Common Mistakes to Avoid:**
- ❌ Starter plan for SMS testing → Use Basic+ with messaging add-on
- ❌ Basic for marketing automation → Use Pro+
- ❌ Basic for MMS → Use Pro+
- ❌ Missing "+ messaging add-on" notation → Document add-ons in plan or notes

**Validation Process:**
1. Extract feature names from PR/PRD/test case
2. Look up minimum plan in [feature-to-plan-mapping.md](./feature-to-plan-mapping.md)
3. Set Subscription Plan column to required tier
4. Add "+ [add-on name]" if needed
5. Document rationale in Notes column

**See**: [feature-to-plan-mapping.md](./feature-to-plan-mapping.md) for complete feature-to-plan matrix

---

## Column Definitions

### Core Columns (Always Included)

| Column | Description | Example |
|--------|-------------|---------|
| **Test ID** | Unique identifier | `TC-001`, `TC-002` |
| **Category** | Test category type | `Functional Testing`, `UI/UX Testing` |
| **Test Name** | Descriptive test name with context | `[nova-corp/helix-api] [TICKET-ID] Test Name` |
| **Priority** | Test priority level | `P0`, `P1`, `P2`, `P3` |
| **Type** | Test execution type | `Manual`, `Automated`, `Manual + Automated` |
| **Component** | Component being tested | `SMS Service`, `Payment Gateway` |
| **Objective** | What the test validates | `Verify user can send SMS successfully` |
| **Pre-conditions** | Required setup | `1. User is logged in\n2. Credits available` |
| **Test Steps** | Numbered execution steps | `1. Navigate to...\n2. Click...\n3. Enter...` |
| **Expected Results** | What should happen | `SMS is sent and confirmation appears` |

### Optional Enhancement Columns

| Column | Description | Valid Values |
|--------|-------------|--------------|
| **Automation Status** | Automation recommendation | `Already Automated`, `Can Be Automated`, `Manual Only`, `N/A` |
| **Mabl Reference** | Link to Mabl test | `mabl-test-12345`, `See Mabl test: SMS-001` |
| **PRD Reference** | Link to PRD section | `PRD: [Title] \| Section: [Name] \| URL: [link]` |

### Execution Tracking Columns (Always Included, Initially Blank)

| Column | Description | Filled By | Format |
|--------|-------------|-----------|--------|
| **Status** | Test execution status | Participants | `Not Started`, `Pass`, `Fail`, `Blocked`, `Skip` |
| **Tester** | Person executing test | Participants | `First Last` or `email@domain.com` |
| **Date Tested** | Execution date | Participants | `YYYY-MM-DD` or `MM/DD/YYYY` |
| **Actual Results** | What actually happened | Participants | Free text with observations |
| **Notes** | Additional comments | Participants | Free text for edge cases, suggestions |
| **Bug ID** | Bug tracker reference | Participants | `JIRA-1234`, `GH-5678` (if test fails) |

---

## Test Name Format with PR Context

All test names should follow this format to enable traceability:

**Format**: `[nova-corp/helix-api] [TICKET-ID] Test Case Name`

### Examples:
- `[nova-corp/helix-api] [HELIX-2847] SMS Send Success Flow`
- `[nova-corp/notify-service] [HELIX-4103] SMS Dashboard Display - Chrome`
- `[nova-corp/helix-api] [HELIX-3192] SMS Click Event Webhook`

### For PRD-based Tests:
**Format**: `[PRD: PRD-Title] [Section-Name] Test Case Description`

### Examples:
- `[PRD: SMS Scheduling Feature] [User Stories] Verify user can schedule SMS`
- `[PRD: Payment Integration] [Acceptance Criteria] Validate payment flow`

### Extracting PR Context:

1. **Repository**: Extract from PR URL
   - From: `https://github.com/nova-corp/helix-api/pull/123`
   - Extract: `[nova-corp/helix-api]`

2. **Ticket ID**: Extract from PR title or description
   - Look for patterns: `HELIX-####`, `HELIX-####`, `SEC-####`
   - From PR title: "HELIX-2847: Add SMS webhook support"
   - Extract: `[HELIX-2847]`
   - If no ticket found, use: `[NO-TICKET]`

---

## Important Notes

### Execution Tracking Columns
- **Always initialize as EMPTY/BLANK** in generated CSV files
- These are filled by participants **during** the test jam session
- Do **NOT** pre-populate these fields when generating test cases

### CSV Best Practices

**CSV Generation Method**
- **Always use Python's `csv.writer`** for generating CSV files
  - Automatically handles commas, quotes, and special characters
  - Use `csv.QUOTE_MINIMAL` for optimal output
  - Never use manual string formatting/concatenation
- **CSV Formula Injection Prevention** (CRITICAL)
  - **USE NUMBERED LISTS (1., 2., 3.) ONLY** - NEVER use bullet points (-, *, •)
  - **WHY**: Cells starting with `-` cause Excel to display `=NAME?` errors
  - Prefix cells starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with single quote `'`
  - Prevents Excel/Google Sheets from interpreting cells as formulas
  - Eliminates `#NAME?`, `#REF!`, and formula errors
  
**Formatting for Compatibility**
- **Keep newlines for multi-line content** - csv.writer will quote cells automatically
  - Multi-line fields (Test Steps, Expected Results, Pre-conditions) use actual `\n` newlines
  - csv.writer automatically wraps these cells in quotes
  - Excel/Google Sheets display them as line breaks within cells
  - Example display in Excel/Sheets:
    ```
    1. Step one
    2. Step two
    3. Step three
    ```
  - This ensures compatibility with Excel, Google Sheets, and other CSV tools
- **Column header must be "Type"** not "Test Type" (5th column)

**Content Guidelines**
- Keep test steps numbered and clear
- Be specific in expected results
- Include enough detail for someone unfamiliar with the feature to execute the test
- Use proper CSV escaping: Quote cells containing commas, but avoid actual line breaks

### File Naming
- Master file: `testjam_all_test_cases.csv`
- Individual files: `testjam_participant_1.csv`, `testjam_participant_2.csv`, etc.

