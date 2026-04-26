# Food management: spawns randomly weighted food items that
# disappear after a timer expires. Food never spawns on a wall
# or on the snake's body.

import pygame
import random
from settings import (
    CELL_SIZE, HUD_HEIGHT, FOOD_COLORS, FOOD_LIFETIME_MS, MAX_FOOD,
    WHITE, BLACK,
)


class FoodItem:
    """
    A single food item sitting at one grid cell.
    Attributes:
        col, row  — grid position
        weight    — point value (1, 2, or 3); determines colour
        spawn_ms  — pygame.time.get_ticks() value when this food was created
    """

    def __init__(self, col, row, weight):
        self.col      = col
        self.row      = row
        self.weight   = weight                       # point value
        self.color    = FOOD_COLORS[weight]
        self.spawn_ms = pygame.time.get_ticks()      # record birth time

    def is_expired(self):
        """Return True if this food has been on the grid longer than FOOD_LIFETIME_MS."""
        return pygame.time.get_ticks() - self.spawn_ms >= FOOD_LIFETIME_MS

    def time_left_fraction(self):
        """Return a 0.0–1.0 fraction of lifetime remaining (1.0 = just spawned)."""
        elapsed = pygame.time.get_ticks() - self.spawn_ms
        return max(0.0, 1.0 - elapsed / FOOD_LIFETIME_MS)

    def draw(self, surface, grid):
        """Draw the food as a coloured circle with a shrinking timer ring."""
        rect = grid.cell_rect(self.col, self.row)
        cx = rect.centerx
        cy = rect.centery
        radius = CELL_SIZE // 2 - 3

        # Main food circle
        pygame.draw.circle(surface, self.color, (cx, cy), radius)

        # Weight label (1 / 2 / 3) in the centre
        font = pygame.font.SysFont("Arial", 12, bold=True)
        txt  = font.render(str(self.weight), True, WHITE)
        surface.blit(txt, txt.get_rect(center=(cx, cy)))

        # Countdown arc — shrinks as the food ages
        frac = self.time_left_fraction()
        if frac < 1.0:
            # Draw a white arc that spans frac * 360 degrees
            import math
            end_angle = math.radians(90 - frac * 360)   # start from top, go clockwise
            arc_rect  = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
            pygame.draw.arc(surface, WHITE, arc_rect,
                            end_angle, math.radians(90), 2)


class FoodManager:
    """
    Manages a collection of FoodItems on the grid.

    Responsibilities:
      - Keeping up to MAX_FOOD items alive
      - Spawning new items at random free cells with random weights
      - Removing expired items
      - Detecting whether the snake head is on a food item
    """

    def __init__(self):
        self.items = []   # list of active FoodItem objects

    def reset(self):
        """Clear all food (called on game reset)."""
        self.items = []

    def update(self, grid, snake):
        """
        Remove expired food and spawn new items until MAX_FOOD is reached.
        grid  — Grid instance (used to find free cells)
        snake — Snake instance (food must not spawn on snake body)
        """
        # Remove any food that has timed out
        self.items = [f for f in self.items if not f.is_expired()]

        # Spawn new food if below the maximum count
        while len(self.items) < MAX_FOOD:
            food = self._spawn(grid, snake)
            if food is None:
                break   # no free cells available (very full grid)
            self.items.append(food)

    def _spawn(self, grid, snake):
        """
        Choose a random free inner cell and return a new FoodItem there.
        Returns None if no free cell is found after many attempts.
        """
        # Build list of free cells (not a wall, not occupied by the snake,
        # not already occupied by existing food)
        occupied_by_food = {(f.col, f.row) for f in self.items}
        free_cells = [
            (col, row)
            for col, row in grid.inner_cells()
            if not snake.occupies(col, row) and (col, row) not in occupied_by_food
        ]

        if not free_cells:
            return None

        col, row = random.choice(free_cells)

        # Weighted random: weight 1 is most common, 3 is rarest
        weight = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        return FoodItem(col, row, weight)

    def eat_at(self, col, row):
        """
        Check if there is food at (col, row).
        If so, remove it and return its weight; otherwise return 0.
        """
        for item in self.items:
            if item.col == col and item.row == row:
                self.items.remove(item)
                return item.weight
        return 0

    def draw(self, surface, grid):
        """Draw all active food items."""
        for item in self.items:
            item.draw(surface, grid)