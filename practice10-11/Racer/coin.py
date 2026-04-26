# collectible coins that appear randomly on the road

import pygame
import random
from settings import SCREEN_HEIGHT, ROAD_LEFT, ROAD_RIGHT, YELLOW, DARK_YELLOW


class Coin:

    RADIUS = 12

    def __init__(self, speed):
        # Spawn at a random x position within the road
        self.x = random.randint(ROAD_LEFT + self.RADIUS + 5,
                                ROAD_RIGHT - self.RADIUS - 5)
        self.y = -self.RADIUS   # start above the screen
        self.speed = speed
        # Square bounding box used for collision detection
        self.rect = pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS,
                                self.RADIUS * 2, self.RADIUS * 2)

    def update(self):
        """Scroll the coin downward each frame."""
        self.y += self.speed
        self.rect.y = self.y - self.RADIUS

    def is_off_screen(self):
        """Return True when the coin has scrolled past the bottom of the screen."""
        return self.y - self.RADIUS > SCREEN_HEIGHT

    def draw(self, surface):
        # Outer gold circle
        pygame.draw.circle(surface, YELLOW, (self.x, int(self.y)), self.RADIUS)
        # Inner darker circle for a coin look
        pygame.draw.circle(surface, DARK_YELLOW, (self.x, int(self.y)), self.RADIUS - 4)