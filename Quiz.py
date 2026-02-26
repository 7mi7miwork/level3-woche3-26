# ============================================================
#  PYTHON QUIZ-SPIEL  –  Gemeinsam im Unterricht bauen!
#  Datei: Quiz.py
# ============================================================
#
#  WIR BAUEN DAS SPIEL IN 5 STUFEN:
#
#  STUFE 1   print() und input()        -> Begrüssung
#  STUFE 2   if / elif / else           -> Antworten prüfen
#  STUFE 3   Listen                     -> Fragen speichern
#  STUFE 4   for-Schleife               -> Alle Fragen stellen
#  STUFE 5   Funktionen                 -> Alles sauber machen
#
# ============================================================


# ============================================================
# STUFE 1 – print() und input()
# ============================================================
# Mit print() zeigen wir etwas auf dem Bildschirm.
# Mit input() fragen wir den Benutzer etwas.

def begruessung():
    print("=" * 40) # 40 mal das Zeichen "="
    print("   Willkommen beim Python-Quiz!") # Schreibt er den text in ""
    print("=" * 40)
    
    # Frage an euch: Fragt nach dem Namen und speichert ihn?
    name = input("Wie heisst du? ") # Fragt den Benutzer nach seinem Namen
    
    print(f"Hallo, {name}! Viel Erfolg beim Quiz!")
    print()
    
    # Den Namen zurückgeben, damit wir ihn später brauchen können
    return name

# ============================================================
# STUFE 2 – if / elif / else
# ============================================================
# Wir prüfen, ob die Antwort des Spielers richtig ist.

def antwort_pruefen(antwort_spieler, richtige_antwort):
    # .strip()   -> entfernt Leerzeichen am Anfang/Ende
    # .lower()   -> macht alles kleinbuchstaben (Gross/Klein egal)
    antwort_spieler  = antwort_spieler.strip().lower()
    richtige_antwort = richtige_antwort.strip().lower()
    
    if antwort_spieler == richtige_antwort:
        print("Richtig! Super!")
        return True                # True = Punkt bekommen
    else:
        print(f"Leider falsch. Die Antwort war: {richtige_antwort}")
        return False               # False = kein Punkt