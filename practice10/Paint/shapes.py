# functions for drawing all supported shapes onto a surface
 
import pygame
import math
from settings import SIDEBAR_WIDTH
 
 
def canvas_pos(mouse_xy):
    """Convert screen mouse coordinates to canvas-relative coordinates."""
    mx, my = mouse_xy
    return (mx - SIDEBAR_WIDTH, my)
 
 
def draw_shape(surface, tool, color, p1, p2, width=2): 
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
 
    if tool == "Rectangle":
        # Axis-aligned rectangle from p1 to p2
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(dx), abs(dy))
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(surface, color, rect, width)
 
    elif tool == "Square":
        # Like Rectangle, but forces equal sides (smaller of dx/dy)
        side = min(abs(dx), abs(dy))
        rx = x1 if dx >= 0 else x1 - side   # respect drag direction
        ry = y1 if dy >= 0 else y1 - side
        rect = pygame.Rect(rx, ry, side, side)
        if side > 0:
            pygame.draw.rect(surface, color, rect, width)
 
    elif tool == "Circle":
        # Ellipse inscribed in the bounding box p1→p2
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(dx), abs(dy))
        if rect.width > 0 and rect.height > 0:
            pygame.draw.ellipse(surface, color, rect, width)
 
    elif tool == "Rt Triangle":
        # Right angle at p1 (top-left); hypotenuse connects bottom-left to top-right
        pts = [
            (x1, y1),   # top-left  — the right angle
            (x1, y2),   # bottom-left
            (x2, y1),   # top-right
        ]
        pygame.draw.polygon(surface, color, pts, width)
 
    elif tool == "Eq Triangle":
        # Equilateral triangle: base runs from p1 to p2 along y2,
        # apex is centered above the base at height = base * sqrt(3) / 2
        base   = abs(dx)
        height = int(base * math.sqrt(3) / 2)
        apex_y = y2 - height if dy <= 0 else y2 + height
        pts = [
            (x1, y2), # base left
            (x2, y2),  # base right
            ((x1 + x2) // 2, apex_y),  # apex
        ]
        pygame.draw.polygon(surface, color, pts, width)
 
    elif tool == "Rhombus":
        # Diamond shape: four corners at the midpoints of the bounding box edges
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        pts = [
            (cx, y1),   # top
            (x2, cy),   # right
            (cx, y2),   # bottom
            (x1, cy),   # left
        ]
        pygame.draw.polygon(surface, color, pts, width)
 