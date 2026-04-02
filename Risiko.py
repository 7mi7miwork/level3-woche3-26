#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          R I S I K O  -  Welteroberungsstrategie             ║
║          Tkinter GUI Version                                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import os
import random
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
from collections import defaultdict, Counter
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ───────────────────────── SPIELKARTE ────────────────────────────
TERRITORIES = {
    "Alaska":              {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium","Alberta","Kamtschatka"], "pos": (60,110)},
    "Nordwest-Territorium":{"continent": "Nordamerika", "neighbors": ["Alaska","Alberta","Ontario","Grönland"], "pos": (130,95)},
    "Grönland":            {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium","Ontario","Quebec","Island"], "pos": (280,70)},
    "Alberta":             {"continent": "Nordamerika", "neighbors": ["Alaska","Nordwest-Territorium","Ontario","Weststaaten"], "pos": (120,135)},
    "Ontario":             {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium","Grönland","Alberta","Weststaaten","Quebec","Oststaaten"], "pos": (185,135)},
    "Quebec":              {"continent": "Nordamerika", "neighbors": ["Ontario","Grönland","Oststaaten"], "pos": (240,130)},
    "Weststaaten":         {"continent": "Nordamerika", "neighbors": ["Alberta","Ontario","Oststaaten","Mittelamerika"], "pos": (135,175)},
    "Oststaaten":          {"continent": "Nordamerika", "neighbors": ["Weststaaten","Ontario","Quebec","Mittelamerika"], "pos": (205,175)},
    "Mittelamerika":       {"continent": "Nordamerika", "neighbors": ["Weststaaten","Oststaaten","Venezuela"], "pos": (155,220)},
    "Venezuela":           {"continent": "Südamerika", "neighbors": ["Mittelamerika","Peru","Brasilien"], "pos": (210,270)},
    "Peru":                {"continent": "Südamerika", "neighbors": ["Venezuela","Brasilien","Argentinien"], "pos": (210,320)},
    "Brasilien":           {"continent": "Südamerika", "neighbors": ["Venezuela","Peru","Argentinien","Nordafrika"], "pos": (265,305)},
    "Argentinien":         {"continent": "Südamerika", "neighbors": ["Peru","Brasilien"], "pos": (225,370)},
    "Island":              {"continent": "Europa", "neighbors": ["Grönland","Großbritannien","Skandinavien"], "pos": (370,95)},
    "Großbritannien":      {"continent": "Europa", "neighbors": ["Island","Skandinavien","Nordeuropa","Westeuropa"], "pos": (380,135)},
    "Skandinavien":        {"continent": "Europa", "neighbors": ["Island","Großbritannien","Nordeuropa","Ukraine"], "pos": (440,100)},
    "Nordeuropa":          {"continent": "Europa", "neighbors": ["Großbritannien","Skandinavien","Westeuropa","Mitteleuropa","Ukraine"], "pos": (435,140)},
    "Westeuropa":          {"continent": "Europa", "neighbors": ["Großbritannien","Nordeuropa","Mitteleuropa","Nordafrika"], "pos": (400,180)},
    "Mitteleuropa":        {"continent": "Europa", "neighbors": ["Nordeuropa","Westeuropa","Ukraine","Südeuropa"], "pos": (455,175)},
    "Ukraine":             {"continent": "Europa", "neighbors": ["Skandinavien","Nordeuropa","Mitteleuropa","Südeuropa","Ural","Afghanistan","Mittlerer Osten"], "pos": (510,145)},
    "Südeuropa":           {"continent": "Europa", "neighbors": ["Westeuropa","Mitteleuropa","Ukraine","Nordafrika","Ägypten","Mittlerer Osten"], "pos": (460,210)},
    "Nordafrika":          {"continent": "Afrika", "neighbors": ["Brasilien","Westeuropa","Südeuropa","Ägypten","Ostafrika","Zentralafrika"], "pos": (415,255)},
    "Ägypten":             {"continent": "Afrika", "neighbors": ["Nordafrika","Südeuropa","Mittlerer Osten","Ostafrika"], "pos": (490,255)},
    "Zentralafrika":       {"continent": "Afrika", "neighbors": ["Nordafrika","Ostafrika","Südafrika"], "pos": (460,310)},
    "Ostafrika":           {"continent": "Afrika", "neighbors": ["Nordafrika","Ägypten","Zentralafrika","Südafrika","Madagaskar","Mittlerer Osten"], "pos": (520,305)},
    "Südafrika":           {"continent": "Afrika", "neighbors": ["Zentralafrika","Ostafrika","Madagaskar"], "pos": (470,365)},
    "Madagaskar":          {"continent": "Afrika", "neighbors": ["Ostafrika","Südafrika"], "pos": (545,355)},
    "Ural":                {"continent": "Asien", "neighbors": ["Ukraine","Sibirien","Afghanistan","China"], "pos": (580,125)},
    "Sibirien":            {"continent": "Asien", "neighbors": ["Ural","Jakutien","Irkutsk","Mongolei","China"], "pos": (645,100)},
    "Jakutien":            {"continent": "Asien", "neighbors": ["Sibirien","Kamtschatka","Irkutsk"], "pos": (720,85)},
    "Kamtschatka":         {"continent": "Asien", "neighbors": ["Jakutien","Irkutsk","Mongolei","Japan","Alaska"], "pos": (790,100)},
    "Irkutsk":             {"continent": "Asien", "neighbors": ["Sibirien","Jakutien","Kamtschatka","Mongolei"], "pos": (700,140)},
    "Mongolei":            {"continent": "Asien", "neighbors": ["Sibirien","Kamtschatka","Irkutsk","China","Japan"], "pos": (710,175)},
    "Japan":               {"continent": "Asien", "neighbors": ["Kamtschatka","Mongolei"], "pos": (790,170)},
    "Afghanistan":         {"continent": "Asien", "neighbors": ["Ukraine","Ural","China","Indien","Mittlerer Osten"], "pos": (590,195)},
    "China":               {"continent": "Asien", "neighbors": ["Ural","Sibirien","Mongolei","Afghanistan","Indien","Siam"], "pos": (680,205)},
    "Mittlerer Osten":     {"continent": "Asien", "neighbors": ["Ukraine","Südeuropa","Ägypten","Ostafrika","Afghanistan","Indien"], "pos": (555,245)},
    "Indien":              {"continent": "Asien", "neighbors": ["Mittlerer Osten","Afghanistan","China","Siam"], "pos": (635,265)},
    "Siam":                {"continent": "Asien", "neighbors": ["China","Indien","Indonesien"], "pos": (705,270)},
    "Indonesien":          {"continent": "Australien", "neighbors": ["Siam","Neuguinea","Westaustralien"], "pos": (730,330)},
    "Neuguinea":           {"continent": "Australien", "neighbors": ["Indonesien","Westaustralien","Ostaustralien"], "pos": (790,315)},
    "Westaustralien":      {"continent": "Australien", "neighbors": ["Indonesien","Neuguinea","Ostaustralien"], "pos": (760,385)},
    "Ostaustralien":       {"continent": "Australien", "neighbors": ["Neuguinea","Westaustralien"], "pos": (820,380)},
}

CONTINENTS = {
    "Nordamerika": {"bonus": 5, "color": "#d4a843", "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Nordamerika"]},
    "Südamerika":  {"bonus": 2, "color": "#5fad56", "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Südamerika"]},
    "Europa":      {"bonus": 5, "color": "#4a90d9", "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Europa"]},
    "Afrika":      {"bonus": 3, "color": "#c0763e", "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Afrika"]},
    "Asien":       {"bonus": 7, "color": "#9b59b6", "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Asien"]},
    "Australien":  {"bonus": 2, "color": "#e74c3c", "territories": [t for t,d in TERRITORIES.items() if d["continent"]=="Australien"]},
}

PLAYER_COLORS = ["#e74c3c","#3498db","#2ecc71","#9b59b6","#f39c12","#1abc9c"]
PLAYER_NAMES_AI = ["Napoleon","Caesar","Alexandra","Kublai","Bismarck","Hannibal"]
CARD_TYPES = ["Infanterie","Kavallerie","Artillerie"]
CARD_EXCHANGE_BONUS = [4, 6, 8, 10, 12, 15]
SAVE_DIR = os.path.expanduser("~/.risiko_saves")


def ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def roll_dice(n: int) -> List[int]:
    return sorted([random.randint(1,6) for _ in range(n)], reverse=True)


# ───────────────────────────── SPIELER ───────────────────────────
class Player:
    def __init__(self, name, color, is_ai=False, ai_level=1):
        self.name = name
        self.color = color
        self.is_ai = is_ai
        self.ai_level = ai_level
        self.cards: List[str] = []
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


# ─────────────────────────── SPIELLOGIK ──────────────────────────
class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.board: Dict[str, dict] = {}
        self.current_player_idx = 0
        self.turn = 1
        self.card_deck: List[str] = []
        self.exchange_count = 0
        self.phase = "reinforcement"  # reinforcement / attack / fortify
        self.pending_troops = 0
        self.game_over = False
        self.winner: Optional[Player] = None

    def setup(self):
        self.board = {t: {"owner": None, "troops": 0} for t in TERRITORIES}
        terr = list(TERRITORIES.keys())
        random.shuffle(terr)
        for i, t in enumerate(terr):
            p = self.players[i % len(self.players)]
            self.board[t]["owner"] = p.name
            self.board[t]["troops"] = 1
        # card deck
        terr2 = list(TERRITORIES.keys())
        random.shuffle(terr2)
        self.card_deck = [CARD_TYPES[i % 3] for i in range(len(terr2))]
        self.card_deck += ["Wildcard", "Wildcard"]
        random.shuffle(self.card_deck)

    def initial_troops(self):
        return {2:40,3:35,4:30,5:25,6:20}.get(len(self.players), 20)

    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def player_by_name(self, name) -> Optional[Player]:
        for p in self.players:
            if p.name == name:
                return p
        return None

    def is_alive(self, player: Player) -> bool:
        return any(d["owner"] == player.name for d in self.board.values())

    def owned_territories(self, player: Player) -> List[str]:
        return [t for t, d in self.board.items() if d["owner"] == player.name]

    def calc_reinforcements(self, player: Player) -> int:
        owned = self.owned_territories(player)
        troops = max(3, len(owned) // 3)
        for cont, data in CONTINENTS.items():
            if all(self.board[t]["owner"] == player.name for t in data["territories"]):
                troops += data["bonus"]
        return troops

    def find_card_sets(self, cards: List[str]) -> List[Tuple]:
        c = Counter(cards)
        results = []
        for ct in CARD_TYPES:
            if c[ct] >= 3:
                results.append((ct, ct, ct))
        types_have = [t for t in CARD_TYPES if c[t] >= 1]
        if len(types_have) >= 3:
            results.append(("Infanterie","Kavallerie","Artillerie"))
        return results

    def card_exchange_value(self) -> int:
        idx = min(self.exchange_count, len(CARD_EXCHANGE_BONUS)-1)
        return CARD_EXCHANGE_BONUS[idx]

    def resolve_battle(self, from_t, to_t):
        atk = self.board[from_t]["troops"]
        dfc = self.board[to_t]["troops"]
        atk_dice_n = min(3, atk - 1)
        def_dice_n = min(2, dfc)
        atk_rolls = roll_dice(atk_dice_n)
        def_rolls = roll_dice(def_dice_n)
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
            # cards from eliminated player
            elim_p = self.player_by_name(old_owner)
            if elim_p and not self.is_alive(elim_p) and atk_player:
                atk_player.cards += elim_p.cards
                elim_p.cards = []
        return atk_rolls, def_rolls, atk_wins, def_wins, conquered

    def reachable(self, player: Player, start: str) -> set:
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

    # AI logic
    def ai_place_troops(self, player: Player, n: int):
        own = self.owned_territories(player)
        for _ in range(n):
            border = sorted(
                [t for t in own if any(self.board[nb]["owner"] != player.name for nb in TERRITORIES[t]["neighbors"])],
                key=lambda t: self.board[t]["troops"]
            )
            target = border[0] if border else random.choice(own)
            self.board[target]["troops"] += 1

    def ai_attack(self, player: Player) -> bool:
        own = [t for t, d in self.board.items() if d["owner"] == player.name and d["troops"] >= 2]
        random.shuffle(own)
        ratio = {1: 2.5, 2: 1.8, 3: 1.3}[player.ai_level]
        for from_t in own:
            targets = [n for n in TERRITORIES[from_t]["neighbors"] if self.board[n]["owner"] != player.name]
            for to_t in targets:
                if self.board[from_t]["troops"] > self.board[to_t]["troops"] * ratio:
                    while self.board[from_t]["troops"] >= 2 and self.board[to_t]["owner"] != player.name:
                        self.resolve_battle(from_t, to_t)
                    return True
        return False

    def ai_fortify(self, player: Player):
        own = self.owned_territories(player)
        interior = [t for t in own if all(self.board[n]["owner"] == player.name for n in TERRITORIES[t]["neighbors"]) and self.board[t]["troops"] > 1]
        border = sorted([t for t in own if any(self.board[n]["owner"] != player.name for n in TERRITORIES[t]["neighbors"])], key=lambda t: self.board[t]["troops"])
        if interior and border:
            from_t, to_t = interior[0], border[0]
            if to_t in self.reachable(player, from_t):
                n = self.board[from_t]["troops"] - 1
                self.board[from_t]["troops"] = 1
                self.board[to_t]["troops"] += n

    def to_dict(self):
        return {
            "version": 3,
            "saved_at": datetime.now().isoformat(),
            "players": [p.to_dict() for p in self.players],
            "board": self.board,
            "current_player_idx": self.current_player_idx,
            "turn": self.turn,
            "card_deck": self.card_deck,
            "exchange_count": self.exchange_count,
            "phase": self.phase,
            "pending_troops": self.pending_troops,
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


# ──────────────────────── SETUP DIALOG ───────────────────────────
class SetupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Neues Spiel – Einstellungen")
        self.resizable(False, False)
        self.result = None
        self._build()
        self.grab_set()
        self.wait_window()

    def _build(self):
        self.configure(bg="#1a1a2e")
        pad = {"padx": 12, "pady": 6}

        tk.Label(self, text="⚔  RISIKO", font=("Georgia", 22, "bold"), fg="#f0c040", bg="#1a1a2e").pack(pady=(20, 4))
        tk.Label(self, text="Welteroberungsstrategie", font=("Georgia", 11), fg="#a0a0c0", bg="#1a1a2e").pack(pady=(0, 16))

        frame = tk.Frame(self, bg="#16213e", padx=20, pady=16, relief="flat")
        frame.pack(fill="x", padx=20)

        def row(label, widget_fn, row_i):
            tk.Label(frame, text=label, fg="#c0c0e0", bg="#16213e", anchor="w", width=22).grid(row=row_i, column=0, sticky="w", pady=4)
            w = widget_fn(frame)
            w.grid(row=row_i, column=1, sticky="ew", pady=4, padx=(8,0))
            return w

        self.n_human_var = tk.IntVar(value=1)
        self.n_ai_var = tk.IntVar(value=1)
        self.ai_level_var = tk.IntVar(value=2)

        def spin(parent, var, from_, to):
            s = tk.Spinbox(parent, from_=from_, to=to, textvariable=var, width=5,
                           bg="#0f3460", fg="white", buttonbackground="#0f3460",
                           relief="flat", font=("Helvetica", 12))
            return s

        row("Menschliche Spieler:", lambda p: spin(p, self.n_human_var, 1, 6), 0)
        row("KI-Gegner:", lambda p: spin(p, self.n_ai_var, 0, 5), 1)

        tk.Label(frame, text="KI-Schwierigkeit:", fg="#c0c0e0", bg="#16213e", anchor="w", width=22).grid(row=2, column=0, sticky="w", pady=4)
        lvl_frame = tk.Frame(frame, bg="#16213e")
        lvl_frame.grid(row=2, column=1, sticky="w", padx=(8,0))
        for i, lbl in enumerate(["Leicht","Mittel","Schwer"]):
            tk.Radiobutton(lvl_frame, text=lbl, variable=self.ai_level_var, value=i+1,
                           fg="#c0c0e0", bg="#16213e", selectcolor="#0f3460",
                           activebackground="#16213e", activeforeground="white").pack(side="left", padx=4)

        # Player names
        self.name_vars = []
        self.name_frame = tk.LabelFrame(self, text=" Spielernamen ", fg="#f0c040", bg="#1a1a2e",
                                         font=("Helvetica",10), padx=12, pady=8)
        self.name_frame.pack(fill="x", padx=20, pady=(12,0))
        self.n_human_var.trace_add("write", lambda *a: self._update_name_fields())
        self._update_name_fields()

        btn_frame = tk.Frame(self, bg="#1a1a2e")
        btn_frame.pack(pady=16)
        tk.Button(btn_frame, text="Spiel starten", command=self._ok,
                  bg="#f0c040", fg="#1a1a2e", font=("Helvetica",12,"bold"),
                  relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=8)
        tk.Button(btn_frame, text="Abbrechen", command=self.destroy,
                  bg="#333355", fg="white", font=("Helvetica",11),
                  relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left")

    def _update_name_fields(self):
        for w in self.name_frame.winfo_children():
            w.destroy()
        self.name_vars = []
        n = self.n_human_var.get()
        for i in range(n):
            f = tk.Frame(self.name_frame, bg="#1a1a2e")
            f.pack(fill="x", pady=2)
            dot = tk.Label(f, text="●", fg=PLAYER_COLORS[i], bg="#1a1a2e", font=("Helvetica",14))
            dot.pack(side="left", padx=(0,6))
            v = tk.StringVar(value=f"Spieler {i+1}")
            e = tk.Entry(f, textvariable=v, bg="#0f3460", fg="white", insertbackground="white",
                         relief="flat", font=("Helvetica",11), width=20)
            e.pack(side="left")
            self.name_vars.append(v)

    def _ok(self):
        n_h = self.n_human_var.get()
        n_ai = self.n_ai_var.get()
        if n_h + n_ai < 2:
            messagebox.showerror("Fehler", "Mindestens 2 Spieler nötig!", parent=self)
            return
        if n_h + n_ai > 6:
            messagebox.showerror("Fehler", "Maximal 6 Spieler!", parent=self)
            return
        names = [v.get().strip() or f"Spieler {i+1}" for i, v in enumerate(self.name_vars)]
        self.result = {
            "human_names": names,
            "n_ai": n_ai,
            "ai_level": self.ai_level_var.get(),
        }
        self.destroy()


# ───────────────────────── HAUPTFENSTER ──────────────────────────
class RisikoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RISIKO – Welteroberungsstrategie")
        self.configure(bg="#0d0d1a")
        self.state("zoomed") if sys.platform == "win32" else self.attributes("-zoomed", True)
        self.minsize(1100, 700)

        self.gs: Optional[GameState] = None
        self.selected_from: Optional[str] = None  # for attack/fortify
        self.initial_mode = False
        self.initial_remaining = {}
        self.placing_phase_idx = 0

        self._build_ui()
        self._show_main_menu()

    # ── UI Aufbau ──
    def _build_ui(self):
        # Top bar
        self.topbar = tk.Frame(self, bg="#0d0d1a", height=48)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        tk.Label(self.topbar, text="⚔ RISIKO", font=("Georgia",16,"bold"),
                 fg="#f0c040", bg="#0d0d1a").pack(side="left", padx=16)
        self.turn_label = tk.Label(self.topbar, text="", font=("Helvetica",12),
                                   fg="#a0a0c0", bg="#0d0d1a")
        self.turn_label.pack(side="left", padx=16)
        self.phase_label = tk.Label(self.topbar, text="", font=("Helvetica",12,"bold"),
                                    fg="#f0c040", bg="#0d0d1a")
        self.phase_label.pack(side="left", padx=8)

        btn_style = dict(bg="#1a1a3e", fg="#c0c0e0", relief="flat",
                         font=("Helvetica",10), padx=10, pady=4, cursor="hand2")
        self.btn_menu   = tk.Button(self.topbar, text="Hauptmenü", command=self._show_main_menu, **btn_style)
        self.btn_menu.pack(side="right", padx=6)
        self.btn_save   = tk.Button(self.topbar, text="💾 Speichern", command=self._save_game, **btn_style)
        self.btn_save.pack(side="right", padx=4)
        self.btn_cards  = tk.Button(self.topbar, text="🃏 Karten", command=self._show_cards_dialog, **btn_style)
        self.btn_cards.pack(side="right", padx=4)
        self.btn_stats  = tk.Button(self.topbar, text="📊 Stats", command=self._show_stats, **btn_style)
        self.btn_stats.pack(side="right", padx=4)

        # Main area
        self.main_frame = tk.Frame(self, bg="#0d0d1a")
        self.main_frame.pack(fill="both", expand=True)

        # Left: map
        self.map_frame = tk.Frame(self.main_frame, bg="#0d1a2e")
        self.map_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(self.map_frame, bg="#0d1a2e", highlightthickness=0, cursor="hand2")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw_map())
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Right panel
        self.right_panel = tk.Frame(self.main_frame, bg="#0d0d1a", width=260)
        self.right_panel.pack(side="right", fill="y", padx=(0,0))
        self.right_panel.pack_propagate(False)

        # Player status
        self.status_frame = tk.Frame(self.right_panel, bg="#0d0d1a")
        self.status_frame.pack(fill="x", padx=8, pady=(8,0))
        tk.Label(self.status_frame, text="SPIELER", font=("Helvetica",9,"bold"),
                 fg="#606080", bg="#0d0d1a").pack(anchor="w")

        self.player_status_widgets = []
        self.player_frame_container = tk.Frame(self.right_panel, bg="#0d0d1a")
        self.player_frame_container.pack(fill="x", padx=8)

        # Action panel
        self.action_frame = tk.LabelFrame(self.right_panel, text=" AKTION ", font=("Helvetica",9,"bold"),
                                           fg="#f0c040", bg="#16213e", padx=8, pady=8)
        self.action_frame.pack(fill="x", padx=8, pady=8)

        self.action_label = tk.Label(self.action_frame, text="", font=("Helvetica",10),
                                     fg="#c0c0e0", bg="#16213e", wraplength=220, justify="left")
        self.action_label.pack(anchor="w")

        self.troop_var = tk.IntVar(value=1)
        self.troop_spin = tk.Spinbox(self.action_frame, from_=1, to=99, textvariable=self.troop_var,
                                     width=5, bg="#0f3460", fg="white", buttonbackground="#0f3460",
                                     relief="flat", font=("Helvetica",12))

        self.btn_confirm = tk.Button(self.action_frame, text="Bestätigen", command=self._confirm_action,
                                     bg="#2ecc71", fg="white", font=("Helvetica",11,"bold"),
                                     relief="flat", padx=12, pady=6, cursor="hand2")

        self.btn_next_phase = tk.Button(self.action_frame, text="Nächste Phase ▶",
                                        command=self._next_phase,
                                        bg="#3498db", fg="white", font=("Helvetica",11,"bold"),
                                        relief="flat", padx=12, pady=6, cursor="hand2")
        self.btn_next_phase.pack(fill="x", pady=(6,0))

        # Log
        log_frame = tk.LabelFrame(self.right_panel, text=" EREIGNISSE ", font=("Helvetica",9,"bold"),
                                   fg="#f0c040", bg="#0d0d1a", padx=6, pady=6)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))

        self.log_text = tk.Text(log_frame, bg="#060612", fg="#c0d0e0", font=("Courier",9),
                                state="disabled", relief="flat", wrap="word",
                                height=10)
        scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

        # Continent legend
        leg = tk.Frame(self.right_panel, bg="#0d0d1a")
        leg.pack(fill="x", padx=8, pady=(0,4))
        tk.Label(leg, text="KONTINENTE", font=("Helvetica",8,"bold"), fg="#505070", bg="#0d0d1a").pack(anchor="w")
        for cont, data in CONTINENTS.items():
            row = tk.Frame(leg, bg="#0d0d1a")
            row.pack(fill="x")
            tk.Label(row, text="■", fg=data["color"], bg="#0d0d1a", font=("Helvetica",9)).pack(side="left")
            tk.Label(row, text=f"{cont} (+{data['bonus']})", fg="#808090", bg="#0d0d1a",
                     font=("Helvetica",8)).pack(side="left", padx=2)

    # ── Hauptmenü ──
    def _show_main_menu(self):
        self.gs = None
        for w in self.main_frame.winfo_children():
            w.pack_forget()

        menu = tk.Frame(self.main_frame, bg="#0d1a2e")
        menu.pack(fill="both", expand=True)

        center = tk.Frame(menu, bg="#0d1a2e")
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="⚔", font=("Georgia",48), fg="#f0c040", bg="#0d1a2e").pack()
        tk.Label(center, text="RISIKO", font=("Georgia",42,"bold"), fg="#f0c040", bg="#0d1a2e").pack()
        tk.Label(center, text="Welteroberungsstrategie", font=("Georgia",14), fg="#a0a0b0", bg="#0d1a2e").pack(pady=(0,40))

        btn_cfg = dict(font=("Helvetica",14,"bold"), relief="flat",
                       padx=40, pady=12, cursor="hand2", width=22)

        tk.Button(center, text="Neues Spiel", bg="#f0c040", fg="#0d0d1a",
                  command=self._new_game, **btn_cfg).pack(pady=6)
        tk.Button(center, text="Spiel laden", bg="#3498db", fg="white",
                  command=self._load_game, **btn_cfg).pack(pady=6)
        tk.Button(center, text="Regeln", bg="#333355", fg="#c0c0e0",
                  command=self._show_rules, **btn_cfg).pack(pady=6)
        tk.Button(center, text="Beenden", bg="#2c2c3e", fg="#808090",
                  command=self.quit, **btn_cfg).pack(pady=(20,0))

        self.btn_save.configure(state="disabled")
        self.btn_cards.configure(state="disabled")
        self.btn_stats.configure(state="disabled")
        self.turn_label.configure(text="")
        self.phase_label.configure(text="")

    def _show_game_ui(self):
        for w in self.main_frame.winfo_children():
            w.pack_forget()
        self.map_frame.pack(side="left", fill="both", expand=True)
        self.right_panel.pack(side="right", fill="y")
        self.btn_save.configure(state="normal")
        self.btn_cards.configure(state="normal")
        self.btn_stats.configure(state="normal")

    # ── Neues Spiel ──
    def _new_game(self):
        dlg = SetupDialog(self)
        if dlg.result is None:
            return
        cfg = dlg.result
        gs = GameState()
        color_idx = 0
        for name in cfg["human_names"]:
            gs.players.append(Player(name, PLAYER_COLORS[color_idx]))
            color_idx += 1
        for i in range(cfg["n_ai"]):
            ai_name = PLAYER_NAMES_AI[i % len(PLAYER_NAMES_AI)]
            gs.players.append(Player(ai_name, PLAYER_COLORS[color_idx], is_ai=True, ai_level=cfg["ai_level"]))
            color_idx += 1
        random.shuffle(gs.players)
        gs.setup()
        self.gs = gs

        # Initial troop placement
        initial = gs.initial_troops()
        n_terr_each = len(TERRITORIES) // len(gs.players)
        self.initial_remaining = {p.name: initial - n_terr_each for p in gs.players}
        for i in range(len(TERRITORIES) % len(gs.players)):
            self.initial_remaining[gs.players[i].name] -= 1
        self.initial_mode = True
        self.placing_phase_idx = 0

        self._show_game_ui()
        self._start_initial_placement()

    def _start_initial_placement(self):
        self.gs.phase = "initial"
        self._update_player_status()
        self._redraw_map()
        self._run_initial_placement()

    def _run_initial_placement(self):
        if not self.initial_mode:
            return
        # Check if anyone still has troops left
        if all(v <= 0 for v in self.initial_remaining.values()):
            self.initial_mode = False
            self._begin_game()
            return

        # Advance to next player with troops
        while self.initial_remaining.get(self.gs.current_player().name, 0) <= 0:
            self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
            if all(v <= 0 for v in self.initial_remaining.values()):
                self.initial_mode = False
                self._begin_game()
                return

        player = self.gs.current_player()
        if player.is_ai:
            self._ai_initial_place(player)
            self.initial_remaining[player.name] -= 1
            self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
            self.after(80, self._run_initial_placement)
        else:
            rem = self.initial_remaining[player.name]
            self._set_action(f"{player.name}: Platziere Starttruppe\n({rem} verbleibend)\n→ Klicke auf eigenes Gebiet", show_confirm=False)
            self.phase_label.configure(text="STARTAUFSTELLUNG")
            self.turn_label.configure(text=f"| Runde 0")
            self._redraw_map()

    def _ai_initial_place(self, player: Player):
        own = self.gs.owned_territories(player)
        border = [t for t in own if any(self.gs.board[nb]["owner"] != player.name for nb in TERRITORIES[t]["neighbors"])]
        target = random.choice(border if border else own)
        self.gs.board[target]["troops"] += 1

    def _begin_game(self):
        self.gs.current_player_idx = 0
        self.gs.turn = 1
        self._update_player_status()
        self._redraw_map()
        self._start_turn()

    # ── Zugrunde ──
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
        self.turn_label.configure(text=f"| Runde {self.gs.turn}")
        self._update_player_status()
        self._redraw_map()

        if player.is_ai:
            self._run_ai_turn(player)
        else:
            self._check_card_trade(player)
            n = self.gs.calc_reinforcements(player)
            self.gs.pending_troops = n
            self._set_phase_label()
            self._set_action(f"Du erhältst {n} Truppe(n).\n→ Klicke auf Gebiet zum Platzieren.", show_spin=True, spin_max=n)

    def _check_card_trade(self, player: Player):
        sets = self.gs.find_card_sets(player.cards)
        if len(player.cards) >= 5:
            self._do_card_trade(player, force=True)
        elif sets and len(player.cards) >= 3:
            if messagebox.askyesno("Karten tauschen?",
                                   f"Du hast {len(player.cards)} Karten. Set tauschen?\n+{self.gs.card_exchange_value()} Truppen"):
                self._do_card_trade(player)

    def _do_card_trade(self, player: Player, force=False):
        sets = self.gs.find_card_sets(player.cards)
        if not sets:
            if force:
                messagebox.showinfo("Karten", "Kein gültiges Set möglich.", parent=self)
            return
        bonus = self.gs.card_exchange_value()
        chosen = sets[0]
        for card in chosen:
            if card in player.cards:
                player.cards.remove(card)
        self.gs.exchange_count += 1
        self.gs.pending_troops += bonus
        self._log(f"🃏 {player.name} tauscht Karten: +{bonus} Truppen")

    def _set_phase_label(self):
        labels = {
            "reinforcement": "🟢 VERSTÄRKUNG",
            "attack": "🔴 ANGRIFF",
            "fortify": "🔵 VERSCHIEBEN",
            "initial": "⚪ STARTAUFSTELLUNG",
        }
        self.phase_label.configure(text=labels.get(self.gs.phase, ""))

    def _next_phase(self):
        if not self.gs or self.initial_mode:
            return
        player = self.gs.current_player()
        if player.is_ai:
            return

        if self.gs.phase == "reinforcement":
            if self.gs.pending_troops > 0:
                messagebox.showwarning("Truppen platzieren", f"Noch {self.gs.pending_troops} Truppe(n) zu platzieren!", parent=self)
                return
            self.gs.phase = "attack"
            self.selected_from = None
            self._set_phase_label()
            self._set_action("Wähle ein eigenes Gebiet (≥2 Tr.) zum Angreifen.\nOder nächste Phase.", show_confirm=False)
            self._redraw_map()

        elif self.gs.phase == "attack":
            self.gs.phase = "fortify"
            self.selected_from = None
            self._set_phase_label()
            self._set_action("Wähle Gebiet zum Verschieben (≥2 Tr.),\ndann Zielgebiet.\nOder Zug beenden.", show_confirm=False)
            self._redraw_map()

        elif self.gs.phase == "fortify":
            # Draw card
            if player.territories_conquered_this_turn > 0 and self.gs.card_deck:
                card = self.gs.card_deck.pop()
                player.cards.append(card)
                self._log(f"🃏 {player.name} zieht Karte: {card}")
            self._end_turn()

    def _end_turn(self):
        self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
        if self.gs.current_player_idx == 0:
            self.gs.turn += 1
        self.gs.check_winner()
        if self.gs.game_over:
            self._show_winner()
            return
        self._start_turn()

    # ── KI Zug ──
    def _run_ai_turn(self, player: Player):
        self._log(f"🤖 {player.name} ist am Zug...")
        self.phase_label.configure(text="🤖 KI AM ZUG")
        self.update_idletasks()

        # Cards
        if self.gs.find_card_sets(player.cards) and len(player.cards) >= 3:
            sets = self.gs.find_card_sets(player.cards)
            for card in sets[0]:
                if card in player.cards:
                    player.cards.remove(card)
            bonus = self.gs.card_exchange_value()
            self.gs.exchange_count += 1
            self.gs.pending_troops = bonus
            self._log(f"🃏 {player.name}: Kartentausch +{bonus}")

        n = self.gs.calc_reinforcements(player) + self.gs.pending_troops
        self.gs.pending_troops = 0
        self.gs.ai_place_troops(player, n)
        self._log(f"➕ {player.name} erhält {n} Truppen")

        # Attack
        for _ in range(15 * player.ai_level):
            if not self.gs.ai_attack(player):
                break
            self.gs.check_winner()
            if self.gs.game_over:
                self._redraw_map()
                self._update_player_status()
                self._show_winner()
                return

        # Fortify
        self.gs.ai_fortify(player)

        # Card
        if player.territories_conquered_this_turn > 0 and self.gs.card_deck:
            card = self.gs.card_deck.pop()
            player.cards.append(card)

        self._redraw_map()
        self._update_player_status()
        self.after(300, self._end_turn)

    # ── Canvas Klick ──
    def _on_canvas_click(self, event):
        if not self.gs or self.gs.game_over:
            return
        player = self.gs.current_player()
        if player.is_ai:
            return

        clicked = self._territory_at(event.x, event.y)
        if not clicked:
            return

        if self.initial_mode:
            self._handle_initial_click(clicked, player)
        elif self.gs.phase == "reinforcement":
            self._handle_reinforce_click(clicked, player)
        elif self.gs.phase == "attack":
            self._handle_attack_click(clicked, player)
        elif self.gs.phase == "fortify":
            self._handle_fortify_click(clicked, player)

    def _handle_initial_click(self, terr, player):
        if self.gs.board[terr]["owner"] != player.name:
            return
        self.gs.board[terr]["troops"] += 1
        self.initial_remaining[player.name] -= 1
        self._log(f"📍 {player.name}: +1 → {terr} ({self.gs.board[terr]['troops']} Tr.)")
        self._redraw_map()
        self.gs.current_player_idx = (self.gs.current_player_idx + 1) % len(self.gs.players)
        self.after(50, self._run_initial_placement)

    def _handle_reinforce_click(self, terr, player):
        if self.gs.board[terr]["owner"] != player.name:
            return
        if self.gs.pending_troops <= 0:
            return
        n = min(self.troop_var.get(), self.gs.pending_troops)
        self.gs.board[terr]["troops"] += n
        self.gs.pending_troops -= n
        self._log(f"➕ {player.name}: +{n} → {terr} ({self.gs.board[terr]['troops']} Tr.)")
        self._redraw_map()
        if self.gs.pending_troops > 0:
            max_v = self.gs.pending_troops
            self._set_action(f"{self.gs.pending_troops} Truppe(n) verbleibend.\n→ Klicke auf eigenes Gebiet.", show_spin=True, spin_max=max_v)
        else:
            self._set_action("Alle Truppen platziert.\n▶ Nächste Phase: Angriff", show_confirm=False)
            self.troop_spin.pack_forget()

    def _handle_attack_click(self, terr, player):
        board = self.gs.board
        if self.selected_from is None:
            if board[terr]["owner"] == player.name and board[terr]["troops"] >= 2:
                self.selected_from = terr
                self._set_action(f"Von: {terr} ({board[terr]['troops']} Tr.)\n→ Klicke auf feindliches Nachbargebiet.", show_confirm=False)
                self._redraw_map()
            else:
                self._set_action("Wähle eigenes Gebiet mit ≥2 Truppen.", show_confirm=False)
        else:
            if terr == self.selected_from:
                self.selected_from = None
                self._set_action("Auswahl aufgehoben.\nWähle Angriffsgebiet.", show_confirm=False)
                self._redraw_map()
                return
            neighbors = TERRITORIES[self.selected_from]["neighbors"]
            if terr not in neighbors or board[terr]["owner"] == player.name:
                self.selected_from = None
                self._set_action("Kein gültiges Ziel.\nNeu wählen.", show_confirm=False)
                self._redraw_map()
                return
            # Battle!
            self._do_attack(self.selected_from, terr, player)
            self.selected_from = None

    def _do_attack(self, from_t, to_t, player):
        def_owner = self.gs.board[to_t]["owner"]
        atk_r, def_r, atk_w, def_w, conquered = self.gs.resolve_battle(from_t, to_t)
        result = f"⚔ {from_t} → {to_t}\n  [{', '.join(str(r) for r in atk_r)}] vs [{', '.join(str(r) for r in def_r)}]"
        if conquered:
            result += f"\n  ✅ {to_t} eingenommen!"
            def_p = self.gs.player_by_name(def_owner)
            if def_p and not self.gs.is_alive(def_p):
                result += f"\n  💀 {def_owner} eliminiert!"
                self._log(f"💀 {def_owner} wurde eliminiert von {player.name}!")
        else:
            result += f"\n  Angreifer -{def_w}, Verteidiger -{atk_w}"
        self._log(result)
        self._redraw_map()
        self._update_player_status()
        self.gs.check_winner()
        if self.gs.game_over:
            self._show_winner()
        else:
            self._set_action("Wähle nächsten Angriff\noder nächste Phase.", show_confirm=False)

    def _handle_fortify_click(self, terr, player):
        board = self.gs.board
        if self.selected_from is None:
            if board[terr]["owner"] == player.name and board[terr]["troops"] >= 2:
                self.selected_from = terr
                self._set_action(f"Von: {terr} ({board[terr]['troops']} Tr.)\n→ Klicke auf verbundenes eigenes Gebiet.", show_confirm=False)
                self._redraw_map()
        else:
            if terr == self.selected_from:
                self.selected_from = None
                self._redraw_map()
                return
            if board[terr]["owner"] != player.name:
                self.selected_from = None
                self._redraw_map()
                return
            reachable = self.gs.reachable(player, self.selected_from)
            if terr not in reachable:
                self._set_action("Nicht verbunden!\nNeu wählen.", show_confirm=False)
                self.selected_from = None
                self._redraw_map()
                return
            max_m = board[self.selected_from]["troops"] - 1
            n = self.troop_var.get()
            n = min(n, max_m)
            board[self.selected_from]["troops"] -= n
            board[terr]["troops"] += n
            self._log(f"🔀 {player.name}: {n} Tr. {self.selected_from} → {terr}")
            self.selected_from = None
            self._redraw_map()
            self._set_action("Verschoben.\nZug beenden?", show_confirm=False)

    def _confirm_action(self):
        pass  # handled inline

    # ── Karte zeichnen ──
    def _redraw_map(self):
        if not self.gs:
            return
        c = self.canvas
        c.delete("all")
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 2 or H < 2:
            return

        sx = W / 880
        sy = H / 480

        # Draw connections
        for t, data in TERRITORIES.items():
            x1, y1 = data["pos"][0]*sx, data["pos"][1]*sy
            for nb in data["neighbors"]:
                if nb in TERRITORIES:
                    x2, y2 = TERRITORIES[nb]["pos"][0]*sx, TERRITORIES[nb]["pos"][1]*sy
                    # Skip long connections across map edge (Kamtschatka-Alaska etc.)
                    if abs(x1 - x2) > W * 0.4:
                        continue
                    c.create_line(x1, y1, x2, y2, fill="#1a2a4a", width=1)

        # Draw territories
        for t, data in TERRITORIES.items():
            x, y = data["pos"][0]*sx, data["pos"][1]*sy
            owner_name = self.gs.board[t]["owner"]
            troops = self.gs.board[t]["troops"]
            player = self.gs.player_by_name(owner_name) if owner_name else None
            color = player.color if player else "#404040"
            cont_color = CONTINENTS[data["continent"]]["color"]

            # Highlight selected
            is_selected = (t == self.selected_from)
            is_attackable = (self.selected_from and self.gs.phase == "attack" and
                             t in TERRITORIES[self.selected_from]["neighbors"] and
                             self.gs.board[t]["owner"] != self.gs.current_player().name)
            is_fortifiable = (self.selected_from and self.gs.phase == "fortify" and
                              self.gs.board[t]["owner"] == self.gs.current_player().name and
                              t in self.gs.reachable(self.gs.current_player(), self.selected_from))

            r = max(14, int(16 * min(sx, sy)))
            outline_color = "#ffffff" if is_selected else ("#ff4444" if is_attackable else ("#44aaff" if is_fortifiable else cont_color))
            outline_w = 3 if (is_selected or is_attackable or is_fortifiable) else 1

            c.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=outline_color, width=outline_w, tags=("territory", t))
            c.create_text(x, y, text=str(troops), fill="white",
                          font=("Helvetica", max(8, int(9*min(sx,sy))), "bold"), tags=("territory", t))

            # Territory name (abbreviated for small maps)
            name_short = t if len(t) <= 10 else t[:9]+"."
            c.create_text(x, y+r+6, text=name_short,
                          fill="#a0b0c0", font=("Helvetica", max(6, int(7*min(sx,sy)))),
                          tags=("territory", t))

    def _territory_at(self, mx, my) -> Optional[str]:
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        sx = W / 880
        sy = H / 480
        r = max(14, int(16 * min(sx, sy))) + 4
        best, best_d = None, r*r
        for t, data in TERRITORIES.items():
            x, y = data["pos"][0]*sx, data["pos"][1]*sy
            d = (mx-x)**2 + (my-y)**2
            if d < best_d:
                best_d = d
                best = t
        return best

    # ── Rechtes Panel ──
    def _set_action(self, text, show_confirm=False, show_spin=False, spin_max=10):
        self.action_label.configure(text=text)
        if show_spin:
            self.troop_var.set(1)
            self.troop_spin.configure(to=spin_max)
            self.troop_spin.pack(fill="x", pady=(6,0))
        else:
            self.troop_spin.pack_forget()
        if show_confirm:
            self.btn_confirm.pack(fill="x", pady=(4,0))
        else:
            self.btn_confirm.pack_forget()

    def _update_player_status(self):
        for w in self.player_frame_container.winfo_children():
            w.destroy()
        if not self.gs:
            return
        for p in self.gs.players:
            alive = self.gs.is_alive(p)
            terr = len(self.gs.owned_territories(p))
            troops = sum(d["troops"] for d in self.gs.board.values() if d["owner"] == p.name)
            is_current = (p == self.gs.current_player() and not self.gs.game_over)

            row = tk.Frame(self.player_frame_container,
                           bg="#1a2a3e" if is_current else "#0d0d1a",
                           pady=3, padx=6)
            row.pack(fill="x", pady=1)
            if is_current:
                tk.Label(row, text="▶", fg="#f0c040", bg="#1a2a3e", font=("Helvetica",8)).pack(side="left")

            dot_bg = "#1a2a3e" if is_current else "#0d0d1a"
            tk.Label(row, text="●", fg=p.color if alive else "#404040",
                     bg=dot_bg, font=("Helvetica",14)).pack(side="left")
            name_color = "#f0f0f0" if alive else "#505050"
            tk.Label(row, text=p.name[:14], fg=name_color,
                     bg=dot_bg, font=("Helvetica",9)).pack(side="left", padx=4)
            ai_str = f"{'AI' if p.is_ai else ''}"
            tk.Label(row, text=ai_str, fg="#606070", bg=dot_bg, font=("Helvetica",8)).pack(side="left")
            tk.Label(row, text=f"{terr}🗺 {troops}⚔", fg="#80a0c0",
                     bg=dot_bg, font=("Helvetica",8)).pack(side="right")

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ── Dialoge ──
    def _show_cards_dialog(self):
        if not self.gs:
            return
        player = self.gs.current_player()
        if player.is_ai:
            return
        c = Counter(player.cards)
        msg = f"Karten von {player.name}:\n\n"
        if not player.cards:
            msg += "(keine Karten)"
        else:
            for k, v in c.items():
                msg += f"  {v}× {k}\n"
            sets = self.gs.find_card_sets(player.cards)
            if sets:
                msg += f"\n✅ Tauschbar: {len(sets)} Set(s) → +{self.gs.card_exchange_value()} Truppen"
                if messagebox.askyesno("Karten", msg + "\n\nJetzt tauschen?", parent=self):
                    self._do_card_trade(player)
                    if self.gs.phase == "reinforcement":
                        n = self.gs.pending_troops
                        self._set_action(f"{n} Truppe(n) zu platzieren.\n→ Klicke auf eigenes Gebiet.", show_spin=True, spin_max=n)
                return
        messagebox.showinfo("Karten", msg, parent=self)

    def _show_stats(self):
        if not self.gs:
            return
        win = tk.Toplevel(self)
        win.title("Statistiken")
        win.configure(bg="#0d1a2e")
        win.geometry("500x350")

        tk.Label(win, text="STATISTIKEN", font=("Helvetica",14,"bold"),
                 fg="#f0c040", bg="#0d1a2e").pack(pady=12)

        cols = ["Spieler","Gebiete","Truppen","Angriffe","Gewonnen","Get./Verl."]
        f = tk.Frame(win, bg="#0d1a2e")
        f.pack(fill="both", expand=True, padx=16)

        for j, col in enumerate(cols):
            tk.Label(f, text=col, fg="#606080", bg="#0d1a2e",
                     font=("Helvetica",9,"bold"), width=10).grid(row=0, column=j, pady=4)

        for i, p in enumerate(self.gs.players):
            terr = len(self.gs.owned_territories(p))
            troops = sum(d["troops"] for d in self.gs.board.values() if d["owner"] == p.name)
            wr = f"{100*p.attacks_won//p.attacks_total}%" if p.attacks_total > 0 else "–"
            vals = [p.name, terr, troops, p.attacks_total, wr, f"{p.troops_killed}/{p.troops_lost}"]
            for j, v in enumerate(vals):
                fg = p.color if j == 0 else "#c0c0e0"
                tk.Label(f, text=str(v), fg=fg, bg="#0d1a2e",
                         font=("Helvetica",10), width=10).grid(row=i+1, column=j, pady=3)

        tk.Button(win, text="Schließen", command=win.destroy,
                  bg="#333355", fg="white", relief="flat", padx=16, pady=6).pack(pady=12)

    def _show_winner(self):
        w = self.gs.winner
        self._update_player_status()
        self._redraw_map()
        win = tk.Toplevel(self)
        win.title("Spielende")
        win.configure(bg="#0d1a2e")
        win.geometry("400x300")
        win.grab_set()

        tk.Label(win, text="🏆", font=("Helvetica",48), bg="#0d1a2e").pack(pady=(20,0))
        tk.Label(win, text=f"{w.name} HAT GEWONNEN!", font=("Helvetica",16,"bold"),
                 fg=w.color, bg="#0d1a2e").pack(pady=8)
        tk.Label(win, text=f"Nach {self.gs.turn} Runden", fg="#a0a0c0",
                 bg="#0d1a2e", font=("Helvetica",11)).pack()
        tk.Label(win, text=f"Eroberungen: {w.territories_captured}  |  Angriffe: {w.attacks_total}",
                 fg="#808090", bg="#0d1a2e", font=("Helvetica",10)).pack(pady=4)

        tk.Button(win, text="Statistiken", command=lambda: (win.destroy(), self._show_stats()),
                  bg="#3498db", fg="white", relief="flat", padx=16, pady=8,
                  font=("Helvetica",11)).pack(pady=(16,4))
        tk.Button(win, text="Hauptmenü", command=lambda: (win.destroy(), self._show_main_menu()),
                  bg="#333355", fg="white", relief="flat", padx=16, pady=8,
                  font=("Helvetica",11)).pack(pady=4)

    def _show_rules(self):
        win = tk.Toplevel(self)
        win.title("Regeln")
        win.configure(bg="#0d1a2e")
        win.geometry("520x480")

        tk.Label(win, text="RISIKO – REGELN", font=("Georgia",14,"bold"),
                 fg="#f0c040", bg="#0d1a2e").pack(pady=12)

        text = tk.Text(win, bg="#060612", fg="#c0d0e0", font=("Helvetica",10),
                       relief="flat", wrap="word", padx=12, pady=8)
        text.pack(fill="both", expand=True, padx=16, pady=(0,8))

        rules = """ZIEL: Alle Gebiete der Welt erobern.

SPIELABLAUF je Runde:
  1. Verstärkung: Erhalte Truppen (max(3, Gebiete/3) + Kontinent-Boni).
  2. Angriff: Greife feindliche Nachbargebiete an (klicken).
  3. Verschieben: Bewege Truppen zwischen verbundenen eigenen Gebieten.

KAMPF:
  • Angreifer würfelt bis zu 3 Würfel (benötigt ≥2 Truppen).
  • Verteidiger würfelt bis zu 2 Würfel.
  • Bei Gleichstand gewinnt der Verteidiger.

KONTINENTE (Bonus pro Runde):
  • Nordamerika: +5    • Südamerika: +2
  • Europa: +5         • Afrika: +3
  • Asien: +7          • Australien: +2

KARTEN:
  • Bei jedem eroberten Gebiet gibt es eine Karte.
  • 3 Karten (gleich oder je eine) → Truppen-Bonus.
  • Bonus steigt mit jedem Tausch.

BEDIENUNG:
  • Verstärkung: Gebiet anklicken, Anzahl mit Spinbox.
  • Angriff: Eigenes Gebiet wählen → feindliches anklicken.
  • Verschieben: Eigenes Gebiet wählen → Ziel anklicken.
  • ▶ Nächste Phase mit dem Button rechts.
"""
        text.insert("1.0", rules)
        text.configure(state="disabled")
        tk.Button(win, text="Schließen", command=win.destroy,
                  bg="#333355", fg="white", relief="flat", padx=16, pady=6).pack(pady=8)

    # ── Speichern / Laden ──
    def _save_game(self):
        if not self.gs:
            return
        ensure_save_dir()
        slot = simpledialog.askstring("Speichern", "Spielstand-Name:", initialvalue="autosave", parent=self)
        if not slot:
            return
        path = os.path.join(SAVE_DIR, f"{slot}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.gs.to_dict(), f, ensure_ascii=False, indent=2)
        self._log(f"💾 Gespeichert: {slot}")
        messagebox.showinfo("Gespeichert", f"Spielstand '{slot}' gespeichert.", parent=self)

    def _load_game(self):
        ensure_save_dir()
        saves = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        if not saves:
            messagebox.showinfo("Laden", "Keine gespeicherten Spiele gefunden.", parent=self)
            return

        win = tk.Toplevel(self)
        win.title("Spiel laden")
        win.configure(bg="#0d1a2e")
        win.geometry("300x300")
        win.grab_set()

        tk.Label(win, text="Spielstand wählen:", fg="#c0c0e0", bg="#0d1a2e",
                 font=("Helvetica",12)).pack(pady=12)

        lb = tk.Listbox(win, bg="#060612", fg="#c0d0e0", font=("Helvetica",11),
                        selectbackground="#3498db", relief="flat")
        lb.pack(fill="both", expand=True, padx=16)
        for s in saves:
            lb.insert("end", s.replace(".json",""))

        def do_load():
            sel = lb.curselection()
            if not sel:
                return
            slot = saves[sel[0]].replace(".json","")
            path = os.path.join(SAVE_DIR, f"{slot}.json")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            gs = GameState()
            gs.from_dict(data)
            self.gs = gs
            self.initial_mode = False
            win.destroy()
            self._show_game_ui()
            self._update_player_status()
            self._redraw_map()
            self._set_phase_label()
            self.turn_label.configure(text=f"| Runde {gs.turn}")
            self._log(f"📂 Spielstand geladen: {slot}")
            player = gs.current_player()
            if not player.is_ai:
                if gs.phase == "reinforcement":
                    n = gs.pending_troops if gs.pending_troops > 0 else gs.calc_reinforcements(player)
                    gs.pending_troops = n
                    self._set_action(f"{n} Truppe(n) zu platzieren.", show_spin=True, spin_max=n)
                else:
                    self._set_action("Zug fortsetzen.", show_confirm=False)
            else:
                self.after(500, lambda: self._run_ai_turn(player))

        tk.Button(win, text="Laden", command=do_load,
                  bg="#2ecc71", fg="white", font=("Helvetica",11,"bold"),
                  relief="flat", padx=16, pady=8).pack(pady=12)


if __name__ == "__main__":
    app = RisikoApp()
    app.mainloop()
