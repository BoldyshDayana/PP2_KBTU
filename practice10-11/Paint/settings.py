# all shared constants for the Paint application

# Screen dimensions and frame rate
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# colours
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
GREY = (200, 200, 200)
DARK_GREY  = (100, 100, 100)
LIGHT_GREY = (230, 230, 230)

# Selectable drawing colours shown in the palette
PALETTE = [
    (0, 0, 0),      # black
    (255, 255, 255),    # white
    (200, 0, 0),      # red
    (0, 180, 0),      # green
    (0, 0, 200),    # blue
    (255, 165, 0),      # orange
    (255, 255, 0),      # yellow
    (128, 0, 128),    # purple
    (0, 200, 200),    # cyan
    (255, 105, 180),    # pink
    (139, 69, 19),     # brown
    (64, 64, 64),     # dark grey
]

# Sidebar width; canvas starts to the right of it
SIDEBAR_WIDTH = 150

# Available drawing tools (order determines button order)
TOOLS = [
    "Pencil",
    "Eraser",
    "Rectangle",
    "Square",
    "Circle",
    "Rt Triangle",    # right-angle triangle
    "Eq Triangle",    # equilateral triangle
    "Rhombus",
]