# constants.py

import pygame

# --- Configurare Ecran (7 inch RPi) ---
# Change these values to your tablet's resolution
SCREEN_WIDTH = 768  
SCREEN_HEIGHT = 1024 

# Colors and other constants remain the same...
FPS = 24

# --- Culori ---
COLOR_BG = (240, 240, 240)
COLOR_BLOCK = (0, 151, 157)         # Arduino Teal
COLOR_BLOCK_BORDER = (0, 100, 105)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_TEXT_BLACK = (0, 0, 0)
COLOR_SUCCESS = (40, 180, 40)
COLOR_FAIL = (200, 50, 50)

# --- Timpi ---
DEMO_START_DELAY_MS = 5000  # 5 secunde pauză înainte de demo
GAME_DURATION_SEC = 60      # 60 secunde timp de joc

# --- Modelul Țintă (SOLUȚIA) ---
# Format: (Stare LED, Durata ms, Text Afișat, E Final?)
TARGET_PATTERN = [
    (True,  1000, "digitalWrite(HIGH);\ndelay(1000);", False),
    (False, 2000, "digitalWrite(LOW);\ndelay(2000);", False),
    (True,  2000, "digitalWrite(HIGH);\ndelay(2000);", False),
    (True,  3000, "digitalWrite(HIGH);\ndelay(3000);", False),
    (False, 0,    "digitalWrite(LOW);\n(FINAL)",       True)
]

# --- Blocurile Disponibile (Inventar) ---
# Jucătorul le vede amestecate
AVAILABLE_BLOCKS_DATA = [
    (False, 2000, "digitalWrite(LOW);\ndelay(2000);", False),
    (True,  3000, "digitalWrite(HIGH);\ndelay(3000);", False),
    (True,  1000, "digitalWrite(HIGH);\ndelay(1000);", False),
    (False, 0,    "digitalWrite(LOW);\n(FINAL)",       True),
    (True,  2000, "digitalWrite(HIGH);\ndelay(2000);", False),
]

# Zona dreptunghiulară unde utilizatorul trebuie să pună blocurile
SOLUTION_ZONE_RECT = pygame.Rect(450, 50, 300, 400)