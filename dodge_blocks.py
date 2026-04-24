import pygame
import random

# Initialisieren
pygame.init()

# Fenster
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Blocks")

# Farben
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 50, 50)

# Spieler
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 7

# Gegner (fallende Blöcke)
block_size = 50
block_x = random.randint(0, WIDTH - block_size)
block_y = -50
block_speed = 5

# Score
score = 0
font = pygame.font.SysFont("Arial", 30)

clock = pygame.time.Clock()
running = True

# Game Loop
while running:
    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tasten
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Spieler im Bildschirm halten
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_size:
        player_x = WIDTH - player_size

    # Block bewegen
    block_y += block_speed

    # Wenn Block unten ist → neuer Block + Punkt
    if block_y > HEIGHT:
        block_y = -50
        block_x = random.randint(0, WIDTH - block_size)
        score += 1

    # Kollision prüfen
    if (player_x < block_x + block_size and
        player_x + player_size > block_x and
        player_y < block_y + block_size and
        player_y + player_size > block_y):
        print("Game Over!")
        running = False

    # Zeichnen
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    pygame.draw.rect(screen, RED, (block_x, block_y, block_size, block_size))

    # Score anzeigen
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
