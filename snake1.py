import pygame
import random
import sys

# Initialisierung
pygame.init()
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Farben
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Spielvariablen
snake_size = 20
snake_speed = 10
snake = [(width // 2, height // 2)]
snake_direction = (snake_size, 0) # Startbewegung nach rechts
food = (random.randint(0, (width - snake_size)//snake_size)*snake_size, random.randint(0, (height - snake_size)//snake_size)*snake_size)
score = 0
game_over = False

# Schriftart initialisieren
font = pygame.font.SysFont(None, 35)

def draw_snake(snake_list):
    for segment in snake_list:
        pygame.draw.rect(screen, GREEN, (*segment, snake_size, snake_size))
        
def draw_food(food_pos):
    pygame.draw.rect(screen, GREEN, [segment[0], segment[1], snake_size, snake_size])
    
def message(msg, color):
    text = font.render(msg, True, color)
    screen.blit(text, [width / 6, height / 3]) # Checkpoint

# Hauptspiel-Schleife
while not game_over:
    # Event-Handlung
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # Steuerung der Schlange
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and snake_direction != (snake_size, 0):
                snake_direction = (-snake_size, 0) # Links
            elif event.key == pygame.K_d and snake_direction != (-snake_size, 0):
                snake_direction = (snake_size, 0) # Rechts
            elif event.key == pygame.K_w and snake_direction != (0, snake_size):
                snake_direction = (0, -snake_size) # Hoch
            elif event.key == pygame.K_s and snake_direction != (0, -snake_size):
                snake_direction = (0, snake_size) # Runter
    
    # Schlange bewegen
    head_x, head_y = snake[-1]
    new_head = (head_x + snake_direction[0], head_y + snake_direction[1])
    
    # Kollision mit Wänden
    if new_head[0] >= width or new_head[0] < 0 or new_head[1] >= height or new_head[1] < 0:
        game_over = True
    
    # Kollision mit sich selbst
    if new_head in snake:
        game_over = True
        
    # Neuer Kopf der Schlange hinzufügen
    snake.append(new_head)
    
    # Essen essen?
    if new_head == food:
        score += 1
        food = (random.randint(0, (width - snake_size)//snake_size)*snake_size, 
                random.randint(0, (height - snake_size)//snake_size)*snake_size)
        
    else:
        snake.pop(0) # Schwanz entfernen, wenn kein Essen gegessen wurde

    # Bildschirm zeichnen
    screen.fill(BLACK)
    draw_snake(snake)
    draw_food(food)
    
    # Punktestand anzeigen
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, [0, 0])
    
    pygame.display.update()
    clock.tick(snake_speed)
    
