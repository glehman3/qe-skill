# Example Test Jam Session

**Last Updated**: January 8, 2026  
**Purpose**: Reference examples for TestJam CSV format and structure

---

## ⚠️ IMPORTANT: CSV Format Standards

All CSV files in this folder follow the **corrected format** that prevents Excel `=NAME?` errors:

### ✅ CORRECT Format (Used in These Examples)

**Pre-conditions**: Numbered lists
```
1. Valid API credentials
2. SMS plan with available credits
3. Test phone number
```

**Test Steps**: Numbered lists
```
1. Authenticate with valid API credentials
2. Call /messages/send-sms endpoint
3. Include required parameters
```

**Expected Results**: Numbered lists
```
1. API returns 200 status code
2. Response includes message_id
3. SMS is queued for delivery
```

### ❌ NEVER Use This Format

**Pre-conditions**: ~~Semicolon-separated~~ (WRONG)
```
Valid API credentials; SMS plan active; Test phone number
```

**Expected Results**: ~~Bullet points~~ (WRONG - causes =NAME? errors)
```
- API returns 200 status code
- Response includes message_id
- SMS is queued for delivery
```

---

## Files in This Folder

### Test Case Files

**testjam_all_test_cases.csv**
- Master file containing all 14 test cases
- Use as reference for complete test jam structure
- Shows all categories: Functional, Security, Performance, Regression, etc.

**testjam_participant_1.csv**
- First 7 test cases (TC-001 through TC-007)
- Focus: Core API functionality, security, performance baseline
- Priority breakdown: 3 P0, 3 P1, 1 P2

**testjam_participant_2.csv**
- Last 7 test cases (TC-008 through TC-014)
- Focus: Advanced features, integrations, accessibility, error handling
- Priority breakdown: 2 P0, 3 P1, 2 P2

### Other Files

**EXAMPLE_PRD_FORMAT.md**
- Shows how test cases are generated from PRD content
- Demonstrates PRD traceability format
- Example of PRD-based naming convention

**test_jam_summary.md**
- Example summary report for a test jam session
- Shows overview, distribution, timeline, success criteria
- Template for organizing test jam documentation

**testjam_test_accounts.csv**
- Example test account creation CSV
- Shows account setup format for test jams
- Includes account configuration details

---

## Format Compliance

### Version History

| Date | Version | Changes |
|------|---------|---------|
| Jan 8, 2026 | v2.0 | **FIXED**: Converted to numbered lists throughout |
| | | - Pre-conditions: Changed from semicolons to numbered lists |
| | | - Expected Results: Changed from bullet points to numbered lists |
| | | - Prevents Excel =NAME? errors |
| Before | v1.0 | Original version (had formatting issues) |

### Validation Checklist

When these examples were last updated, we verified:

- ✅ All Pre-conditions use numbered lists (1., 2., 3.)
- ✅ All Test Steps use numbered lists (1., 2., 3.)
- ✅ All Expected Results use numbered lists (1., 2., 3.)
- ✅ No bullet points (-, *, •) in any CSV files
- ✅ No semicolon-separated lists
- ✅ Files open correctly in Excel without =NAME? errors
- ✅ All multi-line fields display properly with line breaks

---

## Using These Examples

### For AI Generation

When `/testjam` command generates test cases, it should follow the format demonstrated in these examples:

1. **Test ID**: TC-001, TC-002, etc.
2. **Category**: Functional Testing, Security Testing, Performance Testing, etc.
3. **Test Name**: [org/repo] [TICKET-ID] Descriptive Name
4. **Priority**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
5. **Type**: Manual, Automated, Manual + Automated
6. **Component**: The system component being tested
7. **Objective**: Clear statement of what is being verified
8. **Pre-conditions**: Numbered list (1., 2., 3.)
9. **Test Steps**: Numbered list (1., 2., 3.)
10. **Expected Results**: Numbered list (1., 2., 3.)
11. **Status, Tester, Date Tested, Actual Results, Notes, Bug ID**: All BLANK (filled during execution)

### For Manual Creation

If manually creating test cases:

1. Copy the format from these examples
2. Use numbered lists for Pre-conditions, Test Steps, and Expected Results
3. Never use bullet points or semicolon-separated lists
4. Keep execution tracking columns blank

### For Testing

To verify CSV format is correct:

1. Open CSV file in Excel or Google Sheets
2. Check that no cells show `=NAME?` error
3. Verify all multi-line fields display with proper line breaks
4. Confirm Pre-conditions, Test Steps, and Expected Results are readable

---

## Related Documentation

- [TROUBLESHOOTING.md](../../qualityforge/guides/TROUBLESHOOTING.md) - Comprehensive troubleshooting guide
- [csv-formats.md](../../qualityforge/templates/csv-formats.md) - Detailed CSV format specifications
- [FORMAT-REFERENCE.md](../../qualityforge/reference/FORMAT-REFERENCE.md) - Complete CSV technical reference
- [NUMBERED-LISTS-ONLY.md](../../qualityforge/NUMBERED-LISTS-ONLY.md) - Visual guide to numbered-list enforcement

---

## Verification

These example files were opened in Excel after update to verify:

- ✅ No `=NAME?` errors
- ✅ All cells display correctly
- ✅ Multi-line fields show line breaks
- ✅ Numbered lists display cleanly
- ✅ Professional appearance

**Last Verified**: January 8, 2026

---

## Questions?

If you find formatting issues in these examples or have questions:

1. Check [TROUBLESHOOTING.md](../../qualityforge/guides/TROUBLESHOOTING.md) for common issues
2. Ensure you're using the latest version of these files

**Remember**: Always use numbered lists, never bullet points! 🎯

