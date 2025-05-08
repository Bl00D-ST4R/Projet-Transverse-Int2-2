# ui_functions.py
import pygame
import game_config as cfg
import utility_functions as util
import objects # Nécessaire pour objects.get_item_stats
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
        elif game_state.current_wave_number >= game_state.max_waves and game_state.max_waves > 0 :
             wave_text_str = "Toutes vagues terminées!"
        else:
             wave_text_str = f"Prochaine vague dans {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    
    wave_text_surf = util.render_text_surface(wave_text_str, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
    wave_text_x = city_hp_start_x - city_label_text.get_width() - cfg.scale_value(5) - wave_text_surf.get_width() - padding_x
    screen.blit(wave_text_surf, (wave_text_x, padding_y_center - wave_text_surf.get_height() // 2))


def draw_base_grid(screen, game_state):
    """Dessine la grille de construction."""
    grid_origin_x = game_state.buildable_area_rect_pixels.x
    grid_origin_y = game_state.buildable_area_rect_pixels.y

    for r in range(game_state.grid_height_tiles):
        for c in range(game_state.grid_width_tiles):
            tile_rect = pygame.Rect(
                grid_origin_x + c * cfg.TILE_SIZE,
                grid_origin_y + r * cfg.TILE_SIZE,
                cfg.TILE_SIZE, cfg.TILE_SIZE
            )
            
            initial_bottom_row_logical_idx = cfg.INITIAL_GRID_HEIGHT_TILES - 1 # Si la grille 0,0 est en haut à gauche
            # Et que l'expansion vers le "haut" signifie insérer des lignes au début de la structure de données
            # ET que grid_height_tiles a été mis à jour.
            # La rangée "renforcée" serait alors à `initial_bottom_row_logical_idx + game_state.num_expansions_up`
            # (Si l'index 0 est toujours la rangée la plus haute affichée)
            # Ou plus simplement, si la grille est toujours rendue de 0 à N,
            # la ligne renforcée est celle qui correspondait à la dernière ligne initiale.
            # Sa position logique (index de ligne) dans le game_grid dépend de comment game_grid est géré.
            # Assumons que 'r' ici est l'index de la rangée DANS LA GRILLE ACTUELLE.
            # On a besoin de savoir quelle est la rangée "logique" correspondant à la dernière rangée
            # de la zone de construction d'origine.
            # Par exemple, si on a étendu 2 fois vers le haut, et que la rangée renforcée est la 3ème (index 2)
            # à partir du "bas" de la structure originale.
            # C'est plus simple si on a un `game_state.reinforced_row_index_visual` qui est mis à jour.
            # Pour cet exemple, on garde la logique précédente, qui est correcte si 0,0 est toujours le coin sup gauche
            # de la zone construisible initiale et qu'on ajoute des rangées en "haut" de la structure de données
            # de la grille, ce qui décale les index.
            # Ou si `game_state.buildable_area_rect_pixels.y` change, et `r` est relatif à ce nouveau `y`.

            # Simplifions : la rangée renforcée est la dernière rangée de la zone de construction initiale.
            # Sa position visuelle dépendra de l'expansion vers le haut.
            # Si `game_state.buildable_area_rect_pixels.y` est l'origine de la grille affichée
            # et que la rangée renforcée est toujours à `cfg.INITIAL_GRID_HEIGHT_TILES - 1` par rapport
            # au "bas" logique de la zone initiale.
            # Pour la coloration, on veut savoir si la tuile (r,c) est une "ancienne" fondation.
            # C'est plus complexe qu'il n'y paraît sans savoir exactement comment l'expansion est gérée.
            # Gardons la version la plus simple pour l'instant:
            
            # is_reinforced_spot = (r == (cfg.INITIAL_GRID_HEIGHT_TILES - 1) + game_state.expansions_up_count) 
            # (si 'r' est indexé depuis le haut de la grille actuellement visible, et que 0 est la première ligne)
            # La logique initiale était:
            # initial_bottom_row_logical_idx = cfg.INITIAL_GRID_HEIGHT_TILES - 1
            # is_reinforced_spot = (r == initial_bottom_row_logical_idx and c < cfg.INITIAL_GRID_WIDTH_TILES)
            # Cela ne fonctionne que si la grille ne s'étend pas vers le haut.
            # Solution plus robuste: stocker les coordonnées des tuiles renforcées, ou une ligne d'index.
            # Ou, si game_state a `reinforced_foundation_row_index_in_current_grid`:
            is_reinforced_spot = (hasattr(game_state, 'reinforced_foundation_row_index_in_current_grid') and \
                                 r == game_state.reinforced_foundation_row_index_in_current_grid and \
                                 c < cfg.INITIAL_GRID_WIDTH_TILES) # Limiter aux colonnes initiales aussi

            tile_color = cfg.COLOR_GRID_REINFORCED if is_reinforced_spot else cfg.COLOR_GRID_DEFAULT
            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, cfg.COLOR_GRID_BORDER, tile_rect, 1)


build_menu_layout = []

def initialize_build_menu_layout(game_state):
    global build_menu_layout
    build_menu_layout = []

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
        icon_path = cfg.UI_SPRITE_PATH + item_def["icon_name"]
        icon_surf_orig = util.load_sprite(icon_path)
        # S'assurer que l'icône n'est pas None avant de la scaler
        if icon_surf_orig:
            icon_surf_scaled = util.scale_sprite_to_size(icon_surf_orig, button_size_w - cfg.scale_value(10), button_size_h - cfg.scale_value(10))
        else: # Fallback si l'icône n'est pas chargée
            icon_surf_scaled = pygame.Surface((button_size_w - cfg.scale_value(10), button_size_h - cfg.scale_value(10)))
            icon_surf_scaled.fill(cfg.COLOR_GREY) # Couleur de placeholder

        btn_rect = pygame.Rect(start_x, button_y, button_size_w, button_size_h)
        build_menu_layout.append({
            "id": item_def["id"],
            "rect": btn_rect,
            "tooltip": item_def["tooltip"],
            "icon": icon_surf_scaled
        })
        start_x += button_size_w + BUILD_MENU_BUTTON_PADDING


def draw_build_menu_ui(screen, game_state):
    if not build_menu_layout:
        initialize_build_menu_layout(game_state)

    menu_rect = pygame.Rect(0, cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT, cfg.SCREEN_WIDTH, cfg.UI_BUILD_MENU_HEIGHT)
    pygame.draw.rect(screen, cfg.COLOR_BUILD_MENU_BG, menu_rect)
    pygame.draw.line(screen, cfg.COLOR_GRID_BORDER, menu_rect.topleft, menu_rect.topright, 2)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_tooltip_text = None # Renommé pour clarté

    for button_info in build_menu_layout:
        btn_rect = button_info["rect"]
        is_selected = (game_state.selected_item_to_place_type == button_info["id"])
        border_color = cfg.COLOR_BUTTON_SELECTED_BORDER if is_selected else cfg.COLOR_BUTTON_BORDER
        
        pygame.draw.rect(screen, cfg.COLOR_BUTTON_BG, btn_rect)
        if button_info["icon"]:
            icon_x = btn_rect.centerx - button_info["icon"].get_width() // 2
            icon_y = btn_rect.centery - button_info["icon"].get_height() // 2
            screen.blit(button_info["icon"], (icon_x, icon_y))
        pygame.draw.rect(screen, border_color, btn_rect, 2)

        if btn_rect.collidepoint(mouse_x, mouse_y):
            current_tooltip_base = button_info["tooltip"]
            if not button_info["id"].startswith("expand_"):
                # Utilisation de objects.get_item_stats
                item_stats = objects.get_item_stats(button_info["id"])
                cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
                cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
                current_tooltip_base += f" ($:{cost_money} Fe:{cost_iron})"
            else:
                cost = 0
                # CORRIGÉ: appeler la fonction de game_state pour obtenir le coût d'expansion
                if button_info["id"] == "expand_up": 
                    cost = game_state.get_next_expansion_cost("up")
                elif button_info["id"] == "expand_side": 
                    cost = game_state.get_next_expansion_cost("side")
                current_tooltip_base += f" ($:{cost})"
            hovered_tooltip_text = current_tooltip_base


    if hovered_tooltip_text:
        tooltip_surf = util.render_text_surface(hovered_tooltip_text, cfg.FONT_SIZE_SMALL, TOOLTIP_TEXT_COLOR)
        tooltip_rect = tooltip_surf.get_rect(midbottom=(mouse_x, mouse_y + TOOLTIP_OFFSET_Y))
        tooltip_rect.clamp_ip(screen.get_rect())

        bg_rect = tooltip_rect.inflate(cfg.scale_value(10), cfg.scale_value(6))
        tooltip_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        tooltip_bg_surf.fill(TOOLTIP_BG_COLOR)
        screen.blit(tooltip_bg_surf, bg_rect.topleft)
        screen.blit(tooltip_surf, tooltip_rect.topleft)


def check_build_menu_click(game_state, mouse_pixel_pos):
    if not build_menu_layout: return None

    menu_ui_rect = pygame.Rect(0, cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT, cfg.SCREEN_WIDTH, cfg.UI_BUILD_MENU_HEIGHT)
    if not menu_ui_rect.collidepoint(mouse_pixel_pos):
        return None

    for button_info in build_menu_layout:
        if button_info["rect"].collidepoint(mouse_pixel_pos):
            print(f"UI Clicked: {button_info['id']}")
            return button_info["id"]
    return None


def draw_placement_preview(screen, game_state):
    if game_state.selected_item_to_place_type and game_state.placement_preview_sprite:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        grid_r, grid_c = util.convert_pixels_to_grid(
            (mouse_x, mouse_y), 
            (game_state.buildable_area_rect_pixels.x, game_state.buildable_area_rect_pixels.y) # Utiliser l'offset X et Y actuel
        )

        if 0 <= grid_r < game_state.grid_height_tiles and 0 <= grid_c < game_state.grid_width_tiles:
            preview_x, preview_y = util.convert_grid_to_pixels(
                (grid_r, grid_c), 
                (game_state.buildable_area_rect_pixels.x, game_state.buildable_area_rect_pixels.y)
            )
            
            temp_sprite = game_state.placement_preview_sprite.copy()
            if game_state.is_placement_valid_preview:
                temp_sprite.fill((0, 255, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                temp_sprite.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            
            screen.blit(temp_sprite, (preview_x, preview_y))


def draw_error_message(screen, message):
    if not message: return
    error_surf = util.render_text_surface(message, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_RED, background_color=(50,50,50, 200))
    pos_x = (cfg.SCREEN_WIDTH - error_surf.get_width()) // 2
    pos_y = cfg.UI_TOP_BAR_HEIGHT + cfg.scale_value(20)
    screen.blit(error_surf, (pos_x, pos_y))


def draw_pause_screen(screen):
    overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    pause_text_surf = util.render_text_surface("PAUSE", cfg.FONT_SIZE_LARGE, cfg.COLOR_WHITE)
    text_rect = pause_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 3))
    screen.blit(pause_text_surf, text_rect)


def check_pause_menu_click(event, mouse_pos):
    # TODO: Implémenter la logique des boutons
    return None


def draw_game_over_screen(screen, final_score):
    overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    go_text_surf = util.render_text_surface("GAME OVER", cfg.FONT_SIZE_LARGE, cfg.COLOR_RED)
    score_text_surf = util.render_text_surface(f"Score Final: {final_score}", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_WHITE)

    go_rect = go_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - cfg.scale_value(30)))
    score_rect = score_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + cfg.scale_value(20)))

    screen.blit(go_text_surf, go_rect)
    screen.blit(score_text_surf, score_rect)


def check_game_over_menu_click(event, mouse_pos):
    # TODO: Implémenter la logique des boutons
    return None

def draw_tutorial_message(screen, message):
    if not message: return
    msg_surf = util.render_text_surface(message, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_WHITE, background_color=(20,20,80, 200))
    pos_x = (cfg.SCREEN_WIDTH - msg_surf.get_width()) // 2
    pos_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - msg_surf.get_height() - cfg.scale_value(10)
    screen.blit(msg_surf, (pos_x, pos_y))

main_menu_buttons = []

def initialize_main_menu_layout():
    global main_menu_buttons
    main_menu_buttons = []
    button_texts = ["Jouer", "Tutoriel", "Lore (Optionnel)", "Quitter"] # "Options" ?
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
    screen.fill(cfg.COLOR_MENU_BACKGROUND) # Utiliser une couleur de cfg si définie

    title_surf = util.render_text_surface("THE LAST STAND: 1941", cfg.FONT_SIZE_TITLE, cfg.COLOR_TITLE_TEXT)
    title_rect = title_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.scale_value(150)))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()
    for btn in main_menu_buttons:
        color = cfg.COLOR_BUTTON_BORDER
        bg_color = cfg.COLOR_BUTTON_BG
        if btn["rect"].collidepoint(mouse_pos):
            color = cfg.COLOR_BUTTON_SELECTED_BORDER
            bg_color = cfg.COLOR_BUTTON_HOVER_BG # Couleur de survol
        
        pygame.draw.rect(screen, bg_color, btn["rect"])
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

def draw_lore_screen(screen):
    screen.fill(cfg.COLOR_MENU_BACKGROUND)
    lore_text = [
        "Année 1941. L'ennemi déferle du ciel.",
        "Votre mission: construire et défendre la dernière ligne.",
        "Protégez la ville à tout prix.",
        "",
        "Appuyez sur Espace ou Clic pour continuer..."
    ]
    current_y = cfg.SCREEN_HEIGHT // 2 - (len(lore_text) * cfg.scale_value(35)) // 2
    for line in lore_text:
        surf = util.render_text_surface(line, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
        rect = surf.get_rect(center=(cfg.SCREEN_WIDTH//2, current_y))
        screen.blit(surf, rect)
        current_y += cfg.scale_value(35)
