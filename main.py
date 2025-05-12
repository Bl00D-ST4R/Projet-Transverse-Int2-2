# main.py
import pygame
import sys
import os
import game_config as cfg
import utility_functions as util
import ui_functions
import gamemodes
import game_functions


def main_application_loop(screen, clock, scaler):
    current_game_state_instance = game_functions.GameState(scaler)
    current_game_state_instance.screen = screen
    current_game_state_instance.clock = clock #initialisation of the clock
    current_game_state_instance.load_ui_icons() #chargement des icones


    ui_functions.initialize_main_menu_layout(scaler)
    ui_functions.initialize_build_menu_layout(current_game_state_instance, scaler) # Passe game_state pour les coûts
    ui_functions.initialize_pause_menu_layout(scaler) # pause menu
    ui_functions.initialize_game_over_layout(scaler)  # game over screen

    application_running = True
    current_application_state = cfg.STATE_MENU # Commencer par le menu principal

    while application_running:
        mouse_pos = pygame.mouse.get_pos()
        # next_state doit être réinitialisé à chaque tour de boucle
        # pour ne pas rester bloqué sur un état retourné par un mode de jeu
        next_state_from_event = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                application_running = False
                # exit for the loop


            if current_application_state == cfg.STATE_MENU:
                action = ui_functions.check_main_menu_click(event, mouse_pos, scaler)
                if action is not None:
                    next_state_from_event = action

            elif current_application_state == cfg.STATE_LORE:
                if event.type == pygame.MOUSEBUTTONDOWN or \
                   (event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE)):
                    next_state_from_event = cfg.STATE_MENU

            # Les événements pour GAMEPLAY et TUTORIAL sont gérés DANS leurs boucles respectives
            # gamemodes.py gère les inputs quand le jeu est actif, en pause, ou game over.

        # Si un événement a déjà déterminé le prochain état (ex: clic sur menu)
        if next_state_from_event is not None:
            if next_state_from_event == cfg.STATE_QUIT:
                application_running = False
            else:
                if cfg.DEBUG_MODE and current_application_state != next_state_from_event:
                    print(f"MAIN_APP_LOOP: Event changed state from {current_application_state} to {next_state_from_event}")
                current_application_state = next_state_from_event

        # --- Exécution et Dessin de l'État Actuel ---
        screen.fill(cfg.COLOR_BACKGROUND) # Remplir l'écran au début de chaque frame de la boucle principale

        if current_application_state == cfg.STATE_MENU:
            ui_functions.draw_main_menu(screen, scaler)

        elif current_application_state == cfg.STATE_LORE:
            ui_functions.draw_lore_screen(screen, scaler)

        elif current_application_state == cfg.STATE_GAMEPLAY:
            returned_state = gamemodes.run_main_game_mode(screen, clock, current_game_state_instance, scaler)
            # Après la fin de run_main_game_mode, on met à jour l'état
            if returned_state == "restart_game": # Logique pour redémarrer
                 # Réinitialiser l'instance GameState pour un nouveau jeu
                 current_game_state_instance = game_functions.GameState(scaler)
                 current_game_state_instance.screen = screen
                 current_game_state_instance.clock = clock
                 current_game_state_instance.load_ui_icons()
                 # Il faut aussi réinitialiser les layouts qui dépendent de game_state si nécessaire
                 ui_functions.initialize_build_menu_layout(current_game_state_instance, scaler)
                 current_application_state = cfg.STATE_GAMEPLAY # Reste dans le même état, init_new_game sera appelé
            elif returned_state == cfg.STATE_QUIT:
                 application_running = False
            else: # Typiquement retour au menu ou autre état défini par returned_state
                 current_application_state = returned_state if returned_state else cfg.STATE_MENU
                 if current_application_state == cfg.STATE_MENU:
                     ui_functions.initialize_main_menu_layout(scaler)


        elif current_application_state == cfg.STATE_TUTORIAL:
            returned_state = gamemodes.run_tutorial_mode(screen, clock, current_game_state_instance, scaler)
            if returned_state == "restart_tutorial":
                # Réinitialiser l'instance GameState pour un nouveau tutoriel
                current_game_state_instance = game_functions.GameState(scaler)
                current_game_state_instance.screen = screen
                current_game_state_instance.clock = clock
                current_game_state_instance.load_ui_icons()
                current_game_state_instance.is_tutorial = True # S'assurer que le mode tutoriel est bien actif
                ui_functions.initialize_build_menu_layout(current_game_state_instance, scaler)
                current_application_state = cfg.STATE_TUTORIAL
            elif returned_state == cfg.STATE_QUIT:
                application_running = False
            else: # Typiquement retour au menu ou autre état défini par returned_state
                current_application_state = returned_state if returned_state else cfg.STATE_MENU
                if current_application_state == cfg.STATE_MENU:
                    ui_functions.initialize_main_menu_layout(scaler)


        elif current_application_state == cfg.STATE_OPTIONS:
            if cfg.DEBUG_MODE: print("État Options (non implémenté)")
            # action = ui_functions.check_options_menu_click(event, mouse_pos, scaler) ...
            current_application_state = cfg.STATE_MENU # Placeholder pour retourner au menu

        pygame.display.flip()
        clock.tick(cfg.FPS)

    print("Fin de main_application_loop.")


#main game running loop
def run_game():
    print("Initialisation de Pygame...")
    pygame.init()
    try:
        pygame.mixer.init()
        if cfg.DEBUG_MODE: print("Pygame Mixer initialisé.")
    except pygame.error as e:
        print(f"AVERTISSEMENT: Mixer init échoué: {e}")

    # ndt : La classe Scaler utilise screen.get_size() pour la taille réelle
    screen_width_request = cfg.REF_WIDTH
    screen_height_request = cfg.REF_HEIGHT
    if cfg.DEBUG_MODE: print(f"Configuration de l'affichage (demandé): {screen_width_request}x{screen_height_request}")

    screen = pygame.display.set_mode((screen_width_request, screen_height_request))
    pygame.display.set_caption(cfg.GAME_TITLE)

    actual_screen_width, actual_screen_height = screen.get_size()
    scaler = util.Scaler(actual_screen_width, actual_screen_height, cfg.REF_WIDTH, cfg.REF_HEIGHT)

    try:
        icon_path = os.path.join(cfg.UI_SPRITE_PATH, "game_icon_32.png") # Assurez-vous que ce fichier existe
        if os.path.exists(icon_path):
            game_icon = util.load_sprite(icon_path) # Ne scale pas ici
            if game_icon and game_icon.get_width() > 0:
               pygame.display.set_icon(game_icon)
               if cfg.DEBUG_MODE: print("Icône du jeu définie.")
        # else: if cfg.DEBUG_MODE: print(f"Icône non trouvée: {icon_path}")
    except Exception as e_icon:
        if cfg.DEBUG_MODE: print(f"Erreur icône: {e_icon}")

    print("Lancement de la boucle principale de l'application...")
    main_application_loop(screen, pygame.time.Clock(), scaler)

    print("Fermeture de Pygame...")
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


#the mainmain
if __name__ == '__main__':
    run_game()
