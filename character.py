import pygame
import math
import constants


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, mob_animations, char_type, boss, size, animation_cooldown = 250):
        super().__init__()
        self.char_type = char_type #which character it is in the list of characters
        self.boss = boss #if the character is a boss or not
        self.score = 0 #used in the items class
        self.flip = False
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0 #controls which frame of animation to show, starts at 0
        self.action = 0 #0: idle, 1: run 
        self.update_time = pygame.time.get_ticks() #how much time has passed since last updated frame, tells to move to next frame
        self.animation_cooldown = animation_cooldown #cooldown for animation (animation speed)
        self.running = False #if the character is running
        
        #variables for the image of the character (the image file, its rectangle, the coordinates of it)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * constants.SCALE * size, constants.TILE_SIZE * constants.SCALE * size)
        self.rect.center = (x, y)

    #movement
    def move(self, dx, dy, obstacle_tiles, exit_tile = None, can_enter_final_quest = False):
        screen_scroll = [0, 0] #this screen_scroll variable is only used within this move method
        level_complete = False #used later for the portal tile to trigger next scene
        self.running = False #starts with assumption that player is idle, not running
        
        if dx != 0 or dy != 0: #when dx or dy is anything but zero, means character is running and not idle
            self.running = True #sets running to true 
        if dx < 0: #flip character when moving left
            self.flip = True
        if dx > 0: #unflip character when moving right
            self.flip = False
        
        #control diagonal speed (ensures it is not faster)
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)

        
        self.rect.x += dx
        #check for collision with map in x direction
        for obstacle in obstacle_tiles:
            #check for collision
            if obstacle[1].colliderect(self.rect):
                #check which side the collision is from
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right

        self.rect.y += dy
        #check for collision with map in y direction
        for obstacle in obstacle_tiles:
            #check for collision
            if obstacle[1].colliderect(self.rect):
                #check which side the collision is from
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                if dy < 0:
                    self.rect.top = obstacle[1].bottom

        if self.char_type == 0:
            if can_enter_final_quest and exit_tile[1].colliderect(self.rect):
                level_complete = True
            
            #move camera left and right
            if self.rect.right > (constants.SCREEN_WIDTH - constants.SCROLL_THRESH):
                screen_scroll[0] = (constants.SCREEN_WIDTH - constants.SCROLL_THRESH) - self.rect.right
                self.rect.right = constants.SCREEN_WIDTH - constants.SCROLL_THRESH
            if self.rect.left < constants.SCROLL_THRESH:
                screen_scroll[0] = constants.SCROLL_THRESH - self.rect.left
                self.rect.left = constants.SCROLL_THRESH

            #move camera up and down
            if self.rect.bottom > (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH):
                screen_scroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH) - self.rect.bottom
                self.rect.bottom = constants.SCREEN_HEIGHT - constants.SCROLL_THRESH
            if self.rect.top < constants.SCROLL_THRESH: 
                screen_scroll[1] = constants.SCROLL_THRESH - self.rect.top
                self.rect.top = constants.SCROLL_THRESH

        return screen_scroll,level_complete

    def ai(self,screen_scroll): #used for npcs to not move with the screen
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

    def update(self):

        #determine action: 0=idle, 1 =run
        #checks if character is running to set the action
        #if running and a run animation exists, switch action to run (1)
        #otherwise, set action to idle (0)
        if self.running and len(self.animation_list[1]) > 0:
            self.update_action(1)
        else:
            self.update_action(0)

        #storing the animation speed locally in the method for readability
        animation_cooldown = self.animation_cooldown

        #make sure there's at least one frame in the current animation
        #gets the animation list for the current action (idle or run)
        current_anim = self.animation_list[self.action]
        if len(current_anim) == 0:
            return  #skip update if no frames (shouldn't happen, but safe guard)

        #update image - sets sprite image to current animation frame
        self.image = current_anim[self.frame_index]

        #update animation frame timing
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        #loop animation, advances to next frame and resets timer 
        if self.frame_index >= len(current_anim):
            self.frame_index = 0

    
    def update_action(self, new_action):
        
        #check if new action is different to the previous one
        if new_action != self.action:
            self.action = new_action #updates current action state
            self.frame_index = 0 #update the animation settings
            self.update_time = pygame.time.get_ticks() #reset the animation timer

    def draw(self, screen):
        #flip character according to direction of movement .flip(object, x, y) 
        flipped_image = pygame.transform.flip(self.image, self.flip, False) 
        #draw the character on the screen
        screen.blit(flipped_image, (self.rect.x, self.rect.y - constants.SCALE * constants.OFFSET))
     



