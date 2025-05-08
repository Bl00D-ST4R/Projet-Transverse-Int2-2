# main.py
import pygame
import sys 
import game_config as cfg
import utility_functions as util # CORRIGÉ: Nom du module
import ui_functions
import gamemodes
import game_functions 

def main_application_loop():
    """
    Contient la boucle principale de l'application et la gestion des états.
    Assume que Pygame est déjà initialisé.
    """
    screen = pygame.display.get_surface() # Récupère l'écran initialisé
    if not screen:
        print("ERREUR: Écran non initialisé avant d'entrer dans la boucle principale.")
        return

    clock = pygame.time.Clock()

    current_game_state_instance = game_functions.GameState()
    current_game_state_instance.screen = screen
    current_game_state_instance.clock = clock
    current_game_state_instance.load_ui_icons()

    ui_functions.initialize_main_menu_layout()
    # Passe game_state pour que initialize_build_menu_layout puisse accéder aux coûts si besoin
    ui_functions.initialize_build_menu_layout(current_game_state_instance)


    application_running = True
    current_application_state = cfg.STATE_MENU

    while application_running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                application_running = False

            if current_application_state == cfg.STATE_MENU:
                action = ui_functions.check_main_menu_click(event, mouse_pos)
                if action is not None:
                    if action == cfg.STATE_QUIT:
                        application_running = False
                    else:
                        current_application_state = action
            
            elif current_application_state == cfg.STATE_LORE:
                if event.type == pygame.MOUSEBUTTONDOWN or \
                   (event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE)):
                    current_application_state = cfg.STATE_MENU
            
            # Les événements pour GAMEPLAY et TUTORIAL sont dans leurs boucles gamemodes

        # --- Exécution de l'État Actuel ---
        if current_application_state == cfg.STATE_MENU:
            ui_functions.draw_main_menu(screen)
        
        elif current_application_state == cfg.STATE_LORE:
            ui_functions.draw_lore_screen(screen)

        elif current_application_state == cfg.STATE_GAMEPLAY:
            gamemodes.run_main_game_mode(screen, clock, current_game_state_instance)
            current_application_state = cfg.STATE_MENU
            ui_functions.initialize_main_menu_layout() # Réinitialiser au cas où
            ui_functions.initialize_build_menu_layout(current_game_state_instance)


        elif current_application_state == cfg.STATE_TUTORIAL:
            gamemodes.run_tutorial_mode(screen, clock, current_game_state_instance)
            current_application_state = cfg.STATE_MENU
            ui_functions.initialize_main_menu_layout()
            ui_functions.initialize_build_menu_layout(current_game_state_instance)

        elif current_application_state == cfg.STATE_OPTIONS:
            print("État Options (non implémenté)") # Placeholder
            # TODO: ui_functions.draw_options_screen(screen)
            # action = ui_functions.check_options_menu_click(event, mouse_pos) ...
            current_application_state = cfg.STATE_MENU

        pygame.display.flip()
        clock.tick(cfg.FPS)

    return # Fin de la boucle de l'application


def run_game():
    """
    Fonction principale qui initialise Pygame, lance la boucle de l'application,
    et nettoie en quittant.
    C'EST LE POINT D'ENTRÉE PRINCIPAL.
    """
    print("Initialisation de Pygame...")
    pygame.init()  # Initialise tous les modules Pygame importés
    
    # Il est crucial d'initialiser le mixer APRÈS pygame.init() et AVANT de charger des sons.
    try:
        pygame.mixer.init()
        print("Pygame Mixer initialisé.")
    except pygame.error as e:
        print(f"AVERTISSEMENT: Impossible d'initialiser Pygame Mixer: {e}. Les sons pourraient ne pas fonctionner.")

    print(f"Configuration de l'affichage: {cfg.SCREEN_WIDTH}x{cfg.SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption(cfg.GAME_TITLE)

    # SPRITE: Définir une icône pour la fenêtre (optionnel mais recommandé)
    try:
        # Assurez-vous que le chemin et le nom du fichier sont corrects.
        icon_path = cfg.UI_SPRITE_PATH + "game_icon_32.png" # Exemple de nom
        # Vérifier si le fichier existe avant de tenter de le charger peut être une bonne idée.
        # import os
        # if os.path.exists(icon_path):
        #   game_icon = util.load_sprite(icon_path) # load_sprite gère les erreurs
        #   if game_icon and game_icon.get_width() > 0 : # S'assurer que le chargement n'a pas renvoyé un placeholder vide
        #       pygame.display.set_icon(game_icon)
        #       print("Icône du jeu définie.")
        #   else:
        #       print(f"AVERTISSEMENT: L'icône du jeu '{icon_path}' n'a pas pu être chargée correctement.")
        # else:
        #   print(f"AVERTISSEMENT: Fichier d'icône du jeu non trouvé à '{icon_path}'.")
        pass # Placeholder pour le code de l'icône, à décommenter et adapter
    except Exception as e_icon:
        print(f"AVERTISSEMENT: Erreur lors de la configuration de l'icône du jeu: {e_icon}")

    print("Lancement de la boucle principale de l'application...")
    main_application_loop() # Lance la logique principale du jeu

    print("Fermeture de Pygame...")
    pygame.mixer.quit() # Important de quitter le mixer
    pygame.quit()       # Désinitialise tous les modules Pygame
    sys.exit()          # Termine le programme Python


if __name__ == '__main__':
    run_game() # Appelle la fonction qui gère l'initialisation et la boucle principale
