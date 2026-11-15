"""
TabbyPatrol - AI Agent HUD & Command Center
Integrated with LangChain DeepAgents:
- Active Goal & Session Planner (planner subagent)
- Appeal Tab & Grace Allowances (appeals_judge subagent)
- End-of-Session Focus Reflection (coach subagent)
- Real-Time Cognitive Thought Feed and Task Classifier (Productive vs Wasteful)
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox


class AgentHudWindow:
    def __init__(self, parent, agent, on_style_change, on_test_pounce):
        self.agent = agent
        self.on_style_change = on_style_change
        self.on_test_pounce = on_test_pounce

        self.win = tk.Toplevel(parent)
        self.win.title("TabbyPatrol AI Agent - Command Center")
        self.win.geometry("520x760")
        self.win.configure(bg="#fffbf7")
        self.win.attributes("-topmost", True)

        self._build_ui()
        self._update_loop()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.win, bg="#fffbf7", pady=6)
        hdr.pack(fill=tk.X, padx=16)

        title = tk.Label(
            hdr,
            text="🐱 TabbyPatrol Deep Agent",
            font=("Segoe UI", 15, "bold"),
            bg="#fffbf7",
            fg="#431407"
        )
        title.pack(anchor=tk.W)

        sub = tk.Label(
            hdr,
            text="Goal-Aware AI Guardian • Planner • Appeals Judge • Focus Coach",
            font=("Segoe UI", 9),
            bg="#fffbf7",
            fg="#9a3412"
        )
        sub.pack(anchor=tk.W)

        # Status Card
        card = tk.Frame(self.win, bg="#ffffff", highlightthickness=1, highlightbackground="#fed7aa", padx=12, pady=6)
        card.pack(fill=tk.X, padx=16, pady=4)

        self.status_lbl = tk.Label(
            card,
            text="● AI Agent Status: Active & Monitoring Desktop",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#15803d"
        )
        self.status_lbl.pack(anchor=tk.W)

        self.swat_lbl = tk.Label(
            card,
            text="Wasteful Tasks Sniped: 0   |   Productive Tasks Approved: 0",
            font=("Segoe UI", 8, "bold"),
            bg="#ffffff",
            fg="#78350f"
        )
        self.swat_lbl.pack(anchor=tk.W, pady=2)

        # --- GOAL & SESSION PLANNER (Requirement 3: planner) ---
        goal_frame = tk.LabelFrame(
            self.win,
            text=" 🎯 Focus Goal & Session Planner (SubAgent: planner) ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#7c2d12",
            padx=10,
            pady=6
        )
        goal_frame.pack(fill=tk.X, padx=16, pady=4)

        self.goal_entry = tk.Entry(goal_frame, font=("Segoe UI", 9))
        self.goal_entry.pack(fill=tk.X, pady=(0, 4))
        current_goal = self.agent.get_goal() if hasattr(self.agent, "get_goal") else "Hackathon: Python & AI Agent Development"
        self.goal_entry.insert(0, current_goal)

        goal_btn_row = tk.Frame(goal_frame, bg="#ffffff")
        goal_btn_row.pack(fill=tk.X)

        set_goal_btn = tk.Button(
            goal_btn_row,
            text="Update Goal",
            font=("Segoe UI", 8, "bold"),
            bg="#f97316",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._on_set_goal
        )
        set_goal_btn.pack(side=tk.LEFT, padx=(0, 6))

        plan_btn = tk.Button(
            goal_btn_row,
            text="📋 AI Session Plan",
            font=("Segoe UI", 8, "bold"),
            bg="#8b5cf6",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._on_plan_session
        )
        plan_btn.pack(side=tk.LEFT)

        # --- ACTIVE TAB CLASSIFIER CARD ---
        perc_card = tk.LabelFrame(
            self.win,
            text=" 🧠 Active Tab Task Classifier ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#7c2d12",
            padx=10,
            pady=6
        )
        perc_card.pack(fill=tk.X, padx=16, pady=4)

        self.perc_badge_lbl = tk.Label(
            perc_card,
            text="🟢 PRODUCTIVE TASK",
            font=("Segoe UI", 9, "bold"),
            bg="#dcfce7",
            fg="#15803d",
            padx=8,
            pady=2,
            relief=tk.FLAT
        )
        self.perc_badge_lbl.pack(anchor=tk.W, pady=(0, 2))

        self.perc_domain_lbl = tk.Label(
            perc_card,
            text="Domain: Waiting for active browser tab...",
            font=("Segoe UI", 8, "bold"),
            bg="#ffffff",
            fg="#9a3412",
            anchor=tk.W
        )
        self.perc_domain_lbl.pack(fill=tk.X)

        self.perc_title_lbl = tk.Label(
            perc_card,
            text="Content: None",
            font=("Segoe UI", 8, "bold"),
            bg="#ffffff",
            fg="#1f2937",
            anchor=tk.W,
            wraplength=460,
            justify=tk.LEFT
        )
        self.perc_title_lbl.pack(fill=tk.X, pady=(2, 2))

        self.perc_about_lbl = tk.Label(
            perc_card,
            text="Analysis: Open an educational video or entertainment tab to see live classification.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#4b5563",
            anchor=tk.W,
            wraplength=460,
            justify=tk.LEFT
        )
        self.perc_about_lbl.pack(fill=tk.X)

        # --- SUBAGENT ACTION BUTTONS (Requirement 3: appeals_judge & coach) ---
        actions_frame = tk.Frame(self.win, bg="#fffbf7")
        actions_frame.pack(fill=tk.X, padx=16, pady=4)

        # Appeal Button (wired to appeals_judge)
        self.appeal_btn = tk.Button(
            actions_frame,
            text="⚖️ Appeal Tab (Appeals Judge)",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._on_appeal_tab
        )
        self.appeal_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Coach Reflection Button (wired to coach)
        self.coach_btn = tk.Button(
            actions_frame,
            text="🐱 Coach Reflection",
            font=("Segoe UI", 9, "bold"),
            bg="#059669",
            fg="#ffffff",
            activebackground="#047857",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._on_coach_reflection
        )
        self.coach_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Test Pounce Button
        test_btn = tk.Button(
            actions_frame,
            text="🐾 Test Pounce",
            font=("Segoe UI", 8),
            bg="#ffffff",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.on_test_pounce
        )
        test_btn.pack(side=tk.LEFT)

        # Toggle Agent Button
        self.toggle_btn = tk.Button(
            actions_frame,
            text="⏸ Pause",
            font=("Segoe UI", 8),
            bg="#ffffff",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._toggle_agent
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=(6, 0))

        # Pillow Theme Selector
        theme_row = tk.Frame(self.win, bg="#fffbf7")
        theme_row.pack(fill=tk.X, padx=16, pady=3)

        tk.Label(
            theme_row,
            text="Pillow Style:",
            font=("Segoe UI", 8, "bold"),
            bg="#fffbf7",
            fg="#451a03"
        ).pack(side=tk.LEFT, padx=(0, 8))

        for theme_name, label in [("pink", "🍓 Pink"), ("lavender", "💜 Lavender"), ("mint", "🍃 Mint")]:
            tk.Button(
                theme_row,
                text=label,
                font=("Segoe UI", 8),
                bg="#ffffff",
                relief=tk.SOLID,
                bd=1,
                padx=6,
                pady=1,
                cursor="hand2",
                command=lambda t=theme_name: self.on_style_change(t)
            ).pack(side=tk.LEFT, padx=3)

        # Real-time AI Agent Thought Feed
        feed_frame = tk.LabelFrame(
            self.win,
            text=" 📝 Real-Time AI Agent Thought Feed & Trace ",
            font=("Segoe UI", 9, "bold"),
            bg="#fffbf7",
            fg="#7c2d12",
            padx=10,
            pady=6
        )
        feed_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.thought_text = tk.Text(
            feed_frame,
            height=6,
            font=("Consolas", 8),
            bg="#18181b",
            fg="#4ade80",
            wrap=tk.WORD,
            bd=0
        )
        self.thought_text.pack(fill=tk.BOTH, expand=True)

    def _on_set_goal(self):
        val = self.goal_entry.get().strip()
        if val and hasattr(self.agent, "set_goal"):
            self.agent.set_goal(val)
            messagebox.showinfo("Focus Goal Updated", f"Active focus goal updated to:\n'{val}'")

    def _on_plan_session(self):
        req = self.goal_entry.get().strip()
        if not req:
            req = "Study session for exam preparation"

        self.agent._add_thought(f"Planning session with planner subagent for: '{req}'")
        try:
            plan = self.agent.engine.create_session_plan(req)
            title = plan.get("session_title", "Focus Session")
            blocks = plan.get("blocks", [])
            summary = f"Session Plan: {title}\nTotal: {plan.get('total_duration_hours', 2)}h\nBlocks: {len(blocks)}"
            messagebox.showinfo("AI Planner Output", summary)
            self.agent._add_thought(f"Session plan saved: {len(blocks)} study blocks created in memory/session_plan.md")
        except Exception as e:
            messagebox.showerror("Planner Error", str(e))

    def _on_appeal_tab(self):
        """Invokes appeals_judge subagent (Requirement 3)"""
        perc = getattr(self.agent, "active_tab_perception", {}) or {}
        curr_title = perc.get("title") or "Active Tab"
        curr_url = perc.get("url") or ""

        argument = simpledialog.askstring(
            "TabbyPatrol Appeals Judge",
            f"Enter justification for why this tab aligns with your goal:\n\nTab: '{curr_title[:45]}'\n\nArgument:",
            parent=self.win
        )

        if argument and argument.strip():
            self.agent._add_thought(f"Submitting appeal to appeals_judge for '{curr_title[:30]}': '{argument.strip()}'")
            try:
                result = self.agent.engine.submit_appeal(curr_title, curr_url, argument.strip())
                ruling = result.get("ruling", "denied").upper()
                grace = result.get("grace_minutes", 0)
                reason = result.get("reason", "")

                msg = f"Ruling: {ruling}\nGrace Period: {grace} minutes\nReason: {reason}"
                messagebox.showinfo("Appeals Judge Ruling", msg)
                self.agent._add_thought(f"Appeals Judge Verdict: {ruling} ({grace}m grace) - {reason}")
            except Exception as e:
                messagebox.showerror("Appeals Error", str(e))

    def _on_coach_reflection(self):
        """Invokes coach subagent (Requirement 3)"""
        self.agent._add_thought("Requesting session reflection from coach subagent...")
        try:
            report = self.agent.engine.generate_coach_reflection()
            # Show in modal dialog
            ref_win = tk.Toplevel(self.win)
            ref_win.title("🐱 TabbyPatrol Focus Reflection")
            ref_win.geometry("500x420")
            ref_win.configure(bg="#fffbf7")
            ref_win.attributes("-topmost", True)

            txt = tk.Text(ref_win, font=("Segoe UI", 9), bg="#ffffff", fg="#1f2937", wrap=tk.WORD, padx=12, pady=12)
            txt.pack(fill=tk.BOTH, expand=True)
            txt.insert(tk.END, report)
            txt.config(state=tk.DISABLED)

            self.agent._add_thought("Coach reflection report generated and saved to memory/reflection.md!")
        except Exception as e:
            messagebox.showerror("Coach Error", str(e))

    def _toggle_agent(self):
        self.agent.enabled = not self.agent.enabled
        if self.agent.enabled:
            self.status_lbl.config(text="● AI Agent Status: Active & Monitoring Desktop", fg="#15803d")
            self.toggle_btn.config(text="⏸ Pause")
        else:
            self.status_lbl.config(text="● AI Agent Status: Paused", fg="#b45309")
            self.toggle_btn.config(text="▶ Resume")

    def _update_loop(self):
        if not self.win.winfo_exists():
            return

        prod_count = getattr(self.agent, "productive_count", 0)
        self.swat_lbl.config(text=f"Wasteful Tasks Sniped: {self.agent.swat_count}   |   Productive Tasks Approved: {prod_count}")

        # Update Live Task Classification Card
        perc = getattr(self.agent, "active_tab_perception", None)
        if perc:
            t = perc.get("topic") or perc.get("title") or "Unknown Tab"
            if len(t) > 52:
                t = t[:49] + "..."
            self.perc_title_lbl.config(text=f"Content: {t}")

            domain = perc.get("domain") or perc.get("site") or "Web"
            self.perc_domain_lbl.config(text=f"Domain: {domain} (Monitored)")

            is_wasteful = perc.get("is_distraction", False)
            if is_wasteful:
                self.perc_badge_lbl.config(
                    text="🎯 WASTEFUL TASK (SNIPING)",
                    bg="#fee2e2",
                    fg="#dc2626"
                )
            else:
                self.perc_badge_lbl.config(
                    text="🟢 PRODUCTIVE TASK (APPROVED)",
                    bg="#dcfce7",
                    fg="#15803d"
                )

            about = perc.get("about", "Analyzing tab content...")
            self.perc_about_lbl.config(text=f"Analysis: {about}")

        # Update thought feed
        self.thought_text.delete("1.0", tk.END)
        recent = self.agent.thoughts[-15:]
        self.thought_text.insert(tk.END, "\n".join(recent))
        self.thought_text.see(tk.END)

        self.win.after(600, self._update_loop)
