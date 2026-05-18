"""Tkinter interface for the Dog Cognitive Experiment."""

import tkinter as tk
from tkinter import messagebox

from evaluator import (
    evaluate_state,
    generate_cognitive_summary,
    generate_reflection,
    load_memory,
    process_experience,
    save_memory,
)


BACKGROUND = "#9be3d1"
TEXT_DARK = "#124d66"
TEXT_MUTED = "#2f5d6f"
PANEL_BG = "#edf6f8"
INPUT_BG = "#ffffff"
PRIMARY_BUTTON = "#0b5570"
SECONDARY_BUTTON = "#0f9277"


class RoundedButton(tk.Canvas):
    """Canvas-based rounded button used to match the visual reference."""

    def __init__(self, master, text, command, width=170, height=44, bg=PRIMARY_BUTTON):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=master["bg"],
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self.base_color = bg
        self.hover_color = self._darken(bg)
        self.text = text
        self.width = width
        self.height = height
        self.draw(self.base_color)
        self.bind("<Button-1>", lambda _event: self.command())
        self.bind("<Enter>", lambda _event: self.draw(self.hover_color))
        self.bind("<Leave>", lambda _event: self.draw(self.base_color))

    def _darken(self, color):
        channels = [int(color[index:index + 2], 16) for index in (1, 3, 5)]
        return "#" + "".join(f"{max(0, channel - 24):02x}" for channel in channels)

    def draw(self, color):
        self.delete("all")
        self.create_rounded_rectangle(1, 1, self.width - 1, self.height - 1, 7, fill=color, outline=color)
        self.create_text(
            self.width / 2,
            self.height / 2,
            text=self.text,
            fill="white",
            font=("Segoe UI", 11, "bold"),
        )

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class DogCognitiveApp:
    """Main application window and live memory dashboard."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DOG COGNITIVE EXPERIMENT")
        self.root.geometry("970x720")
        self.root.minsize(900, 680)
        self.root.configure(bg=BACKGROUND)

        self.memory = load_memory()
        self.memory["current_assessment"] = evaluate_state(self.memory.get("fear_total", 0))
        save_memory(self.memory)

        self.status_vars = {
            "fear": tk.StringVar(),
            "confidence": tk.StringVar(),
            "assessment": tk.StringVar(),
            "reflection": tk.StringVar(),
        }

        self.build_layout()
        self.refresh_interface()

    def run(self):
        self.root.mainloop()

    def build_layout(self):
        container = tk.Frame(self.root, bg=BACKGROUND)
        container.pack(fill="both", expand=True, padx=82, pady=(50, 34))

        self.build_header(container)
        self.build_input_panel(container)
        self.build_status_grid(container)
        self.build_history_panel(container)

    def build_header(self, parent):
        header = tk.Frame(parent, bg=BACKGROUND)
        header.pack(fill="x", pady=(0, 58))

        title_area = tk.Frame(header, bg=BACKGROUND)
        title_area.pack(side="left", fill="x", expand=True)

        tk.Label(
            title_area,
            text="DOG COGNITIVE EXPERIMENT",
            bg=BACKGROUND,
            fg=TEXT_DARK,
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="Experimental simulation of cognitive adaptation",
            bg=BACKGROUND,
            fg=TEXT_MUTED,
            font=("Segoe UI", 15),
        ).pack(anchor="w", pady=(8, 0))

        tk.Label(
            header,
            text="🐶",
            bg=BACKGROUND,
            fg=TEXT_DARK,
            font=("Segoe UI Emoji", 62),
        ).pack(side="right", padx=(16, 20))

    def build_input_panel(self, parent):
        panel = self.make_panel(parent, padx=22, pady=20)
        panel.pack(fill="x", pady=(0, 18))

        tk.Label(
            panel,
            text="Enter a dog-related experience",
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")

        self.input_text = tk.Text(
            panel,
            height=3,
            wrap="word",
            bg=INPUT_BG,
            fg="#123744",
            insertbackground=TEXT_DARK,
            relief="flat",
            padx=12,
            pady=10,
            font=("Segoe UI", 12),
        )
        self.input_text.pack(fill="x", pady=(12, 16))

        buttons = tk.Frame(panel, bg=PANEL_BG)
        buttons.pack(anchor="w")
        RoundedButton(buttons, "SUBMIT", self.submit_experience).pack(side="left", padx=(0, 18))
        RoundedButton(buttons, "GENERATE ASSESSMENT", self.show_assessment, width=190, bg=SECONDARY_BUTTON).pack(side="left")

    def build_status_grid(self, parent):
        grid = tk.Frame(parent, bg=BACKGROUND)
        grid.pack(fill="x", pady=(0, 18))

        state_panel = self.make_panel(grid, padx=22, pady=20)
        state_panel.pack(side="left", fill="both", expand=True, padx=(0, 9))

        reflection_panel = self.make_panel(grid, padx=22, pady=20)
        reflection_panel.pack(side="left", fill="both", expand=True, padx=(9, 0))

        tk.Label(
            state_panel,
            text="STATE PANEL",
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        self.add_status_line(state_panel, "FEAR TOTAL:", self.status_vars["fear"])
        self.add_status_line(state_panel, "BELIEF CONFIDENCE:", self.status_vars["confidence"])
        self.add_status_line(state_panel, "CURRENT ASSESSMENT:", self.status_vars["assessment"], wrap=360)

        tk.Label(
            reflection_panel,
            text="COGNITIVE REFLECTION",
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            reflection_panel,
            textvariable=self.status_vars["reflection"],
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 12),
            wraplength=360,
            justify="left",
        ).pack(anchor="w")

    def build_history_panel(self, parent):
        panel = self.make_panel(parent, padx=22, pady=18)
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="RECENT HISTORY",
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")

        self.history_box = tk.Text(
            panel,
            height=7,
            wrap="word",
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            relief="flat",
            font=("Segoe UI", 10),
            padx=0,
            pady=8,
        )
        self.history_box.pack(fill="both", expand=True)
        self.history_box.configure(state="disabled")

    def make_panel(self, parent, padx, pady):
        return tk.Frame(parent, bg=PANEL_BG, padx=padx, pady=pady, highlightthickness=0)

    def add_status_line(self, parent, title, variable, wrap=None):
        tk.Label(
            parent,
            text=title,
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(6, 0))
        tk.Label(
            parent,
            textvariable=variable,
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold"),
            wraplength=wrap,
            justify="left",
        ).pack(anchor="w")

    def submit_experience(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty experience", "Enter an experience before submitting.")
            return

        self.memory, _result = process_experience(text, self.memory)
        self.input_text.delete("1.0", "end")
        self.refresh_interface()

    def show_assessment(self):
        summary = (
            f"Fear total: {self.memory.get('fear_total', 0)}\n"
            f"Belief confidence: {self.memory.get('belief_confidence', 0)}%\n\n"
            f"Current assessment:\n{self.memory.get('current_assessment', '')}\n\n"
            f"Cognitive summary:\n{generate_cognitive_summary(self.memory)}"
        )
        messagebox.showinfo("Cognitive Assessment", summary)

    def refresh_interface(self):
        fear = self.memory.get("fear_total", 0)
        confidence = self.memory.get("belief_confidence", 0)
        assessment = self.memory.get("current_assessment") or evaluate_state(fear)

        self.status_vars["fear"].set(str(fear))
        self.status_vars["confidence"].set(f"{confidence}%")
        self.status_vars["assessment"].set(f"\"{assessment}\"")
        self.status_vars["reflection"].set(generate_reflection(self.memory))

        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        for experience in self.memory.get("experiences", [])[-5:]:
            self.history_box.insert(
                "end",
                f"- {experience.get('text', '')}\n"
                f"  impact: {experience.get('impact', 0)} | "
                f"resulting fear: {experience.get('resulting_fear', 0)}\n\n",
            )
        self.history_box.configure(state="disabled")
