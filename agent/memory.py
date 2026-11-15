"""
TabbyPatrol Persistent Memory System
Manages persistent local state in the memory/ folder using Markdown files:
- memory/goal.md
- memory/session_plan.md
- memory/verdict_log.md
- memory/learned_preferences.md
- memory/appeals.md
- memory/reflection.md

Files are read before each verdict and written after each verdict,
with full trace logging when --agent-trace is active.
"""

import json
import os
import re
import time
from typing import Dict, Any, List, Optional

from agent.trace import trace_file_read, trace_file_write

MEMORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory"))


class TabbyMemory:
    def __init__(self, memory_dir: str = MEMORY_DIR):
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)

        self.goal_file = os.path.join(self.memory_dir, "goal.md")
        self.plan_file = os.path.join(self.memory_dir, "session_plan.md")
        self.verdicts_file = os.path.join(self.memory_dir, "verdict_log.md")
        self.prefs_file = os.path.join(self.memory_dir, "learned_preferences.md")
        self.appeals_file = os.path.join(self.memory_dir, "appeals.md")
        self.coach_file = os.path.join(self.memory_dir, "reflection.md")

        self._ensure_defaults()

    def _ensure_defaults(self):
        """Initializes empty files in Markdown format if they don't already exist"""
        if not os.path.exists(self.goal_file):
            self.save_goal("Hackathon: Python & AI Agent Development")

        if not os.path.exists(self.plan_file):
            default_plan = {
                "session_title": "Focus Session",
                "total_duration_hours": 2.0,
                "blocks": [
                    {"title": "Deep Work Block 1", "duration_minutes": 50, "focus": "Core Task & Implementation"},
                    {"title": "Deep Work Block 2", "duration_minutes": 50, "focus": "Review & Testing"}
                ],
                "break_times": [{"after_block": 1, "duration_minutes": 10}],
                "allowed_resources": ["github.com", "docs.python.org", "arxiv.org"]
            }
            self.save_plan(default_plan)

        if not os.path.exists(self.verdicts_file):
            with open(self.verdicts_file, "w", encoding="utf-8") as f:
                f.write(
                    "# TabbyPatrol Verdict Log\n\n"
                    "| Timestamp | Title | URL | Verdict | Relevance | Confidence | Source | Reason |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                )

        if not os.path.exists(self.prefs_file):
            with open(self.prefs_file, "w", encoding="utf-8") as f:
                f.write(
                    "# Learned Site Preferences\n\n"
                    "| Pattern | Allowed | Reason | Updated |\n"
                    "|---|---|---|---|\n"
                )

        if not os.path.exists(self.appeals_file):
            with open(self.appeals_file, "w", encoding="utf-8") as f:
                f.write(
                    "# TabbyPatrol Appeals Log\n\n"
                    "| Timestamp | Title | URL | Ruling | Grace Mins | Expires At | Argument | Reason |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                )

        if not os.path.exists(self.coach_file):
            with open(self.coach_file, "w", encoding="utf-8") as f:
                f.write(
                    "# 🐱 TabbyPatrol Focus Reflection Report\n\n"
                    "*No reflection generated yet. Complete a study session or request a coach review in the HUD!*\n"
                )

    # -------------------------------------------------------------
    # Explicit Pre/Post Verdict Lifecycle Hooks (Requirement 4)
    # -------------------------------------------------------------
    def read_before_verdict(self) -> Dict[str, Any]:
        """
        Reads memory files before verdict evaluation:
        - memory/goal.md
        - memory/session_plan.md
        - memory/learned_preferences.md
        - memory/appeals.md
        """
        goal = self.get_goal()
        plan = self.get_plan()
        prefs = self.get_preferences()
        appeals = self.get_appeals(limit=5)
        return {
            "goal": goal,
            "plan": plan,
            "preferences": prefs,
            "appeals": appeals
        }

    def write_after_verdict(self, record: Dict[str, Any]):
        """
        Writes verdict record to memory/verdict_log.md after evaluation.
        """
        self.record_verdict(record)

    # -------------------------------------------------------------
    # Goal Management (memory/goal.md)
    # -------------------------------------------------------------
    def save_goal(self, goal_text: str):
        clean_goal = goal_text.strip()
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        content = (
            f"# Active Focus Goal\n\n"
            f"**Goal**: {clean_goal}\n"
            f"**Updated**: {time_str}\n"
        )
        with open(self.goal_file, "w", encoding="utf-8") as f:
            f.write(content)
        trace_file_write(self.goal_file)

    def get_goal(self) -> str:
        if os.path.exists(self.goal_file):
            trace_file_read(self.goal_file)
            try:
                with open(self.goal_file, "r", encoding="utf-8") as f:
                    text = f.read()
                    m = re.search(r"\*\*Goal\*\*:\s*([^\n]+)", text)
                    if m:
                        return m.group(1).strip()
            except Exception:
                pass
        return "Hackathon: Python & AI Agent Development"

    # -------------------------------------------------------------
    # Session Plan Management (memory/session_plan.md)
    # -------------------------------------------------------------
    def save_plan(self, plan_data: Dict[str, Any]):
        title = plan_data.get("session_title", "Focus Session")
        duration = plan_data.get("total_duration_hours", 2.0)
        blocks = plan_data.get("blocks", [])
        breaks = plan_data.get("break_times", [])
        allowed = plan_data.get("allowed_resources", [])

        lines = [
            f"# Session Plan: {title}",
            f"**Total Duration**: {duration} hours\n",
            "## Study Blocks"
        ]
        for idx, b in enumerate(blocks, start=1):
            btitle = b.get("title", f"Block {idx}")
            bdur = b.get("duration_minutes", 45)
            bfocus = b.get("focus", "Focused study")
            lines.append(f"- **{btitle}** ({bdur} mins) - Focus: {bfocus}")

        lines.append("\n## Break Times")
        for brk in breaks:
            lines.append(f"- {brk.get('duration_minutes', 10)} mins after Block {brk.get('after_block', 1)}")

        lines.append("\n## Allowed Resources")
        for res in allowed:
            lines.append(f"- {res}")

        # Embed JSON representation in markdown comment for exact roundtrip
        lines.append(f"\n<!-- json\n{json.dumps(plan_data, indent=2)}\n-->\n")

        with open(self.plan_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        trace_file_write(self.plan_file)

    def get_plan(self) -> Optional[Dict[str, Any]]:
        if os.path.exists(self.plan_file):
            trace_file_read(self.plan_file)
            try:
                with open(self.plan_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Check for embedded json comment
                    m = re.search(r"<!-- json\s*(\{.*?\})\s*-->", content, re.DOTALL)
                    if m:
                        return json.loads(m.group(1))

                    # Parse from markdown fields
                    title_match = re.search(r"# Session Plan:\s*([^\n]+)", content)
                    session_title = title_match.group(1).strip() if title_match else "Focus Session"
                    return {
                        "session_title": session_title,
                        "raw_markdown": content
                    }
            except Exception:
                pass
        return None

    # -------------------------------------------------------------
    # Verdicts History (memory/verdict_log.md)
    # -------------------------------------------------------------
    def record_verdict(self, record: Dict[str, Any]):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        title = str(record.get("title", "")).replace("|", "-").replace("\n", " ").strip()
        url = str(record.get("url", "")).replace("|", "-").replace("\n", " ").strip()
        verdict = str(record.get("verdict", "")).strip().upper()
        relevance = float(record.get("relevance", record.get("relevance_to_goal", 0.5)))
        confidence = float(record.get("confidence", 0.85))
        source = str(record.get("source", "agent")).strip()
        reason = str(record.get("reason", "")).replace("|", "-").replace("\n", " ").strip()

        row = f"| {timestamp} | {title} | {url} | {verdict} | {relevance:.2f} | {confidence:.2f} | {source} | {reason} |\n"

        try:
            with open(self.verdicts_file, "a", encoding="utf-8") as f:
                f.write(row)
            trace_file_write(self.verdicts_file)
        except Exception as e:
            print(f"[Memory] Failed to record verdict: {e}")

    def get_verdicts(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not os.path.exists(self.verdicts_file):
            return []
        trace_file_read(self.verdicts_file)
        verdicts = []
        try:
            with open(self.verdicts_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not line.startswith("| Timestamp") and not line.startswith("|---"):
                        parts = [p.strip() for p in line.split("|")[1:-1]]
                        if len(parts) >= 8:
                            verdicts.append({
                                "timestamp": parts[0],
                                "title": parts[1],
                                "url": parts[2],
                                "verdict": parts[3],
                                "relevance": float(parts[4]) if parts[4] else 0.5,
                                "confidence": float(parts[5]) if parts[5] else 0.85,
                                "source": parts[6],
                                "reason": parts[7]
                            })
        except Exception:
            return []
        return verdicts[-limit:]

    # -------------------------------------------------------------
    # Learned Per-Site Preferences (memory/learned_preferences.md)
    # -------------------------------------------------------------
    def get_preferences(self) -> Dict[str, Any]:
        if not os.path.exists(self.prefs_file):
            return {}
        trace_file_read(self.prefs_file)
        prefs = {}
        try:
            with open(self.prefs_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not line.startswith("| Pattern") and not line.startswith("|---"):
                        parts = [p.strip() for p in line.split("|")[1:-1]]
                        if len(parts) >= 4:
                            pattern = parts[0].lower()
                            allowed = parts[1].lower() in ("true", "allowed", "1", "pass")
                            reason = parts[2]
                            updated = parts[3]
                            prefs[pattern] = {
                                "allowed": allowed,
                                "reason": reason,
                                "updated": updated
                            }
        except Exception:
            pass
        return prefs

    def update_preference(self, pattern: str, allowed: bool, reason: str):
        prefs = self.get_preferences()
        key = pattern.strip().lower()
        prefs[key] = {
            "allowed": allowed,
            "reason": reason.replace("|", "-").replace("\n", " "),
            "updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Rewrite learned_preferences.md
        lines = [
            "# Learned Site Preferences\n",
            "| Pattern | Allowed | Reason | Updated |",
            "|---|---|---|---|"
        ]
        for pat, info in prefs.items():
            lines.append(f"| {pat} | {info['allowed']} | {info['reason']} | {info['updated']} |")

        with open(self.prefs_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        trace_file_write(self.prefs_file)

    def check_learned_preference(self, title: str, url: str) -> Optional[Dict[str, Any]]:
        prefs = self.get_preferences()
        combined = f"{(title or '').lower()} {(url or '').lower()}"
        for pattern, info in prefs.items():
            if pattern in combined:
                return info
        return None

    # -------------------------------------------------------------
    # Appeals & Grace Periods (memory/appeals.md)
    # -------------------------------------------------------------
    def record_appeal(self, appeal_record: Dict[str, Any]):
        now = time.time()
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        grace_minutes = int(appeal_record.get("grace_minutes", 0))
        ruling = str(appeal_record.get("ruling", "denied")).strip().upper()
        expires_at = int(now + (grace_minutes * 60)) if (ruling == "GRANTED" and grace_minutes > 0) else 0

        title = str(appeal_record.get("title", "")).replace("|", "-").replace("\n", " ").strip()
        url = str(appeal_record.get("url", "")).replace("|", "-").replace("\n", " ").strip()
        argument = str(appeal_record.get("argument", "")).replace("|", "-").replace("\n", " ").strip()
        reason = str(appeal_record.get("reason", "")).replace("|", "-").replace("\n", " ").strip()

        row = f"| {time_str} | {title} | {url} | {ruling} | {grace_minutes} | {expires_at} | {argument} | {reason} |\n"

        try:
            with open(self.appeals_file, "a", encoding="utf-8") as f:
                f.write(row)
            trace_file_write(self.appeals_file)
        except Exception as e:
            print(f"[Memory] Failed to record appeal: {e}")

    def get_appeals(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not os.path.exists(self.appeals_file):
            return []
        trace_file_read(self.appeals_file)
        appeals = []
        try:
            with open(self.appeals_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not line.startswith("| Timestamp") and not line.startswith("|---"):
                        parts = [p.strip() for p in line.split("|")[1:-1]]
                        if len(parts) >= 8:
                            appeals.append({
                                "timestamp": parts[0],
                                "title": parts[1],
                                "url": parts[2],
                                "ruling": parts[3].lower(),
                                "grace_minutes": int(parts[4]) if parts[4].isdigit() else 0,
                                "expires_at": float(parts[5]) if parts[5].replace(".", "").isdigit() else 0,
                                "argument": parts[6],
                                "reason": parts[7]
                            })
        except Exception:
            pass
        return appeals[-limit:]

    def check_active_grace_period(self, title: str, url: str) -> Optional[Dict[str, Any]]:
        """Checks if a tab has an active, unexpired appeal grant"""
        now = time.time()
        appeals = self.get_appeals(limit=50)
        title_lower = (title or "").lower()
        url_lower = (url or "").lower()

        # Look from most recent backwards
        for a in reversed(appeals):
            if a.get("ruling") == "granted" and a.get("expires_at", 0) > now:
                app_title = a.get("title", "").lower()
                app_url = a.get("url", "").lower()
                if (app_url and app_url in url_lower) or (app_title and app_title in title_lower):
                    remaining_mins = max(1, int((a["expires_at"] - now) / 60))
                    return {
                        "granted": True,
                        "reason": a.get("reason", "Appeal granted"),
                        "remaining_minutes": remaining_mins,
                        "expires_at": a["expires_at"]
                    }
        return None

    # -------------------------------------------------------------
    # Session Todos
    # -------------------------------------------------------------
    def get_todos(self) -> List[Dict[str, Any]]:
        plan = self.get_plan() or {}
        return plan.get("todos", [])

    def save_todos(self, todos: List[Dict[str, Any]]):
        plan = self.get_plan() or {}
        plan["todos"] = todos
        self.save_plan(plan)

    def add_todo(self, task: str, status: str = "pending") -> Dict[str, Any]:
        todos = self.get_todos()
        item = {
            "id": len(todos) + 1,
            "task": task.strip(),
            "status": status,
            "created_at": time.time()
        }
        todos.append(item)
        self.save_todos(todos)
        return item

    def update_todo(self, todo_id: int, status: str) -> bool:
        todos = self.get_todos()
        for t in todos:
            if t.get("id") == todo_id:
                t["status"] = status
                self.save_todos(todos)
                return True
        return False

    # -------------------------------------------------------------
    # Coach Reflection (memory/reflection.md)
    # -------------------------------------------------------------
    def save_coach_reflection(self, content: str):
        with open(self.coach_file, "w", encoding="utf-8") as f:
            f.write(content)
        trace_file_write(self.coach_file)

    def get_coach_reflection(self) -> str:
        if os.path.exists(self.coach_file):
            trace_file_read(self.coach_file)
            try:
                with open(self.coach_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "No session reflection generated yet. Complete a study session or request a coach review in the HUD!"

    # -------------------------------------------------------------
    # Context Aggregator for Prompt / Filesystem Memory
    # -------------------------------------------------------------
    def get_system_context_summary(self) -> str:
        goal = self.get_goal()
        plan = self.get_plan()
        prefs = self.get_preferences()
        appeals = self.get_appeals(limit=5)

        lines = [
            f"CURRENT ACTIVE FOCUS GOAL: {goal}",
        ]

        if plan:
            lines.append("CURRENT SESSION PLAN:")
            blocks = plan.get("blocks", [])
            for b in blocks:
                lines.append(f" - Block: {b.get('title')} ({b.get('duration_minutes', 25)} mins)")
            allowed = plan.get("allowed_resources", [])
            if allowed:
                lines.append(f" - Allowed Resource Types / Sites: {', '.join(allowed)}")

        if prefs:
            lines.append("LEARNED SITE PREFERENCES:")
            for k, v in prefs.items():
                status = "ALLOWED" if v.get("allowed") else "BLOCKED"
                lines.append(f" - {k}: {status} ({v.get('reason')})")

        if appeals:
            lines.append("RECENT APPEALS & OUTCOMES:")
            for a in appeals[-3:]:
                lines.append(f" - '{a.get('title', '')[:30]}': {a.get('ruling')} - {a.get('reason', '')}")

        return "\n".join(lines)
