"""Space Shooter 2D - Cosmic Battlefield & Astra Odyssey.

Controls:
  Arrows / WASD : Fly Spaceship
  SPACE         : Shoot Astra
  P             : Pause / Resume Mission
  R             : Restart Level (2 Continues Available)
  F             : Toggle Fullscreen
  1-9           : Delete Specific Score from Leaderboard
  C             : Clear All Scores
  ENTER         : Start Game
  ESC           : Quit / Back
"""
import math
import random
import sys
from array import array

import pygame

try:
    from database import ScoreDB
except ImportError:
    class ScoreDB:
        def __init__(self):
            self._s = []
        def top_scores(self):
            return sorted(self._s, key=lambda x: -x[1])[:9]
        def add_score(self, name, score, level):
            self._s.append((name, score, level))
        def delete_score_at(self, idx):
            scores = self.top_scores()
            if 0 <= idx < len(scores):
                target = scores[idx]
                if target in self._s:
                    self._s.remove(target)
        def clear_scores(self):
            self._s.clear()
        def close(self):
            pass

# ----------------------------------------------------------------- settings
pygame.init()
info = pygame.display.Info()
WIDTH = min(1366, max(1024, info.current_w - 60))
HEIGHT = min(768, max(600, info.current_h - 80))
FPS = 60

WHITE = (245, 245, 245)
GRAY = (130, 130, 150)
BLACK = (4, 4, 12)
CYAN = (60, 220, 255)
YELLOW = (255, 225, 70)
RED = (255, 50, 50)
BLOOD_RED = (180, 15, 25)
CRIMSON = (220, 20, 55)
ORANGE = (255, 130, 20)
GREEN = (70, 240, 110)
PINK = (255, 105, 180)
BLUE = (60, 130, 255)
PURPLE = (175, 70, 255)
DARK_PURPLE = (38, 12, 55)
GOLD = (255, 215, 40)
ICE = (140, 225, 255)
VIOLET = (215, 105, 255)

WEAPONS = {
    "arrow": {"name": "Surya Laser", "color": YELLOW, "delay": 210, "speed": 16, "dmg": 1,
              "pierce": False, "sound": "laser"},
    "agni": {"name": "Agni Astra", "color": ORANGE, "delay": 190, "speed": 17, "dmg": 2,
             "pierce": False, "sound": "agni"},
    "indra": {"name": "Indra Astra", "color": ICE, "delay": 170, "speed": 21, "dmg": 2,
              "pierce": True, "sound": "indra"},
    "brahma": {"name": "Brahmastra", "color": VIOLET, "delay": 360, "speed": 24, "dmg": 7,
               "pierce": True, "sound": "brahma"},
}


# ------------------------------------------------------------------ audio engine
def tone(f0, f1, dur, vol=0.45, wave="sine", noise=0.0):
    freq, _fmt, channels = pygame.mixer.get_init()
    n = int(freq * dur)
    buf = array("h")
    phase = 0.0
    for i in range(n):
        t = i / n
        phase += 2 * math.pi * (f0 + (f1 - f0) * t) / freq
        if wave == "square":
            v = 1.0 if math.sin(phase) > 0 else -1.0
        elif wave == "saw":
            v = ((phase / (2 * math.pi)) % 1.0) * 2 - 1
        else:
            v = math.sin(phase)
        v = v * (1 - noise) + random.uniform(-1, 1) * noise
        v *= min(1.0, i / 120) * (1 - t) ** 1.3
        sample = int(32767 * vol * v)
        for _ in range(channels):
            buf.append(sample)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def tone_sequence(notes, vol=0.65):
    freq, _fmt, channels = pygame.mixer.get_init()
    buf = array("h")
    for f, dur, wave in notes:
        n = int(freq * dur)
        phase = 0.0
        for i in range(n):
            t = i / n
            phase += 2 * math.pi * f / freq
            v = 1.0 if (wave == "square" and math.sin(phase) > 0) else math.sin(phase)
            env = math.sin(math.pi * t)
            sample = int(32767 * vol * v * env)
            for _ in range(channels):
                buf.append(sample)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def build_sounds():
    if not pygame.mixer.get_init():
        return {}
    try:
        return {
            "laser": tone(900, 380, 0.09, 0.25, "saw", 0.05),
            "agni": tone(300, 120, 0.26, 0.38, "saw", 0.35),
            "indra": tone(1900, 190, 0.26, 0.32, "square", 0.2),
            "brahma": tone(160, 40, 0.70, 0.65, "saw", 0.45),
            "boom": tone(130, 25, 0.45, 0.55, "sine", 0.8),
            "hit": tone(320, 110, 0.10, 0.35, "square"),
            "hurt": tone(190, 45, 0.40, 0.50, "saw", 0.4),
            "power": tone(380, 1200, 0.26, 0.35, "sine"),
            "level": tone(440, 880, 0.45, 0.40, "square"),
            "roar": tone(90, 45, 1.10, 0.60, "saw", 0.4),
            "delete": tone(600, 200, 0.12, 0.30, "square"),
            "jaishreeram": tone_sequence([
                (294, 0.22, "saw"),
                (370, 0.26, "saw"),
                (440, 0.50, "sine"),
                (587, 0.75, "sine")
            ], vol=0.70)
        }
    except Exception:
        return {}


# ------------------------------------------------------------------ space environment
class NebulaCluster:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.points = [
            (random.randint(-120, 120), random.randint(-80, 80), random.randint(40, 95))
            for _ in range(7)
        ]

    def update(self):
        self.y += 0.15
        if self.y > HEIGHT + 150:
            self.y = -180
            self.x = random.randint(100, WIDTH - 100)

    def draw(self, surf):
        neb_surf = pygame.Surface((320, 240), pygame.SRCALPHA)
        for ox, oy, rad in self.points:
            pygame.draw.circle(neb_surf, (*self.color, 16), (160 + ox, 120 + oy), rad)
        surf.blit(neb_surf, (self.x - 160, self.y - 120))


class Planet:
    def __init__(self, x, y, r, color, ring=False, speed=0.3):
        self.x = float(x)
        self.y = float(y)
        self.r = r
        self.color = color
        self.ring = ring
        self.speed = speed

    def update(self):
        self.y += self.speed
        if self.y - self.r > HEIGHT + 60:
            self.y = -self.r - random.randint(150, 450)
            self.x = random.randint(self.r + 20, WIDTH - self.r - 20)

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surf, (self.color[0] // 3, self.color[1] // 3, self.color[2] // 3), (cx, cy), self.r + 6)
        pygame.draw.circle(surf, self.color, (cx, cy), self.r)
        band_c = (max(0, self.color[0] - 40), max(0, self.color[1] - 40), max(0, self.color[2] - 40))
        pygame.draw.ellipse(surf, band_c, (cx - self.r + 5, cy - self.r // 3, (self.r - 5) * 2, self.r // 2))
        shadow_surf = pygame.Surface((self.r * 2 + 10, self.r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 70), (self.r + 5 + int(self.r * 0.35), self.r + 5), self.r)
        surf.blit(shadow_surf, (cx - self.r - 5, cy - self.r - 5))

        if self.ring:
            pygame.draw.ellipse(surf, GOLD, (cx - int(self.r * 1.65), cy - 10, int(self.r * 3.3), 20), 3)


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.7, 3.2)
        shade = int(80 + self.speed * 48)
        self.color = (shade, shade, shade + 15)
        self.size = 2 if self.speed > 2.5 else 1

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)


# ------------------------------------------------------------------ sprites
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.w, self.h = 60, 68
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
        self.speed = 10.2
        self.lives = 3
        self.shield = 0
        self.last_shot = 0
        self.double_until = 0
        self.invincible_until = 0
        self.thrust_phase = 0
        self.tilt = 0.0

    def update(self, keys):
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self.thrust_phase = (self.thrust_phase + 1) % 12
        self.tilt = self.tilt * 0.75 + dx * 0.25

        self.image.fill((0, 0, 0, 0))
        cx, cy = self.w // 2, self.h // 2
        t = int(self.tilt * 6)

        pygame.draw.polygon(self.image, (45, 60, 95), [(cx, 10), (cx + 28, cy + 18 + t), (cx + 18, cy + 28 + t), (cx, cy + 16)])
        pygame.draw.polygon(self.image, (45, 60, 95), [(cx, 10), (cx - 28, cy + 18 - t), (cx - 18, cy + 28 - t), (cx, cy + 16)])
        pygame.draw.line(self.image, CYAN, (cx, 10), (cx + 28, cy + 18 + t), 2)
        pygame.draw.line(self.image, CYAN, (cx, 10), (cx - 28, cy + 18 - t), 2)

        pygame.draw.polygon(self.image, (195, 210, 235), [(cx, 2), (cx + 13, cy + 8), (cx + 10, cy + 26), (cx - 10, cy + 26), (cx - 13, cy + 8)])
        pygame.draw.polygon(self.image, WHITE, [(cx, 6), (cx + 6, cy + 12), (cx - 6, cy + 12)])

        pygame.draw.ellipse(self.image, (0, 190, 255), (cx - 5, cy - 4, 10, 16))
        pygame.draw.ellipse(self.image, WHITE, (cx - 3, cy - 2, 6, 8))

        for sg in (-8, 8):
            pygame.draw.rect(self.image, (70, 75, 95), (cx + sg - 3, cy + 24, 6, 6))

    def is_invincible(self, now):
        return now < self.invincible_until


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, kind, hostile=False):
        super().__init__()
        self.vx, self.vy = vx, vy
        self.kind = kind
        self.hostile = hostile
        spec = WEAPONS.get(kind)
        self.dmg = spec["dmg"] if spec else 1
        self.pierce = spec["pierce"] if spec else False
        self.hit = set()

        if hostile:
            r = 12 if kind == "fire" else 7
            self.image = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            color = BLOOD_RED if kind == "bolt" else ORANGE
            pygame.draw.circle(self.image, (90, 10, 15), (r + 2, r + 2), r + 2)
            pygame.draw.circle(self.image, color, (r + 2, r + 2), r)
            pygame.draw.circle(self.image, YELLOW, (r + 2, r + 2), max(2, r // 2))
        else:
            self.image = pygame.Surface((28, 38), pygame.SRCALPHA)
            if kind == "arrow":
                pygame.draw.line(self.image, YELLOW, (14, 6), (14, 34), 3)
                pygame.draw.polygon(self.image, WHITE, [(14, 0), (9, 10), (19, 10)])
            elif kind == "agni":
                pygame.draw.line(self.image, ORANGE, (14, 8), (14, 34), 5)
                pygame.draw.circle(self.image, RED, (14, 18), 8)
                pygame.draw.circle(self.image, YELLOW, (14, 8), 5)
                pygame.draw.polygon(self.image, WHITE, [(14, 0), (7, 12), (21, 12)])
            elif kind == "indra":
                pts = [(14, 0), (20, 8), (10, 18), (18, 26), (14, 36)]
                pygame.draw.lines(self.image, ICE, False, pts, 4)
                pygame.draw.lines(self.image, WHITE, False, pts, 2)
                pygame.draw.circle(self.image, WHITE, (14, 5), 4)
            elif kind == "brahma":
                pygame.draw.circle(self.image, VIOLET, (14, 14), 13)
                pygame.draw.circle(self.image, GOLD, (14, 14), 8)
                pygame.draw.circle(self.image, WHITE, (14, 14), 4)
                pygame.draw.line(self.image, GOLD, (14, 18), (14, 36), 4)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if (self.rect.bottom < -50 or self.rect.top > HEIGHT + 50 or
                self.rect.right < -50 or self.rect.left > WIDTH + 50):
            self.kill()


class SavageAlien(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.big = level >= 2 and random.random() < 0.35
        self.hp = self.max_hp = 5 if self.big else 1
        self.points = 40 if self.big else 10
        self.w, self.h = (90, 80) if self.big else (56, 48)
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.base_x = random.randint(self.w, WIDTH - self.w)
        self.rect.center = (self.base_x, -self.h)
        self.y = float(-self.h)
        self.speed_y = random.uniform(2.0, 2.8) + (level * 0.2)
        self.phase = random.uniform(0, math.tau)
        self.amp = random.randint(30, 90)
        self.can_shoot = level >= 2
        self.next_shot = pygame.time.get_ticks() + random.randint(1200, 2800)
        self.flash = 0
        self.render_alien()

    def render_alien(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.w // 2, self.h // 2

        if self.big:
            skin = WHITE if self.flash > 0 else (55, 18, 26)
            for sg in (-1, 1):
                horn = [(cx + sg * 16, cy - 22), (cx + sg * 40, cy - 36), (cx + sg * 34, cy - 10)]
                pygame.draw.polygon(self.image, (18, 14, 20), horn)
                pygame.draw.line(self.image, BLOOD_RED, horn[0], horn[1], 3)
            pygame.draw.polygon(self.image, skin, [(cx - 24, cy - 14), (cx + 24, cy - 14),
                                                   (cx + 16, cy + 20), (cx, cy + 32), (cx - 16, cy + 20)])
            for sg in (-1, 1):
                tusk = [(cx + sg * 12, cy + 16), (cx + sg * 26, cy + 4), (cx + sg * 17, cy + 24)]
                pygame.draw.polygon(self.image, (240, 230, 200), tusk)
            for sg in (-8, 8):
                pygame.draw.ellipse(self.image, RED, (cx + sg - 4, cy - 3, 8, 5))
                pygame.draw.circle(self.image, YELLOW, (cx + sg, cy - 1), 2)
            pygame.draw.circle(self.image, CRIMSON, (cx, cy - 11), 3)
        else:
            skin = WHITE if self.flash > 0 else (42, 14, 32)
            for sg in (-1, 1):
                m = [(cx + sg * 8, cy - 4), (cx + sg * 22, cy - 18), (cx + sg * 18, cy + 8)]
                pygame.draw.polygon(self.image, (22, 18, 25), m)
            pygame.draw.polygon(self.image, skin, [(cx, cy - 18), (cx + 16, cy - 4),
                                                   (cx + 10, cy + 16), (cx, cy + 22),
                                                   (cx - 10, cy + 16), (cx - 16, cy - 4)])
            for sg in (-7, 7):
                pygame.draw.circle(self.image, RED, (cx + sg, cy - 2), 4)
                pygame.draw.circle(self.image, YELLOW, (cx + sg, cy - 2), 2)
            fangs = [(cx - 6, cy + 9), (cx - 3, cy + 15), (cx, cy + 10), (cx + 3, cy + 15), (cx + 6, cy + 9)]
            pygame.draw.lines(self.image, WHITE, False, fangs, 2)

    def update(self):
        self.y += self.speed_y
        self.phase += 0.045
        self.rect.x = int(self.base_x + math.sin(self.phase) * self.amp)
        self.rect.y = int(self.y)
        if self.flash > 0:
            self.flash -= 1
            self.render_alien()
        if self.rect.top > HEIGHT + 40:
            self.kill()


class RavanaBoss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.hp = self.max_hp = 50 + 6 * level
        self.w, self.h = 300, 130
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(WIDTH // 2, -120))
        self.target_y = 125
        self.t = 0
        self.flash = 0
        self.next_shot = pygame.time.get_ticks() + 1800
        self.render_boss()

    def render_boss(self):
        self.image.fill((0, 0, 0, 0))
        skin = WHITE if self.flash > 0 else (195, 60, 40)
        cx, cy = self.w // 2, self.h // 2 + 15

        pygame.draw.ellipse(self.image, (85, 10, 20), (cx - 135, cy - 46, 270, 90))
        pygame.draw.polygon(self.image, GOLD, [(cx - 44, cy + 8), (cx + 44, cy + 8),
                                               (cx + 26, cy + 44), (cx - 26, cy + 44)])
        pygame.draw.circle(self.image, BLOOD_RED, (cx, cy + 24), 10)

        for i in range(9):
            ang = math.radians(190 + i * (160 / 8))
            hx = int(cx + math.cos(ang) * 110)
            hy = int(cy - 22 + math.sin(ang) * 36)
            pygame.draw.circle(self.image, skin, (hx, hy), 14)
            pygame.draw.polygon(self.image, GOLD, [(hx - 8, hy - 8), (hx, hy - 22), (hx + 8, hy - 8)])
            for sg in (-3, 3):
                pygame.draw.circle(self.image, RED, (hx + sg, hy - 2), 2)

        pygame.draw.circle(self.image, skin, (cx, cy - 15), 24)
        crown = [(cx - 22, cy - 28), (cx - 14, cy - 50), (cx, cy - 35), (cx + 14, cy - 50), (cx + 22, cy - 28)]
        pygame.draw.polygon(self.image, GOLD, crown)
        pygame.draw.circle(self.image, BLOOD_RED, (cx, cy - 35), 4)
        pygame.draw.circle(self.image, YELLOW, (cx, cy - 22), 3)
        for sg in (-8, 8):
            pygame.draw.circle(self.image, RED, (cx + sg, cy - 15), 4)
            pygame.draw.circle(self.image, YELLOW, (cx + sg, cy - 15), 2)
        pygame.draw.line(self.image, (35, 10, 10), (cx - 13, cy - 5), (cx + 13, cy - 5), 3)

    def update(self):
        if self.rect.centery < self.target_y:
            self.rect.centery += 2
        else:
            self.t += 1
            self.rect.centerx = int(WIDTH // 2 + math.sin(self.t * 0.025) * 240)
            self.rect.centery = int(self.target_y + math.sin(self.t * 0.04) * 20)

        if self.flash > 0:
            self.flash -= 1
            self.render_boss()


class PlanetPowerUp(pygame.sprite.Sprite):
    def __init__(self, center, kind):
        super().__init__()
        self.kind = kind
        self.size = 44
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.spin = random.uniform(0, math.tau)
        self.render_mini_planet()

    def render_mini_planet(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        r = 15

        if self.kind == "double":
            pygame.draw.circle(self.image, (30, 140, 60, 90), (cx, cy), r + 4)
            pygame.draw.circle(self.image, (25, 175, 75), (cx, cy), r)
            pygame.draw.ellipse(self.image, (12, 100, 42), (cx - r + 3, cy - 4, (r - 3) * 2, 7))
            pygame.draw.ellipse(self.image, GOLD, (cx - 20, cy - 5, 40, 10), 2)
            font = pygame.font.Font(None, 20)
            txt = font.render("2X", True, WHITE)
            self.image.blit(txt, txt.get_rect(center=(cx, cy)))

        elif self.kind == "life":
            pygame.draw.circle(self.image, (220, 70, 150, 90), (cx, cy), r + 4)
            pygame.draw.circle(self.image, (215, 65, 140), (cx, cy), r)
            pygame.draw.circle(self.image, (160, 30, 95), (cx - 5, cy - 4), 6)
            pygame.draw.circle(self.image, (255, 160, 210), (cx + 5, cy + 4), 5)
            pygame.draw.circle(self.image, WHITE, (cx, cy), r, 1)
            font = pygame.font.Font(None, 26)
            txt = font.render("+", True, WHITE)
            self.image.blit(txt, txt.get_rect(center=(cx, cy - 1)))

        elif self.kind == "shield":
            pygame.draw.circle(self.image, (50, 180, 230, 90), (cx, cy), r + 4)
            pygame.draw.circle(self.image, (40, 160, 220), (cx, cy), r)
            pygame.draw.ellipse(self.image, (20, 90, 150), (cx - r + 3, cy - 5, (r - 3) * 2, 9))
            pygame.draw.ellipse(self.image, ICE, (cx - 18, cy - 4, 36, 8), 2)
            font = pygame.font.Font(None, 20)
            txt = font.render("K", True, GOLD)
            self.image.blit(txt, txt.get_rect(center=(cx, cy)))

    def update(self):
        self.rect.y += 2
        self.spin += 0.05
        if self.rect.top > HEIGHT + 20:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        size = random.randint(3, 7)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.x, self.y = float(pos[0]), float(pos[1])
        self.rect = self.image.get_rect(center=pos)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.8, 6.5)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.life = self.max_life = random.randint(20, 38)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        self.life -= 1
        if self.life <= 0:
            self.kill()
        else:
            self.image.set_alpha(int(255 * self.life / self.max_life))


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos, text, color, font):
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=pos)
        self.life = 45

    def update(self):
        self.rect.y -= 1
        self.life -= 1
        self.image.set_alpha(max(0, int(255 * self.life / 45)))
        if self.life <= 0:
            self.kill()


# --------------------------------------------------------------------- Game Engine
class Game:
    def __init__(self, db=None):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Space Shooter 2D - Astra Odyssey")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 84)
        self.font_big = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 26)
        self.sounds = build_sounds()
        self.db = db if db is not None else ScoreDB()

        self.stars = [Star() for _ in range(130)]
        self.planets = [
            Planet(WIDTH * 0.18, 90, 44, (190, 85, 55), speed=0.25),
            Planet(WIDTH * 0.78, 440, 72, (200, 165, 115), ring=True, speed=0.35),
            Planet(WIDTH * 0.45, -180, 52, (65, 125, 215), speed=0.2)
        ]
        self.nebulae = [
            NebulaCluster(WIDTH * 0.25, 200, (60, 100, 200)),
            NebulaCluster(WIDTH * 0.75, 550, (160, 50, 190))
        ]

        self.dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.dim.fill((0, 0, 16, 175))
        self.state = "menu"
        self.return_state = "menu"
        self.player_name = ""
        self.scores = self.db.top_scores()
        self.restarts_left = 2
        self.reset()

    def toggle_fullscreen(self):
        """Safe fullscreen toggle for all Windows/Pygame setups."""
        self.fullscreen = not self.fullscreen
        try:
            if self.fullscreen:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
            else:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        except Exception:
            # Fallback agar resolution direct switch na le
            self.fullscreen = False
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    def delete_single_score(self, idx):
        if hasattr(self.db, "delete_score_at"):
            self.db.delete_score_at(idx)
        else:
            scores = self.db.top_scores()
            if 0 <= idx < len(scores):
                target = scores[idx]
                if hasattr(self.db, "delete_score"):
                    self.db.delete_score(target[0], target[1])
        self.scores = self.db.top_scores()
        self.play("delete")

    def reset(self, hard_reset=True):
        if hard_reset:
            self.score = 0
            self.level = 1
            self.restarts_left = 2

        self.player = Spaceship()
        self.aliens = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.floaters = pygame.sprite.Group()
        self.boss = None
        self.kills_this_level = 0
        self.last_spawn = pygame.time.get_ticks()
        self.banner_until = 0
        self.banner_text = ""
        self.shake_until = 0
        self.last_weapon = "arrow"
        self.astra_banner_until = 0
        self.astra_banner_text = ""
        self.astra_banner_color = WHITE
        self.victory_banner_until = 0
        self.next_score_threshold = ((self.score // 200) + 1) * 200

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def start_game(self):
        self.reset(hard_reset=True)
        self.player_name = ""
        self.state = "playing"
        self.banner_text = "LEVEL 1"
        self.banner_until = pygame.time.get_ticks() + 1500

    def end_game(self):
        self.explode(self.player.rect.center, CYAN, 45)
        self.play("boom")
        if self.score > 0:
            self.state = "name_entry"
        else:
            self.state = "gameover"
            self.scores = self.db.top_scores()

    def quit(self):
        self.db.close()
        pygame.quit()
        sys.exit()

    @property
    def spawn_delay(self):
        base = max(300, 950 - self.level * 75)
        return base * 2.8 if self.boss else base

    @property
    def kills_needed(self):
        return 8 + 2 * self.level

    def explode(self, pos, color, count=16):
        for _ in range(count):
            self.particles.add(Particle(pos, color))

    def next_level(self):
        self.level += 1
        self.kills_this_level = 0
        now = pygame.time.get_ticks()
        self.banner_text = f"LEVEL {self.level}"
        self.banner_until = now + 1600
        self.play("level")
        if self.level % 5 == 0:
            self.boss = RavanaBoss(self.level)
            self.banner_text = "RAVANA HAS ENTERED THE SECTOR!"
            self.banner_until = now + 2500
            self.play("roar")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_f:
                self.toggle_fullscreen()
                continue

            if event.key == pygame.K_p:
                if self.state == "playing":
                    self.state = "paused"
                elif self.state == "paused":
                    self.state = "playing"
                continue

            if event.key == pygame.K_ESCAPE:
                if self.state == "confirm_clear":
                    self.state = self.return_state
                    continue
                if self.state == "paused":
                    self.state = "playing"
                    continue
                self.quit()

            if self.state in ("menu", "gameover"):
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    self.delete_single_score(idx)
                    continue

                if event.key == pygame.K_RETURN:
                    self.start_game()
                elif event.key == pygame.K_c:
                    self.return_state = self.state
                    self.state = "confirm_clear"
                elif event.key == pygame.K_r and self.state == "gameover":
                    if self.restarts_left > 0:
                        self.restarts_left -= 1
                        self.reset(hard_reset=False)
                        self.state = "playing"
                    else:
                        self.start_game()

            elif self.state == "confirm_clear":
                if event.key == pygame.K_y:
                    self.db.clear_scores()
                    self.scores = []
                    self.state = self.return_state
                elif event.key == pygame.K_n:
                    self.state = self.return_state

            elif self.state == "name_entry":
                self.handle_name_input(event)

    def handle_name_input(self, event):
        if event.key == pygame.K_RETURN:
            name = self.player_name.strip() or "PILOT"
            self.db.add_score(name, self.score, self.level)
            self.scores = self.db.top_scores()
            self.state = "gameover"
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif event.unicode and event.unicode.isprintable() and len(self.player_name) < 12:
            self.player_name += event.unicode

    def current_weapon(self, now):
        if (self.boss and self.boss.hp > 0) or self.level >= 10:
            return "brahma"
        if self.level > 5:
            return "indra"
        if now < self.player.double_until:
            return "agni"
        return "arrow"

    def fire_weapon(self, now, kind):
        p = self.player
        spec = WEAPONS[kind]
        if now - p.last_shot < spec["delay"]:
            return
        p.last_shot = now

        offsets = (-16, 16) if now < p.double_until else (0,)
        for ox in offsets:
            self.player_bullets.add(Bullet(p.rect.centerx + ox, p.rect.top - 5, 0, -spec["speed"], kind))
        self.play(spec["sound"])

    def update(self):
        for star in self.stars:
            star.update()
        for planet in self.planets:
            planet.update()
        for neb in self.nebulae:
            neb.update()

        self.particles.update()
        self.floaters.update()

        if self.state != "playing":
            return

        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        weapon = self.current_weapon(now)
        if weapon != self.last_weapon:
            if weapon != "arrow":
                self.astra_banner_text = f"{WEAPONS[weapon]['name'].upper()} ENGAGED!"
                self.astra_banner_color = WEAPONS[weapon]["color"]
                self.astra_banner_until = now + 1900
                self.play("power")
            self.last_weapon = weapon

        if keys[pygame.K_SPACE]:
            self.fire_weapon(now, weapon)

        if self.score >= self.next_score_threshold:
            self.powerups.add(PlanetPowerUp((random.randint(80, WIDTH - 80), -20), "double"))
            self.next_score_threshold += 200

        if now - self.last_spawn > self.spawn_delay:
            self.aliens.add(SavageAlien(self.level))
            self.last_spawn = now

        self.aliens.update()
        self.player_bullets.update()
        self.enemy_bullets.update()
        self.powerups.update()

        if self.boss:
            self.boss.update()
            if now >= self.boss.next_shot:
                for vx in (-5, -2.5, 0, 2.5, 5):
                    self.enemy_bullets.add(Bullet(self.boss.rect.centerx, self.boss.rect.bottom, vx, 7.5, "fire", hostile=True))
                self.boss.next_shot = now + 1150
                self.play("agni")

        for a in self.aliens:
            if a.can_shoot and now >= a.next_shot and a.rect.top > 10:
                dx = 0
                if self.player.rect.centerx > a.rect.centerx + 20:
                    dx = 2.0
                elif self.player.rect.centerx < a.rect.centerx - 20:
                    dx = -2.0
                self.enemy_bullets.add(Bullet(a.rect.centerx, a.rect.bottom, dx, 7.0, "bolt", hostile=True))
                a.next_shot = now + random.randint(1500, 3200)

        self.check_collisions(now)

    def check_collisions(self, now):
        for b in list(self.player_bullets):
            hits = pygame.sprite.spritecollide(b, self.aliens, False)
            for alien in hits:
                if id(alien) in b.hit:
                    continue
                b.hit.add(id(alien))
                alien.hp -= b.dmg
                alien.flash = 4
                self.explode(b.rect.center, WEAPONS[b.kind]["color"], 8)
                self.play("hit")
                if alien.hp <= 0:
                    self.destroy_alien(alien)
                if not b.pierce:
                    b.kill()
                    break

        if self.boss:
            boss_hits = pygame.sprite.spritecollide(self.boss, self.player_bullets, False)
            for b in boss_hits:
                if id(self.boss) not in b.hit:
                    b.hit.add(id(self.boss))
                    self.boss.hp -= b.dmg
                    self.boss.flash = 4
                    self.explode(b.rect.center, WEAPONS[b.kind]["color"], 12)
                    self.play("hit")
                    if not b.pierce:
                        b.kill()
                    if self.boss.hp <= 0:
                        self.defeat_boss()
                        break

        if not self.player.is_invincible(now):
            hit = False
            alien_hit = pygame.sprite.spritecollide(self.player, self.aliens, True)
            if alien_hit:
                self.explode(alien_hit[0].rect.center, PURPLE, 24)
                hit = True

            bullet_hit = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if bullet_hit:
                hit = True

            if hit:
                if self.player.shield > 0:
                    self.player.shield -= 1
                    self.shake_until = now + 120
                    self.explode(self.player.rect.center, CYAN, 14)
                    self.floaters.add(FloatingText(self.player.rect.center, f"KAVACH: {self.player.shield}", CYAN, self.font_small))
                    self.player.invincible_until = now + 500
                else:
                    self.damage_player(now)

        for pu in pygame.sprite.spritecollide(self.player, self.powerups, True):
            self.play("power")
            if pu.kind == "double":
                self.player.double_until = now + 9000
                self.floaters.add(FloatingText(self.player.rect.center, "2X BOOST WORLD!", GREEN, self.font_small))
            elif pu.kind == "life":
                self.player.lives = min(5, self.player.lives + 1)
                self.floaters.add(FloatingText(self.player.rect.center, "+1 EDEN LIFE!", PINK, self.font_small))
            elif pu.kind == "shield":
                self.player.shield = 3
                self.floaters.add(FloatingText(self.player.rect.center, "KAVACH (3 HITS)", CYAN, self.font_small))

    def destroy_alien(self, alien):
        self.score += alien.points
        self.floaters.add(FloatingText(alien.rect.center, f"+{alien.points}", YELLOW, self.font_small))
        self.explode(alien.rect.center, BLOOD_RED if alien.big else ORANGE, 24 if alien.big else 15)
        self.shake_until = pygame.time.get_ticks() + 110
        self.play("boom")
        if random.random() < 0.15:
            kind = "life" if random.random() < 0.7 else "shield"
            self.powerups.add(PlanetPowerUp(alien.rect.center, kind))
        alien.kill()
        self.kills_this_level += 1
        if self.level % 5 != 0 and self.kills_this_level >= self.kills_needed:
            self.next_level()

    def defeat_boss(self):
        now = pygame.time.get_ticks()
        self.score += 1000
        self.play("jaishreeram")
        self.victory_banner_until = now + 3500
        self.floaters.add(FloatingText(self.boss.rect.center, "+1000 JAI SHREE RAM!", GOLD, self.font_big))

        for _ in range(14):
            rx = self.boss.rect.centerx + random.randint(-110, 110)
            ry = self.boss.rect.centery + random.randint(-50, 50)
            self.explode((rx, ry), random.choice([GOLD, RED, ORANGE, VIOLET]), 30)

        self.shake_until = now + 700
        self.powerups.add(PlanetPowerUp(self.boss.rect.center, "life"))
        self.boss = None
        self.enemy_bullets.empty()
        self.next_level()

    def damage_player(self, now):
        self.player.lives -= 1
        self.player.invincible_until = now + 1500
        self.explode(self.player.rect.center, CYAN, 24)
        self.shake_until = now + 200
        self.play("hurt")
        if self.player.lives <= 0:
            self.end_game()

    def draw_text(self, text, font, color, center):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=center))

    def draw_space_background(self, surf):
        cycle = (self.level - 1) // 2
        if cycle == 0:
            top_c = (5, 5, 20)
            bot_c = (15, 22, 50)
        elif cycle == 1:
            top_c = (16, 6, 28)
            bot_c = (42, 16, 62)
        elif cycle == 2:
            top_c = (24, 6, 14)
            bot_c = (60, 15, 28)
        else:
            top_c = (20, 14, 6)
            bot_c = (52, 32, 14)

        for y in range(0, HEIGHT, 4):
            factor = y / HEIGHT
            r = int(top_c[0] + (bot_c[0] - top_c[0]) * factor)
            g = int(top_c[1] + (bot_c[1] - top_c[1]) * factor)
            b = int(top_c[2] + (bot_c[2] - top_c[2]) * factor)
            pygame.draw.rect(surf, (r, g, b), (0, y, WIDTH, 4))

    def draw_hud(self, now):
        w = WEAPONS[self.last_weapon]
        self.screen.blit(self.font_small.render(f"Score: {self.score}", True, WHITE), (18, 14))
        self.screen.blit(self.font_small.render(f"Sector Level: {self.level}", True, CYAN), (18, 42))
        self.screen.blit(self.font_small.render(f"Active Astra: {w['name']}", True, w["color"]), (18, 70))

        lives_surf = self.font_small.render(f"Hull Lives: {self.player.lives}", True, PINK)
        self.screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 18, 14))

        p_hint = self.font_small.render("P: Pause  |  F: Fullscreen", True, GRAY)
        self.screen.blit(p_hint, (WIDTH - p_hint.get_width() - 18, 42))

        if self.player.shield > 0:
            shield_txt = self.font_small.render(f"Kavach Shield: {'[O] ' * self.player.shield}", True, CYAN)
            self.screen.blit(shield_txt, (18, 98))

        if now < self.player.double_until:
            secs = (self.player.double_until - now) // 1000 + 1
            txt = self.font_small.render(f"2X Boost World: {secs}s", True, GREEN)
            self.screen.blit(txt, (WIDTH - txt.get_width() - 18, 70))

        if self.boss:
            bw = 420
            x0 = WIDTH // 2 - bw // 2
            pygame.draw.rect(self.screen, (50, 10, 15), (x0, 16, bw, 16))
            pygame.draw.rect(self.screen, BLOOD_RED, (x0, 16, int(bw * max(0, self.boss.hp) / self.boss.max_hp), 16))
            pygame.draw.rect(self.screen, GOLD, (x0, 16, bw, 16), 2)
            self.draw_text("RAVANA BOSS - DEPLOY BRAHMASTRA!", self.font_small, GOLD, (WIDTH // 2, 46))

        if now < self.astra_banner_until:
            self.draw_text(self.astra_banner_text, self.font_big, self.astra_banner_color, (WIDTH // 2, 120))

        if now < self.banner_until:
            self.draw_text(self.banner_text, self.font_title, YELLOW, (WIDTH // 2, HEIGHT // 2 - 35))

        if now < self.victory_banner_until:
            self.draw_text("|| JAI SHREE RAM ||", self.font_title, GOLD, (WIDTH // 2, HEIGHT // 2 - 70))
            self.draw_text("RAVANA DESTROYED - VICTORY SECURED!", self.font_med, WHITE, (WIDTH // 2, HEIGHT // 2 - 15))

    def draw_leaderboard(self, top_y):
        self.draw_text("ACE PILOTS LEADERBOARD", self.font_med, YELLOW, (WIDTH // 2, top_y))
        if not self.scores:
            self.draw_text("No cosmic flight records yet!", self.font_small, GRAY, (WIDTH // 2, top_y + 36))
            return

        self.draw_text("(Press number 1-9 to delete individual score)", self.font_small, GRAY, (WIDTH // 2, top_y + 32))
        for i, (name, score, level) in enumerate(self.scores):
            row = f"[{i + 1}]  {name:<12} {score:>7}   (Level {level})"
            self.draw_text(row, self.font_small, WHITE, (WIDTH // 2, top_y + 60 + i * 26))

    def draw(self):
        now = pygame.time.get_ticks()
        offset = (random.randint(-4, 4), random.randint(-4, 4)) if now < self.shake_until else (0, 0)

        play_surface = pygame.Surface((WIDTH, HEIGHT))
        self.draw_space_background(play_surface)

        for neb in self.nebulae:
            neb.draw(play_surface)
        for planet in self.planets:
            planet.draw(play_surface)
        for star in self.stars:
            pygame.draw.circle(play_surface, star.color, (int(star.x), int(star.y)), star.size)

        if self.state in ("playing", "paused", "name_entry", "gameover"):
            self.powerups.draw(play_surface)
            self.aliens.draw(play_surface)
            if self.boss:
                play_surface.blit(self.boss.image, self.boss.rect)
            self.player_bullets.draw(play_surface)
            self.enemy_bullets.draw(play_surface)
            self.particles.draw(play_surface)
            self.floaters.draw(play_surface)

            if self.state in ("playing", "paused"):
                blink = self.player.is_invincible(now) and (now // 100) % 2 == 0
                if not blink:
                    play_surface.blit(self.player.image, self.player.rect)
                    fh = 8 + (self.player.thrust_phase % 6)
                    for sg in (-8, 8):
                        flame = [
                            (self.player.rect.centerx + sg - 3, self.player.rect.bottom - 4),
                            (self.player.rect.centerx + sg, self.player.rect.bottom + fh),
                            (self.player.rect.centerx + sg + 3, self.player.rect.bottom - 4)
                        ]
                        pygame.draw.polygon(play_surface, CYAN, flame)
                        pygame.draw.polygon(play_surface, WHITE, [
                            (self.player.rect.centerx + sg - 1, self.player.rect.bottom - 3),
                            (self.player.rect.centerx + sg, self.player.rect.bottom + fh - 3),
                            (self.player.rect.centerx + sg + 1, self.player.rect.bottom - 3)
                        ])

        self.screen.blit(play_surface, offset)

        if self.state == "menu":
            self.draw_text("SPACE SHOOTER: ASTRA ODYSSEY", self.font_title, CYAN, (WIDTH // 2, 75))
            self.draw_text("Arrows / WASD = Fly   |   SPACE = Fire   |   P = Pause   |   F = Fullscreen",
                           self.font_small, WHITE, (WIDTH // 2, 135))
            self.draw_text("Level 1-5: Laser / Agni  |  Level 6+: Indra Astra  |  Boss Level: Brahmastra",
                           self.font_small, ORANGE, (WIDTH // 2, 162))
            self.draw_text("Power-Up Moons: Emerald 2X (200 pts)  |  Eden Life (+)  |  Kavach Shield", self.font_small, GREEN, (WIDTH // 2, 190))
            self.draw_text("Press ENTER to Launch", self.font_med, YELLOW, (WIDTH // 2, 238))
            self.draw_text("1-9 = Delete Single Score  |  C = Reset All Scores", self.font_small, GRAY, (WIDTH // 2, 270))
            self.draw_leaderboard(310)

        elif self.state == "paused":
            self.screen.blit(self.dim, (0, 0))
            self.draw_text("MISSION PAUSED", self.font_big, YELLOW, (WIDTH // 2, HEIGHT // 2 - 40))
            self.draw_text("Press P or ESC to Resume Mission", self.font_med, WHITE, (WIDTH // 2, HEIGHT // 2 + 30))

        elif self.state == "confirm_clear":
            self.screen.blit(self.dim, (0, 0))
            self.draw_text("PURGE ALL SCORES?", self.font_big, RED, (WIDTH // 2, 220))
            self.draw_text("This cannot be undone.", self.font_small, GRAY, (WIDTH // 2, 280))
            self.draw_text("Y = Confirm Wipe   |   N / ESC = Cancel", self.font_med, YELLOW, (WIDTH // 2, 350))

        elif self.state == "playing":
            self.draw_hud(now)

        elif self.state == "name_entry":
            self.screen.blit(self.dim, (0, 0))
            self.draw_text("VESSEL COMPROMISED", self.font_big, RED, (WIDTH // 2, 180))
            self.draw_text(f"Flight Score: {self.score}", self.font_med, WHITE, (WIDTH // 2, 250))
            self.draw_text("Enter Call-Sign and press ENTER", self.font_small, GRAY, (WIDTH // 2, 310))
            cursor = "_" if (now // 500) % 2 == 0 else " "
            self.draw_text(self.player_name + cursor, self.font_med, CYAN, (WIDTH // 2, 365))

        elif self.state == "gameover":
            self.screen.blit(self.dim, (0, 0))
            self.draw_text("MISSION OVER", self.font_big, RED, (WIDTH // 2, 90))
            self.draw_text(f"Score: {self.score}   Level: {self.level}", self.font_med, WHITE, (WIDTH // 2, 150))
            if self.restarts_left > 0:
                restart_txt = f"R = Resume/Restart ({self.restarts_left} Left)   |   1-9 = Delete Score   |   ENTER = New Game"
            else:
                restart_txt = "Continues Exhausted! ENTER = New Game from Level 1   |   1-9 = Delete Score"
            self.draw_text(restart_txt, self.font_small, YELLOW, (WIDTH // 2, 195))
            self.draw_leaderboard(255)

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().run()