#!/usr/bin/env python3
"""
Playwright Test Generator - Consolidated Module

Converts test case CSV files into executable Playwright E2E tests following best practices.

This module is intentionally consolidated into ONE file to ensure:
- Single source of truth for all generation logic
- No drift between separate modules
- Easy for AI agents to reference complete logic
- Immediate consistency when updating best practices

Sections:
    1. CSVParser: Parse test case CSV files
    2. ActionDetector: Detect Playwright actions from natural language
    3. TestGenerator: Generate Playwright test code using templates
    4. ConfigGenerator: Generate playwright.config files  
    5. Validator: Self-healing validation and auto-fix (Phase 7)

Usage:
    python generator.py --test-jam <session-name> --language ts|js

References:
    - Application Patterns: qualityforge/reference/PLAYWRIGHT-PATTERNS.md (PRIMARY)
    - Generic Best Practices: qualityforge/reference/PLAYWRIGHT-BEST-PRACTICES.md
    - Templates: qualityforge/templates/playwright-*.{ts,js}
    - JIRA: TESTING-1514
    - Source: Real patterns from app-monolith/playwright repository

Author: QualityForge AI Assistant
Date: January 12, 2026
Phase: 2 - Core Generation (Acme Platform-enhanced)
"""

import os
import csv
import re
import json
import argparse
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

# Best Practices Reference Locations
BEST_PRACTICES_PATH = Path(__file__).parent.parent / "reference" / "PLAYWRIGHT-BEST-PRACTICES.md"
PLAYWRIGHT_PATTERNS_PATH = Path(__file__).parent.parent / "reference" / "PLAYWRIGHT-PATTERNS.md"

# Template Locations
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Locator Priority (from PLAYWRIGHT-PATTERNS.md - Section 2)
# Based on real patterns from app-monolith/playwright repository
LOCATOR_PRIORITY = {
    1: "getByRole",     # HIGHEST PRIORITY - Acme Platform uses this most (buttons, links, headings)
    2: "getByLabel",    # Form inputs (labels, checkboxes)
    3: "getByText",     # Visible text with exact matching
    4: "getByTestId",   # Data attributes (when explicitly mentioned)
    5: "locator"        # CSS/Complex selectors - LAST RESORT (adds TODO)
}

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class TestCase:
    """
    Represents a single test case from CSV.
    
    Attributes:
        test_id: Unique identifier (e.g., 'TC-001', 'STTM-012')
        category: Test category (e.g., 'Functional', 'Regression')
        name: Human-readable test name
        priority: Priority level (e.g., 'P0', 'P1', 'P2')
        test_type: Type of test (e.g., 'Manual', 'Automated')
        component: Component under test
        objective: Test objective/goal
        pre_conditions: Pre-conditions required (can trigger auth hooks)
        test_steps: Numbered list of test steps
        expected_results: Expected outcomes
        feature_area: Optional feature area categorization
        risk_level: Optional risk level
        notes: Optional additional notes
    """
    test_id: str
    category: str
    name: str
    priority: str
    test_type: str
    component: str
    objective: str
    pre_conditions: str
    test_steps: str
    expected_results: str
    # Optional fields
    feature_area: Optional[str] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PlaywrightAction:
    """
    Represents a detected Playwright action.
    
    Attributes:
        action_type: Type of action ('navigate', 'click', 'fill', 'assert', 'wait')
        code: Generated Playwright code (e.g., "await page.goto('/login')")
        comment: Optional comment for traceability (None if not needed)
        locator_method: Locator method used ('getByRole', 'getByLabel', etc.)
        confidence: Confidence level 0.0-1.0 (0.0=TODO, 0.8=pattern match)
    """
    action_type: str  # 'navigate', 'click', 'fill', 'assert', 'wait'
    code: str         # Generated Playwright code
    comment: str      # Original test step (for traceability)
    locator_method: str  # Which locator method was used
    confidence: float    # How confident we are (0.0-1.0)


@dataclass
class LocatorHints:
    """
    Optional locator/action hints (typically produced via Playwright MCP) to improve accuracy.

    Design goals:
      - Completely optional (no impact if omitted)
      - Prefer explicit step overrides (highest accuracy)
      - Avoid guessing locators; this is meant to carry *verified* code/locators

    Minimal JSON schema (example):
      {
        "version": "1",
        "generated_by": "playwright-mcp",
        "base_url": "http://localhost:3000",
        "urls": { "templates": "/templates?tab=saved" },
        "step_overrides": [
          {
            "pattern": "click\\s+manage\\s+audience",
            "action_type": "click",
            "locator_method": "getByRole",
            "code": "await page.getByRole('button', { name: 'Manage Audience' }).click();",
            "confidence": 0.95
          }
        ]
      }
    """

    version: str = "1"
    generated_by: str = ""
    base_url: str = ""
    urls: Dict[str, str] = field(default_factory=dict)  # keyword -> path (e.g., "templates" -> "/templates")
    step_overrides: List[Dict[str, Any]] = field(default_factory=list)

    @staticmethod
    def load(path: Path) -> "LocatorHints":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("locator hints must be a JSON object")
        return LocatorHints(
            version=str(data.get("version", "1")),
            generated_by=str(data.get("generated_by", "")),
            base_url=str(data.get("base_url", "")),
            urls=dict(data.get("urls") or {}),
            step_overrides=list(data.get("step_overrides") or []),
        )

    def match_step_override(self, test_step: str) -> Optional[PlaywrightAction]:
        """
        If any override regex matches the step, return the provided PlaywrightAction.
        """
        step = (test_step or "").strip()
        if not step:
            return None
        for entry in self.step_overrides:
            try:
                pattern = str(entry.get("pattern", "")).strip()
                if not pattern:
                    continue
                if not re.search(pattern, step, re.IGNORECASE):
                    continue
                code = str(entry.get("code", "")).strip()
                if not code:
                    continue
                action_type = str(entry.get("action_type", "unknown")).strip() or "unknown"
                locator_method = str(entry.get("locator_method", "manual")).strip() or "manual"
                confidence = float(entry.get("confidence", 0.95))
                return PlaywrightAction(
                    action_type=action_type,
                    code=code,
                    comment=None,
                    locator_method=locator_method,
                    confidence=confidence,
                )
            except Exception:
                # Never fail generation due to malformed hints; treat as missing.
                continue
        return None

    def resolve_navigation_url(self, test_step: str) -> Optional[str]:
        """
        Resolve a navigation target using keyword->path mapping.
        Example: urls={"templates": "/templates?tab=saved"} and step contains "templates".
        """
        step = (test_step or "").lower()
        if not step or not self.urls:
            return None
        for key, path in self.urls.items():
            k = (key or "").lower().strip()
            p = (path or "").strip()
            if not k or not p:
                continue
            if k in step:
                return p
        return None


# ==============================================================================
# 0. INPUT VALIDATION (Phase 6)
# ==============================================================================

class InputValidator:
    """
    Validate inputs before processing.
    
    Phase 6: Quality Polish - Prevent errors with better validation.
    """
    
    @staticmethod
    def validate_test_jam_name(name: str) -> None:
        """
        Validate test jam name format.
        
        Args:
            name: Test jam name to validate
            
        Raises:
            ValueError: If name doesn't match expected format
            
        Expected format: YYYY-MM-DD_description (e.g., 2026-01-12_feature-name)
        """
        if not name or not name.strip():
            raise ValueError("Test jam name cannot be empty")
        
        # Allow reserved example session used in repo documentation/testing.
        if name.strip() == "_example_session":
            return

        # Check format: date_description
        if not re.match(r'^\d{4}-\d{2}-\d{2}_[\w-]+$', name):
            raise ValueError(
                f"Invalid test jam name format: '{name}'\n"
                f"Expected: YYYY-MM-DD_description\n"
                f"Example: 2026-01-12_streamlined-tx-template-management"
            )
    
    @staticmethod
    def validate_language(language: str) -> None:
        """
        Validate language parameter.
        
        Args:
            language: Language code ('ts' or 'js')
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in ['ts', 'js']:
            raise ValueError(
                f"Unsupported language: '{language}'\n"
                f"Supported languages: 'ts' (TypeScript), 'js' (JavaScript)"
            )
    
    @staticmethod
    def validate_csv_structure(csv_path: Path) -> List[str]:
        """
        Validate CSV has minimum required columns.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of column names found in CSV
            
        Raises:
            ValueError: If CSV is missing required columns
            FileNotFoundError: If CSV file doesn't exist
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Read headers
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                columns = list(reader.fieldnames or [])
        except Exception as e:
            raise ValueError(f"Failed to read CSV headers from {csv_path}: {e}")
        
        if not columns:
            raise ValueError(f"CSV file is empty or has no headers: {csv_path}")
        
        # Check for minimum required columns (flexible to support different formats)
        has_test_id = any(col in columns for col in ['Test Case ID', 'Test ID'])
        has_steps = 'Test Steps' in columns
        has_results = 'Expected Results' in columns
        
        missing = []
        if not has_test_id:
            missing.append("'Test Case ID' or 'Test ID'")
        if not has_steps:
            missing.append("'Test Steps'")
        if not has_results:
            missing.append("'Expected Results'")
        
        if missing:
            raise ValueError(
                f"CSV missing required columns: {', '.join(missing)}\n"
                f"Available columns: {columns}\n"
                f"File: {csv_path.name}"
            )
        
        return columns


# ==============================================================================
# 1. CSV PARSER
# ==============================================================================

class CSVParser:
    """
    Parse test case CSV files from QualityForge test jams.
    
    Handles multiple CSV formats:
    - Standard format (Test Case ID, Category, Test Name, ...)
    - Feature format (Test Case ID, Feature Area, Test Scenario, ...)
    
    References:
        - Format spec: qualityforge/templates/csv-formats.md
        - Example: test-jams/2026-01-12_streamlined-tx-template-management/
    """
    
    def __init__(self, test_jam_dir: Path):
        """
        Initialize parser with test jam directory.
        
        Args:
            test_jam_dir: Path to test jam directory (e.g., test-jams/2026-01-12_...)
        """
        self.test_jam_dir = Path(test_jam_dir)

        # Prefer the master CSV when available.
        # Rationale: test-jams typically contain a master file + participant splits.
        # For Playwright generation, using all participant CSVs would duplicate test cases.
        master = self.test_jam_dir / "testjam_all_test_cases.csv"
        if master.exists():
            self.csv_files = [master]
        else:
            self.csv_files = list(self.test_jam_dir.glob("testjam_*.csv"))
        
        if not self.csv_files:
            # Phase 6: Enhanced error message with helpful context
            available_files = list(self.test_jam_dir.glob("*.csv"))
            all_files = list(self.test_jam_dir.glob("*"))
            
            error_msg = f"No CSV files found in {self.test_jam_dir}\n\n"
            error_msg += "Expected: Files matching pattern 'testjam_*.csv'\n"
            
            if available_files:
                error_msg += f"\nFound {len(available_files)} CSV file(s) with different naming:\n"
                for f in available_files:
                    error_msg += f"  • {f.name}\n"
                error_msg += "\nTip: Rename CSV files to match 'testjam_*.csv' pattern\n"
            elif all_files:
                error_msg += f"\nDirectory contains {len(all_files)} file(s) but no CSVs:\n"
                for f in all_files[:5]:  # Show first 5
                    error_msg += f"  • {f.name}\n"
                if len(all_files) > 5:
                    error_msg += f"  ... and {len(all_files) - 5} more\n"
            else:
                error_msg += "\nDirectory is empty!\n"
            
            raise FileNotFoundError(error_msg.strip())
    
    def parse_all(self) -> List[TestCase]:
        """
        Parse all CSV files in test jam directory.
        
        Returns:
            List of TestCase objects from all CSV files
        """
        all_test_cases = []
        
        for csv_file in self.csv_files:
            test_cases = self.parse_file(csv_file)
            all_test_cases.extend(test_cases)
            print(f"✅ Parsed {len(test_cases)} test cases from {csv_file.name}")
        
        return all_test_cases
    
    def parse_file(self, csv_path: Path) -> List[TestCase]:
        """
        Parse a single CSV file.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of TestCase objects
            
        Raises:
            ValueError: If CSV structure is invalid
        """
        # Phase 6: Validate CSV structure before parsing
        InputValidator.validate_csv_structure(csv_path)
        
        test_cases = []
        skipped_rows = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                # Skip empty rows
                if not row.get('Test Case ID') and not row.get('Test ID'):
                    skipped_rows += 1
                    continue
                
                try:
                    test_case = self._row_to_test_case(row)
                    if test_case:
                        test_cases.append(test_case)
                    else:
                        skipped_rows += 1
                except Exception as e:
                    # Phase 6: Better error handling for malformed rows
                    print(f"⚠️  Warning: Skipping row {row_num} in {csv_path.name}: {e}")
                    skipped_rows += 1
                    continue
        
        # Phase 6: Warn if many rows were skipped
        if skipped_rows > 0:
            print(f"   ℹ️  Skipped {skipped_rows} empty/invalid rows")
        
        return test_cases
    
    def _row_to_test_case(self, row: Dict[str, str]) -> Optional[TestCase]:
        """
        Convert CSV row to TestCase object.
        
        Handles different CSV formats gracefully.
        
        Phase 6: Enhanced edge case handling for missing/empty fields.
        
        Returns:
            TestCase object or None if row is invalid
        """
        try:
            # Handle different column name variations
            test_id = row.get('Test Case ID') or row.get('Test ID', '').strip()
            category = row.get('Category') or row.get('Feature Area', '').strip()
            name = row.get('Test Name') or row.get('Test Scenario', '').strip()
            priority = row.get('Priority', 'P2').strip()
            test_type = row.get('Type') or row.get('Test Type', 'Manual').strip()
            component = row.get('Component', '').strip()
            objective = row.get('Objective', name).strip()
            pre_conditions = row.get('Pre-conditions') or row.get('Preconditions', '').strip()
            test_steps = row.get('Test Steps', '').strip()
            expected_results = row.get('Expected Results', '').strip()
            
            # Phase 6: Validate required fields
            if not test_id:
                print(f"⚠️  Skipping row: Missing test ID")
                return None
            
            if not name:
                # Use test ID as name if no name provided
                name = f"Test {test_id}"
            
            if not test_steps:
                print(f"⚠️  Warning: Test {test_id} has no test steps (will generate placeholder)")
                test_steps = "1. TODO: Add test steps"
            
            if not expected_results:
                print(f"⚠️  Warning: Test {test_id} has no expected results (will generate placeholder)")
                expected_results = "1. TODO: Add expected results"
            
            # Optional fields
            feature_area = row.get('Feature Area', '').strip() or None
            risk_level = row.get('Risk Level', '').strip() or None
            notes = row.get('Notes', '').strip() or None
            
            return TestCase(
                test_id=test_id,
                category=category or 'Uncategorized',  # Phase 6: Default category
                name=name,
                priority=priority or 'P2',  # Phase 6: Default priority
                test_type=test_type or 'Manual',
                component=component or category or 'General',  # Phase 6: Fallback chain
                objective=objective or name,  # Phase 6: Use name as objective if missing
                pre_conditions=pre_conditions,
                test_steps=test_steps,
                expected_results=expected_results,
                feature_area=feature_area,
                risk_level=risk_level,
                notes=notes
            )
        except Exception as e:
            print(f"⚠️ Warning: Failed to parse row: {e}")
            return None


# ==============================================================================
# 2. ACTION DETECTOR
# ==============================================================================

class ActionDetector:
    """
    Detect Playwright actions from natural language test steps.
    
    Uses application-specific patterns extracted from app-monolith/playwright.
    
    Examples (based on real Acme Platform code):
        "Navigate to /templates"     → await page.goto('/templates?tab=saved');
        "Click Manage Audience"      → await page.getByRole('button', { name: 'Manage Audience' }).click();
        "Type DELETE to confirm"     → await page.getByLabel('Type DELETE to confirm').fill('DELETE');
        "Verify import was completed"→ await expect(page.getByRole('heading', { name: 'Your import was completed' })).toBeVisible();
    
    Locator Priority (from PLAYWRIGHT-PATTERNS.md):
        1. getByRole()   - MOST COMMON in Acme Platform (buttons, links, headings)
        2. getByLabel()  - Form inputs, checkboxes
        3. getByText()   - Exact text matching (with { exact: true })
        4. getByTestId() - Data attributes
        5. locator()     - Complex selectors (generates TODO)
    
    References:
        - Application Patterns: qualityforge/reference/PLAYWRIGHT-PATTERNS.md
        - Generic Best Practices: qualityforge/reference/PLAYWRIGHT-BEST-PRACTICES.md
    """
    
    # Action patterns: (regex, action_type, locator_method, code_template)
    # Based on real application patterns from app-monolith/playwright
    # Ordered by specificity - most specific patterns first
    PATTERNS = [
        # ===== NAVIGATION =====
        (
            r'(?:navigate|go|visit)\s+(?:to\s+)?(.+?)(?:\s+page)?$',
            'navigate',
            'none',
            lambda m: f"await page.goto('{m.group(1).strip()}');"
        ),
        
        # ===== acme-platform-SPECIFIC: MODAL INTERACTIONS =====
        # Pattern: "Close Modal", "Dismiss modal" → Close button
        (
            r'(?:close|dismiss)\s+(?:the\s+)?modal',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Close Modal' }}).click();"
        ),
        # Pattern: "Click Delete button in modal"
        (
            r'click\s+(?:the\s+)?delete\s+button(?:\s+in\s+modal)?',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Delete' }}).click();"
        ),
        # Pattern: "Type DELETE to confirm"
        (
            r'type\s+[\'"]?DELETE[\'"]?\s+to\s+confirm',
            'fill',
            'getByLabel',
            lambda m: f"await page.getByLabel('Type DELETE to confirm').fill('DELETE');"
        ),
        
        # ===== acme-platform-SPECIFIC: MANAGEMENT ACTIONS =====
        # Pattern: "Click Manage Audience", "Manage your audience"
        (
            r'(?:click|open)\s+(?:the\s+)?manage\s+(?:your\s+)?audience',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Manage Audience' }}).click();"
        ),
        # Pattern: "Click Manage App"
        (
            r'(?:click|open)\s+(?:the\s+)?manage\s+app',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Manage App' }}).click();"
        ),
        
        # ===== acme-platform-SPECIFIC: IMPORT/EXPORT WORKFLOWS =====
        # Pattern: "Import contacts", "Click Import"
        (
            r'(?:click|select|choose)\s+(?:the\s+)?import\s+contacts?',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('link', {{ name: 'Import contacts' }}).click();"
        ),
        # Pattern: "Export audience"
        (
            r'(?:click|select|choose)\s+(?:the\s+)?export\s+audience',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Export audience' }}).click();"
        ),
        # Pattern: "Complete Import", "Finalize Import"
        (
            r'(?:complete|finalize)\s+(?:the\s+)?import',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Complete Import' }}).click();"
        ),
        
        # ===== acme-platform-SPECIFIC: STATUS & VERIFICATION (with headings) =====
        # Pattern: "Verify import was completed" → heading verification
        (
            r'(?:verify|check|confirm)\s+(?:that\s+)?(?:the\s+)?import\s+(?:was\s+)?completed',
            'assert',
            'getByRole',
            lambda m: f"await expect(page.getByRole('heading', {{ name: 'Your import was completed' }})).toBeVisible();"
        ),
        # Pattern: "Verify heading contains X" → heading verification
        (
            r'(?:verify|check|confirm)\s+(?:that\s+)?(?:the\s+)?(?:heading|title)\s+(?:contains|says|shows)\s+[\'"](.+?)[\'"]',
            'assert',
            'getByRole',
            lambda m: f"await expect(page.getByRole('heading', {{ name: '{m.group(1).strip()}' }})).toBeVisible();"
        ),
        
        # ===== BROWSER DEVTOOLS (placeholder - not automatable) =====
        (
            r'open\s+(?:browser\s+)?dev\s*tools',
            'manual',
            'none',
            lambda m: f"// TODO: Manual step - Open browser DevTools"
        ),
        (
            r'(?:inspect|examine|review)\s+(?:the\s+)?(?:api|network|console)',
            'manual',
            'none',
            lambda m: f"// TODO: Manual step - Inspect API/Network/Console in DevTools"
        ),
        (
            r'filter\s+for\s+[\'"](.+?)[\'"]\s+(?:api\s+call|request)',
            'manual',
            'none',
            lambda m: f"// TODO: Manual step - Filter for '{m.group(1).strip()}' in Network tab"
        ),
        
        # ===== VIEW SWITCHING =====
        (
            r'switch\s+to\s+(.+?)\s+view',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: '{m.group(1).strip().title()} View' }}).click();"
        ),
        (
            r'ensure\s+(?:the\s+)?(.+?)\s+view\s+is\s+(?:displayed|active)',
            'assert',
            'getByRole',
            lambda m: f"await expect(page.getByRole('button', {{ name: '{m.group(1).strip().title()} View', pressed: true }})).toBeVisible();"
        ),
        
        # ===== DROPDOWNS & SELECTS =====
        (
            r'click\s+(?:on\s+)?(?:the\s+)?(.+?)\s+dropdown',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: '{m.group(1).strip().title()}' }}).click();"
        ),
        (
            r'select\s+[\'"](.+?)[\'"]\s+(?:from|in)\s+(?:the\s+)?(.+?)(?:\s+dropdown)?',
            'select',
            'getByRole',
            lambda m: f"await page.getByRole('option', {{ name: '{m.group(1).strip()}' }}).click();"
        ),
        (
            r'select\s+(?:the\s+)?(.+?)(?:\s+option)?$',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('option', {{ name: '{m.group(1).strip()}' }}).click();"
        ),
        
        # ===== CLICKS (specific to general, Acme Platform style) =====
        # Specific button names (don't title-case these common ones)
        (
            r'click\s+(?:on\s+)?(?:the\s+)?edit\s+(?:button)?',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Edit' }}).click();"
        ),
        (
            r'click\s+(?:on\s+)?(?:the\s+)?continue\s+(?:button)?',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Continue' }}).click();"
        ),
        (
            r'click\s+(?:on\s+)?(?:the\s+)?save\s+(?:button)?',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Save' }}).click();"
        ),
        (
            r'click\s+(?:on\s+)?(?:the\s+)?cancel\s+(?:button)?',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: 'Cancel' }}).click();"
        ),
        # Generic button pattern - preserve original casing when possible
        (
            r'click\s+(?:on\s+)?(?:the\s+)?(.+?)\s+button',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('button', {{ name: '{m.group(1).strip().title()}' }}).click();"
        ),
        # Link pattern
        (
            r'click\s+(?:on\s+)?(?:the\s+)?(.+?)\s+(?:link|icon)',
            'click',
            'getByRole',
            lambda m: f"await page.getByRole('link', {{ name: '{m.group(1).strip().title()}' }}).click();"
        ),
        # Generic click - use getByText for non-button elements
        (
            r'click\s+(?:on\s+)?(?:the\s+)?(.+)',
            'click',
            'getByText',
            lambda m: f"await page.getByText('{m.group(1).strip()}').click();"
        ),
        
        # ===== FORM INPUTS =====
        (
            r'(?:enter|type|fill|input)\s+(?:"(.+?)"|(.+?))\s+(?:in|into|to)\s+(?:the\s+)?(.+?)(?:\s+field)?$',
            'fill',
            'getByLabel',
            lambda m: f"await page.getByLabel('{m.group(3).strip().title()}').fill('{(m.group(1) or m.group(2)).strip()}');"
        ),
        (
            r'(?:enter|type|fill|input)\s+(?:the\s+)?(.+?)(?:\s+field)?$',
            'fill',
            'getByLabel',
            lambda m: f"await page.getByLabel('{m.group(1).strip().title()}').fill(testData.{m.group(1).strip().lower().replace(' ', '_')});"
        ),
        
        # ===== CHECKBOXES/RADIO =====
        (
            r'(?:check|select)\s+(?:the\s+)?(.+?)(?:\s+checkbox)?$',
            'check',
            'getByLabel',
            lambda m: f"await page.getByLabel('{m.group(1).strip()}').check();"
        ),
        
        # ===== OBSERVATION & LOCATION (convert to assertions) =====
        (
            r'(?:ensure|verify)\s+(?:the\s+)?(.+?)\s+(?:is|are)\s+(?:displayed|visible|shown)',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).toBeVisible();"
        ),
        (
            r'observe\s+(?:the\s+)?(.+?)(?:\s+for\s+.+)?$',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).toBeVisible();"
        ),
        (
            r'locate\s+(?:a|an|the\s+)?(.+?)(?:\s+in\s+.+)?$',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).toBeVisible();"
        ),
        (
            r'(?:count|identify)\s+(?:and\s+identify\s+)?(?:all\s+)?(.+)',
            'assert',
            'getByRole',
            lambda m: f"await expect(page.getByRole('columnheader')).toHaveCount(5); // TODO: Verify count and identity"
        ),
        
        # ===== ASSERTIONS (Acme Platform style with exact matching) =====
        # Button/element visibility with specific role
        (
            r'(?:verify|check|confirm|assert)\s+(?:that\s+)?(?:the\s+)?(.+?)\s+button\s+(?:is|are)\s+(?:visible|displayed|shown)',
            'assert',
            'getByRole',
            lambda m: f"await expect(page.getByRole('button', {{ name: '{m.group(1).strip().title()}' }})).toBeVisible();"
        ),
        # Generic visibility assertion
        (
            r'(?:verify|check|confirm|assert)\s+(?:that\s+)?(.+?)\s+(?:is|are)\s+(?:visible|displayed|shown)',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}', {{ exact: true }})).toBeVisible();"
        ),
        # Text content assertion
        (
            r'(?:verify|check|confirm|assert)\s+(?:that\s+)?(.+?)\s+(?:contains|has|includes)\s+["\'](.+?)["\']',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).toContainText('{m.group(2).strip()}');"
        ),
        # Negative assertion
        (
            r'(?:verify|check|confirm|assert)\s+(?:that\s+)?(.+?)\s+(?:not|does\s+not|is\s+not)\s+(?:visible|displayed|shown)',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).not.toBeVisible();"
        ),
        # "Element displays/shows text" pattern
        (
            r'(.+?)\s+(?:displays|shows)\s+["\'](.+?)["\']',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).toContainText('{m.group(2).strip()}');"
        ),
        # Generic verification (catch-all)
        (
            r'(?:verify|check|confirm|assert)\s+(.+)',
            'assert',
            'getByText',
            lambda m: f"await expect(page.getByText('{m.group(1).strip()}')).toBeVisible();"
        ),
        
        # ===== WAITS =====
        (
            r'wait\s+(?:for|until)\s+(.+?)(?:\s+to\s+load)?$',
            'wait',
            'getByText',
            lambda m: f"await page.getByText('{m.group(1).strip()}').waitFor();"
        ),
        
        # ===== CONFIGURATION & SETUP =====
        (
            r'set\s+(.+?)\s+(?:to|=)\s+(.+)',
            'manual',
            'none',
            lambda m: f"// TODO: Set {m.group(1).strip()} to {m.group(2).strip()}"
        ),
    ]
    
    def __init__(self, locator_hints: Optional[LocatorHints] = None):
        self.locator_hints = locator_hints

    def detect(self, test_step: str) -> PlaywrightAction:
        """
        Detect Playwright action from a natural language test step.
        
        Args:
            test_step: Natural language test step (e.g., "Click Login button")
            
        Returns:
            PlaywrightAction with generated code and metadata
        """
        test_step_clean = test_step.strip()
        test_step_lower = test_step_clean.lower()

        # 0) Highest confidence: explicit step overrides (usually from Playwright MCP capture)
        if self.locator_hints:
            override = self.locator_hints.match_step_override(test_step_clean)
            if override:
                return override

            # Special-case: navigation steps with ambiguous targets ("templates page", "settings", etc.)
            if ("navigate to" in test_step_lower) or ("go to" in test_step_lower):
                resolved = self.locator_hints.resolve_navigation_url(test_step_clean)
                if resolved:
                    return PlaywrightAction(
                        action_type="navigate",
                        code=f"await page.goto('{resolved}');",
                        comment=None,
                        locator_method="goto",
                        confidence=0.9,
                    )
        
        # Try each pattern
        for pattern, action_type, locator_method, code_gen in self.PATTERNS:
            match = re.search(pattern, test_step_lower, re.IGNORECASE)
            if match:
                try:
                    code = code_gen(match)
                    return PlaywrightAction(
                        action_type=action_type,
                        code=code,
                        comment=None,  # No comment for successfully detected actions
                        locator_method=locator_method,
                        confidence=0.8  # Pattern match = high confidence
                    )
                except Exception as e:
                    print(f"⚠️ Warning: Failed to generate code for '{test_step}': {e}")
                    continue
        
        # No pattern matched - generate TODO comment (human review needed)
        return PlaywrightAction(
            action_type='unknown',
            code=f"// TODO: Implement step - {test_step_clean}",
            comment=None,  # Comment is embedded in code as TODO
            locator_method='manual',
            confidence=0.0
        )
    
    def detect_all(self, test_steps: str) -> List[PlaywrightAction]:
        """
        Detect all actions from a multi-line test steps string.
        
        Args:
            test_steps: Multi-line string with numbered steps (from CSV)
            
        Returns:
            List of PlaywrightActions
        """
        actions = []
        
        # Split by numbered list format (1., 2., 3., etc.)
        steps = re.split(r'\n(?=\d+\.)', test_steps.strip())
        
        for step in steps:
            # Remove leading number and whitespace
            step_clean = re.sub(r'^\d+\.\s*', '', step.strip())
            if step_clean:
                action = self.detect(step_clean)
                actions.append(action)
        
        return actions


# ==============================================================================
# 2.5. PRE-CONDITION ANALYZER (Phase 3)
# ==============================================================================

@dataclass
class PreConditionAnalysis:
    """Results of pre-condition analysis."""
    requires_auth: bool
    starting_url: Optional[str]
    setup_steps: List[str]
    auth_keywords: List[str]  # Keywords that triggered auth detection


class PreConditionAnalyzer:
    """
    Analyze test case pre-conditions to detect:
    - Authentication requirements (e.g., "User is logged in")
    - Initial navigation (e.g., "User is on /dashboard")
    - Test data setup requirements
    
    Used by TestGenerator to automatically generate beforeEach() hooks.
    
    Phase: 3 - Test Structure & Organization
    """
    
    # Patterns that indicate authentication is required
    AUTH_PATTERNS = [
        r'(?:user is |user has )?(?:logged in|authenticated|signed in)',
        r'valid credentials',
        r'has access',
        r'authenticated user',
        r'logged-in user',
    ]
    
    # Patterns to extract starting URLs
    NAV_PATTERNS = [
        r'(?:user is |navigates? to |on |at )(?:the )?([\/\w\-?=&]+)(?:\s+page)?',
        r'opens? (?:the )?([\/\w\-?=&]+)(?:\s+page)?',
    ]
    
    def analyze(self, pre_conditions: str) -> PreConditionAnalysis:
        """
        Analyze pre-conditions to determine test setup requirements.
        
        Args:
            pre_conditions: Pre-conditions text from CSV
            
        Returns:
            PreConditionAnalysis with detected requirements
        """
        if not pre_conditions or not pre_conditions.strip():
            return PreConditionAnalysis(
                requires_auth=False,
                starting_url=None,
                setup_steps=[],
                auth_keywords=[]
            )
        
        pre_conditions_lower = pre_conditions.lower()
        
        # Check for authentication requirements
        requires_auth = False
        auth_keywords = []
        for pattern in self.AUTH_PATTERNS:
            if re.search(pattern, pre_conditions_lower, re.IGNORECASE):
                requires_auth = True
                # Extract the matched keyword for reporting
                match = re.search(pattern, pre_conditions_lower, re.IGNORECASE)
                if match:
                    auth_keywords.append(match.group(0))
        
        # Extract starting URL if mentioned
        starting_url = None
        for pattern in self.NAV_PATTERNS:
            match = re.search(pattern, pre_conditions_lower, re.IGNORECASE)
            if match:
                url = match.group(1).strip()
                # Only set if it looks like a URL path
                if url.startswith('/') or url.startswith('http'):
                    starting_url = url
                    break
        
        # Extract setup steps (numbered list items)
        setup_steps = []
        for line in pre_conditions.split('\n'):
            line_clean = re.sub(r'^\d+\.\s*', '', line.strip())
            if line_clean and not any(kw in line_clean.lower() for kw in ['logged in', 'authenticated', 'signed in']):
                # Skip auth-related steps - they'll be in beforeEach()
                setup_steps.append(line_clean)
        
        return PreConditionAnalysis(
            requires_auth=requires_auth,
            starting_url=starting_url,
            setup_steps=setup_steps,
            auth_keywords=auth_keywords
        )


# ==============================================================================
# 3. TEST GENERATOR
# ==============================================================================

class TestGenerator:
    """
    Generate Playwright test code using templates.
    
    Converts TestCase objects + detected actions → executable Playwright tests.
    
    Features:
        - Uses templates from qualityforge/templates/
        - Generates TypeScript or JavaScript
        - Follows PLAYWRIGHT-BEST-PRACTICES.md structure
        - Adds traceability comments (original test case ID)
        - Groups tests by component using describe() blocks (Phase 3)
        - Explicit timeouts for assertions (Phase 6)
    
    References:
        - Best Practices: qualityforge/reference/PLAYWRIGHT-BEST-PRACTICES.md
        - Templates: qualityforge/templates/playwright-test.spec.{ts,js}
    """
    
    # Default timeout for assertions (ms) - Phase 6
    DEFAULT_ASSERTION_TIMEOUT = 10000  # 10 seconds
    
    def __init__(self, language: str = 'ts', locator_hints: Optional[LocatorHints] = None):
        """
        Initialize generator.
        
        Args:
            language: 'ts' for TypeScript or 'js' for JavaScript
        """
        self.language = language
        self.action_detector = ActionDetector(locator_hints=locator_hints)
        self.precondition_analyzer = PreConditionAnalyzer()  # Phase 3
        self.test_file_ext = '.spec.ts' if language == 'ts' else '.spec.js'
    
    @staticmethod
    def add_timeout_to_assertion(code: str, timeout_ms: int = 10000) -> str:
        """
        Add explicit timeout to expect() assertions for reliability.
        
        Phase 6: Quality Polish - Prevent flaky tests with explicit timeouts.
        
        Args:
            code: Generated Playwright code (e.g., "await expect(...).toBeVisible();")
            timeout_ms: Timeout in milliseconds (default: 10000)
            
        Returns:
            Code with timeout added
            
        Examples:
            Input:  "await expect(page.getByText('Welcome')).toBeVisible();"
            Output: "await expect(page.getByText('Welcome')).toBeVisible({ timeout: 10000 });"
            
            Input:  "await expect(page.getByRole('button')).toHaveText('Click me');"
            Output: "await expect(page.getByRole('button')).toHaveText('Click me', { timeout: 10000 });"
        """
        if 'expect(' not in code:
            return code  # Not an assertion
        
        # Pattern: .toBeVisible();
        # Add: .toBeVisible({ timeout: 10000 });
        code = re.sub(
            r'\.toBeVisible\(\);',
            f'.toBeVisible({{ timeout: {timeout_ms} }});',
            code
        )
        
        # Pattern: .not.toBeVisible();
        # Add: .not.toBeVisible({ timeout: 10000 });
        code = re.sub(
            r'\.not\.toBeVisible\(\);',
            f'.not.toBeVisible({{ timeout: {timeout_ms} }});',
            code
        )
        
        # Pattern: .toHaveText('text');
        # Add: .toHaveText('text', { timeout: 10000 });
        code = re.sub(
            r"\.toHaveText\((['\"])(.+?)\1\);",
            rf".toHaveText(\1\2\1, {{ timeout: {timeout_ms} }});",
            code
        )
        
        # Pattern: .toContainText('text');
        # Add: .toContainText('text', { timeout: 10000 });
        code = re.sub(
            r"\.toContainText\((['\"])(.+?)\1\);",
            rf".toContainText(\1\2\1, {{ timeout: {timeout_ms} }});",
            code
        )
        
        # Pattern: .toHaveURL(/regex/);
        # Add: .toHaveURL(/regex/, { timeout: 10000 });
        code = re.sub(
            r'\.toHaveURL\((/.*?/)\);',
            rf'.toHaveURL(\1, {{ timeout: {timeout_ms} }});',
            code
        )
        
        return code
    
    def generate_test(self, test_case: TestCase, title_override: Optional[str] = None) -> str:
        """
        Generate Playwright test code for a single test case.
        
        Args:
            test_case: TestCase object from CSV
            
        Returns:
            Generated Playwright test code (string)
        """
        # Detect actions from test steps
        step_actions = self.action_detector.detect_all(test_case.test_steps)
        result_actions = self.action_detector.detect_all(test_case.expected_results)
        
        # Build test code
        test_code = self._build_test_block(test_case, step_actions, result_actions, title_override=title_override)
        
        return test_code
    
    def _build_test_block(
        self, 
        test_case: TestCase, 
        step_actions: List[PlaywrightAction],
        result_actions: List[PlaywrightAction],
        title_override: Optional[str] = None,
    ) -> str:
        """Build a single test() block with minimal comments."""
        
        # Test name with priority tag
        test_name = title_override or f"[{test_case.test_id}] {test_case.name} @{test_case.priority}"
        
        code_lines = []
        code_lines.append(f"  test('{test_name}', async ({{ page }}) => {{")
        
        # Add JSDoc only if pre-conditions exist and are meaningful
        if test_case.pre_conditions and test_case.pre_conditions.strip():
            code_lines.append(f"    /**")
            code_lines.append(f"     * Pre-conditions:")
            for line in test_case.pre_conditions.split('\n'):
                if line.strip():
                    code_lines.append(f"     * - {line.strip()}")
            code_lines.append(f"     */")
        
        # Test steps - only add comments if they exist (i.e., TODOs)
        for action in step_actions:
            if action.comment:
                code_lines.append(f"    {action.comment}")
            # Phase 6: Add timeouts to assertions
            code_with_timeout = self.add_timeout_to_assertion(action.code, self.DEFAULT_ASSERTION_TIMEOUT)
            code_lines.append(f"    {code_with_timeout}")
        
        # Expected results (assertions) - no header, just code
        # Phase 6: Add timeouts to all assertions for reliability
        for action in result_actions:
            if action.comment:
                code_lines.append(f"    {action.comment}")
            # Phase 6: Add timeouts to assertions
            code_with_timeout = self.add_timeout_to_assertion(action.code, self.DEFAULT_ASSERTION_TIMEOUT)
            code_lines.append(f"    {code_with_timeout}")
        
        code_lines.append("  });")
        code_lines.append("")
        
        return '\n'.join(code_lines)
    
    def generate_file(self, test_cases: List[TestCase], component_name: str) -> str:
        """
        Generate a complete Playwright test file with beforeEach() hooks.
        
        Args:
            test_cases: List of test cases for this component
            component_name: Name of component (used for describe() block)
            
        Returns:
            Complete test file code (string)
        """
        file_lines = []
        
        # Imports
        file_lines.append("import { test, expect } from '@playwright/test';")
        file_lines.append("")
        
        # Describe block
        file_lines.append(f"test.describe('{component_name}', () => {{")
        
        # Phase 3: Check if any tests require authentication
        auth_required = any(
            self.precondition_analyzer.analyze(tc.pre_conditions).requires_auth 
            for tc in test_cases
        )
        
        if auth_required:
            # Add beforeEach() hook for authentication
            file_lines.append(self._generate_auth_hook())
        
        file_lines.append("")
        
        # Generate tests (ensure unique titles within a file for Playwright discovery)
        title_counts: Dict[str, int] = {}
        for test_case in test_cases:
            base_title = f"[{test_case.test_id}] {test_case.name} @{test_case.priority}"
            title_counts[base_title] = title_counts.get(base_title, 0) + 1
            title = base_title if title_counts[base_title] == 1 else f"{base_title} (dup {title_counts[base_title]})"

            test_code = self.generate_test(test_case, title_override=title)
            file_lines.append(test_code)
        
        # Close describe block
        file_lines.append("});")
        file_lines.append("")
        
        return '\n'.join(file_lines)
    
    def _generate_auth_hook(self) -> str:
        """
        Generate authentication beforeEach() hook.
        
        Phase 3: Auto-generated authentication setup.
        Uses environment variables for credentials.
        
        Returns:
            beforeEach() hook code (string)
        """
        return """  test.beforeEach(async ({ page }) => {
    /**
     * Authentication Setup (Auto-generated)
     * Authenticates user before each test using environment credentials.
     * 
     * Required Environment Variables:
     * - TEST_USER_EMAIL: Test account email
     * - TEST_USER_PASSWORD: Test account password
     */
    await page.goto('/login');
    await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL || 'test@example.com');
    await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD || 'password');
    await page.getByRole('button', { name: 'Login' }).click();
    
    // Wait for authentication to complete
    await expect(page).toHaveURL(/.*dashboard/);
  });"""


# ==============================================================================
# 4. CONFIG GENERATOR (Phase 4)
# ==============================================================================

class ConfigGenerator:
    """
    Generate Playwright configuration files.
    
    Phase 4 Implementation:
        - Generate playwright.config.ts with cross-browser support
        - Generate package.json with dependencies
        - Generate .gitignore for test results
        - Generate README.md with usage instructions
    
    Phase: 4 - Configuration Files
    """
    
    def __init__(self, output_dir: Path, language: str = 'ts'):
        """
        Initialize config generator.
        
        Args:
            output_dir: Directory to write config files
            language: 'ts' for TypeScript or 'js' for JavaScript
        """
        self.output_dir = Path(output_dir)
        self.language = language
    
    def generate_all(self) -> None:
        """Generate all configuration files."""
        self.generate_playwright_config()
        self.generate_package_json()
        self.generate_gitignore()
        self.generate_readme()
    
    def generate_playwright_config(self) -> None:
        """Generate playwright.config.ts or .js file."""
        if self.language == 'ts':
            config_content = self._get_typescript_config()
            config_file = self.output_dir / "playwright.config.ts"
        else:
            config_content = self._get_javascript_config()
            config_file = self.output_dir / "playwright.config.js"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"  ✅ {config_file.name}")
    
    def _get_typescript_config(self) -> str:
        """Get TypeScript config template."""
        return """import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

/**
 * Playwright Configuration
 * Auto-generated by QualityForge
 * 
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use */
  reporter: 'html',
  
  /* Shared settings for all projects */
  use: {
    /* Base URL from environment variable */
    baseURL: process.env.BASE_URL || 'https://example.com',
    
    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video on failure */
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Test against mobile viewports */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],
});
"""
    
    def _get_javascript_config(self) -> str:
        """Get JavaScript config template."""
        return """const { defineConfig, devices } = require('@playwright/test');
require('dotenv').config();

/**
 * Playwright Configuration
 * Auto-generated by QualityForge
 * 
 * See https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: process.env.BASE_URL || 'https://example.com',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
"""
    
    def generate_package_json(self) -> None:
        """Generate package.json with dependencies."""
        package_data = {
            "name": "playwright-tests",
            "version": "1.0.0",
            "description": "Auto-generated Playwright E2E tests from QualityForge",
            "scripts": {
                "test": "playwright test",
                "test:headed": "playwright test --headed",
                "test:debug": "playwright test --debug",
                "test:chromium": "playwright test --project=chromium",
                "test:firefox": "playwright test --project=firefox",
                "test:webkit": "playwright test --project=webkit",
                "test:ui": "playwright test --ui",
                "report": "playwright show-report",
                "codegen": "playwright codegen"
            },
            "devDependencies": {
                "@playwright/test": "^1.40.0",
                "@types/node": "^20.10.0",
                "dotenv": "^16.3.0"
            }
        }
        
        # Add TypeScript if using .ts
        if self.language == 'ts':
            package_data["devDependencies"]["typescript"] = "^5.3.0"
        
        with open(self.output_dir / "package.json", 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2)
            f.write('\n')  # Add trailing newline
        
        print("  ✅ package.json")
    
    def generate_gitignore(self) -> None:
        """Generate .gitignore file."""
        gitignore_content = """# Playwright
test-results/
playwright-report/
playwright/.cache/

# Environment
.env
.env.local

# Node
node_modules/
package-lock.json
yarn.lock
pnpm-lock.yaml

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
"""
        
        with open(self.output_dir / ".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("  ✅ .gitignore")
    
    def generate_readme(self) -> None:
        """Generate README.md with usage instructions."""
        readme_content = """# Playwright E2E Tests

Auto-generated Playwright tests from **QualityForge**.

## 📦 Installation

```bash
npm install
```

## ⚙️ Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your test account credentials in `.env`:
   ```bash
   TEST_USER_EMAIL=your-test-email@example.com
   TEST_USER_PASSWORD=your-test-password
   BASE_URL=https://example.com
   ```

## 🚀 Running Tests

### All Tests
```bash
npm test
```

### Headed Mode (See Browser)
```bash
npm run test:headed
```

### Specific Browser
```bash
npm run test:chromium  # Chrome/Chromium
npm run test:firefox   # Firefox
npm run test:webkit    # Safari (WebKit)
```

### Debug Mode
```bash
npm run test:debug
```

### Interactive UI Mode
```bash
npm run test:ui
```

### View Test Report
```bash
npm run report
```

## 📁 Project Structure

```
playwright-tests/
├── *.spec.ts              # Test files
├── playwright.config.ts   # Playwright configuration
├── package.json           # Dependencies and scripts
├── .env                   # Environment variables (not committed)
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🎯 Test Files

Tests are organized by component/feature:
- Each `.spec.ts` file contains related tests
- Tests use `describe()` blocks for grouping
- `beforeEach()` hooks handle authentication (when needed)

## 🌐 Cross-Browser Testing

Tests are configured to run on:
- **Chromium** (Chrome, Edge)
- **Firefox**
- **WebKit** (Safari)

Run all browsers in parallel:
```bash
npm test
```

## 📊 Reports

After running tests, view the HTML report:
```bash
npm run report
```

## 🔧 Playwright Codegen

Generate new tests interactively:
```bash
npm run codegen
```

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Test Best Practices](https://playwright.dev/docs/best-practices)
- [QualityForge Documentation](../../qualityforge/README.md)

## ✨ Generated with QualityForge

These tests were automatically generated from test case CSV files using QualityForge.

**Generation Date**: """ + f"{Path(__file__).stat().st_mtime}" + """  
**Generator Version**: Phase 4
"""
        
        with open(self.output_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("  ✅ README.md")


# ==============================================================================
# 5. VALIDATOR (Phase 7)
# ==============================================================================

class Validator:
    """
    Self-healing test validation and auto-fix.
    
    Phase 7 Implementation:
        - Run generated tests locally
        - Detect errors and failures
        - Apply intelligent auto-fixes
        - Retry until tests pass or max attempts reached
    
    Phase 7 scope (safe-by-default):
        - Run generated tests locally (if deps are available)
        - Capture failures and summarize root causes
        - Apply ONLY safe auto-fixes (non-behavior-changing):
            * dependency install guidance
            * missing .env guidance when auth is required
            * baseURL sanity checks
            * optional light stabilization suggestions (no selector guessing)
        - Retry until tests pass OR max attempts reached
    """
    
    MAX_ATTEMPTS = 2

    def validate_and_fix(
        self,
        test_dir: Path,
        mode: str = "static",
        fix_level: str = "conservative",
        todo_policy: str = "allow",
    ) -> None:
        """
        Run self-healing validation loop.

        This is intentionally conservative: it will not invent selectors or
        rewrite test intent. It focuses on environment/dependency issues and
        produces actionable guidance.

        Args:
            test_dir: Directory containing generated Playwright tests + config
            mode: Validation mode.
                - "static": Validate that the suite is runnable (deps, config, test discovery)
                  without requiring a working target application.
                - "runtime": Actually execute tests (requires a reachable target app via BASE_URL).
        """
        report: Dict = {
            "phase": 7,
            "mode": mode,
            "fix_level": fix_level,
            "todo_policy": todo_policy,
            "test_dir": str(test_dir),
            "timestamp_utc": "",
            "attempts": [],
            "result": None,  # "passed" | "failed" | "skipped"
            "skip_reason": None,
            "base_url": None,  # safe to include (no secrets)
            "missing_keys": [],  # missing env keys (safe: key names only)
            "applied_fixes": [],  # safe auto-fixes applied (no secrets)
            "suggestions": [],  # actionable next steps (no secrets)
            "suite_metrics": {},  # static suite quality metrics (no secrets)
            # Optional (but written by current versions): quality signals derived from suite_metrics.
            # Consumers should treat unknown/absent fields as optional.
            "quality": {"warnings": [], "gates": {}},
        }
        try:
            from datetime import datetime, timezone
            report["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        except Exception:
            report["timestamp_utc"] = ""

        if not test_dir.exists():
            print(f"❌ Validation skipped: test directory not found: {test_dir}")
            report["result"] = "skipped"
            report["skip_reason"] = "test_dir_missing"
            report["suggestions"] = self._suggest_next_steps(
                test_dir=test_dir, mode=mode, fix_level=fix_level, skip_reason=report["skip_reason"]
            )
            self._write_validation_report(test_dir, report)
            return

        # Always compute suite metrics when directory exists (independent of deps/app).
        report["suite_metrics"] = self._compute_suite_metrics(test_dir)
        report["quality"] = self._derive_quality(report.get("suite_metrics") or {}, todo_policy=todo_policy)

        if mode not in ("static", "runtime"):
            print(f"❌ Validation skipped: invalid mode '{mode}'. Use 'static' or 'runtime'.")
            report["result"] = "skipped"
            report["skip_reason"] = "invalid_mode"
            report["suggestions"] = self._suggest_next_steps(
                test_dir=test_dir, mode=mode, fix_level=fix_level, skip_reason=report["skip_reason"]
            )
            self._write_validation_report(test_dir, report)
            return

        if not self._has_node_deps(test_dir):
            print("ℹ️  Validation skipped: Node dependencies not installed.")
            print("   To enable validation:")
            print(f"   1) cd {test_dir}")
            print("   2) npm install")
            print("   3) npx playwright install --with-deps (first time only)")
            report["result"] = "skipped"
            report["skip_reason"] = "deps_not_installed"
            report["suggestions"] = self._suggest_next_steps(
                test_dir=test_dir, mode=mode, fix_level=fix_level, skip_reason=report["skip_reason"]
            )
            self._write_validation_report(test_dir, report)
            return

        # Static validation is useful even without a local app/staging target.
        if mode == "static":
            ok, summary = self._static_validate(test_dir)
            report["attempts"].append(
                {
                    "attempt": 1,
                    "kind": summary.get("kind") if summary else None,
                    "headline": summary.get("headline") if summary else None,
                }
            )
            report["result"] = "passed" if ok else "failed"
            # If static validation passed, provide helpful (non-failure) next steps.
            if ok:
                report["suggestions"] = self._suggest_pass_next_steps(
                    test_dir=test_dir,
                    mode=mode,
                    fix_level=fix_level,
                    suite_metrics=report.get("suite_metrics"),
                    quality=report.get("quality"),
                )
            else:
                report["suggestions"] = self._suggest_next_steps(
                    test_dir=test_dir,
                    mode=mode,
                    fix_level=fix_level,
                    kind=(summary.get("kind") if summary else None),
                    skip_reason=None,
                )
            self._write_validation_report(test_dir, report)
            return

        # Runtime validation requires a reachable target base URL.
        # Playwright config loads dotenv, so support BASE_URL coming from playwright-tests/.env too.
        # Phase 7 v2: pre-bootstrap .env from .env.example (safe) to reduce friction.
        # This does not add secrets; it only creates a local .env template.
        try:
            env_example = test_dir / ".env.example"
            env_file = test_dir / ".env"
            if env_example.exists() and not env_file.exists():
                env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
                report["applied_fixes"].append("created_env_from_env_example")
                print("   🛠 Applied safe fix (precheck): created .env from .env.example")
        except Exception:
            # Never fail validation due to env bootstrapping
            pass

        base_url = self._get_env_value(test_dir, "BASE_URL")
        report["base_url"] = base_url or None
        if not base_url:
            print("ℹ️  Runtime validation skipped: BASE_URL is not set.")
            print("   Set BASE_URL in playwright-tests/.env (or export it) and re-run with --validate-mode runtime.")
            print(f"   Example: BASE_URL=http://localhost:3000")
            report["result"] = "skipped"
            report["skip_reason"] = "base_url_missing"
            report["missing_keys"] = ["BASE_URL"]
            report["suggestions"] = self._suggest_next_steps(
                test_dir=test_dir, mode=mode, fix_level=fix_level, skip_reason=report["skip_reason"]
            )
            self._write_validation_report(test_dir, report)
            return

        # Validate BASE_URL shape early (avoid confusing runtime errors).
        if not self._is_valid_base_url(base_url):
            print("ℹ️  Runtime validation skipped: BASE_URL is invalid (must be an absolute URL).")
            print(f"   Got: {base_url}")
            print("   Example: BASE_URL=http://localhost:3000")
            report["result"] = "skipped"
            report["skip_reason"] = "baseurl_invalid"
            report["missing_keys"] = ["BASE_URL"]
            report["suggestions"] = self._suggest_next_steps(
                test_dir=test_dir, mode=mode, fix_level=fix_level, skip_reason=report["skip_reason"]
            )
            self._write_validation_report(test_dir, report)
            return

        # Auth credential precheck (only if suite likely needs auth).
        # Signal sources (safe):
        #  - suite_metrics auth hooks count
        #  - presence of auth keys in .env.example
        auth_hooks = 0
        try:
            auth_hooks = int((report.get("suite_metrics") or {}).get("auth_hooks") or 0)
        except Exception:
            auth_hooks = 0
        env_example_keys = set(self._env_example_keys(test_dir))
        auth_keys = {"TEST_USER_EMAIL", "TEST_USER_PASSWORD"}
        auth_required = auth_hooks > 0 or bool(auth_keys.intersection(env_example_keys))

        if auth_required:
            missing: List[str] = []
            for k in sorted(auth_keys):
                v = self._get_env_value(test_dir, k)
                if not v:
                    missing.append(k)
            if missing:
                print("ℹ️  Runtime validation skipped: missing required auth credentials.")
                print(f"   Missing: {', '.join(missing)}")
                print("   Provide credentials via playwright-tests/.env or CLI flags.")
                report["result"] = "skipped"
                report["skip_reason"] = "auth_missing"
                report["missing_keys"] = missing
                report["suggestions"] = self._suggest_next_steps(
                    test_dir=test_dir, mode=mode, fix_level=fix_level, skip_reason=report["skip_reason"]
                )
                self._write_validation_report(test_dir, report)
                return

        # Run up to MAX_ATTEMPTS (attempt 1 is initial run, attempt 2 after safe fixes)
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            print(f"   ▶ Running Playwright tests (attempt {attempt}/{self.MAX_ATTEMPTS})...")
            ok, stdout, stderr, exit_code = self._run_playwright_tests(test_dir)

            if ok:
                print("   ✅ Validation passed: all Playwright tests succeeded.")
                report["attempts"].append(
                    {"attempt": attempt, "exit_code": exit_code, "kind": None, "headline": "passed"}
                )
                report["result"] = "passed"
                report["suggestions"] = self._suggest_pass_next_steps(
                    test_dir=test_dir,
                    mode=mode,
                    fix_level=fix_level,
                    suite_metrics=report.get("suite_metrics"),
                    quality=report.get("quality"),
                )
                self._write_validation_report(test_dir, report)
                return

            # Summarize and decide whether we can apply safe fixes
            print(f"   ❌ Validation failed (exit code {exit_code}).")
            summary = self._summarize_failure(stdout, stderr)
            self._print_failure_summary(summary)
            report["attempts"].append(
                {
                    "attempt": attempt,
                    "exit_code": exit_code,
                    "kind": summary.get("kind"),
                    "headline": summary.get("headline"),
                }
            )

            if attempt >= self.MAX_ATTEMPTS:
                print("   🛑 Reached max validation attempts. Leaving tests unchanged.")
                report["result"] = "failed"
                report["suggestions"] = self._suggest_next_steps(
                    test_dir=test_dir, mode=mode, fix_level=fix_level, kind=summary.get("kind"), skip_reason=None
                )
                self._write_validation_report(test_dir, report)
                return

            applied = self._apply_safe_fixes(test_dir, summary)
            if not applied:
                print("   🛑 No safe auto-fixes applicable. Leaving tests unchanged.")
                report["result"] = "failed"
                report["suggestions"] = self._suggest_next_steps(
                    test_dir=test_dir, mode=mode, fix_level=fix_level, kind=summary.get("kind"), skip_reason=None
                )
                self._write_validation_report(test_dir, report)
                return

        # Defensive: should never reach here
        print("   🛑 Validation loop ended without success.")
        report["result"] = "failed"
        last_kind = None
        if report["attempts"]:
            last_kind = report["attempts"][-1].get("kind")
        report["suggestions"] = self._suggest_next_steps(
            test_dir=test_dir, mode=mode, fix_level=fix_level, kind=last_kind, skip_reason=None
        )
        self._write_validation_report(test_dir, report)

    # ---------------------------
    # Helpers
    # ---------------------------

    @staticmethod
    def _which(cmd: str) -> Optional[str]:
        """Return path to executable if available in PATH."""
        try:
            import shutil
            return shutil.which(cmd)
        except Exception:
            return None

    @staticmethod
    def _read_env_value(env_path: Path, key: str) -> Optional[str]:
        """Read a single KEY=value from a .env file (minimal parser)."""
        if not env_path.exists():
            return None
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    val = v.strip()
                    return val if val else None
        except Exception:
            return None
        return None

    def _read_env_map(self, env_path: Path) -> Dict[str, str]:
        """
        Parse a .env file into a dict (minimal, safe parser). Values may be empty.
        """
        out: Dict[str, str] = {}
        if not env_path.exists():
            return out
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                if not k:
                    continue
                out[k] = v.strip()
        except Exception:
            return {}
        return out

    def _get_env_value(self, test_dir: Path, key: str) -> str:
        """
        Resolve env value with precedence:
          1) process environment
          2) suite .env file
        Treat empty strings as missing.
        """
        v = (os.environ.get(key) or "").strip()
        if v:
            return v
        v2 = self._read_env_value(test_dir / ".env", key)
        return (v2 or "").strip()

    @staticmethod
    def _is_valid_base_url(value: str) -> bool:
        try:
            from urllib.parse import urlparse
            u = urlparse(value.strip())
            return u.scheme in ("http", "https") and bool(u.netloc)
        except Exception:
            return False

    def _env_example_keys(self, test_dir: Path) -> List[str]:
        """
        Parse .env.example keys (safe: only key names).
        """
        env_example = test_dir / ".env.example"
        keys: List[str] = []
        if not env_example.exists():
            return keys
        try:
            for line in env_example.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _ = line.split("=", 1)
                k = k.strip()
                if k:
                    keys.append(k)
        except Exception:
            return []
        return sorted(set(keys))

    def _has_node_deps(self, test_dir: Path) -> bool:
        """
        Check if validation can run.

        We require either:
        - node_modules exists (npm install was run), OR
        - npx is available (can run playwright, still likely needs install)
        """
        if (test_dir / "node_modules").exists():
            return True
        return self._which("npx") is not None and (test_dir / "package.json").exists()

    def _suggest_next_steps(
        self,
        test_dir: Path,
        mode: str,
        fix_level: str = "conservative",
        kind: Optional[str] = None,
        skip_reason: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Return actionable, non-secret next steps for a given validation outcome.

        Output is structured so it can be consumed by humans or future automation.
        """
        suggestions: List[Dict[str, str]] = []

        def add(title: str, command: Optional[str] = None, note: Optional[str] = None) -> None:
            item: Dict[str, str] = {"title": title}
            if command:
                item["command"] = command
            if note:
                item["note"] = note
            suggestions.append(item)

        def env_keys_from_example() -> List[str]:
            """
            Parse .env.example keys if present (no secrets, only key names).
            """
            keys: List[str] = []
            env_example = test_dir / ".env.example"
            if not env_example.exists():
                return keys
            try:
                for line in env_example.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _ = line.split("=", 1)
                    k = k.strip()
                    if k:
                        keys.append(k)
            except Exception:
                return keys
            # stable order
            return sorted(set(keys))

        auth_keys = {"TEST_USER_EMAIL", "TEST_USER_PASSWORD"}
        example_keys = set(env_keys_from_example())

        # Skip reasons
        if skip_reason == "deps_not_installed":
            add("Install Node dependencies", f"cd {test_dir} && npm install")
            add("Install Playwright browsers", "npx playwright install --with-deps")
            return suggestions
        if skip_reason == "auth_missing":
            add(
                "Set auth credentials in playwright-tests/.env (do not commit secrets)",
                None,
                "Expected keys: TEST_USER_EMAIL and TEST_USER_PASSWORD.",
            )
            add(
                "Re-run validation (runtime)",
                f"python3 qualityforge/playwright/generator.py --validate-only {test_dir} --validate-mode runtime --base-url http://localhost:3000",
                "You can also pass --test-user-email and --test-user-password to write values into .env.",
            )
            return suggestions
        if skip_reason == "base_url_missing":
            add(
                "Set BASE_URL for runtime validation",
                "BASE_URL=http://localhost:3000",
                "Put this in playwright-tests/.env (recommended) or export it before running.",
            )
            if auth_keys.intersection(example_keys):
                add(
                    "If this suite requires auth, set credentials in .env",
                    None,
                    "Expected keys: TEST_USER_EMAIL and TEST_USER_PASSWORD (do not commit secrets).",
                )
            add(
                "Re-run validation",
                f"python3 qualityforge/playwright/generator.py --validate-only {test_dir} --validate-mode runtime --base-url http://localhost:3000",
            )
            return suggestions
        if skip_reason == "baseurl_invalid":
            add(
                "Set BASE_URL to a valid absolute URL",
                "BASE_URL=http://localhost:3000",
                "Put this in playwright-tests/.env (recommended) or export it before running.",
            )
            return suggestions
        if skip_reason == "invalid_mode":
            add("Use a valid validation mode", None, "Supported: static, runtime")
            return suggestions
        if skip_reason == "test_dir_missing":
            add("Verify the suite directory path exists", None, "It should be the folder containing package.json and playwright.config.*")
            return suggestions

        # Failure kinds
        if kind == "deps_missing":
            add("Install Node dependencies", f"cd {test_dir} && npm install")
            add("Install Playwright browsers", "npx playwright install --with-deps")
            add("Re-run validation (static)", f"python3 qualityforge/playwright/generator.py --validate-only {test_dir} --validate-mode static")
            if mode == "runtime":
                add("Re-run validation (runtime)", f"python3 qualityforge/playwright/generator.py --validate-only {test_dir} --validate-mode runtime")
            return suggestions
        if kind == "playwright_browsers_missing":
            add("Install Playwright browsers", f"cd {test_dir} && npx playwright install --with-deps")
            return suggestions
        if kind == "env_missing":
            add("Create .env from .env.example", f"cd {test_dir} && cp .env.example .env", "Then fill in required values (do not commit secrets).")
            if auth_keys.intersection(example_keys):
                add(
                    "Fill auth credentials in .env (if required)",
                    None,
                    "Set TEST_USER_EMAIL and TEST_USER_PASSWORD. Keep secrets local; never commit .env.",
                )
            if mode == "runtime":
                add("Ensure BASE_URL is set", None, "Required for runtime runs.")
            return suggestions
        if kind == "baseurl_invalid":
            add("Set BASE_URL to a valid absolute URL", None, "Example: http://localhost:3000")
            return suggestions
        if kind == "config_missing":
            add("Regenerate configuration files", None, "Ensure playwright.config.* exists in the suite directory.")
            return suggestions

        # Phase 7 v2: New failure kinds with targeted suggestions
        if kind == "timeout":
            add(
                "Increase test timeout in playwright.config",
                None,
                "Default is 30s. For slow apps or complex flows, set timeout: 60000 (60s) or higher in playwright.config.ts.",
            )
            add(
                "Check if the target app is responsive",
                None,
                "Slow responses may indicate app performance issues or network latency.",
            )
            if fix_level == "aggressive":
                add(
                    "Consider adding explicit waits",
                    None,
                    "Use page.waitForLoadState('networkidle') after navigation if the app loads resources dynamically.",
                )
            return suggestions

        if kind == "network_error":
            add(
                "Verify BASE_URL is reachable",
                f"curl -I ${{BASE_URL:-http://localhost:3000}}",
                "Connection refused often means the target app is not running or the URL is incorrect.",
            )
            add(
                "Check if the app requires VPN or special network access",
                None,
                "Some staging environments may require VPN or IP allowlisting.",
            )
            add(
                "Ensure the app is started before running tests",
                None,
                "For local development, start the app server first: npm run dev (or equivalent).",
            )
            return suggestions

        if kind == "auth_failure":
            add(
                "Verify auth credentials in .env",
                None,
                "Check TEST_USER_EMAIL and TEST_USER_PASSWORD are valid for the target environment.",
            )
            add(
                "Check if the test account exists and is active",
                None,
                "Auth failures (401/403) may indicate expired passwords, disabled accounts, or missing permissions.",
            )
            add(
                "Review auth flow in the generated tests",
                None,
                "Ensure the login sequence matches the app's actual auth flow (SSO, MFA, etc.).",
            )
            return suggestions

        if kind == "element_not_found":
            add(
                "Generate a locator-hints seed (from TODO steps)",
                f"python3 qualityforge/playwright/generator.py --emit-locator-hints-seed {test_dir}",
                "Element not found often means selectors are outdated or incorrect. Use locator hints to provide accurate selectors.",
            )
            add(
                "Run tests in headed mode to debug",
                f"cd {test_dir} && npx playwright test --headed",
                "Watching the browser can reveal timing issues or unexpected UI states.",
            )
            if fix_level == "aggressive":
                add(
                    "Consider using more resilient locators",
                    None,
                    "Prefer getByRole, getByLabel, getByText over CSS selectors. Check Playwright best practices.",
                )
            return suggestions

        if kind == "test_failures":
            # Keep guidance conservative: do not suggest selector guessing. Point to MCP + hints workflow.
            add(
                "Generate a locator-hints seed (from TODO steps)",
                f"python3 qualityforge/playwright/generator.py --emit-locator-hints-seed {test_dir}",
                "Fill the generated locator-hints.seed.json using Playwright MCP and then regenerate with --locator-hints.",
            )
            add(
                "Run tests in headed mode to debug",
                f"cd {test_dir} && npx playwright test --headed",
                "Watching the browser can reveal timing issues, unexpected UI states, or navigation problems.",
            )
            if fix_level == "aggressive":
                # Phase 7 v2: Enhanced aggressive-mode suggestions
                add(
                    "Add waitForLoadState after navigation",
                    None,
                    "If tests fail after page.goto(), add: await page.waitForLoadState('networkidle'); This waits for network activity to settle.",
                )
                add(
                    "Use more resilient locators",
                    None,
                    "Replace CSS selectors with accessible locators: getByRole('button', { name: 'Submit' }) instead of locator('button.submit').",
                )
                add(
                    "Consider adding explicit waits",
                    None,
                    "For dynamic content, use: await expect(element).toBeVisible(); before interacting with elements.",
                )
            add(
                "Regenerate tests with locator hints (optional)",
                None,
                "If you have locator-hints.json, re-run generation with --locator-hints to reduce TODOs and improve locator fidelity.",
            )
            return suggestions

        # Generic fallback
        add("Review validation output", None, "See the failure headline and adjust suite/environment accordingly.")
        return suggestions

    def _suggest_pass_next_steps(
        self,
        test_dir: Path,
        mode: str,
        fix_level: str = "conservative",
        suite_metrics: Optional[Dict[str, object]] = None,
        quality: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, str]]:
        """
        Return optional "next steps" guidance when validation passes.

        Unlike failure suggestions, these are non-urgent recommendations for
        improving the suite quality or taking the next logical step.

        Phase 7 v2: Provides helpful guidance without implying failure.
        """
        suggestions: List[Dict[str, str]] = []

        def add(title: str, command: Optional[str] = None, note: Optional[str] = None) -> None:
            item: Dict[str, str] = {"title": title}
            if command:
                item["command"] = command
            if note:
                item["note"] = note
            suggestions.append(item)

        metrics = suite_metrics or {}
        qual = quality or {}
        warnings = qual.get("warnings") or []
        gates = qual.get("gates") or {}

        # 1. If static mode passed, suggest upgrading to runtime
        if mode == "static":
            add(
                "Run runtime validation against a live app",
                f"python3 qualityforge/playwright/generator.py --validate-only {test_dir} --validate-mode runtime --base-url http://localhost:3000",
                "Static validation confirms structure; runtime validates actual behavior.",
            )

        # 2. If TODOs present, suggest locator-hints workflow
        todos = 0
        try:
            todos = int(metrics.get("todos") or 0)
        except Exception:
            todos = 0
        if todos > 0:
            add(
                "Reduce TODO steps with locator hints",
                f"python3 qualityforge/playwright/generator.py --emit-locator-hints-seed {test_dir}",
                f"Suite has {todos} TODO(s). Fill the seed file using Playwright MCP, then regenerate with --locator-hints.",
            )

        # 3. If tests with zero assertions exist, flag it
        tests_zero_assert = 0
        try:
            tests_zero_assert = int(metrics.get("tests_with_zero_assertions") or 0)
        except Exception:
            tests_zero_assert = 0
        if tests_zero_assert > 0:
            add(
                "Add assertions to tests",
                None,
                f"{tests_zero_assert} test(s) have no expect() calls. Tests without assertions may pass but not verify behavior.",
            )

        # 4. If quality warnings present, point to the report
        if warnings:
            high_sev = [w for w in warnings if w.get("severity") == "high"]
            if high_sev:
                add(
                    "Review quality warnings in validation-report.json",
                    None,
                    f"{len(high_sev)} high-severity warning(s) detected. See quality.warnings in the report.",
                )

        # 5. If runtime mode passed cleanly, suggest CI integration
        if mode == "runtime" and not warnings:
            add(
                "Integrate tests into CI",
                None,
                "Suite passes runtime validation. Consider adding to CI pipeline for regression coverage.",
            )

        return suggestions

    def _compute_suite_metrics(self, test_dir: Path) -> Dict[str, object]:
        """
        Compute static “generation quality” metrics by scanning the suite files.

        This does not require Playwright dependencies or a running app.
        It is designed to help quantify how complete the generated suite is.
        """
        metrics: Dict[str, object] = {
            "spec_files": 0,
            "tests": 0,
            "todos": 0,
            "assertions": 0,
            "page_actions": 0,
            "auth_hooks": 0,
            "has_env_example": False,
            "has_env": False,
            # Quality signals (static, heuristic):
            "tests_with_zero_assertions": 0,
            "tests_with_todos": 0,
            "waitForTimeout_calls": 0,
            "css_locator_calls": 0,
            "accessible_locator_calls": 0,
        }

        try:
            metrics["has_env_example"] = (test_dir / ".env.example").exists()
            metrics["has_env"] = (test_dir / ".env").exists()

            spec_files = list(test_dir.glob("*.spec.ts")) + list(test_dir.glob("*.spec.js"))
            metrics["spec_files"] = len(spec_files)

            # NOTE: These are conservative heuristics; they are used as trend metrics and for warnings.
            test_re = re.compile(r"\btest\(\s*['\"]")  # avoid test.describe()
            todo_re = re.compile(r"//\s*TODO:")
            expect_re = re.compile(r"\bexpect\(")
            page_action_re = re.compile(r"\bpage\.(goto|click|fill|check|uncheck|press|type|selectOption|waitFor|waitForSelector|waitForURL|locator|getByRole|getByText|getByLabel|getByTestId)\b")
            auth_hook_re = re.compile(r"\btest\.beforeEach\(")

            for path in spec_files:
                try:
                    content = path.read_text(encoding="utf-8")
                except Exception:
                    continue

                metrics["tests"] += len(test_re.findall(content))
                metrics["todos"] += len(todo_re.findall(content))
                metrics["assertions"] += len(expect_re.findall(content))
                metrics["page_actions"] += len(page_action_re.findall(content))
                metrics["auth_hooks"] += len(auth_hook_re.findall(content))

                # File-level quality posture signals (cheap and stable).
                metrics["waitForTimeout_calls"] += content.count("waitForTimeout(")
                # Locator strategy: prefer accessible locators over CSS locator().
                metrics["accessible_locator_calls"] += (
                    content.count(".getByRole(")
                    + content.count(".getByLabel(")
                    + content.count(".getByText(")
                    + content.count(".getByTestId(")
                )
                metrics["css_locator_calls"] += content.count(".locator(")

                # Per-test heuristics: count tests that have 0 assertions and/or contain TODOs.
                # This is a simple line-based scan (intentionally not a TS parser).
                in_test = False
                cur_assertions = 0
                cur_todos = 0
                saw_any_test = False
                for line in content.splitlines():
                    if test_re.search(line):
                        # finalize previous test (if any)
                        if in_test:
                            if cur_assertions == 0:
                                metrics["tests_with_zero_assertions"] += 1
                            if cur_todos > 0:
                                metrics["tests_with_todos"] += 1
                        # start new test
                        in_test = True
                        saw_any_test = True
                        cur_assertions = 0
                        cur_todos = 0
                        continue
                    if not in_test:
                        continue
                    if "expect(" in line:
                        cur_assertions += 1
                    if "// TODO:" in line:
                        cur_todos += 1
                # finalize last test in file
                if saw_any_test and in_test:
                    if cur_assertions == 0:
                        metrics["tests_with_zero_assertions"] += 1
                    if cur_todos > 0:
                        metrics["tests_with_todos"] += 1

            # A simple “completion” signal: fewer TODOs relative to tests.
            # This is not perfect, but it’s a useful trend metric.
            tests = int(metrics["tests"] or 0)
            todos = int(metrics["todos"] or 0)
            if tests > 0:
                metrics["avg_todos_per_test"] = round(todos / tests, 2)
            else:
                metrics["avg_todos_per_test"] = None

        except Exception:
            # Never fail validation due to metrics.
            return metrics

        return metrics

    @staticmethod
    def _derive_quality(suite_metrics: Dict[str, object], todo_policy: str = "allow") -> Dict[str, object]:
        """
        Derive high-signal quality warnings/gates from suite_metrics.

        This does not change validation result; it is guidance to prevent
        "tests that run but are low value" (e.g., TODO-heavy or no assertions).
        """
        def to_int(v: object) -> int:
            try:
                return int(v or 0)
            except Exception:
                return 0

        def to_float(v: object) -> Optional[float]:
            try:
                if v is None:
                    return None
                return float(v)
            except Exception:
                return None

        tests = to_int(suite_metrics.get("tests"))
        todos = to_int(suite_metrics.get("todos"))
        assertions = to_int(suite_metrics.get("assertions"))
        tests_zero_assert = to_int(suite_metrics.get("tests_with_zero_assertions"))
        tests_with_todos = to_int(suite_metrics.get("tests_with_todos"))
        wait_for_timeout = to_int(suite_metrics.get("waitForTimeout_calls"))
        css_loc = to_int(suite_metrics.get("css_locator_calls"))
        acc_loc = to_int(suite_metrics.get("accessible_locator_calls"))
        avg_todos = to_float(suite_metrics.get("avg_todos_per_test"))

        warnings: List[Dict[str, object]] = []

        # Warnings (actionable, but non-fatal)
        if tests == 0:
            warnings.append(
                {
                    "severity": "high",
                    "rule": "no_tests_detected",
                    "message": "Suite metrics detected 0 tests. This likely means discovery failed or specs are missing.",
                }
            )
        if tests_zero_assert > 0:
            warnings.append(
                {
                    "severity": "high",
                    "rule": "tests_need_assertions",
                    "message": f"{tests_zero_assert} test(s) appear to have 0 expect() assertions. Add at least one deterministic assertion per test.",
                }
            )
        if todos > 0:
            warnings.append(
                {
                    "severity": "medium",
                    "rule": "todos_present",
                    "message": f"Suite contains TODOs ({todos} total across {tests_with_todos} test(s)). TODOs should be driven down using locator hints / MCP or manual implementation.",
                }
            )
        if avg_todos is not None and avg_todos >= 1.0:
            warnings.append(
                {
                    "severity": "medium",
                    "rule": "todo_density_high",
                    "message": f"High TODO density (avg_todos_per_test={avg_todos}). Consider running the locator-hints seed workflow to convert TODO steps into real actions.",
                }
            )
        if wait_for_timeout > 0:
            warnings.append(
                {
                    "severity": "high",
                    "rule": "avoid_waitForTimeout",
                    "message": f"Found page.waitForTimeout() usage ({wait_for_timeout} call(s)). Prefer deterministic waits (expect/toHaveURL/waitForLoadState).",
                }
            )
        if css_loc > acc_loc and css_loc > 0:
            warnings.append(
                {
                    "severity": "low",
                    "rule": "prefer_accessible_locators",
                    "message": "Suite appears to use CSS locators more than accessible locators; prefer getByRole/getByLabel/getByText when possible.",
                }
            )

        # Gates: quick, machine-consumable pass/fail signals (still non-fatal).
        gates: Dict[str, object] = {
            "has_tests": tests > 0,
            "no_zero_assertion_tests": tests_zero_assert == 0,
            "no_waitForTimeout": wait_for_timeout == 0,
            "no_todos": todos == 0,
        }

        # Enforce TODO policy (opt-in): warn/error semantics for consumers.
        # This does not change runtime validation status; it is a quality gate.
        if todo_policy not in ("allow", "warn", "error"):
            todo_policy = "allow"
        gates["todo_policy"] = todo_policy
        if todo_policy == "allow":
            gates["todo_policy_pass"] = True
        elif todo_policy == "warn":
            gates["todo_policy_pass"] = True
            if todos > 0:
                warnings.append(
                    {
                        "severity": "high",
                        "rule": "todo_policy_warn",
                        "message": "TODO policy is set to 'warn' and TODOs were detected. Treat this suite as incomplete until TODOs are resolved.",
                    }
                )
        else:  # error
            gates["todo_policy_pass"] = (todos == 0)
            if todos > 0:
                warnings.append(
                    {
                        "severity": "high",
                        "rule": "todo_policy_error",
                        "message": "TODO policy is set to 'error' and TODOs were detected. For 'Full Context' users, TODOs should be driven to zero via locator-hints/MCP/manual implementation.",
                    }
                )

        # If assertions are 0 overall, that’s a strong smell.
        if tests > 0 and assertions == 0:
            warnings.append(
                {
                    "severity": "high",
                    "rule": "suite_has_no_assertions",
                    "message": "Suite contains tests but 0 total assertions. Tests without assertions are usually not effective.",
                }
            )

        return {"warnings": warnings, "gates": gates}

    def _run_playwright_tests(self, test_dir: Path) -> Tuple[bool, str, str, int]:
        """
        Run Playwright tests using npx.

        Returns:
            (ok, stdout, stderr, exit_code)
        """
        import subprocess

        # Prefer local install via npx. Use --reporter=line for compact output.
        # Use --pass-with-no-tests to avoid false failures in empty dirs.
        cmd = ["npx", "playwright", "test", "--reporter=line", "--pass-with-no-tests"]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(test_dir),
                capture_output=True,
                text=True,
            )
            ok = proc.returncode == 0
            return ok, proc.stdout or "", proc.stderr or "", proc.returncode
        except FileNotFoundError:
            return False, "", "npx not found on PATH", 127
        except Exception as e:
            return False, "", f"Unexpected error running Playwright: {e}", 1

    def _static_validate(self, test_dir: Path) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Perform static validation of the generated suite without executing against an app.

        Checks:
          - Playwright CLI can be invoked
          - Tests can be discovered (`--list`)
          - Config file exists

        This does NOT assert application behavior; it ensures the generated
        suite is structurally runnable.
        """
        import subprocess

        config_ts = test_dir / "playwright.config.ts"
        config_js = test_dir / "playwright.config.js"
        if not config_ts.exists() and not config_js.exists():
            print("   ❌ Static validation failed: playwright config file missing.")
            return False, {"kind": "config_missing", "headline": "playwright config missing"}

        # 1) Print Playwright version
        try:
            proc_ver = subprocess.run(
                ["npx", "playwright", "--version"],
                cwd=str(test_dir),
                capture_output=True,
                text=True,
            )
            if proc_ver.returncode == 0:
                ver = (proc_ver.stdout or proc_ver.stderr or "").strip()
                print(f"   ✅ Playwright available: {ver}")
            else:
                print("   ❌ Static validation failed: cannot run `npx playwright --version`.")
                summary = self._summarize_failure(proc_ver.stdout or "", proc_ver.stderr or "")
                self._print_failure_summary(summary)
                return False, summary
        except Exception as e:
            print(f"   ❌ Static validation failed: error invoking Playwright: {e}")
            return False, {"kind": "exception", "headline": str(e)}

        # 2) Test discovery (no execution)
        try:
            proc_list = subprocess.run(
                ["npx", "playwright", "test", "--list"],
                cwd=str(test_dir),
                capture_output=True,
                text=True,
            )
            if proc_list.returncode == 0:
                out = (proc_list.stdout or "").strip()
                # Print a compact success message; list output can be long.
                print("   ✅ Test discovery succeeded (`npx playwright test --list`).")
                if out:
                    # Heuristic: show only first few lines
                    lines = out.splitlines()
                    preview = "\n".join(lines[:6])
                    print("   ℹ️  Discovered tests (preview):")
                    for ln in preview.splitlines():
                        print(f"      {ln}")
                return True, None
            else:
                print("   ❌ Static validation failed: test discovery failed.")
                summary = self._summarize_failure(proc_list.stdout or "", proc_list.stderr or "")
                self._print_failure_summary(summary)

                # If we can provide a safe remediation message, do so (without spamming stack traces).
                if summary.get("kind") in ("deps_missing", "playwright_browsers_missing"):
                    print("   🛠 Suggested next steps:")
                    print(f"      cd {test_dir}")
                    print("      npm install")
                    print("      npx playwright install --with-deps")
                return False, summary
        except Exception as e:
            return False, {"kind": "exception", "headline": str(e)}

    @staticmethod
    def _summarize_failure(stdout: str, stderr: str) -> Dict[str, str]:
        """
        Pull out the most useful signals from Playwright output.

        Phase 7 v2: Expanded pattern detection for better diagnostics.

        Supported kinds (in detection order):
          - deps_missing: Node module not found
          - playwright_browsers_missing: Browser executable missing
          - env_missing: Environment variable undefined
          - baseurl_invalid: Invalid BASE_URL format
          - timeout: Test or action timeout exceeded
          - network_error: Connection refused or network failure
          - auth_failure: 401/403 or auth-related error
          - element_not_found: Locator failed to find element
          - test_failures: Generic test assertion failure (fallback)
        """
        combined = "\n".join([stdout.strip(), stderr.strip()]).strip()
        combined_lower = combined.lower()
        summary: Dict[str, str] = {"raw": combined}

        # Detection order matters: more specific patterns first, generic last.

        # 1. Environment/setup issues (highest priority - must fix before tests can run)
        if "Cannot find module" in combined or "MODULE_NOT_FOUND" in combined:
            summary["kind"] = "deps_missing"
        elif "browserType.launch" in combined and "Executable doesn't exist" in combined:
            summary["kind"] = "playwright_browsers_missing"
        elif "process.env." in combined and "undefined" in combined:
            summary["kind"] = "env_missing"
        elif "baseURL" in combined and ("Invalid URL" in combined or "ERR_INVALID_URL" in combined):
            summary["kind"] = "baseurl_invalid"

        # 2. Network/connectivity issues
        elif any(p in combined for p in ("ERR_CONNECTION_REFUSED", "ECONNREFUSED", "net::ERR_")):
            summary["kind"] = "network_error"
        elif "ETIMEDOUT" in combined or "ENOTFOUND" in combined:
            summary["kind"] = "network_error"

        # 3. Auth failures (HTTP 401/403 or explicit auth errors)
        elif any(p in combined_lower for p in ("401", "403", "unauthorized", "forbidden")):
            # Verify it's an actual auth error, not just a test name
            if any(p in combined for p in ("status 401", "status 403", "HTTP 401", "HTTP 403", "Error: 401", "Error: 403")):
                summary["kind"] = "auth_failure"
            elif "unauthorized" in combined_lower or "forbidden" in combined_lower:
                summary["kind"] = "auth_failure"
            else:
                summary["kind"] = "test_failures"

        # 4. Timeout issues
        elif any(p in combined for p in ("TimeoutError", "Timeout exceeded", "Test timeout")):
            summary["kind"] = "timeout"
        elif "timeout" in combined_lower and ("exceeded" in combined_lower or "waiting" in combined_lower):
            summary["kind"] = "timeout"

        # 5. Element/locator not found
        elif any(p in combined for p in ("locator.click:", "locator.fill:", "waiting for locator")):
            summary["kind"] = "element_not_found"
        elif "strict mode violation" in combined_lower:
            summary["kind"] = "element_not_found"
        elif "no element matching" in combined_lower or "element not found" in combined_lower:
            summary["kind"] = "element_not_found"

        # 6. Generic test failures (fallback)
        else:
            summary["kind"] = "test_failures"

        # Try to extract a concise headline
        headline = ""
        for line in combined.splitlines():
            if "Error:" in line or "ERR_" in line or "Cannot find module" in line:
                headline = line.strip()
                break
            if "TimeoutError" in line or "timeout" in line.lower():
                headline = line.strip()
                break
        summary["headline"] = headline or "Playwright tests failed (see raw output)"
        return summary

    @staticmethod
    def _print_failure_summary(summary: Dict[str, str]) -> None:
        """Pretty-print failure summary."""
        print("   🔎 Failure summary:")
        print(f"      • kind: {summary.get('kind')}")
        print(f"      • headline: {summary.get('headline')}")

    def _apply_safe_fixes(self, test_dir: Path, summary: Dict[str, str]) -> bool:
        """
        Apply ONLY safe, non-behavior-changing fixes.

        Phase 7 v2: Expanded to handle new failure kinds with targeted diagnostics.

        Returns:
            True if any fix was applied, else False.
        """
        kind = summary.get("kind", "")

        if kind in ("deps_missing", "playwright_browsers_missing"):
            # We can't install deps in the sandbox reliably (network restrictions),
            # so we provide guidance only.
            print("   🛠 Safe fix suggestion:")
            print(f"      cd {test_dir}")
            print("      npm install")
            print("      npx playwright install --with-deps")
            return False

        if kind == "env_missing":
            env_example = test_dir / ".env.example"
            env_file = test_dir / ".env"
            if env_example.exists() and not env_file.exists():
                # Safe fix: create a .env by copying .env.example (still requires user to fill secrets)
                try:
                    env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
                    print("   🛠 Applied safe fix: created .env from .env.example (fill in credentials).")
                    return True
                except Exception as e:
                    print(f"   ⚠️  Failed to create .env from .env.example: {e}")
                    return False

            print("   🛠 Safe fix suggestion: Ensure required environment variables are set (.env).")
            return False

        if kind == "baseurl_invalid":
            env_example = test_dir / ".env.example"
            env_file = test_dir / ".env"
            # Safe fix: ensure a .env exists so baseURL can be set without touching code.
            if env_example.exists() and not env_file.exists():
                try:
                    env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
                    print("   🛠 Applied safe fix: created .env from .env.example (set BASE_URL).")
                    return True
                except Exception as e:
                    print(f"   ⚠️  Failed to create .env from .env.example: {e}")
                    return False
            print("   🛠 Safe fix suggestion: Set BASE_URL in .env to a valid absolute URL.")
            return False

        # Phase 7 v2: Expanded safe fix coverage for new failure kinds

        if kind == "timeout":
            # Safe diagnostic: print config guidance (no auto-edit)
            print("   🛠 Safe fix suggestion (timeout):")
            print("      Consider increasing timeout in playwright.config.ts:")
            print("      export default defineConfig({")
            print("        timeout: 60000, // 60 seconds")
            print("        expect: { timeout: 10000 },")
            print("      });")
            return False

        if kind == "network_error":
            # Safe diagnostic: attempt to check if BASE_URL is reachable
            base_url = self._get_env_value(test_dir, "BASE_URL")
            if base_url:
                print(f"   🔍 Checking if BASE_URL is reachable: {base_url}")
                try:
                    import urllib.request
                    import urllib.error
                    req = urllib.request.Request(base_url, method="HEAD")
                    req.add_header("User-Agent", "QualityForge-Validator/1.0")
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        print(f"   ✅ BASE_URL responded with status {resp.status}")
                        print("   🛠 Network error may be intermittent. Consider re-running.")
                except urllib.error.URLError as e:
                    print(f"   ❌ BASE_URL is not reachable: {e.reason}")
                    print("   🛠 Safe fix suggestion: Ensure the target app is running.")
                except Exception as e:
                    print(f"   ⚠️  Could not check BASE_URL: {e}")
            else:
                print("   🛠 Safe fix suggestion: Set BASE_URL in .env and ensure the app is running.")
            return False

        if kind == "auth_failure":
            # Safe diagnostic: remind about credentials (no auto-edit)
            print("   🛠 Safe fix suggestion (auth failure):")
            print("      1. Verify TEST_USER_EMAIL and TEST_USER_PASSWORD in .env")
            print("      2. Ensure the test account exists and is active")
            print("      3. Check if the auth flow matches the generated tests")
            return False

        if kind == "element_not_found":
            # Safe diagnostic: suggest headed mode for debugging
            print("   🛠 Safe fix suggestion (element not found):")
            print(f"      Run tests in headed mode to debug:")
            print(f"      cd {test_dir} && npx playwright test --headed")
            print("      Use --emit-locator-hints-seed to generate a seed file for better selectors.")
            return False

        # For generic test failures, we do not auto-edit.
        print("   🛠 No safe automated edits for this failure type.")
        return False

    def _write_validation_report(self, test_dir: Path, report: Dict) -> None:
        """
        Write validation-report.json into the generated suite directory.

        Important:
          - This report must not contain secrets.
          - We only store mode, base_url (safe), and error summaries.
        """
        try:
            if not test_dir.exists():
                return
            report_path = test_dir / "validation-report.json"
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"   📝 Validation report: {report_path.name}")
        except Exception:
            # Never fail generation/validation due to report writing.
            return


# ==============================================================================
# 6. SPEC REVIEWER (Static Best-Practice Review)
# ==============================================================================

class SpecReviewer:
    """
    Static review of Playwright spec files (no execution).

    This is designed for meeting-time reviews when you may not have:
      - a runnable app target, or
      - dependencies installed, or
      - time to execute tests.

    It produces a machine-readable report (`spec-review-report.json`) that highlights:
      - duplicate test titles (Playwright discovery blocker)
      - flaky anti-patterns (waitForTimeout, arbitrary sleeps)
      - locator strategy issues (overuse of CSS locators vs accessible locators)
      - performance-test pitfalls (basic heuristics)
    """

    def review_path(self, path: Path) -> Dict[str, object]:
        if path.is_file():
            if not path.name.endswith((".spec.ts", ".spec.js")):
                raise ValueError(f"Not a Playwright spec file: {path}")
            suite_dir = path.parent
            spec_files = [path]
        else:
            suite_dir = path
            spec_files = list(suite_dir.glob("*.spec.ts")) + list(suite_dir.glob("*.spec.js"))
            if not spec_files:
                raise FileNotFoundError(f"No *.spec.ts/*.spec.js files found in {suite_dir}")

        findings: List[Dict[str, object]] = []
        stats: Dict[str, int] = {
            "spec_files": len(spec_files),
            "tests": 0,
            "duplicate_titles": 0,
            "waitForTimeout_calls": 0,
            "css_locator_calls": 0,
            "accessible_locator_calls": 0,
        }

        # Aggregate duplicate title detection across the reviewed set.
        seen_titles: Dict[str, str] = {}  # title -> "file:line"

        for file_path in sorted(spec_files):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()

            # Detect test titles: test('title', ...) / test("title", ...)
            for idx, line in enumerate(lines, start=1):
                m = re.search(r"\btest\(\s*(['\"])(.+?)\1\s*,", line)
                if m:
                    title = m.group(2).strip()
                    stats["tests"] += 1
                    loc = f"{file_path.name}:{idx}"
                    if title in seen_titles:
                        stats["duplicate_titles"] += 1
                        findings.append(
                            {
                                "severity": "high",
                                "rule": "duplicate_test_title",
                                "message": f"Duplicate test title: \"{title}\" (first: {seen_titles[title]}, duplicate: {loc})",
                                "file": str(file_path),
                                "line": idx,
                            }
                        )
                    else:
                        seen_titles[title] = loc

                if "waitForTimeout(" in line:
                    stats["waitForTimeout_calls"] += 1
                    findings.append(
                        {
                            "severity": "high",
                            "rule": "avoid_waitForTimeout",
                            "message": "Avoid page.waitForTimeout() in most cases; prefer deterministic waits (toBeVisible/toHaveURL/waitForLoadState).",
                            "file": str(file_path),
                            "line": idx,
                        }
                    )

                # Locator strategy heuristics
                if ".getByRole(" in line or ".getByLabel(" in line or ".getByText(" in line or ".getByTestId(" in line:
                    stats["accessible_locator_calls"] += 1
                if ".locator(" in line:
                    stats["css_locator_calls"] += 1

                # Goto hygiene (common generator TODO issue): page.goto('some words')
                m_goto = re.search(r"\bpage\.goto\(\s*(['\"])(.+?)\1\s*\)", line)
                if m_goto:
                    url = m_goto.group(2).strip()
                    if not (url.startswith("/") or url.startswith("http")):
                        findings.append(
                            {
                                "severity": "medium",
                                "rule": "goto_should_be_url_or_path",
                                "message": f"page.goto() target does not look like a URL/path: '{url}'. Prefer '/path' or 'https://...'.",
                                "file": str(file_path),
                                "line": idx,
                            }
                        )

            # Performance-test heuristics (file-level)
            is_perf = bool(re.search(r"\bperformance\b", file_path.name, re.IGNORECASE)) or bool(
                re.search(r"\bPerformance\b", text)
            )
            if is_perf:
                if "expect(" not in text:
                    findings.append(
                        {
                            "severity": "medium",
                            "rule": "performance_tests_need_assertions",
                            "message": "Performance-oriented specs should include at least one deterministic assertion (avoid purely logging timings).",
                            "file": str(file_path),
                            "line": 1,
                        }
                    )

        # Summarize locator posture
        if stats["css_locator_calls"] > stats["accessible_locator_calls"]:
            findings.append(
                {
                    "severity": "low",
                    "rule": "prefer_accessible_locators",
                    "message": "Suite appears to use CSS locators more than accessible locators; prefer getByRole/getByLabel/getByText when possible.",
                    "file": str(suite_dir),
                    "line": 0,
                }
            )

        report = {
            "phase": 7,
            "type": "spec_review",
            "reviewed_path": str(path),
            "suite_dir": str(suite_dir),
            "stats": stats,
            "findings": findings,
        }
        return report

    @staticmethod
    def write_report(suite_dir: Path, report: Dict[str, object]) -> Path:
        out_path = suite_dir / "spec-review-report.json"
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return out_path

    @staticmethod
    def emit_locator_hints_seed(path: Path, repo_playwright_root: Optional[Path] = None) -> Tuple[Path, Dict[str, object]]:
        """
        Create a locator-hints seed file from TODO steps found in generated specs.

        This is meant to be filled using Playwright MCP (or manual edits) and then
        consumed by the generator via --locator-hints.

        Output file: locator-hints.seed.json (written to suite dir)

        Optional:
          - If repo_playwright_root is provided (e.g., a local repo Playwright tests folder),
            the seed will include lightweight repo candidate snippets per step to accelerate filling
            (still safe-by-default: it does not auto-fill code).
        """
        if path.is_file():
            if not path.name.endswith((".spec.ts", ".spec.js")):
                raise ValueError(f"Not a Playwright spec file: {path}")
            suite_dir = path.parent
            spec_files = [path]
        else:
            suite_dir = path
            spec_files = list(suite_dir.glob("*.spec.ts")) + list(suite_dir.glob("*.spec.js"))
            if not spec_files:
                raise FileNotFoundError(f"No *.spec.ts/*.spec.js files found in {suite_dir}")

        # Extract TODO steps of the form: // TODO: Implement step - <step text>
        todo_step_re = re.compile(r"^\s*//\s*TODO:\s*Implement step\s*-\s*(.+?)\s*$")
        unique_steps: Dict[str, int] = {}  # step text -> count

        for file_path in spec_files:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                m = todo_step_re.match(line)
                if m:
                    step = m.group(1).strip()
                    if step:
                        unique_steps[step] = unique_steps.get(step, 0) + 1

        repo_candidates_by_step: Dict[str, List[Dict[str, object]]] = {}
        if repo_playwright_root:
            try:
                repo_candidates_by_step = SpecReviewer._mine_repo_candidates(
                    steps=list(unique_steps.keys()),
                    repo_root=repo_playwright_root,
                    max_candidates_per_step=3,
                )
            except Exception:
                repo_candidates_by_step = {}

        # Build seed JSON. We intentionally leave code empty so it won't apply until the user fills it in.
        step_overrides: List[Dict[str, object]] = []
        for step_text, count in sorted(unique_steps.items(), key=lambda x: (-x[1], x[0])):
            step_overrides.append(
                {
                    "pattern": re.escape(step_text),
                    "action_type": "unknown",
                    "locator_method": "manual",
                    "code": "",
                    "confidence": 0.0,
                    "note": f"TODO occurrences: {count}. Fill code using Playwright MCP locator capture.",
                    "repo_candidates": repo_candidates_by_step.get(step_text, []),
                }
            )

        seed: Dict[str, object] = {
            "version": "1",
            "generated_by": "qualityforge",
            "base_url": "",
            "urls": {},
            "step_overrides": step_overrides,
            "repo_context": {
                "repo_playwright_root": (str(repo_playwright_root) if repo_playwright_root else None),
                "note": "repo_candidates are optional hints only; review carefully before copying into code.",
            },
        }

        out_path = suite_dir / "locator-hints.seed.json"
        out_path.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return out_path, seed

    @staticmethod
    def _mine_repo_candidates(
        steps: List[str],
        repo_root: Path,
        max_candidates_per_step: int = 3,
    ) -> Dict[str, List[Dict[str, object]]]:
        """
        Best-effort, safe suggestion helper:

        Given TODO step texts and a repo Playwright root (directory), scan repo spec files for likely
        relevant lines (usually getByRole/getByLabel/getByText + click/fill/expect).

        This intentionally does NOT auto-fill overrides; it only provides small candidate snippets.
        """
        if not repo_root.exists():
            return {}

        repo_specs = list(repo_root.glob("**/*.spec.ts")) + list(repo_root.glob("**/*.spec.js"))
        if not repo_specs:
            return {}

        def tokenize(s: str) -> List[str]:
            s = (s or "").lower()
            parts = re.findall(r"[a-z0-9]{4,}", s)
            seen = set()
            out: List[str] = []
            for p in parts:
                if p not in seen:
                    seen.add(p)
                    out.append(p)
            return out

        step_tokens: Dict[str, List[str]] = {s: tokenize(s) for s in steps}
        results: Dict[str, List[Tuple[int, str, int, str]]] = {s: [] for s in steps}  # (score, file, line, code)

        interesting_re = re.compile(
            r"(getByRole|getByLabel|getByText|getByTestId|\\.locator\\(|expect\\(|\\.click\\(|\\.fill\\()",
            re.IGNORECASE,
        )

        for spec_path in repo_specs:
            try:
                lines = spec_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue
            for idx, line in enumerate(lines, start=1):
                if not interesting_re.search(line):
                    continue
                line_tokens = set(tokenize(line))
                if not line_tokens:
                    continue
                for step_text, toks in step_tokens.items():
                    if not toks:
                        continue
                    shared = 0
                    for t in toks[:10]:
                        if t in line_tokens:
                            shared += 1
                    if shared <= 0:
                        continue
                    results[step_text].append((shared, str(spec_path), idx, line.strip()))

        out: Dict[str, List[Dict[str, object]]] = {}
        for step_text, scored in results.items():
            if not scored:
                continue
            scored.sort(key=lambda x: (-x[0], x[1], x[2]))
            top = scored[:max_candidates_per_step]
            out[step_text] = [{"score": s, "file": f, "line": ln, "code": code} for (s, f, ln, code) in top]
        return out

    def _run_playwright_tests(self, test_dir: Path) -> Tuple[bool, str, str, int]:
        """
        Run Playwright tests using npx.

        Returns:
            (ok, stdout, stderr, exit_code)
        """
        import subprocess

        # Prefer local install via npx. Use --reporter=line for compact output.
        # Use --pass-with-no-tests to avoid false failures in empty dirs.
        cmd = ["npx", "playwright", "test", "--reporter=line", "--pass-with-no-tests"]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(test_dir),
                capture_output=True,
                text=True,
            )
            ok = proc.returncode == 0
            return ok, proc.stdout or "", proc.stderr or "", proc.returncode
        except FileNotFoundError:
            return False, "", "npx not found on PATH", 127
        except Exception as e:
            return False, "", f"Unexpected error running Playwright: {e}", 1

    def _static_validate(self, test_dir: Path) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Perform static validation of the generated suite without executing against an app.

        Checks:
          - Playwright CLI can be invoked
          - Tests can be discovered (`--list`)
          - Config file exists

        This does NOT assert application behavior; it ensures the generated
        suite is structurally runnable.
        """
        import subprocess

        config_ts = test_dir / "playwright.config.ts"
        config_js = test_dir / "playwright.config.js"
        if not config_ts.exists() and not config_js.exists():
            print("   ❌ Static validation failed: playwright config file missing.")
            return False, {"kind": "config_missing", "headline": "playwright config missing"}

        # 1) Print Playwright version
        try:
            proc_ver = subprocess.run(
                ["npx", "playwright", "--version"],
                cwd=str(test_dir),
                capture_output=True,
                text=True,
            )
            if proc_ver.returncode == 0:
                ver = (proc_ver.stdout or proc_ver.stderr or "").strip()
                print(f"   ✅ Playwright available: {ver}")
            else:
                print("   ❌ Static validation failed: cannot run `npx playwright --version`.")
                summary = self._summarize_failure(proc_ver.stdout or "", proc_ver.stderr or "")
                self._print_failure_summary(summary)
                return False, summary
        except Exception as e:
            print(f"   ❌ Static validation failed: error invoking Playwright: {e}")
            return False, {"kind": "exception", "headline": str(e)}

        # 2) Test discovery (no execution)
        try:
            proc_list = subprocess.run(
                ["npx", "playwright", "test", "--list"],
                cwd=str(test_dir),
                capture_output=True,
                text=True,
            )
            if proc_list.returncode == 0:
                out = (proc_list.stdout or "").strip()
                # Print a compact success message; list output can be long.
                print("   ✅ Test discovery succeeded (`npx playwright test --list`).")
                if out:
                    # Heuristic: show only first few lines
                    lines = out.splitlines()
                    preview = "\n".join(lines[:6])
                    print("   ℹ️  Discovered tests (preview):")
                    for ln in preview.splitlines():
                        print(f"      {ln}")
                return True, None
            else:
                print("   ❌ Static validation failed: test discovery failed.")
                summary = self._summarize_failure(proc_list.stdout or "", proc_list.stderr or "")
                self._print_failure_summary(summary)

                # If we can provide a safe remediation message, do so (without spamming stack traces).
                if summary.get("kind") in ("deps_missing", "playwright_browsers_missing"):
                    print("   🛠 Suggested next steps:")
                    print(f"      cd {test_dir}")
                    print("      npm install")
                    print("      npx playwright install --with-deps")
                return False, summary
        except Exception as e:
            print(f"   ❌ Static validation failed: error during test discovery: {e}")
            return False, {"kind": "exception", "headline": str(e)}

    @staticmethod
    def _summarize_failure(stdout: str, stderr: str) -> Dict[str, str]:
        """
        Pull out the most useful signals from Playwright output.

        Phase 7 v2: Expanded pattern detection for better diagnostics.

        Supported kinds (in detection order):
          - deps_missing: Node module not found
          - playwright_browsers_missing: Browser executable missing
          - env_missing: Environment variable undefined
          - baseurl_invalid: Invalid BASE_URL format
          - timeout: Test or action timeout exceeded
          - network_error: Connection refused or network failure
          - auth_failure: 401/403 or auth-related error
          - element_not_found: Locator failed to find element
          - test_failures: Generic test assertion failure (fallback)
        """
        combined = "\n".join([stdout.strip(), stderr.strip()]).strip()
        combined_lower = combined.lower()
        summary: Dict[str, str] = {"raw": combined}

        # Detection order matters: more specific patterns first, generic last.

        # 1. Environment/setup issues (highest priority - must fix before tests can run)
        if "Cannot find module" in combined or "MODULE_NOT_FOUND" in combined:
            summary["kind"] = "deps_missing"
        elif "browserType.launch" in combined and "Executable doesn't exist" in combined:
            summary["kind"] = "playwright_browsers_missing"
        elif "process.env." in combined and "undefined" in combined:
            summary["kind"] = "env_missing"
        elif "baseURL" in combined and ("Invalid URL" in combined or "ERR_INVALID_URL" in combined):
            summary["kind"] = "baseurl_invalid"

        # 2. Network/connectivity issues
        elif any(p in combined for p in ("ERR_CONNECTION_REFUSED", "ECONNREFUSED", "net::ERR_")):
            summary["kind"] = "network_error"
        elif "ETIMEDOUT" in combined or "ENOTFOUND" in combined:
            summary["kind"] = "network_error"

        # 3. Auth failures (HTTP 401/403 or explicit auth errors)
        elif any(p in combined_lower for p in ("401", "403", "unauthorized", "forbidden")):
            # Verify it's an actual auth error, not just a test name
            if any(p in combined for p in ("status 401", "status 403", "HTTP 401", "HTTP 403", "Error: 401", "Error: 403")):
                summary["kind"] = "auth_failure"
            elif "unauthorized" in combined_lower or "forbidden" in combined_lower:
                summary["kind"] = "auth_failure"
            else:
                summary["kind"] = "test_failures"

        # 4. Timeout issues
        elif any(p in combined for p in ("TimeoutError", "Timeout exceeded", "Test timeout")):
            summary["kind"] = "timeout"
        elif "timeout" in combined_lower and ("exceeded" in combined_lower or "waiting" in combined_lower):
            summary["kind"] = "timeout"

        # 5. Element/locator not found
        elif any(p in combined for p in ("locator.click:", "locator.fill:", "waiting for locator")):
            summary["kind"] = "element_not_found"
        elif "strict mode violation" in combined_lower:
            summary["kind"] = "element_not_found"
        elif "no element matching" in combined_lower or "element not found" in combined_lower:
            summary["kind"] = "element_not_found"

        # 6. Generic test failures (fallback)
        else:
            summary["kind"] = "test_failures"

        # Try to extract a concise headline
        headline = ""
        for line in combined.splitlines():
            if "Error:" in line or "ERR_" in line or "Cannot find module" in line:
                headline = line.strip()
                break
            if "TimeoutError" in line or "timeout" in line.lower():
                headline = line.strip()
                break
        summary["headline"] = headline or "Playwright tests failed (see raw output)"
        return summary

    @staticmethod
    def _print_failure_summary(summary: Dict[str, str]) -> None:
        """Pretty-print failure summary."""
        print("   🔎 Failure summary:")
        print(f"      • kind: {summary.get('kind')}")
        print(f"      • headline: {summary.get('headline')}")

    def _apply_safe_fixes(self, test_dir: Path, summary: Dict[str, str]) -> bool:
        """
        Apply ONLY safe, non-behavior-changing fixes.

        Phase 7 v2: Expanded to handle new failure kinds with targeted diagnostics.

        Returns:
            True if any fix was applied, else False.
        """
        kind = summary.get("kind", "")

        if kind in ("deps_missing", "playwright_browsers_missing"):
            # We can't install deps in the sandbox reliably (network restrictions),
            # so we provide guidance only.
            print("   🛠 Safe fix suggestion:")
            print(f"      cd {test_dir}")
            print("      npm install")
            print("      npx playwright install --with-deps")
            return False

        if kind == "env_missing":
            env_example = test_dir / ".env.example"
            env_file = test_dir / ".env"
            if env_example.exists() and not env_file.exists():
                # Safe fix: create a .env by copying .env.example (still requires user to fill secrets)
                try:
                    env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
                    print("   🛠 Applied safe fix: created .env from .env.example (fill in credentials).")
                    return True
                except Exception as e:
                    print(f"   ⚠️  Failed to create .env from .env.example: {e}")
                    return False

            print("   🛠 Safe fix suggestion: Ensure required environment variables are set (.env).")
            return False

        if kind == "baseurl_invalid":
            env_example = test_dir / ".env.example"
            env_file = test_dir / ".env"
            # Safe fix: ensure a .env exists so baseURL can be set without touching code.
            if env_example.exists() and not env_file.exists():
                try:
                    env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
                    print("   🛠 Applied safe fix: created .env from .env.example (set BASE_URL).")
                    return True
                except Exception as e:
                    print(f"   ⚠️  Failed to create .env from .env.example: {e}")
                    return False
            print("   🛠 Safe fix suggestion: Set BASE_URL in .env to a valid absolute URL.")
            return False

        # Phase 7 v2: Expanded safe fix coverage for new failure kinds

        if kind == "timeout":
            # Safe diagnostic: print config guidance (no auto-edit)
            print("   🛠 Safe fix suggestion (timeout):")
            print("      Consider increasing timeout in playwright.config.ts:")
            print("      export default defineConfig({")
            print("        timeout: 60000, // 60 seconds")
            print("        expect: { timeout: 10000 },")
            print("      });")
            return False

        if kind == "network_error":
            # Safe diagnostic: attempt to check if BASE_URL is reachable
            base_url = self._get_env_value(test_dir, "BASE_URL")
            if base_url:
                print(f"   🔍 Checking if BASE_URL is reachable: {base_url}")
                try:
                    import urllib.request
                    import urllib.error
                    req = urllib.request.Request(base_url, method="HEAD")
                    req.add_header("User-Agent", "QualityForge-Validator/1.0")
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        print(f"   ✅ BASE_URL responded with status {resp.status}")
                        print("   🛠 Network error may be intermittent. Consider re-running.")
                except urllib.error.URLError as e:
                    print(f"   ❌ BASE_URL is not reachable: {e.reason}")
                    print("   🛠 Safe fix suggestion: Ensure the target app is running.")
                except Exception as e:
                    print(f"   ⚠️  Could not check BASE_URL: {e}")
            else:
                print("   🛠 Safe fix suggestion: Set BASE_URL in .env and ensure the app is running.")
            return False

        if kind == "auth_failure":
            # Safe diagnostic: remind about credentials (no auto-edit)
            print("   🛠 Safe fix suggestion (auth failure):")
            print("      1. Verify TEST_USER_EMAIL and TEST_USER_PASSWORD in .env")
            print("      2. Ensure the test account exists and is active")
            print("      3. Check if the auth flow matches the generated tests")
            return False

        if kind == "element_not_found":
            # Safe diagnostic: suggest headed mode for debugging
            print("   🛠 Safe fix suggestion (element not found):")
            print(f"      Run tests in headed mode to debug:")
            print(f"      cd {test_dir} && npx playwright test --headed")
            print("      Use --emit-locator-hints-seed to generate a seed file for better selectors.")
            return False

        # For generic test failures, we do not auto-edit.
        print("   🛠 No safe automated edits for this failure type.")
        return False

    def _write_validation_report(self, test_dir: Path, report: Dict) -> None:
        """
        Write validation-report.json into the generated suite directory.

        Important:
          - This report must not contain secrets.
          - We only store mode, base_url (safe), and error summaries.
        """
        try:
            if not test_dir.exists():
                return
            report_path = test_dir / "validation-report.json"
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"   📝 Validation report: {report_path.name}")
        except Exception:
            # Never fail generation/validation due to report writing.
            return


# ==============================================================================
# MAIN GENERATOR ORCHESTRATOR
# ==============================================================================

class PlaywrightGenerator:
    """
    Main orchestrator for Playwright test generation.
    
    Coordinates all components:
        1. Parse CSV files (CSVParser)
        2. Detect actions (ActionDetector)
        3. Generate tests (TestGenerator)
        4. Generate config (ConfigGenerator - Phase 4)
        5. Validate tests (Validator - Phase 7)
    """
    
    def __init__(
        self,
        test_jam_name: str,
        language: str = 'ts',
        locator_hints_path: Optional[str] = None,
    ):
        """
        Initialize generator.
        
        Args:
            test_jam_name: Name of test jam (e.g., '2026-01-12_streamlined-tx-template-management')
            language: 'ts' for TypeScript or 'js' for JavaScript
        
        Raises:
            ValueError: If inputs are invalid
            FileNotFoundError: If test jam directory not found
        """
        # Phase 6: Validate inputs before proceeding
        InputValidator.validate_test_jam_name(test_jam_name)
        InputValidator.validate_language(language)
        
        self.test_jam_name = test_jam_name
        self.language = language
        
        # Paths
        self.project_root = Path(__file__).parent.parent.parent
        # Core project location for runtime artifacts
        test_jam_path = self.project_root / "test-jams" / test_jam_name

        if test_jam_path.exists():
            self.test_jam_dir = test_jam_path
        else:
            raise FileNotFoundError(
                f"Test jam '{test_jam_name}' not found in:\n"
                f"  - {test_jam_path}\n\n"
                f"Note: `_project-dev/` is planning-only; test jams must live under `test-jams/`."
            )
        
        self.output_dir = self.test_jam_dir / "playwright-tests"

        self.locator_hints: Optional[LocatorHints] = None
        if locator_hints_path:
            try:
                p = Path(locator_hints_path).expanduser()
                if not p.is_absolute():
                    p = (Path.cwd() / p).resolve()
                if not p.exists():
                    raise FileNotFoundError(str(p))
                self.locator_hints = LocatorHints.load(p)
            except Exception as e:
                raise ValueError(
                    f"Failed to load --locator-hints JSON.\n"
                    f"Path: {locator_hints_path}\n"
                    f"Error: {e}"
                )
        
        # Components
        self.csv_parser = CSVParser(self.test_jam_dir)
        self.test_generator = TestGenerator(language, locator_hints=self.locator_hints)
        self.config_generator = ConfigGenerator(self.output_dir, language)  # Phase 4
        self.validator = Validator()
    
    def generate(
        self,
        validate: bool = False,
        validate_mode: str = "static",
        env_overrides: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Main generation workflow.
        
        Args:
            validate: Whether to run self-healing validation (Phase 7)
            validate_mode: Validation mode ("static" or "runtime"). See Validator.validate_and_fix.
            env_overrides: Optional env overrides to write into playwright-tests/.env (safe; file is gitignored)
        """
        print("🎭 Playwright Test Generator")
        print(f"Test Jam: {self.test_jam_name}")
        print(f"Language: {self.language.upper()}")
        print(f"Output: {self.output_dir}")
        print("")
        
        # Step 1: Parse CSV files
        print("📋 Step 1: Parsing CSV test cases...")
        test_cases = self.csv_parser.parse_all()
        self._log_parsing_statistics(test_cases)  # Phase 6: Enhanced logging
        print("")
        
        # Step 2: Group by component
        print("📦 Step 2: Grouping by component...")
        grouped = self._group_by_component(test_cases)
        print(f"✅ Grouped into {len(grouped)} components")
        for comp_name, comp_tests in grouped.items():
            print(f"   • {comp_name}: {len(comp_tests)} tests")
        print("")
        
        # Step 3: Generate test files
        print("🔧 Step 3: Generating Playwright tests...")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for component_name, component_tests in grouped.items():
            file_name = self._sanitize_filename(component_name) + self.test_generator.test_file_ext
            file_path = self.output_dir / file_name
            
            test_code = self.test_generator.generate_file(component_tests, component_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            print(f"  ✅ {file_name} ({len(component_tests)} tests)")
        
        print("")
        print(f"✅ Generated {len(grouped)} test files")
        print("")
        
        # Step 3.5: Generate .env.example (Phase 3)
        print("🔐 Step 3.5: Generating environment template...")
        env_example_created = self._generate_env_example(test_cases)
        if env_example_created:
            print("  ✅ .env.example")
        print("")
        
        # Step 4: Generate config files (Phase 4)
        print("⚙️ Step 4: Generating configuration files...")
        self.config_generator.generate_all()
        print("")

        # Step 4.5: Write .env (optional) for runtime validation / user convenience
        # Never logs secrets; writes to gitignored file in output directory.
        if env_overrides:
            self._write_env_overrides(env_overrides)
        
        # Step 5: Validate (Phase 7)
        if validate:
            print("🔍 Step 5: Running self-healing validation...")
            self.validator.validate_and_fix(self.output_dir, mode=validate_mode)
            print("")
        
        # Summary
        print("=" * 60)
        print("✅ Playwright Test Generation Complete!")
        print("=" * 60)
        print(f"📁 Location: {self.output_dir}")
        print(f"📊 Test Files: {len(grouped)}")
        print(f"📝 Test Cases: {len(test_cases)}")
        print("")
        print("🎯 Next Steps:")
        print("1. Review generated tests in playwright-tests/ folder")
        print("2. Install dependencies: cd playwright-tests && npm install")
        print("3. Run tests: npx playwright test")
        print("")

    def _write_env_overrides(self, env_overrides: Dict[str, str]) -> None:
        """
        Write/update playwright-tests/.env with provided overrides.

        This is intended to support runtime validation where the end user has a local
        Acme Platform (or relevant slice) running and wants tests to execute immediately.

        Notes:
          - We never print secret values.
          - `.env` is already gitignored by the generated suite.
        """
        env_path = self.output_dir / ".env"
        existing: Dict[str, str] = {}

        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()
            except Exception:
                # If parsing fails, we overwrite conservatively below.
                existing = {}

        # Merge (overrides win)
        merged = {**existing, **{k: v for k, v in env_overrides.items() if v is not None}}

        # Write file
        lines = ["# Auto-generated by QualityForge (do not commit secrets)"]
        for key in sorted(merged.keys()):
            value = merged[key]
            lines.append(f"{key}={value}")

        try:
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            keys_written = ", ".join(sorted(env_overrides.keys()))
            print(f"  ✅ .env updated ({keys_written})")
        except Exception as e:
            print(f"  ⚠️  Failed to write .env overrides: {e}")
    
    def _log_parsing_statistics(self, test_cases: List[TestCase]) -> None:
        """
        Log detailed statistics about parsed test cases.
        
        Phase 6: Quality Polish - Enhanced logging for better visibility.
        
        Args:
            test_cases: List of all parsed test cases
        """
        from collections import defaultdict
        
        print(f"✅ Parsed {len(test_cases)} test cases")
        
        # Category breakdown
        by_category = defaultdict(int)
        by_priority = defaultdict(int)
        total_steps = 0
        total_results = 0
        
        for tc in test_cases:
            by_category[tc.category] += 1
            by_priority[tc.priority] += 1
            # Count steps (rough estimate by newlines)
            total_steps += len(tc.test_steps.split('\n'))
            total_results += len(tc.expected_results.split('\n'))
        
        # Category breakdown
        if by_category:
            print(f"   📊 By Category:")
            for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
                percentage = (count / len(test_cases)) * 100
                print(f"      • {cat}: {count} tests ({percentage:.1f}%)")
        
        # Priority breakdown
        if by_priority:
            print(f"   🔥 By Priority:")
            for priority, count in sorted(by_priority.items()):
                percentage = (count / len(test_cases)) * 100
                print(f"      • {priority}: {count} tests ({percentage:.1f}%)")
        
        # Authentication detection
        precondition_analyzer = PreConditionAnalyzer()
        auth_count = sum(
            1 for tc in test_cases 
            if precondition_analyzer.analyze(tc.pre_conditions).requires_auth
        )
        if auth_count > 0:
            print(f"   🔐 Authentication:")
            print(f"      • {auth_count} tests require authentication")
            print(f"      • {len(test_cases) - auth_count} tests are public")
        
        # Complexity metrics
        avg_steps = total_steps / len(test_cases) if test_cases else 0
        avg_results = total_results / len(test_cases) if test_cases else 0
        print(f"   📈 Complexity:")
        print(f"      • Avg steps per test: {avg_steps:.1f}")
        print(f"      • Avg assertions per test: {avg_results:.1f}")
    
    def _generate_env_example(self, test_cases: List[TestCase]) -> bool:
        """
        Generate .env.example file with test account credentials template.
        
        Phase 3: Only generated if tests require authentication.
        
        Args:
            test_cases: All test cases (to check if auth is needed)
        """
        # Check if any tests require authentication
        precondition_analyzer = PreConditionAnalyzer()
        auth_required = any(
            precondition_analyzer.analyze(tc.pre_conditions).requires_auth 
            for tc in test_cases
        )
        
        if not auth_required:
            print("  ℹ️  No authentication required - skipping .env.example")
            return False
        
        env_content = """# Playwright Test Environment Variables
# Copy this file to .env and fill in your test account credentials

# Test Account Credentials
TEST_USER_EMAIL=your-test-email@example.com
TEST_USER_PASSWORD=your-test-password

# Application URL
BASE_URL=https://example.com

# Optional: API Keys (if needed for API tests)
# API_KEY=your-api-key

# Note: Never commit the actual .env file to version control!
# Add .env to your .gitignore file.
"""
        
        env_file_path = self.output_dir / ".env.example"
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        return True
    
    def _group_by_component(self, test_cases: List[TestCase]) -> Dict[str, List[TestCase]]:
        """Group test cases by component."""
        grouped = {}
        for test_case in test_cases:
            component = test_case.component or test_case.category or "General"
            if component not in grouped:
                grouped[component] = []
            grouped[component].append(test_case)
        return grouped
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert component name to valid filename."""
        # Remove special characters, replace spaces with hyphens
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[\s_]+', '-', sanitized)
        return sanitized.lower()


# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    """Command-line interface for the generator."""
    parser = argparse.ArgumentParser(
        description='Generate Playwright tests from test case CSV files'
    )

    # Either generate from a test jam OR validate/review an existing suite.
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '--test-jam',
        help='Test jam name (e.g., 2026-01-12_streamlined-tx-template-management)'
    )
    target_group.add_argument(
        '--validate-only',
        dest='validate_only_dir',
        help="Validate an existing generated suite directory (e.g., /path/to/playwright-tests). No regeneration."
    )
    target_group.add_argument(
        '--review-only',
        dest='review_only_path',
        help="Static review of a Playwright suite or spec file (no execution). Provide /path/to/playwright-tests or /path/to/file.spec.ts"
    )
    target_group.add_argument(
        '--emit-locator-hints-seed',
        dest='emit_locator_hints_seed_path',
        help="Generate locator-hints.seed.json from TODO steps in a suite/spec (no execution). Provide /path/to/playwright-tests or /path/to/file.spec.ts"
    )
    parser.add_argument(
        '--language',
        choices=['ts', 'js'],
        default='ts',
        help='Output language: ts (TypeScript) or js (JavaScript)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run self-healing validation after generation (Phase 7)'
    )
    parser.add_argument(
        '--locator-hints',
        default=None,
        help="Optional path to a locator-hints JSON file (typically produced via Playwright MCP) to improve locator accuracy and reduce TODOs."
    )
    parser.add_argument(
        '--repo-playwright-root',
        default=None,
        help="Optional path to a repo Playwright tests folder to mine candidate snippets when emitting locator-hints.seed.json."
    )
    parser.add_argument(
        '--validate-mode',
        choices=['static', 'runtime'],
        default='static',
        help="Validation mode: 'static' validates deps/config/test discovery; 'runtime' executes tests (requires target app via BASE_URL)"
    )
    parser.add_argument(
        '--validate-fix-level',
        choices=['conservative', 'aggressive'],
        default='conservative',
        help="Validation fix level. conservative = safe guidance/edits only; aggressive = opt-in stronger suggestions (no selector guessing)."
    )
    parser.add_argument(
        '--todo-policy',
        choices=['allow', 'warn', 'error'],
        default='allow',
        help="TODO policy for generated suites. allow=permit TODOs; warn=flag TODOs as high-severity; error=quality gate expects zero TODOs (for full-context users)."
    )

    # Optional env overrides for runtime validation convenience.
    # These are written into playwright-tests/.env (gitignored).
    parser.add_argument(
        '--base-url',
        default=None,
        help="Optional BASE_URL to write into playwright-tests/.env (recommended for --validate-mode runtime)"
    )
    parser.add_argument(
        '--test-user-email',
        default=None,
        help="Optional TEST_USER_EMAIL to write into playwright-tests/.env (only if auth tests are generated)"
    )
    parser.add_argument(
        '--test-user-password',
        default=None,
        help="Optional TEST_USER_PASSWORD to write into playwright-tests/.env (only if auth tests are generated)"
    )
    
    args = parser.parse_args()

    env_overrides = {}
    if args.base_url:
        env_overrides["BASE_URL"] = args.base_url
    if args.test_user_email:
        env_overrides["TEST_USER_EMAIL"] = args.test_user_email
    if args.test_user_password:
        env_overrides["TEST_USER_PASSWORD"] = args.test_user_password

    # Review-only mode: static best-practice review (no execution).
    if args.review_only_path:
        review_path = Path(args.review_only_path).expanduser()
        if not review_path.is_absolute():
            review_path = (Path.cwd() / review_path).resolve()
        suite_dir = review_path.parent if review_path.is_file() else review_path
        report = SpecReviewer().review_path(review_path)
        out = SpecReviewer.write_report(suite_dir=suite_dir, report=report)
        print("🔎 Playwright Spec Review Complete")
        print(f"📁 Location: {out}")
        print(f"📊 Specs: {report['stats']['spec_files']}, Tests: {report['stats']['tests']}")
        print(
            f"⚠️ Findings: {len(report['findings'])} "
            f"(high: {sum(1 for f in report['findings'] if f.get('severity') == 'high')}, "
            f"medium: {sum(1 for f in report['findings'] if f.get('severity') == 'medium')}, "
            f"low: {sum(1 for f in report['findings'] if f.get('severity') == 'low')})"
        )
        return

    # Emit locator hints seed (no execution).
    if args.emit_locator_hints_seed_path:
        seed_path = Path(args.emit_locator_hints_seed_path).expanduser()
        if not seed_path.is_absolute():
            seed_path = (Path.cwd() / seed_path).resolve()
        suite_dir = seed_path.parent if seed_path.is_file() else seed_path
        repo_root = None
        if args.repo_playwright_root:
            repo_root = Path(args.repo_playwright_root).expanduser()
            if not repo_root.is_absolute():
                repo_root = (Path.cwd() / repo_root).resolve()
        out, seed = SpecReviewer.emit_locator_hints_seed(seed_path, repo_playwright_root=repo_root)
        print("🧩 Locator Hints Seed Generated")
        print(f"📁 Location: {out}")
        print(f"📝 TODO steps extracted: {len(seed.get('step_overrides') or [])}")
        return

    # Validate-only mode: run Validator against an existing suite directory (or a single spec file).
    if args.validate_only_dir:
        validate_path = Path(args.validate_only_dir).expanduser()
        if not validate_path.is_absolute():
            validate_path = (Path.cwd() / validate_path).resolve()

        # Allow passing a single spec file path for convenience; treat its parent as the suite dir.
        # This keeps the UX simple for reviewers who only have a *.spec.ts file.
        if validate_path.is_file():
            if validate_path.name.endswith((".spec.ts", ".spec.js")):
                suite_dir = validate_path.parent
            else:
                raise ValueError(
                    f"--validate-only must be a Playwright suite directory or a single *.spec.ts/*.spec.js file.\n"
                    f"Got file: {validate_path}"
                )
        else:
            suite_dir = validate_path

        # Ensure we operate on an absolute resolved directory.
        suite_dir = suite_dir.resolve()
        if not suite_dir.is_absolute():
            suite_dir = (Path.cwd() / suite_dir).resolve()

        # Optionally write env overrides into suite_dir/.env (gitignored by generated suite).
        if env_overrides:
            env_path = suite_dir / ".env"
            existing: Dict[str, str] = {}
            if env_path.exists():
                try:
                    for line in env_path.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        existing[k.strip()] = v.strip()
                except Exception:
                    existing = {}

            merged = {**existing, **env_overrides}
            lines = ["# Auto-generated by QualityForge (do not commit secrets)"]
            for key in sorted(merged.keys()):
                lines.append(f"{key}={merged[key]}")
            try:
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                print(f"✅ .env updated ({', '.join(sorted(env_overrides.keys()))})")
            except Exception as e:
                print(f"⚠️  Failed to write .env overrides: {e}")

        # Run validation (static/runtime) and always emit validation-report.json
        print("🔍 Validating existing Playwright suite...")
        print(f"Suite: {suite_dir}")
        print(f"Mode: {args.validate_mode}")
        print("")
        Validator().validate_and_fix(
            suite_dir,
            mode=args.validate_mode,
            fix_level=args.validate_fix_level,
            todo_policy=args.todo_policy,
        )
        return

    # Default mode: generate from test jam (optional validate after generation).
    generator = PlaywrightGenerator(
        test_jam_name=args.test_jam,
        language=args.language,
        locator_hints_path=args.locator_hints,
    )

    generator.generate(
        validate=args.validate,
        validate_mode=args.validate_mode,
        env_overrides=env_overrides if env_overrides else None,
    )


if __name__ == '__main__':
    main()

