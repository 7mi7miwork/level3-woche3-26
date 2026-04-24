import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Dodge")

# Farben
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
YELLOW = (255, 220, 0)
BLUE = (50, 150, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
PURPLE = (180, 50, 255)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 60)

clock = pygame.time.Clock()

# Zustände
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
game_state = MENU

# Straße
def draw_road():
    screen.fill(GRAY)
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 5, y, 10, 20))

# Auto
def draw_car(x, y, color):
    pygame.draw.rect(screen, color, (x, y, 50, 80))
    pygame.draw.rect(screen, WHITE, (x+5, y+10, 40, 20))

# PowerUp
def draw_powerup(x, y, type):
    color = GREEN if type == "shield" else PURPLE if type == "slow" else YELLOW
    pygame.draw.circle(screen, color, (x+25, y+25), 20)

def reset_game(difficulty):
    global player_x, player_y, cars, powerups
    global score, level, speed, spawn_rate
    global shield, slow_timer, double_score_timer

    player_x = WIDTH // 2 - 25
    player_y = HEIGHT - 120

    cars = []
    powerups = []

    score = 0
    level = 1

    shield = False
    slow_timer = 0
    double_score_timer = 0

    if difficulty == "easy":
        speed = 4
        spawn_rate = 40
    elif difficulty == "hard":
        speed = 8
        spawn_rate = 20
    else:
        speed = 5
        spawn_rate = 30

difficulty = "medium"

running = True
while running:
    draw_road()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_1:
                    difficulty = "easy"
                    reset_game(difficulty)
                    game_state = PLAYING
                if event.key == pygame.K_2:
                    difficulty = "medium"
                    reset_game(difficulty)
                    game_state = PLAYING
                if event.key == pygame.K_3:
                    difficulty = "hard"
                    reset_game(difficulty)
                    game_state = PLAYING

            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    reset_game(difficulty)
                    game_state = PLAYING
                if event.key == pygame.K_m:
                    game_state = MENU

    # -------- MENU --------
    if game_state == MENU:
        screen.blit(big_font.render("TRAFFIC DODGE", True, WHITE), (80, 200))
        screen.blit(font.render("1 - Easy", True, WHITE), (220, 350))
        screen.blit(font.render("2 - Medium", True, WHITE), (220, 400))
        screen.blit(font.render("3 - Hard", True, WHITE), (220, 450))

    # -------- SPIEL --------
    elif game_state == PLAYING:

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= 7
        if keys[pygame.K_RIGHT]:
            player_x += 7

        player_x = max(0, min(WIDTH - 50, player_x))

        # Gegner spawnen (freie Position + Drift)
        if random.randint(1, spawn_rate) == 1:
            x = random.randint(0, WIDTH - 50)
            drift = random.choice([-1, 1]) * random.uniform(0.5, 2)
            cars.append([x, -100, drift])

        # Bewegung
        for car in cars:
            current_speed = speed * (0.5 if slow_timer > 0 else 1)
            car[1] += current_speed
            car[0] += car[2]

            # Abprallen
            if car[0] <= 0 or car[0] >= WIDTH - 50:
                car[2] *= -1

            # Optional: Richtungswechsel
            if random.randint(1, 100) == 1:
                car[2] = random.choice([-2, -1, 1, 2])

        # PowerUps spawnen
        if random.randint(1, 200) == 1:
            x = random.randint(0, WIDTH - 50)
            type = random.choice(["shield", "slow", "double"])
            powerups.append([x, -50, type])

        for p in powerups:
            p[1] += speed

        # Kollision + Score
        for car in cars[:]:
            if (player_x < car[0] + 50 and
                player_x + 50 > car[0] and
                player_y < car[1] + 80 and
                player_y + 80 > car[1]):

                if shield:
                    shield = False
                    cars.remove(car)
                else:
                    game_state = GAME_OVER

            if car[1] > HEIGHT:
                cars.remove(car)
                score += 2 if double_score_timer > 0 else 1

        # PowerUp einsammeln
        for p in powerups[:]:
            if (player_x < p[0] + 50 and
                player_x + 50 > p[0] and
                player_y < p[1] + 50 and
                player_y + 50 > p[1]):

                if p[2] == "shield":
                    shield = True
                elif p[2] == "slow":
                    slow_timer = 300
                elif p[2] == "double":
                    double_score_timer = 300

                powerups.remove(p)

        # Timer
        if slow_timer > 0:
            slow_timer -= 1
        if double_score_timer > 0:
            double_score_timer -= 1

        # Level
        if score // 10 + 1 > level:
            level += 1
            speed += 0.5
            spawn_rate = max(10, spawn_rate - 2)

        # Zeichnen
        draw_car(player_x, player_y, BLUE)

        for car in cars:
            draw_car(car[0], car[1], RED)

        for p in powerups:
            draw_powerup(p[0], p[1], p[2])

        # UI
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 50))

        if shield:
            screen.blit(font.render("Shield!", True, GREEN), (10, 90))
        if slow_timer > 0:
            screen.blit(font.render("Slow!", True, PURPLE), (10, 130))
        if double_score_timer > 0:
            screen.blit(font.render("2x Score!", True, YELLOW), (10, 170))

    # -------- GAME OVER --------
    elif game_state == GAME_OVER:
        screen.blit(big_font.render("CRASH!", True, RED), (180, 250))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (240, 350))
        screen.blit(font.render("R - Restart", True, WHITE), (200, 450))
        screen.blit(font.render("M - Menu", True, WHITE), (200, 500))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
