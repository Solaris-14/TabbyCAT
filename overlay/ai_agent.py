"""
AI Agent & Perception Engine for TabbyPatrol
Supports Intelligent Tab Content Recognition & Multi-Target Distraction Elimination:
- Understands WHAT is open on every tab (videos, topics, articles, discussions).
- Explains what the tab is about and categorizes it (Education, Tech, Entertainment, Memes, News).
- Protects educational content (lectures, tutorials, docs, coding) while sniping off-task distractions!
"""

import ctypes
from ctypes import wintypes
import json
import os
import subprocess
import time

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
    """Bypasses Windows foreground lock restriction without changing window state (preserves maximized/normal)."""
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    # If already foreground, do nothing that could change window state
    if user32.GetForegroundWindow() == hwnd:
        return True

    # Only restore if minimized; never un-maximize a maximized window!
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE only if minimized
    elif user32.IsZoomed(hwnd):
        user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE (keeps maximized)
    else:
        user32.ShowWindow(hwnd, 5)  # SW_SHOW (preserves normal size)

    if user32.GetForegroundWindow() == hwnd:
        return True

    # Alt-key trick to bypass Windows foreground lock
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
    # Secondary fallback
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    time.sleep(0.02)
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


class AiTabGuardAgent:
    def __init__(self, blocked_keywords=None):
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

        self.recognizer = TabContentRecognizer()
        self.active_tab_perception = None
        self.last_perceived_key = ""
        self.productive_count = 0

        self.thoughts = []
        self._add_thought("AI Tab Guard Agent online. Task Classifier: Productive vs Wasteful Tasks active.")

        self.last_swat_time = 0
        self.cooldown_seconds = 3.0
        self.swat_count = 0
        self.enabled = True

        self.browser_classes = [
            "Chrome_WidgetWin_1",
            "MozillaWindowClass",
            "ApplicationFrameWindow"
        ]

        self.ps_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "inspect_tabs.ps1")
        )

    def _add_thought(self, text):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {text}"
        self.thoughts.append(entry)
        if len(self.thoughts) > 50:
            self.thoughts.pop(0)
        print(f"[AI AGENT] {entry}")

    def get_latest_thought(self):
        return self.thoughts[-1] if self.thoughts else "Observing..."

    def get_active_tab_perception(self):
        return self.active_tab_perception

    def _query_all_tabs(self, hwnd):
        """
        Queries active URL and all tabs from the browser window using UI Automation.
        """
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

    def scan_for_distraction(self):
        """
        Perceives what is open on the active tab, analyzes its topic/content,
        and decides whether it is an allowed productive resource or a distraction to snipe.
        """
        if not self.enabled:
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
        screen_w = user32.GetSystemMetrics(0)
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

        # Intelligent Content Recognition across all sites
        perception = self.recognizer.analyze_tab(active_title, url, custom_blocked=self.blocked_keywords)
        self.active_tab_perception = perception

        # Log new perception thought when tab/topic changes
        perceive_key = f"{perception['title']}||{perception['topic']}"
        if perceive_key != self.last_perceived_key:
            self.last_perceived_key = perceive_key
            task_label = perception.get("task_label", "🟢 PRODUCTIVE TASK")
            domain_name = perception.get("domain") or perception.get("site") or "Web"
            if perception.get("task_type") == "PRODUCTIVE":
                self.productive_count += 1
            self._add_thought(f"Task: {task_label} on {domain_name} -> '{perception['topic']}' ({perception['about']})")

        # CRITICAL PROTECTION: If the active task is PRODUCTIVE, NEVER target or snipe anything!
        if not perception.get("is_distraction") or perception.get("task_type") == "PRODUCTIVE":
            return None

        # Cooldown check for sniping
        now = time.time()
        if now - self.last_swat_time < self.cooldown_seconds:
            return None

        matched_targets = []

        # Target the active wasteful task
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
            "selected": True
        })

        target_count = len(matched_targets)
        self._add_thought(f"Action: Wasteful distraction locked for sniper elimination!")
        self._add_thought(f"  Target: [{perception['category']}] '{perception['topic']}' at Screen ({center_x}, {center_y})")

        return {
            "hwnd": hwnd,
            "targets": matched_targets,
            "target_count": target_count,
            "is_multi": False,
            "perception": perception
        }

    def execute_tab_close(self, target_info):
        """
        Closes a specific tab using Ctrl+W or by clicking its close button.
        """
        hwnd = target_info.get("hwnd")
        if not hwnd:
            return False

        try:
            # PRE-CLOSE SAFEGUARD: Verify foreground tab is NOT a productive task!
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title_buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title_buf, length + 1)
                curr_title = title_buf.value
                curr_perc = self.recognizer.analyze_tab(curr_title, "", custom_blocked=self.blocked_keywords)
                if curr_perc.get("task_type") == "PRODUCTIVE" or not curr_perc.get("is_distraction"):
                    self._add_thought(f"🛡️ SAFEGUARD ABORT: Tab '{curr_title}' is a PRODUCTIVE TASK! Tabby refuses to close it!")
                    return False

            force_foreground_window(hwnd)
            time.sleep(0.05)

            # If specific close coordinates are provided and tab is not selected, click close button
            close_x = target_info.get("close_x")
            close_y = target_info.get("close_y")
            if close_x and close_y and not target_info.get("selected", True):
                orig_pos = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(orig_pos))
                user32.SetCursorPos(int(close_x), int(close_y))
                time.sleep(0.02)
                user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                time.sleep(0.02)
                user32.SetCursorPos(orig_pos.x, orig_pos.y)
            else:
                # Dispatch Ctrl+W on active tab
                send_ctrl_w()

            self.last_swat_time = time.time()
            self.swat_count += 1
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
