# gamemodes.py
import pygame
import sys # Import sys pour quitter si besoin (même si géré par main.py)
import game_config as cfg
import utility_functions as util # Ensure Scaler can be type hinted if used: util.Scaler
import game_functions
import ui_functions
import wave_definitions # Assurez-vous que ce fichier est importé si utilisé (ex: tutorial waves)

# MODIFIER: Accepter et passer scaler
def run_main_game_mode(screen, clock, game_state_instance, scaler):
    """
    Lance et gère la boucle principale du mode de jeu standard.
    Retourne l'état suivant du jeu (ex: cfg.STATE_MENU, cfg.STATE_QUIT).
    """
    # init_new_game utilise le scaler déjà dans game_state_instance (passé lors de GameState.__init__)
    game_state_instance.init_new_game(screen, clock)
    game_state_instance.running_game = True
    game_state_instance.game_over_flag = False
    game_state_instance.game_paused = False

    print("Lancement du Mode de Jeu Principal...")

    while game_state_instance.running_game:
        delta_time = game_state_instance.clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                return cfg.STATE_QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag:
                        game_state_instance.running_game = False
                        return cfg.STATE_MENU # Esc sur Game Over -> Menu
                    else:
                        game_state_instance.toggle_pause()

            # Gestion Input spécifique à l'état (Pause, Game Over, Jeu Actif)
            if game_state_instance.game_paused:
                # MODIFIER: Passer scaler à check_pause_menu_click
                action = ui_functions.check_pause_menu_click(event, mouse_pos, scaler)
                if action == "resume":
                    game_state_instance.toggle_pause()
                elif action == "restart":
                    print("Action 'Recommencer' sélectionnée.")
                    game_state_instance.running_game = False
                    return "restart_game"
                elif action == cfg.STATE_MENU:
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
                elif action == cfg.STATE_QUIT:
                    game_state_instance.running_game = False
                    return cfg.STATE_QUIT
            elif game_state_instance.game_over_flag:
                # MODIFIER: Passer scaler à check_game_over_menu_click
                action = ui_functions.check_game_over_menu_click(event, mouse_pos, scaler)
                if action == "retry":
                     print("Action 'Recommencer' (Game Over) sélectionnée.")
                     game_state_instance.running_game = False
                     return "restart_game"
                elif action == cfg.STATE_MENU:
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
                elif action == cfg.STATE_QUIT:
                    game_state_instance.running_game = False
                    return cfg.STATE_QUIT
            else: # Jeu actif (pas en pause, pas game over)
                # handle_player_input utilise game_state_instance.scaler
                game_state_instance.handle_player_input(event, mouse_pos)


        # --- Logique du Jeu ---
        if not game_state_instance.game_paused:
            # update_game_logic passe scaler aux objets via game_state_instance.scaler
            game_state_instance.update_game_logic(delta_time)

        # --- Affichage ---
        # draw_game_world et draw_game_ui_elements passent scaler aux draws UI via game_state_instance.scaler
        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements()
        pygame.display.flip()

    print("Mode de Jeu Principal terminé.")
    return cfg.STATE_MENU

# MODIFIER: Accepter et passer scaler
def run_tutorial_mode(screen, clock, game_state_instance, scaler):
    """
    Lance et gère la boucle du mode tutoriel.
    Retourne l'état suivant du jeu.
    """
    # init_new_game utilise le scaler déjà dans game_state_instance
    game_state_instance.init_new_game(screen, clock)
    game_state_instance.running_game = True
    game_state_instance.game_over_flag = False
    game_state_instance.game_paused = False

    current_tutorial_step = 0
    # tutorial_objectives_met = [False] * 5 # Not used in current logic
    tutorial_steps = [
        {"msg": "Bienvenue! Construisez une 'Structure' (icône 1) sur la grille.", "condition": lambda gs: any(b.type == "frame" for b in gs.buildings)},
        {"msg": "Placez un 'Générateur' (icône 2) sur une structure.", "condition": lambda gs: any(b.type == "generator" for b in gs.buildings)},
        {"msg": "Placez une 'Mine de Fer' (icône 4) sur la rangée renforcée (plus foncée) ou sur une autre mine.", "condition": lambda gs: any(b.type == "miner" for b in gs.buildings)},
        {"msg": "Construisez une 'Tourelle Gatling' (icône 5) sur une structure.", "condition": lambda gs: any(t.type == "gatling_turret" for t in gs.turrets)},
        {"msg": "Parfait ! Le tutoriel est terminé. Appuyez sur Echap pour quitter.", "condition": lambda gs: False}
    ]
    
    if tutorial_steps:
         game_state_instance.show_tutorial_message(tutorial_steps[0]["msg"], duration=999)

    print("Lancement du Mode Tutoriel...")

    while game_state_instance.running_game:
        delta_time = game_state_instance.clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                return cfg.STATE_QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
            
            if game_state_instance.game_paused:
                # MODIFIER: Passer scaler
                action = ui_functions.check_pause_menu_click(event, mouse_pos, scaler)
                if action == "resume":
                    game_state_instance.toggle_pause()
                elif action == "restart":
                     game_state_instance.running_game = False
                     return "restart_tutorial"
                elif action == cfg.STATE_MENU:
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
                elif action == cfg.STATE_QUIT:
                    game_state_instance.running_game = False
                    return cfg.STATE_QUIT
            elif game_state_instance.game_over_flag: # Fin du tutoriel
                 # MODIFIER: Passer scaler
                 action = ui_functions.check_game_over_menu_click(event, mouse_pos, scaler)
                 if action == cfg.STATE_MENU:
                     game_state_instance.running_game = False
                     return cfg.STATE_MENU
                 elif action == cfg.STATE_QUIT:
                     game_state_instance.running_game = False
                     return cfg.STATE_QUIT
            else: # Tutoriel actif
                # handle_player_input utilise game_state_instance.scaler
                game_state_instance.handle_player_input(event, mouse_pos)

                if current_tutorial_step < len(tutorial_steps):
                    condition_func = tutorial_steps[current_tutorial_step].get("condition")
                    # Condition lambdas use 'gs' (game_state_instance) which has 'gs.scaler' if needed
                    if condition_func and condition_func(game_state_instance):
                         print(f"Tutoriel: Étape {current_tutorial_step} terminée.")
                         current_tutorial_step += 1
                         if current_tutorial_step < len(tutorial_steps):
                             game_state_instance.show_tutorial_message(tutorial_steps[current_tutorial_step]["msg"], duration=999)
                         else:
                             game_state_instance.show_tutorial_message("Tutoriel terminé! Appuyez sur Echap.", duration=999)
                             # game_state_instance.game_over_flag = True # Optionnel: pour utiliser un écran de fin


        if not game_state_instance.game_paused:
            game_state_instance.update_timers_and_waves(delta_time)
            game_state_instance.update_resources_per_tick(delta_time)
            is_globally_powered = game_state_instance.electricity_produced >= game_state_instance.electricity_consumed
            for turret in game_state_instance.turrets:
                 # MODIFIER: Passer scaler à turret.update
                 turret.update(delta_time, [], is_globally_powered, game_state_instance, scaler)

        # draw_game_world et draw_game_ui_elements passent scaler via game_state_instance.scaler
        # draw_game_ui_elements handles drawing tutorial messages using game_state_instance.scaler
        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements()

        pygame.display.flip()

    print("Mode Tutoriel terminé.")
    return cfg.STATE_MENU
