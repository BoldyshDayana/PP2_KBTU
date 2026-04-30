# Controls:
#   Mouse drag — draw with the active tool
#   1 / 2 / 3  — switch brush size (small / medium / large)
#   Ctrl + S  — save canvas as timestamped PNG
#   C — clear canvas
#   ESC — quit  (or cancel text entry)

import pygame
import sys

from tools import (
    TOOLS, BRUSH_SIZES, KEY_TO_SIZE,
    draw_shape, flood_fill, save_canvas, TextCursor,
)

# Initialisation

pygame.init()

SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 700
SIDEBAR_W  = 170         

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()
FPS = 60

# Canvas sits to the right of the sidebar, full screen height
CANVAS_X = SIDEBAR_W
CANVAS_W = SCREEN_WIDTH - SIDEBAR_W
CANVAS_H = SCREEN_HEIGHT
canvas_rect = pygame.Rect(CANVAS_X, 0, CANVAS_W, CANVAS_H)

# Persistent drawing surface — all committed strokes live here
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((255, 255, 255))   # start with a white background


# Colour palette

PALETTE = [
    (0,   0,   0),      # black
    (255, 255, 255),    # white
    (200, 0,   0),      # red
    (0,   180, 0),      # green
    (0,   0,   200),    # blue
    (255, 165, 0),      # orange
    (255, 255, 0),      # yellow
    (128, 0,   128),    # purple
    (0,   200, 200),    # cyan
    (255, 105, 180),    # pink
    (139, 69,  19),     # brown
    (80,  80,  80),     # dark grey
]


# Fonts

font_bold  = pygame.font.SysFont("Arial", 13, bold=True)
font_small = pygame.font.SysFont("Arial", 12)


# Application state

current_tool  = "Pencil"
current_color = (0, 0, 0)
brush_name    = "medium"          # "small" | "medium" | "large"
drawing       = False             # True while left mouse button is held
start_pos     = (0, 0)           # canvas-relative drag start
last_pos      = (0, 0)           # previous mouse pos (pencil continuity)
text_cursor   = TextCursor()      # handles text tool state
status_msg    = ""                # temporary status line (e.g. "Saved!")
status_timer  = 0                 # time when status_msg was set


# Coordinate helper
def to_canvas(screen_xy):
    """Convert a screen-space (x, y) to canvas-space coordinates."""
    mx, my = screen_xy
    return (mx - CANVAS_X, my)



# Sidebar layout helpers

def _tool_rect(index):
    """Return the pygame.Rect for tool button at *index*."""
    return pygame.Rect(6, 30 + index * 32, SIDEBAR_W - 12, 26)


def _size_rect(index):
    """Return the pygame.Rect for the brush-size button at *index* (0/1/2)."""
    palette_y   = 30 + len(TOOLS) * 32 + 14
    size_row_y  = palette_y + 24 + _palette_rows() * 30 + 14
    w = (SIDEBAR_W - 18) // 3
    return pygame.Rect(6 + index * (w + 3), size_row_y, w, 24)


def _palette_rows():
    """Number of rows in the colour swatch grid."""
    return (len(PALETTE) + 3) // 4   # 4 swatches per row


def _swatch_rect(index):
    """Return the pygame.Rect for palette swatch at *index*."""
    palette_y  = 30 + len(TOOLS) * 32 + 14
    col_i      = index % 4
    row_i      = index // 4
    return pygame.Rect(6 + col_i * 38, palette_y + 24 + row_i * 30, 32, 24)



# Sidebar drawing


def draw_sidebar(surface):
    """Render the full left sidebar: tools, brush sizes, palette, and hints."""
    # Background
    pygame.draw.rect(surface, (210, 210, 210), (0, 0, SIDEBAR_W, SCREEN_HEIGHT))
    pygame.draw.line(surface, (130, 130, 130), (SIDEBAR_W - 1, 0), (SIDEBAR_W - 1, SCREEN_HEIGHT))

    # --- Section: Tools ---
    lbl = font_bold.render("TOOLS", True, (60, 60, 60))
    surface.blit(lbl, (8, 10))

    for i, tool in enumerate(TOOLS):
        rect = _tool_rect(i)
        selected = (tool == current_tool)
        bg = (160, 200, 255) if selected else (230, 230, 230)
        pygame.draw.rect(surface, bg, rect, border_radius=4)
        pygame.draw.rect(surface, (120, 120, 120), rect, 1, border_radius=4)
        txt = font_small.render(tool, True, (0, 0, 0))
        surface.blit(txt, (rect.x + 5, rect.y + (rect.height - txt.get_height()) // 2))

    # Brush size 
    palette_y  = 30 + len(TOOLS) * 32 + 14
    size_row_y = palette_y + 24 + _palette_rows() * 30 + 14

    size_lbl = font_bold.render("SIZE  [1/2/3]", True, (60, 60, 60))
    surface.blit(size_lbl, (6, size_row_y - 16))

    size_labels = [("S", "small"), ("M", "medium"), ("L", "large")]
    for i, (label, name) in enumerate(size_labels):
        rect     = _size_rect(i)
        selected = (brush_name == name)
        bg       = (160, 200, 255) if selected else (230, 230, 230)
        pygame.draw.rect(surface, bg, rect, border_radius=4)
        pygame.draw.rect(surface, (120, 120, 120), rect, 1, border_radius=4)
        txt = font_bold.render(label, True, (0, 0, 0))
        surface.blit(txt, txt.get_rect(center=rect.center))

    # Colour palette 
    col_lbl = font_bold.render("COLORS", True, (60, 60, 60))
    surface.blit(col_lbl, (6, palette_y))

    for idx, col in enumerate(PALETTE):
        rect   = _swatch_rect(idx)
        pygame.draw.rect(surface, col, rect)
        border = (0, 0, 0) if col == current_color else (120, 120, 120)
        thick  = 3 if col == current_color else 1
        pygame.draw.rect(surface, border, rect, thick)

    # Active colour preview
    preview_y = size_row_y + 30
    pygame.draw.rect(surface, current_color, pygame.Rect(6, preview_y, SIDEBAR_W - 12, 22))
    pygame.draw.rect(surface, (0, 0, 0),     pygame.Rect(6, preview_y, SIDEBAR_W - 12, 22), 1)

    # Keyboard hints
    hints = [
        "Ctrl+S  save",
        "C       clear",
        "ESC     quit",
    ]
    hy = preview_y + 30
    for hint in hints:
        ht = font_small.render(hint, True, (80, 80, 80))
        surface.blit(ht, (6, hy))
        hy += 14

    # Status message (e.g. "Saved!")
    if status_msg:
        sm = font_bold.render(status_msg, True, (0, 120, 0))
        surface.blit(sm, (6, hy + 6))



# Sidebar click detection


def clicked_tool(pos):
    """Return the tool name if a tool button was clicked, else None."""
    mx, my = pos
    if mx >= SIDEBAR_W:
        return None
    for i, tool in enumerate(TOOLS):
        if _tool_rect(i).collidepoint(mx, my):
            return tool
    return None


def clicked_size(pos):
    """Return the brush size name if a size button was clicked, else None."""
    mx, my = pos
    if mx >= SIDEBAR_W:
        return None
    size_names = ["small", "medium", "large"]
    for i, name in enumerate(size_names):
        if _size_rect(i).collidepoint(mx, my):
            return name
    return None


def clicked_color(pos):
    """Return the palette colour if a swatch was clicked, else None."""
    mx, my = pos
    if mx >= SIDEBAR_W:
        return None
    for idx, col in enumerate(PALETTE):
        if _swatch_rect(idx).collidepoint(mx, my):
            return col
    return None



# Main loop


def main():
    global current_tool, current_color, brush_name, drawing
    global start_pos, last_pos, status_msg, status_timer

    running = True

    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        # Clear status message after 2 seconds
        if status_msg and now - status_timer > 2000:
            status_msg = ""


        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Text tool
            if text_cursor.is_active():
                result = text_cursor.handle_event(event)
                if result == "confirm":
                    # Stamp text permanently onto canvas
                    text_cursor.render_to_canvas(canvas, current_color)
                elif result == "cancel":
                    text_cursor.cancel()
                # Consume all events while text input is active
                if event.type in (pygame.TEXTINPUT, pygame.KEYDOWN):
                    continue

            # --- Keyboard shortcuts ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Brush size via digit keys
                elif event.key in KEY_TO_SIZE:
                    brush_name = KEY_TO_SIZE[event.key]

                # Clear canvas
                elif event.key == pygame.K_c and not (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    canvas.fill((255, 255, 255))

                # Save canvas (Ctrl+S)
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    filename     = save_canvas(canvas)
                    status_msg   = f"Saved: {filename}"
                    status_timer = now

            #Mouse button pressed
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                mx, my = pos

                # Check sidebar interactions first
                t = clicked_tool(pos)
                s = clicked_size(pos)
                c = clicked_color(pos)

                if t:
                    current_tool = t
                elif s:
                    brush_name = s
                elif c is not None:
                    current_color = c
                elif canvas_rect.collidepoint(mx, my):
                    # Click is on the canvas
                    cp = to_canvas(pos)

                    if current_tool == "Fill":
                        # Flood-fill immediately on click
                        flood_fill(canvas, cp[0], cp[1], current_color)

                    elif current_tool == "Text":
                        # Start a text session at the clicked position
                        text_cursor.start(cp[0], cp[1])

                    else:
                        # Begin a drag for pencil / shape tools
                        drawing   = True
                        start_pos = cp
                        last_pos  = cp

            # Mouse button released — commit shape to canvas
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    end_pos = to_canvas(event.pos)
                    # Shapes (not pencil/eraser) are stamped on release
                    if current_tool not in ("Pencil", "Eraser", "Fill", "Text"):
                        draw_shape(canvas, current_tool, current_color,
                                   start_pos, end_pos,
                                   brush_size=BRUSH_SIZES[brush_name])
                drawing = False

            # Mouse motion — pencil draws continuously
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    cur = to_canvas(event.pos)

                    if current_tool == "Pencil":
                        # Draw line segment from last position to current
                        draw_shape(canvas, "Pencil", current_color,
                                   last_pos, cur,
                                   brush_size=BRUSH_SIZES[brush_name])
                        last_pos = cur

                    elif current_tool == "Eraser":
                        # Eraser paints white continuously
                        draw_shape(canvas, "Pencil", (255, 255, 255),
                                   last_pos, cur,
                                   brush_size=BRUSH_SIZES[brush_name] * 3)
                        last_pos = cur

      
        # Rendering
  
        screen.fill((255, 255, 255))

        # Blit the permanent canvas
        screen.blit(canvas, (CANVAS_X, 0))

        # Live preview for shape / line tools while dragging
        if drawing and current_tool not in ("Pencil", "Eraser", "Fill", "Text"):
            cur_pos = to_canvas(pygame.mouse.get_pos())
            # Draw preview on a copy so the canvas is not modified
            preview = canvas.copy()
            draw_shape(preview, current_tool, current_color,
                       start_pos, cur_pos,
                       brush_size=BRUSH_SIZES[brush_name])
            screen.blit(preview, (CANVAS_X, 0))

        # Text cursor preview (blinking cursor + typed text)
        if text_cursor.is_active():
            text_cursor.draw_preview(screen, CANVAS_X, 0, current_color)

        # Sidebar drawn last so it always appears on top
        draw_sidebar(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()



# Entry point
if __name__ == "__main__":
    main()