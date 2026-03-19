"""
╔══════════════════════════════════════════════════════╗
║    BUSINESS TYCOON PRO  —  by Michael (其米）         ║
║    Läuft mit Standard-Python (tkinter, kein pip!)    ║
║    python business_tycoon.py                         ║
╚══════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import random
import sys

# ─────────────────────────────────────────────────────
#  FARBEN
# ─────────────────────────────────────────────────────
BG      = "#0a0e1a"
PANEL   = "#111827"
PANEL2  = "#1f2937"
BORDER  = "#374151"
ACCENT  = "#3b82f6"
GREEN   = "#10b981"
RED     = "#ef4444"
YELLOW  = "#f59e0b"
CYAN    = "#06b6d4"
GOLD    = "#fbbf24"
WHITE   = "#f0f0f8"
MUTED   = "#6b7280"
ORANGE  = "#f97316"
PURPLE  = "#8b5cf6"
DARK_GREEN = "#0f2820"
DARK_RED   = "#3a1515"
DARK_YELLOW= "#3a2e0a"

# ─────────────────────────────────────────────────────
#  HILFSFUNKTIONEN
# ─────────────────────────────────────────────────────
def fmt(n: float) -> str:
    n = float(n)
    if abs(n) >= 1e9: return f"{n/1e9:.2f} Mrd €"
    if abs(n) >= 1e6: return f"{n/1e6:.2f} Mio €"
    if abs(n) >= 1e3: return f"{n/1e3:.1f}k €"
    return f"{n:,.0f} €".replace(",", ".")

# ─────────────────────────────────────────────────────
#  KATALOGE
# ─────────────────────────────────────────────────────
PROP_CATALOG = [
    {"id":"flat",   "name":"Kleine Wohnung",  "icon":"🏠", "price":75000,    "rent":550,    "maint":90,    "lvl_max":5},
    {"id":"house",  "name":"Einfamilienhaus", "icon":"🏡", "price":240000,   "rent":1300,   "maint":270,   "lvl_max":5},
    {"id":"condo",  "name":"Luxus-Penthouse", "icon":"🏙", "price":650000,   "rent":4000,   "maint":600,   "lvl_max":5},
    {"id":"office", "name":"Bürogebäude",     "icon":"🏢", "price":1200000,  "rent":9000,   "maint":1400,  "lvl_max":5},
    {"id":"mall",   "name":"Einkaufszentrum", "icon":"🛍", "price":3000000,  "rent":25000,  "maint":3500,  "lvl_max":5},
    {"id":"hotel",  "name":"Luxus-Hotel",     "icon":"🏨", "price":5000000,  "rent":40000,  "maint":6000,  "lvl_max":5},
]
COMP_CATALOG = [
    {"id":"cafe",   "name":"Café / Kiosk",       "icon":"☕", "price":15000,    "profit":280,    "maint":40,    "risk":0.05, "lvl_max":8},
    {"id":"craft",  "name":"Handwerksbetrieb",   "icon":"🔨", "price":80000,    "profit":1100,   "maint":180,   "risk":0.05, "lvl_max":8},
    {"id":"retail", "name":"Einzelhandel",       "icon":"🛒", "price":200000,   "profit":2500,   "maint":400,   "risk":0.08, "lvl_max":8},
    {"id":"tech",   "name":"Software-Startup",   "icon":"💻", "price":500000,   "profit":7000,   "maint":800,   "risk":0.12, "lvl_max":8},
    {"id":"factory","name":"Fabrik",             "icon":"🏭", "price":1500000,  "profit":18000,  "maint":2800,  "risk":0.06, "lvl_max":8},
    {"id":"media",  "name":"Medienkonzern",      "icon":"📺", "price":4000000,  "profit":50000,  "maint":8000,  "risk":0.10, "lvl_max":8},
    {"id":"pharma", "name":"Pharmaunternehmen",  "icon":"💊", "price":8000000,  "profit":110000, "maint":15000, "risk":0.14, "lvl_max":8},
    {"id":"ibank",  "name":"Investmentbank",     "icon":"🏦", "price":20000000, "profit":300000, "maint":40000, "risk":0.18, "lvl_max":8},
]
STOCK_CATALOG = [
    {"sid":"tg",  "name":"TechGiant",    "price":150.0, "vol":0.13, "div":0.005, "sector":"Tech"},
    {"sid":"ac",  "name":"AutoCorp",     "price":85.0,  "vol":0.09, "div":0.018, "sector":"Auto"},
    {"sid":"ec",  "name":"EnergyCo",     "price":110.0, "vol":0.07, "div":0.022, "sector":"Energie"},
    {"sid":"bg",  "name":"BankGroup",    "price":65.0,  "vol":0.11, "div":0.012, "sector":"Finanzen"},
    {"sid":"ph",  "name":"PharmaHealth", "price":200.0, "vol":0.10, "div":0.008, "sector":"Gesundheit"},
    {"sid":"re",  "name":"RealEstCorp",  "price":90.0,  "vol":0.08, "div":0.025, "sector":"Immobilien"},
    {"sid":"ai",  "name":"AI-Ventures",  "price":350.0, "vol":0.25, "div":0.001, "sector":"Tech"},
    {"sid":"food","name":"FoodChain",    "price":45.0,  "vol":0.06, "div":0.030, "sector":"Konsum"},
]
PHASES = {
    "BOOM":          {"label":"Boom",           "col":GREEN,  "stk":+.04, "rent":+.02, "profit":+.05},
    "STABLE":        {"label":"Stabil",         "col":CYAN,   "stk": .00, "rent": .00, "profit": .00},
    "RECESSION":     {"label":"Rezession",      "col":YELLOW, "stk":-.03, "rent":-.01, "profit":-.03},
    "DEPRESSION":    {"label":"Depression",     "col":RED,    "stk":-.08, "rent":-.03, "profit":-.08},
    "STAGFLATION":   {"label":"Stagflation",    "col":ORANGE, "stk":-.02, "rent":+.01, "profit":-.04},
    "HYPERINFLATION":{"label":"Hyperinflation", "col":"#ec4899","stk":+.01,"rent":+.06,"profit":-.06},
}
TENANT_TYPES = [
    {"name":"Privat-Mieter",  "bonus": 0.00, "dmg":0.03, "months":12},
    {"name":"Student",        "bonus":-0.10, "dmg":0.10, "months":6},
    {"name":"Firmenkunde",    "bonus":+0.25, "dmg":0.05, "months":24},
    {"name":"Luxusmieter",    "bonus":+0.40, "dmg":0.04, "months":18},
    {"name":"Sozialmieter",   "bonus":-0.20, "dmg":0.01, "months":36},
]
ACHIEVEMENTS = [
    ("first",    "Erster Kauf",        "Erste Immobilie oder Firma gekauft",
     lambda g: len(g.props)+len(g.comps) >= 1),
    ("millionaire","Millionär",        "Nettovermögen > 1 Mio €",
     lambda g: g.net_worth() >= 1_000_000),
    ("tenmio",  "10-Millionär",        "Nettovermögen > 10 Mio €",
     lambda g: g.net_worth() >= 10_000_000),
    ("landlord","Vermieter",           "3 oder mehr Immobilien besitzen",
     lambda g: len(g.props) >= 3),
    ("tycoon",  "Tycoon",             "5 oder mehr Unternehmen besitzen",
     lambda g: len(g.comps) >= 5),
    ("debtfree","Schuldenfrei",        "Alle Schulden getilgt",
     lambda g: g.loan == 0 and len(g.nw_hist) > 3),
    ("investor","Investor",            "Aktienportfolio > 200k €",
     lambda g: g.stock_value() >= 200_000),
    ("diversify","Diversifiziert",     "In Immo, Firmen UND Aktien investiert",
     lambda g: len(g.props)>0 and len(g.comps)>0 and g.stock_value()>0),
    ("survivor","Krisenüberlebender",  "Depression überlebt",
     lambda g: getattr(g, "_survived_dep", False)),
    ("legend",  "Legende",            "Nettovermögen > 100 Mio €",
     lambda g: g.net_worth() >= 100_000_000),
    ("fullhouse","Vollvermieter",      "Alle Immo vermietet (mind. 3)",
     lambda g: len(g.props)>=3 and all(not p["vacant"] for p in g.props)),
    ("premium", "Premium-Vermieter",  "Luxusmieter in einer Immobilie",
     lambda g: any(p.get("tenant")==3 for p in g.props)),
]
TIPS = {
    "BOOM":          "Aktien kaufen! Firmengewinne steigen. Immowert steigt.",
    "STABLE":        "Stabile Phase – ideal für Schuldenabbau und Sparen.",
    "RECESSION":     "Vorsicht! ETFs sicherer als Einzelaktien.",
    "DEPRESSION":    "Bargeld halten. Kein unnötiges Risiko eingehen!",
    "STAGFLATION":   "Sachwerte (Immobilien) schützen vor Inflation.",
    "HYPERINFLATION":"Immobilien kaufen! Bargeld verliert rasant an Wert.",
}

# ─────────────────────────────────────────────────────
#  SPIELZUSTAND
# ─────────────────────────────────────────────────────
class GS:
    def __init__(self, name="Investor"):
        self.name      = name
        self.cash      = 50_000.0
        self.loan      = 0.0
        self.savings   = 0.0
        self.sav_rate  = 0.0035
        self.loan_rate = 0.006
        self.props     = []
        self.comps     = []
        self.stocks    = {}
        self.etf       = 0.0
        self.stock_data = {
            s["sid"]: {"name":s["name"],"price":s["price"],"vol":s["vol"],
                       "div":s["div"],"sector":s["sector"],"hist":[s["price"]]}
            for s in STOCK_CATALOG
        }
        self.etf_price = 100.0
        self.etf_hist  = [100.0]
        self.month     = 1
        self.year      = 2024
        self.phase     = "STABLE"
        self.phase_dur = 8
        self.base_rate = 5.0
        self.inflation = 0.002
        self.gdp       = 2.0
        self.unemp     = 5.0
        self.sentiment = 50.0
        self.reputation= 50
        self.tax_rate  = 0.25
        self.achiev_done = set()
        self.log       = []
        self.news      = []
        self.nw_hist   = []
        self.cf_hist   = []
        self._survived_dep = False

    def net_worth(self):
        v = self.cash + self.savings
        for p in self.props: v += p["price"]
        for c in self.comps: v += c["val"]
        for sid, qty in self.stocks.items():
            v += qty * self.stock_data[sid]["price"]
        v += self.etf * self.etf_price
        v -= self.loan
        return v

    def stock_value(self):
        v = sum(qty * self.stock_data[sid]["price"]
                for sid, qty in self.stocks.items() if qty > 0)
        return v + self.etf * self.etf_price

    def monthly_income(self):
        i  = sum(p["rent"] for p in self.props if not p["vacant"])
        i += sum(c["profit"] for c in self.comps)
        for sid, qty in self.stocks.items():
            if qty > 0:
                s = self.stock_data[sid]
                i += qty * s["price"] * s["div"] / 12.0
        i += self.etf * self.etf_price * 0.002 / 12.0
        i += self.savings * self.sav_rate
        return i

    def monthly_expenses(self):
        e  = sum(p["maint"] for p in self.props)
        e += sum(c["maint"] for c in self.comps)
        e += self.loan * (self.loan_rate + self.base_rate / 100.0 / 12.0)
        return e

    def add_log(self, msg, kind="info"):
        self.log.insert(0, (msg, kind))
        if len(self.log) > 80: self.log.pop()

    def add_news(self, msg):
        self.news.insert(0, msg)
        if len(self.news) > 20: self.news.pop()

# ─────────────────────────────────────────────────────
#  SPIELLOGIK
# ─────────────────────────────────────────────────────
def make_prop(row):
    return {
        "id": row["id"], "name": row["name"], "icon": row["icon"],
        "price":     float(row["price"]),
        "base_rent": float(row["rent"]),
        "rent":      float(row["rent"]),
        "maint":     float(row["maint"]),
        "level": 1, "lvl_max": row["lvl_max"],
        "vacant":  True, "listed": False,
        "tenant":  None, "contract_left": 0,
        "rent_hist": [],
    }

def make_comp(row):
    return {
        "id": row["id"], "name": row["name"], "icon": row["icon"],
        "base_price":  float(row["price"]),
        "val":         float(row["price"]),
        "base_profit": float(row["profit"]),
        "profit":      float(row["profit"]),
        "maint":       float(row["maint"]),
        "risk":        row["risk"],
        "level": 1, "lvl_max": row["lvl_max"],
    }

def tick(gs: GS):
    gs.month += 1
    if gs.month > 12:
        gs.month = 1
        gs.year += 1
        _year_end(gs)

    _update_economy(gs)
    _update_markets(gs)

    ph = PHASES[gs.phase]
    income = 0.0
    expenses = 0.0

    for p in gs.props:
        if p["tenant"] is not None and p["contract_left"] > 0:
            p["contract_left"] -= 1
            if p["contract_left"] == 0:
                tname = TENANT_TYPES[p["tenant"]]["name"]
                gs.add_log(f"Mietvertrag abgelaufen: {p['name']} ({tname})", "warn")
                p["tenant"] = None
                p["vacant"] = True
                p["listed"] = False

        if p["listed"] and p["vacant"]:
            chance = {"BOOM":0.55,"STABLE":0.40,"RECESSION":0.25,
                      "DEPRESSION":0.10,"STAGFLATION":0.20,"HYPERINFLATION":0.15}.get(gs.phase, 0.30)
            if random.random() < chance:
                weights = [4, 3, 2, 1, 2]
                ti = random.choices(range(len(TENANT_TYPES)), weights=weights)[0]
                t = TENANT_TYPES[ti]
                p["tenant"]        = ti
                p["vacant"]        = False
                p["contract_left"] = t["months"]
                p["rent"]          = p["base_rent"] * (1 + t["bonus"])
                gs.add_log(f"Neuer Mieter: {t['name']} in {p['name']} ({t['months']} Monate)", "good")

        if not p["vacant"] and p["tenant"] is not None:
            dmg_risk = TENANT_TYPES[p["tenant"]]["dmg"]
            if random.random() < dmg_risk * 0.4:
                dmg = p["maint"] * (0.5 + random.random())
                expenses += dmg
                gs.add_log(f"Mieterschaden in {p['name']}: -{fmt(dmg)}", "bad")

        rent = p["rent"] * (1 + ph["rent"]) if not p["vacant"] else 0.0
        income   += rent
        expenses += p["maint"]
        p["rent_hist"].append(round(rent))
        if len(p["rent_hist"]) > 24: p["rent_hist"].pop(0)
        p["price"]     *= 1 + gs.inflation*0.7 + (0.004 if gs.phase=="BOOM" else -0.001)
        p["base_rent"] *= 1 + gs.inflation*0.35
        if not p["vacant"]:
            p["rent"] *= 1 + gs.inflation*0.35

    rep_bonus = (gs.reputation - 50) / 2000.0
    for c in gs.comps:
        eff = c["base_profit"] * (1 + ph["profit"] + rep_bonus)
        c["profit"] = max(0.0, eff)
        if random.random() < c["risk"] * 0.35:
            dmg = c["profit"] * (0.15 + random.random()*0.25)
            expenses += dmg
            gs.add_log(f"Schadenfall bei {c['name']}: -{fmt(dmg)}", "bad")
        income   += c["profit"]
        expenses += c["maint"]
        c["val"]         *= 1 + gs.inflation*0.4
        c["base_profit"] *= 1 + gs.inflation*0.2

    eff_rate = gs.loan_rate + gs.base_rate/100.0/12.0
    expenses += gs.loan * eff_rate
    income   += gs.savings * gs.sav_rate

    for sid, qty in gs.stocks.items():
        if qty > 0:
            s = gs.stock_data[sid]
            income += qty * s["price"] * s["div"] / 12.0
    income += gs.etf * gs.etf_price * 0.002 / 12.0

    _random_events(gs)

    gross = income - expenses
    tax   = max(0.0, gross * gs.tax_rate)
    expenses += tax

    cf = income - expenses
    gs.cash += cf
    gs.cf_hist.append(cf)
    gs.nw_hist.append(gs.net_worth())
    if len(gs.cf_hist) > 24: gs.cf_hist.pop(0)
    if len(gs.nw_hist) > 24: gs.nw_hist.pop(0)

    gs.inflation = 0.001 + random.random()*0.004
    if gs.phase == "HYPERINFLATION": gs.inflation *= 4

    if gs.phase == "DEPRESSION" and gs.cash > 0:
        gs._survived_dep = True

    if gs.cash < -50_000 and gs.loan > gs.net_worth()*2:
        return "bankrott"
    return None

def _year_end(gs):
    gs.add_news(f"Jahresabschluss {gs.year-1}: NV {fmt(gs.net_worth())}")
    if gs.net_worth() > 2_000_000:
        wt = (gs.net_worth() - 2_000_000) * 0.005
        gs.cash -= wt
        gs.add_log(f"Vermögenssteuer: -{fmt(wt)}", "bad")

def _update_economy(gs):
    gs.phase_dur -= 1
    if gs.phase_dur <= 0:
        prev = gs.phase
        r = random.random()
        if   r < 0.07: gs.phase, gs.phase_dur = "DEPRESSION",     random.randint(2,5)
        elif r < 0.22: gs.phase, gs.phase_dur = "RECESSION",      random.randint(3,7)
        elif r < 0.28: gs.phase, gs.phase_dur = "STAGFLATION",    random.randint(2,4)
        elif r < 0.30: gs.phase, gs.phase_dur = "HYPERINFLATION", random.randint(1,3)
        elif r < 0.65: gs.phase, gs.phase_dur = "STABLE",         random.randint(5,10)
        else:          gs.phase, gs.phase_dur = "BOOM",            random.randint(3,6)
        if gs.phase != prev:
            label = PHASES[gs.phase]["label"]
            gs.add_news(f"Wirtschaftswechsel: {label}")
            kind = "good" if gs.phase=="BOOM" else ("bad" if "DEPRESS" in gs.phase else "warn")
            gs.add_log(f"Wirtschaft: {label}", kind)

    delta = {"BOOM":+.06,"STABLE":0,"RECESSION":-.1,"DEPRESSION":-.15,"STAGFLATION":0,"HYPERINFLATION":0}
    gs.base_rate = max(0, min(15, gs.base_rate + delta.get(gs.phase,0)))
    gs.loan_rate = 0.004 + gs.base_rate/100.0/12.0
    gs.gdp   += {"BOOM":.15,"STABLE":0,"RECESSION":-.2,"DEPRESSION":-.4,
                 "STAGFLATION":-.1,"HYPERINFLATION":-.15}.get(gs.phase,0)
    gs.unemp += {"BOOM":-.1,"STABLE":0,"RECESSION":.25,"DEPRESSION":.5,
                 "STAGFLATION":.1,"HYPERINFLATION":.1}.get(gs.phase,0)
    gs.gdp   = max(-15, min(12, gs.gdp))
    gs.unemp = max(1,   min(30, gs.unemp))
    gs.sentiment += (random.random()-.48)*8
    gs.sentiment  = max(0, min(100, gs.sentiment))

def _update_markets(gs):
    ph  = PHASES[gs.phase]
    sent= (gs.sentiment-50)/5000.0
    sector_bonus = {
        "Tech":("BOOM",.015), "Energie":("STAGFLATION",.02),
        "Finanzen":("DEPRESSION",-.025), "Gesundheit":(None,.005), "Konsum":(None,.003)
    }
    for sid, s in gs.stock_data.items():
        se = 0.0
        for sec,(cond,val) in sector_bonus.items():
            if s["sector"]==sec and (cond is None or gs.phase==cond):
                se = val
        chg = (random.random()-.5)*2*s["vol"] + ph["stk"] + se + sent
        s["price"] = max(0.5, s["price"]*(1+chg))
        s["hist"].append(round(s["price"],2))
        if len(s["hist"]) > 40: s["hist"].pop(0)

    etf_chg = (random.random()-.48)*.045 + ph["stk"]*.5
    gs.etf_price = max(5, gs.etf_price*(1+etf_chg))
    gs.etf_hist.append(round(gs.etf_price,2))
    if len(gs.etf_hist) > 40: gs.etf_hist.pop(0)

def _random_events(gs):
    events = [
        (0.025, lambda: _ev_fire(gs)),
        (0.020, lambda: _ev_vacancy(gs)),
        (0.015, lambda: _ev_lawsuit(gs)),
        (0.022, lambda: _ev_subsidy(gs)),
        (0.008, lambda: _ev_crash(gs)),
        (0.008, lambda: _ev_rally(gs)),
        (0.016, lambda: _ev_bad_press(gs)),
        (0.016, lambda: _ev_good_press(gs)),
        (0.010, lambda: _ev_tax_audit(gs)),
        (0.018, lambda: _ev_infra(gs)),
        (0.010, lambda: _ev_regulation(gs)),
    ]
    for prob, fn in events:
        if random.random() < prob: fn()

def _ev_fire(gs):
    if not gs.props: return
    p = random.choice(gs.props)
    dmg = p["price"]*0.06; gs.cash -= dmg; p["price"] -= dmg
    gs.add_log(f"Feuer in {p['name']}! -{fmt(dmg)}", "bad")
    gs.add_news("Feuer in der Innenstadt!")

def _ev_vacancy(gs):
    occupied = [p for p in gs.props if not p["vacant"]]
    if not occupied: return
    p = random.choice(occupied)
    tname = TENANT_TYPES[p["tenant"]]["name"] if p["tenant"] is not None else "Mieter"
    p["tenant"] = None; p["vacant"] = True; p["contract_left"] = 0
    gs.add_log(f"{tname} ausgezogen: {p['name']} jetzt leer", "bad")

def _ev_lawsuit(gs):
    if not gs.comps: return
    c = random.choice(gs.comps)
    pen = c["val"]*0.07; gs.cash -= pen
    gs.add_log(f"Klage vs {c['name']}: -{fmt(pen)}", "bad")
    gs.add_news("Unternehmen verklagt!")

def _ev_subsidy(gs):
    amt = 8_000 + random.random()*45_000; gs.cash += amt
    gs.add_log(f"Staatliche Förderung: +{fmt(amt)}", "good")

def _ev_crash(gs):
    for s in gs.stock_data.values(): s["price"] *= 0.80+random.random()*0.10
    gs.add_log("Marktcrash! Alle Aktien stark gefallen.", "bad")
    gs.add_news("CRASH: Börsenpanik!")

def _ev_rally(gs):
    for s in gs.stock_data.values(): s["price"] *= 1.10+random.random()*0.10
    gs.add_log("Bullenmarkt! Aktien stark gestiegen.", "good")
    gs.add_news("Börsenrekord! Märkte feiern Allzeithoch.")

def _ev_bad_press(gs):
    gs.reputation = max(0, gs.reputation-10)
    gs.add_log("Schlechte Presse: Ruf -10", "bad")

def _ev_good_press(gs):
    gs.reputation = min(100, gs.reputation+8)
    gs.add_log("Positiver Artikel: Ruf +8", "good")

def _ev_tax_audit(gs):
    amt = gs.cash*0.04; gs.cash -= amt
    gs.add_log(f"Sondersteuer-Prüfung: -{fmt(amt)}", "bad")

def _ev_infra(gs):
    if not gs.props: return
    p = random.choice(gs.props); p["price"] *= 1.10
    gs.add_log(f"Stadtentwicklung: {p['name']} +10%", "good")

def _ev_regulation(gs):
    for c in gs.comps:
        c["profit"] *= 0.85; c["base_profit"] *= 0.85
    gs.add_log("Neue Regulierung: Firmengewinne -15%", "bad")
    gs.add_news("Regierung beschließt neue Unternehmensauflagen.")

# ─────────────────────────────────────────────────────
#  MINI SPARKLINE (auf Canvas zeichnen)
# ─────────────────────────────────────────────────────
def draw_sparkline(canvas, hist, x, y, w, h, color=None):
    if len(hist) < 2: return
    mn, mx = min(hist), max(hist)
    if mx == mn: mx = mn + 1
    col = color or (GREEN if hist[-1] >= hist[0] else RED)
    pts = []
    for i, v in enumerate(hist):
        px = x + int(i/(len(hist)-1)*w)
        py = y + h - int((v-mn)/(mx-mn)*h)
        pts.append(px); pts.append(py)
    if len(pts) >= 4:
        canvas.create_line(*pts, fill=col, width=2, smooth=True)

# ─────────────────────────────────────────────────────
#  HAUPT-APP
# ─────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Tycoon Pro — by Michael (其米）")
        self.root.configure(bg=BG)
        self.root.geometry("1280x760")
        self.root.minsize(900, 600)

        self.gs          = None
        self.speed_ms    = 2000
        self.paused      = False
        self.current_tab = 0
        self._tick_job   = None
        self._news_offset= 0
        self._news_job   = None
        self._ach_popup_job = None

        self._build_name_screen()

    # ══════════════════════════════════════════════════
    #  NAME SCREEN
    # ══════════════════════════════════════════════════
    def _build_name_screen(self):
        self.name_frame = tk.Frame(self.root, bg=BG)
        self.name_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        center = tk.Frame(self.name_frame, bg=BG)
        center.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(center, text="Business Tycoon Pro", font=("Arial", 36, "bold"),
                 fg=GOLD, bg=BG).pack(pady=(0,4))
        tk.Label(center, text="by Michael (其米）", font=("Arial", 13),
                 fg=MUTED, bg=BG).pack(pady=(0,22))
        tk.Label(center, text="Wie heißt du?", font=("Arial", 14),
                 fg=WHITE, bg=BG).pack(pady=(0,8))

        self.name_var = tk.StringVar()
        entry = tk.Entry(center, textvariable=self.name_var,
                         font=("Arial", 16), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat",
                         justify="center", width=22)
        entry.pack(ipady=8, pady=(0,16))
        entry.focus_set()
        entry.bind("<Return>", lambda e: self._start_game())

        btn = tk.Button(center, text="Spielen", font=("Arial", 15, "bold"),
                        bg=GREEN, fg=BG, bd=0, relief="flat",
                        padx=36, pady=10, cursor="hand2",
                        command=self._start_game)
        btn.pack()

    def _start_game(self):
        name = self.name_var.get().strip() or "Investor"
        self.gs = GS(name)
        self.gs.add_log(f"Willkommen, {name}! Startkapital: {fmt(self.gs.cash)}", "info")
        self.gs.add_news("Spielstart! Viel Erfolg beim Investieren.")
        self.name_frame.destroy()
        self._build_game_ui()
        self._schedule_tick()
        self._scroll_news()

    # ══════════════════════════════════════════════════
    #  GAME UI LAYOUT
    # ══════════════════════════════════════════════════
    def _build_game_ui(self):
        self.game_frame = tk.Frame(self.root, bg=BG)
        self.game_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ── Topbar ──
        self.topbar = tk.Frame(self.game_frame, bg=PANEL, height=44)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)
        self._build_topbar()

        # ── Tabbar ──
        self.tabbar = tk.Frame(self.game_frame, bg=PANEL, height=32)
        self.tabbar.pack(fill="x", side="top")
        self.tabbar.pack_propagate(False)
        self._build_tabbar()

        # ── Newsbar ──
        self.newsbar = tk.Frame(self.game_frame, bg=PANEL, height=22)
        self.newsbar.pack(fill="x", side="bottom")
        self.newsbar.pack_propagate(False)
        self.news_canvas = tk.Canvas(self.newsbar, bg=PANEL, height=22,
                                     highlightthickness=0)
        self.news_canvas.pack(fill="both", expand=True)

        # ── Middle (sidebar + content) ──
        middle = tk.Frame(self.game_frame, bg=BG)
        middle.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(middle, bg=PANEL, width=188)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Separator
        tk.Frame(middle, bg=BORDER, width=1).pack(side="left", fill="y")

        # Content
        self.content_frame = tk.Frame(middle, bg=BG)
        self.content_frame.pack(fill="both", expand=True)

        # Achievement popup label
        self.ach_popup = tk.Label(self.root, text="", bg="#502884", fg=GOLD,
                                  font=("Arial", 11, "bold"), bd=1,
                                  relief="solid", justify="left", padx=10, pady=6)

        self._render_tab()

    # ── TOPBAR ──
    def _build_topbar(self):
        tk.Label(self.topbar, text="Business Tycoon Pro",
                 font=("Arial", 13, "bold"), fg=GOLD, bg=PANEL).pack(side="left", padx=10)

        self.tb_vars = {}
        stats = [
            ("cash",  "Bargeld"),
            ("nw",    "Nettoverm."),
            ("date",  ""),
            ("loan",  "Schulden"),
            ("rep",   "Ruf"),
        ]
        for key, label in stats:
            f = tk.Frame(self.topbar, bg=PANEL2, padx=8, pady=2)
            f.pack(side="left", padx=3, pady=6)
            if label:
                tk.Label(f, text=label+":", font=("Arial", 9), fg=MUTED, bg=PANEL2).pack(side="left")
            var = tk.StringVar(value="—")
            lbl = tk.Label(f, textvariable=var, font=("Arial", 9, "bold"),
                           fg=CYAN, bg=PANEL2)
            lbl.pack(side="left", padx=(3,0))
            self.tb_vars[key] = (var, lbl)

        # Speed
        spd_frame = tk.Frame(self.topbar, bg=PANEL)
        spd_frame.pack(side="right", padx=6)
        self.pause_btn = tk.Button(spd_frame, text="Pause",
                                   font=("Arial", 10, "bold"),
                                   bg=GREEN, fg=BG, bd=0, relief="flat",
                                   padx=10, pady=2, cursor="hand2",
                                   command=self._toggle_pause)
        self.pause_btn.pack(side="right", padx=(4,0))

        self.spd_btns = {}
        for ms, lbl in [(2000,"1x"),(800,"3x"),(300,"10x")]:
            b = tk.Button(spd_frame, text=lbl, font=("Arial", 10),
                          bg=ACCENT if ms==2000 else PANEL2,
                          fg=WHITE, bd=0, relief="flat",
                          padx=8, pady=2, cursor="hand2",
                          command=lambda m=ms: self._set_speed(m))
            b.pack(side="left", padx=2)
            self.spd_btns[ms] = b

    def _update_topbar(self):
        gs = self.gs
        nw = gs.net_worth()
        data = {
            "cash":  (fmt(gs.cash),  GREEN if gs.cash >= 0 else RED),
            "nw":    (fmt(nw),       CYAN),
            "date":  (f"{gs.month:02d}.{gs.year}", CYAN),
            "loan":  (fmt(gs.loan),  GREEN if gs.loan == 0 else RED),
            "rep":   (str(int(gs.reputation)), GREEN if gs.reputation >= 50 else RED),
        }
        for key, (val, col) in data.items():
            var, lbl = self.tb_vars[key]
            var.set(val)
            lbl.config(fg=col)

    # ── TABBAR ──
    def _build_tabbar(self):
        # Spacer for sidebar width
        tk.Frame(self.tabbar, bg=PANEL, width=188).pack(side="left")
        self.tab_buttons = []
        tabs = ["Dashboard", "Wirtschaft", "Aktien", "Erfolge", "Log"]
        for i, name in enumerate(tabs):
            b = tk.Button(self.tabbar, text=name,
                          font=("Arial", 10),
                          bg=PANEL, fg=ACCENT if i==0 else MUTED,
                          bd=0, relief="flat", padx=12,
                          cursor="hand2",
                          command=lambda idx=i: self._switch_tab(idx))
            b.pack(side="left")
            self.tab_buttons.append(b)

    def _switch_tab(self, idx):
        self.current_tab = idx
        for i, b in enumerate(self.tab_buttons):
            b.config(fg=ACCENT if i==idx else MUTED)
        self._render_tab()

    # ── SIDEBAR ──
    def _build_sidebar(self):
        sections = [
            (None, "IMMOBILIEN"),
            ("buy_prop",  "  Immo kaufen"),
            ("sell_prop", "  Immo verkaufen"),
            ("upg_prop",  "  Renovieren"),
            ("rent_prop", "  Vermieten"),
            (None, "UNTERNEHMEN"),
            ("buy_comp",  "  Firma gründen"),
            ("sell_comp", "  Firma verkaufen"),
            ("upg_comp",  "  Firma erweitern"),
            (None, "FINANZEN"),
            ("loan",      "  Kredit aufnehmen"),
            ("repay",     "  Kredit tilgen"),
            ("savings",   "  Festgeld"),
            ("buy_etf",   "  ETF kaufen"),
        ]
        self.sb_btns = {}
        for key, label in sections:
            if key is None:
                tk.Label(self.sidebar, text=label, font=("Arial", 8),
                         fg=MUTED, bg=PANEL, anchor="w"
                         ).pack(fill="x", padx=6, pady=(8,1))
            else:
                b = tk.Button(self.sidebar, text=label,
                              font=("Arial", 11), bg=PANEL2, fg=WHITE,
                              bd=0, relief="flat", anchor="w",
                              padx=6, pady=5, cursor="hand2",
                              command=lambda k=key: self._open_modal(k))
                b.pack(fill="x", padx=4, pady=1)
                self.sb_btns[key] = b

    def _update_sidebar(self):
        # Highlight "Vermieten" wenn Leerstand
        if "rent_prop" in self.sb_btns:
            has_vacant = any(p["vacant"] for p in self.gs.props)
            b = self.sb_btns["rent_prop"]
            if has_vacant:
                b.config(bg=DARK_YELLOW, fg=YELLOW)
            else:
                b.config(bg=PANEL2, fg=WHITE)

    # ══════════════════════════════════════════════════
    #  CONTENT TABS
    # ══════════════════════════════════════════════════
    def _render_tab(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        tabs = [self._tab_dashboard, self._tab_economy,
                self._tab_stocks, self._tab_achievements, self._tab_log]
        tabs[self.current_tab]()

    # ── SCROLL FRAME HELPER ──
    def _scrollable(self, parent):
        """Returns (outer_frame, inner_frame) — inner has scrollbar."""
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0,0), window=inner, anchor="nw")
        def _cfg(e): canvas.configure(scrollregion=canvas.bbox("all"))
        def _resize(e): canvas.itemconfig(win, width=e.width)
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", _resize)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return outer, inner

    # ─────────── DASHBOARD ───────────
    def _tab_dashboard(self):
        gs = self.gs
        _, inner = self._scrollable(self.content_frame)

        # 6 Tiles
        tile_f = tk.Frame(inner, bg=BG)
        tile_f.pack(fill="x", padx=10, pady=(10,6))
        tiles = [
            ("Bargeld",           fmt(gs.cash),              gs.cash >= 0),
            ("Nettovermögen",     fmt(gs.net_worth()),        True),
            ("Immobilien",        f"{len(gs.props)} Objekte", True),
            ("Unternehmen",       f"{len(gs.comps)} Firmen",  True),
            ("Monatl. Einnahmen", fmt(gs.monthly_income()),   True),
            ("Monatl. Ausgaben",  fmt(gs.monthly_expenses()), False),
        ]
        for i, (label, val, good) in enumerate(tiles):
            col = i % 3
            row = i // 3
            f = tk.Frame(tile_f, bg=PANEL2, bd=1, relief="flat")
            f.grid(row=row, column=col, padx=5, pady=4, sticky="nsew")
            tile_f.columnconfigure(col, weight=1)
            tk.Label(f, text=label, font=("Arial", 9), fg=MUTED, bg=PANEL2,
                     anchor="w").pack(anchor="w", padx=10, pady=(8,2))
            tk.Label(f, text=val, font=("Arial", 14, "bold"),
                     fg=GREEN if good else RED, bg=PANEL2,
                     anchor="w").pack(anchor="w", padx=10, pady=(0,8))

        # Vermietungsstatus
        if gs.props:
            sf = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
            sf.pack(fill="x", padx=10, pady=(0,6))
            tk.Label(sf, text="Immobilien-Status:", font=("Arial", 9),
                     fg=MUTED, bg=PANEL2).pack(side="left", padx=8, pady=4)
            for p in gs.props:
                if p["vacant"] and not p["listed"]:
                    col, status = RED, "LEER"
                elif p["vacant"] and p["listed"]:
                    col, status = YELLOW, "Suche..."
                else:
                    ti = p.get("tenant")
                    col = GREEN
                    status = TENANT_TYPES[ti]["name"][:8] if ti is not None else "Vermietet"
                bg = DARK_RED if col==RED else (DARK_YELLOW if col==YELLOW else DARK_GREEN)
                lf = tk.Frame(sf, bg=bg, padx=6, pady=2)
                lf.pack(side="left", padx=3, pady=4)
                tk.Label(lf, text=f"{p['name'][:7]}: {status}", font=("Arial", 9, "bold"),
                         fg=col, bg=bg).pack()

        # NW Chart
        chart_f = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
        chart_f.pack(fill="x", padx=10, pady=(0,6))
        tk.Label(chart_f, text="Nettovermögen (24 Monate)", font=("Arial", 9),
                 fg=MUTED, bg=PANEL2, anchor="w").pack(anchor="w", padx=10, pady=(6,0))
        nw_canvas = tk.Canvas(chart_f, bg=PANEL2, height=100,
                              highlightthickness=0)
        nw_canvas.pack(fill="x", padx=10, pady=(2,4))
        nw_canvas.update_idletasks()
        w = nw_canvas.winfo_width() or 800
        if len(gs.nw_hist) >= 2:
            draw_sparkline(nw_canvas, gs.nw_hist, 5, 5, w-10, 85, CYAN)

        # CF Bar Chart
        if len(gs.cf_hist) >= 2:
            cf_f = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
            cf_f.pack(fill="x", padx=10, pady=(0,6))
            tk.Label(cf_f, text="Monatlicher Cashflow (24 Monate)", font=("Arial", 9),
                     fg=MUTED, bg=PANEL2, anchor="w").pack(anchor="w", padx=10, pady=(6,0))
            cf_canvas = tk.Canvas(cf_f, bg=PANEL2, height=80, highlightthickness=0)
            cf_canvas.pack(fill="x", padx=10, pady=(2,4))
            cf_canvas.update_idletasks()
            w2 = cf_canvas.winfo_width() or 800
            hist = gs.cf_hist
            mn, mx = min(hist), max(hist)
            rng = mx - mn if mx != mn else 1
            bw = max(2, (w2-10)//max(1,len(hist)))
            zero_y = 70 - int(max(0,mx)/rng*65)
            for ii, cf in enumerate(hist):
                bx = 5 + ii*bw
                bar_h = max(1, int(abs(cf)/rng*65))
                col = GREEN if cf >= 0 else RED
                if cf >= 0:
                    cf_canvas.create_rectangle(bx, zero_y-bar_h, bx+bw-1, zero_y, fill=col, outline="")
                else:
                    cf_canvas.create_rectangle(bx, zero_y, bx+bw-1, zero_y+bar_h, fill=col, outline="")

    # ─────────── WIRTSCHAFT ───────────
    def _tab_economy(self):
        gs = self.gs
        ph = PHASES[gs.phase]
        _, inner = self._scrollable(self.content_frame)

        # Phase banner
        pf = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
        pf.pack(fill="x", padx=10, pady=(10,6))
        left_bar = tk.Frame(pf, bg=ph["col"], width=5)
        left_bar.pack(side="left", fill="y")
        info_f = tk.Frame(pf, bg=PANEL2)
        info_f.pack(side="left", padx=12, pady=8)
        tk.Label(info_f, text="Aktuelle Wirtschaftsphase", font=("Arial", 9),
                 fg=MUTED, bg=PANEL2).pack(anchor="w")
        tk.Label(info_f, text=ph["label"], font=("Arial", 20, "bold"),
                 fg=ph["col"], bg=PANEL2).pack(anchor="w")
        tk.Label(info_f, text=f"Noch ca. {gs.phase_dur} Monate", font=("Arial", 9),
                 fg=MUTED, bg=PANEL2).pack(anchor="w")

        # Indikatoren
        ig = tk.Frame(inner, bg=BG)
        ig.pack(fill="x", padx=10, pady=(0,6))
        indics = [
            ("Leitzins",        f"{gs.base_rate:.2f}%",          gs.base_rate < 6),
            ("BIP-Wachstum",    f"{gs.gdp:.1f}%",                gs.gdp > 0),
            ("Arbeitslosigkeit",f"{gs.unemp:.1f}%",              gs.unemp < 8),
            ("Marktstimmung",   f"{int(gs.sentiment)}/100",      gs.sentiment > 50),
            ("Inflation",       f"{gs.inflation*12*100:.1f}% pa", gs.inflation*12 < 0.03),
            ("Kreditrate",      f"{gs.loan_rate*12*100:.2f}% pa", True),
        ]
        for i, (label, val, good) in enumerate(indics):
            col = i % 3
            row = i // 3
            f = tk.Frame(ig, bg=PANEL2, bd=1, relief="flat")
            f.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")
            ig.columnconfigure(col, weight=1)
            tk.Label(f, text=label, font=("Arial", 9), fg=MUTED, bg=PANEL2,
                     anchor="w").pack(anchor="w", padx=8, pady=(6,2))
            tk.Label(f, text=val, font=("Arial", 13, "bold"),
                     fg=GREEN if good else RED, bg=PANEL2,
                     anchor="w").pack(anchor="w", padx=8, pady=(0,6))

        # Phasen-Übersicht
        prow = tk.Frame(inner, bg=BG)
        prow.pack(fill="x", padx=10, pady=(0,6))
        tk.Label(prow, text="Alle Wirtschaftsphasen:", font=("Arial", 9),
                 fg=MUTED, bg=BG).pack(side="left", padx=(0,8))
        for pname, pd in PHASES.items():
            active = gs.phase == pname
            bg = pd["col"] if active else PANEL2
            fg = BG if active else pd["col"]
            tk.Label(prow, text=pd["label"], font=("Arial", 10, "bold" if active else "normal"),
                     fg=fg, bg=bg, padx=8, pady=4, bd=1 if not active else 0,
                     relief="flat").pack(side="left", padx=3)

        # Tipp
        tip = TIPS.get(gs.phase, "")
        tf = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
        tf.pack(fill="x", padx=10, pady=(0,10))
        tk.Label(tf, text=f"💡 Tipp: {tip}", font=("Arial", 11),
                 fg=YELLOW, bg=PANEL2, anchor="w",
                 wraplength=800).pack(anchor="w", padx=10, pady=8)

    # ─────────── AKTIEN ───────────
    def _tab_stocks(self):
        gs = self.gs
        _, inner = self._scrollable(self.content_frame)

        tk.Label(inner, text="Klick auf eine Aktie: Kaufen/Verkaufen",
                 font=("Arial", 9), fg=MUTED, bg=BG).pack(anchor="w", padx=10, pady=(6,4))

        grid = tk.Frame(inner, bg=BG)
        grid.pack(fill="x", padx=10)

        sids = list(gs.stock_data.keys())
        for i, sid in enumerate(sids):
            s   = gs.stock_data[sid]
            qty = gs.stocks.get(sid, 0)
            row = i // 2
            col = i % 2
            grid.columnconfigure(col, weight=1)

            sf = tk.Frame(grid, bg=PANEL2, bd=1, relief="flat", cursor="hand2")
            sf.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")
            sf.bind("<Button-1>", lambda e, s2=sid: self._open_modal("buy_stock", sid=s2))

            top = tk.Frame(sf, bg=PANEL2)
            top.pack(fill="x", padx=8, pady=(6,0))

            pchg = (s["hist"][-1]/s["hist"][-2]-1)*100 if len(s["hist"])>=2 else 0
            tk.Label(top, text=s["name"], font=("Arial", 12, "bold"),
                     fg=WHITE, bg=PANEL2).pack(side="left")
            tk.Label(top, text=f"Div: {s['div']*100:.1f}%", font=("Arial", 9),
                     fg=MUTED, bg=PANEL2).pack(side="right")

            mid = tk.Frame(sf, bg=PANEL2)
            mid.pack(fill="x", padx=8)
            tk.Label(mid, text=fmt(s["price"]), font=("Arial", 11, "bold"),
                     fg=CYAN, bg=PANEL2).pack(side="left")
            tk.Label(mid, text=f"  {pchg:+.1f}%", font=("Arial", 10),
                     fg=GREEN if pchg>=0 else RED, bg=PANEL2).pack(side="left")
            if qty > 0:
                tk.Label(mid, text=f"{qty:.0f} Stk = {fmt(qty*s['price'])}",
                         font=("Arial", 9), fg=PURPLE, bg=PANEL2).pack(side="right")

            # Sparkline
            c = tk.Canvas(sf, bg=PANEL2, height=40, highlightthickness=0)
            c.pack(fill="x", padx=8, pady=(2,6))
            c.update_idletasks()
            cw = c.winfo_width() or 300
            if len(s["hist"]) >= 2:
                draw_sparkline(c, s["hist"], 2, 2, cw-4, 34)

            btn_row = tk.Frame(sf, bg=PANEL2)
            btn_row.pack(fill="x", padx=8, pady=(0,6))
            tk.Button(btn_row, text="Kaufen", font=("Arial", 9, "bold"),
                      bg=ACCENT, fg=WHITE, bd=0, relief="flat",
                      padx=10, pady=3, cursor="hand2",
                      command=lambda s2=sid: self._open_modal("buy_stock", sid=s2)
                      ).pack(side="left", padx=(0,4))
            tk.Button(btn_row, text="Verkaufen", font=("Arial", 9),
                      bg=RED, fg=WHITE, bd=0, relief="flat",
                      padx=10, pady=3, cursor="hand2",
                      command=lambda s2=sid: self._open_modal("sell_stock", sid=s2)
                      ).pack(side="left")

        # ETF
        ef = tk.Frame(inner, bg=PANEL2, bd=2, relief="flat",
                      cursor="hand2")
        ef.pack(fill="x", padx=10, pady=8)
        ef.bind("<Button-1>", lambda e: self._open_modal("buy_etf"))

        etop = tk.Frame(ef, bg=PANEL2)
        etop.pack(fill="x", padx=10, pady=(8,2))
        tk.Label(etop, text="🌍 Welt-ETF", font=("Arial", 14, "bold"),
                 fg=GOLD, bg=PANEL2).pack(side="left")
        tk.Label(etop, text="Div: 2.4% pa | Geringes Risiko",
                 font=("Arial", 9), fg=MUTED, bg=PANEL2).pack(side="right")

        ebot = tk.Frame(ef, bg=PANEL2)
        ebot.pack(fill="x", padx=10, pady=(0,6))
        tk.Label(ebot, text=fmt(gs.etf_price), font=("Arial", 12, "bold"),
                 fg=CYAN, bg=PANEL2).pack(side="left")
        if gs.etf > 0:
            tk.Label(ebot, text=f"  {gs.etf:.1f} Anteile = {fmt(gs.etf*gs.etf_price)}",
                     font=("Arial", 10), fg=PURPLE, bg=PANEL2).pack(side="left")

        ec = tk.Canvas(ef, bg=PANEL2, height=50, highlightthickness=0)
        ec.pack(fill="x", padx=10, pady=(0,8))
        ec.update_idletasks()
        ew = ec.winfo_width() or 600
        if len(gs.etf_hist) >= 2:
            draw_sparkline(ec, gs.etf_hist, 2, 2, ew-4, 44, ACCENT)

        ebtn = tk.Frame(ef, bg=PANEL2)
        ebtn.pack(padx=10, pady=(0,8), anchor="w")
        tk.Button(ebtn, text="Kaufen", font=("Arial", 10, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, relief="flat",
                  padx=14, pady=4, cursor="hand2",
                  command=lambda: self._open_modal("buy_etf")).pack(side="left", padx=(0,6))
        if gs.etf > 0:
            tk.Button(ebtn, text="Alles verkaufen", font=("Arial", 10),
                      bg=RED, fg=WHITE, bd=0, relief="flat",
                      padx=14, pady=4, cursor="hand2",
                      command=self._sell_all_etf).pack(side="left")

    def _sell_all_etf(self):
        gs = self.gs
        if gs.etf > 0:
            proceeds = gs.etf * gs.etf_price
            gs.cash += proceeds
            gs.add_log(f"Alle ETF-Anteile verkauft: +{fmt(proceeds)}", "info")
            gs.etf = 0
        self._render_tab()

    # ─────────── ERFOLGE ───────────
    def _tab_achievements(self):
        gs = self.gs
        _, inner = self._scrollable(self.content_frame)
        n = len(gs.achiev_done)
        tk.Label(inner, text=f"Erfolge {n}/{len(ACHIEVEMENTS)}",
                 font=("Arial", 14, "bold"), fg=GOLD, bg=BG
                 ).pack(anchor="w", padx=10, pady=(10,6))
        for aid, title, desc, _ in ACHIEVEMENTS:
            earned = aid in gs.achiev_done
            bg = DARK_GREEN if earned else PANEL2
            border = GREEN if earned else BORDER
            f = tk.Frame(inner, bg=bg, bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=3)
            icon = "✅" if earned else "⬜"
            tk.Label(f, text=icon, font=("Arial", 14), bg=bg).pack(side="left", padx=8, pady=6)
            info = tk.Frame(f, bg=bg)
            info.pack(side="left", pady=6)
            tk.Label(info, text=title, font=("Arial", 12, "bold" if earned else "normal"),
                     fg=WHITE if earned else MUTED, bg=bg).pack(anchor="w")
            tk.Label(info, text=desc, font=("Arial", 9),
                     fg=MUTED, bg=bg).pack(anchor="w")

    # ─────────── LOG ───────────
    def _tab_log(self):
        gs = self.gs
        _, inner = self._scrollable(self.content_frame)
        tk.Label(inner, text="Aktivitätslog", font=("Arial", 14, "bold"),
                 fg=GOLD, bg=BG).pack(anchor="w", padx=10, pady=(10,6))
        kind_col = {"good": GREEN, "bad": RED, "warn": YELLOW, "info": CYAN}
        for msg, kind in gs.log[:60]:
            col = kind_col.get(kind, MUTED)
            row = tk.Frame(inner, bg=BG)
            row.pack(fill="x", padx=10, pady=1)
            tk.Frame(row, bg=col, width=3).pack(side="left", fill="y", padx=(0,8))
            tk.Label(row, text=msg, font=("Arial", 11), fg=WHITE,
                     bg=BG, anchor="w", wraplength=900).pack(side="left", anchor="w")

    # ══════════════════════════════════════════════════
    #  MODALS
    # ══════════════════════════════════════════════════
    def _open_modal(self, modal_type, **kwargs):
        self.modal_top = tk.Toplevel(self.root)
        self.modal_top.title("")
        self.modal_top.configure(bg=PANEL)
        self.modal_top.resizable(False, False)
        # Center
        self.modal_top.update_idletasks()
        mw, mh = 660, 540
        rx = self.root.winfo_x() + (self.root.winfo_width()-mw)//2
        ry = self.root.winfo_y() + (self.root.winfo_height()-mh)//2
        self.modal_top.geometry(f"{mw}x{mh}+{rx}+{ry}")
        self.modal_top.grab_set()
        self.modal_top.bind("<Escape>", lambda e: self.modal_top.destroy())

        # Modal content
        getattr(self, f"_modal_{modal_type}")(self.modal_top, **kwargs)

    def _modal_header(self, parent, title):
        hf = tk.Frame(parent, bg=PANEL)
        hf.pack(fill="x", padx=14, pady=(12,6))
        tk.Label(hf, text=title, font=("Arial", 15, "bold"),
                 fg=GOLD, bg=PANEL).pack(side="left")
        tk.Button(hf, text="✕", font=("Arial", 12, "bold"),
                  bg=RED, fg=WHITE, bd=0, relief="flat",
                  padx=8, pady=2, cursor="hand2",
                  command=lambda: self.modal_top.destroy()
                  ).pack(side="right")

    def _scrollable_modal(self, parent):
        frame = tk.Frame(parent, bg=PANEL)
        frame.pack(fill="both", expand=True, padx=0)
        canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=0)
        sb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=PANEL)
        win = canvas.create_window((0,0), window=inner, anchor="nw")
        def _cfg(e): canvas.configure(scrollregion=canvas.bbox("all"))
        def _rsz(e): canvas.itemconfig(win, width=e.width)
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", _rsz)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
        return inner

    def _close_and_refresh(self):
        self.modal_top.destroy()
        self._render_tab()
        self._update_topbar()
        self._update_sidebar()
        self._check_achievements()

    # ── Immobilie kaufen ──
    def _modal_buy_prop(self, parent):
        self._modal_header(parent, "Immobilie kaufen")
        tk.Label(parent, text=f"Bargeld: {fmt(self.gs.cash)}", font=("Arial", 11),
                 fg=CYAN, bg=PANEL).pack(anchor="w", padx=16, pady=(0,6))
        inner = self._scrollable_modal(parent)
        for row in PROP_CATALOG:
            can = self.gs.cash >= row["price"]
            self._prop_buy_row(inner, row, can)

    def _prop_buy_row(self, parent, row, can):
        f = tk.Frame(parent, bg=PANEL2 if can else "#191e29",
                     bd=1, relief="flat")
        f.pack(fill="x", padx=10, pady=4)
        info = tk.Frame(f, bg=f["bg"])
        info.pack(side="left", padx=10, pady=8, fill="x", expand=True)
        tk.Label(info, text=f"{row['icon']}  {row['name']}",
                 font=("Arial", 12, "bold"), fg=WHITE if can else MUTED,
                 bg=f["bg"]).pack(anchor="w")
        tk.Label(info, text=f"Preis: {fmt(row['price'])}   Miete: +{fmt(row['rent'])}/Monat   "
                             f"Kosten: -{fmt(row['maint'])}/Monat   "
                             f"Netto: {fmt(row['rent']-row['maint'])}/Monat",
                 font=("Arial", 9), fg=MUTED, bg=f["bg"]).pack(anchor="w")
        col = ACCENT if can else BORDER
        tk.Button(f, text="Kaufen" if can else "Kein Geld",
                  font=("Arial", 10, "bold"), bg=col, fg=WHITE,
                  bd=0, relief="flat", padx=12, pady=6,
                  cursor="hand2" if can else "arrow",
                  command=lambda r=row: self._buy_prop(r) if can else None
                  ).pack(side="right", padx=10, pady=10)

    def _buy_prop(self, row):
        gs = self.gs
        if gs.cash >= row["price"]:
            gs.cash -= row["price"]
            gs.props.append(make_prop(row))
            gs.add_log(f"Immobilie gekauft: {row['name']} ({fmt(row['price'])})", "good")
        self._close_and_refresh()

    # ── Immobilie verkaufen ──
    def _modal_sell_prop(self, parent):
        self._modal_header(parent, "Immobilie verkaufen")
        gs = self.gs
        if not gs.props:
            tk.Label(parent, text="Keine Immobilien vorhanden.", font=("Arial", 12),
                     fg=MUTED, bg=PANEL).pack(padx=16, pady=20)
            return
        inner = self._scrollable_modal(parent)
        for i, p in enumerate(gs.props):
            sv = p["price"] * 0.94
            f = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=4)
            info = tk.Frame(f, bg=PANEL2)
            info.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(info, text=f"{p['name']}  (Lvl {p['level']})",
                     font=("Arial", 12, "bold"), fg=WHITE, bg=PANEL2).pack(anchor="w")
            tk.Label(info, text=f"Verkaufswert: {fmt(sv)}  |  Netto: {fmt(p['rent']-p['maint'])}/Monat"
                                 + ("  ⚠️ LEERSTAND" if p["vacant"] else ""),
                     font=("Arial", 9), fg=MUTED, bg=PANEL2).pack(anchor="w")
            tk.Button(f, text="Verkaufen", font=("Arial", 10, "bold"),
                      bg=RED, fg=WHITE, bd=0, relief="flat", padx=12, pady=6,
                      cursor="hand2",
                      command=lambda idx=i: self._sell_prop(idx)
                      ).pack(side="right", padx=10, pady=10)

    def _sell_prop(self, idx):
        gs = self.gs
        p = gs.props[idx]
        sv = p["price"] * 0.94
        gs.cash += sv
        gs.props.pop(idx)
        gs.add_log(f"Immobilie verkauft: {p['name']} +{fmt(sv)}", "info")
        self._close_and_refresh()

    # ── Renovieren ──
    def _modal_upg_prop(self, parent):
        self._modal_header(parent, "Immobilie renovieren")
        tk.Label(parent, text="Kosten: 12% des Immowerts  |  +15% Miete, +8% Wert",
                 font=("Arial", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(0,4))
        gs = self.gs
        if not gs.props:
            tk.Label(parent, text="Keine Immobilien vorhanden.", font=("Arial", 12),
                     fg=MUTED, bg=PANEL).pack(padx=16, pady=20)
            return
        inner = self._scrollable_modal(parent)
        for i, p in enumerate(gs.props):
            cost  = p["price"] * 0.12
            maxed = p["level"] >= p["lvl_max"]
            can   = gs.cash >= cost and not maxed
            f = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=4)
            info = tk.Frame(f, bg=PANEL2)
            info.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(info, text=p["name"], font=("Arial", 12, "bold"),
                     fg=WHITE, bg=PANEL2).pack(anchor="w")
            tk.Label(info, text=f"Level {p['level']}/{p['lvl_max']}  |  Kosten: {fmt(cost)}",
                     font=("Arial", 9), fg=MUTED, bg=PANEL2).pack(anchor="w")
            # progress bar
            pf = tk.Frame(info, bg=PANEL2)
            pf.pack(anchor="w", pady=2)
            total_w = 200
            fill_w  = int(total_w * p["level"] / p["lvl_max"])
            tk.Frame(pf, bg=BORDER, width=total_w, height=6).place(x=0, y=0)
            tk.Frame(pf, bg=ACCENT, width=fill_w, height=6).pack(side="left")
            tk.Frame(pf, width=total_w, height=6).pack()  # spacer

            lbl = "Max Level" if maxed else ("Renovieren" if can else "Kein Geld")
            col = BORDER if (maxed or not can) else ACCENT
            tk.Button(f, text=lbl, font=("Arial", 10, "bold"),
                      bg=col, fg=WHITE, bd=0, relief="flat", padx=12, pady=6,
                      cursor="hand2" if can else "arrow",
                      command=lambda idx=i: self._upg_prop(idx) if can else None
                      ).pack(side="right", padx=10, pady=10)

    def _upg_prop(self, idx):
        gs = self.gs
        p = gs.props[idx]
        cost = p["price"] * 0.12
        if gs.cash >= cost:
            gs.cash -= cost
            p["level"] += 1
            p["price"] *= 1.08
            p["base_rent"] *= 1.15
            p["rent"]      *= 1.15
            p["maint"]     *= 1.06
            gs.add_log(f"Renoviert: {p['name']} Lvl {p['level']}", "good")
        self._close_and_refresh()

    # ── Vermieten ──
    def _modal_rent_prop(self, parent):
        self._modal_header(parent, "Vermietungs-Verwaltung")
        tk.Label(parent,
                 text="Biete leere Immobilien an. Mieter kommen je nach Wirtschaftslage.",
                 font=("Arial", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(0,4))
        gs = self.gs
        if not gs.props:
            tk.Label(parent, text="Keine Immobilien vorhanden.", font=("Arial", 12),
                     fg=MUTED, bg=PANEL).pack(padx=16, pady=20)
            return
        inner = self._scrollable_modal(parent)
        for i, p in enumerate(gs.props):
            if p["vacant"] and not p["listed"]:
                bg, border = DARK_RED, RED
            elif p["vacant"] and p["listed"]:
                bg, border = DARK_YELLOW, YELLOW
            else:
                bg, border = DARK_GREEN, GREEN
            f = tk.Frame(inner, bg=bg, bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=4)

            left = tk.Frame(f, bg=bg)
            left.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(left, text=f"{p['name']}  Lvl {p['level']}",
                     font=("Arial", 12, "bold"), fg=WHITE, bg=bg).pack(anchor="w")
            if p["vacant"] and not p["listed"]:
                status = "LEER"; sc = RED
            elif p["vacant"] and p["listed"]:
                status = "SUCHE MIETER..."; sc = YELLOW
            else:
                ti = p["tenant"]
                tname = TENANT_TYPES[ti]["name"] if ti is not None else "Mieter"
                status = f"VERMIETET: {tname}  ({p['contract_left']} Monate)"; sc = GREEN
            tk.Label(left, text=status, font=("Arial", 10, "bold"),
                     fg=sc, bg=bg).pack(anchor="w")
            if not p["vacant"]:
                tk.Label(left, text=f"Miete: {fmt(p['rent'])}/Monat  |  Netto: {fmt(p['rent']-p['maint'])}/Monat",
                         font=("Arial", 9), fg=CYAN, bg=bg).pack(anchor="w")
            else:
                tk.Label(left, text=f"Basis-Miete: {fmt(p['base_rent'])}/Monat  |  Kosten: -{fmt(p['maint'])}/Monat",
                         font=("Arial", 9), fg=MUTED, bg=bg).pack(anchor="w")
                if not p["listed"]:
                    # Mietertypen-Vorschau
                    preview = "  |  ".join(
                        f"{t['name']}: {'+' if t['bonus']>=0 else ''}{t['bonus']*100:.0f}% ({t['months']}M)"
                        for t in TENANT_TYPES
                    )
                    tk.Label(left, text=f"Mögl. Mieter: {preview}",
                             font=("Arial", 8), fg=MUTED, bg=bg,
                             wraplength=420).pack(anchor="w")

            if p["vacant"] and not p["listed"]:
                btn_text, btn_col, fn = "Anbieten", GREEN, lambda idx=i: self._list_prop(idx)
            elif p["vacant"] and p["listed"]:
                btn_text, btn_col, fn = "Suche stoppen", YELLOW, lambda idx=i: self._unlist_prop(idx)
            else:
                btn_text, btn_col, fn = "Kündigen (-2M)", RED, lambda idx=i: self._evict_prop(idx)
            tk.Button(f, text=btn_text, font=("Arial", 10, "bold"),
                      bg=btn_col, fg=BG if btn_col!=RED else WHITE,
                      bd=0, relief="flat", padx=12, pady=6, cursor="hand2",
                      command=fn).pack(side="right", padx=10, pady=10)

    def _list_prop(self, idx):
        p = self.gs.props[idx]; p["listed"] = True
        self.gs.add_log(f"{p['name']} auf Mietmarkt angeboten", "info")
        self._close_and_refresh()

    def _unlist_prop(self, idx):
        p = self.gs.props[idx]; p["listed"] = False
        self.gs.add_log(f"{p['name']} vom Mietmarkt genommen", "info")
        self._close_and_refresh()

    def _evict_prop(self, idx):
        gs = self.gs; p = gs.props[idx]
        tname = TENANT_TYPES[p["tenant"]]["name"] if p["tenant"] is not None else "Mieter"
        penalty = p["rent"] * 2; gs.cash -= penalty
        p["tenant"] = None; p["vacant"] = True; p["listed"] = False; p["contract_left"] = 0
        gs.add_log(f"{tname} rausgekündigt: -{fmt(penalty)} Strafe", "bad")
        self._close_and_refresh()

    # ── Firma gründen ──
    def _modal_buy_comp(self, parent):
        self._modal_header(parent, "Unternehmen gründen")
        tk.Label(parent, text=f"Bargeld: {fmt(self.gs.cash)}", font=("Arial", 11),
                 fg=CYAN, bg=PANEL).pack(anchor="w", padx=16, pady=(0,6))
        inner = self._scrollable_modal(parent)
        for row in COMP_CATALOG:
            can = self.gs.cash >= row["price"]
            f = tk.Frame(inner, bg=PANEL2 if can else "#191e29", bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=4)
            info = tk.Frame(f, bg=f["bg"])
            info.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(info, text=f"{row['icon']}  {row['name']}",
                     font=("Arial", 12, "bold"), fg=WHITE if can else MUTED,
                     bg=f["bg"]).pack(anchor="w")
            tk.Label(info,
                     text=f"Preis: {fmt(row['price'])}   Gewinn: +{fmt(row['profit'])}/Monat   "
                          f"Risiko: {row['risk']*100:.0f}%   Kosten: -{fmt(row['maint'])}/Monat",
                     font=("Arial", 9), fg=MUTED, bg=f["bg"]).pack(anchor="w")
            tk.Button(f, text="Gründen" if can else "Kein Geld",
                      font=("Arial", 10, "bold"), bg=ACCENT if can else BORDER,
                      fg=WHITE, bd=0, relief="flat", padx=12, pady=6,
                      cursor="hand2" if can else "arrow",
                      command=lambda r=row: self._buy_comp(r) if can else None
                      ).pack(side="right", padx=10, pady=10)

    def _buy_comp(self, row):
        gs = self.gs
        if gs.cash >= row["price"]:
            gs.cash -= row["price"]
            gs.comps.append(make_comp(row))
            gs.add_log(f"Firma gegründet: {row['name']} ({fmt(row['price'])})", "good")
        self._close_and_refresh()

    # ── Firma verkaufen ──
    def _modal_sell_comp(self, parent):
        self._modal_header(parent, "Unternehmen verkaufen")
        gs = self.gs
        if not gs.comps:
            tk.Label(parent, text="Keine Unternehmen vorhanden.", font=("Arial", 12),
                     fg=MUTED, bg=PANEL).pack(padx=16, pady=20)
            return
        inner = self._scrollable_modal(parent)
        for i, c in enumerate(gs.comps):
            sv = c["val"] * 0.88
            f = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=4)
            info = tk.Frame(f, bg=PANEL2)
            info.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(info, text=f"{c['name']}  (Lvl {c['level']})",
                     font=("Arial", 12, "bold"), fg=WHITE, bg=PANEL2).pack(anchor="w")
            tk.Label(info, text=f"Verkaufswert: {fmt(sv)}  |  Gewinn: {fmt(c['profit'])}/Monat",
                     font=("Arial", 9), fg=MUTED, bg=PANEL2).pack(anchor="w")
            tk.Button(f, text="Verkaufen", font=("Arial", 10, "bold"),
                      bg=RED, fg=WHITE, bd=0, relief="flat", padx=12, pady=6, cursor="hand2",
                      command=lambda idx=i: self._sell_comp(idx)
                      ).pack(side="right", padx=10, pady=10)

    def _sell_comp(self, idx):
        gs = self.gs; c = gs.comps[idx]
        sv = c["val"] * 0.88; gs.cash += sv
        gs.comps.pop(idx)
        gs.add_log(f"Firma verkauft: {c['name']} +{fmt(sv)}", "info")
        self._close_and_refresh()

    # ── Firma erweitern ──
    def _modal_upg_comp(self, parent):
        self._modal_header(parent, "Unternehmen erweitern")
        tk.Label(parent, text="Kosten: 15% des Unternehmenswerts  |  +22% Gewinn, +12% Wert",
                 font=("Arial", 9), fg=MUTED, bg=PANEL).pack(anchor="w", padx=16, pady=(0,4))
        gs = self.gs
        if not gs.comps:
            tk.Label(parent, text="Keine Unternehmen vorhanden.", font=("Arial", 12),
                     fg=MUTED, bg=PANEL).pack(padx=16, pady=20)
            return
        inner = self._scrollable_modal(parent)
        for i, c in enumerate(gs.comps):
            cost  = c["val"] * 0.15
            maxed = c["level"] >= c["lvl_max"]
            can   = gs.cash >= cost and not maxed
            f = tk.Frame(inner, bg=PANEL2, bd=1, relief="flat")
            f.pack(fill="x", padx=10, pady=4)
            info = tk.Frame(f, bg=PANEL2)
            info.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            tk.Label(info, text=c["name"], font=("Arial", 12, "bold"),
                     fg=WHITE, bg=PANEL2).pack(anchor="w")
            tk.Label(info, text=f"Level {c['level']}/{c['lvl_max']}  |  Kosten: {fmt(cost)}  |  Gewinn: {fmt(c['profit'])}/Monat",
                     font=("Arial", 9), fg=MUTED, bg=PANEL2).pack(anchor="w")
            lbl = "Max Level" if maxed else ("Erweitern" if can else "Kein Geld")
            col = BORDER if (maxed or not can) else ACCENT
            tk.Button(f, text=lbl, font=("Arial", 10, "bold"),
                      bg=col, fg=WHITE, bd=0, relief="flat", padx=12, pady=6,
                      cursor="hand2" if can else "arrow",
                      command=lambda idx=i: self._upg_comp(idx) if can else None
                      ).pack(side="right", padx=10, pady=10)

    def _upg_comp(self, idx):
        gs = self.gs; c = gs.comps[idx]
        cost = c["val"] * 0.15
        if gs.cash >= cost:
            gs.cash -= cost; c["level"] += 1
            c["val"] *= 1.12; c["base_profit"] *= 1.22
            c["profit"] = c["base_profit"]; c["maint"] *= 1.08
            gs.add_log(f"Firma erweitert: {c['name']} Lvl {c['level']}", "good")
        self._close_and_refresh()

    # ── Kredit ──
    def _modal_loan(self, parent):
        self._modal_header(parent, "Kredit aufnehmen")
        gs = self.gs
        max_l = max(0, gs.net_worth()*0.6 - gs.loan)
        rate  = (gs.loan_rate + gs.base_rate/100/12)*12*100
        body  = tk.Frame(parent, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        for text, col in [
            (f"Aktuelle Schulden: {fmt(gs.loan)}", RED),
            (f"Max. Kreditrahmen: {fmt(max_l)}", CYAN),
            (f"Effektiver Jahreszins: {rate:.2f}%", YELLOW),
        ]:
            tk.Label(body, text=text, font=("Arial", 12), fg=col, bg=PANEL).pack(anchor="w", pady=2)

        tk.Label(body, text="Betrag (€):", font=("Arial", 11), fg=MUTED, bg=PANEL
                 ).pack(anchor="w", pady=(12,2))
        entry = tk.Entry(body, font=("Arial", 13), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat", width=20)
        entry.pack(anchor="w", ipady=6, padx=4)

        def do_loan():
            try: amt = float(entry.get().replace(",","."))
            except: return
            if 0 < amt <= max_l and gs.cash + amt > 0:
                gs.cash += amt; gs.loan += amt
                gs.add_log(f"Kredit aufgenommen: +{fmt(amt)}", "warn")
            self._close_and_refresh()

        tk.Button(body, text="Kredit aufnehmen", font=("Arial", 12, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, relief="flat", padx=16, pady=6,
                  cursor="hand2", command=do_loan).pack(anchor="w", pady=10)
        tk.Label(body, text="⚠️  Warnung: Hohe Schulden führen zu Bankrott!",
                 font=("Arial", 10), fg=RED, bg=PANEL).pack(anchor="w")

    # ── Kredit tilgen ──
    def _modal_repay(self, parent):
        self._modal_header(parent, "Kredit tilgen")
        gs = self.gs
        body = tk.Frame(parent, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        tk.Label(body, text=f"Offene Schulden: {fmt(gs.loan)}",
                 font=("Arial", 12), fg=RED, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Verfügbares Bargeld: {fmt(gs.cash)}",
                 font=("Arial", 12), fg=CYAN, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text="Betrag (€):", font=("Arial", 11), fg=MUTED, bg=PANEL
                 ).pack(anchor="w", pady=(12,2))
        entry = tk.Entry(body, font=("Arial", 13), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat", width=20)
        entry.pack(anchor="w", ipady=6, padx=4)

        def do_repay():
            try: amt = float(entry.get().replace(",","."))
            except: amt = 0
            amt = min(amt, gs.cash, gs.loan)
            if amt > 0:
                gs.cash -= amt; gs.loan = max(0, gs.loan - amt)
                gs.add_log(f"Kredit getilgt: -{fmt(amt)}", "good")
            self._close_and_refresh()

        def do_repay_all():
            amt = min(gs.cash, gs.loan)
            if amt > 0:
                gs.cash -= amt; gs.loan = max(0, gs.loan - amt)
                gs.add_log(f"Alle Schulden getilgt: -{fmt(amt)}", "good")
            self._close_and_refresh()

        btn_row = tk.Frame(body, bg=PANEL)
        btn_row.pack(anchor="w", pady=10)
        tk.Button(btn_row, text="Teilbetrag tilgen", font=("Arial", 12, "bold"),
                  bg=GREEN, fg=BG, bd=0, relief="flat", padx=14, pady=6,
                  cursor="hand2", command=do_repay).pack(side="left", padx=(0,8))
        tk.Button(btn_row, text="Alles tilgen", font=("Arial", 12, "bold"),
                  bg=YELLOW, fg=BG, bd=0, relief="flat", padx=14, pady=6,
                  cursor="hand2", command=do_repay_all).pack(side="left")

    # ── Festgeld ──
    def _modal_savings(self, parent):
        self._modal_header(parent, "Festgeld-Konto")
        gs = self.gs
        body = tk.Frame(parent, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        rate = gs.sav_rate * 12 * 100
        tk.Label(body, text=f"Einlage: {fmt(gs.savings)}", font=("Arial", 12), fg=CYAN, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Zinssatz: {rate:.2f}% pa = {fmt(gs.savings*gs.sav_rate)}/Monat",
                 font=("Arial", 12), fg=GREEN, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Bargeld: {fmt(gs.cash)}", font=("Arial", 11), fg=MUTED, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text="Betrag einzahlen (€):", font=("Arial", 11), fg=MUTED, bg=PANEL
                 ).pack(anchor="w", pady=(12,2))
        entry = tk.Entry(body, font=("Arial", 13), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat", width=20)
        entry.pack(anchor="w", ipady=6, padx=4)

        def do_deposit():
            try: amt = float(entry.get().replace(",","."))
            except: return
            if 0 < amt <= gs.cash:
                gs.cash -= amt; gs.savings += amt
                gs.add_log(f"Festgeld eingelegt: {fmt(amt)}", "info")
            self._close_and_refresh()

        def do_withdraw():
            if gs.savings > 0:
                gs.cash += gs.savings
                gs.add_log(f"Festgeld ausgezahlt: {fmt(gs.savings)}", "info")
                gs.savings = 0
            self._close_and_refresh()

        btn_row = tk.Frame(body, bg=PANEL)
        btn_row.pack(anchor="w", pady=10)
        tk.Button(btn_row, text="Einzahlen", font=("Arial", 12, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, relief="flat", padx=14, pady=6,
                  cursor="hand2", command=do_deposit).pack(side="left", padx=(0,8))
        if gs.savings > 0:
            tk.Button(btn_row, text="Auszahlen", font=("Arial", 12, "bold"),
                      bg=YELLOW, fg=BG, bd=0, relief="flat", padx=14, pady=6,
                      cursor="hand2", command=do_withdraw).pack(side="left")

    # ── Aktie kaufen ──
    def _modal_buy_stock(self, parent, sid):
        gs = self.gs; s = gs.stock_data[sid]
        qty_owned = gs.stocks.get(sid, 0)
        self._modal_header(parent, "Aktie kaufen")
        body = tk.Frame(parent, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        tk.Label(body, text=f"{s['name']}  |  Kurs: {fmt(s['price'])}  |  Div: {s['div']*100:.1f}% pa",
                 font=("Arial", 12, "bold"), fg=WHITE, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Im Besitz: {qty_owned:.0f} Stk = {fmt(qty_owned*s['price'])}",
                 font=("Arial", 11), fg=CYAN, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Bargeld: {fmt(gs.cash)}", font=("Arial", 11), fg=MUTED, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text="Anzahl Aktien:", font=("Arial", 11), fg=MUTED, bg=PANEL
                 ).pack(anchor="w", pady=(12,2))
        entry = tk.Entry(body, font=("Arial", 13), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat", width=20)
        entry.pack(anchor="w", ipady=6, padx=4)

        def do_buy():
            try: qty = int(float(entry.get()))
            except: return
            cost = qty * s["price"]
            if qty > 0 and gs.cash >= cost:
                gs.cash -= cost
                gs.stocks[sid] = gs.stocks.get(sid, 0) + qty
                gs.add_log(f"Aktie gekauft: {qty}x {s['name']}", "good")
            self._close_and_refresh()

        tk.Button(body, text="Kaufen", font=("Arial", 12, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, relief="flat", padx=16, pady=6,
                  cursor="hand2", command=do_buy).pack(anchor="w", pady=10)

        # Sparkline
        if len(s["hist"]) >= 2:
            tk.Label(body, text="Kursverlauf:", font=("Arial", 9), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(10,0))
            c = tk.Canvas(body, bg=PANEL2, height=120, highlightthickness=0)
            c.pack(fill="x", pady=4)
            c.update_idletasks()
            cw = c.winfo_width() or 580
            draw_sparkline(c, s["hist"], 5, 5, cw-10, 110)

    # ── Aktie verkaufen ──
    def _modal_sell_stock(self, parent, sid):
        gs = self.gs; s = gs.stock_data[sid]
        qty_owned = gs.stocks.get(sid, 0)
        self._modal_header(parent, "Aktie verkaufen")
        body = tk.Frame(parent, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        tk.Label(body, text=f"{s['name']}  |  Kurs: {fmt(s['price'])}",
                 font=("Arial", 12, "bold"), fg=WHITE, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Im Besitz: {qty_owned:.0f} Stk = {fmt(qty_owned*s['price'])}",
                 font=("Arial", 11), fg=CYAN, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text="Anzahl verkaufen:", font=("Arial", 11), fg=MUTED, bg=PANEL
                 ).pack(anchor="w", pady=(12,2))
        entry = tk.Entry(body, font=("Arial", 13), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat", width=20)
        entry.pack(anchor="w", ipady=6, padx=4)

        def do_sell():
            try: qty = int(float(entry.get()))
            except: return
            qty = min(qty, int(qty_owned))
            if qty > 0:
                proceeds = qty * s["price"]; gs.cash += proceeds
                gs.stocks[sid] = qty_owned - qty
                gs.add_log(f"Aktie verkauft: {qty}x {s['name']}", "info")
            self._close_and_refresh()

        def do_sell_all():
            if qty_owned > 0:
                proceeds = qty_owned * s["price"]; gs.cash += proceeds
                gs.stocks[sid] = 0
                gs.add_log(f"Alle {s['name']} verkauft: +{fmt(proceeds)}", "info")
            self._close_and_refresh()

        btn_row = tk.Frame(body, bg=PANEL)
        btn_row.pack(anchor="w", pady=10)
        tk.Button(btn_row, text="Verkaufen", font=("Arial", 12, "bold"),
                  bg=RED, fg=WHITE, bd=0, relief="flat", padx=16, pady=6,
                  cursor="hand2", command=do_sell).pack(side="left", padx=(0,8))
        if qty_owned > 0:
            tk.Button(btn_row, text="Alles verkaufen", font=("Arial", 12, "bold"),
                      bg=YELLOW, fg=BG, bd=0, relief="flat", padx=16, pady=6,
                      cursor="hand2", command=do_sell_all).pack(side="left")

    # ── ETF ──
    def _modal_buy_etf(self, parent):
        self._modal_header(parent, "Welt-ETF kaufen / verkaufen")
        gs = self.gs
        body = tk.Frame(parent, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=8)
        tk.Label(body, text=f"Kurs: {fmt(gs.etf_price)}  |  Im Besitz: {gs.etf:.1f} Anteile = {fmt(gs.etf*gs.etf_price)}",
                 font=("Arial", 12, "bold"), fg=WHITE, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text="Diversifiziert, geringes Risiko, Dividende: 2.4% pa",
                 font=("Arial", 11), fg=GREEN, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text=f"Bargeld: {fmt(gs.cash)}", font=("Arial", 11), fg=MUTED, bg=PANEL).pack(anchor="w", pady=2)
        tk.Label(body, text="Anzahl Anteile:", font=("Arial", 11), fg=MUTED, bg=PANEL
                 ).pack(anchor="w", pady=(12,2))
        entry = tk.Entry(body, font=("Arial", 13), bg=PANEL2, fg=WHITE,
                         insertbackground=WHITE, bd=0, relief="flat", width=20)
        entry.pack(anchor="w", ipady=6, padx=4)

        def do_buy():
            try: qty = float(entry.get().replace(",","."))
            except: return
            cost = qty * gs.etf_price
            if qty > 0 and gs.cash >= cost:
                gs.cash -= cost; gs.etf += qty
                gs.add_log(f"ETF gekauft: {qty:.1f} Anteile ({fmt(cost)})", "good")
            self._close_and_refresh()

        def do_sell_all():
            if gs.etf > 0:
                proceeds = gs.etf * gs.etf_price; gs.cash += proceeds
                gs.add_log(f"Alle ETF-Anteile verkauft: +{fmt(proceeds)}", "info")
                gs.etf = 0
            self._close_and_refresh()

        btn_row = tk.Frame(body, bg=PANEL)
        btn_row.pack(anchor="w", pady=10)
        tk.Button(btn_row, text="Kaufen", font=("Arial", 12, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, relief="flat", padx=16, pady=6,
                  cursor="hand2", command=do_buy).pack(side="left", padx=(0,8))
        if gs.etf > 0:
            tk.Button(btn_row, text="Alles verkaufen", font=("Arial", 12, "bold"),
                      bg=RED, fg=WHITE, bd=0, relief="flat", padx=16, pady=6,
                      cursor="hand2", command=do_sell_all).pack(side="left")

        if len(gs.etf_hist) >= 2:
            tk.Label(body, text="ETF-Verlauf:", font=("Arial", 9), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(10,0))
            c = tk.Canvas(body, bg=PANEL2, height=100, highlightthickness=0)
            c.pack(fill="x", pady=4)
            c.update_idletasks()
            cw = c.winfo_width() or 580
            draw_sparkline(c, gs.etf_hist, 5, 5, cw-10, 90, ACCENT)

    # ══════════════════════════════════════════════════
    #  TICK / GAME LOOP
    # ══════════════════════════════════════════════════
    def _schedule_tick(self):
        if self._tick_job:
            self.root.after_cancel(self._tick_job)
        self._tick_job = self.root.after(self.speed_ms, self._do_tick)

    def _do_tick(self):
        if not self.paused and self.gs:
            result = tick(self.gs)
            self._update_topbar()
            self._update_sidebar()
            self._check_achievements()
            self._render_tab()
            if result == "bankrott":
                self._show_bankrott()
                return
        self._schedule_tick()

    def _toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(
            text="Weiter" if self.paused else "Pause",
            bg=YELLOW if self.paused else GREEN
        )

    def _set_speed(self, ms):
        self.speed_ms = ms
        for m, b in self.spd_btns.items():
            b.config(bg=ACCENT if m==ms else PANEL2)
        self._schedule_tick()

    def _check_achievements(self):
        gs = self.gs
        for aid, title, desc, cond in ACHIEVEMENTS:
            if aid not in gs.achiev_done and cond(gs):
                gs.achiev_done.add(aid)
                gs.add_log(f"Erfolg freigeschaltet: {title}", "good")
                self._show_ach_popup(title, desc)

    def _show_ach_popup(self, title, desc):
        if self._ach_popup_job:
            self.root.after_cancel(self._ach_popup_job)
        self.ach_popup.config(text=f"🏆 Erfolg: {title}\n{desc}")
        self.ach_popup.place(relx=1.0, rely=1.0, x=-16, y=-36, anchor="se")
        self._ach_popup_job = self.root.after(4000, lambda: self.ach_popup.place_forget())

    # ── NEWSBAR scrolling ──
    def _scroll_news(self):
        gs = self.gs
        if not gs: return
        c = self.news_canvas
        c.delete("all")
        c.update_idletasks()
        w = c.winfo_width()
        news_str = "  //  ".join(gs.news[:5]) if gs.news else "Willkommen!"
        self._news_offset -= 1
        # Compute text width roughly
        char_w = 7
        total_w = len(news_str) * char_w
        if self._news_offset < -total_w:
            self._news_offset = w
        c.create_text(self._news_offset, 11, text=news_str, anchor="w",
                      fill=MUTED, font=("Arial", 10))
        self._news_job = self.root.after(30, self._scroll_news)

    # ── BANKROTT ──
    def _show_bankrott(self):
        if self._tick_job:
            self.root.after_cancel(self._tick_job)
        if self._news_job:
            self.root.after_cancel(self._news_job)

        top = tk.Toplevel(self.root)
        top.title("BANKROTT")
        top.configure(bg=BG)
        top.geometry("500x320")
        top.resizable(False, False)
        top.grab_set()
        rx = self.root.winfo_x() + (self.root.winfo_width()-500)//2
        ry = self.root.winfo_y() + (self.root.winfo_height()-320)//2
        top.geometry(f"500x320+{rx}+{ry}")

        tk.Label(top, text="BANKROTT", font=("Arial", 48, "bold"),
                 fg=RED, bg=BG).pack(pady=(30,8))
        tk.Label(top, text="Du bist zahlungsunfähig!", font=("Arial", 14),
                 fg=WHITE, bg=BG).pack()
        gs = self.gs
        tk.Label(top, text=f"Nettovermögen: {fmt(gs.net_worth())}", font=("Arial", 12),
                 fg=MUTED, bg=BG).pack(pady=4)
        months = (gs.year-2024)*12 + gs.month
        tk.Label(top, text=f"Gespielte Monate: {months}", font=("Arial", 12),
                 fg=MUTED, bg=BG).pack()

        def restart():
            top.destroy()
            self.game_frame.destroy()
            self.gs = None
            self._build_name_screen()

        tk.Button(top, text="Neu starten", font=("Arial", 14, "bold"),
                  bg=GREEN, fg=BG, bd=0, relief="flat",
                  padx=36, pady=10, cursor="hand2",
                  command=restart).pack(pady=20)


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.configure(bg=BG)

    # Style ttk Scrollbar
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background=PANEL2, troughcolor=PANEL,
                    arrowcolor=MUTED, borderwidth=0)

    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()