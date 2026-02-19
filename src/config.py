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

# Fixed timestep is optional; for now we use dt from clock.tick()
# If later we want deterministic physics, add FIXED_DT = 1/60.


# -----------------------------
# Colors (RGB)
# -----------------------------
BG_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)

# Agent colors (placeholder; we’ll formalize states later)
HEALTHY_COLOR = (80, 200, 120)
INFECTED_COLOR = (230, 80, 80)
RECOVERED_COLOR = (80, 160, 230)

# Doctor / UI
DOCTOR_COLOR = (80, 160, 230)
UI_COLOR = (235, 235, 235)


# -----------------------------
# UI / fonts
# -----------------------------
FONT_NAME = None  # None = default pygame font
FONT_SIZE_TITLE = 48
FONT_SIZE_UI = 20
SHOW_FPS = True  # toggle debug fps overlay


# -----------------------------
# Game states
# -----------------------------
MENU = "MENU"
SETTINGS = "SETTINGS"
PLAYING = "PLAYING"
PAUSED = "PAUSED"
WIN = "WIN"
LOSE = "LOSE"



# -----------------------------
# Simulation parameters (Agents)
# -----------------------------
AGENT_COUNT = 150
AGENT_RADIUS = 6

# Speeds are in pixels per second
AGENT_SPEED_MIN = 40
AGENT_SPEED_MAX = 140

# Random motion / wander (stochastic movement)
WANDER_STRENGTH = 60   # px/s^2-ish feel: higher = more jitter
MAX_SPEED = 170        # hard cap on speed (px/s)

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

# Lose condition (proposal: > 50% infected for > 2 minutes)
LOSE_THRESHOLD_RATIO = 0.50
LOSE_THRESHOLD_SECONDS = 120.0

# Win condition
WIN_THRESHOLD_RATIO = 0.10      # win if infected ratio stays below 10%
WIN_THRESHOLD_SECONDS = 30.0    # for this many seconds
WIN_CHECK_WARMUP = 10.0         # seconds to wait before checking win condition

# Doctor mechanics (placeholder; later)
CURE_RADIUS = 24
CURE_COOLDOWN = 0.15  # seconds between cures

# Doctor follow smoothing (fixes projectile aim quantization)
DOCTOR_FOLLOW_SPEED = 25.0  # higher = follows cursor more tightly (try 20–45)


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



# -----------------------------
# Difficulty scaling
# -----------------------------
DIFFICULTY_ENABLED = True               # Toggle difficulty scaling on/off
DIFFICULTY_START_MULTIPLIER = 1.0       # Initial speed multiplier (1.0 = normal speed)
DIFFICULTY_MAX_MULTIPLIER = 2.5         # Maximum speed multiplier
DIFFICULTY_RAMP_TIME = 180.0            # Time in seconds to reach max difficulty (3 minutes)
DIFFICULTY_CURVE_TYPE = "sigmoid"       # Curve shape: "linear", "exponential", or "sigmoid"
DIFFICULTY_CURVE_STEEPNESS = 0.5        # Controls curve aggressiveness (0.1 = gentle, 1.0 = steep)