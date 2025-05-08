# ui_functions.py
import pygame
import game_config as cfg
import utility_functions as util
import objects # Import nécessaire pour get_item_stats si utilisé ailleurs

# --- Constantes spécifiques à l'UI (si non déjà dans cfg) ---
BUILD_MENU_BUTTON_PADDING = cfg.scale_value(5) # Espace entre les boutons du menu de construction
TOOLTIP_BG_COLOR = (30, 30, 30, 220) # Fond semi-transparent pour les tooltips
TOOLTIP_TEXT_COLOR = cfg.COLOR_WHITE
TOOLTIP_OFFSET_Y = cfg.scale_value(-30) # Décalage Y pour afficher le tooltip au-dessus du bouton


# --- Menu Principal ---

# Liste définissant les options du menu principal
main_menu_options = [
    {"text": "Jouer",           "action": cfg.STATE_GAMEPLAY, "key": pygame.K_1},
    {"text": "Tutoriel",        "action": cfg.STATE_TUTORIAL, "key": pygame.K_2},
    # {"text": "Lore",            "action": cfg.STATE_LORE,     "key": pygame.K_3}, # Décommenter si Lore est actif
    {"text": "Quitter",         "action": cfg.STATE_QUIT,     "key": pygame.K_3}, # Ajuster la clé si Lore est actif (K_4)
]

main_menu_rendered_rects = {} # Dictionnaire {action: rect}

def initialize_main_menu_layout():
    global main_menu_rendered_rects
    main_menu_rendered_rects = {}
    print("Layout menu principal initialisé (texte seulement).")

def draw_main_menu(screen):
    global main_menu_rendered_rects
    main_menu_rendered_rects = {} 

    screen.fill(cfg.COLOR_WHITE) 

    title_surf = util.render_text_surface(cfg.GAME_TITLE, cfg.FONT_SIZE_XLARGE, cfg.COLOR_BLACK)
    title_rect = title_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.scale_value(150)))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()
    num_options = len(main_menu_options)
    button_height_approx = cfg.scale_value(50) 
    total_menu_height = num_options * button_height_approx + (num_options - 1) * cfg.scale_value(15)
    start_y = (cfg.SCREEN_HEIGHT - total_menu_height) // 2 
    current_y_center = start_y + button_height_approx // 2

    for index, option in enumerate(main_menu_options):
        key_char = pygame.key.name(option["key"])
        if key_char.isdigit(): 
             display_key_char = key_char
        elif key_char.startswith("[") and key_char.endswith("]") and len(key_char) == 3 and key_char[1].isdigit(): 
             display_key_char = key_char[1]
        else: 
            display_key_char = key_char.upper()

        option_text = f"({display_key_char}) {option['text']}"
        text_surf = util.render_text_surface(option_text, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_BLACK)
        text_rect = text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, current_y_center))

        is_hovered = text_rect.collidepoint(mouse_pos)
        text_color = cfg.COLOR_BLUE if is_hovered else cfg.COLOR_BLACK

        if is_hovered:
             text_surf = util.render_text_surface(option_text, cfg.FONT_SIZE_MEDIUM, text_color)

        screen.blit(text_surf, text_rect.topleft)
        main_menu_rendered_rects[option["action"]] = text_rect 
        current_y_center += button_height_approx + cfg.scale_value(15) 

def check_main_menu_click(event, mouse_pos):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for action, rect in main_menu_rendered_rects.items():
            if rect and rect.collidepoint(mouse_pos): 
                print(f"Menu action sélectionnée par clic: {action}")
                return action
                
    if event.type == pygame.KEYDOWN:
        for option in main_menu_options:
            if event.key == option["key"]:
                print(f"Menu action sélectionnée par clavier ({pygame.key.name(event.key)}): {option['action']}")
                return option["action"]
                
    return None

def draw_lore_screen(screen): 
    screen.fill(cfg.COLOR_WHITE) 
    lore_text = [
        "Année 1941. L'ennemi déferle du ciel.",
        "Votre mission: construire et défendre la dernière ligne.",
        "Protégez la ville à tout prix.",
        "",
        "Appuyez sur Espace ou clic pour continuer..."
    ]
    current_y = cfg.scale_value(150)
    text_color = cfg.COLOR_BLACK 

    for line in lore_text:
        surf = util.render_text_surface(line, cfg.FONT_SIZE_MEDIUM, text_color)
        rect = surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, current_y))
        screen.blit(surf, rect)
        current_y += cfg.scale_value(40)

# --- Fonctions d'Affichage Générales (en jeu) ---

# Modif 2 Appliquée Ici
def draw_top_bar_ui(screen, game_state):
    """Affiche la barre supérieure avec fond gris simple et texte."""
    top_bar_rect = pygame.Rect(0, 0, cfg.SCREEN_WIDTH, cfg.UI_TOP_BAR_HEIGHT)
    # MODIFIÉ: Utiliser une couleur grise définie dans cfg
    bg_color = getattr(cfg, 'COLOR_GREY_MEDIUM', (128, 128, 128)) # Fallback gris moyen
    pygame.draw.rect(screen, bg_color, top_bar_rect)
    # Optionnel: Ajouter une ligne de bordure en bas
    # border_color = getattr(cfg, 'COLOR_GREY_DARK', (50, 50, 50))
    # pygame.draw.line(screen, border_color, top_bar_rect.bottomleft, top_bar_rect.bottomright, 2)


    padding_x = cfg.scale_value(15)
    padding_y_center = cfg.UI_TOP_BAR_HEIGHT // 2
    # Utiliser une couleur de texte contrastante
    text_color_default = getattr(cfg, 'COLOR_UI_TEXT_ON_GREY', cfg.COLOR_BLACK) # Fallback noir

    current_x = padding_x

    # --- Affichage des Ressources (Texte seulement) ---
    # Argent
    money_text_surf = util.render_text_surface(f"$ {int(game_state.money)}", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_MONEY) # Couleur spécifique pour argent
    if money_text_surf:
        money_rect = money_text_surf.get_rect(midleft=(current_x, padding_y_center))
        screen.blit(money_text_surf, money_rect)
        current_x += money_rect.width + padding_x * 1.5

    # Fer
    iron_text_surf = util.render_text_surface(
        f"Fe: {int(game_state.iron_stock)}/{game_state.iron_storage_capacity} (+{game_state.iron_production_per_minute:.1f}/m)",
        cfg.FONT_SIZE_MEDIUM, cfg.COLOR_IRON # Couleur spécifique pour fer
    )
    if iron_text_surf:
        iron_rect = iron_text_surf.get_rect(midleft=(current_x, padding_y_center))
        screen.blit(iron_text_surf, iron_rect)
        current_x += iron_rect.width + padding_x * 1.5

    # Énergie
    available_energy = game_state.electricity_produced - game_state.electricity_consumed
    energy_color = cfg.COLOR_ENERGY_OK if available_energy >= 0 else cfg.COLOR_ENERGY_FAIL
    if -5 < available_energy < 0 : energy_color = cfg.COLOR_ENERGY_LOW
    energy_text_surf = util.render_text_surface(
        f"W: {available_energy} ({game_state.electricity_produced}P/{game_state.electricity_consumed}C)",
        cfg.FONT_SIZE_MEDIUM, energy_color # Couleur dynamique pour énergie
    )
    if energy_text_surf:
        energy_rect = energy_text_surf.get_rect(midleft=(current_x, padding_y_center))
        screen.blit(energy_text_surf, energy_rect)
        # current_x += energy_rect.width + padding_x * 1.5 # Pas besoin si dernier à gauche

    # --- Infos Droite (HP Ville, Vague) ---
    right_align_x = cfg.SCREEN_WIDTH - padding_x

    # Vague (à droite)
    wave_text_str = ""
    if game_state.wave_in_progress: wave_text_str = f"Vague {game_state.current_wave_number}"
    elif game_state.game_over_flag: wave_text_str = "Game Over"
    elif game_state.all_waves_completed: wave_text_str = "Vagues Finies!" # Ajouté pour état victoire/fin
    elif game_state.current_wave_number == 0 and game_state.time_to_next_wave_seconds > 0: wave_text_str = f"Début {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    elif game_state.time_to_next_wave_seconds > 0: wave_text_str = f"Suivante {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    else: wave_text_str = "Préparation..."


    wave_text_surf = util.render_text_surface(wave_text_str, cfg.FONT_SIZE_MEDIUM, text_color_default)
    if wave_text_surf:
        wave_rect = wave_text_surf.get_rect(midright=(right_align_x, padding_y_center))
        screen.blit(wave_text_surf, wave_rect)
        right_align_x = wave_rect.left - padding_x * 1.5 # Mettre à jour pour l'élément suivant

    # HP Ville (à gauche de Vague)
    hp_text_surf = util.render_text_surface(f"Ville HP: {game_state.city_hp}/{game_state.max_city_hp}", cfg.FONT_SIZE_MEDIUM, text_color_default)
    if hp_text_surf:
        hp_rect = hp_text_surf.get_rect(midright=(right_align_x, padding_y_center))
        screen.blit(hp_text_surf, hp_rect)

# Modif 3 Appliquée Ici
def draw_base_grid(screen, game_state):
    """Dessine la grille de construction."""
    if not hasattr(game_state, 'buildable_area_rect_pixels') or not game_state.buildable_area_rect_pixels:
        print("AVERTISSEMENT: game_state.buildable_area_rect_pixels non initialisé dans draw_base_grid.")
        return

    # CORRIGÉ: Utiliser explicitement les coordonnées du rect pour l'origine
    grid_origin_x = game_state.buildable_area_rect_pixels.left
    grid_origin_y = game_state.buildable_area_rect_pixels.top # Utiliser .top est identique à .y

    for r in range(game_state.grid_height_tiles):
        for c in range(game_state.grid_width_tiles):
            tile_rect = pygame.Rect(
                grid_origin_x + c * cfg.TILE_SIZE,
                grid_origin_y + r * cfg.TILE_SIZE, # Utilise le bon Y de départ
                cfg.TILE_SIZE, cfg.TILE_SIZE
            )

            # CORRIGÉ: Simplification de la logique reinforced spot basée sur la ligne initiale
            # La ligne la plus basse *initialement* est GRID_INITIAL_HEIGHT_TILES - 1
            is_reinforced_spot = False
            # On vérifie si l'index de ligne 'r' correspond à la dernière ligne initiale
            # ET que la colonne est dans les limites de la largeur initiale
            if hasattr(cfg, 'GRID_INITIAL_HEIGHT_TILES') and hasattr(cfg, 'GRID_INITIAL_WIDTH_TILES'):
                if r == (cfg.GRID_INITIAL_HEIGHT_TILES - 1) and c < cfg.GRID_INITIAL_WIDTH_TILES:
                     is_reinforced_spot = True
            
            # S'assurer que les couleurs sont définies dans cfg, sinon utiliser des fallbacks
            color_reinforced = getattr(cfg, 'COLOR_GRID_REINFORCED', (65, 75, 85))
            color_default = getattr(cfg, 'COLOR_GRID_DEFAULT', (45, 55, 65))
            color_border = getattr(cfg, 'COLOR_GRID_BORDER', (80, 90, 100))

            tile_color = color_reinforced if is_reinforced_spot else color_default
            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, color_border, tile_rect, 1)


build_menu_layout = [] 

# Modif 4 Appliquée Ici
def initialize_build_menu_layout(game_state):
    global build_menu_layout
    build_menu_layout = []

    # CORRIGÉ: Adapter les items disponibles dans le menu
    menu_item_definitions = [
        {"id": "frame",         "tooltip": "Structure",     "icon_name": "icon_frame.png"}, # SPRITE: Icône pour frame
        {"id": "generator",     "tooltip": "Générateur",    "icon_name": "icon_generator.png"},
        {"id": "storage",       "tooltip": "Stockage Fer",  "icon_name": "icon_storage.png"},
        {"id": "miner",         "tooltip": "Mine de Fer",   "icon_name": "icon_miner.png"}, # Peut être sélectionné, mais placement échouera si pas sur fondation/miner
        {"id": "gatling_turret","tooltip": "Tourelle Gatling","icon_name": "icon_turret_gatling.png"},
        {"id": "mortar_turret", "tooltip": "Tourelle Mortier","icon_name": "icon_turret_mortar.png"},
        {"id": "expand_up",     "tooltip": "Étendre Haut",  "icon_name": "icon_expand_up.png"},
        {"id": "expand_side",   "tooltip": "Étendre Côté",  "icon_name": "icon_expand_side.png"},
    ]

    button_size_w, button_size_h = cfg.UI_BUILD_MENU_BUTTON_SIZE
    start_x = cfg.scale_value(10)
    menu_rect_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT
    button_y = menu_rect_y + (cfg.UI_BUILD_MENU_HEIGHT - button_size_h) // 2

    for item_def in menu_item_definitions:
        icon_full_path = cfg.UI_SPRITE_PATH + item_def["icon_name"]
        icon_surf_orig = util.load_sprite(icon_full_path)
        
        icon_scaled_w = button_size_w - cfg.scale_value(10)
        icon_scaled_h = button_size_h - cfg.scale_value(10)
        icon_surf_scaled = util.scale_sprite_to_size(icon_surf_orig, icon_scaled_w, icon_scaled_h)

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
    hovered_tooltip_text = None 

    for button_info in build_menu_layout:
        btn_rect = button_info["rect"]
        is_selected = (hasattr(game_state, 'selected_item_to_place_type') and \
                       game_state.selected_item_to_place_type == button_info["id"])
        border_color = cfg.COLOR_BUTTON_SELECTED_BORDER if is_selected else cfg.COLOR_BUTTON_BORDER
        
        bg_color = cfg.COLOR_BUTTON_BG
        if btn_rect.collidepoint(mouse_x, mouse_y):
            bg_color = cfg.COLOR_BUTTON_HOVER_BG 

        pygame.draw.rect(screen, bg_color, btn_rect)
        if button_info["icon"]: 
            icon_x = btn_rect.centerx - button_info["icon"].get_width() // 2
            icon_y = btn_rect.centery - button_info["icon"].get_height() // 2
            screen.blit(button_info["icon"], (icon_x, icon_y))
        pygame.draw.rect(screen, border_color, btn_rect, 2)

        if btn_rect.collidepoint(mouse_x, mouse_y):
            current_tooltip_base = button_info["tooltip"]
            item_id_for_stats = button_info["id"]
            # Si l'ID est "frame", chercher les stats de "foundation" pour le coût
            if item_id_for_stats == "frame":
                item_id_for_stats = "foundation" # Assumer que 'foundation' contient le coût du 'frame'

            if not button_info["id"].startswith("expand_"):
                item_stats = objects.get_item_stats(item_id_for_stats) # Utiliser l'ID ajusté
                cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
                cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
                current_tooltip_base += f" ($:{cost_money} Fe:{cost_iron})"
            else:
                cost = 0
                if hasattr(game_state, 'get_next_expansion_cost'):
                    if button_info["id"] == "expand_up": 
                        cost = game_state.get_next_expansion_cost("up")
                    elif button_info["id"] == "expand_side": 
                        cost = game_state.get_next_expansion_cost("side")
                current_tooltip_base += f" ($:{cost})"
            hovered_tooltip_text = current_tooltip_base

    if hovered_tooltip_text:
        tooltip_surf = util.render_text_surface(hovered_tooltip_text, cfg.FONT_SIZE_SMALL, TOOLTIP_TEXT_COLOR)
        if tooltip_surf:
            tooltip_rect = tooltip_surf.get_rect(midbottom=(mouse_x, mouse_y + TOOLTIP_OFFSET_Y))
            screen_boundary = screen.get_rect()
            tooltip_rect.clamp_ip(screen_boundary)
            bg_rect = tooltip_rect.inflate(cfg.UI_TOOLTIP_PADDING_X * 2, cfg.UI_TOOLTIP_PADDING_Y * 2)
            bg_rect.clamp_ip(screen_boundary) 
            tooltip_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            tooltip_bg_surf.fill(cfg.COLOR_TOOLTIP_BG) 
            screen.blit(tooltip_bg_surf, bg_rect.topleft)
            screen.blit(tooltip_surf, tooltip_rect.topleft) 


def check_build_menu_click(game_state, mouse_pixel_pos):
    if not build_menu_layout: return None

    menu_ui_rect = pygame.Rect(0, cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT, cfg.SCREEN_WIDTH, cfg.UI_BUILD_MENU_HEIGHT)
    if not menu_ui_rect.collidepoint(mouse_pixel_pos):
        return None

    for button_info in build_menu_layout:
        if button_info["rect"].collidepoint(mouse_pixel_pos):
            return button_info["id"]
    return None


def draw_placement_preview(screen, game_state):
    if hasattr(game_state, 'selected_item_to_place_type') and game_state.selected_item_to_place_type and \
       hasattr(game_state, 'placement_preview_sprite') and game_state.placement_preview_sprite and \
       hasattr(game_state, 'buildable_area_rect_pixels'): 

        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_r, grid_c = util.convert_pixels_to_grid(
            (mouse_x, mouse_y), 
            (game_state.buildable_area_rect_pixels.x, game_state.buildable_area_rect_pixels.y)
        )

        if 0 <= grid_r < game_state.grid_height_tiles and 0 <= grid_c < game_state.grid_width_tiles:
            preview_x, preview_y = util.convert_grid_to_pixels(
                (grid_r, grid_c), 
                (game_state.buildable_area_rect_pixels.x, game_state.buildable_area_rect_pixels.y)
            )
            temp_sprite = game_state.placement_preview_sprite.copy()
            color_tint = cfg.COLOR_PLACEMENT_INVALID 
            if hasattr(game_state, 'is_placement_valid_preview') and game_state.is_placement_valid_preview:
                color_tint = cfg.COLOR_PLACEMENT_VALID 
            temp_sprite.fill(color_tint, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(temp_sprite, (preview_x, preview_y))


def draw_error_message(screen, message, game_state): 
    if not message or not hasattr(game_state, 'error_message_timer') or game_state.error_message_timer <= 0:
        return
    error_surf = util.render_text_surface(message, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_RED, background_color=(50,50,50, 200))
    if error_surf:
        pos_x = (cfg.SCREEN_WIDTH - error_surf.get_width()) // 2
        pos_y = cfg.UI_TOP_BAR_HEIGHT + cfg.UI_ERROR_MESSAGE_OFFSET_Y
        screen.blit(error_surf, (pos_x, pos_y))


pause_menu_buttons_layout = [] 

def initialize_pause_menu_layout():
    global pause_menu_buttons_layout
    pause_menu_buttons_layout = []
    options = [
        {"text": "Reprendre", "action": "resume"},
        {"text": "Recommencer", "action": "restart"},
        {"text": "Menu Principal", "action": "main_menu"},
        {"text": "Quitter le Jeu", "action": "quit_game"}
    ]
    btn_width = cfg.scale_value(220)
    btn_height = cfg.scale_value(50)
    spacing = cfg.scale_value(20)
    num_buttons = len(options)
    total_height = num_buttons * btn_height + (num_buttons - 1) * spacing
    start_y = (cfg.SCREEN_HEIGHT - total_height) / 2 + cfg.scale_value(50) 

    for i, opt in enumerate(options):
        rect = pygame.Rect((cfg.SCREEN_WIDTH - btn_width) / 2, start_y + i * (btn_height + spacing), btn_width, btn_height)
        pause_menu_buttons_layout.append({"text": opt["text"], "rect": rect, "action": opt["action"]})

def draw_pause_screen(screen):
    if not pause_menu_buttons_layout:
        initialize_pause_menu_layout()

    overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    pause_text_surf = util.render_text_surface("PAUSE", cfg.FONT_SIZE_XLARGE, cfg.COLOR_WHITE)
    if pause_text_surf:
        text_rect = pause_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 3))
        screen.blit(pause_text_surf, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    for btn in pause_menu_buttons_layout:
        bg_color = cfg.COLOR_BUTTON_BG
        border_color = cfg.COLOR_BUTTON_BORDER
        if btn["rect"].collidepoint(mouse_pos):
            bg_color = cfg.COLOR_BUTTON_HOVER_BG
            border_color = cfg.COLOR_BUTTON_SELECTED_BORDER
        
        pygame.draw.rect(screen, bg_color, btn["rect"])
        pygame.draw.rect(screen, border_color, btn["rect"], 3)
        
        btn_text_surf = util.render_text_surface(btn["text"], cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
        if btn_text_surf:
            btn_text_rect = btn_text_surf.get_rect(center=btn["rect"].center)
            screen.blit(btn_text_surf, btn_text_rect)

# Modif 1 Appliquée Ici
def check_pause_menu_click(event, mouse_pos):
    if not pause_menu_buttons_layout: return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for btn in pause_menu_buttons_layout:
            if btn["rect"].collidepoint(mouse_pos):
                # CORRIGÉ: Retourner les constantes d'état de cfg
                action_str = btn["action"]
                if action_str == "resume":
                    return "resume" # Garder string pour action immédiate
                elif action_str == "restart":
                     # TODO: Implémenter la logique de redémarrage (réinitialiser game_state)
                     print("Action 'Recommencer' cliquée - Logique à implémenter dans main.py ou game_state")
                     return "restart" # Retourner un identifiant pour que la boucle principale gère
                elif action_str == "main_menu":
                    return cfg.STATE_MENU # Retourner l'état du menu
                elif action_str == "quit_game":
                    return cfg.STATE_QUIT # Retourner l'état quitter
    return None


game_over_buttons_layout = []

def initialize_game_over_layout():
    global game_over_buttons_layout
    game_over_buttons_layout = []
    options = [
        {"text": "Recommencer", "action": "retry"},
        {"text": "Menu Principal", "action": "main_menu_from_go"}, 
        {"text": "Quitter le Jeu", "action": "quit_game_from_go"}
    ]
    btn_width = cfg.scale_value(250)
    btn_height = cfg.scale_value(50)
    spacing = cfg.scale_value(20)
    num_buttons = len(options)
    total_height = num_buttons * btn_height + (num_buttons - 1) * spacing
    start_y = (cfg.SCREEN_HEIGHT / 2) + cfg.scale_value(60) 

    for i, opt in enumerate(options):
        rect = pygame.Rect((cfg.SCREEN_WIDTH - btn_width) / 2, start_y + i * (btn_height + spacing), btn_width, btn_height)
        game_over_buttons_layout.append({"text": opt["text"], "rect": rect, "action": opt["action"]})

def draw_game_over_screen(screen, final_score):
    if not game_over_buttons_layout:
        initialize_game_over_layout()

    overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    go_text_surf = util.render_text_surface("GAME OVER", cfg.FONT_SIZE_XLARGE, cfg.COLOR_RED)
    score_text_surf = util.render_text_surface(f"Score Final: {final_score}", cfg.FONT_SIZE_LARGE, cfg.COLOR_WHITE)

    if go_text_surf:
        go_rect = go_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - cfg.scale_value(60)))
        screen.blit(go_text_surf, go_rect)
    if score_text_surf:
        score_rect = score_text_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + cfg.scale_value(0)))
        screen.blit(score_text_surf, score_rect)
    
    mouse_pos = pygame.mouse.get_pos()
    for btn in game_over_buttons_layout:
        bg_color = cfg.COLOR_BUTTON_BG
        border_color = cfg.COLOR_BUTTON_BORDER
        if btn["rect"].collidepoint(mouse_pos):
            bg_color = cfg.COLOR_BUTTON_HOVER_BG
            border_color = cfg.COLOR_BUTTON_SELECTED_BORDER
        
        pygame.draw.rect(screen, bg_color, btn["rect"])
        pygame.draw.rect(screen, border_color, btn["rect"], 3)
        
        btn_text_surf = util.render_text_surface(btn["text"], cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
        if btn_text_surf:
            btn_text_rect = btn_text_surf.get_rect(center=btn["rect"].center)
            screen.blit(btn_text_surf, btn_text_rect)


def check_game_over_menu_click(event, mouse_pos):
    if not game_over_buttons_layout: return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for btn in game_over_buttons_layout:
            if btn["rect"].collidepoint(mouse_pos):
                # Retourner l'action string pour être traitée dans la boucle principale
                action_str = btn["action"]
                if action_str == "retry":
                    return "retry"
                elif action_str == "main_menu_from_go":
                     return cfg.STATE_MENU # Retourner l'état menu
                elif action_str == "quit_game_from_go":
                     return cfg.STATE_QUIT # Retourner l'état quitter
    return None

def draw_tutorial_message(screen, message, game_state): 
    if not message or not hasattr(game_state, 'tutorial_message_timer') or game_state.tutorial_message_timer <=0:
        return
    msg_surf = util.render_text_surface(message, cfg.FONT_SIZE_MEDIUM, cfg.COLOR_WHITE, background_color=(20,20,80, 200))
    if msg_surf:
        pos_x = (cfg.SCREEN_WIDTH - msg_surf.get_width()) // 2
        pos_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - msg_surf.get_height() - cfg.UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y
        screen.blit(msg_surf, (pos_x, pos_y))
