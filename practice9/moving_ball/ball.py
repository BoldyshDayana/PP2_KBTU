import pygame

class Ball:
    def __init__(self, x, y, radius, color, screen_width, screen_height):
        # Initialize ball properties: position, size, color, and screen boundaries
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.step = 20  # Movement step size (not used in move method directly)
        
    def move(self, dx, dy):
        # Move ball by (dx, dy) only if it stays within screen boundaries
        new_x = self.x + dx
        new_y = self.y + dy

        if (self.radius <= new_x <= self.screen_width - self.radius and
            self.radius <= new_y <= self.screen_height - self.radius):
            self.x = new_x
            self.y = new_y
        
    def draw(self, screen):
        # Draw the ball on the given pygame screen surface
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)