# config.py — All shared constants for the Snake TSIS4 project.
#
# Import from here in every other module so magic numbers live in one place.

# ── Window & grid ─────────────────────────────────────────────────────────────
CELL        = 24          # pixel size of one grid cell
COLS        = 25          # grid columns  (playable area, inside the border wall)
ROWS        = 25          # grid rows
HUD_H       = 48          # pixels for the top HUD bar
SCREEN_W    = CELL * COLS
SCREEN_H    = CELL * ROWS + HUD_H
FPS         = 60          # pygame frame-rate cap

# ── Directions (col-delta, row-delta) ─────────────────────────────────────────
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

# ── Palette ───────────────────────────────────────────────────────────────────
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
GREY        = (160, 160, 160)
DARK_GREY   = ( 55,  55,  55)
LIGHT_GREY  = (220, 220, 220)
BG          = ( 12,  16,  30)   # menu background
DARK_GREEN  = ( 18, 110,  18)   # grid background
GRID_LINE   = ( 28, 130,  28)   # faint grid lines
WALL_COL    = ( 55,  55,  55)   # border wall
HUD_BG      = (  8,  10,  20)   # HUD bar background

SNAKE_HEAD_DEFAULT = (  0, 220,  80)
SNAKE_BODY_DEFAULT = (  0, 170,  55)

# Food colours
FOOD_COLORS = {
    1: (255,  80,  80),   # red    — weight 1
    2: (255, 200,   0),   # gold   — weight 2
    3: ( 80, 160, 255),   # blue   — weight 3
}
POISON_COLOR  = (120,   0,  20)   # dark red  — poison food
FOOD_LIFETIME = 6000              # ms before a food item vanishes

# Power-up colours & durations
PU_COLORS = {
    "speed":  (255, 165,   0),   # orange
    "slow":   ( 80, 200, 200),   # cyan
    "shield": ( 80,  80, 255),   # blue
}
PU_DURATION    = 5000   # ms that the effect lasts after collection
PU_FIELD_LIFE  = 8000   # ms before an uncollected power-up vanishes

# Obstacle block colour
OB_COLOR    = ( 90,  60,  20)   # brown
OB_START_LV = 3                  # obstacles first appear at this level

# Level progression
FOODS_PER_LEVEL = 5   # foods eaten to advance one level

# ── Database connection ────────────────────────────────────────────────────────
# Edit these to match your local PostgreSQL setup.
DB_CONFIG = {
    "host":     "localhost",
    "port":     2407,
    "dbname":   "snake_db",
    "user":     "postgres",
    "password": "dayana2407D+",
}

# SQL to create tables if they don't exist
DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""