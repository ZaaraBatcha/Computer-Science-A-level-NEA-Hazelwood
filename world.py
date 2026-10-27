import pygame
import constants
from character import Character
from items import Item


class World():
    def __init__(self):
        self.map_tiles = []
        self.obstacle_tiles = []
        self.elder = None
        self.blacksmith = None
        self.player = None
        self.farmer = None
        self.lumberjack = None
        self.innkeeper = None
        self.cloaked = None
        self.exit_tile = None
        self.final_quest = False

        self.item_list = []

    def process_data(self, data, tile_list,item_images, mob_animations):
        self.level_length = len(data)
        for y, row in enumerate(data):
            for x, tile in enumerate(row):

                image_x = x * 48
                image_y = y * 48

                #character spawnpoints
                if tile == 140:
                    self.elder = Character(image_x, image_y, mob_animations, 2, False, 1) 
                    image = tile_list[0]
                elif tile == 141:
                    self.blacksmith = Character(image_x, image_y, mob_animations, 1, False, 1)
                    image = tile_list[0]
                elif tile == 145:
                    self.player = Character(image_x, image_y, mob_animations, 0, False, 1)
                    image = tile_list[143]
                elif tile == 147:
                    self.farmer = Character(image_x, image_y, mob_animations, 3, False, 1)
                    image = tile_list[0]
                elif tile == 148:
                    self.lumberjack = Character(image_x, image_y, mob_animations, 6, False, 1)
                    image = tile_list[0]
                elif tile == 149:
                    self.innkeeper = Character(image_x, image_y, mob_animations, 5, False, 1)
                    image = tile_list[0]
                    
                #item spawnpoints
                elif tile == 150:
                    wood = Item(image_x, image_y, 0, [item_images[0]])
                    self.item_list.append(wood)
                    image = tile_list[0]
                elif tile == 146:
                    chicken = Item(image_x, image_y, 2, [item_images[2]])
                    self.item_list.append(chicken)
                    image = tile_list[0]
                elif tile == 151:
                    lantern = Item(image_x, image_y, 3, [item_images[3]])
                    self.item_list.append(lantern)
                    image = tile_list[0]
                elif tile == 152:
                    lantern = Item(image_x, image_y, 1, [item_images[1]])
                    self.item_list.append(lantern)
                    image = tile_list[0]
                elif tile == 153:
                    self.cloaked = Character(image_x, image_y, mob_animations, 4, False, 1)
                    image = tile_list[0]

                elif tile >= 0 and tile < len(tile_list):
                    image = tile_list[tile]
                else:
                    continue  # skip invalid tiles

                image_rect = image.get_rect()
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]

                if tile not in (0, 1, 2, 43, 142, 143, 144,145,150,146,151,152,140,148,149,141,147,153,108,155):
                    self.obstacle_tiles.append(tile_data)

                #triggers final quest
                if tile == 155:
                    self.exit_tile = tile_data #stores [image, rect, x, y]

                self.map_tiles.append(tile_data)

    def update(self,screen_scroll):
         for tile in self.map_tiles:
             tile[2] += screen_scroll[0]
             tile[3] += screen_scroll[1]
             tile[1].center = (tile[2],tile[3])

    def draw(self,surface):
        for tile in self.map_tiles:
            surface.blit(tile[0],tile[1])