import pygame
 

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def draw(self, surface):
        action = False
        
        #get mouse position
        pos = pygame.mouse.get_pos()
        
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos): #collidepoint is to check if the mouse position collides with button
            if pygame.mouse.get_pressed()[0]: #0 is left mouse button
                action = True
            
        surface.blit(self.image, self.rect)            
        
        return action
    
    
    
# class Button():
#     def __init__(self, x, y, image):
#         self.image = image
#         self.rect = self.image.get_rect(topleft=(x, y))

#     def draw(self, surface):
#         surface.blit(self.image, self.rect)