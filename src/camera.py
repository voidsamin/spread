"""Viewport camera that follows the player through the world.

The camera stores an offset (top-left corner of the visible area in world
coordinates) and provides helpers to convert between world-space and
screen-space.  Supports a zoom factor (>1 = zoomed in).
"""

from __future__ import annotations

import pygame
import config


class Camera:
    """Smooth-follow camera centred on a target position, with zoom."""

    def __init__(self, world_w: int, world_h: int) -> None:
        self.world_w = world_w
        self.world_h = world_h
        self.zoom = config.CAMERA_ZOOM
        # offset = world-coordinate of the top-left pixel currently shown
        self.offset = pygame.Vector2(0, 0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def view_w(self) -> float:
        """Width of the world area visible on screen (in world pixels)."""
        return config.WIDTH / self.zoom

    @property
    def view_h(self) -> float:
        """Height of the world area visible on screen (in world pixels)."""
        return config.HEIGHT / self.zoom

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, target: pygame.Vector2, dt: float) -> None:
        """Move the camera towards *target* (world pos) with smoothing."""
        vw, vh = self.view_w, self.view_h

        # Desired offset: place target at screen centre
        desired_x = target.x - vw / 2
        desired_y = target.y - vh / 2

        # Smooth interpolation (frame-rate independent via dt)
        smoothing = config.CAMERA_SMOOTHING
        alpha = min(1.0, smoothing * dt * 60)   # normalise around 60 fps

        dx = desired_x - self.offset.x
        dy = desired_y - self.offset.y

        # Dead-zone: don't jitter for sub-pixel differences
        deadzone = config.CAMERA_DEADZONE
        if abs(dx) > deadzone:
            self.offset.x += dx * alpha
        if abs(dy) > deadzone:
            self.offset.y += dy * alpha

        # Clamp so we never show outside the world
        self.offset.x = max(0, min(self.offset.x, self.world_w - vw))
        self.offset.y = max(0, min(self.offset.y, self.world_h - vh))

    def apply(self, world_pos: pygame.Vector2) -> tuple[int, int]:
        """Convert a world position to screen coordinates (zoom-aware)."""
        return (int((world_pos.x - self.offset.x) * self.zoom),
                int((world_pos.y - self.offset.y) * self.zoom))

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Shift a world-space rect into screen space (zoom-aware)."""
        return pygame.Rect(
            int((rect.x - self.offset.x) * self.zoom),
            int((rect.y - self.offset.y) * self.zoom),
            int(rect.w * self.zoom),
            int(rect.h * self.zoom),
        )

    def screen_to_world(self, screen_pos: tuple[int, int]) -> pygame.Vector2:
        """Convert screen (mouse) coordinates to world coordinates."""
        return pygame.Vector2(
            screen_pos[0] / self.zoom + self.offset.x,
            screen_pos[1] / self.zoom + self.offset.y,
        )

    def visible_rect(self) -> pygame.Rect:
        """Return the world-space rect that is currently visible."""
        return pygame.Rect(
            int(self.offset.x), int(self.offset.y),
            int(self.view_w), int(self.view_h),
        )

    def reset(self, target: pygame.Vector2) -> None:
        """Snap the camera to the target immediately (no lerp)."""
        vw, vh = self.view_w, self.view_h
        self.offset.x = max(0, min(target.x - vw / 2, self.world_w - vw))
        self.offset.y = max(0, min(target.y - vh / 2, self.world_h - vh))
