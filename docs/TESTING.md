# Testing Guide

## Install test dependencies

```bash
pip install -r requirements-dev.txt
```

## Run all tests

```bash
pytest
```

## What is tested?

1. Database creation.
2. Adding leaderboard scores.
3. Sorting leaderboard scores by highest score.
4. Deleting an individual leaderboard entry.
5. Clearing all leaderboard entries.
6. Important weapon configuration.
7. Basic game module import in headless mode.

## Manual game testing

After automated tests pass, run:

```bash
python main.py
```

Check movement, shooting, pause, fullscreen, power-ups, level progression, boss level, game over, leaderboard entry, score deletion and score clearing.
