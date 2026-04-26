# the player-controlled car
 
import pygame
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, ROAD_LEFT, ROAD_RIGHT,
                      BLUE, WHITE, BLACK)
 
 
class PlayerCar:
    WIDTH = 40
    HEIGHT = 70
    SPEED = 5   # horizontal movement speed in pixels per frame
 
    def __init__(self):
        # Start in the centre of the road
        self.x = SCREEN_WIDTH // 2 - self.WIDTH // 2
        self.y = SCREEN_HEIGHT - self.HEIGHT - 20
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
 
    def update(self, keys):
        """Move left/right based on held arrow keys"""
        if keys[pygame.K_LEFT]:
            self.x -= self.SPEED
        if keys[pygame.K_RIGHT]:
            self.x += self.SPEED
 
        # Clamp so the car cannot leave the road
        self.x = max(ROAD_LEFT + 2, self.x)
        self.x = min(ROAD_RIGHT - self.WIDTH - 2, self.x)
        self.rect.x = self.x
 
    def draw(self, surface):
        """Draw a simple blocky car shape."""
        pygame.draw.rect(surface, BLUE, self.rect)
        # Windshield
        pygame.draw.rect(surface, WHITE,
                         (self.x + 5, self.y + 10, self.WIDTH - 10, 15))
        # Left wheel
        pygame.draw.rect(surface, BLACK, (self.x - 5, self.y + 10, 8, 20))
        # Right wheel
        pygame.draw.rect(surface, BLACK, (self.x + self.WIDTH - 3, self.y + 10, 8, 20))