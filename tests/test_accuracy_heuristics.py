"""Unit tests for H1/H2 accuracy heuristics (AC1/AC2)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "qualityforge"))

from test_jam_accuracy import (  # noqa: E402
    AccuracyAnalyzer,
    detect_brittle_locator_syntax,
    detect_terminal_action_without_outcome,
    detect_vagueness,
    has_observable_outcome_marker,
    has_terminal_action_verb,
)


class TestH1TerminalActionWithoutOutcome(unittest.TestCase):
    """AC1 — terminal action requires observable paired expected outcome."""

    def test_flags_click_with_empty_last_expected(self):
        steps = "1. Open settings\n2. Click Save"
        results = "1. Settings page displays\n2."
        self.assertTrue(detect_terminal_action_without_outcome(steps, results))

    def test_flags_submit_with_vague_last_expected(self):
        steps = "1. Fill form\n2. Submit the form"
        results = "1. Form is filled\n2. Works as expected"
        self.assertTrue(detect_terminal_action_without_outcome(steps, results))
        self.assertTrue(detect_vagueness("Works as expected"))

    def test_flags_tap_without_observable_marker(self):
        steps = "1. Tap Continue"
        results = "1. User proceeds"
        self.assertTrue(detect_terminal_action_without_outcome(steps, results))

    def test_does_not_flag_tc001_credit_balance_decrements(self):
        """Canonical TC-001: observable 'decrements' must suppress H1."""
        steps = "1. Purchase credits\n2. Confirm purchase"
        results = "1. Checkout completes\n2. Credit balance decrements"
        self.assertFalse(detect_terminal_action_without_outcome(steps, results))
        self.assertTrue(has_observable_outcome_marker("Credit balance decrements"))

    def test_does_not_flag_when_last_expected_is_observable(self):
        steps = "1. Click Export"
        results = "1. Export modal appears\n2. File download completes"
        self.assertFalse(detect_terminal_action_without_outcome(steps, results))

    def test_does_not_flag_non_terminal_last_step(self):
        steps = "1. Navigate to billing\n2. Review invoice details"
        results = "1. Billing page displays\n2."
        self.assertFalse(detect_terminal_action_without_outcome(steps, results))

    def test_blank_expected_results_skips_h1(self):
        steps = "1. Click Delete"
        results = ""
        self.assertFalse(detect_terminal_action_without_outcome(steps, results))

    def test_enter_field_step_not_terminal(self):
        self.assertFalse(has_terminal_action_verb("Enter valid phone number"))
        self.assertFalse(has_terminal_action_verb("Enter email in the email field"))

    def test_enter_with_observable_outcome_no_h1(self):
        steps = "1. Enter valid phone number\n2. Click Send"
        results = "1. Phone field accepts input\n2. Confirmation message appears"
        self.assertFalse(detect_terminal_action_without_outcome(steps, results))

    def test_misaligned_counts_observable_last_result_no_h1(self):
        steps = "1. Open app\n2. Click Submit"
        results = "1. Confirmation modal appears"
        self.assertFalse(detect_terminal_action_without_outcome(steps, results))

    def test_misaligned_counts_weak_last_result_fires_h1(self):
        steps = "1. Open app\n2. Click Submit"
        results = "1. Page loads"
        self.assertTrue(detect_terminal_action_without_outcome(steps, results))


class TestH2BrittleLocatorSyntax(unittest.TestCase):
    """AC2 — brittle locator patterns; plain English clicks are allowed."""

    def test_flags_xpath(self):
        self.assertTrue(detect_brittle_locator_syntax("Click xpath=//button[@id='save']"))

    def test_flags_nth_child(self):
        self.assertTrue(detect_brittle_locator_syntax("Select nth-child(2) in list"))

    def test_flags_css_prefix(self):
        self.assertTrue(detect_brittle_locator_syntax("Click css=.btn-primary"))

    def test_flags_css_module_class(self):
        self.assertTrue(detect_brittle_locator_syntax("Tap .css-1a2b3c4"))

    def test_flags_class_attribute_selector(self):
        self.assertTrue(detect_brittle_locator_syntax("Click [class=submit]"))

    def test_flags_xpath_div(self):
        self.assertTrue(detect_brittle_locator_syntax("Press //div[contains(text(),'OK')]"))

    def test_flags_xpath_span(self):
        self.assertTrue(detect_brittle_locator_syntax("Click //span[@role='button']"))

    def test_flags_data_testid_sole(self):
        self.assertTrue(detect_brittle_locator_syntax("data-testid=checkout-submit"))

    def test_allows_plain_english_button_click(self):
        self.assertFalse(detect_brittle_locator_syntax("Click the Save button"))
        self.assertFalse(detect_brittle_locator_syntax("Select the first row in the table"))
        self.assertFalse(detect_brittle_locator_syntax("Press Continue on the confirmation dialog"))


class TestAnalyzeQuickIntegration(unittest.TestCase):
    """B5 — analyze_quick emits H1 on a minimal jam-shaped row."""

    def test_analyze_quick_emits_h1_for_terminal_without_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            jam_dir = repo / "test-jams" / "h1_fixture"
            jam_dir.mkdir(parents=True)
            (jam_dir / "testjam_all_test_cases.csv").write_text(
                "Test Case ID,Test Name,Test Steps,Expected Results\n"
                'TC-H1-1,Save flow,"1. Click Save","1. Works as expected"\n',
                encoding="utf-8",
            )
            analyzer = AccuracyAnalyzer(repo_root=repo)
            report = analyzer.analyze_quick(jam_dir)
            h1 = [
                f
                for f in report["findings"]
                if "terminal action" in f.get("issue", "").lower()
            ]
            self.assertEqual(len(h1), 1)
            self.assertEqual(h1[0]["severity"], "medium")
            self.assertEqual(h1[0]["test_id"], "TC-H1-1")

    def test_analyze_quick_skips_h1_when_expected_results_blank(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            jam_dir = repo / "test-jams" / "h1_blank"
            jam_dir.mkdir(parents=True)
            (jam_dir / "testjam_all_test_cases.csv").write_text(
                "Test Case ID,Test Name,Test Steps,Expected Results\n"
                'TC-H1-2,Delete flow,"1. Click Delete",""\n',
                encoding="utf-8",
            )
            analyzer = AccuracyAnalyzer(repo_root=repo)
            report = analyzer.analyze_quick(jam_dir)
            h1 = [
                f
                for f in report["findings"]
                if "terminal action" in f.get("issue", "").lower()
            ]
            self.assertEqual(h1, [])
            missing = [f for f in report["findings"] if "Missing Expected Results" in f.get("issue", "")]
            self.assertEqual(len(missing), 1)


if __name__ == "__main__":
    unittest.main()
