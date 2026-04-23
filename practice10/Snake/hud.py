#Heads-Up Display: draws the score, level, and progress bar at the top of the screen.

import pygame
from settings import (
    SCREEN_WIDTH, HUD_HEIGHT, LEVELS,
    HUD_BG, WHITE, BLACK,
    FOOD_COLORS,
)

pygame.font.init()
_font_large = pygame.font.SysFont("Arial", 26, bold=True)
_font_small = pygame.font.SysFont("Arial", 16)


def draw_hud(surface, score, level, foods_eaten):
    """
    Render the HUD bar at the top of the screen.

    Parameters:
        surface  — main pygame display surface
        score — current total score (int)
        level   — current level number, 1-based (int)
        foods_eaten — total foods eaten this session (int)
    """
    # Background bar
    pygame.draw.rect(surface, HUD_BG, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
    pygame.draw.line(surface, (60, 60, 60), (0, HUD_HEIGHT - 1), (SCREEN_WIDTH, HUD_HEIGHT - 1))

    # Score text
    score_txt = _font_large.render(f"Score: {score}", True, WHITE)
    surface.blit(score_txt, (12, (HUD_HEIGHT - score_txt.get_height()) // 2))

    # Level text
    level_txt = _font_large.render(f"Level: {level}", True, (100, 220, 255))
    surface.blit(level_txt, (SCREEN_WIDTH // 2 - level_txt.get_width() // 2,
                              (HUD_HEIGHT - level_txt.get_height()) // 2))

    # Progress bar toward next level
    current_lvl_data = LEVELS[min(level - 1, len(LEVELS) - 1)]
    next_lvl_data    = LEVELS[min(level, len(LEVELS) - 1)]

    foods_at_start = current_lvl_data["foods_needed"]
    foods_at_next  = next_lvl_data["foods_needed"]

    if foods_at_next > foods_at_start:
        progress = (foods_eaten - foods_at_start) / (foods_at_next - foods_at_start)
    else:
        progress = 1.0   # max level reached

    bar_w  = 120
    bar_h  = 10
    bar_x  = SCREEN_WIDTH - bar_w - 12
    bar_y  = (HUD_HEIGHT - bar_h) // 2 + 8

    # Background track
    pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
    # Filled portion
    fill_w = int(bar_w * min(progress, 1.0))
    if fill_w > 0:
        pygame.draw.rect(surface, (80, 200, 100), (bar_x, bar_y, fill_w, bar_h), border_radius=5)
    # Border
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=5)

    # "Next level" label above the bar
    lbl = _font_small.render("Next lvl", True, (180, 180, 180))
    surface.blit(lbl, (bar_x + bar_w // 2 - lbl.get_width() // 2, bar_y - 16))