"""
╔══════════════════════════════════════════════════════╗
║           ULTRA PONG  –  tkinter edition             ║
║  Modi: 1P vs KI | 2P lokal | KI vs KI               ║
║  Schwierigkeit: Easy / Medium / Hard / Insane        ║
║  Upgrades: Shop mit Coins                            ║
╚══════════════════════════════════════════════════════╝
Starten: python pingpong.py
"""

import tkinter as tk
import random, math, json, os

# ──────────────────────────── Konstanten ──────────────────────────────────────
W, H          = 1000, 640
PAD_W         = 14
BALL_R        = 11
MAX_SCORE     = 7
FPS           = 15
SAVE_FILE     = "pong_save.json"

BG      = "#07070f"
C_NET   = "#1a1a2e"
C_WHITE = "#e2e8f0"
C_DIM   = "#475569"
C_L     = "#38bdf8"
C_R     = "#f472b6"
C_GOLD  = "#fbbf24"
C_GREEN = "#4ade80"
C_RED   = "#f87171"
C_PURP  = "#a78bfa"

FONT_BIG  = ("Courier", 56, "bold")
FONT_MED  = ("Courier", 22, "bold")
FONT_SM   = ("Courier", 13)
FONT_XSM  = ("Courier", 11)

AI_PROFILES = {
    "Easy":   (0.35, 5,  80),
    "Medium": (0.55, 9,  35),
    "Hard":   (0.78, 14, 10),
    "Insane": (0.98, 22,  0),
}

UPGRADES_DEF = [
    ("pad_size",     "Paddle XL",     "+20 px Paddle-Hoehe",          60,  4, C_L),
    ("ball_slow",    "Slow-Mo",       "Ball startet 15% langsamer",   80,  3, C_PURP),
    ("multi_ball",   "Multi-Ball",    "+1 Ball (max 3)",              150, 2, C_GOLD),
    ("wall_bounce",  "Seitenwaende",  "Waende prallen den Ball",      100, 1, C_GREEN),
    ("coin_boost",   "Coin-Boost",    "+50% Coins pro Punkt",         120, 3, C_GOLD),
    ("pad_speed",    "Speed-Paddle",  "+4 Paddle-Geschwindigkeit",     90, 3, C_R),
    ("shield",       "Schild",        "1x Tor abwehren pro Spiel",    200, 2, C_GREEN),
    ("shrink_enemy", "Enemy Shrink",  "Gegner-Paddle -15 px",         180, 2, C_RED),
]

# ──────────────────────────── Hilfsfunktionen ─────────────────────────────────
def clamp(v, lo, hi): return max(lo, min(hi, v))

def draw_rounded_rect(canvas, x1, y1, x2, y2, r=12, **kw):
    pts = [
        x1+r, y1,   x2-r, y1,
        x2,   y1,   x2,   y1+r,
        x2,   y2-r, x2,   y2,
        x2-r, y2,   x1+r, y2,
        x1,   y2,   x1,   y2-r,
        x1,   y1+r, x1,   y1,
        x1+r, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)

def load_save():
    default = {"coins": 0, "upgrades": {uid: 0 for uid, *_ in UPGRADES_DEF}}
    if not os.path.exists(SAVE_FILE):
        return default
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        for uid, *_ in UPGRADES_DEF:
            data["upgrades"].setdefault(uid, 0)
        return data
    except Exception:
        return default

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ULTRA PONG")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.save = load_save()
        self.canvas = tk.Canvas(self, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self._show_main_menu()

    def _clear(self):
        self.canvas.delete("all")

    def _show_main_menu(self):
        self._clear()
        MainMenu(self)

    def _show_mode_select(self):
        self._clear()
        ModeSelect(self)

    def _show_upgrade_shop(self):
        self._clear()
        UpgradeShop(self)

    def start_game(self, mode, difficulty):
        self._clear()
        GameScreen(self, mode, difficulty)

# ══════════════════════════════════════════════════════════════════════════════
class MainMenu:
    def __init__(self, app):
        self.app = app
        c = app.canvas
        for y in range(0, H, 4):
            c.create_line(0, y, W, y, fill="#0d0d1a", width=1)
        for y in range(0, H, 28):
            c.create_rectangle(W//2 - 2, y, W//2 + 2, y + 14, fill=C_NET, outline="")

        c.create_text(W//2, 105, text="ULTRA", font=("Courier", 80, "bold"), fill=C_L, anchor="center")
        c.create_text(W//2, 195, text="PONG",  font=("Courier", 80, "bold"), fill=C_R, anchor="center")
        c.create_text(W//2, 255, text="─── RETRO ARCADE ───", font=FONT_XSM, fill=C_DIM, anchor="center")
        c.create_text(W - 20, 18, text=f"Coins: {app.save['coins']}", font=FONT_SM, fill=C_GOLD, anchor="ne")

        for i, (label, cmd, col) in enumerate([
            ("SPIELEN",   app._show_mode_select,  C_L),
            ("UPGRADES",  app._show_upgrade_shop, C_GOLD),
        ]):
            self._btn(c, W//2, 370 + i * 95, label, cmd, col)

        c.create_text(W//2, H - 28,
                      text="W/S  Linkes Paddle     Up/Down  Rechtes Paddle     SPACE  Pause",
                      font=FONT_XSM, fill=C_DIM, anchor="center")

    def _btn(self, c, x, y, text, cmd, col, w=300, h=54):
        rect = draw_rounded_rect(c, x-w//2, y-h//2, x+w//2, y+h//2,
                                 r=10, fill="#0f0f1e", outline=col, width=2)
        lbl  = c.create_text(x, y, text=text, font=FONT_MED, fill=col, anchor="center")
        def on_enter(e): c.itemconfig(rect, fill=col);       c.itemconfig(lbl, fill=BG)
        def on_leave(e): c.itemconfig(rect, fill="#0f0f1e"); c.itemconfig(lbl, fill=col)
        for item in (rect, lbl):
            c.tag_bind(item, "<Enter>",    on_enter)
            c.tag_bind(item, "<Leave>",    on_leave)
            c.tag_bind(item, "<Button-1>", lambda e, f=cmd: f())

# ══════════════════════════════════════════════════════════════════════════════
class ModeSelect:
    MODES = [("1P  vs  KI","pve",C_L), ("2P  Lokal","pvp",C_R), ("KI  vs  KI","eve",C_PURP)]
    DIFFS = ["Easy","Medium","Hard","Insane"]

    def __init__(self, app):
        self.app = app
        self.mode = tk.StringVar(value="pve")
        self.diff = tk.StringVar(value="Medium")
        c = app.canvas
        for y in range(0, H, 4):
            c.create_line(0, y, W, y, fill="#0d0d1a", width=1)
        for y in range(0, H, 28):
            c.create_rectangle(W//2-2, y, W//2+2, y+14, fill=C_NET, outline="")

        c.create_text(W//2, 55, text="SPIELMODUS  WAEHLEN", font=FONT_MED, fill=C_WHITE, anchor="center")

        self._mode_items = {}
        for i, (label, mid, col) in enumerate(self.MODES):
            self._mode_card(c, 200 + i*300, 190, label, mid, col)

        c.create_text(W//2, 305, text="SCHWIERIGKEIT", font=("Courier",14,"bold"), fill=C_DIM, anchor="center")
        self._diff_items = {}
        for i, d in enumerate(self.DIFFS):
            self._diff_btn(c, 275 + i*152, 368, d)

        # Beschreibungen
        desc_map = {
            "Easy":   "KI reagiert langsam – perfekt zum Einstieg",
            "Medium": "Ausgeglichenes Spiel",
            "Hard":   "KI spielt fast fehlerfrei",
            "Insane": "Keine Gnade. Kein Fehler. Kein Entkommen.",
        }
        self._desc_id = c.create_text(W//2, 425, text=desc_map["Medium"],
                                       font=FONT_XSM, fill=C_PURP, anchor="center")
        self._desc_map = desc_map

        # Start
        sx, sy = W//2, 528
        sr = draw_rounded_rect(c, sx-190, sy-38, sx+190, sy+38, r=12,
                                fill="#0f0f1e", outline=C_GREEN, width=2)
        sl = c.create_text(sx, sy, text="START", font=FONT_MED, fill=C_GREEN, anchor="center")
        def go(e=None): app.start_game(self.mode.get(), self.diff.get())
        def se(e): c.itemconfig(sr, fill=C_GREEN); c.itemconfig(sl, fill=BG)
        def sl2(e): c.itemconfig(sr, fill="#0f0f1e"); c.itemconfig(sl, fill=C_GREEN)
        for item in (sr, sl):
            c.tag_bind(item, "<Button-1>", go)
            c.tag_bind(item, "<Enter>", se)
            c.tag_bind(item, "<Leave>", sl2)

        back = c.create_text(40, H-30, text="< Zurueck", font=FONT_SM, fill=C_DIM, anchor="w")
        c.tag_bind(back, "<Button-1>", lambda e: app._show_main_menu())
        c.tag_bind(back, "<Enter>",    lambda e: c.itemconfig(back, fill=C_WHITE))
        c.tag_bind(back, "<Leave>",    lambda e: c.itemconfig(back, fill=C_DIM))

    def _mode_card(self, c, x, y, label, mid, col):
        rect = draw_rounded_rect(c, x-115, y-50, x+115, y+50, r=12,
                                 fill="#0f0f1e", outline=col, width=2)
        lbl  = c.create_text(x, y, text=label, font=("Courier",15,"bold"), fill=col, anchor="center")
        self._mode_items[mid] = (rect, lbl, col)
        def select(e=None):
            self.mode.set(mid); self._refresh_cards()
        def on_enter(e):
            if self.mode.get() != mid: c.itemconfig(rect, fill="#1a1a2e")
        def on_leave(e):
            if self.mode.get() != mid: c.itemconfig(rect, fill="#0f0f1e")
        for item in (rect, lbl):
            c.tag_bind(item, "<Button-1>", select)
            c.tag_bind(item, "<Enter>", on_enter)
            c.tag_bind(item, "<Leave>", on_leave)
        self._refresh_cards()

    def _refresh_cards(self):
        c = self.app.canvas
        for mid, (rect, lbl, col) in self._mode_items.items():
            if self.mode.get() == mid:
                c.itemconfig(rect, fill=col); c.itemconfig(lbl, fill=BG)
            else:
                c.itemconfig(rect, fill="#0f0f1e"); c.itemconfig(lbl, fill=col)

    def _diff_btn(self, c, x, y, d):
        col_map = {"Easy":C_GREEN,"Medium":C_L,"Hard":C_GOLD,"Insane":C_R}
        col  = col_map[d]
        rect = draw_rounded_rect(c, x-62, y-26, x+62, y+26, r=8, fill="#0f0f1e", outline=col, width=2)
        lbl  = c.create_text(x, y, text=d, font=("Courier",13,"bold"), fill=col, anchor="center")
        self._diff_items[d] = (rect, lbl, col)
        def select(e=None):
            self.diff.set(d)
            self._refresh_diffs()
            self.app.canvas.itemconfig(self._desc_id, text=self._desc_map[d])
        for item in (rect, lbl):
            c.tag_bind(item, "<Button-1>", select)
        self._refresh_diffs()

    def _refresh_diffs(self):
        c = self.app.canvas
        for d, (rect, lbl, col) in self._diff_items.items():
            if self.diff.get() == d:
                c.itemconfig(rect, fill=col); c.itemconfig(lbl, fill=BG)
            else:
                c.itemconfig(rect, fill="#0f0f1e"); c.itemconfig(lbl, fill=col)

# ══════════════════════════════════════════════════════════════════════════════
class UpgradeShop:
    def __init__(self, app):
        self.app = app
        c = app.canvas
        self._draw(c)

    def _draw(self, c):
        c.delete("all")
        app = self.app
        for y in range(0, H, 4):
            c.create_line(0, y, W, y, fill="#0d0d1a", width=1)
        c.create_text(W//2, 44, text="UPGRADE  SHOP", font=FONT_MED, fill=C_GOLD, anchor="center")
        self.coin_id = c.create_text(W-20, 18, text=f"Coins: {app.save['coins']}",
                                     font=FONT_SM, fill=C_GOLD, anchor="ne")
        cols, cw, ch = 4, W//4, 195
        ups = app.save["upgrades"]
        for idx, (uid, name, desc, price, max_lv, col) in enumerate(UPGRADES_DEF):
            ci = idx % cols; ri = idx // cols
            cx = ci * cw + cw//2; cy = 90 + ri*(ch+12) + ch//2
            lv = ups.get(uid, 0); maxed = lv >= max_lv
            ac = col if not maxed else C_DIM
            draw_rounded_rect(c, cx-cw//2+8, cy-ch//2, cx+cw//2-8, cy+ch//2, r=10,
                              fill="#0f0f1e", outline=ac, width=2)
            c.create_text(cx, cy-ch//2+26, text=name, font=("Courier",12,"bold"), fill=ac, anchor="center")
            c.create_text(cx, cy-ch//2+52, text=desc, font=FONT_XSM, fill=C_DIM, anchor="center")
            for s in range(max_lv):
                dx2 = cx-(max_lv-1)*10+s*20; dy2 = cy+8
                c.create_oval(dx2-6,dy2-6,dx2+6,dy2+6, fill=(col if s<lv else "#1a1a2e"), outline="")
            btn_y = cy+ch//2-26
            if maxed:
                c.create_text(cx, btn_y, text="MAX", font=("Courier",12,"bold"), fill=C_GREEN, anchor="center")
            else:
                cost = price*(lv+1); can = app.save["coins"] >= cost; bc = col if can else C_DIM
                br = draw_rounded_rect(c, cx-68, btn_y-17, cx+68, btn_y+17, r=6, fill="#0f0f1e", outline=bc, width=2)
                bl = c.create_text(cx, btn_y, text=f"Coins {cost}  Lv {lv+1}", font=FONT_XSM, fill=bc, anchor="center")
                if can:
                    def buy(e, _uid=uid, _cost=cost):
                        app.save["coins"] -= _cost
                        app.save["upgrades"][_uid] += 1
                        save_data(app.save)
                        self._draw(c)
                        self._add_back(c)
                    for item in (br, bl):
                        c.tag_bind(item, "<Button-1>", buy)
        self._add_back(c)

    def _add_back(self, c):
        back = c.create_text(40, H-30, text="< Zurueck", font=FONT_SM, fill=C_DIM, anchor="w")
        c.tag_bind(back, "<Button-1>", lambda e: self.app._show_main_menu())
        c.tag_bind(back, "<Enter>",    lambda e: c.itemconfig(back, fill=C_WHITE))
        c.tag_bind(back, "<Leave>",    lambda e: c.itemconfig(back, fill=C_DIM))

# ══════════════════════════════════════════════════════════════════════════════
class Ball:
    def __init__(self, canvas, x, y, dx, dy):
        self.c = canvas; self.x=x; self.y=y; self.dx=dx; self.dy=dy; self.frozen=0
        self.id = canvas.create_oval(0,0,0,0, fill=C_WHITE, outline="")
        self.trail = []

    def draw(self):
        r = BALL_R
        self.c.coords(self.id, self.x-r, self.y-r, self.x+r, self.y+r)
        tr = self.c.create_oval(self.x-r+3, self.y-r+3, self.x+r-3, self.y+r-3,
                                 fill="#1e293b", outline="")
        self.trail.append(tr)
        if len(self.trail) > 5: self.c.delete(self.trail.pop(0))
        self.c.tag_raise(self.id)

    def destroy(self):
        for t in self.trail: self.c.delete(t)
        self.c.delete(self.id)

# ══════════════════════════════════════════════════════════════════════════════
class GameScreen:
    def __init__(self, app, mode, difficulty):
        self.app=app; self.mode=mode; self.difficulty=difficulty; self.c=app.canvas
        ups = app.save["upgrades"]

        self.pad_h      = 100 + ups.get("pad_size",0)*20
        self.pad_spd    = 18  + ups.get("pad_speed",0)*4
        self.enemy_pad_h= max(40, self.pad_h - ups.get("shrink_enemy",0)*15)
        self.ball_spd0  = max(4, 7 - ups.get("ball_slow",0)*1.0)
        self.wall_bounce= bool(ups.get("wall_bounce",0))
        self.coin_mult  = 1 + ups.get("coin_boost",0)*0.5
        extra_balls     = ups.get("multi_ball",0)
        self.shield_l   = ups.get("shield",0)
        self.shield_r   = ups.get("shield",0)

        self.score_l=0; self.score_r=0
        self.py_l=H//2; self.py_r=H//2
        self.keys={}; self.running=False; self.paused=False; self.game_over=False
        self.earned_coins=0; self.particles=[]

        self._build_static()
        self._reset_balls(extra_balls)
        self._bind_keys()
        mode_txt = {"pve":"1P vs KI","pvp":"2P Lokal","eve":"KI vs KI"}[mode]
        self._show_overlay("BEREIT?", f"{mode_txt}  /  {difficulty}", "SPACE  Starten")

    def _build_static(self):
        c = self.c
        for y in range(0, H, 4): c.create_line(0,y,W,y, fill="#0d0d1a", width=1)
        for y in range(0, H, 28): c.create_rectangle(W//2-2,y,W//2+2,y+14, fill=C_NET, outline="")
        if self.wall_bounce:
            c.create_line(0,8,W,8, fill=C_PURP, width=3)
            c.create_line(0,H-8,W,H-8, fill=C_PURP, width=3)
        self.pad_l_id = c.create_rectangle(0,0,0,0, fill=C_L, outline="")
        self.pad_r_id = c.create_rectangle(0,0,0,0, fill=C_R, outline="")
        self.sc_l_id  = c.create_text(W//4,   44, text="0", font=FONT_BIG, fill=C_L, anchor="center")
        self.sc_r_id  = c.create_text(W*3//4, 44, text="0", font=FONT_BIG, fill=C_R, anchor="center")
        self.sh_l_id  = c.create_text(90,   H-18, text="", font=FONT_XSM, fill=C_GREEN, anchor="w")
        self.sh_r_id  = c.create_text(W-90, H-18, text="", font=FONT_XSM, fill=C_GREEN, anchor="e")
        self.coin_live= c.create_text(W//2, H-18, text="Coins: +0", font=FONT_XSM, fill=C_GOLD, anchor="center")
        self._update_shields()

        self.ov_bg    = draw_rounded_rect(c, W//2-300, H//2-120, W//2+300, H//2+140,
                                          r=16, fill="#10101e", outline=C_DIM, width=2, tags="ov")
        self.ov_title = c.create_text(W//2, H//2-55, text="", font=("Courier",36,"bold"),
                                      fill=C_WHITE, anchor="center", tags="ov")
        self.ov_sub   = c.create_text(W//2, H//2+15, text="", font=FONT_SM,
                                      fill=C_DIM, anchor="center", tags="ov")
        self.ov_hint  = c.create_text(W//2, H//2+75, text="", font=FONT_XSM,
                                      fill=C_PURP, anchor="center", tags="ov")
        self._hide_overlay()

    def _update_shields(self):
        self.c.itemconfig(self.sh_l_id, text="SHIELD "*self.shield_l if self.shield_l else "")
        self.c.itemconfig(self.sh_r_id, text="SHIELD "*self.shield_r if self.shield_r else "")

    def _reset_balls(self, extra=0):
        if hasattr(self,"balls"):
            for b in self.balls: b.destroy()
        self.balls=[]
        for i in range(1+extra): self._spawn_ball(i*28)

    def _spawn_ball(self, delay=0):
        spd=self.ball_spd0
        dx=spd*(1 if random.random()>0.5 else -1)
        dy=spd*random.uniform(-0.55,0.55)
        b=Ball(self.c, W//2, H//2+random.randint(-60,60), dx, dy)
        b.frozen=delay; self.balls.append(b)

    def _bind_keys(self):
        self.app.bind("<KeyPress>",   self._on_press)
        self.app.bind("<KeyRelease>", self._on_release)

    def _on_press(self,ev):
        self.keys[ev.keysym]=True
        if ev.keysym=="space": self._toggle_pause()

    def _on_release(self,ev): self.keys[ev.keysym]=False

    def _toggle_pause(self):
        if self.game_over:
            self.app.unbind("<KeyPress>"); self.app.unbind("<KeyRelease>")
            self.app._show_main_menu(); return
        if not self.running:
            self._hide_overlay(); self.running=True; self._loop()
        elif self.paused:
            self.paused=False; self._hide_overlay(); self._loop()
        else:
            self.paused=True; self._show_overlay("PAUSE","","SPACE  Weiterspielen")

    def _show_overlay(self,title,sub,hint):
        c=self.c
        c.itemconfig(self.ov_title,text=title); c.itemconfig(self.ov_sub,text=sub)
        c.itemconfig(self.ov_hint,text=hint); c.tag_raise("ov")
        for item in (self.ov_bg,self.ov_title,self.ov_sub,self.ov_hint): c.itemconfig(item,state="normal")

    def _hide_overlay(self):
        for item in (self.ov_bg,self.ov_title,self.ov_sub,self.ov_hint): self.c.itemconfig(item,state="hidden")

    def _loop(self):
        if not self.running or self.paused or self.game_over: return
        self._move_paddles(); self._ai_move(); self._update_balls()
        self._update_particles(); self._draw_paddles()
        self.app.after(FPS, self._loop)

    def _move_paddles(self):
        spd=self.pad_spd
        if self.mode in ("pvp","pve"):
            if self.keys.get("w") or self.keys.get("W"): self.py_l-=spd
            if self.keys.get("s") or self.keys.get("S"): self.py_l+=spd
        if self.mode=="pvp":
            if self.keys.get("Up"):   self.py_r-=spd
            if self.keys.get("Down"): self.py_r+=spd
        hl=self.pad_h//2
        hr=(self.enemy_pad_h if self.mode=="pve" else self.pad_h)//2
        self.py_l=clamp(self.py_l,hl,H-hl); self.py_r=clamp(self.py_r,hr,H-hr)

    def _ai_move(self):
        react,max_spd,err = AI_PROFILES[self.difficulty]
        def target(side):
            pool=[b for b in self.balls if not b.frozen]
            if not pool: return H//2
            ap=[b for b in pool if (side=="l" and b.dx<0) or (side=="r" and b.dx>0)]
            pool=ap if ap else pool
            ref=80 if side=="l" else W-80
            b=min(pool, key=lambda b:abs(b.x-ref))
            return clamp(b.y+b.dy*react*8+random.uniform(-err,err),0,H)
        if self.mode in ("pve","eve"):
            d=target("r")-self.py_r; self.py_r+=clamp(d*react,-max_spd,max_spd)
            self.py_r=clamp(self.py_r,self.enemy_pad_h//2,H-self.enemy_pad_h//2)
        if self.mode=="eve":
            d=target("l")-self.py_l; self.py_l+=clamp(d*react,-max_spd,max_spd)
            self.py_l=clamp(self.py_l,self.pad_h//2,H-self.pad_h//2)

    def _draw_paddles(self):
        c=self.c; lx=30
        c.coords(self.pad_l_id,lx,self.py_l-self.pad_h//2,lx+PAD_W,self.py_l+self.pad_h//2)
        rx=W-30-PAD_W; ph=self.enemy_pad_h if self.mode=="pve" else self.pad_h
        c.coords(self.pad_r_id,rx,self.py_r-ph//2,rx+PAD_W,self.py_r+ph//2)

    def _update_balls(self):
        dead=[]
        for b in self.balls:
            if b.frozen>0: b.frozen-=1; b.draw(); continue
            b.x+=b.dx; b.y+=b.dy
            top=8 if self.wall_bounce else 0; bot=H-8 if self.wall_bounce else H
            if b.y-BALL_R<=top:   b.y=top+BALL_R;   b.dy=abs(b.dy);  self._particles(b.x,b.y,C_PURP)
            if b.y+BALL_R>=bot:   b.y=bot-BALL_R;   b.dy=-abs(b.dy); self._particles(b.x,b.y,C_PURP)
            self._check_paddle(b)
            if b.x<-30:
                if self.shield_r>0: self.shield_r-=1; b.x=W//2; b.dx=abs(b.dx); self._update_shields()
                else: self.score_r+=1; self._coin(); self.c.itemconfig(self.sc_r_id,text=str(self.score_r)); self._particles(0,b.y,C_R,25); dead.append(b)
            elif b.x>W+30:
                if self.shield_l>0: self.shield_l-=1; b.x=W//2; b.dx=-abs(b.dx); self._update_shields()
                else: self.score_l+=1; self._coin(); self.c.itemconfig(self.sc_l_id,text=str(self.score_l)); self._particles(W,b.y,C_L,25); dead.append(b)
            else: b.draw()
        for b in dead:
            b.destroy(); self.balls.remove(b)
            if not self.game_over:
                self._check_win()
                if not self.game_over: self._spawn_ball()

    def _check_paddle(self,b):
        lx1,lx2=30,30+PAD_W
        if b.dx<0 and lx1<=b.x-BALL_R<=lx2+4 and self.py_l-self.pad_h//2<=b.y<=self.py_l+self.pad_h//2:
            spd=min(math.hypot(b.dx,b.dy)+0.35,22); rel=(b.y-self.py_l)/(self.pad_h/2)
            b.dx=spd; b.dy=spd*rel*0.95; b.x=lx2+BALL_R+1; self._particles(lx2,b.y,C_L)
        ph=self.enemy_pad_h if self.mode=="pve" else self.pad_h
        rx1,rx2=W-30-PAD_W,W-30
        if b.dx>0 and rx1-4<=b.x+BALL_R<=rx2 and self.py_r-ph//2<=b.y<=self.py_r+ph//2:
            spd=min(math.hypot(b.dx,b.dy)+0.35,22); rel=(b.y-self.py_r)/(ph/2)
            b.dx=-spd; b.dy=spd*rel*0.95; b.x=rx1-BALL_R-1; self._particles(rx1,b.y,C_R)

    def _coin(self):
        earned=max(1,int(self.coin_mult))
        self.app.save["coins"]+=earned; self.earned_coins+=earned
        save_data(self.app.save)
        self.c.itemconfig(self.coin_live,text=f"Coins: +{self.earned_coins}")

    def _check_win(self):
        if self.score_l>=MAX_SCORE or self.score_r>=MAX_SCORE:
            self.game_over=True; self.running=False
            w="LINKS gewinnt!" if self.score_l>=MAX_SCORE else "RECHTS gewinnt!"
            self._show_overlay(w,f"{self.score_l}  :  {self.score_r}   |   +{self.earned_coins} Coins","SPACE  Zum Hauptmenue")

    def _particles(self,x,y,col,n=10):
        for _ in range(n):
            a=random.uniform(0,2*math.pi); spd=random.uniform(2,7)
            self.particles.append({"id":self.c.create_oval(x-3,y-3,x+3,y+3,fill=col,outline=""),
                                    "x":x,"y":y,"dx":math.cos(a)*spd,"dy":math.sin(a)*spd,
                                    "life":random.randint(8,18)})

    def _update_particles(self):
        alive=[]
        for p in self.particles:
            p["x"]+=p["dx"]; p["y"]+=p["dy"]; p["dy"]+=0.4; p["life"]-=1
            if p["life"]>0:
                r=max(1,p["life"]//4)
                self.c.coords(p["id"],p["x"]-r,p["y"]-r,p["x"]+r,p["y"]+r); alive.append(p)
            else: self.c.delete(p["id"])
        self.particles=alive

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
