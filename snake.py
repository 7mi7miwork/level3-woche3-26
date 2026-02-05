import random       # Library
import time         # Library
import keyboard     # Library muss installiert werden

class SnakeGame:    # Klasse
    def __init__(self, width=20, height=10): # Feldgroesse
        self.width = width  # Bildschirmbreite
        self.height = height    # Bildschirmhoehe
        self.snake = [(width // 2, height // 2)] #Schlangen Groesse
        self.direction = (1, 0) # Startrichtung der Schlange
        self.food = self._generate_food() # Schlangenfutter
        self.score = 0  # Punktestand
        self.game_over = False # Spiel laeuft
        
    def _generate_food(self):   # Schlangenfutter erschaffen
        """Ezeugt das Essen an zufaelligen plaetzen""" # """ """ = Nur hier
        while True:
            food = (random.rand(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food
    
    def _draw(self):
        """Zeichnet das Spielfeld"""
        print("\033[H") # Der Zeiger wird zurueck gesetzt
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.snake:
                    print("0", end=" ")
                elif (x, y) == self.food:
                    print("X", end=" ")
                else:
                    print(".", end=" ")
            print()
        print(f"Score: {self.score}")
        
    def _update(self):
        """Aktualisiern die SChlange auf Kollisionen"""
        head_x, head_y = self.snake(0, new_head)
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % self.width,(head_y + dir_y) % self.height)
        
        #Kollisionen mit sich selbst
        if new_head in self.snake:
            self.game_over = True
            return
        
        self. snake.insert(0, new_head)
        
        # Essen fressen?
        if new_head == self.food:
            self.score += 1
            self.food = self._generate_food()
        else:
            self.snake. pop()
    
    def run(self):
        """Hauptspielschleife"""
        print ("Snake-Spiel! Steuerung: WASD. Beenden mit ESC.")
        time.sleep(0.2)
        
        while not self.game_over:
            self._draw()
            time.sleep(0.2)
            
            # Tastaturbelegung
            if keyboard.is_pressed("w") and self.direction != (0, 1):
                self.direction = (0, -1)
            elif keyboard.is_pressed("s") and self.direction != (0, -1):
                self.direction = (0, 1)
            elif keyboard.is_pressed("a") and self.direction != (1, 0):
                self.direction = (0, 1)
            elif keyboard.is_pressed("d") and self.direction != (-1, 0):
                self.direction = (0, 1)
            elif keyboard.is_pressed("esc"):
                break
                
            self._update()
            
        print("Game Over! Endstand:", self.score)
        
# Spiel starten
if __name__ == "__main__":
    game = SnakeGame()
    game.run()