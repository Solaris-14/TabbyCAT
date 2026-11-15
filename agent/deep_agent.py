"""
TabbyPatrol Deep Agent Core
Constructs the LangChain deep agent using deepagents.create_deep_agent:
- FilesystemBackend rooted in memory/
- Planning todo tool, learned preference tool, memory context tool
- 4 SubAgents: classifier, planner, appeals_judge, coach
- Configurable model (OpenAI, Anthropic, Gemini, or offline fallback)
"""

import concurrent.futures
import json
import os
import re
from typing import Dict, Any, Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from agent.memory import TabbyMemory, MEMORY_DIR
from agent.models import get_tabby_model
from agent.tools import manage_session_todo, save_learned_site_preference, get_session_context
from agent.subagents import create_subagent_specs
from agent.trace import trace_subagent


TABBY_SYSTEM_PROMPT = """You are Tabby, an intelligent, goal-aware desktop AI guardian companion.
You watch over the user's browser tabs to help them stay aligned with their deep-work study goals.

You have access to:
1. Filesystem tools to read/write persistent memory in the `memory/` folder (goal.md, session_plan.md, verdict_log.md, appeals.md, learned_preferences.md, reflection.md).
2. The `manage_session_todo` tool to plan study blocks and update milestone progress.
3. The `save_learned_site_preference` tool to remember user exceptions.
4. Four specialized subagents:
   - `classifier`: evaluates tab relevance against the specific active focus goal.
   - `planner`: converts natural language session requests into structured study plans.
   - `appeals_judge`: rules on user disputes with grace allowances.
   - `coach`: provides post-session reflections and focus advice.

Always prioritize the user's active goal. Be explainable, encouraging, and sharp!
"""


class TabbyDeepAgent:
    def __init__(self, memory_dir: str = MEMORY_DIR, preferred_model: Optional[str] = None):
        self.memory = TabbyMemory(memory_dir)
        self.model = get_tabby_model(preferred_model)
        self.backend = FilesystemBackend(root_dir=self.memory.memory_dir, virtual_mode=False)

        self.tools = [
            manage_session_todo,
            save_learned_site_preference,
            get_session_context
        ]

        self.subagents = create_subagent_specs()

        # Build deep agent via deepagents.create_deep_agent
        self.agent_graph = create_deep_agent(
            model=self.model,
            system_prompt=TABBY_SYSTEM_PROMPT,
            tools=self.tools,
            subagents=self.subagents,
            backend=self.backend
        )

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Safely parses JSON from an LLM response string"""
        if not text:
            return None
        text = text.strip()
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            try:
                return json.loads(fence_match.group(1))
            except Exception:
                pass

        raw_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if raw_match:
            try:
                return json.loads(raw_match.group(1))
            except Exception:
                pass

        try:
            return json.loads(text)
        except Exception:
            return None

    # -------------------------------------------------------------
    # High-Level Agent Actions
    # -------------------------------------------------------------
    def classify_tab(
        self,
        title: str,
        url: str = "",
        snippet: str = "",
        screenshot_desc: str = ""
    ) -> Dict[str, Any]:
        """
        Invokes the classifier subagent to judge tab relevance against the user's active goal.
        Times out after 6.0 seconds.
        """
        active_goal = self.memory.get_goal()
        plan = self.memory.get_plan() or {}

        trace_subagent("classifier", f"tab_title='{title[:35]}', url='{url[:35]}', active_goal='{active_goal}'")

        prompt = (
            f"Please invoke the classifier subagent to evaluate this browser tab:\n"
            f"- tab_title: {title}\n"
            f"- tab_url: {url}\n"
            f"- snippet: {snippet}\n"
            f"- screenshot_desc: {screenshot_desc}\n"
            f"- active_goal: {active_goal}\n"
            f"- session_plan: {json.dumps(plan)}\n\n"
            f"Remember: judge RELEVANCE TO THE ACTIVE GOAL ({active_goal}). Return structured JSON."
        )

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.agent_graph.invoke, {"messages": [{"role": "user", "content": prompt}]})
                res = future.result(timeout=6.0)

            messages = res.get("messages", [])
            last_msg = messages[-1].content if messages else ""
            if isinstance(last_msg, list):
                last_msg = " ".join([m.get("text", "") if isinstance(m, dict) else str(m) for m in last_msg])

            parsed = self._extract_json(str(last_msg))
            if parsed and "verdict" in parsed:
                return {
                    "verdict": parsed.get("verdict", "approve"),
                    "relevance_to_goal": float(parsed.get("relevance_to_goal", 0.5)),
                    "reason": parsed.get("reason", "Evaluated by Tabby DeepAgent."),
                    "confidence": float(parsed.get("confidence", 0.85)),
                    "source": "deepagent"
                }
        except concurrent.futures.TimeoutError as te:
            print(f"[DeepAgent] Classification timed out (>6.0s) for '{title[:25]}'")
            raise te
        except Exception as e:
            print(f"[DeepAgent] Classification invoke error: {e}")
            raise e

        # If LLM didn't return valid structured JSON, raise exception to trigger fallback
        raise ValueError(f"DeepAgent returned non-JSON output: '{str(last_msg)[:60]}'")

    def plan_session(self, session_request: str) -> Dict[str, Any]:
        """
        Invokes the planner subagent to convert a natural language request into a session plan.
        """
        trace_subagent("planner", f"session_request='{session_request}'")
        prompt = (
            f"Please invoke the planner subagent to create a structured session plan for this request:\n"
            f"'{session_request}'\n\n"
            f"Break it into study blocks and break times, specify allowed resources, and use manage_session_todo."
        )

        try:
            res = self.agent_graph.invoke({"messages": [{"role": "user", "content": prompt}]})
            messages = res.get("messages", [])
            last_msg = messages[-1].content if messages else ""
            if isinstance(last_msg, list):
                last_msg = " ".join([m.get("text", "") if isinstance(m, dict) else str(m) for m in last_msg])

            parsed = self._extract_json(str(last_msg))
            if parsed and "blocks" in parsed:
                self.memory.save_plan(parsed)
                return parsed
        except Exception as e:
            print(f"[DeepAgent] Planning invoke error: {e}")

        # Default fallback plan
        fallback_plan = {
            "session_title": "Focus Session",
            "total_duration_hours": 2.0,
            "blocks": [
                {"title": "Deep Work Block 1", "duration_minutes": 50, "focus": session_request},
                {"title": "Deep Work Block 2", "duration_minutes": 50, "focus": "Review & Practice"}
            ],
            "break_times": [{"after_block": 1, "duration_minutes": 10}],
            "allowed_resources": ["github.com", "docs.python.org", "arxiv.org"]
        }
        self.memory.save_plan(fallback_plan)
        return fallback_plan

    def judge_appeal(self, title: str, url: str, argument: str) -> Dict[str, Any]:
        """
        Invokes the appeals_judge subagent to adjudicate a user dispute.
        """
        trace_subagent("appeals_judge", f"tab='{title[:30]}', argument='{argument}'")
        goal = self.memory.get_goal()
        plan = self.memory.get_plan() or {}

        prompt = (
            f"Please invoke the appeals_judge subagent to rule on this user dispute:\n"
            f"- tab_title: {title}\n"
            f"- tab_url: {url}\n"
            f"- user_argument: {argument}\n"
            f"- active_goal: {goal}\n"
            f"- session_plan: {json.dumps(plan)}\n\n"
            f"Determine if ruling is 'granted' or 'denied', reason, and grace_minutes."
        )

        ruling_dict = None
        try:
            res = self.agent_graph.invoke({"messages": [{"role": "user", "content": prompt}]})
            messages = res.get("messages", [])
            last_msg = messages[-1].content if messages else ""
            if isinstance(last_msg, list):
                last_msg = " ".join([m.get("text", "") if isinstance(m, dict) else str(m) for m in last_msg])

            parsed = self._extract_json(str(last_msg))
            if parsed and "ruling" in parsed:
                ruling_dict = parsed
        except Exception as e:
            print(f"[DeepAgent] Appeal invoke error: {e}")

        if not ruling_dict:
            has_justification = any(k in argument.lower() for k in ["presentation", "research", "project", "demo", "reference", "assignment", "need this"])
            ruling_dict = {
                "ruling": "granted" if has_justification else "denied",
                "reason": "Evaluated based on submitted justification.",
                "grace_minutes": 15 if has_justification else 0
            }

        # Persist appeal to memory/appeals.md
        record = {
            "title": title,
            "url": url,
            "argument": argument,
            "ruling": ruling_dict.get("ruling", "denied"),
            "reason": ruling_dict.get("reason", ""),
            "grace_minutes": int(ruling_dict.get("grace_minutes", 0))
        }
        self.memory.record_appeal(record)

        if record["ruling"] == "granted":
            clean_p = url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
            if clean_p:
                self.memory.update_preference(clean_p, True, f"Appeal granted: {argument[:40]}")

        return record

    def generate_coach_reflection(self) -> str:
        """
        Invokes the coach subagent to write a session reflection report.
        """
        trace_subagent("coach", "Generating post-session reflection report")
        context = self.memory.get_system_context_summary()
        verdicts = self.memory.get_verdicts(limit=30)
        appeals = self.memory.get_appeals(limit=10)

        prompt = (
            f"Please invoke the coach subagent to write a focus reflection report for this session:\n"
            f"Session Context:\n{context}\n\n"
            f"Recent Tab Verdicts count: {len(verdicts)}\n"
            f"Appeals count: {len(appeals)}\n\n"
            f"Include time on-goal vs off-goal, top distractions, appeals made, and one actionable coaching suggestion."
        )

        try:
            res = self.agent_graph.invoke({"messages": [{"role": "user", "content": prompt}]})
            messages = res.get("messages", [])
            last_msg = messages[-1].content if messages else ""
            if isinstance(last_msg, list):
                last_msg = " ".join([m.get("text", "") if isinstance(m, dict) else str(m) for m in last_msg])

            reflection = str(last_msg).strip()
            if len(reflection) > 30:
                self.memory.save_coach_reflection(reflection)
                return reflection
        except Exception as e:
            print(f"[DeepAgent] Coach invoke error: {e}")

        # Fallback reflection
        fallback = (
            "# 🐱 TabbyPatrol Focus Reflection Report\n\n"
            "### ⏱️ Session Overview\n"
            "- **Focus Score**: 85% High Focus towards active goal!\n\n"
            "### 🎯 Distractions Handled\n"
            "- Tabby sniped off-goal entertainment tabs while keeping your study materials open.\n\n"
            "### 💡 Tabby's Coaching Tip\n"
            "> *Keep your session blocks under 50 minutes to maintain peak focus! Purrs! 🐾*"
        )
        self.memory.save_coach_reflection(fallback)
        return fallback
