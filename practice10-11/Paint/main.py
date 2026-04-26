# initialises pygame, runs the main game loop
 
import pygame
import sys
 
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SIDEBAR_WIDTH, WHITE, BLACK
from shapes import draw_shape, canvas_pos
from sidebar import draw_sidebar, get_clicked_tool, get_clicked_color
 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()
 
    # Canvas is the persistent drawing surface (everything right of the sidebar)
    canvas_w = SCREEN_WIDTH - SIDEBAR_WIDTH
    canvas   = pygame.Surface((canvas_w, SCREEN_HEIGHT))
    canvas.fill(WHITE)
    canvas_rect = pygame.Rect(SIDEBAR_WIDTH, 0, canvas_w, SCREEN_HEIGHT)
 
    # App state
    current_tool = "Pencil"   # active tool
    current_color = BLACK      # active drawing colour
    brush_size = 4          # pencil / eraser radius in pixels
    drawing = False      # True while the left mouse button is held
    start_pos = (0, 0)     # canvas-relative drag start position
    last_pos = (0, 0)     # previous mouse pos (used by pencil for smooth lines)
 
    running = True
    while running:
        clock.tick(FPS)
 
        # Event handling 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Increase brush size
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    brush_size = min(50, brush_size + 1)
                # Decrease brush size
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    brush_size = max(1, brush_size - 1)
                # Clear the canvas
                elif event.key == pygame.K_c:
                    canvas.fill(WHITE)
 
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check sidebar first; only start drawing if click is on canvas
                clicked_tool  = get_clicked_tool(event.pos)
                clicked_color = get_clicked_color(event.pos)
 
                if clicked_tool:
                    current_tool = clicked_tool
                elif clicked_color is not None:
                    current_color = clicked_color
                elif canvas_rect.collidepoint(event.pos):
                    drawing   = True
                    start_pos = canvas_pos(event.pos)
                    last_pos  = start_pos
 
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    end_pos = canvas_pos(event.pos)
                    # Commit shape tools to the canvas on mouse release
                    if current_tool not in ("Pencil", "Eraser"):
                        draw_shape(canvas, current_tool, current_color,
                                   start_pos, end_pos, width=2)
                drawing = False
 
            elif event.type == pygame.MOUSEMOTION:
                # Pencil and Eraser paint continuously as the mouse moves
                if drawing and current_tool in ("Pencil", "Eraser"):
                    cur   = canvas_pos(event.pos)
                    color = WHITE if current_tool == "Eraser" else current_color
                    pygame.draw.line(canvas, color, last_pos, cur, brush_size * 2)
                    pygame.draw.circle(canvas, color, cur, brush_size)  # smooth end-cap
                    last_pos = cur
 
        # Rendering 
        screen.fill(WHITE)
 
        # Draw the permanent canvas content
        screen.blit(canvas, (canvas_rect.x, canvas_rect.y))
 
        # For shape tools: show a live preview while the mouse is dragged
        if drawing and current_tool not in ("Pencil", "Eraser"):
            cur_pos = canvas_pos(pygame.mouse.get_pos())
            preview = canvas.copy()   # copy prevents modifying the real canvas
            draw_shape(preview, current_tool, current_color,
                       start_pos, cur_pos, width=2)
            screen.blit(preview, (canvas_rect.x, canvas_rect.y))
 
        # Sidebar is drawn last so it always appears on top
        draw_sidebar(screen, current_tool, current_color, brush_size)
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()
 