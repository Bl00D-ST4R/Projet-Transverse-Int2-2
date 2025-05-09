# gamemodes.py
import pygame
import sys
import game_config as cfg
import utility_functions as util
import game_functions  # Assuming GameState has toggle_pause, trigger_game_over, handle_player_input methods
import ui_functions


def run_main_game_mode(screen, clock, game_state_instance: game_functions.GameState, scaler: util.Scaler):
    # game_state_instance is already initialized with the scaler in main.py
    # init_new_game is called to reset its state for this specific game mode run
    game_state_instance.init_new_game(screen, clock, is_tutorial=False)  # Pass False for main game
    # game_state_instance.running_game = True # This is managed by the while loop condition below
    # game_paused and game_over_flag are reset by init_new_game

    if cfg.DEBUG_MODE: print("GAMEMODE: Lancement du Mode de Jeu Principal...")

    running_this_mode = True  # Local loop control
    while running_this_mode:
        delta_time = clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_this_mode = False
                return cfg.STATE_QUIT  # Signal to main app to quit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag:
                        if cfg.DEBUG_MODE: print("GAMEMODE: ESC on Game Over screen, returning to MENU.")
                        running_this_mode = False
                        return cfg.STATE_MENU
                    else:
                        game_state_instance.toggle_pause()
                        if cfg.DEBUG_MODE: print(
                            f"GAMEMODE: ESC pressed. Pause toggled. Paused: {game_state_instance.game_paused}")

            # --- Event handling based on game sub-state (paused, game over, active) ---
            if game_state_instance.game_paused:
                action = ui_functions.check_pause_menu_click(event, mouse_pos, scaler)  # Pass scaler
                if action:
                    if cfg.DEBUG_MODE: print(f"GAMEMODE: Pause menu action: {action}")
                    if action == "resume":
                        game_state_instance.toggle_pause()
                    elif action == "restart_game":
                        if cfg.DEBUG_MODE: print("GAMEMODE: Action Recommencer depuis pause.")
                        running_this_mode = False
                        return "restart_game"
                    elif action == cfg.STATE_MENU:
                        running_this_mode = False
                        return cfg.STATE_MENU
                    elif action == cfg.STATE_QUIT:
                        running_this_mode = False
                        return cfg.STATE_QUIT

            elif game_state_instance.game_over_flag:
                action = ui_functions.check_game_over_menu_click(event, mouse_pos, scaler)  # Pass scaler
                if action:
                    if cfg.DEBUG_MODE: print(f"GAMEMODE: Game Over menu action: {action}")
                    if action == "retry":
                        if cfg.DEBUG_MODE: print("GAMEMODE: Action Recommencer (Retry) depuis game over.")
                        running_this_mode = False
                        return "restart_game"
                    elif action == cfg.STATE_MENU:
                        running_this_mode = False
                        return cfg.STATE_MENU
                    elif action == cfg.STATE_QUIT:
                        running_this_mode = False
                        return cfg.STATE_QUIT

            else:  # Game is active (not paused, not game over)
                game_state_instance.handle_player_input(event, mouse_pos)

        # --- Logic Update ---
        if not game_state_instance.game_paused and not game_state_instance.game_over_flag:
            game_state_instance.update_game_logic(delta_time)
            # Check for game over condition AFTER updating logic (e.g., city_hp drops to 0)
            # GameState's update_game_logic or a dedicated method should set game_state_instance.game_over_flag
            if hasattr(game_state_instance,
                       'city_hp') and game_state_instance.city_hp <= 0 and not game_state_instance.game_over_flag:
                game_state_instance.trigger_game_over()
                if cfg.DEBUG_MODE: print("GAMEMODE: Game Over condition met (City HP <= 0).")

        else:  # Still update UI message timers even if paused/game over
            game_state_instance.update_ui_message_timers(delta_time)

        # --- Drawing (Layered Approach) ---
        # 1. Game World (Background, Grid, Objects, Placement Preview)
        game_state_instance.draw_game_world()

        # 2. Static UI and Modal UI (Top Bar, Build Menu, Messages, Pause/Game Over Screens)
        game_state_instance.draw_game_ui_elements()

        pygame.display.flip()

    if cfg.DEBUG_MODE: print("GAMEMODE: Main game loop ended.")
    return cfg.STATE_MENU  # Default return to menu if loop exits unexpectedly


def run_tutorial_mode(screen, clock, game_state_instance: game_functions.GameState, scaler: util.Scaler):
    game_state_instance.init_new_game(screen, clock, is_tutorial=True)
    if cfg.DEBUG_MODE: print("GAMEMODE: Lancement du Mode Tutoriel...")

    # Example tutorial steps (could be loaded from a config file)
    tutorial_steps = [
        {"id": 0, "msg": "Bienvenue! Construisez une 'Structure' (Frame) sur une case vide.",
         "condition": lambda gs: any(b.type == "frame" for b in gs.buildings)},
        {"id": 1, "msg": "Super! Maintenant, construisez un 'Générateur' sur la structure.",
         "condition": lambda gs: any(b.type == "generator" for b in gs.buildings)},
        {"id": 2, "msg": "Bien joué! Les générateurs produisent de l'énergie. Essayez une 'Mine de Fer'.",
         "condition": lambda gs: any(b.type == "miner" for b in gs.buildings)},
        {"id": 3, "msg": "Excellent! Les mines produisent du fer. Préparez-vous à vous défendre!",
         "condition": lambda gs: False},  # End
    ]
    current_tutorial_step_index = 0
    if tutorial_steps:
        game_state_instance.show_tutorial_message(tutorial_steps[current_tutorial_step_index]["msg"],
                                                  9999)  # Long duration

    running_this_mode = True
    while running_this_mode:
        delta_time = clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_this_mode = False
                return cfg.STATE_QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag:  # Should not happen in tutorial
                        running_this_mode = False
                        return cfg.STATE_MENU
                    else:
                        game_state_instance.toggle_pause()

            if game_state_instance.game_paused:
                action = ui_functions.check_pause_menu_click(event, mouse_pos, scaler)
                if action:
                    if action == "resume":
                        game_state_instance.toggle_pause()
                    elif action == "restart_game":  # Or "restart_tutorial"
                        running_this_mode = False
                        return "restart_tutorial"
                    elif action == cfg.STATE_MENU:
                        running_this_mode = False
                        return cfg.STATE_MENU
                    elif action == cfg.STATE_QUIT:
                        running_this_mode = False
                        return cfg.STATE_QUIT
            # No game_over_flag check typically for tutorial
            else:  # Game is active
                game_state_instance.handle_player_input(event, mouse_pos)
                game_state_instance.update_tutorial_specific_logic(event)  # For any event-driven tutorial logic

        # Tutorial Progression Check
        if not game_state_instance.game_paused and current_tutorial_step_index < len(tutorial_steps):
            current_step_data = tutorial_steps[current_tutorial_step_index]
            if current_step_data["condition"](game_state_instance):
                current_tutorial_step_index += 1
                if current_tutorial_step_index < len(tutorial_steps):
                    game_state_instance.show_tutorial_message(tutorial_steps[current_tutorial_step_index]["msg"], 9999)
                else:
                    game_state_instance.show_tutorial_message("Tutoriel Terminé! Bravo!",
                                                              5)  # Short message then maybe auto-exit
                    # Could add a delay then: running_this_mode = False; return cfg.STATE_MENU

        if not game_state_instance.game_paused and not game_state_instance.game_over_flag:
            game_state_instance.update_game_logic(delta_time)  # General game logic (timers, etc.)
            game_state_instance.update_tutorial_progression(delta_time)  # For time-based tutorial steps
        else:
            game_state_instance.update_ui_message_timers(delta_time)

        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements()

        pygame.display.flip()

    if cfg.DEBUG_MODE: print("GAMEMODE: Tutorial loop ended.")
    return cfg.STATE_MENU