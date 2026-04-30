# All screen drawing, Button widget, InputBox, and HUD.
# Screens:  main_menu | username | settings | leaderboard | game_over


import pygame
from persistence import load_leaderboard

# Palette 
WHITE = (255, 255, 255);  BLACK = (0,   0,   0)
GREY = (160, 160, 160);  DARK_GREY = (60,  60,  60)
LGREY = (220, 220, 220);  BG = (12,  16,  30)
RED = (200,  30,  30);  GREEN = (30, 170,  30)
BLUE = (30,   80, 210);  YELLOW = (240, 200,   0)
ORANGE = (230, 120,   0);  CYAN = (0,  200, 220)
TEAL = (0,   155, 140);  PURPLE = (140,  0,  200)
GOLD = (255, 200,   0);  SILVER = (200, 200, 200)
BRONZE = (180, 110,  40)

CAR_COLORS = {
    "blue":   (40,  90, 220),
    "red":    (200,  30,  30),
    "green":  (30,  160,  30),
    "yellow": (220, 200,   0),
}

_fonts: dict = {}

def _f(size: int, bold: bool = False) -> pygame.font.Font:
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = pygame.font.SysFont("Arial", size, bold=bold)
    return _fonts[k]

def _center(surf, text, font, color, cx, y) -> int:
    img = font.render(text, True, color)
    surf.blit(img, (cx - img.get_width() // 2, y))
    return img.get_height()


# Reusable widgets 

class Button:
    """Clickable rectangular button with hover highlight"""

    def __init__(self, label, rect, color=TEAL,
                 text_color=WHITE, font_size=21):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.color= color
        self.text_color = text_color
        self._fs = font_size

    def draw(self, surface):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        bg = tuple(min(255, c + 35) for c in self.color) if hover else self.color
        pygame.draw.rect(surface, bg,    self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        txt = _f(self._fs, bold=True).render(self.label, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


class InputBox:
    """Single-line keyboard text input"""

    def __init__(self, rect, placeholder="", max_len=20, font_size=22):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.max_len = max_len
        self.text = ""
        self.active = False
        self._fs = font_size

    def handle_event(self, event) -> bool:
        """Returns True when Enter is pressed."""
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
        pygame.draw.rect(surface, (25, 30, 50), self.rect, border_radius=6)
        pygame.draw.rect(surface, border,       self.rect, 2, border_radius=6)
        display = self.text or self.placeholder
        color = WHITE if self.text else DARK_GREY
        txt = _f(self._fs).render(display, True, color)
        surface.blit(txt, (self.rect.x + 8,
                           self.rect.y + (self.rect.height - txt.get_height()) // 2))


# Background helper

def _bg(surface, title=None):
    W, H = surface.get_size()
    surface.fill(BG)
    for i in range(0, H, 55):
        pygame.draw.line(surface, (18, 22, 40), (0, i), (W, i))
    if title:
        _center(surface, title, _f(44, bold=True), CYAN, W // 2, 28)


# Main Menu 

def make_main_menu_buttons(W, H) -> dict:
    cx, bw, bh, gap = W // 2, 230, 50, 16
    sy = H // 2 - 105
    return {
        "Play": Button("Play", (cx-bw//2, sy, bw, bh), TEAL),
        "Leaderboard": Button("Leaderboard", (cx-bw//2, sy+bh+gap, bw, bh), BLUE),
        "Settings": Button("Settings", (cx-bw//2, sy+2*(bh+gap), bw, bh), DARK_GREY),
        "Quit": Button("Quit", (cx-bw//2, sy+3*(bh+gap), bw, bh), RED),
    }

def draw_main_menu(surface, buttons: dict):
    W, H = surface.get_size()
    _bg(surface, "RACER")
    _center(surface, "Advanced Driving Experience", _f(18), GREY, W//2, 84)
    for btn in buttons.values():
        btn.draw(surface)


# Username entry 

def draw_username_screen(surface, input_box: InputBox,
                          btn_start: Button, error: str = ""):
    W, H = surface.get_size()
    _bg(surface, "ENTER YOUR NAME")
    _center(surface, "Your name will appear on the leaderboard.",
            _f(18), GREY, W//2, 96)
    if error:
        _center(surface, error, _f(17), RED, W//2, 126)
    input_box.draw(surface)
    btn_start.draw(surface)


# Settings

def make_settings_buttons(W, H) -> dict:
    cx   = W // 2
    bh = 42
    btns = {}

    # Sound
    btns["sound_on"]  = Button("ON",  (cx - 115, 148, 105, bh), GREEN)
    btns["sound_off"] = Button("OFF", (cx +  10, 148, 105, bh), RED)

    # Car colour
    col_list = list(CAR_COLORS.items())
    total = len(col_list) * 82 - 10
    sx = cx - total // 2
    for i, (name, col) in enumerate(col_list):
        btns[f"car_{name}"] = Button(name.capitalize(), (sx + i*82, 248, 78, bh), col)

    # Difficulty
    for i, (name, col) in enumerate(zip(
            ["easy", "normal", "hard"], [GREEN, TEAL, RED])):
        btns[f"diff_{name}"] = Button(name.capitalize(),
                                       (cx - 165 + i*115, 348, 105, bh), col)

    btns["back"] = Button("← Back", (cx - 115, H - 78, 230, 48), DARK_GREY)
    return btns

def draw_settings(surface, settings: dict, buttons: dict):
    W, H = surface.get_size()
    _bg(surface, "SETTINGS")
    fh = _f(20, bold=True)

    _center(surface, "Sound Effects", fh, GREY, W//2, 116)
    buttons["sound_on"].draw(surface);  buttons["sound_off"].draw(surface)
    sel = buttons["sound_on"] if settings["sound"] else buttons["sound_off"]
    pygame.draw.rect(surface, YELLOW, sel.rect, 3, border_radius=8)

    _center(surface, "Car Colour", fh, GREY, W//2, 216)
    for name in CAR_COLORS:
        buttons[f"car_{name}"].draw(surface)
    pygame.draw.rect(surface, YELLOW,
                     buttons[f"car_{settings['car_color']}"].rect, 3, border_radius=8)

    _center(surface, "Difficulty", fh, GREY, W//2, 316)
    for diff in ("easy", "normal", "hard"):
        buttons[f"diff_{diff}"].draw(surface)
    pygame.draw.rect(surface, YELLOW,
                     buttons[f"diff_{settings['difficulty']}"].rect, 3, border_radius=8)

    buttons["back"].draw(surface)


# Leaderboard 

def draw_leaderboard(surface, btn_back: Button):
    W, H  = surface.get_size()
    _bg(surface, "LEADERBOARD")

    entries = load_leaderboard()
    col_xs = (W//2-310, W//2-190, W//2+30, W//2+140, W//2+250)
    headers = ("Rank", "Name", "Score", "Distance", "Coins")
    fh, fn = _f(17, bold=True), _f(16)

    y = 96
    for hdr, cx in zip(headers, col_xs):
        surface.blit(fh.render(hdr, True, YELLOW), (cx, y))
    y += 26
    pygame.draw.line(surface, GREY, (W//2-330, y), (W//2+310, y), 1)
    y += 8

    medal = [GOLD, SILVER, BRONZE]
    for i, e in enumerate(entries):
        col = medal[i] if i < 3 else WHITE
        for val, cx in zip(
            [f"#{i+1}", e.get("name","?"), str(e.get("score",0)),
             f"{e.get('distance',0)} m", str(e.get("coins",0))],
            col_xs
        ):
            surface.blit(fn.render(val, True, col), (cx, y))
        y += 30

    if not entries:
        _center(surface, "No entries yet — play a game!",
                _f(20), GREY, W//2, H//2)

    btn_back.draw(surface)


# Game Over 

def make_game_over_buttons(W, H) -> dict:
    cx, bw, bh = W//2, 210, 50
    return {
        "retry": Button("Retry", (cx-bw//2, H-160, bw, bh), TEAL),
        "menu":  Button("Main Menu", (cx-bw//2, H- 98, bw, bh), DARK_GREY),
    }

def draw_game_over(surface, score: int, distance: int,
                   coins: int, buttons: dict):
    W, H = surface.get_size()
    _bg(surface, "GAME OVER")
    y = H//2 - 80
    for label, value in [("Score", str(score)),
                          ("Distance", f"{distance} m"),
                          ("Coins", str(coins))]:
        _center(surface, f"{label}:  {value}", _f(28, bold=True), WHITE, W//2, y)
        y += 48
    for btn in buttons.values():
        btn.draw(surface)


# In-game HUD 

PU_COLORS = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}

def draw_hud(surface, score: int, distance: int, coins: int, level: int,
             active_pu=None, pu_timer: float = 0.0, shield_active: bool = False):
    """
    Top bar showing score, distance, level, and active power-up
    Height = 44 px
    """
    W  = surface.get_width()
    fh = _f(18, bold=True)
    fs = _f(15)
    pygame.draw.rect(surface, (8, 10, 20), (0, 0, W, 44))
    pygame.draw.line(surface, GREY, (0, 44), (W, 44), 1)

    # Left: score + coins
    surface.blit(fh.render(f"Score: {score}", True, WHITE), (8, 4))
    surface.blit(fs.render(f"Coins: {coins}",  True, YELLOW),(8, 26))

    # Centre: distance + level
    dt = fh.render(f"{distance} m", True, CYAN)
    surface.blit(dt, (W//2 - dt.get_width()//2, 4))
    lt = fs.render(f"Level {level}", True, LGREY)
    surface.blit(lt, (W//2 - lt.get_width()//2, 26))

    # Right: power-up indicator
    if active_pu and active_pu != "shield":
        col = PU_COLORS.get(active_pu, WHITE)
        pt  = fh.render(f"{active_pu.upper()}  {pu_timer:.1f}s", True, col)
        surface.blit(pt, (W - pt.get_width() - 8, 4))
    elif shield_active or active_pu == "shield":
        st = fh.render(" SHIELD", True, CYAN)
        surface.blit(st, (W - st.get_width() - 8, 4))