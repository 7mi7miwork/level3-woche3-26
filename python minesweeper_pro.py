import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

# ══════════════════════════════════════════════════════════════════════════════
#  KONSTANTEN
# ══════════════════════════════════════════════════════════════════════════════

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "ms_scores.json")

# Level-Definitionen: name, rows, cols, mines, mine_density_hint
LEVELS = [
    {"id": 1,  "name": "Rookie",      "rows": 8,  "cols": 8,  "mines": 8,   "powerups": 2},
    {"id": 2,  "name": "Scout",       "rows": 9,  "cols": 9,  "mines": 12,  "powerups": 2},
    {"id": 3,  "name": "Soldier",     "rows": 10, "cols": 10, "mines": 15,  "powerups": 3},
    {"id": 4,  "name": "Veteran",     "rows": 12, "cols": 12, "mines": 22,  "powerups": 3},
    {"id": 5,  "name": "Elite",       "rows": 14, "cols": 14, "mines": 35,  "powerups": 3},
    {"id": 6,  "name": "Kommandant",  "rows": 16, "cols": 16, "mines": 50,  "powerups": 4},
    {"id": 7,  "name": "General",     "rows": 16, "cols": 20, "mines": 65,  "powerups": 4},
    {"id": 8,  "name": "Legende",     "rows": 16, "cols": 24, "mines": 85,  "powerups": 4},
    {"id": 9,  "name": "Mythos",      "rows": 16, "cols": 28, "mines": 100, "powerups": 5},
    {"id": 10, "name": "NIGHTMARE",   "rows": 20, "cols": 30, "mines": 140, "powerups": 5},
]

# Powerups
POWERUPS = {
    "radar":    {"label": "🔍 RADAR",    "desc": "Zeigt 3 sichere Felder an",         "color": "#00c8ff", "uses": 1},
    "shield":   {"label": "🛡 SCHILD",   "desc": "Überlebst 1 Mine",                  "color": "#44ff88", "uses": 1},
    "scanner":  {"label": "🧲 SCANNER",  "desc": "Zeigt alle Minen-Nummern kurz auf", "color": "#ff9900", "uses": 1},
    "defuse":   {"label": "✂ ENTSCHÄRFEN","desc": "Entfernt 1 zufällige Mine",         "color": "#ff44aa", "uses": 1},
}

# Farben
BG            = "#0d1117"
BG2           = "#161b22"
BG3           = "#21262d"
ACCENT        = "#f78166"
ACCENT2       = "#79c0ff"
CELL_HIDDEN   = "#1c2a3a"
CELL_HOVER    = "#243a50"
CELL_REVEALED = "#090d11"
CELL_BORDER   = "#0d1f30"
FLAG_COLOR    = "#f5a623"
TEXT_COLOR    = "#c9d1d9"
DIM_COLOR     = "#484f58"
GOLD          = "#ffd700"
GREEN         = "#3fb950"
RED           = "#f85149"

NUMBER_COLORS = {
    1: "#79c0ff", 2: "#56d364", 3: "#f85149",
    4: "#d2a8ff", 5: "#ffa657", 6: "#39d5cf",
    7: "#e6edf3", 8: "#8b949e",
}

FONT_TITLE   = ("Courier New", 18, "bold")
FONT_BOLD    = ("Courier New", 11, "bold")
FONT_SMALL   = ("Courier New", 9)
FONT_TINY    = ("Courier New", 8)
FONT_CELL    = ("Courier New", 12, "bold")
FONT_STATUS  = ("Courier New", 11, "bold")
FONT_MEGA    = ("Courier New", 28, "bold")
FONT_LEVEL   = ("Courier New", 10, "bold")

CELL_SIZE = 36
PAD       = 2


# ══════════════════════════════════════════════════════════════════════════════
#  HIGHSCORE MANAGER
# ══════════════════════════════════════════════════════════════════════════════

def load_scores():
    try:
        with open(HIGHSCORE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_scores(scores):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(scores, f)
    except Exception:
        pass

def record_score(level_id, seconds):
    scores = load_scores()
    key = str(level_id)
    old = scores.get(key, 9999)
    if seconds < old:
        scores[key] = seconds
        save_scores(scores)
        return True  # new record
    return False

def get_best(level_id):
    scores = load_scores()
    return scores.get(str(level_id), None)


# ══════════════════════════════════════════════════════════════════════════════
#  HAUPT-APP
# ══════════════════════════════════════════════════════════════════════════════

class Minesweeper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💣 Minesweeper PRO")
        self.resizable(False, False)
        self.configure(bg=BG)

        # State
        self.current_level_idx = 0
        self.unlocked_level    = 0  # höchstes freigeschaltetes Level (index)
        self.score             = 0
        self.total_score       = 0
        self.lives             = 3
        self.combo             = 0
        self.combo_timer_id    = None
        self.shield_active     = False
        self.active_powerup    = None  # aktuell ausgewähltes Powerup zum Einsetzen
        self.powerup_stock     = {}    # powerup_key -> count
        self.scanner_active    = False
        self.scanner_timer     = None

        # Board state
        self.rows = self.cols = self.mines = 0
        self.board = self.revealed = self.flagged = self.buttons = []
        self.game_over   = False
        self.first_click = True
        self.start_time  = None
        self.timer_id    = None

        self._build_ui()
        self._load_level(0)

    # ──────────────────────────────────────────────────────────────────────────
    #  UI
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── TOP BAR ──
        top = tk.Frame(self, bg=BG2, pady=6)
        top.pack(fill="x")

        tk.Label(top, text="💣 MINESWEEPER PRO", font=FONT_TITLE,
                 bg=BG2, fg=ACCENT).pack(side="left", padx=16)

        right_top = tk.Frame(top, bg=BG2)
        right_top.pack(side="right", padx=16)

        self.total_score_lbl = tk.Label(right_top, text="★ 0",
                                        font=FONT_BOLD, bg=BG2, fg=GOLD)
        self.total_score_lbl.pack(side="right", padx=8)

        tk.Button(right_top, text="🏆 SCORES", font=FONT_SMALL,
                  bg=BG3, fg=ACCENT2, activebackground=ACCENT2,
                  activeforeground=BG, relief="flat", padx=8, pady=3,
                  cursor="hand2", command=self._show_highscores).pack(side="right")

        # ── LEVEL BAR ──
        level_outer = tk.Frame(self, bg=BG3, pady=4)
        level_outer.pack(fill="x")

        self.level_canvas = tk.Canvas(level_outer, bg=BG3,
                                      height=36, highlightthickness=0)
        self.level_canvas.pack(fill="x", padx=10)
        self._draw_level_bar()

        # ── STATUS BAR ──
        status = tk.Frame(self, bg=BG, pady=6)
        status.pack(fill="x", padx=12)

        # Minen
        self.mine_lbl = tk.Label(status, text="💣 000",
                                 font=FONT_STATUS, bg=BG, fg=FLAG_COLOR)
        self.mine_lbl.pack(side="left", padx=6)

        # Leben
        self.lives_lbl = tk.Label(status, text="❤❤❤",
                                  font=FONT_STATUS, bg=BG, fg=RED)
        self.lives_lbl.pack(side="left", padx=6)

        # NEU-Button
        self.new_btn = tk.Button(status, text="↺ NEU",
                                 font=FONT_BOLD, bg=BG3, fg=ACCENT,
                                 activebackground=ACCENT, activeforeground=BG,
                                 relief="flat", padx=10, pady=3,
                                 cursor="hand2", command=self._restart_level)
        self.new_btn.pack(side="left", expand=True)

        # Combo
        self.combo_lbl = tk.Label(status, text="",
                                  font=FONT_STATUS, bg=BG, fg=GOLD)
        self.combo_lbl.pack(side="left", padx=6)

        # Zeit
        self.time_lbl = tk.Label(status, text="⏱ 000",
                                 font=FONT_STATUS, bg=BG, fg=TEXT_COLOR)
        self.time_lbl.pack(side="right", padx=6)

        # Score
        self.score_lbl = tk.Label(status, text="⭐ 0",
                                  font=FONT_STATUS, bg=BG, fg=ACCENT2)
        self.score_lbl.pack(side="right", padx=6)

        # ── POWERUP BAR ──
        self.pu_frame = tk.Frame(self, bg=BG2, pady=6)
        self.pu_frame.pack(fill="x")
        self._build_powerup_bar()

        # ── BOARD ──
        self.board_outer = tk.Frame(self, bg=BG, padx=10, pady=8)
        self.board_outer.pack()
        self.board_frame = tk.Frame(self.board_outer, bg=CELL_BORDER)
        self.board_frame.pack()

        # ── FOOTER ──
        self.footer_lbl = tk.Label(self, font=FONT_TINY, bg=BG, fg=DIM_COLOR,
            text="LK: Aufdecken  |  RK: Flagge  |  Doppelklick: Chord-Aufdecken")
        self.footer_lbl.pack(pady=(2, 6))

    def _draw_level_bar(self):
        self.level_canvas.delete("all")
        self.after(10, self._draw_level_bar_real)

    def _draw_level_bar_real(self):
        self.level_canvas.delete("all")
        w = self.level_canvas.winfo_width()
        if w < 10:
            self.after(50, self._draw_level_bar_real)
            return
        n = len(LEVELS)
        slot_w = w / n
        for i, lv in enumerate(LEVELS):
            x = i * slot_w
            locked = i > self.unlocked_level
            current = i == self.current_level_idx
            if current:
                bg = ACCENT
                fg = BG
            elif locked:
                bg = BG3
                fg = DIM_COLOR
            else:
                bg = "#1e3a2a"
                fg = GREEN
            self.level_canvas.create_rectangle(x+2, 2, x+slot_w-2, 34,
                                                fill=bg, outline="", width=0)
            sym = "🔒" if locked else f"{lv['id']}"
            self.level_canvas.create_text(x + slot_w/2, 12,
                                           text=sym, font=FONT_LEVEL, fill=fg)
            short = lv["name"][:6]
            self.level_canvas.create_text(x + slot_w/2, 26,
                                           text=short, font=FONT_TINY, fill=fg)
            if not locked:
                self.level_canvas.tag_bind(
                    self.level_canvas.create_rectangle(x+2, 2, x+slot_w-2, 34,
                                                        fill="", outline=""),
                    "<Button-1>",
                    lambda e, idx=i: self._load_level(idx) if idx <= self.unlocked_level else None
                )

    def _build_powerup_bar(self):
        for w in self.pu_frame.winfo_children():
            w.destroy()

        tk.Label(self.pu_frame, text="POWERUPS:", font=FONT_TINY,
                 bg=BG2, fg=DIM_COLOR).pack(side="left", padx=(12, 4))

        self.pu_buttons = {}
        for key, pu in POWERUPS.items():
            count = self.powerup_stock.get(key, 0)
            state = "normal" if count > 0 else "disabled"
            relief = "sunken" if self.active_powerup == key else "flat"
            color  = pu["color"] if count > 0 else DIM_COLOR
            btn = tk.Button(self.pu_frame,
                            text=f"{pu['label']} ×{count}",
                            font=FONT_TINY,
                            bg=BG3, fg=color,
                            activebackground=pu["color"], activeforeground=BG,
                            relief=relief, bd=1, padx=8, pady=3,
                            cursor="hand2" if count > 0 else "arrow",
                            state=state,
                            command=lambda k=key: self._toggle_powerup(k))
            btn.pack(side="left", padx=4)
            btn.bind("<Enter>", lambda e, k=key: self._show_pu_tooltip(k))
            btn.bind("<Leave>", self._hide_pu_tooltip)
            self.pu_buttons[key] = btn

        # Tooltip label
        self.pu_tip = tk.Label(self.pu_frame, text="", font=FONT_TINY,
                               bg=BG2, fg=ACCENT2)
        self.pu_tip.pack(side="right", padx=12)

    def _show_pu_tooltip(self, key):
        self.pu_tip.config(text=POWERUPS[key]["desc"])

    def _hide_pu_tooltip(self, e=None):
        self.pu_tip.config(text="")

    def _toggle_powerup(self, key):
        if self.powerup_stock.get(key, 0) <= 0:
            return
        if self.active_powerup == key:
            self.active_powerup = None
        else:
            self.active_powerup = key
            # Scanner wirkt sofort
            if key == "scanner":
                self._use_scanner()
                return
            # Schild wirkt sofort
            if key == "shield":
                self._use_shield()
                return
        self._build_powerup_bar()

    # ──────────────────────────────────────────────────────────────────────────
    #  LEVEL MANAGEMENT
    # ──────────────────────────────────────────────────────────────────────────

    def _load_level(self, idx):
        if idx > self.unlocked_level:
            return
        self._stop_timer()
        self.current_level_idx = idx
        cfg = LEVELS[idx]
        self.rows  = cfg["rows"]
        self.cols  = cfg["cols"]
        self.mines = cfg["mines"]

        self.lives       = 3
        self.score       = 0
        self.combo       = 0
        self.game_over   = False
        self.first_click = True
        self.start_time  = None
        self.shield_active = False
        self.active_powerup = None
        self.scanner_active = False

        # Powerups verteilen
        n_pu = cfg["powerups"]
        keys = list(POWERUPS.keys())
        self.powerup_stock = {k: 0 for k in keys}
        for k in random.choices(keys, k=n_pu):
            self.powerup_stock[k] += 1

        self.board    = [[0]*self.cols for _ in range(self.rows)]
        self.revealed = [[False]*self.cols for _ in range(self.rows)]
        self.flagged  = [[False]*self.cols for _ in range(self.rows)]

        self._update_status()
        self._build_board()
        self._build_powerup_bar()
        self._draw_level_bar()
        # Update window title
        self.title(f"💣 Minesweeper PRO – Level {cfg['id']}: {cfg['name']}")

    def _restart_level(self):
        self._load_level(self.current_level_idx)

    def _next_level(self):
        nxt = self.current_level_idx + 1
        if nxt < len(LEVELS):
            if nxt > self.unlocked_level:
                self.unlocked_level = nxt
            self.after(600, lambda: self._load_level(nxt))
        else:
            self.after(600, self._show_victory_screen)

    # ──────────────────────────────────────────────────────────────────────────
    #  GAME LOGIC
    # ──────────────────────────────────────────────────────────────────────────

    def _place_mines(self, safe_r, safe_c):
        safe_zone = {(safe_r+dr, safe_c+dc)
                     for dr in (-1,0,1) for dc in (-1,0,1)}
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)
                     if (r, c) not in safe_zone]
        chosen = random.sample(positions, min(self.mines, len(positions)))
        for r, c in chosen:
            self.board[r][c] = 'M'
        # numbers
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    continue
                self.board[r][c] = sum(
                    1 for dr in (-1,0,1) for dc in (-1,0,1)
                    if (dr or dc) and
                    0 <= r+dr < self.rows and 0 <= c+dc < self.cols and
                    self.board[r+dr][c+dc] == 'M'
                )

    def _reveal(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if self.revealed[r][c] or self.flagged[r][c]:
            return
        self.revealed[r][c] = True
        self._draw_cell(r, c)
        if self.board[r][c] == 0:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr or dc:
                        self._reveal(r+dr, c+dc)

    def _check_win(self):
        return all(
            self.board[r][c] == 'M' or self.revealed[r][c]
            for r in range(self.rows) for c in range(self.cols)
        )

    def _count_flags(self):
        return sum(self.flagged[r][c]
                   for r in range(self.rows) for c in range(self.cols))

    def _neighbors(self, r, c):
        return [(r+dr, c+dc)
                for dr in (-1,0,1) for dc in (-1,0,1)
                if (dr or dc) and 0 <= r+dr < self.rows and 0 <= c+dc < self.cols]

    # ── Klick-Handler ─────────────────────────────────────────────────────────

    def _on_left(self, r, c):
        if self.game_over or self.revealed[r][c] or self.flagged[r][c]:
            return

        # Powerup anwenden
        if self.active_powerup == "radar":
            self._use_radar(r, c)
            return
        if self.active_powerup == "defuse":
            self._use_defuse(r, c)
            return

        if self.first_click:
            self.first_click = False
            self.start_time  = time.time()
            self._tick()
            self._place_mines(r, c)

        if self.board[r][c] == 'M':
            if self.shield_active:
                self.shield_active = False
                self.board[r][c]   = 0  # entschärfe diese Mine
                # Neu berechnen
                self._recalc_numbers()
                self._reveal(r, c)
                self._flash_message("🛡 SCHILD AKTIVIERT!", GREEN)
                self._build_powerup_bar()
            else:
                self.lives -= 1
                self._update_status()
                self.combo = 0
                self._update_combo()
                if self.lives <= 0:
                    self.game_over = True
                    self._reveal_all_mines(r, c)
                    self._stop_timer()
                    self.after(300, self._show_game_over)
                else:
                    self._flash_message(f"💥 GETROFFEN! {self.lives}❤ übrig", RED)
                    self.revealed[r][c] = True
                    self._draw_cell(r, c, exploded=True)
        else:
            cells_before = sum(self.revealed[r2][c2]
                               for r2 in range(self.rows) for c2 in range(self.cols))
            self._reveal(r, c)
            cells_after = sum(self.revealed[r2][c2]
                              for r2 in range(self.rows) for c2 in range(self.cols))
            revealed_now = cells_after - cells_before

            # Scoring
            pts = revealed_now * 10
            self.combo += 1
            if self.combo >= 3:
                bonus = (self.combo - 2) * 5
                pts  += bonus
                self._update_combo()
            self._add_score(pts)
            self._reset_combo_timer()

            if self._check_win():
                self._on_win()

    def _on_right(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return
        if self.first_click:
            return
        self.flagged[r][c] = not self.flagged[r][c]
        self._draw_cell(r, c)
        self._update_status()

    def _on_chord(self, r, c):
        if not self.revealed[r][c] or self.board[r][c] == 0:
            return
        nb = self._neighbors(r, c)
        flags = sum(1 for nr, nc in nb if self.flagged[nr][nc])
        if flags == self.board[r][c]:
            for nr, nc in nb:
                if not self.flagged[nr][nc]:
                    self._on_left(nr, nc)

    # ── Win / Lose ─────────────────────────────────────────────────────────────

    def _on_win(self):
        self.game_over = True
        self._stop_timer()
        elapsed = int(time.time() - self.start_time) if self.start_time else 0

        # Zeitbonus
        time_bonus = max(0, 300 - elapsed) * 5
        self._add_score(time_bonus)
        self.total_score += self.score
        self.total_score_lbl.config(text=f"★ {self.total_score}")

        is_record = record_score(LEVELS[self.current_level_idx]["id"], elapsed)
        best = get_best(LEVELS[self.current_level_idx]["id"])

        # Alle Minen flaggen
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    self.flagged[r][c] = True
                    self._draw_cell(r, c)
        self._update_status()

        record_txt = "🏆 NEUER REKORD!" if is_record else f"Bestzeit: {best}s"
        msg = (f"Level {LEVELS[self.current_level_idx]['id']} – "
               f"{LEVELS[self.current_level_idx]['name']} abgeschlossen!\n\n"
               f"Zeit: {elapsed}s   {record_txt}\n"
               f"Punkte: {self.score}  (inkl. Zeitbonus +{time_bonus})")

        if self.current_level_idx + 1 < len(LEVELS):
            msg += "\n\nWeiter zum nächsten Level?"
            if messagebox.askyesno("🎉 LEVEL ABGESCHLOSSEN!", msg):
                self._next_level()
        else:
            messagebox.showinfo("🏆 ALLE LEVEL ABGESCHLOSSEN!", msg)
            self._show_victory_screen()

    def _show_game_over(self):
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        msg = (f"Du hast alle Leben verloren!\n\n"
               f"Level: {LEVELS[self.current_level_idx]['name']}\n"
               f"Zeit: {elapsed}s\n"
               f"Punkte: {self.score}\n\n"
               f"Nochmal versuchen?")
        if messagebox.askyesno("💀 GAME OVER", msg):
            self._restart_level()

    def _show_victory_screen(self):
        win = tk.Toplevel(self)
        win.title("🏆 VICTORY")
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text="🏆", font=("Courier New", 60), bg=BG, fg=GOLD).pack(pady=10)
        tk.Label(win, text="ALLE 10 LEVEL\nABGESCHLOSSEN!", font=FONT_MEGA,
                 bg=BG, fg=GOLD).pack()
        tk.Label(win, text=f"Gesamtpunkte: {self.total_score}",
                 font=FONT_BOLD, bg=BG, fg=ACCENT2).pack(pady=8)
        tk.Button(win, text="[ NOCHMAL ]", font=FONT_BOLD, bg=BG3, fg=ACCENT,
                  activebackground=ACCENT, activeforeground=BG,
                  relief="flat", padx=20, pady=6, cursor="hand2",
                  command=lambda: [win.destroy(), self._full_reset()]).pack(pady=10)

    def _full_reset(self):
        self.total_score = 0
        self.unlocked_level = 0
        self.total_score_lbl.config(text="★ 0")
        self._load_level(0)

    # ──────────────────────────────────────────────────────────────────────────
    #  POWERUP LOGIK
    # ──────────────────────────────────────────────────────────────────────────

    def _use_radar(self, r, c):
        """Zeigt bis zu 3 sichere, unverminte Felder."""
        self.powerup_stock["radar"] -= 1
        self.active_powerup = None
        safe = [(r2, c2) for r2 in range(self.rows) for c2 in range(self.cols)
                if not self.revealed[r2][c2] and not self.flagged[r2][c2]
                and self.board[r2][c2] != 'M']
        picks = random.sample(safe, min(3, len(safe)))
        for pr, pc in picks:
            cv = self.buttons[pr][pc]
            orig_bg = cv.cget("bg")
            cv.config(bg="#003355")
            cv.create_rectangle(2, 2, CELL_SIZE-PAD-2, CELL_SIZE-PAD-2,
                                 outline="#00c8ff", width=2)
            self.after(2000, lambda r2=pr, c2=pc: self._draw_cell(r2, c2))
        self._build_powerup_bar()
        self._flash_message(f"🔍 RADAR: {len(picks)} sichere Felder markiert", "#00c8ff")

    def _use_shield(self):
        """Aktiviert Schutzschild."""
        self.powerup_stock["shield"] -= 1
        self.active_powerup = None
        self.shield_active = True
        self._build_powerup_bar()
        self._flash_message("🛡 SCHILD aktiv – überlebst die nächste Mine!", GREEN)

    def _use_scanner(self):
        """Zeigt kurz alle Minen."""
        self.powerup_stock["scanner"] -= 1
        self.active_powerup = None
        self._build_powerup_bar()
        self.scanner_active = True
        # Minen kurz aufleuchten lassen
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M' and not self.revealed[r][c]:
                    cv = self.buttons[r][c]
                    cv.delete("all")
                    cv.config(bg="#3a0a0a")
                    cv.create_text(CELL_SIZE//2-PAD//2, CELL_SIZE//2-PAD//2,
                                   text="💣", font=("", 11))
        self._flash_message("🧲 SCANNER: Minen für 3s sichtbar!", "#ff9900")
        self.scanner_timer = self.after(3000, self._scanner_off)

    def _scanner_off(self):
        self.scanner_active = False
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.revealed[r][c]:
                    self._draw_cell(r, c)

    def _use_defuse(self, r, c):
        """Entfernt 1 Mine aus dem Board (nächste zur geklickten Zelle)."""
        self.powerup_stock["defuse"] -= 1
        self.active_powerup = None
        mines = [(r2, c2) for r2 in range(self.rows) for c2 in range(self.cols)
                 if self.board[r2][c2] == 'M' and not self.revealed[r2][c2]]
        if mines:
            # nächste Mine zur geklickten Zelle
            mr, mc = min(mines, key=lambda p: abs(p[0]-r)+abs(p[1]-c))
            self.board[mr][mc] = 0
            self._recalc_numbers()
            self.mines -= 1
            self._draw_cell(mr, mc)
            self._update_status()
            self._flash_message("✂ MINE ENTSCHÄRFT!", "#ff44aa")
        self._build_powerup_bar()

    def _recalc_numbers(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    continue
                self.board[r][c] = sum(
                    1 for dr in (-1,0,1) for dc in (-1,0,1)
                    if (dr or dc) and
                    0 <= r+dr < self.rows and 0 <= c+dc < self.cols and
                    self.board[r+dr][c+dc] == 'M'
                )
        for r in range(self.rows):
            for c in range(self.cols):
                if self.revealed[r][c]:
                    self._draw_cell(r, c)

    # ──────────────────────────────────────────────────────────────────────────
    #  COMBO & SCORE
    # ──────────────────────────────────────────────────────────────────────────

    def _add_score(self, pts):
        self.score += pts
        self.score_lbl.config(text=f"⭐ {self.score}")

    def _update_combo(self):
        if self.combo >= 5:
            self.combo_lbl.config(text=f"🔥 COMBO ×{self.combo}!", fg=ACCENT)
        elif self.combo >= 3:
            self.combo_lbl.config(text=f"⚡ COMBO ×{self.combo}", fg=GOLD)
        else:
            self.combo_lbl.config(text="")

    def _reset_combo_timer(self):
        if self.combo_timer_id:
            self.after_cancel(self.combo_timer_id)
        self.combo_timer_id = self.after(3000, self._break_combo)

    def _break_combo(self):
        self.combo = 0
        self._update_combo()

    # ──────────────────────────────────────────────────────────────────────────
    #  STATUS & TIMER
    # ──────────────────────────────────────────────────────────────────────────

    def _update_status(self):
        remaining = self.mines - self._count_flags()
        self.mine_lbl.config(text=f"💣 {remaining:03d}")
        hearts = "❤" * self.lives + "♡" * (3 - self.lives)
        self.lives_lbl.config(text=hearts)

    def _flash_message(self, txt, color):
        self.footer_lbl.config(text=txt, fg=color)
        self.after(3000, lambda: self.footer_lbl.config(
            text="LK: Aufdecken  |  RK: Flagge  |  Doppelklick: Chord",
            fg=DIM_COLOR))

    def _tick(self):
        if self.game_over or not self.start_time:
            return
        elapsed = int(time.time() - self.start_time)
        self.time_lbl.config(text=f"⏱ {min(elapsed, 999):03d}")
        self.timer_id = self.after(1000, self._tick)

    def _stop_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    # ──────────────────────────────────────────────────────────────────────────
    #  HIGHSCORE FENSTER
    # ──────────────────────────────────────────────────────────────────────────

    def _show_highscores(self):
        win = tk.Toplevel(self)
        win.title("🏆 Bestzeiten")
        win.configure(bg=BG)
        win.resizable(False, False)
        tk.Label(win, text="🏆 BESTZEITEN", font=FONT_BOLD, bg=BG, fg=GOLD,
                 pady=10).pack()
        scores = load_scores()
        for lv in LEVELS:
            key = str(lv["id"])
            best = scores.get(key)
            txt  = f"{best}s" if best else "—"
            row  = tk.Frame(win, bg=BG, pady=2)
            row.pack(fill="x", padx=20)
            tk.Label(row, text=f"Level {lv['id']:2d}  {lv['name']:<12}",
                     font=FONT_SMALL, bg=BG, fg=TEXT_COLOR, anchor="w").pack(side="left")
            tk.Label(row, text=txt, font=FONT_SMALL, bg=BG,
                     fg=GOLD if best else DIM_COLOR, anchor="e").pack(side="right")
        tk.Button(win, text="SCHLIESSEN", font=FONT_SMALL, bg=BG3, fg=ACCENT,
                  activebackground=ACCENT, activeforeground=BG,
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  command=win.destroy).pack(pady=10)

    # ──────────────────────────────────────────────────────────────────────────
    #  BOARD RENDERING
    # ──────────────────────────────────────────────────────────────────────────

    def _build_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()
        self.buttons = []
        for r in range(self.rows):
            row_btns = []
            for c in range(self.cols):
                cv = tk.Canvas(self.board_frame,
                               width=CELL_SIZE - PAD,
                               height=CELL_SIZE - PAD,
                               highlightthickness=0,
                               cursor="hand2")
                cv.grid(row=r, column=c, padx=PAD//2, pady=PAD//2)
                cv.bind("<Button-1>",        lambda e, r=r, c=c: self._on_left(r, c))
                cv.bind("<Button-3>",        lambda e, r=r, c=c: self._on_right(r, c))
                cv.bind("<Double-Button-1>", lambda e, r=r, c=c: self._on_chord(r, c))
                cv.bind("<Button-2>",        lambda e, r=r, c=c: self._on_chord(r, c))
                cv.bind("<Enter>",           lambda e, r=r, c=c: self._hover(r, c, True))
                cv.bind("<Leave>",           lambda e, r=r, c=c: self._hover(r, c, False))
                row_btns.append(cv)
                self._draw_cell_cv(cv, r, c)
            self.buttons.append(row_btns)

    def _draw_cell(self, r, c, exploded=False):
        self._draw_cell_cv(self.buttons[r][c], r, c, exploded=exploded)

    def _draw_cell_cv(self, cv, r, c, hover=False, exploded=False):
        cv.delete("all")
        w = CELL_SIZE - PAD
        h = CELL_SIZE - PAD
        cx, cy = w // 2, h // 2

        if self.revealed[r][c]:
            val = self.board[r][c]
            if val == 'M':
                cv.config(bg=ACCENT if exploded else "#1a0505")
                cv.create_text(cx, cy, text="💣", font=("", 12))
                if exploded:
                    cv.create_oval(2, 2, w-2, h-2, outline=ACCENT, width=2)
            else:
                cv.config(bg=CELL_REVEALED)
                if val > 0:
                    cv.create_text(cx, cy, text=str(val), font=FONT_CELL,
                                   fill=NUMBER_COLORS.get(val, TEXT_COLOR))
                cv.create_rectangle(0, 0, w-1, h-1, outline="#111a22", width=1)
        elif self.flagged[r][c]:
            cv.config(bg=CELL_HIDDEN)
            cv.create_text(cx, cy, text="🚩", font=("", 13))
            self._bevel(cv, w, h)
        else:
            # Powerup-Cursor-Hinweis
            if self.active_powerup in ("radar", "defuse"):
                bg = "#1a2a1a" if hover else CELL_HIDDEN
            else:
                bg = CELL_HOVER if hover else CELL_HIDDEN
            cv.config(bg=bg)
            self._bevel(cv, w, h)

    def _bevel(self, cv, w, h):
        cv.create_line(0, 0, w, 0,   fill="#254a6e", width=1)
        cv.create_line(0, 0, 0, h,   fill="#254a6e", width=1)
        cv.create_line(w-1, 0, w-1, h-1, fill="#060e16", width=1)
        cv.create_line(0, h-1, w-1, h-1, fill="#060e16", width=1)

    def _hover(self, r, c, entering):
        if self.game_over or self.revealed[r][c] or self.flagged[r][c]:
            return
        self._draw_cell_cv(self.buttons[r][c], r, c, hover=entering)

    def _reveal_all_mines(self, hit_r, hit_c):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    self.revealed[r][c] = True
                    self._draw_cell(r, c, exploded=(r == hit_r and c == hit_c))


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = Minesweeper()
    app.mainloop()