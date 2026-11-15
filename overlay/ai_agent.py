"""
AI Agent & Perception Engine for TabbyPatrol
Integrated with LangChain GoalAwareAgentEngine & Multi-Tier Perception:
- Prefilter (< 1ms) -> DeepAgent (6s timeout) -> Heuristic Fallback on error.
- Understands WHAT is open on every tab (videos, topics, articles, discussions).
- Protects educational content and goal-aligned study while eliminating off-task distractions!
- Complete safeguards: fail-open, dry run, kill switch, fuzzy matching, and rate limits.
"""

import ctypes
from ctypes import wintypes
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import urlparse

# Enable Per-Monitor DPI Awareness v2
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_CONTROL = 0x11
VK_W = 0x57
KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent import GoalAwareAgentEngine, print_startup_banner, is_trace_enabled
from tab_recognizer import TabContentRecognizer, clean_browser_title


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUT_UNION),
    ]


def force_foreground_window(hwnd):
    """Bypasses Windows foreground lock restriction without changing window state."""
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    if user32.GetForegroundWindow() == hwnd:
        return True

    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    elif user32.IsZoomed(hwnd):
        user32.ShowWindow(hwnd, 3)
    else:
        user32.ShowWindow(hwnd, 5)

    if user32.GetForegroundWindow() == hwnd:
        return True

    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, KEYEVENTF_KEYUP, 0)

    cur_tid = kernel32.GetCurrentThreadId()
    target_tid = user32.GetWindowThreadProcessId(hwnd, None)
    attached = False
    if cur_tid != target_tid:
        attached = bool(user32.AttachThreadInput(cur_tid, target_tid, True))

    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)

    if attached:
        user32.AttachThreadInput(cur_tid, target_tid, False)

    return user32.GetForegroundWindow() == hwnd


def send_ctrl_w():
    """Sends Ctrl+W via SendInput with fallback to keybd_event"""
    extra = ctypes.c_ulong(0)
    extra_p = ctypes.pointer(extra)

    inputs = (INPUT * 4)()
    inputs[0].type = 1
    inputs[0].u.ki = KEYBDINPUT(VK_CONTROL, 0, 0, 0, extra_p)
    inputs[1].type = 1
    inputs[1].u.ki = KEYBDINPUT(VK_W, 0, 0, 0, extra_p)
    inputs[2].type = 1
    inputs[2].u.ki = KEYBDINPUT(VK_W, 0, KEYEVENTF_KEYUP, 0, extra_p)
    inputs[3].type = 1
    inputs[3].u.ki = KEYBDINPUT(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, extra_p)

    user32.SendInput(4, inputs, ctypes.sizeof(INPUT))
    time.sleep(0.02)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    time.sleep(0.02)
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


class AiTabGuardAgent:
    def __init__(self, blocked_keywords=None, enable_hotkey=True, current_goal=None):
        self.blocked_keywords = blocked_keywords or [
            "youtube",
            "reddit",
            "twitter",
            "x.com",
            "tiktok",
            "instagram",
            "twitch",
            "netflix",
            "facebook",
            "pinterest",
            "buzzfeed",
            "hulu",
            "shorts",
            "reels",
            "mrbeast"
        ]

        # Initialize Cognitive DeepAgent Engine
        self.engine = GoalAwareAgentEngine(
            current_goal=current_goal or "Hackathon: Python & AI Agent Development",
            on_thinking_callback=self._add_thought
        )

        self.recognizer = TabContentRecognizer()
        self.active_tab_perception = None
        self.last_perceived_key = ""
        self.productive_count = 0

        self.thoughts = []
        self._add_thought("AI Tab Guard Agent online. LangChain DeepAgent & Cognitive Classifier active.")

        self.last_swat_time = 0
        self.cooldown_seconds = 30.0 if os.environ.get("TABBY_ENFORCEMENT") == "1" else 3.0
        self.swat_count = 0
        self.max_session_closes = 5
        self.enabled = True
        self.enforcement_enabled = True

        self.browser_classes = [
            "Chrome_WidgetWin_1",
            "MozillaWindowClass",
            "ApplicationFrameWindow"
        ]

        self.allowlisted_domains = [
            "docs.google.com",
            "sheets.google.com",
            "github.com",
            "gitlab.com",
            "localhost",
            "127.0.0.1",
            "docs.python.org",
            "stackoverflow.com",
            "arxiv.org"
        ]

        self.ps_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "inspect_tabs.ps1")
        )

        # Startup banner requirement
        print_startup_banner()

    @property
    def is_dry_run(self) -> bool:
        return os.environ.get("TABBY_DRY_RUN", "1") in ("1", "true", "True")

    def set_goal(self, goal_text: str):
        self.engine.set_goal(goal_text)
        self._add_thought(f"Active goal updated: '{goal_text}'")

    def get_goal(self) -> str:
        return self.engine.get_goal()

    def _add_thought(self, text):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {text}"
        self.thoughts.append(entry)
        if len(self.thoughts) > 50:
            self.thoughts.pop(0)
        if is_trace_enabled():
            print(f"[AI AGENT] {entry}", flush=True)

    def get_latest_thought(self):
        return self.thoughts[-1] if self.thoughts else "AI Tab Guard Agent observing..."

    def get_active_tab_perception(self):
        return self.active_tab_perception

    def force_foreground_window(self, hwnd):
        return force_foreground_window(hwnd)

    def send_ctrl_w_input(self):
        send_ctrl_w()
        return True

    def _query_all_tabs(self, hwnd, select_tab_name=""):
        if not os.path.exists(self.ps_script_path):
            return "", []

        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", self.ps_script_path,
                "-Hwnd", str(hwnd)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=1.4)
            out = res.stdout.strip()
            if out:
                data = json.loads(out)
                if isinstance(data, dict):
                    return data.get("url", ""), data.get("tabs", [])
                elif isinstance(data, list):
                    return "", data
        except Exception:
            pass
        return "", []

    def fuzzy_tab_match(self, classified_title: str, classified_url: str, active_title: str, active_url: str):
        """
        Safeguard check: verifies that foreground tab still matches classified tab before close.
        Returns: (matched: bool, score: float, description: str)
        """
        c_url_clean = (classified_url or "").strip().lower()
        a_url_clean = (active_url or "").strip().lower()

        c_parsed = urlparse(c_url_clean) if c_url_clean else None
        a_parsed = urlparse(a_url_clean) if a_url_clean else None

        # Check URL match
        if c_parsed and a_parsed and c_parsed.netloc and a_parsed.netloc:
            if c_parsed.netloc == a_parsed.netloc:
                if c_parsed.path and c_parsed.path == a_parsed.path:
                    return True, 0.95, "Exact domain and path match"
                if c_parsed.path and a_parsed.path and (c_parsed.path.startswith(a_parsed.path) or a_parsed.path.startswith(c_parsed.path)):
                    return True, 0.85, "Domain and path prefix match"
                return True, 0.75, "Domain match"

        # Clean titles
        c_clean = clean_browser_title(classified_title).lower()
        a_clean = clean_browser_title(active_title).lower()

        # Strip notification badges like "(2) "
        c_clean = re.sub(r"^\(\d+\)\s*", "", c_clean)
        a_clean = re.sub(r"^\(\d+\)\s*", "", a_clean)

        c_words = set(re.findall(r"\b\w+\b", c_clean))
        a_words = set(re.findall(r"\b\w+\b", a_clean))

        stop_words = {"the", "a", "an", "and", "or", "to", "in", "on", "of", "for", "with", "youtube", "google", "chrome", "edge", "reddit"}
        c_sig = {w for w in c_words if len(w) > 2 and w not in stop_words}
        a_sig = {w for w in a_words if len(w) > 2 and w not in stop_words}

        if c_sig and a_sig:
            intersection = c_sig & a_sig
            union = c_sig | a_sig
            jaccard = len(intersection) / len(union) if union else 0.0
            overlap_c = len(intersection) / len(c_sig) if c_sig else 0.0

            score = max(jaccard, overlap_c)
            if score >= 0.50:
                return True, round(score, 2), f"Title keyword overlap ({len(intersection)} shared words)"

        if c_clean and a_clean and (c_clean in a_clean or a_clean in c_clean):
            return True, 0.80, "Substring title match"

        return False, 0.0, "Different tab detected"

    def scan_for_distraction(self):
        """
        Perceives active browser tab and passes through GoalAwareAgentEngine pipeline:
        Prefilter -> DeepAgent (6s timeout) -> Heuristic Fallback on error.
        """
        if not self.enabled or not self.enforcement_enabled:
            return None

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        class_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buf, 256)
        class_name = class_buf.value

        is_browser = any(bc in class_name for bc in self.browser_classes)

        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return None
        title_buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title_buf, length + 1)
        title = title_buf.value

        lower_title = title.lower()
        if not is_browser:
            browser_indicators = ["chrome", "edge", "brave", "firefox", "opera", "browser"]
            is_browser = any(bi in lower_title for bi in browser_indicators)

        if not is_browser:
            return None

        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        win_left = rect.left
        win_top = rect.top

        is_maximized = (win_left < 0 and win_top < 0)
        norm_left = 0 if is_maximized else win_left
        norm_top = 0 if is_maximized else win_top

        # Query UIA for URL and tabstrip tabs
        url, all_tabs = self._query_all_tabs(hwnd)

        # Determine active tab title and coordinates
        active_title = title
        active_tab_elem = None
        for t in all_tabs:
            if t.get("selected"):
                active_tab_elem = t
                if t.get("name"):
                    active_title = t.get("name")
                break

        # --- REAL CLASSIFICATION PIPELINE (Requirement 2) ---
        analysis = self.engine.evaluate(active_title, url)

        # Build perception dict for HUD & Overlay compatibility
        domain = ""
        if url:
            domain = urlparse(url).netloc.replace("www.", "")
        if not domain:
            domain = "YouTube" if "youtube" in lower_title else ("Reddit" if "reddit" in lower_title else "Web")

        is_distraction = (analysis["action"] == "pop")
        task_type = "PRODUCTIVE" if analysis["is_productive"] else "WASTEFUL"
        task_label = "🟢 PRODUCTIVE TASK (APPROVED)" if analysis["is_productive"] else "🎯 WASTEFUL TASK (SNIPING)"

        perception = {
            "title": clean_browser_title(active_title),
            "url": url,
            "domain": domain,
            "topic": analysis["topic"],
            "about": analysis["reason"],
            "category": "Educational" if analysis["is_productive"] else "Entertainment",
            "task_type": task_type,
            "task_label": task_label,
            "is_distraction": is_distraction,
            "bubble_text": f"Tabby: {analysis['verdict']} - {analysis['reason'][:45]}",
            "analysis": analysis
        }
        self.active_tab_perception = perception

        # Log new perception thought when tab/topic changes
        perceive_key = f"{perception['title']}||{analysis['verdict']}"
        if perceive_key != self.last_perceived_key:
            self.last_perceived_key = perceive_key
            if analysis["is_productive"]:
                self.productive_count += 1
            self._add_thought(f"Task: {task_label} on {domain} -> '{perception['title'][:40]}' ({analysis['reason']}) [{analysis['source']}]")

        # CRITICAL PROTECTION: If task is PRODUCTIVE or BROWSING, NEVER snipe!
        if not is_distraction or analysis["action"] != "pop":
            return None

        # Cooldown check for sniping
        now = time.time()
        if now - self.last_swat_time < self.cooldown_seconds:
            return None

        matched_targets = []
        if active_tab_elem:
            center_x = (active_tab_elem["left"] + active_tab_elem["right"]) // 2
            center_y = active_tab_elem["top"] + (active_tab_elem["height"] // 2)
            close_x = active_tab_elem["right"] - 18
            close_y = center_y
        else:
            center_x = norm_left + 160
            center_y = norm_top + 20
            close_x = center_x
            close_y = center_y

        matched_targets.append({
            "hwnd": hwnd,
            "title": perception["title"],
            "url": url,
            "keyword": perception["topic"],
            "about": perception["about"],
            "category": perception["category"],
            "task_type": "WASTEFUL",
            "task_label": "🎯 WASTEFUL TASK",
            "bubble_text": perception["bubble_text"],
            "target_x": center_x,
            "target_y": center_y,
            "close_x": close_x,
            "close_y": close_y,
            "selected": True,
            "analysis": analysis
        })

        self._add_thought(f"Action: Wasteful distraction locked for sniper elimination! Target: '{perception['title'][:35]}'")

        return {
            "hwnd": hwnd,
            "targets": matched_targets,
            "target_count": len(matched_targets),
            "is_multi": False,
            "perception": perception
        }

    def execute_tab_close(self, target_info):
        """
        Executes tab close with full safeguards:
        1. Kill switch check
        2. Dry-run check (TABBY_DRY_RUN)
        3. Fail-open verdict check
        4. Protected tabs / allowlist check
        5. Rate limits and session limit
        6. Pre-close fuzzy match check
        7. Send Ctrl+W input
        8. Post-close verification
        """
        if not self.enabled or not self.enforcement_enabled:
            self._add_thought("Kill switch / enforcement disabled. Close aborted.")
            return False

        # SAFEGUARD: Session limit
        if self.swat_count >= self.max_session_closes:
            self.enforcement_enabled = False
            self._add_thought("Session limit (5) reached. Enforcement automatically suspended for user safety.")
            return False

        # SAFEGUARD: Rate limit cooldown (30s in strict enforcement mode)
        now = time.time()
        if now - self.last_swat_time < self.cooldown_seconds:
            self._add_thought(f"Rate limit cooldown active ({self.cooldown_seconds}s). Close aborted.")
            return False

        # SAFEGUARD: Protected tab flags
        if target_info.get("is_first_tab") or target_info.get("is_pinned") or target_info.get("is_last_tab"):
            self._add_thought("Protected tab flag (first/pinned/last). Close aborted.")
            return False

        # SAFEGUARD: Allowlist check
        target_url = target_info.get("url", "").lower()
        if any(ad in target_url for ad in self.allowlisted_domains):
            self._add_thought(f"Allowlisted domain in URL ({target_url[:30]}). Close aborted.")
            return False

        # SAFEGUARD: Fail-Open analysis verification
        analysis = target_info.get("analysis")
        if analysis:
            verdict = str(analysis.get("verdict", "")).strip().upper()
            action = analysis.get("action", "")
            confidence = float(analysis.get("confidence", 0.0))
            if action != "pop" or verdict != "DISTRACTION" or confidence < 0.70:
                self._add_thought(f"Fail-Open safeguard: Non-distraction or low confidence ({confidence:.2f}). Close aborted.")
                return False

        # SAFEGUARD: Dry Run mode check
        if self.is_dry_run:
            self._add_thought("🐾 DRY RUN ACTIVE (TABBY_DRY_RUN=1): Sniping simulated! Keypress suppressed.")
            return False

        hwnd = target_info.get("hwnd")
        if not hwnd or not user32.IsWindow(hwnd):
            return False

        try:
            # SAFEGUARD: Pre-close fuzzy verification against actual foreground tab
            curr_title = ""
            try:
                ret = user32.GetWindowTextLengthW(hwnd)
                if isinstance(ret, int) and ret > 0:
                    title_buf = ctypes.create_unicode_buffer(ret + 1)
                    user32.GetWindowTextW(hwnd, title_buf, ret + 1)
                    curr_title = title_buf.value
            except Exception:
                pass

            curr_url, curr_tabs = self._query_all_tabs(hwnd)
            if curr_tabs:
                for ct in curr_tabs:
                    if ct.get("selected") and ct.get("name"):
                        curr_title = ct.get("name")
                        break
            if not curr_title and target_info.get("title"):
                curr_title = target_info.get("title")

            # Verify foreground matches classified target
            matched, score, desc = self.fuzzy_tab_match(
                classified_title=target_info.get("title", ""),
                classified_url=target_info.get("url", ""),
                active_title=curr_title,
                active_url=curr_url
            )
            if not matched:
                self._add_thought(f"🛡️ SAFEGUARD ABORT: Tab mismatch before close! Active: '{curr_title[:30]}'. Aborted.")
                return False

            # Bring to foreground
            self.force_foreground_window(hwnd)
            time.sleep(0.04)

            # Send close input
            self.send_ctrl_w_input()

            # SAFEGUARD: Post-close UI Automation verification
            time.sleep(0.05)
            verify_url, verify_tabs = self._query_all_tabs(hwnd)
            if verify_tabs:
                target_title_clean = clean_browser_title(target_info.get("title", "")).lower()
                for vt in verify_tabs:
                    v_name = clean_browser_title(vt.get("name", "")).lower()
                    if v_name and target_title_clean and (v_name == target_title_clean or target_title_clean in v_name):
                        self._add_thought("Verification warning: Tab still present after Ctrl+W.")
                        return False

            self.last_swat_time = time.time()
            self.swat_count += 1
            if self.swat_count >= self.max_session_closes:
                self.enforcement_enabled = False

            kw = target_info.get("keyword", "Distraction")
            self._add_thought(f"ELIMINATED! '{kw}' sniped. (Total sniped: {self.swat_count})")
            return True

        except Exception as e:
            self._add_thought(f"Action error: {e}")
            return False

    def add_keyword(self, keyword):
        clean = keyword.strip().lower()
        if clean and clean not in self.blocked_keywords:
            self.blocked_keywords.append(clean)
            self._add_thought(f"Added custom rule: '{clean}'")

    def remove_keyword(self, keyword):
        clean = keyword.strip().lower()
        if clean in self.blocked_keywords:
            self.blocked_keywords.remove(clean)
            self._add_thought(f"Removed custom rule: '{clean}'")
