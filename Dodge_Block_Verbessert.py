import pygame
import random

pygame.init()

# Fenster
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Blocks")

# Farben
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 60)

clock = pygame.time.Clock()

# Spielzustände
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU

# Globale Variablen
def reset_game(difficulty):
    global player_x, player_y, blocks, score, level, block_speed, spawn_rate

    player_x = WIDTH // 2
    player_y = HEIGHT - 100

    blocks = []
    score = 0
    level = 1

    if difficulty == "easy":
        block_speed = 4
        spawn_rate = 40
    elif difficulty == "hard":
        block_speed = 7
        spawn_rate = 20
    else:
        block_speed = 5
        spawn_rate = 30

difficulty = "medium"

running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # MENU
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

            # GAME OVER
            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    reset_game(difficulty)
                    game_state = PLAYING
                if event.key == pygame.K_m:
                    game_state = MENU

    # -------- MENU --------
    if game_state == MENU:
        title = big_font.render("DODGE GAME", True, BLACK)
        screen.blit(title, (120, 200))

        screen.blit(font.render("1 - Easy", True, BLACK), (220, 350))
        screen.blit(font.render("2 - Medium", True, BLACK), (220, 400))
        screen.blit(font.render("3 - Hard", True, BLACK), (220, 450))

    # -------- SPIEL --------
    elif game_state == PLAYING:

        # Spieler
        player_size = 50
        player_speed = 7

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        player_x = max(0, min(WIDTH - player_size, player_x))

        # Spawnen
        if random.randint(1, spawn_rate) == 1:
            blocks.append([random.randint(0, WIDTH - 50), -50])

        # Bewegen
        for block in blocks:
            block[1] += block_speed

        # Kollision + Score
        for block in blocks[:]:
            if (player_x < block[0] + 50 and
                player_x + 50 > block[0] and
                player_y < block[1] + 50 and
                player_y + 50 > block[1]):

                game_state = GAME_OVER

            if block[1] > HEIGHT:
                blocks.remove(block)
                score += 1

        # Level Up
        if score // 10 + 1 > level:
            level += 1
            block_speed += 0.5
            spawn_rate = max(10, spawn_rate - 2)

        # Zeichnen
        pygame.draw.rect(screen, BLUE, (player_x, player_y, 50, 50))
        for block in blocks:
            pygame.draw.rect(screen, RED, (block[0], block[1], 50, 50))

        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, BLACK), (10, 50))

    # -------- GAME OVER --------
    elif game_state == GAME_OVER:
        screen.blit(big_font.render("GAME OVER", True, RED), (140, 250))
        screen.blit(font.render(f"Score: {score}", True, BLACK), (240, 350))
        screen.blit(font.render("R - Restart", True, BLACK), (200, 450))
        screen.blit(font.render("M - Menu", True, BLACK), (200, 500))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
