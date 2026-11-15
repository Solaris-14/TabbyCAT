"""
Goal-Aware Agent Adapter for TabbyPatrol
Bridges the LangChain DeepAgent, FastRulePreFilter, and Memory system
to the Tkinter overlay, HUD window, and Win32 UI perception loop.

Pipeline:
1. memory/ read before verdicts (goal.md, session_plan.md, learned_preferences.md, appeals.md)
2. Cache check
3. PreFilter check (< 1ms)
4. Active Grace Period check
5. Learned Site Preferences check
6. Ambiguous Tab -> DeepAgent classifier (6s timeout) -> Fallback heuristics only on error (logging exact exception)
7. memory/ write after verdicts (verdict_log.md)
"""

import json
import os
import re
import sys
import threading
import time
from typing import Dict, Any, List, Optional, Callable

from agent.memory import TabbyMemory, MEMORY_DIR
from agent.prefilter import FastRulePreFilter
from agent.deep_agent import TabbyDeepAgent
from agent.trace import is_trace_enabled, trace_file_read, trace_file_write


class GoalAwareAgentEngine:
    """
    Cognitive Agent Engine powering TabbyPatrol.
    """

    def __init__(
        self,
        current_goal: Optional[str] = None,
        memory_dir: str = MEMORY_DIR,
        on_thinking_callback: Optional[Callable[[str], None]] = None
    ):
        self.memory = TabbyMemory(memory_dir)
        if current_goal:
            self.memory.save_goal(current_goal)

        self.prefilter = FastRulePreFilter()
        self.deep_agent = TabbyDeepAgent(memory_dir=self.memory.memory_dir)

        # Cache of evaluated tabs keyed by (url, title, goal)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()

        # Approved signatures set (compatible with existing overlay)
        self.approved_signatures: set = set()

        # UI callback when Tabby is thinking
        self.on_thinking_callback = on_thinking_callback

        # Latest evaluation store for HUD
        self._latest_analysis: Optional[Dict[str, Any]] = None

    def get_goal(self) -> str:
        return self.memory.get_goal()

    def set_goal(self, goal_text: str):
        """Sets the user's active focus goal, saves to memory/goal.md, and clears cache"""
        self.memory.save_goal(goal_text)
        with self._cache_lock:
            self._cache.clear()
        self.approved_signatures.clear()
        print(f"[TabbyEngine] Active goal updated to: '{goal_text}'. Cache refreshed.")

    def get_latest_analysis(self) -> Optional[Dict[str, Any]]:
        return self._latest_analysis

    def _make_cache_key(self, title: str, url: str, goal: str) -> str:
        return f"{(url or '').strip().lower()}|{(title or '').strip().lower()}|{(goal or '').strip().lower()}"

    def _log_classification(self, title: str, url: str, path: str, res: Dict[str, Any]):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        v = res.get("verdict", "UNKNOWN")
        conf = float(res.get("confidence", 0.0))
        reason = res.get("reason", "")
        entry = (
            f"[CLASSIFICATION] {timestamp} | "
            f"Path: {path} | "
            f"Title: '{title}' | "
            f"URL: '{url}' | "
            f"Verdict: {v} | "
            f"Confidence: {conf:.2f} | "
            f"Reason: '{reason}'"
        )
        if is_trace_enabled():
            print(entry, flush=True)

    def evaluate(self, title: str, url: str = "") -> Dict[str, Any]:
        """
        Evaluates active tab title and URL against the user's active focus goal.
        Follows Requirement 4: Read memory before verdict, write after verdict.
        Follows Requirement 2: Prefilter -> DeepAgent (6s timeout) -> Fallback heuristics on error.
        """
        # --- REQUIREMENT 4: READ MEMORY BEFORE VERDICT ---
        mem_ctx = self.memory.read_before_verdict()
        active_goal = mem_ctx.get("goal") or self.get_goal()
        cache_key = self._make_cache_key(title, url, active_goal)

        # 1. Cache Check
        with self._cache_lock:
            if cache_key in self._cache:
                cached = self._cache[cache_key]
                self._latest_analysis = cached
                self._log_classification(title, url, "cache", cached)
                return cached

        # 2. Fast Rule Pre-Filter Check (< 1ms for obvious homepages, search, shorts, reels)
        pre_result = self.prefilter.evaluate(title, url)
        if pre_result:
            res = self._format_verdict(
                verdict=pre_result["verdict"],
                relevance=pre_result.get("relevance_to_goal", 0.5),
                confidence=pre_result.get("confidence", 1.0),
                reason=pre_result["reason"],
                topic=pre_result.get("topic", "General"),
                source="prefilter",
                title=title,
                url=url
            )
            self._store_cache(cache_key, res)
            self._log_classification(title, url, "prefilter", res)

            # --- REQUIREMENT 4: WRITE MEMORY AFTER VERDICT ---
            self.memory.write_after_verdict({
                "title": title,
                "url": url,
                "goal": active_goal,
                "verdict": res["verdict"],
                "relevance": res["relevance_to_goal"],
                "confidence": res["confidence"],
                "source": res["source"],
                "reason": res["reason"]
            })
            return res

        # 3. Active Appeal Grace Period Check
        grace_info = self.memory.check_active_grace_period(title, url)
        if grace_info:
            res = self._format_verdict(
                verdict="approve",
                relevance=0.85,
                confidence=1.0,
                reason=f"Active appeal grant in effect ({grace_info['remaining_minutes']} min left). Reason: {grace_info['reason']}",
                topic="Appeals Allowance",
                source="grace_period",
                title=title,
                url=url
            )
            self._store_cache(cache_key, res)
            self._log_classification(title, url, "grace_period", res)

            # --- REQUIREMENT 4: WRITE MEMORY AFTER VERDICT ---
            self.memory.write_after_verdict({
                "title": title,
                "url": url,
                "goal": active_goal,
                "verdict": res["verdict"],
                "relevance": res["relevance_to_goal"],
                "confidence": res["confidence"],
                "source": res["source"],
                "reason": res["reason"]
            })
            return res

        # 4. Learned Site Preferences Check
        learned_pref = self.memory.check_learned_preference(title, url)
        if learned_pref:
            if learned_pref.get("allowed"):
                res = self._format_verdict(
                    verdict="approve",
                    relevance=0.90,
                    confidence=0.98,
                    reason=f"User-learned allowed site: {learned_pref.get('reason')}",
                    topic="Learned Preference",
                    source="learned_pref",
                    title=title,
                    url=url
                )
            else:
                res = self._format_verdict(
                    verdict="distraction",
                    relevance=0.05,
                    confidence=0.98,
                    reason=f"User-learned blocked site: {learned_pref.get('reason')}",
                    topic="Learned Preference",
                    source="learned_pref",
                    title=title,
                    url=url
                )
            self._store_cache(cache_key, res)
            self._log_classification(title, url, "learned_pref", res)

            # --- REQUIREMENT 4: WRITE MEMORY AFTER VERDICT ---
            self.memory.write_after_verdict({
                "title": title,
                "url": url,
                "goal": active_goal,
                "verdict": res["verdict"],
                "relevance": res["relevance_to_goal"],
                "confidence": res["confidence"],
                "source": res["source"],
                "reason": res["reason"]
            })
            return res

        # 5. Ambiguous Tab: Invoke LangChain DeepAgent with 6s timeout (Requirement 2)
        if self.on_thinking_callback:
            try:
                self.on_thinking_callback(f"Thinking: Analyzing '{title[:25]}' with DeepAgent... 🐾")
            except Exception:
                pass

        agent_result = None
        path_used = "deepagent"

        try:
            agent_result = self.deep_agent.classify_tab(title=title, url=url)
        except Exception as e:
            # REQUIREMENT 2: Fallback to heuristics only on error. Log the exact exception on any fallback!
            print(f"[DeepAgent Fallback] Classification failed with exception: {type(e).__name__}: {e}. Falling back to heuristics.")
            fallback_res = self._fallback_rule_classifier(title, url, active_goal)
            agent_result = fallback_res
            path_used = "fallback"

        res = self._format_verdict(
            verdict=agent_result.get("verdict", "browsing"),
            relevance=agent_result.get("relevance_to_goal", 0.5),
            confidence=agent_result.get("confidence", 0.85),
            reason=agent_result.get("reason", "Analyzed by Tabby DeepAgent."),
            topic="Goal-Aware Evaluation",
            source=agent_result.get("source", "deepagent"),
            title=title,
            url=url
        )
        self._store_cache(cache_key, res)
        self._log_classification(title, url, path_used, res)

        # --- REQUIREMENT 4: WRITE MEMORY AFTER VERDICT ---
        self.memory.write_after_verdict({
            "title": title,
            "url": url,
            "goal": active_goal,
            "verdict": res["verdict"],
            "relevance": res["relevance_to_goal"],
            "confidence": res["confidence"],
            "source": res["source"],
            "reason": res["reason"]
        })

        return res

    def _fallback_rule_classifier(self, title: str, url: str, goal: str) -> Dict[str, Any]:
        """
        Requirement 2: Heuristic fallback when DeepAgent times out or errors.
        """
        lower_title = (title or "").lower()
        lower_url = (url or "").lower()
        goal_words = [w for w in re.findall(r"\b\w+\b", (goal or "").lower()) if len(w) > 3]

        # 1. Goal keyword match
        if any(gw in lower_title or gw in lower_url for gw in goal_words):
            return {
                "verdict": "approve",
                "relevance_to_goal": 0.90,
                "confidence": 0.85,
                "reason": f"Fallback rule: Content matches active focus goal '{goal}'.",
                "source": "fallback_heuristics"
            }

        # 2. Viral entertainment / memes
        is_entertainment = any(k in lower_title or k in lower_url for k in [
            "mrbeast", "mr beast", "shorts", "reels", "tiktok", "instagram",
            "fails", "funny", "gaming", "stream", "challenge", "comedy", "prank",
            "r/memes", "memes"
        ])
        if is_entertainment:
            return {
                "verdict": "distraction",
                "relevance_to_goal": 0.05,
                "confidence": 0.95,
                "reason": f"Fallback rule: Entertainment / viral media detected off-goal.",
                "source": "fallback_heuristics"
            }

        # 3. General educational lecture / study content
        edu_signals = [
            "lecture", "course", "tutorial", "learn", "study", "exam", "mit",
            "khan academy", "textbook", "professor", "class", "chemistry", "physics"
        ]
        if any(es in lower_title for es in edu_signals):
            return {
                "verdict": "approve",
                "relevance_to_goal": 0.85,
                "confidence": 0.85,
                "reason": "Fallback rule: Educational lecture or study material detected.",
                "source": "fallback_heuristics"
            }

        # 4. YouTube watch / Reddit subreddit off-goal
        if "youtube.com/watch" in lower_url or "/watch?v=" in lower_url or "reddit.com/r/" in lower_url or "r/" in lower_title:
            return {
                "verdict": "distraction",
                "relevance_to_goal": 0.15,
                "confidence": 0.85,
                "reason": f"Fallback rule: Video or forum thread is off-goal for '{goal}'.",
                "source": "fallback_heuristics"
            }

        # 5. Default browsing
        return {
            "verdict": "browsing",
            "relevance_to_goal": 0.50,
            "confidence": 0.70,
            "reason": "Fallback rule: General unclassified tab allowed under fail-open safeguard.",
            "source": "fallback_heuristics"
        }

    def _format_verdict(
        self,
        verdict: str,
        relevance: float,
        confidence: float,
        reason: str,
        topic: str,
        source: str,
        title: str,
        url: str
    ) -> Dict[str, Any]:
        """
        Maps internal verdict to overlay dictionary schema with FAIL-OPEN safeguards.
        """
        v_clean = str(verdict or "").strip().lower()
        conf = float(confidence or 0.0)
        reason_str = str(reason or "").strip()

        is_hard_rule = (source in ("prefilter", "fallback_heuristics", "fallback_rule"))
        has_agent_reason = bool(reason_str)

        is_targeted_platform = "reddit.com/r/" in (url or "").lower() or "youtube.com/watch" in (url or "").lower() or "/watch?v=" in (url or "").lower()
        required_conf = 0.70 if is_targeted_platform else 0.80

        if v_clean == "distraction" and conf >= required_conf and (is_hard_rule or has_agent_reason):
            action = "pop"
            score = -max(0.6, 1.0 - relevance)
            verdict_str = "DISTRACTION"
            is_productive = False
            is_browsing = False
            intent = "Off-Goal Entertainment / Distraction"
        elif v_clean in ("approve", "approved", "productive", "pass"):
            action = "pass"
            score = max(0.6, relevance)
            verdict_str = "PRODUCTIVE"
            is_productive = True
            is_browsing = False
            intent = "Goal-Aligned Study / Work"
        else:
            action = "browse"
            score = 0.50
            verdict_str = "BROWSING"
            is_productive = True
            is_browsing = True
            intent = "Searching / Browsing (Fail-Open Allowed)"
            if v_clean == "distraction" and conf < 0.8:
                reason_str = f"Low confidence ({conf:.2f} < 0.80) on distraction. Fail-open allowed: {reason_str}"
            elif v_clean not in ("browsing", "browse"):
                reason_str = f"Uncertain verdict '{verdict}'. Fail-open safe default: allowed."

        res = {
            "is_productive": is_productive,
            "is_browsing": is_browsing,
            "score": round(score, 2),
            "verdict": verdict_str,
            "action": action,
            "topic": topic,
            "intent": intent,
            "reason": reason_str,
            "relevance_to_goal": round(relevance, 2),
            "confidence": round(conf, 2),
            "source": source,
            "matched_positive": [topic] if is_productive else [],
            "matched_negative": [topic] if not is_productive and not is_browsing else [],
            "goal_matches": [self.get_goal()] if is_productive else []
        }
        self._latest_analysis = res
        return res

    def _store_cache(self, key: str, value: Dict[str, Any]):
        with self._cache_lock:
            self._cache[key] = value
            if len(self._cache) > 500:
                first_key = next(iter(self._cache))
                del self._cache[first_key]

    # -------------------------------------------------------------
    # DeepAgent Capabilities for Session Planning, Appeals, Coach
    # -------------------------------------------------------------
    def create_session_plan(self, session_request: str) -> Dict[str, Any]:
        """Creates a session plan using the Planner subagent"""
        return self.deep_agent.plan_session(session_request)

    def submit_appeal(self, title: str, url: str, argument: str) -> Dict[str, Any]:
        """Submits a user appeal to the Appeals Judge subagent"""
        result = self.deep_agent.judge_appeal(title, url, argument)
        active_goal = self.get_goal()
        cache_key = self._make_cache_key(title, url, active_goal)
        with self._cache_lock:
            self._cache.pop(cache_key, None)
        return result

    def generate_coach_reflection(self) -> str:
        """Generates a focus reflection using the Coach subagent"""
        return self.deep_agent.generate_coach_reflection()
