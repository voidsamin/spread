# Changelog
All notable changes to this project will be documented here.

## v0.1 – Initial Setup + Foundation
- Project structure created
- Pygame window + game loop
- Config system added

## v0.12 — Foundation + Agents module
### Added
- Centralized configuration via `src/config.py` (window settings, colors, simulation constants).
- Agent system implemented:
  - `Agent` data model (position, velocity, radius, infected state)
  - Random spawn for N agents with minimal overlap tolerance
  - Wall/boundary bounce
  - State-based rendering (healthy vs infected)
- New module `src/agents.py` to keep `main.py` cleaner.

### Changed
- Refactored main loop into a clean Game structure using dt timing (`dt = clock.tick(FPS)/1000`).
- `src/main.py` now imports agent spawning logic instead of containing all agent code.
- Removed placeholder title rendering (temporary splash text) from the runtime view.

### Fixed / Notes
- Repo hygiene: documentation updated to reflect new structure and run instructions.

## v0.13 — Stochastic agent motion
### Added
- Stochastic “wander” motion for agents using small random velocity perturbations.
- Velocity clamping to enforce a maximum agent speed and prevent runaway acceleration.
- Configurable randomness parameters (`WANDER_STRENGTH`, `MAX_SPEED`) centralized in `config.py`.

### Changed
- Agent movement updated from straight-line motion to smooth, continuously varying trajectories.
- Agent update logic refactored to incorporate dt-scaled random acceleration for frame-rate–independent behavior.

### Fixed / Notes
- Movement behavior now appears more natural and less deterministic.
- Global difficulty-based speed scaling is not yet implemented (planned for a later version).

## v0.14 — Agent-agent collisions
### Added
- Agent–agent circle collision detection (contact/overlap check using radii).
- Collision resolution via positional separation to prevent overlap/sticking.
- Optional elastic collision response (velocity impulse) controlled by `COLLISION_RESTITUTION` in `config.py`.

### Changed
- Agent update loop now includes a collision-resolution pass each frame (after movement + wall bounce).
- Collision tuning parameters added to `config.py` (enable toggle + restitution + slop).

### Fixed / Notes
- Set `COLLISION_RESTITUTION = 1.0` to avoid gradual slow-down after many collisions.
- Current implementation is O(N²); spatial partitioning (uniform grid) is deferred until higher agent counts are needed.

## v0.15 — Initial infection model
### Added
- Patient-zero initialization: a random subset of agents start infected (`INITIAL_INFECTED`).
- Probabilistic infection spread on agent contact/collision using `INFECTION_PROBABILITY`.
- Per-frame infection statistics tracking: `infected_count`, `healthy_count`, and `infected_ratio`.
- Threshold timer tracking for the lose condition: accumulates `time_above_threshold` when infected ratio exceeds `LOSE_THRESHOLD_RATIO`.

### Changes
- Collision handling now also triggers infection checks when agents make contact.
- Game update loop now computes and stores infection metrics every frame.

### Fixed / Notes
- Incubation and natural recovery timers are not implemented yet (deferred).
- Lose condition is only tracked (no win/lose screen yet).

## v0.16 — Win/Lose conditions and game states
### Added
- Formal game state system (`MENU`, `PLAYING`, `PAUSED`, `WIN`, `LOSE`) centralized in `config.py`.
- Lose condition enforcement: game transitions to LOSE if infected ratio stays above threshold for the configured duration.
- Win condition enforcement: game transitions to WIN if infected ratio stays below threshold for the configured duration.
- Pause functionality (`P` key) to toggle between PLAYING and PAUSED states.

### Changed
- Game update loop now advances simulation **only** in the `PLAYING` state.
- Infection threshold timers are frozen automatically when the game is paused or finished.
- Placeholder survival-based win condition removed in favor of ratio-based containment logic.

### Fixed / Notes
- Simulation now cleanly freezes on WIN or LOSE states (no background updates).
- Menu state is defined but not yet implemented visually (planned for a later version).
