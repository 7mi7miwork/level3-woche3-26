import pygame
import random
import time

pygame.init()

# Bildschirmgröße
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Reaktionsspiel")

font = pygame.font.Font(None, 50)

state = "wait"
start_time = 0
reaction_time = 0
change_time = time.time() + random.uniform(2,5)

running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "go":
                reaction_time = time.time() - start_time
                state = "result"
            elif state == "wait":
                state = "too_early"
                
    # Zustand wechseln
    if state == "wait" and time.time() > change_time:
        state = "go"
        start_time = time.time()
        
    # Bildschirm
    if state == "wait":
        screen.fill((200, 0, 0))
        text = font.render("Warte...", True, (255, 255, 255))
        
    elif state == "go":
        screen.fill((0, 200, 0))
        text = font.render("Klick!", True, (0, 0, 0))
        
    elif state == "result":
        screen.fill((0, 0, 0))
        text = font.render(f"{reaction_time:.3f} Sekunden", True, (255, 0, 0))
    
    elif state == "too early":
        screen.fill((0, 0, 0))
        text = font.render("Zu früh!", True, (255, 0, 0))
        
    screen.blit(text, (width//2 - text.get_width()//2, height//2))
    pygame.display.flip()
    
pygame.quit()