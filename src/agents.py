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
    infected: bool = False  # state: healthy(False) / infected(True)

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

    def draw(self, surface: pygame.Surface, virus_sprite: pygame.Surface | None = None, healthy_sprite: pygame.Surface | None = None) -> None:
        if self.infected and virus_sprite:
            # Center the sprite on the agent's position
            rect = virus_sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(virus_sprite, rect)
        elif (not self.infected) and healthy_sprite:
            # Center the healthy sprite
            rect = healthy_sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(healthy_sprite, rect)
        else:
            color = config.INFECTED_COLOR if self.infected else config.HEALTHY_COLOR
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

        for _attempt in range(config.SPAWN_MAX_ATTEMPTS):
            pos = pygame.Vector2(
                random.uniform(r, config.WIDTH - r),
                random.uniform(r, config.HEIGHT - r),
            )
            if not _is_overlapping(pos, r, agents):
                agents.append(Agent(pos=pos, vel=_random_velocity(), radius=r))
                placed = True
                break

        # Minimal overlap tolerance if it gets too dense
        if not placed:
            pos = pygame.Vector2(
                random.uniform(r, config.WIDTH - r),
                random.uniform(r, config.HEIGHT - r),
            )
            agents.append(Agent(pos=pos, vel=_random_velocity(), radius=r))

    # Patient-zero (random initial infected)
    infected_count = min(config.INITIAL_INFECTED, len(agents))
    for a in random.sample(agents, infected_count):
        a.infected = True

    return agents

def try_spread_infection(a: Agent, b: Agent) -> None:
    """
    If one agent is infected and the other is not,
    infect the healthy one with probability INFECTION_PROBABILITY.
    """
    p = config.INFECTION_PROBABILITY

    # One infected, one healthy
    if a.infected and (not b.infected):
        if random.random() < p:
            b.infected = True
    elif b.infected and (not a.infected):
        if random.random() < p:
            a.infected = True


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
