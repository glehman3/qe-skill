# Testing Guide - /qforge Command

This guide will help you test and validate the `/qforge` command implementation.

## How to Test the Command

### Step 1: Invoke the Command

In Cursor, simply type:
```
/qforge
```

Select Option 1 (Test Case/Jam Generation) from the menu. The AI should respond with the Test Jam workflow options.

### Step 2: Test with Example PR

For your first test, use a real PR from an company repository you have access to:

```
Example input:
PR: https://github.com/nova-corp/helix-api/pull/[number]
Focus: Core functionality and regression testing
```

### Step 3: Specify Participants

```
Example: 3
```

### Step 4: Answer Context Questions

```
1. Primary focus: Functional and regression testing
2. Specific areas: User authentication and data validation
3. Timeline: Testing tomorrow, results by Friday
4. Environments: Chrome, Firefox, Safari desktop browsers
```

### Step 5: Verify Output

After generation, check:
- Files created in `test-jams/[timestamp-name]/` (relative to repository root)
- CSV files exist for each participant
- `test_jam_summary.md` is comprehensive
- Test cases are well-formatted and actionable

---

## Test Scenarios

### Test Scenario 1: Single PR (Basic)
**Input**:
- Single PR URL
- 3 participants
- Focus on functional testing

**Expected Output**:
- 3 CSV files created
- Test cases evenly distributed
- Summary includes PR details
- Test cases relevant to PR changes

### Test Scenario 2: Multiple PR's
**Input**:
- 2-3 PR URLs (comma-separated)
- 5 participants
- Mixed focus (functional + performance)

**Expected Output**:
- 5 CSV files created
- Test cases cover all PR's
- Priority balanced across participants
- Summary lists all PR's

### Test Scenario 3: Repository-based
**Input**:
- Repository name (e.g., "nova-corp/helix-api")
- 7 participants
- Last 4 weeks focus

**Expected Output**:
- Tool fetches recent PR's
- Prioritizes critical PR's
- 7 CSV files with balanced distribution
- Summary includes PR analysis

### Test Scenario 4: Large Team
**Input**:
- Single large PR
- 10 participants
- Comprehensive testing

**Expected Output**:
- 10 CSV files created
- Even distribution (6-7 cases each if 60 total)
- Priority levels balanced
- Each participant has manageable workload

---

## Validation Checklist

After running `/qforge` → Option 1, verify:

### ✅ Files Created
- [ ] Timestamped folder exists in `test-jams/`
- [ ] Correct number of participant CSV files
- [ ] `test_jam_summary.md` exists
- [ ] Files are not empty

### ✅ CSV Format
- [ ] Headers match expected format
- [ ] All required columns present
- [ ] Test IDs are sequential (TC-001, TC-002, etc.)
- [ ] No malformed CSV data

### ✅ Content Quality
- [ ] Test cases are relevant to PR/repo
- [ ] Pre-conditions are clear
- [ ] Test steps are actionable
- [ ] Expected results are specific
- [ ] Priority levels appropriate

### ✅ Distribution
- [ ] Test cases evenly distributed
- [ ] Priority levels balanced
- [ ] Related cases grouped together
- [ ] No duplicate test IDs

### ✅ Summary Report
- [ ] Overview is clear
- [ ] PR's listed with links
- [ ] Critical areas identified
- [ ] Participant breakdown included
- [ ] Timeline specified
- [ ] Success criteria defined

---

## Troubleshooting Test Issues

### Issue: Command not recognized
**Solution**:
- Ensure `.cursor/skills/qforge/SKILL.md` exists in your cloned `qe-suite/` folder
- Restart Cursor (Cmd+Q / fully quit) so it reloads skills

### Issue: MCP GitHub errors
**Solution**:
- Verify GitHub MCP is configured in Cursor
- Check repository access permissions
- Use valid, accessible repository names
- Ensure PR exists and isn't deleted

### Issue: No files generated
**Solution**:
- Check permissions on `test-jams/` directory
- Verify the command completed successfully
- Look for error messages in Cursor
- Check disk space

### Issue: Poor test case quality
**Solution**:
- Provide more specific focus areas
- Add context about what's critical
- Mention specific components or features
- Try regenerating with clearer input

---

## Example Test Run

Here's a complete example you can use to test:

```
User: /qforge

AI: 🛠️ Welcome to Quality Engineering Suite by QE Suite!
    (powered by QualityForge)
    
    📋 AVAILABLE FEATURES:
    [1] Test Case/Jam Generation
    ...
    
User: 1

AI: Test Jam Workflow Options
    [A] Create New Test Jam (generate test cases)
    [B] Complete Test Jam (upload completed CSV → generate Jira draft tickets)
    [C] Return to Main Menu

User: a

AI: Let's create comprehensive test cases! 🎯
    To get started, please provide:
    - PR URL(s) or Repository name
    - Any specific areas of focus or concerns

User: https://github.com/nova-corp/helix-api/pull/12345
      Focus on SMS functionality, especially error handling and quota management

AI: Thank you for submitting those! 
    How many participants will be part of this Test Jam?

User: 5

AI: Great! A few more questions to help create the best test cases:
    1. What is the primary focus?
    2. Are there any specific user flows or features that need extra attention?
    3. What is the testing timeline/deadline?
    4. Any specific devices, browsers, or environments to prioritize?

User: 1. Functional testing and regression
      2. SMS sending API, quota validation, error messages
      3. Testing tomorrow (Nov 21), results by Nov 22 EOD
      4. Chrome desktop, iOS Safari mobile

AI: [Fetches PR details using GitHub MCP...]
    [Analyzes changes and generates test cases...]
    [Creates CSV files and summary...]

    ✅ Test Jam Created Successfully!
    
    📁 Location: test-jams/2025-11-20_sms-pr-12345/
    
    📊 Summary:
    - Total Test Cases: 35
    - Participants: 5
    - Files Generated:
      - testjam_participant_1.csv (7 test cases)
      - testjam_participant_2.csv (7 test cases)
      - testjam_participant_3.csv (7 test cases)
      - testjam_participant_4.csv (7 test cases)
      - testjam_participant_5.csv (7 test cases)
      - test_jam_summary.md
    
    🎯 Next Steps:
    1. Review the test_jam_summary.md for overview
    2. Distribute CSV files to participants
    3. Brief participants on focus areas
    4. Schedule test jam session
    5. Track results and report findings
```

---

## Verifying MCP Integration

To ensure GitHub MCP is working:

### Check 1: MCP Configuration
Check MCP config in Cursor settings:
1. Open Cursor Settings (Cmd+, on Mac)
2. Search for "MCP"
3. Verify GitHub MCP server is listed and connected

Should show GitHub MCP server configuration with proper authentication.

### Check 2: Repository Access
The tool will use these MCP functions:
- `mcp_github-mcp_search_repositories`
- `mcp_github-mcp_get_pull_request`
- `mcp_github-mcp_get_pull_request_files`
- `mcp_github-mcp_list_pull_requests`

If these aren't available, configure GitHub MCP in Cursor.

---

## Performance Expectations

### Expected Timing:
- **User input phase**: 1-2 minutes (interactive)
- **PR analysis**: 10-30 seconds (depends on MCP API)
- **Test case generation**: 30-60 seconds (depends on complexity)
- **File creation**: < 5 seconds

### Total time: 2-5 minutes from start to finish

---

## Success Indicators

Your implementation is working correctly if:

1. ✅ Command invokes without errors
2. ✅ Interactive prompts guide you through process
3. ✅ GitHub MCP successfully fetches PR data
4. ✅ Test cases are generated and relevant
5. ✅ CSV files are properly formatted
6. ✅ Distribution is even and balanced
7. ✅ Summary report is comprehensive
8. ✅ Files are created in correct location
9. ✅ Test cases are actionable and clear
10. ✅ Participant count matches file count

---

## Next Steps After Testing

Once you've verified the command works:

1. **Share with team**: Introduce `/qforge` to QA team
2. **Create real test jams**: Use for actual PR testing
3. **Gather feedback**: Ask users about improvements
4. **Iterate**: Update rules based on feedback
5. **Document successes**: Track time saved and bugs found

---

## Getting Help

If you encounter issues:
1. Check this testing guide
2. Review the main README
3. Look at example session output
4. Verify MCP configuration
5. Check Cursor console for errors

---

**Ready to test?** Open Cursor and type `/qforge` to get started!

---

## Troubleshooting

### Common Issues and Solutions

#### ❌ Issue: `=NAME?` Errors in Excel/Google Sheets

**Symptoms:**
- When opening generated CSV files in Excel or Google Sheets, cells display `=NAME?` instead of expected content
- Often affects Pre-conditions, Test Steps, or Expected Results columns
- Makes the CSV file difficult or impossible to read

**Root Cause:**
Excel/Google Sheets interprets certain characters at the start of a cell as formulas:
- `-` (dash/minus) → Excel thinks it's a formula
- `=` (equals) → Formula indicator
- `+` (plus) → Formula operator
- `@` (at sign) → Formula reference

When test cases use **bullet points** like `- User is logged in`, Excel sees the `-` and tries to interpret it as a formula, resulting in `=NAME?` errors.

**Solution 1: Prevention (Preferred)**
When generating test cases, **always use numbered lists**, never bullet points:

✅ **CORRECT** (Numbered Lists):
```
1. User is logged in
2. Valid credentials available
3. SMS credits > 10
```

❌ **WRONG** (Bullet Points - causes =NAME? errors):
```
- User is logged in
- Valid credentials available
- SMS credits > 10
```

**Solution 2: Fix Existing CSV Files**

If you already have CSV files with bullet points that are showing `=NAME?` errors:

**Option A: Re-generate the Test Cases**
1. Run `/qforge` again with the same input
2. The updated command will now generate numbered lists
3. Replace the old CSV files with the new ones

**Option B: Manual Fix in Spreadsheet**
1. Open the CSV in Excel/Google Sheets
2. For each cell showing `=NAME?`:
   - Click the cell
   - Press F2 or double-click to edit
   - Add a single quote `'` at the very beginning
   - Press Enter
3. This forces Excel to treat it as text, not a formula
4. Re-export as CSV when done

**Option C: Python Script to Fix CSV**
```python
import csv

def fix_csv_file(input_file, output_file):
    """Add single quote prefix to cells starting with formula characters"""
    formula_chars = ('=', '+', '-', '@', '\t', '\r')
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        reader = csv.reader(f_in)
        rows = list(reader)
    
    # Fix each cell
    for row in rows[1:]:  # Skip header
        for i, cell in enumerate(row):
            if cell and cell[0] in formula_chars:
                row[i] = "'" + cell
    
    # Write fixed CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerows(rows)

# Usage
fix_csv_file('testjam_all_test_cases.csv', 'testjam_all_test_cases_fixed.csv')
```

**Prevention for Future Test Jams:**

The `/qforge` command has been updated to:
1. ✅ Always use numbered lists (1., 2., 3.)
2. ✅ Never use bullet points (-, *, •)
3. ✅ Validate formatting before CSV generation
4. ✅ Apply sanitization to prevent formula injection
5. ✅ Include explicit warnings in documentation

---

#### 🔍 Issue: CSV Not Opening Correctly in Excel

**Symptoms:**
- All data appears in one column
- Strange characters displayed (encoding issues)
- Missing line breaks in multi-line fields

**Also common:**
- Columns look "shifted" (e.g., content appears under **Status**/**Tester**)
  - Usually caused by **unquoted commas** in a field (often Objective/Test Name), which breaks the CSV structure.

**Solutions:**
1. **Import as Data** instead of double-clicking:
   - Excel: Data → From Text/CSV → Select file → Import
   - Google Sheets: File → Import → Upload → Select file
2. **Ensure UTF-8 encoding**:
   - CSV files should be saved as UTF-8
   - When importing, select UTF-8 as the character encoding
3. **Multi-line fields**:
   - Excel should automatically wrap cells with line breaks
   - If not working, check that cells are quoted in CSV
4. **Run the CSV structural validator (recommended)**:
   - `python3 qualityforge/test_jam_csv_validate.py --test-jam <session-name>`
   - This will catch misquoted commas/newlines that cause column shifts.

---

#### 📝 Issue: Test Steps Not Displaying as Separate Lines

**Symptoms:**
- Test Steps, Pre-conditions, or Expected Results appear on one line
- Numbered items run together without line breaks

**Cause:**
CSV may be using pipe `|` delimiter instead of actual newlines

**Solution:**
Test cases should use actual newlines (`\n`) within quoted cells, not pipe delimiters.

When generating test cases, the format should be:
```csv
"1. Step one
2. Step two
3. Step three"
```

NOT:
```csv
"1. Step one | 2. Step two | 3. Step three"
```

---

#### ⚠️ Issue: "Type" Column Shows as "Test Type"

**Symptoms:**
- Column 5 header is "Test Type" instead of "Type"
- May cause import issues with some test management systems

**Solution:**
The correct header is simply "Type" (not "Test Type"). If your CSV has "Test Type":
1. Open CSV in text editor
2. Find & replace: `Test Type` → `Type` (in header row only)
3. Save and re-import

---

#### 🔐 Issue: Formula Injection Security Warnings

**Symptoms:**
- Security warnings when opening CSV
- Spreadsheet application warns about potential formulas

**Cause:**
Cells starting with `=`, `+`, `-`, `@` without sanitization

**Solution:**
All QualityForge CSVs should have formula injection prevention applied. If you see warnings:
1. Cells starting with formula characters should be prefixed with `'`
2. Use numbered lists (not bullet points) for better compatibility
3. Re-generate test cases with updated `/qforge` command

---

### Best Practices to Avoid Issues

1. ✅ **Always use numbered lists** (1., 2., 3.) in:
   - Pre-conditions
   - Test Steps
   - Expected Results

2. ✅ **Never use bullet points** (-, *, •) in CSV fields

3. ✅ **Use proper CSV import**:
   - Don't double-click CSV files
   - Use "Import" or "Open with" in Excel/Sheets

4. ✅ **Keep CSV files UTF-8 encoded**

5. ✅ **Test CSV import** immediately after generation:
   - Open one file in Excel/Sheets
   - Verify no `=NAME?` errors
   - Check that multi-line fields display correctly
   - If issues found, fix before distributing to participants

---

### Quick Reference: Numbered Lists vs Bullet Points

| Format | Status | Excel Behavior |
|--------|--------|----------------|
| `1. User is logged in` | ✅ CORRECT | Displays as text |
| `2. Navigate to page` | ✅ CORRECT | Displays as text |
| `- User is logged in` | ❌ WRONG | Shows `=NAME?` error |
| `* Navigate to page` | ❌ WRONG | May show errors |
| `• Item description` | ❌ WRONG | May show errors |

**Remember**: When in doubt, use numbered lists!


