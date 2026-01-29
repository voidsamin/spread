"""Central configuration for SPREAD.

Keep *all tunable constants* here so gameplay/simulation parameters
can be changed without hunting through code.

Rule of thumb:
- Anything you'd want to tweak (sizes, speeds, probabilities, timers) goes here.
- Code logic stays in other modules.
"""

from __future__ import annotations

# -----------------------------
# Window / timing
# -----------------------------
TITLE = "SPREAD - Simulation Lab"
WIDTH, HEIGHT = 800, 600
FPS = 60

# Fixed timestep is optional; for now we use dt from clock.tick()
# If later you want deterministic physics, add FIXED_DT = 1/60.

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
# Simulation parameters (we'll use these in upcoming steps)
# -----------------------------
AGENT_COUNT = 150
AGENT_RADIUS = 6

# Speeds are in pixels per second
AGENT_SPEED_MIN = 40
AGENT_SPEED_MAX = 140

# Random motion / noise
# Amount of velocity change (px/s) applied per second (scaled by dt)
WANDER_STRENGTH = 60
MAX_SPEED = 170

# Infection model
INITIAL_INFECTED = 3
INFECTION_PROBABILITY = 0.25  # p in the proposal

# Lose condition (proposal: > 50% infected for > 2 minutes)
LOSE_THRESHOLD_RATIO = 0.50
LOSE_THRESHOLD_SECONDS = 120.0

# Win condition (placeholder; we'll define properly later)
WIN_SURVIVE_SECONDS = 180.0  # survive 3 minutes

# Doctor mechanics (placeholder; later)
CURE_RADIUS = 24
CURE_COOLDOWN = 0.15  # seconds between cures
