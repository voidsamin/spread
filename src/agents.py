# src/agents.py
from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

import config


@dataclass
class Agent:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: int
    infected: bool = False  # state: healthy(False) / infected(True)

    def update(self, dt: float) -> None:
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

    def draw(self, surface: pygame.Surface) -> None:
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