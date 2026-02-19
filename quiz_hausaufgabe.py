# ============================================================
#  🐍 PYTHON QUIZ-SPIEL  –  HAUSAUFGABE
#  Datei: quiz_hausaufgabe.py
# ============================================================
#
#  AUFGABE: Finde und korrigiere alle Fehler!
#  Es gibt in jeder Stufe mindestens einen Fehler.
#  Suche nach den Kommentaren mit  ❌ FEHLER
#
#  TIPP: Führe die Datei aus – Python zeigt dir wo es kracht!
#
#  STUFE 1 – print() und input()
#  STUFE 2 – if / elif / else
#  STUFE 3 – Listen / Dictionaries
#  STUFE 4 – for-Schleife
#  STUFE 5 – Funktionen & Auswertung
#
# ============================================================


# ============================================================
# STUFE 1 – print() und input()
# ============================================================
# print()  → zeigt etwas auf dem Bildschirm
# input()  → liest eine Eingabe vom Benutzer

def begruessung():
    Print("=" * 40)                          # ❌ FEHLER – Gross/Kleinschreibung!
    print("   Willkommen beim Python-Quiz! 🐍")
    print("=" * 40)

    name = Input("Wie heisst du? ")          # ❌ FEHLER – Gross/Kleinschreibung!

    print(f"Hallo, {name}! Viel Erfolg beim Quiz!")
    print()

    return name


# ============================================================
# STUFE 2 – if / elif / else
# ============================================================
# Wir prüfen, ob die Antwort des Spielers richtig ist.

def antwort_pruefen(antwort_spieler, richtige_antwort):
    # .strip()  → entfernt Leerzeichen am Anfang/Ende
    # .lower()  → macht alles kleinbuchstaben (Gross/Klein egal)
    antwort_spieler  = antwort_spieler.strip().lower()
    richtige_antwort = richtige_antwort.strip().lower()

    If antwort_spieler == richtige_antwort:  # ❌ FEHLER – Gross/Kleinschreibung!
        print("✅ Richtig! Super!")
        return True
    Else:                                    # ❌ FEHLER – Gross/Kleinschreibung!
        print(f"❌ Leider falsch. Die Antwort war: {richtige_antwort}")
        return False


# ============================================================
# STUFE 3 – Listen / Dictionaries
# ============================================================
# Jede Frage ist ein Dictionary mit drei Einträgen:
#   "frage"   → der Fragetext
#   "antwort" → die richtige Antwort
#   "tipp"    → ein Hinweis

def fragen_erstellen():
    fragen = [

        {
            "frage":   "Was gibt print('Hallo') auf dem Bildschirm aus?",
            "antwort": "Hallo",
            "tipp":    "Genau das, was zwischen den Anführungszeichen steht!"
        }                                    # ❌ FEHLER – fehlendes Trennzeichen zwischen Einträgen!

        {
            "frage":   "Welches Schlüsselwort benutzt man für eine Bedingung?",
            "antwort": "if",
            "tipp":    "Auf Deutsch bedeutet es 'falls' oder 'wenn'."
        },

        {
            "frage":   "Wie lautet das Ergebnis von: 3 * 4?",
            "antwort": "12",
            "tipp":    "Das ist eine einfache Multiplikation."
        },

        {
            "frage":   "Womit liest man eine Eingabe vom Benutzer ein?",
            "antwort": "input",
            "tipp":    "Diese Funktion haben wir ganz am Anfang benutzt!"
        },

        {
            "frage":   "Was ist der Datentyp von: [1, 2, 3]?",
            "antwort": "list",
            "tipp":    "Auf Deutsch: Liste. type([1,2,3]) verrät es dir!"
        },

    ]

    Return fragen                            # ❌ FEHLER – Gross/Kleinschreibung!


# ============================================================
# STUFE 4 – for-Schleife
# ============================================================
# Wir gehen alle Fragen der Reihe nach durch.

def quiz_spielen(name, fragen):
    punkte = 0
    frage_nummer = 1

    print(f"Los geht's, {name}! Es gibt {len(fragen)} Fragen.\n")

    For frage_dict in fragen:                # ❌ FEHLER – Gross/Kleinschreibung!

        print(f"Frage {frage_nummer} von {len(fragen)}:")
        print(f"👉 {frage_dict['frage']}")

        tipp_wunsch = input("   Willst du einen Tipp? (j/n) ")
        if tipp_wunsch.lower() == "j":
            print(f"   💡 Tipp: {frage_dict['tipp']}")

        antwort = input("   Deine Antwort: ")

        richtig = antwort_pruefen(antwort, frage_dict["antwort"])

        if richtig:
            punkte =+ 1                      # ❌ FEHLER – falscher Operator! (+=  vs  =+)

        print()
        frage_nummer += 1

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

    prozent = (punkte / gesamt) * 100

    if prozent == 100:
        print("🏆 Perfekt! Du bist ein Python-Profi!")
    Elif prozent >= 80:                      # ❌ FEHLER – Gross/Kleinschreibung!
        print("🎉 Sehr gut! Fast alles richtig!")
    elif prozent >= 60:
        print("👍 Gut gemacht! Weiter üben!")
    elif prozent >= 40
        print("📚 Nicht schlecht, aber noch Luft nach oben.")   # ❌ FEHLER – fehlendes Zeichen am Ende der Bedingung!
    else:
        print("💪 Nicht aufgeben – nochmal versuchen!")

    print()


# ============================================================
# HAUPTPROGRAMM
# ============================================================

def main():
    name = begruessung()
    fragen = fragen_erstellen()
    punkte = quiz_spielen(name, fragen)
    ergebnis_anzeigen(name, punkte, len(fragen))


if __name__ == "__main__":
    main()


# ============================================================
# 📋 CHECKLISTE FÜR SCHÜLER
# ============================================================
#
#  Hast du alle Fehler gefunden? Hier die Liste zum Abhaken:
#
#  STUFE 1:
#   [ ] Fehler 1 – Zeile ~20  : falscher Befehl (Gross/Klein)
#   [ ] Fehler 2 – Zeile ~23  : falscher Befehl (Gross/Klein)
#
#  STUFE 2:
#   [ ] Fehler 3 – Zeile ~37  : falsches Schlüsselwort
#   [ ] Fehler 4 – Zeile ~40  : falsches Schlüsselwort
#
#  STUFE 3:
#   [ ] Fehler 5 – Zeile ~58  : fehlendes Zeichen zwischen zwei Einträgen
#   [ ] Fehler 6 – Zeile ~80  : falscher Befehl (Gross/Klein)
#
#  STUFE 4:
#   [ ] Fehler 7 – Zeile ~92  : falsches Schlüsselwort
#   [ ] Fehler 8 – Zeile ~103 : falscher Operator
#
#  STUFE 5:
#   [ ] Fehler 9 – Zeile ~120 : falsches Schlüsselwort
#   [ ] Fehler 10 – Zeile ~122 : fehlendes Zeichen
#
#  Insgesamt: 10 Fehler  🔍
#
# ============================================================
