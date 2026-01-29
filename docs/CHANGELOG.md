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