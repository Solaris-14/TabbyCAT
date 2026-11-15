"""
Unit Tests for TabbyPatrol Fail-Safe Safeguards
Verifies:
1. error => no close (fail-open)
2. unknown verdict => no close (fail-open)
3. low confidence (< 0.8) => no close (fail-open)
4. mismatch between classified and active tab => no close
5. rate limit (30s) and session limit (5) enforced
6. dry run mode (TABBY_DRY_RUN=1) never calls physical close function
7. allowlisted domains and protected tabs (first, pinned, last) never closed
"""

import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "overlay")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.adapter import GoalAwareAgentEngine
from ai_agent import AiTabGuardAgent


class TestFailSafeSafeguards(unittest.TestCase):
    def setUp(self):
        os.environ["TABBY_DRY_RUN"] = "1"
        self.agent = AiTabGuardAgent(enable_hotkey=False)
        self.engine = GoalAwareAgentEngine(current_goal="Hackathon: Python & AI Agent Development")

    def test_error_fails_open_no_close(self):
        """1. Error or exception during evaluation => fail open to 'browse', no close"""
        res = self.engine._format_verdict(
            verdict="error: network timeout",
            relevance=0.0,
            confidence=0.0,
            reason="API timeout or connection refused",
            topic="Error",
            source="error_handler",
            title="Some Tab",
            url="https://example.com"
        )
        self.assertEqual(res["action"], "browse")
        self.assertEqual(res["verdict"], "BROWSING")
        self.assertTrue(res["is_productive"])

        target = {
            "title": "Some Tab",
            "url": "https://example.com",
            "analysis": res,
            "hwnd": 1234
        }
        closed = self.agent.execute_tab_close(target)
        self.assertFalse(closed)

    def test_unknown_verdict_fails_open_no_close(self):
        """2. Unknown verdict string => fail open to 'browse', no close"""
        unknown_verdicts = ["unknown", "neutral", "unclear", "maybe", "", None, 123]
        for uv in unknown_verdicts:
            res = self.engine._format_verdict(
                verdict=uv,
                relevance=0.5,
                confidence=0.5,
                reason="Unknown verdict",
                topic="General",
                source="test",
                title="Unknown Tab",
                url="https://example.com"
            )
            self.assertEqual(res["action"], "browse", f"Failed for verdict '{uv}': {res}")
            self.assertEqual(res["verdict"], "BROWSING")

            target = {
                "title": "Unknown Tab",
                "url": "https://example.com",
                "analysis": res,
                "hwnd": 1234
            }
            closed = self.agent.execute_tab_close(target)
            self.assertFalse(closed)

    def test_low_confidence_fails_open_no_close(self):
        """3. Distraction verdict with low confidence (< 0.8) => fail open to 'browse', no close"""
        low_confidences = [0.79, 0.70, 0.50, 0.20, 0.0]
        for conf in low_confidences:
            res = self.engine._format_verdict(
                verdict="distraction",
                relevance=0.1,
                confidence=conf,
                reason="Possible distraction but uncertain",
                topic="Entertainment",
                source="deepagent",
                title="Ambiguous Clip",
                url="https://example.com/clip"
            )
            self.assertEqual(res["action"], "browse", f"Failed for confidence {conf}: {res}")
            self.assertEqual(res["verdict"], "BROWSING")

            target = {
                "title": "Ambiguous Clip",
                "url": "https://example.com/clip",
                "analysis": res,
                "hwnd": 1234
            }
            closed = self.agent.execute_tab_close(target)
            self.assertFalse(closed)

    def test_mismatch_classified_active_tab_no_close(self):
        """4. Active tab title mismatch immediately before close => abort close"""
        self.agent.enforcement_enabled = True
        os.environ["TABBY_DRY_RUN"] = "0"
        self.agent.force_foreground_window = MagicMock(return_value=True)
        self.agent.send_ctrl_w_input = MagicMock(return_value=True)

        target = {
            "hwnd": 12345,
            "title": "MrBeast Extreme Challenge - YouTube",
            "url": "https://youtube.com/watch?v=123",
            "analysis": {
                "verdict": "DISTRACTION",
                "confidence": 0.95,
                "reason": "Pure viral entertainment stunt",
                "action": "pop"
            }
        }

        self.agent._query_all_tabs = MagicMock(return_value=(
            "https://github.com/project",
            [{"name": "GitHub - TabbyPatrol Code Review - Google Chrome", "selected": True}]
        ))

        with patch("ai_agent.user32") as mock_user32:
            mock_user32.IsWindow.return_value = True

            def mock_get_window_text(hwnd, buf, max_len):
                buf.value = "GitHub - TabbyPatrol Code Review - Google Chrome"
                return len(buf.value)

            mock_user32.GetWindowTextLengthW.return_value = len("GitHub - TabbyPatrol Code Review - Google Chrome")
            mock_user32.GetWindowTextW.side_effect = mock_get_window_text

            closed = self.agent.execute_tab_close(target)
            self.assertFalse(closed, "Expected close to abort due to tab title mismatch!")
            self.agent.send_ctrl_w_input.assert_not_called()

    def test_rate_limit_and_session_limit_enforced(self):
        """5. Rate limit (30s) and session limit (5) enforced"""
        self.agent.enforcement_enabled = True
        self.agent.cooldown_seconds = 30.0
        os.environ["TABBY_DRY_RUN"] = "0"
        self.agent.force_foreground_window = MagicMock(return_value=True)
        self.agent.send_ctrl_w_input = MagicMock(return_value=True)

        self.agent._query_all_tabs = MagicMock(side_effect=lambda hwnd, select_tab_name="": (
            "https://youtube.com/watch?v=meme",
            []
        ))

        target = {
            "hwnd": 12345,
            "title": "Viral Meme Video - YouTube",
            "url": "https://youtube.com/watch?v=meme",
            "analysis": {
                "verdict": "DISTRACTION",
                "confidence": 0.95,
                "reason": "Off-goal entertainment",
                "action": "pop"
            }
        }

        with patch("ai_agent.user32") as mock_user32:
            mock_user32.IsWindow.return_value = True

            def mock_get_window_text(hwnd, buf, max_len):
                buf.value = "Viral Meme Video - YouTube"
                return len(buf.value)

            mock_user32.GetWindowTextLengthW.return_value = len("Viral Meme Video - YouTube")
            mock_user32.GetWindowTextW.side_effect = mock_get_window_text

            # Shot 1: Should succeed
            closed1 = self.agent.execute_tab_close(target)
            self.assertTrue(closed1)
            self.assertEqual(self.agent.swat_count, 1)

            # Shot 2 (immediate, within 30s): MUST BE BLOCKED BY RATE LIMIT
            closed2 = self.agent.execute_tab_close(target)
            self.assertFalse(closed2, "Expected rate limit to block second close within 30s")

            # Advance time past 30s rate limit to test session limit
            self.agent.last_swat_time = time.time() - 35.0

            # Execute up to 5 closes
            for i in range(2, 6):
                self.agent.last_swat_time = time.time() - 35.0
                c = self.agent.execute_tab_close(target)
                self.assertTrue(c)

            self.assertEqual(self.agent.swat_count, 5)
            # Session limit reached: enforcement must be auto-disabled!
            self.assertFalse(self.agent.enforcement_enabled)

            # Shot 6: MUST BE BLOCKED BY SESSION LIMIT
            self.agent.last_swat_time = time.time() - 35.0
            closed6 = self.agent.execute_tab_close(target)
            self.assertFalse(closed6, "Expected session limit to block 6th close")

    def test_dry_run_never_calls_close_function(self):
        """6. DRY_RUN mode (TABBY_DRY_RUN=1, default) never dispatches physical close"""
        os.environ["TABBY_DRY_RUN"] = "1"
        self.agent = AiTabGuardAgent(enable_hotkey=False)
        self.agent.enforcement_enabled = True
        self.agent.force_foreground_window = MagicMock(return_value=True)
        self.agent.send_ctrl_w_input = MagicMock(return_value=True)

        target = {
            "hwnd": 12345,
            "title": "Viral Shorts Challenge - YouTube",
            "url": "https://youtube.com/shorts/xyz",
            "analysis": {
                "verdict": "DISTRACTION",
                "confidence": 0.99,
                "reason": "Shorts distraction",
                "action": "pop"
            }
        }

        with patch("ai_agent.user32") as mock_user32:
            mock_user32.IsWindow.return_value = True

            def mock_get_window_text(hwnd, buf, max_len):
                buf.value = "Viral Shorts Challenge - YouTube"
                return len(buf.value)

            mock_user32.GetWindowTextLengthW.return_value = len("Viral Shorts Challenge - YouTube")
            mock_user32.GetWindowTextW.side_effect = mock_get_window_text

            closed = self.agent.execute_tab_close(target)
            self.assertFalse(closed)
            self.agent.send_ctrl_w_input.assert_not_called()

    def test_allowlist_and_protected_tabs_never_closed(self):
        """7. Allowlisted domains, first tab, pinned tabs, and last remaining tab never closed"""
        self.agent.enforcement_enabled = True
        os.environ["TABBY_DRY_RUN"] = "0"
        self.agent.force_foreground_window = MagicMock(return_value=True)
        self.agent.send_ctrl_w_input = MagicMock(return_value=True)

        protected_cases = [
            {"title": "Google Docs - Architecture Design", "url": "https://docs.google.com/document/d/123"},
            {"title": "GitHub - langchain-ai/deepagents: Deep agents", "url": "https://github.com/langchain-ai/deepagents"},
            {"title": "Localhost Development Server", "url": "http://localhost:3000/"},
            {"title": "Python Documentation", "url": "https://docs.python.org/3/library/"},
            {"title": "Some Tab", "url": "https://random.com", "is_first_tab": True},
            {"title": "Pinned Web App", "url": "https://random.com", "is_pinned": True},
            {"title": "Last Remaining Tab", "url": "https://random.com", "is_last_tab": True}
        ]

        with patch("ai_agent.user32") as mock_user32:
            mock_user32.IsWindow.return_value = True
            for pt in protected_cases:
                pt["hwnd"] = 12345
                pt["analysis"] = {
                    "verdict": "DISTRACTION",
                    "confidence": 0.95,
                    "reason": "Test distraction",
                    "action": "pop"
                }
                closed = self.agent.execute_tab_close(pt)
                self.assertFalse(closed, f"Protected tab was closed! Case: {pt}")
                self.agent.send_ctrl_w_input.assert_not_called()

    def test_fuzzy_match_passes_for_changed_titles(self):
        """Fuzzy match passes for changed/badge titles and host matching"""
        matched, score, desc = self.agent.fuzzy_tab_match(
            classified_title="Instagram",
            classified_url="https://www.instagram.com/",
            active_title="(2) Instagram - Google Chrome",
            active_url="https://www.instagram.com/"
        )
        self.assertTrue(matched)
        self.assertGreaterEqual(score, 0.60)

        matched, score, desc = self.agent.fuzzy_tab_match(
            classified_title="MrBeast - 100 Days Challenge - YouTube",
            classified_url="https://www.youtube.com/watch?v=100days",
            active_title="100 Days In Solitary Circle - YouTube",
            active_url="https://www.youtube.com/watch?v=100days"
        )
        self.assertTrue(matched)
        self.assertGreaterEqual(score, 0.60)

        matched, score, desc = self.agent.fuzzy_tab_match(
            classified_title="Reddit",
            classified_url="https://www.reddit.com/r/memes",
            active_title="Hot Posts in r/memes - Microsoft Edge",
            active_url="https://www.reddit.com/r/memes/"
        )
        self.assertTrue(matched)
        self.assertGreaterEqual(score, 0.60)

    def test_fuzzy_match_aborts_for_different_tab(self):
        """Fuzzy match aborts when foreground tab is switched to a completely different tab"""
        matched, score, desc = self.agent.fuzzy_tab_match(
            classified_title="Instagram - Reels",
            classified_url="https://www.instagram.com/reels/xyz",
            active_title="Python Asyncio Documentation - Google Chrome",
            active_url="https://docs.python.org/3/library/asyncio.html"
        )
        self.assertFalse(matched)
        self.assertLess(score, 0.60)

    def test_close_verified_after_ctrl_w(self):
        """UI Automation verification: close succeeds when tab is gone, fails if still present"""
        self.agent.enforcement_enabled = True
        os.environ["TABBY_DRY_RUN"] = "0"
        self.agent.force_foreground_window = MagicMock(return_value=True)
        self.agent.send_ctrl_w_input = MagicMock(return_value=True)

        target = {
            "hwnd": 12345,
            "title": "Cat Fails 2026 - YouTube",
            "url": "https://youtube.com/watch?v=cat",
            "analysis": {"verdict": "DISTRACTION", "confidence": 0.98, "reason": "Distraction", "action": "pop"}
        }

        # Case A: Tab confirmed removed after Ctrl+W -> returns True
        self.agent._query_all_tabs = MagicMock(side_effect=[
            ("https://youtube.com/watch?v=cat", [{"name": "Cat Fails 2026 - YouTube", "selected": True}]),
            ("", [{"name": "Python Asyncio Docs", "selected": True}])
        ])

        with patch("ai_agent.user32") as mock_user32:
            mock_user32.IsWindow.return_value = True
            closed = self.agent.execute_tab_close(target)
            self.assertTrue(closed)
            self.agent.send_ctrl_w_input.assert_called_once()

        # Case B: Tab remains present in tabstrip after Ctrl+W -> verification fails, returns False
        self.agent.last_swat_time = time.time() - 35.0
        self.agent.send_ctrl_w_input.reset_mock()
        self.agent._query_all_tabs = MagicMock(side_effect=[
            ("https://youtube.com/watch?v=cat", [{"name": "Cat Fails 2026 - YouTube", "selected": True}]),
            ("https://youtube.com/watch?v=cat", [{"name": "Cat Fails 2026 - YouTube", "selected": True}])
        ])

        with patch("ai_agent.user32") as mock_user32:
            mock_user32.IsWindow.return_value = True
            closed_fail = self.agent.execute_tab_close(target)
            self.assertFalse(closed_fail)

    def test_mrbeast_and_entertainment_youtube_classified_as_distraction(self):
        """MrBeast and viral entertainment challenge videos are flagged as distraction"""
        test_cases = [
            ("MrBeast - $10,000 Every Day You Survive In The Wilderness - YouTube", "https://www.youtube.com/watch?v=wilderness"),
            ("I Spent 7 Days In Solitary Confinement - YouTube", "https://www.youtube.com/watch?v=solitary"),
            ("$1 vs $1,000,000 Hotel Room! - YouTube", "https://www.youtube.com/watch?v=hotel"),
            ("Survive 100 Days In Circle, Win $500,000 - YouTube", "https://www.youtube.com/watch?v=circle"),
            ("Ages 1 - 100 Fight For $500,000 - YouTube", "https://www.youtube.com/watch?v=fight"),
            ("Extreme Hide And Seek For $100,000 - YouTube", "https://www.youtube.com/watch?v=hideseek"),
        ]

        for title, url in test_cases:
            res = self.engine.evaluate(title, url)
            self.assertEqual(res["verdict"], "DISTRACTION", f"Failed for {title}: {res}")
            self.assertEqual(res["action"], "pop", f"Failed for {title}: {res}")
            self.assertGreaterEqual(float(res["confidence"]), 0.80)


if __name__ == "__main__":
    unittest.main()
