"""Tkinter-based prototype UI for Thalos Prime."""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from .thalos_sbi_core import SBIConfig, ThalosSBICore


class MatrixBackground(tk.Canvas):
    def __init__(self, master: tk.Widget, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        self.columns = []
        self.running = False
        self.speed_ms = 120

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._setup_columns()
        self._animate()

    def stop(self) -> None:
        self.running = False

    def _setup_columns(self) -> None:
        self.columns.clear()
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        col_width = 14
        for x in range(0, width, col_width):
            y = random.randint(-height, 0)
            speed = random.randint(2, 5)
            self.columns.append({"x": x, "y": y, "speed": speed})

    def _animate(self) -> None:
        if not self.running:
            return
        self.delete("matrix")
        width = self.winfo_width()
        height = self.winfo_height()
        for column in self.columns:
            column["y"] += column["speed"]
            if column["y"] > height:
                column["y"] = random.randint(-height, 0)
                column["speed"] = random.randint(2, 5)
            text = "".join(random.choice("01") for _ in range(8))
            self.create_text(
                column["x"],
                column["y"],
                text=text,
                fill="#3aff3a",
                font=("Courier", 10),
                anchor="nw",
                tags="matrix",
            )
        self.after(self.speed_ms, self._animate)

    def set_speed(self, speed_ms: int) -> None:
        self.speed_ms = max(40, min(300, speed_ms))


class ThalosPrimeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Thalos Prime")
        self.geometry("900x600")
        self.minsize(720, 480)
        self.configure(bg="black")

        self.core = ThalosSBICore(SBIConfig(max_context_items=100))

        self._build_layout()
        self._bind_events()
        self.matrix.start()

    def _build_layout(self) -> None:
        self.matrix = MatrixBackground(self, bg="black", highlightthickness=0)
        self.matrix.place(relwidth=1, relheight=1)

        self.toolbar = tk.Frame(self, bg="#111111", width=120)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        self.settings_label = tk.Label(
            self.toolbar,
            text="Settings",
            bg="#111111",
            fg="#9cf59c",
            font=("Courier", 10, "bold"),
        )
        self.settings_label.pack(pady=(12, 4))

        self.font_size = tk.IntVar(value=12)
        self.font_style = tk.StringVar(value="Courier")

        ttk.Label(self.toolbar, text="Font size", background="#111111", foreground="#9cf59c").pack(
            pady=(8, 2)
        )
        self.size_scale = ttk.Scale(
            self.toolbar,
            from_=4,
            to=32,
            orient=tk.HORIZONTAL,
            command=self._update_font,
        )
        self.size_scale.set(self.font_size.get())
        self.size_scale.pack(fill=tk.X, padx=8)

        ttk.Label(self.toolbar, text="Font", background="#111111", foreground="#9cf59c").pack(
            pady=(8, 2)
        )
        self.font_box = ttk.Combobox(
            self.toolbar,
            textvariable=self.font_style,
            values=["Courier", "Consolas", "Arial", "Helvetica"],
            state="readonly",
        )
        self.font_box.pack(fill=tk.X, padx=8)
        self.font_box.bind("<<ComboboxSelected>>", lambda _: self._update_font())

        ttk.Label(
            self.toolbar, text="Matrix speed", background="#111111", foreground="#9cf59c"
        ).pack(pady=(8, 2))
        self.speed_scale = ttk.Scale(
            self.toolbar,
            from_=60,
            to=240,
            orient=tk.HORIZONTAL,
            command=self._update_speed,
        )
        self.speed_scale.set(self.matrix.speed_ms)
        self.speed_scale.pack(fill=tk.X, padx=8)

        self.main_panel = tk.Frame(self, bg="#0b0b0b", highlightbackground="#2f2f2f", highlightthickness=1)
        self.main_panel.place(relx=0.15, rely=0.1, relwidth=0.7, relheight=0.8)

        self.output = tk.Text(
            self.main_panel,
            bg="#0b0b0b",
            fg="#c8f7c5",
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=(self.font_style.get(), self.font_size.get()),
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 6))

        self.input_box = tk.Entry(
            self.main_panel,
            bg="#111111",
            fg="#c8f7c5",
            insertbackground="#c8f7c5",
            font=(self.font_style.get(), self.font_size.get()),
        )
        self.input_box.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.action_row = tk.Frame(self.main_panel, bg="#0b0b0b")
        self.action_row.pack(pady=(0, 12))

        self.submit_button = tk.Button(
            self.action_row,
            text="Submit",
            command=self._submit,
            bg="#1c1c1c",
            fg="#9cf59c",
            relief=tk.FLAT,
        )
        self.submit_button.pack(side=tk.LEFT, padx=6)

        self.clear_button = tk.Button(
            self.action_row,
            text="Clear",
            command=self._clear_output,
            bg="#1c1c1c",
            fg="#9cf59c",
            relief=tk.FLAT,
        )
        self.clear_button.pack(side=tk.LEFT, padx=6)

        self.status_tab = tk.Button(
            self,
            text="System Status",
            command=self._toggle_status,
            bg="#1c1c1c",
            fg="#9cf59c",
            relief=tk.FLAT,
        )
        self.status_tab.place(relx=0.86, rely=0.4, width=120, height=32)

        self.status_panel = tk.Frame(self, bg="#0b0b0b", highlightbackground="#2f2f2f", highlightthickness=1)
        self.status_label = tk.Label(
            self.status_panel,
            text="Core: Prototype\nMemory: 0\nMode: SBI",
            bg="#0b0b0b",
            fg="#c8f7c5",
            font=("Courier", 10),
            justify=tk.LEFT,
        )
        self.status_label.pack(padx=10, pady=10)
        self.status_visible = False

    def _bind_events(self) -> None:
        self.input_box.bind("<Return>", lambda _: self._submit())
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is self:
            self.matrix._setup_columns()

    def _update_font(self, *_: object) -> None:
        self.font_size.set(int(self.size_scale.get()))
        font = (self.font_style.get(), self.font_size.get())
        self.output.configure(font=font)
        self.input_box.configure(font=font)

    def _update_speed(self, *_: object) -> None:
        self.matrix.set_speed(int(self.speed_scale.get()))

    def _toggle_status(self) -> None:
        if self.status_visible:
            self.status_panel.place_forget()
        else:
            self.status_panel.place(relx=0.82, rely=0.2, relwidth=0.17, relheight=0.25)
        self.status_visible = not self.status_visible

    def _clear_output(self) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)

    def _submit(self) -> None:
        prompt = self.input_box.get().strip()
        if not prompt:
            return
        response = self.core.generate(prompt)
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, f"\n> {prompt}\n{response}\n")
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)
        self.input_box.delete(0, tk.END)
        self.status_label.configure(
            text=(
                f"Core: Prototype\nMemory: {len(self.core.memory.history)}\nMode: SBI"
            )
        )


def main() -> None:
    app = ThalosPrimeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
