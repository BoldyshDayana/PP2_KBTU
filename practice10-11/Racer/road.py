# scrolling road with lane marker dashes
 
import pygame
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, ROAD_LEFT, ROAD_RIGHT,
                      ROAD_WIDTH, GREY, GREEN, WHITE)
 
 
class Road:
    def __init__(self):
        self.stripe_width = 6
        self.stripe_height = 40
        self.stripe_gap = 30   # vertical gap between stripes
        self.speed = 5   # pixels per frame
 
        # x positions of the two divider columns
        self.cols = [
            ROAD_LEFT + ROAD_WIDTH // 3,
            ROAD_LEFT + 2 * ROAD_WIDTH // 3,
        ]
 
        # Build initial list of stripe [x, y] positions
        self.stripes = []
        for col_x in self.cols:
            y = 0
            while y < SCREEN_HEIGHT:
                self.stripes.append([col_x, y])
                y += self.stripe_height + self.stripe_gap
 
    def update(self):
        """Move all stripes downward; wrap back to the top when off-screen."""
        for stripe in self.stripes:
            stripe[1] += self.speed
            if stripe[1] > SCREEN_HEIGHT:
                stripe[1] -= (self.stripe_height + self.stripe_gap) * len(self.stripes) // 2
 
    def draw(self, surface):
        # Grey road
        pygame.draw.rect(surface, GREY, (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
        # Green grass on both sides
        pygame.draw.rect(surface, GREEN, (0, 0, ROAD_LEFT, SCREEN_HEIGHT))
        pygame.draw.rect(surface, GREEN, (ROAD_RIGHT, 0, SCREEN_WIDTH - ROAD_RIGHT, SCREEN_HEIGHT))
        # White dashed lane markers
        for stripe in self.stripes:
            pygame.draw.rect(surface, WHITE,
                             (stripe[0] - self.stripe_width // 2, stripe[1],
                              self.stripe_width, self.stripe_height))
 