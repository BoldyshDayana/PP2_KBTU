#game loop and entry point
 
import pygame
import sys
 
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, RED, WHITE, YELLOW
from road import Road
from player import PlayerCar
from enemy import EnemyCar
from coin import Coin
from hud import HUD, draw_text, font_large, font_small
 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racer")
    clock = pygame.time.Clock()
 
    # Create game objects
    road = Road()
    player = PlayerCar()
    hud = HUD()
 
    enemies = []   # active EnemyCar objects
    coins = []   # active Coin objects
 
    score = 0
    lives = 3
    coin_count = 0   # coins collected
 
    base_speed = 5
    current_speed = base_speed
 
    # Spawn timers 
    enemy_spawn_timer = 0
    enemy_spawn_delay = 1500
    coin_spawn_timer  = 0
    coin_spawn_delay  = 2000
 
    running = True
 
    while running:
        dt = clock.tick(FPS)   # ms since last frame; also caps FPS
 
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
 
        # Difficulty: speed and spawn rate increase over time
        score += 1
        current_speed = base_speed + score // 500
        enemy_spawn_delay = max(600, 1500 - score // 10)
 
        # Spawn enemies
        enemy_spawn_timer += dt
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemies.append(EnemyCar(current_speed))
            enemy_spawn_timer = 0
 
        # Spawn coins randomly on the road 
        coin_spawn_timer += dt
        if coin_spawn_timer >= coin_spawn_delay:
            coins.append(Coin(current_speed))
            coin_spawn_timer = 0
 
        # Update player and road 
        keys = pygame.key.get_pressed()
        player.update(keys)
        road.update()
 
        # Update enemies; check collision with player 
        for enemy in enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                enemies.remove(enemy)
            elif player.rect.colliderect(enemy.rect):
                lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    running = False
 
        # Update coins; check if player collects them 
        for coin in coins[:]:
            coin.update()
            if coin.is_off_screen():
                coins.remove(coin)
            elif player.rect.colliderect(coin.rect):
                coin_count += 1
                score      += 50   # bonus points for collecting a coin
                coins.remove(coin)
 
        # Draw
        screen.fill(BLACK)
        road.draw(screen)
 
        for coin in coins:      
            coin.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)
 
        hud.draw(screen, score, lives, coin_count)  
        pygame.display.flip()
 
    # Game-over screen 
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", font_large, RED,    SCREEN_WIDTH // 2, 200, align="center")
    draw_text(screen, f"Score: {score}", font_small, WHITE,  SCREEN_WIDTH // 2, 260, align="center")
    draw_text(screen, f"Coins: {coin_count}", font_small, YELLOW, SCREEN_WIDTH // 2, 290, align="center")
    draw_text(screen, "Press any key to exit",font_small, WHITE,  SCREEN_WIDTH // 2, 340, align="center")
    pygame.display.flip()
 
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                waiting = False
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()