import pygame, sys
from racer import GameState, SW, SH, HUD_H
from ui import (
    Button, InputBox,
    make_main_menu_buttons, draw_main_menu,
    draw_username_screen,
    make_settings_buttons,  draw_settings,
    draw_leaderboard,
    make_game_over_buttons, draw_game_over,
    draw_hud,
)
from persistence import (
    load_settings, save_settings,
    add_leaderboard_entry,
)

# Init
pygame.init()
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Racer — TSIS 3")
clock = pygame.time.Clock()
FPS = 60

# State machine labels 
MENU = "menu"
USERNAME = "username"
PLAYING = "playing"
GAME_OVER  = "game_over"
LEADERBOARD = "leaderboard"
SETTINGS = "settings"


def main():
    settings = load_settings()          # load from settings.json
    state = MENU
    username = settings.get("username", "")

    # Build UI widgets once (recreated on screen transitions where needed)
    menu_btns = make_main_menu_buttons(SW, SH)
    sett_btns = make_settings_buttons(SW, SH)
    go_btns   = make_game_over_buttons(SW, SH)
    lb_back   = Button("← Back", (SW//2 - 110, SH - 78, 220, 48),
                        color=(60,60,60))

    # Username screen widgets
    ib_name = InputBox((SW//2 - 130, SH//2 - 30, 260, 46),
                          placeholder="Type your name…")
    ib_name.text = username
    btn_start = Button(" Start Race",
                        (SW//2 - 130, SH//2 + 40, 260, 48))
    name_error = ""

    # Game state (created fresh each run)
    game: GameState = None

    running = True
    while running:
        dt = clock.tick(FPS)

        # Event pump
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # MENU
            elif state == MENU:
                if menu_btns["Play"].is_clicked(event):
                    ib_name.text = settings.get("username", "")
                    name_error = ""
                    state = USERNAME
                elif menu_btns["Leaderboard"].is_clicked(event):
                    state = LEADERBOARD
                elif menu_btns["Settings"].is_clicked(event):
                    state = SETTINGS
                elif menu_btns["Quit"].is_clicked(event):
                    running = False

            # USERNAME 
            elif state == USERNAME:
                ib_name.handle_event(event)
                if (btn_start.is_clicked(event)
                        or (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_RETURN)):
                    name = ib_name.text.strip()
                    if not name:
                        name_error = "Please enter a name before racing!"
                    else:
                        username = name
                        settings["username"] = name
                        save_settings(settings)
                        game  = GameState(
                            car_color  = settings["car_color"],
                            difficulty = settings["difficulty"],
                        )
                        state = PLAYING
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = MENU

            # PLAYING 
            elif state == PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = MENU

            # GAME OVER
            elif state == GAME_OVER:
                if go_btns["retry"].is_clicked(event):
                    game  = GameState(
                        car_color  = settings["car_color"],
                        difficulty = settings["difficulty"],
                    )
                    state = PLAYING
                elif go_btns["menu"].is_clicked(event):
                    state = MENU

            # LEADERBOARD
            elif state == LEADERBOARD:
                if lb_back.is_clicked(event):
                    state = MENU
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = MENU

            # SETTINGS
            elif state == SETTINGS:
                if sett_btns["back"].is_clicked(event):
                    save_settings(settings)
                    sett_btns = make_settings_buttons(SW, SH)   # rebuild highlights
                    state = MENU
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    state = MENU
                # Sound toggle
                if sett_btns["sound_on"].is_clicked(event):
                    settings["sound"] = True
                if sett_btns["sound_off"].is_clicked(event):
                    settings["sound"] = False
                # Car colour
                for col in ("blue","red","green","yellow"):
                    if sett_btns[f"car_{col}"].is_clicked(event):
                        settings["car_color"] = col
                # Difficulty
                for diff in ("easy","normal","hard"):
                    if sett_btns[f"diff_{diff}"].is_clicked(event):
                        settings["difficulty"] = diff

        # Game logic 
        if state == PLAYING and game is not None:
            keys = pygame.key.get_pressed()
            game.tick(dt, keys)

            if not game.alive:
                # Save to leaderboard then show game-over screen
                add_leaderboard_entry(
                    username,
                    game.score,
                    game.distance,
                    game.coins_n,
                )
                state = GAME_OVER

        # Draw 
        screen.fill((12, 16, 30))

        if state == MENU:
            draw_main_menu(screen, menu_btns)

        elif state == USERNAME:
            draw_username_screen(screen, ib_name, btn_start, name_error)

        elif state == PLAYING and game is not None:
            game.draw(screen)
            draw_hud(
                screen,
                score = game.score,
                distance = game.distance,
                coins = game.coins_n,
                level = game.level,
                active_pu = game.active_pu,
                pu_timer = game.pu_timer,
                shield_active = game.player.shield_active,
            )

        elif state == GAME_OVER and game is not None:
            game.draw(screen)
            draw_hud(screen, game.score, game.distance,
                     game.coins_n, game.level)
            draw_game_over(screen, game.score, game.distance,
                           game.coins_n, go_btns)

        elif state == LEADERBOARD:
            draw_leaderboard(screen, lb_back)

        elif state == SETTINGS:
            draw_settings(screen, settings, sett_btns)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()