# main.py
import pygame
import sys # Pour quitter proprement
import game_config as cfg
import utility_func as util # Fonctions utilitaires (chargement, etc.)
import ui_functions   # Pour le menu principal, écrans de lore, etc.
import gamemodes      # Contient les boucles pour les modes de jeu (principal, tutoriel)
import game_functions # Pour l'instance GameState

def main():
    # --- Initialisation de Pygame et de ses modules ---
    pygame.init()
    pygame.mixer.init() # Initialiser le mixer pour les sons (important!)
    
    # Créer la fenêtre du jeu
    # Utilise les dimensions de cfg, qui sont déjà potentiellement scalées
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption(cfg.GAME_TITLE)
    # TODO: Définir une icône pour la fenêtre
    # try:
    #     icon = util.load_sprite(cfg.UI_SPRITE_PATH + "game_icon.png") # SPRITE: Votre icône de jeu
    #     pygame.display.set_icon(icon)
    # except Exception as e:
    #     print(f"Erreur de chargement de l'icône: {e}")

    clock = pygame.time.Clock()

    # --- Création de l'instance de l'état du jeu ---
    # Cette instance sera passée aux différents modes de jeu.
    # Elle contient toutes les variables d'état (ressources, grille, listes d'objets, etc.)
    current_game_state_instance = game_functions.GameState()
    current_game_state_instance.screen = screen # Attribuer l'écran et l'horloge
    current_game_state_instance.clock = clock
    current_game_state_instance.load_ui_icons() # Charger les icônes UI une fois

    # Initialiser les layouts des menus UI (si pas déjà fait ailleurs au besoin)
    ui_functions.initialize_main_menu_layout()
    ui_functions.initialize_build_menu_layout(current_game_state_instance) # Nécessite game_state pour coûts dynamiques

    # --- Machine d'état du jeu ---
    application_running = True
    current_application_state = cfg.STATE_MENU # Commencer par le menu principal

    while application_running:
        # Gérer les événements globaux (comme QUITTER l'application)
        # Les événements spécifiques à un état (ex: clic sur bouton "Jouer")
        # sont gérés dans les fonctions de cet état.
        
        mouse_pos = pygame.mouse.get_pos() # Position de la souris, utile pour tous les états

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                application_running = False # Sortir de la boucle principale de l'application

            # --- Logique de la Machine d'État ---
            if current_application_state == cfg.STATE_MENU:
                action = ui_functions.check_main_menu_click(event, mouse_pos)
                if action is not None:
                    if action == cfg.STATE_QUIT:
                        application_running = False
                    else:
                        current_application_state = action # Change d'état (vers Jeu, Lore, etc.)
            
            elif current_application_state == cfg.STATE_LORE:
                # L'écran de lore pourrait se terminer par un clic ou une touche
                if event.type == pygame.MOUSEBUTTONDOWN or \
                   (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    current_application_state = cfg.STATE_MENU # Retour au menu après le lore
            
            # Les événements pour STATE_GAMEPLAY et STATE_TUTORIAL sont gérés
            # à l'intérieur de leurs boucles respectives dans gamemodes.py


        # --- Exécution de l'État Actuel ---
        if current_application_state == cfg.STATE_MENU:
            ui_functions.draw_main_menu(screen)
        
        elif current_application_state == cfg.STATE_LORE:
            ui_functions.draw_lore_screen(screen) # Affiche l'écran de lore

        elif current_application_state == cfg.STATE_GAMEPLAY:
            # Lance le mode de jeu principal. Cette fonction a sa propre boucle.
            # Quand elle se termine, on revient ici (typiquement à l'état menu).
            gamemodes.run_main_game_mode(screen, clock, current_game_state_instance)
            current_application_state = cfg.STATE_MENU # Retour au menu après le jeu
            # Réinitialiser/recharger les layouts UI si nécessaire après un mode de jeu
            ui_functions.initialize_main_menu_layout() 
            ui_functions.initialize_build_menu_layout(current_game_state_instance)


        elif current_application_state == cfg.STATE_TUTORIAL:
            gamemodes.run_tutorial_mode(screen, clock, current_game_state_instance)
            current_application_state = cfg.STATE_MENU # Retour au menu après le tutoriel
            ui_functions.initialize_main_menu_layout()
            ui_functions.initialize_build_menu_layout(current_game_state_instance)

        elif current_application_state == cfg.STATE_OPTIONS:
            # TODO: Implémenter l'écran d'options
            # ui_functions.draw_options_screen(screen)
            # action = ui_functions.check_options_menu_click(event, mouse_pos)
            # if action == "back_to_menu": current_application_state = cfg.STATE_MENU
            print("État Options (non implémenté)")
            current_application_state = cfg.STATE_MENU # Placeholder

        # Mettre à jour l'affichage global (surtout pour les états simples comme Menu/Lore)
        pygame.display.flip()
        clock.tick(cfg.FPS) # Contrôler le framerate global

    # --- Fin du Jeu ---
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
