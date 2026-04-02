#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║          R I S I K O  -  Welteroberungsstrategie                 ║
║          Pygame Premium Edition mit HD-Grafik & Extras           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import os
import json
import random
import math
import time
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Pygame initialisieren
pygame.init()
pygame.mixer.init()

# ───────────────────────── KONFIGURATION ─────────────────────────
WIDTH, HEIGHT = 1280, 800
FPS = 60
TARGET_FPS = 60

# Farben
COLORS = {
    "bg_dark": "#0a0a1a",
    "bg_panel": "#0d1a2e",
    "bg_card": "#16213e",
    "gold": "#f0c040",
    "gold_dark": "#c09020",
    "text_primary": "#f0f0f0",
    "text_secondary": "#a0a0c0",
    "text_dim": "#606080",
    "accent_red": "#e74c3c",
    "accent_blue": "#3498db",
    "accent_green": "#2ecc71",
    "accent_purple": "#9b59b6",
    "accent_orange": "#f39c12",
    "accent_cyan": "#1abc9c",
    "player_colors": ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6", "#f39c12", "#1abc9c"],
    "continent_colors": {
        "Nordamerika": "#d4a843",
        "Südamerika": "#5fad56",
        "Europa": "#4a90d9",
        "Afrika": "#c0763e",
        "Asien": "#9b59b6",
        "Australien": "#e74c3c",
    }
}

# Spielkarte (Koordinaten für Pygame angepasst)
TERRITORIES = {
    "Alaska":              {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium","Alberta","Kamtschatka"], "pos": (80,140)},
    "Nordwest-Territorium":{"continent": "Nordamerika", "neighbors": ["Alaska","Alberta","Ontario","Grönland"], "pos": (160,120)},
    "Grönland":            {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium","Ontario","Quebec","Island"], "pos": (320,90)},
    "Alberta":             {"continent": "Nordamerika", "neighbors": ["Alaska","Nordwest-Territorium","Ontario","Weststaaten"], "pos": (150,170)},
    "Ontario":             {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium","Grönland","Alberta","Weststaaten","Quebec","Oststaaten"], "pos": (230,170)},
    "Quebec":              {"continent": "Nordamerika", "neighbors": ["Ontario","Grönland","Oststaaten"], "pos": (300,165)},
    "Weststaaten":         {"continent": "Nordamerika", "neighbors": ["Alberta","Ontario","Oststaaten","Mittelamerika"], "pos": (165,220)},
    "Oststaaten":          {"continent": "Nordamerika", "neighbors": ["Weststaaten","Ontario","Quebec","Mittelamerika"], "pos": (250,220)},
    "Mittelamerika":       {"continent": "Nordamerika", "neighbors": ["Weststaaten","Oststaaten","Venezuela"], "pos": (190,275)},
    "Venezuela":           {"continent": "Südamerika", "neighbors": ["Mittelamerika","Peru","Brasilien"], "pos": (250,330)},
    "Peru":                {"continent": "Südamerika", "neighbors": ["Venezuela","Brasilien","Argentinien"], "pos": (250,390)},
    "Brasilien":           {"continent": "Südamerika", "neighbors": ["Venezuela","Peru","Argentinien","Nordafrika"], "pos": (315,370)},
    "Argentinien":         {"continent": "Südamerika", "neighbors": ["Peru","Brasilien"], "pos": (270,440)},
    "Island":              {"continent": "Europa", "neighbors": ["Grönland","Großbritannien","Skandinavien"], "pos": (420,120)},
    "Großbritannien":      {"continent": "Europa", "neighbors": ["Island","Skandinavien","Nordeuropa","Westeuropa"], "pos": (435,165)},
    "Skandinavien":        {"continent": "Europa", "neighbors": ["Island","Großbritannien","Nordeuropa","Ukraine"], "pos": (500,125)},
    "Nordeuropa":          {"continent": "Europa", "neighbors": ["Großbritannien","Skandinavien","Westeuropa","Mitteleuropa","Ukraine"], "pos": (495,170)},
    "Westeuropa":          {"continent": "Europa", "neighbors": ["Großbritannien","Nordeuropa","Mitteleuropa","Nordafrika"], "pos": (455,220)},
    "Mitteleuropa":        {"continent": "Europa", "neighbors": ["Nordeuropa","Westeuropa","Ukraine","Südeuropa"], "pos": (515,210)},
    "Ukraine":             {"continent": "Europa", "neighbors": ["Skandinavien","Nordeuropa","Mitteleuropa","Südeuropa","Ural","Afghanistan","Mittlerer Osten"], "pos": (580,180)},
    "Südeuropa":           {"continent": "Europa", "neighbors": ["Westeuropa","Mitteleuropa","Ukraine","Nordafrika","Ägypten","Mittlerer Osten"], "pos": (520,255)},
    "Nordafrika":          {"continent": "Afrika", "neighbors": ["Brasilien","Westeuropa","Südeuropa","Ägypten","Ostafrika","Zentralafrika"], "pos": (470,305)},
    "Ägypten":             {"continent": "Afrika", "neighbors": ["Nordafrika","Südeuropa","Mittlerer Osten","Ostafrika"], "pos": (555,305)},
    "Zentralafrika":       {"continent": "Afrika", "neighbors": ["Nordafrika","Ostafrika","Südafrika"], "pos": (520,370)},
    "Ostafrika":           {"continent": "Afrika", "neighbors": ["Nordafrika","Ägypten","Zentralafrika","Südafrika","Madagaskar","Mittlerer Osten"], "pos": (590,365)},
    "Südafrika":           {"continent": "Afrika", "neighbors": ["Zentralafrika","Ostafrika","Madagaskar"], "pos": (535,440)},
    "Madagaskar":          {"continent": "Afrika", "neighbors": ["Ostafrika","Südafrika"], "pos": (620,425)},
    "Ural":                {"continent": "Asien", "neighbors": ["Ukraine","Sibirien","Afghanistan","China"], "pos": (660,155)},
    "Sibirien":            {"continent": "Asien", "neighbors": ["Ural","Jakutien","Irkutsk","Mongolei","China"], "pos": (735,125)},
    "Jakutien":            {"continent": "Asien", "neighbors": ["Sibirien","Kamtschatka","Irkutsk"], "pos": (820,110)},
    "Kamtschatka":         {"continent": "Asien", "neighbors": ["Jakutien","Irkutsk","Mongolei","Japan","Alaska"], "pos": (910,125)},
    "Irkutsk":             {"continent": "Asien", "neighbors": ["Sibirien","Jakutien","Kamtschatka","Mongolei"], "pos": (800,175)},
    "Mongolei":            {"continent": "Asien", "neighbors": ["Sibirien","Kamtschatka","Irkutsk","China","Japan"], "pos": (810,220)},
    "Japan":               {"continent": "Asien", "neighbors": ["Kamtschatka","Mongolei"], "pos": (910,210)},
    "Afghanistan":         {"continent": "Asien", "neighbors": ["Ukraine","Ural","China","Indien","Mittlerer Osten"], "pos": (670,240)},
    "China":               {"continent": "Asien", "neighbors": ["Ural","Sibirien","Mongolei","Afghanistan","Indien","Siam"], "pos": (770,255)},
    "Mittlerer Osten":     {"continent": "Asien", "neighbors": ["Ukraine","Südeuropa","Ägypten","Ostafrika","Afghanistan","Indien"], "pos": (630,295)},
    "Indien":              {"continent": "Asien", "neighbors": ["Mittlerer Osten","Afghanistan","China","Siam"], "pos": (720,320)},
    "Siam":                {"continent": "Asien", "neighbors": ["China","Indien","Indonesien"], "pos": (800,325)},
    "Indonesien":          {"continent": "Australien", "neighbors": ["Siam","Neuguinea","Westaustralien"], "pos": (835,400)},
    "Neuguinea":           {"continent": "Australien", "neighbors": ["Indonesien","Westaustralien","Ostaustralien"], "pos": (910,380)},
    "Westaustralien":      {"continent": "Australien", "neighbors": ["Indonesien","Neuguinea","Ostaustralien"], "pos": (875,465)},
    "Ostaustralien":       {"continent": "Australien", "neighbors": ["Neuguinea","Westaustralien"], "pos": (950,460)},
}

CONTINENTS = {
    "Nordamerika": {"bonus": 5, "color": COLORS["continent_colors"]["Nordamerika"], 
                    "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Nordamerika"]},
    "Südamerika":  {"bonus": 2, "color": COLORS["continent_colors"]["Südamerika"],
                    "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Südamerika"]},
    "Europa":      {"bonus": 5, "color": COLORS["continent_colors"]["Europa"],
                    "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Europa"]},
    "Afrika":      {"bonus": 3, "color": COLORS["continent_colors"]["Afrika"],
                    "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Afrika"]},
    "Asien":       {"bonus": 7, "color": COLORS["continent_colors"]["Asien"],
                    "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Asien"]},
    "Australien":  {"bonus": 2, "color": COLORS["continent_colors"]["Australien"],
                    "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Australien"]},
}

CARD_TYPES = ["Infanterie","Kavallerie","Artillerie"]
CARD_EXCHANGE_BONUS = [4, 6, 8, 10, 12, 15]

# ───────────────────────── SOUND SYSTEM ──────────────────────────
class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.music_playing = False
        self._generate_sounds()

    def _generate_sounds(self):
        """Generiert Sound-Effekte programmatisch"""
        try:
            # Attack sound
            attack_buffer = bytearray()
            for i in range(8000):
                val = int(127 * math.sin(2 * math.pi * 440 * i / 22050) * 
                         (1 - i/8000) ** 2)
                attack_buffer.extend([(val + 128) % 256])
            self.sounds["attack"] = pygame.mixer.Sound(buffer=bytes(attack_buffer))
            self.sounds["attack"].set_volume(0.3)

            # Conquest sound
            conquest_buffer = bytearray()
            for i in range(10000):
                freq = 440 + (i / 10000) * 440
                val = int(127 * math.sin(2 * math.pi * freq * i / 22050) * 
                         (1 - i/10000))
                conquest_buffer.extend([(val + 128) % 256])
            self.sounds["conquest"] = pygame.mixer.Sound(buffer=bytes(conquest_buffer))
            self.sounds["conquest"].set_volume(0.4)

            # Place troop sound
            place_buffer = bytearray()
            for i in range(4000):
                val = int(60 * math.sin(2 * math.pi * 600 * i / 22050) * 
                         (1 - i/4000) ** 3)
                place_buffer.extend([(val + 128) % 256])
            self.sounds["place"] = pygame.mixer.Sound(buffer=bytes(place_buffer))
            self.sounds["place"].set_volume(0.2)

            # UI click
            click_buffer = bytearray()
            for i in range(2000):
                val = int(40 * math.sin(2 * math.pi * 1000 * i / 22050) * 
                         (1 - i/2000) ** 4)
                click_buffer.extend([(val + 128) % 256])
            self.sounds["click"] = pygame.mixer.Sound(buffer=bytes(click_buffer))
            self.sounds["click"].set_volume(0.3)

        except Exception as e:
            print(f"Sound-Generierung fehlgeschlagen: {e}")
            self.enabled = False

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled


# ───────────────────────── PARTIKEL-SYSTEM ───────────────────────
class Particle:
    def __init__(self, x, y, color, vx, vy, life, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # Schwerkraft
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = self.life / self.max_life
        r, g, b = self.color
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((r, g, b, int(255 * alpha)))
        surface.blit(s, (int(self.x), int(self.y)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, speed=2, size=3):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - 1
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, vx, vy, life, size))

    def explosion(self, x, y, count=30):
        colors = [(255, 100, 50), (255, 200, 50), (255, 50, 50), (200, 200, 200)]
        for _ in range(count):
            color = random.choice(colors)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.particles.append(Particle(
                x, y, color,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 1.5,
                random.randint(15, 35),
                random.randint(2, 5)
            ))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


# ───────────────────────── ANIMATIONEN ───────────────────────────
class Animation:
    def __init__(self, duration, easing="linear"):
        self.duration = duration
        self.elapsed = 0
        self.easing = easing
        self.running = True
        self.complete = False

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.complete = True
            self.running = False
        return self.progress()

    def progress(self):
        t = min(1.0, self.elapsed / self.duration)
        if self.easing == "ease_out":
            return 1 - (1 - t) ** 3
        elif self.easing == "ease_in_out":
            return t * t * (3 - 2 * t)
        elif self.easing == "bounce":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - (-2 * t + 2) ** 2 / 2
        return t


class PulsingAnimation(Animation):
    def __init__(self, min_val=1.0, max_val=1.3, duration=1.0):
        super().__init__(duration, "linear")
        self.min_val = min_val
        self.max_val = max_val
        self.running = True

    def progress(self):
        t = (self.elapsed % self.duration) / self.duration
        return self.min_val + (self.max_val - self.min_val) * (0.5 + 0.5 * math.sin(2 * math.pi * t))


# ───────────────────────── SPIELER ───────────────────────────
class Player:
    def __init__(self, name, color, is_ai=False, ai_level=1):
        self.name = name
        self.color = color
        self.is_ai = is_ai
        self.ai_level = ai_level
        self.cards = []
        self.territories_conquered_this_turn = 0
        self.attacks_total = 0
        self.attacks_won = 0
        self.territories_captured = 0
        self.troops_lost = 0
        self.troops_killed = 0

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        p = cls(d["name"], d["color"], d["is_ai"], d["ai_level"])
        for k, v in d.items():
            setattr(p, k, v)
        return p


# ───────────────────────── SPIELLOGIK ──────────────────────────
class GameState:
    def __init__(self):
        self.players = []
        self.board = {}
        self.current_player_idx = 0
        self.turn = 1
        self.card_deck = []
        self.exchange_count = 0
        self.phase = "reinforcement"
        self.pending_troops = 0
        self.game_over = False
        self.winner = None
        self.help_mode = "easy"
        self.difficulty = 2

    def setup(self):
        self.board = {t: {"owner": None, "troops": 0} for t in TERRITORIES}
        terr = list(TERRITORIES.keys())
        random.shuffle(terr)
        for i, t in enumerate(terr):
            p = self.players[i % len(self.players)]
            self.board[t]["owner"] = p.name
            self.board[t]["troops"] = 1
        
        terr2 = list(TERRITORIES.keys())
        random.shuffle(terr2)
        self.card_deck = [CARD_TYPES[i % 3] for i in range(len(terr2))]
        self.card_deck += ["Wildcard", "Wildcard"]
        random.shuffle(self.card_deck)

    def initial_troops(self):
        return {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}.get(len(self.players), 20)

    def current_player(self):
        return self.players[self.current_player_idx]

    def player_by_name(self, name):
        for p in self.players:
            if p.name == name:
                return p
        return None

    def is_alive(self, player):
        return any(d["owner"] == player.name for d in self.board.values())

    def owned_territories(self, player):
        return [t for t, d in self.board.items() if d["owner"] == player.name]

    def calc_reinforcements(self, player):
        owned = self.owned_territories(player)
        troops = max(3, len(owned) // 3)
        for cont, data in CONTINENTS.items():
            if all(self.board[t]["owner"] == player.name for t in data["territories"]):
                troops += data["bonus"]
        return troops

    def find_card_sets(self, cards):
        c = Counter(cards)
        results = []
        for ct in CARD_TYPES:
            if c[ct] >= 3:
                results.append((ct, ct, ct))
        types_have = [t for t in CARD_TYPES if c[t] >= 1]
        if len(types_have) >= 3:
            results.append(("Infanterie", "Kavallerie", "Artillerie"))
        return results

    def card_exchange_value(self):
        idx = min(self.exchange_count, len(CARD_EXCHANGE_BONUS) - 1)
        return CARD_EXCHANGE_BONUS[idx]

    def resolve_battle(self, from_t, to_t):
        atk = self.board[from_t]["troops"]
        dfc = self.board[to_t]["troops"]
        atk_dice_n = min(3, atk - 1)
        def_dice_n = min(2, dfc)
        
        atk_rolls = sorted([random.randint(1, 6) for _ in range(atk_dice_n)], reverse=True)
        def_rolls = sorted([random.randint(1, 6) for _ in range(def_dice_n)], reverse=True)
        
        atk_wins = sum(1 for a, d in zip(atk_rolls, def_rolls) if a > d)
        def_wins = len(list(zip(atk_rolls, def_rolls))) - atk_wins
        
        self.board[from_t]["troops"] -= def_wins
        self.board[to_t]["troops"] -= atk_wins
        
        atk_player = self.player_by_name(self.board[from_t]["owner"])
        def_player = self.player_by_name(self.board[to_t]["owner"])
        
        if atk_player:
            atk_player.troops_lost += def_wins
            atk_player.troops_killed += atk_wins
            atk_player.attacks_total += 1
        if def_player:
            def_player.troops_lost += atk_wins
        
        conquered = False
        if self.board[to_t]["troops"] <= 0:
            move = min(atk_dice_n, self.board[from_t]["troops"] - 1)
            move = max(1, move)
            old_owner = self.board[to_t]["owner"]
            self.board[to_t]["owner"] = self.board[from_t]["owner"]
            self.board[to_t]["troops"] = move
            self.board[from_t]["troops"] -= move
            
            if atk_player:
                atk_player.territories_conquered_this_turn += 1
                atk_player.attacks_won += 1
                atk_player.territories_captured += 1
            conquered = True
            
            elim_p = self.player_by_name(old_owner)
            if elim_p and not self.is_alive(elim_p) and atk_player:
                atk_player.cards += elim_p.cards
                elim_p.cards = []
        
        return atk_rolls, def_rolls, atk_wins, def_wins, conquered

    def reachable(self, player, start):
        visited, queue = set(), [start]
        while queue:
            cur = queue.pop()
            if cur in visited:
                continue
            visited.add(cur)
            for n in TERRITORIES[cur]["neighbors"]:
                if self.board[n]["owner"] == player.name and n not in visited:
                    queue.append(n)
        return visited

    def check_winner(self):
        alive = [p for p in self.players if self.is_alive(p)]
        if len(alive) == 1:
            self.game_over = True
            self.winner = alive[0]

    def ai_place_troops(self, player, n):
        own = self.owned_territories(player)
        for _ in range(n):
            border = sorted(
                [t for t in own if any(self.board[nb]["owner"] != player.name for nb in TERRITORIES[t]["neighbors"])],
                key=lambda t: self.board[t]["troops"]
            )
            target = border[0] if border else random.choice(own)
            self.board[target]["troops"] += 1

    def ai_attack(self, player):
        own = [t for t, d in self.board.items() if d["owner"] == player.name and d["troops"] >= 2]
        random.shuffle(own)
        ratio = {1: 2.5, 2: 1.8, 3: 1.3}.get(player.ai_level, 1.8)
        
        for from_t in own:
            targets = [n for n in TERRITORIES[from_t]["neighbors"] if self.board[n]["owner"] != player.name]
            for to_t in targets:
                if self.board[from_t]["troops"] > self.board[to_t]["troops"] * ratio:
                    while self.board[from_t]["troops"] >= 2 and self.board[to_t]["owner"] != player.name:
                        self.resolve_battle(from_t, to_t)
                    return True
        return False

    def ai_fortify(self, player):
        own = self.owned_territories(player)
        interior = [t for t in own if all(self.board[n]["owner"] == player.name for n in TERRITORIES[t]["neighbors"]) and self.board[t]["troops"] > 1]
        border = sorted([t for t in own if any(self.board[n]["owner"] != player.name for n in TERRITORIES[t]["neighbors"])], 
                       key=lambda t: self.board[t]["troops"])
        if interior and border:
            from_t, to_t = interior[0], border[0]
            if to_t in self.reachable(player, from_t):
                n = self.board[from_t]["troops"] - 1
                self.board[from_t]["troops"] = 1
                self.board[to_t]["troops"] += n

    def to_dict(self):
        return {
            "version": 4,
            "saved_at": datetime.now().isoformat(),
            "players": [p.to_dict() for p in self.players],
            "board": self.board,
            "current_player_idx": self.current_player_idx,
            "turn": self.turn,
            "card_deck": self.card_deck,
            "exchange_count": self.exchange_count,
            "phase": self.phase,
            "pending_troops": self.pending_troops,
            "help_mode": self.help_mode,
            "difficulty": self.difficulty,
        }

    def from_dict(self, d):
        self.players = [Player.from_dict(p) for p in d["players"]]
        self.board = d["board"]
        self.current_player_idx = d["current_player_idx"]
        self.turn = d["turn"]
        self.card_deck = d["card_deck"]
        self.exchange_count = d["exchange_count"]
        self.phase = d.get("phase", "reinforcement")
        self.pending_troops = d.get("pending_troops", 0)
        self.help_mode = d.get("help_mode", "easy")
        self.difficulty = d.get("difficulty", 2)


# ───────────────────────── UI KOMPONENTEN ──────────────────────
class Button:
    def __init__(self, x, y, width, height, text, font_size=16, 
                 bg_color="#1a1a3e", hover_color="#2a2a5e", text_color="#f0c040",
                 border_color="#f0c040", border_width=2, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.callback = callback
        self.hovered = False
        self.clicked = False
        self.animation = Animation(0.15, "ease_out")
        self.scale = 1.0

    def draw(self, surface):
        # Animations-Update
        if self.clicked:
            self.scale = 1.0 - self.animation.progress() * 0.05
        else:
            self.scale = 1.0 + (self.hovered - 0.5) * 0.05

        # Zeichne Button mit Schatten
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(surface, "#000000", self.rect.move(2, 2), border_radius=8)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, 
                           width=self.border_width, border_radius=8)
        
        # Text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                self.animation.elapsed = 0
                self.animation.running = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.clicked = False
                if self.callback:
                    self.callback()
                return True
            self.clicked = False
        return False


class Card:
    def __init__(self, card_type, x=0, y=0, width=80, height=110):
        self.type = card_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False
        self.hovered = False
        self.animation = Animation(0.3, "bounce")
        self.y_offset = 0

        # Farben basierend auf Kartentyp
        self.colors = {
            "Infanterie": (46, 204, 113),
            "Kavallerie": (52, 152, 219),
            "Artillerie": (231, 76, 60),
            "Wildcard": (240, 192, 64)
        }
        self.icons = {
            "Infanterie": "⚔",
            "Kavallerie": "🐎",
            "Artillerie": "💣",
            "Wildcard": "⭐"
        }

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y + self.y_offset, self.width, self.height)
        
        # Hover/Selected Animation
        if self.hovered:
            self.y_offset = -5
        elif self.selected:
            self.y_offset = -10
        else:
            self.y_offset = 0

        rect.y += self.y_offset
        
        # Schatten
        shadow_rect = rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=8)
        
        # Karte
        color = self.colors.get(self.type, (200, 200, 200))
        pygame.draw.rect(surface, "#1a1a2e", rect, border_radius=8)
        pygame.draw.rect(surface, color, rect, width=2, border_radius=8)
        
        # Icon
        font = pygame.font.Font(None, 48)
        icon_text = self.icons.get(self.type, "?")
        icon_surf = font.render(icon_text, True, color)
        icon_rect = icon_surf.get_rect(center=(rect.centerx, rect.centery - 10))
        surface.blit(icon_surf, icon_rect)
        
        # Text
        font_small = pygame.font.Font(None, 20)
        text_surf = font_small.render(self.type, True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(rect.centerx, rect.bottom - 20))
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        rect = pygame.Rect(self.x, self.y + self.y_offset, self.width, self.height)
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                self.selected = not self.selected
                return True
        return False


class Tooltip:
    def __init__(self):
        self.visible = False
        self.text = ""
        self.x = 0
        self.y = 0
        self.font = pygame.font.Font(None, 24)
        self.padding = 10
        self.max_width = 300

    def show(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self, surface):
        if not self.visible:
            return
        
        lines = self.text.split('\n')
        line_height = 20
        height = len(lines) * line_height + self.padding * 2
        width = min(self.max_width, max(self.font.size(line)[0] for line in lines)) + self.padding * 2
        
        rect = pygame.Rect(self.x, self.y, width, height)
        
        # Passe Position an, wenn außerhalb des Bildschirms
        if rect.right > WIDTH:
            rect.x = WIDTH - rect.width - 5
        if rect.bottom > HEIGHT:
            rect.y = HEIGHT - rect.height - 5
        
        # Hintergrund mit Schatten
        pygame.draw.rect(surface, (0, 0, 0), rect.move(2, 2), border_radius=8)
        pygame.draw.rect(surface, "#1a1a3e", rect, border_radius=8)
        pygame.draw.rect(surface, "#f0c040", rect, width=1, border_radius=8)
        
        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, "#c0d0e0")
            surface.blit(text_surf, (rect.x + self.padding, rect.y + self.padding + i * line_height))


# ───────────────────────── HAUPTKLASSE ──────────────────────────
class RisikoGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("RISIKO – Welteroberungsstrategie (Pygame Edition)")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Systeme
        self.sound_manager = SoundManager()
        self.particles = ParticleSystem()
        self.tooltip = Tooltip()
        
        # Spielzustand
        self.gs = None
        self.state = "menu"  # menu, setup, playing, paused, game_over
        self.selected_from = None
        self.initial_mode = False
        self.initial_remaining = {}
        self.hovered_territory = None
        self.camera_offset = (0, 0)
        self.zoom = 1.0
        self.target_zoom = 1.0
        
        # Hilfe-System
        self.help_mode = "easy"
        self.tutorial_step = 0
        self.show_tutorial = False
        
        # UI-Elemente
        self.buttons = []
        self.cards = []
        self.logs = []
        self.max_logs = 50
        
        # Animationen
        self.bg_animation = Animation(5.0, "linear")
        self.bg_animation.running = True
        
        # Font-Cache
        self.fonts = {}
        self._load_fonts()
        
        # Background
        self.bg_stars = self._generate_stars()
        
        self._setup_main_menu()

    def _load_fonts(self):
        try:
            self.fonts["title"] = pygame.font.Font(None, 72)
            self.fonts["subtitle"] = pygame.font.Font(None, 36)
            self.fonts["normal"] = pygame.font.Font(None, 28)
            self.fonts["small"] = pygame.font.Font(None, 22)
            self.fonts["tiny"] = pygame.font.Font(None, 18)
            self.fonts["bold"] = pygame.font.Font(None, 32)
        except Exception as e:
            print(f"Font-Laden fehlgeschlagen: {e}")
            # Fallback
            for key in ["title", "subtitle", "normal", "small", "tiny", "bold"]:
                self.fonts[key] = pygame.font.Font(None, 24)

    def _generate_stars(self):
        stars = []
        for _ in range(100):
            stars.append({
                "x": random.uniform(0, WIDTH),
                "y": random.uniform(0, HEIGHT),
                "size": random.uniform(0.5, 2),
                "brightness": random.uniform(0.3, 1),
                "twinkle_speed": random.uniform(0.5, 2)
            })
        return stars

    def _setup_main_menu(self):
        self.buttons = []
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        self.buttons.append(Button(cx - 120, cy - 80, 240, 60, "🎮 Neues Spiel", 24, callback=self._show_setup))
        self.buttons.append(Button(cx - 120, cy, 240, 60, "💾 Spiel laden", 24, callback=self._load_game))
        self.buttons.append(Button(cx - 120, cy + 80, 240, 60, "📜 Regeln", 24, callback=self._show_rules))
        self.buttons.append(Button(cx - 120, cy + 160, 240, 60, "🔊 Sound: AN", 24, callback=self._toggle_sound))
        self.buttons.append(Button(cx - 120, cy + 240, 240, 60, "❌ Beenden", 24, callback=self._quit))
        
        self.sound_button = self.buttons[3]

    def _show_setup(self):
        self.sound_manager.play("click")
        self.state = "setup"
        self._create_setup_ui()

    def _create_setup_ui(self):
        self.buttons = []
        cx = WIDTH // 2
        y = 100
        
        # Titel
        # (Wird in draw gerendert)
        
        # Optionen
        y = 200
        self.setup_options = {
            "human": 1,
            "ai": 1,
            "difficulty": 2,
            "help_mode": "easy"
        }
        
        # Human Spieler
        self.buttons.append(Button(cx - 150, y, 120, 50, "-  Menschen", 20, callback=lambda: self._change_setup("human", -1)))
        self.human_count_label_pos = (cx, y)
        self.buttons.append(Button(cx + 30, y, 120, 50, "+  Menschen", 20, callback=lambda: self._change_setup("human", 1)))
        y += 60
        
        # KI Gegner
        self.buttons.append(Button(cx - 150, y, 120, 50, "-  KI-Gegner", 20, callback=lambda: self._change_setup("ai", -1)))
        self.ai_count_label_pos = (cx, y)
        self.buttons.append(Button(cx + 30, y, 120, 50, "+  KI-Gegner", 20, callback=lambda: self._change_setup("ai", 1)))
        y += 60
        
        # Schwierigkeit
        diff_labels = {1: "Leicht", 2: "Mittel", 3: "Schwer"}
        self.buttons.append(Button(cx - 150, y, 120, 50, "-  Schwierigkeit", 18, callback=lambda: self._change_setup("difficulty", -1)))
        self.diff_label_pos = (cx, y)
        self.buttons.append(Button(cx + 30, y, 120, 50, "+  Schwierigkeit", 18, callback=lambda: self._change_setup("difficulty", 1)))
        y += 60
        
        # Hilfe-Modus
        help_labels = {"easy": "Leicht (Tipps)", "medium": "Mittel", "hard": "Schwer (keine Hilfe)"}
        self.buttons.append(Button(cx - 150, y, 260, 50, "Hilfe: " + help_labels[self.setup_options["help_mode"]], 18,
                                  callback=self._cycle_help_mode))
        y += 60
        
        # Start
        y += 40
        self.buttons.append(Button(cx - 120, y, 240, 60, "🚀 Spiel starten!", 24, callback=self._start_game))
        self.buttons.append(Button(cx - 120, y + 70, 240, 50, "← Zurück", 20, callback=self._back_to_menu))

    def _change_setup(self, key, delta):
        self.sound_manager.play("click")
        if key == "human":
            self.setup_options["human"] = max(1, min(6, self.setup_options["human"] + delta))
        elif key == "ai":
            self.setup_options["ai"] = max(0, min(5, self.setup_options["ai"] + delta))
        elif key == "difficulty":
            self.setup_options["difficulty"] = max(1, min(3, self.setup_options["difficulty"] + delta))
        
        # Validierung
        if self.setup_options["human"] + self.setup_options["ai"] < 2:
            self.setup_options["ai"] = max(0, 2 - self.setup_options["human"])
        if self.setup_options["human"] + self.setup_options["ai"] > 6:
            self.setup_options["ai"] = 6 - self.setup_options["human"]

    def _cycle_help_mode(self):
        self.sound_manager.play("click")
        modes = ["easy", "medium", "hard"]
        current_idx = modes.index(self.setup_options["help_mode"])
        self.setup_options["help_mode"] = modes[(current_idx + 1) % len(modes)]
        help_labels = {"easy": "Leicht (Tipps)", "medium": "Mittel", "hard": "Schwer (keine Hilfe)"}
        self.buttons[-3].text = "Hilfe: " + help_labels[self.setup_options["help_mode"]]

    def _start_game(self):
        self.sound_manager.play("click")
        self.gs = GameState()
        self.gs.help_mode = self.setup_options["help_mode"]
        self.gs.difficulty = self.setup_options["difficulty"]
        self.help_mode = self.setup_options["help_mode"]
        
        color_idx = 0
        for i in range(self.setup_options["human"]):
            self.gs.players.append(Player(f"Spieler {i+1}", COLORS["player_colors"][color_idx]))
            color_idx += 1
        for i in range(self.setup_options["ai"]):
            ai_names = ["Napoleon", "Caesar", "Alexandra", "Kublai", "Bismarck", "Hannibal"]
            self.gs.players.append(Player(ai_names[i % len(ai_names)], COLORS["player_colors"][color_idx], 
                                         is_ai=True, ai_level=self.setup_options["difficulty"]))
            color_idx += 1
        
        random.shuffle(self.gs.players)
        self.gs.setup()
        
        # Initial placement
        initial = self.gs.initial_troops()
        n_terr = len(TERRITORIES) // len(self.gs.players)
        self.initial_remaining = {p.name: initial - n_terr for p in self.gs.players}
        for i in range(len(TERRITORIES) % len(self.gs.players)):
            self.initial_remaining[self.gs.players[i].name] -= 1
        self.initial_mode = True
        
        self.state = "playing"
        self.selected_from = None
        self.logs = []
        self._log("🎮 Neues Spiel gestartet!")
        
        if self.help_mode == "easy":
            self.show_tutorial = True
            self.tutorial_step = 0

    def _back_to_menu(self):
        self.sound_manager.play("click")
        self.state = "menu"
        self._setup_main_menu()

    def _toggle_sound(self):
        enabled = self.sound_manager.toggle()
        self.sound_button.text = "🔊 Sound: AN" if enabled else "🔇 Sound: AUS"
        self.sound_manager.play("click")

    def _quit(self):
        self.sound_manager.play("click")
        self.running = False

    # ──────────── GAME LOGIC ────────────
    def _start_turn(self):
        player = self.gs.current_player()
        while not self.gs.is_alive(player):
            self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
            if self.gs.current_player_idx == 0:
                self.gs.turn += 1
            player = self.gs.current_player()
        
        self.gs.phase = "reinforcement"
        player.territories_conquered_this_turn = 0
        self.selected_from = None
        self._log(f"--- Runde {self.gs.turn}: {player.name} ist am Zug ---")
        
        if player.is_ai:
            self._run_ai_turn()
        else:
            n = self.gs.calc_reinforcements(player)
            self.gs.pending_troops = n
            self._log(f"➕ {player.name} erhält {n} Truppen")

    def _run_ai_turn(self):
        player = self.gs.current_player()
        self._log(f"🤖 {player.name} denkt nach...")
        pygame.time.wait(500)
        
        # Kartentausch
        if self.gs.find_card_sets(player.cards) and len(player.cards) >= 3:
            sets = self.gs.find_card_sets(player.cards)
            for card in sets[0]:
                if card in player.cards:
                    player.cards.remove(card)
            bonus = self.gs.card_exchange_value()
            self.gs.exchange_count += 1
            self.gs.pending_troops = bonus
            self._log(f"🃏 {player.name}: Kartentausch +{bonus}")
        
        # Verstärkung
        n = self.gs.calc_reinforcements(player) + self.gs.pending_troops
        self.gs.pending_troops = 0
        self.gs.ai_place_troops(player, n)
        self._log(f"➕ {player.name} platziert {n} Truppen")
        
        # Angriffe
        for _ in range(15 * player.ai_level):
            if not self.gs.ai_attack(player):
                break
            self.gs.check_winner()
            if self.gs.game_over:
                self._show_game_over()
                return
        
        # Verschieben
        self.gs.ai_fortify(player)
        
        # Karte ziehen
        if player.territories_conquered_this_turn > 0 and self.gs.card_deck:
            card = self.gs.card_deck.pop()
            player.cards.append(card)
        
        self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
        if self.gs.current_player_idx == 0:
            self.gs.turn += 1
        self._start_turn()

    def _next_phase(self):
        if not self.gs or self.initial_mode:
            return
        
        player = self.gs.current_player()
        if player.is_ai:
            return
        
        if self.gs.phase == "reinforcement":
            if self.gs.pending_troops > 0:
                self._log(f"⚠️ Noch {self.gs.pending_troops} Truppen zu platzieren!")
                return
            self.gs.phase = "attack"
            self.selected_from = None
            self._log("🔴 Angriffsphase - Wähle Angriffsgebiet")
            
        elif self.gs.phase == "attack":
            self.gs.phase = "fortify"
            self.selected_from = None
            self._log("🔵 Verschiebephase")
            
        elif self.gs.phase == "fortify":
            if player.territories_conquered_this_turn > 0 and self.gs.card_deck:
                card = self.gs.card_deck.pop()
                player.cards.append(card)
                self._log(f"🃏 {player.name} zieht Karte: {card}")
            
            self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
            if self.gs.current_player_idx == 0:
                self.gs.turn += 1
            self.gs.check_winner()
            if self.gs.game_over:
                self._show_game_over()
                return
            self._start_turn()

    def _show_game_over(self):
        self.state = "game_over"
        w = self.gs.winner
        self._log(f"🏆 {w.name} HAT GEWONNEN!")
        self.sound_manager.play("conquest")

    # ──────────── RENDERING ────────────
    def draw_background(self):
        # Dunkler Gradient
        for y in range(HEIGHT):
            progress = y / HEIGHT
            color = (int(10 + 15 * progress), int(10 + 20 * progress), int(26 + 20 * progress))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))
        
        # Sterne
        time_val = pygame.time.get_ticks() / 1000
        for star in self.bg_stars:
            twinkle = 0.5 + 0.5 * math.sin(time_val * star["twinkle_speed"] + star["x"])
            alpha = int(star["brightness"] * twinkle * 255)
            color = (200, 200, 255, alpha)
            pygame.draw.circle(self.screen, color[:3], (int(star["x"]), int(star["y"])), int(star["size"]))

    def draw_map(self):
        if not self.gs:
            return
        
        # Skalierung und Offset
        map_width = 1000
        map_height = 520
        scale_x = (WIDTH - 300) / map_width * self.zoom
        scale_y = (HEIGHT) / map_height * self.zoom
        scale = min(scale_x, scale_y)
        
        offset_x = 50
        offset_y = 50
        
        for t, data in TERRITORIES.items():
            x = data["pos"][0] * scale + offset_x
            y = data["pos"][1] * scale + offset_y
            owner_name = self.gs.board[t]["owner"]
            troops = self.gs.board[t]["troops"]
            player = self.gs.player_by_name(owner_name) if owner_name else None
            
            # Farbe basierend auf Besitzer
            base_color = (64, 64, 64)
            if player:
                hex_color = player.color.lstrip("#")
                base_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Größe basierend auf Truppen
            radius = 15 + min(troops, 20) * 0.5
            radius *= scale / 1.0
            
            # Zeige Verbindungen
            for nb in data["neighbors"]:
                if nb in TERRITORIES:
                    x2 = TERRITORIES[nb]["pos"][0] * scale + offset_x
                    y2 = TERRITORIES[nb]["pos"][1] * scale + offset_y
                    
                    # Überspringe lange Verbindungen
                    if abs(x - x2) > WIDTH * 0.4:
                        continue
                    
                    pygame.draw.line(self.screen, (40, 60, 80), (x, y), (x2, y2), max(1, int(scale)))
            
            # Zeichne Gebiet
            pygame.draw.circle(self.screen, base_color, (int(x), int(y)), int(radius))
            pygame.draw.circle(self.screen, (200, 200, 200), (int(x), int(y)), int(radius), 2)
            
            # Hover-Effekt
            if self.hovered_territory == t:
                pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), int(radius + 3), 2)
            
            # Truppen-Anzahl
            font = pygame.font.Font(None, max(16, int(20 * scale)))
            text_surf = font.render(str(troops), True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(int(x), int(y)))
            self.screen.blit(text_surf, text_rect)
            
            # Gebietsname
            name_font = pygame.font.Font(None, max(12, int(14 * scale)))
            name_short = t if len(t) <= 10 else t[:9] + "."
            name_surf = name_font.render(name_short, True, (160, 180, 200))
            name_rect = name_surf.get_rect(center=(int(x), int(y) + int(radius) + 8))
            self.screen.blit(name_surf, name_rect)

    def draw_ui(self):
        if self.state != "playing" or not self.gs:
            return
        
        # Rechte Seite - Panel
        panel_x = WIDTH - 280
        pygame.draw.rect(self.screen, "#0d1a2e", (panel_x, 0, 280, HEIGHT))
        pygame.draw.line(self.screen, "#f0c040", (panel_x, 0), (panel_x, HEIGHT), 2)
        
        # Phasen-Anzeige
        phase_labels = {
            "reinforcement": "🟢 VERSTÄRKUNG",
            "attack": "🔴 ANGRIFF",
            "fortify": "🔵 VERSCHIEBEN",
            "initial": "⚪ START"
        }
        phase_text = phase_labels.get(self.gs.phase, "")
        
        font = pygame.font.Font(None, 24)
        text_surf = font.render(f"Runde {self.gs.turn} | {phase_text}", True, "#f0c040")
        self.screen.blit(text_surf, (panel_x + 10, 10))
        
        # Spieler-Liste
        y = 50
        font_small = pygame.font.Font(None, 20)
        for p in self.gs.players:
            if not self.gs.is_alive(p):
                continue
            
            is_current = (p == self.gs.current_player())
            color = (255, 255, 255) if is_current else (160, 160, 180)
            
            # Hintergrund für aktuellen Spieler
            if is_current:
                pygame.draw.rect(self.screen, "#1a2a3e", (panel_x + 5, y - 2, 270, 22))
            
            # Punkt
            hex_color = p.color.lstrip("#")
            dot_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            pygame.draw.circle(self.screen, dot_color, (panel_x + 15, y + 8), 6)
            
            # Name
            name_text = p.name
            if p.is_ai:
                name_text += " (KI)"
            name_surf = font_small.render(name_text, True, color)
            self.screen.blit(name_surf, (panel_x + 30, y))
            
            # Stats
            terr_count = len(self.gs.owned_territories(p))
            troop_count = sum(d["troops"] for d in self.gs.board.values() if d["owner"] == p.name)
            stats_surf = font_small.render(f"{terr_count}🗺 {troop_count}⚔", True, (128, 160, 192))
            self.screen.blit(stats_surf, (panel_x + 180, y))
            
            y += 24
        
        # Aktionen
        y += 20
        self.buttons = []
        
        if self.gs.phase == "attack":
            self.buttons.append(Button(panel_x + 10, y, 260, 40, "Nächste Phase ▶", 18, callback=self._next_phase))
        elif self.gs.phase == "fortify":
            self.buttons.append(Button(panel_x + 10, y, 260, 40, "Zug beenden ✅", 18, callback=self._next_phase))
        
        # Hilfe-Button
        self.buttons.append(Button(panel_x + 10, y + 50, 260, 35, "❓ Hilfe", 16, callback=self._show_help))
        
        # Sound-Button
        self.buttons.append(Button(panel_x + 10, y + 95, 260, 35, 
                                  "🔊 Sound: AN" if self.sound_manager.enabled else "🔇 Sound: AUS", 
                                  16, callback=self._toggle_sound))
        
        # Karten-Button
        player = self.gs.current_player()
        if not player.is_ai:
            card_text = f"🃏 Karten ({len(player.cards)})"
            self.buttons.append(Button(panel_x + 10, y + 140, 260, 35, card_text, 16, callback=self._show_cards))
        
        # Draw Buttons
        for btn in self.buttons:
            btn.draw(self.screen)
        
        # Log
        log_y = HEIGHT - 200
        pygame.draw.rect(self.screen, "#060612", (panel_x, log_y, 280, 200))
        pygame.draw.line(self.screen, "#304050", (panel_x, log_y), (panel_x + 280, log_y), 1)
        
        font_tiny = pygame.font.Font(None, 16)
        for i, log in enumerate(self.logs[-8:]):
            log_surf = font_tiny.render(log[:30], True, (192, 208, 224))
            self.screen.blit(log_surf, (panel_x + 5, log_y + 10 + i * 20))
        
        # Tutorial-Overlay
        if self.show_tutorial and self.help_mode == "easy":
            self._draw_tutorial()

    def _draw_tutorial(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Tutorial-Box
        box_w, box_h = 500, 300
        box_x = (WIDTH - box_w) // 2
        box_y = (HEIGHT - box_h) // 2
        
        pygame.draw.rect(self.screen, "#0d1a2e", (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(self.screen, "#f0c040", (box_x, box_y, box_w, box_h), 2, border_radius=12)
        
        tutorial_texts = [
            ("🎮 Willkommen zu RISIKO!", "Erobere die Welt! Klicke auf Gebiete zum Platzieren."),
            ("📍 Startaufstellung", "Platziere Truppen auf deinen Gebieten."),
            ("➕ Verstärkung", "Erhalte Truppen und platziere sie strategisch."),
            ("⚔ Angriff", "Wähle eigenes Gebiet → feindliches Nachbargebiet."),
            ("🔀 Verschieben", "Bewege Truppen zwischen eigenen Gebieten."),
            ("✅ Bereit!", "Viel Erfolg bei der Welteroberung!"),
        ]
        
        if self.tutorial_step < len(tutorial_texts):
            title, text = tutorial_texts[self.tutorial_step]
            
            font_title = pygame.font.Font(None, 32)
            font_text = pygame.font.Font(None, 24)
            
            title_surf = font_title.render(title, True, "#f0c040")
            text_surf = font_text.render(text, True, "#c0d0e0")
            
            self.screen.blit(title_surf, (box_x + 20, box_y + 20))
            self.screen.blit(text_surf, (box_x + 20, box_y + 60))
            
            # Weiter-Button
            btn = Button(box_x + 150, box_y + 220, 200, 50, "Weiter ▶", 20, 
                        callback=self._next_tutorial_step)
            btn.draw(self.screen)
            self.buttons.append(btn)

    def _next_tutorial_step(self):
        self.sound_manager.play("click")
        self.tutorial_step += 1
        if self.tutorial_step >= 6:
            self.show_tutorial = False

    def _show_help(self):
        self.sound_manager.play("click")
        if self.gs:
            help_texts = {
                "reinforcement": "Klicke auf eigenes Gebiet zum Platzieren.",
                "attack": "Wähle eigenes Gebiet (≥2 Tr.) → feindliches Nachbargebiet.",
                "fortify": "Wähle Start → Ziel zum Verschieben.",
            }
            self._log("❓ " + help_texts.get(self.gs.phase, "Wähle eine Phase."))

    def _show_cards(self):
        self.sound_manager.play("click")
        if not self.gs:
            return
        
        player = self.gs.current_player()
        if player.is_ai:
            return
        
        self._log(f"🃏 {player.name} hat {len(player.cards)} Karten: {', '.join(player.cards)}")
        
        # Prüfe auf Tauschmöglichkeit
        sets = self.gs.find_card_sets(player.cards)
        if sets:
            self._log(f"✅ Tausch möglich! +{self.gs.card_exchange_value()} Truppen")
            # Automatischer Tausch für Einfachheit
            for card in sets[0]:
                if card in player.cards:
                    player.cards.remove(card)
            bonus = self.gs.card_exchange_value()
            self.gs.exchange_count += 1
            self.gs.pending_troops += bonus
            self._log(f"🃏 Kartentausch durchgeführt! +{bonus} Truppen")

    def _show_rules(self):
        # Vereinfachte Regel-Anzeige
        self.sound_manager.play("click")
        self._log("📜 Regeln: 1. Verstärkung  2. Angriff  3. Verschieben")
        # In einer vollständigen Version würde hier ein Overlay erscheinen

    # ──────────── EVENT HANDLING ────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Buttons
            for btn in self.buttons:
                btn.handle_event(event)
            
            if event.type == pygame.MOUSEMOTION:
                self.hovered_territory = self._get_territory_at(event.pos)
                if self.hovered_territory and self.gs:
                    data = self.gs.board[self.hovered_territory]
                    owner = data["owner"] or "Niemand"
                    troops = data["troops"]
                    cont = TERRITORIES[self.hovered_territory]["continent"]
                    self.tooltip.show(f"📍 {self.hovered_territory}\n👤 {owner}\n⚔ {troops} Truppen\n🌍 {cont}", 
                                     event.pos[0], event.pos[1])
                else:
                    self.tooltip.hide()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "playing" and self.gs and self.hovered_territory:
                    self._handle_territory_click(self.hovered_territory)
            
            # Tastatur
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                        self._setup_main_menu()
                    else:
                        self.running = False
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.target_zoom = min(2.0, self.target_zoom + 0.1)
                elif event.key == pygame.K_MINUS:
                    self.target_zoom = max(0.5, self.target_zoom - 0.1)
                elif event.key == pygame.K_h:
                    self._show_help()

    def _get_territory_at(self, pos):
        mx, my = pos
        map_width = 1000
        scale_x = (WIDTH - 300) / map_width * self.zoom
        scale_y = (HEIGHT) / map_height * self.zoom if 'map_height' in dir() else self.zoom
        scale = min(scale_x, scale_y)
        offset_x = 50
        offset_y = 50
        
        for t, data in TERRITORIES.items():
            x = data["pos"][0] * scale + offset_x
            y = data["pos"][1] * scale + offset_y
            dist = math.sqrt((mx - x) ** 2 + (my - y) ** 2)
            if dist < 25 * scale:
                return t
        return None

    def _handle_territory_click(self, terr):
        if not self.gs or self.gs.game_over:
            return
        
        player = self.gs.current_player()
        if player.is_ai:
            return
        
        self.sound_manager.play("click")
        
        if self.initial_mode:
            if self.gs.board[terr]["owner"] == player.name:
                self.gs.board[terr]["troops"] += 1
                self.initial_remaining[player.name] -= 1
                self._log(f"📍 {player.name}: +1 → {terr}")
                
                # Partikeleffekt
                x, y = TERRITORIES[terr]["pos"]
                scale = min((WIDTH - 300) / 1000, HEIGHT / 520) * self.zoom
                px = x * scale + 50
                py = y * scale + 50
                self.particles.emit(px, py, (255, 255, 255), 8, 1.5, 2)
                
                self._next_initial_player()
        
        elif self.gs.phase == "reinforcement":
            if self.gs.board[terr]["owner"] == player.name and self.gs.pending_troops > 0:
                self.gs.board[terr]["troops"] += 1
                self.gs.pending_troops -= 1
                self._log(f"➕ +1 → {terr} ({self.gs.pending_troops} übrig)")
                self.sound_manager.play("place")
                
                x, y = TERRITORIES[terr]["pos"]
                scale = min((WIDTH - 300) / 1000, HEIGHT / 520) * self.zoom
                px = x * scale + 50
                py = y * scale + 50
                self.particles.emit(px, py, (46, 204, 113), 12, 2, 3)
        
        elif self.gs.phase == "attack":
            if self.selected_from is None:
                if self.gs.board[terr]["owner"] == player.name and self.gs.board[terr]["troops"] >= 2:
                    self.selected_from = terr
                    self._log(f"🎯 Von: {terr}")
            else:
                if terr in TERRITORIES[self.selected_from]["neighbors"] and self.gs.board[terr]["owner"] != player.name:
                    # Kampf!
                    atk_r, def_r, atk_w, def_w, conquered = self.gs.resolve_battle(self.selected_from, terr)
                    result = f"⚔ {self.selected_from} → {terr} [{atk_r}] vs [{def_r}]"
                    if conquered:
                        result += " ✅ EROBERT!"
                        self.sound_manager.play("conquest")
                        x, y = TERRITORIES[terr]["pos"]
                        scale = min((WIDTH - 300) / 1000, HEIGHT / 520) * self.zoom
                        px = x * scale + 50
                        py = y * scale + 50
                        self.particles.explosion(px, py, 25)
                    else:
                        result += f" (-{def_w}/-{atk_w})"
                        self.sound_manager.play("attack")
                    self._log(result)
                    self.selected_from = None
                else:
                    self.selected_from = None
                    self._log("❌ Ungültiges Ziel")
        
        elif self.gs.phase == "fortify":
            if self.selected_from is None:
                if self.gs.board[terr]["owner"] == player.name and self.gs.board[terr]["troops"] >= 2:
                    self.selected_from = terr
                    self._log(f"🔀 Von: {terr}")
            else:
                if self.gs.board[terr]["owner"] == player.name:
                    reachable = self.gs.reachable(player, self.selected_from)
                    if terr in reachable:
                        move = self.gs.board[self.selected_from]["troops"] - 1
                        if move > 0:
                            self.gs.board[self.selected_from]["troops"] -= move
                            self.gs.board[terr]["troops"] += move
                            self._log(f"🔀 {move} Tr. {self.selected_from} → {terr}")
                            self.selected_from = None
                    else:
                        self._log("❌ Nicht erreichbar")
                        self.selected_from = None
                else:
                    self.selected_from = None

    def _next_initial_player(self):
        if all(v <= 0 for v in self.initial_remaining.values()):
            self.initial_mode = False
            self.gs.current_player_idx = 0
            self.gs.turn = 1
            self._log("🎉 Startaufstellung abgeschlossen!")
            self._start_turn()
            return
        
        # Nächster Spieler mit Truppen finden
        while self.initial_remaining.get(self.gs.current_player().name, 0) <= 0:
            self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
            if all(v <= 0 for v in self.initial_remaining.values()):
                self.initial_mode = False
                self.gs.current_player_idx = 0
                self.gs.turn = 1
                self._log("🎉 Startaufstellung abgeschlossen!")
                self._start_turn()
                return

    def _log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def _show_setup(self):
        pass  # Already defined

    def _load_game(self):
        self.sound_manager.play("click")
        self._log("💾 Laden nicht verfügbar in Demo")

    # ──────────── MAIN LOOP ────────────
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Zoom-Animation
            self.zoom += (self.target_zoom - self.zoom) * 0.1
            
            self.handle_events()
            
            # Zeichne
            self.draw_background()
            
            if self.state == "menu":
                self._draw_menu()
            elif self.state == "setup":
                self._draw_setup()
            elif self.state == "playing":
                self.draw_map()
                self.draw_ui()
            elif self.state == "game_over":
                self.draw_map()
                self._draw_game_over()
            
            # Partikel
            self.particles.update()
            self.particles.draw(self.screen)
            
            # Tooltip
            self.tooltip.draw(self.screen)
            
            pygame.display.flip()

    def _draw_menu(self):
        # Titel
        font_title = pygame.font.Font(None, 72)
        title_surf = font_title.render("⚔ RISIKO", True, "#f0c040")
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        self.screen.blit(title_surf, title_rect)
        
        font_sub = pygame.font.Font(None, 36)
        sub_surf = font_sub.render("Welteroberungsstrategie", True, "#a0a0c0")
        sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90))
        self.screen.blit(sub_surf, sub_rect)
        
        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

    def _draw_setup(self):
        # Titel
        font_title = pygame.font.Font(None, 48)
        title_surf = font_title.render("🎮 Neues Spiel konfigurieren", True, "#f0c040")
        self.screen.blit(title_surf, (WIDTH // 2 - 200, 50))
        
        # Optionen
        font = pygame.font.Font(None, 28)
        
        # Menschen
        label = f"Menschen: {self.setup_options['human']}"
        surf = font.render(label, True, "#c0d0e0")
        self.screen.blit(surf, (WIDTH // 2 - 60, self.human_count_label_pos[1] + 10))
        
        # KI
        label = f"KI-Gegner: {self.setup_options['ai']}"
        surf = font.render(label, True, "#c0d0e0")
        self.screen.blit(surf, (WIDTH // 2 - 50, self.ai_count_label_pos[1] + 10))
        
        # Schwierigkeit
        diff_labels = {1: "Leicht", 2: "Mittel", 3: "Schwer"}
        label = f"Schwierigkeit: {diff_labels[self.setup_options['difficulty']]}"
        surf = font.render(label, True, "#c0d0e0")
        self.screen.blit(surf, (WIDTH // 2 - 80, self.diff_label_pos[1] + 10))
        
        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

    def _draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        if self.gs.winner:
            font = pygame.font.Font(None, 64)
            winner_surf = font.render(f"🏆 {self.gs.winner.name} GEWINNT!", True, self.gs.winner.color)
            rect = winner_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            self.screen.blit(winner_surf, rect)
            
            font_small = pygame.font.Font(None, 32)
            stats_surf = font_small.render(f"Nach {self.gs.turn} Runden | {self.gs.winner.territories_captured} Eroberungen", True, "#c0d0e0")
            stats_rect = stats_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            self.screen.blit(stats_surf, stats_rect)
            
            # Buttons
            btn_menu = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Hauptmenü", 20, callback=self._back_to_menu)
            btn_menu.draw(self.screen)
            self.buttons = [btn_menu]


if __name__ == "__main__":
    game = RisikoGame()
    game.run()
    pygame.quit()
    sys.exit()
