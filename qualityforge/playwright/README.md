# Playwright Test Generation (Feature 3) — **BETA**

**Status**: **BETA** · Phase 6 ✅ Complete · Phase 7 🔄 In Progress  
**JIRA**: [TESTING-1514](https://jira.example.com/browse/TESTING-1514)

Automatically generate executable Playwright E2E tests from test case CSV files using real application patterns.

---

## Quick Links

- **🎯 Application Patterns** (PRIMARY): [reference/PLAYWRIGHT-PATTERNS.md](../reference/PLAYWRIGHT-PATTERNS.md) ← **AI Agents: Read this FIRST!**
- **📚 Generic Best Practices**: [reference/PLAYWRIGHT-BEST-PRACTICES.md](../reference/PLAYWRIGHT-BEST-PRACTICES.md)
- **⚙️ Main Workflow**: [.cursor/skills/qforge/references/FEATURE-3-PLAYWRIGHT.md](../../.cursor/skills/qforge/references/FEATURE-3-PLAYWRIGHT.md)
- **🧾 Validation Report Contract**: [VALIDATION-REPORT.md](VALIDATION-REPORT.md) (schema: [validation-report.schema.json](validation-report.schema.json))
- **🚀 How to Use**: Playwright generation guide (coming soon) (Coming in Phase 8)

### Planning Docs (Development Only)
These planning docs live under `_project-dev/` locally and are intentionally **not** shipped with the repo clone.

---

## What It Does

Converts manual test cases (CSV) → Executable Playwright tests (TypeScript/JavaScript)

**Input**: Test case CSV from Feature 1 (Test Case Generation)  
**Output**: Ready-to-run Playwright test suite

### Optional (Recommended): Playwright MCP for Higher Accuracy

If the end user has a running local/staging target app, installing **Playwright MCP** allows the agent to validate real flows and generate higher-confidence locators from the accessibility tree.

- **Install/Run** (Node 18+):

```bash
npx @playwright/mcp@latest
```

- **Reference**: [Playwright MCP server](https://github.com/microsoft/playwright-mcp)

**How QualityForge uses this** (high-level):
- Use MCP-driven snapshots to confirm UI structure
- Prefer Acme Platform-first locator patterns (`getByRole`, `getByLabel`, `getByText`)
- Replace TODO placeholders where the live UI makes the intent unambiguous

If Playwright MCP is not installed, generation still works (it just relies on CSV + heuristics + application patterns and will produce more TODOs).

#### Using MCP output with the generator (optional)

If you capture stable, verified locators/steps using Playwright MCP, you can feed them into the generator as a JSON hints file:

```bash
python3 qualityforge/playwright/generator.py \
  --test-jam 2026-01-12_streamlined-tx-template-management \
  --language ts \
  --locator-hints /absolute/path/to/locator-hints.json
```

The hints file supports high-confidence regex step overrides (best) and simple URL keyword→path mappings. If omitted, the generator behaves exactly as before.

#### Workflow: generate a hints seed from TODOs (recommended starting point)

If a generated suite has many TODO steps, you can create a seed file that lists the missing steps so you can fill them using Playwright MCP:

```bash
python3 qualityforge/playwright/generator.py \
  --emit-locator-hints-seed /absolute/path/to/playwright-tests
```

This writes:
- `playwright-tests/locator-hints.seed.json`

Fill in `step_overrides[].code` entries (leave empty ones untouched), then regenerate with:

```bash
python3 qualityforge/playwright/generator.py \
  --test-jam 2026-01-12_streamlined-tx-template-management \
  --language ts \
  --locator-hints /absolute/path/to/playwright-tests/locator-hints.seed.json
```

### Example

**CSV Test Case**:
```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results
TC-001,Functional,User Login,P0,Manual,Authentication,Verify user can login,"1. User has valid credentials","1. Navigate to login page
2. Enter email
3. Enter password
4. Click login button","1. Page redirects to dashboard
2. Welcome message displays
3. User menu is visible"
```

**Generated Playwright Test**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('[TC-001] User Login @P0', async ({ page }) => {
    // Original test case: TC-001 - User Login
    // Objective: Verify user can login
    
    // Pre-conditions: User has valid credentials
    const email = 'test@example.com';
    const password = 'SecurePass123';
    
    // Step 1: Navigate to login page
    await page.goto('/login');
    
    // Step 2: Enter email
    await page.getByLabel('Email').fill(email);
    
    // Step 3: Enter password
    await page.getByLabel('Password').fill(password);
    
    // Step 4: Click login button
    await page.getByRole('button', { name: 'Login' }).click();
    
    // Expected: Page redirects to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Expected: Welcome message displays
    await expect(page.getByText('Welcome')).toBeVisible();
    
    // Expected: User menu is visible
    await expect(page.getByRole('navigation', { name: 'User menu' })).toBeVisible();
  });
});
```

---

## Implementation

### Core Module: `generator.py`

All generation logic is in ONE consolidated file for consistency and easy AI reference.

**Sections**:
1. **CSVParser** - Parse test case CSV files
2. **ActionDetector** - Detect Playwright actions from natural language test steps
3. **TestGenerator** - Generate Playwright test code using templates
4. **ConfigGenerator** - Generate playwright.config.ts files
5. **Validator** - Self-healing validation and auto-fix (Phase 7)

**Why one file?** Ensures consistency, prevents drift, easy for AI to reference complete logic.

---

## Phase Progress

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Foundation - Menu structure & workflow |
| Phase 2 | ✅ Complete | Core Generation - CSV → Playwright tests with application patterns |
| Phase 3 | ✅ Complete | Test Structure - Authentication hooks, .env.example, pre-condition analysis |
| Phase 4 | ✅ Complete | Configuration - playwright.config.ts, package.json, cross-browser support |
| Phase 5 | ⏭️ Deferred | API Testing - Support API test generation |
| Phase 6 | ✅ Complete | Quality Polish - validation, timeouts, logging, error handling |
| Phase 7 | 🔄 In Progress | Self-Healing - static validation + optional runtime validation |
| Phase 8 | ⏳ Pending | Documentation - User guides |

---

## File Structure (Clean & Consolidated)

```
qualityforge/
├── guides/
│   ├── PLAYWRIGHT-GENERATION.md           # User-facing guide (Phase 8)
│   ├── TESTING-GUIDE.md                   # Testing strategies
│   ├── TROUBLESHOOTING.md                 # Common issues
│   └── ...
│
├── reference/
│   ├── PLAYWRIGHT-PATTERNS.md   # PRIMARY - Real application patterns
│   ├── PLAYWRIGHT-BEST-PRACTICES.md       # Generic Playwright best practices
│   ├── FORMAT-REFERENCE.md                # CSV formats
│   └── WORKFLOW-EXAMPLES.md               # Example workflows
│
├── templates/
│   ├── playwright-test.spec.ts            # TypeScript test template
│   ├── playwright-test.spec.js            # JavaScript test template
│   ├── playwright.config.ts               # Config template
│   └── playwright-README.md               # Generated README template
│
└── playwright/
    ├── README.md                          # This file
    └── generator.py                       # Consolidated generator (all logic)
```

**Total Active Files**: 2 (generator.py + README.md)  
**Reference Docs**: 4 in `reference/`  
**No Archives**: Keeping it clean!

---

## Key Design Decisions

### 1. Single Source of Truth
- All generation logic in ONE file (`generator.py`)
- Best practices in `reference/PLAYWRIGHT-PATTERNS.md` (PRIMARY)
- Generic patterns in `reference/PLAYWRIGHT-BEST-PRACTICES.md`
- No duplication = no drift = accurate tests ✅

### 2. Acme Platform-First Locators
**Priority order** (from PLAYWRIGHT-PATTERNS.md, based on real monolith code):
1. `getByRole()` - **HIGHEST** (buttons, links, headings) - Used 127+ times in monolith
2. `getByLabel()` - Form inputs, checkboxes
3. `getByText()` - Visible text with `{ exact: true }`
4. `getByTestId()` - Data attributes
5. `locator()` - Complex CSS (generates TODO comment)

### 3. Template-Based Generation
- Uses templates from `templates/` directory
- Ensures consistent structure
- Easy to update all generated tests

### 4. Natural Language → Actions
**Action patterns** (in generator.py):
- "Navigate to..." → `page.goto()`
- "Click..." → `page.getByRole('button').click()`
- "Enter..." → `page.getByLabel().fill()`
- "Verify..." → `await expect().toBeVisible()`

---

## Testing the Generator

```bash
# Example: Generate tests from an existing test jam
cd qualityforge/playwright

python generator.py \
  --test-jam 2026-01-12_streamlined-tx-template-management \
  --language ts

# Optional (Phase 7): validate generation output
# - static: validates deps/config/test discovery (does not require the app running)
python generator.py --test-jam 2026-01-12_streamlined-tx-template-management --language ts --validate --validate-mode static
#
# - runtime: executes tests against BASE_URL (requires a reachable local/staging app)
python generator.py --test-jam 2026-01-12_streamlined-tx-template-management --language ts --validate --validate-mode runtime

# Optional (recommended for runtime): write env values into playwright-tests/.env (gitignored)
python generator.py \
  --test-jam 2026-01-12_streamlined-tx-template-management \
  --language ts \
  --validate --validate-mode runtime \
  --base-url http://localhost:3000

# If authentication is required by the generated suite, you can also set credentials:
python generator.py \
  --test-jam 2026-01-12_streamlined-tx-template-management \
  --language ts \
  --validate --validate-mode runtime \
  --base-url http://localhost:3000 \
  --test-user-email you@example.com \
  --test-user-password "your-password"

### Validation Report (Phase 7)

When validation runs, QualityForge writes a machine-readable report into the generated suite:
- `playwright-tests/validation-report.json`

This report contains **no secrets** and includes:
- validation mode (static/runtime)
- base_url (if provided)
- attempt outcomes + failure summaries
- actionable `suggestions` (commands/notes) to resolve common failures (deps, browsers, env, baseURL)
- `suite_metrics` (static quality metrics like tests/specs/TODOs/assertions) to quantify generation completeness

### Validate an Existing Suite (No Regeneration)

If someone shares a generated `playwright-tests/` folder with you, you can validate it directly:

```bash
python3 qualityforge/playwright/generator.py \
  --validate-only /absolute/path/to/playwright-tests \
  --validate-mode static
```

You can also pass a single spec file path (the parent folder will be validated):

```bash
python3 qualityforge/playwright/generator.py \
  --validate-only /absolute/path/to/playwright-tests/some-test.spec.ts \
  --validate-mode static
```

### Review an Existing Spec (Static Review, No Execution)

If you need a quick “meeting-time” review of a Playwright test (especially performance tests) and don’t want to run it, use:

```bash
python3 qualityforge/playwright/generator.py \
  --review-only /absolute/path/to/playwright-tests/some-test.spec.ts
```

This writes `spec-review-report.json` into the suite folder. It flags:
- duplicate test titles (discovery blockers)
- `page.waitForTimeout()` (flaky anti-pattern)
- suspicious `page.goto()` targets (not a URL/path)
- locator strategy posture (accessible locators vs CSS `.locator()`)

Runtime validation against a running app:

```bash
python3 qualityforge/playwright/generator.py \
  --validate-only /absolute/path/to/playwright-tests \
  --validate-mode runtime \
  --base-url http://localhost:3000
```

Optional validation fix level:

```bash
python3 qualityforge/playwright/generator.py \
  --validate-only /absolute/path/to/playwright-tests \
  --validate-mode static \
  --validate-fix-level conservative
```

If auth is required, you can optionally provide credentials (written to `.env`, which is gitignored):

```bash
python3 qualityforge/playwright/generator.py \
  --validate-only /absolute/path/to/playwright-tests \
  --validate-mode runtime \
  --base-url http://localhost:3000 \
  --test-user-email you@example.com \
  --test-user-password "your-password"
```
```

---

## Related Documentation

### AI Agents: Read These First!
1. **Application Patterns** (PRIMARY): [reference/PLAYWRIGHT-PATTERNS.md](../reference/PLAYWRIGHT-PATTERNS.md)
   - Real patterns from `app-monolith/playwright` repository
   - 15 sections of production-tested code
   - Examples from 127+ test files
2. **Generic Best Practices**: [reference/PLAYWRIGHT-BEST-PRACTICES.md](../reference/PLAYWRIGHT-BEST-PRACTICES.md)
3. **Main Workflow**: [.cursor/skills/qforge/references/FEATURE-3-PLAYWRIGHT.md](../../.cursor/skills/qforge/references/FEATURE-3-PLAYWRIGHT.md)

### Users: Read These!
- **Quick Start**: [../QUICK-START.md](../QUICK-START.md)
- **Documentation Index**: [../DOCUMENTATION-INDEX.md](../DOCUMENTATION-INDEX.md)
- **Testing Guide**: [../guides/TESTING-GUIDE.md](../guides/TESTING-GUIDE.md)

### Planning Docs (Development Only)
These planning docs live under `_project-dev/` locally and are intentionally **not** shipped with the repo clone.

---

## Current Status

**What's Working**:
- CSV parsing (100 test cases)
- Action detection (60-70% success rate)
- application-specific workflows (modals, imports, management)
- Role-based locators (`getByRole`, `getByLabel`)
- Authentication hooks (`beforeEach()` with auto-login)
- Pre-condition analysis (detects auth requirements)
- `.env.example` generation (test account credentials)
- **`playwright.config.ts`** (cross-browser support) 
- **`package.json`** (dependencies & scripts) 
- **`.gitignore`** (test results & env files) 
- **`README.md`** (comprehensive documentation) 
- Proper test structure with JSDoc pre-conditions
- Clean TypeScript/JavaScript output

✅ **Phase 6 Quality Improvements**:
- Input validation (test jam name, language, CSV columns)
- Explicit assertion timeouts (default 10s)
- Enhanced parsing statistics
- Better error messages + edge case handling

🔄 **Phase 7 Validation (In Progress)**:
- `--validate-mode static`: checks Playwright availability + test discovery (no app required)
- `--validate-mode runtime`: runs tests (requires target app via `BASE_URL`)

**What's Next (Phase 7)**:
- Improve validation reporting (machine-readable summary per run)
- Add more safe auto-fixes (environment/config) without selector guessing
- Add opt-in “aggressive” mode later (guardrails required)

---

**Last Updated**: January 14, 2026  
**Maintainer**: Greg Lehman  
**Version**: 2.0 (Acme Platform-enhanced)

