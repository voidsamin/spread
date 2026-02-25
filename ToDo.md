# SPREAD — To-Do List (Build Plan)

This is the step-by-step build checklist for **SPREAD** (agent-based disease transmission arcade sim) as described in the project proposal.
See the [Project Proposal](docs/Simulation%20Lab%20Project%20Proposal.pdf).

> **Legend:**  
> - [ ] Not started task
> - [x] Done task
> - ⏳ Ongoing task
> - (★) = must-have for MVP  
> - (☆) = nice-to-have / polish  

---

## 0) Project hygiene (once)
- [x] (★) Confirm repo structure is final: `assets/`, `docs/`, `src/`
- [x] (★) Add `requirements.txt` (at least `pygame`)
- [x] (★) Decide constants + config pattern (e.g., `src/config.py`)
- [x] (★) Add a basic run command to README (`python src/main.py`)
- [x] (☆) Create a simple `docs/CHANGELOG.md` (optional but helpful)

---

## 1) Foundation: window, loop, timing (Week 1)
- [x] (★) Replace “Hello SPREAD” with a minimal game framework:
  - [x] Game class (init, handle_events, update, draw)
  - [x] Delta-time (dt) based movement
  - [x] FPS cap + on-screen FPS counter (debug)
- [x] (★) Implement a simple camera-less 2D world (screen == world)

Deliverable: A clean blank scene with a stable loop and debug overlay.

---

## 2) Agents: data model + rendering (Week 1)
- [x] (★) Create an `Agent` class:
  - [x] Position (x, y)
  - [x] Velocity (vx, vy)
  - [x] Radius
  - [x] State: Healthy / Infected / (optional) Recovered
- [x] (★) Spawn N agents randomly without overlap (or minimal overlap tolerance)
- [x] (★) Draw agents as circles with state-based colors
- [x] (★) Implement boundary collisions (bounce off walls)

Deliverable: 100+ moving dots bouncing in the window.

---

## 3) Stochastic motion (randomness) (Week 1)
- [x] (★) Add random/noisy velocity updates (random-walk / jitter)
  - [x] Small noise applied every few frames or based on dt
  - [x] Clamp max speed
- [x] (☆) Add “wander” behavior (smooth direction change) to reduce twitchiness

Deliverable: Agents move unpredictably but controllably.

---

## 4) Collisions: agent-agent contact detection (Week 2)
- [x] (★) Implement circle-circle collision detection
- [x] (★) Resolve overlaps (simple separation) to avoid sticking
- [x] (☆) Add elastic collision response (swap velocity components) for nicer physics
- [ ] (☆) Optimization prep: spatial partitioning (uniform grid) if needed

Deliverable: Dots collide and don’t phase through each other.

---

## 5) Infection model: patient zero + probabilistic spread (Week 2)
- [x] (★) Randomly select initial infected agents (patient zero count)
- [x] (★) On collision between infected & healthy, infect with probability `p`
- [x] (★) Track stats each frame:
  - [x] infected_count, healthy_count, infected_ratio
  - [x] time_above_threshold (for lose condition)
- [ ] (☆) Add incubation timer (infected but not infectious) (optional)
- [ ] (☆) Add recovery timer (natural recovery) (optional; proposal emphasizes cure via player)

Deliverable: Infection spreads stochastically across collisions.

---

## 6) Win/Lose rules + stopwatch (Week 2)
From proposal:
- **Lose** if infection rate exceeds **50%** for over **2 minutes**.

- [x] (★) Implement threshold logic:
  - [x] When infected_ratio > 0.5, accumulate `time_above_50`
  - [x] If drops back <= 0.5, reset timer or decay timer
- [x] (★) Define win condition:
  - [x] Survive for X total minutes OR cure to below Y% for Z seconds (pick one)
- [x] (★) Implement game states: MENU, PLAYING, PAUSED, WIN, LOSE

Deliverable: You can “lose” correctly; “win” condition exists.

---

## 7) The Doctor: cursor-follow + click-to-cure (Week 3)
- [x] (★) Draw the doctor as a blue cross that follows mouse position
- [x] (★) Click-to-cure mechanic:
  - [x] On click, find nearest infected within a cure radius
  - [x] Set infected → healthy (or recovered)
  - [x] Add cooldown to prevent spam (optional)
- [ ] (☆) Add curing effect (pulse ring / particles)

Deliverable: Player can actively reduce infections.

---

## 8) Vaccine pellets: ranged curing (Week 4)
- [x] (★) Implement projectile class:
  - [x] Spawn from doctor toward mouse direction on right click / key
  - [x] Projectile speed, lifetime, radius
- [x] (★) Projectile hits infected agent → cures it
- [x] (★) Ammo / cooldown balancing
- [x] (☆) Improve projectile aiming geometry (continuous angles when doctor overlaps cursor)
- [ ] (☆) Add ricochet or piercing shots (advanced/polish)

Deliverable: Ranged curing works and feels responsive.

---

## 9) HUD + in-game telemetry (Week 5)
- [x] (★) HUD elements:
  - [x] Infected %
  - [x] Healthy count
  - [x] Timer above 50%
  - [x] Total elapsed time
  - [x] Pellet cooldown/ammo
- [x] (★) Infection curve overlay (simple):
  - [x] Keep a time series buffer (e.g., last 120s)
  - [x] Draw as a line graph in a corner
- [x] (☆) Toggle debug UI (F1)
- [ ] (☆) Polish HUD layout and visual grouping

Deliverable: The player understands the system state at all times.

---

## 10) Menus, UX, and feedback (Week 5)
- [x] (★) Main menu: Start / Quit
- [x] (★) End screens: Win / Lose + restart
- [x] (★) Pause menu (Esc)
- [x] (★) Restart game from WIN / LOSE state
- [x] (☆) Settings screen (agent count, infection probability p, speed)

Deliverable: A playable loop from menu → play → end → restart.

---

## 11) Audio + assets (Week 5)
- [ ] (☆) Add click cure sound
- [ ] (☆) Add pellet shoot sound
- [ ] (☆) Add subtle background loop
- [ ] (☆) Add hit/impact sound for collisions (careful: can get noisy)
- [x] (☆) Add simple sprites (optional; circles are fine for MVP)

Deliverable: Basic audio feedback improves feel.

---

## 12) Difficulty tuning + balance (Week 6)
- [x] (★) Implement global difficulty scaling over time (speed multiplier/curve)
- [x] (★) Tune difficulty curve parameters (how fast it ramps up)
- [x] (★) Tune infection probability `p`
- [x] (★) Tune pellet cooldown/ammo
- [x] (★) Ensure loss condition is fair (not instant doom)
- [x] (★) Prevent instant-win at game start (e.g., win-check warmup)
- [ ] (☆) Add infection re-seeding when infected count reaches zero (difficulty-dependent)
- [ ] (☆) Add difficulty levels (Easy/Normal/Hard)

Deliverable: “Containment” is challenging but possible.

---

## 13) Simulation Extensions

- [ ] (★) Multiple virus strains
  - [ ] Different infection probabilities per strain
  - [ ] Different colors per strain
  - [ ] Optional: different incubation/recovery behaviors per strain
  - [ ] Track per-strain infection statistics

- [ ] (★) Statistical modeling features
  - [ ] Support different infection probability models:
    - [ ] Uniform probability (current)
    - [ ] Gaussian / Normal distribution
    - [ ] Exponential distribution
  - [ ] Compare spread dynamics between distributions

- [ ] (★) Advanced graphing / analytics
  - [ ] Per-strain infection curves
  - [ ] Overlay multiple curves on the same graph
  - [ ] Histogram of infection durations (optional)
  - [ ] Display reproduction number (R₀ approximation)

- [ ] (☆) Simulation mode toggle (Game Mode vs Simulation Mode)

Deliverable: The project demonstrates clear computational modeling and statistical simulation concepts beyond arcade mechanics.

---

## 14) Performance + polish (Week 6)
- [ ] (★) Profile with high agent counts (e.g., 500, 1000)
- [ ] (★) Add spatial hashing/grid if collisions become slow
- [ ] (☆) Add screen shake or subtle FX
- [ ] (☆) Add smooth trails or motion blur (optional)
- [ ] (★) Bug fixes + edge cases (stuck agents, runaway speeds, etc.)

Deliverable: Smooth performance and stable gameplay.

---

## 15) Documentation + final submission
- [ ] (★) Update README with:
  - [ ] How to run
  - [ ] Controls
  - [ ] Rules (win/lose)
  - [ ] Parameters (N, p, speed)
- [ ] (★) Add short report in `docs/`:
  - [ ] Model description (agents, contact rule, p)
  - [ ] Randomness explanation
  - [ ] Metrics collected
- [ ] (☆) Add screenshots / GIFs to docs

Deliverable: Clear documentation and reproducible results.

---

## Suggested implementation order
1. Game skeleton + dt loop  
2. Agent class + spawn + wall bounce  
3. Stochastic motion  
4. Collision detection  
5. Infection probability + tracking  
6. Doctor cross + click cure  
7. Win/lose states + HUD  
8. Pellets + infection graph  
9. Menu + polish  
