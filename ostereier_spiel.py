import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ostereiersuche 🐣")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 48)

# Farben
WHITE = (255, 255, 255)
GREEN = (100, 200, 100)
DARK_GREEN = (50, 120, 50)
BLUE = (135, 206, 235)
YELLOW = (255, 230, 0)

# Spieler
player = pygame.Rect(100, 120, 40, 40)
speed = 5

# Ei Klasse
class Egg:
    def __init__(self, obstacles):
        while True:
            self.size = random.randint(15, 25)
            self.x = random.randint(20, WIDTH - self.size - 20)
            self.y = random.randint(120, HEIGHT - self.size - 20)
            rect = pygame.Rect(self.x, self.y, self.size, self.size)

            # nicht in Hindernissen spawnen
            if not any(rect.colliderect(o) for o in obstacles):
                break

        self.color = random.choice([(255,0,0),(255,255,0),(0,255,255),(255,0,255)])
        self.collected = False

    def draw(self):
        if not self.collected:
            pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.size, self.size+10))

    def collide(self, player):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        if player.colliderect(rect):
            self.collected = True
            return True
        return False

# Level erstellen
level = 1
eggs = []
score = 0
time_left = 30
start_ticks = pygame.time.get_ticks()

# Hindernis
obstacles = []

def safe_player_spawn():
    global player
    while True:
        new_player = pygame.Rect(random.randint(20, WIDTH-60), random.randint(120, HEIGHT-60), 40, 40)
        if not any(new_player.colliderect(o) for o in obstacles):
            return new_player


def create_level(level):
    global eggs, obstacles, time_left, start_ticks, player

    # Hindernisse zuerst erzeugen
    obstacles = []
    for _ in range(level * 2):
        obstacles.append(pygame.Rect(random.randint(20, WIDTH-80), random.randint(120, HEIGHT-80), 60, 60))

    # Spieler sicher platzieren
    player = safe_player_spawn()

    # Eier erzeugen (nicht in Hindernissen)
    eggs = [Egg(obstacles) for _ in range(level * 5)]

    time_left = 30 + level * 5
    start_ticks = pygame.time.get_ticks()

create_level(level)

running = True

while running:
    screen.fill(BLUE)
    pygame.draw.rect(screen, GREEN, (0, 100, WIDTH, HEIGHT-100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0

    if keys[pygame.K_LEFT]: dx = -speed
    if keys[pygame.K_RIGHT]: dx = speed
    if keys[pygame.K_UP]: dy = -speed
    if keys[pygame.K_DOWN]: dy = speed

    # Bewegung vorbereiten
    new_player = player.move(dx, dy)

    # Bildschirmbegrenzung (Fix gegen rauslaufen)
    new_player.x = max(0, min(WIDTH - player.width, new_player.x))
    new_player.y = max(100, min(HEIGHT - player.height, new_player.y))

    # Kollisionsprüfung mit Hindernissen
    if not any(new_player.colliderect(o) for o in obstacles):
        player = new_player

    # Eier zeichnen
    collected_count = 0
    for egg in eggs:
        egg.draw()
        if egg.collide(player):
            score += 1
        if egg.collected:
            collected_count += 1

    # Hindernisse
    for o in obstacles:
        pygame.draw.rect(screen, DARK_GREEN, o)

    # Spieler
    pygame.draw.rect(screen, YELLOW, player)

    # Zeit
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    remaining = max(0, time_left - seconds)

    # UI
    screen.blit(FONT.render(f"Level: {level}", True, WHITE), (10,10))
    screen.blit(FONT.render(f"Score: {score}", True, WHITE), (10,40))
    screen.blit(FONT.render(f"Zeit: {remaining}", True, WHITE), (10,70))

    # Level geschafft
    if collected_count == len(eggs):
        level += 1
        create_level(level)

    # Zeit abgelaufen
    if remaining <= 0:
        running = False

    pygame.display.flip()
    clock.tick(60)

# Game Over Screen
screen.fill((0,0,0))
text = BIG_FONT.render("Game Over", True, WHITE)
score_text = FONT.render(f"Dein Score: {score}", True, WHITE)
screen.blit(text, (WIDTH//2 - 120, HEIGHT//2 - 50))
screen.blit(score_text, (WIDTH//2 - 100, HEIGHT//2 + 10))
pygame.display.flip()
pygame.time.wait(4000)

pygame.quit()
