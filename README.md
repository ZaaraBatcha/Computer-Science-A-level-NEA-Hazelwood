# Computer-Science-A-level-NEA-Hazelwood

A 2D exploration and quest game built in Python using Pygame. The project follows the story of Hazelwood, a quiet village with NPC interactions, quests, atmospheric ambience, and a final challenge sequence.

## Overview

This project was created as a Computer Science A-level NEA and focuses on:

- interactive gameplay using tile-based world exploration
- NPC dialogue and quest progression
- environmental storytelling and world-building
- day/night cycle and ambient effects
- audio and menu systems
- a complete playable game loop with menus, settings, and pause states

## Features

- Village exploration and movement across a large map
- NPC interaction and quest-based progression
- Final quest sequence with a different gameplay mood
- Day/night cycle and atmospheric overlays
- Audio effects and background music
- Pause menu, settings menu, and player guide
- Screenshot/gallery system
- Zen mode for relaxed exploration

## Requirements

To run the project locally, make sure you have:

- Python 3.9+
- pygame
- Pillow

Install the dependencies with:

```bash
pip install pygame pillow
```

## How to run

From the project folder, run:

```bash
python main.py
```

If you are on Windows and Python is installed but not in PATH, you can use:

```powershell
py main.py
```

## Controls

- WASD or arrow keys: move the player
- E: interact with NPCs or objects
- Esc: pause menu
- Mouse: menu buttons and UI interaction

## Project structure

- `main.py` – main game loop and setup
- `constants.py` – global game constants and settings
- `character.py` – player and NPC logic
- `world.py` – map and world management
- `items.py` – collectible and interaction objects
- `button.py` – UI button functionality
- `particles.py` – visual effects
- `assets/` – images, fonts, sound, and game resources
- `maps/` – CSV and tilemap data

## Notes

This project is designed as a standalone desktop game and is best run from the project directory so the asset paths resolve correctly.

## License

This project is for educational use as part of the NEA submission. See the project files and assets for any specific licensing or usage notes.
