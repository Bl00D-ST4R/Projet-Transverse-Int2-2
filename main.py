# main.py
import pygame
import sys 
import game_config as cfg
import utility_functions as util # Assurez-vous que le nom est correct
import ui_functions
import gamemodes
import game_functions 

def main_application_loop():
    """
    Contient la boucle principale de l'application et la gestion des états.
    Assume que Pygame est déjà initialisé.
    """
    screen = pygame.display.get_surface() 
    if not screen:
        print("ERREUR: Écran non initialisé avant d'entrer dans la boucle principale.")
        return

    clock = pygame.time.Clock()

    current_game_state_instance = game_functions.GameState()
    current_game_state_instance.screen = screen
    current_game_state_instance.clock = clock
    current_game_state_instance.load_ui_icons()

    ui_functions.initialize_main_menu_layout()
    ui_functions.initialize_build_menu_layout(current_game_state_instance)
    ui_functions.initialize_pause_menu_layout() # Initialiser aussi le menu pause
    ui_functions.initialize_game_over_layout() # Initialiser aussi le menu game over

    application_running = True
    current_application_state = cfg.STATE_MENU

    while application_running:
        mouse_pos = pygame.mouse.get_pos()
        next_state = None # Réinitialiser l'état demandé à chaque frame

        # --- Gestion des Événements Spécifiques à l'État ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                application_running = False
                next_state = cfg.STATE_QUIT # Marquer pour quitter proprement

            # --- Logique Machine d'État ---
            if current_application_state == cfg.STATE_MENU:
                action = ui_functions.check_main_menu_click(event, mouse_pos)
                if action is not None:
                     next_state = action # L'action est déjà un état ou STATE_QUIT

            elif current_application_state == cfg.STATE_LORE:
                if event.type == pygame.MOUSEBUTTONDOWN or \
                   (event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE)):
                    next_state = cfg.STATE_MENU

            # Les événements pour GAMEPLAY et TUTORIAL sont gérés DANS leurs boucles respectives (gamemodes.py)
            # On ne gère ici que les événements QUI FONT SORTIR de ces modes ou changer l'état global.
            # Ces modes de jeu retournent l'état suivant quand ils se terminent.

            # Gérer le cas où un état non prévu serait actif
            # else:
            #     print(f"Avertissement: Gestion d'événement pour l'état inconnu {current_application_state}")


        # --- Exécution de l'État Actuel ---
        # Seulement exécuter le code de l'état si next_state n'a pas déjà été défini par un événement
        if next_state is None:
            if current_application_state == cfg.STATE_MENU:
                ui_functions.draw_main_menu(screen)
            
            elif current_application_state == cfg.STATE_LORE:
                ui_functions.draw_lore_screen(screen)

            elif current_application_state == cfg.STATE_GAMEPLAY:
                # CORRIGÉ: Récupérer l'état retourné par le mode de jeu
                # La boucle interne de run_main_game_mode gère ses propres événements
                returned_state = gamemodes.run_main_game_mode(screen, clock, current_game_state_instance)
                next_state = returned_state # Mettre à jour l'état suivant basé sur le retour du mode jeu
                
                # Gérer le signal de redémarrage spécifique
                if next_state == "restart_game":
                    print("Redémarrage du mode de jeu principal...")
                    next_state = cfg.STATE_GAMEPLAY # Revenir immédiatement à l'état gameplay
                    # La réinitialisation se fera au début de run_main_game_mode

                # Réinitialiser les layouts UI des menus après être sorti du mode jeu (sauf si on quitte)
                if next_state != cfg.STATE_QUIT and next_state != cfg.STATE_GAMEPLAY: # Ne pas réinitialiser si on quitte ou redémarre immédiatement
                    print("Retour au menu, réinitialisation des layouts UI...")
                    ui_functions.initialize_main_menu_layout()
                    # Le layout du build menu n'a pas besoin d'être réinitialisé sauf si la résolution change
                    # ui_functions.initialize_build_menu_layout(current_game_state_instance) 

            elif current_application_state == cfg.STATE_TUTORIAL:
                returned_state = gamemodes.run_tutorial_mode(screen, clock, current_game_state_instance)
                next_state = returned_state
                
                if next_state == "restart_tutorial":
                     print("Redémarrage du tutoriel...")
                     next_state = cfg.STATE_TUTORIAL
                
                if next_state != cfg.STATE_QUIT and next_state != cfg.STATE_TUTORIAL:
                    print("Retour au menu depuis tuto, réinitialisation layout menu...")
                    ui_functions.initialize_main_menu_layout()
                    # ui_functions.initialize_build_menu_layout(current_game_state_instance)

            elif current_application_state == cfg.STATE_OPTIONS:
                print("État Options (non implémenté)") # Placeholder
                # TODO: ui_functions.draw_options_screen(screen)
                # action = ui_functions.check_options_menu_click(event, mouse_pos) ...
                next_state = cfg.STATE_MENU

        # --- Mise à jour de l'État ---
        if next_state is not None:
            if next_state == cfg.STATE_QUIT:
                application_running = False # Arrêter la boucle principale
            else:
                # Vérifier si l'état change réellement pour éviter des prints inutiles
                if current_application_state != next_state:
                    print(f"Changement d'état: {current_application_state} -> {next_state}")
                    current_application_state = next_state # Changer l'état pour la prochaine frame
                # Si next_state est le même que current_state, on ne fait rien (ex: redémarrage)

        pygame.display.flip()
        # Le tick du clock est géré à l'intérieur des boucles de gamemodes si elles sont actives,
        # ou ici si on est dans un état simple comme MENU ou LORE.
        # Pour simplifier, on peut le laisser ici, même s'il sera appelé en plus dans les gamemodes.
        # Une meilleure approche serait de passer delta_time aux fonctions draw des états simples.
        # Ou de ne PAS appeler clock.tick() dans les gamemodes. Laissons-le ici pour l'instant.
        clock.tick(cfg.FPS) 

    print("Fin de la boucle principale de l'application.")
    # Pas besoin de retourner quoi que ce soit ici, la fin de la boucle suffit.


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

    print(f"Configuration de l'affichage: {cfg.SCREEN_WIDTH}x{cfg.SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption(cfg.GAME_TITLE)

    try:
        icon_path = cfg.UI_SPRITE_PATH + "game_icon_32.png" # Assurez-vous que ce fichier existe
        import os # Importer os ici si ce n'est pas déjà fait globalement
        if os.path.exists(icon_path):
            game_icon = util.load_sprite(icon_path, use_alpha=True) # Charger avec transparence
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
    main_application_loop() # Lance la logique principale du jeu

    print("Fermeture de Pygame...")
    pygame.mixer.quit() 
    pygame.quit()       
    sys.exit()          


if __name__ == '__main__':
    run_game() 
