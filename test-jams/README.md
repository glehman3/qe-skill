# Test Jams Output Directory

This directory contains generated test jam sessions created by **`/qforge` Feature 1 (Test Case/Jam Generation)**.

Notes:
- **Primary command**: `/qforge`
- **Legacy compatibility**: `/testjam` (still available; test case/jam generation only)

## Structure

Each test jam session is stored in its own timestamped folder:

```
test-jams/
  ├── 2025-11-20_sms-features/
  │   ├── testjam_all_test_cases.csv
  │   ├── testjam_participant_1.csv
  │   ├── testjam_participant_2.csv
  │   ├── testjam_participant_3.csv
  │   └── test_jam_summary.md
  ├── 2025-11-21_authentication-pr-12345/
  │   ├── testjam_all_test_cases.csv
  │   ├── testjam_participant_1.csv
  │   ├── testjam_participant_2.csv
  │   └── test_jam_summary.md
  └── ...
```

## Folder Naming Convention

Folders use the format: `YYYY-MM-DD_[descriptive-name]`

- **Date**: When the test jam was created
- **Name**: Descriptive name based on PR or repository being tested

## Files in Each Session

### Master CSV File
- **Format**: `testjam_all_test_cases.csv`
- **Purpose**: Complete test plan with ALL test cases in one file
- **Content**: Every test case generated for the test jam
- **Usage**: Reference, import to test management systems, complete overview

### Participant CSV Files
- **Format**: `testjam_participant_[number].csv`
- **Purpose**: Individual test case assignments for each participant
- **Content**: Subset of test cases assigned to specific participant

### Summary Report
- **Format**: `test_jam_summary.md`
- **Purpose**: Overview and context for the entire test jam
- **Content**: 
  - What's being tested
  - PR's or changes included
  - Critical areas of focus
  - Test case distribution
  - Timeline and success criteria
  - Additional notes

## CSV Format with Execution Tracking

All CSV files include execution tracking columns for real-time test management:

```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
```

**Execution Tracking Columns** (initially blank, filled during testing):
- **Status**: `Not Started`, `Pass`, `Fail`, `Blocked`, `Skip`
- **Tester**: Name/email of person executing the test
- **Date Tested**: Date in `YYYY-MM-DD` format
- **Actual Results**: What actually happened during testing
- **Notes**: Observations, edge cases, or comments
- **Bug ID**: Reference to filed bug (e.g., `JIRA-1234`)

## Using Test Jam Files

### Recommended Workflow (Google Sheets)

1. **Review Master File**: Check `testjam_all_test_cases.csv` for complete test plan
2. **Review Summary**: Read `test_jam_summary.md` to understand scope and priorities
3. **Import to Google Sheets** (recommended):
   - Upload CSV files to Google Sheets
   - Share with all participants
   - Enable real-time collaboration
   - Use filters to track progress by Status column
   - Apply conditional formatting for Pass/Fail visualization
4. **Brief Team**: Review critical areas and priorities together
5. **Execute Tests**: Participants work through assigned test cases and **fill tracking columns**:
   - Mark Status as Pass, Fail, Blocked, or Skip
   - Add Tester name
   - Record Date Tested
   - Document Actual Results
   - Add Notes for edge cases
   - Link Bug IDs for failures
6. **Monitor Progress**: Use Google Sheets filters and formulas to track:
   - Tests completed vs remaining
   - Pass/Fail rates
   - Blocked test cases
   - Bug density
7. **Report Findings**: Export completed sheet or compile results

### Alternative: Local CSV Workflow

1. **Distribute CSV Files**: Send each participant their individual CSV file
2. **Track in CSV**: Participants fill execution tracking columns locally
3. **Collect Results**: Gather updated CSV files from all participants
4. **Consolidate**: Merge results for reporting

## ⚠️ IMPORTANT: Repository Policy

**Default policy: don’t commit real customer/test data or large, one-off sessions.**

This repository ships with:
- ✅ **Curated examples** (e.g., `_example_session/`) to show expected output formats
- ✅ Documentation and templates under `qualityforge/`
- ✅ The `test-jams/` folder as the canonical output location when you run `/qforge`

When you run real sessions, treat them as **local artifacts** unless you explicitly want to share them:
- Don’t commit anything with sensitive data
- Avoid committing very large CSVs (token/size bloat)
- Prefer archiving outputs in your test management system / drive

### Why?
- Token/size optimization: Large CSVs significantly increase repo + AI context size
- Data hygiene: real sessions may contain sensitive info
- Workflow: completed test jams are usually better stored in your test management system or local archives

## Archiving Completed Test Jams

When a test jam is complete, **archive it locally or in your test management system**:

### Recommended Archival Options:
1. **Google Drive/Confluence**: Upload completed Google Sheets and summary
2. **Jira/Test Management System**: Import results into your test tracking system
3. **Local Archive**: Move completed sessions to a local `~/archived-testjams/` directory
4. **Delete from repo**: Remove the session folder to keep the repository clean

### What to Archive:
- Completed Google Sheets (with execution tracking filled out)
- Final `test_jam_summary.md` with results
- Links to filed bugs
- Any post-mortem notes or learnings

## Best Practices

- **Use Google Sheets**: Import CSVs to Google Sheets for easier collaboration and real-time tracking
- **Fill tracking columns**: Always complete Status, Tester, Date Tested, Actual Results, Notes, and Bug ID
- **File bugs immediately**: When tests fail, file bugs and add the ID to the Bug ID column
- **Export completed results**: Save a copy of the completed Google Sheet for records
- **Don't modify generated files**: If you need changes, regenerate the test jam
- **Reference PRs**: Always link back to the original PR or change being tested
- **Document blockers**: Use Status "Blocked" and note reason in Notes column
- **Track progress**: Use filters and formulas to monitor completion rates


