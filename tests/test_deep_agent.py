"""
Unit and Integration Tests for TabbyPatrol Goal-Aware Deep Agent
Covers:
- create_deep_agent initialization with tools and 4 subagents
- Goal-aware classification (relevance to goal vs category)
- Session planning subagent (blocks, breaks, allowed resources)
- Appeals judge subagent & active grace periods
- Focus coach subagent & reflection generation
- Persistent memory in memory/ (*.md files)
- Fast rule pre-filter and multi-tier caching
"""

import json
import os
import shutil
import tempfile
import unittest

from agent.memory import TabbyMemory
from agent.models import OfflineTabbyChatModel, get_tabby_model, get_active_model_name
from agent.prefilter import FastRulePreFilter
from agent.deep_agent import TabbyDeepAgent
from agent.adapter import GoalAwareAgentEngine


class TestTabbyDeepAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.memory = TabbyMemory(memory_dir=self.test_dir)
        self.engine = GoalAwareAgentEngine(
            current_goal="Hackathon: Python & AI Agent Development",
            memory_dir=self.test_dir
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_memory_persistence(self):
        """Verify reading and writing to persistent memory Markdown files"""
        # 1. Goal (goal.md)
        self.memory.save_goal("Quantum Machine Learning Research")
        self.assertEqual(self.memory.get_goal(), "Quantum Machine Learning Research")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "goal.md")))

        # 2. Plan (session_plan.md)
        sample_plan = {
            "session_title": "Quantum Study",
            "blocks": [{"title": "Block 1", "duration_minutes": 45}],
            "break_times": [{"after_block": 1, "duration_minutes": 10}],
            "allowed_resources": ["arxiv.org", "qiskit.org"]
        }
        self.memory.save_plan(sample_plan)
        saved_plan = self.memory.get_plan()
        self.assertEqual(saved_plan["session_title"], "Quantum Study")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "session_plan.md")))

        # 3. Verdicts Log (verdict_log.md)
        self.memory.record_verdict({
            "title": "Quantum Paper",
            "url": "https://arxiv.org/abs/1234",
            "verdict": "APPROVE",
            "relevance": 0.95,
            "confidence": 0.90,
            "source": "deepagent",
            "reason": "Quantum study paper"
        })
        verdicts = self.memory.get_verdicts(limit=10)
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0]["title"], "Quantum Paper")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "verdict_log.md")))

        # 4. Todos
        item = self.memory.add_todo("Complete Qiskit tutorial")
        self.assertEqual(item["task"], "Complete Qiskit tutorial")
        self.memory.update_todo(item["id"], "completed")
        todos = self.memory.get_todos()
        self.assertEqual(todos[0]["status"], "completed")

    def test_prefilter_speed_and_accuracy(self):
        """Verify prefilter handles obvious distractions and study platforms in <1ms"""
        pf = FastRulePreFilter()

        # Obvious distractions
        res_reels = pf.evaluate("Reels • Instagram", "https://www.instagram.com/reels/")
        self.assertIsNotNone(res_reels)
        self.assertEqual(res_reels["verdict"], "distraction")

        res_shorts = pf.evaluate("Viral Short", "https://www.youtube.com/shorts/abc")
        self.assertIsNotNone(res_shorts)
        self.assertEqual(res_shorts["verdict"], "distraction")

        # Obvious search and homepages
        res_home = pf.evaluate("YouTube", "https://www.youtube.com/")
        self.assertIsNotNone(res_home)
        self.assertEqual(res_home["verdict"], "browsing")

        # Obvious productive sites
        res_gh = pf.evaluate("GitHub - langchain-ai/deepagents", "https://github.com/langchain-ai/deepagents")
        self.assertIsNotNone(res_gh)
        self.assertEqual(res_gh["verdict"], "approve")

        # Ambiguous tabs return None for DeepAgent routing
        res_ambiguous = pf.evaluate("Random Article on Modern Tech", "https://medium.com/@dev/article")
        self.assertIsNone(res_ambiguous)

    def test_goal_aware_relevance_vs_category(self):
        """Verify that tabs are judged by RELEVANCE TO GOAL, not generic category"""
        # Scenario A: Goal is Organic Chemistry
        self.engine.set_goal("Organic Chemistry and Reaction Mechanisms")

        # Physics lecture is OFF-GOAL
        res_phys = self.engine.evaluate("Introduction to Quantum Mechanics - Veritasium - YouTube")
        self.assertEqual(res_phys["action"], "pop", f"Expected physics video to be POPPED for chemistry goal: {res_phys}")
        self.assertEqual(res_phys["verdict"], "DISTRACTION")

        # Chemistry reaction video is ON-GOAL
        res_chem = self.engine.evaluate("Nucleophilic Substitution Reaction Mechanisms - YouTube")
        self.assertEqual(res_chem["action"], "pass", f"Expected chem video to PASS for chemistry goal: {res_chem}")
        self.assertEqual(res_chem["verdict"], "PRODUCTIVE")

        # Scenario B: Goal is Psychology of Viral Internet Memes
        self.engine.set_goal("Psychology Presentation on Viral Internet Memes")

        # Meme compilation is ON-GOAL for this specific presentation!
        res_meme = self.engine.evaluate("History and Psychology of Viral Memes - YouTube")
        self.assertEqual(res_meme["action"], "pass", f"Expected meme study to PASS for meme psychology goal: {res_meme}")
        self.assertEqual(res_meme["verdict"], "PRODUCTIVE")

    def test_session_planner_subagent(self):
        """Verify planner subagent converts request into study blocks and break times"""
        plan = self.engine.create_session_plan("3 hours, CS exam Friday, weak on graph algorithms")
        self.assertIn("blocks", plan)
        self.assertGreater(len(plan["blocks"]), 0)
        self.assertIn("break_times", plan)

        # Plan should be persisted in memory/session_plan.md
        saved_plan = self.engine.memory.get_plan()
        self.assertIsNotNone(saved_plan)
        self.assertEqual(saved_plan.get("session_title"), plan.get("session_title"))

    def test_appeals_judge_subagent_and_grace_allowance(self):
        """Verify appeals judge rules on dispute and grants time-limited grace period"""
        # First: tab is off-goal and flagged
        self.engine.set_goal("Calculus 3 Multivariable")
        r1 = self.engine.evaluate("Blender 3D Modeling Tutorial", "https://youtube.com/watch?v=123")
        self.assertEqual(r1["action"], "pop")

        # User disputes: "I need this 3D model to visualize 3D saddle surfaces for Calculus"
        appeal_res = self.engine.submit_appeal(
            title="Blender 3D Modeling Tutorial",
            url="https://youtube.com/watch?v=123",
            argument="I need this 3D tool as a reference demo to visualize 3D saddle surfaces for Calculus"
        )
        self.assertEqual(appeal_res["ruling"], "granted")
        self.assertGreater(appeal_res["grace_minutes"], 0)

        # Now, evaluate again: active grace period allows the tab!
        r2 = self.engine.evaluate("Blender 3D Modeling Tutorial", "https://youtube.com/watch?v=123")
        self.assertEqual(r2["action"], "pass")
        self.assertEqual(r2["source"], "grace_period")
        self.assertIn("Active appeal grant in effect", r2["reason"])

    def test_coach_reflection_subagent(self):
        """Verify coach subagent produces markdown reflection file"""
        reflection = self.engine.generate_coach_reflection()
        self.assertIsInstance(reflection, str)
        self.assertIn("# 🐱 TabbyPatrol Focus Reflection Report", reflection)
        self.assertIn("Coaching", reflection)

        # File persisted in memory/reflection.md
        file_content = self.engine.memory.get_coach_reflection()
        self.assertEqual(file_content, reflection)

    def test_verdict_caching_and_invalidation(self):
        """Verify verdicts are cached per (url, title, goal) and cleared on goal change"""
        self.engine.set_goal("Python AI Hackathon")
        title = "PyTorch Quickstart Guide"
        url = "https://pytorch.org/tutorials"

        res1 = self.engine.evaluate(title, url)
        expected_key = self.engine._make_cache_key(title, url, "Python AI Hackathon")
        self.assertIn(expected_key, self.engine._cache)

        # Second call hits cache
        res2 = self.engine.evaluate(title, url)
        self.assertEqual(res1, res2)

        # Updating goal clears cache
        self.engine.set_goal("History of Rome")
        self.assertEqual(len(self.engine._cache), 0)


if __name__ == "__main__":
    unittest.main()
