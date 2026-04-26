# HUD overlay and text-drawing helper

import pygame
from settings import WHITE, YELLOW, SCREEN_WIDTH

pygame.font.init()
font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 22)


def draw_text(surface, text, font, color, x, y, align="left"):
    """Render text onto surface at (x, y)"""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if align == "center":
        rect.centerx = x
        rect.top = y
    elif align == "right":
        rect.right = x
        rect.top = y
    else:
        rect.left = x
        rect.top = y
    surface.blit(rendered, rect)


class HUD:
    """Draws score and lives (top-left) and coin count (top-right)."""

    def draw(self, surface, score, lives, coins):
        # Score and lives — top left
        draw_text(surface, f"Score: {score}", font_small, WHITE, 10, 10)
        draw_text(surface, f"Lives: {lives}", font_small, WHITE, 10, 35)
        # Coin count — top right
        draw_text(surface, f"Coins: {coins}", font_small, YELLOW,
                  SCREEN_WIDTH - 10, 10, align="right")