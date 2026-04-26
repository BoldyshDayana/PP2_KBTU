# all shared constants for the Snake game

# Grid dimensions 
CELL_SIZE = 24        # pixel size of one grid cell
GRID_COLS = 25        # number of columns in the playing area
GRID_ROWS = 25        # number of rows in the playing area

# HUD bar at the top 
HUD_HEIGHT = 48        # pixels reserved above the grid for score/level display

# Derived screen dimensions 
SCREEN_WIDTH = CELL_SIZE * GRID_COLS
SCREEN_HEIGHT = CELL_SIZE * GRID_ROWS + HUD_HEIGHT

# Frame rate 
FPS = 60

# Colours 
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
DARK_GREEN = (20,  120, 20)    # grid background
GRID_LINE = (30,  140, 30)    # faint grid lines
WALL_COLOR = (60,  60,  60)    # border wall colour
SNAKE_HEAD = (0,   220, 80)    # head of the snake
SNAKE_BODY = (0,   180, 60)    # body of the snake
HUD_BG = (15,  15,  15)    # HUD bar background

# Food colours per weight value
FOOD_COLORS = {
    1: (255, 80,  80),   # red  — worth 1 point
    2: (255, 200, 0),    # gold — worth 2 points
    3: (80,  160, 255),  # blue — worth 3 points
}

# Level settings 
# Each entry: (foods_to_advance, base_move_delay_ms)
# foods_to_advance = how many foods eaten to reach this level
LEVELS = [
    {"foods_needed": 0,  "delay": 180},   # level 1 — starting speed
    {"foods_needed": 4,  "delay": 140},   # level 2
    {"foods_needed": 8,  "delay": 110},   # level 3
    {"foods_needed": 12, "delay": 85},    # level 4
    {"foods_needed": 16, "delay": 65},    # level 5  (max speed)
]

# How long a food item stays on the grid before disappearing (ms)
FOOD_LIFETIME_MS = 6000

# Maximum number of food items on the grid at once
MAX_FOOD = 3

# Directions (column delta, row delta)
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)