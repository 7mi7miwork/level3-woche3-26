import pygame
import random

pygame.init()

# Fenster
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Dodge")

# Farben
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
YELLOW = (255, 220, 0)
BLUE = (50, 150, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 60)

clock = pygame.time.Clock()

# Zustände
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
game_state = MENU

# Straße zeichnen
def draw_road():
    screen.fill(GRAY)

    # Mittellinie (gestrichelt)
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 5, y, 10, 20))

# Auto zeichnen
def draw_car(x, y, color):
    pygame.draw.rect(screen, color, (x, y, 50, 80))  # Karosserie
    pygame.draw.rect(screen, WHITE, (x+5, y+10, 40, 20))  # Fenster
    pygame.draw.rect(screen, BLACK, (x+5, y+60, 10, 15))  # Räder
    pygame.draw.rect(screen, BLACK, (x+35, y+60, 10, 15))

# Reset
def reset_game(difficulty):
    global player_x, player_y, cars, score, level, speed, spawn_rate

    player_x = WIDTH // 2 - 25
    player_y = HEIGHT - 120

    cars = []
    score = 0
    level = 1

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

        # Gegner spawnen
        if random.randint(1, spawn_rate) == 1:
            lane_x = random.choice([100, 250, 400])  # Fahrspuren
            cars.append([lane_x, -100])

        # Bewegung
        for car in cars:
            car[1] += speed

        # Kollision + Score
        for car in cars[:]:
            if (player_x < car[0] + 50 and
                player_x + 50 > car[0] and
                player_y < car[1] + 80 and
                player_y + 80 > car[1]):
                game_state = GAME_OVER

            if car[1] > HEIGHT:
                cars.remove(car)
                score += 1

        # Level
        if score // 10 + 1 > level:
            level += 1
            speed += 0.5
            spawn_rate = max(10, spawn_rate - 2)

        # Zeichnen
        draw_car(player_x, player_y, BLUE)

        for car in cars:
            draw_car(car[0], car[1], RED)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 50))

    # -------- GAME OVER --------
    elif game_state == GAME_OVER:
        screen.blit(big_font.render("CRASH!", True, RED), (180, 250))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (240, 350))
        screen.blit(font.render("R - Restart", True, WHITE), (200, 450))
        screen.blit(font.render("M - Menu", True, WHITE), (200, 500))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
