# QualityForge - Quality Engineering Suite (powered by QE Suite)

**QualityForge** is a comprehensive Quality Engineering Suite that provides multiple tools for building better software. It includes test case generation, risk analysis, and automation features.

## 🛠️ What is QualityForge?

QualityForge brings together multiple quality engineering capabilities in one unified command:
- **Test Case/Jam Generation**: Automate creation of comprehensive test cases for collaborative testing sessions
- **Quality Risk Analysis** [BETA]: Identify risks before development starts
- **Bug Ticket Creation**: Generate Jira bug tickets from completed test results
- **Import Test Cases to Jira**: Import existing test cases to Jira as Task tickets

### What is a Test Jam?

Test Jam is a collaborative testing session where team members work together to validate changes, find bugs, and ensure quality before release. QualityForge automates the creation of test cases for these sessions.

## Quality Risk Analysis (BETA)

**Shift Left - Identify Risks Before You Code**

QualityForge includes a **Quality Risk Analysis (BETA)** feature that analyzes documentation (PRDs, Jira tickets, Figma designs) to identify implementation risks **before development begins**.

### Why Risk Identification?

Teams often discover risks too late—during development or in production. This leads to:
- Schedule slips and rushed implementations
- Technical debt accumulation
- Unforeseen downstream impacts
- Late-stage design changes

### What Quality Risk Analysis Does

```
/qforge → Option 2: Quality Risk Analysis
```

This feature will (BETA):
1. 📄 **Analyze your documentation** (PRD, Jira tickets, Figma designs)
2. 🔍 **Map to codebase** (identify which files/services will be affected)
3. ⚠️ **Identify risks** (technical, integration, downstream, team/process)
4. 💡 **Suggest mitigations** (actionable strategies for each risk)
5. 📊 **Generate report** (comprehensive risk analysis with severity ratings)

### Risk Categories Detected

- **🔴 Critical Risks**: Breaking API changes, large data migrations, legacy code modifications
- **🟠 High Risks**: Third-party rate limiting, performance concerns, cross-team coordination
- **🟡 Medium Risks**: Error handling gaps, audit requirements, cost implications
- **🟢 Low Risks**: UI/UX changes, minor enhancements

### Example Output

```
✅ Risk Analysis Complete!

📊 Summary:
- Total Risks: 12
  🔴 Critical: 2
  🟠 High: 5
  🟡 Medium: 4
  🟢 Low: 1

- Codebase Touch Points: 8 files, 3 services
- Downstream Impacts: 2 dependent services
- Recommended Spikes: 3

🔴 Top Risks:
1. Breaking API change affecting 3 downstream services
   → Mitigation: Version API (create /v2/endpoint)
2. Data migration for 500M+ records
   → Mitigation: Online schema change tool + blue-green deployment
```

**Learn More:**
- [Risk Analysis Guide](./risk/GUIDE.md) - Complete usage guide
- [Example Risk Report](./templates/EXAMPLE-RISK-REPORT.md) - See what reports look like
- [Content Accuracy Rubric](./risk/CONTENT-ACCURACY-RUBRIC.md) - How to keep reports evidence-based

---

## Quick Start

### Usage

Simply invoke the command in Cursor:

```
/qforge
```

**First Time Use**: The tool will automatically verify that required MCPs (GitHub MCP) are configured. If not, you'll receive setup instructions.

**Menu Options**:
1. **Test Case/Jam Generation** - Create comprehensive test cases with optional Google Sheets export
2. **Quality Risk Analysis** - Identify risks before development (**BETA**)
3. **Bug Ticket Creation** - Generate Jira bug tickets from completed tests
4. **Import Test Cases to Jira** - Import test cases as Jira Task tickets

When you select **Test Case/Jam Generation**, the tool will guide you through an interactive process to:
1. **Verify MCP setup** (first time only)
2. Gather PR URLs or repository names
3. Determine number of participants
4. Understand testing focus and priorities
5. Automatically generate test cases
6. Split test cases across participants
7. Create CSV files ready for distribution

## Features

### 🎯 Intelligent Test Case Generation
- Analyzes PR changes using GitHub MCP integration
- Identifies critical areas of code affected
- Prioritizes test cases based on labels (critical, high-priority, P0, P1)
- Generates comprehensive test coverage including:
  - Functional testing
  - Regression testing
  - Performance testing
  - Security testing
  - Cross-browser testing
  - Accessibility testing
  - API testing
  - Mobile/responsive testing

### 📊 Smart Distribution
- Automatically splits test cases evenly across participants
- Balances priority levels across participants
- Groups related test cases together
- Handles uneven distributions intelligently

### 🔍 PR Analysis
- Fetches PR details, descriptions, and labels
- Identifies files changed and components affected
- Analyzes PR comments for context
- Prioritizes based on impact and criticality

### 📦 Repository Testing
- Analyzes merged PR's from last 4 weeks
- Focuses on critical and high-priority changes
- Includes performance testing scenarios
- Groups by component/feature area

## Output Structure

Test jams are organized in timestamped folders:

```
test-jams/
  └── YYYY-MM-DD_[repo-or-pr-name]/
      ├── testjam_all_test_cases.csv    # Master file with ALL test cases
      ├── testjam_participant_1.csv      # Individual participant files
      ├── testjam_participant_2.csv
      ├── testjam_participant_3.csv
      ├── ...
      └── test_jam_summary.md
```

### CSV Format

All CSV files (master and individual participant files) use this structure with **execution tracking columns**:

```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
TC-001,Functional Testing,[org/project] [TXPLAT-3858] Login Flow Validation,P0,Manual,Authentication,Verify user login,...,...,...,,,,,,
```

**CSV Formatting Requirements:**
- **Column 5 must be "Type"** not "Test Type"
- **Multi-line content**: Uses numbered format (1., 2., 3.) with actual newlines in quoted cells
  - **Pre-conditions, Test Steps, and Expected Results** all use numbered lists
  - **CRITICAL**: NEVER use bullet points (-, *, •) - ONLY numbered lists (1., 2., 3.)
  - **WHY**: Bullet points starting with `-` cause Excel `=NAME?` formula errors
  - Format example in Excel/Sheets (content varies per test):
    ```
    1. User is logged in
    2. Credits available
    3. Valid phone number
    ```
  - Use numbered structure - actual wording should match your test scenario
  - Consistent, professional formatting across all three fields
- **Formula injection prevention**: Cells starting with `=`, `+`, `-`, `@` are prefixed with `'`
  - Prevents `#NAME?` errors in Excel/Google Sheets
  - Combined with numbered lists (not bullet points) for complete protection
- Ensures compatibility with Excel, Google Sheets, and other CSV tools

**Test Name Format**: `[org/repo] [TICKET-ID] Test Case Name`

**Execution Tracking Columns** (filled during test jam):
- **Status**: `Not Started`, `Pass`, `Fail`, `Blocked`, `Skip` (initially blank)
- **Tester**: Name/email of person executing the test (initially blank)
- **Date Tested**: Date test was executed in `YYYY-MM-DD` format (initially blank)
- **Actual Results**: What actually happened during testing (initially blank)
- **Notes**: Additional observations, edge cases, or comments (initially blank)
- **Bug ID**: Reference to filed bug if test fails, e.g. `JIRA-1234` (initially blank)

### Completed Test Jam → Jira Draft Tickets

After a test jam is completed, you can generate **Jira-ready ticket drafts** from the CSV export:

```
python3 qualityforge/test_jam_complete_jira.py \
  --csv /path/to/completed_test_jam.csv \
  --project-key EEE \
  --epic EEE-10332 \
  --label tx_fy26_tx-template-management \
  --priority P3 \
  --issue-type Story \
  --feature-flags "flag_one, flag_two" \
  --experiment-command 'document.cookie = "opt_experiments=example:variation_1; domain=.example.com; path=/"'
```

Output:
1. `jira_ticket_drafts.md` (next to the CSV by default)
2. Title + Description blocks for each failed test
3. Includes **Test Case ID** in the description for traceability
4. If artifact links are detected in Notes/Testing Evidence, the draft notes that attachments must be added manually

Each test case name is prefixed with:
- **Repository context**: `[org/repo]` extracted from PR URL
- **Ticket ID**: `[TICKET-####]` extracted from PR title/description
- **Test name**: Descriptive name of the test

This makes it easy to:
- ✅ Trace test cases back to source PRs
- ✅ Group test cases by repository or ticket
- ✅ Filter and organize in test management systems
- ✅ Generate reports by PR or epic

### Files Generated

Each test jam creates:
1. **`testjam_all_test_cases.csv`** - Master file containing ALL test cases for complete reference
2. **`testjam_participant_N.csv`** - Individual files split across participants
3. **`test_jam_summary.md`** - Executive summary and overview

### Summary Report

The markdown summary includes:
- Overview of what's being tested
- List of PR's and changes included
- Critical areas requiring focus
- Test case distribution across participants
- Timeline and success criteria
- Additional notes and context

### Test Account Creation

Some test cases require specific test accounts with pre-configured settings. When needed, the test jam generator can also create a **Test Account CSV** file that includes all the information needed to create test accounts via the Test Tools UI.

**Test Account CSV File**: `testjam_test_accounts.csv`

This file contains:
- Pre-populated form data for creating test accounts
- Account configuration (shard, plan, feature flags)
- Contact information and credentials
- Links to specific test cases requiring each account

**Benefits**:
- ✅ Saves time - no need to figure out what data to enter
- ✅ Consistency - all participants use the same account configurations
- ✅ Traceability - accounts are linked to specific test cases
- ✅ Documentation - credentials and settings are recorded

**Guides**:
- [Test Account Setup Guide](./setup/TEST-ACCOUNT-SETUP.md) - Step-by-step instructions for creating test accounts
- [Test Account Fields](./templates/test_account_fields.md) - Detailed field definitions
- [admin-console Navigation Guide](./setup/Admin Console-NAVIGATION.md) - Post-creation account modifications (MRR, plan changes, etc.)

See the **Test Account Format** section in [templates/csv-formats.md](./templates/csv-formats.md) for full CSV structure details.

## Test Case Categories

1. **Functional Testing** - Core feature functionality
2. **UI/UX Testing** - Visual and interaction testing
3. **Integration Testing** - Cross-component interactions
4. **Regression Testing** - Existing functionality validation
5. **Performance Testing** - Load, response time, resources
6. **Security Testing** - Auth, authorization, data protection
7. **Cross-Browser Testing** - Browser compatibility
8. **Accessibility Testing** - WCAG compliance
9. **API Testing** - Endpoint validation, error handling
10. **Mobile/Responsive Testing** - Device compatibility

## Priority Levels

- **Critical/P0**: Core functionality, security, data integrity
- **High/P1**: Important user flows, payment, authentication
- **Medium/P2**: Secondary features, UI improvements
- **Low/P3**: Nice-to-have, cosmetic changes

## Requirements

### MCP Integration

This tool integrates with multiple MCP servers:

#### GitHub MCP (Required):
- Search and validate repositories
- Fetch PR details and metadata
- Analyze files changed
- Retrieve PR comments and reviews
- Search code for context

#### Mabl MCP (Optional):
- Query existing automated test coverage
- Identify test automation gaps
- Reference Mabl test IDs
- Suggest automation opportunities
- Link to existing Mabl tests

**Note**: GitHub MCP is required. Mabl MCP is optional and enhances test case generation when available.

### 🚀 Setup Guides - Choose Your Path:

**👋 First Time User? (Never installed MCPs before)**
- → [First Time Setup](./setup/FIRST-TIME-SETUP.md) - Complete walkthrough
- Includes: Cursor installation, GitHub authentication, GitHub MCP configuration
- Time: 15-20 minutes
- Starts from scratch with zero assumptions

**⚙️ Need to configure MCPs?**
- → [MCP Setup Guide](./setup/MCP-SETUP.md) - Quick MCP configuration guide
- Configure GitHub MCP in Cursor settings
- Time: 5 minutes

Ensure MCP servers are configured in your Cursor settings before using `/qforge`.

## Example Usage

### Example 1: PR Test Jam with Mabl Integration

```
User: /qforge

AI: 🛠️ Welcome to Quality Engineering Suite by QE Suite!
    (powered by QualityForge)
    
    Select a feature:
    1. Test Case/Jam Generation
    2. Risk Analysis [BETA]
    3. Bug Ticket Creation
    4. Import Test Cases to Jira
    5. Exit

User: 1

AI: Let's create comprehensive test cases! 🎯
    
    Provide PR URL(s), Repository, PRD, or Jira ticket...

User: https://github.com/org/project/pull/12345
      Focus on SMS functionality and billing integration

AI: How many participants?

User: 5

AI: Should I check Mabl for existing automated test coverage?

User: Yes

AI: [Analyzes PR + queries Mabl for existing tests]
    ✅ Test Cases Created Successfully!
    
    📁 Location: test-jams/2025-11-20_sms-billing-pr-12345/
    
    📊 Summary:
    - Total Test Cases: 45
    - Already Automated in Mabl: 12
    - Can Be Automated: 18
    - Manual Only: 15
    - Participants: 5
    
    📋 Mabl Coverage:
    - Found 12 existing Mabl tests covering core SMS flows
    - Identified 18 test cases as good automation candidates
    - 15 test cases require manual exploratory testing
```

### Example 2: PRD-based Test Jam (Early Stage)

```
User: /qforge

AI: Select a feature: 1-5

User: 1

AI: Let's create comprehensive test cases! 🎯
    For PRD-based testing, please provide:
    1. PRD URL
    2. PRD Contents (paste full text)

User: PRD URL: https://confluence.example.com/display/MAIL/SMS-Scheduling-Feature
      
      PRD Contents:
      ===
      Title: SMS Scheduling Feature
      
      Section: User Stories
      - As a user, I want to schedule SMS messages for future delivery...
      - As a user, I want to edit scheduled messages...
      
      Section: Acceptance Criteria
      - System must allow scheduling up to 30 days in advance...
      - Users must be able to cancel scheduled messages...
      
      Section: Technical Requirements  
      - API endpoint for scheduling...
      - Database schema for scheduled messages...
      ===
      
      We're in design phase, need test cases before implementation
      5 participants

AI: [Analyzes PRD, extracts title and sections]
    ✅ Generated 30 test cases from PRD
    
    Test cases formatted as:
    - [PRD: SMS Scheduling Feature] [User Stories] Test Case Name
    - [PRD: SMS Scheduling Feature] [Acceptance Criteria] Test Case Name
    
    Each test case includes PRD Reference column:
    - PRD: SMS Scheduling Feature | Section: User Stories | URL: https://confluence.example.com/...
    
    Ready for early validation and requirement refinement!
```

### Example 3: Repository-based Test Jam

```
User: /qforge

AI: Select a feature: 1-5

User: 1

AI: Let's create comprehensive test cases! 🎯

User: Repository: org/project
      Focus on all changes from the last 4 weeks

AI: How many participants will be part of this Test Jam?

User: 10

[Analyzes last 4 weeks of merged PR's, prioritizes critical changes, generates comprehensive test cases]

AI: ✅ Test Cases Created Successfully!
    Analyzed 23 PR's from the last 4 weeks
    Focused on 8 critical PR's affecting core functionality
```

## Best Practices

1. **Be Specific**: Provide clear PR URLs or repo names
2. **Add Context**: Mention specific areas of concern or focus
3. **Right-Size Participants**: Match participant count to test scope
   - Small PR: 3-5 participants
   - Medium changes: 5-8 participants
   - Major release: 8-15 participants
4. **Review Generated Cases**: Always review the summary before distributing
5. **Adjust as Needed**: You can regenerate or ask for modifications

## Tips for Test Jam Success

- **Pre-brief participants**: Review the summary together before starting
- **Set time limits**: Each test case should take 5-15 minutes
- **Use tracking**: Participants fill in execution tracking columns as they test
  - Update **Status** column: Mark as `Pass`, `Fail`, `Blocked`, or `Skip`
  - Fill **Tester** column: Add your name/email
  - Fill **Date Tested**: Use today's date
  - Document **Actual Results**: What you observed
  - Add **Notes**: Any edge cases or observations
  - Link **Bug ID**: File bugs for failures and add the ID
- **Import to Google Sheets**: Open the CSV in Google Sheets for easy collaboration
- **Share progress**: Use Google Sheets' built-in sharing for real-time updates
- **Filter and sort**: Use Status column to track progress and identify failures
- **Communicate findings**: Create a shared space for bug reports
- **Follow up**: Schedule a debrief to discuss findings

## Troubleshooting

### MCP Not Configured

**Symptom**: Error message "GitHub MCP Not Detected" when running `/qforge`

**Solution**:
1. Check Cursor Settings → MCP Servers
2. Verify "github-mcp" (or similar) is configured
3. Follow setup instructions in [MCP Setup Guide](./setup/MCP-SETUP.md)
4. Restart Cursor and try again

**Manual Verification**:
Type in Cursor: "check my MCP setup" or re-run `/qforge`

### MCP Connection Errors

**Symptom**: Errors when fetching PR details or repository information

**Solution**:
1. Verify your GitHub Personal Access Token is valid
2. Check you have access to the target repository
3. Ensure you're connected to company network/VPN
4. Try accessing the repository directly in your browser
5. Check MCP server status in Cursor settings

### PR Not Found
- Verify the PR URL is correct
- Ensure you have access to the repository
- Check that the PR exists and isn't deleted
- Confirm GitHub MCP has proper repository permissions

### API Rate Limits
- Wait a few minutes and try again
- Consider reducing scope (fewer PR's or shorter timeframe)
- Check GitHub API rate limit status

### Too Many/Few Test Cases
- Adjust by specifying focus areas
- Request regeneration with different parameters
- Manually combine or split participant files if needed

### Mabl Features Not Working

**Symptom**: Mabl automation coverage not appearing in test cases

**Status**: This is NORMAL if Mabl MCP isn't configured (it's optional)

**Solution** (if you want Mabl features):
1. Contact Mabl admin for API credentials
2. Configure Mabl MCP following [MCP Setup Guide](./setup/MCP-SETUP.md)
3. Re-run `/qforge`, select option 1, and answer "yes" when asked about Mabl integration

## Support

For issues or questions:
1. Check the generated `test_jam_summary.md` for context
2. Review the CSV files for completeness
3. Re-run `/testjam` with clarified requirements
4. Adjust participant count and regenerate if needed

## Sharing with Your Team

### Option 1: Git Repository (Recommended)

```bash
# Clone the repository
git clone https://github.com/glehman/qe-suite ~/cursor-rules

# Pull updates anytime
cd ~/cursor-rules && git pull
```

### Option 2: Zip Distribution

```bash
cd qe-suite
zip -r quality-engineering-suite.zip qualityforge/ .cursor/ README.md
```

Share via Slack, email, or shared drive.

### What Recipients Need

1. **Cursor IDE** installed
2. **Skill folder** in their workspace (`.cursor/skills/qforge/`)
3. **GitHub MCP** configured for company repositories

### Quick Setup for Recipients

1. Extract/clone to their Cursor workspace
2. Ensure structure includes: `[workspace]/.cursor/skills/qforge/SKILL.md`
3. Configure GitHub MCP (see [MCP Setup Guide](./setup/MCP-SETUP.md))
4. Type `/qforge` to start

### Verification

After setup, recipients should verify:
- `/qforge` displays the welcome menu
- GitHub MCP can search repositories
- `test-jams/` directory is created on first use

---

## Documentation Index

| Document | Description |
|----------|-------------|
| [QUICK-START.md](./QUICK-START.md) | 5-minute quickstart guide |
| [setup/FIRST-TIME-SETUP.md](./setup/FIRST-TIME-SETUP.md) | Complete first-time setup |
| [setup/MCP-SETUP.md](./setup/MCP-SETUP.md) | MCP configuration guide |
| [setup/TEST-ACCOUNT-SETUP.md](./setup/TEST-ACCOUNT-SETUP.md) | Test account creation |
| [setup/Admin Console-NAVIGATION.md](./setup/Admin Console-NAVIGATION.md) | admin-console navigation guide |
| [guides/TESTING-GUIDE.md](./guides/TESTING-GUIDE.md) | Testing and troubleshooting |
| [reference/FORMAT-REFERENCE.md](./reference/FORMAT-REFERENCE.md) | CSV format specification |
| [risk/GUIDE.md](./risk/GUIDE.md) | Risk analysis guide |
| [templates/](./templates/) | Template files for outputs |

---

## Version History

- **v1.0.0** (2026-04-03): QualityForge Consolidation
  - Consolidated documentation structure
  - Added version checking with GitHub release tags
  - Added usage metrics tracking
  - Added Google Sheets creation for test jams
  - Moved Playwright to `_project-dev/` (deprecated)
  - Streamlined menu to 4 core features

- **v2.0** (2026-01-09): QualityForge Rebrand
  - Rebranded as QualityForge - comprehensive Quality Engineering Suite
  - New `/qforge` command with menu-driven interface
  - Test Case/Jam Generation (live and fully functional)
  - Risk Analysis feature (BETA)
  - Maintained backward compatibility

- **v1.0** (2025-11-20): Initial release
  - Interactive test jam creation
  - GitHub MCP integration
  - Smart test case distribution
  - CSV output per participant
  - Markdown summary reports


