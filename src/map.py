"""Hospital map with collision mask.

Loads the visual map (hospital_map.png) and the border map
(hospital_map_borders.png) which has green painted over all
walls / obstacles.  A collision mask is built from the green pixels
so agents and the doctor bounce off them.
"""

from __future__ import annotations

import os
import pygame
import config


class HospitalMap:
    """Manages the game world background and its collision mask."""

    def __init__(self) -> None:
        base = os.path.join(os.path.dirname(__file__), "components", "Map")

        # ---------- visual surface ----------
        vis_path = os.path.join(base, "hospital_map.png")
        self.surface = pygame.image.load(vis_path).convert()

        # World dimensions come from the image itself
        self.world_w = self.surface.get_width()
        self.world_h = self.surface.get_height()
        config.WORLD_WIDTH = self.world_w
        config.WORLD_HEIGHT = self.world_h

        # ---------- collision mask ----------
        border_path = os.path.join(base, "hospital_map_borders.png")
        border_img = pygame.image.load(border_path).convert()
        # Ensure the border image is the same size as the visual map
        if border_img.get_size() != (self.world_w, self.world_h):
            border_img = pygame.transform.smoothscale(
                border_img, (self.world_w, self.world_h)
            )

        # Build a 1-bit mask:  1 = wall (green pixel), 0 = walkable
        self._build_collision_mask(border_img)

    # ------------------------------------------------------------------
    # Collision helpers
    # ------------------------------------------------------------------

    def _build_collision_mask(self, border_img: pygame.Surface) -> None:
        """Create a pygame.mask.Mask from the green pixels."""
        w, h = border_img.get_size()
        # We create a surface where wall pixels are opaque (alpha=255)
        # and walkable pixels are transparent (alpha=0), then make a Mask.
        mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        mask_surf.fill((0, 0, 0, 0))

        # Use PixelArray for faster access than get_at/set_at
        border_arr = pygame.PixelArray(border_img)
        mask_arr = pygame.PixelArray(mask_surf)

        for y in range(h):
            for x in range(w):
                # Unmap the pixel to get RGB
                color = border_img.unmap_rgb(border_arr[x, y])
                r, g, b = color[0], color[1], color[2]
                if (g >= config.COLLISION_GREEN_THRESHOLD
                        and r <= config.COLLISION_RED_MAX
                        and b <= config.COLLISION_BLUE_MAX):
                    mask_arr[x, y] = mask_surf.map_rgb((255, 255, 255, 255))

        # Release PixelArrays before creating mask
        del border_arr
        del mask_arr

        self.collision_mask = pygame.mask.from_surface(mask_surf)

    def is_wall(self, x: int, y: int) -> bool:
        """Return True if the world-pixel (x, y) is inside a wall."""
        if x < 0 or y < 0 or x >= self.world_w or y >= self.world_h:
            return True  # out-of-bounds counts as wall
        return bool(self.collision_mask.get_at((x, y)))

    def is_circle_colliding(self, cx: float, cy: float, radius: int) -> bool:
        """Quick check: does a circle at (cx, cy) overlap any wall pixel?

        We sample a few points around the circumference + centre.
        """
        ix, iy = int(cx), int(cy)
        if self.is_wall(ix, iy):
            return True
        # Sample 8 points on circumference
        for angle_deg in range(0, 360, 45):
            dx = int(radius * pygame.math.Vector2(1, 0).rotate(angle_deg).x)
            dy = int(radius * pygame.math.Vector2(1, 0).rotate(angle_deg).y)
            if self.is_wall(ix + dx, iy + dy):
                return True
        return False

    def push_out_of_wall(self, pos: pygame.Vector2, radius: int) -> pygame.Vector2:
        """If *pos* is inside a wall, nudge it to the nearest walkable pixel.

        Uses a simple radial search: try small offsets in 8 directions until
        the circle no longer overlaps any wall.
        """
        if not self.is_circle_colliding(pos.x, pos.y, radius):
            return pos

        # Try increasingly large offsets
        for dist in range(1, 40, 2):
            for angle_deg in range(0, 360, 30):
                d = pygame.Vector2(dist, 0).rotate(angle_deg)
                test = pos + d
                if not self.is_circle_colliding(test.x, test.y, radius):
                    return test
        return pos  # give up if nothing found

    def find_walkable_pos(self, radius: int, rng=None) -> pygame.Vector2 | None:
        """Return a random walkable position, or None after many attempts."""
        import random
        _rng = rng or random
        for _ in range(2000):
            x = _rng.uniform(radius, self.world_w - radius)
            y = _rng.uniform(radius, self.world_h - radius)
            if not self.is_circle_colliding(x, y, radius):
                return pygame.Vector2(x, y)
        return None

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, camera) -> None:
        """Blit the portion of the map that is currently visible (zoom-aware)."""
        # The camera tells us what world rectangle is visible
        vw = int(camera.view_w)
        vh = int(camera.view_h)
        ox = int(camera.offset.x)
        oy = int(camera.offset.y)

        # Clamp so we don't read past the image edges
        vw = min(vw, self.world_w - ox)
        vh = min(vh, self.world_h - oy)

        # Grab the visible slice of the world
        src_rect = pygame.Rect(ox, oy, vw, vh)
        visible = self.surface.subsurface(src_rect)

        # Scale it up to fill the entire screen
        scaled = pygame.transform.scale(visible, (config.WIDTH, config.HEIGHT))
        surface.blit(scaled, (0, 0))
