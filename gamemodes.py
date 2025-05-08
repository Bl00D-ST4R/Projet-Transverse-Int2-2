# gamemodes.py
import pygame
import sys # Import sys pour quitter si besoin (même si géré par main.py)
import game_config as cfg
import utility_functions as util
import game_functions
import ui_functions
import wave_definitions # Assurez-vous que ce fichier est importé si utilisé (ex: tutorial waves)

def run_main_game_mode(screen, clock, game_state_instance):
    """
    Lance et gère la boucle principale du mode de jeu standard.
    Retourne l'état suivant du jeu (ex: cfg.STATE_MENU, cfg.STATE_QUIT).
    """
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
                return cfg.STATE_QUIT # <--- AJOUT: Retourner l'état QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag:
                        game_state_instance.running_game = False
                        return cfg.STATE_MENU # Esc sur Game Over -> Menu
                    else:
                        game_state_instance.toggle_pause()

            # Gestion Input spécifique à l'état (Pause, Game Over, Jeu Actif)
            if game_state_instance.game_paused:
                action = ui_functions.check_pause_menu_click(event, mouse_pos)
                if action == "resume":
                    game_state_instance.toggle_pause()
                elif action == "restart": # Action pour recommencer
                    print("Action 'Recommencer' sélectionnée.")
                    game_state_instance.running_game = False # Arrête cette instance de jeu
                    return "restart_game" # Signal spécifique pour relancer le même mode
                elif action == cfg.STATE_MENU: # Retourne l'état défini dans cfg
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
                elif action == cfg.STATE_QUIT: # Retourne l'état défini dans cfg
                    game_state_instance.running_game = False
                    return cfg.STATE_QUIT
            elif game_state_instance.game_over_flag:
                action = ui_functions.check_game_over_menu_click(event, mouse_pos)
                if action == "retry": # Action pour recommencer
                     print("Action 'Recommencer' (Game Over) sélectionnée.")
                     game_state_instance.running_game = False
                     return "restart_game" # Signal spécifique pour relancer le même mode
                elif action == cfg.STATE_MENU: # Utilise la constante pour aller au menu
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
                elif action == cfg.STATE_QUIT: # Utilise la constante pour quitter
                    game_state_instance.running_game = False
                    return cfg.STATE_QUIT
            else: # Jeu actif (pas en pause, pas game over)
                game_state_instance.handle_player_input(event, mouse_pos)


        # --- Logique du Jeu ---
        if not game_state_instance.game_paused: # Mettre à jour la logique seulement si pas en pause
            game_state_instance.update_game_logic(delta_time)

        # --- Affichage ---
        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements() # Gère aussi l'affichage Pause/Game Over

        pygame.display.flip()

    print("Mode de Jeu Principal terminé.")
    # Si la boucle se termine normalement (ex: running_game mis à False sans action spécifique), retourner au menu
    return cfg.STATE_MENU

# --- Modifier aussi run_tutorial_mode de la même manière ---
def run_tutorial_mode(screen, clock, game_state_instance):
    """
    Lance et gère la boucle du mode tutoriel.
    Retourne l'état suivant du jeu.
    """
    game_state_instance.init_new_game(screen, clock)
    game_state_instance.running_game = True
    game_state_instance.game_over_flag = False # Le tutoriel peut utiliser ce flag pour indiquer sa fin
    game_state_instance.game_paused = False

    # --- Logique spécifique au tutoriel ---
    current_tutorial_step = 0
    tutorial_objectives_met = [False] * 5 # Exemple: 5 étapes
    # Structure des étapes (exemple simplifié)
    tutorial_steps = [
        {"msg": "Bienvenue! Construisez une 'Structure' (icône 1) sur la grille.", "condition": lambda gs: any(b.type == "frame" for b in gs.buildings)},
        {"msg": "Placez un 'Générateur' (icône 2) sur une structure.", "condition": lambda gs: any(b.type == "generator" for b in gs.buildings)},
        {"msg": "Placez une 'Mine de Fer' (icône 4) sur la rangée renforcée (plus foncée) ou sur une autre mine.", "condition": lambda gs: any(b.type == "miner" for b in gs.buildings)},
        {"msg": "Construisez une 'Tourelle Gatling' (icône 5) sur une structure.", "condition": lambda gs: any(t.type == "gatling_turret" for t in gs.turrets)},
        {"msg": "Parfait ! Le tutoriel est terminé. Appuyez sur Echap pour quitter.", "condition": lambda gs: False} # Condition jamais remplie, fin manuelle
    ]
    
    # Afficher le premier message
    if tutorial_steps:
         game_state_instance.show_tutorial_message(tutorial_steps[0]["msg"], duration=999) # Message persistant

    print("Lancement du Mode Tutoriel...")

    while game_state_instance.running_game:
        delta_time = game_state_instance.clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                return cfg.STATE_QUIT # <--- AJOUT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Esc quitte toujours le tutoriel vers le menu
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
            
            # Gestion Input spécifique à l'état (Pause, Fin Tuto, Jeu Actif)
            if game_state_instance.game_paused: # Le tutoriel peut-il être mis en pause ? Oui.
                action = ui_functions.check_pause_menu_click(event, mouse_pos)
                if action == "resume":
                    game_state_instance.toggle_pause()
                elif action == "restart": # Recommencer le tutoriel
                     game_state_instance.running_game = False
                     return "restart_tutorial" # Signal spécifique
                elif action == cfg.STATE_MENU:
                    game_state_instance.running_game = False
                    return cfg.STATE_MENU
                elif action == cfg.STATE_QUIT:
                    game_state_instance.running_game = False
                    return cfg.STATE_QUIT
            elif game_state_instance.game_over_flag: # Fin du tutoriel (utilisation du flag game_over)
                # Utiliser un écran de fin de tutoriel (peut être simple texte ou reuse game over)
                 action = ui_functions.check_game_over_menu_click(event, mouse_pos) # Ou une fonction dédiée check_tutorial_end_click
                 if action == cfg.STATE_MENU:
                     game_state_instance.running_game = False
                     return cfg.STATE_MENU
                 elif action == cfg.STATE_QUIT:
                     game_state_instance.running_game = False
                     return cfg.STATE_QUIT
            else: # Tutoriel actif
                game_state_instance.handle_player_input(event, mouse_pos)

                # Vérifier si l'objectif de l'étape actuelle est atteint
                if current_tutorial_step < len(tutorial_steps):
                    condition_func = tutorial_steps[current_tutorial_step].get("condition")
                    if condition_func and condition_func(game_state_instance):
                         print(f"Tutoriel: Étape {current_tutorial_step} terminée.")
                         current_tutorial_step += 1
                         if current_tutorial_step < len(tutorial_steps):
                             game_state_instance.show_tutorial_message(tutorial_steps[current_tutorial_step]["msg"], duration=999)
                         else:
                             # Dernière étape atteinte
                             game_state_instance.show_tutorial_message("Tutoriel terminé! Appuyez sur Echap.", duration=999)
                             # On pourrait utiliser game_over_flag ici pour afficher l'écran de fin
                             # game_state_instance.game_over_flag = True


        # --- Logique du Jeu (limitée pour le tuto si besoin) ---
        if not game_state_instance.game_paused:
            # Pas de vagues dans ce tutoriel simple, mais on update quand même les ressources/timers
            game_state_instance.update_timers_and_waves(delta_time) # Gère les timers des messages
            game_state_instance.update_resources_per_tick(delta_time)
            # Mettre à jour les objets placés (tourelles etc.) même s'il n'y a pas d'ennemis
            is_globally_powered = game_state_instance.electricity_produced >= game_state_instance.electricity_consumed
            for turret in game_state_instance.turrets:
                 turret.update(delta_time, [], is_globally_powered, game_state_instance) # Pas d'ennemis à viser
            # Pas besoin d'update_game_logic complet qui gère vagues/ennemis/collisions ici

        # --- Affichage ---
        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements() # Affiche top bar, build menu, et messages tuto/erreur

        # Gérer l'affichage de fin de tutoriel (si on utilise game_over_flag)
        # if game_state_instance.game_over_flag:
        #     ui_functions.draw_game_over_screen(screen, "Tutoriel Complété") # Passer un message au lieu du score

        pygame.display.flip()

     print("Mode Tutoriel terminé.")
     return cfg.STATE_MENU # Retourner au menu par défaut
