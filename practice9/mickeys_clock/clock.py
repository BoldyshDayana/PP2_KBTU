import pygame

#rotates around the center

def rotate_center(image, angle, center):
    rotated_image = pygame.transform.rotate(image, angle) #Pygame's built-in function to rotate an image
    new_rect = rotated_image.get_rect(center=image.get_rect(center=center).center)
    return rotated_image, new_rect  

"""image.get_rect(center=center).center-gets the center coordinates of the original image
rotated_image.get_rect(center=...)-creates a rectangle for the rotated image, but sets its center to the same point as the original"""