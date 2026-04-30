# All gameplay entities: Road, PlayerCar, EnemyCar,
# Obstacle, RoadEvent, Coin, PowerUp, and GameState.
# Everything is pixel-based
# The HUD occupies the top 44 px


import pygame, random, math

# Layout constants 
SW, SH  = 400, 660      # full window size
HUD_H = 44            # pixels for top HUD bar
ROAD_L = 60            # left kerb x
ROAD_R = 340           # right kerb x
ROAD_W = ROAD_R - ROAD_L   # 280 px
LANE_W = ROAD_W // 4       # 70 px per lane
# Centre x of each of the 4 lanes
LANES   = [ROAD_L + LANE_W * i + LANE_W // 2 for i in range(4)]

# Colours
WHITE = (255,255,255); BLACK = (0,  0,  0)
GREY = (100,100,100); DK_GREY = (55, 55, 55)
GREEN = (0,  180,  0); RED = (200,  0,  0)
YELLOW = (240,200,  0); ORANGE = (230,120,  0)
CYAN = (0, 200,220); BLUE = (30,  80,220)
PURPLE = (150, 0,200); BROWN = (110, 65, 15)

CAR_COLOR_MAP = {
    "blue":   (40, 90, 220),
    "red":    (200, 30, 30),
    "green":  (30, 160, 30),
    "yellow": (220, 200, 0),
}

# Per-difficulty multipliers for speed and spawn rate
DIFF = {
    "easy":   {"speed": 0.70, "spawn": 0.60},
    "normal": {"speed": 1.00, "spawn": 1.00},
    "hard":   {"speed": 1.40, "spawn": 1.55},
}


# Road 

class Road:
    """
    Scrolling road surface with:
    -Three dashed lane-divider columns
    -Hazard zones (oil spills, slow zones, potholes) that scroll down
    -Nitro strips — bright green panels that boost the player on contact
    """
    STRIPE_H = 40
    STRIPE_G = 28

    def __init__(self):
        self.speed = 5.0
        # Three divider column x positions
        div_xs = [ROAD_L + LANE_W * k for k in range(1, 4)]
        self.stripes: list = []
        for cx in div_xs:
            y = 0
            while y < SH:
                self.stripes.append([cx, y])
                y += self.STRIPE_H + self.STRIPE_G
        self.n_per_col    = len(self.stripes) // 3

        self.hazards: list = []   # {"type", "lane", "y", "h"}
        self.nitro_strips: list = []   # {"x", "y", "w"}
        self._hz_t   = 0
        self._hz_del = 3800   # ms between hazard spawns

    def update(self, dt: int, speed: float):
        self.speed = speed

        # Scroll divider stripes — wrap individually
        for s in self.stripes:
            s[1] += speed
            if s[1] > SH:
                s[1] -= (self.STRIPE_H + self.STRIPE_G) * self.n_per_col

        # Spawn hazard zones
        self._hz_t += dt
        if self._hz_t >= self._hz_del:
            self._hz_t = 0
            kind = random.choice(["oil", "slow", "pothole"])
            self.hazards.append({
                "type": kind,
                "lane": random.randint(0, 3),
                "y":    float(-90),
                "h":    random.randint(60, 110),
            })

        # Scroll hazards and nitro strips
        for hz in self.hazards[:]:
            hz["y"] += speed
            if hz["y"] > SH:
                self.hazards.remove(hz)

        for ns in self.nitro_strips[:]:
            ns["y"] += speed
            if ns["y"] > SH:
                self.nitro_strips.remove(ns)

    def spawn_nitro_strip(self):
        """Place a nitro boost strip in a random lane."""
        lane = random.choice(LANES)
        self.nitro_strips.append({"x": lane - LANE_W // 2,
                                   "y": float(-50), "w": LANE_W})

    def hz_rect(self, hz) -> pygame.Rect:
        lx = ROAD_L + hz["lane"] * LANE_W
        return pygame.Rect(lx, int(hz["y"]), LANE_W, hz["h"])

    def ns_rect(self, ns) -> pygame.Rect:
        return pygame.Rect(int(ns["x"]), int(ns["y"]), ns["w"], 50)

    def draw(self, surface):
        # Green verges
        pygame.draw.rect(surface, GREEN,  (0, HUD_H, ROAD_L, SH))
        pygame.draw.rect(surface, GREEN,  (ROAD_R, HUD_H, SW - ROAD_R, SH))
        # Grey tarmac
        pygame.draw.rect(surface, GREY,   (ROAD_L, HUD_H, ROAD_W, SH))

        # Hazard tints
        for hz in self.hazards:
            r = self.hz_rect(hz)
            r.y = max(HUD_H, r.y)
            if hz["type"] == "oil":
                ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                ov.fill((100, 0, 180, 85))
                surface.blit(ov, (r.x, r.y))
            elif hz["type"] == "slow":
                ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                ov.fill((210, 70, 0, 70))
                surface.blit(ov, (r.x, r.y))
            elif hz["type"] == "pothole":
                pygame.draw.ellipse(surface, DK_GREY, r.inflate(-22, -28))

        # Nitro strips
        for ns in self.nitro_strips:
            r = self.ns_rect(ns)
            ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            ov.fill((0, 255, 90, 100))
            surface.blit(ov, (r.x, max(HUD_H, r.y)))
            for dy in range(0, r.h, 10):
                pygame.draw.line(surface, (0, 255, 70),
                                 (r.x + 4, r.y + dy), (r.x + r.w - 4, r.y + dy), 2)

        # Lane-divider dashes
        for s in self.stripes:
            pygame.draw.rect(surface, WHITE, (s[0] - 3, s[1], 6, self.STRIPE_H))


# Player

class PlayerCar:
    """
    Player vehicle
    Power-up states: nitro (timed speed boost), shield (one-hit absorb)
    """
    W, H = 40, 70
    BASE_SPEED = 5     # lateral px per frame

    def __init__(self, color_name: str = "blue"):
        self.x = SW // 2 - self.W // 2
        self.y = SH - self.H - 20
        self.rect = pygame.Rect(self.x, self.y, self.W, self.H)
        self.color = CAR_COLOR_MAP.get(color_name, BLUE)
        # Power-up state
        self.nitro_active = False
        self.nitro_timer = 0.0    # seconds remaining
        self.shield_active = False

    def update(self, keys, dt: int):
        """Move left/right; tick nitro timer; keep inside road."""
        spd = self.BASE_SPEED + (4 if self.nitro_active else 0)
        if keys[pygame.K_LEFT]:  self.x -= spd
        if keys[pygame.K_RIGHT]: self.x += spd
        self.x = max(ROAD_L + 2, min(ROAD_R - self.W - 2, self.x))
        self.rect.x = self.x

        if self.nitro_active:
            self.nitro_timer -= dt / 1000.0
            if self.nitro_timer <= 0:
                self.nitro_active = False

    def activate_nitro(self, duration: float = 4.0):
        self.nitro_active = True
        self.nitro_timer  = duration

    def activate_shield(self):
        self.shield_active = True

    def take_hit(self) -> bool:
        """Returns True = player dies; False = shield absorbed it."""
        if self.shield_active:
            self.shield_active = False
            return False
        return True

    def draw(self, surface):
        # Body
        pygame.draw.rect(surface, self.color, self.rect)
        # Windshield
        pygame.draw.rect(surface, WHITE,
                         (self.x + 5, self.y + 10, self.W - 10, 15))
        # Wheels
        pygame.draw.rect(surface, BLACK, (self.x - 5,           self.y + 10, 8, 20))
        pygame.draw.rect(surface, BLACK, (self.x + self.W - 3,  self.y + 10, 8, 20))
        # Shield aura
        if self.shield_active:
            pygame.draw.rect(surface, CYAN, self.rect.inflate(8, 8), 3, border_radius=6)
        # Nitro flame
        if self.nitro_active:
            fx, fy = self.x + self.W // 2, self.y + self.H
            pygame.draw.polygon(surface, ORANGE,
                                [(fx-8, fy), (fx+8, fy), (fx, fy+20)])
            pygame.draw.polygon(surface, YELLOW,
                                [(fx-4, fy), (fx+4, fy), (fx, fy+12)])


# Enemy car 

class EnemyCar:
    """Downward-scrolling traffic car. Collision ends the run."""
    W, H = 40, 70

    def __init__(self, speed: float):
        self.x = random.choice(LANES) - self.W // 2
        self.y = float(-self.H)
        self.speed = speed
        self.rect = pygame.Rect(int(self.x), int(self.y), self.W, self.H)
        self.color = random.choice([RED, (255,130,0), (160,30,220), (170,0,0)])

    def update(self, speed: float):
        self.y     += speed
        self.rect.y = int(self.y)

    def is_off_screen(self) -> bool:
        return self.y > SH

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE,
                         (self.rect.x+5, self.rect.y+self.H-25, 30, 15))
        pygame.draw.rect(surface, BLACK, (self.rect.x-5, self.rect.y+10, 8, 20))
        pygame.draw.rect(surface, BLACK, (self.rect.x+self.W-3, self.rect.y+10, 8, 20))


# Road obstacle 

class Obstacle:
    """
    barrier, oil drum, or speed bump.
    All kinds except "speed_bump" cost a life on contact.
    """

    KINDS = {
        "barrier": {"w": 60, "h": 18, "col": (255, 75,  0)},
        "oil_drum": {"w": 24, "h": 30, "col": DK_GREY},
        "speed_bump": {"w": 82, "h": 13, "col": (200, 160, 0)},
    }

    def __init__(self, speed: float):
        self.kind  = random.choice(list(self.KINDS))
        spec = self.KINDS[self.kind]
        self.x = float(random.randint(ROAD_L + 8, ROAD_R - spec["w"] - 8))
        self.y = float(-spec["h"])
        self.speed = speed
        self.color = spec["col"]
        self.rect = pygame.Rect(int(self.x), int(self.y), spec["w"], spec["h"])

    def update(self, speed: float):
        self.y     += speed
        self.rect.y = int(self.y)

    def is_off_screen(self) -> bool:
        return self.y > SH

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        if self.kind == "barrier":
            for i in range(0, self.rect.w, 12):
                pygame.draw.line(surface, BLACK,
                                 (self.rect.x+i,   self.rect.y),
                                 (self.rect.x+i+8, self.rect.y+self.rect.h), 3)
        elif self.kind == "oil_drum":
            pygame.draw.ellipse(surface, (90, 90, 90), self.rect.inflate(-4, -6))
        else:  # speed_bump
            for i in range(0, self.rect.w, 10):
                pygame.draw.rect(surface, BLACK,
                                 (self.rect.x+i, self.rect.y+3, 6, self.rect.h-6))


# Road event (moving barrier)

class RoadEvent:
    """
    A short-lived dynamic event: a barrier that slides horizontally
    across lanes, forcing the player to dodge
    """

    def __init__(self, speed: float):
        self.y = float(-28)
        self.x = float(ROAD_L)
        self.spd_y = speed
        self.spd_x = random.choice([-2.2, 2.2])
        self.w, self.h = 52, 18
        self.rect  = pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, speed: float):
        self.y  += speed
        self.x  += self.spd_x
        if self.x < ROAD_L or self.x + self.w > ROAD_R:
            self.spd_x *= -1
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def is_off_screen(self) -> bool:
        return self.y > SH

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 50, 50), self.rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=4)


# Coin 

class Coin:
    """Weighted collectible. Weight 1/2/3 maps to bronze/silver/gold colours"""
    R = 11
    COLORS = {1: (200,150,30), 2: (190,190,190), 3: (255,215,0)}

    def __init__(self, speed: float):
        self.x = random.choice(LANES)
        self.y = float(-self.R)
        self.speed  = speed
        self.weight = random.choices([1,2,3], weights=[60,30,10])[0]
        self.color = self.COLORS[self.weight]
        self.rect = pygame.Rect(self.x-self.R, int(self.y)-self.R,
                                  self.R*2, self.R*2)

    def update(self, speed: float):
        self.y += speed
        self.rect.y = int(self.y) - self.R

    def is_off_screen(self) -> bool:
        return self.y > SH

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, int(self.y)), self.R)
        t = pygame.font.SysFont("Arial", 11, bold=True).render(
                str(self.weight), True, BLACK)
        surface.blit(t, t.get_rect(center=(self.x, int(self.y))))


# Power-up
class PowerUp:
    """
    Collectible power-up (Nitro / Shield / Repair)
    Disappears after LIFETIME_MS if the player misses it
    Only one power-up may be active at a time (enforced by GameState)
    """
    LIFETIME_MS = 5000
    R = 14
    DATA = {
        "nitro":  {"col": ORANGE, "lbl": "N"},
        "shield": {"col": CYAN, "lbl": "S"},
        "repair": {"col": (80, 205, 80), "lbl": "R"},
    }

    def __init__(self, speed: float):
        self.kind  = random.choice(["nitro", "shield", "repair"])
        self.x = random.choice(LANES)
        self.y = float(-self.R)
        self.speed = speed
        self.spawn_ms = pygame.time.get_ticks()
        self.color = self.DATA[self.kind]["col"]
        self.label = self.DATA[self.kind]["lbl"]
        self.rect = pygame.Rect(self.x-self.R, int(self.y)-self.R,
                                    self.R*2, self.R*2)

    def update(self, speed: float):
        self.y += speed
        self.rect.y = int(self.y) - self.R

    def is_off_screen(self) -> bool:  return self.y > SH
    def is_expired(self)    -> bool:
        return pygame.time.get_ticks() - self.spawn_ms >= self.LIFETIME_MS

    def draw(self, surface):
        # Pulsing radius to attract attention
        pulse = int(self.R * (0.75 + 0.25 * math.sin(
                    pygame.time.get_ticks() / 140)))
        pygame.draw.circle(surface, self.color, (self.x, int(self.y)), pulse)
        pygame.draw.circle(surface, WHITE, (self.x, int(self.y)), pulse, 2)
        t = pygame.font.SysFont("Arial", 13, bold=True).render(
                self.label, True, BLACK)
        surface.blit(t, t.get_rect(center=(self.x, int(self.y))))


# GameState

class GameState:
    """
    Owns every live object and drives one game tick per call to tick()
    Read .alive to detect game-over.
    Read .score / .distance / .coins_n / .level for HUD and leaderboard
    """

    # Base spawn intervals (ms) before difficulty scaling
    E_DELAY  = 1500   # enemy
    OB_DELAY = 2600   # obstacle
    CO_DELAY = 1900   # coin
    PU_DELAY = 6200   # power-up
    EV_DELAY = 8500   # road event

    def __init__(self, car_color: str = "blue", difficulty: str = "normal"):
        d = DIFF.get(difficulty, DIFF["normal"])
        self._spd_scale = d["speed"]
        self._spwn_scale = d["spawn"]

        self.road = Road()
        self.player = PlayerCar(car_color)

        self.enemies:   list = []
        self.obstacles: list = []
        self.events:    list = []
        self.coins:     list = []
        self.powerups:  list = []

        # Stats
        self.score = 0
        self.coins_n = 0
        self.distance = 0
        self.level = 1
        self.alive = True

        # Active power-up tracking (only one at a time)
        self.active_pu  = None    # kind string or None
        self.pu_timer = 0.0    # seconds remaining (nitro only)

        # Spawn timers
        self._et  = self._obt = self._ct = self._put = self._evt = 0
        self._dst = 0   # distance accumulator (ms)

        self._base_spd = 5.0 * self._spd_scale

    # Computed helpers 

    @property
    def scroll_speed(self) -> float:
        """Road scroll speed — faster during nitro."""
        s = self._base_spd
        return s * 1.6 if self.player.nitro_active else s

    def _e_delay(self)  -> int:
        return max(500,  int(self.E_DELAY  / self._spwn_scale - self.level * 55))
    def _ob_delay(self) -> int:
        return max(900,  int(self.OB_DELAY / self._spwn_scale - self.level * 70))
    def _co_delay(self) -> int:
        return max(800,  int(self.CO_DELAY / self._spwn_scale))
    def _pu_delay(self) -> int:
        return max(4000, int(self.PU_DELAY / self._spwn_scale))

    # Main tick
    def tick(self, dt: int, keys):
        """Advance the game by dt milliseconds"""
        if not self.alive:
            return

        spd = self.scroll_speed

        # Level = 1 + one level per 15 coins
        self.level = 1 + self.coins_n // 15
        self._base_spd = (5.0 + self.level * 0.45) * self._spd_scale

        # Distance + score-per-metre
        self._dst += dt
        if self._dst >= 100:
            self.distance += 1
            self.score += 1
            self._dst -= 100

        # Tick power-up timer
        if self.active_pu and self.active_pu != "shield":
            self.pu_timer -= dt / 1000.0
            if self.pu_timer <= 0:
                self.active_pu = None
                self.pu_timer  = 0.0

        # Updates 
        self.player.update(keys, dt)
        self.road.update(dt, spd)

        # Spawn enemies
        self._et += dt
        if self._et >= self._e_delay():
            self._et = 0
            e = EnemyCar(spd)
            if not e.rect.colliderect(self.player.rect):
                self.enemies.append(e)

        # Spawn obstacles
        self._obt += dt
        if self._obt >= self._ob_delay():
            self._obt = 0
            o = Obstacle(spd)
            if not o.rect.colliderect(self.player.rect):
                self.obstacles.append(o)

        # Spawn coins
        self._ct += dt
        if self._ct >= self._co_delay():
            self._ct = 0
            self.coins.append(Coin(spd))

        # Spawn power-ups (at most one on screen at a time)
        self._put += dt
        if self._put >= self._pu_delay() and not self.powerups:
            self._put = 0
            self.powerups.append(PowerUp(spd))

        # Spawn road events
        self._evt += dt
        if self._evt >= self.EV_DELAY:
            self._evt = 0
            self.events.append(RoadEvent(spd))
            if random.random() < 0.4:
                self.road.spawn_nitro_strip()

        # Enemy collisions
        for e in self.enemies[:]:
            e.update(spd)
            if e.is_off_screen():
                self.enemies.remove(e)
            elif self.player.rect.colliderect(e.rect):
                self.enemies.remove(e)
                if self.player.take_hit():
                    self.alive = False;  return

        # Obstacle collisions
        for o in self.obstacles[:]:
            o.update(spd)
            if o.is_off_screen():
                self.obstacles.remove(o)
            elif self.player.rect.colliderect(o.rect):
                self.obstacles.remove(o)
                if o.kind != "speed_bump":   # speed bump is cosmetic only
                    if self.player.take_hit():
                        self.alive = False;  return

        # Road-event collisions
        for ev in self.events[:]:
            ev.update(spd)
            if ev.is_off_screen():
                self.events.remove(ev)
            elif self.player.rect.colliderect(ev.rect):
                self.events.remove(ev)
                if self.player.take_hit():
                    self.alive = False;  return

        # Hazard zone effects
        for hz in self.road.hazards:
            if self.road.hz_rect(hz).colliderect(self.player.rect):
                if hz["type"] == "oil" and not self.player.shield_active:
                    self.player.x += random.choice([-3, 3])   # drift effect

        # Nitro strip pickup
        for ns in self.road.nitro_strips[:]:
            if self.road.ns_rect(ns).colliderect(self.player.rect):
                self.road.nitro_strips.remove(ns)
                self._apply_powerup("nitro")

        # Coin collection
        for c in self.coins[:]:
            c.update(spd)
            if c.is_off_screen():
                self.coins.remove(c)
            elif self.player.rect.colliderect(c.rect):
                self.coins.remove(c)
                self.coins_n += 1
                self.score   += c.weight * 10

        # Power-up collection
        for pu in self.powerups[:]:
            pu.update(spd)
            if pu.is_off_screen() or pu.is_expired():
                self.powerups.remove(pu)
            elif self.player.rect.colliderect(pu.rect):
                self.powerups.remove(pu)
                self._apply_powerup(pu.kind)

    # Power-up application

    def _apply_powerup(self, kind: str):
        """Apply effect of collected power-up (only one active at a time)."""
        if kind == "nitro":
            self.player.activate_nitro(4.0)
            self.active_pu = "nitro"
            self.pu_timer  = 4.0
        elif kind == "shield":
            self.player.activate_shield()
            self.active_pu = "shield"
            self.pu_timer  = 0.0    # shield lasts until hit, no countdown
        elif kind == "repair":
            if self.obstacles:
                self.obstacles.pop(0)   # clear nearest obstacle
            self.score += 50
            self.active_pu = None       # repair is instant

    # Draw 

    def draw(self, surface):
        surface.fill(BLACK)
        self.road.draw(surface)
        for c   in self.coins:     c.draw(surface)
        for pu  in self.powerups:  pu.draw(surface)
        for o   in self.obstacles: o.draw(surface)
        for ev  in self.events:    ev.draw(surface)
        for e   in self.enemies:   e.draw(surface)
        self.player.draw(surface)