# gamemodes.py
import pygame
import sys
import game_config as cfg
import utility_functions as util
import game_functions # Assuming GameState has toggle_pause, trigger_game_over, handle_player_input methods
import ui_functions

def run_main_game_mode(screen, clock, game_state_instance: game_functions.GameState, scaler: util.Scaler):
    game_state_instance.init_new_game(screen, clock) # Crucial for resetting/starting game state
    game_state_instance.running_game = True
    # game_state_instance.game_paused is set by init_new_game or toggle_pause
    # game_state_instance.game_over_flag is set by init_new_game or trigger_game_over

    if cfg.DEBUG_MODE: print(f"GAMEMODE: Lancement du Mode de Jeu Principal. Paused: {game_state_instance.game_paused}, Game Over: {game_state_instance.game_over_flag}")

    while game_state_instance.running_game:
        delta_time = clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                return cfg.STATE_QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag:
                        # On game over screen, ESC might mean "go to menu"
                        if cfg.DEBUG_MODE: print("GAMEMODE: ESC on Game Over screen, returning to MENU.")
                        game_state_instance.running_game = False
                        return cfg.STATE_MENU
                    else:
                        # Toggle pause if not game over (handles both pausing and unpausing)
                        game_state_instance.toggle_pause() 
                        if cfg.DEBUG_MODE: print(f"GAMEMODE: ESC pressed. Pause toggled. Paused: {game_state_instance.game_paused}")
            
            # --- Event handling based on game sub-state (paused, game over, active) ---
            if game_state_instance.game_paused:
                action = ui_functions.check_pause_menu_click(event, mouse_pos, scaler)
                if action:
                    if cfg.DEBUG_MODE: print(f"GAMEMODE: Pause menu action: {action}")
                    if action == "resume":
                        game_state_instance.toggle_pause() # Unpauses
                    elif action == "restart_game":
                        if cfg.DEBUG_MODE: print("GAMEMODE: Action Recommencer depuis pause.")
                        game_state_instance.running_game = False # Quitte cette instance du mode jeu
                        return "restart_game" # Signal à main.py pour relancer
                    elif action == cfg.STATE_MENU:
                        game_state_instance.running_game = False
                        return cfg.STATE_MENU
                    elif action == cfg.STATE_QUIT:
                        game_state_instance.running_game = False
                        return cfg.STATE_QUIT
            
            elif game_state_instance.game_over_flag:
                action = ui_functions.check_game_over_menu_click(event, mouse_pos, scaler)
                if action:
                    if cfg.DEBUG_MODE: print(f"GAMEMODE: Game Over menu action: {action}")
                    if action == "retry": # "retry" is used in initialize_game_over_layout
                        if cfg.DEBUG_MODE: print("GAMEMODE: Action Recommencer (Retry) depuis game over.")
                        game_state_instance.running_game = False
                        return "restart_game" # main.py handles "restart_game" for both scenarios
                    elif action == cfg.STATE_MENU:
                        game_state_instance.running_game = False
                        return cfg.STATE_MENU
                    elif action == cfg.STATE_QUIT:
                        game_state_instance.running_game = False
                        return cfg.STATE_QUIT
            
            else: # Game is active (not paused, not game over)
                game_state_instance.handle_player_input(event, mouse_pos) # Process regular game input


        # --- Logic Update ---
        if not game_state_instance.game_paused and not game_state_instance.game_over_flag:
            game_state_instance.update_game_logic(delta_time)
            # Check for game over condition AFTER updating logic
            # This is often handled within update_game_logic or a specific check_game_over method
            # For example, if city_hp drops to 0:
            if hasattr(game_state_instance, 'city_hp') and game_state_instance.city_hp <= 0 and not game_state_instance.game_over_flag:
                game_state_instance.trigger_game_over() # GameState method to set game_over_flag = True
                if cfg.DEBUG_MODE: print("GAMEMODE: Game Over triggered by city HP.")
        elif game_state_instance.game_paused or game_state_instance.game_over_flag:
            # If paused or game over, we still want to update timers for UI messages
            game_state_instance.update_ui_message_timers(delta_time)


        # --- Affichage ---
        # GameState's draw methods should handle what to display based on its internal state
        # (e.g., if paused, draw_game_ui_elements might call ui_functions.draw_pause_screen)
        game_state_instance.draw_game_world()       # Dessine fond, grille, objets (even when paused for background effect)
        game_state_instance.draw_game_ui_elements() # Dessine top bar, build menu, OR pause/game_over screen, messages

        pygame.display.flip()

    # If loop exits without a specific return, default to returning to menu
    if cfg.DEBUG_MODE: print("GAMEMODE: Main game loop ended, returning to MENU by default.")
    return cfg.STATE_MENU

# run_tutorial_mode can be commenté ou simplifié de manière similaire si vous testez le mode principal
def run_tutorial_mode(screen, clock, game_state_instance: game_functions.GameState, scaler: util.Scaler):
    game_state_instance.init_new_game(screen, clock, is_tutorial=True) # Crucial
    game_state_instance.running_game = True
    # game_state_instance.game_paused = False # Assurer que ce n'est pas en pause
    # game_state_instance.game_over_flag = False # Tutoriel ne devrait pas avoir de game over typiquement

    if cfg.DEBUG_MODE: print(f"GAMEMODE: Lancement du Mode Tutoriel. Paused: {game_state_instance.game_paused}")

    while game_state_instance.running_game:
        delta_time = clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                return cfg.STATE_QUIT
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # In tutorial, ESC might always go to menu or toggle a simpler pause
                    if game_state_instance.game_paused:
                        game_state_instance.toggle_pause()
                    else: # If active, or if you want ESC to always exit tutorial pause
                        game_state_instance.toggle_pause() # Or directly return to menu:
                        # game_state_instance.running_game = False
                        # return cfg.STATE_MENU
                    if cfg.DEBUG_MODE: print(f"GAMEMODE (TUTORIAL): ESC pressed. Pause toggled. Paused: {game_state_instance.game_paused}")

            if game_state_instance.game_paused:
                action = ui_functions.check_pause_menu_click(event, mouse_pos, scaler)
                if action:
                    if cfg.DEBUG_MODE: print(f"GAMEMODE (TUTORIAL): Pause menu action: {action}")
                    if action == "resume":
                        game_state_instance.toggle_pause()
                    elif action == "restart_game": # "restart_tutorial" might be more appropriate
                        if cfg.DEBUG_MODE: print("GAMEMODE (TUTORIAL): Action Recommencer (Tutoriel) depuis pause.")
                        game_state_instance.running_game = False
                        return "restart_tutorial" # Signal à main.py pour relancer le tutoriel
                    elif action == cfg.STATE_MENU:
                        game_state_instance.running_game = False
                        return cfg.STATE_MENU
                    elif action == cfg.STATE_QUIT:
                        game_state_instance.running_game = False
                        return cfg.STATE_QUIT
            # No game_over_flag check for tutorial generally
            else: # Tutorial is active
                game_state_instance.handle_player_input(event, mouse_pos)
                # Tutorial-specific input handling or progression
                game_state_instance.update_tutorial_specific_logic(event) # Assumed method

        if not game_state_instance.game_paused:
            game_state_instance.update_game_logic(delta_time) # General updates (timers, etc.)
            game_state_instance.update_tutorial_progression(delta_time) # Assumed method for tutorial steps
        elif game_state_instance.game_paused:
             game_state_instance.update_ui_message_timers(delta_time)


        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements() # Should also handle pause screen for tutorial

        pygame.display.flip()
    
    if cfg.DEBUG_MODE: print("GAMEMODE: Tutorial loop ended, returning to MENU by default.")
    return cfg.STATE_MENU
