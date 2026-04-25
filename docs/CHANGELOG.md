# Changelog
All notable changes to this project will be documented here.

## v0.34 — Agent Animation Sprites
### Added
- **Agent Animation Sprites**: Added animation sprites for healthy agents and infected agents (three strains) using spritesheets.

### Changed
- **Agent Drawing**: Agents are now drawn using animation frames instead of simple colored circles.
- **Agent Sprite Scale**: Increased agent sprite scale factor from 2.2 to 3.2 for better visibility.

## v0.33 — Map & UI polish
### Added
- **Map**: Added a hospital floor background image to the game.

### Changed
- **Background**: Changed the background color of the game to a light gray to improve contrast against the new background.
- **HUD**: Changed the color of the HUD and Infection Curve to a dark gray to improve contrast against the new background.
- **UI**: Added a semi-transparent backing panel to the HUD and Infection Curve to improve readability.

## v0.32 — Animation Bug Fixes & Post-Game Sequence
### Added
- **Per-Animation Scaling**: Each animation state now has its own scale factor (`DOCTOR_ANIMATION_SCALES` in config) to balance visual sizes between idle/running and shooting/injecting sprites.
- **Post-Game Animation Sequence**: Win/Lose conditions now transition to a dedicated animation state where all agents are cleared and only the doctor is shown for 2.5 seconds before the end-game menu appears.

### Fixed
- Doctor animation getting stuck on the last frame of injecting or shooting (state never transitioned back to idle).
- Idle animation not cycling through its frames.
- Running animation not triggering when moving the mouse.
- Unable to shoot or inject after the first shot action.
- Win/Lose sprite persisting on screen after game restart.

## v0.31 — Doctor Agent Sprite Animations
### Added
- **Animated Doctor Sprite**: Replaced the primitive blue cross with a fully animated character sprite.
  - **Standing (Idle)**: 4-frame looping breathing/idle animation.
  - **Running**: 5-frame animation with distinct start, loop (frames 1–3), and end transitions triggered by mouse movement.
  - **Shooting**: 8-frame single-action animation; vaccine pellet spawns precisely at frame 6 for visual sync.
  - **Injecting (Cure)**: 5-frame single-action animation triggered on successful left-click cure.
  - **Win / Lose**: 3-frame animations triggered at end-of-game.
- **Bullet Sprite**: Projectiles now render using `bullet_transparent_bg.png` instead of a plain circle.
- **Doctor State Machine**: Introduced `AnimState` (IDLE, RUNNING, SHOOTING, INJECTING, WIN, LOSE) with priority-based transitions and frame-accurate action synchronization.

### Changed
- **Projectile Class**: Added optional `sprite` field to `Projectile` dataclass; `draw()` blits sprite when available, falls back to circle otherwise.

## v0.30 — UI Enhancements & Modern Pause Menu
### Added
- **Modern Pause Menu ('S' Key)**: Pressing 'S' now triggers a feature-rich pause overlay.
  - **Dynamic Background Blur**: Captures and blurs the game world in real-time.
  - **Comprehensive Statistics**: Displays elapsed time, healthy/infected counts, and current speed multipliers.
  - **Enlarged Infection Graph**: Shows the detailed infection trend lines for all strains.
  - **Simulation Insights**: Provides a clean explanation of the current infection model's logic (Uniform, Gaussian, or Exponential).
  - **Strain Legend**: Added a color-coded legend to clarify which color represents which virus strain (Alpha/Beta/Gamma).
- **Branding Refresh**: Significantly increased the main menu logo size for a more premium first impression.
  - **Dynamic Layout**: Implemented a responsive panel system for the main menu that automatically scales to prevent logo/text overflow.

### Changed
- **Pause Logic**: Both 'Esc' and 'S' can now be used to toggle the pause state.
- **HUD Consistency**: Statistics in the pause menu remain consistent with the live HUD.

## v0.29 — Statistical Infection Models
### Added
- **Statistical Infection Models**: Added support for three infection probability models:
  - **Uniform**: Every agent has the same susceptibility (1.0).
  - **Gaussian (Normal)**: Agent susceptibility follows a Normal distribution.
  - **Exponential**: Agent susceptibility follows an Exponential distribution (vulnerable clusters).
- **Runtime Model Selection**: Players can switch between infection models in the settings menu.
- **Susceptibility Mechanics**: Contact infection probability is now weighted by the individual agent's susceptibility.

### Changed
- **Virus Sprite Scaling**: Reduced virus sprite size (2.2x multiplier) to match visual parity with healthy agents and the Doctor's hitboxes.
- **Settings Menu**: Expanded with an "Infection Model" option.

## v0.28 — Multiple Virus Strains
### Added
- **Multi-Strain System**: Support for multiple virus strains (Alpha, Beta, Gamma) with unique properties.
- **Per-Strain Infection Probabilities**: Strains can spread at different rates (e.g., Alpha: 18%, Beta: 12%, Gamma: 25%).
- **Visual Distinction**: Each strain has a unique color (Red, Orange, Purple) displayed as a glow/ring under the virus sprite.
- **Strain Telemetry**: HUD now tracks and displays the count of agents infected with each specific strain.
- **Advanced Infection Graph**: The infection curve graph now displays multiple lines—one for each strain (colored) and a thicker white line for total infection percentage.

### Changed
- **Agent Data Model**: Updated `Agent` state from a boolean `infected` flag to a nullable `strain_id`.
- **Infection Logic**: Contact-based infection now transfers the specific strain of the donor to the recipient.
- **Spawning Logic**: Agents are now initialized with multiple patient-zeros across different strains based on configuration.

## v0.27 — Fast-forward mode and Virus sprites
### Added
- **Fast-Forward Mechanic**: Simulation can now be speeded up using keys **1** (1x), **2** (2x), and **3** (4x).
- **Simulation Speed Display**: Added "Sim Speed" telemetry to the HUD to show the current time scale.
- **Virus & Healthy Circle Sprite Rendering**: Infected agents and healthy agents are now rendered using a high-quality `virus.png` sprite and `healthy.png` sprite instead of simple red and green circles.

### Changed
- **Sprite Scaling Refinement**: Adjusted virus sprite dimensions (4x radius) to compensate for asset padding, ensuring visual parity with healthy dots.
- **HUD Layout Updates**: Added new telemetry lines for simulation speed and difficulty.

### Fixed / Notes
- Time scaling correctly affects all aspects of the simulation, including infection spread rate and win/loss timers.

## v0.26 — Fullscreen mode and gameplay balance tuning
### Added
- **Fullscreen Mode**: The game now launches in native resolution fullscreen by default.
- **Dynamic Resolution Tracking**: `config.WIDTH` and `config.HEIGHT` are updated automatically at runtime to match the display.
- **Win-condition Warmup**: Added a 10-second "warmup" period before the win condition can trigger, preventing instant wins at game start.
- **Dynamic UI Scaling**: HUD elements and the Infection Curve graph now reposition themselves relative to the screen edges regardless of resolution.

### Changed
- **Balanced Infection Spread**: Reduced `INFECTION_PROBABILITY` from 0.25 to 0.18 to prevent rapid "instant doom" scenarios.
- **Pellet Buffs**: Increased maximum ammo tray size to 16 and reduced reload time to 2.0s for better player agency.
- **Menu Background Handling**: Implemented aspect-correct cropping for the menu background image to cover any screen size without distortion.

### Fixed / Notes
- Verified that all physics and boundaries scale correctly with fullscreen dimensions.

## v0.25 — Global difficulty scaling + in-game settings menu
### Added
- **Global difficulty scaling system**: Agent speed now increases over time based on a configurable curve.
  - Difficulty multiplier ramps from 1.0x to a configurable maximum (default: 2.5x) over a set time period (default: 3 minutes).
  - Three curve types supported: linear, exponential, and sigmoid (default: sigmoid for smooth progression).
  - Difficulty multiplier displayed in HUD when enabled.
  - All parameters configurable via `config.py` or the new settings menu.
- **In-game settings menu**: Fully interactive settings menu accessible from the main menu.
  - Adjust difficulty parameters: enable/disable scaling, max multiplier, ramp time, curve type, and steepness.
  - Adjust game parameters: agent count, infection probability, and initial infected count.
  - Real-time value updates with visual feedback.
  - Navigate with Up/Down, adjust with Left/Right arrow keys.
  - Apply changes or cancel back to menu.

### Changed
- Main menu now includes "Settings" option between "Start" and "Quit".
- Agent movement system updated to accept and apply difficulty multiplier to speed and acceleration.
- Difficulty calculation performed each frame based on elapsed time and selected curve type.

### Fixed / Notes
- Settings are applied to the config module when "Apply & Back" is selected, allowing changes to take effect on the next game start.
- Difficulty scaling can be toggled on/off via settings menu without editing config files.
- Provides players with easy access to customize game difficulty and parameters for different skill levels.

## v0.24 — Menu interaction improvements (keyboard + mouse support)
### Added
- Full keyboard navigation support for WIN/LOSE end screens (↑/↓ + Enter).
- Mouse hover highlighting for menu options (main menu, pause menu, end screens).
- Mouse click selection for menu options (left-click triggers selection).

### Changed
- Unified menu selection logic so both keyboard (Enter) and mouse clicks use the same execution path.
- `draw_menu()` now returns clickable option rectangles to enable proper mouse interaction.

### Fixed / Notes
- Fixed inability to navigate end-screen menus using arrow keys.
- Fixed lack of mouse interaction on menu screens.
- No gameplay logic changed; this update improves UI usability and consistency only.

## v0.23 — Menu system implementation and UI rendering cleanup
### Added
- Main menu system (Start / Quit).
- Pause menu (Resume / Restart / Quit to Menu).
- End screens (WIN / LOSE) with restart and navigation options.
- Restart functionality to reset simulation state without restarting the program.

### Changed
- Rendering pipeline reorganized to be fully state-driven (MENU, PLAYING, PAUSED, WIN, LOSE).
- Simulation elements (agents, doctor, HUD, projectiles) no longer render behind the main menu.
- End screens now use the unified menu overlay system instead of legacy center-message overlays.

### Fixed / Notes
- Removed duplicate "YOU WIN" overlay caused by overlapping rendering paths.
- Improved visual clarity of start and end screens without altering gameplay logic.
- Future refinement planned: separate Core HUD (essential gameplay info) from Debug Overlay (FPS, infection graph) with independent toggles.

## v0.22 — HUD and infection telemetry
### Added
- Basic in-game HUD displaying simulation state (infected count, healthy count, infected percentage).
- Total elapsed time display.
- Pellet status indicators (ammo count, reload timer, shot cooldown).
- Infection ratio history tracking with a simple line-graph overlay.
- HUD/debug visibility toggle (F1).

### Changed
- Game loop now records and samples infection statistics over time for visualization purposes.
- UI responsibilities expanded to include telemetry rendering alongside existing overlays.

### Fixed / Notes
- HUD is functional and accurate but intentionally minimal in layout and styling.
- Visual polish, layout refinement, and UI grouping are deferred to later UX/menu work.

## v0.21 — Continuous projectile aiming bugfix
### Added
- Smoothed Doctor cursor-follow behavior to ensure a non-zero aiming vector during shooting.

### Changed
- Projectile aim direction is now derived from the continuous vector between the Doctor and the cursor rather than discrete mouse movement deltas.
- Doctor aim direction is updated internally each frame, removing dependence on `MOUSEMOTION` event deltas.

### Fixed / Notes
- Fixed an issue where projectile aiming collapsed into a limited set of discrete directions (axis-aligned or diagonal) when the Doctor overlapped the cursor.
- Ranged curing now supports full 360° aiming as intended.

## v0.20 — Projectile aiming correctness fixes
### Added
- Persistent aim-direction tracking for the Doctor to allow shooting even when the mouse is stationary.

### Changed
- Vaccine pellets now spawn slightly in front of the Doctor (muzzle offset) instead of directly at the cursor position.
- Projectile direction selection now falls back to the last valid aim direction when the cursor does not move.

### Fixed / Notes
- Fixed an issue where right-click shooting failed if the mouse was not moving.
- Improved clarity and usability of ranged curing without changing balance parameters.
- **Known issue:** When the Doctor is exactly on the cursor, projectile aiming may collapse to a limited set of discrete directions (axis-aligned or diagonal). This is a correctness issue related to input geometry and is planned to be fixed later (e.g., via smoothed doctor follow or alternative aiming logic).

## v0.19 — Vaccine pellets (projectiles) baseline implementation
### Added
- New projectile system for ranged curing (vaccine pellets).
- Right-click firing mechanic integrated with Doctor controls.
- Projectile lifecycle handling (speed, radius, lifetime/despawn) and on-hit curing for infected agents.

### Changed
- Game update loop now updates and renders active projectiles each frame.
- Input handling extended to include right-click shooting alongside left-click curing.

### Fixed / Notes
- Known issues / polish pending:
  - Shooting direction can fail when the doctor is exactly on the cursor (zero-length aim vector).
  - Pellets currently spawn at the cursor/doctor position, making feedback feel unclear.
  - Ranged curing feels underpowered with current agent density and hitbox size; tuning/polish planned (ammo, pellet radius, pierce/AoE).

## v0.18 — Doctor mechanics (cursor-follow + click-to-cure)
### Added
- New `src/doctor.py` module implementing the Doctor entity.
- Doctor cross that follows the mouse cursor and displays a cure-radius ring.
- Click-to-cure mechanic: left-click cures the nearest infected agent within `CURE_RADIUS`.
- Cure cooldown system using `CURE_COOLDOWN` to limit cure spam.

### Changed
- Game loop now updates and draws the Doctor each frame (while `PLAYING`).
- Event handling updated to support mouse input for curing infected agents.
- Project structure extended to keep player interaction logic out of the main game/simulation modules.

### Fixed / Notes
- Gameplay balance is not finalized yet:
  - Early-game “instant win by curing patient zero” is still possible under current win rules.
  - Late-game difficulty may be too high when infection rate grows (tuning/fixes pending).

## v0.17 — Codebase refactor (game + UI modules)
### Added
- New `src/game.py` module containing the `Game` class (loop, state handling, update/draw pipeline).
- New `src/ui.py` module for rendering helpers (`draw_fps`, `draw_stats`, `draw_center_message`).

### Changed
- `src/main.py` simplified into a minimal entrypoint that only starts `Game().run()`.
- UI drawing logic moved out of the Game loop file to keep orchestration code cleaner and easier to extend.

### Fixed / Notes
- No gameplay/simulation behavior changes intended; this update is an organizational refactor to support upcoming features (menus, doctor, projectiles, HUD).

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

## v0.1 – Initial Setup + Foundation
- Project structure created
- Pygame window + game loop
- Config system added
