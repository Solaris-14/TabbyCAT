"""
Automated Unit Tests for TabbyPatrol
Verifies sprite generation, pillow scaling, AI agent CV scanning, intelligent task classification, and overlay initialization.
"""

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "overlay")))

from cat_sprites import create_cat_frame
from pillow_sprites import create_pillow_sprite, create_pillow_with_cat
from ai_agent import AiTabGuardAgent
from tab_recognizer import TabContentRecognizer


class TestTabbyPatrol(unittest.TestCase):
    def test_cat_sprites_generation(self):
        """Verify that all cat states and directional flips generate valid images"""
        states = ["idle", "walk", "alert", "hammer_windup", "hammer_slam", "hammer_rest"]
        for st in states:
            im_r = create_cat_frame(st, 0, facing_right=True, scale=1.35)
            im_l = create_cat_frame(st, 0, facing_right=False, scale=1.35)
            self.assertIsNotNone(im_r)
            self.assertIsNotNone(im_l)
            self.assertEqual(im_r.size, im_l.size)
            self.assertEqual(im_r.mode, "RGBA")

    def test_pillow_sprites_generation(self):
        """Verify pillow themes and cat-on-pillow composites"""
        for theme in ["pink", "lavender", "mint"]:
            im_pillow = create_pillow_sprite(color_theme=theme, scale=1.35)
            self.assertIsNotNone(im_pillow)
            self.assertEqual(im_pillow.mode, "RGBA")

            for act in ["sleep", "sit", "knead", "sniper_aim", "sniper_fire", "sniper_chamber", "sniper_smug"]:
                comp = create_pillow_with_cat(act, 0, color_theme=theme, scale=1.35)
                self.assertIsNotNone(comp)
                self.assertEqual(comp.mode, "RGBA")

    def test_sniper_actions_both_directions(self):
        """Verify sniper sprite generation facing both left and right"""
        for act in ["sniper_aim", "sniper_fire", "sniper_chamber", "sniper_smug"]:
            for facing_left in [True, False]:
                comp = create_pillow_with_cat(act, 0, color_theme="pink", facing_left=facing_left, scale=1.35)
                self.assertIsNotNone(comp)
                self.assertEqual(comp.size, (108, 75))

    def test_ai_agent_rules(self):
        """Verify AI Agent rule management and keyword filtering"""
        agent = AiTabGuardAgent()
        self.assertTrue("youtube" in agent.blocked_keywords)
        self.assertTrue("reddit" in agent.blocked_keywords)

        # Test adding custom rule
        agent.add_keyword("procrastinate.com")
        self.assertTrue("procrastinate.com" in agent.blocked_keywords)

        # Test removing rule
        agent.remove_keyword("procrastinate.com")
        self.assertFalse("procrastinate.com" in agent.blocked_keywords)

    def test_ai_agent_thoughts(self):
        """Verify AI cognitive thought logging"""
        agent = AiTabGuardAgent()
        latest = agent.get_latest_thought()
        self.assertIn("AI Tab Guard Agent", latest)

    def test_task_classification_productive_vs_wasteful(self):
        """Verify differentiation between PRODUCTIVE TASKS and WASTEFUL TASKS across monitored domains"""
        rec = TabContentRecognizer()

        # 1. Educational YouTube Video -> PRODUCTIVE TASK
        yt_edu = rec.analyze_tab("MIT 6.006 Lecture 1: Algorithms - YouTube")
        self.assertEqual(yt_edu["task_type"], "PRODUCTIVE")
        self.assertFalse(yt_edu["is_distraction"])
        self.assertIn("Algorithms", yt_edu["topic"])
        self.assertIn("Educational", yt_edu["about"])

        # 2. Funny / Entertainment / Clickbait YouTube Video -> WASTEFUL TASK
        yt_fun = rec.analyze_tab("Try Not To Laugh Challenge 2026 (Funny Fails) - YouTube")
        self.assertEqual(yt_fun["task_type"], "WASTEFUL")
        self.assertTrue(yt_fun["is_distraction"])

        yt_beast = rec.analyze_tab("I Spent 7 Days In Solitary Confinement - YouTube")
        self.assertEqual(yt_beast["task_type"], "WASTEFUL")
        self.assertTrue(yt_beast["is_distraction"])

        # 3. YouTube Shorts -> WASTEFUL TASK
        yt_shorts = rec.analyze_tab("Viral Shorts", "https://youtube.com/shorts/123")
        self.assertEqual(yt_shorts["task_type"], "WASTEFUL")
        self.assertTrue(yt_shorts["is_distraction"])

        # 4. Instagram Reels -> WASTEFUL TASK
        ig_reels = rec.analyze_tab("Instagram", "https://instagram.com/reels")
        self.assertEqual(ig_reels["task_type"], "WASTEFUL")
        self.assertTrue(ig_reels["is_distraction"])

        # 5. Reddit Advice & Career Discussions -> PRODUCTIVE TASK
        rd_advice = rec.analyze_tab("r/Advice - Best study advice for college exams - Reddit")
        self.assertEqual(rd_advice["task_type"], "PRODUCTIVE")
        self.assertFalse(rd_advice["is_distraction"])

        rd_code = rec.analyze_tab("r/learnprogramming - Best advice for learning data structures? - Reddit")
        self.assertEqual(rd_code["task_type"], "PRODUCTIVE")
        self.assertFalse(rd_code["is_distraction"])

        # 6. Odd Reddit Articles & Memes -> WASTEFUL TASK
        rd_odd = rec.analyze_tab("r/mildlyinteresting: This odd potato shaped like a duck - Reddit")
        self.assertEqual(rd_odd["task_type"], "WASTEFUL")
        self.assertTrue(rd_odd["is_distraction"])

        rd_meme = rec.analyze_tab("r/memes: When the code finally works - Reddit")
        self.assertEqual(rd_meme["task_type"], "WASTEFUL")
        self.assertTrue(rd_meme["is_distraction"])

        # 7. Wikipedia Reference -> PRODUCTIVE TASK
        wiki = rec.analyze_tab("Theory of relativity - Wikipedia")
        self.assertEqual(wiki["task_type"], "PRODUCTIVE")
        self.assertFalse(wiki["is_distraction"])

    def test_productive_tasks_protection(self):
        """Verify that productive tasks are NEVER targeted or closed"""
        agent = AiTabGuardAgent()

        for title in [
            "MIT 6.006 Lecture 1: Algorithms - YouTube",
            "Python Full Course for Beginners - YouTube",
            "r/learnprogramming - Best career advice for beginners - Reddit",
            "r/Advice - Study tips for final exams - Reddit",
            "Theory of relativity - Wikipedia"
        ]:
            perc = agent.recognizer.analyze_tab(title, "")
            self.assertEqual(perc["task_type"], "PRODUCTIVE")
            self.assertFalse(perc["is_distraction"])


if __name__ == "__main__":
    unittest.main()
