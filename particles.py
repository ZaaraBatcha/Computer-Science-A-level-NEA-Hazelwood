import pygame
import random
import math
import constants

class AmbientParticle:
    def __init__(self):
        self.reset()  #ensure all particles are random
        self.visible_alpha = 0  #start invisible

    def reset(self):
        #spawn particle at random screen location with random properties
        self.x = random.randint(0, constants.SCREEN_WIDTH)  #random x position
        self.y = random.randint(0, constants.SCREEN_HEIGHT)  #random y position
        self.radius = random.randint(2, 6)  #random size
        self.speed = random.uniform(0.2, 0.5)  #random speed
        self.alpha = random.randint(80, 160)  #random initial transparency
        self.fade_dir = random.choice([-1, 1])  #random fade direction (dim or brighten)
        self.color = (255, 230, 180)  #warm glow colour (for fireflies)
        #self.color = (180, 220, 255)  #moonlight
        #self.color = (200, 255, 200)  #lighter colour

    def update(self):
        #move particles upwards slowly and control its speed of moving
        self.y -= self.speed  #drift/float upwards
        self.alpha += self.fade_dir * 1  #change brightness by 1 per frame

        #fading in and out 
        if self.alpha <= 60 or self.alpha >= 180:
            self.fade_dir *= -1 #reverse fading direction when reaching limits

        #reset particle when it goes off the screen
        if self.y < -10:
            self.reset()
            self.y = constants.SCREEN_HEIGHT + 10 #respawn just below the screen for smooth transition

    def draw(self, screen):
        #draw the particle as a circle with its current alpha transparency
        #SCRALPHA allows transparency
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        #visible_alpha is used to control the overall visibility of the particles 
        #self.alpha and visible_alpha combined because we want the particles to fade in and out individually but 
        #also be able to fade in and out as a group 
        draw_alpha = int(self.alpha * (self.visible_alpha / 255))
        
        #drawing the circle with parameters (color, alpha, position, radius)
        pygame.draw.circle(surface, (*self.color, draw_alpha), (self.radius, self.radius), self.radius)
        screen.blit(surface, (self.x, self.y))