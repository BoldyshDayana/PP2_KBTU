#Snake game entry point.

import pygame
import sys

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, HUD_HEIGHT,
    CELL_SIZE, GRID_COLS, GRID_ROWS,
    UP, DOWN, LEFT, RIGHT,
    LEVELS, BLACK, WHITE,
    DARK_GREEN, SNAKE_HEAD,
)
from grid  import Grid
from snake import Snake
from food  import FoodManager
from hud   import draw_hud



# Screen helpers

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

font_big  = pygame.font.SysFont("Arial", 42, bold=True)
font_med  = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18)


def draw_centered(surface, text, font, color, y):
    """Blit text centered horizontally at a given y position."""
    img = font.render(text, True, color)
    surface.blit(img, (SCREEN_WIDTH // 2 - img.get_width() // 2, y))


def show_message_screen(lines):
    """
    Display a simple overlay with multiple lines of text.
    Each line is a (text, font, colour) tuple.
    Waits for SPACE or ENTER to continue, or ESCAPE/QUIT to exit.
    Returns True to continue, False to quit.
    """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    y = SCREEN_HEIGHT // 2 - len(lines) * 28
    for text, font, color in lines:
        draw_centered(screen, text, font, color, y)
        y += font.get_height() + 10

    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
    return False



# Level helper

def get_level_and_delay(foods_eaten):
    """
    Return (level_number_1based, move_delay_ms) based on total foods eaten.
    Scans LEVELS list to find the highest level the player has reached.
    """
    current_level = 1
    current_delay = LEVELS[0]["delay"]
    for i, lvl in enumerate(LEVELS):
        if foods_eaten >= lvl["foods_needed"]:
            current_level = i + 1
            current_delay = lvl["delay"]
    return current_level, current_delay



# Main game

def run_game():
    """Run one full game session. Returns True to play again, False to quit."""
    grid = Grid()
    snake = Snake()
    food_manager = FoodManager()

    score = 0
    foods_eaten = 0   # total foods collected (drives level progression)
    level = 1

    # Move timer: snake advances one cell every move_delay milliseconds
    move_delay = LEVELS[0]["delay"]
    last_move_time = pygame.time.get_ticks()

    # Show start screen
    screen.fill(BLACK)
    grid.draw(screen)
    cont = show_message_screen([
        ("SNAKE", font_big, SNAKE_HEAD),
        ("Arrow keys to move", font_med, WHITE),
        ("Eat food before", font_small, (200, 200, 200)),
        ("it disappears!", font_small, (200, 200, 200)),
        ("Press SPACE to start", font_med, (150, 255, 150)),
    ])
    if not cont:
        return False

    running = True
    while running:
        now = pygame.time.get_ticks()
        clock.tick(FPS)

        # Input 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_UP:
                    snake.set_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.set_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.set_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction(RIGHT)

        # Game tick (move snake at fixed intervals) 
        if now - last_move_time >= move_delay:
            last_move_time = now

            # Move snake one cell
            new_head = snake.move()
            col, row = new_head

            # Collision: wall
            if grid.is_wall(col, row):
                break   # snake hit a wall - game over

            # Collision: self 
            if snake.hit_self():
                break   # snake ran into its own body → game over

            # Collect food 
            weight = food_manager.eat_at(col, row)
            if weight > 0:
                snake.grow()             # grow by one cell
                score       += weight    # add food weight to score
                foods_eaten += 1         # track for level progression

                # Check for level-up
                new_level, new_delay = get_level_and_delay(foods_eaten)
                if new_level > level:
                    level = new_level
                    move_delay = new_delay   # increase speed

            # Update food (expire old, spawn new)
            food_manager.update(grid, snake)

        # Render
        screen.fill(BLACK)
        grid.draw(screen)
        food_manager.draw(screen, grid)
        snake.draw(screen, grid)
        draw_hud(screen, score, level, foods_eaten)
        pygame.display.flip()

    # Game Over screen
    return show_message_screen([
        ("GAME OVER", font_big, (220, 60, 60)),
        (f"Score: {score}", font_med, WHITE),
        (f"Level: {level}", font_med, (100, 220, 255)),
        ("SPACE = play again", font_small, (150, 255, 150)),
        ("ESC   = quit", font_small, (200, 200, 200)),
    ])



# Entry point
def main():
    while True:
        play_again = run_game()
        if not play_again:
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
