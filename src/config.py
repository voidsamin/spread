"""Central configuration for SPREAD.

Keep *all tunable constants* here so gameplay/simulation parameters
can be changed without hunting through code.

Rule of thumb:
- Anything that needs tweaks (sizes, speeds, probabilities, timers) goes here.
- Code logic stays in other modules.
"""

from __future__ import annotations

# -----------------------------
# Window / timing
# -----------------------------
TITLE = "SPREAD"
# WIDTH and HEIGHT are updated at runtime to native resolution (FULLSCREEN)
WIDTH, HEIGHT = 800, 600
FPS = 60
TIME_SCALE_1 = 1.0
TIME_SCALE_2 = 2.0
TIME_SCALE_3 = 4.0

# -----------------------------
# Camera / scrolling
# -----------------------------
CAMERA_SMOOTHING = 0.08          # lerp factor per frame (lower = smoother/slower)
CAMERA_DEADZONE = 5              # pixels – camera ignores tiny movements
CAMERA_ZOOM = 2.0                # >1 zooms in (shows less world, fills screen)

# World dimensions – set at runtime from the loaded map image
WORLD_WIDTH = 1672
WORLD_HEIGHT = 941

# Collision mask – green colour in hospital_map_borders.png
COLLISION_GREEN_THRESHOLD = 80   # min green channel to count as wall
COLLISION_RED_MAX = 100          # max red   channel to count as wall-green
COLLISION_BLUE_MAX = 100         # max blue  channel to count as wall-green

# Fixed timestep is optional; for now we use dt from clock.tick()
# If later we want deterministic physics, add FIXED_DT = 1/60.


# -----------------------------
# Colors (RGB)
# -----------------------------
BG_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)

# Agent colors (placeholder; we’ll formalize states later)
# Agent colors
HEALTHY_COLOR = (80, 200, 120)
# RECOVERED_COLOR is kept for possible future use
RECOVERED_COLOR = (80, 160, 230)

# -----------------------------
# Virus Strains
# -----------------------------
# Each strain has a unique color and infection probability.
STRAINS = {
    0: {
        "name": "Alpha",
        "color": (255, 82, 82),  # Vibrant Red
        "infection_probability": 0.18,
        "initial_infected": 2,
    },
    1: {
        "name": "Beta",
        "color": (0, 210, 255),  # Electric Cyan
        "infection_probability": 0.12,
        "initial_infected": 1,
    },
    2: {
        "name": "Gamma",
        "color": (156, 39, 176), # Vivid Purple
        "infection_probability": 0.25,
        "initial_infected": 1,
    }
}

# The default infected color (legacy/fallback)
INFECTED_COLOR = STRAINS[0]["color"]

# Doctor / UI
DOCTOR_COLOR = (80, 160, 230)
UI_COLOR = (235, 235, 235)          # Light — used on dark menu/overlay panels
HUD_COLOR = (25, 25, 30)            # Dark — used on the light hospital floor


# -----------------------------
# UI / fonts
# -----------------------------
FONT_NAME = None  # None = default pygame font
FONT_SIZE_TITLE = 54
FONT_SIZE_UI = 24
SHOW_FPS = True  # toggle debug fps overlay


# -----------------------------
# Game states
# -----------------------------
MENU = "MENU"
SETTINGS = "SETTINGS"
PLAYING = "PLAYING"
PAUSED = "PAUSED"
WIN_ANIMATION = "WIN_ANIMATION"    # intermediate: doctor plays win anim, agents hidden
LOSE_ANIMATION = "LOSE_ANIMATION"  # intermediate: doctor plays lose anim, agents hidden
WIN = "WIN"
LOSE = "LOSE"

# How long the win/lose animation plays before showing the end-game menu (seconds)
POST_GAME_ANIM_DURATION = 2.5



# -----------------------------
# Simulation parameters (Agents)
# -----------------------------
AGENT_COUNT = 40
AGENT_RADIUS = 8

# Speeds are in pixels per second
AGENT_SPEED_MIN = 20
AGENT_SPEED_MAX = 70

# Random motion / wander (stochastic movement)
WANDER_STRENGTH = 30   # px/s^2-ish feel: higher = more jitter
MAX_SPEED = 100        # hard cap on speed (px/s)
AGENT_TARGET_REACH_DIST = 10  # px – agent picks a new target when within this distance

# Agent-agent collisions
ENABLE_AGENT_COLLISIONS = True

# 0.0 = no bounce response (only separation), 1.0 = perfectly elastic-ish
COLLISION_RESTITUTION = 1.0

# Small amount of extra separation to prevent re-overlap jitter
COLLISION_SLOP = 0.2

# Spawn / overlap
SPAWN_MAX_ATTEMPTS = 6000
SPAWN_PADDING = 1  # extra pixels of spacing between circles

# Infection model (state + colors)
INITIAL_INFECTED = 3
INFECTION_PROBABILITY = 0.18  # p in the proposal

# Statistical Infection Models
# Options: "uniform", "gaussian", "exponential"
INFECTION_MODEL = "uniform"
GAUSSIAN_SIGMA = 0.3      # For "gaussian" model
EXPONENTIAL_SCALE = 1.0  # For "exponential" model

# Lose condition (proposal: > 50% infected for > 2 minutes)
LOSE_THRESHOLD_RATIO = 0.50
LOSE_THRESHOLD_SECONDS = 120.0

# Win condition
WIN_THRESHOLD_RATIO = 0.10      # win if infected ratio stays below 10%
WIN_THRESHOLD_SECONDS = 30.0    # for this many seconds
WIN_CHECK_WARMUP = 10.0         # seconds to wait before checking win condition

# Doctor mechanics (placeholder; later)
CURE_RADIUS = 18
CURE_COOLDOWN = 0.15  # seconds between cures

# Doctor follow smoothing (fixes projectile aim quantization)
DOCTOR_FOLLOW_SPEED = 8.0   # lower = smoother camera-friendly movement (was 25)
DOCTOR_MAX_SPEED = 260       # px/s hard cap so doctor can't teleport across map


# -----------------------------
# Vaccine pellets (projectiles)
# -----------------------------
PELLET_SPEED = 520          # px/s
PELLET_RADIUS = 4           # pixels
PELLET_LIFETIME = 1.2       # seconds before despawn

PELLET_COOLDOWN = 0.15      # seconds between shots
PELLET_AMMO_MAX = 16        # max ammo
PELLET_RELOAD_TIME = 2.0    # seconds to reload back to full (simple reload)



# -----------------------------
# HUD / telemetry
# -----------------------------
SHOW_HUD = True              # initial HUD visibility
HUD_TOGGLE_KEY = "F1"        # doc note only; actual key handled in game.py

# Infection curve overlay (last N seconds)
HISTORY_SECONDS = 120.0      # how many seconds of history to keep
HISTORY_SAMPLE_DT = 0.25     # sample infected_ratio every 0.25s

# Graph placement (x, y, width, height)
GRAPH_RECT = (540, 10, 250, 90)

# Logo settings
LOGO_TARGET_WIDTH = 550  # Significantly bigger logo for main menu



# -----------------------------
# Difficulty scaling
# -----------------------------
DIFFICULTY_ENABLED = True               # Toggle difficulty scaling on/off
DIFFICULTY_START_MULTIPLIER = 1.0       # Initial speed multiplier (1.0 = normal speed)
DIFFICULTY_MAX_MULTIPLIER = 2.5         # Maximum speed multiplier
DIFFICULTY_RAMP_TIME = 180.0            # Time in seconds to reach max difficulty (3 minutes)
DIFFICULTY_CURVE_TYPE = "sigmoid"       # Curve shape: "linear", "exponential", or "sigmoid"
DIFFICULTY_CURVE_STEEPNESS = 0.5        # Controls curve aggressiveness (0.1 = gentle, 1.0 = steep)


# -----------------------------
# Doctor animation
# -----------------------------
DOCTOR_ANIM_FPS = 12                    # frames per second for doctor animations
DOCTOR_SPRITE_SCALE = 1.2              # default fallback scale (smaller for zoomed map)

# Per-animation scale overrides (tweak these to balance visual sizes)
DOCTOR_ANIMATION_SCALES = {
    "standing":  1.2,
    "running":   1.2,
    "shooting":  1.6,
    "injecting": 1.6,
    "win":       1.6,
    "lose":      1.6,
}

# Spritesheet frame rects  (x, y, w, h) – auto-detected from transparent gaps
DOCTOR_FRAMES = {
    "standing": [
        (25, 0, 34, 45),
        (61, 0, 33, 45),
        (100, 0, 33, 45),
        (138, 0, 34, 45),
    ],
    "running": [
        (1, 0, 36, 45),
        (40, 0, 37, 45),
        (80, 0, 38, 45),
        (122, 0, 37, 45),
        (162, 0, 35, 45),
    ],
    "shooting": [
        (1, 0, 19, 45),
        (22, 0, 19, 45),
        (42, 0, 19, 45),
        (64, 0, 19, 45),
        (84, 0, 22, 45),
        (111, 0, 33, 45),
        (147, 0, 22, 45),
        (172, 0, 24, 45),
    ],
    "injecting": [
        (0, 0, 36, 45),
        (38, 0, 43, 45),
        (83, 0, 46, 45),
        (131, 0, 35, 45),
        (171, 0, 23, 45),
    ],
    "win": [
        (2, 0, 36, 52),
        (42, 0, 36, 52),
        (82, 0, 36, 52),
    ],
    "lose": [
        (0, 0, 30, 51),
        (35, 0, 29, 51),
        (70, 0, 29, 51),
    ],
}

# Bullet sprite rect inside bullet_transparent_bg.png
DOCTOR_BULLET_RECT = (76, 0, 45, 45)

# Shooting: spawn projectile when this frame index is reached (0-based)
DOCTOR_SHOOT_FIRE_FRAME = 5


# -----------------------------
# Agent animation
# -----------------------------
AGENT_ANIM_FPS = 10                     # walk cycle speed for agents
AGENT_SPRITE_SCALE = 3.0               # scale factor for agent sprites (smaller for zoomed map)

# Spritesheet frame rects  (x, y, w, h) – auto-detected from transparent gaps
AGENT_FRAMES = {
    "healthy": [
        (2, 0, 9, 45),
        (22, 0, 9, 45),
        (42, 0, 7, 45),
        (58, 0, 11, 45),
        (78, 0, 7, 45),
        (94, 0, 11, 45),
        (115, 0, 10, 45),
        (135, 0, 11, 45),
        (155, 0, 7, 45),
        (169, 0, 10, 45),
        (187, 0, 8, 45),
    ],
    "infected1": [
        (3, 0, 9, 45),
        (21, 0, 9, 45),
        (37, 0, 10, 45),
        (55, 0, 9, 45),
        (70, 0, 10, 45),
        (86, 0, 10, 45),
        (103, 0, 10, 45),
        (120, 0, 10, 45),
        (136, 0, 9, 45),
        (152, 0, 9, 45),
        (169, 0, 9, 45),
        (186, 0, 9, 45),
    ],
    "infected2": [
        (2, 0, 10, 45),
        (20, 0, 10, 45),
        (37, 0, 10, 45),
        (54, 0, 9, 45),
        (69, 0, 10, 45),
        (86, 0, 10, 45),
        (102, 0, 11, 45),
        (119, 0, 10, 45),
        (136, 0, 9, 45),
        (151, 0, 9, 45),
        (169, 0, 8, 45),
        (186, 0, 8, 45),
    ],
    "infected3": [
        (2, 0, 11, 45),
        (19, 0, 12, 45),
        (37, 0, 11, 45),
        (53, 0, 11, 45),
        (69, 0, 11, 45),
        (85, 0, 11, 45),
        (102, 0, 10, 45),
        (118, 0, 10, 45),
        (135, 0, 8, 45),
        (149, 0, 10, 45),
        (166, 0, 11, 45),
        (184, 0, 11, 45),
    ],
}

# Maps strain_id (0, 1, 2) to the key in AGENT_FRAMES
STRAIN_TO_ANIM_KEY = {
    0: "infected1",
    1: "infected2",
    2: "infected3",
}