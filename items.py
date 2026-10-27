import pygame
from pygame import mixer
import os
import sys

pygame.init()
mixer.init()

def resource_path(relative_path):
    """Get the correct path to assets, works for PyInstaller exe and dev"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#pick-up sfx
pick_up_sfx = pygame.mixer.Sound(resource_path("assets/audio/pick_up_crop.mp3"))
pick_up_sfx.set_volume(10)


class Item(pygame.sprite.Sprite):
  def __init__(self, x, y, item_type, animation_list):
    pygame.sprite.Sprite.__init__(self)
    self.item_type = item_type
    self.animation_list = animation_list
    self.frame_index = 0
    self.update_time = pygame.time.get_ticks()
    self.image = self.animation_list[self.frame_index]
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)

  def update(self, screen_scroll, player,player_info):
    #reposition based on screen scroll
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    #check to see if item has been collected by the player
    if self.rect.colliderect(player.rect):
      #coin collected
      if self.item_type == 0: #metal
          player_info[0] += 1
          pick_up_sfx.play()
          self.kill()
      elif self.item_type == 1: #wood
          player_info[1] += 1
          pick_up_sfx.play()
          self.kill()
      elif self.item_type == 2: #chicken
          player_info[2] += 1
          pick_up_sfx.play()
          self.kill()
      elif self.item_type == 3: #lantern
          player_info[3] += 1
          pick_up_sfx.play()
          self.kill()

  def draw(self, surface):
    surface.blit(self.image, self.rect)