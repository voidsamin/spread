"""Sound manager for SPREAD.

Handles all music loops (menu, gameplay, danger) with smooth
cross-fading, and one-shot sound effects (menu click, win, lose, game start).
"""

from __future__ import annotations

import os
import pygame
import config


class SoundManager:
    """Centralised audio controller using pygame.mixer."""

    def __init__(self) -> None:
        # Initialise the mixer (may already be init'd by pygame.init())
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self._sounds_dir = os.path.join(
            os.path.dirname(__file__), "components", "Sounds"
        )

        # Pre-load one-shot sound effects
        self._sfx: dict[str, pygame.mixer.Sound] = {}
        for key in ("menu_select", "game_start", "win_sfx", "lose_sfx"):
            path = os.path.join(self._sounds_dir, config.SOUND_FILES[key])
            if os.path.isfile(path):
                self._sfx[key] = pygame.mixer.Sound(path)

        # Apply SFX volumes
        self._apply_sfx_volumes()

        # Track current music state so we don't restart the same track
        self._current_music: str | None = None

    # ------------------------------------------------------------------
    # Volume helpers
    # ------------------------------------------------------------------

    def _apply_sfx_volumes(self) -> None:
        vol_map = {
            "menu_select": config.VOL_SFX,
            "game_start":  config.VOL_GAME_START,
            "win_sfx":     config.VOL_WIN_SFX,
            "lose_sfx":    config.VOL_LOSE_SFX,
        }
        for key, vol in vol_map.items():
            if key in self._sfx:
                self._sfx[key].set_volume(vol)

    # ------------------------------------------------------------------
    # Music (streamed via pygame.mixer.music — only one at a time)
    # ------------------------------------------------------------------

    def _music_path(self, key: str) -> str:
        return os.path.join(self._sounds_dir, config.SOUND_FILES[key])

    def play_music(self, key: str, loops: int = -1, fade_ms: int | None = None) -> None:
        """Start a music track. Does nothing if it's already playing."""
        if self._current_music == key:
            return
        fade = fade_ms if fade_ms is not None else config.MUSIC_FADE_MS
        path = self._music_path(key)
        if not os.path.isfile(path):
            return

        # Fade out current, then start new
        pygame.mixer.music.fadeout(fade)
        pygame.mixer.music.load(path)

        # Set volume based on track type
        vol_map = {
            "menu_music":   config.VOL_MENU_MUSIC,
            "game_music":   config.VOL_GAME_MUSIC,
            "danger_music": config.VOL_DANGER_MUSIC,
        }
        pygame.mixer.music.set_volume(vol_map.get(key, 0.5))
        pygame.mixer.music.play(loops, fade_ms=fade)
        self._current_music = key

    def stop_music(self, fade_ms: int | None = None) -> None:
        fade = fade_ms if fade_ms is not None else config.MUSIC_FADE_MS
        pygame.mixer.music.fadeout(fade)
        self._current_music = None

    # ------------------------------------------------------------------
    # One-shot SFX
    # ------------------------------------------------------------------

    def play_sfx(self, key: str) -> None:
        """Play a one-shot sound effect (doesn't interrupt music)."""
        sfx = self._sfx.get(key)
        if sfx is not None:
            sfx.play()

    # ------------------------------------------------------------------
    # High-level state helpers (called from Game)
    # ------------------------------------------------------------------

    def on_menu(self) -> None:
        """Start menu music."""
        self.play_music("menu_music")

    def on_game_start(self) -> None:
        """Play the start jingle then switch to game music."""
        self.play_sfx("game_start")
        self.play_music("game_music", fade_ms=800)

    def on_danger(self) -> None:
        """Switch to the danger loop."""
        self.play_music("danger_music")

    def on_safe(self) -> None:
        """Switch back to normal game music."""
        self.play_music("game_music")

    def on_win(self) -> None:
        """Play win effect and stop music."""
        self.stop_music(fade_ms=500)
        self.play_sfx("win_sfx")

    def on_lose(self) -> None:
        """Play lose effect and stop music."""
        self.stop_music(fade_ms=500)
        self.play_sfx("lose_sfx")

    def on_menu_select(self) -> None:
        """Play the click / select blip."""
        self.play_sfx("menu_select")
