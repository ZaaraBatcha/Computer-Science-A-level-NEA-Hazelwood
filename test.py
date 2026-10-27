import pygame


class Button():
    def draw(self, surface):
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                action = True
        
        surface.blit(self.image, self.rect)
        # missing return statement! returns None by default