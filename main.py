import pygame
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 40
PLAYER_SPEED = 5
BULLET_SPEED = -10
ENEMY_SIZE = 40
ENEMY_SPEED = 30
PELLET_SIZE = 10
POWER_PELLET_SIZE = 20
PLAYER_MAX_Y = SCREEN_HEIGHT - PLAYER_SIZE // 2 - 10  # Fixed: allow lower movement

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paku Invaders Deluxe")

# Clock
clock = pygame.time.Clock()

# Load font
font = pygame.font.SysFont(None, 36)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.score = 0
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.rect.y < PLAYER_MAX_Y:
            self.rect.y += PLAYER_SPEED
        self.rect.clamp_ip(screen.get_rect())

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.color = color
        self.is_scared = False
        self.chasing = False

    def update(self, current_time, dx=0, dy=0):
        if self.chasing:
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
            if direction.length() > 0:
                direction = direction.normalize()
                self.rect.move_ip(direction.x * 2, direction.y * 2)
        else:
            self.rect.move_ip(dx, dy)

class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PELLET_SIZE, PELLET_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

class PowerPellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((POWER_PELLET_SIZE, POWER_PELLET_SIZE))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(x, y))

# Groups
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
pellets = pygame.sprite.Group()
power_pellets = pygame.sprite.Group()

# Game state
score = 0
wave = 1
scared_until = 0
game_state = "start"

# Functions
def spawn_enemies(rows, cols):
    padding = 10
    start_x = 100
    start_y = 50
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (ENEMY_SIZE + padding)
            y = start_y + row * (ENEMY_SIZE + padding)
            color = random.choice([RED, GREEN, BLUE])
            enemy = Enemy(x, y, color)
            enemies.add(enemy)
            all_sprites.add(enemy)

def spawn_pellets():
    for _ in range(10):
        pellet_zone_bottom = PLAYER_MAX_Y - 10
        x = random.randint(20, SCREEN_WIDTH - 20)
        y = random.randint(SCREEN_HEIGHT // 2, pellet_zone_bottom)
        pellet = Pellet(x, y)
        pellets.add(pellet)
        all_sprites.add(pellet)

def spawn_power_pellet():
    pellet_zone_bottom = PLAYER_MAX_Y - 10
    x = random.randint(20, SCREEN_WIDTH - 20)
    y = random.randint(SCREEN_HEIGHT // 2, pellet_zone_bottom)
    power_pellet = PowerPellet(x, y)
    power_pellets.add(power_pellet)
    all_sprites.add(power_pellet)

def reset_game():
    global game_state, wave, score
    player.lives = 3
    player.score = 0
    wave = 1
    score = 0
    for group in [enemies, bullets, pellets, power_pellets]:
        group.empty()
    all_sprites.empty()
    all_sprites.add(player)
    spawn_enemies(3, 8)
    spawn_pellets()
    spawn_power_pellet()
    game_state = "playing"

# Game loop
running = True
move_direction = 1
move_timer = 0
move_delay = 600
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "start" and event.key == pygame.K_SPACE:
                reset_game()
            if event.key == pygame.K_SPACE and game_state == "playing":
                bullet = Bullet(player.rect.centerx, player.rect.top)
                bullets.add(bullet)
                all_sprites.add(bullet)

    keys = pygame.key.get_pressed()
    if game_state == "playing":
        player.update(keys)

        bullets.update()

        # Ghost random chase
        if random.random() < 0.002:
            bottom_row_enemies = [e for e in enemies if all(other.rect.y <= e.rect.y for other in enemies)]
            if bottom_row_enemies:
                chaser = random.choice(bottom_row_enemies)
                chaser.chasing = True

        # Enemy movement
        if current_time - move_timer > move_delay:
            move_timer = current_time
            dx = ENEMY_SPEED * move_direction
            dy = 0
            for enemy in enemies:
                enemy.rect.x += dx
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    move_direction *= -1
                    dy = ENEMY_SIZE // 2
                    break
            for enemy in enemies:
                enemy.update(current_time, 0, dy)
        else:
            for enemy in enemies:
                enemy.update(current_time)

        # Bullet collisions
        for bullet in bullets:
            enemy_hit = pygame.sprite.spritecollideany(bullet, enemies)
            if enemy_hit:
                bullet.kill()
                player.score += 100
                enemy_hit.kill()

        # Pellet collection
        for pellet in pygame.sprite.spritecollide(player, pellets, True):
            player.score += 10

        # Power pellet collection
        for power in pygame.sprite.spritecollide(player, power_pellets, True):
            scared_until = current_time + 8000
            for enemy in enemies:
                enemy.is_scared = True

        # Scared timer
        if current_time > scared_until:
            for enemy in enemies:
                enemy.is_scared = False

        # Player collides with ghost
        for enemy in pygame.sprite.spritecollide(player, enemies, False):
            if enemy.is_scared:
                enemy.kill()
                player.score += 200
            else:
                player.lives -= 1
                if player.lives <= 0:
                    game_state = "game_over"
                else:
                    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        # Next wave
        if not enemies:
            wave += 1
            spawn_enemies(3, 8)
            spawn_pellets()
            spawn_power_pellet()

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (10, 50))

    if game_state == "start":
        title = font.render("Paku Invaders Deluxe", True, YELLOW)
        prompt = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 40))
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))
    elif game_state == "game_over":
        game_over = font.render("Game Over", True, RED)
        prompt = font.render("Press SPACE to Restart", True, WHITE)
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//2 - 40))
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))

    pygame.display.flip()

pygame.quit()




