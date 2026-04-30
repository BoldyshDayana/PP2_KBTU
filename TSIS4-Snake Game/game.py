# game.py — All gameplay logic for TSIS4 Snake.
#
# Classes:
#   Grid        — coordinate system, wall detection, inner-cell iteration
#   Snake       — body, movement, growth, collision
#   FoodItem    — weighted food or poison; disappears on timer
#   FoodManager — spawns & manages multiple food items
#   PowerUp     — speed / slow / shield collectible with field lifetime
#   Obstacle    — static wall blocks placed from Level 3 onward
#   GameState   — owns all entities, drives one tick, tracks score/level

import pygame
import random
import math
from config import (
    CELL, COLS, ROWS, HUD_H, FPS,
    UP, DOWN, LEFT, RIGHT,
    DARK_GREEN, GRID_LINE, WALL_COL,
    SNAKE_HEAD_DEFAULT, SNAKE_BODY_DEFAULT,
    FOOD_COLORS, POISON_COLOR, FOOD_LIFETIME,
    PU_COLORS, PU_DURATION, PU_FIELD_LIFE,
    OB_COLOR, OB_START_LV,
    FOODS_PER_LEVEL, WHITE, BLACK, GREY,
)

# ── Grid ──────────────────────────────────────────────────────────────────────

class Grid:
    """
    Grid coordinate system.

    Walls occupy the outer ring (col or row == 0 / COLS-1 / ROWS-1).
    Inner cells are col in [1, COLS-2], row in [1, ROWS-2].
    """

    def __init__(self):
        # Pre-build pixel Rect for every cell (fast lookup)
        self._rects = {
            (c, r): pygame.Rect(c * CELL, r * CELL + HUD_H, CELL, CELL)
            for c in range(COLS)
            for r in range(ROWS)
        }

    def rect(self, col, row) -> pygame.Rect:
        return self._rects[(col, row)]

    def is_wall(self, col, row) -> bool:
        return col == 0 or row == 0 or col == COLS - 1 or row == ROWS - 1

    def is_inside(self, col, row) -> bool:
        return 0 < col < COLS - 1 and 0 < row < ROWS - 1

    def inner_cells(self):
        """Yield all (col, row) inside the border walls."""
        for c in range(1, COLS - 1):
            for r in range(1, ROWS - 1):
                yield (c, r)

    def draw(self, surface, show_grid: bool, obstacles: set):
        """Draw background, optional grid lines, walls, and obstacle blocks."""
        # Grid background
        surface.fill(DARK_GREEN, (0, HUD_H, COLS * CELL, ROWS * CELL))
        # Faint grid lines
        if show_grid:
            for c in range(COLS):
                pygame.draw.line(surface, GRID_LINE,
                                 (c * CELL, HUD_H), (c * CELL, surface.get_height()))
            for r in range(ROWS):
                pygame.draw.line(surface, GRID_LINE,
                                 (0, r * CELL + HUD_H), (surface.get_width(), r * CELL + HUD_H))
        # Border walls
        for c in range(COLS):
            for r in range(ROWS):
                if self.is_wall(c, r):
                    pygame.draw.rect(surface, WALL_COL, self._rects[(c, r)])
        # Internal obstacle blocks
        for (c, r) in obstacles:
            pygame.draw.rect(surface, OB_COLOR, self._rects[(c, r)])
            pygame.draw.rect(surface, (60, 40, 10), self._rects[(c, r)], 2)


# ── Snake ─────────────────────────────────────────────────────────────────────

class Snake:
    """
    Player snake stored as a list of (col, row) cells, index 0 = HEAD.
    Movement is grid-cell-at-a-time, driven by a timer in GameState.
    """

    def __init__(self, head_color=None, body_color=None):
        self.reset(head_color, body_color)

    def reset(self, head_color=None, body_color=None):
        mc, mr = COLS // 2, ROWS // 2
        self.body      = [(mc, mr), (mc-1, mr), (mc-2, mr)]
        self.direction = RIGHT
        self._next_dir = RIGHT
        self._grow     = 0          # segments to add on next N moves
        self.head_color = head_color or SNAKE_HEAD_DEFAULT
        self.body_color = body_color or SNAKE_BODY_DEFAULT

    def set_direction(self, new_dir):
        """Buffer direction; reject U-turn into own neck."""
        head, neck = self.body[0], self.body[1]
        candidate  = (head[0] + new_dir[0], head[1] + new_dir[1])
        if candidate != neck:
            self._next_dir = new_dir

    def move(self) -> tuple:
        """Advance one cell. Returns new head position."""
        self.direction = self._next_dir
        hc, hr = self.body[0]
        dc, dr = self.direction
        new_head = (hc + dc, hr + dr)
        self.body.insert(0, new_head)
        if self._grow > 0:
            self._grow -= 1         # keep tail — snake grows
        else:
            self.body.pop()
        return new_head

    def grow(self, n: int = 1):
        """Schedule growing by n additional segments."""
        self._grow += n

    def shrink(self, n: int = 2):
        """
        Remove n tail segments (poison effect).
        Returns True if the snake is still alive (length > 1).
        """
        for _ in range(n):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) > 1

    def head(self) -> tuple:
        return self.body[0]

    def occupies(self, col, row) -> bool:
        return (col, row) in self.body

    def hit_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def draw(self, surface, grid):
        for i, (c, r) in enumerate(self.body):
            rect  = grid.rect(c, r).inflate(-4, -4)
            color = self.head_color if i == 0 else self.body_color
            pygame.draw.rect(surface, color, rect, border_radius=5)


# ── Food ──────────────────────────────────────────────────────────────────────

class FoodItem:
    """
    One food item on the grid.

    kind:
      "normal"  — weight 1/2/3, adds score and grows snake
      "poison"  — dark red, shrinks snake by 2 segments
    """

    def __init__(self, col, row, weight=1, kind="normal"):
        self.col       = col
        self.row       = row
        self.weight    = weight
        self.kind      = kind
        self.spawn_ms  = pygame.time.get_ticks()
        if kind == "poison":
            self.color = POISON_COLOR
        else:
            self.color = FOOD_COLORS.get(weight, FOOD_COLORS[1])

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_ms >= FOOD_LIFETIME

    def lifetime_frac(self) -> float:
        """1.0 = just spawned, 0.0 = about to vanish."""
        return max(0.0, 1.0 - (pygame.time.get_ticks() - self.spawn_ms) / FOOD_LIFETIME)

    def draw(self, surface, grid):
        rect = grid.rect(self.col, self.row)
        r    = CELL // 2 - 3
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        # Countdown arc — shrinks as food ages
        frac = self.lifetime_frac()
        if frac < 0.95:
            import math as _m
            end_a = _m.radians(90 - frac * 360)
            arc_r = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.arc(surface, (255, 255, 255), arc_r,
                            end_a, _m.radians(90), 2)
        # Weight label (only for normal food)
        if self.kind == "normal":
            f   = pygame.font.SysFont("Arial", 11, bold=True)
            txt = f.render(str(self.weight), True, BLACK)
            surface.blit(txt, txt.get_rect(center=(cx, cy)))


class FoodManager:
    """
    Manages normal food items AND the single poison food.

    Normal food: up to MAX_NORMAL items at once.
    Poison food: up to 1 item at once (spawns with POISON_CHANCE probability
                 each time a new normal food would be spawned).
    """
    MAX_NORMAL   = 3
    POISON_CHANCE = 0.20   # 20 % chance each spawn cycle produces poison

    def __init__(self):
        self.items: list[FoodItem] = []

    def reset(self):
        self.items = []

    def _free_cell(self, grid, snake, obstacles, exclude: set) -> tuple | None:
        """Pick a random inner cell not occupied by snake, walls, obstacles, or existing food."""
        taken = set(snake.body) | obstacles | exclude
        free  = [(c, r) for (c, r) in grid.inner_cells() if (c, r) not in taken]
        return random.choice(free) if free else None

    def update(self, grid, snake, obstacles: set):
        """Remove expired items; spawn replacements."""
        self.items = [f for f in self.items if not f.is_expired()]

        existing_food = {(f.col, f.row) for f in self.items}
        normal_count  = sum(1 for f in self.items if f.kind == "normal")
        poison_count  = sum(1 for f in self.items if f.kind == "poison")

        # Spawn normal food up to MAX_NORMAL
        while normal_count < self.MAX_NORMAL:
            pos = self._free_cell(grid, snake, obstacles, existing_food)
            if pos is None:
                break
            weight = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            self.items.append(FoodItem(pos[0], pos[1], weight, "normal"))
            existing_food.add(pos)
            normal_count += 1

        # Possibly spawn one poison item
        if poison_count == 0 and random.random() < self.POISON_CHANCE:
            pos = self._free_cell(grid, snake, obstacles, existing_food)
            if pos:
                self.items.append(FoodItem(pos[0], pos[1], kind="poison"))

    def eat_at(self, col, row) -> FoodItem | None:
        """Remove and return the food at (col,row), or None."""
        for f in self.items:
            if f.col == col and f.row == row:
                self.items.remove(f)
                return f
        return None

    def draw(self, surface, grid):
        for f in self.items:
            f.draw(surface, grid)


# ── Power-up ──────────────────────────────────────────────────────────────────

class PowerUp:
    """
    A collectible power-up on the grid.
    Vanishes from the field after PU_FIELD_LIFE ms if not collected.
    Effect lasts PU_DURATION ms after collection.
    Only one power-up on the field at a time (enforced by GameState).
    """
    KINDS = ["speed", "slow", "shield"]

    def __init__(self, col, row):
        self.col       = col
        self.row       = row
        self.kind      = random.choice(self.KINDS)
        self.color     = PU_COLORS[self.kind]
        self.spawn_ms  = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_ms >= PU_FIELD_LIFE

    def draw(self, surface, grid):
        rect = grid.rect(self.col, self.row)
        r    = CELL // 2 - 2
        cx, cy = rect.centerx, rect.centery
        # Pulsing ring
        pulse = int(r * (0.7 + 0.3 * math.sin(pygame.time.get_ticks() / 160)))
        pygame.draw.circle(surface, self.color, (cx, cy), pulse)
        pygame.draw.circle(surface, WHITE, (cx, cy), pulse, 2)
        label = {"speed": "S", "slow": "W", "shield": "🛡"}[self.kind]
        f   = pygame.font.SysFont("Arial", 12, bold=True)
        txt = f.render(label, True, BLACK)
        surface.blit(txt, txt.get_rect(center=(cx, cy)))


# ── Obstacles ─────────────────────────────────────────────────────────────────

class ObstacleManager:
    """
    Manages a set of static obstacle blocks inside the arena.
    Blocks are added at each new level (from OB_START_LV onward).
    Guarantees the snake head is never immediately surrounded.
    """
    BLOCKS_PER_LEVEL = 3   # blocks added per new level

    def __init__(self):
        self.blocks: set = set()   # set of (col, row)

    def reset(self):
        self.blocks = set()

    def add_for_level(self, level: int, grid, snake):
        """Place BLOCKS_PER_LEVEL new blocks, avoiding snake body and flood-trap."""
        if level < OB_START_LV:
            return
        taken   = set(snake.body) | self.blocks
        candidates = [
            (c, r) for (c, r) in grid.inner_cells()
            if (c, r) not in taken
        ]
        # Simple anti-trap: exclude cells adjacent to head
        hc, hr = snake.head()
        safe_zone = {(hc+dc, hr+dr) for dc in range(-2,3) for dr in range(-2,3)}
        candidates = [p for p in candidates if p not in safe_zone]

        random.shuffle(candidates)
        added = 0
        for pos in candidates:
            if added >= self.BLOCKS_PER_LEVEL:
                break
            self.blocks.add(pos)
            added += 1


# ── GameState ─────────────────────────────────────────────────────────────────

class GameState:
    """
    Owns every live game object and drives one tick per call.

    Call tick(dt)   — advance game logic by dt ms
    Call draw(surf) — render everything
    Read  .alive    — False = game over
    """

    # Power-up spawn interval
    PU_SPAWN_INTERVAL = 8000   # ms between power-up spawn attempts

    def __init__(self, snake_color: tuple = None,
                 show_grid: bool = True,
                 personal_best: int = 0):
        head_col = snake_color or SNAKE_HEAD_DEFAULT
        # Derive a slightly darker body colour from the head colour
        body_col = tuple(max(0, c - 50) for c in head_col)

        self.grid     = Grid()
        self.snake    = Snake(head_col, body_col)
        self.food_mgr = FoodManager()
        self.obs_mgr  = ObstacleManager()
        self.show_grid    = show_grid
        self.personal_best = personal_best

        # Active power-up state
        self.field_pu: PowerUp | None = None   # the item currently on the grid
        self.active_pu: str | None    = None   # "speed"|"slow"|"shield"|None
        self.pu_end_ms: int           = 0      # when the active effect expires
        self.shield_used: bool        = False  # shield consumed flag

        # Score / progression
        self.score         = 0
        self.foods_eaten   = 0
        self.level         = 1
        self.alive         = True
        self._prev_level   = 1

        # Move timer
        self._base_delay   = 200    # ms between snake moves at level 1
        self._move_timer   = 0

        # Power-up spawn timer
        self._pu_timer     = 0

        # Initial food spawn
        self.food_mgr.update(self.grid, self.snake, self.obs_mgr.blocks)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def move_delay(self) -> int:
        """Move interval in ms, modified by active power-up."""
        base = max(60, self._base_delay - (self.level - 1) * 15)
        if self.active_pu == "speed":
            return max(40, base - 60)
        if self.active_pu == "slow":
            return base + 80
        return base

    def _level_up(self):
        """Advance one level, increase base speed, add obstacles."""
        self.level += 1
        self._base_delay = max(80, self._base_delay - 15)
        self.obs_mgr.add_for_level(self.level, self.grid, self.snake)

    # ── Tick ──────────────────────────────────────────────────────────────────

    def tick(self, dt: int):
        """Advance game logic by dt milliseconds."""
        if not self.alive:
            return

        # Expire active power-up effect
        if self.active_pu and pygame.time.get_ticks() >= self.pu_end_ms:
            self.active_pu = None

        # Expire field power-up
        if self.field_pu and self.field_pu.is_expired():
            self.field_pu = None

        # Move timer
        self._move_timer += dt
        if self._move_timer < self.move_delay:
            return   # not yet time to move
        self._move_timer = 0

        # ── Snake moves ───────────────────────────────────────────────────────
        new_head = self.snake.move()
        hc, hr   = new_head

        # ── Wall collision ────────────────────────────────────────────────────
        if self.grid.is_wall(hc, hr):
            if self.active_pu == "shield" and not self.shield_used:
                self.shield_used  = True
                self.active_pu    = None   # shield consumed
                # Push head back inside (reverse one cell)
                dc, dr = self.snake.direction
                self.snake.body[0] = (hc - dc, hr - dr)
                hc, hr = self.snake.body[0]
            else:
                self.alive = False
                return

        # ── Obstacle collision ────────────────────────────────────────────────
        if (hc, hr) in self.obs_mgr.blocks:
            if self.active_pu == "shield" and not self.shield_used:
                self.shield_used = True
                self.active_pu   = None
                dc, dr = self.snake.direction
                self.snake.body[0] = (hc - dc, hr - dr)
                hc, hr = self.snake.body[0]
            else:
                self.alive = False
                return

        # ── Self-collision ────────────────────────────────────────────────────
        if self.snake.hit_self():
            if self.active_pu == "shield" and not self.shield_used:
                self.shield_used = True
                self.active_pu   = None
                dc, dr = self.snake.direction
                self.snake.body[0] = (hc - dc, hr - dr)
                hc, hr = self.snake.body[0]
            else:
                self.alive = False
                return

        # ── Food collection ───────────────────────────────────────────────────
        eaten = self.food_mgr.eat_at(hc, hr)
        if eaten:
            if eaten.kind == "poison":
                survived = self.snake.shrink(2)
                self.score = max(0, self.score - 5)
                if not survived:
                    self.alive = False
                    return
            else:
                self.snake.grow()
                self.score       += eaten.weight * 10
                self.foods_eaten += 1
                # Level up every FOODS_PER_LEVEL
                if self.foods_eaten % FOODS_PER_LEVEL == 0:
                    self._level_up()

        # ── Power-up collection ───────────────────────────────────────────────
        if self.field_pu and (hc, hr) == (self.field_pu.col, self.field_pu.row):
            kind = self.field_pu.kind
            self.active_pu   = kind
            self.pu_end_ms   = pygame.time.get_ticks() + PU_DURATION
            self.shield_used = False
            self.field_pu    = None
            self.score       += 5   # small bonus for collecting

        # ── Spawn power-up ────────────────────────────────────────────────────
        self._pu_timer += dt
        if self._pu_timer >= self.PU_SPAWN_INTERVAL and self.field_pu is None:
            self._pu_timer = 0
            taken = set(self.snake.body) | self.obs_mgr.blocks
            taken |= {(f.col, f.row) for f in self.food_mgr.items}
            free  = [(c,r) for (c,r) in self.grid.inner_cells() if (c,r) not in taken]
            if free:
                pos = random.choice(free)
                self.field_pu = PowerUp(pos[0], pos[1])

        # ── Refresh food ──────────────────────────────────────────────────────
        self.food_mgr.update(self.grid, self.snake, self.obs_mgr.blocks)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface):
        self.grid.draw(surface, self.show_grid, self.obs_mgr.blocks)
        self.food_mgr.draw(surface, self.grid)
        if self.field_pu:
            self.field_pu.draw(surface, self.grid)
        self.snake.draw(surface, self.grid)