import random

def zahlenrate_spiel():
    print("=" * 50)
    print("Willkommen beim Zahlenratespiel!")
    print("=" * 50)
    
    # Zufällige Zahl zwischen 1 und 100 generieren
    geheime_zahl = random.randint(1, 100)
    versuche = 0
    max_versuche = 10
    
    print(f"\nIch habe mir eine Zahl zwischen 1 und 100 ausgedacht.")
    print(f"Du hast {max_versuche} Versuche, sie zu erraten.\n")
    
    while versuche < max_versuche:
        try:
            # Benutzereingabe
            eingabe = input(f"Versuch {versuche + 1}/{max_versuche} - Deine Zahl: ")
            geratene_zahl = int(eingabe)
            
            # Überprüfung ob Zahl im gültigen Bereich
            if geratene_zahl < 1 or geratene_zahl > 100:
                print("Bitte gib eine Zahl zwischen 1 und 100 ein!")
                continue
            
            versuche += 1
            
            # Überprüfung der geratenen Zahl
            if geratene_zahl < geheime_zahl:
                print("❌ Zu niedrig! Versuche es mit einer höheren Zahl.\n")
            elif geratene_zahl > geheime_zahl:
                print("❌ Zu hoch! Versuche es mit einer niedrigeren Zahl.\n")
            else:
                print(f"\n🎉 Glückwunsch! Du hast die Zahl {geheime_zahl} erraten!")
                print(f"Du hast {versuche} Versuch(e) gebraucht.\n")
                return
                
        except ValueError:
            print("Das ist keine gültige Zahl! Bitte gib eine Ganzzahl ein.\n")
    
    # Maximale Versuche erreicht
    print(f"\n💔 Leider verloren! Die gesuchte Zahl war {geheime_zahl}.")
    print("Viel Glück beim nächsten Mal!\n")

def hauptmenu():
    while True:
        zahlenrate_spiel()
        
        # Neues Spiel?
        antwort = input("Möchtest du noch eine Runde spielen? (j/n): ").lower()
        if antwort != 'j' and antwort != 'ja':
            print("\nDanke fürs Spielen! Bis zum nächsten Mal! 👋")
            break
        print("\n")

if __name__ == "__main__":
    hauptmenu()