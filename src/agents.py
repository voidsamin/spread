from __future__ import annotations

import random
from dataclasses import dataclass, field

import pygame

import config


def _clamp_speed(v: pygame.Vector2, max_speed: float) -> pygame.Vector2:
    if v.length_squared() > max_speed * max_speed:
        v.scale_to_length(max_speed)
    return v


@dataclass
class Agent:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: int
    strain_id: int | None = None  # None = healthy, int = specific strain ID
    susceptibility: float = 1.0   # How easily this agent gets infected

    # Target-based wandering
    target_pos: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    _wall_hit_count: int = 0      # consecutive wall collisions (for stuck detection)

    # Animation state (managed per-agent)
    anim_timer: float = 0.0
    current_frame: int = 0
    facing_left: bool = False

    def update(self, dt: float, difficulty_multiplier: float = 1.0) -> None:
        # --- Target-based steering ---
        to_target = self.target_pos - self.pos
        dist = to_target.length()

        if dist > config.AGENT_TARGET_REACH_DIST:
            # Steer toward target with some wander jitter
            desired_dir = to_target / dist  # normalize
            jitter = pygame.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            )
            if jitter.length_squared() > 0:
                jitter = jitter.normalize()
            # Blend: mostly go toward target, with some random wander
            steer = desired_dir * 0.7 + jitter * 0.3
            if steer.length_squared() > 0:
                steer = steer.normalize()
            self.vel += steer * config.WANDER_STRENGTH * dt * difficulty_multiplier
        else:
            # Reached target — will pick a new one in bounce_off_map_walls
            self._wall_hit_count = 0

        # Clamp speed
        _clamp_speed(self.vel, config.MAX_SPEED * difficulty_multiplier)

        # Move
        self.pos += self.vel * dt

        # Update facing direction based on horizontal velocity
        if abs(self.vel.x) > 0.5:
            self.facing_left = self.vel.x < 0

        # Advance walk animation
        self.anim_timer += dt
        frame_duration = 1.0 / config.AGENT_ANIM_FPS
        if self.anim_timer >= frame_duration:
            self.anim_timer -= frame_duration
            if self.strain_id is not None:
                anim_key = config.STRAIN_TO_ANIM_KEY.get(self.strain_id, "infected1")
            else:
                anim_key = "healthy"
            total_frames = len(config.AGENT_FRAMES.get(anim_key, []))
            if total_frames > 0:
                self.current_frame = (self.current_frame + 1) % total_frames
            else:
                self.current_frame = 0

    def pick_new_target(self, hospital_map) -> None:
        """Pick a new random walkable target position."""
        new_target = hospital_map.find_walkable_pos(self.radius)
        if new_target is not None:
            self.target_pos = new_target
        self._wall_hit_count = 0



    def bounce_off_walls(self, width: int, height: int) -> None:
        # Left / Right
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.vel.x *= -1
        elif self.pos.x + self.radius > width:
            self.pos.x = width - self.radius
            self.vel.x *= -1

        # Top / Bottom
        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.vel.y *= -1
        elif self.pos.y + self.radius > height:
            self.pos.y = height - self.radius
            self.vel.y *= -1

    def bounce_off_map_walls(self, hospital_map) -> None:
        """Handle collision with map walls using target-based avoidance."""
        # World-boundary clamping first
        w, h = hospital_map.world_w, hospital_map.world_h
        clamped = False
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            clamped = True
        elif self.pos.x + self.radius > w:
            self.pos.x = w - self.radius
            clamped = True
        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            clamped = True
        elif self.pos.y + self.radius > h:
            self.pos.y = h - self.radius
            clamped = True

        # Check collision with map geometry
        if hospital_map.is_circle_colliding(self.pos.x, self.pos.y, self.radius):
            self.pos = hospital_map.push_out_of_wall(self.pos, self.radius)
            self._wall_hit_count += 1
            clamped = True

        # If we hit anything or reached our target, pick a new destination
        dist_to_target = (self.target_pos - self.pos).length()
        if clamped or dist_to_target < config.AGENT_TARGET_REACH_DIST:
            self.pick_new_target(hospital_map)
            # Steer velocity toward the new target
            to_new = self.target_pos - self.pos
            if to_new.length_squared() > 1:
                speed = max(self.vel.length(), config.AGENT_SPEED_MIN)
                self.vel = to_new.normalize() * speed

    def draw(
        self,
        surface: pygame.Surface,
        agent_anims: dict[str, list[pygame.Surface]] | None = None,
        virus_sprites: dict[int, pygame.Surface] | None = None,
        healthy_sprite: pygame.Surface | None = None,
        camera=None,
    ) -> None:
        # Convert world position to screen position
        if camera is not None:
            sx, sy = camera.apply(self.pos)
        else:
            sx, sy = int(self.pos.x), int(self.pos.y)

        # Determine animation key
        if self.strain_id is not None:
            anim_key = config.STRAIN_TO_ANIM_KEY.get(self.strain_id, "infected1")
        else:
            anim_key = "healthy"

        # Try animated sprite first
        if agent_anims and anim_key in agent_anims:
            frames = agent_anims[anim_key]
            if frames:
                idx = self.current_frame % len(frames)
                frame = frames[idx]
                if self.facing_left:
                    frame = pygame.transform.flip(frame, True, False)
                rect = frame.get_rect(center=(sx, sy))
                surface.blit(frame, rect)
                return

        # Fallback: static sprites (legacy path)
        if self.strain_id is not None and virus_sprites:
            sprite = virus_sprites.get(self.strain_id)
            if sprite:
                rect = sprite.get_rect(center=(sx, sy))
                color = config.STRAINS[self.strain_id]["color"]
                glow_radius = int(self.radius * 1.6) 
                pygame.draw.circle(surface, color, (sx, sy), glow_radius)
                surface.blit(sprite, rect)
            else:
                color = config.STRAINS[self.strain_id]["color"]
                pygame.draw.circle(surface, color, (sx, sy), self.radius)
        elif self.strain_id is None and healthy_sprite:
            rect = healthy_sprite.get_rect(center=(sx, sy))
            surface.blit(healthy_sprite, rect)
        else:
            if self.strain_id is not None:
                color = config.STRAINS[self.strain_id]["color"]
            else:
                color = config.HEALTHY_COLOR
            pygame.draw.circle(surface, color, (sx, sy), self.radius)


def _random_velocity() -> pygame.Vector2:
    angle = random.uniform(0, 360)
    speed = random.uniform(config.AGENT_SPEED_MIN, config.AGENT_SPEED_MAX)
    return pygame.Vector2(1, 0).rotate(angle) * speed


def _is_overlapping(pos: pygame.Vector2, radius: int, agents: list[Agent]) -> bool:
    min_dist = radius * 2 + config.SPAWN_PADDING
    for a in agents:
        if pos.distance_to(a.pos) < min_dist:
            return True
    return False


def spawn_agents(hospital_map=None) -> list[Agent]:
    agents: list[Agent] = []
    r = config.AGENT_RADIUS
    world_w = getattr(config, "WORLD_WIDTH", config.WIDTH)
    world_h = getattr(config, "WORLD_HEIGHT", config.HEIGHT)

    for _ in range(config.AGENT_COUNT):
        placed = False
        
        # Calculate susceptibility based on selected model
        model = getattr(config, "INFECTION_MODEL", "uniform")
        if model == "gaussian":
            susc = random.gauss(1.0, config.GAUSSIAN_SIGMA)
            susc = max(0.1, susc) # Clamp to positive
        elif model == "exponential":
            susc = random.expovariate(1.0 / config.EXPONENTIAL_SCALE)
            susc = max(0.1, susc)
        else: # uniform or default
            susc = 1.0

        # Use map-aware spawning if a map is provided
        if hospital_map is not None:
            for _map_attempt in range(50):
                pos = hospital_map.find_walkable_pos(r)
                if pos is not None and not _is_overlapping(pos, r, agents):
                    target = hospital_map.find_walkable_pos(r) or pos.copy()
                    agent = Agent(pos=pos, vel=_random_velocity(), radius=r,
                                  susceptibility=susc, target_pos=target)
                    agents.append(agent)
                    placed = True
                    break

        if not placed:
            # Fallback: world-sized random placement
            for _attempt in range(config.SPAWN_MAX_ATTEMPTS):
                pos = pygame.Vector2(
                    random.uniform(r, world_w - r),
                    random.uniform(r, world_h - r),
                )
                if not _is_overlapping(pos, r, agents):
                    agents.append(Agent(pos=pos, vel=_random_velocity(), radius=r, susceptibility=susc))
                    placed = True
                    break

            if not placed:
                pos = pygame.Vector2(
                    random.uniform(r, world_w - r),
                    random.uniform(r, world_h - r),
                )
                agents.append(Agent(pos=pos, vel=_random_velocity(), radius=r, susceptibility=susc))

    # Initial infected per strain
    for strain_id, s_config in config.STRAINS.items():
        count = min(s_config.get("initial_infected", 1), len(agents))
        healthy_agents = [a for a in agents if a.strain_id is None]
        if not healthy_agents:
            break
        for a in random.sample(healthy_agents, min(count, len(healthy_agents))):
            a.strain_id = strain_id

    return agents

def try_spread_infection(a: Agent, b: Agent) -> None:
    """
    If one agent is infected and the other is not,
    infect the healthy one with the specific strain.
    """
    # One infected, one healthy
    if a.strain_id is not None and b.strain_id is None:
        p = config.STRAINS[a.strain_id]["infection_probability"]
        # Multiply by target agent's susceptibility
        if random.random() < p * b.susceptibility:
            b.strain_id = a.strain_id
    elif b.strain_id is not None and a.strain_id is None:
        p = config.STRAINS[b.strain_id]["infection_probability"]
        # Multiply by target agent's susceptibility
        if random.random() < p * a.susceptibility:
            a.strain_id = b.strain_id


def resolve_agent_collisions(agents: list[Agent]) -> None:
    """
    Resolves circle-circle overlaps between agents (simple separation),
    and optionally applies a basic elastic velocity response.

    This is O(N^2) and fine for ~150 agents. If we go much higher,
    we'll add a uniform grid later.
    """
    if len(agents) < 2:
        return

    restitution = getattr(config, "COLLISION_RESTITUTION", 0.0)
    slop = getattr(config, "COLLISION_SLOP", 0.0)

    for i in range(len(agents)):
        a = agents[i]
        for j in range(i + 1, len(agents)):
            b = agents[j]

            delta = b.pos - a.pos
            dist_sq = delta.length_squared()

            min_dist = a.radius + b.radius
            min_dist_sq = min_dist * min_dist

            # No collision/overlap
            if dist_sq >= min_dist_sq or dist_sq == 0:
                # dist_sq == 0: perfectly overlapping (rare). We'll handle below.
                if dist_sq != 0:
                    continue

            # Handle zero-distance overlap (same position)
            if dist_sq == 0:
                # Nudge in a random-ish direction
                delta = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if delta.length_squared() == 0:
                    delta = pygame.Vector2(1, 0)
                delta = delta.normalize()
                dist = 0.0
            else:
                dist = dist_sq ** 0.5
                delta = delta / dist  # normalized

            # Overlap amount
            overlap = (min_dist - dist) + slop
            if overlap <= 0:
                continue

            # Infection spread happens on collision
            try_spread_infection(a, b)

            # --- 1) Separate positions (push each agent half the overlap)
            correction = delta * (overlap * 0.5)
            a.pos -= correction
            b.pos += correction

            # --- 2) Optional: elastic-ish velocity response
            # Only if they are moving towards each other along the normal.
            if restitution > 0:
                rel_vel = b.vel - a.vel
                vel_along_normal = rel_vel.dot(delta)

                # If vel_along_normal > 0 they’re separating already -> skip impulse
                if vel_along_normal < 0:
                    # Equal mass impulse scalar
                    j_impulse = -(1 + restitution) * vel_along_normal / 2.0
                    impulse = delta * j_impulse

                    a.vel -= impulse
                    b.vel += impulse

                    # Clamp after impulse (keeps system stable)
                    _clamp_speed(a.vel, config.MAX_SPEED)
                    _clamp_speed(b.vel, config.MAX_SPEED)
