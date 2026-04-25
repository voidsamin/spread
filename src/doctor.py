from __future__ import annotations

import os
import pygame
import config
from agents import Agent
from projectiles import Projectile


# ---------------------------------------------------------------------------
# Animation helpers
# ---------------------------------------------------------------------------

def _load_sheet(filename: str) -> pygame.Surface:
    """Load a spritesheet from the Doctor asset folder."""
    path = os.path.join(os.path.dirname(__file__), "components", "Doctor", filename)
    return pygame.image.load(path).convert_alpha()


def _cut_frames(sheet: pygame.Surface, rects: list[tuple], scale: float) -> list[pygame.Surface]:
    """Extract and scale individual frames from a spritesheet using predefined rects."""
    frames: list[pygame.Surface] = []
    for (x, y, w, h) in rects:
        sub = sheet.subsurface(pygame.Rect(x, y, w, h))
        if scale != 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            sub = pygame.transform.smoothscale(sub, (new_w, new_h))
        frames.append(sub)
    return frames


# ---------------------------------------------------------------------------
# Animation state enum
# ---------------------------------------------------------------------------

class AnimState:
    IDLE = "idle"
    RUNNING = "running"
    SHOOTING = "shooting"
    INJECTING = "injecting"
    WIN = "win"
    LOSE = "lose"


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------

class Doctor:
    """
    Doctor follows the mouse and can cure infected agents with left click.
    Now rendered as an animated sprite instead of a primitive cross.
    """

    def __init__(self) -> None:
        self.pos = pygame.Vector2(config.WIDTH // 2, config.HEIGHT // 2)
        self.target_pos = self.pos.copy()
        self.cooldown_timer = 0.0  # seconds until next cure allowed

        # Projectile (pellet) shooting
        self.shot_cooldown_timer = 0.0
        self.ammo = config.PELLET_AMMO_MAX
        self.reload_timer = 0.0

        # Aim direction fallback
        self.aim_dir = pygame.Vector2(1, 0)

        # ------ Sprite / Animation setup ------
        scales = config.DOCTOR_ANIMATION_SCALES
        fallback = config.DOCTOR_SPRITE_SCALE

        # Load spritesheets once
        standing_sheet = _load_sheet("standing_transparent_bg.png")
        running_sheet  = _load_sheet("running_transparent_bg.png")
        shooting_sheet = _load_sheet("shooting_transparent_bg.png")
        injecting_sheet = _load_sheet("injecting_transparent_bg.png")
        win_sheet      = _load_sheet("win_transparent_bg.png")
        lose_sheet     = _load_sheet("lose_transparent_bg.png")
        bullet_sheet   = _load_sheet("bullet_transparent_bg.png")

        # Cut frames using config rects with per-animation scales
        self.frames: dict[str, list[pygame.Surface]] = {
            AnimState.IDLE:      _cut_frames(standing_sheet, config.DOCTOR_FRAMES["standing"], scales.get("standing", fallback)),
            AnimState.RUNNING:   _cut_frames(running_sheet,  config.DOCTOR_FRAMES["running"],  scales.get("running", fallback)),
            AnimState.SHOOTING:  _cut_frames(shooting_sheet, config.DOCTOR_FRAMES["shooting"], scales.get("shooting", fallback)),
            AnimState.INJECTING: _cut_frames(injecting_sheet, config.DOCTOR_FRAMES["injecting"], scales.get("injecting", fallback)),
            AnimState.WIN:       _cut_frames(win_sheet,      config.DOCTOR_FRAMES["win"],      scales.get("win", fallback)),
            AnimState.LOSE:      _cut_frames(lose_sheet,     config.DOCTOR_FRAMES["lose"],     scales.get("lose", fallback)),
        }

        # Also pre-flip every frame set for facing-left rendering
        self.frames_flipped: dict[str, list[pygame.Surface]] = {}
        for key, frame_list in self.frames.items():
            self.frames_flipped[key] = [pygame.transform.flip(f, True, False) for f in frame_list]

        # Bullet sprite (single image)
        bx, by, bw, bh = config.DOCTOR_BULLET_RECT
        bullet_sub = bullet_sheet.subsurface(pygame.Rect(bx, by, bw, bh))
        bullet_size = int(config.PELLET_RADIUS * 5)  # scale bullet to look nice
        self.bullet_sprite = pygame.transform.smoothscale(bullet_sub, (bullet_size, bullet_size))

        # Animation state
        self.anim_state = AnimState.IDLE
        self.current_frame = 0
        self.anim_timer = 0.0
        self.anim_spf = 1.0 / config.DOCTOR_ANIM_FPS  # seconds per frame

        # Running sub-state management
        # Frame 0 = start, 1-3 = loop, 4 = end
        self._run_started = False  # True once frame 0 has played

        # Facing direction (False = right / default, True = left / flipped)
        self.facing_left = False

        # Pending projectile: when shooting, the projectile is spawned at frame 6
        self._pending_projectile: Projectile | None = None
        self._projectile_fired = False  # True once the projectile has been emitted this shot

        # Movement detection threshold
        self._prev_pos = self.pos.copy()
        self._move_threshold = 2.0  # pixels of movement to count as "running"

    # ------------------------------------------------------------------
    # Animation state transitions
    # ------------------------------------------------------------------

    def _set_anim(self, state: str, reset: bool = True) -> None:
        """Change animation state, optionally resetting frame counter."""
        if self.anim_state == state and not reset:
            return
        self.anim_state = state
        if reset:
            self.current_frame = 0
            self.anim_timer = 0.0
            self._run_started = False

    def set_end_state(self, won: bool) -> None:
        """Called by game.py when the game ends."""
        self._set_anim(AnimState.WIN if won else AnimState.LOSE)

    def reset(self) -> None:
        """Reset doctor animation and action state for a new game."""
        self._set_anim(AnimState.IDLE)
        self.cooldown_timer = 0.0
        self.shot_cooldown_timer = 0.0
        self.ammo = config.PELLET_AMMO_MAX
        self.reload_timer = 0.0
        self._pending_projectile = None
        self._projectile_fired = False
        self.pos = pygame.Vector2(config.WIDTH // 2, config.HEIGHT // 2)
        self.target_pos = self.pos.copy()
        self._prev_pos = self.pos.copy()

    # ------------------------------------------------------------------
    # Core update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        # --- Follow mouse position with smoothing ---
        mx, my = pygame.mouse.get_pos()
        self.target_pos.update(mx, my)

        alpha = min(1.0, config.DOCTOR_FOLLOW_SPEED * dt)
        self._prev_pos = self.pos.copy()
        self.pos += (self.target_pos - self.pos) * alpha

        # --- Aim direction ---
        aim_vec = self.target_pos - self.pos
        if aim_vec.length_squared() > 1e-6:
            self.aim_dir = aim_vec.normalize()

        # --- Facing direction (based on mouse relative to doctor) ---
        self.facing_left = (mx < self.pos.x)

        # --- Cooldowns ---
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

        if self.shot_cooldown_timer > 0:
            self.shot_cooldown_timer = max(0.0, self.shot_cooldown_timer - dt)

        # Simple reload
        if self.ammo <= 0:
            self.reload_timer += dt
            if self.reload_timer >= config.PELLET_RELOAD_TIME:
                self.ammo = config.PELLET_AMMO_MAX
                self.reload_timer = 0.0
        else:
            self.reload_timer = 0.0

        # --- Animation state machine ---
        # Priority: WIN/LOSE > SHOOTING > INJECTING > RUNNING > IDLE
        # WIN/LOSE are set externally and lock the doctor
        if self.anim_state in (AnimState.WIN, AnimState.LOSE):
            self._advance_animation(dt, loop=False)
            return

        # SHOOTING: play through once, then return to idle
        if self.anim_state == AnimState.SHOOTING:
            finished = self._advance_animation(dt, loop=False)
            # Check if we should fire the projectile this frame
            if not self._projectile_fired and self.current_frame >= config.DOCTOR_SHOOT_FIRE_FRAME:
                self._projectile_fired = True
                self._create_pending_projectile()
            # Animation finished?
            if finished:
                self._set_anim(AnimState.IDLE)
            return

        # INJECTING: play through once, then return to idle
        if self.anim_state == AnimState.INJECTING:
            finished = self._advance_animation(dt, loop=False)
            if finished:
                self._set_anim(AnimState.IDLE)
            return

        # Detect movement: use distance from doctor to cursor target
        dist_to_target = (self.target_pos - self.pos).length()
        is_moving = dist_to_target > self._move_threshold

        if is_moving:
            if self.anim_state != AnimState.RUNNING:
                self._set_anim(AnimState.RUNNING)
            self._advance_running(dt)
        else:
            if self.anim_state == AnimState.RUNNING:
                # Play the "end" frame (frame 4) before going idle
                if self.current_frame < 4:
                    self.current_frame = 4
                    self.anim_timer = 0.0
                finished = self._advance_animation(dt, loop=False)
                if finished:
                    self._set_anim(AnimState.IDLE)
            else:
                if self.anim_state != AnimState.IDLE:
                    self._set_anim(AnimState.IDLE)
                self._advance_animation(dt, loop=True)

    # ------------------------------------------------------------------
    # Animation frame advancement
    # ------------------------------------------------------------------

    def _advance_animation(self, dt: float, loop: bool) -> bool:
        """Advance animation timer; move to next frame if needed.
        
        Returns True if a non-looping animation has completed its last frame.
        """
        self.anim_timer += dt
        if self.anim_timer >= self.anim_spf:
            self.anim_timer -= self.anim_spf
            max_frame = len(self.frames[self.anim_state]) - 1
            if self.current_frame < max_frame:
                self.current_frame += 1
            elif loop:
                self.current_frame = 0
            else:
                # Non-looping animation reached the end
                return True
        return False

    def _advance_running(self, dt: float) -> None:
        """Handle the running animation with start/loop/end sub-states.
        
        Frame 0 = start (play once), Frames 1-3 = loop, Frame 4 = end (on stop).
        """
        self.anim_timer += dt
        if self.anim_timer >= self.anim_spf:
            self.anim_timer -= self.anim_spf
            if not self._run_started:
                # Playing the start frame (frame 0)
                if self.current_frame == 0:
                    self.current_frame = 1
                    self._run_started = True
            else:
                # Loop through frames 1-3
                self.current_frame += 1
                if self.current_frame > 3:
                    self.current_frame = 1

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def can_cure(self) -> bool:
        return self.cooldown_timer <= 0.0

    def try_cure(self, agents: list[Agent]) -> bool:
        """
        Cure the nearest infected agent within CURE_RADIUS.
        Returns True if someone was cured, else False.
        """
        if not self.can_cure():
            return False

        # Don't interrupt shooting
        if self.anim_state == AnimState.SHOOTING:
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

        # Trigger injecting animation
        self._set_anim(AnimState.INJECTING)

        return True

    def update_aim(self, dx: int, dy: int) -> None:
        v = pygame.Vector2(dx, dy)
        if v.length_squared() > 0:
            self.aim_dir = v.normalize()

    def try_shoot(self) -> Projectile | None:
        """
        Initiate a shooting animation. The actual projectile is spawned
        mid-animation at the configured fire frame.
        Returns None always — use collect_projectile() to get the projectile later.
        """
        if self.shot_cooldown_timer > 0:
            return None
        if self.ammo <= 0:
            return None

        # Don't interrupt an ongoing action animation
        if self.anim_state in (AnimState.SHOOTING, AnimState.INJECTING):
            return None

        self.ammo -= 1
        self.shot_cooldown_timer = config.PELLET_COOLDOWN

        # Start shooting animation — projectile will spawn at frame 6
        self._set_anim(AnimState.SHOOTING)
        self._projectile_fired = False
        self._pending_projectile = None

        return None  # projectile comes later via collect_projectile()

    def _create_pending_projectile(self) -> None:
        """Build the projectile at the moment the shooting animation fires."""
        mx, my = pygame.mouse.get_pos()
        target = pygame.Vector2(mx, my)
        direction = target - self.pos

        if direction.length_squared() > 1e-6:
            direction = direction.normalize()
        else:
            direction = self.aim_dir

        vel = direction * config.PELLET_SPEED

        muzzle_offset = 14
        spawn_pos = self.pos + direction * muzzle_offset

        self._pending_projectile = Projectile(
            pos=spawn_pos,
            vel=vel,
            radius=config.PELLET_RADIUS,
            life=config.PELLET_LIFETIME,
            sprite=self.bullet_sprite,
        )

    def collect_projectile(self) -> Projectile | None:
        """Called by game.py each frame to collect a projectile if one was spawned."""
        if self._pending_projectile is not None:
            proj = self._pending_projectile
            self._pending_projectile = None
            return proj
        return None

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the doctor's current animation frame centered at position."""
        frame_bank = self.frames_flipped if self.facing_left else self.frames
        frame_list = frame_bank.get(self.anim_state)

        if not frame_list:
            # Fallback to idle if something went wrong
            frame_list = frame_bank[AnimState.IDLE]

        idx = min(self.current_frame, len(frame_list) - 1)
        sprite = frame_list[idx]

        # Center the sprite on the doctor's position
        rect = sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surface.blit(sprite, rect)

        # Optional: show cure radius as a thin ring (useful feedback)
        pygame.draw.circle(
            surface,
            config.DOCTOR_COLOR,
            (int(self.pos.x), int(self.pos.y)),
            config.CURE_RADIUS,
            1,
        )
