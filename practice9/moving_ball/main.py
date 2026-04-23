import pygame
from ball import Ball

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
LILAC = (200, 162, 200)
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")
clock = pygame.time.Clock()

# Create ball at the center of the screen
ball = Ball(WIDTH // 2, HEIGHT // 2, 25, LILAC, WIDTH, HEIGHT)

running = True
while running:
    screen.fill(WHITE)  # Clear screen with white background

    # Handle user input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Move ball with arrow keys (20 pixels per press)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                ball.move(0, -ball.step)
            if event.key == pygame.K_DOWN:
                ball.move(0, ball.step)
            if event.key == pygame.K_LEFT:
                ball.move(-ball.step, 0)
            if event.key == pygame.K_RIGHT:
                ball.move(ball.step, 0)
        
    ball.draw(screen)  # Draw ball at its current position

    pygame.display.flip()  # Update the display
    clock.tick(FPS)  # Maintain 60 FPS

pygame.quit()