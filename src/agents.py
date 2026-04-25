from __future__ import annotations

import random
from dataclasses import dataclass

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

    # Animation state (managed per-agent)
    anim_timer: float = 0.0
    current_frame: int = 0
    facing_left: bool = False

    def update(self, dt: float, difficulty_multiplier: float = 1.0) -> None:
        # Stochastic "wander": small random acceleration that changes velocity gradually
        # This makes movement look more human/random without teleporting directions.
        jitter = pygame.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1),
        )

        if jitter.length_squared() > 0:
            jitter = jitter.normalize()

        # Apply wander strength scaled by dt and difficulty multiplier
        self.vel += jitter * config.WANDER_STRENGTH * dt * difficulty_multiplier

        # Clamp speed so agents don't accelerate forever (scaled by difficulty)
        _clamp_speed(self.vel, config.MAX_SPEED * difficulty_multiplier)

        # Move (velocity already affected by difficulty through wander and clamping)
        self.pos += self.vel * dt

        # Update facing direction based on horizontal velocity
        if abs(self.vel.x) > 0.5:
            self.facing_left = self.vel.x < 0

        # Advance walk animation
        self.anim_timer += dt
        frame_duration = 1.0 / config.AGENT_ANIM_FPS
        if self.anim_timer >= frame_duration:
            self.anim_timer -= frame_duration
            # Determine the correct frame count for the current animation
            if self.strain_id is not None:
                anim_key = config.STRAIN_TO_ANIM_KEY.get(self.strain_id, "infected1")
            else:
                anim_key = "healthy"
            total_frames = len(config.AGENT_FRAMES.get(anim_key, []))
            if total_frames > 0:
                self.current_frame = (self.current_frame + 1) % total_frames
            else:
                self.current_frame = 0



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

    def draw(
        self,
        surface: pygame.Surface,
        agent_anims: dict[str, list[pygame.Surface]] | None = None,
        virus_sprites: dict[int, pygame.Surface] | None = None,
        healthy_sprite: pygame.Surface | None = None,
    ) -> None:
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
                rect = frame.get_rect(center=(int(self.pos.x), int(self.pos.y)))
                surface.blit(frame, rect)
                return

        # Fallback: static sprites (legacy path)
        if self.strain_id is not None and virus_sprites:
            sprite = virus_sprites.get(self.strain_id)
            if sprite:
                rect = sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
                color = config.STRAINS[self.strain_id]["color"]
                glow_radius = int(self.radius * 1.6) 
                pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), glow_radius)
                surface.blit(sprite, rect)
            else:
                color = config.STRAINS[self.strain_id]["color"]
                pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        elif self.strain_id is None and healthy_sprite:
            rect = healthy_sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(healthy_sprite, rect)
        else:
            if self.strain_id is not None:
                color = config.STRAINS[self.strain_id]["color"]
            else:
                color = config.HEALTHY_COLOR
            pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)


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


def spawn_agents() -> list[Agent]:
    agents: list[Agent] = []
    r = config.AGENT_RADIUS

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

        for _attempt in range(config.SPAWN_MAX_ATTEMPTS):
            pos = pygame.Vector2(
                random.uniform(r, config.WIDTH - r),
                random.uniform(r, config.HEIGHT - r),
            )
            if not _is_overlapping(pos, r, agents):
                agents.append(Agent(pos=pos, vel=_random_velocity(), radius=r, susceptibility=susc))
                placed = True
                break

        # Minimal overlap tolerance if it gets too dense
        if not placed:
            pos = pygame.Vector2(
                random.uniform(r, config.WIDTH - r),
                random.uniform(r, config.HEIGHT - r),
            )
            agents.append(Agent(pos=pos, vel=_random_velocity(), radius=r, susceptibility=susc))

    # Initial infected per strain
    for strain_id, s_config in config.STRAINS.items():
        count = min(s_config.get("initial_infected", 1), len(agents))
        # Get agents that are currently healthy
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
