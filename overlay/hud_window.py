"""
TabbyPatrol - AI Agent HUD & Settings Panel
Allows configuring blocked keywords, viewing real-time AI reasoning thoughts,
displaying live task classification (PRODUCTIVE TASK vs WASTEFUL TASK) across monitored domains,
and switching pillow styles.
"""

import tkinter as tk
from tkinter import ttk


class AgentHudWindow:
    def __init__(self, parent, agent, on_style_change, on_test_pounce):
        self.agent = agent
        self.on_style_change = on_style_change
        self.on_test_pounce = on_test_pounce

        self.win = tk.Toplevel(parent)
        self.win.title("TabbyPatrol AI Agent - Command Center")
        self.win.geometry("470x620")
        self.win.configure(bg="#fffbf7")
        self.win.attributes("-topmost", True)

        self._build_ui()
        self._update_loop()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.win, bg="#fffbf7", pady=8)
        hdr.pack(fill=tk.X, padx=16)

        title = tk.Label(
            hdr,
            text="🐱 TabbyPatrol AI Agent",
            font=("Segoe UI", 15, "bold"),
            bg="#fffbf7",
            fg="#431407"
        )
        title.pack(anchor=tk.W)

        sub = tk.Label(
            hdr,
            text="Autonomous Task Classifier: Productive vs Wasteful Task Guardian",
            font=("Segoe UI", 9),
            bg="#fffbf7",
            fg="#9a3412"
        )
        sub.pack(anchor=tk.W)

        # Status Card
        card = tk.Frame(self.win, bg="#ffffff", highlightthickness=1, highlightbackground="#fed7aa", padx=12, pady=8)
        card.pack(fill=tk.X, padx=16, pady=4)

        self.status_lbl = tk.Label(
            card,
            text="● AI Agent Status: Active & Monitoring Desktop",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#15803d"
        )
        self.status_lbl.pack(anchor=tk.W)

        self.swat_lbl = tk.Label(
            card,
            text="Wasteful Tasks Sniped: 0   |   Productive Tasks Approved: 0",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#78350f"
        )
        self.swat_lbl.pack(anchor=tk.W, pady=2)

        # Real-Time Tab Task Classifier Card (Productive vs Wasteful)
        perc_card = tk.LabelFrame(
            self.win,
            text=" 🧠 Active Tab Task Classifier (Productive vs Wasteful) ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#7c2d12",
            padx=12,
            pady=8
        )
        perc_card.pack(fill=tk.X, padx=16, pady=4)

        # Prominent Task Badge (🟢 PRODUCTIVE TASK vs 🎯 WASTEFUL TASK)
        self.perc_badge_lbl = tk.Label(
            perc_card,
            text="🟢 PRODUCTIVE TASK",
            font=("Segoe UI", 10, "bold"),
            bg="#dcfce7",
            fg="#15803d",
            padx=8,
            pady=3,
            relief=tk.FLAT
        )
        self.perc_badge_lbl.pack(anchor=tk.W, pady=(0, 4))

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
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#1f2937",
            anchor=tk.W,
            wraplength=420,
            justify=tk.LEFT
        )
        self.perc_title_lbl.pack(fill=tk.X, pady=(2, 2))

        self.perc_about_lbl = tk.Label(
            perc_card,
            text="Analysis: Open an educational video, Reddit advice, or entertainment tab to see live task separation.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#4b5563",
            anchor=tk.W,
            wraplength=420,
            justify=tk.LEFT
        )
        self.perc_about_lbl.pack(fill=tk.X)

        # Quick Actions Row
        btn_row = tk.Frame(self.win, bg="#fffbf7")
        btn_row.pack(fill=tk.X, padx=16, pady=4)

        test_btn = tk.Button(
            btn_row,
            text="🐾 Test Tab Pounce",
            font=("Segoe UI", 9, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.on_test_pounce
        )
        test_btn.pack(side=tk.LEFT)

        self.toggle_btn = tk.Button(
            btn_row,
            text="⏸ Pause Agent",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#374151",
            relief=tk.SOLID,
            bd=1,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._toggle_agent
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=8)

        # Pillow Theme Selector
        theme_row = tk.Frame(self.win, bg="#fffbf7")
        theme_row.pack(fill=tk.X, padx=16, pady=3)

        tk.Label(
            theme_row,
            text="Pillow Style:",
            font=("Segoe UI", 9, "bold"),
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
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda t=theme_name: self.on_style_change(t)
            ).pack(side=tk.LEFT, padx=3)

        # Blocked Rules Section
        rules_frame = tk.LabelFrame(
            self.win,
            text=" Monitored & Blocked Domains ",
            font=("Segoe UI", 9, "bold"),
            bg="#fffbf7",
            fg="#7c2d12",
            padx=10,
            pady=6
        )
        rules_frame.pack(fill=tk.BOTH, expand=False, padx=16, pady=4)

        add_row = tk.Frame(rules_frame, bg="#fffbf7")
        add_row.pack(fill=tk.X, pady=(0, 4))

        self.kw_entry = tk.Entry(add_row, font=("Segoe UI", 9))
        self.kw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.kw_entry.bind("<Return>", lambda e: self._add_rule())

        add_btn = tk.Button(
            add_row,
            text="Add Rule",
            font=("Segoe UI", 9),
            bg="#ffffff",
            bd=1,
            relief=tk.SOLID,
            padx=8,
            cursor="hand2",
            command=self._add_rule
        )
        add_btn.pack(side=tk.LEFT)

        # Rules listbox with scrollbar
        list_container = tk.Frame(rules_frame, bg="#ffffff")
        list_container.pack(fill=tk.X)

        self.rules_list = tk.Listbox(
            list_container,
            height=3,
            font=("Segoe UI", 9),
            bd=1,
            relief=tk.SOLID
        )
        self.rules_list.pack(side=tk.LEFT, fill=tk.X, expand=True)

        del_btn = tk.Button(
            rules_frame,
            text="Remove Selected Rule",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#dc2626",
            bd=1,
            relief=tk.SOLID,
            pady=2,
            cursor="hand2",
            command=self._remove_rule
        )
        del_btn.pack(anchor=tk.E, pady=(2, 0))

        # Real-time AI Agent Thought Feed
        feed_frame = tk.LabelFrame(
            self.win,
            text=" Real-Time AI Agent Thought Feed (CV & Task Classification Log) ",
            font=("Segoe UI", 9, "bold"),
            bg="#fffbf7",
            fg="#7c2d12",
            padx=10,
            pady=6
        )
        feed_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.thought_text = tk.Text(
            feed_frame,
            height=5,
            font=("Consolas", 8),
            bg="#18181b",
            fg="#4ade80",
            wrap=tk.WORD,
            bd=0
        )
        self.thought_text.pack(fill=tk.BOTH, expand=True)

        self._refresh_rules_list()

    def _toggle_agent(self):
        self.agent.enabled = not self.agent.enabled
        if self.agent.enabled:
            self.status_lbl.config(text="● AI Agent Status: Active & Monitoring Desktop", fg="#15803d")
            self.toggle_btn.config(text="⏸ Pause Agent")
        else:
            self.status_lbl.config(text="● AI Agent Status: Paused", fg="#b45309")
            self.toggle_btn.config(text="▶ Resume Agent")

    def _add_rule(self):
        val = self.kw_entry.get().strip()
        if val:
            self.agent.add_keyword(val)
            self.kw_entry.delete(0, tk.END)
            self._refresh_rules_list()

    def _remove_rule(self):
        sel = self.rules_list.curselection()
        if sel:
            kw = self.rules_list.get(sel[0])
            self.agent.remove_keyword(kw)
            self._refresh_rules_list()

    def _refresh_rules_list(self):
        self.rules_list.delete(0, tk.END)
        for kw in self.agent.blocked_keywords:
            self.rules_list.insert(tk.END, kw)

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
