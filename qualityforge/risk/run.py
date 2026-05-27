#!/usr/bin/env python3
"""
Quality Risk Analysis runner (scaffold + optional quality gate + optional export).

This does NOT generate the risk content itself (that's produced via /qforge Feature 2).
Instead, it helps streamline the workflow by:
  - creating the canonical output folder under test-jams/
  - writing a risk_analysis_report.md from the canonical template
  - writing a stub risk_summary.md
  - optionally running the content-accuracy quality gate checker
  - optionally exporting a Google Docs-compatible .docx file
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import sys


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "feature"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _fill_template(
    template_text: str,
    *,
    date: str,
    feature_name: str,
    repo: str,
    prd_url: str,
    prd_title: Optional[str],
    jira: Optional[str],
    figma_url: Optional[str],
) -> str:
    # Keep this intentionally simple: replace the top metadata placeholders + source links placeholders.
    out = template_text

    out = out.replace("<YYYY-MM-DD>", date)
    out = out.replace("<FEATURE NAME>", feature_name)
    out = out.replace("<org/repo>", repo)

    out = out.replace("<JIRA URL OR KEY (optional)>", jira or "<JIRA URL OR KEY (optional)>")
    out = out.replace("<FIGMA URL (optional)>", figma_url or "<FIGMA URL (optional)>")

    # PRD line is markdown link with placeholders for title/url.
    title = prd_title or "<PRD TITLE>"
    out = out.replace("[<PRD TITLE>](<PRD URL>)", f"[{title}]({prd_url})")

    # Source links section at bottom.
    out = out.replace("- PRD: <PRD URL>", f"- PRD: {prd_url}")
    out = out.replace("- Jira: <Jira URL (optional)>", f"- Jira: {jira or '<Jira URL (optional)>'}")
    out = out.replace("- Figma: <Figma URL (optional)>", f"- Figma: {figma_url or '<Figma URL (optional)>'}")

    return out


def scaffold(
    *,
    out_root: Path,
    date: str,
    feature_slug: str,
    feature_name: str,
    repo: str,
    prd_url: str,
    prd_title: Optional[str],
    jira: Optional[str],
    figma_url: Optional[str],
    template_path: Path,
    overwrite: bool,
) -> Path:
    session_dir = out_root / f"{date}_{feature_slug}-risk-analysis"
    session_dir.mkdir(parents=True, exist_ok=True)

    report_path = session_dir / "risk_analysis_report.md"
    summary_path = session_dir / "risk_summary.md"

    if (report_path.exists() or summary_path.exists()) and not overwrite:
        raise FileExistsError(
            "Output files already exist. Re-run with --overwrite to replace:\n"
            f"- {report_path}\n"
            f"- {summary_path}"
        )

    template_text = _read_text(template_path)
    report_text = _fill_template(
        template_text,
        date=date,
        feature_name=feature_name,
        repo=repo,
        prd_url=prd_url,
        prd_title=prd_title,
        jira=jira,
        figma_url=figma_url,
    )
    _write_text(report_path, report_text.rstrip() + "\n")

    summary_text = (
        f"# Risk Summary: {feature_name}\n\n"
        f"**Generated:** {date}\n\n"
        "## Top Risks (Top 3)\n"
        "1. \n"
        "2. \n"
        "3. \n\n"
        "## Immediate Next Actions\n"
        "1. \n"
        "2. \n"
        "3. \n"
    )
    _write_text(summary_path, summary_text)

    return session_dir


def export_docx(report_path: Path) -> Optional[Path]:
    """
    Export the risk analysis report to a Google Docs-compatible .docx file.

    Pipeline: markdown → pandoc HTML → premailer (inline CSS) → pandoc docx.
    This ensures tables survive Google Docs import (Google Docs strips <style> blocks
    but respects inline style="" attributes on elements).

    Returns the path to the generated .docx, or None if export failed.
    """
    if not shutil.which("pandoc"):
        print("⚠️  pandoc not found — skipping .docx export. Install with: brew install pandoc")
        return None

    session_dir = report_path.parent
    html_intermediate = session_dir / "_export_intermediate.html"
    html_inlined = session_dir / "_export_inlined.html"
    docx_name = report_path.stem.replace("risk_analysis_report", "quality_risk_analysis") + ".docx"
    docx_path = session_dir / docx_name

    # Full CSS matching risk_analysis_report_styled.html
    css_block = """
    html { color: #1a1a1a; background-color: #ffffff; }
    body {
      margin: 0 auto;
      font-family: 'Google Sans', Arial, sans-serif;
      line-height: 1.6;
      max-width: 50em;
      padding-left: 50px; padding-right: 50px;
      padding-top: 40px; padding-bottom: 50px;
    }
    p { margin: 1em 0; }
    a { color: #1a73e8; text-decoration: none; }
    a:visited { color: #1a73e8; }
    img { max-width: 100%; }
    svg { height: auto; max-width: 100%; }
    h1, h2, h3, h4, h5, h6 { margin-top: 1.4em; color: #202124; }
    h2 { font-size: 1.5em; border-bottom: 2px solid #e8eaed; padding-bottom: 0.3em; }
    h3 { font-size: 1.2em; color: #3c4043; }
    h5, h6 { font-size: 1em; font-style: italic; }
    h6 { font-weight: normal; }
    ol, ul { padding-left: 1.7em; margin-top: 0.5em; }
    li { margin-bottom: 0.3em; }
    li > ol, li > ul { margin-top: 0; }
    blockquote {
      margin: 1em 0 1em 0;
      padding: 12px 16px;
      border-left: 4px solid #fbbc04;
      background-color: #fef7e0;
      color: #5f6368;
      border-radius: 0 4px 4px 0;
    }
    code {
      font-family: 'Roboto Mono', Menlo, Monaco, Consolas, monospace;
      font-size: 85%;
      margin: 0;
      background-color: #f1f3f4;
      padding: 2px 6px;
      border-radius: 4px;
      color: #d93025;
    }
    pre { margin: 1em 0; overflow: auto; }
    pre code { padding: 0; }
    hr { border: none; border-top: 2px solid #e8eaed; height: 0; margin: 2em 0; }
    table {
      margin: 1.5em 0;
      border-collapse: collapse;
      width: 100%;
      font-size: 0.95em;
      border: 1px solid #dadce0;
      border-radius: 8px;
    }
    table caption { margin-bottom: 0.75em; }
    tbody { margin-top: 0; }
    thead { background-color: #f1f3f4; }
    th {
      border: 1px solid #dadce0;
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
      color: #202124;
      font-size: 0.9em;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    td { border: 1px solid #dadce0; padding: 10px 14px; vertical-align: top; }
    tr:nth-child(even) { background-color: #f8f9fa; }
    tr:hover { background-color: #e8f0fe; }
    header { margin-bottom: 4em; text-align: center; }
    """

    try:
        # Step 1: Markdown → styled HTML
        result = subprocess.run(
            ["pandoc", str(report_path), "-o", str(html_intermediate),
             "--from", "markdown", "--to", "html5", "--standalone"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"⚠️  pandoc markdown→html failed: {result.stderr.strip()}")
            return None

        # Step 2: Inject CSS and inline it with premailer (if available)
        html_text = html_intermediate.read_text(encoding="utf-8")
        # Inject our CSS into the <style> block
        html_text = html_text.replace("</style>", css_block + "\n</style>", 1)

        try:
            from premailer import transform
            html_text = transform(html_text, remove_classes=True, strip_important=True, keep_style_tags=False)
        except ImportError:
            # premailer not installed — still export, but tables may not be perfectly styled in Google Docs
            print("⚠️  premailer not installed — exporting without CSS inlining. Tables may lose styling in Google Docs.")
            print("   Install with: pip3 install premailer")

        html_inlined.write_text(html_text, encoding="utf-8")

        # Step 3: Inlined HTML → docx
        result = subprocess.run(
            ["pandoc", str(html_inlined), "-o", str(docx_path),
             "--from", "html", "--to", "docx"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"⚠️  pandoc html→docx failed: {result.stderr.strip()}")
            return None

        return docx_path

    except Exception as exc:
        print(f"⚠️  Export failed: {exc}")
        return None

    finally:
        # Clean up intermediate files
        for f in (html_intermediate, html_inlined):
            if f.exists():
                f.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold Quality Risk Analysis outputs (and optionally run the quality gate).")
    parser.add_argument("--feature-slug", required=True, help="Short slug, e.g. 'sms-scheduling' (used in folder name).")
    parser.add_argument("--feature-name", default=None, help="Display name, e.g. 'SMS Scheduling Feature' (defaults to slug).")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (defaults to today).")
    parser.add_argument("--out-root", default="test-jams", help="Root output directory (default: test-jams).")

    parser.add_argument("--repo", required=True, help="Repository org/repo, e.g. org/project")
    parser.add_argument("--prd-url", required=True, help="PRD URL")
    parser.add_argument("--prd-title", default=None, help="Optional PRD title for the template header")
    parser.add_argument("--jira", default=None, help="Optional Jira URL or key (e.g. TESTING-1518)")
    parser.add_argument("--figma-url", default=None, help="Optional Figma URL")

    parser.add_argument(
        "--template",
        default="qualityforge/templates/RISK-REPORT-TEMPLATE.md",
        help="Path to canonical risk report template",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files if present")
    parser.add_argument("--check", action="store_true", help="Run the quality gate after scaffolding (will likely FAIL until filled)")
    parser.add_argument("--export", action="store_true", help="Export a Google Docs-compatible .docx file (requires pandoc)")

    args = parser.parse_args()

    date = args.date or _dt.date.today().isoformat()
    feature_slug = _slugify(args.feature_slug)
    feature_name = args.feature_name or args.feature_slug

    out_root = Path(args.out_root).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    session_dir = scaffold(
        out_root=out_root,
        date=date,
        feature_slug=feature_slug,
        feature_name=feature_name,
        repo=args.repo,
        prd_url=args.prd_url,
        prd_title=args.prd_title,
        jira=args.jira,
        figma_url=args.figma_url,
        template_path=template_path,
        overwrite=bool(args.overwrite),
    )

    report_path = session_dir / "risk_analysis_report.md"
    print("✅ Quality Risk Analysis scaffold created")
    print(f"📁 Folder: {session_dir}")
    print(f"📝 Report: {report_path}")
    print(f"🧾 Summary: {session_dir / 'risk_summary.md'}")

    if args.check:
        # Load the checker by file path so this works even if `qualityforge/` is not a Python package.
        checker_path = (Path(__file__).resolve().parent / "risk_report_quality.py").resolve()
        spec = importlib.util.spec_from_file_location("qualityforge_risk_report_quality", str(checker_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load checker module from {checker_path}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["qualityforge_risk_report_quality"] = mod
        spec.loader.exec_module(mod)  # type: ignore[call-arg]
        check_report = getattr(mod, "check_report")

        result = check_report(report_path)
        out_path = report_path.parent / "risk_quality_report.json"
        out_path.write_text(__import__("json").dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "✅ PASS" if result.get("passed") else "❌ FAIL"
        print(status)
        print(f"📝 Output: {out_path}")

    if args.export:
        docx = export_docx(report_path)
        if docx:
            print(f"📄 Google Docs export: {docx}")
        else:
            print("⚠️  Google Docs export skipped (see warnings above)")


if __name__ == "__main__":
    main()

