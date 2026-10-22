import os

# Keep pygame from opening a real window during automated tests.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import main


def test_weapon_configuration():
    assert "arrow" in main.WEAPONS
    assert "agni" in main.WEAPONS
    assert "indra" in main.WEAPONS
    assert "brahma" in main.WEAPONS
    assert main.WEAPONS["brahma"]["dmg"] == 7
    assert main.WEAPONS["indra"]["pierce"] is True


def test_game_constants():
    assert main.FPS == 60
    assert main.WIDTH >= 1024
    assert main.HEIGHT >= 600


def test_spaceship_initial_state():
    ship = main.Spaceship()
    assert ship.lives == 3
    assert ship.shield == 0
    ship.kill()
