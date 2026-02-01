# SPREAD — To-Do List (Build Plan)

This is the step-by-step build checklist for **SPREAD** (agent-based disease transmission arcade sim) as described in the project proposal. fileciteturn0file0

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

Deliverable: A clean blank scene with a stable loop and debug overlay. fileciteturn0file1

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
- [ ] (★) Add a global difficulty parameter for speed scaling over time
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
- **Lose** if infection rate exceeds **50%** for over **2 minutes**. fileciteturn0file0

- [x] (★) Implement threshold logic:
  - [x] When infected_ratio > 0.5, accumulate `time_above_50`
  - [x] If drops back <= 0.5, reset timer or decay timer
- [x] (★) Define win condition:
  - [x] Survive for X total minutes OR cure to below Y% for Z seconds (pick one)
- [x] (★) Implement game states: MENU, PLAYING, PAUSED, WIN, LOSE

Deliverable: You can “lose” correctly; “win” condition exists.

---

## 7) The Doctor: cursor-follow + click-to-cure (Week 3)
- [ ] (★) Draw the doctor as a blue cross that follows mouse position
- [ ] (★) Click-to-cure mechanic:
  - [ ] On click, find nearest infected within a cure radius
  - [ ] Set infected → healthy (or recovered)
  - [ ] Add cooldown to prevent spam (optional)
- [ ] (☆) Add curing effect (pulse ring / particles)

Deliverable: Player can actively reduce infections.

---

## 8) Vaccine pellets: ranged curing (Week 4)
- [ ] (★) Implement projectile class:
  - [ ] Spawn from doctor toward mouse direction on right click / key
  - [ ] Projectile speed, lifetime, radius
- [ ] (★) Projectile hits infected agent → cures it
- [ ] (★) Ammo / cooldown balancing
- [ ] (☆) Add ricochet or piercing shots (advanced/polish)

Deliverable: Ranged curing works and feels responsive.

---

## 9) HUD + in-game telemetry (Week 5)
- [ ] (★) HUD elements:
  - [ ] Infected %
  - [ ] Healthy count
  - [ ] Timer above 50%
  - [ ] Total elapsed time
  - [ ] Pellet cooldown/ammo
- [ ] (★) Infection curve overlay (simple):
  - [ ] Keep a time series buffer (e.g., last 120s)
  - [ ] Draw as a line graph in a corner
- [ ] (☆) Toggle debug UI (F1)

Deliverable: The player understands the system state at all times.

---

## 10) Menus, UX, and feedback (Week 5)
- [ ] (★) Main menu: Start / Quit
- [ ] (★) End screens: Win / Lose + restart
- [ ] (★) Pause menu (Esc)
- [ ] (☆) Settings screen (agent count, infection probability p, speed)

Deliverable: A playable loop from menu → play → end → restart.

---

## 11) Audio + assets (Week 5)
- [ ] (☆) Add click cure sound
- [ ] (☆) Add pellet shoot sound
- [ ] (☆) Add subtle background loop
- [ ] (☆) Add hit/impact sound for collisions (careful: can get noisy)
- [ ] (☆) Add simple sprites (optional; circles are fine for MVP)

Deliverable: Basic audio feedback improves feel.

---

## 12) Difficulty tuning + balance (Week 6)
- [ ] (★) Tune agent speed curve over time
- [ ] (★) Tune infection probability `p`
- [ ] (★) Tune pellet cooldown/ammo
- [ ] (★) Ensure loss condition is fair (not instant doom)
- [ ] (☆) Add difficulty levels (Easy/Normal/Hard)

Deliverable: “Containment” is challenging but possible.

---

## 13) Performance + polish (Week 6)
- [ ] (★) Profile with high agent counts (e.g., 500, 1000)
- [ ] (★) Add spatial hashing/grid if collisions become slow
- [ ] (☆) Add screen shake or subtle FX
- [ ] (☆) Add smooth trails or motion blur (optional)
- [ ] (★) Bug fixes + edge cases (stuck agents, runaway speeds, etc.)

Deliverable: Smooth performance and stable gameplay.

---

## 14) Documentation + final submission
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
