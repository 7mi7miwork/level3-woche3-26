import tkinter as tk
from tkinter import messagebox
import random
import time

# ── Konfiguration ──────────────────────────────────────────────────────────────
DIFFICULTIES = {
    "Leicht":   {"rows": 9,  "cols": 9,  "mines": 10},
    "Mittel":   {"rows": 16, "cols": 16, "mines": 40},
    "Schwer":   {"rows": 16, "cols": 30, "mines": 99},
}

# Farben für Zahlen 1-8
NUMBER_COLORS = {
    1: "#1a73e8",
    2: "#2d9e2d",
    3: "#e83030",
    4: "#6a0dad",
    5: "#8b0000",
    6: "#008b8b",
    7: "#000000",
    8: "#808080",
}

BG        = "#1a1a2e"
BG2       = "#16213e"
ACCENT    = "#e94560"
CELL_HIDDEN   = "#0f3460"
CELL_HOVER    = "#1a4a7a"
CELL_REVEALED = "#0a0a1a"
CELL_BORDER   = "#0d2844"
CELL_MINE     = "#e94560"
FLAG_COLOR    = "#f5a623"
TEXT_COLOR    = "#e0e0e0"
FONT_TITLE    = ("Courier New", 22, "bold")
FONT_BTN      = ("Courier New", 11, "bold")
FONT_CELL     = ("Courier New", 13, "bold")
FONT_STATUS   = ("Courier New", 12)
FONT_DIFF     = ("Courier New", 10, "bold")

CELL_SIZE = 38
PADDING   = 3

class Minesweeper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.difficulty = tk.StringVar(value="Mittel")
        self.rows = 0
        self.cols = 0
        self.mines = 0

        self.board = []        # 0..8 or 'M'
        self.revealed = []
        self.flagged  = []
        self.buttons  = []

        self.game_over  = False
        self.start_time = None
        self.timer_id   = None
        self.first_click = True

        self._build_ui()
        self._new_game()

    # ── UI Construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG, pady=12)
        header.pack(fill="x", padx=20)

        tk.Label(header, text="⬛ MINESWEEPER", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack()

        # Difficulty bar
        diff_frame = tk.Frame(self, bg=BG2, pady=8)
        diff_frame.pack(fill="x", padx=0)

        tk.Label(diff_frame, text="SCHWIERIGKEIT:", font=FONT_DIFF,
                 bg=BG2, fg="#888").pack(side="left", padx=(20, 8))

        for d in DIFFICULTIES:
            rb = tk.Radiobutton(diff_frame, text=d, variable=self.difficulty,
                                value=d, command=self._new_game,
                                font=FONT_DIFF, bg=BG2, fg=TEXT_COLOR,
                                selectcolor=BG, activebackground=BG2,
                                activeforeground=ACCENT,
                                indicatoron=False,
                                relief="flat", padx=10, pady=4,
                                cursor="hand2")
            rb.pack(side="left", padx=4)

        # Status bar
        self.status_frame = tk.Frame(self, bg=BG, pady=8)
        self.status_frame.pack(fill="x", padx=20)

        self.mine_label  = tk.Label(self.status_frame, text="💣 10",
                                    font=FONT_STATUS, bg=BG, fg=FLAG_COLOR)
        self.mine_label.pack(side="left")

        self.new_btn = tk.Button(self.status_frame, text="[ NEU ]",
                                 font=FONT_BTN, bg=BG2, fg=ACCENT,
                                 activebackground=ACCENT, activeforeground=BG,
                                 relief="flat", bd=0, padx=12, pady=4,
                                 cursor="hand2", command=self._new_game)
        self.new_btn.pack(side="left", expand=True)

        self.time_label  = tk.Label(self.status_frame, text="⏱ 000",
                                    font=FONT_STATUS, bg=BG, fg=TEXT_COLOR)
        self.time_label.pack(side="right")

        # Board container
        self.board_outer = tk.Frame(self, bg=BG, padx=16, pady=10)
        self.board_outer.pack()

        self.board_frame = tk.Frame(self.board_outer, bg=CELL_BORDER)
        self.board_frame.pack()

        # Footer
        tk.Label(self, text="Linksklick: Aufdecken  |  Rechtsklick: Flagge",
                 font=("Courier New", 9), bg=BG, fg="#555").pack(pady=(0, 10))

    # ── Game Logic ─────────────────────────────────────────────────────────────

    def _new_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        cfg = DIFFICULTIES[self.difficulty.get()]
        self.rows  = cfg["rows"]
        self.cols  = cfg["cols"]
        self.mines = cfg["mines"]

        self.game_over   = False
        self.first_click = True
        self.start_time  = None

        self.board    = [[0]*self.cols for _ in range(self.rows)]
        self.revealed = [[False]*self.cols for _ in range(self.rows)]
        self.flagged  = [[False]*self.cols for _ in range(self.rows)]

        self._update_mine_counter()
        self.time_label.config(text="⏱ 000")
        self._build_board()

    def _place_mines(self, safe_r, safe_c):
        """Place mines after first click, avoiding the clicked cell."""
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)
                     if not (abs(r - safe_r) <= 1 and abs(c - safe_c) <= 1)]
        chosen = random.sample(positions, self.mines)
        for r, c in chosen:
            self.board[r][c] = 'M'

        # Calculate numbers
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    continue
                count = sum(
                    1 for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if (dr or dc) and
                    0 <= r+dr < self.rows and 0 <= c+dc < self.cols and
                    self.board[r+dr][c+dc] == 'M'
                )
                self.board[r][c] = count

    def _reveal(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if self.revealed[r][c] or self.flagged[r][c]:
            return

        self.revealed[r][c] = True
        self._draw_cell(r, c)

        if self.board[r][c] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc:
                        self._reveal(r+dr, c+dc)

    def _check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != 'M' and not self.revealed[r][c]:
                    return False
        return True

    def _count_flags(self):
        return sum(self.flagged[r][c]
                   for r in range(self.rows) for c in range(self.cols))

    def _update_mine_counter(self):
        remaining = self.mines - self._count_flags()
        self.mine_label.config(text=f"💣 {remaining:03d}")

    # ── Click Handlers ─────────────────────────────────────────────────────────

    def _on_left(self, r, c):
        if self.game_over or self.revealed[r][c] or self.flagged[r][c]:
            return

        if self.first_click:
            self.first_click = False
            self.start_time = time.time()
            self._tick()
            self._place_mines(r, c)

        if self.board[r][c] == 'M':
            self.game_over = True
            self._reveal_all_mines(r, c)
            self._stop_timer()
            self.after(400, lambda: messagebox.showinfo(
                "💥 BOOM!", "Erwischt! Spiel vorbei.\nDrücke [NEU] für eine neue Runde."))
        else:
            self._reveal(r, c)
            if self._check_win():
                self.game_over = True
                self._stop_timer()
                self._flag_remaining_mines()
                elapsed = int(time.time() - self.start_time) if self.start_time else 0
                self.after(300, lambda: messagebox.showinfo(
                    "🎉 GEWONNEN!", f"Alle Minen gefunden!\nZeit: {elapsed} Sekunden"))

    def _on_right(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return
        if self.first_click:
            return  # keine Flaggen vor erstem Klick

        self.flagged[r][c] = not self.flagged[r][c]
        self._draw_cell(r, c)
        self._update_mine_counter()

    def _on_chord(self, r, c):
        """Middle-click / double-click: chord reveal."""
        if not self.revealed[r][c] or self.board[r][c] == 0:
            return
        neighbors = [(r+dr, c+dc)
                     for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                     if (dr or dc) and 0 <= r+dr < self.rows and 0 <= c+dc < self.cols]
        flag_count = sum(1 for nr, nc in neighbors if self.flagged[nr][nc])
        if flag_count == self.board[r][c]:
            for nr, nc in neighbors:
                if not self.flagged[nr][nc]:
                    self._on_left(nr, nc)

    def _reveal_all_mines(self, hit_r, hit_c):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    self.revealed[r][c] = True
                    self._draw_cell(r, c, exploded=(r == hit_r and c == hit_c))

    def _flag_remaining_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M' and not self.flagged[r][c]:
                    self.flagged[r][c] = True
                    self._draw_cell(r, c)
        self._update_mine_counter()

    # ── Timer ──────────────────────────────────────────────────────────────────

    def _tick(self):
        if self.game_over or not self.start_time:
            return
        elapsed = int(time.time() - self.start_time)
        self.time_label.config(text=f"⏱ {min(elapsed, 999):03d}")
        self.timer_id = self.after(1000, self._tick)

    def _stop_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    # ── Board Rendering ────────────────────────────────────────────────────────

    def _build_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()
        self.buttons = []

        for r in range(self.rows):
            row_btns = []
            for c in range(self.cols):
                btn = tk.Canvas(self.board_frame,
                                width=CELL_SIZE - PADDING,
                                height=CELL_SIZE - PADDING,
                                highlightthickness=0,
                                cursor="hand2")
                btn.grid(row=r, column=c, padx=PADDING//2, pady=PADDING//2)
                btn.bind("<Button-1>",        lambda e, r=r, c=c: self._on_left(r, c))
                btn.bind("<Button-3>",        lambda e, r=r, c=c: self._on_right(r, c))
                btn.bind("<Double-Button-1>", lambda e, r=r, c=c: self._on_chord(r, c))
                btn.bind("<Button-2>",        lambda e, r=r, c=c: self._on_chord(r, c))
                btn.bind("<Enter>",           lambda e, r=r, c=c: self._on_hover(r, c, True))
                btn.bind("<Leave>",           lambda e, r=r, c=c: self._on_hover(r, c, False))
                row_btns.append(btn)
                self._draw_cell_canvas(btn, r, c)
            self.buttons.append(row_btns)

    def _draw_cell(self, r, c, exploded=False):
        self._draw_cell_canvas(self.buttons[r][c], r, c, exploded=exploded)

    def _draw_cell_canvas(self, canvas, r, c, hover=False, exploded=False):
        canvas.delete("all")
        w = CELL_SIZE - PADDING
        h = CELL_SIZE - PADDING

        if self.revealed[r][c]:
            val = self.board[r][c]
            if val == 'M':
                bg = CELL_MINE if exploded else "#2a0a0a"
                canvas.config(bg=bg)
                # mine symbol
                cx, cy = w//2, h//2
                canvas.create_oval(cx-9, cy-9, cx+9, cy+9,
                                   fill="#ff2020" if exploded else "#cc0000",
                                   outline="#ff6060" if exploded else "#880000", width=1)
                canvas.create_text(cx, cy, text="💣", font=("", 13))
            else:
                canvas.config(bg=CELL_REVEALED)
                if val > 0:
                    color = NUMBER_COLORS.get(val, "#ffffff")
                    canvas.create_text(w//2, h//2, text=str(val),
                                       font=FONT_CELL, fill=color)
                # subtle inset border
                canvas.create_rectangle(0, 0, w-1, h-1,
                                        outline="#1a1a30", width=1)
        elif self.flagged[r][c]:
            canvas.config(bg=CELL_HIDDEN)
            canvas.create_text(w//2, h//2, text="🚩", font=("", 14))
            self._draw_raised(canvas, w, h)
        else:
            bg = CELL_HOVER if hover else CELL_HIDDEN
            canvas.config(bg=bg)
            self._draw_raised(canvas, w, h)

    def _draw_raised(self, canvas, w, h):
        """Draw a subtle raised/beveled effect."""
        canvas.create_line(0, 0, w, 0,   fill="#1e5a8a", width=1)
        canvas.create_line(0, 0, 0, h,   fill="#1e5a8a", width=1)
        canvas.create_line(w-1, 0, w-1, h-1, fill="#071e33", width=1)
        canvas.create_line(0, h-1, w-1, h-1, fill="#071e33", width=1)

    def _on_hover(self, r, c, entering):
        if self.game_over or self.revealed[r][c] or self.flagged[r][c]:
            return
        self._draw_cell_canvas(self.buttons[r][c], r, c, hover=entering)


if __name__ == "__main__":
    app = Minesweeper()
    app.mainloop()