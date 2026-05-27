# QualityForge metrics & Google Sheets sync

QualityForge logs `/qforge` invocations to `qualityforge/metrics.log` (JSONL). Optional sync to the **Invocations** tab in the metrics spreadsheet is best-effort and must never block local logging.

## Troubleshooting: MCP `sheets_append` appears to hang

### What you may see

- The Cursor agent or tool run stalls after calling `sheets_append`.
- No error message for tens of seconds or longer; you cancel the tool call.

### Likely causes

1. **No client-side timeout** — MCP tool calls wait for the server to respond. If the Google Sheets request inside the MCP server blocks (network, DNS, proxy, or waiting on token refresh), the whole call blocks.
2. **Authentication / consent** — First-time or expired Google OAuth can stall until a browser flow completes; in headless or agent context that may never finish.
3. **Wrong MCP server** — `user-DAST-Orch` bundles many tools; its Sheets path may behave differently than a dedicated Google Drive MCP.

### Recommended workflow (avoids hangs)

1. **Always** rely on `metrics.log` as the source of truth (local-first).
2. During **`/qforge`**, agents should **not** call `user-DAST-Orch` `sheets_append` (known to block indefinitely in some environments).
3. Prefer **`user-google-drive-mcp`** `sheets_append` when that server is enabled and you need automated append.
4. **Manual, non-blocking sync** — Export rows in the terminal, paste into Sheets, then mark synced:

```bash
cd /path/to/qe-suite   # or your clone root containing qualityforge/

python3 qualityforge/metrics.py --export-pending
# Paste the TSV into the Invocations sheet (same column order as the header).

python3 qualityforge/metrics.py --mark-synced "2026-04-10T21:27:51.602511+00:00"
```

Use exact `timestamp` values from `metrics.log` or from the export output.

### Useful CLI commands

| Command | Purpose |
|--------|---------|
| `python3 qualityforge/metrics.py --summary` | Show total invocations, pending sync count, log path |
| `python3 qualityforge/metrics.py --export-pending` | Print pending rows as TSV (header + data) |
| `python3 qualityforge/metrics.py --mark-synced <ts> ...` | Mark rows synced after append |

### Spreadsheet

- **Spreadsheet ID** (from URL): `15Px9z6MBG8b5o6dZcRaLO-cnaG61LNcdbbxiAaDu_-o`
- **Sheet name**: `Invocations`

### If you maintain the DAST-Orch MCP server

A durable fix is server-side: enforce **HTTP timeouts** on all Google API calls, fail fast with a clear error, and avoid blocking the MCP response on interactive OAuth during agent sessions.
