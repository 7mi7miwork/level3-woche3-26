"""
Frogger Spiel - Zwei Versionen in einer Datei
=============================================
Dieses Programm bietet ein einfaches Frogger-Spiel.
Beim Start kann gewählt werden zwischen:
1. Version ohne pygame (nutzt tkinter aus der Standardbibliothek)
2. Version mit pygame (bessere Grafik und Performance)

Der Code ist für Lernzwecke kommentiert.
"""

import sys
import time
import random

# -----------------------------------------------------------------------------
# VERSION 1: Ohne pygame (mit tkinter)
# -----------------------------------------------------------------------------

def start_version_tkinter():
    """
    Startet die Version mit der Standardbibliothek tkinter.
    tkinter ist bei den meisten Python-Installationen dabei.
    """
    try:
        import tkinter as tk
    except ImportError:
        print("Fehler: tkinter ist nicht verfügbar.")
        return

    print("Starte Version 1 (Tkinter)...")

    # --- Konfiguration ---
    BREITE = 600
    HOEHE = 400
    GROESSE_FROSCH = 30
    GROESSE_AUTO = 60
    GESCHWINDIGKEIT_AUTO = 3
    
    # Spielzustand
    spiel_laeuft = True
    punkte = 0

    # Fenster erstellen
    root = tk.Tk()
    root.title("Frogger - Tkinter Version")
    root.resizable(False, False)

    # Canvas (Zeichenfläche) erstellen
    canvas = tk.Canvas(root, width=BREITE, height=HOEHE, bg="black")
    canvas.pack()

    # Frosch Position (Start unten mitte)
    frog_x = BREITE // 2
    frog_y = HOHE - GROESSE_FROSCH - 10

    # Frosch auf dem Canvas zeichnen (grünes Rechteck)
    frog_id = canvas.create_rectangle(
        frog_x, frog_y, 
        frog_x + GROESSE_FROSCH, frog_y + GROESSE_FROSCH, 
        fill="green", outline="white"
    )

    # Autos Liste: Jedes Auto ist ein Dictionary mit Koordinaten, Geschwindigkeit und Canvas-ID
    autos = []

    def auto_erstellen():
        """Erstellt ein neues Auto an zufälliger Y-Position."""
        y = random.randint(50, HOHE - 100) # Nicht zu nah am Rand
        x = random.choice([-GROESSE_AUTO, BREITE]) # Start links oder rechts
        speed = GESCHWINDIGKEIT_AUTO * random.choice([-1, 1]) # Richtung zufällig
        
        # Auto zeichnen (rotes Rechteck)
        auto_id = canvas.create_rectangle(
            x, y, x + GROESSE_AUTO, y + GROESSE_AUTO,
            fill="red", outline="yellow"
        )
        autos.append({"id": auto_id, "x": x, "y": y, "speed": speed})

    # Initial ein paar Autos erstellen
    for _ in range(5):
        auto_erstellen()

    def steuerung(event):
        """Bewegt den Frosch basierend auf Tasteneingabe."""
        nonlocal frog_x, frog_y, spiel_laeuft
        if not spiel_laeuft:
            return

        schritt = 20
        if event.keysym in ['Up', 'w', 'W']:
            frog_y -= schritt
        elif event.keysym in ['Down', 's', 'S']:
            frog_y += schritt
        elif event.keysym in ['Left', 'a', 'A']:
            frog_x -= schritt
        elif event.keysym in ['Right', 'd', 'D']:
            frog_x += schritt

        # Grenzen prüfen (Frosch bleibt im Fenster)
        frog_x = max(0, min(BREITE - GROESSE_FROSCH, frog_x))
        frog_y = max(0, min(HOEHE - GROESSE_FROSCH, frog_y))

        # Frosch neu positionieren
        canvas.coords(frog_id, frog_x, frog_y, frog_x + GROESSE_FROSCH, frog_y + GROESSE_FROSCH)

    def kollision_pruefen():
        """Prüft, ob der Frosch ein Auto berührt."""
        # Frosch Koordinaten holen
        fx1, fy1, fx2, fy2 = canvas.coords(frog_id)

        for auto in autos:
            # Auto Koordinaten holen
            ax1, ay1, ax2, ay2 = canvas.coords(auto["id"])

            # Einfache Rechteck-Kollision (Überlappung)
            if not (fx2 < ax1 or fx1 > ax2 or fy2 < ay1 or fy1 > ay2):
                return True # Kollision!
        return False

    def spiel_schleife():
        """
        Diese Funktion wird immer wieder aufgerufen (Game Loop).
        Sie bewegt die Autos und prüft den Spielstatus.
        """
        nonlocal spiel_laeuft, punkte, frog_x, frog_y

        if not spiel_laeuft:
            return

        # Autos bewegen
        for auto in autos:
            auto["x"] += auto["speed"]
            # Auto neu zeichnen
            canvas.coords(auto["id"], 
                          auto["x"], auto["y"], 
                          auto["x"] + GROESSE_AUTO, auto["y"] + GROESSE_AUTO)
            
            # Wenn Auto aus dem Bild fährt, zurücksetzen (Endlosschleife)
            if auto["speed"] > 0 and auto["x"] > BREITE:
                auto["x"] = -GROESSE_AUTO
            elif auto["speed"] < 0 and auto["x"] < -GROESSE_AUTO:
                auto["x"] = BREITE

        # Kollision prüfen
        if kollision_pruefen():
            spiel_laeuft = False
            canvas.create_text(BREITE//2, HOEHE//2, text="GAME OVER", fill="white", font=("Arial", 30))
            canvas.create_text(BREITE//2, HOEHE//2 + 40, text="Fenster schließen für Menü", fill="gray")
            return # Schleife stoppen

        # Gewinnbedingung: Oben angekommen (y < 20)
        if frog_y < 20:
            punkte += 1
            # Frosch zurücksetzen
            frog_x = BREITE // 2
            frog_y = HOHE - GROESSE_FROSCH - 10
            canvas.coords(frog_id, frog_x, frog_y, frog_x + GROESSE_FROSCH, frog_y + GROESSE_FROSCH)
            # Optional: Autos schneller machen oder mehr Autos
            # Hier einfach nur Meldung
            print(f"Punkt erreicht! Gesamt: {punkte}")

        # Nächsten Frame planen (ca. 30 FPS -> 1000ms / 30 ≈ 33ms)
        root.after(33, spiel_schleife)

    # Tastaturbindung
    root.bind("<Key>", steuerung)

    # Spiel starten
    root.after(100, spiel_schleife)
    
    # Hinweis im Terminal
    print("Steuerung: WASD oder Pfeiltasten. Fenster schließen zum Beenden.")

    # Tkinter Hauptloop starten (blockiert bis Fenster geschlossen wird)
    root.mainloop()
    print("Zurück zum Menü...")


# -----------------------------------------------------------------------------
# VERSION 2: Mit pygame
# -----------------------------------------------------------------------------

def start_version_pygame():
    """
    Startet die Version mit pygame.
    Prüft vorher, ob pygame installiert ist.
    """
    # Import versuchen (lokal, damit das Script ohne pygame nicht sofort crasht)
    try:
        import pygame
    except ImportError:
        print("\n[FEHLER] pygame ist nicht installiert!")
        print("Installiere es mit: pip install pygame")
        print("Zurück zum Menü...\n")
        return

    print("Starte Version 2 (Pygame)...")

    # --- Initialisierung ---
    pygame.init()
    
    # Konstanten
    BREITE = 600
    HOEHE = 400
    FPS = 60
    FROSCH_GROESSE = 30
    AUTO_GROESSE = (60, 30) # Breite, Höhe
    FARBE_HINTERGRUND = (30, 30, 30)
    FARBE_FROSCH = (0, 255, 0)
    FARBE_AUTO = (255, 50, 50)
    FARBE_TEXT = (255, 255, 255)

    # Fenster erstellen
    screen = pygame.display.set_mode((BREITE, HOEHE))
    pygame.display.set_caption("Frogger - Pygame Version")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # --- Klassen für Struktur ---
    
    class Frosch:
        def __init__(self):
            self.reset()
            self.rect = pygame.Rect(self.x, self.y, FROSCH_GROESSE, FROSCH_GROESSE)
            self.speed = 5

        def reset(self):
            self.x = BREITE // 2 - FROSCH_GROESSE // 2
            self.y = HOHE - FROSCH_GROESSE - 10
            self.rect.topleft = (self.x, self.y)

        def bewegen(self, dx, dy):
            self.x += dx * self.speed
            self.y += dy * self.speed
            
            # Grenzen
            self.x = max(0, min(BREITE - FROSCH_GROESSE, self.x))
            self.y = max(0, min(HOEHE - FROSCH_GROESSE, self.y))
            
            self.rect.topleft = (self.x, self.y)

        def zeichnen(self, oberflaeche):
            pygame.draw.rect(oberflaeche, FARBE_FROSCH, self.rect)

    class Auto:
        def __init__(self):
            self.reset()

        def reset(self):
            self.breite = AUTO_GROESSE[0]
            self.hoehe = AUTO_GROESSE[1]
            self.y = random.randint(50, HOHE - 100)
            # Zufällige Startposition links oder rechts
            self.x = random.choice([-self.breite, BREITE])
            # Geschwindigkeit (positiv = nach rechts, negativ = nach links)
            self.speed = random.choice([-3, -4, 3, 4])
            self.rect = pygame.Rect(self.x, self.y, self.breite, self.hoehe)

        def update(self):
            self.x += self.speed
            self.rect.topleft = (self.x, self.y)

            # Wenn aus dem Bild, zurücksetzen
            if self.speed > 0 and self.x > BREITE:
                self.x = -self.breite
                self.y = random.randint(50, HOHE - 100) # Neue Spur
            elif self.speed < 0 and self.x < -self.breite:
                self.x = BREITE
                self.y = random.randint(50, HOHE - 100) # Neue Spur
            
            self.rect.topleft = (self.x, self.y)

        def zeichnen(self, oberflaeche):
            pygame.draw.rect(oberflaeche, FARBE_AUTO, self.rect)

    # --- Spielobjekte ---
    frosch = Frosch()
    autos = [Auto() for _ in range(6)] # 6 Autos
    
    punkte = 0
    spiel_laeuft = True
    game_over = False

    # --- Game Loop ---
    while spiel_laeuft:
        clock.tick(FPS) # FPS begrenzen

        # 1. Events verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_laeuft = False
            
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    frosch.bewegen(0, -1)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    frosch.bewegen(0, 1)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    frosch.bewegen(-1, 0)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    frosch.bewegen(1, 0)
            
            # Bei Game Over Taste drücken zum Neustart
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Reset
                    frosch.reset()
                    for auto in autos:
                        auto.reset()
                    punkte = 0
                    game_over = False

        if not game_over:
            # 2. Update Logik
            for auto in autos:
                auto.update()
                # Kollision prüfen
                if frosch.rect.colliderect(auto.rect):
                    game_over = True

            # Gewinnbedingung (Oben erreicht)
            if frosch.y < 20:
                punkte += 1
                frosch.reset() # Frosch zurück zum Start
                # Optional: Schwierigkeit erhöhen (Autos schneller)
                for auto in autos:
                    auto.speed *= 1.1 

        # 3. Zeichnen
        screen.fill(FARBE_HINTERGRUND)

        # Zielzone markieren
        pygame.draw.rect(screen, (50, 50, 100), (0, 0, BREITE, 40))
        
        frosch.zeichnen(screen)
        for auto in autos:
            auto.zeichnen(screen)

        # UI Text
        text_punkte = font.render(f"Punkte: {punkte}", True, FARBE_TEXT)
        screen.blit(text_punkte, (10, 10))

        if game_over:
            text_go = font.render("GAME OVER - Drücke 'R' für Neustart", True, (255, 0, 0))
            text_rect = text_go.get_rect(center=(BREITE//2, HOEHE//2))
            screen.blit(text_go, text_rect)

        pygame.display.flip() # Bildschirm aktualisieren

    pygame.quit()
    print("Zurück zum Menü...")


# -----------------------------------------------------------------------------
# HAUPTMENÜ & EINSTIEGSPUNKT
# -----------------------------------------------------------------------------

def hauptmenü():
    """
    Zeigt das Auswahlmenü an und startet die gewünschte Version.
    """
    print("=" * 40)
    print("       WILLKOMMEN BEIM FROGGER SPIEL")
    print("=" * 40)
    
    while True:
        print("\nBitte wähle eine Version:")
        print("1 = Version ohne pygame (nur Standardbibliothek / Tkinter)")
        print("2 = Version mit pygame (bessere Grafik)")
        print("0 = Beenden")
        
        wahl = input("\nDeine Eingabe: ").strip()

        if wahl == "1":
            start_version_tkinter()
        elif wahl == "2":
            start_version_pygame()
        elif wahl == "0":
            print("Spiel wird beendet. Tschüss!")
            sys.exit(0)
        else:
            print("Ungültige Eingabe. Bitte 1, 2 oder 0 wählen.")

if __name__ == "__main__":
    try:
        hauptmenü()
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer abgebrochen.")
        sys.exit(0)
