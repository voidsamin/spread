"""Sound manager for SPREAD.

Uses pre-loaded Sound objects on dedicated channels for music loops
so there is zero disk I/O during transitions (eliminates the lag
caused by pygame.mixer.music.load).

One-shot SFX are played on auto-assigned channels.
"""

from __future__ import annotations

import os
import pygame
import config


# Reserve channels 0-2 for music loops
_CH_MENU   = 0
_CH_GAME   = 1
_CH_DANGER = 2
_NUM_RESERVED = 3


class SoundManager:
    """Centralised audio controller — zero-lag music transitions."""

    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Ensure we have enough channels (reserved + plenty for SFX)
        pygame.mixer.set_num_channels(max(pygame.mixer.get_num_channels(), 16))

        self._sounds_dir = os.path.join(
            os.path.dirname(__file__), "components", "Sounds"
        )

        # --- Pre-load music loops as Sound objects (in-memory) ----------
        self._music: dict[str, pygame.mixer.Sound] = {}
        for key in ("menu_music", "game_music", "danger_music"):
            path = os.path.join(self._sounds_dir, config.SOUND_FILES[key])
            if os.path.isfile(path):
                self._music[key] = pygame.mixer.Sound(path)

        # Dedicated channels for music
        self._ch_menu   = pygame.mixer.Channel(_CH_MENU)
        self._ch_game   = pygame.mixer.Channel(_CH_GAME)
        self._ch_danger  = pygame.mixer.Channel(_CH_DANGER)

        # --- Pre-load SFX ---
        self._sfx: dict[str, pygame.mixer.Sound] = {}
        sfx_keys = (
            "menu_select", "game_start", "win_sfx", "lose_sfx",
            "inject_sfx", "shot_sfx", "hit_sfx",
        )
        for key in sfx_keys:
            path = os.path.join(self._sounds_dir, config.SOUND_FILES[key])
            if os.path.isfile(path):
                self._sfx[key] = pygame.mixer.Sound(path)

        # State tracking
        self._mode: str = "silent"       # "menu" | "game" | "silent"
        self._danger_blend: float = 0.0  # 0 = full normal, 1 = full danger

        # Apply initial volumes
        self._refresh_volumes()

    # ------------------------------------------------------------------
    # Volume maths:  final = base * category * master
    # ------------------------------------------------------------------

    def _music_vol(self, base: float) -> float:
        return base * config.MUSIC_VOLUME * config.MASTER_VOLUME

    def _sfx_vol(self, base: float) -> float:
        return base * config.SFX_VOLUME * config.MASTER_VOLUME

    def _refresh_volumes(self) -> None:
        """Re-apply all volumes (call after slider changes)."""
        # SFX
        vol_map = {
            "menu_select": config.VOL_MENU_SELECT,
            "game_start":  config.VOL_GAME_START,
            "win_sfx":     config.VOL_WIN_SFX,
            "lose_sfx":    config.VOL_LOSE_SFX,
            "inject_sfx":  config.VOL_INJECT,
            "shot_sfx":    config.VOL_SHOT,
            "hit_sfx":     config.VOL_HIT,
        }
        for key, base in vol_map.items():
            if key in self._sfx:
                self._sfx[key].set_volume(self._sfx_vol(base))

        # Music channel volumes are handled continuously by update_music()
        # but we set menu volume immediately
        if "menu_music" in self._music:
            self._music["menu_music"].set_volume(self._music_vol(config.VOL_MENU_MUSIC))

    # ------------------------------------------------------------------
    # Music control
    # ------------------------------------------------------------------

    def _stop_all_music(self, fade_ms: int = 500) -> None:
        self._ch_menu.fadeout(fade_ms)
        self._ch_game.fadeout(fade_ms)
        self._ch_danger.fadeout(fade_ms)

    def on_menu(self) -> None:
        """Switch to menu music."""
        if self._mode == "menu":
            return
        self._stop_all_music(400)
        snd = self._music.get("menu_music")
        if snd:
            snd.set_volume(self._music_vol(config.VOL_MENU_MUSIC))
            self._ch_menu.play(snd, loops=-1, fade_ms=400)
        self._mode = "menu"

    def on_game_start(self) -> None:
        """Transition to gameplay music."""
        self._stop_all_music(300)
        self.play_sfx("game_start")

        # Start both loops simultaneously — normal at full vol, danger at zero
        self._danger_blend = 0.0
        game_snd = self._music.get("game_music")
        danger_snd = self._music.get("danger_music")
        if game_snd:
            game_snd.set_volume(self._music_vol(config.VOL_GAME_MUSIC))
            self._ch_game.play(game_snd, loops=-1, fade_ms=600)
        if danger_snd:
            danger_snd.set_volume(0.0)
            self._ch_danger.play(danger_snd, loops=-1, fade_ms=0)
        self._mode = "game"

    def on_win(self) -> None:
        self._stop_all_music(500)
        self.play_sfx("win_sfx")
        self._mode = "silent"

    def on_lose(self) -> None:
        self._stop_all_music(500)
        self.play_sfx("lose_sfx")
        self._mode = "silent"

    def update_music(self, dt: float, infection_ratio: float) -> None:
        """Smoothly cross-fade between normal and danger music each frame.
        Call this every frame from Game.update().
        """
        if self._mode != "game":
            return

        # Determine target blend
        target = 1.0 if infection_ratio >= config.DANGER_THRESHOLD else 0.0

        # Smoothly move toward target
        if self._danger_blend < target:
            self._danger_blend = min(target, self._danger_blend + config.CROSSFADE_SPEED * dt)
        elif self._danger_blend > target:
            self._danger_blend = max(target, self._danger_blend - config.CROSSFADE_SPEED * dt)

        # Apply volumes
        normal_vol = self._music_vol(config.VOL_GAME_MUSIC) * (1.0 - self._danger_blend)
        danger_vol = self._music_vol(config.VOL_DANGER_MUSIC) * self._danger_blend

        game_snd = self._music.get("game_music")
        danger_snd = self._music.get("danger_music")
        if game_snd:
            game_snd.set_volume(normal_vol)
        if danger_snd:
            danger_snd.set_volume(danger_vol)

    # ------------------------------------------------------------------
    # One-shot SFX
    # ------------------------------------------------------------------

    def play_sfx(self, key: str) -> None:
        sfx = self._sfx.get(key)
        if sfx is not None:
            sfx.play()

    def on_menu_select(self) -> None:
        self.play_sfx("menu_select")

    # ------------------------------------------------------------------
    # Settings callback — re-apply volumes after slider changes
    # ------------------------------------------------------------------

    def apply_volume_settings(self) -> None:
        """Called when the user adjusts volume sliders in settings."""
        self._refresh_volumes()
        # Re-apply current music blend immediately
        if self._mode == "game":
            self.update_music(0.0, 0.0)  # just refresh volumes
        elif self._mode == "menu":
            snd = self._music.get("menu_music")
            if snd:
                snd.set_volume(self._music_vol(config.VOL_MENU_MUSIC))
