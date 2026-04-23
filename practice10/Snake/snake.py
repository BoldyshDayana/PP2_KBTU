# Snake entity: stores body as a list of (col, row) grid cells,
# handles movement, growth, and self/wall collision detection.

import pygame
from settings import (
    GRID_COLS, GRID_ROWS, CELL_SIZE, HUD_HEIGHT,
    SNAKE_HEAD, SNAKE_BODY, RIGHT,
)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        """Place the snake in the centre of the grid, moving right, length 3."""
        mid_col = GRID_COLS // 2
        mid_row = GRID_ROWS // 2
        # Body: head first, then tail cells to the left
        self.body      = [(mid_col, mid_row), (mid_col - 1, mid_row), (mid_col - 2, mid_row)]
        self.direction = RIGHT      # current movement direction (col_delta, row_delta)
        self._next_dir = RIGHT      # buffered direction (set by input, applied on tick)
        self._grow     = False      # if True, don't remove tail on next move (snake grows)

    # Input
    def set_direction(self, new_dir):
        """
        Buffer a direction change.
        Ignores attempts to reverse directly into the snake's own neck.
        """
        head = self.body[0]
        neck = self.body[1]
        # Calculate what the head position would be in the new direction
        candidate = (head[0] + new_dir[0], head[1] + new_dir[1])
        if candidate != neck:   # only allow if not moving into own neck
            self._next_dir = new_dir

    # Game logic
    def move(self):
        """
        Advance the snake one cell in the current direction.
        Called once per game tick (not every frame).
        Returns the new head position as (col, row).
        """
        self.direction = self._next_dir
        head_col, head_row = self.body[0]
        dc, dr = self.direction
        new_head = (head_col + dc, head_row + dr)

        self.body.insert(0, new_head) # prepend new head

        if self._grow:
            self._grow = False  # keep tail — snake is longer now
        else:
            self.body.pop() # remove tail — constant length move

        return new_head

    def grow(self):
        """Schedule the snake to grow by one cell on the next move."""
        self._grow = True

    def head(self):
        """Return the current head position (col, row)."""
        return self.body[0]

    def occupies(self, col, row):
        """Return True if any part of the snake is at (col, row)."""
        return (col, row) in self.body

    def hit_self(self):
        """Return True if the head overlaps any body segment (self-collision)."""
        return self.body[0] in self.body[1:]

    # Drawing
    def draw(self, surface, grid):
        """Draw each body segment; the head is a brighter shade."""
        for i, (col, row) in enumerate(self.body):
            rect  = grid.cell_rect(col, row)
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            # Shrink by 2px on each side for a visual gap between cells
            inner = rect.inflate(-4, -4)
            pygame.draw.rect(surface, color, inner, border_radius=4)