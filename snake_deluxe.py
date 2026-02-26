"""
╔══════════════════════════════════════════════════════╗
║              S N A K E   D E L U X E               ║
║                                                      ║
║  Features:                                           ║
║  • 3 Schwierigkeitsgrade (Easy / Normal / Hard)     ║
║  • 6 Frucht-Typen mit unterschiedlichen Effekten    ║
║  • 5 Power-ups (Schild, Zeitlupe, Geist, Magnet,   ║
║    Doppelpunkte)                                     ║
║  • KI-Gegner-Schlange (ab Normal)                   ║
║  • Geister-Gegner (ab Hard)                         ║
║  • Hindernisse die auftauchen & verschwinden        ║
║  • Combo-System & Highscore                         ║
║  • Partikel-Effekte & animierte HUD                 ║
╚══════════════════════════════════════════════════════╝

Steuerung:
  Pfeiltasten / WASD  →  Bewegen
  P                   →  Pause
  ESC                 →  Menü
"""

import pygame
import random
import sys
import math
import os

# ═══════════════════════════════════════════════════════════════
#  KONSTANTEN
# ═══════════════════════════════════════════════════════════════
CELL  = 22
COLS  = 28
ROWS  = 26
W     = COLS * CELL
H     = ROWS * CELL + 80   # 80px HUD oben

# ── Farben ──────────────────────────────────────────────────────
BG          = (  6,  12,  6)
GRID_C      = (  9,  22,  9)
HUD_BG      = (  2,   6,  2)
GREEN       = (  0, 255, 65)
GREEN_DIM   = (  0, 130, 35)
GREEN_DARK  = (  0,  60, 15)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,  0)

# Schlange
S_HEAD      = (  0, 255,  65)
S_BODY      = (  0, 200,  50)
S_TAIL      = (  0,  80,  20)
S_SHIELD    = ( 80, 160, 255)   # Blau = Schild aktiv
S_GHOST     = (180, 100, 255)   # Lila = Geist-Modus

# Früchte
FRUIT_COLORS = {
    "apple":      ((255,  60,  60), "🍎", "+1 Seg, +10 Pkt"),
    "cherry":     ((220,  30, 100), "🍒", "+2 Seg, +25 Pkt"),
    "banana":     ((255, 220,  30), "🍌", "+1 Seg, +15 Pkt, Speed↑"),
    "blueberry":  (( 80, 100, 255), "🫐", "+3 Seg, +40 Pkt"),
    "strawberry": ((255,  80, 120), "🍓", "+1 Seg, +20 Pkt, Slow"),
    "lemon":      ((255, 240,  80), "🍋", "+0 Seg, +50 Pkt, Schrumpf"),
}

# Power-ups
PU_COLORS = {
    "shield":    ((80,  160, 255), "🛡", "SCHILD – 1 Treffer überleben"),
    "slow":      ((80,  255, 200), "⏱", "ZEITLUPE – alle verlangsamt"),
    "ghost":     ((180, 100, 255), "👻", "GEIST – durch dich selbst gehen"),
    "magnet":    ((255, 180,  40), "🧲", "MAGNET – Früchte anziehen"),
    "double":    ((255, 220,   0), "×2", "DOPPEL – 2× Punkte"),
}

# Hindernisse
OBSTACLE_C  = ( 80,  40,  10)
OBSTACLE_E  = (160,  80,  20)

# Gegner
ENEMY_C     = (220,  50,  50)
GHOST_C     = (200,  80, 255)

# ── Schwierigkeit ───────────────────────────────────────────────
DIFFICULTIES = {
    "easy": {
        "speed": 6, "obstacle_chance": 0.003,
        "enemy": False, "ghosts": False,
        "pu_duration": 10, "obstacle_max": 4,
    },
    "normal": {
        "speed": 9, "obstacle_chance": 0.005,
        "enemy": True, "ghosts": False,
        "pu_duration": 8, "obstacle_max": 7,
    },
    "hard": {
        "speed": 13, "obstacle_chance": 0.008,
        "enemy": True, "ghosts": True,
        "pu_duration": 6, "obstacle_max": 10,
    },
}


# ═══════════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ═══════════════════════════════════════════════════════════════
def cell_px(cx, cy):
    """Gibt Pixel-Koordinate oben-links einer Zelle zurück."""
    return cx * CELL, cy * CELL + 80


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def opposite(d1, d2):
    return d1[0] == -d2[0] and d1[1] == -d2[1]


def neighbors(x, y):
    return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]


def bfs_path(start, goal, blocked):
    """Einfaches BFS für KI-Pfadfindung."""
    from collections import deque
    q = deque([(start, [])])
    visited = {start}
    while q:
        pos, path = q.popleft()
        if pos == goal:
            return path
        for nb in neighbors(*pos):
            nx, ny = nb
            if nb not in visited and 0 <= nx < COLS and 0 <= ny < ROWS and nb not in blocked:
                visited.add(nb)
                q.append((nb, path + [nb]))
    return []


# ═══════════════════════════════════════════════════════════════
#  PARTIKEL-SYSTEM
# ═══════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, life=None, size=None):
        self.x    = x
        self.y    = y
        self.color = color
        self.vx   = vx if vx is not None else random.uniform(-2, 2)
        self.vy   = vy if vy is not None else random.uniform(-3, 0.5)
        self.life = life or random.randint(20, 50)
        self.max_life = self.life
        self.size = size or random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1   # Schwerkraft
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r, g, b = self.color
        col = (min(255, r), min(255, g), min(255, b))
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def burst(self, x, y, color, n=12):
        for _ in range(n):
            self.particles.append(Particle(x, y, color))

    def ring(self, x, y, color, n=16, speed=3):
        for i in range(n):
            angle = 2 * math.pi * i / n
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, color, vx, vy, life=30, size=3))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)


# ═══════════════════════════════════════════════════════════════
#  FLOATING TEXT
# ═══════════════════════════════════════════════════════════════
class FloatText:
    def __init__(self, x, y, text, color, size=18):
        self.x    = x
        self.y    = y
        self.text = text
        self.color = color
        self.life  = 60
        self.max_life = 60
        self.size  = size

    def update(self):
        self.y   -= 1
        self.life -= 1

    def draw(self, surf, font):
        alpha = self.life / self.max_life
        col = tuple(int(c * alpha) for c in self.color)
        s = font.render(self.text, True, col)
        surf.blit(s, (int(self.x) - s.get_width()//2, int(self.y)))


# ═══════════════════════════════════════════════════════════════
#  SCHLANGE (Spieler)
# ═══════════════════════════════════════════════════════════════
class Snake:
    def __init__(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body      = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.direction = (1, 0)
        self.next_dir  = (1, 0)
        self.grow_by   = 0

        # Power-up Status
        self.shield     = 0    # Ticks übrig
        self.slow_self  = 0
        self.ghost      = 0
        self.magnet     = 0
        self.double_pts = 0

        self.alive = True

    def set_direction(self, d):
        if not opposite(d, self.direction):
            self.next_dir = d

    def move(self):
        self.direction = self.next_dir
        dx, dy = self.direction
        hx, hy = self.body[0]
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self.grow_by > 0:
            self.grow_by -= 1
        else:
            self.body.pop()

    def head(self):
        return self.body[0]

    def shrink(self, n=2):
        for _ in range(min(n, len(self.body) - 1)):
            self.body.pop()

    def tick_powerups(self):
        if self.shield     > 0: self.shield     -= 1
        if self.slow_self  > 0: self.slow_self  -= 1
        if self.ghost      > 0: self.ghost      -= 1
        if self.magnet     > 0: self.magnet     -= 1
        if self.double_pts > 0: self.double_pts -= 1

    def collides_wall(self):
        x, y = self.head()
        return x < 0 or x >= COLS or y < 0 or y >= ROWS

    def collides_self(self):
        return self.ghost == 0 and self.head() in self.body[1:]

    def body_set(self):
        return set(self.body)


# ═══════════════════════════════════════════════════════════════
#  KI-GEGNER-SCHLANGE
# ═══════════════════════════════════════════════════════════════
class EnemySnake:
    def __init__(self):
        # Startet gegenüber dem Spieler
        sx, sy = COLS - 4, ROWS - 4
        self.body = [(sx, sy), (sx+1, sy), (sx+2, sy)]
        self.direction = (-1, 0)
        self.alive = True
        self.move_timer = 0
        self.move_interval = 3  # bewegt sich alle 3 Spieler-Ticks

    def think(self, target, blocked):
        """BFS zum nächsten Futter oder weg vom Spieler."""
        path = bfs_path(self.body[0], target, blocked | set(self.body[1:]))
        if path:
            nx, ny = path[0]
            hx, hy = self.body[0]
            self.direction = (nx - hx, ny - hy)
        else:
            # Zufällige Richtung wählen die nicht blockiert ist
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            random.shuffle(dirs)
            hx, hy = self.body[0]
            for d in dirs:
                nb = (hx + d[0], hy + d[1])
                if nb not in blocked and 0 <= nb[0] < COLS and 0 <= nb[1] < ROWS:
                    self.direction = d
                    break

    def move(self):
        dx, dy = self.direction
        hx, hy = self.body[0]
        new_head = (hx + dx, hy + dy)
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False   # Wand getroffen → tot
        self.body.insert(0, new_head)
        self.body.pop()
        return True

    def head(self):
        return self.body[0]


# ═══════════════════════════════════════════════════════════════
#  GEIST-GEGNER
# ═══════════════════════════════════════════════════════════════
class Ghost:
    def __init__(self):
        edge = random.choice(['top','bottom','left','right'])
        if edge == 'top':
            self.x, self.y = random.uniform(0, W), 80.0
            self.vx, self.vy = random.uniform(-0.5, 0.5), random.uniform(0.5, 1.5)
        elif edge == 'bottom':
            self.x, self.y = random.uniform(0, W), float(H)
            self.vx, self.vy = random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5)
        elif edge == 'left':
            self.x, self.y = 0.0, random.uniform(80, H)
            self.vx, self.vy = random.uniform(0.5, 1.5), random.uniform(-0.5, 0.5)
        else:
            self.x, self.y = float(W), random.uniform(80, H)
            self.vx, self.vy = random.uniform(-1.5, -0.5), random.uniform(-0.5, 0.5)
        self.alive = True
        self.flash = 0

    def update(self, target_px, target_py):
        """Bewegt sich langsam zum Spieler."""
        dx = target_px - self.x
        dy = target_py - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        speed = 0.8
        self.vx = self.vx * 0.95 + (dx/dist) * speed * 0.05
        self.vy = self.vy * 0.95 + (dy/dist) * speed * 0.05
        self.x += self.vx
        self.y += self.vy
        if self.flash > 0:
            self.flash -= 1

    def cell(self):
        return (int((self.x) // CELL), int((self.y - 80) // CELL))

    def draw(self, surf, tick):
        alpha = 0.6 + 0.4 * math.sin(tick * 0.1)
        r = int(CELL * 0.6)
        col = GHOST_C
        # Körper
        pygame.draw.ellipse(surf, col,
            (int(self.x)-r, int(self.y)-r, r*2, int(r*1.4)))
        # Untere Welle
        for i in range(3):
            cx = int(self.x) - r + i * (r*2//3)
            pygame.draw.circle(surf, col, (cx + r//3, int(self.y) + r//2), r//3)
        # Augen
        pygame.draw.circle(surf, BLACK, (int(self.x)-4, int(self.y)-2), 3)
        pygame.draw.circle(surf, BLACK, (int(self.x)+4, int(self.y)-2), 3)
        pygame.draw.circle(surf, WHITE, (int(self.x)-3, int(self.y)-3), 1)
        pygame.draw.circle(surf, WHITE, (int(self.x)+5, int(self.y)-3), 1)


# ═══════════════════════════════════════════════════════════════
#  SPIELFELD-OBJEKTE: Früchte & Power-ups & Hindernisse
# ═══════════════════════════════════════════════════════════════
class Fruit:
    WEIGHTS = {
        "apple":      40,
        "cherry":     20,
        "banana":     15,
        "blueberry":  10,
        "strawberry": 10,
        "lemon":       5,
    }

    def __init__(self, x, y):
        self.x = x
        self.y = y
        types = list(self.WEIGHTS.keys())
        weights = [self.WEIGHTS[t] for t in types]
        self.kind = random.choices(types, weights=weights)[0]
        self.color = FRUIT_COLORS[self.kind][0]
        self.symbol = FRUIT_COLORS[self.kind][1]
        self.desc   = FRUIT_COLORS[self.kind][2]
        self.age    = 0          # für Pulsieren
        self.lifetime = random.randint(300, 600)   # Ticks bis sie verschwindet

    def grow_amount(self):
        return {"apple":1,"cherry":2,"banana":1,"blueberry":3,"strawberry":1,"lemon":0}[self.kind]

    def points(self):
        return {"apple":10,"cherry":25,"banana":15,"blueberry":40,"strawberry":20,"lemon":50}[self.kind]

    def effect(self, snake, game):
        if self.kind == "banana":
            game.base_speed = min(game.base_speed + 1, 20)
        elif self.kind == "strawberry":
            snake.slow_self = game.cfg["pu_duration"] * 60
        elif self.kind == "lemon":
            snake.shrink(2)

    def draw(self, surf, font_emoji, tick):
        self.age += 1
        px, py = cell_px(self.x, self.y)
        cx, cy = px + CELL//2, py + CELL//2
        pulse = 1.0 + 0.12 * math.sin(self.age * 0.15)
        r = int(CELL * 0.38 * pulse)

        # Hinterglühen
        glow_surf = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 60), (r*2, r*2), r*2)
        surf.blit(glow_surf, (cx - r*2, cy - r*2))

        pygame.draw.circle(surf, self.color, (cx, cy), r)
        shine_r = max(2, r//3)
        shine_col = tuple(min(255, c+80) for c in self.color)
        pygame.draw.circle(surf, shine_col, (cx-r//4, cy-r//4), shine_r)

        # Ablauf-Warnung: blinken
        if self.lifetime - self.age < 90 and (self.age // 8) % 2 == 0:
            pygame.draw.circle(surf, WHITE, (cx, cy), r+2, 2)


class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = random.choice(list(PU_COLORS.keys()))
        self.color = PU_COLORS[self.kind][0]
        self.symbol = PU_COLORS[self.kind][1]
        self.desc   = PU_COLORS[self.kind][2]
        self.age    = 0
        self.lifetime = 400

    def apply(self, snake, game):
        dur = game.cfg["pu_duration"] * 60
        if self.kind == "shield":
            snake.shield = dur
        elif self.kind == "slow":
            game.slow_all = dur
        elif self.kind == "ghost":
            snake.ghost = dur
        elif self.kind == "magnet":
            snake.magnet = dur
        elif self.kind == "double":
            snake.double_pts = dur

    def draw(self, surf, font_pu, tick):
        self.age += 1
        px, py = cell_px(self.x, self.y)
        cx, cy = px + CELL//2, py + CELL//2

        # Rotierender Rahmen
        angle = self.age * 3
        r = int(CELL * 0.42 + 2 * math.sin(self.age * 0.1))
        pygame.draw.circle(surf, self.color, (cx, cy), r)
        pygame.draw.circle(surf, WHITE, (cx, cy), r, 2)

        # Symbol
        s = font_pu.render(self.symbol, True, BLACK if sum(self.color) > 400 else WHITE)
        surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))

        # Ablauf
        if self.lifetime - self.age < 90 and (self.age // 8) % 2 == 0:
            pygame.draw.circle(surf, WHITE, (cx, cy), r+3, 2)


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0
        self.fade_in  = 40    # Ticks zum Einblenden
        self.lifetime = random.randint(400, 900)
        self.fade_out = 40

    def alpha(self):
        if self.age < self.fade_in:
            return self.age / self.fade_in
        remaining = self.lifetime - self.age
        if remaining < self.fade_out:
            return remaining / self.fade_out
        return 1.0

    def draw(self, surf, tick):
        self.age += 1
        a = self.alpha()
        px, py = cell_px(self.x, self.y)
        col = tuple(int(c * a) for c in OBSTACLE_C)
        edge = tuple(int(c * a) for c in OBSTACLE_E)
        pygame.draw.rect(surf, col, (px+1, py+1, CELL-2, CELL-2), border_radius=3)
        pygame.draw.rect(surf, edge, (px+1, py+1, CELL-2, CELL-2), 2, border_radius=3)

        # Kreuz-Muster
        pygame.draw.line(surf, edge, (px+4, py+4), (px+CELL-5, py+CELL-5), 2)
        pygame.draw.line(surf, edge, (px+CELL-5, py+4), (px+4, py+CELL-5), 2)


# ═══════════════════════════════════════════════════════════════
#  HAUPT-SPIEL
# ═══════════════════════════════════════════════════════════════
class Game:
    def __init__(self, difficulty="normal"):
        self.cfg        = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.snake      = Snake()
        self.fruits     : list[Fruit]    = []
        self.powerups   : list[PowerUp]  = []
        self.obstacles  : list[Obstacle] = []
        self.enemy      : EnemySnake | None = None
        self.ghosts     : list[Ghost]    = []
        self.particles  = ParticleSystem()
        self.floats     : list[FloatText] = []

        self.score      = 0
        self.combo      = 0
        self.combo_timer = 0
        self.level      = 1
        self.base_speed = self.cfg["speed"]
        self.slow_all   = 0    # Ticks Zeitlupe

        self.tick       = 0
        self.move_timer = 0

        if self.cfg["enemy"]:
            self.enemy = EnemySnake()
        if self.cfg["ghosts"]:
            for _ in range(2):
                self.ghosts.append(Ghost())

        # Erste Früchte
        for _ in range(3):
            self.spawn_fruit()

    # ── Hilfsmethoden ──────────────────────────────────────────
    def all_blocked(self, include_snake=True):
        blocked = set(self.obstacles_cells())
        if include_snake:
            blocked |= self.snake.body_set()
        if self.enemy:
            blocked |= set(self.enemy.body)
        return blocked

    def obstacles_cells(self):
        return {(o.x, o.y) for o in self.obstacles}

    def free_cell(self):
        blocked = self.all_blocked() | {(f.x,f.y) for f in self.fruits} | {(p.x,p.y) for p in self.powerups}
        attempts = 0
        while attempts < 500:
            x = random.randint(1, COLS-2)
            y = random.randint(1, ROWS-2)
            if (x,y) not in blocked:
                return x, y
            attempts += 1
        return None

    def spawn_fruit(self):
        pos = self.free_cell()
        if pos:
            self.fruits.append(Fruit(*pos))

    def spawn_powerup(self):
        pos = self.free_cell()
        if pos:
            self.powerups.append(PowerUp(*pos))

    def spawn_obstacle(self):
        blocked = self.all_blocked() | {(f.x,f.y) for f in self.fruits} | {(p.x,p.y) for p in self.powerups}
        # Nicht zu nah an Schlangenkopf
        hx, hy = self.snake.head()
        for _ in range(100):
            x = random.randint(1, COLS-2)
            y = random.randint(1, ROWS-2)
            if (x,y) not in blocked and abs(x-hx)+abs(y-hy) > 5:
                self.obstacles.append(Obstacle(x, y))
                return

    def add_float(self, x, y, text, color=(255,255,100)):
        px, py = cell_px(x, y)
        self.floats.append(FloatText(px + CELL//2, py, text, color))

    def effective_speed(self):
        speed = self.base_speed
        if self.slow_all > 0:
            speed = max(2, speed // 2)
        if self.snake.slow_self > 0:
            speed = max(2, speed - 2)
        return speed

    # ── Haupt-Update ───────────────────────────────────────────
    def update(self, dt):
        self.tick += 1

        # Combo-Timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # Zeitlupe
        if self.slow_all > 0:
            self.slow_all -= 1

        # Power-up-Timer Schlange
        self.snake.tick_powerups()

        # Partikel & Floats
        self.particles.update()
        self.floats = [f for f in self.floats if f.life > 0]
        for f in self.floats:
            f.update()

        # Früchte-Timeout
        self.fruits = [f for f in self.fruits if f.age < f.lifetime]
        self.powerups = [p for p in self.powerups if p.age < p.lifetime]

        # Hindernisse spawn/despawn
        if random.random() < self.cfg["obstacle_chance"] and len(self.obstacles) < self.cfg["obstacle_max"]:
            self.spawn_obstacle()
        self.obstacles = [o for o in self.obstacles if o.age < o.lifetime]

        # Power-up spawn (alle ~10s zufällig)
        if random.random() < 0.003 and len(self.powerups) < 2:
            self.spawn_powerup()

        # Früchte nachfüllen
        if len(self.fruits) < 3 and random.random() < 0.05:
            self.spawn_fruit()

        # Geister updaten
        hpx, hpy = cell_px(*self.snake.head())
        hpx += CELL//2; hpy += CELL//2
        for g in self.ghosts:
            g.update(hpx, hpy)

        # Schlangenbewegungs-Timing
        interval = 1000 / self.effective_speed()
        self.move_timer += dt
        if self.move_timer < interval:
            return None   # noch nicht Zeit zum Bewegen

        self.move_timer -= interval

        # ── Schlange bewegen ───────────────────────────────────
        # Magnet: nächste Frucht anziehen (zur Schlange hin verschieben)
        if self.snake.magnet > 0 and self.fruits:
            hx, hy = self.snake.head()
            closest = min(self.fruits, key=lambda f: abs(f.x-hx)+abs(f.y-hy))
            # Frucht schrittweise anziehen
            dx = 0 if closest.x == hx else (1 if closest.x > hx else -1)
            dy = 0 if closest.y == hy else (1 if closest.y > hy else -1)
            # Nur bewegen wenn Zielzelle frei
            nx, ny = closest.x - dx, closest.y - dy
            if (nx, ny) not in self.all_blocked() and 0 < nx < COLS-1 and 0 < ny < ROWS-1:
                closest.x, closest.y = nx, ny

        self.snake.move()

        # ── Kollision Wand / Selbst ────────────────────────────
        if self.snake.collides_wall() or self.snake.collides_self():
            if self.snake.shield > 0:
                self.snake.shield = 0
                # Schlange zurücksetzen zum vorletzten Segment
                self.snake.body = self.snake.body[1:]
                self.add_float(*self.snake.head(), "SCHILD!", (80,160,255))
                self.particles.ring(*cell_px(*self.snake.head()), S_SHIELD)
            else:
                return "dead"

        # ── Kollision Hindernisse ──────────────────────────────
        if self.snake.head() in self.obstacles_cells():
            if self.snake.shield > 0:
                self.snake.shield = 0
                self.snake.body = self.snake.body[1:]
                self.add_float(*self.snake.head(), "SCHILD!", (80,160,255))
                self.particles.ring(*cell_px(*self.snake.head()), S_SHIELD)
            else:
                return "dead"

        # ── Früchte fressen ───────────────────────────────────
        eaten = [f for f in self.fruits if f.x == self.snake.head()[0] and f.y == self.snake.head()[1]]
        for f in eaten:
            self.fruits.remove(f)
            self.snake.grow_by += f.grow_amount()
            f.effect(self.snake, self)

            self.combo += 1
            self.combo_timer = 180
            pts = f.points() * self.combo
            if self.snake.double_pts > 0:
                pts *= 2
            self.score += pts

            px, py = cell_px(f.x, f.y)
            self.particles.burst(px + CELL//2, py + CELL//2, f.color, n=16)
            combo_str = f"+{pts}" + (f" ×{self.combo}!" if self.combo > 1 else "")
            self.add_float(f.x, f.y, combo_str, f.color)

            self.spawn_fruit()
            # Level berechnen
            self.level = self.score // 150 + 1

        # ── Power-ups aufheben ────────────────────────────────
        taken = [p for p in self.powerups if p.x == self.snake.head()[0] and p.y == self.snake.head()[1]]
        for p in taken:
            self.powerups.remove(p)
            p.apply(self.snake, self)
            px, py = cell_px(p.x, p.y)
            self.particles.ring(px + CELL//2, py + CELL//2, p.color, n=20, speed=4)
            self.add_float(p.x, p.y, p.desc.split("–")[0].strip(), p.color)

        # ── KI-Gegner ─────────────────────────────────────────
        if self.enemy and self.enemy.alive:
            self.enemy.move_timer += 1
            if self.enemy.move_timer >= self.enemy.move_interval:
                self.enemy.move_timer = 0
                blocked = self.all_blocked(include_snake=False) | self.snake.body_set()
                # KI zielt auf nächste Frucht
                if self.fruits:
                    target = min(self.fruits, key=lambda f: abs(f.x-self.enemy.head()[0])+abs(f.y-self.enemy.head()[1]))
                    self.enemy.think((target.x, target.y), blocked)
                self.enemy.move()

                # Gegner frisst Frucht?
                eaten_by_enemy = [f for f in self.fruits if f.x == self.enemy.head()[0] and f.y == self.enemy.head()[1]]
                for f in eaten_by_enemy:
                    self.fruits.remove(f)
                    self.spawn_fruit()

                # Spieler vom Gegner getroffen?
                if self.enemy.head() == self.snake.head():
                    if self.snake.shield > 0:
                        self.snake.shield = 0
                        # Gegner zurücksetzen
                        self.enemy = EnemySnake()
                        self.add_float(*self.snake.head(), "BLOCK!", (80,160,255))
                    else:
                        return "dead"

                # Gegner in Hindernis?
                if self.enemy.head() in self.obstacles_cells():
                    px2, py2 = cell_px(*self.enemy.head())
                    self.particles.burst(px2+CELL//2, py2+CELL//2, ENEMY_C)
                    self.enemy = EnemySnake()   # Respawn

        # ── Geister ───────────────────────────────────────────
        for g in self.ghosts:
            if g.cell() == self.snake.head():
                if self.snake.shield > 0:
                    self.snake.shield = 0
                    g.flash = 30
                    self.add_float(*self.snake.head(), "SCHILD!", (80,160,255))
                elif self.snake.ghost > 0:
                    pass   # Geist-Modus: Geister ignorieren
                else:
                    return "dead"

        return None

    # ── Zeichnen ───────────────────────────────────────────────
    def draw(self, surf, fonts):
        font_hud, font_sm, font_pu, font_float = fonts

        # Hintergrund & Grid
        surf.fill(BG)
        for x in range(COLS):
            for y in range(ROWS):
                px, py = cell_px(x, y)
                pygame.draw.rect(surf, GRID_C, (px, py, CELL, CELL), 1)

        # Hindernisse
        for o in self.obstacles:
            o.draw(surf, self.tick)

        # Früchte
        for f in self.fruits:
            f.draw(surf, font_pu, self.tick)

        # Power-ups
        for p in self.powerups:
            p.draw(surf, font_pu, self.tick)

        # Schlange
        self._draw_snake(surf)

        # Gegner-Schlange
        if self.enemy and self.enemy.alive:
            self._draw_enemy(surf)

        # Geister
        for g in self.ghosts:
            g.draw(surf, self.tick)

        # Partikel
        self.particles.draw(surf)

        # Floating Texts
        for ft in self.floats:
            ft.draw(surf, font_float)

        # HUD
        self._draw_hud(surf, font_hud, font_sm, font_pu)

        # Power-up-Leiste
        self._draw_powerup_bar(surf, font_sm)

    def _draw_snake(self, surf):
        n = len(self.snake.body)
        has_shield = self.snake.shield > 0
        has_ghost  = self.snake.ghost > 0

        for i, (x, y) in enumerate(self.snake.body):
            px, py = cell_px(x, y)
            if i == 0:
                if has_shield:
                    base = S_SHIELD
                elif has_ghost:
                    base = S_GHOST
                else:
                    base = S_HEAD
            else:
                t = i / n
                base = lerp_color(S_BODY, S_TAIL, t)
                if has_ghost:
                    base = lerp_color(base, S_GHOST, 0.5)

            # Geist-Modus: halb transparent
            alpha = 140 if has_ghost and i > 0 else 255
            seg_surf = pygame.Surface((CELL-2, CELL-2), pygame.SRCALPHA)
            seg_surf.fill((*base, alpha))
            surf.blit(seg_surf, (px+1, py+1))
            if i == 0:
                pygame.draw.rect(surf, base, (px+1, py+1, CELL-2, CELL-2), border_radius=5)
            else:
                pygame.draw.rect(surf, base, (px+1, py+1, CELL-2, CELL-2), border_radius=3)

            # Schild-Aura
            if i == 0 and has_shield:
                prog = (self.tick % 30) / 30
                r2 = int(CELL * 0.7 + 4 * math.sin(prog * 2 * math.pi))
                cx2, cy2 = px + CELL//2, py + CELL//2
                shield_surf = pygame.Surface((r2*2+4, r2*2+4), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, (*S_SHIELD, 80), (r2+2, r2+2), r2)
                pygame.draw.circle(shield_surf, (*S_SHIELD, 200), (r2+2, r2+2), r2, 2)
                surf.blit(shield_surf, (cx2 - r2-2, cy2 - r2-2))

            # Augen am Kopf
            if i == 0:
                dx, dy = self.snake.direction
                cx2, cy2 = px + CELL//2, py + CELL//2
                perp = (-dy, dx)
                for sign in (+1, -1):
                    ex = cx2 + dx*5 + perp[0]*4*sign
                    ey = cy2 + dy*5 + perp[1]*4*sign
                    pygame.draw.circle(surf, BLACK, (ex, ey), 2)
                    pygame.draw.circle(surf, WHITE, (ex-1, ey-1), 1)

    def _draw_enemy(self, surf):
        n = len(self.enemy.body)
        for i, (x, y) in enumerate(self.enemy.body):
            px, py = cell_px(x, y)
            t = i / n
            col = lerp_color(ENEMY_C, (80, 10, 10), t)
            pygame.draw.rect(surf, col, (px+1, py+1, CELL-2, CELL-2), border_radius=3)
            if i == 0:
                # Gegner-Augen
                dx, dy = self.enemy.direction
                cx2, cy2 = px + CELL//2, py + CELL//2
                perp = (-dy, dx)
                for sign in (+1, -1):
                    ex = cx2 + dx*5 + perp[0]*4*sign
                    ey = cy2 + dy*5 + perp[1]*4*sign
                    pygame.draw.circle(surf, (255, 200, 0), (ex, ey), 2)

    def _draw_hud(self, surf, font_hud, font_sm, font_pu):
        pygame.draw.rect(surf, HUD_BG, (0, 0, W, 80))
        pygame.draw.line(surf, GREEN, (0, 79), (W, 79), 1)

        # Titel
        title = font_hud.render("SNAKE DELUXE", True, GREEN)
        surf.blit(title, (10, 8))

        # Werte
        items = [
            (f"SCORE  {self.score:06d}", GREEN),
            (f"LEVEL  {self.level}", (100,255,150)),
            (f"COMBO  ×{self.combo}", (255,220,50) if self.combo > 1 else GREEN_DIM),
        ]
        for i, (txt, col) in enumerate(items):
            s = font_sm.render(txt, True, col)
            surf.blit(s, (10 + i * (W//3), 38))

        # Schwierigkeit
        diff_col = {"easy":(80,255,80),"normal":(255,200,50),"hard":(255,80,80)}[self.difficulty]
        ds = font_sm.render(self.difficulty.upper(), True, diff_col)
        surf.blit(ds, (W - ds.get_width() - 10, 8))

        # Schlangen-Länge
        ls = font_sm.render(f"LEN {len(self.snake.body):03d}", True, GREEN_DIM)
        surf.blit(ls, (W - ls.get_width() - 10, 38))

    def _draw_powerup_bar(self, surf, font_sm):
        """Zeigt aktive Power-ups mit Timer-Balken."""
        active = []
        if self.snake.shield     > 0: active.append(("SCHILD",    self.snake.shield,     self.cfg["pu_duration"]*60, S_SHIELD))
        if self.snake.ghost      > 0: active.append(("GEIST",     self.snake.ghost,      self.cfg["pu_duration"]*60, S_GHOST))
        if self.snake.magnet     > 0: active.append(("MAGNET",    self.snake.magnet,     self.cfg["pu_duration"]*60, (255,180,40)))
        if self.snake.double_pts > 0: active.append(("×2 PTS",    self.snake.double_pts, self.cfg["pu_duration"]*60, (255,220,0)))
        if self.slow_all         > 0: active.append(("ZEITLUPE",  self.slow_all,         self.cfg["pu_duration"]*60, (80,255,200)))
        if self.snake.slow_self  > 0: active.append(("SLOW",      self.snake.slow_self,  self.cfg["pu_duration"]*60, (200,200,80)))

        bw = 80
        for i, (label, remaining, total, col) in enumerate(active):
            bx = 10 + i * (bw + 8)
            by = H - 28
            # Hintergrund
            pygame.draw.rect(surf, (20, 20, 20), (bx, by, bw, 20), border_radius=4)
            # Fortschritt
            prog = remaining / total
            pw = int(bw * prog)
            pygame.draw.rect(surf, col, (bx, by, pw, 20), border_radius=4)
            # Label
            s = font_sm.render(label, True, BLACK if sum(col) > 400 else WHITE)
            surf.blit(s, (bx + bw//2 - s.get_width()//2, by + 2))


# ═══════════════════════════════════════════════════════════════
#  MENÜ-BILDSCHIRM
# ═══════════════════════════════════════════════════════════════
class Menu:
    def __init__(self, fonts):
        self.selected = 1   # 0=easy, 1=normal, 2=hard
        self.fonts    = fonts
        self.tick     = 0
        self.labels   = ["EASY", "NORMAL", "HARD"]
        self.descs    = [
            "Langsam · Wenig Hindernisse · Kein Gegner",
            "Normal · Hindernisse · KI-Gegner",
            "Schnell · Viele Hindernisse · Gegner + Geister",
        ]
        self.cols = [
            (80, 255, 80),
            (255, 200, 50),
            (255, 80, 80),
        ]

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % 3
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return ["easy","normal","hard"][self.selected]
        return None

    def draw(self, surf):
        self.tick += 1
        surf.fill(BG)

        font_big, font_med, font_sm, font_pu, font_float = self.fonts

        # Animated grid background
        for x in range(COLS):
            for y in range(ROWS+4):
                px2, py2 = x * CELL, y * CELL
                pygame.draw.rect(surf, GRID_C, (px2, py2, CELL, CELL), 1)

        # Titel
        title_text = "SNAKE DELUXE"
        t = font_big.render(title_text, True, GREEN)
        glow_surf = pygame.Surface((t.get_width()+20, t.get_height()+20), pygame.SRCALPHA)
        g_t = font_big.render(title_text, True, (*GREEN, 60))
        for off in [(-2,0),(2,0),(0,-2),(0,2)]:
            glow_surf.blit(g_t, (10+off[0], 10+off[1]))
        surf.blit(glow_surf, (W//2 - t.get_width()//2 - 10, H//2 - 160 - 10))
        surf.blit(t, (W//2 - t.get_width()//2, H//2 - 160))

        sub = font_sm.render("Wähle Schwierigkeitsgrad  ←  →", True, GREEN_DIM)
        surf.blit(sub, (W//2 - sub.get_width()//2, H//2 - 110))

        # Schwierigkeit-Auswahl
        box_w, box_h = 160, 70
        total_w = 3 * box_w + 2 * 20
        start_x = W//2 - total_w//2

        for i, (label, desc, col) in enumerate(zip(self.labels, self.descs, self.cols)):
            bx = start_x + i * (box_w + 20)
            by = H//2 - 50
            selected = (i == self.selected)

            # Kasten
            bg_col = (20, 40, 20) if not selected else (int(col[0]*0.3), int(col[1]*0.3), int(col[2]*0.3))
            pygame.draw.rect(surf, bg_col, (bx, by, box_w, box_h), border_radius=8)
            border_col = col if selected else GREEN_DARK
            border_w   = 3 if selected else 1
            pygame.draw.rect(surf, border_col, (bx, by, box_w, box_h), border_w, border_radius=8)

            pulse = 1 + 0.05 * math.sin(self.tick * 0.08) if selected else 1
            ls = font_med.render(label, True, col if selected else GREEN_DIM)
            surf.blit(ls, (bx + box_w//2 - ls.get_width()//2, by + 12))

            if selected:
                arrow = font_sm.render("▲ ENTER", True, col)
                surf.blit(arrow, (bx + box_w//2 - arrow.get_width()//2, by + box_h + 5))

        # Beschreibung
        desc = self.descs[self.selected]
        ds = font_sm.render(desc, True, self.cols[self.selected])
        surf.blit(ds, (W//2 - ds.get_width()//2, H//2 + 50))

        # Feature-Liste
        features = [
            "🍎 Apfel  🍒 Kirsche  🍌 Banane  🫐 Heidelbeere  🍓 Erdbeere  🍋 Zitrone",
            "🛡 Schild  ⏱ Zeitlupe  👻 Geist  🧲 Magnet  ×2 Doppelpunkte",
            "Steuerung: Pfeiltasten / WASD  |  P = Pause  |  ESC = Menü",
        ]
        for i, feat in enumerate(features):
            fs = font_float.render(feat, True, GREEN_DIM)
            surf.blit(fs, (W//2 - fs.get_width()//2, H//2 + 100 + i * 26))


# ═══════════════════════════════════════════════════════════════
#  HAUPT-PROGRAMM
# ═══════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("SNAKE DELUXE")
    clock = pygame.time.Clock()

    # Fonts
    def try_font(name, size, bold=False):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            return pygame.font.SysFont(None, size, bold=bold)

    font_big   = try_font("Courier New", 42, bold=True)
    font_med   = try_font("Courier New", 24, bold=True)
    font_hud   = try_font("Courier New", 15, bold=True)
    font_sm    = try_font("Courier New", 14)
    font_pu    = try_font("Courier New", 13, bold=True)
    font_float = try_font("Courier New", 13)

    highscore = 0
    state     = "menu"
    game      = None
    menu      = Menu([font_big, font_med, font_sm, font_pu, font_float])
    chosen_diff = "normal"

    paused    = False

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "menu":
                result = menu.handle(event)
                if result:
                    chosen_diff = result
                    game = Game(chosen_diff)
                    state = "playing"
                    paused = False

            elif state == "playing" and not paused:
                if event.type == pygame.KEYDOWN:
                    km = {
                        pygame.K_UP:    (0,-1), pygame.K_w: (0,-1),
                        pygame.K_DOWN:  (0, 1), pygame.K_s: (0, 1),
                        pygame.K_LEFT:  (-1,0), pygame.K_a: (-1,0),
                        pygame.K_RIGHT: ( 1,0), pygame.K_d: ( 1,0),
                    }
                    if event.key in km:
                        game.snake.set_direction(km[event.key])
                    elif event.key == pygame.K_p:
                        paused = True
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                        menu = Menu([font_big, font_med, font_sm, font_pu, font_float])

            elif paused:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        paused = False

            elif state == "gameover":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = Game(chosen_diff)
                        state = "playing"
                        paused = False
                    elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                        state = "menu"
                        menu = Menu([font_big, font_med, font_sm, font_pu, font_float])

        # ── Update ─────────────────────────────────────────────
        if state == "playing" and not paused:
            result = game.update(dt)
            if result == "dead":
                if game.score > highscore:
                    highscore = game.score
                state = "gameover"

        # ── Zeichnen ───────────────────────────────────────────
        if state == "menu":
            menu.draw(screen)

        elif state in ("playing", "gameover"):
            game.draw(screen, [font_hud, font_sm, font_pu, font_float])

            if paused:
                _draw_overlay(screen, font_big, font_sm,
                              "PAUSE",
                              ["P / ESC zum Fortfahren"],
                              (10, 30, 10, 200))

            elif state == "gameover":
                new_hs = game.score >= highscore
                lines = [
                    f"Score:      {game.score}",
                    f"Highscore:  {highscore}",
                    f"Level:      {game.level}",
                    f"Länge:      {len(game.snake.body)}",
                    "",
                    "R = Nochmal  |  ESC / M = Menü",
                ]
                if new_hs and game.score > 0:
                    lines.insert(0, "★ NEUER HIGHSCORE! ★")
                _draw_overlay(screen, font_big, font_sm,
                              "GAME OVER", lines, (20, 5, 5, 210))

        pygame.display.flip()


def _draw_overlay(surf, font_big, font_sm, title, lines, bg_color=(5,15,5,200)):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill(bg_color)
    surf.blit(ov, (0, 0))

    t = font_big.render(title, True, GREEN)
    surf.blit(t, t.get_rect(center=(W//2, H//2 - 80 - len(lines)*14)))

    for i, line in enumerate(lines):
        col = (255, 220, 50) if "★" in line else GREEN
        s = font_sm.render(line, True, col)
        surf.blit(s, s.get_rect(center=(W//2, H//2 - 40 + i * 26 - len(lines)*7)))


if __name__ == "__main__":
    main()