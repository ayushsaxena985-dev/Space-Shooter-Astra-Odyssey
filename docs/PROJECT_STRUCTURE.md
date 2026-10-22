# Project Structure

## Main files

### `main.py`
Contains the complete Pygame game implementation:
- game settings and colors
- sound generation
- space environment
- spaceship
- bullets
- aliens
- Ravana boss
- power-ups
- particles and floating text
- game engine and game states
- leaderboard UI

### `database.py`
Contains `ScoreDB`, the SQLite leaderboard layer used by `main.py`.

### `requirements.txt`
Runtime dependency for Pygame.

### `requirements-dev.txt`
Runtime dependencies plus Pytest for development/testing.

## Tests

`tests/test_database.py` verifies leaderboard CRUD behavior.

`tests/test_game_config.py` verifies important game configuration and imports the game in a headless Pygame environment.

## GitHub files

- `.gitignore` keeps caches, virtual environments and the local `scores.db` out of Git.
- `.gitattributes` normalizes text files and marks the SQLite database as binary.
- `LICENSE` contains the MIT license.
- `.github/workflows/tests.yml` runs tests automatically on pushes and pull requests.
