# draws the left sidebar and handles click detection

import pygame
from settings import (
    SCREEN_HEIGHT, SIDEBAR_WIDTH, TOOLS, PALETTE,
    GREY, DARK_GREY, LIGHT_GREY, BLACK,
)

# Fonts used inside the sidebar
pygame.font.init()
font = pygame.font.SysFont("Arial", 14, bold=True)
font_tiny = pygame.font.SysFont("Arial", 12)

# Palette layout constants
SWATCH_SIZE = 26    # pixel size of each color swatch
SWATCH_GAP = 4     # gap between swatches
PALETTE_COLS = 4    # number of swatch columns


def _palette_start_y():
    """Y coordinate where the color palette section begins."""
    return 32 + len(TOOLS) * 34 + 16 + 20   # below tool buttons + header


def draw_tool_button(surface, label, rect, selected):
    """Draw one tool button; highlighted in blue if it is the active tool."""
    bg_color = (180, 210, 255) if selected else LIGHT_GREY
    pygame.draw.rect(surface, bg_color, rect, border_radius=4)
    pygame.draw.rect(surface, DARK_GREY, rect, 1, border_radius=4)
    text = font_tiny.render(label, True, BLACK)
    surface.blit(text, (rect.x + 6, rect.y + (rect.height - text.get_height()) // 2))


def draw_sidebar(surface, current_tool, current_color, brush_size):
 
    # Background and right-edge divider line
    pygame.draw.rect(surface, GREY, (0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(surface, DARK_GREY,
                     (SIDEBAR_WIDTH - 1, 0), (SIDEBAR_WIDTH - 1, SCREEN_HEIGHT))

    # Tool buttons 
    surface.blit(font.render("TOOLS", True, DARK_GREY), (10, 10))
    for i, tool in enumerate(TOOLS):
        btn_rect = pygame.Rect(8, 32 + i * 34, SIDEBAR_WIDTH - 16, 28)
        draw_tool_button(surface, tool, btn_rect, tool == current_tool)

    # Color palette header 
    palette_y = _palette_start_y() - 20
    surface.blit(font.render("COLORS", True, DARK_GREY), (10, palette_y))
    palette_y += 20

    # Color swatches 
    for idx, col in enumerate(PALETTE):
        col_i = idx % PALETTE_COLS
        row_i = idx // PALETTE_COLS
        sx = 8 + col_i * (SWATCH_SIZE + SWATCH_GAP)
        sy = palette_y + row_i * (SWATCH_SIZE + SWATCH_GAP)
        rect = pygame.Rect(sx, sy, SWATCH_SIZE, SWATCH_SIZE)
        pygame.draw.rect(surface, col, rect)
        # Thick black border on the selected colour; thin grey on the rest
        border = 3 if col == current_color else 1
        border_col = BLACK if col == current_color else DARK_GREY
        pygame.draw.rect(surface, border_col, rect, border)

    # Active colour preview 
    rows = (len(PALETTE) + PALETTE_COLS - 1) // PALETTE_COLS
    preview_y = palette_y + rows * (SWATCH_SIZE + SWATCH_GAP) + 10
    surface.blit(font.render("Active:", True, DARK_GREY), (10, preview_y))
    preview_rect = pygame.Rect(10, preview_y + 18, SIDEBAR_WIDTH - 20, 24)
    pygame.draw.rect(surface, current_color, preview_rect)
    pygame.draw.rect(surface, BLACK, preview_rect, 1)

    # Brush size info 
    size_y = preview_y + 54
    surface.blit(font_tiny.render(f"Brush: {brush_size}px", True, DARK_GREY), (10, size_y))
    surface.blit(font_tiny.render("[+/-] to resize", True, DARK_GREY), (10, size_y + 14))


def get_clicked_tool(mouse_xy):
    """Return the tool name if a tool button was clicked, else None."""
    mx, my = mouse_xy
    if mx >= SIDEBAR_WIDTH:
        return None
    for i, tool in enumerate(TOOLS):
        btn_rect = pygame.Rect(8, 32 + i * 34, SIDEBAR_WIDTH - 16, 28)
        if btn_rect.collidepoint(mx, my):
            return tool
    return None


def get_clicked_color(mouse_xy):
    """Return the palette colour tuple if a swatch was clicked, else None."""
    mx, my = mouse_xy
    if mx >= SIDEBAR_WIDTH:
        return None
    palette_y = _palette_start_y()
    for idx, col in enumerate(PALETTE):
        col_i = idx % PALETTE_COLS
        row_i = idx // PALETTE_COLS
        sx = 8 + col_i * (SWATCH_SIZE + SWATCH_GAP)
        sy = palette_y + row_i * (SWATCH_SIZE + SWATCH_GAP)
        if pygame.Rect(sx, sy, SWATCH_SIZE, SWATCH_SIZE).collidepoint(mx, my):
            return col
    return None