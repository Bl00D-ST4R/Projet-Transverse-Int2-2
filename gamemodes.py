# gamemodes.py
import pygame
import sys
import game_config as cfg
import utility_functions as util
import game_functions
import ui_functions

def run_main_game_mode(screen, clock, game_state_instance, scaler):
    game_state_instance.init_new_game(screen, clock) # Crucial
    game_state_instance.running_game = True
    game_state_instance.game_paused = False # Assurer que ce n'est pas en pause
    game_state_instance.game_over_flag = False

    if cfg.DEBUG_MODE: print("GAMEMODE: Lancement du Mode de Jeu Principal (test dessin UI)...")

    while game_state_instance.running_game:
        delta_time = clock.tick(cfg.FPS) / 1000.0 # delta_time might still be needed by game_state.update_game_logic if re-enabled

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                return cfg.STATE_QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU # Quitter au menu avec Echap pour test
            
            # Minimal input handling for testing pause/game_over screens if needed
            # game_state_instance.handle_player_input(event, pygame.mouse.get_pos())


        # Minimal logic updates for this test
        # game_state_instance.update_game_logic(delta_time) # Commenter pour simplifier, 
                                                          # or call the simplified stub in game_functions.py
        # If game_state.update_game_logic is the simplified stub, it's fine to call it.
        # It mainly updates error/tutorial message timers.
        game_state_instance.update_game_logic(delta_time)


        # --- Affichage ---
        game_state_instance.draw_game_world()       # Dessine fond, grille, objets
        game_state_instance.draw_game_ui_elements() # Dessine top bar, build menu, messages

        pygame.display.flip()

    return cfg.STATE_MENU

# run_tutorial_mode peut être commenté ou simplifié de manière similaire si vous testez le mode principal
def run_tutorial_mode(screen, clock, game_state_instance, scaler):
    print("Tutoriel désactivé pour le test UI.")
    # Optional: show a message on screen that tutorial is disabled
    # screen.fill(cfg.COLOR_MENU_BACKGROUND)
    # msg_surf = util.render_text_surface("Tutorial Mode Disabled for this Test", scaler.font_size_large, cfg.COLOR_WHITE)
    # if msg_surf:
    #     screen.blit(msg_surf, (scaler.actual_w // 2 - msg_surf.get_width() // 2, scaler.actual_h // 2 - msg_surf.get_height() // 2))
    # pygame.display.flip()
    # pygame.time.wait(2000) # Wait 2 seconds
    return cfg.STATE_MENU # Retourne directement au menu
