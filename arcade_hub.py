#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

ROOT_DIR = Path(__file__).resolve().parent
COMMON_ENTRYPOINTS = [
    "main.py",
    "game.py",
    "launcher.py",
    "__main__.py",
    "app.py",
    "main_game.py",
]
SKIP_NAMES = {".git", ".venv", "__pycache__", ".idea", ".vscode"}


def discover_games(base_dir: Path):
    games = []
    for child in sorted(base_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        if child.name in SKIP_NAMES or child.name.startswith("."):
            continue

        script = None
        for candidate in COMMON_ENTRYPOINTS:
            possible = child / candidate
            if possible.is_file():
                script = possible
                break

        if script is None:
            py_files = sorted(
                p for p in child.iterdir() if p.is_file() and p.suffix.lower() == ".py"
            )
            if py_files:
                script = py_files[0]

        if script is None:
            continue

        title = child.name.replace("_", " ")
        description = ""
        readme = child / "README.md"
        if readme.is_file():
            try:
                lines = readme.read_text(encoding="utf-8", errors="ignore").splitlines()
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and not stripped.startswith("["):
                        description = stripped
                        break
            except Exception:
                description = "Play this game"
        if not description:
            description = "Play this game"

        games.append({
            "name": title,
            "path": child,
            "script": script,
            "readme": readme if readme.is_file() else None,
            "description": description,
        })

    return games


def launch_game(script_path: Path, game_dir: Path):
    try:
        env = os.environ.copy()
        env["TK_SILENCE_DEPRECATION"] = "1"
        subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(game_dir),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
        return True
    except Exception as exc:
        messagebox.showerror(
            "Launch failed",
            f"Unable to start {game_dir.name}:\n{exc}",
        )
        return False


def open_readme(readme_path: Path):
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(readme_path)])
        elif os.name == "nt":
            startfile = getattr(os, "startfile", None)
            if startfile is None:
                raise OSError("The operating system's file opener is unavailable.")
            startfile(str(readme_path))
        else:
            subprocess.Popen(["xdg-open", str(readme_path)])
    except OSError as exc:
        messagebox.showerror(
            "Unable to open README",
            f"Unable to open {readme_path}:\n{exc}",
        )


class ArcadeHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Arcade Hub")
        self.root.configure(background="#f3f4f6")
        self.root.geometry("980x640")
        self.root.minsize(780, 420)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f3f4f6")
        self.style.configure("TLabel", background="#f3f4f6")
        self.style.configure("TButton", background="#ffffff")

        container = tk.Frame(root, bg="#f3f4f6", padx=18, pady=18)
        container.pack(fill="both", expand=True)

        top = tk.Frame(container, bg="#f3f4f6")
        top.pack(fill="x", pady=(0, 12))

        title_label = tk.Label(top, text="Python Arcade Hub", font=("Segoe UI", 22, "bold"), fg="#111827", bg="#f3f4f6")
        title_label.pack(anchor="w")
        subtitle = tk.Label(top, text="Choose a game and launch it in its own window.", font=("Segoe UI", 10), fg="#4b5563", bg="#f3f4f6")
        subtitle.pack(anchor="w", pady=(4, 0))

        actions = tk.Frame(container, bg="#f3f4f6")
        actions.pack(fill="x", pady=(0, 14))
        refresh_btn = tk.Button(actions, text="Refresh Games", command=self.refresh_games, bg="#ffffff", fg="#111827", activebackground="#e5e7eb")
        refresh_btn.pack(side="left")
        quit_btn = tk.Button(actions, text="Quit", command=root.destroy, bg="#ffffff", fg="#111827", activebackground="#e5e7eb")
        quit_btn.pack(side="right")

        self.canvas = tk.Canvas(container, bg="#f3f4f6", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.content = tk.Frame(self.canvas, bg="#f3f4f6")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._on_frame_configure)
        self.refresh_games()
        self._bind_scroll_events(root)

    def _on_canvas_resize(self, event):
        if self.canvas_window:
            self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        event_num = getattr(event, "num", None)
        if event_num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event_num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            delta = getattr(event, "delta", 0)
            if delta:
                direction = -1 if delta > 0 else 1
                self.canvas.yview_scroll(direction, "units")

    def _bind_scroll_events(self, widget):
        for sequence in ("<MouseWheel>", "<Shift-MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(sequence, self._on_mousewheel, add="+")
        for child in widget.winfo_children():
            self._bind_scroll_events(child)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def refresh_games(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        games = discover_games(ROOT_DIR)
        if not games:
            none_label = tk.Label(self.content, text="No playable game folders were found in this project.", font=("Segoe UI", 11), bg="#f3f4f6", fg="#374151")
            none_label.pack(pady=24)
            return

        for index, game in enumerate(games):
            card = tk.Frame(self.content, bg="#ffffff", padx=14, pady=12, highlightbackground="#d1d5db", highlightthickness=1)
            card.pack(fill="x", pady=(0, 10), padx=0)

            title = tk.Label(card, text=game["name"], font=("Segoe UI", 14, "bold"), fg="#111827", bg="#ffffff", justify="left")
            title.pack(anchor="w", pady=(0, 4))

            meta = tk.Label(card, text=game["description"], wraplength=700, justify="left", font=("Segoe UI", 9), fg="#4b5563", bg="#ffffff")
            meta.pack(anchor="w", pady=(0, 8))

            button_row = tk.Frame(card, bg="#ffffff")
            button_row.pack(anchor="w")

            action = tk.Button(button_row, text="Play", command=lambda selected=game: self.launch_selected(selected), bg="#f3f4f6", fg="#111827", activebackground="#e5e7eb", relief="flat")
            action.pack(side="left")

            readme_path = game["readme"]
            readme_btn = tk.Button(
                button_row,
                text="Read Me",
                command=lambda path=readme_path: open_readme(path),
                state="normal" if readme_path else "disabled",
                bg="#f3f4f6",
                fg="#111827",
                activebackground="#e5e7eb",
                relief="flat",
            )
            readme_btn.pack(side="left", padx=(8, 0))

            if index < len(games) - 1:
                separator = tk.Frame(self.content, height=1, bg="#e5e7eb")
                separator.pack(fill="x", pady=(0, 6))

        self._bind_scroll_events(self.content)

    def launch_selected(self, game):
        if launch_game(game["script"], game["path"]):
            self.root.withdraw()
            self.root.deiconify()


if __name__ == "__main__":
    if not ROOT_DIR.exists():
        raise FileNotFoundError(f"Project root not found: {ROOT_DIR}")

    root = tk.Tk()
    app = ArcadeHubApp(root)
    root.mainloop()
