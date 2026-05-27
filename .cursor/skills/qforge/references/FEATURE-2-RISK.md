# Feature 2: Risk Analysis (Pre-Development) — **BETA**

*When user selects Option 2, proceed with this workflow*

## Goal

Generate a **risk analysis report** before implementation by ingesting documentation and mapping requirements to codebase touch points, then identifying risks with mitigations and questions.

## Content Accuracy Rules (must follow)

Use: `qualityforge/risk/CONTENT-ACCURACY-RUBRIC.md`

Key rules:
- Do **not** invent metrics (coverage %, churn counts, complexity numbers) unless you actually verified them.
- Every risk must include **Evidence + Confidence**.
- If something is uncertain, state it as an **assumption** and add a **question** or **spike** to validate it.

## MCP Requirements (Feature 2)

- **Required**: DAST-Orch (GitHub) - codebase search/mapping
- **Optional**: DAST-Orch (Jira) - ticket details
- **Optional**: Google Drive MCP - Docs/Sheets access

If optional MCPs are not available, continue with user-provided text/attachments and clearly note the limitation in the report.

## Interactive Flow

### Step 0: Preflight (required)

Order matters: **verify required MCP first** so we don't waste time collecting inputs we can't validate.

- Confirm **GitHub MCP is available** (required for code touch points).
  - If missing: show setup instructions and STOP.
- Check optional MCPs (DAST-Orch Jira, Google Drive). If DAST-Orch Jira available, verify with `jira_search_issues`. If missing, continue with message: "Continuing without Jira integration - please paste ticket content manually."

### Step 1: Welcome + Input Collection (streamlined)

Start with:

```
🔍 Risk Analysis (BETA)

Let's identify implementation risks before coding.

Please paste ONE block containing:

REQUIRED:
1) PRD URL
2) PRD full content (full text)
3) Repository (org/repo), e.g. org/project

OPTIONAL (recommended):
4) Jira ticket URL or key (e.g., TXPLAT-1234, TESTING-1518)
5) Figma file URL
6) Any specific concerns (performance, security, rollout, migrations, etc.)

OPTIONAL (streamlining):
7) Depth: quick | thorough (default: quick)
```

**Depth guidance**:
- `quick`: focus on highest-signal touch points + top risks (recommended for speed)
- `thorough`: broader codebase mapping + deeper dependency/ownership considerations

### Step 2: Ingest Documentation (build a unified requirements summary)

Implementation guidance:
- Parse PRD content into:
  - goals, user stories, acceptance criteria, constraints, success metrics
- If DAST-Orch Jira is available and a ticket is provided:
  - Call `jira_search_issues` with issueKeys to fetch ticket details
  - Or use `get_issue` (requires `eiam_login` auth) for full details
  - Extract description, ACs, comments (include links)
- If design URL is provided:
  - extract key UI components, flows, and notable constraints
- Produce a short "Unified Requirements Summary" section for the report.

### Step 3: Codebase Touch Points (GitHub MCP search)

Implementation guidance:
- Use GitHub MCP to:
  - identify likely impacted services/components/files
  - locate existing APIs, models, schemas, and key entry points
  - list relevant directories and key files with brief "why it matters"
- Output should include:
  - file paths
  - component/service names
  - external dependencies/3rd parties mentioned
  - best-effort code references (line ranges/snippets) when available

### Step 4: Risk Identification (4 categories + severity)

Generate risks across:
- **Technical**
- **Integration**
- **Downstream**
- **Team/Process**

Rules:
- Each risk MUST have a unique ID (`RISK-001`, `RISK-002`, ...)
- Severity MUST be one of:
  - 🔴 Critical (P0)
  - 🟠 High (P1)
  - 🟡 Medium (P2)
  - 🟢 Low (P3)
- Each risk includes: description, affected areas, impact, and **2–3 mitigations**

**Output quality requirements (AC9)**:
- Use severity symbols (🔴/🟠/🟡/🟢) + P-levels (P0–P3)
- Include file paths and best-effort line references in "Codebase Touch Points"
- Assign unique IDs (`RISK-001`, `RISK-002`, …)

### Step 5: Questions + Spikes + Testing Complexity

Include:
- Clarifying questions (by urgency)
- Recommended spikes/POCs (with success criteria)
- Testing complexity assessment (what's hard to validate and why)

### Step 6: Write Outputs (canonical location)

Write to:
`test-jams/{YYYY-MM-DD}_{feature-slug}-risk-analysis/`

**Markdown Files** (always generated):
- `risk_analysis_report.md` (full report)
- `risk_summary.md` (executive summary)
- `test_coverage_map.md` (if test cases exist - maps requirements/risks to test cases)

The report MUST link back to source documentation (PRD URL, Jira URL, Figma URL when provided).

**Report template**:
- Use: `qualityforge/templates/RISK-REPORT-TEMPLATE.md` as the canonical structure for `risk_analysis_report.md`
- Use the Evidence tags convention:
  - `REQ-###` for requirements evidence (PRD/Jira/Figma)
  - `CODE-###` for code evidence (GitHub MCP search/file reads)

### Step 6.5: Quality Gate (required for completion)

- After writing `risk_analysis_report.md`, run the checker:
  - `python3 qualityforge/risk/risk_report_quality.py test-jams/{YYYY-MM-DD}_{feature-slug}-risk-analysis/risk_analysis_report.md`
- Ensure it outputs:
  - `risk_quality_report.json` in the same folder
  - A clear PASS/FAIL summary
- If it fails: run **Self-Repair** (max **2** attempts) and re-run the checker after each repair.

### Step 6.7: Generate DOCX Outputs (required for sharing)

After the quality gate passes, generate formatted Word documents for sharing/upload:

```bash
# Create virtual environment if not exists
python3 -m venv test-jams/{YYYY-MM-DD}_{feature-slug}-risk-analysis/.venv
source test-jams/{YYYY-MM-DD}_{feature-slug}-risk-analysis/.venv/bin/activate
pip install python-docx

# Generate DOCX files
python3 qualityforge/risk/generate_risk_docx.py test-jams/{YYYY-MM-DD}_{feature-slug}-risk-analysis/
```

**DOCX Files Generated**:
- `risk_analysis_report.docx` - Full risk analysis with proper tables and formatting
- `test_coverage_map.docx` - Test case coverage mapping (if test_coverage_map.md exists)

**Branding Applied**:
- **Font**: Avenir Next For company (company brand font)
- **Colors**: Peppercorn (#241C15) for headers, white text on dark table headers
- **Tables**: Native Word tables with proper borders and styling

**Why DOCX instead of HTML/PDF**:
- Native Word tables render correctly in Google Docs when uploaded
- Pandoc HTML→DOCX conversion loses table formatting; `python-docx` creates native tables
- Recipients can edit/comment in Google Docs

**Ask user**: "Would you like me to generate the DOCX files for sharing? (yes/no)"

### Step 6.6: Self-Repair Loop (max 2 attempts, safe fixes only)

**Goal**: improve the report until the quality gate **PASSes** without lowering content integrity.

Rules:
- **Max attempts**: 2 total.
- **No invented evidence**: do NOT add fake `REQ-###`/`CODE-###` tags. Only reference evidence you actually observed from the provided PRD/Jira/Figma or GitHub MCP mapping.
- **No invented metrics**: do NOT introduce numbers like coverage %, churn, complexity, record counts, or timing claims unless explicitly evidenced.
- **Prefer "clarify, don't guess"**: if information is missing, downgrade confidence and add a question/spike rather than making up facts.

**Repair actions allowed (safe):**
- Add missing required sections (e.g., "Unified Requirements Summary", "Assumptions").
- Add missing `**Confidence:** High|Medium|Low` line for a risk (choose the lowest confidence that matches the available evidence).
- Replace unverified metric claims with:
  - an explicit **assumption** + **verification step** (question/spike), or
  - remove the claim if it can't be supported.
- If evidence tags are missing but you *do* have evidence from earlier steps:
  - add the correct `REQ-###`/`CODE-###` references and a short evidence bullet.

**Stopping condition:**
- If still failing after 2 attempts:
  - stop self-repair,
  - summarize the remaining findings (high-signal only),
  - ask the minimum follow-up inputs needed to resolve (e.g., missing repo, missing PRD content, missing Jira key).

### Step 7: Test Coverage Mapping (if test cases exist)

If test cases have already been generated for this feature (either from Feature 1 or provided by user):

1. Generate `test_coverage_map.md` using template: `qualityforge/templates/TEST-COVERAGE-MAP-TEMPLATE.md`
2. Map each requirement (REQ-###) to its covering test cases
3. Map each risk (RISK-###) to test cases that mitigate it
4. Calculate coverage metrics:
   - Requirements coverage: X/Y requirements have at least 1 test
   - Risk coverage: X/Y risks have at least 1 mitigating test
5. Identify coverage gaps and recommend additional test cases
6. Include in DOCX generation

### Step 8: Optional Handoff to Test Case Generation (AC8 hook)

Ask:
```
Would you like to proceed to Test Case/Jam Generation next (Feature 1) using this risk report to emphasize high-risk areas? (yes/no)
```

If yes:
- continue into Feature 1 and explicitly bias coverage toward the highest severity risks and touch points.
