# ============================================================
#  🐍 PYTHON QUIZ-SPIEL  –  Gemeinsam im Unterricht bauen!
#  Datei: Quiz.py
# ============================================================
#
#  WIR BAUEN DAS SPIEL IN 5 STUFEN:
#
#  STUFE 1 ✅  print() und input()          → Begrüssung
#  STUFE 2 ✅  if / elif / else             → Antworten prüfen
#  STUFE 3 ✅  Listen                       → Fragen speichern
#  STUFE 4 ✅  for-Schleife                 → Alle Fragen stellen
#  STUFE 5 ✅  Funktionen                   → Alles sauber machen
#
# ============================================================


# ============================================================
# STUFE 1 – print() und input()
# ============================================================
# Mit print() zeigen wir etwas auf dem Bildschirm.
# Mit input() fragen wir den Benutzer etwas.

def begruessung():
    print("=" * 40)
    print("   Willkommen beim Python-Quiz! 🐍")
    print("=" * 40)

    # TODO (Schüler ergänzen): Fragt nach dem Namen und speichert ihn
    name = input("Wie heisst du? ")

    print(f"Hallo, {name}! Viel Erfolg beim Quiz!")
    print()

    # Den Namen zurückgeben, damit wir ihn später brauchen können
    return name


# ============================================================
# STUFE 2 – if / elif / else
# ============================================================
# Wir prüfen, ob die Antwort des Spielers richtig ist.

def antwort_pruefen(antwort_spieler, richtige_antwort):
    # .strip()    → entfernt Leerzeichen am Anfang/Ende
    # .lower()    → macht alles kleinbuchstaben (Gross/Klein egal)
    antwort_spieler  = antwort_spieler.strip().lower()
    richtige_antwort = richtige_antwort.strip().lower()

    if antwort_spieler == richtige_antwort:
        print("✅ Richtig! Super!")
        return True                # True = Punkt bekommen
    else:
        print(f"❌ Leider falsch. Die Antwort war: {richtige_antwort}")
        return False               # False = kein Punkt


# ============================================================
# STUFE 3 – Listen
# ============================================================
# Wir speichern alle Fragen in einer Liste.
# Jede Frage ist ein Dictionary (Schlüssel → Wert).
#
# Aufbau:
#   {
#       "frage":   "...",        ← die Frage
#       "antwort": "...",        ← die richtige Antwort
#       "tipp":    "..."         ← ein kleiner Hinweis
#   }

def fragen_erstellen():
    fragen = [

        # --- Frage 1 ---
        {
            "frage":   "Was gibt print('Hallo') auf dem Bildschirm aus?",
            "antwort": "Hallo",
            "tipp":    "Genau das, was zwischen den Anführungszeichen steht!"
        },

        # --- Frage 2 ---
        {
            "frage":   "Welches Schlüsselwort benutzt man für eine Bedingung?",
            "antwort": "if",
            "tipp":    "Auf Deutsch bedeutet es 'falls' oder 'wenn'."
        },

        # --- Frage 3 ---
        {
            "frage":   "Wie lautet das Ergebnis von: 3 * 4?",
            "antwort": "12",
            "tipp":    "Das ist eine einfache Multiplikation."
        },

        # --- Frage 4 ---
        {
            "frage":   "Womit liest man eine Eingabe vom Benutzer ein?",
            "antwort": "input",
            "tipp":    "Diese Funktion haben wir ganz am Anfang benutzt!"
        },

        # --- Frage 5 ---
        {
            "frage":   "Was ist der Datentyp von: [1, 2, 3]?",
            "antwort": "list",
            "tipp":    "Auf Deutsch: Liste. type([1,2,3]) verrät es dir!"
        },

        # TODO (Schüler ergänzen): Fügt hier eigene Fragen hinzu!
        # Kopiert einfach den Block oben und ändert frage/antwort/tipp.

    ]

    return fragen


# ============================================================
# STUFE 4 – for-Schleife (und while als Extra)
# ============================================================
# Wir gehen alle Fragen der Reihe nach durch.

def quiz_spielen(name, fragen):
    punkte = 0
    frage_nummer = 1

    print(f"Los geht's, {name}! Es gibt {len(fragen)} Fragen.\n")

    # Die for-Schleife holt jede Frage einzeln aus der Liste
    for frage_dict in fragen:

        print(f"Frage {frage_nummer} von {len(fragen)}:")
        print(f"👉 {frage_dict['frage']}")

        # Tipp anbieten
        tipp_wunsch = input("   Willst du einen Tipp? (j/n) ")
        if tipp_wunsch.lower() == "j":
            print(f"   💡 Tipp: {frage_dict['tipp']}")

        # Antwort einlesen
        antwort = input("   Deine Antwort: ")

        # Antwort prüfen (Funktion aus Stufe 2)
        richtig = antwort_pruefen(antwort, frage_dict["antwort"])

        if richtig:
            punkte += 1    # Punkt dazuzählen

        print()            # Leerzeile für Übersicht
        frage_nummer += 1  # Nächste Frage

    return punkte


# ============================================================
# STUFE 5 – Funktionen & Auswertung
# ============================================================
# Am Ende zeigen wir das Ergebnis und bewerten es.

def ergebnis_anzeigen(name, punkte, gesamt):
    print("=" * 40)
    print(f"   Quiz beendet! Ergebnis für {name}:")
    print(f"   {punkte} von {gesamt} Punkten")
    print("=" * 40)

    # Prozentzahl ausrechnen
    prozent = (punkte / gesamt) * 100

    # Bewertung mit if / elif / else
    if prozent == 100:
        print("🏆 Perfekt! Du bist ein Python-Profi!")
    elif prozent >= 80:
        print("🎉 Sehr gut! Fast alles richtig!")
    elif prozent >= 60:
        print("👍 Gut gemacht! Weiter üben!")
    elif prozent >= 40:
        print("📚 Nicht schlecht, aber noch Luft nach oben.")
    else:
        print("💪 Nicht aufgeben – nochmal versuchen!")

    print()

    # TODO (Schüler ergänzen): Fragt, ob der Spieler nochmal spielen will
    # Tipp: input() + if + True/False zurückgeben


# ============================================================
# HAUPTPROGRAMM  –  Alles zusammensetzen
# ============================================================
# Diese Funktion ruft alle anderen Funktionen auf.

def main():
    # Stufe 1: Begrüssung
    name = begruessung()

    # Stufe 3: Fragen laden
    fragen = fragen_erstellen()

    # Stufe 4: Quiz spielen
    punkte = quiz_spielen(name, fragen)

    # Stufe 5: Ergebnis
    ergebnis_anzeigen(name, punkte, len(fragen))


# ============================================================
# EINSTIEGSPUNKT
# ============================================================
# Diese Zeile sorgt dafür, dass main() nur läuft,
# wenn wir die Datei direkt starten (nicht importieren).

if __name__ == "__main__":
    main()
