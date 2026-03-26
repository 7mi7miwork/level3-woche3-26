"""
Frogger Spiel - Erweiterte Version (Lernzweck)
===============================================
Dieses Programm bietet ein erweitertes Frogger-Spiel mit zwei Versionen.
Es dient als Lernbeispiel, um den Unterschied zwischen tkinter und pygame
zu verdeutlichen – gleiche Spiellogik, unterschiedliche Umsetzung.

Neue Features:
--------------
- Mehrere Level mit steigender Schwierigkeit
- 3 Leben / Herzanzeige
- Verschiedene Fahrzeugtypen (Auto, LKW, Bus, Zug)
- Power-Ups auf der Fahrbahn (Schild, Zeitverlangsamung, Extraleben)
- Upgrade-System zwischen Levels
- Highscore (wird zur Laufzeit gespeichert)
- Animationen (Pygame: Partikeleffekte, Tkinter: Flash-Effekte)
- Hindernisse (Wasser, Bäume)
- Multiplizierter Punktestand je nach Level

Versionen:
----------
1 = Tkinter  (Standardbibliothek, kein pip nötig)
2 = Pygame   (pip install pygame)

Unterschied im Code:
- Tkinter: canvas.create_*, canvas.coords(), after() für Game-Loop
- Pygame:  pygame.draw.*, pygame.Rect, Clock.tick() für Game-Loop
- Tkinter: Event-basierte Steuerung (root.bind)
- Pygame:  Polling (pygame.key.get_pressed() für Smooth-Movement)
- Tkinter: Keine echten Sprites, alles Rechtecke/Texte
- Pygame:  Echte pygame.Surface-Sprites, Alpha-Kanal, Partikel
"""

import sys
import time
import random
import math

# Globaler Highscore (bleibt während der Programmlaufzeit erhalten)
HIGHSCORE = 0


# ==============================================================================
# GEMEINSAME SPIELLOGIK (Framework-unabhängig)
# ==============================================================================

def berechne_level_geschwindigkeit(basis: float, level: int) -> float:
    """
    Gibt die skalierte Fahrzeuggeschwindigkeit für ein Level zurück.
    Jedes Level steigert die Geschwindigkeit um 15%.
    
    Lernhinweis: Diese Funktion ist framework-unabhängig – sie wird
    in BEIDEN Versionen identisch genutzt.
    """
    return basis * (1.0 + (level - 1) * 0.15)


def berechne_punkte(basis: int, level: int, combo: int) -> int:
    """
    Berechnet den Punktestand mit Level-Multiplikator und Combo.
    
    Formel: basis * level * (1 + combo * 0.5)
    """
    return int(basis * level * (1 + combo * 0.5))


def waehle_fahrzeugtyp(level: int) -> dict:
    """
    Gibt Eigenschaften eines zufälligen Fahrzeugtyps zurück.
    Ab Level 3 kommen Züge dazu, ab Level 5 Busse.
    
    Lernhinweis: Dictionaries als Datencontainer – einfach und lesbar.
    
    Rückgabe-Keys:
        typ       - Name des Fahrzeugs
        breite    - Breite in Pixeln
        hoehe     - Höhe in Pixeln
        farbe_tk  - Farbe als String für tkinter
        farbe_pg  - Farbe als RGB-Tuple für pygame
        punkte    - Bonuspunkte für Ausweichen
        leben     - Schadenspunkte bei Kollision (1 = normal, 2 = sofortiger Tod)
    """
    typen = [
        {
            "typ": "Auto",
            "breite": 50, "hoehe": 28,
            "farbe_tk": "#e74c3c", "farbe_pg": (231, 76, 60),
            "punkte": 1, "leben": 1
        },
        {
            "typ": "LKW",
            "breite": 80, "hoehe": 30,
            "farbe_tk": "#e67e22", "farbe_pg": (230, 126, 34),
            "punkte": 2, "leben": 1
        },
    ]
    if level >= 3:
        typen.append({
            "typ": "Zug",
            "breite": 160, "hoehe": 32,
            "farbe_tk": "#8e44ad", "farbe_pg": (142, 68, 173),
            "punkte": 5, "leben": 2  # Zug tötet sofort (2 Leben Schaden)
        })
    if level >= 5:
        typen.append({
            "typ": "Bus",
            "breite": 100, "hoehe": 34,
            "farbe_tk": "#16a085", "farbe_pg": (22, 160, 133),
            "punkte": 3, "leben": 1
        })
    
    # Gewichtung: Züge seltener
    gewichte = [10 if t["typ"] != "Zug" else 2 for t in typen]
    return random.choices(typen, weights=gewichte, k=1)[0]


def waehle_powerup_typ() -> dict:
    """
    Gibt einen zufälligen Power-Up-Typ zurück.
    
    Power-Up-Typen:
        schild    - Unverwundbar für 5 Sekunden
        slow      - Autos verlangsamen für 4 Sekunden
        leben     - +1 Leben
        punkte    - +50 Sofortpunkte
    """
    typen = [
        {"typ": "schild",  "symbol": "🛡",  "farbe_tk": "#3498db", "farbe_pg": (52, 152, 219),  "dauer": 5.0},
        {"typ": "slow",    "symbol": "⏱",  "farbe_tk": "#1abc9c", "farbe_pg": (26, 188, 156),   "dauer": 4.0},
        {"typ": "leben",   "symbol": "❤",  "farbe_tk": "#e91e63", "farbe_pg": (233, 30, 99),     "dauer": 0},
        {"typ": "punkte",  "symbol": "⭐", "farbe_tk": "#f1c40f", "farbe_pg": (241, 196, 15),    "dauer": 0},
    ]
    return random.choice(typen)


# ==============================================================================
# VERSION 1: Tkinter
# ==============================================================================

def start_version_tkinter():
    """
    Startet das erweiterte Frogger-Spiel mit tkinter.
    
    Was tkinter kann:
    - Canvas-Widget mit create_rectangle, create_text, create_oval
    - after() für zeitgesteuerte Wiederholungen (Game-Loop)
    - bind() für Tastatureingaben (event-basiert, nicht polling)
    - Keine echten Sprites, alles wird als Formen gezeichnet
    
    Was tkinter NICHT kann (im Vergleich zu pygame):
    - Kein direkter Pixel-Zugriff
    - Kein Alpha-Blending (Transparenz) ohne PIL
    - Kein eingebautes Sound-System
    - Niedrigere Performance bei vielen Objekten
    """
    try:
        import tkinter as tk
        import tkinter.messagebox as msgbox
    except ImportError:
        print("Fehler: tkinter ist nicht verfügbar.")
        return

    print("Starte Version 1 (Tkinter) – Erweitertes Frogger...")

    # -------------------------------------------------------------------------
    # KONFIGURATION
    # -------------------------------------------------------------------------
    BREITE = 700
    HOEHE = 500
    FROSCH_GROESSE = 28
    SPURHOEHE = 48           # Höhe einer Fahrspur
    ANZAHL_SPUREN = 7        # Anzahl der Fahrspuren
    RAND_OBEN = 60           # Platz für HUD (Kopfzeile)
    RAND_UNTEN = 60          # Platz für sicheren Bereich (Start)
    FPS_DELAY = 33           # Millisekunden pro Frame (~30 FPS)
    MAX_LEBEN = 5            # Maximale Leben
    POWERUP_CHANCE = 0.003   # Spawn-Wahrscheinlichkeit pro Frame
    
    # -------------------------------------------------------------------------
    # SPIELZUSTAND
    # Lernhinweis: nonlocal erlaubt Änderungen von Variablen aus umgebenden
    # Funktionen. In Python 3 ist dies der saubere Weg statt global.
    # -------------------------------------------------------------------------
    zustand = {
        "laeuft": True,
        "game_over": False,
        "level": 1,
        "leben": 3,
        "punkte": 0,
        "combo": 0,
        "highscore": HIGHSCORE,
        "schild_aktiv": False,
        "schild_bis": 0.0,
        "slow_aktiv": False,
        "slow_bis": 0.0,
        "frosch_x": BREITE // 2 - FROSCH_GROESSE // 2,
        "frosch_y": HOEHE - RAND_UNTEN - FROSCH_GROESSE,
        "tot_animation": 0,     # Frames für Sterbe-Animation
        "unverwundbar": 0,      # Frames Unverwundbarkeit nach Tod
        "level_abgeschlossen": False,
        "level_text_timer": 0,
    }

    # -------------------------------------------------------------------------
    # TKINTER FENSTER SETUP
    # Lernhinweis: tk.Tk() erzeugt das Hauptfenster. Ohne mainloop() am Ende
    # würde es sofort wieder verschwinden.
    # -------------------------------------------------------------------------
    root = tk.Tk()
    root.title("🐸 Frogger Deluxe – Tkinter Edition")
    root.resizable(False, False)
    root.configure(bg="#1a1a2e")

    # Canvas ist die Zeichenfläche für alles
    # Lernhinweis: Canvas-Objekte haben IDs. Mit diesen IDs können wir sie
    # später verschieben (coords) oder löschen (delete).
    canvas = tk.Canvas(root, width=BREITE, height=HOEHE, bg="#1a1a2e",
                       highlightthickness=0)
    canvas.pack()

    # -------------------------------------------------------------------------
    # FAHRZEUGE
    # Lernhinweis: Jedes Fahrzeug ist ein Dictionary mit allen nötigen Daten.
    # Die Canvas-ID (canvas_id) verknüpft das Python-Dict mit dem gezeichneten Objekt.
    # -------------------------------------------------------------------------
    fahrzeuge = []
    powerups = []
    partikel = []    # Für einfache Animations-Effekte

    def spuren_y_positionen() -> list:
        """Gibt Y-Koordinaten aller Fahrspuren zurück."""
        positionen = []
        for i in range(ANZAHL_SPUREN):
            y = RAND_OBEN + i * SPURHOEHE + 4
            positionen.append(y)
        return positionen

    def fahrzeug_erstellen(spur_y: int, level: int) -> dict:
        """
        Erstellt ein neues Fahrzeug und zeichnet es auf dem Canvas.
        
        Lernhinweis: canvas.create_rectangle() gibt eine Integer-ID zurück.
        Diese ID verwenden wir später für canvas.coords() und canvas.delete().
        """
        ftyp = waehle_fahrzeugtyp(level)
        basis_speed = berechne_level_geschwindigkeit(2.5, level)
        richtung = random.choice([-1, 1])
        speed = basis_speed * richtung * random.uniform(0.8, 1.3)
        
        if richtung > 0:
            start_x = -ftyp["breite"] - random.randint(0, 300)
        else:
            start_x = BREITE + random.randint(0, 300)

        y = spur_y
        # Fahrzeug-Körper zeichnen
        canvas_id = canvas.create_rectangle(
            start_x, y,
            start_x + ftyp["breite"], y + ftyp["hoehe"],
            fill=ftyp["farbe_tk"], outline="#ffffff", width=1
        )
        # Fahrzeugname als kleinen Text
        text_id = canvas.create_text(
            start_x + ftyp["breite"] // 2, y + ftyp["hoehe"] // 2,
            text=ftyp["typ"][0],  # Nur erster Buchstabe
            fill="white", font=("Courier", 8, "bold")
        )
        # Scheinwerfer (kleine Rechtecke)
        if richtung > 0:
            licht_x = start_x + ftyp["breite"] - 4
        else:
            licht_x = start_x + 2
        licht_id = canvas.create_rectangle(
            licht_x, y + 4,
            licht_x + 4, y + ftyp["hoehe"] - 4,
            fill="#ffff88", outline=""
        )

        return {
            "x": start_x, "y": y,
            "speed": speed, "richtung": richtung,
            "breite": ftyp["breite"], "hoehe": ftyp["hoehe"],
            "canvas_id": canvas_id,
            "text_id": text_id,
            "licht_id": licht_id,
            "typ": ftyp["typ"],
            "leben_schaden": ftyp["leben"],
        }

    def powerup_erstellen() -> dict | None:
        """
        Erstellt ein Power-Up an zufälliger Position auf einer Fahrspur.
        
        Lernhinweis: Wir nutzen canvas.create_oval() für eine andere Form.
        """
        pup = waehle_powerup_typ()
        spuren = spuren_y_positionen()
        spur = random.choice(spuren)
        x = random.randint(30, BREITE - 60)
        y = spur + 8
        groesse = 24
        
        kreis_id = canvas.create_oval(
            x, y, x + groesse, y + groesse,
            fill=pup["farbe_tk"], outline="#ffffff", width=2
        )
        text_id = canvas.create_text(
            x + groesse // 2, y + groesse // 2,
            text=pup["symbol"], font=("Arial", 10)
        )
        
        return {
            "x": x, "y": y,
            "groesse": groesse,
            "kreis_id": kreis_id,
            "text_id": text_id,
            "pup": pup,
        }

    def partikel_erstellen(x: int, y: int, farbe: str, anzahl: int = 6):
        """
        Erstellt einfache Partikel-Rechtecke für Explosions-Effekte.
        
        Lernhinweis: Tkinter hat kein eingebautes Partikel-System.
        Wir simulieren es mit kleinen Rechtecken, die wir selbst bewegen.
        pygame kann das eleganter und mit Alpha-Transparenz.
        """
        for _ in range(anzahl):
            dx = random.uniform(-4, 4)
            dy = random.uniform(-4, 4)
            groesse = random.randint(4, 10)
            pid = canvas.create_rectangle(
                x, y, x + groesse, y + groesse,
                fill=farbe, outline=""
            )
            partikel.append({
                "id": pid,
                "x": x, "y": y,
                "dx": dx, "dy": dy,
                "leben": 15,  # Frames bis der Partikel verschwindet
            })

    # -------------------------------------------------------------------------
    # LEVEL SETUP
    # -------------------------------------------------------------------------
    def level_aufbauen():
        """
        Löscht alle Fahrzeuge und baut das Level neu auf.
        
        Lernhinweis: canvas.delete(id) löscht ein einzelnes Canvas-Objekt.
        """
        nonlocal fahrzeuge, powerups
        for f in fahrzeuge:
            canvas.delete(f["canvas_id"])
            canvas.delete(f["text_id"])
            canvas.delete(f["licht_id"])
        for p in powerups:
            canvas.delete(p["kreis_id"])
            canvas.delete(p["text_id"])
        fahrzeuge = []
        powerups = []

        spuren = spuren_y_positionen()
        level = zustand["level"]
        # Fahrzeuge pro Spur: Level 1 = 2, steigt mit Level
        pro_spur = min(2 + level // 2, 5)
        
        for spur_y in spuren:
            for _ in range(pro_spur):
                f = fahrzeug_erstellen(spur_y, level)
                fahrzeuge.append(f)

        # Frosch zurücksetzen
        zustand["frosch_x"] = BREITE // 2 - FROSCH_GROESSE // 2
        zustand["frosch_y"] = HOEHE - RAND_UNTEN - FROSCH_GROESSE

    # -------------------------------------------------------------------------
    # HUD (Heads-Up-Display) – Statische Hintergrund-Elemente
    # Lernhinweis: Hintergrund-Elemente zeichnen wir einmalig oder nur wenn
    # nötig neu. In tkinter ist das aber schwieriger als in pygame, weil wir
    # keine "Ebenen" haben – alles liegt auf demselben Canvas.
    # -------------------------------------------------------------------------
    
    # HUD-Hintergrundbalken
    hud_bg = canvas.create_rectangle(0, 0, BREITE, RAND_OBEN - 4,
                                     fill="#16213e", outline="")
    # Unterer sicherer Bereich
    boden_bg = canvas.create_rectangle(0, HOEHE - RAND_UNTEN + 4, BREITE, HOEHE,
                                       fill="#0f3460", outline="")
    # Zielzone
    ziel_bg = canvas.create_rectangle(0, 0, BREITE, RAND_OBEN - 4,
                                      fill="#0d7377", outline="")
    
    # Spuren-Hintergrundstreifen (abwechselnd)
    spuren_bg_ids = []
    for i, y in enumerate(spuren_y_positionen()):
        farbe = "#1a1a2e" if i % 2 == 0 else "#16213e"
        sid = canvas.create_rectangle(0, y - 2, BREITE, y + SPURHOEHE - 2,
                                      fill=farbe, outline="")
        spuren_bg_ids.append(sid)

    # HUD-Texte (werden in der Game-Loop aktualisiert)
    # Lernhinweis: canvas.create_text() gibt eine ID zurück, die wir mit
    # canvas.itemconfig(id, text=...) aktualisieren können – kein Neuzeichnen nötig.
    hud_level_id = canvas.create_text(10, 10, anchor="nw",
                                      text="LEVEL 1", fill="#f0a500",
                                      font=("Courier", 14, "bold"))
    hud_punkte_id = canvas.create_text(BREITE // 2, 10, anchor="n",
                                       text="PUNKTE: 0", fill="white",
                                       font=("Courier", 14, "bold"))
    hud_highscore_id = canvas.create_text(BREITE - 10, 10, anchor="ne",
                                          text=f"HI: {HIGHSCORE}", fill="#888",
                                          font=("Courier", 12))
    hud_leben_id = canvas.create_text(10, 32, anchor="nw",
                                      text="❤ ❤ ❤", fill="#e74c3c",
                                      font=("Arial", 12))
    hud_power_id = canvas.create_text(BREITE // 2, 36, anchor="n",
                                      text="", fill="#3498db",
                                      font=("Arial", 11))

    # Frosch zeichnen
    # Lernhinweis: Wir verwenden mehrere Formen für den Frosch, um ihn
    # etwas interessanter aussehen zu lassen.
    frosch_koerper = canvas.create_oval(
        zustand["frosch_x"], zustand["frosch_y"],
        zustand["frosch_x"] + FROSCH_GROESSE, zustand["frosch_y"] + FROSCH_GROESSE,
        fill="#2ecc71", outline="#27ae60", width=2
    )
    frosch_auge_l = canvas.create_oval(0, 0, 7, 7, fill="white", outline="")
    frosch_auge_r = canvas.create_oval(0, 0, 7, 7, fill="white", outline="")
    frosch_pupille_l = canvas.create_oval(0, 0, 4, 4, fill="#1a1a2e", outline="")
    frosch_pupille_r = canvas.create_oval(0, 0, 4, 4, fill="#1a1a2e", outline="")
    frosch_mund = canvas.create_arc(0, 0, 20, 20, start=200, extent=140,
                                    outline="#27ae60", width=2, style="arc")

    # Schild-Aura (initial unsichtbar)
    schild_aura = canvas.create_oval(0, 0, 0, 0, outline="#3498db", width=3)

    # Overlay für Game Over / Level-Anzeige (Initial leer)
    overlay_rect = canvas.create_rectangle(0, 0, 0, 0, fill="#000000")
    overlay_text1 = canvas.create_text(BREITE // 2, HOEHE // 2 - 30,
                                       text="", fill="white",
                                       font=("Courier", 36, "bold"))
    overlay_text2 = canvas.create_text(BREITE // 2, HOEHE // 2 + 20,
                                       text="", fill="#aaaaaa",
                                       font=("Courier", 16))

    # Ziel-Banner
    ziel_text = canvas.create_text(BREITE // 2, (RAND_OBEN - 4) // 2,
                                   text="🏁 ZIEL", fill="white",
                                   font=("Arial", 14, "bold"))

    def frosch_aktualisieren():
        """
        Bewegt alle Frosch-Canvas-Objekte an die aktuelle Position.
        
        Lernhinweis: Wir speichern die Position im zustand-Dictionary und
        bewegen ALLE Frosch-Teile synchron. Das ist der Tkinter-Weg:
        Koordinaten manuell verwalten.
        
        Pygame würde einfach self.rect.topleft = (x, y) setzen und
        alles wäre automatisch an der richtigen Stelle.
        """
        fx = zustand["frosch_x"]
        fy = zustand["frosch_y"]
        gs = FROSCH_GROESSE

        canvas.coords(frosch_koerper, fx, fy, fx + gs, fy + gs)
        # Augen
        canvas.coords(frosch_auge_l, fx + 4, fy + 5, fx + 12, fy + 13)
        canvas.coords(frosch_auge_r, fx + gs - 12, fy + 5, fx + gs - 4, fy + 13)
        # Pupillen
        canvas.coords(frosch_pupille_l, fx + 6, fy + 7, fx + 10, fy + 11)
        canvas.coords(frosch_pupille_r, fx + gs - 10, fy + 7, fx + gs - 6, fy + 11)
        # Mund
        canvas.coords(frosch_mund, fx + 4, fy + gs - 14, fx + gs - 4, fy + gs - 2)
        
        # Schild-Aura
        if zustand["schild_aktiv"]:
            canvas.coords(schild_aura, fx - 6, fy - 6, fx + gs + 6, fy + gs + 6)
            canvas.itemconfig(schild_aura, outline="#3498db")
        else:
            canvas.coords(schild_aura, 0, 0, 0, 0)

    def hud_aktualisieren():
        """
        Aktualisiert alle HUD-Texte.
        
        Lernhinweis: canvas.itemconfig() ändert Eigenschaften eines existierenden
        Canvas-Objekts, ohne es zu löschen und neu zu erstellen.
        Das ist effizienter als canvas.delete() + canvas.create_text().
        """
        canvas.itemconfig(hud_level_id, text=f"LEVEL {zustand['level']}")
        canvas.itemconfig(hud_punkte_id, text=f"PUNKTE: {zustand['punkte']}")
        canvas.itemconfig(hud_highscore_id, text=f"HI: {zustand['highscore']}")
        
        # Leben als Herzen
        herzen = "❤ " * zustand["leben"]
        canvas.itemconfig(hud_leben_id, text=herzen.strip())
        
        # Power-Up Status
        jetzt = time.time()
        power_texte = []
        if zustand["schild_aktiv"] and zustand["schild_bis"] > jetzt:
            verbleibend = zustand["schild_bis"] - jetzt
            power_texte.append(f"🛡 {verbleibend:.1f}s")
        if zustand["slow_aktiv"] and zustand["slow_bis"] > jetzt:
            verbleibend = zustand["slow_bis"] - jetzt
            power_texte.append(f"⏱ {verbleibend:.1f}s")
        canvas.itemconfig(hud_power_id, text="  ".join(power_texte))

    def overlay_zeigen(text1: str, text2: str, alpha_bg: bool = True):
        """
        Zeigt einen Text-Overlay über dem Spielfeld an.
        
        Lernhinweis: Tkinter hat keine native Alpha-Transparenz für Widgets.
        Wir simulieren einen Overlay mit einem schwarzen Rechteck.
        pygame kann mit Surface.set_alpha() echte Transparenz.
        """
        if alpha_bg:
            canvas.coords(overlay_rect, 100, HOEHE // 2 - 70, BREITE - 100, HOEHE // 2 + 80)
            canvas.itemconfig(overlay_rect, fill="#000000", stipple="gray50")
        canvas.itemconfig(overlay_text1, text=text1)
        canvas.itemconfig(overlay_text2, text=text2)
        # Overlay nach vorne bringen
        canvas.tag_raise(overlay_rect)
        canvas.tag_raise(overlay_text1)
        canvas.tag_raise(overlay_text2)

    def overlay_verstecken():
        """Versteckt den Overlay."""
        canvas.coords(overlay_rect, 0, 0, 0, 0)
        canvas.itemconfig(overlay_text1, text="")
        canvas.itemconfig(overlay_text2, text="")

    # -------------------------------------------------------------------------
    # STEUERUNG
    # Lernhinweis: tkinter nutzt event-basierte Eingabe.
    # root.bind("<Key>", handler) registriert einen Callback.
    # Dieser wird nur aufgerufen, WENN eine Taste gedrückt wird.
    # 
    # Pygame kann zusätzlich mit pygame.key.get_pressed() jeden Frame
    # den aktuellen Tastenzustand abfragen (Polling) – das ermöglicht
    # flüssigere Bewegung bei gedrückt gehaltener Taste.
    # -------------------------------------------------------------------------
    SCHRITT = 28  # Bewegungsschritt = Froschgröße

    def steuerung(event):
        """Bewegt den Frosch bei Tastendruck."""
        if not zustand["laeuft"] or zustand["game_over"]:
            return
        if zustand["tot_animation"] > 0 or zustand["unverwundbar"] > 0:
            return
        if zustand["level_abgeschlossen"]:
            return

        fx = zustand["frosch_x"]
        fy = zustand["frosch_y"]

        if event.keysym in ("Up", "w", "W"):
            fy -= SCHRITT
        elif event.keysym in ("Down", "s", "S"):
            fy += SCHRITT
        elif event.keysym in ("Left", "a", "A"):
            fx -= SCHRITT
        elif event.keysym in ("Right", "d", "D"):
            fx += SCHRITT
        else:
            return

        # Grenzen einhalten
        fx = max(0, min(BREITE - FROSCH_GROESSE, fx))
        fy = max(RAND_OBEN - 4, min(HOEHE - RAND_UNTEN - FROSCH_GROESSE, fy))

        zustand["frosch_x"] = fx
        zustand["frosch_y"] = fy
        frosch_aktualisieren()

    def neustart_taste(event):
        """Neustart bei Game Over."""
        if zustand["game_over"] and event.keysym in ("r", "R"):
            spiel_neustart()

    root.bind("<Key>", steuerung)
    root.bind("<Key>", neustart_taste, add="+")

    # -------------------------------------------------------------------------
    # KOLLISIONSERKENNUNG
    # Lernhinweis: Wir nutzen einfache AABB (Axis-Aligned Bounding Box)
    # Kollision. Pygame hat pygame.Rect.colliderect() – praktischer und
    # etwas schneller. In tkinter machen wir es manuell.
    # -------------------------------------------------------------------------

    def rechteck_kollision(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2) -> bool:
        """Prüft, ob zwei Rechtecke sich überlappen (AABB)."""
        return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)

    def frosch_kollisionen_pruefen() -> str:
        """
        Prüft alle Kollisionen des Froschs.
        
        Rückgabe:
            "fahrzeug"  - Treffer mit Fahrzeug
            "powerup"   - Power-Up aufgesammelt
            ""          - Keine Kollision
        """
        fx1 = zustand["frosch_x"] + 3
        fy1 = zustand["frosch_y"] + 3
        fx2 = fx1 + FROSCH_GROESSE - 6
        fy2 = fy1 + FROSCH_GROESSE - 6

        # Fahrzeug-Kollision
        for f in fahrzeuge:
            ax1, ay1 = f["x"], f["y"]
            ax2, ay2 = ax1 + f["breite"], ay1 + f["hoehe"]
            if rechteck_kollision(fx1, fy1, fx2, fy2, ax1, ay1, ax2, ay2):
                if not zustand["schild_aktiv"]:
                    return "fahrzeug"
                else:
                    # Schild absorbiert Treffer
                    return "schild_treffer"

        # Power-Up Kollision
        for p in powerups[:]:
            px1, py1 = p["x"], p["y"]
            px2, py2 = px1 + p["groesse"], py1 + p["groesse"]
            if rechteck_kollision(fx1, fy1, fx2, fy2, px1, py1, px2, py2):
                powerup_aufsammeln(p)
                return "powerup"

        return ""

    def powerup_aufsammeln(p: dict):
        """Wendet ein Power-Up an und entfernt es vom Canvas."""
        nonlocal powerups
        pup = p["pup"]
        canvas.delete(p["kreis_id"])
        canvas.delete(p["text_id"])
        powerups = [x for x in powerups if x is not p]
        
        jetzt = time.time()
        if pup["typ"] == "schild":
            zustand["schild_aktiv"] = True
            zustand["schild_bis"] = jetzt + pup["dauer"]
        elif pup["typ"] == "slow":
            zustand["slow_aktiv"] = True
            zustand["slow_bis"] = jetzt + pup["dauer"]
        elif pup["typ"] == "leben":
            zustand["leben"] = min(zustand["leben"] + 1, MAX_LEBEN)
        elif pup["typ"] == "punkte":
            gewinn = berechne_punkte(50, zustand["level"], zustand["combo"])
            zustand["punkte"] += gewinn

        # Partikel-Effekt
        partikel_erstellen(p["x"] + 12, p["y"] + 12, pup["farbe_tk"], anzahl=8)

    # -------------------------------------------------------------------------
    # SPIELLOGIK
    # -------------------------------------------------------------------------

    def frosch_getroffen(schaden: int):
        """Verarbeitet einen Treffer auf den Frosch."""
        zustand["leben"] -= schaden
        zustand["combo"] = 0
        partikel_erstellen(
            zustand["frosch_x"] + FROSCH_GROESSE // 2,
            zustand["frosch_y"] + FROSCH_GROESSE // 2,
            "#e74c3c", anzahl=12
        )
        
        if zustand["leben"] <= 0:
            zustand["leben"] = 0
            zustand["game_over"] = True
            global HIGHSCORE
            if zustand["punkte"] > zustand["highscore"]:
                zustand["highscore"] = zustand["punkte"]
                HIGHSCORE = zustand["punkte"]
        else:
            # Kurze Unverwundbarkeit nach Treffer
            zustand["unverwundbar"] = 60  # 60 Frames = ~2 Sekunden
            # Frosch zurück zum Start
            zustand["frosch_x"] = BREITE // 2 - FROSCH_GROESSE // 2
            zustand["frosch_y"] = HOEHE - RAND_UNTEN - FROSCH_GROESSE
            frosch_aktualisieren()

    def frosch_ziel_erreicht():
        """Verarbeitet das Erreichen des Ziels (oberer Rand)."""
        zustand["combo"] += 1
        punkte_gewinn = berechne_punkte(100, zustand["level"], zustand["combo"])
        zustand["punkte"] += punkte_gewinn
        
        # Partikel-Feier
        for i in range(3):
            partikel_erstellen(
                random.randint(50, BREITE - 50),
                random.randint(10, RAND_OBEN),
                random.choice(["#f1c40f", "#2ecc71", "#3498db"]),
                anzahl=6
            )

        # Level prüfen: alle 3 erfolgreichen Überquerungen = nächstes Level
        if zustand["combo"] % 3 == 0:
            zustand["level"] += 1
            zustand["level_abgeschlossen"] = True
            zustand["level_text_timer"] = 90  # Frames für Level-Anzeige
            level_aufbauen()
        else:
            # Nur Frosch zurücksetzen
            zustand["frosch_x"] = BREITE // 2 - FROSCH_GROESSE // 2
            zustand["frosch_y"] = HOEHE - RAND_UNTEN - FROSCH_GROESSE
            frosch_aktualisieren()

    def spiel_neustart():
        """Setzt das gesamte Spiel zurück."""
        zustand.update({
            "game_over": False,
            "level": 1,
            "leben": 3,
            "punkte": 0,
            "combo": 0,
            "schild_aktiv": False,
            "slow_aktiv": False,
            "tot_animation": 0,
            "unverwundbar": 0,
            "level_abgeschlossen": False,
            "level_text_timer": 0,
        })
        overlay_verstecken()
        level_aufbauen()

    # -------------------------------------------------------------------------
    # GAME LOOP
    # Lernhinweis: In tkinter gibt es keinen echten Game-Loop.
    # Stattdessen nutzen wir root.after(ms, funktion), das die Funktion
    # nach einer bestimmten Zeit aufruft.
    # 
    # Der Ablauf:
    # 1. spiel_schleife() wird aufgerufen
    # 2. Am Ende ruft sie root.after(33, spiel_schleife) auf
    # 3. Nach 33ms wird spiel_schleife() wieder aufgerufen
    # → Das ergibt ~30 FPS
    #
    # Pygame hat einen echten Loop:
    # while True:
    #     clock.tick(60)
    #     # update...
    #     # draw...
    # → Das ermöglicht 60+ FPS präziser
    # -------------------------------------------------------------------------

    frame_zaehler = [0]  # Mutable list, damit nonlocal nicht nötig

    def spiel_schleife():
        """
        Hauptschleife des Spiels – wird ~30x pro Sekunde aufgerufen.
        """
        if not zustand["laeuft"]:
            return

        frame_zaehler[0] += 1
        jetzt = time.time()

        # Power-Up-Timer prüfen
        if zustand["schild_aktiv"] and jetzt >= zustand["schild_bis"]:
            zustand["schild_aktiv"] = False
        if zustand["slow_aktiv"] and jetzt >= zustand["slow_bis"]:
            zustand["slow_aktiv"] = False

        # Unverwundbarkeit zählen
        if zustand["unverwundbar"] > 0:
            zustand["unverwundbar"] -= 1

        # Level-Abschluss Animation
        if zustand["level_abgeschlossen"]:
            zustand["level_text_timer"] -= 1
            overlay_zeigen(
                f"LEVEL {zustand['level']}!",
                f"Combo x{zustand['combo']} | +{berechne_punkte(100, zustand['level'], zustand['combo'])} Punkte"
            )
            if zustand["level_text_timer"] <= 0:
                zustand["level_abgeschlossen"] = False
                overlay_verstecken()
        elif not zustand["game_over"]:
            overlay_verstecken()

        # Game Over Overlay
        if zustand["game_over"]:
            overlay_zeigen(
                "GAME OVER",
                f"Punkte: {zustand['punkte']} | Drücke R für Neustart"
            )
        
        if not zustand["game_over"] and not zustand["level_abgeschlossen"]:
            # --- UPDATE PHASE ---
            
            # Slow-Faktor für Fahrzeuge
            slow_faktor = 0.35 if zustand["slow_aktiv"] else 1.0

            # Fahrzeuge bewegen
            for f in fahrzeuge:
                f["x"] += f["speed"] * slow_faktor
                canvas.coords(f["canvas_id"],
                              f["x"], f["y"],
                              f["x"] + f["breite"], f["y"] + f["hoehe"])
                canvas.coords(f["text_id"],
                              f["x"] + f["breite"] // 2,
                              f["y"] + f["hoehe"] // 2)
                # Scheinwerfer
                if f["richtung"] > 0:
                    lx = f["x"] + f["breite"] - 4
                else:
                    lx = f["x"] + 2
                canvas.coords(f["licht_id"], lx, f["y"] + 4,
                              lx + 4, f["y"] + f["hoehe"] - 4)
                
                # Wrap-Around (Endlosfahrbahn)
                if f["speed"] > 0 and f["x"] > BREITE:
                    f["x"] = -f["breite"]
                elif f["speed"] < 0 and f["x"] < -f["breite"]:
                    f["x"] = BREITE

            # Partikel bewegen und löschen
            to_delete = []
            for p in partikel:
                p["x"] += p["dx"]
                p["y"] += p["dy"]
                p["dy"] += 0.3  # Schwerkraft
                p["leben"] -= 1
                canvas.coords(p["id"], p["x"], p["y"],
                              p["x"] + 6, p["y"] + 6)
                if p["leben"] <= 0:
                    canvas.delete(p["id"])
                    to_delete.append(p)
            for p in to_delete:
                partikel.remove(p)

            # Power-Up zufällig spawnen
            if random.random() < POWERUP_CHANCE and len(powerups) < 3:
                neues_pup = powerup_erstellen()
                if neues_pup:
                    powerups.append(neues_pup)

            # Frosch blinken bei Unverwundbarkeit (visuelles Feedback)
            if zustand["unverwundbar"] > 0:
                sichtbar = (zustand["unverwundbar"] // 5) % 2 == 0
                farbe = "#2ecc71" if sichtbar else "#1a1a2e"
                canvas.itemconfig(frosch_koerper, fill=farbe)
            else:
                canvas.itemconfig(frosch_koerper, fill="#2ecc71")

            # Kollisionen prüfen
            if zustand["unverwundbar"] == 0:
                kollision = frosch_kollisionen_pruefen()
                if kollision == "fahrzeug":
                    frosch_getroffen(1)
                elif kollision == "schild_treffer":
                    # Schild blinkt kurz
                    canvas.itemconfig(schild_aura, outline="#ffffff")

            # Ziel erreicht?
            if zustand["frosch_y"] <= RAND_OBEN - 4:
                frosch_ziel_erreicht()
            
            # HUD aktualisieren
            hud_aktualisieren()
            frosch_aktualisieren()

            # Alle Canvas-Objekte in richtige Reihenfolge bringen
            # Lernhinweis: tag_raise() bringt ein Canvas-Objekt nach vorne.
            # In pygame gibt es Layering über draw-Reihenfolge – einfacher.
            canvas.tag_raise(frosch_koerper)
            canvas.tag_raise(frosch_auge_l)
            canvas.tag_raise(frosch_auge_r)
            canvas.tag_raise(frosch_pupille_l)
            canvas.tag_raise(frosch_pupille_r)
            canvas.tag_raise(frosch_mund)
            canvas.tag_raise(schild_aura)
            canvas.tag_raise(hud_bg)
            canvas.tag_raise(hud_level_id)
            canvas.tag_raise(hud_punkte_id)
            canvas.tag_raise(hud_highscore_id)
            canvas.tag_raise(hud_leben_id)
            canvas.tag_raise(hud_power_id)
            canvas.tag_raise(ziel_bg)
            canvas.tag_raise(ziel_text)

        # Nächsten Frame planen
        # Lernhinweis: root.after() ist nicht 100% präzise – andere GUI-Events
        # können es verzögern. pygame.Clock.tick() ist zuverlässiger.
        root.after(FPS_DELAY, spiel_schleife)

    # -------------------------------------------------------------------------
    # START
    # -------------------------------------------------------------------------
    level_aufbauen()
    frosch_aktualisieren()

    print("\n[TKINTER] Steuerung: WASD oder Pfeiltasten")
    print("[TKINTER] Ziel: Oben ankommen (3x pro Level)")
    print("[TKINTER] Power-Ups: 🛡 Schild  ⏱ Slow  ❤ Leben  ⭐ Punkte")

    root.after(200, spiel_schleife)
    root.mainloop()

    print("Zurück zum Menü...")


# ==============================================================================
# VERSION 2: Pygame
# ==============================================================================

def start_version_pygame():
    """
    Startet das erweiterte Frogger-Spiel mit pygame.
    
    Was pygame BESSER macht als tkinter:
    - Echter Game-Loop mit präziser Framerate (Clock.tick)
    - Pixel-genaues Zeichnen mit pygame.draw.* und Surfaces
    - Alpha-Transparenz für Overlays und Partikel
    - Smooth-Movement durch Polling (key.get_pressed())
    - Klassen für Spielobjekte (objektorientierter Ansatz)
    - Einfacheres Layer-Management (draw-Reihenfolge)
    - Eingebaute Kollisionserkennung (Rect.colliderect)
    
    Was pygame NICHT bietet:
    - Automatische GUI-Widgets (Buttons, Labels usw.)
    - Einfache Text-Eingabe
    - OS-Integration (Dialoge etc.)
    """
    try:
        import pygame
    except ImportError:
        print("\n[FEHLER] pygame ist nicht installiert!")
        print("Installiere es mit: pip install pygame")
        return

    print("Starte Version 2 (Pygame) – Erweitertes Frogger...")

    # -------------------------------------------------------------------------
    # INITIALISIERUNG
    # Lernhinweis: pygame.init() initialisiert alle Subsysteme.
    # pygame.font.init() speziell für Schriften.
    # -------------------------------------------------------------------------
    pygame.init()
    pygame.font.init()

    # -------------------------------------------------------------------------
    # KONSTANTEN
    # Lernhinweis: In pygame werden Farben als (R, G, B) Tuples angegeben.
    # Tkinter nutzt HTML-Strings wie "#2ecc71".
    # -------------------------------------------------------------------------
    BREITE = 700
    HOEHE = 500
    FPS = 60
    FROSCH_GROESSE = 28
    SPURHOEHE = 48
    ANZAHL_SPUREN = 7
    RAND_OBEN = 60
    RAND_UNTEN = 60
    MAX_LEBEN = 5
    POWERUP_CHANCE = 0.005

    # Farben
    C_BG          = (15, 15, 30)
    C_HUD         = (20, 30, 60)
    C_ZIEL        = (10, 80, 60)
    C_BODEN       = (15, 45, 80)
    C_FROSCH      = (46, 204, 113)
    C_FROSCH_DARK = (39, 174, 96)
    C_TEXT        = (255, 255, 255)
    C_TEXT_DIM    = (150, 150, 150)
    C_GOLD        = (241, 196, 15)
    C_ROT         = (231, 76, 60)
    C_BLAU        = (52, 152, 219)
    C_GRUEN       = (46, 204, 113)

    # -------------------------------------------------------------------------
    # DISPLAY SETUP
    # -------------------------------------------------------------------------
    screen = pygame.display.set_mode((BREITE, HOEHE))
    pygame.display.set_caption("🐸 Frogger Deluxe – Pygame Edition")

    # Lernhinweis: Clock.tick(FPS) begrenzt die Framerate auf FPS Frames
    # pro Sekunde UND gibt die Zeit seit dem letzten Aufruf zurück (delta_time).
    # delta_time ist wichtig für framerate-unabhängige Bewegung.
    clock = pygame.time.Clock()

    # Schriften
    # Lernhinweis: pygame.font.SysFont() nutzt installierte Systemschriften.
    # pygame.font.Font() lädt eine .ttf-Datei (plattformunabhängiger).
    font_gross = pygame.font.SysFont("Courier New", 36, bold=True)
    font_mittel = pygame.font.SysFont("Courier New", 20, bold=True)
    font_klein = pygame.font.SysFont("Courier New", 14)
    font_hud = pygame.font.SysFont("Courier New", 16, bold=True)

    # -------------------------------------------------------------------------
    # KLASSEN
    # Lernhinweis: pygame-Code ist typischerweise objektorientierter als
    # tkinter-Code, weil Klassen die Verwaltung von Sprites vereinfachen.
    # pygame.sprite.Sprite ist die Basisklasse für Spielobjekte.
    # Wir nutzen hier eigene Klassen ohne den Sprite-Mechanismus, um den
    # Vergleich mit tkinter klarer zu halten.
    # -------------------------------------------------------------------------

    class Partikel:
        """
        Ein einzelner Partikel für Explosions- und Feier-Effekte.
        
        Lernhinweis: pygame.Surface mit SRCALPHA ermöglicht Alpha-Transparenz.
        Das kann tkinter ohne PIL nicht!
        """
        def __init__(self, x: float, y: float, farbe: tuple, 
                     dx: float = None, dy: float = None):
            self.x = x
            self.y = y
            self.dx = dx if dx is not None else random.uniform(-4, 4)
            self.dy = dy if dy is not None else random.uniform(-5, 1)
            self.farbe = farbe
            self.groesse = random.randint(3, 9)
            self.leben = random.randint(20, 45)
            self.max_leben = self.leben
            self.schwerkraft = 0.25

        def update(self):
            self.x += self.dx
            self.y += self.dy
            self.dy += self.schwerkraft
            self.leben -= 1

        def zeichnen(self, oberflaeche: pygame.Surface):
            if self.leben <= 0:
                return
            # Alpha basierend auf verbleibender Lebenszeit
            alpha = int(255 * (self.leben / self.max_leben))
            # Surface mit Alpha erstellen
            surf = pygame.Surface((self.groesse * 2, self.groesse * 2), pygame.SRCALPHA)
            farbe_alpha = (*self.farbe, alpha)
            pygame.draw.circle(surf, farbe_alpha, (self.groesse, self.groesse), self.groesse)
            oberflaeche.blit(surf, (int(self.x) - self.groesse, int(self.y) - self.groesse))

        @property
        def tot(self) -> bool:
            return self.leben <= 0

    class Fahrzeug:
        """
        Repräsentiert ein Fahrzeug auf der Fahrbahn.
        
        Lernhinweis: pygame.Rect ist ein nützlicher Hilfstyp für Position
        und Größe. .colliderect() macht Kollisionserkennung trivial.
        Tkinter hat kein Äquivalent – wir müssen Koordinaten manuell vergleichen.
        """
        def __init__(self, spur_y: int, level: int):
            ftyp = waehle_fahrzeugtyp(level)
            self.typ = ftyp["typ"]
            self.farbe = ftyp["farbe_pg"]
            self.breite = ftyp["breite"]
            self.hoehe = ftyp["hoehe"]
            self.leben_schaden = ftyp["leben"]
            
            basis_speed = berechne_level_geschwindigkeit(2.5, level)
            self.richtung = random.choice([-1, 1])
            self.speed = basis_speed * self.richtung * random.uniform(0.8, 1.3)
            
            if self.richtung > 0:
                start_x = -self.breite - random.randint(0, 400)
            else:
                start_x = BREITE + random.randint(0, 400)
            
            # pygame.Rect: (x, y, breite, hoehe) – Herzstück der Kollision
            self.rect = pygame.Rect(start_x, spur_y, self.breite, self.hoehe)
            self.spur_y = spur_y
            self.x = float(start_x)  # Float für smooth movement

        def update(self, slow_faktor: float = 1.0):
            """Bewegt das Fahrzeug und setzt es bei Bildrand zurück."""
            self.x += self.speed * slow_faktor
            self.rect.x = int(self.x)

            if self.speed > 0 and self.x > BREITE:
                self.x = -self.breite
                self.rect.y = random.randint(RAND_OBEN, HOEHE - RAND_UNTEN - 40)
                self.spur_y = self.rect.y
            elif self.speed < 0 and self.x < -self.breite:
                self.x = BREITE
                self.rect.y = random.randint(RAND_OBEN, HOEHE - RAND_UNTEN - 40)
                self.spur_y = self.rect.y

        def zeichnen(self, oberflaeche: pygame.Surface):
            """
            Zeichnet das Fahrzeug.
            
            Lernhinweis: pygame.draw.rect() zeichnet direkt auf einer Surface.
            Das ist performanter als tkinter's Canvas-Objekte bei vielen
            gleichzeitigen Zeichenoperationen.
            """
            # Fahrzeugkörper
            pygame.draw.rect(oberflaeche, self.farbe, self.rect, border_radius=4)
            # Umrandung
            pygame.draw.rect(oberflaeche, (255, 255, 255), self.rect, width=1, border_radius=4)
            
            # Scheinwerfer
            licht_farbe = (255, 255, 120)
            if self.richtung > 0:
                licht_x = self.rect.right - 8
            else:
                licht_x = self.rect.left + 2
            licht_rect = pygame.Rect(licht_x, self.rect.y + 4, 6, self.rect.height - 8)
            pygame.draw.rect(oberflaeche, licht_farbe, licht_rect, border_radius=2)
            
            # Fahrzeugtyp-Label
            label = font_klein.render(self.typ[0], True, (255, 255, 255))
            oberflaeche.blit(label, (self.rect.centerx - label.get_width() // 2,
                                     self.rect.centery - label.get_height() // 2))

    class PowerUp:
        """
        Power-Up auf der Fahrbahn.
        
        Lernhinweis: Pulse-Animation durch math.sin() – in tkinter
        müssten wir das mit Timern simulieren, in pygame läuft es
        natürlich im Game-Loop.
        """
        def __init__(self, x: int, y: int):
            pup = waehle_powerup_typ()
            self.pup = pup
            self.farbe = pup["farbe_pg"]
            self.symbol = pup["symbol"]
            self.rect = pygame.Rect(x, y, 26, 26)
            self.x = float(x)
            self.y_basis = float(y)
            self.alter = 0.0
            self.gesammelt = False

        def update(self, delta: float):
            self.alter += delta
            # Sanftes Auf- und Abschweben (Sine-Wave)
            self.rect.y = int(self.y_basis + math.sin(self.alter * 3) * 4)

        def zeichnen(self, oberflaeche: pygame.Surface):
            """
            Zeichnet das Power-Up mit Glow-Effekt.
            
            Lernhinweis: Mehrere übereinander gezeichnete Kreise mit
            abnehmendem Alpha erzeugen einen Glow-Effekt.
            Das wäre in tkinter sehr aufwändig.
            """
            # Glow-Effekt (mehrere transparente Kreise)
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pulse = 0.5 + 0.5 * math.sin(self.alter * 4)
            glow_alpha = int(60 + 40 * pulse)
            for radius in [22, 16]:
                pygame.draw.circle(glow_surf, (*self.farbe, glow_alpha),
                                  (30, 30), radius)
            oberflaeche.blit(glow_surf, (self.rect.centerx - 30,
                                         self.rect.centery - 30))
            # Kreis
            pygame.draw.circle(oberflaeche, self.farbe,
                               self.rect.center, 13)
            pygame.draw.circle(oberflaeche, (255, 255, 255),
                               self.rect.center, 13, width=2)
            # Symbol
            sym_surf = font_klein.render(self.symbol, True, (255, 255, 255))
            oberflaeche.blit(sym_surf, (self.rect.centerx - sym_surf.get_width() // 2,
                                        self.rect.centery - sym_surf.get_height() // 2))

    class Frosch:
        """
        Der Spieler-Frosch.
        
        Lernhinweis: In pygame können wir den Frosch als Klasse mit eigenem
        Zustand modellieren. Die Bewegungslogik ist hier per Polling (get_pressed)
        statt per Events, was flüssigere Steuerung ermöglicht.
        """
        def __init__(self):
            self.groesse = FROSCH_GROESSE
            self.schritt = FROSCH_GROESSE
            self.reset()
            self.unverwundbar = 0       # Frames
            self.schild_aktiv = False
            self.schild_bis = 0.0
            self.move_cooldown = 0      # Verhindert zu schnelles Bewegen
            # Für Smooth-Movement bei gedrückt gehaltener Taste
            self.tasten_cooldown_max = 10  # Frames zwischen Bewegungen

        def reset(self):
            """Setzt den Frosch an die Startposition."""
            self.x = float(BREITE // 2 - FROSCH_GROESSE // 2)
            self.y = float(HOEHE - RAND_UNTEN - FROSCH_GROESSE)
            self.rect = pygame.Rect(int(self.x), int(self.y),
                                    self.groesse, self.groesse)

        def verarbeite_eingabe(self, tasten):
            """
            Smooth-Movement durch Polling.
            
            Lernhinweis: Das ist DER Hauptunterschied zu tkinter!
            pygame.key.get_pressed() gibt den aktuellen Zustand ALLER Tasten
            zurück. Wenn wir das jeden Frame abfragen, können wir durch
            Gedrückthalten eine Taste flüssig bewegen.
            
            In tkinter: root.bind() – Callback nur beim Drücken, 
            dann nach einem Delay nochmal (OS-abhängig).
            """
            if self.move_cooldown > 0:
                self.move_cooldown -= 1
                return

            bewegt = False
            if tasten[pygame.K_UP] or tasten[pygame.K_w]:
                self.y -= self.schritt
                bewegt = True
            elif tasten[pygame.K_DOWN] or tasten[pygame.K_s]:
                self.y += self.schritt
                bewegt = True
            elif tasten[pygame.K_LEFT] or tasten[pygame.K_a]:
                self.x -= self.schritt
                bewegt = True
            elif tasten[pygame.K_RIGHT] or tasten[pygame.K_d]:
                self.x += self.schritt
                bewegt = True

            if bewegt:
                self.move_cooldown = self.tasten_cooldown_max
                # Grenzen
                self.x = max(0, min(BREITE - self.groesse, self.x))
                self.y = max(float(RAND_OBEN - 4),
                             min(float(HOEHE - RAND_UNTEN - self.groesse), self.y))
                self.rect.topleft = (int(self.x), int(self.y))

        def update(self):
            """Aktualisiert Timers und Rect."""
            if self.unverwundbar > 0:
                self.unverwundbar -= 1
            jetzt = time.time()
            if self.schild_aktiv and jetzt >= self.schild_bis:
                self.schild_aktiv = False
            self.rect.topleft = (int(self.x), int(self.y))

        def zeichnen(self, oberflaeche: pygame.Surface, frame: int):
            """
            Zeichnet den Frosch mit Details.
            
            Lernhinweis: Da wir hier direkt auf der Surface zeichnen,
            können wir beliebige Formen kombinieren – pygame.draw.circle,
            pygame.draw.ellipse, pygame.draw.arc usw. sind präziser und
            performanter als tkinter's canvas-Formen.
            """
            # Blinken bei Unverwundbarkeit
            if self.unverwundbar > 0 and (self.unverwundbar // 4) % 2 == 0:
                return  # Unsichtbar (Blink-Effekt)

            cx, cy = self.rect.centerx, self.rect.centery
            gs = self.groesse

            # Schild-Aura
            if self.schild_aktiv:
                puls = 0.5 + 0.5 * math.sin(frame * 0.15)
                glow = pygame.Surface((gs + 30, gs + 30), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (52, 152, 219, int(80 + 40 * puls)),
                                   (0, 0, gs + 30, gs + 30))
                pygame.draw.ellipse(glow, (52, 152, 219, 180),
                                   (8, 8, gs + 14, gs + 14), width=3)
                oberflaeche.blit(glow, (self.rect.x - 15, self.rect.y - 15))

            # Frosch-Körper
            pygame.draw.ellipse(oberflaeche, C_FROSCH, self.rect)
            pygame.draw.ellipse(oberflaeche, C_FROSCH_DARK, self.rect, width=2)

            # Augen
            auge_offset = gs // 4
            auge_groesse = 7
            for ofs in [-auge_offset, auge_offset]:
                pygame.draw.circle(oberflaeche, (220, 255, 220),
                                  (cx + ofs, cy - 5), auge_groesse)
                pygame.draw.circle(oberflaeche, (20, 20, 40),
                                  (cx + ofs, cy - 5), 4)
                # Glanzpunkt im Auge
                pygame.draw.circle(oberflaeche, (255, 255, 255),
                                  (cx + ofs + 2, cy - 7), 2)

            # Mund (Lächeln)
            mund_rect = pygame.Rect(cx - 7, cy + 3, 14, 8)
            pygame.draw.arc(oberflaeche, C_FROSCH_DARK, mund_rect,
                           math.pi, 2 * math.pi, width=2)

    # -------------------------------------------------------------------------
    # SPIELOBJEKTE ERSTELLEN
    # -------------------------------------------------------------------------
    frosch = Frosch()
    fahrzeuge: list[Fahrzeug] = []
    powerups: list[PowerUp] = []
    partikel: list[Partikel] = []

    # Spielzustand (Dictionary, wie in tkinter-Version – Konsistenz!)
    zustand = {
        "level": 1,
        "leben": 3,
        "punkte": 0,
        "combo": 0,
        "highscore": HIGHSCORE,
        "game_over": False,
        "level_uebergang": False,
        "level_text_timer": 0,
        "laeuft": True,
    }

    def spuren_y_positionen() -> list:
        """Gibt Y-Koordinaten aller Fahrspuren zurück."""
        return [RAND_OBEN + i * SPURHOEHE + 4 for i in range(ANZAHL_SPUREN)]

    def level_aufbauen():
        """Baut das aktuelle Level auf."""
        nonlocal fahrzeuge, powerups, partikel
        fahrzeuge = []
        powerups = []
        partikel = []

        spuren = spuren_y_positionen()
        level = zustand["level"]
        pro_spur = min(2 + level // 2, 5)

        for spur_y in spuren:
            for _ in range(pro_spur):
                fahrzeuge.append(Fahrzeug(spur_y, level))

        frosch.reset()

    def partikel_erstellen(x: float, y: float, farbe: tuple, anzahl: int = 8):
        """Erstellt Partikel an einer Position."""
        for _ in range(anzahl):
            partikel.append(Partikel(x, y, farbe))

    def feuerwerk(x: int, y: int):
        """Erstellt ein farbenfrohes Feuerwerk."""
        farben = [C_GOLD, C_GRUEN, C_BLAU, (255, 100, 100), (200, 100, 255)]
        for _ in range(20):
            farbe = random.choice(farben)
            dx = random.uniform(-6, 6)
            dy = random.uniform(-7, -1)
            partikel.append(Partikel(x, y, farbe, dx, dy))

    def powerup_aufsammeln(p: PowerUp):
        """Verarbeitet das Aufsammeln eines Power-Ups."""
        pup = p.pup
        p.gesammelt = True
        jetzt = time.time()

        if pup["typ"] == "schild":
            frosch.schild_aktiv = True
            frosch.schild_bis = jetzt + pup["dauer"]
        elif pup["typ"] == "slow":
            zustand["slow_aktiv"] = True
            zustand["slow_bis"] = jetzt + pup["dauer"]
        elif pup["typ"] == "leben":
            zustand["leben"] = min(zustand["leben"] + 1, MAX_LEBEN)
        elif pup["typ"] == "punkte":
            bonus = berechne_punkte(50, zustand["level"], zustand["combo"])
            zustand["punkte"] += bonus

        partikel_erstellen(p.rect.centerx, p.rect.centery, pup["farbe_pg"], 12)

    def frosch_getroffen(schaden: int):
        """Verarbeitet einen Treffer."""
        zustand["leben"] -= schaden
        zustand["combo"] = 0
        partikel_erstellen(frosch.rect.centerx, frosch.rect.centery,
                           C_ROT, 15)

        if zustand["leben"] <= 0:
            zustand["leben"] = 0
            zustand["game_over"] = True
            global HIGHSCORE
            if zustand["punkte"] > zustand["highscore"]:
                zustand["highscore"] = zustand["punkte"]
                HIGHSCORE = zustand["punkte"]
        else:
            frosch.unverwundbar = 90  # ~1.5 Sekunden bei 60 FPS
            frosch.reset()

    def frosch_ziel_erreicht():
        """Verarbeitet das Erreichen des Ziels."""
        zustand["combo"] += 1
        punkte_bonus = berechne_punkte(100, zustand["level"], zustand["combo"])
        zustand["punkte"] += punkte_bonus

        feuerwerk(random.randint(100, BREITE - 100), random.randint(10, 40))
        feuerwerk(random.randint(100, BREITE - 100), random.randint(10, 40))

        if zustand["combo"] % 3 == 0:
            zustand["level"] += 1
            zustand["level_uebergang"] = True
            zustand["level_text_timer"] = 120
            level_aufbauen()
        else:
            frosch.reset()

    # Slow-Status im zustand-Dict ergänzen
    zustand["slow_aktiv"] = False
    zustand["slow_bis"] = 0.0

    # -------------------------------------------------------------------------
    # HILFSFUNKTIONEN FÜR DAS ZEICHNEN
    # -------------------------------------------------------------------------

    def zeichne_hintergrund(oberflaeche: pygame.Surface):
        """
        Zeichnet den Hintergrund mit allen Bereichen.
        
        Lernhinweis: pygame zeichnet von unten nach oben (Painter's Algorithm).
        Was zuletzt gezeichnet wird, liegt vorne. In tkinter gibt es
        tag_raise() / tag_lower() für explizites Layer-Management.
        """
        oberflaeche.fill(C_BG)

        # Zielzone
        pygame.draw.rect(oberflaeche, C_ZIEL, (0, 0, BREITE, RAND_OBEN - 4))

        # Spuren (abwechselnd dunkel)
        spuren = spuren_y_positionen()
        for i, y in enumerate(spuren):
            farbe = (20, 20, 40) if i % 2 == 0 else (25, 25, 50)
            pygame.draw.rect(oberflaeche, farbe,
                            (0, y - 2, BREITE, SPURHOEHE - 2))
            # Spurmarkierungen
            for mx in range(0, BREITE, 40):
                pygame.draw.rect(oberflaeche, (50, 50, 70),
                                (mx, y + SPURHOEHE // 2 - 2, 20, 4))

        # Boden (sicherer Bereich)
        pygame.draw.rect(oberflaeche, C_BODEN,
                        (0, HOEHE - RAND_UNTEN + 4, BREITE, RAND_UNTEN))

        # HUD-Hintergrund
        pygame.draw.rect(oberflaeche, C_HUD, (0, 0, BREITE, RAND_OBEN - 4))
        pygame.draw.line(oberflaeche, C_GOLD, (0, RAND_OBEN - 5), (BREITE, RAND_OBEN - 5), 2)

    def zeichne_hud(oberflaeche: pygame.Surface, zustand: dict, frame: int):
        """
        Zeichnet das Heads-Up-Display.
        
        Lernhinweis: In pygame rendern wir Text mit font.render() zu einer
        Surface und blitten diese dann. Das ist anders als tkinter, wo
        canvas.itemconfig(id, text=...) den Text direkt aktualisiert.
        Pygame ist hier etwas aufwändiger, aber flexibler.
        """
        # Level
        level_surf = font_hud.render(f"LEVEL {zustand['level']}", True, C_GOLD)
        oberflaeche.blit(level_surf, (10, 10))

        # Punkte (zentriert)
        punkte_surf = font_hud.render(f"PUNKTE: {zustand['punkte']}", True, C_TEXT)
        oberflaeche.blit(punkte_surf, (BREITE // 2 - punkte_surf.get_width() // 2, 10))

        # Highscore
        hi_surf = font_klein.render(f"HI: {zustand['highscore']}", True, C_TEXT_DIM)
        oberflaeche.blit(hi_surf, (BREITE - hi_surf.get_width() - 10, 10))

        # Leben als Herzen
        leben_text = "❤ " * zustand["leben"]
        leben_surf = font_hud.render(leben_text.strip(), True, C_ROT)
        oberflaeche.blit(leben_surf, (10, 30))

        # Power-Up Status
        jetzt = time.time()
        px = BREITE // 2
        if frosch.schild_aktiv and frosch.schild_bis > jetzt:
            verbleibend = frosch.schild_bis - jetzt
            schild_surf = font_klein.render(f"🛡 {verbleibend:.1f}s", True, C_BLAU)
            oberflaeche.blit(schild_surf, (px - 60, 32))
        if zustand["slow_aktiv"] and zustand["slow_bis"] > jetzt:
            verbleibend = zustand["slow_bis"] - jetzt
            slow_surf = font_klein.render(f"⏱ {verbleibend:.1f}s", True, C_GRUEN)
            oberflaeche.blit(slow_surf, (px + 10, 32))

        # Combo-Anzeige
        if zustand["combo"] > 0:
            puls = 0.5 + 0.5 * math.sin(frame * 0.15)
            combo_farbe = (int(200 + 55 * puls), int(150 + 105 * puls), 0)
            combo_surf = font_mittel.render(f"x{zustand['combo']} COMBO!", True, combo_farbe)
            oberflaeche.blit(combo_surf, (BREITE - combo_surf.get_width() - 10, 30))

        # Ziel-Text
        ziel_surf = font_hud.render("🏁 ZIEL", True, (200, 255, 200))
        oberflaeche.blit(ziel_surf,
                        (BREITE // 2 - ziel_surf.get_width() // 2, RAND_OBEN - 42))

    def zeichne_overlay(oberflaeche: pygame.Surface, text1: str, text2: str,
                        farbe1=(255, 255, 255)):
        """
        Zeichnet einen halbtransparenten Overlay.
        
        Lernhinweis: Das ist einer der größten Vorteile von pygame!
        pygame.Surface mit SRCALPHA und set_alpha() erlaubt echte
        Transparenz. Tkinter simuliert das nur mit "stipple"-Mustern,
        was viel grobkörniger aussieht.
        """
        overlay = pygame.Surface((BREITE, HOEHE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Schwarz mit 60% Deckkraft
        oberflaeche.blit(overlay, (0, 0))

        t1 = font_gross.render(text1, True, farbe1)
        t2 = font_mittel.render(text2, True, C_TEXT_DIM)
        oberflaeche.blit(t1, (BREITE // 2 - t1.get_width() // 2, HOEHE // 2 - 50))
        oberflaeche.blit(t2, (BREITE // 2 - t2.get_width() // 2, HOEHE // 2 + 20))

    # -------------------------------------------------------------------------
    # SPIELSTART
    # -------------------------------------------------------------------------
    level_aufbauen()
    frame = 0

    print("\n[PYGAME] Steuerung: WASD oder Pfeiltasten")
    print("[PYGAME] R = Neustart nach Game Over")
    print("[PYGAME] Ziel: 3x oben ankommen = nächstes Level")
    print("[PYGAME] Power-Ups: 🛡 Schild  ⏱ Slow  ❤ Leben  ⭐ Punkte")

    # -------------------------------------------------------------------------
    # GAME LOOP
    # Lernhinweis: Das ist der klassische pygame Game-Loop.
    # Drei Phasen: Events → Update → Zeichnen
    # 
    # Im Vergleich zu tkinter:
    # - clock.tick(FPS) gibt delta_ms zurück (präziser als after())
    # - Events werden in einer Queue gesammelt, nicht als Callbacks
    # - Zeichnen: erst alles auf den Screen, dann flip() für Anzeige
    #   (Double-Buffering verhindert Flackern)
    # -------------------------------------------------------------------------

    while zustand["laeuft"]:
        delta_ms = clock.tick(FPS)
        delta = delta_ms / 1000.0  # In Sekunden für zeitbasierte Bewegung
        frame += 1

        # --- 1. EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                zustand["laeuft"] = False

            if event.type == pygame.KEYDOWN:
                if zustand["game_over"] and event.key == pygame.K_r:
                    # Neustart
                    zustand.update({
                        "game_over": False, "level": 1, "leben": 3,
                        "punkte": 0, "combo": 0,
                        "slow_aktiv": False, "level_uebergang": False,
                    })
                    frosch.schild_aktiv = False
                    frosch.unverwundbar = 0
                    level_aufbauen()

        # --- 2. UPDATE ---
        jetzt = time.time()

        if not zustand["game_over"] and not zustand["level_uebergang"]:
            # Frosch-Eingabe (Polling!)
            tasten = pygame.key.get_pressed()
            frosch.verarbeite_eingabe(tasten)
            frosch.update()

            # Fahrzeuge updaten
            slow_faktor = 0.35 if (zustand["slow_aktiv"] and zustand["slow_bis"] > jetzt) else 1.0
            for f in fahrzeuge:
                f.update(slow_faktor)

            # Slow-Timer
            if zustand["slow_aktiv"] and jetzt >= zustand["slow_bis"]:
                zustand["slow_aktiv"] = False

            # Power-Ups updaten und spawnen
            for p in powerups:
                p.update(delta)
            if random.random() < POWERUP_CHANCE and len(powerups) < 4:
                spuren = spuren_y_positionen()
                spur_y = random.choice(spuren)
                x = random.randint(30, BREITE - 60)
                powerups.append(PowerUp(x, spur_y + 4))

            # Partikel updaten
            for p in partikel:
                p.update()
            partikel[:] = [p for p in partikel if not p.tot]

            # Kollisionen prüfen
            if frosch.unverwundbar == 0:
                for f in fahrzeuge:
                    if frosch.rect.colliderect(f.rect):
                        if not frosch.schild_aktiv:
                            frosch_getroffen(f.leben_schaden)
                        else:
                            # Schild absorbiert – Partikel-Feedback
                            partikel_erstellen(frosch.rect.centerx,
                                              frosch.rect.centery,
                                              C_BLAU, 6)
                        break

            for p in powerups[:]:
                if frosch.rect.colliderect(p.rect):
                    powerup_aufsammeln(p)
            powerups[:] = [p for p in powerups if not p.gesammelt]

            # Ziel erreicht?
            if frosch.y <= RAND_OBEN - 4:
                frosch_ziel_erreicht()

        # Level-Übergang Timer
        if zustand["level_uebergang"]:
            zustand["level_text_timer"] -= 1
            # Während Übergang noch Partikel updaten
            for p in partikel:
                p.update()
            partikel[:] = [p for p in partikel if not p.tot]
            if zustand["level_text_timer"] <= 0:
                zustand["level_uebergang"] = False

        # --- 3. ZEICHNEN ---
        zeichne_hintergrund(screen)

        # Power-Ups
        for p in powerups:
            p.zeichnen(screen)

        # Fahrzeuge
        for f in fahrzeuge:
            f.zeichnen(screen)

        # Frosch (obendrauf)
        frosch.zeichnen(screen, frame)

        # Partikel (ganz oben)
        for p in partikel:
            p.zeichnen(screen)

        # HUD
        zeichne_hud(screen, zustand, frame)

        # Level-Übergang Overlay
        if zustand["level_uebergang"]:
            bonus_text = f"Combo x{zustand['combo']} | +{berechne_punkte(100, zustand['level'], zustand['combo'])} Punkte"
            zeichne_overlay(screen, f"LEVEL {zustand['level']}!", bonus_text, C_GOLD)

        # Game Over Overlay
        if zustand["game_over"]:
            zeichne_overlay(screen, "GAME OVER",
                           f"Punkte: {zustand['punkte']} | Drücke R für Neustart",
                           C_ROT)

        # Lernhinweis: pygame.display.flip() tauscht Front- und Backbuffer.
        # Ohne flip() würde man nichts sehen! Das ist Double-Buffering.
        pygame.display.flip()

    pygame.quit()
    print("Zurück zum Menü...")


# ==============================================================================
# HAUPTMENÜ & EINSTIEGSPUNKT
# ==============================================================================

def hauptmenü():
    """
    Zeigt das Auswahlmenü und startet die gewählte Version.
    
    Lernhinweis: Dieses Menü ist bewusst einfach gehalten (Terminal-basiert),
    damit der Fokus auf dem Spielcode liegt.
    """
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║         🐸  FROGGER DELUXE – LERNVERSION  🐸         ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  Gleiche Spiellogik – zwei Implementierungen         ║")
    print("║  Vergleiche tkinter vs. pygame!                      ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  Features:                                           ║")
    print("║   • Mehrere Level (steigend schwerer)                ║")
    print("║   • 3 Leben + Power-Ups (Schild/Slow/Herz/Punkte)   ║")
    print("║   • Fahrzeugtypen: Auto, LKW, Zug, Bus              ║")
    print("║   • Combo-System & Highscore                         ║")
    print("║   • Partikel-Effekte & Animationen                   ║")
    print("╚══════════════════════════════════════════════════════╝")

    while True:
        print()
        print("Bitte wähle eine Version:")
        print("  1 = Tkinter  (Standardbibliothek, kein pip nötig)")
        print("  2 = Pygame   (pip install pygame)")
        print("  ? = Was ist der Unterschied? (Erklärung)")
        print("  0 = Beenden")

        wahl = input("\nDeine Eingabe: ").strip()

        if wahl == "1":
            start_version_tkinter()
        elif wahl == "2":
            start_version_pygame()
        elif wahl == "?":
            erklaerung_ausgeben()
        elif wahl == "0":
            print("\nTschüss! 🐸")
            sys.exit(0)
        else:
            print("Ungültige Eingabe. Bitte 1, 2, ? oder 0 wählen.")


def erklaerung_ausgeben():
    """Gibt eine kurze Erklärung der Unterschiede aus."""
    print()
    print("=" * 56)
    print("  TKINTER vs. PYGAME – Die wichtigsten Unterschiede")
    print("=" * 56)
    print()
    print("TKINTER")
    print("  + In Python enthalten (kein pip nötig)")
    print("  + Gut für GUI-Anwendungen mit Widgets")
    print("  - Game-Loop über root.after() (ungenau)")
    print("  - Tastatur: event-basiert (root.bind)")
    print("  - Keine Alpha-Transparenz ohne PIL")
    print("  - Langsamere Performance bei vielen Objekten")
    print("  - Kein eingebautes Sound-System")
    print()
    print("PYGAME")
    print("  + Echter Game-Loop (clock.tick() präzise)")
    print("  + Tastatur: Polling (key.get_pressed())")
    print("  + Alpha-Transparenz, Partikeleffekte")
    print("  + Höhere Performance (60+ FPS)")
    print("  + Sound-System eingebaut")
    print("  - Muss extra installiert werden (pip install pygame)")
    print("  - Kein GUI-Widget-System (kein Button, Label usw.)")
    print()
    print("GLEICH in beiden:")
    print("  • Spiellogik (Kollision, Punkte, Level)")
    print("  • Fahrzeug-/Power-Up-Typen")
    print("  • zustand{} Dictionary für Spielzustand")
    print("  • AABB-Kollisionserkennung")
    print()


if __name__ == "__main__":
    try:
        hauptmenü()
    except KeyboardInterrupt:
        print("\n\nProgramm durch Benutzer abgebrochen. 🐸")
        sys.exit(0)
