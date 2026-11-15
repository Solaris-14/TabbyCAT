"""
TabbyPatrol - Full-Fledged Desktop AI Agent Overlay
Tactical Sniper Cat with Laser-Fast Bullets & Multi-Target Rapid-Fire:
- Perched behind a tactical sniper rifle with bipod & high-magnification scope
- Laser-fast railgun bullet travelling at hyper speeds across the screen
- Multi-target rapid-fire double-tap: snipes multiple blocked tabs in quick succession!
- Rapid bolt-action cycling (CH-CHK!) between shots with casing ejection
- Smug post-shot pose blowing smoke from the barrel, then curls back to sleep!
"""

import math
import os
import queue
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk

import ctypes
from ctypes import wintypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

user32 = ctypes.windll.user32

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

from pillow_sprites import create_pillow_with_cat, create_pillow_sprite
from ai_agent import AiTabGuardAgent, RECT
from hud_window import AgentHudWindow


class FullFledgedTabbyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TabbyPatrol Desktop AI Agent")

        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        self.trans_color = "#010101"
        self.root.wm_attributes("-transparentcolor", self.trans_color)
        self.root.config(bg=self.trans_color)

        self.screen_w = user32.GetSystemMetrics(0)
        self.screen_h = user32.GetSystemMetrics(1)
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            bg=self.trans_color,
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Prevent overlay from stealing focus
        self.root.update_idletasks()
        try:
            hwnd = self.root.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOOLWINDOW = 0x00000080
            cur_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        except Exception:
            pass

        self.agent = AiTabGuardAgent()
        self.sound_enabled = True

        # Compact Pillow Roost in bottom-right corner
        self.pillow_x = float(self.screen_w - 150)
        self.pillow_y = float(self.screen_h - 110)
        self.pillow_theme = "pink"
        self.facing_left = True

        # State Machine:
        # 'on_pillow_sleep', 'on_pillow_sit', 'on_pillow_knead'
        # Tactical Sniper Sequence: 'sniper_aim', 'sniper_firing', 'sniper_chamber', 'sniper_smug'
        self.state = "on_pillow_sleep"
        self.sub_frame = 0
        self.anim_tick = 0
        self.state_timer = 0

        # Multi-Target Sniper Queue
        self.target_queue = []
        self.current_target = None
        self.total_targets_in_run = 0

        # Laser-Fast Bullet Projectile State
        self.laser_bullet = None # { x, y, vx, vy, origin_x, origin_y, target_x, target_y, trail: [] }

        # Laser Sight
        self.show_laser = False

        # Screen Shake parameters
        self.shake_frames = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # Shockwaves
        self.shockwaves = []

        # Speech bubble
        self.bubble_text = "Tabby sniper on watch! 🐾"
        self.bubble_timer = 100

        # Floating FX particles (casing, smoke, sparks)
        self.particles = []

        # Last observed browser tab title
        self.last_observed_title = ""

        # Dragging state for the pillow
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.pillow_cache = {}
        self._load_all_sprites()

        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Button-3>", self._show_context_menu)

        self._build_context_menu()
        self.hud_win = None

        self.ai_thread_running = True
        self.mission_queue = queue.Queue()
        threading.Thread(target=self._ai_monitor_worker, daemon=True).start()

        self.root.after(33, self._game_loop)

    def _load_all_sprites(self):
        """Pre-cache PhotoImage objects for all tactical sniper states"""
        for theme in ["pink", "lavender", "mint"]:
            self.pillow_cache[theme] = {
                "empty": ImageTk.PhotoImage(create_pillow_sprite(color_theme=theme, scale=1.35)),
                True: {},  # facing left
                False: {}  # facing right
            }
            actions = ["sleep", "sit", "knead", "sniper_aim", "sniper_fire", "sniper_chamber", "sniper_smug"]
            for act in actions:
                for facing_left in [True, False]:
                    frames = 2 if act in ("sleep", "knead") else (4 if act == "sit" else 1)
                    self.pillow_cache[theme][facing_left][act] = [
                        ImageTk.PhotoImage(create_pillow_with_cat(act, f, theme, facing_left=facing_left, scale=1.35))
                        for f in range(frames)
                    ]

    def _build_context_menu(self):
        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="🐾 Pet Tabby (Make it purr!)", command=self.pet_cat)
        self.menu.add_command(label="🍞 Make Biscuits (Knead Cushion)", command=self.knead_biscuits)
        self.menu.add_command(label="💤 Take a Cat Nap", command=self.sleep_nap)
        self.menu.add_command(label="🧠 What Is This Tab About?", command=self.inspect_active_tab)
        self.menu.add_separator()
        self.menu.add_command(label="🎯 Test Rapid-Fire Double Tap", command=self.test_double_tap)
        self.menu.add_command(label="🖥️ Open AI Command Center", command=self.open_hud)
        self.menu.add_separator()
        theme_menu = Menu(self.menu, tearoff=0)
        theme_menu.add_command(label="🍓 Strawberry Pink", command=lambda: self.set_pillow_theme("pink"))
        theme_menu.add_command(label="💜 Royal Lavender", command=lambda: self.set_pillow_theme("lavender"))
        theme_menu.add_command(label="🍃 Mint Cloud", command=lambda: self.set_pillow_theme("mint"))
        self.menu.add_cascade(label="🎨 Pillow Style", menu=theme_menu)
        self.menu.add_command(label="🔊 Toggle Sound", command=self.toggle_sound)
        self.menu.add_command(label="📍 Reset to Corner", command=self.reset_to_corner)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Exit TabbyPatrol", command=self.quit_app)

    def _show_context_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _play_sound(self, sound_type):
        if not (self.sound_enabled and HAS_SOUND):
            return
        def _beep():
            try:
                if sound_type == "alert":
                    winsound.Beep(988, 70)
                    winsound.Beep(1318, 110)
                elif sound_type == "sniper_shot":
                    # Powerful gunshot crack
                    winsound.Beep(1600, 40)
                    winsound.Beep(320, 100)
                elif sound_type == "bolt_chamber":
                    # Tactical bolt action cycle (CH-CHK!)
                    winsound.Beep(1200, 30)
                    winsound.Beep(1500, 35)
                elif sound_type == "purr":
                    winsound.Beep(523, 50)
                    winsound.Beep(659, 70)
                    winsound.Beep(784, 90)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.show_speech("Sound ON 🔊" if self.sound_enabled else "Sound Muted 🔇", duration=40)

    def set_pillow_theme(self, theme):
        self.pillow_theme = theme
        self.show_speech(f"Pillow switched to {theme}! ✨", duration=40)

    def reset_to_corner(self):
        self.pillow_x = float(self.screen_w - 150)
        self.pillow_y = float(self.screen_h - 110)
        self.show_speech("Back in cozy corner! 📍", duration=40)

    def pet_cat(self):
        self._play_sound("purr")
        self.show_speech("Purrrr! Good human! ❤️", duration=60)
        for _ in range(5):
            self.particles.append({
                "x": self.pillow_x + 55 + random.randint(-20, 20),
                "y": self.pillow_y + 15 + random.randint(-10, 10),
                "text": "❤️",
                "color": "#f43f5e",
                "vy": -1.2,
                "life": 40
            })

    def knead_biscuits(self):
        self.set_state("on_pillow_knead")
        self.show_speech("Making biscuits on the cushion! 🍞🐾", duration=80)

    def sleep_nap(self):
        self.set_state("on_pillow_sleep")
        self.show_speech("Zzz... snooze time... 💤", duration=60)

    def open_hud(self):
        if self.hud_win is None or not self.hud_win.win.winfo_exists():
            self.hud_win = AgentHudWindow(
                self.root,
                self.agent,
                on_style_change=self.set_pillow_theme,
                on_test_pounce=self.test_double_tap
            )
        else:
            self.hud_win.win.lift()

    def inspect_active_tab(self):
        perc = getattr(self.agent, "active_tab_perception", None)
        if perc:
            self.show_speech(perc.get("bubble_text", "Observing desktop... 🐾"), duration=90)
        else:
            self.show_speech("Observing desktop for active tabs... 🐾", duration=60)

    def test_double_tap(self):
        """Simulates rapid-fire double-tap on 2 distraction tabs in quick succession"""
        hwnd = user32.GetForegroundWindow()
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        norm_left = max(0, rect.left)
        norm_top = max(0, rect.top)

        # Create two distinct target tabs for double-tap
        simulated_mission = {
            "hwnd": hwnd,
            "targets": [
                {
                    "title": "YouTube - Tab 1",
                    "keyword": "youtube",
                    "target_x": norm_left + 180,
                    "target_y": norm_top + 20,
                    "is_test": True
                },
                {
                    "title": "Reddit - Tab 2",
                    "keyword": "reddit",
                    "target_x": norm_left + 360,
                    "target_y": norm_top + 20,
                    "is_test": True
                }
            ],
            "target_count": 2,
            "is_multi": True
        }
        self.mission_queue.put(simulated_mission)

    def quit_app(self):
        self.ai_thread_running = False
        self.root.destroy()
        sys.exit(0)

    def show_speech(self, text, duration=80):
        self.bubble_text = text
        self.bubble_timer = duration

    def set_state(self, new_state):
        self.state = new_state
        self.sub_frame = 0
        self.anim_tick = 0
        self.state_timer = 0

    # Mouse Dragging
    def _on_mouse_down(self, event):
        pw, ph = 115, 75
        if (self.pillow_x <= event.x <= self.pillow_x + pw and
            self.pillow_y <= event.y <= self.pillow_y + ph):
            self.is_dragging = True
            self.drag_offset_x = event.x - self.pillow_x
            self.drag_offset_y = event.y - self.pillow_y

    def _on_mouse_drag(self, event):
        if self.is_dragging:
            self.pillow_x = max(10, min(self.screen_w - 120, event.x - self.drag_offset_x))
            self.pillow_y = max(10, min(self.screen_h - 80, event.y - self.drag_offset_y))

    def _on_mouse_up(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.pet_cat()

    # Autonomous AI Agent Background Thread
    def _ai_monitor_worker(self):
        while self.ai_thread_running:
            time.sleep(0.3)
            if self.state in ("on_pillow_sleep", "on_pillow_sit", "on_pillow_knead") and not self.target_queue:
                distraction_data = self.agent.scan_for_distraction()
                if distraction_data:
                    self.mission_queue.put(distraction_data)
                else:
                    # When switching to productive or unblocked tabs, show Tabby's understanding in speech bubble!
                    perc = getattr(self.agent, "active_tab_perception", None)
                    if perc and perc.get("title") != self.last_observed_title:
                        self.last_observed_title = perc.get("title")
                        bubble_txt = perc.get("bubble_text")
                        if bubble_txt:
                            self.show_speech(bubble_txt, duration=85)

    # Main Animation & Physics Loop (~30 FPS)
    def _game_loop(self):
        self.anim_tick += 1
        self.state_timer += 1

        # Check for new missions from AI Agent
        if not self.mission_queue.empty() and "on_pillow" in self.state:
            try:
                mission_data = self.mission_queue.get_nowait()
                self._start_sniper_mission(mission_data)
            except queue.Empty:
                pass

        # Update screen shake
        if self.shake_frames > 0:
            self.shake_frames -= 1
            intensity = min(14, self.shake_frames * 2)
            self.shake_offset_x = random.randint(-intensity, intensity)
            self.shake_offset_y = random.randint(-intensity, intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        # State Machine Transitions
        if self.state == "on_pillow_sleep":
            self.show_laser = False
            if self.anim_tick % 15 == 0:
                self.sub_frame = (self.sub_frame + 1) % 2
                if random.random() < 0.35:
                    self.particles.append({
                        "x": self.pillow_x + 65,
                        "y": self.pillow_y + 15,
                        "text": random.choice(["z", "Z", "💤"]),
                        "color": "#38bdf8",
                        "vy": -0.8,
                        "life": 40
                    })
            if self.state_timer > 350 and random.random() < 0.01:
                self.set_state("on_pillow_sit")

        elif self.state == "on_pillow_sit":
            self.show_laser = False
            if self.anim_tick % 8 == 0:
                self.sub_frame = (self.sub_frame + 1) % 4
            if self.state_timer > 200 and random.random() < 0.015:
                self.set_state("on_pillow_knead")

        elif self.state == "on_pillow_knead":
            self.show_laser = False
            if self.anim_tick % 10 == 0:
                self.sub_frame = (self.sub_frame + 1) % 2
                if random.random() < 0.3:
                    self.particles.append({
                        "x": self.pillow_x + 55 + random.randint(-8, 8),
                        "y": self.pillow_y + 25,
                        "text": "✨",
                        "color": "#f59e0b",
                        "vy": -0.6,
                        "life": 30
                    })
            if self.state_timer > 160:
                self.set_state("on_pillow_sleep")

        # -------------------------------------------------------------
        # TACTICAL SNIPER RAPID-FIRE SEQUENCE
        # -------------------------------------------------------------
        elif self.state == "sniper_aim":
            # Perched behind rifle, laser sight locked onto current target
            self.show_laser = True
            # Aim duration: shorter on follow-up shots for rapid-fire feel!
            aim_threshold = 12 if self.total_targets_in_run == len(self.target_queue) else 7
            if self.state_timer > aim_threshold:
                # FIRE LASER BULLET!
                self.set_state("sniper_fire")
                self.show_laser = False
                self._fire_laser_bullet()

        elif self.state == "sniper_fire":
            # Bullet travelling at hyper speeds!
            self.show_laser = False
            self._update_laser_bullet()

        elif self.state == "sniper_chamber":
            # Rapid bolt-action cycling (CH-CHK!) to chamber round for next target!
            self.show_laser = False
            if self.state_timer > 6:
                # Immediately aim at the next target in queue!
                if self.target_queue:
                    self.current_target = self.target_queue.pop(0)
                    self.facing_left = (self.current_target["target_x"] < self.pillow_x + 50)
                    self.set_state("sniper_aim")
                else:
                    self.set_state("sniper_smug")

        elif self.state == "sniper_smug":
            # All targets eliminated! Smug pose, blowing smoke, victory wink
            self.show_laser = False
            if self.state_timer % 12 == 0:
                self.particles.append({
                    "x": self.pillow_x + 55 + random.randint(-10, 10),
                    "y": self.pillow_y + 10,
                    "text": random.choice(["❤️", "✨", "👑"]),
                    "color": "#f43f5e",
                    "vy": -1.0,
                    "life": 30
                })

            if self.state_timer > 50:
                self.set_state("on_pillow_sleep")
                self.current_target = None
                self.show_speech("Zzz... back to snooze... 💤", duration=60)
                self._play_sound("purr")

        # Update shockwaves
        alive_sw = []
        for sw in self.shockwaves:
            sw["radius"] += 8
            sw["life"] -= 1
            if sw["life"] > 0:
                alive_sw.append(sw)
        self.shockwaves = alive_sw

        if self.bubble_timer > 0:
            self.bubble_timer -= 1

        # Update particles (including ejecting brass casings)
        alive_particles = []
        for p in self.particles:
            p["x"] += p.get("vx", 0)
            p["y"] += p["vy"]
            if "gravity" in p:
                p["vy"] += p["gravity"]
            p["life"] -= 1
            if p["life"] > 0:
                alive_particles.append(p)
        self.particles = alive_particles

        self._render()
        self.root.after(33, self._game_loop)

    def _start_sniper_mission(self, mission_data):
        targets = mission_data.get("targets", [])
        if not targets:
            return

        self.target_queue = list(targets)
        self.total_targets_in_run = len(self.target_queue)

        # Pop first target
        self.current_target = self.target_queue.pop(0)
        self.facing_left = (self.current_target["target_x"] < self.pillow_x + 50)

        self.set_state("sniper_aim")

        count = self.total_targets_in_run
        if count > 1:
            self.show_speech(f"MULTIPLE TARGETS ({count})! RAPID FIRE! 🎯⚡", duration=80)
        else:
            bubble_txt = self.current_target.get("bubble_text")
            if bubble_txt:
                self.show_speech(bubble_txt, duration=75)
            else:
                kw = self.current_target.get("keyword", "distraction").upper()
                self.show_speech(f"SNIPER LOCKED: {kw}! 🎯", duration=70)
        self._play_sound("alert")

    def _fire_laser_bullet(self):
        """Fires a high-velocity laser bullet at the current target"""
        if not self.current_target:
            return

        origin_x = self.pillow_x + (20 if self.facing_left else 90)
        origin_y = self.pillow_y + 18

        tx = self.current_target["target_x"]
        ty = self.current_target["target_y"]

        dx = tx - origin_x
        dy = ty - origin_y
        dist = math.hypot(dx, dy)

        speed = 175.0 # Laser-fast hyper velocity!
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed

        self.laser_bullet = {
            "x": origin_x,
            "y": origin_y,
            "vx": vx,
            "vy": vy,
            "origin_x": origin_x,
            "origin_y": origin_y,
            "target_x": tx,
            "target_y": ty,
            "trail": [(origin_x, origin_y)]
        }

        self._play_sound("sniper_shot")

        # Eject brass casing into the air!
        casing_x = self.pillow_x + (40 if self.facing_left else 60)
        casing_y = self.pillow_y + 14
        self.particles.append({
            "x": casing_x,
            "y": casing_y,
            "vx": random.uniform(-1.5, 1.5),
            "vy": random.uniform(-4.0, -2.5),
            "gravity": 0.45,
            "text": "🟨",
            "color": "#f59e0b",
            "life": 22
        })

    def _update_laser_bullet(self):
        if not self.laser_bullet:
            return

        b = self.laser_bullet
        b["trail"].append((b["x"], b["y"]))
        if len(b["trail"]) > 5:
            b["trail"].pop(0)

        b["x"] += b["vx"]
        b["y"] += b["vy"]

        dist_to_target = math.hypot(b["target_x"] - b["x"], b["target_y"] - b["y"])

        # IMPACT! Reaches or passes target
        if dist_to_target <= abs(b["vx"]) or b["y"] <= b["target_y"]:
            self._trigger_bullet_impact(b["target_x"], b["target_y"])
            self.laser_bullet = None

            # Quick Succession: Chamber next round if there are more targets!
            if self.target_queue:
                self._play_sound("bolt_chamber")
                self.set_state("sniper_chamber")
                remaining = len(self.target_queue)
                self.show_speech(f"CH-CHK! Next target! ({remaining} left) ⚡", duration=40)
            else:
                self.set_state("sniper_smug")
                if self.total_targets_in_run > 1:
                    self.show_speech("DOUBLE KILL! ALL TABS SNIPED! 🎯😼", duration=70)
                else:
                    self.show_speech("BULLSEYE! TAB ELIMINATED! 🎯😼", duration=65)

    def _trigger_bullet_impact(self, tx, ty):
        """Thunderous railgun laser impact on the tab"""
        # Violent screen shake!
        self.shake_frames = 11

        # Expanding sonic shockwaves
        self.shockwaves.append({
            "x": tx,
            "y": ty,
            "radius": 14,
            "max_radius": 90,
            "life": 13
        })

        # Comic text
        self.particles.append({
            "x": tx,
            "y": ty - 25,
            "text": "⚡ BANG! SNIPED! 🎯💥",
            "color": "#dc2626",
            "vy": -1.5,
            "life": 40
        })

        for _ in range(12):
            self.particles.append({
                "x": tx + random.randint(-25, 25),
                "y": ty + random.randint(-15, 15),
                "text": random.choice(["⚡", "💥", "✨", "🔥"]),
                "color": random.choice(["#facc15", "#ef4444", "#38bdf8"]),
                "vy": random.uniform(-2.5, -0.5),
                "life": 30
            })

        # Physically close the target tab!
        if self.current_target and not self.current_target.get("is_test"):
            self.agent.execute_tab_close(self.current_target)

    def _render(self):
        self.canvas.delete("all")

        ox = self.shake_offset_x
        oy = self.shake_offset_y

        # 1. Render Laser Sight Beam when aiming!
        if self.show_laser and self.current_target:
            origin_x = self.pillow_x + (15 if self.facing_left else 95) + ox
            origin_y = self.pillow_y + 16 + oy
            tx = self.current_target["target_x"] + ox
            ty = self.current_target["target_y"] + oy

            # High-intensity red laser beam
            self.canvas.create_line(origin_x, origin_y, tx, ty, fill="#ef4444", width=2)
            # Glowing core
            self.canvas.create_line(origin_x, origin_y, tx, ty, fill="#fca5a5", width=1)
            # Target reticle
            self.canvas.create_oval(tx - 12, ty - 12, tx + 12, ty + 12, outline="#ef4444", width=2)
            self.canvas.create_line(tx - 16, ty, tx + 16, ty, fill="#ef4444", width=1)
            self.canvas.create_line(tx, ty - 16, tx, ty + 16, fill="#ef4444", width=1)
            self.canvas.create_text(tx, ty - 18, text="SNIPER LOCK 🎯", fill="#dc2626", font=("Segoe UI", 8, "bold"))

        # 2. Render Laser-Fast Railgun Bullet in Flight
        if self.laser_bullet:
            b = self.laser_bullet
            origin_pt = (b["origin_x"] + ox, b["origin_y"] + oy)
            current_pt = (b["x"] + ox, b["y"] + oy)

            # Continuous blazing railgun laser beam from rifle to current position
            self.canvas.create_line(
                origin_pt[0], origin_pt[1], current_pt[0], current_pt[1],
                fill="#38bdf8", width=5
            )
            self.canvas.create_line(
                origin_pt[0], origin_pt[1], current_pt[0], current_pt[1],
                fill="#ffffff", width=2
            )

            # Hyper-velocity tracer projectile head
            self.canvas.create_oval(
                current_pt[0] - 5, current_pt[1] - 5,
                current_pt[0] + 5, current_pt[1] + 5,
                fill="#facc15", outline="#ffffff"
            )

        # 3. Render Shockwaves
        for sw in self.shockwaves:
            r = sw["radius"]
            self.canvas.create_oval(
                sw["x"] - r + ox, sw["y"] - r / 2 + oy,
                sw["x"] + r + ox, sw["y"] + r / 2 + oy,
                outline="#f59e0b",
                width=max(1, int(sw["life"] / 2))
            )
            if r > 12:
                r2 = r - 10
                self.canvas.create_oval(
                    sw["x"] - r2 + ox, sw["y"] - r2 / 2 + oy,
                    sw["x"] + r2 + ox, sw["y"] + r2 / 2 + oy,
                    outline="#ffffff",
                    width=2
                )

        # 4. Render Pillow & Sniper Kitten
        theme_pack = self.pillow_cache.get(self.pillow_theme, self.pillow_cache["pink"])

        # Determine which sprite action to render
        action_map = {
            "on_pillow_sleep": "sleep",
            "on_pillow_sit": "sit",
            "on_pillow_knead": "knead",
            "sniper_aim": "sniper_aim",
            "sniper_fire": "sniper_fire",
            "sniper_chamber": "sniper_chamber",
            "sniper_smug": "sniper_smug"
        }
        spr_key = action_map.get(self.state, "sleep")
        frame_list = theme_pack[self.facing_left].get(spr_key, [])
        if frame_list:
            img = frame_list[self.sub_frame % len(frame_list)]
            self.canvas.create_image(int(self.pillow_x + ox), int(self.pillow_y + oy), image=img, anchor=tk.NW)

        # 5. Render Speech Bubble
        if self.bubble_timer > 0 and self.bubble_text:
            text = self.bubble_text
            bx_ref = self.pillow_x + (30 if self.facing_left else 70)
            by_ref = self.pillow_y

            bx = bx_ref + (-150 if self.facing_left else 50) + ox
            by = max(8, by_ref - 32) + oy

            box_w = max(80, len(text) * 6 + 22)
            box_h = 24
            bx = max(10, min(self.screen_w - box_w - 10, bx))

            self.canvas.create_rectangle(
                bx, by, bx + box_w, by + box_h,
                fill="#ffffff",
                outline="#fdba74",
                width=2
            )
            px = bx_ref + (15 if self.facing_left else 35) + ox
            self.canvas.create_polygon(
                px, by + box_h,
                px + 5, by + box_h + 5,
                px + 10, by + box_h,
                fill="#ffffff",
                outline="#fdba74"
            )
            self.canvas.create_text(
                bx + box_w / 2, by + box_h / 2,
                text=text,
                fill="#431407",
                font=("Segoe UI", 8, "bold")
            )

        # 6. Render Particles
        for p in self.particles:
            self.canvas.create_text(
                int(p["x"] + ox),
                int(p["y"] + oy),
                text=p["text"],
                fill=p["color"],
                font=("Segoe UI Emoji", 11, "bold")
            )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FullFledgedTabbyApp()
    app.run()


TabbyOverlay = FullFledgedTabbyApp
