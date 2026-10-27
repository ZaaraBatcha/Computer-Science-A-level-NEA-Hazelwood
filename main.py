import pygame
from pygame import mixer #mixer used for music and sounds
import constants
from button import Button
from character import Character
from world import World
from items import Item
from particles import AmbientParticle
import os
import sys
import datetime
import csv
from PIL import Image
import math
import random

mixer.init()
pygame.init()

def resource_path(relative_path):
    """Get the correct path to assets, works for PyInstaller exe and dev"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#pygame window size
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)) 
#caption of pygame window
pygame.display.set_caption("Hazelwood") 

#create clock for maintaining frame rate
clock = pygame.time.Clock()

#define game variables
level = 1
start_game = False
pause_game = False
settings_open = False
guide_open = False
start_intro = False

#final quest flags
in_final_quest = False
world_paused = False
final_npc = None
dialogue_index = 0
can_enter_final_quest = False
ember_quest = False
end_of_game = False
ending_credits = False
credits_started = False

#zen mode flags
zen_mode = False
zen_intro = False
zen_timer_started = False
zen_timer_start = 0
zen_player_positioned = False
zen_music_started = False


#quest panel
current_quest_text = "Head to the elder waiting at the end of the bridge."
quest_panel_width = 450
quest_panel_height = 140
dialogue_open = False
show_quest_panel = True

#volume control
current_volume = 0.6  #default volume when game starts, changes when slider dragged
VOLUME_MIN = 0.0  #minimum volume
VOLUME_MAX = 1.0  #maximum volume
VOLUME_STEP = 0.1  #how much volume increases by when dragged

#time day cycle
TIME_DAY = 0  #day starts at 0, changes to 1, 2, 3 as time progresses
TIME_SUNSET = 1
TIME_NIGHT = 2
TIME_DAWN = 3
time_of_day = TIME_DAY
time_change_timer = None  #timer to track when to change time of day
TIME_CHANGE_DELAY = 60000  #how long per phase (60 seconds)

#overlay fade control
current_overlay = [0, 0, 0, 0]   
target_overlay = [0, 0, 0, 0]
OVERLAY_FADE_SPEED = 0.5  #how fast the overlay fades (higher is faster)


#player internal monologue
monologue_text = ""                               #text to display
monologue_alpha = 0                               #transparency (0-180)
monologue_active = False                          #whether monologue is playing
monologue_timer = 0                               #timestamp when monologue started
MONOLOGUE_DURATION = 5000                         #how long text stays visible (ms)
MONOLOGUE_FADE_SPEED = 1200                       #fade in/out speed (ms)
last_time_of_day = TIME_DAY                       #tracks previous time of day
IDLE_MONOLOGUE_COOLDOWN = random.randint(12000, 20000)  #wait time between idle monologues (ms)
last_idle_monologue = 0                           #timestamp of last idle monologue
idle_monologue_triggered = False                  #unused flag

#rain sound effects
rain_playing = False
rain_start_time = 0
next_rain_time = pygame.time.get_ticks() + random.randint(1 * 60000, 2 * 60000)  #1-2 minutes
RAIN_DURATION_MIN = 30000  #30 seconds
RAIN_DURATION_MAX = 90000  #90 seconds


#story intro 
show_story_intro = False
story_scroll = 0
story_text_reveal = 0           #how many characters have appeared
story_last_update = 0           #timestamp for typewriter timing
STORY_TYPE_SPEED = 20           #milliseconds per character
story_manual_speed = 10         #speed for arrow keys

#flash for camera
flash_alpha = 0
flash_active = False
FLASH_MAX_ALPHA = 120   #intensity of flash (lower = softer)
FLASH_FADE_SPEED = 6000  # how fast it fades out

#gallery for screenshots
gallery_open = False        #whether gallery is displayed
gallery_images = []         #list of loaded images (image, filename tuples)
gallery_index = 0           #current image index in gallery

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#define font 
font = pygame.font.Font(resource_path("assets/fonts/AtariClassic.ttf"), 20)
#font = pygame.font.Font("assets/fonts/DePixelHalbfett.ttf", 20) #20 is font size in pixels


 
#helper function to scale image (to cut down long lines of code)
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

#LOAD MUSIC AND SOUNDS ---------------------------------------------------

#load background music
pygame.mixer.music.load(resource_path("assets/audio/main_bg.mp3"))
pygame.mixer.music.set_volume(0.5) #sets volume as a percentage (0.3 is 30% of og file)
#-1 means music plays in a continuous loop, music starts at 0.0 s, 5000 means music fades in over 5000ms (5 seconds)
pygame.mixer.music.play(-1, 0.0, 1000)

#blacksmith sound
blacksmith_sfx = pygame.mixer.Sound(resource_path("assets/audio/blacksmith_sfx.mp3"))
blacksmith_sfx.set_volume(0.8)

#pick-up sfx
pick_up_sfx = pygame.mixer.Sound(resource_path("assets/audio/pick_up_crop.mp3"))
pick_up_sfx.set_volume(1)

#final quest background music
finalQuest_bg = pygame.mixer.Sound(resource_path("assets/audio/finalQuest_bg.mp3"))
finalQuest_bg.set_volume(1.2)

#ending background music
ending_bg = pygame.mixer.Sound(resource_path("assets/audio/ending_bg.mp3"))
ending_bg.set_volume(1.2)

#quest pop up sound
quest_sfx = pygame.mixer.Sound(resource_path("assets/audio/quest_pop.mp3"))
quest_sfx.set_volume(0.3)

#rain sfx sound
rain_sfx = pygame.mixer.Sound(resource_path("assets/audio/rain_sfx.mp3"))
rain_sfx.set_volume(0.3)

#camera sfx sound
camera_sfx = pygame.mixer.Sound(resource_path("assets/audio/camera_sfx.mp3"))
camera_sfx.set_volume(0.3)

#END OF LOAD MUSIC AND SOUNDS ----------------------------------------------------



#function to remove transparency from images
def trim_transparency(surface):
    #crops a surface to remove fully transparent borders
    rect = surface.get_bounding_rect()
    return surface.subsurface(rect).copy()

#load background main menu image
background_image = scale_img(pygame.image.load(resource_path("assets/images/main_menu_bg.png")).convert_alpha(), constants.BG_SCALE)

#load final quest background images
final_quest_bg = scale_img(pygame.image.load(resource_path("assets/images/questFinal/dungeons_bg.png")).convert_alpha(), constants.BG_SCALE)

#main menu logo
raw_logo_image = scale_img(pygame.image.load(resource_path("assets/images/logo.png")).convert_alpha(), constants.LOGO_SCALE)
trim_logo_img = trim_transparency(raw_logo_image)
logo_rect = trim_logo_img.get_rect()
logo_rect.centerx = constants.SCREEN_WIDTH // 2
logo_rect.top = 70  # adjust this to move it up/down

#main menu button images
raw_play_img = scale_img(pygame.image.load(resource_path("assets/images/buttons/button_play.png")).convert_alpha(), constants.BUTTON_SCALE)
trim_play_img = trim_transparency(raw_play_img)
play_rect = trim_play_img.get_rect()

raw_guide_img = scale_img(pygame.image.load(resource_path("assets/images/buttons/button_guide.png")).convert_alpha(), constants.BUTTON_SCALE)
trim_guide_img = trim_transparency(raw_guide_img)
guide_rect = trim_guide_img.get_rect()

raw_quit_img = scale_img(pygame.image.load(resource_path("assets/images/buttons/button_quit.png")).convert_alpha(), constants.BUTTON_SCALE)
trim_quit_img = trim_transparency(raw_quit_img)
quit_rect = trim_quit_img.get_rect()


quitty = scale_img(pygame.image.load(resource_path("assets/images/buttons/quit_buttom.png")).convert_alpha(), constants.BUTTON_SCALE)
#create main menu buttons

quit = Button(230, constants.SCREEN_HEIGHT // 2 + 70, quitty)


play_button = Button(230, constants.SCREEN_HEIGHT // 2 + 70, trim_play_img)
guide_button = Button(560, constants.SCREEN_HEIGHT // 2 + 70, trim_guide_img)
quit_button = Button(890, constants.SCREEN_HEIGHT // 2 + 70, trim_quit_img)


#load guide image (not button)
guide_menu = scale_img(pygame.image.load(resource_path("assets/images/guide_menu.png")).convert_alpha(), constants.GUIDE_MENU_SCALE)

#load thank you menu (zen menu)
zen_menu = scale_img(pygame.image.load(resource_path("assets/images/thank_you_menu.png")).convert_alpha(), constants.GUIDE_MENU_SCALE)


#PAUSE MENU
#load pause menu image
pause_menu_img = scale_img(pygame.image.load(resource_path("assets/images/pause_menu.png")).convert_alpha(), 1)

#loading settings button
raw_settings_btn = scale_img(pygame.image.load(resource_path("assets/images/buttons/settings_button.png")).convert_alpha(), 1)
trim_settings_btn = trim_transparency(raw_settings_btn) #trimming transparent parts of image
#creating the button using the Button class
settings_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 60, trim_settings_btn)

#loading resume/exit button
raw_resume_btn = scale_img(pygame.image.load(resource_path("assets/images/buttons/exit_pause_button.png")).convert_alpha(), 1)
trim_resume_btn = trim_transparency(raw_resume_btn)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 + 70, trim_resume_btn)


#SETTINGS MENU
#load settings menu image
settings_menu_img = scale_img(pygame.image.load(resource_path("assets/images/settings_menu.png")).convert_alpha(), 0.8)

#settings menu buttons
#guide menu button
raw_guide_btn = scale_img(pygame.image.load(resource_path("assets/images/buttons/guide_menu_button.png")).convert_alpha(), 0.8)
trim_guide_btn = trim_transparency(raw_guide_btn)  #removes transparency and white space from the image to trim just the button
#create the button using the Button class and relevant parameters 
settings_guide_button = Button(constants.SCREEN_WIDTH // 2 - 190, constants.SCREEN_HEIGHT // 2 - 20, trim_guide_btn)

#restart game button, return to main menu
raw_main_menu_btn = scale_img(pygame.image.load(resource_path("assets/images/buttons/restart_button.png")).convert_alpha(), 0.8)
trim_main_menu_btn = trim_transparency(raw_main_menu_btn)
settings_main_menu_button = Button(constants.SCREEN_WIDTH // 2 - 190, constants.SCREEN_HEIGHT // 2 + 80, trim_main_menu_btn)

#close settings button (x button)
raw_close_btn = scale_img(pygame.image.load(resource_path("assets/images/buttons/close_button.png")).convert_alpha(), 0.7)
trim_close_btn = trim_transparency(raw_close_btn)
settings_close_button = Button(constants.SCREEN_WIDTH // 2 + 185, constants.SCREEN_HEIGHT // 2 - 230, trim_close_btn)

#slider bar for volume control, drawn as a rectangle with a handle
volume_slider_x = constants.SCREEN_WIDTH // 2 - 100
volume_slider_y = constants.SCREEN_HEIGHT // 2 - 80
volume_slider_width = 200
volume_slider_height = 20


#load character images
mob_animations = [] #master list for all animation lists of the characters
mob_types = ["elf", "blacksmith", "elder", "farmer", "hooded", "innkeeper", "lumberjack", "monster"] #all folders for the characters

#load character frame images
#animations of character, idle and run 
animation_types = ["idle", "run"]

#loop through each mob type
for mob in mob_types:
    #create a temporary overall animation list
    animation_list = []
    #loop through each animation type (idle or run)
    for animation in animation_types:
        #create a temporary list for each animation type
        temp_list = []
        #retrieve file names in the folder
        folder_path = resource_path(f"assets/images/character/{mob}/{animation}")
        
        #check if folder exists (important for 'run' animations that might not exist i.e. for npcs)
        if os.path.exists(folder_path):
            frame_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
            for file_name in frame_files:
                img_path = os.path.join(folder_path, file_name)
                img = pygame.image.load(img_path).convert_alpha()
                img = scale_img(img, constants.NPC_SCALE)
                temp_list.append(img)
        else:
            #if the animation folder doesn't exist, use an empty list 
            temp_list = []
        
        #append the temporary animation list to the overall animation list
        animation_list.append(temp_list)
    #append the overall animation list to the mob animations master list
    mob_animations.append(animation_list)


#player = Character(100, 100, mob_animations, 0, False, 1, animation_cooldown=70)

#creating player
#player = Character(world.player_spawn[0], world.player_spawn[1], mob_animations, 0, False, 1)
# heart_empty = scale_img(pygame.image.load("assets/images//heart_empty.png").convert_alpha(), 3)
# heart_half = scale_img(pygame.image.load("assets/images/heart_half.png").convert_alpha(), 3)
# heart_full = scale_img(pygame.image.load("assets/images/heart_full.png").convert_alpha(), 3)

item_images = []
metal = scale_img(pygame.image.load(resource_path("assets/images/items/metal.png")).convert_alpha(), 0.1)
item_images.append(metal)
wood = scale_img(pygame.image.load(resource_path("assets/images/items/wood.png")).convert_alpha(), 0.1)
item_images.append(wood)
chicken = scale_img(pygame.image.load(resource_path("assets/images/items/chicken.png")).convert_alpha(), 0.1)
item_images.append(chicken)
lantern = scale_img(pygame.image.load(resource_path("assets/images/items/lantern.png")).convert_alpha(), 0.1)
item_images.append(lantern)
letter = scale_img(pygame.image.load(resource_path("assets/images/items/letter.png")).convert_alpha(), 1.35)
compass = scale_img(pygame.image.load(resource_path("assets/images/items/compass.png")).convert_alpha(), 2.1)

ambient_particles = [AmbientParticle() for _ in range(25)]


#END OF LOAD IMAGES -------------------------------------------------------------------------------------




#HELPER FUNCTIONS -------------------------------------------------------------------------------------

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))
player_info = [0,0,0,0]

    
#hud display
def draw_info(player_info):
    #drawing the bar
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50),5)
    draw_text("INV: " , font, constants.WHITE, constants.SCREEN_WIDTH -530, 15)
    
    #the x and y refers to the position of the first item image
    x = 130
    y = 80

    #displaying each item and its count
    index = 0
    for i in item_images: #looping through the list of item images
        screen.blit(i,(constants.SCREEN_WIDTH-x, 0)) #drawing them on the display
        draw_text(f"X{player_info[index]}", font, constants.WHITE, constants.SCREEN_WIDTH -y, 15)
        x += 100
        y += 100
        index += 1



#scaling the characters for the final quest
def scale_character(character, scale_factor):
    #scale all animation frames for a character and update its rect
    
    center = character.rect.center #getting the center of the rect of the character
    for anim_list in character.animation_list: #looping through the animation list of the character
        for i in range(len(anim_list)):
            w, h = anim_list[i].get_width(), anim_list[i].get_height() #getting the width and height of each frame
            #scaling the width and height by a certain scale factor passed in as a parameter
            anim_list[i] = pygame.transform.scale(anim_list[i], (int(w * scale_factor), int(h * scale_factor)))
    
    #updating the character's image and rect to match the new scale
    if character.animation_list[character.action]: #check if the current action for the character has frames
        character.image = character.animation_list[character.action][character.frame_index] #gets the image
        character.rect = character.image.get_rect() #updates the rect
        character.rect.center = center #re-centers the rect to the previous center position


#for including gifs
def load_gif_frames(gif_path, scale=2):
    gif = Image.open(gif_path)
    frames = []
    
    try:
        while True:
            frame = gif.convert("RGBA")
            frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
            
            if scale != 1:
                w, h = frame.get_width(), frame.get_height()
                frame = pygame.transform.scale(frame, (int(w * scale), int(h * scale)))
            
            frames.append(frame)
            gif.seek(gif.tell() + 1)

    except EOFError:
        pass

    return frames

#wrapping text function
def wrap_text(text, font, max_width):
    words = text.split(" ") #split the input text into individual words separated by spaces
    lines = [] #create an empty list to store completed lines of wrapped text
    current_line = "" #initialize a variable to build up current line word by word

    #loop through each word in the text
    for word in words:
        #create a test line to check if adding the word keeps the line within width
        test_line = current_line + word + " " #add the word to current line
        
        #use font.size() to get the width (in pixels) of the test line, then check if it fits
        #font.size() returns a tuple (width, height), so [0] gets just the width
        if font.size(test_line)[0] <= max_width:
            #if the test line fits within max_width, update current_line to include this word
            current_line = test_line
        else:
            #if the test line is too wide, the current line is complete, so append it to lines
            lines.append(current_line)
            #start a new line with the current word that didn't fit
            current_line = word + " "

    #after the loop ends, append the final line
    lines.append(current_line)
    
    return lines #return the list of wrapped lines

#drawing the quest panel function
def draw_quest_panel(screen, text):
    panel_width = 450
    panel_height = 140
    x = 20
    y = constants.SCREEN_HEIGHT - panel_height - 20

    #panel background
    pygame.draw.rect(screen, (209, 118, 33), (x, y, panel_width, panel_height), border_radius=10)
    pygame.draw.rect(screen, (107, 63, 44), (x, y, panel_width, panel_height), 6, border_radius=10)

    #title
    title_surface = font.render("Quest", True, (71, 44, 23))
    screen.blit(title_surface, (x + 15, y + 15))

    #wrapped text
    wrapped_lines = wrap_text(text, font, panel_width - 20)

    offset_y = 40
    for line in wrapped_lines:
        line_surf = font.render(line, True, (252, 211, 154))
        screen.blit(line_surf, (x + 15, y + offset_y))
        offset_y += 20

#setting the text for the quest panel
def set_quest(new_text):
    global current_quest_text
    if current_quest_text != new_text:
        current_quest_text = new_text
        # quest_sfx.play()


#function to draw volume slider and handle volume changes
def draw_volume_slider(screen):
    global current_volume
    
    #create a dark slider background, a rectangle with curved corners (border_radius = 5)
    pygame.draw.rect(screen, (80, 50, 40), (volume_slider_x, volume_slider_y, volume_slider_width, volume_slider_height), border_radius=5)
    
    #create a filled background for when slider is dragged
    #calculate how much of the slider should be filled based on current volume, as a percentage of the slider width
    filled_width = (current_volume / VOLUME_MAX) * volume_slider_width 
    pygame.draw.rect(screen, (209, 118, 33), (volume_slider_x, volume_slider_y, filled_width, volume_slider_height), border_radius=5)
    
    #border for the slider
    pygame.draw.rect(screen, (107, 63, 44), (volume_slider_x, volume_slider_y, volume_slider_width, volume_slider_height), 2, border_radius=5)
    
    #create a handle for the slider
    handle_x = volume_slider_x + filled_width - 8
    handle_y = volume_slider_y - 5
    pygame.draw.rect(screen, (200, 100, 50), (handle_x, handle_y, 16, 30), border_radius=3)
    pygame.draw.rect(screen, (107, 63, 44), (handle_x, handle_y, 16, 30), 2, border_radius=3)
    
    #check for mouse clicks on the slider
    mouse_pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  #check if left mouse button is pressed
        #create a larger invisible rectangle around the slider to make it easier to click and drag, 10 pixels above and below the slider
        slider_rect = pygame.Rect(volume_slider_x, volume_slider_y - 10, volume_slider_width, volume_slider_height + 20)
        if slider_rect.collidepoint(mouse_pos):
            #calculate new volume based on mouse position relative to slider
            new_volume = (mouse_pos[0] - volume_slider_x) / volume_slider_width
            current_volume = max(VOLUME_MIN, min(VOLUME_MAX, new_volume))
            pygame.mixer.music.set_volume(current_volume) #setting the volume to the music
    
    #display volume percentage text 
    volume_text = font.render(f"Volume: {int(current_volume * 100)}%", True, (61, 38, 28))
    screen.blit(volume_text, (volume_slider_x, volume_slider_y - 35))


#story intro function
def draw_story_intro(screen, font, scroll):

    #retrieving the global variables
    global story_text_reveal, story_last_update

    screen.fill((62, 36, 26)) #filling the screen with a dark brown colour

    #introduction text
    story = (
        "Use Arrow Keys to scroll. \n\n"
        "Long ago, the village of Hazelwood was kept warm and safe \nby a gentle magical heart known as the Ember Core.\n"
        "Its light protected the forest, kept the land fertile, and \nbrought peace to everyone who lived there.\n\n"

        "But over the years, the villagers drifted apart.\n"
        "Small disagreements grew, old friendships faded, and \npeople stopped tending to the grove where the Ember Core \nrested.\n"
        "With no one to care for it, the Core began to dim… and \nsomething inside it changed.\n\n"

        "Strange shadows crept into the forest.\n"
        "Lights flickered in the night.\n"
        "Quakes struck the village.\n"
        "And a heavy, uneasy silence settled over Hazelwood.\n\n"

        "The Elder sensed that something was wrong, something deeper \nthan a simple failing of magic, but no one in the village was \nbrave enough to venture and found out why.\n\n"

        "Then you, a wandering traveller passing through Hazelwood, \narrived.\n\n"

        "Seeing that you were kind-hearted and unafraid of the \nstrange, the Elder asked for your help.\n"
        "Not to fight… but to understand.\n"
        "To find what the Ember Core had become.\n"
        "To help the villagers reconnect and heal the wounds that \ncaused the Core to fade.\n"
        "And maybe, just maybe, to restore the light Hazelwood \nonce knew.\n"

        "Your journey begins here — in a quiet village that has \nforgotten its own warmth, and you may be the one \nwho can help it shine again.\n\n\n"
        
        "Press ESC to begin your journey.."
    )

    #typewriter timing system
    now = pygame.time.get_ticks() #getting the current time
    if now - story_last_update > STORY_TYPE_SPEED:
        story_text_reveal += 1
        story_last_update = now

    #clamp reveal so it never exceeds total text length
    if story_text_reveal > len(story):
        story_text_reveal = len(story)

    #visible portion of text that has been "typed"
    visible_text = story[:story_text_reveal]
    
    #draw text and measure height
    y = 100 + scroll

    for line in visible_text.split('\n'):
        render = font.render(line, True, (209, 118, 33))
        screen.blit(render, (100, y))
        y += 40 
    
    
#TIME DAY CYCLE FUNCTIONS

#setting the target overlay (for fading)
def set_time_of_day_overlay(time_of_day):
    global target_overlay

    if time_of_day == TIME_DAY:
        #during the day, there is no overlay, so the target RGBA values are all 0 (fully transparent)
        target_overlay = [0, 0, 0, 0] 

    elif time_of_day == TIME_SUNSET:
        #during sunset, a warm orange overlay with moderate transparency
        target_overlay = [255, 150, 90, 80]

    elif time_of_day == TIME_NIGHT:
        #during night, a cool blue overlay with higher transparency
        target_overlay = [40, 60, 110, 130]

    elif time_of_day == TIME_DAWN:
        #during dawn, a soft pink overlay with moderate transparency
        target_overlay = [190, 200, 255, 70]
        
#fade handling of overlay
def update_overlay_fade():
    for i in range(4):
        #if the current overlay value is less than the target, increase it gradually by the fade speed until it reaches the target
        if current_overlay[i] < target_overlay[i]:
            current_overlay[i] += OVERLAY_FADE_SPEED
            #if it exceeds the target, clamp it to the target value
            if current_overlay[i] > target_overlay[i]:
                current_overlay[i] = target_overlay[i]

        #if the current overlay value is greater than the target, decrease it gradually by the fade speed until it reaches the target
        elif current_overlay[i] > target_overlay[i]:
            current_overlay[i] -= OVERLAY_FADE_SPEED
            #if it goes below the target, clamp it to the target value
            if current_overlay[i] < target_overlay[i]:
                current_overlay[i] = target_overlay[i]

#drawing the overlay
def draw_time_of_day_overlay(screen):
    #create a transparent surface the size of the screen to draw the overlay on
    overlay = pygame.Surface(
        (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    #fill the overlay with the current RGBA values, which creates a colored tint effect when blitted on the screen
    #reference each index position and draw the overlay with the colours in these indexed positions
    overlay.fill((
        int(current_overlay[0]),
        int(current_overlay[1]),
        int(current_overlay[2]),
        int(current_overlay[3])
    ))

    screen.blit(overlay, (0, 0)) #draw the overlay on the screen at (0, 0) so it covers the entire screen


#PLAYER INTERNAL MONOLOGUE SYSTEM
def trigger_monologue(text):
    global monologue_text, monologue_alpha, monologue_active, monologue_timer
    monologue_text = text  #set the text to the display of the monologue
    monologue_alpha = 0  #transparency of the monologue box
    monologue_active = True  #flag that monologue is active 
    monologue_timer = pygame.time.get_ticks()  #record start time of monologue

def draw_monologue(screen, font):
    if not monologue_active and monologue_alpha <= 0:
        return  #don't draw the monologue if it is not fully transparent

    #create the surface text with a light cream colour
    text_surface = font.render(monologue_text, True, (245, 235, 220))
    text_surface.set_alpha(monologue_alpha)

    #create a dark background box around the text
    padding = 20
    bg_width = text_surface.get_width() + padding * 2
    bg_height = text_surface.get_height() + padding * 2

    #create a semi transparent dark background for the monologue box
    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    bg_surface.fill((20, 20, 20, monologue_alpha))  

    #position at bottom center of screen
    x = (constants.SCREEN_WIDTH - bg_width) // 2
    y = constants.SCREEN_HEIGHT - 140

    #draw background first then text on top 
    screen.blit(bg_surface, (x, y))
    screen.blit(text_surface, (x + padding, y + padding))

def update_monologue():
    #variables to control fading of monologue box and how long it stays for
    global monologue_alpha, monologue_active 

    if not monologue_active and monologue_alpha <= 0:
        return  #exit if the monologue is not active

    now = pygame.time.get_ticks()
    elapsed = now - monologue_timer  #time since monologue started

    #defining how the monologue fades in and out
    fade_in_end = MONOLOGUE_FADE_SPEED  #when the fade in finishes 
    hold_end = MONOLOGUE_FADE_SPEED + MONOLOGUE_DURATION  #when the hold finishes
    fade_out_end = MONOLOGUE_FADE_SPEED + MONOLOGUE_DURATION + MONOLOGUE_FADE_SPEED  #when fade out finishes

    #fade in, goes from 0 to 180 alpha gradually
    if elapsed < fade_in_end:
        monologue_alpha = int((elapsed / MONOLOGUE_FADE_SPEED) * 180)

    #hold, monologue box stays at 180 alpha
    elif elapsed < hold_end:
        monologue_alpha = 180

    #fade out, goes from 180 to 0 alpha gradually
    elif elapsed < fade_out_end:
        fade = elapsed - hold_end
        monologue_alpha = int(180 * (1 - fade / MONOLOGUE_FADE_SPEED))

    #done, so everthing is reset for next monologue
    else:
        monologue_alpha = 0
        monologue_active = False
        

#IN GAME CAPTURE FUNCTIONS
def capture_screenshot(screen):
    #make sure folder exists, and if not then create a folder for screenshots
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    #creating a timestap by getting the date and time using pygame functions
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    time_label = datetime.datetime.now().strftime("%d/%m/%Y")
    filename = f"screenshots/zen_capture_{timestamp}.png"

    #save the current screen to the folder as a file (png image file)   
    pygame.image.save(screen, filename)
    print(f"Screenshot saved: {filename}")

def load_gallery_images():
    #load all images from the screenshot folder
    images = []
    if not os.path.exists("screenshots"):
        return images  #return an empty list if the folder doesn't exist 

    #loop through all the files in the screenshots folder 
    for file in sorted(os.listdir("screenshots")):
        if file.endswith(".png"):  #only load png files 
            path = os.path.join("screenshots", file)  #file path of image
            img = pygame.image.load(path).convert_alpha()  #load image
            images.append((img, file))  #store image and filename as a tuple

    return images  #return the list of images   

def draw_gallery(screen, font):
    screen.fill((20, 20, 20))  #dark background for gallery

    #if no images in the gallery, display a message instead of trying to draw an image
    #gallery_images is a list of tuples (image, filename)
    if not gallery_images:
        text = font.render("No memories captured yet.", True, (200, 200, 200))
        screen.blit(text, text.get_rect(center=screen.get_rect().center))
        return

    #get current image and filename from gallery_images using gallery_index
    image, filename = gallery_images[gallery_index]

    #scale image down to 75% of original size 
    ZEN_SCALE = 0.75
    image = pygame.transform.smoothscale(
        image,
        (int(image.get_width() * ZEN_SCALE),
        int(image.get_height() * ZEN_SCALE))
    )

    #center image on screen
    rect = image.get_rect(center=(constants.SCREEN_WIDTH // 2,
                                   constants.SCREEN_HEIGHT // 2 - 20))
    screen.blit(image, rect)

    #draw date label at bottom left 
    label = font.render(datetime.datetime.now().strftime("%d/%m/%Y"), True, (180, 180, 180))
    screen.blit(label, (50, constants.SCREEN_HEIGHT - 60))

    #draw controls instructions at bottom center
    hint = font.render("Arrow Keys: Browse  |  ESC: Close", True, (120, 120, 120))
    screen.blit(hint, (constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT - 60))
    
    #draw title of gallery at top center
    title = font.render("GALLERY", True, (252, 211, 154))
    screen.blit(title, (constants.SCREEN_WIDTH // 2 - 60, 25))

# END OF HELPER FUNCTIONS -------------------------------------------------------------------------------------

run = True

#WORLD MAP LOADING -------------------------------------------------------------------------------------

#initialise a 2D array for the world tile data
world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)

#load tile data and create world
with open(resource_path('maps/map.csv'),newline = '') as csvfile: #open the csv map file
    #read the csv map file
    reader = csv.reader(csvfile,delimiter=',')
    for x,row in enumerate(reader):
        for y,tile in enumerate(row):
            world_data[x][y] = int(tile)

#create a list of all the tile types
tile_list = []
for x in range(156): #there are 156 different tile types
    tile_image = pygame.image.load(resource_path(f'maps/Tiles/tile_00{x}.png')).convert_alpha()
    #scale the tile to fit the pixel grid
    tile_image = pygame.transform.scale(tile_image,(48,48)) 
    tile_list.append(tile_image) #append each tile image to the list
    
# tile_list = []
# for x in range(156): #there are 156 different tile types
#     try:
#         tile_image = pygame.image.load(f'maps/Tiles/tile_00{x}.png').convert_alpha()
#     except FileNotFoundError:
#         #create a placeholder for the missing tile
#         tile_image = pygame.Surface((16, 16))
#     #scale the tile to fit the pixel grid
#     tile_image = pygame.transform.scale(tile_image,(48,48)) 
#     tile_list.append(tile_image) #append each tile image to the list

world = World() 

world.process_data(world_data,tile_list,item_images,mob_animations)

elder = world.elder
blacksmith = world.blacksmith
player = world.player
farmer = world.farmer
lumberjack = world.lumberjack
innkeeper = world.innkeeper
#cloaked = world.cloaked


#COMMENTED OUT - OLD DIALOGUE LOADING CODE (kept for reference)
# #quest dialogues
# dialogue_elder = scale_img(pygame.image.load("assets/images/items/dialogue_elder.png").convert_alpha(), 2)
# dialogue_lumberjack = scale_img(pygame.image.load("assets/images/items/dialogue_lumberjack.png").convert_alpha(), 2)
# dialogue_innkeeper = scale_img(pygame.image.load("assets/images/items/dialogue_innkeeper.png").convert_alpha(), 2)
# dialogue_innkeeper_2 = scale_img(pygame.image.load("assets/images/items/dialogue_innkeeper_2.png").convert_alpha(), 2)
# dialogue_elder_2 = scale_img(pygame.image.load("assets/images/items/dialogue_elder_2.png").convert_alpha(), 2)
# dialogue_blacksmith = scale_img(pygame.image.load("assets/images/items/dialogue_blacksmith.png").convert_alpha(), 2)
# dialogue_blacksmith_2 = scale_img(pygame.image.load("assets/images/items/dialogue_blacksmith_2.png").convert_alpha(), 2)
# dialogue_farmer = scale_img(pygame.image.load("assets/images/items/dialogue_farmer.png").convert_alpha(), 2)
# dialogue_farmer_2 = scale_img(pygame.image.load("assets/images/items/dialogue_farmer_2.png").convert_alpha(), 2)
# dialogue_elder_3 = scale_img(pygame.image.load("assets/images/items/dialogue_elder_3.png").convert_alpha(), 2)
# dialogue_elder_4 = scale_img(pygame.image.load("assets/images/items/dialogue_elder_4.png").convert_alpha(), 2)
#
# #final quest dialogues
# dialogue_wraith_1 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_1.png").convert_alpha(), 2)
# dialogue_player_2 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_2.png").convert_alpha(), 2)
# dialogue_wraith_3 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_3.png").convert_alpha(), 2)
# dialogue_player_4 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_4.png").convert_alpha(), 2)
# dialogue_wraith_5 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_5.png").convert_alpha(), 2)
# dialogue_player_6 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_6.png").convert_alpha(), 2)
# dialogue_wraith_7 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_7.png").convert_alpha(), 2)
# dialogue_player_8 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_8.png").convert_alpha(), 2)
# dialogue_wraith_9 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_9.png").convert_alpha(), 2)
# dialogue_player_10 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_10.png").convert_alpha(), 2)
# dialogue_wraith_11 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_11.png").convert_alpha(), 2)
# dialogue_player_12 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_12.png").convert_alpha(), 2)
# dialogue_wraith_13 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_13.png").convert_alpha(), 2)
# dialogue_player_14 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_player_14.png").convert_alpha(), 2)
# dialogue_wraith_15 = scale_img(pygame.image.load("assets/images/questFinal/dialogue_wraith_15.png").convert_alpha(), 2)
# END OF COMMENTED OUT CODE

#quest dialogues 
quest_dialogue_files = {
    'elder': 'assets/images/items/dialogue_elder.png',
    'elder_2': 'assets/images/items/dialogue_elder_2.png',
    'elder_3': 'assets/images/items/dialogue_elder_3.png',
    'elder_4': 'assets/images/items/dialogue_elder_4.png',
    'blacksmith': 'assets/images/items/dialogue_blacksmith.png',
    'blacksmith_2': 'assets/images/items/dialogue_blacksmith_2.png',
    'farmer': 'assets/images/items/dialogue_farmer.png',
    'farmer_2': 'assets/images/items/dialogue_farmer_2.png',
    'lumberjack': 'assets/images/items/dialogue_lumberjack.png',
    'innkeeper': 'assets/images/items/dialogue_innkeeper.png',
    'innkeeper_2': 'assets/images/items/dialogue_innkeeper_2.png',
}

quest_dialogues = {}
for key, path in quest_dialogue_files.items():
    quest_dialogues[key] = scale_img(pygame.image.load(resource_path(path)).convert_alpha(), 2)

#final quest dialogues - loaded with for loop
final_quest_dialogue_files = {
    'wraith_1': 'assets/images/questFinal/dialogue_wraith_1.png',
    'player_2': 'assets/images/questFinal/dialogue_player_2.png',
    'wraith_3': 'assets/images/questFinal/dialogue_wraith_3.png',
    'player_4': 'assets/images/questFinal/dialogue_player_4.png',
    'wraith_5': 'assets/images/questFinal/dialogue_wraith_5.png',
    'player_6': 'assets/images/questFinal/dialogue_player_6.png',
    'wraith_7': 'assets/images/questFinal/dialogue_wraith_7.png',
    'player_8': 'assets/images/questFinal/dialogue_player_8.png',
    'wraith_9': 'assets/images/questFinal/dialogue_wraith_9.png',
    'player_10': 'assets/images/questFinal/dialogue_player_10.png',
    'wraith_11': 'assets/images/questFinal/dialogue_wraith_11.png',
    'player_12': 'assets/images/questFinal/dialogue_player_12.png',
    'wraith_13': 'assets/images/questFinal/dialogue_wraith_13.png',
    'player_14': 'assets/images/questFinal/dialogue_player_14.png',
    'wraith_15': 'assets/images/questFinal/dialogue_wraith_15.png',
}

final_quest_dialogues = {}
for key, path in final_quest_dialogue_files.items():
    final_quest_dialogues[key] = scale_img(pygame.image.load(resource_path(path)).convert_alpha(), 2)

#zen mode dialogues
dialogue_elder_zen = scale_img(pygame.image.load(resource_path("assets/images/items/zen_dialogues/dialogue_elder_zen.png")).convert_alpha(), 2)
dialogue_lumberjack_zen = scale_img(pygame.image.load(resource_path("assets/images/items/zen_dialogues/dialogue_lumberjack_zen.png")).convert_alpha(), 2)
dialogue_innkeeper_zen = scale_img(pygame.image.load(resource_path("assets/images/items/zen_dialogues/dialogue_innkeeper_zen.png")).convert_alpha(), 2)
dialogue_blacksmith_zen = scale_img(pygame.image.load(resource_path("assets/images/items/zen_dialogues/dialogue_blacksmith_zen.png")).convert_alpha(), 2)
dialogue_farmer_zen = scale_img(pygame.image.load(resource_path("assets/images/items/zen_dialogues/dialogue_farmer_zen.png")).convert_alpha(), 2)

#quest flags
lumberjack_quest = False
blacksmith_quest = False
chicken_complete = False
brick_quest = False
lantern_delivered = False

#create item group
item_group = pygame.sprite.Group()
for item in world.item_list:
    item_group.add(item)

#for toggling the guide menu
show_guide = False

#load GIF animation
gif_frames = load_gif_frames(resource_path("assets/images/questFinal/ember_core.gif"), scale=2)
gif_frame_index = 0
gif_frame_timer = 0
GIF_FRAME_DELAY = 300
gif_finished = False 


#idle monologues
idle_monologues = [
    "It's peaceful here... a good place to reflect.",
    "Everything seems calm for now.",
    "I could stay here a while, just watching the world.",
    "It's nice to take a break from all the chaos.",
    "I wonder what stories the villagers have to tell.",
    "I'm glad everything has been sorted out.",
]



#MAIN GAME LOOP -------------------------------------------------------------------------------------

while run:

    clock.tick(constants.FPS)
    now = pygame.time.get_ticks()
     
    #checking time change timer to see if it's time to change the time of day and update the overlay accordingly
    if time_change_timer is not None:
        now = pygame.time.get_ticks() #get the current time in milliseconds
        #check if the elapsed time since the last change is greater than or equal to the defined delay (60 seconds) for changing time of day
        if now - time_change_timer >= TIME_CHANGE_DELAY:
            #cycle through all time of day states (0 to 3)
            time_of_day = (time_of_day + 1) % 4 
            #setting the overlay using the set_time_of_day_overlay function to update the target RGBA values for the new time of day
            set_time_of_day_overlay(time_of_day) 
            #reset the timer for the next change
            time_change_timer = now 
    
    
    #checking zen mode timer
    if zen_timer_started and not zen_intro:
        if pygame.time.get_ticks() - zen_timer_start >= constants.ZEN_WAIT_MS:
            zen_intro = True

    #MAIN MENU
    if start_game == False:
        screen.fill(constants.BG)
        screen.blit(background_image, (0, 0))
        screen.blit(trim_logo_img, logo_rect)

        #menu buttons
        if play_button.draw(screen):
            #start_game = True
            show_story_intro = True
            story_text_reveal = 0
            story_last_update = pygame.time.get_ticks()
                        
        if quit_button.draw(screen):
            run = False    
            
        if guide_button.draw(screen):
            screen.blit(guide_menu, (0,0))
            

        #STORY INTRO SCREEN
        if show_story_intro:
            
            draw_story_intro(screen, font, story_scroll)

            keys = pygame.key.get_pressed()

            #manual scrolling with arrow keys
            if keys[pygame.K_UP]:
                story_scroll += story_manual_speed

            if keys[pygame.K_DOWN]:
                story_scroll -= story_manual_speed


            
   
    else:
        #screen.fill(constants.BG)
        
        #ZEN MENU
        if zen_intro and not zen_mode:
            screen.blit(zen_menu, (0,0))
            
            
            
        #IN FINAL QUEST
        elif in_final_quest:
            screen.blit(final_quest_bg, (0, 0)) #drawing the final quest background
            
            #update animations for the final player and the final npc (monster)
            if player_final:
                player_final.action = 0 
                player_final.update() 
            if final_npc:
                final_npc.action = 0
                final_npc.update()
               
            #drawing the characters after updating
            if player_final:  
                player_final.draw(screen)
            if final_npc:
                final_npc.draw(screen)

           #referencing the dialogue sequence between player and monster from the dictionary
            dialogue_sequence = [
                final_quest_dialogues['wraith_1'],
                final_quest_dialogues['player_2'],
                final_quest_dialogues['wraith_3'],
                final_quest_dialogues['player_4'],
                final_quest_dialogues['wraith_5'],
                final_quest_dialogues['player_6'],
                final_quest_dialogues['wraith_7'],
                final_quest_dialogues['player_8'],
                final_quest_dialogues['wraith_9'],
                final_quest_dialogues['player_10'],
                final_quest_dialogues['wraith_11'],
                final_quest_dialogues['player_12'],
                final_quest_dialogues['wraith_13'],
                final_quest_dialogues['player_14'],
                final_quest_dialogues['wraith_15']
            ]
            
            #loops through the list of the dialogue sequence and displays it on the screen
            if dialogue_index < len(dialogue_sequence):
                screen.blit(dialogue_sequence[dialogue_index], (0,0))
            else:
                #when the dialogue ends, the player and npc are not displayed anymore
                player_final = None
                final_npc = None
                

                #code to handle playing of gif animation
                if not gif_finished: #while gif is still playing
                    gif_frame_timer += clock.get_time() #increment timer by time since last frame
                    if gif_frame_timer >= GIF_FRAME_DELAY: #time to switch frame
                        gif_frame_index += 1 #move to next frame of gif
                        gif_frame_timer = 0 #reset timer
                    
                    #check if gif has finished
                    if gif_frame_index >= len(gif_frames):
                        gif_finished = True #exit playing the loop
                        gif_frame_index = len(gif_frames) - 1  #stay on last frame of gif
                    
                    #draw current frame of gif
                    screen.blit(gif_frames[gif_frame_index], ((constants.SCREEN_WIDTH // 2) - 200, (constants.SCREEN_HEIGHT // 2) - 200))
                else:
                    #gif if finished, last frame is shown
                    screen.blit(gif_frames[gif_frame_index], ((constants.SCREEN_WIDTH // 2) - 200, (constants.SCREEN_HEIGHT // 2) - 200))
                    
                    #signal player to talk to elder to finish quest
                    current_quest_text = "Talk to the Elder to finish your journey."
                    
                    #show_quest_panel = False
                    
                    #when the gif finishes, the end of the final quest is signalled by the various flags below
                    #the game returns to the main world
                    in_final_quest = False
                    world_paused = False
                    dialogue_index = 0
                    gif_finished = False  
                    gif_frame_index = 0
                    level_complete = False
                    time_of_day = TIME_DAY
                    time_change_timer = pygame.time.get_ticks()
                    
                    #reposition player away from exit tile (near elder)
                    player.rect.center = (elder.rect.centerx - 90, elder.rect.centery + 20)
                    scale_character(player, 0.33) #scale character back to normal size
                    
                    #stop final music and resume ending bg music
                    pygame.mixer.music.fadeout(500)
                    pygame.time.delay(100)
                    pygame.mixer.music.load("assets/audio/ending_bg.mp3")
                    pygame.mixer.music.set_volume(1)
                    pygame.mixer.music.play(-1, 0.0, 1000)

                    #ensure final npc (monster) and player are removed from the main world
                    final_npc = None
                    player_final = None
                    
                    end_of_game = True #flag used to signal end of the game
                                            
          
        
        #ZEN MODE
        elif zen_mode:
            
            if not zen_player_positioned:
                player.rect.center = (elder.rect.centerx + 90, elder.rect.centery + 20)
                zen_player_positioned = True
            
            world.draw(screen)
            
            #movement (same as normal mode)
            dx = 0
            dy = 0
            if moving_right:
                dx = constants.SPEED
            if moving_left:
                dx = -constants.SPEED
            if moving_up:
                dy = -constants.SPEED
            if moving_down:
                dy = constants.SPEED
                
            #stop music and play zen music
            if not zen_music_started:
                pygame.mixer.music.fadeout(500)
                pygame.mixer.music.load("assets/audio/zen_bg.mp3")
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.play(-1, fade_ms=1000)
                zen_music_started = True
            

            #random rain sounds
            now = pygame.time.get_ticks() #getting current pygame time
            if not rain_playing and now >= next_rain_time: #checks if rain is not playing and if it is time to start rain
                rain_sfx.play(-1, fade_ms=2000)  #start rain with fade in, loop audio
                rain_playing = True 
                rain_start_time = now  #record start time
                rain_duration = random.randint(RAIN_DURATION_MIN, RAIN_DURATION_MAX) #random length of time rain plays for

            #checks if rain is playing and if duration has passed
            if rain_playing and now >= rain_start_time + rain_duration: 
                rain_sfx.fadeout(2000)  #fade out over 2 seconds
                rain_playing = False
                #sets next rain time between 2-5 minutes from now
                next_rain_time = now + random.randint(1 * 60000, 5 * 60000)             

            #draw player and NPCs
            player.draw(screen)
            elder.draw(screen)
            blacksmith.draw(screen)
            farmer.draw(screen)
            lumberjack.draw(screen)
            innkeeper.draw(screen)

            #move player normally (no portals, no level_complete)
            #_ used because player.move() returns two values, but in zen mode 
            # #level_complete not needed, only screen_scroll is used
            #_ is the standard Python convention for a variable name
            screen_scroll, _ = player.move(dx, dy, world.obstacle_tiles, None)

            #update world + player
            world.update(screen_scroll)
            player.update()
            #update NPCs
            elder.ai(screen_scroll); elder.update()
            blacksmith.ai(screen_scroll); blacksmith.update()
            farmer.ai(screen_scroll); farmer.update()
            lumberjack.ai(screen_scroll); lumberjack.update()
            innkeeper.ai(screen_scroll); innkeeper.update()
            
            #monologues
            #time of day monologues
            if time_of_day != last_time_of_day: #if the time of day has changed
                #dawn monologue
                if time_of_day == TIME_DAWN:
                    trigger_monologue("A new day begins in Hazelwood.") 
                #night monologue
                elif time_of_day == TIME_NIGHT:
                    trigger_monologue("Night settles over the village.. the villagers can finally rest")
                last_time_of_day = time_of_day #update last time of day variable
            
            #idle monologue
            #check if player is stationary
            if not moving_left and not moving_right and not moving_up and not moving_down:
                #check if enough time has passed since last idle monologue
                if now - last_idle_monologue > IDLE_MONOLOGUE_COOLDOWN: 
                    trigger_monologue(random.choice(idle_monologues)) #trigger random idle monologue
                    last_idle_monologue = now #update last idle monologue time
                    IDLE_MONOLOGUE_COOLDOWN = random.randint(12000, 20000)  #generate new random cooldown
            else:
                #player is moving, reset flag
                idle_monologue_triggered = False

            #zen-only final dialogues
            if player.rect.colliderect(elder.rect):
                screen.blit(dialogue_elder_zen, ((constants.SCREEN_WIDTH / 2) - 700,
                                            constants.SCREEN_HEIGHT - 720))
                dialogue_open = True
            if player.rect.colliderect(blacksmith.rect):
                screen.blit(dialogue_blacksmith_zen, ((constants.SCREEN_WIDTH / 2) - 700,
                                                    constants.SCREEN_HEIGHT - 720))
                dialogue_open = True
            if player.rect.colliderect(farmer.rect):
                screen.blit(dialogue_farmer_zen, ((constants.SCREEN_WIDTH / 2) - 700,
                                                constants.SCREEN_HEIGHT - 720))
                dialogue_open = True
            if player.rect.colliderect(lumberjack.rect):
                screen.blit(dialogue_lumberjack_zen, ((constants.SCREEN_WIDTH / 2) - 700,
                                                constants.SCREEN_HEIGHT - 720))
                dialogue_open = True
            if player.rect.colliderect(innkeeper.rect):
                screen.blit(dialogue_innkeeper_zen, ((constants.SCREEN_WIDTH / 2) - 700,
                                                constants.SCREEN_HEIGHT - 720))  
                dialogue_open = True          
        
        
            #drawing and calling functions for time of day changes - kept at end so it overlays everything before
            update_overlay_fade()
            draw_time_of_day_overlay(screen)
            
            #updating and drawing monologue
            update_monologue()
            if not dialogue_open:
                draw_monologue(screen, font)
            
            
            #drawing the ambient particles
            FADE_SPEED = 3  #how fast particles fade in/out

            for particle in ambient_particles: #looping through list of ambient particles
                if time_of_day == TIME_NIGHT:
                    #fade in at night
                    if particle.visible_alpha < 255:
                        particle.visible_alpha = min(particle.visible_alpha + FADE_SPEED, 255)
                else:
                    #fade out during day
                    if particle.visible_alpha > 0:
                        particle.visible_alpha = max(particle.visible_alpha - FADE_SPEED, 0)

                #update and draw particles only if at least partially visible
                if particle.visible_alpha > 0:
                    particle.update()
                    particle.draw(screen)
        
          
        #MAIN GAME  --------------------------  
        else:
            world.draw(screen) #normal world rendering and updates
            

            #calculate player movement
            dx = 0 #change in x coordinate (left to right)
            dy = 0 #change in y coordinate (up and down)
            if moving_right == True:
                dx = constants.SPEED
            if moving_left == True:
                dx = -constants.SPEED #negative as it is in the opposite direction
            if moving_up == True:
                dy = -constants.SPEED #moving up is negative
            if moving_down == True:
                dy = constants.SPEED
            
            #draw everything on screen
            player.draw(screen)
            blacksmith.draw(screen)
            elder.draw(screen)
            farmer.draw(screen)
            lumberjack.draw(screen)
            innkeeper.draw(screen)
            item_group.draw(screen)
            
            draw_info(player_info)
            screen.blit(compass, (30, 70))
            

            #quest panel drawn only if dialogue is not open
            if show_quest_panel and not dialogue_open:
                draw_quest_panel(screen, current_quest_text)
                
            
            screen_scroll,level_complete = player.move(dx, dy,world.obstacle_tiles,world.exit_tile, can_enter_final_quest)

            #update everything on screen 
            world.update(screen_scroll)
            player.update()
            elder.ai(screen_scroll);elder.update()
            blacksmith.ai(screen_scroll);blacksmith.update()
            farmer.ai(screen_scroll);farmer.update()
            lumberjack.ai(screen_scroll);lumberjack.update()
            innkeeper.ai(screen_scroll);innkeeper.update()
            item_group.update(screen_scroll,player,player_info)
        
            #flag that determines if the dialogue box is open or not 
            #ensures quest panel is only displayed when the dialogue box is not open
            dialogue_open = False 
            
            #QUEST DIALOGUES ----------------------------------
            
            #elder
            if player.rect.colliderect(elder.rect):
                dialogue_open = True 
                if ember_quest and lantern_delivered and blacksmith_quest and brick_quest and end_of_game:
                    show_quest_panel = False
                    time_of_day = TIME_DAY #variable used in time of day changes
                    time_change_timer = pygame.time.get_ticks()
                    screen.blit(quest_dialogues['elder_4'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))

                    #start 1 min timer before displaying thank you message and zen mode instructions
                    if not zen_timer_started:
                        zen_timer_started = True
                        zen_timer_start = pygame.time.get_ticks()   
                        
                elif ember_quest and lantern_delivered and blacksmith_quest and brick_quest:
                    screen.blit(quest_dialogues['elder_3'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    can_enter_final_quest = True
                    set_quest("Head East to the portal.")
                
                #heading to blacksmith after lantern
                elif lantern_delivered:
                    screen.blit(quest_dialogues['elder_2'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    screen.blit(letter, (0, 20))
                    set_quest("Quest complete! Head NE to the Blacksmith")

                #giving in the lantern
                elif player_info[3] == 1 and not lantern_delivered:
                    screen.blit(quest_dialogues['elder_2'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    screen.blit(letter, (0, 20))
                    player_info[3] = 0
                    lantern_delivered = True
                    set_quest("Quest complete! Head NE to the Blacksmith")
                    
                else:
                    screen.blit(quest_dialogues['elder'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    set_quest("Head NW to the woods, find lantern and bring to elder.")

            #lumberjack
            if player.rect.colliderect(lumberjack.rect):
                lumberjack_quest = True
                screen.blit(quest_dialogues['lumberjack'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))

            #farmer
            if player.rect.colliderect(farmer.rect):
                screen.blit(quest_dialogues['farmer'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                set_quest("Explore the village to find the chicken.")
                if player_info[2] == 1:
                    chicken_complete = True
                if chicken_complete:
                    screen.blit(quest_dialogues['farmer_2'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    player_info[2] = 0
                    set_quest("Quest complete! Head NW to the innkeeper.")

            #blacksmith
            if player.rect.colliderect(blacksmith.rect):
                screen.blit(quest_dialogues['blacksmith'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                set_quest("Explore the village and bring back 5 metals.")
                if player_info[0] == 5:
                    blacksmith_quest = True

                if blacksmith_quest:
                    screen.blit(quest_dialogues['blacksmith_2'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    player_info[0] = 0
                    set_quest("Quest complete! Head north to the farmer.")

            #innkeeper
            if player.rect.colliderect(innkeeper.rect):
                screen.blit(quest_dialogues['innkeeper'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                set_quest("Explore the village and bring back 5 woods.")
                if player_info[1] == 5:
                    brick_quest = True

                if brick_quest:
                    screen.blit(quest_dialogues['innkeeper_2'], ((constants.SCREEN_WIDTH / 2) - 700, constants.SCREEN_HEIGHT - 720))
                    player_info[1] = 0
                    ember_quest = True
                    set_quest("Quest complete! Head back to Elder.")
            
            #drawing and calling functions for time of day changes - kept at end so it overlays everything before
            update_overlay_fade()
            draw_time_of_day_overlay(screen)
            
            update_monologue()
            draw_monologue(screen, font)
            
            #PAUSE MENU
            if pause_game and not settings_open: #pause menu displayed if settinge menu not open
                guide_open = False
                #draw a dark semi transparent overlay on the screen
                overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                #display the pause menu image in the middle of the screen
                pause_menu_rect = pause_menu_img.get_rect(center=(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2))
                screen.blit(pause_menu_img, pause_menu_rect)
                
                #when the resume/exit button is pressed, game is no longer paused
                if resume_button.draw(screen):
                    guide_open = False
                    pause_game = False
                
                #when the settings button is pressed, the settings menu is displayed
                if settings_button.draw(screen):
                    guide_open = False  #reset guide_open to ensure settings menu displays first
                    settings_open = True
            
            
            #SETTINGS MENU
            if settings_open:
                guide_open = False
                #draw a dark semi transparent overlay on the screen
                overlay = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                #display the settings menu image in the middle of the screen
                settings_menu_rect = settings_menu_img.get_rect(center=(constants.SCREEN_WIDTH // 2 - 30, constants.SCREEN_HEIGHT // 2 + 50))
                screen.blit(settings_menu_img, settings_menu_rect)
                
                #only draw buttons and slider if guide menu is not open
                if not guide_open:
                    #draw volume slider and handle volume changes
                    draw_volume_slider(screen)
                    
                    #when the guide button is pressed, display the guide menu
                    if settings_guide_button.draw(screen):
                        guide_open = True
                    
                    #when the main menu button is pressed, return to main menu and restart
                    if settings_main_menu_button.draw(screen):
                        #resetting the game state by resetting game flags
                        guide_open = False
                        pause_game = False
                        settings_open = False
                        start_game = False
                        zen_mode = False
                        zen_intro = False
                        in_final_quest = False
                        world_paused = False
                        end_of_game = False
                        ending_credits = False
                        time_of_day = TIME_DAY
                        time_change_timer = pygame.time.get_ticks()
                    
                    #when the close button (x) is pressed, close settings menu and return to pause menu
                    if settings_close_button.draw(screen):
                        settings_open = False
                
                #if guide menu is open, display it
                if guide_open:
                    screen.blit(guide_menu, (0, 0))
            
            
            # #DRAWING FLASH - MOVE TO ZEN MODE AFTER -----------------------------------
            # if flash_active:
            #     flash_surface = pygame.Surface(
            #         (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            #         pygame.SRCALPHA
            #     )
            #     flash_surface.fill((255, 245, 230, flash_alpha))  # warm white
            #     screen.blit(flash_surface, (0, 0))
 
            
            #pause the world and enter final quest mode, world is not destroyed
            if level_complete == True:
                item_group.empty() #empty the item group as it is not required anymore
                
                #fill the background with the final quest background
                screen.fill(constants.BG)
                screen.blit(final_quest_bg, (0, 0))
                
                #stop current music and start final quest music
                pygame.mixer.music.fadeout(800)
                pygame.time.delay(300)
                pygame.mixer.music.load("assets/audio/finalQuest_bg.mp3")  
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1, 0.0, 1000)
                
                #flags to indicate final quest state
                in_final_quest = True
                current_quest_text = ""
                level_complete = False
                  
                #create another player character for the final quest in the different setting              
                player_final = Character(400, (constants.SCREEN_HEIGHT // 2) + 200,
                                   mob_animations, 0, False, 1, animation_cooldown=200)
                #scale player bigger for final scene
                scale_character(player_final, 3)

                #draw the final npc
                final_npc = Character(constants.SCREEN_WIDTH - 400,
                                        (constants.SCREEN_HEIGHT // 2) + 170,
                                        mob_animations, 7, False, 1, animation_cooldown=400)
                #scale final_npc 
                scale_character(final_npc, 0.7)

                #draw final background immediately (already added above, ensures background is drawn)
                screen.fill(constants.BG)
                screen.blit(final_quest_bg, (0, 0)) 



            

    #event handler (close window, click keybord, etc)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        #take keyboard preses 
        if event.type == pygame.KEYDOWN:
            
            #advance dialogue with spacebar
            if in_final_quest and event.key == pygame.K_SPACE:     
                dialogue_index += 1  
                
            #esc key handler - used for both story intro and pause game
            if event.key == pygame.K_ESCAPE:
                if guide_open:
                    #close guide menu if it is open
                    guide_open = False
                elif show_story_intro:
                    show_story_intro = False
                    start_game = True
                    time_of_day = TIME_DAY
                    
                    time_change_timer = pygame.time.get_ticks()
                #toggle pause during normal gameplay   
                elif start_game:                    
                    pause_game = not pause_game #game resumes if currently paused, pauses if currently running
            
                #elif start_game and not in_final_quest and not zen_mode:  
            
            #spacebar to enter zen mode
            if zen_intro and event.key == pygame.K_SPACE:
                zen_mode = True
                
            
                
            #if zen_mode and event.key == pygame.K_c:
            if event.key == pygame.K_c:  #if C key is pressed
                
                camera_sfx.play()  #play camera shutter sound
                capture_screenshot(screen)  #capture screenshot to file
                
                #create flash effect (wide fade on screen)
                flash_alpha = FLASH_MAX_ALPHA #stored as 120 initially
                flash_active = True
                
                if flash_active:
                    #the surface of the flash is the entire screen
                    flash_surface = pygame.Surface(
                        (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
                        pygame.SRCALPHA
                    )
                    #fill with a warm white colour with transparency
                    flash_surface.fill((255, 245, 230, flash_alpha))
                    screen.blit(flash_surface, (0, 0))
                    
                    #fade out of the flash
                    flash_alpha -= FLASH_FADE_SPEED  #stored as 6000 (ms)
                    if flash_alpha <= 0:
                        flash_alpha = 0
                        flash_active = False

            if event.key == pygame.K_g:
                gallery_images = load_gallery_images()  #load all screenshots
                gallery_index = 0  #start at the first image
                gallery_open = True  #display gallery

            #gallery controls
            if gallery_open:    
                if event.key == pygame.K_ESCAPE:  #if ESC pressed, gallery closes
                    gallery_open = False

                #if the right arrow pressed, increase index by 1 and advance through gallery
                #% len(gallery_images) means that when the index reaches the end of the list, 
                #it loops back to the start (circular navigation)
                elif event.key == pygame.K_RIGHT: 
                    gallery_index = (gallery_index + 1) % len(gallery_images)

                #if the left arrow pressed, decrease index by 1 and go back in gallery
                elif event.key == pygame.K_LEFT:
                    gallery_index = (gallery_index - 1) % len(gallery_images)
                
            
            #normal movement only when not in final quest
            if not in_final_quest:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_w:
                    moving_up = True
                if event.key == pygame.K_s:
                    moving_down = True


                        # if event.key == pygame.K_ESCAPE:
            #     pause_game = True
                    
            #     # stop final music and resume main bg music
            #     pygame.mixer.music.fadeout(500)
            #     pygame.time.delay(100)
            #     pygame.mixer.music.load("assets/audio/ending_bg.mp3")
            #     pygame.mixer.music.set_volume(0.3)
            #     pygame.mixer.music.play(-1, 0.0, 1000)

            #     # restore items to screen
            #     item_group.empty()
            #     for item in world.item_list:
            #         item_group.add(item)

            #     # remove final NPC and player
            #     final_npc = None
            #     player_final = None
            
        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False
                
    if gallery_open:
        draw_gallery(screen, font)

        pygame.display.update()
        continue  #skip the rest of the game loop while the gallery is open
    
    pygame.display.update()


pygame.quit()

        # elif zen_mode:
            
        #     #positioning player near elder when zen mode is entered
        #     if not zen_player_positioned:
        #         player.rect.center = (elder.rect.centerx + 90, elder.rect.centery + 20)
        #         zen_player_positioned = True
            
        #     world.draw(screen) #drawing the world on the screen
            
        #     #movement (same as normal mode)
        #     dx = 0
        #     dy = 0
        #     if moving_right:
        #         dx = constants.SPEED
        #     if moving_left:
        #         dx = -constants.SPEED
        #     if moving_up:
        #         dy = -constants.SPEED
        #     if moving_down:
        #         dy = constants.SPEED
                
        #     #stop music and play zen music
        #     #.......

        #     #random rain sounds
        #     #.......
            
        #     #draw player and NPCs
        #     player.draw(screen)
        #     elder.draw(screen)
        #     blacksmith.draw(screen)
        #     farmer.draw(screen)
        #     lumberjack.draw(screen)
        #     innkeeper.draw(screen)

        #     #move player normally (no portals, no level_complete)
        #     #_ used because player.move() returns two values, but in zen mode 
        #     # #level_complete not needed, only screen_scroll is used
        #     #_ is the standard Python convention for a variable name
        #     screen_scroll, _ = player.move(dx, dy, world.obstacle_tiles, None)

        #     #update world + player
        #     world.update(screen_scroll)
        #     player.update()
        #     #update NPCs
        #     elder.ai(screen_scroll); elder.update()
        #     blacksmith.ai(screen_scroll); blacksmith.update()
        #     farmer.ai(screen_scroll); farmer.update()
        #     lumberjack.ai(screen_scroll); lumberjack.update()
        #     innkeeper.ai(screen_scroll); innkeeper.update()
            
        #     #monologues
        #     #time of day monologues
        #     #.......
            
        #     #idle monologue
        #     #.......

        #     #zen-only final dialogues
        #     #.......      
        
        #     #drawing and calling functions for time of day changes, kept at end so it overlays everything before
        #     update_overlay_fade()
        #     draw_time_of_day_overlay(screen)
            
        #     #updating and drawing monologue
        #     update_monologue()
        #     if not dialogue_open:
        #         draw_monologue(screen, font)
            
        #     #drawing the ambient particles
        #     #.......

