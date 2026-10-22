# 🚀 Space Shooter 2D — Astra Odyssey

A Python + Pygame 2D space-shooter game with a cosmic battlefield, Astra weapons, power-ups, boss battles, particles, sound effects, and a persistent SQLite leaderboard.

## ✨ Features

- 🚀 Spaceship movement with **Arrow Keys / WASD**
- 🔥 Shooting with **SPACE**
- ⚡ Astra weapon progression:
   - Surya Laser
   - Agni Astra
   - Indra Astra
   - Brahmastra

- 👾 Normal and stronger alien enemies
- 👹 Ravana boss battle every 5th level
- 🛡️ Kavach shield power-up
- ❤️ Extra-life power-up
- ✨ 2X score/weapon boost power-up
- 🏆 SQLite leaderboard
- 💥 Particle effects and screen shake
- 🔊 Procedurally generated sound effects
- ⏸️ Pause / resume
- 🖥️ Fullscreen toggle
- 🔄 Restart/continue system
- 🧪 Pytest test suite

## 🎮 Controls

| Key | Action |
|---|---|
| Arrow Keys / WASD | Move spaceship |
| SPACE | Fire |
| P | Pause / Resume |
| R | Restart after game over |
| F | Fullscreen |
| ENTER | Start / new game |
| 1–9 | Delete leaderboard entry |
| C | Clear leaderboard |
| ESC | Quit / back |

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd Space_Shooter_Astra_Odyssey
```

### 2. Create virtual environment (recommended)

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For development/testing:

```bash
pip install -r requirements-dev.txt
```

## ▶️ Run the game

```bash
python main.py
```

The game creates `scores.db` automatically when the leaderboard database is first used. The local database is intentionally ignored by Git.

## 🧪 Run tests

```bash
pytest
```

## 📁 Project Structure

```text
Space_Shooter_Astra_Odyssey/
├── .github/
│   └── workflows/
│       └── tests.yml
├── docs/
│   ├── PROJECT_STRUCTURE.md
│   └── TESTING.md
├── tests/
│   ├── test_database.py
│   └── test_game_config.py
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── database.py
├── main.py
├── pytest.ini
├── requirements-dev.txt
└── requirements.txt
```

## 🧠 Architecture

- `main.py` — game loop, player, enemies, bullets, power-ups, boss, rendering and game states.
- `database.py` — SQLite leaderboard operations.
- `tests/` — automated tests for the database and important game configuration.
- `docs/` — project and testing documentation.
- `.github/workflows/tests.yml` — GitHub Actions workflow that installs dependencies and runs tests.

## 📌 Notes

The game draws its sprites and sound effects programmatically, so no external image/audio asset folder is required for the current version.
