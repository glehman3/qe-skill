# Test Case Coverage Map

**Feature:** <FEATURE NAME>  
**Test Suite:** <path to test cases CSV>  
**Total Test Cases:** <N>  
**Generated:** <YYYY-MM-DD>

---

## Coverage Metrics Summary

| Metric | Value | Status |
|--------|-------|--------|
| Requirements Covered | X / Y | XX% - PASS/FAIL |
| Risks Covered | X / Y | XX% - PASS/FAIL |
| Total Test Cases | N | - |
| P0 (Critical) Tests | N | - |
| P1 (High) Tests | N | - |
| P2 (Medium) Tests | N | - |

---

## Requirements to Test Cases Matrix

| Req ID | Requirement | Priority | Test Cases | Coverage |
|--------|-------------|----------|------------|----------|
| REQ-001 | <requirement text> | P0 | TC-001, TC-002 | N tests - Strong/Covered/Gap |
| REQ-002 | <requirement text> | P1 | TC-003 | N tests - Strong/Covered/Gap |

---

## Risks to Test Cases Matrix

| Risk ID | Risk Title | Severity | Test Cases | Coverage Status |
|---------|------------|----------|------------|-----------------|
| RISK-001 | <risk title> | CRITICAL | TC-001, TC-002 | Strong/Warning/Gap |
| RISK-002 | <risk title> | HIGH | TC-003 | Strong/Warning/Gap |

---

## Test Cases by Category

### <Category Name> (N tests)

| Test ID | Test Name | Priority | Risks Covered |
|---------|-----------|----------|---------------|
| TC-001 | <test name> | P0 | RISK-001 |
| TC-002 | <test name> | P1 | RISK-002, RISK-003 |

---

## Coverage Gaps and Recommendations

| Gap | Affected Risk | Priority | Recommendation |
|-----|---------------|----------|----------------|
| <gap description> | RISK-001 | HIGH | <action to take> |
| <gap description> | RISK-002 | MEDIUM | <action to take> |

### Recommended Additional Test Cases

| Test ID | Description | Priority | Addresses Gap |
|---------|-------------|----------|---------------|
| TC-NEW-001 | <description> | P1 | <gap name> |

---

## Traceability Matrix

### Requirements → Test Cases

| Requirement | Test Cases |
|-------------|------------|
| REQ-001 | TC-001, TC-002, TC-003 |
| REQ-002 | TC-004, TC-005 |

### Risks → Test Cases

| Risk | Test Cases |
|------|------------|
| RISK-001 (Critical) | TC-001, TC-002 |
| RISK-002 (High) | TC-003, TC-004 |

---

## Sources

- **Risk Analysis:** <path to risk_analysis_report.md>
- **Test Cases:** <path to test cases CSV>
- **Requirements:** <source of requirements (PRD/CSV/Jira)>
