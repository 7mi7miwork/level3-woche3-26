"""
PAC-MAN DELUXE – tkinter-Version
Keine externe Bibliothek nötig! Läuft mit Standard-Python 3.
Starten: python pacman_tkinter.py
Steuerung: WASD oder Pfeiltasten | P = Pause | ESC = Menü
"""

import tkinter as tk
import random
import math
import json
import os
import sys

# ─── KONSTANTEN ───────────────────────────────────────────────────────────────
CELL  = 26
COLS  = 21
ROWS  = 21
W     = COLS * CELL
H     = ROWS * CELL
HUD_H = 60
FPS   = 60
DELAY = 1000 // FPS   # ms pro Frame

# ─── FARBEN ───────────────────────────────────────────────────────────────────
BLACK  = "#000000"
YELLOW = "#FFDC00"
WHITE  = "#FFFFFF"
BLUE   = "#2121DE"
RED    = "#FF0000"
PINK   = "#FFB8FF"
CYAN   = "#00FFFF"
ORANGE = "#FFA500"
GREEN  = "#00C800"
PURPLE = "#B400FF"
GRAY   = "#787878"
DKBLUE = "#000050"
GOLD   = "#FFD700"
LIME   = "#00FF80"
WALL_C = "#2121B4"
WALL_B = "#4444FF"

# ─── POWERUP-TYPEN ────────────────────────────────────────────────────────────
POWERUP_TYPES = {
    "speed":  {"color": LIME,   "sym": "S", "dur": 8,  "desc": "SPEED"},
    "freeze": {"color": CYAN,   "sym": "F", "dur": 6,  "desc": "FREEZE"},
    "magnet": {"color": GOLD,   "sym": "M", "dur": 7,  "desc": "MAGNET"},
    "shield": {"color": WHITE,  "sym": "X", "dur": 10, "desc": "SHIELD"},
    "double": {"color": ORANGE, "sym": "2", "dur": 8,  "desc": "x2 PTS"},
    "life":   {"color": RED,    "sym": "♥", "dur": 0,  "desc": "+LEBEN"},
    "bomb":   {"color": GRAY,   "sym": "B", "dur": 0,  "desc": "BOMBE"},
}

# ─── GEISTER-TYPEN ────────────────────────────────────────────────────────────
GHOST_TYPES = [
    {"name": "Blinky", "color": RED,    "ai": "chase",   "sm": 1.0},
    {"name": "Pinky",  "color": PINK,   "ai": "ambush",  "sm": 0.95},
    {"name": "Inky",   "color": CYAN,   "ai": "random",  "sm": 0.9},
    {"name": "Clyde",  "color": ORANGE, "ai": "scatter", "sm": 0.85},
    {"name": "Shadow", "color": PURPLE, "ai": "chase",   "sm": 1.1},
    {"name": "Speedy", "color": LIME,   "ai": "chase",   "sm": 1.2},
]

DIFFICULTIES = {
    "Einfach":  {"gc": 2, "gs": 1, "pd": 600, "el": 2},
    "Normal":   {"gc": 3, "gs": 2, "pd": 400, "el": 1},
    "Schwer":   {"gc": 4, "gs": 2, "pd": 250, "el": 0},
    "Wahnsinn": {"gc": 5, "gs": 3, "pd": 150, "el": 0},
}

LEVEL_SEEDS = [42, 137, 256, 999, 1337]

# ─── MAP-GENERATOR ────────────────────────────────────────────────────────────
def bfs_reachable(grid, sc, sr):
    visited = set()
    queue = [(sc, sr)]
    visited.add((sc, sr))
    while queue:
        c, r = queue.pop(0)
        for dc, dr in ((1,0),(-1,0),(0,1),(0,-1)):
            nc = (c + dc) % COLS
            nr = r + dr
            key = (nc, nr)
            if key not in visited and 0 <= nr < ROWS and grid[nr][nc] == 0:
                visited.add(key)
                queue.append(key)
    return visited


def generate_map(level_num, seed=None):
    if seed is not None:
        random.seed(seed)
    sys.setrecursionlimit(5000)

    grid = [[1] * COLS for _ in range(ROWS)]

    def carve(x, y):
        dirs = [(2,0),(-2,0),(0,2),(0,-2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= COLS-2 and 1 <= ny <= ROWS-2 and grid[ny][nx] == 1:
                grid[y + dy//2][x + dx//2] = 0
                grid[ny][nx] = 0
                carve(nx, ny)

    grid[1][1] = 0
    carve(1, 1)

    for c in range(COLS):
        grid[0][c] = 1
        grid[ROWS-1][c] = 1
    for r in range(ROWS):
        grid[r][0] = 1
        grid[r][COLS-1] = 1

    # Schleifen hinzufügen
    inner = [(c, r) for r in range(2, ROWS-2, 2)
                     for c in range(2, COLS-2, 2) if grid[r][c] == 1]
    random.shuffle(inner)
    for c, r in inner[:len(inner)//5]:
        grid[r][c] = 0

    # Geister-Käfig
    gx, gy = COLS // 2, ROWS // 2
    cage_top  = gy - 1
    cage_left = gx - 2
    cage = ["##=##", "#   #", "#####"]
    for dr, row in enumerate(cage):
        for dc, ch in enumerate(row):
            r2, c2 = cage_top + dr, cage_left + dc
            if 0 < r2 < ROWS-1 and 0 < c2 < COLS-1:
                grid[r2][c2] = 1 if ch == '#' else (2 if ch == '=' else 0)
    for dc in range(-2, 3):
        c2 = gx + dc
        if 0 < c2 < COLS-1:
            grid[cage_top-1][c2] = 0

    ghost_home = (gx, gy)
    ghost_door = (gx, cage_top)

    pac_r = min(gy + 4, ROWS - 2)
    pac_c = gx
    grid[pac_r][pac_c] = 0
    for dc in (-1, 0, 1):
        c2 = pac_c + dc
        if 0 < c2 < COLS-1:
            grid[pac_r][c2] = 0
            if pac_r - 1 > 0:
                grid[pac_r-1][c2] = 0

    powers = set()
    for cr, rr in ((1,1),(COLS-2,1),(1,ROWS-2),(COLS-2,ROWS-2)):
        grid[rr][cr] = 0
        powers.add((cr, rr))
        for dc, dr in ((1,0),(0,1)):
            nc, nr = cr+dc, rr+dr
            if 0 < nc < COLS-1 and 0 < nr < ROWS-1:
                grid[nr][nc] = 0

    cage_cells = {(cage_left+dc, cage_top+dr) for dr in range(3) for dc in range(5)}
    dots = set()
    for r in range(1, ROWS-1):
        for c in range(1, COLS-1):
            if grid[r][c] == 0:
                pos = (c, r)
                if pos not in powers and pos not in cage_cells and pos != (pac_c, pac_r):
                    dots.add(pos)

    reachable = bfs_reachable(grid, pac_c, pac_r)
    dots   -= {p for p in dots   if p not in reachable}
    powers -= {p for p in powers if p not in reachable}

    attempts = 0
    while len(dots) < 60 and attempts < 50:
        attempts += 1
        walls = [(c, r) for r in range(1, ROWS-1) for c in range(1, COLS-1)
                 if grid[r][c] == 1 and (c,r) not in cage_cells]
        if not walls:
            break
        c, r = random.choice(walls)
        grid[r][c] = 0
        dots.add((c, r))
        reach2 = bfs_reachable(grid, pac_c, pac_r)
        dots   -= {p for p in dots   if p not in reach2}
        powers -= {p for p in powers if p not in reach2}

    return {
        "grid": grid,
        "dots": dots,
        "powers": powers,
        "ghost_home": ghost_home,
        "ghost_door": ghost_door,
        "pac_c": pac_c,
        "pac_r": pac_r,
    }


def get_level_map(level_num):
    seed = LEVEL_SEEDS[level_num % len(LEVEL_SEEDS)] + level_num * 7
    return generate_map(level_num, seed=seed)


# ─── HILFSFUNKTIONEN ──────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend(color, alpha, bg=(0,0,0)):
    r1, g1, b1 = hex_to_rgb(color)
    r2, g2, b2 = bg
    r = int(r1*alpha + r2*(1-alpha))
    g = int(g1*alpha + g2*(1-alpha))
    b = int(b1*alpha + b2*(1-alpha))
    return f"#{r:02x}{g:02x}{b:02x}"


# ─── PARTICLE ─────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, text=""):
        self.x = x; self.y = y
        self.color = color; self.text = text
        self.vy = -2 - random.random() * 2
        self.vx = random.uniform(-1, 1)
        self.life = 40; self.max_life = 40

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.12; self.life -= 1

    @property
    def alpha(self):
        return self.life / self.max_life


# ─── PAC-MAN ──────────────────────────────────────────────────────────────────
class PacMan:
    SPEED = 2

    def __init__(self, cx, cy):
        self.cx = cx; self.cy = cy
        self.px = cx * CELL; self.py = cy * CELL
        self.dx = 0; self.dy = 0
        self.ndx = 0; self.ndy = 0
        self.mouth = 0; self.mdir = 1
        self.effects = {}
        self.flash = 0

    def set_dir(self, dx, dy):
        self.ndx = dx; self.ndy = dy

    @property
    def spd(self):
        return self.SPEED * 2 if "speed" in self.effects else self.SPEED

    def update(self, gmap):
        for k in list(self.effects):
            self.effects[k] -= 1
            if self.effects[k] <= 0:
                del self.effects[k]
        self.flash = max(0, self.flash - 1)
        self.mouth += 5 * self.mdir
        if self.mouth >= 40: self.mdir = -1
        if self.mouth <= 0:  self.mdir = 1
        for _ in range(self.spd):
            self._step(gmap)

    def _step(self, gmap):
        on_x = (self.px % CELL) == 0
        on_y = (self.py % CELL) == 0
        if on_x and on_y:
            self.cx = (self.px // CELL) % COLS
            self.cy = self.py // CELL
            nnx = (self.cx + self.ndx) % COLS
            nny = self.cy + self.ndy
            if gmap.walkable_pac(nnx, nny):
                self.dx, self.dy = self.ndx, self.ndy
            nx = (self.cx + self.dx) % COLS
            ny = self.cy + self.dy
            if not gmap.walkable_pac(nx, ny):
                self.dx = self.dy = 0
        self.px = (self.px + self.dx) % (COLS * CELL)
        self.py = self.py + self.dy
        self.cx = (self.px // CELL) % COLS
        self.cy = self.py // CELL


# ─── GHOST ────────────────────────────────────────────────────────────────────
class Ghost:
    def __init__(self, gtype, hx, hy, base_spd):
        self.gtype = gtype
        self.color = gtype["color"]
        self.ai    = gtype["ai"]
        self.hx = hx; self.hy = hy
        self.cx = hx; self.cy = hy
        self.px = hx * CELL; self.py = hy * CELL
        self.dx = 0; self.dy = -1
        self.base_spd = max(1, round(base_spd * gtype["sm"]))
        self.spd = self.base_spd
        self.frightened = 0
        self.eaten = False
        self.released = False
        self.release_timer = random.randint(60, 180)
        self.mode_timer = 0
        self.mode = "scatter"
        self.sx = random.choice([0, COLS-1])
        self.sy = random.choice([0, ROWS-1])

    def frighten(self, dur):
        if not self.eaten:
            self.frightened = dur
            self.dx, self.dy = -self.dx, -self.dy

    def reset(self):
        self.cx, self.cy = self.hx, self.hy
        self.px, self.py = self.hx * CELL, self.hy * CELL
        self.dx, self.dy = 0, -1
        self.frightened = 0; self.eaten = False
        self.released = False
        self.release_timer = random.randint(60, 180)
        self.spd = self.base_spd

    def _choose_dir(self, gmap, pcx, pcy, pdx, pdy):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        rev  = (-self.dx, -self.dy)
        choices = [d for d in dirs if d != rev]
        if self.frightened:
            valid = [d for d in choices
                     if gmap.walkable((self.cx+d[0])%COLS, self.cy+d[1])]
            return random.choice(valid) if valid else random.choice(dirs)
        if self.mode == "scatter":
            tx, ty = self.sx, self.sy
        elif self.ai == "chase":
            tx, ty = pcx, pcy
        elif self.ai == "ambush":
            tx, ty = pcx + pdx*4, pcy + pdy*4
        elif self.ai == "random":
            valid = [d for d in choices
                     if gmap.walkable((self.cx+d[0])%COLS, self.cy+d[1])]
            return random.choice(valid) if valid else random.choice(dirs)
        else:
            if abs(self.cx-pcx)+abs(self.cy-pcy) > 8:
                tx, ty = pcx, pcy
            else:
                tx, ty = self.sx, self.sy
        best, best_d = None, float("inf")
        for d in choices:
            nx = (self.cx+d[0])%COLS
            ny = self.cy+d[1]
            if gmap.walkable(nx, ny):
                dist = (nx-tx)**2 + (ny-ty)**2
                if dist < best_d:
                    best_d, best = dist, d
        if best:
            return best
        valid = [d for d in dirs if gmap.walkable((self.cx+d[0])%COLS, self.cy+d[1])]
        return random.choice(valid) if valid else (0, 0)

    def update(self, gmap, pcx, pcy, pdx, pdy, frozen):
        if frozen and not self.eaten:
            return
        if not self.released:
            self.release_timer -= 1
            if self.release_timer <= 0:
                self.released = True
                dx, dy = gmap.ghost_door
                self.cx, self.cy = dx, dy
                self.px, self.py = dx*CELL, dy*CELL
                self.dx, self.dy = 0, -1
            return
        self.spd = 3 if self.eaten else (max(1, self.base_spd-1) if self.frightened else self.base_spd)
        if self.frightened > 0:
            self.frightened -= 1
        self.mode_timer += 1
        if   self.mode_timer < 300: self.mode = "scatter"
        elif self.mode_timer < 600: self.mode = "chase"
        elif self.mode_timer < 750: self.mode = "scatter"
        else:                        self.mode = "chase"
        if self.mode_timer > 800:
            self.mode_timer = 300
        for _ in range(self.spd):
            self._step(gmap, pcx, pcy, pdx, pdy)
        if self.eaten and self.cx == self.hx and self.cy == self.hy:
            self.eaten = False; self.frightened = 0; self.spd = self.base_spd

    def _step(self, gmap, pcx, pcy, pdx, pdy):
        on_x = (self.px % CELL) == 0
        on_y = (self.py % CELL) == 0
        if on_x and on_y:
            self.cx = (self.px // CELL) % COLS
            self.cy = self.py // CELL
            d = self._choose_dir(gmap, pcx, pcy, pdx, pdy)
            if d: self.dx, self.dy = d
        npx = self.px + self.dx
        npy = self.py + self.dy
        nc = (npx // CELL) % COLS
        nr = npy // CELL
        if gmap.walkable(nc, nr):
            self.px = npx % (COLS * CELL)
            self.py = npy
        else:
            self.px = (self.px // CELL) * CELL
            self.py = (self.py // CELL) * CELL
            self.cx = (self.px // CELL) % COLS
            self.cy = self.py // CELL
            d = self._choose_dir(gmap, pcx, pcy, pdx, pdy)
            if d: self.dx, self.dy = d
            else: self.dx = self.dy = 0
            return
        self.cx = (self.px // CELL) % COLS
        self.cy = self.py // CELL


# ─── GAME-MAP ─────────────────────────────────────────────────────────────────
class GameMap:
    def __init__(self, data, level_num):
        self.grid = data["grid"]
        self.dots = data["dots"]
        self.powers = data["powers"]
        self.ghost_home = data["ghost_home"]
        self.ghost_door = data["ghost_door"]
        self.pac_c = data["pac_c"]
        self.pac_r = data["pac_r"]
        self.special_powers = {}
        empties = [
            (c, r)
            for r in range(ROWS) for c in range(COLS)
            if self.grid[r][c] == 0
            and (c, r) not in self.dots
            and (c, r) not in self.powers
        ]
        random.shuffle(empties)
        types = list(POWERUP_TYPES.keys())
        for pos in empties[:3 + level_num]:
            self.special_powers[pos] = random.choice(types)

    def walkable(self, c, r):
        c = c % COLS
        if r < 0 or r >= ROWS: return False
        return self.grid[r][c] in (0, 2)

    def walkable_pac(self, c, r):
        c = c % COLS
        if r < 0 or r >= ROWS: return False
        return self.grid[r][c] == 0


# ─── HAUPT-ANWENDUNG ──────────────────────────────────────────────────────────
class PacManApp:
    HI_FILE = "pacman_hi.json"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PAC-MAN DELUXE")
        self.root.resizable(False, False)
        self.root.configure(bg=BLACK)

        # Canvas
        self.canvas = tk.Canvas(
            self.root, width=W, height=H + HUD_H,
            bg=BLACK, highlightthickness=0
        )
        self.canvas.pack()

        # Zustand
        self.state      = "menu"
        self.score      = 0
        self.hi_score   = self._load_hi()
        self.lives      = 3
        self.level      = 0
        self.diff_name  = "Normal"
        self.diff       = DIFFICULTIES[self.diff_name]
        self.particles  = []
        self.ghost_combo = 0
        self.total_dots  = 0
        self.freeze_timer = 0
        self.tick = 0
        self.map    = None
        self.pac    = None
        self.ghosts = []

        # Eingabe
        self._bind_keys()

        # Menü aufbauen und Schleife starten
        self._loop()

    # ── Highscore ─────────────────────────────────────────────────────────
    def _load_hi(self):
        try:
            with open(self.HI_FILE) as f:
                return json.load(f).get("hi", 0)
        except:
            return 0

    def _save_hi(self):
        try:
            with open(self.HI_FILE, "w") as f:
                json.dump({"hi": self.hi_score}, f)
        except:
            pass

    # ── Eingabe ───────────────────────────────────────────────────────────
    def _bind_keys(self):
        self.root.bind("<KeyPress>", self._on_key)

    def _on_key(self, e):
        k = e.keysym

        if self.state == "playing":
            if k in ("Left",  "a"): self.pac.set_dir(-1,  0)
            if k in ("Right", "d"): self.pac.set_dir( 1,  0)
            if k in ("Up",    "w"): self.pac.set_dir( 0, -1)
            if k in ("Down",  "s"): self.pac.set_dir( 0,  1)
            if k in ("p", "P", "Escape"):
                self.state = "paused"

        elif self.state == "paused":
            if k in ("p", "P", "Return", "Escape"):
                self.state = "playing"

        elif self.state == "menu":
            if k == "Return":     self.start_game()
            if k in ("d", "D"):   self._open_diff_dialog()

        elif self.state == "dead":
            if k == "Return":
                self._load_level(); self.state = "playing"
            if k == "Escape":
                self.state = "menu"

        elif self.state == "win":
            if k == "Return":
                self._load_level(); self.state = "playing"

        elif self.state == "gameover":
            if k == "Return":     self.state = "menu"
            if k in ("r", "R"):   self.start_game()
            if k == "Escape":     self.state = "menu"

        # ESC immer → Menü (außer im Menü selbst → Beenden)
        if k == "Escape":
            if self.state == "menu":
                self._save_hi(); self.root.destroy()

    def _open_diff_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Schwierigkeit")
        dlg.configure(bg=BLACK)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="SCHWIERIGKEIT", font=("Courier", 16, "bold"),
                 fg=YELLOW, bg=BLACK).pack(pady=(20, 10))

        for name, d in DIFFICULTIES.items():
            is_sel = (name == self.diff_name)
            bg = "#1a1a00" if is_sel else "#111111"
            fg = GOLD     if is_sel else WHITE
            lbl = f"{name:<10}  Geister: {d['gc']}   +{d['el']} Leben"
            btn = tk.Button(
                dlg, text=lbl, font=("Courier", 11, "bold"),
                fg=fg, bg=bg, activeforeground=GOLD, activebackground="#2a2a00",
                relief="flat", padx=16, pady=8, width=34,
                command=lambda n=name: (
                    setattr(self, "diff_name", n),
                    setattr(self, "diff", DIFFICULTIES[n]),
                    dlg.destroy()
                )
            )
            btn.pack(pady=4, padx=20)

        tk.Button(dlg, text="ZURÜCK", font=("Courier", 10, "bold"),
                  fg=GRAY, bg=BLACK, relief="flat", command=dlg.destroy).pack(pady=12)
        self.root.wait_window(dlg)

    # ── Level laden ───────────────────────────────────────────────────────
    def _load_level(self):
        data = get_level_map(self.level)
        self.map = GameMap(data, self.level)
        self.total_dots = len(self.map.dots) + len(self.map.powers)
        self.pac = PacMan(data["pac_c"], data["pac_r"])
        spd = self.diff["gs"]
        gc  = min(self.diff["gc"] + self.level // 2, len(GHOST_TYPES))
        types = random.sample(GHOST_TYPES, gc)
        hx, hy = self.map.ghost_home
        self.ghosts = [
            Ghost(t, hx + random.randint(-1, 1), hy, spd)
            for t in types
        ]
        self.freeze_timer = 0
        self.ghost_combo  = 0

    # ── Spiel starten ─────────────────────────────────────────────────────
    def start_game(self):
        self.score  = 0
        self.lives  = 3 + self.diff["el"]
        self.level  = 0
        self.particles = []
        self._load_level()
        self.state = "playing"

    # ── Hauptschleife ─────────────────────────────────────────────────────
    def _loop(self):
        self._update()
        self._draw()
        self.root.after(DELAY, self._loop)

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self):
        if self.state != "playing":
            return
        self.tick += 1
        frozen = self.freeze_timer > 0
        if frozen:
            self.freeze_timer -= 1

        self.pac.update(self.map)
        for g in self.ghosts:
            g.update(self.map,
                     self.pac.cx, self.pac.cy,
                     self.pac.dx, self.pac.dy,
                     frozen)

        self._check_dots()
        self._check_ghosts()
        self._check_win()

        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def _check_dots(self):
        pos = (self.pac.cx, self.pac.cy)
        check = {pos}
        if "magnet" in self.pac.effects:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check.add(((pos[0]+dx) % COLS, pos[1]+dy))

        for p in list(check):
            if p in self.map.dots:
                self.map.dots.discard(p)
                pts = 20 if "double" in self.pac.effects else 10
                self.score += pts
                self._spawn(p[0]*CELL, p[1]*CELL, WHITE, f"+{pts}")

            if p in self.map.powers:
                self.map.powers.discard(p)
                dur = self.diff["pd"]
                for g in self.ghosts:
                    g.frighten(dur)
                self.ghost_combo = 0
                pts = 100 if "double" in self.pac.effects else 50
                self.score += pts
                self._spawn(pos[0]*CELL, pos[1]*CELL, GOLD, "POWER!")

            if p in self.map.special_powers:
                tp = self.map.special_powers.pop(p)
                self._apply_powerup(tp)

    def _apply_powerup(self, tp):
        info = POWERUP_TYPES[tp]
        self._spawn(self.pac.px, self.pac.py, info["color"], info["desc"])
        if tp == "life":
            self.lives += 1
        elif tp == "bomb":
            for g in self.ghosts:
                g.frighten(200); g.eaten = True
            self.score += 500
        elif tp == "freeze":
            self.freeze_timer = info["dur"] * FPS
        else:
            self.pac.effects[tp] = info["dur"] * FPS

    def _check_ghosts(self):
        for g in self.ghosts:
            if not g.released or g.eaten:
                continue
            if abs(g.px - self.pac.px) < CELL-4 and abs(g.py - self.pac.py) < CELL-4:
                if "shield" in self.pac.effects:
                    del self.pac.effects["shield"]
                    self.pac.flash = 40
                    g.frighten(200)
                    self._spawn(self.pac.px, self.pac.py, CYAN, "SHIELD!")
                elif g.frightened:
                    g.eaten = True
                    self.ghost_combo += 1
                    pts = 200 * (2 ** min(self.ghost_combo-1, 6))
                    if "double" in self.pac.effects:
                        pts *= 2
                    self.score += pts
                    self._spawn(g.px, g.py, ORANGE, f"+{pts}")
                else:
                    self._die()
                    return

    def _die(self):
        self.lives -= 1
        if self.lives <= 0:
            if self.score > self.hi_score:
                self.hi_score = self.score
                self._save_hi()
            self.state = "gameover"
        else:
            self.state = "dead"

    def _check_win(self):
        if self.map and not self.map.dots and not self.map.powers:
            self.score += 500 * (self.level + 1)
            self.level += 1
            self.state = "win"

    def _spawn(self, x, y, color, text):
        self.particles.append(Particle(x, y, color, text))

    # ── Zeichnen ──────────────────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete("all")
        c.configure(bg=BLACK)

        t = self.tick   # Animationstimer

        if self.state in ("playing", "paused", "dead", "win"):
            self._draw_map(t)
            self._draw_pac()
            self._draw_ghosts(t)
            self._draw_particles()
            self._draw_hud()

        if self.state == "menu":
            self._draw_menu(t)
        elif self.state == "paused":
            self._draw_overlay("PAUSE", YELLOW)
        elif self.state == "dead":
            self._draw_overlay(f"VERLOREN!  ({self.lives} Leben)", RED)
            self._draw_overlay_hint("ENTER – weiter  |  ESC – Menü")
        elif self.state == "win":
            self._draw_overlay("LEVEL GESCHAFFT!", GREEN)
            self._draw_overlay_hint("ENTER – nächstes Level")
        elif self.state == "gameover":
            self._draw_gameover()

    def _draw_map(self, t):
        c = self.canvas
        for r in range(ROWS):
            for col in range(COLS):
                cell = self.map.grid[r][col]
                rx, ry = col*CELL, r*CELL
                if cell == 1:
                    c.create_rectangle(rx+1, ry+1, rx+CELL-1, ry+CELL-1,
                                       fill=WALL_C, outline=WALL_B, width=1)
                elif cell == 2:
                    c.create_rectangle(rx+4, ry+CELL//2-2,
                                       rx+CELL-4, ry+CELL//2+2,
                                       fill=PINK, outline="")

        # Punkte
        for (col, r) in self.map.dots:
            cx = col*CELL + CELL//2
            cy = r*CELL   + CELL//2
            c.create_oval(cx-2, cy-2, cx+2, cy+2, fill=WHITE, outline="")

        # Power-Pills (pulsierend)
        pulse = int(abs(math.sin(t / 20)) * 3)
        for (col, r) in self.map.powers:
            cx = col*CELL + CELL//2
            cy = r*CELL   + CELL//2
            c.create_oval(cx-7-pulse, cy-7-pulse, cx+7+pulse, cy+7+pulse,
                          fill=GOLD, outline="")
            c.create_oval(cx-5-pulse, cy-5-pulse, cx+5+pulse, cy+5+pulse,
                          fill=YELLOW, outline="")

        # Spezial-PowerUps
        for (col, r), tp in self.map.special_powers.items():
            info = POWERUP_TYPES[tp]
            cx = col*CELL + CELL//2
            cy = r*CELL   + CELL//2
            c.create_oval(cx-8, cy-8, cx+8, cy+8, fill=info["color"], outline="")
            c.create_text(cx, cy, text=info["sym"], fill=BLACK,
                          font=("Courier", 7, "bold"))

    def _draw_pac(self):
        c = self.canvas
        px, py = self.pac.px, self.pac.py
        cx = px + CELL//2
        cy = py + CELL//2
        r  = CELL//2 - 2

        if self.pac.flash > 0 and (self.pac.flash // 4) % 2 == 0:
            col = WHITE
        elif "shield" in self.pac.effects:
            col = CYAN
        else:
            col = YELLOW

        mo = self.pac.mouth
        if self.pac.dx == 0 and self.pac.dy == 0:
            c.create_oval(cx-r, cy-r, cx+r, cy+r, fill=col, outline="")
        else:
            angle = math.degrees(math.atan2(-self.pac.dy, self.pac.dx))
            start = angle + mo/2
            extent = 360 - mo
            c.create_arc(cx-r, cy-r, cx+r, cy+r,
                         start=start, extent=extent,
                         fill=col, outline="", style=tk.PIESLICE)

    def _draw_ghosts(self, t):
        c = self.canvas
        for g in self.ghosts:
            if not g.released:
                continue
            cx = g.px + CELL//2
            cy = g.py + CELL//2
            r  = CELL//2 - 2

            if g.eaten:
                c.create_text(cx, cy, text="^^", fill=WHITE,
                              font=("Courier", 12, "bold"))
                continue

            if g.frightened:
                col = BLUE if (g.frightened > 60 or (t//12) % 2 == 0) else WHITE
            else:
                col = g.color

            # Körper: Obere Hälfte = Halbkreis, untere = Rechteck
            c.create_arc(cx-r, cy-r, cx+r, cy+r,
                         start=0, extent=180,
                         fill=col, outline="")
            c.create_rectangle(cx-r, cy, cx+r, cy+r,
                               fill=col, outline="")

            # Zacken unten
            zw = (r*2) // 4
            for i in range(4):
                bx = cx - r + i*zw
                ty2 = cy + r//2 if i % 2 == 0 else cy+r
                c.create_polygon(
                    bx, cy, bx+zw, cy, bx+zw, ty2, bx, cy+r,
                    fill=col, outline=""
                )

            # Augen
            ex = cx - r//3
            ey = cy - r//4
            er = max(2, r//4)
            c.create_oval(ex-er, ey-er, ex+er, ey+er, fill=WHITE, outline="")
            c.create_oval(ex+r//2-er, ey-er, ex+r//2+er, ey+er, fill=WHITE, outline="")
            if not g.frightened:
                dx2 = g.dx * 2; dy2 = g.dy * 2
                ep = max(1, er//2)
                c.create_oval(ex+dx2-ep, ey+dy2-ep, ex+dx2+ep, ey+dy2+ep,
                              fill=DKBLUE, outline="")
                c.create_oval(ex+r//2+dx2-ep, ey+dy2-ep,
                              ex+r//2+dx2+ep, ey+dy2+ep,
                              fill=DKBLUE, outline="")

    def _draw_particles(self):
        c = self.canvas
        for p in self.particles:
            col = blend(p.color, p.alpha)
            if p.text:
                c.create_text(int(p.x), int(p.y), text=p.text, fill=col,
                              font=("Courier", 9, "bold"))
            else:
                c.create_oval(p.x-3, p.y-3, p.x+3, p.y+3, fill=col, outline="")

    def _draw_hud(self):
        c   = self.canvas
        y0  = H + 4
        c.create_rectangle(0, H, W, H+HUD_H, fill="#0a0a1a", outline="")
        c.create_line(0, H, W, H, fill=BLUE, width=2)

        c.create_text(10, y0+8, text=f"SCORE {self.score}",
                      fill=YELLOW, font=("Courier", 12, "bold"), anchor="nw")
        c.create_text(W//2, y0+8, text=f"HI {self.hi_score}",
                      fill=GOLD, font=("Courier", 10, "bold"), anchor="n")
        c.create_text(W-10, y0+8, text=f"LVL {self.level+1}  {self.diff_name}",
                      fill=CYAN, font=("Courier", 9, "bold"), anchor="ne")

        # Leben
        for i in range(self.lives):
            lx = W - 20 - i*22
            ly = y0 + 28
            c.create_oval(lx-8, ly-8, lx+8, ly+8, fill=YELLOW, outline="")

        # Effekte
        ex = 10
        for name, frames in self.pac.effects.items():
            info  = POWERUP_TYPES.get(name, {})
            col   = info.get("color", WHITE)
            desc  = info.get("desc", name.upper())
            dur_f = info.get("dur", 1) * FPS
            bar_w = max(1, int(40 * frames / max(1, dur_f)))
            c.create_rectangle(ex, y0+28, ex+40, y0+36,
                               fill="#222", outline="")
            c.create_rectangle(ex, y0+28, ex+bar_w, y0+36,
                               fill=col, outline="")
            c.create_text(ex, y0+26, text=desc[:4], fill=col,
                          font=("Courier", 7, "bold"), anchor="sw")
            ex += 50

        # Fortschrittsbalken
        if self.map:
            eaten = self.total_dots - len(self.map.dots) - len(self.map.powers)
            pct   = eaten / max(1, self.total_dots)
            c.create_rectangle(0, H-4, W, H, fill="#333", outline="")
            c.create_rectangle(0, H-4, int(W*pct), H, fill=GREEN, outline="")

    def _draw_overlay(self, text, color):
        c = self.canvas
        c.create_rectangle(0, H//2-60, W, H//2+60,
                           fill="#000000", stipple="gray50", outline="")
        c.create_text(W//2, H//2-20, text=text, fill=color,
                      font=("Courier", 22, "bold"))

    def _draw_overlay_hint(self, text):
        self.canvas.create_text(W//2, H//2+25, text=text, fill=WHITE,
                                font=("Courier", 9))

    def _draw_menu(self, t):
        c = self.canvas
        # Animierte Punkte
        for i in range(12):
            x = int(W/2 + math.cos(t/30 + i*0.5) * 180)
            y = int((H+HUD_H)/2 + math.sin(t/40 + i*0.6) * 100)
            cols = [YELLOW, RED, CYAN, PINK]
            col = cols[i % 4]
            c.create_oval(x-6, y-6, x+6, y+6, fill=col, outline="")

        c.create_text(W//2, 80, text="PAC-MAN",
                      fill=YELLOW, font=("Courier", 36, "bold"))
        c.create_text(W//2, 130, text="D  E  L  U  X  E",
                      fill=GOLD, font=("Courier", 14, "bold"))

        opts = [
            ("ENTER  –  Neues Spiel",  WHITE,  210),
            ("D      –  Schwierigkeit", CYAN,  255),
            ("ESC    –  Beenden",       GRAY,  300),
        ]
        for txt, col, y in opts:
            c.create_text(W//2, y, text=txt, fill=col,
                          font=("Courier", 12, "bold"))

        c.create_text(W//2, 360,
                      text=f"HIGHSCORE: {self.hi_score}",
                      fill=GOLD, font=("Courier", 11, "bold"))
        c.create_text(W//2, 390,
                      text=f"Schwierigkeit: {self.diff_name}",
                      fill=ORANGE, font=("Courier", 10))
        c.create_text(W//2, H+HUD_H-20,
                      text="WASD / Pfeiltasten  |  P = Pause",
                      fill="#444", font=("Courier", 8))

    def _draw_gameover(self):
        c = self.canvas
        c.create_text(W//2, 120, text="GAME OVER",
                      fill=RED, font=("Courier", 32, "bold"))
        c.create_text(W//2, 210, text=f"Score: {self.score}",
                      fill=YELLOW, font=("Courier", 20, "bold"))
        if self.score >= self.hi_score and self.score > 0:
            c.create_text(W//2, 270, text="NEUER HIGHSCORE!",
                          fill=GOLD, font=("Courier", 14, "bold"))
        c.create_text(W//2, 340, text="ENTER – Menü  |  R – Neustart",
                      fill=WHITE, font=("Courier", 11))

    # ── Starten ───────────────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


# ─── START ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PacManApp()
    app.run()
