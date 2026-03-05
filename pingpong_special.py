import tkinter as tk
import random

# ── Einstellungen ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT   = 900, 600
PAD_W, PAD_H    = 14, 100
BALL_R          = 12
PAD_SPEED       = 18
BALL_SPEED_INIT = 7
MAX_SCORE       = 7
FPS             = 16          # ms pro Frame (~60 fps ≈ 16 ms)

BG      = "#0a0a0f"
FG      = "#e8e0ff"
ACCENT  = "#c084fc"
ACCENT2 = "#38bdf8"
NET_CLR = "#2d2d3a"


class PingPong:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("PING  PONG")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self._build_ui()
        self._reset_state()
        self._bind_keys()
        self._show_start_screen()

    # ── UI aufbauen ────────────────────────────────────────────────────────────
    def _build_ui(self):
        c = self.canvas

        # Mittellinie (gestrichelt durch einzelne Rechtecke)
        for y in range(0, HEIGHT, 28):
            c.create_rectangle(WIDTH//2 - 2, y, WIDTH//2 + 2, y + 14,
                                fill=NET_CLR, outline="")

        # Paddles
        self.pad_l = c.create_rectangle(0, 0, 0, 0, fill=ACCENT,  outline="", tags="pad_l")
        self.pad_r = c.create_rectangle(0, 0, 0, 0, fill=ACCENT2, outline="", tags="pad_r")

        # Ball
        self.ball = c.create_oval(0, 0, 0, 0, fill=FG, outline="", tags="ball")

        # Punkte
        self.score_l_txt = c.create_text(WIDTH//4,     50, text="0",
                                          font=("Courier", 64, "bold"),
                                          fill=ACCENT,  anchor="center")
        self.score_r_txt = c.create_text(WIDTH*3//4,   50, text="0",
                                          font=("Courier", 64, "bold"),
                                          fill=ACCENT2, anchor="center")

        # Overlay (Start / Pause / Ende)
        self.overlay_bg = c.create_rectangle(WIDTH//2 - 280, HEIGHT//2 - 110,
                                              WIDTH//2 + 280, HEIGHT//2 + 130,
                                              fill="#14141e", outline=ACCENT, width=2,
                                              tags="overlay")
        self.overlay_title = c.create_text(WIDTH//2, HEIGHT//2 - 55,
                                            text="", font=("Courier", 38, "bold"),
                                            fill=FG, anchor="center", tags="overlay")
        self.overlay_sub   = c.create_text(WIDTH//2, HEIGHT//2 + 15,
                                            text="", font=("Courier", 16),
                                            fill=NET_CLR, anchor="center", tags="overlay")
        self.overlay_hint  = c.create_text(WIDTH//2, HEIGHT//2 + 75,
                                            text="", font=("Courier", 13),
                                            fill=ACCENT, anchor="center", tags="overlay")

    def _show_overlay(self, title, sub, hint):
        c = self.canvas
        c.itemconfig(self.overlay_title, text=title)
        c.itemconfig(self.overlay_sub,   text=sub)
        c.itemconfig(self.overlay_hint,  text=hint)
        for tag in ("overlay",):
            c.tag_raise(tag)
        c.itemconfig(self.overlay_bg,    state="normal")
        c.itemconfig(self.overlay_title, state="normal")
        c.itemconfig(self.overlay_sub,   state="normal")
        c.itemconfig(self.overlay_hint,  state="normal")

    def _hide_overlay(self):
        for item in (self.overlay_bg, self.overlay_title,
                     self.overlay_sub, self.overlay_hint):
            self.canvas.itemconfig(item, state="hidden")

    def _show_start_screen(self):
        self._place_objects()
        self._show_overlay("PING PONG",
                           "Erster bis  7  Punkte gewinnt",
                           "LEERTASTE  –  Start  /  Pause\n"
                           "W / S  –  Linkes Paddle     ↑ / ↓  –  Rechtes Paddle")

    # ── Spielzustand ──────────────────────────────────────────────────────────
    def _reset_state(self):
        self.score_l = 0
        self.score_r = 0
        self.running = False
        self.paused  = False
        self.game_over = False
        self._reset_ball()
        self._reset_paddles()

    def _reset_paddles(self):
        self.py_l = HEIGHT // 2   # Mitte (y des Paddle-Zentrums)
        self.py_r = HEIGHT // 2
        self.keys: dict[str, bool] = {}

    def _reset_ball(self):
        self.bx = WIDTH  // 2
        self.by = HEIGHT // 2
        angle = random.uniform(-0.6, 0.6)
        dx = BALL_SPEED_INIT * (1 if random.random() > 0.5 else -1)
        dy = BALL_SPEED_INIT * angle
        self.bdx = dx
        self.bdy = dy
        self.ball_speed = BALL_SPEED_INIT

    # ── Tastenbelegung ────────────────────────────────────────────────────────
    def _bind_keys(self):
        self.root.bind("<KeyPress>",   self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

    def _on_key_press(self, event):
        self.keys[event.keysym] = True
        if event.keysym == "space":
            self._toggle_pause()

    def _on_key_release(self, event):
        self.keys[event.keysym] = False

    def _toggle_pause(self):
        if self.game_over:
            self._restart()
            return
        if not self.running:
            self._hide_overlay()
            self.running = True
            self._loop()
        elif self.paused:
            self.paused = False
            self._hide_overlay()
            self._loop()
        else:
            self.paused = True
            self._show_overlay("PAUSE", "", "LEERTASTE  –  Weiterspielen")

    def _restart(self):
        self.game_over = False
        self._reset_state()
        self._place_objects()
        self._update_scores()
        self._show_start_screen()

    # ── Spielschleife ─────────────────────────────────────────────────────────
    def _loop(self):
        if not self.running or self.paused or self.game_over:
            return
        self._move_paddles()
        self._move_ball()
        self._place_objects()
        self.root.after(FPS, self._loop)

    def _move_paddles(self):
        # Linkes Paddle: W / S
        if self.keys.get("w") or self.keys.get("W"):
            self.py_l -= PAD_SPEED
        if self.keys.get("s") or self.keys.get("S"):
            self.py_l += PAD_SPEED

        # Rechtes Paddle: Pfeil hoch / runter
        if self.keys.get("Up"):
            self.py_r -= PAD_SPEED
        if self.keys.get("Down"):
            self.py_r += PAD_SPEED

        half = PAD_H // 2
        self.py_l = max(half, min(HEIGHT - half, self.py_l))
        self.py_r = max(half, min(HEIGHT - half, self.py_r))

    def _move_ball(self):
        self.bx += self.bdx
        self.by += self.bdy

        # Oben / Unten abprallen
        if self.by - BALL_R <= 0:
            self.by = BALL_R
            self.bdy = abs(self.bdy)
        if self.by + BALL_R >= HEIGHT:
            self.by = HEIGHT - BALL_R
            self.bdy = -abs(self.bdy)

        # Kollision linkes Paddle
        lx1 = 30
        lx2 = 30 + PAD_W
        if (self.bdx < 0 and
                lx1 <= self.bx - BALL_R <= lx2 and
                self.py_l - PAD_H//2 <= self.by <= self.py_l + PAD_H//2):
            self._bounce_off_paddle(self.py_l, left=True)

        # Kollision rechtes Paddle
        rx1 = WIDTH - 30 - PAD_W
        rx2 = WIDTH - 30
        if (self.bdx > 0 and
                rx1 <= self.bx + BALL_R <= rx2 and
                self.py_r - PAD_H//2 <= self.by <= self.py_r + PAD_H//2):
            self._bounce_off_paddle(self.py_r, left=False)

        # Punkt links / rechts
        if self.bx < 0:
            self.score_r += 1
            self._update_scores()
            self._check_win("Rechts")
            if not self.game_over:
                self._reset_ball()
        elif self.bx > WIDTH:
            self.score_l += 1
            self._update_scores()
            self._check_win("Links")
            if not self.game_over:
                self._reset_ball()

    def _bounce_off_paddle(self, pad_cy, left: bool):
        # Winkel abhängig davon, wo der Ball auftrifft
        rel    = (self.by - pad_cy) / (PAD_H / 2)   # -1 … +1
        angle  = rel * 0.9                           # max ~52°
        self.ball_speed = min(self.ball_speed + 0.4, 22)
        self.bdx = self.ball_speed * (1 if left else -1)
        self.bdy = self.ball_speed * angle

    def _check_win(self, side):
        if self.score_l >= MAX_SCORE or self.score_r >= MAX_SCORE:
            self.game_over = True
            self.running   = False
            self._show_overlay(f"🏆  {side} gewinnt!",
                               f"{self.score_l}  :  {self.score_r}",
                               "LEERTASTE  –  Nochmal spielen")

    # ── Zeichnen ──────────────────────────────────────────────────────────────
    def _place_objects(self):
        c = self.canvas

        # Linkes Paddle
        lx = 30
        c.coords(self.pad_l,
                 lx, self.py_l - PAD_H//2,
                 lx + PAD_W, self.py_l + PAD_H//2)

        # Rechtes Paddle
        rx = WIDTH - 30 - PAD_W
        c.coords(self.pad_r,
                 rx, self.py_r - PAD_H//2,
                 rx + PAD_W, self.py_r + PAD_H//2)

        # Ball
        c.coords(self.ball,
                 self.bx - BALL_R, self.by - BALL_R,
                 self.bx + BALL_R, self.by + BALL_R)

    def _update_scores(self):
        self.canvas.itemconfig(self.score_l_txt, text=str(self.score_l))
        self.canvas.itemconfig(self.score_r_txt, text=str(self.score_r))


# ── Einstiegspunkt ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = PingPong(root)
    root.mainloop()
