# ui_functions.py
import pygame
import game_config as cfg
import utility_func as util
# game_functions et objects sont accédés via l'instance game_state passée en argument

# --- Constantes spécifiques à l'UI (si non déjà dans cfg) ---
BUILD_MENU_BUTTON_PADDING = cfg.scale_value(5) # Espace entre les boutons du menu de construction
TOOLTIP_BG_COLOR = (30, 30, 30, 220) # Fond semi-transparent pour les tooltips
TOOLTIP_TEXT_COLOR = cfg.COLOR_WHITE
TOOLTIP_OFFSET_Y = cfg.scale_value(-30) # Décalage Y pour afficher le tooltip au-dessus du bouton

# --- Fonctions d'Affichage Générales ---

def draw_top_bar_ui(screen, game_state):
    """Affiche la barre supérieure avec les ressources, HP ville, vague."""
    top_bar_rect = pygame.Rect(0, 0, cfg.SCREEN_WIDTH, cfg.UI_TOP_BAR_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 30, 200), top_bar_rect) # Fond semi-transparent

    padding_x = cfg.scale_value(15)
    padding_y_center = cfg.UI_TOP_BAR_HEIGHT // 2
    icon_size = cfg.scale_value(30) # Taille pour les icônes de ressource
    current_x = padding_x

    # Icônes pré-scalées une fois si possible, ou scalées ici
    # Argent
    money_icon = util.scale_sprite_to_size(game_state.ui_icons.get('money'), icon_size, icon_size)
    if money_icon:
        screen.blit(money_icon, (current_x, padding_y_center - money_icon.get_height() // 2))
        current_x += money_icon.get_width() + cfg.scale_value(5)
    money_text_surf = util.render_text_surface(f"{int(game_state.money)} $", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_MONEY)
    screen.blit(money_text_surf, (current_x, padding_y_center - money_text_surf.get_height() // 2))
    current_x += money_text_surf.get_width() + padding_x * 1.5

    # Fer
    iron_icon = util.scale_sprite_to_size(game_state.ui_icons.get('iron'), icon_size, icon_size)
    if iron_icon:
        screen.blit(iron_icon, (current_x, padding_y_center - iron_icon.get_height() // 2))
        current_x += iron_icon.get_width() + cfg.scale_value(5)
    iron_text_surf = util.render_text_surface(
        f"{int(game_state.iron_stock)} / {game_state.iron_storage_capacity} Fe (+{game_state.iron_production_per_minute:.1f}/m)",
        cfg.FONT_SIZE_MEDIUM, cfg.COLOR_IRON
    )
    screen.blit(iron_text_surf, (current_x, padding_y_center - iron_text_surf.get_height() // 2))
    current_x += iron_text_surf.get_width() + padding_x * 1.5

    # Énergie
    energy_icon = util.scale_sprite_to_size(game_state.ui_icons.get('energy'), icon_size, icon_size)
    available_energy = game_state.electricity_produced - game_state.electricity_consumed
    energy_color = cfg.COLOR_ENERGY_OK if available_energy >= 0 else cfg.COLOR_ENERGY_FAIL
    if available_energy < 0 and available_energy > -5 : energy_color = cfg.COLOR_ENERGY_LOW # seuil pour orange

    if energy_icon:
        screen.blit(energy_icon, (current_x, padding_y_center - energy_icon.get_height() // 2))
        current_x += energy_icon.get_width() + cfg.scale_value(5)
    energy_text_surf = util.render_text_surface(
        f"{available_energy}W ({game_state.electricity_produced}P/{game_state.electricity_consumed}C)",
        cfg.FONT_SIZE_MEDIUM, energy_color
    )
    screen.blit(energy_text_surf, (current_x, padding_y_center - energy_text_surf.get_height() // 2))
    # current_x += energy_text_surf.get_width() + padding_x * 1.5 # Pas nécessaire si c'est le dernier à gauche

    # HP Ville (à droite de la barre)
    heart_icon_full = util.scale_sprite_to_size(game_state.ui_icons.get('heart_full'), icon_size, icon_size)
    heart_icon_empty = util.scale_sprite_to_size(game_state.ui_icons.get('heart_empty'), icon_size, icon_size)
    
    hp_per_heart = game_state.max_city_hp / cfg.CITY_HEARTS if cfg.CITY_HEARTS > 0 else game_state.max_city_hp
    full_hearts = int(game_state.city_hp / hp_per_heart) if hp_per_heart > 0 else 0
    
    city_hp_start_x = cfg.SCREEN_WIDTH - padding_x - (cfg.CITY_HEARTS * (icon_size + cfg.scale_value(2)))
    for i in range(cfg.CITY_HEARTS):
        icon_to_draw = heart_icon_full if i < full_hearts else heart_icon_empty
        if icon_to_draw:
            screen.blit(icon_to_draw, (city_hp_start_x + i * (icon_size + cfg.scale_value(2)), 
                                     padding_y_center - icon_to_draw.get_height() // 2))
    city_label_text = util.render_text_surface("Ville:", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
    screen.blit(city_label_text, (city_hp_start_x - city_label_text.get_width() - cfg.scale_value(5), 
                                  padding_y_center - city_label_text.get_height() // 2))


    # Vague (au centre ou à côté des HP)
    wave_text_str = ""
    if game_state.wave_in_progress:
        wave_text_str = f"Vague {game_state.current_wave_number} en cours"
    else:
        if game_state.current_wave_number == 0 :
             wave_text_str = f"Préparation..."
        elif game_state.current_wave_number >= game_state.max_waves and game_state.max_waves > 0 : # si max_waves est 0, mode infini?
             wave_text_str = "Toutes vagues terminées!"
        else:
             wave_text_str = f"Prochaine vague dans {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    
    wave_text_surf = util.render_text_surface(wave_text_str, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
    wave_text_x = city_hp_start_x - city_label_text.get_width() - cfg.scale_value(5) - wave_text_surf.get_width() - padding_x
    # Ou centrer le texte de vague:
    # wave_text_x = (cfg.SCREEN_WIDTH - wave_text_surf.get_width()) // 2
    screen.blit(wave_text_surf, (wave_text_x, padding_y_center - wave_text_surf.get_height() // 2))


def draw_base_grid(screen, game_state):
    """Dessine la grille de construction."""
    # Le game_state.buildable_area_rect_pixels est déjà calculé avec le bon offset Y
    grid_origin_x = game_state.buildable_area_rect_pixels.x
    grid_origin_y = game_state.buildable_area_rect_pixels.y

    for r in range(game_state.grid_height_tiles):
        for c in range(game_state.grid_width_tiles):
            tile_rect = pygame.Rect(
                grid_origin_x + c * cfg.TILE_SIZE,
                grid_origin_y + r * cfg.TILE_SIZE,
                cfg.TILE_SIZE, cfg.TILE_SIZE
            )
            
            # TODO: Déterminer si la case est une "fondation renforcée" pour une couleur différente
            # (Ex: si r est la dernière ligne de la grille initiale)
            # La "dernière ligne" change si on étend vers le haut, donc il faut une logique.
            # Supposons que la "reinforced_foundation_row_index" est stockée dans game_state
            # ou calculée : cfg.INITIAL_GRID_HEIGHT_TILES - 1 + game_state.current_expansion_up_tiles
            # (si 0 est en haut et qu'on ajoute des rangées en haut).
            # Si 0 est en haut et qu'on ajoute des rangées EN BAS de la structure de données pour l'expansion "vers le haut":
            initial_bottom_row_logical_idx = cfg.INITIAL_GRID_HEIGHT_TILES - 1
            is_reinforced_spot = (r == initial_bottom_row_logical_idx and c < cfg.INITIAL_GRID_WIDTH_TILES)
            
            tile_color = cfg.COLOR_GRID_REINFORCED if is_reinforced_spot else cfg.COLOR_GRID_DEFAULT
            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, cfg.COLOR_GRID_BORDER, tile_rect, 1)


build_menu_layout = [] # Sera rempli avec les infos des boutons (rect, id, tooltip, icon_surf)

def initialize_build_menu_layout(game_state):
    """Prépare la disposition des boutons du menu de construction."""
    global build_menu_layout
    build_menu_layout = [] # Vider pour recalcul si la résolution change en cours de jeu (peu probable ici)

    # TODO: Définir les items du menu. Charger les sprites d'icônes ici.
    # SPRITE: Assurez-vous d'avoir les icônes pour chaque item.
    menu_item_definitions = [
        {"id": "foundation", "tooltip": "Fondation", "icon_name": "icon_foundation.png"},
        {"id": "generator", "tooltip": "Générateur", "icon_name": "icon_generator.png"},
        {"id": "miner", "tooltip": "Mine de Fer", "icon_name": "icon_miner.png"},
        {"id": "storage", "tooltip": "Stockage Fer", "icon_name": "icon_storage.png"},
        {"id": "gatling_turret", "tooltip": "Tourelle Gatling", "icon_name": "icon_turret_gatling.png"},
        {"id": "mortar_turret", "tooltip": "Tourelle Mortier", "icon_name": "icon_turret_mortar.png"},
        {"id": "expand_up", "tooltip": "Étendre Haut", "icon_name": "icon_expand_up.png"},
        {"id": "expand_side", "tooltip": "Étendre Côté", "icon_name": "icon_expand_side.png"},
    ]

    button_size_w, button_size_h = cfg.UI_BUILD_MENU_BUTTON_SIZE
    start_x = cfg.scale_value(10)
    menu_rect_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT
    button_y = menu_rect_y + (cfg.UI_BUILD_MENU_HEIGHT - button_size_h) // 2

    for item_def in menu_item_definitions:
        icon_path = cfg.UI_SPRITE_PATH + item_def["icon_name"] # Ou cfg.BUILDING_SPRITE_PATH etc.
        icon_surf_orig = util.load_sprite(icon_path)
        icon_surf_scaled = util.scale_sprite_to_size(icon_surf_orig, button_size_w - cfg.scale_value(10), button_size_h - cfg.scale_value(10)) # Laisse un peu de marge

        btn_rect = pygame.Rect(start_x, button_y, button_size_w, button_size_h)
        build_menu_layout.append({
            "id": item_def["id"],
            "rect": btn_rect,
            "tooltip": item_def["tooltip"],
            "icon": icon_surf_scaled
        })
        start_x += button_size_w + BUILD_MENU_BUTTON_PADDING

# Appeler initialize_build_menu_layout une fois que pygame est initialisé (ex: dans GameState.init_new_game)


def draw_build_menu_ui(screen, game_state):
    """Affiche le menu de construction en bas de l'écran."""
    if not build_menu_layout: # S'assurer que c'est initialisé
        initialize_build_menu_layout(game_state)

    menu_rect = pygame.Rect(0, cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT, cfg.SCREEN_WIDTH, cfg.UI_BUILD_MENU_HEIGHT)
    pygame.draw.rect(screen, cfg.COLOR_BUILD_MENU_BG, menu_rect)
    pygame.draw.line(screen, cfg.COLOR_GRID_BORDER, menu_rect.topleft, menu_rect.topright, 2) # Ligne de séparation

    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_tooltip = None

    for button_info in build_menu_layout:
        btn_rect = button_info["rect"]
        is_selected = (game_state.selected_item_to_place_type == button_info["id"])
        border_color = cfg.COLOR_BUTTON_SELECTED_BORDER if is_selected else cfg.COLOR_BUTTON_BORDER
        
        pygame.draw.rect(screen, cfg.COLOR_BUTTON_BG, btn_rect) # Fond du bouton
        if button_info["icon"]:
            icon_x = btn_rect.centerx - button_info["icon"].get_width() // 2
            icon_y = btn_rect.centery - button_info["icon"].get_height() // 2
            screen.blit(button_info["icon"], (icon_x, icon_y))
        pygame.draw.rect(screen, border_color, btn_rect, 2) # Bordure

        if btn_rect.collidepoint(mouse_x, mouse_y):
            hovered_tooltip = button_info["tooltip"]
            # Afficher le coût si disponible
            if not button_info["id"].startswith("expand_"):
                item_stats = objects.get_item_stats(button_info["id"])
                cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
                cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
                hovered_tooltip += f" ($:{cost_money} Fe:{cost_iron})"
            else: # Pour les expansions, le coût est dynamique
                cost = 0
                if button_info["id"] == "expand_up": cost = game_state.calculate_expansion_cost("up")
                elif button_info["id"] == "expand_side": cost = game_state.calculate_expansion_cost("side")
                hovered_tooltip += f" ($:{cost})"


    # Afficher le tooltip
    if hovered_tooltip:
        tooltip_surf = util.render_text_surface(hovered_tooltip, cfg.FONT_SIZE_SMALL, TOOLTIP_TEXT_COLOR)
        tooltip_rect = tooltip_surf.get_rect(midbottom=(mouse_x, mouse_y + TOOLTIP_OFFSET_Y))
        
        # S'assurer que le tooltip reste à l'écran
        tooltip_rect.clamp_ip(screen.get_rect())

        # Fond pour le tooltip
        bg_rect = tooltip_rect.inflate(cfg.scale_value(10), cfg.scale_value(6))
        # Créer une surface pour le fond avec alpha
        tooltip_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        tooltip_bg_surf.fill(TOOLTIP_BG_COLOR)
        screen.blit(tooltip_bg_surf, bg_rect.topleft)
        screen.blit(tooltip_surf, tooltip_rect.topleft)


def check_build_menu_click(game_state, mouse_pixel_pos):
    """Vérifie si un clic a eu lieu sur un bouton du menu de construction. Retourne l'ID de l'item ou None."""
    if not build_menu_layout: return None

    menu_ui_rect = pygame.Rect(0, cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT, cfg.SCREEN_WIDTH, cfg.UI_BUILD_MENU_HEIGHT)
    if not menu_ui_rect.collidepoint(mouse_pixel_pos):
        return None # Clic en dehors du menu

    for button_info in build_menu_layout:
        if button_info["rect"].collidepoint(mouse_pixel_pos):
            print(f"UI Clicked: {button_info['id']}")
            return button_info["id"]
    return None


def draw_placement_preview(screen, game_state):
    """Affiche un 'fantôme' de l'item sélectionné à la position de la souris sur la grille."""
    if game_state.selected_item_to_place_type and game_state.placement_preview_sprite:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convertir la position de la souris en coin supérieur gauche de la case de la grille
        grid_r, grid_c = util.convert_pixels_to_grid(
            (mouse_x, mouse_y), 
            (cfg.GRID_OFFSET_X, game_state.buildable_area_rect_pixels.y) # Utiliser l'offset Y actuel de la grille
        )

        if 0 <= grid_r < game_state.grid_height_tiles and 0 <= grid_c < game_state.grid_width_tiles:
            preview_x, preview_y = util.convert_grid_to_pixels(
                (grid_r, grid_c), 
                (cfg.GRID_OFFSET_X, game_state.buildable_area_rect_pixels.y)
            )
            
            # Teinter le sprite en fonction de la validité du placement
            temp_sprite = game_state.placement_preview_sprite.copy()
            if game_state.is_placement_valid_preview:
                temp_sprite.fill((0, 255, 0, 100), special_flags=pygame.BLEND_RGBA_MULT) # Vert si valide
            else:
                temp_sprite.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT) # Rouge si invalide
            
            screen.blit(temp_sprite, (preview_x, preview_y))


def draw_error_message(screen, message):
    """Affiche un message d'erreur/d'information temporaire."""
    if not message: return
    error_surf = util.render_text_surface(message, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_RED, background_color=(50,50,50, 200))
    pos_x = (cfg.SCREEN_WIDTH - error_surf.get_width()) // 2
    pos_y = cfg.UI_TOP_BAR_HEIGHT + cfg.scale_value(20) # Sous la barre du haut
    screen.blit(error_surf, (pos_x, pos_y))


def draw_pause_screen(screen):
    """Affiche l'écran de pause."""
    overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Noir semi-transparent
    screen.blit(overlay, (0, 0))

    pause_text_surf = util.render_text_surface("PAUSE", cfg.FONT_SIZE_LARGE, cfg.COLOR_WHITE)
    text_rect = pause_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 3))
    screen.blit(pause_text_surf, text_rect)

    # TODO: Ajouter des boutons "Reprendre", "Options", "Quitter au Menu"
    # et la logique dans check_pause_menu_click


def check_pause_menu_click(event, mouse_pos):
    """Vérifie les clics sur les boutons du menu pause. Retourne une action (string) ou None."""
    # TODO: Définir les rects des boutons du menu pause et vérifier les collisions.
    # Exemple:
    # resume_button_rect = pygame.Rect(...)
    # if event.type == pygame.MOUSEBUTTONDOWN and resume_button_rect.collidepoint(mouse_pos):
    #     return "resume"
    # if quit_button_rect.collidepoint(mouse_pos): return "quit_to_menu"
    return None


def draw_game_over_screen(screen, final_score):
    """Affiche l'écran de Game Over."""
    overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220)) # Plus opaque
    screen.blit(overlay, (0, 0))

    go_text_surf = util.render_text_surface("GAME OVER", cfg.FONT_SIZE_LARGE, cfg.COLOR_RED)
    score_text_surf = util.render_text_surface(f"Score Final: {final_score}", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_WHITE)

    go_rect = go_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - cfg.scale_value(30)))
    score_rect = score_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + cfg.scale_value(20)))

    screen.blit(go_text_surf, go_rect)
    screen.blit(score_text_surf, score_rect)
    
    # TODO: Ajouter boutons "Rejouer", "Menu Principal"


def check_game_over_menu_click(event, mouse_pos):
    """Vérifie les clics sur les boutons de l'écran Game Over."""
    # TODO: Définir les rects des boutons et vérifier les collisions.
    # Exemple:
    # retry_button_rect = pygame.Rect(...)
    # if event.type == pygame.MOUSEBUTTONDOWN and retry_button_rect.collidepoint(mouse_pos):
    #     return "retry"
    return None

def draw_tutorial_message(screen, message):
    """Affiche un message spécifique au tutoriel."""
    if not message: return
    # Positionner en bas au centre, au-dessus du menu de construction
    msg_surf = util.render_text_surface(message, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_WHITE, background_color=(20,20,80, 200))
    pos_x = (cfg.SCREEN_WIDTH - msg_surf.get_width()) // 2
    pos_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - msg_surf.get_height() - cfg.scale_value(10)
    screen.blit(msg_surf, (pos_x, pos_y))

# --- Fonctions pour le Menu Principal (si non dans main.py) ---
main_menu_buttons = []

def initialize_main_menu_layout():
    global main_menu_buttons
    main_menu_buttons = []
    button_texts = ["Jouer", "Tutoriel", "Lore (Optionnel)", "Quitter"]
    button_actions = [cfg.STATE_GAMEPLAY, cfg.STATE_TUTORIAL, cfg.STATE_LORE, cfg.STATE_QUIT]
    
    btn_width = cfg.scale_value(200)
    btn_height = cfg.scale_value(50)
    start_y = cfg.SCREEN_HEIGHT // 2 - (len(button_texts) * (btn_height + cfg.scale_value(15))) // 2
    
    for i, text in enumerate(button_texts):
        rect = pygame.Rect((cfg.SCREEN_WIDTH - btn_width) // 2, 
                           start_y + i * (btn_height + cfg.scale_value(15)), 
                           btn_width, btn_height)
        main_menu_buttons.append({"text": text, "rect": rect, "action": button_actions[i]})

def draw_main_menu(screen):
    if not main_menu_buttons: initialize_main_menu_layout()
    screen.fill((20, 30, 50)) # Fond du menu

    title_surf = util.render_text_surface("THE LAST STAND: 1941", cfg.FONT_SIZE_LARGE, cfg.COLOR_TEXT) # Utiliser le vrai titre
    title_rect = title_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.scale_value(150)))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()
    for btn in main_menu_buttons:
        color = cfg.COLOR_BUTTON_BORDER
        if btn["rect"].collidepoint(mouse_pos):
            color = cfg.COLOR_BUTTON_SELECTED_BORDER
        
        pygame.draw.rect(screen, cfg.COLOR_BUTTON_BG, btn["rect"])
        pygame.draw.rect(screen, color, btn["rect"], 3)
        
        text_surf = util.render_text_surface(btn["text"], cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
        text_r = text_surf.get_rect(center=btn["rect"].center)
        screen.blit(text_surf, text_r)

def check_main_menu_click(event, mouse_pos):
    if not main_menu_buttons: return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for btn in main_menu_buttons:
            if btn["rect"].collidepoint(mouse_pos):
                return btn["action"]
    return None

def draw_lore_screen(screen): # Placeholder
    screen.fill((10,10,10))
    lore_text = [
        "Année 1941. L'ennemi déferle du ciel.",
        "Votre mission: construire et défendre la dernière ligne.",
        "Protégez la ville à tout prix.",
        "Appuyez sur Espace ou clic pour continuer..."
    ]
    current_y = cfg.scale_value(100)
    for line in lore_text:
        surf = util.render_text_surface(line, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
        rect = surf.get_rect(center=(cfg.SCREEN_WIDTH//2, current_y))
        screen.blit(surf, rect)
        current_y += cfg.scale_value(40)
