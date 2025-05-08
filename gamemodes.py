# gamemodes.py
import pygame
import game_config as cfg
import utility_functions as util # CORRIGÉ: Nom du module
import game_functions 
import ui_functions   


def run_main_game_mode(screen, clock, game_state_instance):
    """
    Lance et gère la boucle principale du mode de jeu standard.
    """
    game_state_instance.init_new_game(screen, clock) # Réinitialise l'état pour une nouvelle partie
    game_state_instance.running_game = True
    game_state_instance.game_over_flag = False
    game_state_instance.game_paused = False

    print("Lancement du Mode de Jeu Principal...")

    while game_state_instance.running_game:
        delta_time = game_state_instance.clock.tick(cfg.FPS) / 1000.0 # Secondes écoulées

        # --- Gestion des Événements ---
        mouse_pos = pygame.mouse.get_pos() # Obtenir la position de la souris une fois par frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
                # Pourrait retourner un code pour quitter complètement l'application
                # return cfg.STATE_QUIT 
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag:
                        # Si game over, Esc revient au menu principal
                        game_state_instance.running_game = False 
                    else:
                        game_state_instance.toggle_pause()
                # TODO: Ajouter d'autres raccourcis clavier si nécessaire (ex: ouvrir menu construction)

            # Passer les événements à game_functions pour la construction, etc., seulement si pas en pause
            if not game_state_instance.game_paused and not game_state_instance.game_over_flag:
                game_state_instance.handle_player_input(event, mouse_pos)
            elif game_state_instance.game_paused:
                # Gérer les clics sur le menu pause (ex: Reprendre, Quitter au menu)
                action = ui_functions.check_pause_menu_click(event, mouse_pos)
                if action == "resume":
                    game_state_instance.toggle_pause()
                elif action == "quit_to_menu":
                    game_state_instance.running_game = False
            elif game_state_instance.game_over_flag:
                # Gérer les clics sur l'écran de game over (ex: Rejouer, Menu Principal)
                action = ui_functions.check_game_over_menu_click(event, mouse_pos)
                if action == "retry": # Si on implémente un bouton rejouer
                    game_state_instance.init_new_game(screen, clock) # Réinitialise pour un nouvel essai
                elif action == "quit_to_menu":
                    game_state_instance.running_game = False


        # --- Logique du Jeu ---
        # game_functions.update_game_logic s'occupe de tout si pas en pause
        game_state_instance.update_game_logic(delta_time)


        # --- Affichage ---
        # 1. Dessiner le monde du jeu (grille, bâtiments, ennemis, projectiles)
        game_state_instance.draw_game_world()

        # 2. Dessiner l'interface utilisateur par-dessus (barres de ressources, menus)
        game_state_instance.draw_game_ui_elements() # Gère aussi l'écran de pause et game over

        pygame.display.flip() # Mettre à jour l'affichage complet

    print("Mode de Jeu Principal terminé.")
    # Retourne implicitement au menu principal (géré dans main.py)


def run_tutorial_mode(screen, clock, game_state_instance):
    """
    Lance et gère la boucle du mode tutoriel.
    (Pour l'instant, c'est une copie du mode principal, à adapter avec des objectifs spécifiques)
    """
    game_state_instance.init_new_game(screen, clock)
    game_state_instance.running_game = True
    game_state_instance.game_over_flag = False # Le tutoriel peut avoir ses propres conditions de fin
    game_state_instance.game_paused = False

    # MODIFIABLE: Paramètres spécifiques au tutoriel
    # game_state_instance.money = 5000 # Plus d'argent pour commencer
    # game_state_instance.all_wave_definitions = wave_definitions.load_tutorial_waves() # Vagues plus simples
    # game_state_instance.max_waves = len(game_state_instance.all_wave_definitions)
    # game_state_instance.set_time_for_first_wave() # Pourrait avoir un temps de prépa différent

    current_tutorial_step = 0
    tutorial_messages = [
        "Bienvenue! Construisez une 'Fondation' (clic gauche sur l'icône puis sur la grille).",
        "Excellent! Maintenant, placez un 'Générateur' sur une fondation.",
        "Placez une 'Mine de Fer' sur la rangée du bas ou sur une autre mine.",
        "Construisez une 'Tourelle Gatling' sur une fondation pour vous défendre.",
        "Préparez-vous, des ennemis arrivent bientôt !"
    ]
    # TODO: Afficher ces messages et vérifier les conditions pour passer à l'étape suivante.

    print("Lancement du Mode Tutoriel...")

    while game_state_instance.running_game:
        delta_time = game_state_instance.clock.tick(cfg.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state_instance.running_game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state_instance.game_over_flag: # Ou fin du tutoriel
                        game_state_instance.running_game = False
                    else:
                        game_state_instance.toggle_pause()
            
            # Gestion des inputs pour le tutoriel
            if not game_state_instance.game_paused and not game_state_instance.game_over_flag:
                game_state_instance.handle_player_input(event, mouse_pos)
                # TODO: Vérifier si l'action du joueur correspond à l'objectif du tutoriel actuel
                # if current_tutorial_step == 0 and any(b.type == "foundation" for b in game_state_instance.buildings):
                #     current_tutorial_step += 1
                #     game_state_instance.show_error_message(tutorial_messages[current_tutorial_step], 5)
                # etc.

            elif game_state_instance.game_paused:
                action = ui_functions.check_pause_menu_click(event, mouse_pos)
                if action == "resume": game_state_instance.toggle_pause()
                elif action == "quit_to_menu": game_state_instance.running_game = False
            elif game_state_instance.game_over_flag: # Fin du tutoriel (réussi ou échoué)
                 action = ui_functions.check_game_over_menu_click(event, mouse_pos) # Utiliser un écran de fin de tuto
                 if action == "quit_to_menu": game_state_instance.running_game = False


        game_state_instance.update_game_logic(delta_time)
        
        # TODO: Vérifier les conditions de fin du tutoriel
        # if current_tutorial_step >= len(tutorial_messages) and not game_state_instance.wave_in_progress and not game_state_instance.enemies:
        #     game_state_instance.show_error_message("Tutoriel terminé avec succès!", 10)
        #     game_state_instance.game_over_flag = True # Marquer comme terminé

        game_state_instance.draw_game_world()
        game_state_instance.draw_game_ui_elements()
        
        # Afficher le message du tutoriel actuel
        if not game_state_instance.game_over_flag and current_tutorial_step < len(tutorial_messages):
             # S'assurer que ce message ne se superpose pas trop avec show_error_message
            if game_state_instance.error_message_timer <=0:
                ui_functions.draw_tutorial_message(game_state_instance.screen, tutorial_messages[current_tutorial_step])


        pygame.display.flip()

    print("Mode Tutoriel terminé.")


# --- Fonctions pour le menu principal et l'animation de lore (si déplacées ici) ---
# (Pour l'instant, on suppose qu'elles sont dans main.py ou ui_functions.py)

# def run_lore_animation(screen, clock):
#     print("Affichage de l'animation/lore...")
#     # ... logique de l'animation ...
#     # Retourne au menu principal une fois terminé ou skippé

# def run_main_menu(screen, clock):
#     print("Affichage du Menu Principal...")
#     # ... logique du menu avec boutons ...
#     # Retourne un code d'état (STATE_GAMEPLAY, STATE_TUTORIAL, STATE_LORE, STATE_QUIT)
