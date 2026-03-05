import pygame
import tkinter as tk
from tkinter import messagebox
import random
import sys
import os
import json
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 165, 0), (128, 0, 128), (0, 128, 128)
]

# Game modes
MODE_SINGLEPLAYER = 0
MODE_MULTIPLAYER = 1

# Difficulty levels
DIFFICULTIES = {
    0: {"name": "Sehr einfach", "ai_speed": 2},
    1: {"name": "Einfach", "ai_speed": 3},
    2: {"name": "Normal", "ai_speed": 4},
    3: {"name": "Schwer", "ai_speed": 5},
    4: {"name": "Experte", "ai_speed": 6},
    5: {"name": "Meister", "ai_speed": 7},
    6: {"name": "Unmöglich", "ai_speed": 9}
}

# Power-Up types
POWER_UPS = {
    "speed_up": {"name": "Schneller Ball", "color": (255, 0, 0)},
    "speed_down": {"name": "Langsamer Ball", "color": (0, 0, 255)},
    "paddle_big": {"name": "Großer Schläger", "color": (0, 255, 0)},
    "paddle_small": {"name": "Kleiner Schläger", "color": (255, 255, 0)},
    "ball_multiply": {"name": "Ballvervielfachung", "color": (255, 0, 255)},
    "ball_slow_all": {"name": "Alle Bälle langsam", "color": (0, 255, 255)},
    "paddle_invisible": {"name": "Unsichtbarer Schläger", "color": (128, 0, 128)},
    "ball_fast_all": {"name": "Alle Bälle schnell", "color": (255, 165, 0)},
    "paddle_freeze": {"name": "Gegner einfrieren", "color": (0, 128, 128)},
    "ball_big": {"name": "Großer Ball", "color": (75, 0, 130)}
}

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 7
        self.color = WHITE
        self.visible = True

    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def ai_move(self, ball, difficulty):
        if not self.visible:
            return
        ai_speed = DIFFICULTIES[difficulty]["ai_speed"]
        if self.rect.centery < ball.rect.centery and self.rect.bottom < HEIGHT:
            self.rect.y += ai_speed
        elif self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= ai_speed

    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = 5 * random.choice([-1, 1])
        self.color = WHITE
        self.size = BALL_SIZE

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wall collision
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class PowerUp:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            30, 30
        )
        self.type = random.choice(list(POWER_UPS.keys()))
        self.color = POWER_UPS[self.type]["color"]
        self.active = True

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw power-up name (optional)
            font = pygame.font.Font(None, 16)
            text = font.render(POWER_UPS[self.type]["name"], True, WHITE)
            screen.blit(text, (self.rect.x - 10, self.rect.y - 20))

def load_highscores():
    if os.path.exists("highscores.json"):
        with open("highscores.json", "r") as f:
            return json.load(f)
    return []

def save_highscores(highscores):
    with open("highscores.json", "w") as f:
        json.dump(highscores, f)

def show_menu():
    root = tk.Tk()
    root.title("PingPong Deluxe - Menü")
    root.geometry("400x400")

    mode = tk.IntVar(value=MODE_SINGLEPLAYER)
    difficulty = tk.IntVar(value=2)  # Default: Normal

    def start_game():
        root.destroy()

    tk.Label(root, text="Spielmodus:").pack(pady=5)
    tk.Radiobutton(root, text="Singleplayer (vs. KI)", variable=mode, value=MODE_SINGLEPLAYER).pack()
    tk.Radiobutton(root, text="Multiplayer (2 Spieler)", variable=mode, value=MODE_MULTIPLAYER).pack()

    tk.Label(root, text="\nSchwierigkeitsgrad:").pack(pady=5)
    for i, diff in DIFFICULTIES.items():
        tk.Radiobutton(root, text=diff["name"], variable=difficulty, value=i).pack()

    tk.Button(root, text="Spiel starten", command=start_game).pack(pady=20)
    tk.Button(root, text="Highscores anzeigen", command=lambda: show_highscores(root)).pack()

    root.mainloop()
    return mode.get(), difficulty.get()

def show_highscores(root):
    highscores = load_highscores()
    message = "Highscores:\n\n"
    for i, score in enumerate(highscores[:5], 1):
        message += f"{i}. {score['name']}: {score['score']} (am {score['date']})\n"
    messagebox.showinfo("Highscores", message if highscores else "No highscores yet!")

def main():
    mode, difficulty = show_menu()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PingPong Deluxe")
    clock = pygame.time.Clock()

    # Game objects
    player = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    opponent = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    balls = [Ball()]
    powerups = []
    powerup_timers = {}

    # Game state
    player_score = 0
    opponent_score = 0
    font = pygame.font.Font(None, 36)
    bg_color = BLACK
    game_over = False
    highscores = load_highscores()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Reset game
                    player_score = 0
                    opponent_score = 0
                    balls = [Ball()]
                    powerups = []
                    powerup_timers = {}
                    game_over = False
                if event.key == pygame.K_h:
                    show_highscores(pygame.display.get_surface())

        if game_over:
            screen.fill(BLACK)
            game_over_text = font.render("GAME OVER! Drücke R zum Neustart", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - 180, HEIGHT // 2))
            pygame.display.flip()
            continue

        # Move paddles
        player.move(pygame.K_w, pygame.K_s)
        if mode == MODE_SINGLEPLAYER:
            opponent.ai_move(balls[0], difficulty)
        else:
            opponent.move(pygame.K_UP, pygame.K_DOWN)

        # Move balls
        for ball in balls[:]:
            ball.move()

            # Ball collision with paddles
            if ball.rect.colliderect(player.rect) or ball.rect.colliderect(opponent.rect):
                ball.speed_x *= -1.1  # Speed up on hit

            # Scoring
            if ball.rect.left <= 0:
                opponent_score += 1
                balls.remove(ball)
                if not balls:
                    balls.append(Ball())
            if ball.rect.right >= WIDTH:
                player_score += 1
                balls.remove(ball)
                if not balls:
                    balls.append(Ball())

        # PowerUp logic
        if random.random() < 0.003 and len(powerups) < 3:
            powerups.append(PowerUp())

        for powerup in powerups[:]:
            if powerup.active:
                for ball in balls:
                    if ball.rect.colliderect(powerup.rect):
                        # Apply power-up effect
                        if powerup.type == "speed_up":
                            ball.speed_x *= 1.5
                            ball.speed_y *= 1.5
                        elif powerup.type == "speed_down":
                            ball.speed_x *= 0.7
                            ball.speed_y *= 0.7
                        elif powerup.type == "paddle_big":
                            player.rect.height = 150
                            opponent.rect.height = 150
                            powerup_timers["paddle_big"] = 300
                        elif powerup.type == "paddle_small":
                            player.rect.height = 50
                            opponent.rect.height = 50
                            powerup_timers["paddle_small"] = 300
                        elif powerup.type == "ball_multiply":
                            balls.append(Ball())
                        elif powerup.type == "ball_slow_all":
                            for b in balls:
                                b.speed_x *= 0.5
                                b.speed_y *= 0.5
                            powerup_timers["ball_slow_all"] = 300
                        elif powerup.type == "paddle_invisible":
                            player.visible = False
                            powerup_timers["paddle_invisible"] = 180
                        elif powerup.type == "ball_fast_all":
                            for b in balls:
                                b.speed_x *= 1.8
                                b.speed_y *= 1.8
                            powerup_timers["ball_fast_all"] = 300
                        elif powerup.type == "paddle_freeze":
                            opponent.speed = 0
                            powerup_timers["paddle_freeze"] = 180
                        elif powerup.type == "ball_big":
                            ball.size = 30
                            ball.rect.width = ball.size
                            ball.rect.height = ball.size
                            powerup_timers["ball_big"] = 300

                        powerup.active = False
                        powerups.remove(powerup)
                        break

        # Update power-up timers
        for timer in list(powerup_timers.keys()):
            powerup_timers[timer] -= 1
            if powerup_timers[timer] <= 0:
                if timer == "paddle_big" or timer == "paddle_small":
                    player.rect.height = PADDLE_HEIGHT
                    opponent.rect.height = PADDLE_HEIGHT
                elif timer == "paddle_invisible":
                    player.visible = True
                elif timer == "paddle_freeze":
                    opponent.speed = DIFFICULTIES[difficulty]["ai_speed"]
                elif timer == "ball_big":
                    for ball in balls:
                        ball.size = BALL_SIZE
                        ball.rect.width = BALL_SIZE
                        ball.rect.height = BALL_SIZE
                del powerup_timers[timer]

        # Change background color randomly
        if random.random() < 0.002:
            bg_color = random.choice(COLORS)

        # Draw everything
        screen.fill(bg_color)
        player.draw(screen)
        opponent.draw(screen)
        for ball in balls:
            ball.draw(screen)
        for powerup in powerups:
            powerup.draw(screen)

        # Draw scores
        player_text = font.render(f"{player_score}", True, WHITE)
        opponent_text = font.render(f"{opponent_score}", True, WHITE)
        screen.blit(player_text, (WIDTH // 4, 20))
        screen.blit(opponent_text, (3 * WIDTH // 4, 20))

        # Check for game over (score >= 10)
        if player_score >= 10 or opponent_score >= 10:
            game_over = True
            name = "Player" if player_score >= 10 else "Opponent"
            highscores.append({
                "name": name,
                "score": max(player_score, opponent_score),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            highscores.sort(key=lambda x: x["score"], reverse=True)
            save_highscores(highscores[:5])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
