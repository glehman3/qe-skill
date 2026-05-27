# CSV Format Reference Guide

**Last Updated**: January 8, 2026  
**Purpose**: Comprehensive guide to CSV format requirements and cross-platform compatibility

---

## 🚨 Critical Rule (Most Important)

### Pre-conditions, Test Steps, Expected Results → **NUMBERED LISTS ONLY**

✅ **ALWAYS Use**:
```
1. First item
2. Second item
3. Third item
```

❌ **NEVER Use**:
```
- Bullet points  ← Causes Excel =NAME? errors
* Asterisks      ← Causes Excel =NAME? errors  
• Bullet symbols ← Causes Excel =NAME? errors
+ Plus signs     ← Causes Excel =NAME? errors
```

**Why**: Cells starting with `-` cause Excel to display `=NAME?` errors

**Visual Guide**: See [../NUMBERED-LISTS-ONLY.md](../NUMBERED-LISTS-ONLY.md) for quick visual reference

---

## Quick Reference

### Format Rules

| Rule | Requirement | Reason |
|------|-------------|--------|
| Pre-conditions | Numbered lists (1., 2., 3.) | Excel compatibility |
| Test Steps | Numbered lists (1., 2., 3.) | Excel compatibility |
| Expected Results | Numbered lists (1., 2., 3.) | Excel compatibility |
| Bullet points | ❌ NEVER | Causes =NAME? errors |
| Semicolons | ❌ NEVER | Inconsistent format |

### Quick Check

Before generating/saving CSV:
- ☑ Pre-conditions starts with `1.`?
- ☑ Test Steps starts with `1.`?
- ☑ Expected Results starts with `1.`?
- ☑ No `-` at start of lines?
- ☑ No `*` at start of lines?
- ☑ No `;` separating items?

**All checked?** → ✅ Safe to save!

---

## Cross-Platform Compatibility

### Platforms Tested & Supported

✅ **Microsoft Excel**:
- Excel for Windows (2016, 2019, 2021, 365)
- Excel for Mac (2016, 2019, 2021, 365)
- Excel Online (Web)

✅ **Google Sheets**:
- Google Sheets (Web)
- Google Sheets (Mobile - iOS/Android)

✅ **Other Tools**:
- LibreOffice Calc
- Numbers (Mac)
- Any RFC 4180 compliant CSV reader

---

### Technical Implementation

#### 1. UTF-8-sig Encoding (BOM for Excel)

**Code**:
```python
encoding='utf-8-sig'  # UTF-8 with BOM (Byte Order Mark)
```

**Why**:
- ✅ Excel on Windows recognizes UTF-8 automatically
- ✅ Special characters display correctly (é, ñ, 中, etc.)
- ✅ Google Sheets handles UTF-8 natively
- ✅ No "gibberish" characters

**Without BOM**:
- ❌ Excel on Windows shows garbled characters
- ❌ Requires manual encoding selection

---

#### 2. LF Line Endings (Unix-style)

**Code**:
```python
lineterminator='\n'  # Unix-style line endings
```

**Why**:
- ✅ Works on Windows, Mac, Linux
- ✅ Smaller file size
- ✅ Git-friendly (no CRLF issues)
- ✅ Excel and Sheets handle LF correctly

---

#### 3. QUOTE_MINIMAL Quoting

**Code**:
```python
quoting=csv.QUOTE_MINIMAL
```

**Why**:
- ✅ Quotes only when necessary
- ✅ Keeps file size small
- ✅ Maximum compatibility
- ✅ Readable in text editors

**Quotes Added When**:
- Cell contains comma
- Cell contains newline
- Cell contains quote character
- Cell starts/ends with whitespace

---

#### 4. Empty newline Parameter

**Code**:
```python
newline=''  # Let csv.writer handle line endings
```

**Why**:
- ✅ Prevents extra blank lines on Windows
- ✅ csv.writer manages line endings correctly
- ✅ Cross-platform consistent output

---

### Multi-line Cells

**CSV Content**:
```csv
"1. First step
2. Second step
3. Third step"
```

**Displays In Excel/Sheets**:
```
┌─────────────────┐
│ 1. First step   │
│ 2. Second step  │
│ 3. Third step   │
└─────────────────┘
```

Both platforms show line breaks within the cell correctly!

---

## Format Enforcement

### Automatic Conversion

The `/testjam` command automatically enforces correct format:

```python
def enforce_numbered_lists(text, field_name):
    """
    Automatically converts bullet points → numbered lists
    
    Detects: -, *, •, +, semicolons
    Converts: To numbered lists (1., 2., 3.)
    Logs: Warnings when conversion happens
    """
```

**Called on Every Test Case**:
- Pre-conditions
- Test Steps
- Expected Results

**Result**: Even if AI accidentally generates bullet points, they're automatically converted!

---

### Formula Injection Prevention

**The Problem**:
Cells starting with `=`, `+`, `-`, `@` are interpreted as formulas by Excel/Sheets

**The Solution**:
```python
if cell_value[0] in ('=', '+', '-', '@', '\t', '\r'):
    cell_value = "'" + cell_value
```

**Result**:
- Excel: Treats as text, displays without quote
- Sheets: Treats as text, displays without quote
- Both: No formula errors

---

## Opening CSV Files

### Microsoft Excel

**Method 1: Import (Recommended)**:
1. Open Excel
2. Go to: **Data** → **From Text/CSV**
3. Select your CSV file
4. Excel auto-detects encoding and format
5. Click **Load**

**Method 2: Double-click** (works with UTF-8-sig):
1. Double-click CSV file
2. Excel opens it correctly (thanks to BOM)
3. Multi-line cells display properly

---

### Google Sheets

**Method 1: Import**:
1. Open Google Sheets
2. Go to: **File** → **Import**
3. Click **Upload** tab
4. Drag CSV file or browse
5. Select import location
6. Click **Import data**

**Method 2: Drive Upload**:
1. Upload CSV to Google Drive
2. Right-click file
3. **Open with** → **Google Sheets**
4. Sheets converts to native format

---

## Troubleshooting Format Issues

### Issue: `=NAME?` Errors in Excel

**Cause**: Cell starts with `-` (bullet point)

**Solution**:
1. **Prevention**: Use numbered lists (1., 2., 3.)
2. **Quick Fix**: Add `'` at start of cell in Excel
3. **Regenerate**: Run `/testjam` again (auto-converts)

**See**: [../NUMBERED-LISTS-ONLY.md](../NUMBERED-LISTS-ONLY.md)

---

### Issue: All Data in One Column

**Cause**: Wrong delimiter detected

**Solution**:
- Excel: Data → From Text/CSV → Select comma delimiter
- Sheets: Import and ensure comma is selected

---

### Issue: Garbled Characters (é → Ã©)

**Cause**: Wrong encoding detected

**Solution**:
- Ensure file saved as UTF-8 with BOM (`utf-8-sig`)
- Excel: Import and select UTF-8 encoding
- Sheets: Usually auto-detects correctly

---

### Issue: Multi-line Cells Show as One Line

**Cause**: Text not wrapped

**Solution**:
- Excel: Format Cells → Alignment → Wrap Text
- Sheets: Usually auto-wraps (check Text wrapping setting)

---

## Validation

### Before Releasing CSV Files

Test on these platforms:

☑ **Excel Windows**
- Import via Data → From Text/CSV
- Check multi-line cells
- Verify no `=NAME?` errors
- Check special characters

☑ **Excel Mac**
- Import via Data → From Text/CSV
- Check multi-line cells
- Verify no `=NAME?` errors

☑ **Google Sheets**
- Import via File → Import
- Check multi-line cells
- Verify no formula errors

---

## Best Practices Summary

### ✅ DO

1. **Always use numbered lists** (1., 2., 3.)
2. **Use UTF-8-sig encoding** (includes BOM)
3. **Use LF line endings** (`\n`)
4. **Use QUOTE_MINIMAL** quoting
5. **Use `newline=''`** parameter
6. **Test on both Excel and Sheets**
7. **Import CSVs** (don't just double-click)

### ❌ DON'T

1. ❌ Use bullet points (-, *, •)
2. ❌ Use UTF-8 without BOM
3. ❌ Use CRLF line endings (unnecessary)
4. ❌ Use QUOTE_ALL (file size bloat)
5. ❌ Omit `newline=''` (blank lines)
6. ❌ Only test on one platform
7. ❌ Leave formula chars unescaped

---

## Skill Reference

**Location**: `.cursor/skills/qforge/SKILL.md`

**Key Requirements**:
- `enforce_numbered_lists()` - Auto-converts format
- `sanitize_csv_cell()` - Prevents formula injection

**These requirements guarantee** correct format in all generated CSV files.

---

## Related Documentation

- [../NUMBERED-LISTS-ONLY.md](../NUMBERED-LISTS-ONLY.md) - Visual format guide
- [../templates/csv-formats.md](../templates/csv-formats.md) - Complete format specs
- [../guides/TESTING-GUIDE.md](../guides/TESTING-GUIDE.md) - Testing and troubleshooting

---

**Last Updated**: January 8, 2026  
**Status**: Production Ready  
**Tested On**: Excel 365 (Windows/Mac), Google Sheets (Web)

