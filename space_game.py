import pygame
import random
import math

# --- Konfiguration & Konstanten ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# --- Klassen ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Erzeugt ein einfaches Raumschiff-Bild (Dreieck)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(0, 40), (20, 0), (40, 40)]) # Schiffform
        pygame.draw.polygon(self.image, (0, 200, 0), [(10, 35), (20, 5), (30, 35)], 2) # Rahmen
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shoot_delay = 250 # Millisekunden
        self.last_shot = pygame.time.get_ticks()
        
        # Powerup Zustände
        self.triple_shot = False
        self.triple_shot_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.shield_active = False
        self.shield_timer = 0

    def update(self):
        # Bewegung
        keys = pygame.key.get_pressed()
        current_speed = self.speed * (2 if self.speed_boost else 1)
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += current_speed
        
        # Grenzen
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

        # Timer für Powerups aktualisieren
        now = pygame.time.get_ticks()
        if self.triple_shot and now > self.triple_shot_timer:
            self.triple_shot = False
        if self.speed_boost and now > self.speed_boost_timer:
            self.speed_boost = False
        if self.shield_active and now > self.shield_timer:
            self.shield_active = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullets = []
            if self.triple_shot:
                bullets.append(Bullet(self.rect.centerx, self.rect.top, -5, 0)) # Links
                bullets.append(Bullet(self.rect.centerx, self.rect.top, 0, 0))   # Mitte
                bullets.append(Bullet(self.rect.centerx, self.rect.top, 5, 0))   # Rechts
            else:
                bullets.append(Bullet(self.rect.centerx, self.rect.top, 0, 0))
            return bullets
        return []

class Enemy(pygame.sprite.Sprite):
    def __init__(self, difficulty_multiplier=1.0, enemy_type="asteroid"):
        super().__init__()
        self.type = enemy_type
        
        if self.type == "asteroid":
            size = random.randint(30, 50)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, RED, (size//2, size//2), size//2)
            pygame.draw.circle(self.image, (150, 0, 0), (size//2, size//2), size//2, 3)
            self.speedy = random.randint(2, 4) * difficulty_multiplier
            self.speedx = random.randint(-2, 2)
            self.health = 10
            self.score_value = 10
        elif self.type == "hunter":
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            # Feindliches Schiff (Dreieck)
            pygame.draw.polygon(self.image, ORANGE, [(15, 0), (30, 30), (0, 30)])
            self.speedy = random.randint(3, 6) * difficulty_multiplier
            self.speedx = 0
            self.health = 20
            self.score_value = 25

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.shield = False # Nur für den Boss relevant

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Bildschirmrand-Wraping für X
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speedx = -self.speedx

        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randint(2, 4)

class Boss(Enemy):
    def __init__(self, level):
        # Wir rufen nicht super() auf, weil wir alles neu definieren wollen
        pygame.sprite.Sprite.__init__(self)
        self.type = "boss"
        size = 100 + level * 10
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # Boss Form (Komplexeres Rechteck mit Dreieck)
        pygame.draw.rect(self.image, (255, 0, 255), (0, 0, size, size)) # Lila Kasten
        pygame.draw.polygon(self.image, (200, 0, 200), [(size//2, 0), (size, size//2), (0, size//2)]) # Dreieck drauf
        
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - size // 2
        self.rect.y = -size
        
        self.speedy = 1
        self.speedx = 2
        self.health = 500 * level
        self.max_health = self.health
        self.score_value = 1000 * level
        self.shoot_timer = pygame.time.get_ticks()
        
    def update(self):
        # Bewegung
        if self.rect.y < 50:
            self.rect.y += self.speedy
        
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speedx = -self.speedx
            
        # Schießen (wird in der Main-Loop gehandhabt, hier nur Bewegung)
        # Oder wir geben Projektile zurück, aber einfacher ist es in der Main-Loop zu prüfen.

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x_offset=0, y_offset=0):
        super().__init__()
        self.image = pygame.Surface((6, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, 6, 10))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x + x_offset
        self.speedy = -10
        self.speedx = x_offset // 5 # Leichte diagonale Bewegung für Triple Shot

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class EnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        pygame.draw.rect(self.image, RED, (0, 0, 6, 10)) # Rotes Projektil
        self.speedy = 8 # Gegner schießen "nach unten"

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, centerx, centery):
        super().__init__()
        self.type = random.choice(['health', 'shield', 'triple', 'speed'])
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        if self.type == 'health':
            pygame.draw.rect(self.image, GREEN, (0, 0, 20, 20))
            pygame.draw.line(self.image, WHITE, (10, 5), (10, 15), 3)
            pygame.draw.line(self.image, WHITE, (5, 10), (15, 10), 3)
        elif self.type == 'shield':
            pygame.draw.circle(self.image, BLUE, (10, 10), 10)
        elif self.type == 'triple':
            pygame.draw.rect(self.image, YELLOW, (0, 0, 20, 20))
            pygame.draw.line(self.image, BLACK, (0, 10), (20, 10), 2)
            pygame.draw.line(self.image, BLACK, (10, 0), (10, 20), 2)
        elif self.type == 'speed':
            pygame.draw.rect(self.image, ORANGE, (0, 0, 20, 20))
            # Pfeil zeichnen
            pygame.draw.polygon(self.image, WHITE, [(10, 5), (15, 15), (5, 15)])

        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = random.randrange(1, 3)
        self.height = self.width
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = random.randrange(SCREEN_HEIGHT)
        self.speedy = random.randrange(1, 3)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = random.randrange(-50, -10)
            self.rect.x = random.randrange(SCREEN_WIDTH)

# --- Hilfsfunktionen ---

def draw_health_bar(surf, x, y, hp, max_hp):
    if hp < 0: hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / max_hp) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_text(surf, text, size, x, y, color=WHITE):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# --- Hauptspiel ---

def game_loop(difficulty_name, diff_mult):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Weltraum Shooter - " + difficulty_name)
    clock = pygame.time.Clock()

    # Sprite Gruppen
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    # Hintergrund Sterne erstellen
    for i in range(50):
        s = Star()
        all_sprites.add(s)
        stars.add(s)

    # Spieler erstellen
    player = Player()
    all_sprites.add(player)

    # Spielvariablen
    score = 0
    level = 1
    boss_spawned = False
    running = True
    game_over = False
    boss = None
    MOB_SPAWN_RATE = 1000 # Millisekunden
    last_mob_spawn = pygame.time.get_ticks()

    # Anfangs-Gegner
    for i in range(3):
        spawn_enemy(mobs, all_sprites, diff_mult, "asteroid")

    while running:
        clock.tick(FPS)
        
        # 1. Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart_menu" # Zurück zum Menü
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    new_bullets = player.shoot()
                    for b in new_bullets:
                        all_sprites.add(b)
                        bullets.add(b)

        if not game_over:
            # 2. Updates
            all_sprites.update()

            # Mob Spawning (je nach Level schneller)
            now = pygame.time.get_ticks()
            spawn_delay = max(200, MOB_SPAWN_RATE - (level * 50))
            if now - last_mob_spawn > spawn_delay and not boss_spawned:
                last_mob_spawn = now
                enemy_type = "asteroid"
                if random.random() < 0.2 + (level * 0.05): # Chance auf Jäger steigt
                    enemy_type = "hunter"
                spawn_enemy(mobs, all_sprites, diff_mult, enemy_type)

            # Boss Spawn Logik alle 5 Level
            if score > 0 and score % 2000 < 10 and not boss_spawned:
                boss_spawned = True
                boss = Boss(level)
                all_sprites.add(boss)
                mobs.add(boss)
                # Alle normalen Gegner entfernen für Boss-Kampf? Optional. Hier lassen wir sie.
            
            # Boss Schießen
            if boss_spawned and boss:
                if now - boss.shoot_timer > 1000:
                    boss.shoot_timer = now
                    eb = EnemyBullet(boss.rect.centerx, boss.rect.bottom)
                    all_sprites.add(eb)
                    enemy_bullets.add(eb)

            # Kollisionen
            # Spieler Schuss trifft Mob
            hits = pygame.sprite.groupcollide(mobs, bullets, False, True) # False = Mob bleibt, True = Kugel weg
            for mob, bullet_hits in hits.items():
                # Schaden berechnen
                mob.health -= 10 # Standard Schaden
                # Wenn tot
                if mob.health <= 0:
                    score += mob.score_value
                    # Chance auf Powerup
                    if random.random() < 0.1:
                        p = Powerup(mob.rect.centerx, mob.rect.centery)
                        all_sprites.add(p)
                        powerups.add(p)
                    
                    # Spezialfall Boss
                    if mob.type == "boss":
                        boss_spawned = False
                        boss = None
                        score += 5000
                    
                    mob.kill()

            # Mob trifft Spieler
            hits = pygame.sprite.spritecollide(player, mobs, True) # True = Mob stirbt bei Berührung
            for hit in hits:
                if not player.shield_active:
                    player.health -= 10 * diff_mult # Schaden skaliert mit Schwierigkeit
                    if player.health <= 0:
                        game_over = True
                # Mob neu spawnen
                spawn_enemy(mobs, all_sprites, diff_mult, "asteroid")

            # Gegnerischer Schuss trifft Spieler
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for hit in hits:
                if not player.shield_active:
                    player.health -= 15
                    if player.health <= 0:
                        game_over = True

            # Powerup Einsammeln
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'health':
                    player.health = min(player.max_health, player.health + 25)
                elif hit.type == 'shield':
                    player.shield_active = True
                    player.shield_timer = pygame.time.get_ticks() + 3000 # 3 Sek
                elif hit.type == 'triple':
                    player.triple_shot = True
                    player.triple_shot_timer = pygame.time.get_ticks() + 5000 # 5 Sek
                elif hit.type == 'speed':
                    player.speed_boost = True
                    player.speed_boost_timer = pygame.time.get_ticks() + 5000

            # Level Up
            if score > level * 1000: # Alle 1000 Punkte Level Up (einfaches System)
                level += 1
                # Schwierigkeit erhöht sich durch globale Variablen in der Loop automatisch

        # 3. Zeichnen
        screen.fill(BLACK)
        
        # Score & Info
        draw_text(screen, f"Score: {score}", 18, SCREEN_WIDTH / 2, 10)
        draw_text(screen, f"Level: {level}", 18, SCREEN_WIDTH - 50, 10)
        draw_text(screen, f"Schwierigkeit: {difficulty_name}", 18, 80, 10)
        
        # Health Bar
        draw_health_bar(screen, 10, 10, player.health, player.max_health)
        
        # Powerup Status
        if player.triple_shot:
            draw_text(screen, "TRIPLE SHOT", 18, SCREEN_WIDTH/2, 50, YELLOW)
        if player.shield_active:
            draw_text(screen, "SHIELD", 18, SCREEN_WIDTH/2, 70, CYAN)

        # Aktive Sprites zeichnen
        all_sprites.draw(screen)

        if game_over:
            draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, RED)
            draw_text(screen, "Drücke R für Neustart", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        pygame.display.flip()

    return "quit"

def spawn_enemy(mobs_group, all_group, mult, etype):
    m = Enemy(mult, etype)
    all_group.add(m)
    mobs_group.add(m)

def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Weltraum Shooter - Menü")
    clock = pygame.time.Clock()
    
    menu_active = True
    selected_difficulty = 1 # 0: Leicht, 1: Mittel, 2: Schwer
    difficulties = [("Leicht", 0.7), ("Mittel", 1.0), ("Schwer", 1.5)]
    
    while menu_active:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_difficulty = (selected_difficulty - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_difficulty = (selected_difficulty + 1) % 3
                elif event.key == pygame.K_RETURN:
                    name, mult = difficulties[selected_difficulty]
                    result = game_loop(name, mult)
                    if result == "quit":
                        return "quit"
                    elif result == "restart_menu":
                        return "menu" # Neustart zeigt Menü

        # Zeichnen
        screen.fill(BLACK)
        # Titel
        draw_text(screen, "WELTRAUM SCHLACHT", 50, SCREEN_WIDTH/2, 100)
        draw_text(screen, "Wähle Schwierigkeitsgrad:", 30, SCREEN_WIDTH/2, 250)
        
        # Optionen
        for i, (name, _) in enumerate(difficulties):
            color = GREEN if i == selected_difficulty else WHITE
            draw_text(screen, name, 30, SCREEN_WIDTH/2, 300 + i * 40, color)
            
        draw_text(screen, "Pfeiltasten: Auswählen | Enter: Starten", 20, SCREEN_WIDTH/2, 500)
        pygame.display.flip()
    
    return "quit"

if __name__ == "__main__":
    status = "menu"
    while status != "quit":
        if status == "menu":
            status = show_menu()
        elif status == "restart_menu":
            status = "menu"
    
    pygame.quit()
