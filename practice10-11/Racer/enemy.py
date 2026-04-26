# enemy (obstacle) cars that scroll down the road
 
import pygame
import random
from settings import SCREEN_HEIGHT, ROAD_LEFT, ROAD_RIGHT, RED, WHITE, BLACK
 
 
class EnemyCar:
    WIDTH = 40
    HEIGHT = 70
 
    def __init__(self, speed):
        # Spawn at a random x position within the road
        self.x = random.randint(ROAD_LEFT + 5, ROAD_RIGHT - self.WIDTH - 5)
        self.y = -self.HEIGHT   # start just above the screen
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        # Random colour for variety
        self.color = random.choice([RED, (255, 140, 0), (160, 32, 240)])
 
    def update(self):
        """Move the enemy car downward each frame."""
        self.y += self.speed
        self.rect.y = self.y
 
    def is_off_screen(self):
        """Return True when the car has scrolled past the bottom of the screen."""
        return self.y > SCREEN_HEIGHT
 
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Windshield at the bottom (car is coming toward us)
        pygame.draw.rect(surface, WHITE,
                         (self.x + 5, self.y + self.HEIGHT - 25, self.WIDTH - 10, 15))
        # Wheels
        pygame.draw.rect(surface, BLACK, (self.x - 5, self.y + 10, 8, 20))
        pygame.draw.rect(surface, BLACK, (self.x + self.WIDTH - 3, self.y + 10, 8, 20))
 