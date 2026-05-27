## `validation-report.json` (Contract)

This document defines the **stable contract** for the Playwright suite validation report written by:

- `python3 qualityforge/playwright/generator.py --validate ...`
- `python3 qualityforge/playwright/generator.py --validate-only ...`

The report is written to:

- `playwright-tests/validation-report.json`

### Safety / Data Classification

- **No secrets**: this report must not include credentials/tokens.
- **Safe to share**: it is intended to be attachable to tickets and PRs.
- **Env reporting**: only **missing key names** are included (never values).

### Schema

- **JSON Schema**: `qualityforge/playwright/validation-report.schema.json`
- The schema is intentionally tolerant (`additionalProperties: true`) so we can add fields without breaking consumers.

## Top-level fields

- **`phase`**: integer phase marker (currently `7`)
- **`mode`**: `"static"` | `"runtime"`
- **`fix_level`**: `"conservative"` | `"aggressive"`
- **`todo_policy`**: `"allow"` | `"warn"` | `"error"` (quality-only policy for TODOs)
- **`test_dir`**: absolute path to the validated suite directory
- **`timestamp_utc`**: ISO-8601 UTC timestamp when available
- **`attempts`**: array of attempt summaries (static: 1 attempt; runtime: up to 2)
- **`result`**: `"passed"` | `"failed"` | `"skipped"`
- **`skip_reason`**: nullable string enum (set only when `result="skipped"`)
- **`base_url`**: nullable string (safe to include; no secrets)
- **`missing_keys`**: array of missing env key names (no values)
- **`applied_fixes`**: array of safe fix identifiers applied (no secrets)
- **`suggestions`**: structured actionable next steps (no secrets)
- **`suite_metrics`**: static suite quality metrics (no Playwright deps/app required)
- **`quality`**: derived quality signals (warnings + quick gates) to prevent “tests that run but are low value”

## Stable enums (consumers may rely on these)

### `result`

- `passed`
- `failed`
- `skipped`

### `skip_reason`

- `test_dir_missing`
- `invalid_mode`
- `deps_not_installed`
- `base_url_missing`
- `baseurl_invalid`
- `auth_missing`

### `attempts[].kind`

The validator attempts to bucket errors into a small set of kinds:

- `deps_missing`
- `playwright_browsers_missing`
- `env_missing`
- `baseurl_invalid`
- `test_failures`
- `config_missing`
- `exception`

## `attempts[]` structure

Each element contains:

- **`attempt`**: 1-based index
- **`kind`**: nullable failure kind (null for pass)
- **`headline`**: short summary (may be `"passed"` for pass)
- **`exit_code`**: present for runtime runs (when Playwright was executed)

## `suggestions[]` structure

Each suggestion is an object with:

- **`title`** (required): short label
- **`command`** (optional): shell command to run
- **`note`** (optional): human-readable guidance

Consumers should treat `suggestions` as optional guidance:

- For `result="passed"`, suggestions may be empty.
- For `result="failed"` / `result="skipped"`, suggestions should be present and actionable.

## `suite_metrics` keys

Current keys (stable):

- `spec_files` (int)
- `tests` (int)
- `todos` (int)
- `assertions` (int)
- `page_actions` (int)
- `auth_hooks` (int)
- `has_env_example` (bool)
- `has_env` (bool)
- `avg_todos_per_test` (number|null)
- `tests_with_zero_assertions` (int) *(heuristic)*
- `tests_with_todos` (int) *(heuristic)*
- `waitForTimeout_calls` (int) *(heuristic)*
- `css_locator_calls` (int) *(heuristic)*
- `accessible_locator_calls` (int) *(heuristic)*

## `quality` (warnings + gates)

`quality` is a convenience summary derived from `suite_metrics`:

- **`quality.warnings[]`**: array of `{ severity: low|medium|high, rule, message }`
- **`quality.gates`**: quick machine-consumable booleans (non-fatal guidance), currently:
  - `has_tests`
  - `no_zero_assertion_tests`
  - `no_waitForTimeout`
  - `no_todos`
  - `todo_policy` / `todo_policy_pass`

## Examples

### Example: skipped (deps not installed)

```json
{
  "phase": 7,
  "mode": "static",
  "fix_level": "conservative",
  "test_dir": "/abs/path/to/playwright-tests",
  "timestamp_utc": "2026-01-16T12:00:00+00:00",
  "attempts": [],
  "result": "skipped",
  "skip_reason": "deps_not_installed",
  "base_url": null,
  "missing_keys": [],
  "applied_fixes": [],
  "suggestions": [
    { "title": "Install Node dependencies", "command": "cd /abs/path/to/playwright-tests && npm install" }
  ],
  "suite_metrics": {
    "spec_files": 13,
    "tests": 100,
    "todos": 42,
    "assertions": 247,
    "page_actions": 310,
    "auth_hooks": 2,
    "has_env_example": true,
    "has_env": false,
    "avg_todos_per_test": 0.42
  }
}
```

### Example: passed (static)

```json
{
  "phase": 7,
  "mode": "static",
  "fix_level": "conservative",
  "test_dir": "/abs/path/to/playwright-tests",
  "timestamp_utc": "2026-01-16T12:00:00+00:00",
  "attempts": [
    { "attempt": 1, "kind": null, "headline": null }
  ],
  "result": "passed",
  "skip_reason": null,
  "base_url": null,
  "missing_keys": [],
  "applied_fixes": [],
  "suggestions": [],
  "suite_metrics": {
    "spec_files": 1,
    "tests": 3,
    "todos": 0,
    "assertions": 8,
    "page_actions": 20,
    "auth_hooks": 0,
    "has_env_example": true,
    "has_env": true,
    "avg_todos_per_test": 0
  }
}
```

## Backward/Forward compatibility notes

- New fields may be added at any time.
- Consumers should not assume `attempts[].headline` is non-null for passes (it is currently `"passed"` for runtime pass, and may be null for static pass).
- Consumers should treat unknown `skip_reason` / `kind` values as `"unknown"` rather than failing parsing.

