# Grid helper: converts between grid (col, row) and pixel coordinates,
# draws the background, grid lines, and border walls.

import pygame
from settings import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, HUD_HEIGHT,
    DARK_GREEN, GRID_LINE, WALL_COLOR,
)


class Grid:
    def __init__(self):
        # Pre-compute the pixel rectangle for every grid cell for fast lookup
        self._rects = {}
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                self._rects[(col, row)] = pygame.Rect(
                    col * CELL_SIZE,
                    row * CELL_SIZE + HUD_HEIGHT,
                    CELL_SIZE,
                    CELL_SIZE,
                )

   
    # Coordinate helpers
    def cell_rect(self, col, row):
        """Return the pixel Rect for grid cell (col, row)."""
        return self._rects[(col, row)]

    def is_wall(self, col, row):
        """Return True if the cell is a border wall (outer ring)."""
        return col == 0 or row == 0 or col == GRID_COLS - 1 or row == GRID_ROWS - 1

    def is_inside(self, col, row):
        """Return True if the cell is inside the walls (playable area)."""
        return 0 < col < GRID_COLS - 1 and 0 < row < GRID_ROWS - 1

    def inner_cells(self):
        """Yield all (col, row) positions that are inside the walls."""
        for col in range(1, GRID_COLS - 1):
            for row in range(1, GRID_ROWS - 1):
                yield (col, row)


    # Drawing
    def draw(self, surface):
        """Draw the background, faint grid lines, and solid border walls."""
        # Fill playable area with dark green
        surface.fill(DARK_GREEN, (0, HUD_HEIGHT, GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE))

        # Faint grid lines (every cell boundary)
        for col in range(GRID_COLS):
            x = col * CELL_SIZE
            pygame.draw.line(surface, GRID_LINE, (x, HUD_HEIGHT), (x, surface.get_height()))
        for row in range(GRID_ROWS):
            y = row * CELL_SIZE + HUD_HEIGHT
            pygame.draw.line(surface, GRID_LINE, (0, y), (surface.get_width(), y))

        # Draw wall cells as solid dark rectangles
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                if self.is_wall(col, row):
                    pygame.draw.rect(surface, WALL_COLOR, self._rects[(col, row)])