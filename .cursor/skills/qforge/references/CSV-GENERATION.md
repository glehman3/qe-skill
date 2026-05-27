# CSV Generation Requirements

**CRITICAL: Use Python's csv.writer for bulletproof CSV generation**

## Implementation Code

```python
import csv

# Prepare test case data (replace newlines with pipe delimiter)
header = ["Test ID", "Category", "Test Name", "Priority", "Type", "Component", 
          "Objective", "Pre-conditions", "Test Steps", "Expected Results", 
          "Status", "Tester", "Date Tested", "Actual Results", "Notes", "Bug ID"]

def enforce_numbered_lists(text, field_name):
    """
    CRITICAL: Enforce numbered lists (1., 2., 3.) ONLY - NO bullet points EVER
    
    This function MUST be called on Pre-conditions, Test Steps, and Expected Results
    before writing to CSV.
    
    Converts any bullet points (-, *, •, +) or semicolon lists to numbered lists.
    
    Why: Bullet points cause Excel =NAME? errors
    Rule: Pre-conditions, Test Steps, Expected Results → ALWAYS numbered lists
    """
    import re
    
    if not text or not text.strip():
        return text
    
    # Check for forbidden bullet points
    has_bullets = bool(re.search(r'^\s*[-*•+]\s+', text, re.MULTILINE))
    has_semicolons = ';' in text and '\n' not in text
    
    if has_bullets or has_semicolons:
        # Convert to numbered list
        if has_semicolons:
            items = [item.strip() for item in text.split(';') if item.strip()]
        else:
            lines = text.split('\n')
            items = []
            for line in lines:
                line = line.strip()
                if line:
                    # Remove leading bullet characters
                    line = re.sub(r'^[-*•+]\s+', '', line)
                    if line:
                        items.append(line)
        
        # Create numbered list
        text = '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])
        print(f"WARNING: {field_name} auto-converted to numbered list (had bullet points)")
    
    # Verify numbered list exists
    if text and not re.search(r'^\d+\.', text, re.MULTILINE):
        items = [line.strip() for line in text.split('\n') if line.strip()]
        if items:
            text = '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])
    
    return text

def sanitize_csv_cell(cell_value):
    """
    Prevent CSV formula injection while preserving multi-line formatting
    
    CRITICAL: This function MUST be called on EVERY cell value before writing to CSV
    
    Why: Excel/Google Sheets interpret cells starting with =, +, -, @, \t, \r as formulas
    Result: Causes #NAME?, #REF!, #VALUE! errors when users open the CSV
    Solution: Prefix these cells with single quote (') to force text interpretation
    
    Example:
        Input:  "- User is logged in"
        Output: "'- User is logged in"
        Excel displays: "- User is logged in" (no formula error)
    """
    if not cell_value:
        return cell_value
    
    cell_value = str(cell_value)
    
    formula_chars = ('=', '+', '-', '@', '\t', '\r')
    if cell_value and cell_value[0] in formula_chars:
        cell_value = "'" + cell_value  

    return cell_value

# CRITICAL: Enforce numbered lists on required fields FIRST (before sanitization)
for test_case in test_cases:
    test_case['Pre-conditions'] = enforce_numbered_lists(
        test_case['Pre-conditions'], 
        f"{test_case['Test ID']} Pre-conditions"
    )
    test_case['Test Steps'] = enforce_numbered_lists(
        test_case['Test Steps'], 
        f"{test_case['Test ID']} Test Steps"
    )
    test_case['Expected Results'] = enforce_numbered_lists(
        test_case['Expected Results'], 
        f"{test_case['Test ID']} Expected Results"
    )

# Then sanitize all fields to prevent formula injection
for test_case in test_cases:
    for key in test_case:
        test_case[key] = sanitize_csv_cell(test_case[key])

# Write CSV using csv.writer (cross-platform compatible)
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    # UTF-8-sig includes BOM for Excel compatibility on Windows
    # newline='' prevents extra blank lines on Windows
    # QUOTE_MINIMAL quotes only when necessary
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    writer.writerow(header)
    writer.writerows(test_case_rows)
    
# Verify file was written successfully
print(f"CSV written: {output_path}")
print(f"   Encoding: UTF-8 with BOM (Excel/Sheets compatible)")
print(f"   Line endings: LF (cross-platform)")
print(f"   Format: Numbered lists (no bullet points)")
```

## Key Requirements

1. **Use numbered format (1., 2., 3.)** for Pre-conditions, Test Steps, and Expected Results
   - All three fields MUST use numbered lists for consistency
   - Keep `\n` newlines intact - csv.writer will quote cells automatically
   - **Format examples** (actual content will vary per test case):
     * **Pre-conditions**: `1. User is logged in\n2. Credits available\n3. Valid phone number`
     * **Test Steps**: `1. Navigate to dashboard\n2. Click button\n3. Verify result`
     * **Expected Results**: `1. Page loads\n2. Button is visible\n3. Result displays`
   - Content is flexible - format structure is what matters (numbered lists)
   - Displays beautifully in Excel/Sheets as line breaks within cells

2. **CSV Formula Injection Prevention** (CRITICAL for security)
   - If cell starts with `=`, `+`, `-`, `@`, `\t`, or `\r`, prefix with single quote `'`
   - Example: `- User is logged in` → `'- User is logged in`
   - Prevents Excel/Google Sheets from interpreting cells as formulas
   - Eliminates `#NAME?`, `#REF!`, and other formula errors

3. **Column 5 must be "Type"** not "Test Type"

4. **Use csv.writer with QUOTE_MINIMAL**
   - Automatically quotes cells with newlines, commas, and special characters
   - Combined with sanitization function for complete protection
   - No manual escaping needed
   - Bulletproof for all edge cases

5. **Why this approach:**
   - Eliminates CSV formatting bugs (commas, quotes, special chars)
   - Prevents CSV formula injection (security + usability)
   - Natural multi-line formatting (not ` | ` delimiters)
   - Standard library (battle-tested, no dependencies)
   - Negligible performance impact (<1ms for 100 test cases)
   - Industry best practice for secure CSV generation

## Example Output Structure

```
test-jams/
  └── 2025-11-20_sms-features/
      ├── testjam_all_test_cases.csv      # Master file with ALL test cases
      ├── testjam_participant_1.csv       # Subset for participant 1
      ├── testjam_participant_2.csv       # Subset for participant 2
      ├── testjam_participant_3.csv       # Subset for participant 3
      └── test_jam_summary.md
```

## Important Notes

- Generate the master file FIRST with all test cases, then split them into individual participant files
- Always use Python's `csv.writer` for writing CSV files (never manual string formatting)
- All execution tracking columns (Status, Tester, Date Tested, Actual Results, Notes, Bug ID) must be initialized as **EMPTY/BLANK**

## CSV Format Reference

See [qualityforge/templates/csv-formats.md](../../../../qualityforge/templates/csv-formats.md) for complete format specifications.
