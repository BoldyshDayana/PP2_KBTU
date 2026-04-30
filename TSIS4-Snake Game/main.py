# State machine and all game screens for TSIS4 Snake.
# Screens / states:
#   MENU  → USERNAME (same screen) → PLAYING → GAME_OVER
#   MENU  → LEADERBOARD → MENU
#   MENU  → SETTINGS    → MENU
#
# DB calls happen at:
#   startup — init_db(), personal-best fetch
#   game-over — save_session()
#   leaderboard - get_top10()

import pygame, sys, json, os
from config import (
    CELL, COLS, ROWS, HUD_H, SCREEN_W, SCREEN_H, FPS,
    UP, DOWN, LEFT, RIGHT,
    BG, HUD_BG, WHITE, BLACK, GREY, DARK_GREY, LIGHT_GREY,
    SNAKE_HEAD_DEFAULT, PU_COLORS, PU_DURATION,
)
from game import GameState
from db import init_db, save_session, get_top10, get_personal_best

SETTINGS_FILE = "settings.json"

# Default / load settings

DEFAULT_SETTINGS = {
    "snake_color": list(SNAKE_HEAD_DEFAULT),
    "show_grid": True,
    "sound": False,
}

def load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings_file(s: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f, indent=2)
    except IOError as e:
        print(f"[settings] save failed: {e}")


# Pygame init ─

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake — TSIS 4")
clock  = pygame.time.Clock()

# Fonts
def _f(sz, bold=False): return pygame.font.SysFont("Arial", sz, bold=bold)
F_BIG = _f(40, True)
F_MED = _f(22, True)
F_SM = _f(16)
F_TINY = _f(13)

# Colours
TEAL   = (0, 155, 140)
RED_C  = (190,  30, 30)
GREEN  = ( 30, 170, 30)
BLUE_C = (40,  80, 210)
YELLOW = (230, 190, 0)
CYAN   = (0, 200, 210)
ORANGE = (230, 120, 0)
GOLD   = (255, 200, 0)
SILVER = (200, 200, 200)
BRONZE = (180, 110, 40)

# Simple UI helpers

def _cx(text, font, color, y, surface):
    img = font.render(text, True, color)
    surface.blit(img, (SCREEN_W//2 - img.get_width()//2, y))
    return img.get_height()

def _bg(surface, title=None):
    surface.fill(BG)
    for i in range(0, SCREEN_H, 55):
        pygame.draw.line(surface, (18, 22, 40), (0, i), (SCREEN_W, i))
    if title:
        _cx(title, F_BIG, CYAN, 24, surface)


class Button:
    def __init__(self, label, rect, color=TEAL, tc=WHITE, fs=20):
        self.label = label
        self.rect  = pygame.Rect(rect)
        self.color = color
        self.tc  = tc
        self.fs  = fs

    def draw(self, surface):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        bg    = tuple(min(255, c+30) for c in self.color) if hover else self.color
        pygame.draw.rect(surface, bg,    self.rect, border_radius=7)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=7)
        txt = _f(self.fs, True).render(self.label, True, self.tc)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


class InputBox:
    def __init__(self, rect, placeholder="", max_len=20):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.text = ""
        self.max_len = max_len
        self.active = False

    def handle(self, event) -> bool:
        """Returns True on Enter."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_len and event.unicode.isprintable():
                self.text += event.unicode
        return False

    def draw(self, surface):
        border = CYAN if self.active else GREY
        pygame.draw.rect(surface, (22, 28, 48), self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        disp  = self.text or self.placeholder
        color = WHITE if self.text else DARK_GREY
        txt = F_MED.render(disp, True, color)
        surface.blit(txt, (self.rect.x+8,
                           self.rect.y+(self.rect.h-txt.get_height())//2))


# State constants 
MENU = "menu"; PLAYING = "playing"; GAME_OVER = "game_over"
LEADERBOARD = "leaderboard"; SETTINGS = "settings"

#HUD 

def draw_hud(surface, gs: GameState, username: str):
    """
    Top bar: score, personal best, level on the left/centre/right.
    Active power-up displayed with a countdown bar.
    """
    pygame.draw.rect(surface, HUD_BG, (0, 0, SCREEN_W, HUD_H))
    pygame.draw.line(surface, GREY, (0, HUD_H-1), (SCREEN_W, HUD_H-1))

    # Left
    surface.blit(F_SM.render(f"Score: {gs.score}", True, WHITE), (6, 4))
    surface.blit(F_TINY.render(f"Best:  {gs.personal_best}", True, YELLOW), (6, 24))

    # Centre
    lt = F_MED.render(f"Level {gs.level}", True, CYAN)
    surface.blit(lt, (SCREEN_W//2 - lt.get_width()//2, 4))
    ut = F_TINY.render(username, True, LIGHT_GREY)
    surface.blit(ut, (SCREEN_W//2 - ut.get_width()//2, 26))

    # Right — active power-up
    if gs.active_pu:
        col = PU_COLORS.get(gs.active_pu, WHITE)
        remain = max(0, gs.pu_end_ms - pygame.time.get_ticks()) / 1000
        pt = F_SM.render(f"{gs.active_pu.upper()}  {remain:.1f}s", True, col)
        surface.blit(pt, (SCREEN_W - pt.get_width() - 6, 4))
        # Mini progress bar
        bw = 90; bh = 6
        bx = SCREEN_W - bw - 6; by = 26
        pygame.draw.rect(surface, DARK_GREY, (bx, by, bw, bh), border_radius=3)
        fill = int(bw * remain / (PU_DURATION/1000))
        if fill > 0:
            pygame.draw.rect(surface, col, (bx, by, fill, bh), border_radius=3)


# Main 

def main():
    # DB init (non-fatal)
    db_ok = init_db()
    if not db_ok:
        print("[main] DB unavailable — using leaderboard.json for persistence.")

    settings = load_settings()
    state = MENU
    username = ""
    gs: GameState = None
    personal_best = 0

    # Menu widgets
    cx, bw, bh, gap = SCREEN_W//2, 220, 48, 14
    sy = SCREEN_H//2 - 110
    menu_btns = {
        "play": Button("Play", (cx-bw//2, sy, bw, bh), TEAL),
        "lb":   Button("Leaderboard", (cx-bw//2, sy+bh+gap, bw, bh), BLUE_C),
        "sett": Button("Settings", (cx-bw//2, sy+2*(bh+gap),bw, bh), DARK_GREY),
        "quit": Button("Quit", (cx-bw//2, sy+3*(bh+gap),bw, bh), RED_C),
    }
    ib_name = InputBox((cx-130, SCREEN_H//2+20, 260, 44), placeholder="Enter username…")
    btn_start = Button("Start", (cx-110, SCREEN_H//2+80, 220, 44), GREEN)
    name_err = ""
    show_name_input = False

    # Game-over widgets 
    go_btns = {
        "retry": Button("Retry",     (cx-110, SCREEN_H-155, 220, 48), TEAL),
        "menu":  Button("Main Menu", (cx-110, SCREEN_H- 95, 220, 48), DARK_GREY),
    }

    # Settings widgets 
    COLOR_OPTIONS = [
        ("Green",  (  0, 200,  70)),
        ("Blue",   ( 40,  90, 220)),
        ("Red",    (200,  40,  40)),
        ("Yellow", (220, 200,   0)),
        ("Purple", (160,  30, 200)),
    ]
    sett_btns = {}
    for i, (name, col) in enumerate(COLOR_OPTIONS):
        sett_btns[f"col_{i}"] = Button(name, (cx-220+i*90, 200, 82, 38), col)
    sett_btns["grid_on"] = Button("ON",  (cx-115, 290, 105, 40), GREEN)
    sett_btns["grid_off"] = Button("OFF", (cx+ 10, 290, 105, 40), RED_C)
    sett_btns["snd_on"] = Button("ON",  (cx-115, 370, 105, 40), GREEN)
    sett_btns["snd_off"] = Button("OFF", (cx+ 10, 370, 105, 40), RED_C)
    sett_btns["save"]  = Button("Save & Back", (cx-115, SCREEN_H-90, 230, 48), TEAL)

    # Leaderboard 
    lb_back = Button("← Back", (cx-110, SCREEN_H-78, 220, 44), DARK_GREY)
    lb_data = []

    # Main loop 
    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # MENU / USERNAME input
            elif state == MENU:
                if menu_btns["play"].clicked(event):
                    show_name_input = True
                    ib_name.text = username
                    name_err = ""
                elif menu_btns["lb"].clicked(event):
                    lb_data = get_top10()
                    state = LEADERBOARD
                elif menu_btns["sett"].clicked(event):
                    state = SETTINGS
                elif menu_btns["quit"].clicked(event):
                    running = False

                if show_name_input:
                    entered = ib_name.handle(event)
                    if btn_start.clicked(event) or entered:
                        name = ib_name.text.strip()
                        if not name:
                            name_err = "Please enter a username!"
                        else:
                            username = name
                            personal_best = get_personal_best(name)
                            sc = tuple(settings["snake_color"])
                            gs = GameState(snake_color=sc,
                                           show_grid=settings["show_grid"],
                                           personal_best=personal_best)
                            show_name_input = False
                            state           = PLAYING

            # PLAYING 
            elif state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = MENU
                    elif event.key in (pygame.K_UP,    pygame.K_w): gs.snake.set_direction(UP)
                    elif event.key in (pygame.K_DOWN,  pygame.K_s): gs.snake.set_direction(DOWN)
                    elif event.key in (pygame.K_LEFT,  pygame.K_a): gs.snake.set_direction(LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): gs.snake.set_direction(RIGHT)

            # GAME OVER 
            elif state == GAME_OVER:
                if go_btns["retry"].clicked(event):
                    sc = tuple(settings["snake_color"])
                    personal_best = get_personal_best(username)
                    gs    = GameState(snake_color=sc,
                                      show_grid=settings["show_grid"],
                                      personal_best=personal_best)
                    state = PLAYING
                elif go_btns["menu"].clicked(event):
                    show_name_input = False
                    state = MENU

            # LEADERBOARD 
            elif state == LEADERBOARD:
                if lb_back.clicked(event) or \
                   (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    state = MENU

            # SETTINGS 
            elif state == SETTINGS:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    save_settings_file(settings)
                    state = MENU
                if sett_btns["save"].clicked(event):
                    save_settings_file(settings)
                    state = MENU
                if sett_btns["grid_on"].clicked(event):  settings["show_grid"] = True
                if sett_btns["grid_off"].clicked(event): settings["show_grid"] = False
                if sett_btns["snd_on"].clicked(event):   settings["sound"] = True
                if sett_btns["snd_off"].clicked(event):  settings["sound"] = False
                for i, (_, col) in enumerate(COLOR_OPTIONS):
                    if sett_btns[f"col_{i}"].clicked(event):
                        settings["snake_color"] = list(col)

        # Game logic
        if state == PLAYING and gs is not None:
            gs.tick(dt)
            if not gs.alive:
                # Auto-save to DB
                if username:
                    save_session(username, gs.score, gs.level)
                # Update personal best if beaten
                if gs.score > personal_best:
                    personal_best = gs.score
                state = GAME_OVER

        # Draw 
        if state == MENU:
            _bg(screen, "SNAKE")
            _cx("Arrow keys / WASD to move", F_SM, GREY, 82, screen)
            if show_name_input:
                _cx("Enter your username to start:", F_SM, LIGHT_GREY,
                    SCREEN_H//2 - 20, screen)
                ib_name.draw(screen)
                btn_start.draw(screen)
                if name_err:
                    _cx(name_err, F_SM, RED_C, SCREEN_H//2+134, screen)
            else:
                for btn in menu_btns.values():
                    btn.draw(screen)

        elif state == PLAYING and gs is not None:
            gs.draw(screen)
            draw_hud(screen, gs, username)

        elif state == GAME_OVER and gs is not None:
            gs.draw(screen)
            draw_hud(screen, gs, username)
            # Semi-transparent overlay
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 155))
            screen.blit(ov, (0, 0))
            # Stats
            _cx("GAME OVER", F_BIG, RED_C, SCREEN_H//2 - 130, screen)
            _cx(f"Score:         {gs.score}",        F_MED, WHITE,  SCREEN_H//2 - 70, screen)
            _cx(f"Level reached: {gs.level}",        F_MED, CYAN,   SCREEN_H//2 - 36, screen)
            _cx(f"Personal best: {personal_best}",   F_MED, YELLOW, SCREEN_H//2 -  2, screen)
            for btn in go_btns.values():
                btn.draw(screen)

        elif state == LEADERBOARD:
            _bg(screen, "LEADERBOARD")
            col_xs = (SCREEN_W//2-280, SCREEN_W//2-160, SCREEN_W//2+10,
                      SCREEN_W//2+100, SCREEN_W//2+210)
            headers = ("Rank", "Username", "Score", "Level", "Date")
            y = 90
            for h, cx2 in zip(headers, col_xs):
                screen.blit(F_SM.render(h, True, YELLOW), (cx2, y))
            y += 24
            pygame.draw.line(screen, GREY,
                             (SCREEN_W//2-295, y), (SCREEN_W//2+295, y), 1)
            y += 6
            medals = [GOLD, SILVER, BRONZE]
            for row in lb_data:
                col = medals[row["rank"]-1] if row["rank"] <= 3 else WHITE
                for val, cx2 in zip(
                    [f"#{row['rank']}", row["username"], str(row["score"]),
                     str(row["level_reached"]), row["played_at"]],
                    col_xs
                ):
                    screen.blit(F_TINY.render(val, True, col), (cx2, y))
                y += 28
            if not lb_data:
                _cx("No entries yet — play a game!", F_MED, GREY,
                    SCREEN_H//2, screen)
            lb_back.draw(screen)

        elif state == SETTINGS:
            _bg(screen, "SETTINGS")
            _cx("Snake Colour", F_MED, GREY, 160, screen)
            for i in range(len(COLOR_OPTIONS)):
                sett_btns[f"col_{i}"].draw(screen)
            # Highlight selected colour
            cur_col = tuple(settings["snake_color"])
            for i, (_, col) in enumerate(COLOR_OPTIONS):
                if col == cur_col:
                    pygame.draw.rect(screen, YELLOW,
                                     sett_btns[f"col_{i}"].rect, 3, border_radius=7)

            _cx("Grid Overlay", F_MED, GREY, 252, screen)
            sett_btns["grid_on"].draw(screen)
            sett_btns["grid_off"].draw(screen)
            sel_grid = "grid_on" if settings["show_grid"] else "grid_off"
            pygame.draw.rect(screen, YELLOW, sett_btns[sel_grid].rect, 3, border_radius=7)

            _cx("Sound", F_MED, GREY, 332, screen)
            sett_btns["snd_on"].draw(screen)
            sett_btns["snd_off"].draw(screen)
            sel_snd = "snd_on" if settings["sound"] else "snd_off"
            pygame.draw.rect(screen, YELLOW, sett_btns[sel_snd].rect, 3, border_radius=7)

            sett_btns["save"].draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()