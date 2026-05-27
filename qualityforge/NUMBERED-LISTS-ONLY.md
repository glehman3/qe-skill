# 🚨 NUMBERED LISTS ONLY - NO BULLET POINTS EVER 🚨

---

## THE RULE (No Exceptions)

### ✅ ALWAYS Use This Format:

```
1. First item
2. Second item
3. Third item
4. Fourth item
5. Fifth item
```

---

### ❌ NEVER Use These Formats:

```
- First item          ← ❌ NO
- Second item         ← ❌ NO
- Third item          ← ❌ NO

* First item          ← ❌ NO
* Second item         ← ❌ NO

• First item          ← ❌ NO
• Second item         ← ❌ NO

+ First item          ← ❌ NO
+ Second item         ← ❌ NO

First; Second; Third  ← ❌ NO
```

---

## Where This Applies

### MANDATORY for these 3 fields:

1. **Pre-conditions** → Numbered lists ONLY
2. **Test Steps** → Numbered lists ONLY
3. **Expected Results** → Numbered lists ONLY

---

## Why This Matters

### What Happens with Bullet Points:

```
CSV Cell Contains:        Excel Displays:
"- User is logged in"  →  =NAME? ❌ ERROR
"* Navigate to page"   →  =NAME? ❌ ERROR
"• Click button"       →  =NAME? ❌ ERROR
```

### What Happens with Numbered Lists:

```
CSV Cell Contains:           Excel Displays:
"1. User is logged in"    →  1. User is logged in ✅ CORRECT
"2. Navigate to page"     →  2. Navigate to page ✅ CORRECT
"3. Click button"         →  3. Click button ✅ CORRECT
```

---

## Real Examples

### ✅ CORRECT Example

```csv
Test ID: TC-001
Pre-conditions:
"1. User is logged in
2. Valid API credentials available
3. SMS credits > 10
4. Test phone number configured"

Test Steps:
"1. Navigate to SMS dashboard
2. Click Send SMS button
3. Enter phone number
4. Enter message text
5. Click Send
6. Verify confirmation"

Expected Results:
"1. SMS sent successfully
2. Confirmation message displays
3. Credit balance decrements
4. Message appears in sent history"
```

**Opens in Excel**: ✅ Perfect - No errors

---

### ❌ WRONG Example (DO NOT USE)

```csv
Test ID: TC-001
Pre-conditions:
"- User is logged in
- Valid API credentials available
- SMS credits > 10
- Test phone number configured"

Test Steps:
"- Navigate to SMS dashboard
- Click Send SMS button
- Enter phone number
- Enter message text
- Click Send
- Verify confirmation"

Expected Results:
"- SMS sent successfully
- Confirmation message displays
- Credit balance decrements
- Message appears in sent history"
```

**Opens in Excel**: ❌ =NAME? errors everywhere

---

## Quick Check

### Before You Generate/Save:

☑ Pre-conditions starts with `1.` ?  
☑ Test Steps starts with `1.` ?  
☑ Expected Results starts with `1.` ?  

☑ No `-` at start of lines?  
☑ No `*` at start of lines?  
☑ No `•` at start of lines?  
☑ No `;` separating items?  

**All checked?** → ✅ Good to save!

**Any NO?** → ❌ Fix before saving!

---

## Remember

| Format | Status | Excel Result |
|--------|--------|--------------|
| `1. Item` | ✅ USE THIS | Works perfectly |
| `2. Item` | ✅ USE THIS | Works perfectly |
| `3. Item` | ✅ USE THIS | Works perfectly |
| `- Item` | ❌ NEVER | =NAME? error |
| `* Item` | ❌ NEVER | =NAME? error |
| `• Item` | ❌ NEVER | =NAME? error |
| `+ Item` | ❌ NEVER | =NAME? error |
| `Item; Item` | ❌ NEVER | Wrong format |

---

## If You See Bullet Points

### STOP! Convert Immediately:

**Wrong**:
```
- User is logged in
- Navigate to page
- Click button
```

**Right**:
```
1. User is logged in
2. Navigate to page
3. Click button
```

---

## No Exceptions

This rule applies to:
- ✅ ALL test jams
- ✅ ALL test cases
- ✅ ALL CSV files
- ✅ ALL examples
- ✅ ALL documentation
- ✅ ALL scenarios

**NO EXCEPTIONS. NUMBERED LISTS ONLY.**

---

## When In Doubt

**Just use numbered lists (1., 2., 3.)**

It's that simple.

---

**Last Updated**: January 8, 2026  
**Status**: MANDATORY  
**Enforcement**: AUTOMATIC

