import pygame
import math
import collections
from datetime import datetime



# Brush sizes (pixels)
BRUSH_SIZES = {
    "small":  2,
    "medium": 5,
    "large":  10,
}

# Maps keyboard digit keys to size names
KEY_TO_SIZE = {
    pygame.K_1: "small",
    pygame.K_2: "medium",
    pygame.K_3: "large",
}

# All tool names available in the application
TOOLS = [
    "Pencil",
    "Line",
    "Rectangle",
    "Square",
    "Circle",
    "Rt Triangle",
    "Eq Triangle",
    "Rhombus",
    "Fill",
    "Eraser",
    "Text",
]


# Shape drawing

def draw_shape(surface, tool, color, p1, p2, brush_size=2):
    """
    Draw the shape identified by *tool* from grid point p1 to p2 on surface.
    """
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    w = brush_size   # shorthand

    if tool == "Pencil":
        # Draw one line segment between two consecutive mouse positions
        pygame.draw.line(surface, color, p1, p2, w)
        # Round cap at the end for smooth strokes
        pygame.draw.circle(surface, color, p2, max(1, w // 2))

    elif tool == "Line":
        # Straight line from p1 to p2
        pygame.draw.line(surface, color, p1, p2, w)

    elif tool == "Rectangle":
        # Axis-aligned rectangle defined by opposite corners p1 and p2
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(dx), abs(dy))
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(surface, color, rect, w)

    elif tool == "Square":
        # Like Rectangle but forces equal sides (min of |dx|, |dy|)
        side = min(abs(dx), abs(dy))
        rx   = x1 if dx >= 0 else x1 - side
        ry   = y1 if dy >= 0 else y1 - side
        rect = pygame.Rect(rx, ry, side, side)
        if side > 0:
            pygame.draw.rect(surface, color, rect, w)

    elif tool == "Circle":
        # Ellipse inscribed in the bounding box p1 → p2
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(dx), abs(dy))
        if rect.width > 0 and rect.height > 0:
            pygame.draw.ellipse(surface, color, rect, w)

    elif tool == "Rt Triangle":
        # Right-angle triangle: right angle at p1 (top-left corner)
        pts = [(x1, y1), (x1, y2), (x2, y1)]
        pygame.draw.polygon(surface, color, pts, w)

    elif tool == "Eq Triangle":
        # Equilateral triangle: base spans x1→x2 at y=y2; apex centred above
        base   = abs(dx)
        height = int(base * math.sqrt(3) / 2)
        apex_y = y2 - height if dy <= 0 else y2 + height
        pts = [(x1, y2), (x2, y2), ((x1 + x2) // 2, apex_y)]
        pygame.draw.polygon(surface, color, pts, w)

    elif tool == "Rhombus":
        # Diamond: four points at mid-edges of the bounding box
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, pts, w)



# Flood fill


def flood_fill(surface, start_x, start_y, fill_color):
    """
    Flood-fill *surface* starting at pixel (start_x, start_y) with *fill_color*.
    """
    # Clamp seed to surface bounds
    width, height = surface.get_size()
    start_x = max(0, min(width  - 1, start_x))
    start_y = max(0, min(height - 1, start_y))

    # Read the target colour at the seed pixel
    target_color = surface.get_at((start_x, start_y))[:3]   # ignore alpha

    # Nothing to do if seed is already the fill colour
    if target_color == fill_color[:3]:
        return

    # Lock surface for direct pixel access (much faster than repeated get/set_at)
    surface.lock()

    queue   = collections.deque()
    queue.append((start_x, start_y))
    visited = set()
    visited.add((start_x, start_y))

    while queue:
        x, y = queue.popleft()

        # Check this pixel still matches the target (guards against revisits)
        if surface.get_at((x, y))[:3] != target_color:
            continue

        # Paint the pixel
        surface.set_at((x, y), fill_color)

        # Enqueue the four neighbours if within bounds and not visited
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    surface.unlock()



# Text cursor / input handler


class TextCursor:
    """
    Manages an in-progress text entry session.
    """

    BLINK_INTERVAL = 500   # ms between cursor blink toggles
    FONT_SIZE = 24

    def __init__(self):
        self._active = False          # True while text entry is in progress
        self._text = ""             # characters typed so far
        self._pos = (0, 0)         # canvas-relative pixel position
        self._font = pygame.font.SysFont("Arial", self.FONT_SIZE)
        self._blink_on  = True           # current blink state
        self._last_blink = 0             # time of last blink toggle

    
    # Session control
    

    def start(self, canvas_x, canvas_y):
        """Begin a new text session at canvas pixel (canvas_x, canvas_y)."""
        self._active = True
        self._text = ""
        self._pos = (canvas_x, canvas_y)
        self._blink_on  = True
        self._last_blink = pygame.time.get_ticks()
        pygame.key.start_text_input()   # enable Unicode key events

    def cancel(self):
        """Discard current input and end the session."""
        self._active = False
        self._text   = ""
        pygame.key.stop_text_input()

    def is_active(self):
        """Return True while a text session is in progress."""
        return self._active


    # Input handling
  

    def handle_event(self, event):
        """
        Process a pygame event during an active text session.
        "confirm" — user pressed Enter; call render_to_canvas() next
        "cancel"— user pressed Escape; call cancel() next
        None — event consumed but session continues
        """
        if not self._active:
            return None

        if event.type == pygame.TEXTINPUT:
            # pygame.TEXTINPUT delivers correctly encoded Unicode characters
            self._text += event.text

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "confirm"
            elif event.key == pygame.K_ESCAPE:
                return "cancel"
            elif event.key == pygame.K_BACKSPACE:
                self._text = self._text[:-1]   # delete last character

        return None

   
    # Rendering
    

    def render_to_canvas(self, canvas, color):
        """
        Stamp the current text permanently onto *canvas* in *color*.
        Ends the session automatically.
        """
        if self._text:
            img = self._font.render(self._text, True, color)
            canvas.blit(img, self._pos)
        self.cancel()

    def draw_preview(self, surface, canvas_offset_x, canvas_offset_y, color):
        """
        Draw the live text preview (with blinking cursor) onto *surface*.
        canvas_offset_x/y convert canvas-relative _pos to screen coordinates.
        """
        if not self._active:
            return

        # Toggle blink state
        now = pygame.time.get_ticks()
        if now - self._last_blink >= self.BLINK_INTERVAL:
            self._blink_on   = not self._blink_on
            self._last_blink = now

        # Render current text
        display_text = self._text + ("|" if self._blink_on else " ")
        img = self._font.render(display_text, True, color)
        sx  = self._pos[0] + canvas_offset_x
        sy  = self._pos[1] + canvas_offset_y
        surface.blit(img, (sx, sy))


# Save canvas


def save_canvas(canvas):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"canvas_{timestamp}.png"
    pygame.image.save(canvas, filename)
    return filename