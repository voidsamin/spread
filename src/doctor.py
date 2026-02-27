from __future__ import annotations

import pygame
import config
from agents import Agent
from projectiles import Projectile


class Doctor:
    """
    Doctor follows the mouse and can cure infected agents with left click.
    """
    def __init__(self) -> None:
        self.pos = pygame.Vector2(config.WIDTH // 2, config.HEIGHT // 2)
        self.target_pos = self.pos.copy() # for smooth following
        self.cooldown_timer = 0.0  # seconds until next cure allowed

        # Projectile (pellet) shooting
        self.shot_cooldown_timer = 0.0
        self.ammo = config.PELLET_AMMO_MAX
        self.reload_timer = 0.0

        # Aim direction fallback (when mouse isn't moving)
        self.aim_dir = pygame.Vector2(1, 0)

    def update(self, dt: float) -> None:
        # Follow mouse position with smoothing
        mx, my = pygame.mouse.get_pos()
        self.target_pos.update(mx, my)

        # Smooth follow so (mouse - doctor) is not zero -> enables true aiming at all angles
        alpha = min(1.0, config.DOCTOR_FOLLOW_SPEED * dt)
        self.pos += (self.target_pos - self.pos) * alpha

        # Update aim direction continuously from doctor -> cursor vector (not mouse rel)
        aim_vec = self.target_pos - self.pos
        if aim_vec.length_squared() > 1e-6:
            self.aim_dir = aim_vec.normalize()


        # Cooldown countdown
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

        # Shot cooldown countdown
        if self.shot_cooldown_timer > 0:
            self.shot_cooldown_timer = max(0.0, self.shot_cooldown_timer - dt)

        # Simple reload: when ammo is empty, wait RELOAD_TIME then refill
        if self.ammo <= 0:
            self.reload_timer += dt
            if self.reload_timer >= config.PELLET_RELOAD_TIME:
                self.ammo = config.PELLET_AMMO_MAX
                self.reload_timer = 0.0
        else:
            self.reload_timer = 0.0


    def can_cure(self) -> bool:
        return self.cooldown_timer <= 0.0

    def try_cure(self, agents: list[Agent]) -> bool:
        """
        Cure the nearest infected agent within CURE_RADIUS.
        Returns True if someone was cured, else False.
        """
        if not self.can_cure():
            return False

        radius = config.CURE_RADIUS
        radius_sq = radius * radius

        nearest: Agent | None = None
        best_d2 = float("inf")

        for a in agents:
            if a.strain_id is None:
                continue
            d2 = (a.pos - self.pos).length_squared()
            if d2 <= radius_sq and d2 < best_d2:
                best_d2 = d2
                nearest = a

        if nearest is None:
            return False

        # Cure
        nearest.strain_id = None

        # Start cooldown
        self.cooldown_timer = config.CURE_COOLDOWN
        return True
    

    def update_aim(self, dx: int, dy: int) -> None:
        v = pygame.Vector2(dx, dy)
        if v.length_squared() > 0:
            self.aim_dir = v.normalize()


    def try_shoot(self) -> Projectile | None:
        """
        Fire a projectile from the doctor toward the mouse cursor.
        Right click (handled by game) should call this.
        Returns Projectile if shot fired, else None.
        """
        if self.shot_cooldown_timer > 0:
            return None
        if self.ammo <= 0:
            return None

        mx, my = pygame.mouse.get_pos()
        target = pygame.Vector2(mx, my)
        direction = target - self.pos

        # Use a tiny epsilon to avoid near-zero vectors causing quantized fallback aiming
        if direction.length_squared() > 1e-6:
            direction = direction.normalize()
        else:
            direction = self.aim_dir

        vel = direction * config.PELLET_SPEED

        # Spawn slightly in front of the doctor (muzzle offset)
        muzzle_offset = 14  # pixels
        spawn_pos = self.pos + direction * muzzle_offset

        proj = Projectile(
            pos=spawn_pos,
            vel=vel,
            radius=config.PELLET_RADIUS,
            life=config.PELLET_LIFETIME,
        )

        self.ammo -= 1
        self.shot_cooldown_timer = config.PELLET_COOLDOWN
        return proj


    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw a blue cross centered at the mouse position + optional cure radius ring.
        """
        x, y = int(self.pos.x), int(self.pos.y)
        color = config.DOCTOR_COLOR

        # Cross size
        arm = 10
        thickness = 3

        pygame.draw.line(surface, color, (x - arm, y), (x + arm, y), thickness)
        pygame.draw.line(surface, color, (x, y - arm), (x, y + arm), thickness)

        # Optional: show cure radius as a thin ring (nice feedback, still MVP-friendly)
        pygame.draw.circle(surface, color, (x, y), config.CURE_RADIUS, 1)
