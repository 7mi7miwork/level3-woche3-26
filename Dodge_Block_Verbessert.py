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

# Spieler
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 7

# Gegner
block_size = 50
blocks = []

# Score & Level
score = 0
level = 1

font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 60)

clock = pygame.time.Clock()

# Schwierigkeit wählen
def choose_difficulty():
    choosing = True
    difficulty = "medium"

    while choosing:
        screen.fill(WHITE)

        title = big_font.render("Choose Difficulty", True, BLACK)
        screen.blit(title, (80, 200))

        easy = font.render("1 - Easy", True, BLACK)
        medium = font.render("2 - Medium", True, BLACK)
        hard = font.render("3 - Hard", True, BLACK)

        screen.blit(easy, (200, 350))
        screen.blit(medium, (200, 400))
        screen.blit(hard, (200, 450))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "easy"
                if event.key == pygame.K_2:
                    return "medium"
                if event.key == pygame.K_3:
                    return "hard"

difficulty = choose_difficulty()

# Startwerte je Schwierigkeit
if difficulty == "easy":
    block_speed = 4
    spawn_rate = 40
elif difficulty == "hard":
    block_speed = 7
    spawn_rate = 20
else:
    block_speed = 5
    spawn_rate = 30

running = True

# Game Loop
while running:
    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Bewegung
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    player_x = max(0, min(WIDTH - player_size, player_x))

    # Neue Blöcke spawnen
    if random.randint(1, spawn_rate) == 1:
        blocks.append([
            random.randint(0, WIDTH - block_size),
            -block_size
        ])

    # Blöcke bewegen
    for block in blocks:
        block[1] += block_speed

    # Kollision & Entfernen
    for block in blocks[:]:
        if (player_x < block[0] + block_size and
            player_x + player_size > block[0] and
            player_y < block[1] + block_size and
            player_y + player_size > block[1]):

            running = False

        if block[1] > HEIGHT:
            blocks.remove(block)
            score += 1

    # Level System (alle 10 Punkte)
    if score // 10 + 1 > level:
        level += 1
        block_speed += 0.5
        spawn_rate = max(10, spawn_rate - 2)

    # Zeichnen
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    for block in blocks:
        pygame.draw.rect(screen, RED, (block[0], block[1], block_size, block_size))

    # UI
    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))

    pygame.display.update()
    clock.tick(60)

# Game Over Screen
screen.fill(WHITE)
game_over = big_font.render("GAME OVER", True, RED)
final_score = font.render(f"Score: {score}", True, BLACK)

screen.blit(game_over, (150, 300))
screen.blit(final_score, (230, 400))

pygame.display.update()
pygame.time.delay(3000)

pygame.quit()
