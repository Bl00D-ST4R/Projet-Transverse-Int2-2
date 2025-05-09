# main.py
import pygame
import sys
import game_config as cfg
import utility_functions as util # Assurez-vous que le nom est correct et Scaler is here
import ui_functions
import gamemodes
import game_functions

# MODIFIED: Accepte screen, clock, et scaler
def main_application_loop(screen, clock, scaler):
    """
    Contient la boucle principale de l'application et la gestion des états.
    Assume que Pygame est déjà initialisé et que scaler est fourni.
    """
    # screen et clock sont maintenant passés en arguments

    # MODIFIED: Passe le scaler à GameState
    current_game_state_instance = game_functions.GameState(scaler)
    current_game_state_instance.screen = screen
    current_game_state_instance.clock = clock
    # load_ui_icons ne scale pas lui-même, il charge les originaux
    current_game_state_instance.load_ui_icons()

    # MODIFIED: Passe le scaler aux initialisations UI
    ui_functions.initialize_main_menu_layout(scaler)
    ui_functions.initialize_build_menu_layout(current_game_state_instance, scaler)
    ui_functions.initialize_pause_menu_layout(scaler)
    ui_functions.initialize_game_over_layout(scaler)

    application_running = True
    current_application_state = cfg.STATE_MENU

    while application_running:
        mouse_pos = pygame.mouse.get_pos()
        next_state = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                application_running = False
                next_state = cfg.STATE_QUIT

            if current_application_state == cfg.STATE_MENU:
                # MODIFIED: Passer le scaler aux fonctions de check de clic UI
                action = ui_functions.check_main_menu_click(event, mouse_pos, scaler)
                if action is not None:
                     next_state = action

            elif current_application_state == cfg.STATE_LORE:
                if event.type == pygame.MOUSEBUTTONDOWN or \
                   (event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE)):
                    next_state = cfg.STATE_MENU
        
        if next_state is None:
            if current_application_state == cfg.STATE_MENU:
                # MODIFIED: Passer scaler
                ui_functions.draw_main_menu(screen, scaler)
            
            elif current_application_state == cfg.STATE_LORE:
                # MODIFIED: Passer scaler
                ui_functions.draw_lore_screen(screen, scaler)

            elif current_application_state == cfg.STATE_GAMEPLAY:
                # MODIFIED: Passer scaler aux modes de jeu
                returned_state = gamemodes.run_main_game_mode(screen, clock, current_game_state_instance, scaler)
                next_state = returned_state
                
                if next_state == "restart_game":
                    print("Redémarrage du mode de jeu principal...")
                    next_state = cfg.STATE_GAMEPLAY 
                
                # MODIFIED: Passer scaler si réinitialisation
                if next_state != cfg.STATE_QUIT and next_state != cfg.STATE_GAMEPLAY:
                    print("Retour au menu, réinitialisation des layouts UI...")
                    ui_functions.initialize_main_menu_layout(scaler)
                    # ui_functions.initialize_build_menu_layout(current_game_state_instance, scaler) # Build menu layout likely fine unless resolution changed

            elif current_application_state == cfg.STATE_TUTORIAL:
                # MODIFIED: Passer scaler aux modes de jeu
                returned_state = gamemodes.run_tutorial_mode(screen, clock, current_game_state_instance, scaler)
                next_state = returned_state
                
                if next_state == "restart_tutorial":
                     print("Redémarrage du tutoriel...")
                     next_state = cfg.STATE_TUTORIAL
                
                # MODIFIED: Passer scaler si réinitialisation
                if next_state != cfg.STATE_QUIT and next_state != cfg.STATE_TUTORIAL:
                    print("Retour au menu depuis tuto, réinitialisation layout menu...")
                    ui_functions.initialize_main_menu_layout(scaler)
                    # ui_functions.initialize_build_menu_layout(current_game_state_instance, scaler)

            elif current_application_state == cfg.STATE_OPTIONS:
                print("État Options (non implémenté)")
                # ui_functions.draw_options_screen(screen, scaler) # MODIFIED if exists
                # action = ui_functions.check_options_menu_click(event, mouse_pos, scaler) # MODIFIED if exists
                next_state = cfg.STATE_MENU

        if next_state is not None:
            if next_state == cfg.STATE_QUIT:
                application_running = False
            else:
                if current_application_state != next_state:
                    print(f"Changement d'état: {current_application_state} -> {next_state}")
                    current_application_state = next_state

        pygame.display.flip()
        clock.tick(cfg.FPS)

    print("Fin de la boucle principale de l'application.")


def run_game():
    """
    Fonction principale qui initialise Pygame, lance la boucle de l'application,
    et nettoie en quittant.
    C'EST LE POINT D'ENTRÉE PRINCIPAL.
    """
    print("Initialisation de Pygame...")
    pygame.init()
    
    try:
        pygame.mixer.init()
        print("Pygame Mixer initialisé.")
    except pygame.error as e:
        print(f"AVERTISSEMENT: Impossible d'initialiser Pygame Mixer: {e}. Les sons pourraient ne pas fonctionner.")

    # MODIFIED: Utiliser REF_WIDTH et REF_HEIGHT de cfg car SCREEN_WIDTH/HEIGHT y ont été retirés
    # Ces valeurs seront utilisées pour initialiser l'écran.
    # Pour une vraie détection, vous utiliseriez pygame.display.Info() avant set_mode,
    # ou vous laisseriez set_mode choisir (ex: avec FULLSCREEN).
    detected_screen_width = cfg.REF_WIDTH
    detected_screen_height = cfg.REF_HEIGHT
    
    print(f"Configuration de l'affichage (référence/demandé): {detected_screen_width}x{detected_screen_height}")
    screen = pygame.display.set_mode((detected_screen_width, detected_screen_height))
    pygame.display.set_caption(cfg.GAME_TITLE)

    # --- Créer l'instance du Scaler APRES avoir défini le mode écran ---
    # Initialise le scaler avec les dimensions effectives de l'écran (ici, celles demandées)
    # et les dimensions de référence du jeu.
    actual_screen_width, actual_screen_height = screen.get_size() # Obtenir la taille réelle après set_mode
    scaler = util.Scaler(actual_screen_width, actual_screen_height, cfg.REF_WIDTH, cfg.REF_HEIGHT)


    try:
        icon_path = cfg.UI_SPRITE_PATH + "game_icon_32.png"
        import os
        if os.path.exists(icon_path):
            # load_sprite ne scale pas, il charge l'image originale.
            game_icon = util.load_sprite(icon_path, use_alpha=True)
            if game_icon and game_icon.get_width() > 0 :
               pygame.display.set_icon(game_icon)
               print("Icône du jeu définie.")
            else:
               print(f"AVERTISSEMENT: L'icône du jeu '{icon_path}' n'a pas pu être chargée correctement (fichier vide ou failsafe?).")
        else:
           print(f"AVERTISSEMENT: Fichier d'icône du jeu non trouvé à '{icon_path}'.")
    except Exception as e_icon:
        print(f"AVERTISSEMENT: Erreur lors de la configuration de l'icône du jeu: {e_icon}")

    print("Lancement de la boucle principale de l'application...")
    # MODIFIED: Passer screen, clock, et scaler à la boucle principale
    main_application_loop(screen, pygame.time.Clock(), scaler)

    print("Fermeture de Pygame...")
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    run_game()
