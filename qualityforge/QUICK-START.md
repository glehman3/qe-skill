# Quick Start Guide - Test Jam Generator

## Prerequisites

Before using `/testjam` or `/qforge`:
- ✅ **GitHub MCP must be configured** in Cursor
- ⭐ Mabl MCP is optional (enhances test generation)
- ⭐ Google Drive MCP is optional (enables Google Sheets creation for test jams)

**Setup Guides** (choose one):
- **👋 First Time User?** → [FIRST-TIME-SETUP.md](./setup/FIRST-TIME-SETUP.md) - Complete walkthrough from scratch
- **⚙️ Configure MCPs** → [MCP-SETUP.md](./setup/MCP-SETUP.md) - Quick MCP configuration

---

## Step 1: Invoke the Command

In Cursor, simply type:

```
/testjam
```

For all features including Risk Analysis, use:

```
/qforge
```

**First Time?** The tool will automatically verify your MCP setup:
- ✅ If GitHub MCP is configured → Proceed to test jam creation
- ⚠️ If GitHub MCP is missing → You'll get setup instructions with a link to [MCP-SETUP.md](./setup/MCP-SETUP.md)

**What to Expect**: The tool will automatically verify MCP setup and guide you through any missing configuration.

**Manual Verification**: At any time, you can check your setup by asking: "check my MCP setup"

## Step 2: Provide Input Source

When prompted, provide ONE of these options:

**Option A - PR(s)** (Recommended):
```
https://github.com/org/project/pull/12345
```

Or multiple PR's (comma-separated):
```
https://github.com/org/project/pull/12345, https://github.com/org/project/pull/12346
```

**Option B - Repository:**
```
Repository: org/project
```

**Option C - PRD** (Early Stage Testing):
```
PRD URL: https://confluence.example.com/display/MAIL/SMS-Feature

PRD Contents: [Paste the full PRD text here, including:]
- PRD Title
- All sections (User Stories, Acceptance Criteria, Technical Requirements, etc.)
- Complete requirements and specifications
```

**Important**: Both PRD URL and full contents are required. This ensures test cases can be traced back to specific PRD sections.

**Also specify:**
- Specific focus areas (e.g., "Focus on SMS functionality and error handling")
- Whether to check Mabl for existing test coverage (optional)

## Step 3: Specify Number of Participants

```
7
```

## Step 4: Answer Context Questions

Provide information about:
- Primary testing focus (functional, regression, performance, security)
- Specific user flows or features needing attention
- Testing timeline/deadline
- Devices, browsers, or environments to prioritize
- **Mabl integration**: Should I check Mabl for existing test coverage? (yes/no)
  - If yes: Tool will identify automation gaps and suggest opportunities
  - If no: Standard test generation without Mabl data

## Step 5: Wait for Generation

The tool will:
1. ✅ Fetch PR details from GitHub
2. ✅ Analyze changes and identify critical areas
3. ✅ Generate comprehensive test cases
4. ✅ Split test cases across participants
5. ✅ Create CSV files and summary report

## Step 6: Review Output

Check the generated files at:
```
test-jams/[session-name]/
```

Files include:
- `testjam_all_test_cases.csv` - Master file with ALL test cases
- `testjam_participant_1.csv` through `testjam_participant_[N].csv` - Individual assignments
- `test_jam_summary.md` - Summary and overview

## Step 7: Distribute and Execute

1. **Review the master file** (`testjam_all_test_cases.csv`) for complete test plan
2. **Import to Google Sheets** (recommended):
   - Upload CSV files to Google Sheets for easier collaboration
   - Share sheets with participants for real-time tracking
   - Use filters and conditional formatting for better visibility
3. **Share the summary** with all participants
4. **Send each participant** their individual CSV file or sheet link
5. **Brief the team** on priorities and focus areas
6. **Execute the test jam** with participants:
   - Work through assigned test cases
   - **Fill execution tracking columns**:
     * Status: `Pass`, `Fail`, `Blocked`, or `Skip`
     * Tester: Your name/email
     * Date Tested: Today's date
     * Actual Results: What you observed
     * Notes: Edge cases, observations
     * Bug ID: Link to filed bugs
7. **Monitor progress** via Google Sheets (if using)
8. **Collect results** and report findings

## Tips for Success

### Choosing Participant Count
- **Small PR** (UI fix, minor bug): 3-5 participants
- **Medium PR** (new feature, significant change): 5-8 participants
- **Large PR or Repo** (major release, multiple features): 8-15 participants

### What Makes Good Input
✅ **Good Examples:**
- Specific PR URLs with context
- Clear focus areas mentioned
- Realistic participant count

❌ **Avoid:**
- Vague repository names without context
- Too many participants for small changes
- No focus areas specified

### Example Session

```
User: /testjam

AI: Welcome to easy Test Jam creation! 🎯
    To get started, please provide:
    1. PR URL(s) or Repository name(s) to be tested
    2. Any specific areas of focus or concerns

User: https://github.com/org/project/pull/12345
      Focus: SMS sending functionality, especially error handling

AI: Thank you for submitting those! 
    How many participants will be part of this Test Jam?

User: 7

AI: Great! A few more questions to help create the best test cases:
    1. What is the primary focus?
    2. Are there any specific user flows or features that need extra attention?
    3. What is the testing timeline/deadline?
    4. Any specific devices, browsers, or environments to prioritize?

User: 1. Functional and regression testing
      2. Error handling when SMS quota exceeded
      3. Testing tomorrow, need results by end of week
      4. Mobile browsers (iOS Safari, Chrome Android) and desktop Chrome

AI: [Analyzes PR, generates test cases, creates files...]

    ✅ Test Jam Created Successfully!
    
    📁 Location: test-jams/2025-11-20_sms-pr-12345/
    
    📊 Summary:
    - Total Test Cases: 42
    - Participants: 7
    - Files Generated:
      - testjam_all_test_cases.csv (42 test cases) ⭐ Master file
      - testjam_participant_1.csv (6 test cases)
      - testjam_participant_2.csv (6 test cases)
      - testjam_participant_3.csv (6 test cases)
      - testjam_participant_4.csv (6 test cases)
      - testjam_participant_5.csv (6 test cases)
      - testjam_participant_6.csv (6 test cases)
      - testjam_participant_7.csv (6 test cases)
      - test_jam_summary.md
    
    🎯 Next Steps:
    1. Review the test_jam_summary.md for overview
    2. Distribute CSV files to participants
    3. Brief participants on focus areas
    4. Schedule test jam session
    5. Track results and report findings
```

## Need Help?

- Review the full README at `qualityforge/README.md`
- Check example test case formats in existing CSV files
- Re-run `/qforge` (or `/testjam` for legacy) with different parameters if needed
- Adjust focus areas or participant count and regenerate

## Common Questions

**Q: Can I modify the generated test cases?**
A: It's better to regenerate with clearer requirements, but you can manually edit CSV files if needed.

**Q: What if there are too many/too few test cases?**
A: Re-run `/testjam` and specify more focused areas or adjust your scope.

**Q: Can I test multiple PR's together?**
A: Yes! Provide multiple PR URLs separated by commas.

**Q: How long should a test jam take?**
A: Plan 5-15 minutes per test case. A 7-person test jam with 42 cases should take 1-2 hours.

**Q: What if a PR isn't found?**
A: Verify the URL, check repository access, and ensure the PR exists and isn't deleted.

---

## Workflow Examples

### Workflow 1: PR-based with Mabl Integration

**Scenario**: Analyzing a specific pull request with automation coverage analysis

1. Invoke `/qforge` → Select Option 1
2. Provide PR URL: `https://github.com/org/project/pull/12345`
3. Specify participants: `7`
4. Answer context questions, opt for Mabl integration
5. Tool fetches PR details, queries Mabl for existing coverage
6. Generates test cases with automation status fields

**Example Output:**
```
✅ Test Jam Created Successfully!

📊 Summary:
- Total Test Cases: 45
- Already Automated in Mabl: 12
- Can Be Automated: 18
- Manual Only: 15
```

### Workflow 2: PRD-based (Early Stage Testing)

**Scenario**: Creating test cases from a Product Requirements Document before implementation

1. Invoke `/qforge` → Select Option 1
2. Provide PRD URL and full PRD contents
3. Tool extracts PRD title and sections
4. Generates test cases using `[PRD: Title] [Section] Test Name` format
5. PRD Reference column tracks traceability

**Example Test Case Naming:**
- `[PRD: SMS Scheduling Feature] [User Stories] Verify user can schedule SMS`
- `[PRD: SMS Scheduling Feature] [Acceptance Criteria] Validate cancellation flow`

### Workflow 3: Repository-based

**Scenario**: Testing all changes merged in the last 4 weeks

1. Invoke `/qforge` → Select Option 1
2. Provide repository name: `org/project`
3. Tool fetches last 4 weeks of merged PRs
4. Prioritizes critical and high-priority PRs
5. Generates test cases grouped by PR/component

**Example Output:**
```
✅ Test Jam Created Successfully!

📊 Summary:
- Analyzed 23 PRs from the last 4 weeks
- Focused on 8 critical PRs affecting core functionality
- Total Test Cases: 67
```

### Tips for Success

1. **Be Specific**: Provide clear PR URLs, repo names, or full PRD content
2. **Add Context**: Mention specific areas of concern or focus
3. **Right-Size Participants**:
   - Small PR (1-2 features): 3-5 participants
   - Medium changes (3-5 features): 5-8 participants
   - Major release: 8-15 participants
4. **Mabl Integration**: Say "yes" to identify automation gaps
5. **Review First**: Always review the summary before distributing


