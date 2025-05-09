# ui_functions.py
import pygame
import game_config as cfg
import utility_functions as util
import objects # Import nécessaire pour get_item_stats si utilisé ailleurs

# --- Constantes spécifiques à l'UI (si non déjà dans cfg) ---
# REMOVED: BUILD_MENU_BUTTON_PADDING = cfg.scale_value(5) -> Will use scaler.scale_value(cfg.BASE_UI_BUILD_MENU_BUTTON_PADDING)
TOOLTIP_BG_COLOR = (30, 30, 30, 220) # Fond semi-transparent pour les tooltips
TOOLTIP_TEXT_COLOR = cfg.COLOR_WHITE
# REMOVED: TOOLTIP_OFFSET_Y = cfg.scale_value(-30) -> Will use scaler.scale_value(cfg.BASE_UI_TOOLTIP_OFFSET_Y)


# --- Menu Principal ---

main_menu_options = [
    {"text": "Jouer",           "action": cfg.STATE_GAMEPLAY, "key": pygame.K_1},
    {"text": "Tutoriel",        "action": cfg.STATE_TUTORIAL, "key": pygame.K_2},
    # {"text": "Lore",            "action": cfg.STATE_LORE,     "key": pygame.K_3},
    {"text": "Quitter",         "action": cfg.STATE_QUIT,     "key": pygame.K_3},
]

main_menu_rendered_rects = {}

# MODIFIED: Accepter scaler
def initialize_main_menu_layout(scaler: util.Scaler):
    global main_menu_rendered_rects
    main_menu_rendered_rects = {} # Rects will be calculated in draw_main_menu
    print("Layout menu principal initialisé (sera calculé au dessin).")

# MODIFIED: Accepter scaler
def draw_main_menu(screen, scaler: util.Scaler):
    global main_menu_rendered_rects
    main_menu_rendered_rects = {}

    screen.fill(cfg.COLOR_MENU_BACKGROUND) # Using a menu-specific background color

    # MODIFIED: Use scaler for font size and positions
    title_surf = util.render_text_surface(cfg.GAME_TITLE, scaler.font_size_title, cfg.COLOR_TITLE_TEXT)
    title_rect = title_surf.get_rect(center=(scaler.actual_w // 2, scaler.scale_value(150)))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()
    num_options = len(main_menu_options)
    # MODIFIED: Use scaler for dimensions
    button_height_approx = scaler.scale_value(60)
    button_spacing = scaler.scale_value(20)
    total_menu_height = num_options * button_height_approx + (num_options - 1) * button_spacing
    start_y = (scaler.actual_h - total_menu_height) // 2 + scaler.scale_value(70) # Adjusted start_y
    current_y_center = start_y + button_height_approx // 2

    for index, option in enumerate(main_menu_options):
        key_char = pygame.key.name(option["key"])
        display_key_char = key_char[1] if key_char.startswith("[") and key_char.endswith("]") and len(key_char) == 3 and key_char[1].isdigit() else key_char.upper()

        option_text = f"({display_key_char}) {option['text']}"
        # MODIFIED: Use scaler for font size
        text_surf_orig = util.render_text_surface(option_text, scaler.font_size_large, cfg.COLOR_TEXT)
        text_rect = text_surf_orig.get_rect(center=(scaler.actual_w // 2, current_y_center))

        is_hovered = text_rect.collidepoint(mouse_pos)
        text_color = cfg.COLOR_BUTTON_HOVER_BORDER if is_hovered else cfg.COLOR_TEXT # Use a hover color

        if is_hovered:
             final_text_surf = util.render_text_surface(option_text, scaler.font_size_large, text_color)
        else:
             final_text_surf = text_surf_orig

        screen.blit(final_text_surf, text_rect.topleft)
        main_menu_rendered_rects[option["action"]] = text_rect
        current_y_center += button_height_approx + button_spacing

# MODIFIED: Accepter scaler (though primarily uses layout)
def check_main_menu_click(event, mouse_pos, scaler: util.Scaler):
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

# MODIFIED: Accepter scaler
def draw_lore_screen(screen, scaler: util.Scaler):
    screen.fill(cfg.COLOR_MENU_BACKGROUND)
    lore_text = [
        "Année 1941. L'ennemi déferle du ciel.",
        "Votre mission: construire et défendre la dernière ligne.",
        "Protégez la ville à tout prix.",
        "",
        "Appuyez sur Espace ou clic pour continuer..."
    ]
    # MODIFIED: Use scaler for positions and font size
    current_y = scaler.scale_value(150)
    text_color = cfg.COLOR_TEXT

    for line in lore_text:
        surf = util.render_text_surface(line, scaler.font_size_medium, text_color)
        rect = surf.get_rect(center=(scaler.actual_w // 2, current_y))
        screen.blit(surf, rect)
        current_y += scaler.scale_value(40)

# --- Fonctions d'Affichage Générales (en jeu) ---

# MODIFIED: Accepter scaler
def draw_top_bar_ui(screen, game_state, scaler: util.Scaler):
    if scaler.ui_top_bar_height <= 0:
        if cfg.DEBUG_MODE: print(f"DEBUG: Top bar not drawn, height <= 0: {scaler.ui_top_bar_height}")
        return

    top_bar_rect = pygame.Rect(0, 0, scaler.actual_w, scaler.ui_top_bar_height)
    bg_color = getattr(cfg, 'COLOR_GREY_MEDIUM', (128, 128, 128))
    if cfg.DEBUG_MODE: print(f"DEBUG: Drawing top bar. Rect: {top_bar_rect}, Color: {bg_color}, Scaler Actual W: {scaler.actual_w}, Scaler UI Top Bar H: {scaler.ui_top_bar_height}")
    pygame.draw.rect(screen, bg_color, top_bar_rect)

    # MODIFIED: Use scaler for padding and font size
    padding_x = scaler.scale_value(15) # Base padding
    padding_y_center = scaler.ui_top_bar_height // 2
    text_color_default = getattr(cfg, 'COLOR_UI_TEXT_ON_GREY', cfg.COLOR_BLACK)

    current_x = padding_x

    money_text_surf = util.render_text_surface(f"$ {int(game_state.money)}", scaler.font_size_medium, cfg.COLOR_MONEY)
    if money_text_surf:
        money_rect = money_text_surf.get_rect(midleft=(current_x, padding_y_center))
        screen.blit(money_text_surf, money_rect)
        current_x += money_rect.width + padding_x * 1.5

    iron_text_surf = util.render_text_surface(
        f"Fe: {int(game_state.iron_stock)}/{game_state.iron_storage_capacity} (+P<0.1f>)",
        scaler.font_size_medium, cfg.COLOR_IRON
    )
    if iron_text_surf:
        iron_rect = iron_text_surf.get_rect(midleft=(current_x, padding_y_center))
        screen.blit(iron_text_surf, iron_rect)
        current_x += iron_rect.width + padding_x * 1.5

    available_energy = game_state.electricity_produced - game_state.electricity_consumed
    energy_color = cfg.COLOR_ENERGY_OK if available_energy >= 0 else cfg.COLOR_ENERGY_FAIL
    if -5 < available_energy < 0 : energy_color = cfg.COLOR_ENERGY_LOW
    energy_text_surf = util.render_text_surface(
        f"W: {available_energy} ({game_state.electricity_produced}P/{game_state.electricity_consumed}C)",
        scaler.font_size_medium, energy_color
    )
    if energy_text_surf:
        energy_rect = energy_text_surf.get_rect(midleft=(current_x, padding_y_center))
        screen.blit(energy_text_surf, energy_rect)

    right_align_x = scaler.actual_w - padding_x # MODIFIED
    wave_text_str = "" # Logic for wave_text_str remains the same
    if game_state.wave_in_progress: wave_text_str = f"Vague {game_state.current_wave_number}"
    elif game_state.game_over_flag: wave_text_str = "Game Over"
    elif game_state.all_waves_completed: wave_text_str = "Vagues Finies!"
    elif game_state.current_wave_number == 0 and game_state.time_to_next_wave_seconds > 0: wave_text_str = f"Début {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    elif game_state.time_to_next_wave_seconds > 0: wave_text_str = f"Suivante {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    else: wave_text_str = "Préparation..."

    wave_text_surf = util.render_text_surface(wave_text_str, scaler.font_size_medium, text_color_default) # MODIFIED
    if wave_text_surf:
        wave_rect = wave_text_surf.get_rect(midright=(right_align_x, padding_y_center))
        screen.blit(wave_text_surf, wave_rect)
        right_align_x = wave_rect.left - padding_x * 1.5

    hp_text_surf = util.render_text_surface(f"Ville HP: {game_state.city_hp}/{game_state.max_city_hp}", scaler.font_size_medium, text_color_default) # MODIFIED
    if hp_text_surf:
        hp_rect = hp_text_surf.get_rect(midright=(right_align_x, padding_y_center))
        screen.blit(hp_text_surf, hp_rect)

# MODIFIED: Accepter scaler
def draw_base_grid(screen, game_state, scaler: util.Scaler):
    if not hasattr(game_state, 'buildable_area_rect_pixels') or not game_state.buildable_area_rect_pixels:
        return

    grid_origin_x = game_state.buildable_area_rect_pixels.left
    grid_origin_y = game_state.buildable_area_rect_pixels.top
    tile_size = scaler.get_tile_size() # MODIFIED

    for r in range(game_state.grid_height_tiles):
        for c in range(game_state.grid_width_tiles):
            # MODIFIED: Use scaled tile_size
            tile_rect = pygame.Rect(
                grid_origin_x + c * tile_size,
                grid_origin_y + r * tile_size,
                tile_size, tile_size
            )
            # Logic for is_reinforced_spot uses BASE counts, which is fine
            is_reinforced_spot = False
            if hasattr(cfg, 'BASE_GRID_INITIAL_HEIGHT_TILES') and hasattr(cfg, 'BASE_GRID_INITIAL_WIDTH_TILES'):
                 # Reinforced row is determined by expansion logic in GameState using current_expansion_up_tiles
                 # and BASE_GRID_INITIAL_HEIGHT_TILES.
                 # Here we use get_reinforced_row_index from GameState if available, or replicate its logic.
                 reinforced_row_idx = game_state.current_expansion_up_tiles + (cfg.BASE_GRID_INITIAL_HEIGHT_TILES -1)
                 if r == reinforced_row_idx and c < game_state.grid_initial_width_tiles: # Check against initial width for "original" reinforced part
                      is_reinforced_spot = True


            color_reinforced = getattr(cfg, 'COLOR_GRID_REINFORCED', (65, 75, 85))
            color_default = getattr(cfg, 'COLOR_GRID_DEFAULT', (45, 55, 65))
            color_border = getattr(cfg, 'COLOR_GRID_BORDER', (80, 90, 100))

            tile_color = color_reinforced if is_reinforced_spot else color_default
            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, color_border, tile_rect, 1)


build_menu_layout = []

# MODIFIED: Accepter scaler
def initialize_build_menu_layout(game_state, scaler: util.Scaler):
    global build_menu_layout
    build_menu_layout = []

    menu_item_definitions = [
        {"id": "frame",         "tooltip": "Structure",     "icon_name": "icon_frame.png"},
        {"id": "generator",     "tooltip": "Générateur",    "icon_name": "icon_generator.png"},
        {"id": "storage",       "tooltip": "Stockage Fer",  "icon_name": "icon_storage.png"},
        {"id": "miner",         "tooltip": "Mine de Fer",   "icon_name": "icon_miner.png"},
        {"id": "gatling_turret","tooltip": "Tourelle Gatling","icon_name": "icon_turret_gatling.png"},
        {"id": "mortar_turret", "tooltip": "Tourelle Mortier","icon_name": "icon_turret_mortar.png"},
        {"id": "expand_up",     "tooltip": "Étendre Haut",  "icon_name": "icon_expand_up.png"},
        {"id": "expand_side",   "tooltip": "Étendre Côté",  "icon_name": "icon_expand_side.png"},
    ]

    # MODIFIED: Use scaler for dimensions
    button_base_w = cfg.BASE_UI_BUILD_MENU_BUTTON_SIZE_W
    button_base_h = cfg.BASE_UI_BUILD_MENU_BUTTON_SIZE_H
    button_size_w = scaler.scale_value(button_base_w)
    button_size_h = scaler.scale_value(button_base_h)
    button_padding = scaler.scale_value(cfg.BASE_UI_BUILD_MENU_BUTTON_PADDING) # Used BUILD_MENU_BUTTON_PADDING before

    start_x = scaler.scale_value(10) # Base padding
    menu_height = scaler.ui_build_menu_height
    menu_rect_y = scaler.actual_h - menu_height
    button_y = menu_rect_y + (menu_height - button_size_h) // 2
    
    icon_padding_internal = scaler.scale_value(10) # Internal padding for icon inside button

    for item_def in menu_item_definitions:
        icon_full_path = cfg.UI_SPRITE_PATH + item_def["icon_name"]
        icon_surf_orig = util.load_sprite(icon_full_path) # Load unscaled

        icon_scaled_w = button_size_w - icon_padding_internal
        icon_scaled_h = button_size_h - icon_padding_internal
        icon_surf_scaled = util.scale_sprite_to_size(icon_surf_orig, icon_scaled_w, icon_scaled_h)

        btn_rect = pygame.Rect(start_x, button_y, button_size_w, button_size_h)
        build_menu_layout.append({
            "id": item_def["id"],
            "rect": btn_rect,
            "tooltip": item_def["tooltip"],
            "icon": icon_surf_scaled
        })
        start_x += button_size_w + button_padding # Use scaled padding

# MODIFIED: Accepter scaler
def draw_build_menu_ui(screen, game_state, scaler: util.Scaler):
    global build_menu_layout # Doit être global ou passé si modifié par initialize
    if not build_menu_layout: # S'assurer qu'il est initialisé
        initialize_build_menu_layout(game_state, scaler) # Passer scaler

    menu_height_runtime = scaler.ui_build_menu_height
    if menu_height_runtime <= 0:
        if cfg.DEBUG_MODE: print(f"DEBUG: Build menu not drawn, height <= 0: {menu_height_runtime}")
        return

    menu_rect = pygame.Rect(0, scaler.actual_h - menu_height_runtime, scaler.actual_w, menu_height_runtime)
    bg_color = cfg.COLOR_BUILD_MENU_BG # Alias for clarity
    if cfg.DEBUG_MODE: print(f"DEBUG: Drawing build menu. Rect: {menu_rect}, Color: {bg_color}, Scaler Actual H: {scaler.actual_h}, Menu Height Runtime: {menu_height_runtime}")
    pygame.draw.rect(screen, bg_color, menu_rect)
    pygame.draw.line(screen, cfg.COLOR_GRID_BORDER, menu_rect.topleft, menu_rect.topright, 2)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_tooltip_text = None

    for button_info in build_menu_layout:
        # Button drawing logic based on scaled layout is fine
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

        if btn_rect.collidepoint(mouse_x, mouse_y): # Tooltip logic
            current_tooltip_base = button_info["tooltip"]
            item_id_for_stats = button_info["id"]
            # Corrected logic for item_id_for_stats: "frame" should map to "frame" stats, not "foundation"
            # "foundation" is likely a distinct item type if it exists. If "frame" means the buildable frame, stats should be for "frame".
            # Assuming original intent was if "frame" button is for placing something whose stats are under "foundation",
            # but this is unusual. Sticking to direct mapping unless objects.get_item_stats handles "foundation" for "frame" id.
            # For now, let's assume item_id_for_stats directly maps.
            # if item_id_for_stats == "frame": item_id_for_stats = "foundation" # Business logic - Original line, keeping for now as per source.

            if not button_info["id"].startswith("expand_"):
                item_stats = objects.get_item_stats(item_id_for_stats) # Uses original item_id_for_stats which might be "foundation"
                cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
                cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
                current_tooltip_base += f" ($:{cost_money} Fe:{cost_iron})"
            else: # Expansion costs
                cost = 0
                if hasattr(game_state, 'get_next_expansion_cost'):
                    cost = game_state.get_next_expansion_cost("up" if button_info["id"] == "expand_up" else "side")
                current_tooltip_base += f" ($:{cost})"
            hovered_tooltip_text = current_tooltip_base

    if hovered_tooltip_text:
        # MODIFIED: Use scaler for font size and tooltip offsets/paddings
        tooltip_surf = util.render_text_surface(hovered_tooltip_text, scaler.font_size_small, TOOLTIP_TEXT_COLOR)
        if tooltip_surf:
            tooltip_offset_y_scaled = scaler.scale_value(cfg.BASE_UI_TOOLTIP_OFFSET_Y)
            tooltip_rect = tooltip_surf.get_rect(midbottom=(mouse_x, mouse_y + tooltip_offset_y_scaled))
            
            screen_boundary = screen.get_rect()
            tooltip_rect.clamp_ip(screen_boundary)

            tooltip_padding_x_scaled = scaler.scale_value(cfg.BASE_UI_TOOLTIP_PADDING_X)
            tooltip_padding_y_scaled = scaler.scale_value(cfg.BASE_UI_TOOLTIP_PADDING_Y)
            bg_rect = tooltip_rect.inflate(tooltip_padding_x_scaled * 2, tooltip_padding_y_scaled * 2)
            bg_rect.clamp_ip(screen_boundary)
            
            tooltip_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            tooltip_bg_surf.fill(TOOLTIP_BG_COLOR)
            screen.blit(tooltip_bg_surf, bg_rect.topleft)
            screen.blit(tooltip_surf, tooltip_rect.topleft)

# MODIFIED: Accepter scaler
def check_build_menu_click(game_state, mouse_pixel_pos, scaler: util.Scaler):
    if not build_menu_layout: return None
    # MODIFIED: Use scaler for menu rect dimensions
    menu_ui_rect = pygame.Rect(0, scaler.actual_h - scaler.ui_build_menu_height, scaler.actual_w, scaler.ui_build_menu_height)
    if not menu_ui_rect.collidepoint(mouse_pixel_pos):
        return None
    for button_info in build_menu_layout: # build_menu_layout contains scaled rects
        if button_info["rect"].collidepoint(mouse_pixel_pos):
            return button_info["id"]
    return None

# MODIFIED: Accepter scaler
def draw_placement_preview(screen, game_state, scaler: util.Scaler):
     if hasattr(game_state, 'selected_item_to_place_type') and game_state.selected_item_to_place_type and \
       hasattr(game_state, 'placement_preview_sprite') and game_state.placement_preview_sprite and \
       hasattr(game_state, 'buildable_area_rect_pixels'):

        # MODIFIED: game_state.placement_preview_sprite is original, scale it here
        preview_sprite_orig = game_state.placement_preview_sprite
        preview_sprite_scaled = util.scale_sprite_to_tile(preview_sprite_orig, scaler)

        if preview_sprite_scaled: # Only if scaling succeeded
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_origin = (game_state.buildable_area_rect_pixels.x, game_state.buildable_area_rect_pixels.y)
            # MODIFIED: Pass scaler to conversion functions
            grid_r, grid_c = util.convert_pixels_to_grid((mouse_x, mouse_y), grid_origin, scaler)

            if 0 <= grid_r < game_state.grid_height_tiles and 0 <= grid_c < game_state.grid_width_tiles:
                preview_x, preview_y = util.convert_grid_to_pixels((grid_r, grid_c), grid_origin, scaler) # MODIFIED
                
                temp_sprite = preview_sprite_scaled.copy() # Use the scaled sprite
                # Set alpha on the copy if desired (original has alpha set from GameState)
                # temp_sprite.set_alpha(150) # Example
                color_tint = cfg.COLOR_PLACEMENT_INVALID
                if hasattr(game_state, 'is_placement_valid_preview') and game_state.is_placement_valid_preview:
                    color_tint = cfg.COLOR_PLACEMENT_VALID
                temp_sprite.fill(color_tint, special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(temp_sprite, (preview_x, preview_y))

# MODIFIED: Accepter scaler
def draw_error_message(screen, message, game_state, scaler: util.Scaler):
    if not message or not hasattr(game_state, 'error_message_timer') or game_state.error_message_timer <= 0:
        return
    # MODIFIED: Use scaler for font size, positions, offsets
    error_surf = util.render_text_surface(message, scaler.font_size_medium, cfg.COLOR_RED, background_color=(50,50,50, 200))
    if error_surf:
        pos_x = (scaler.actual_w - error_surf.get_width()) // 2
        pos_y = scaler.ui_top_bar_height + scaler.scale_value(cfg.BASE_UI_ERROR_MESSAGE_OFFSET_Y)
        screen.blit(error_surf, (pos_x, pos_y))

pause_menu_buttons_layout = []

# MODIFIED: Accepter scaler
def initialize_pause_menu_layout(scaler: util.Scaler):
    global pause_menu_buttons_layout
    pause_menu_buttons_layout = []
    options = [
        {"text": "Reprendre", "action": "resume"},
        {"text": "Recommencer", "action": "restart"},
        {"text": "Menu Principal", "action": cfg.STATE_MENU}, # Using cfg constant
        {"text": "Quitter le Jeu", "action": cfg.STATE_QUIT}  # Using cfg constant
    ]
    # MODIFIED: Use scaler for dimensions
    btn_width = scaler.scale_value(220) # Example base width: 220
    btn_height = scaler.scale_value(50) # Example base height: 50
    spacing = scaler.scale_value(20)    # Example base spacing: 20
    num_buttons = len(options)
    total_height = num_buttons * btn_height + (num_buttons - 1) * spacing
    start_y = (scaler.actual_h - total_height) / 2 + scaler.scale_value(50) # Example base offset: 50

    for i, opt in enumerate(options):
        rect = pygame.Rect((scaler.actual_w - btn_width) / 2, start_y + i * (btn_height + spacing), btn_width, btn_height)
        pause_menu_buttons_layout.append({"text": opt["text"], "rect": rect, "action": opt["action"]})

# MODIFIED: Accepter scaler
def draw_pause_screen(screen, scaler: util.Scaler):
    if not pause_menu_buttons_layout:
        initialize_pause_menu_layout(scaler) # Pass scaler

    # MODIFIED: Use scaler for dimensions
    overlay = pygame.Surface((scaler.actual_w, scaler.actual_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # MODIFIED: Use scaler for font size and positions
    pause_text_surf = util.render_text_surface("PAUSE", scaler.font_size_xlarge, cfg.COLOR_WHITE)
    if pause_text_surf:
        text_rect = pause_text_surf.get_rect(center=(scaler.actual_w // 2, scaler.actual_h // 3))
        screen.blit(pause_text_surf, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    for btn in pause_menu_buttons_layout: # Layout contains scaled rects
        bg_color = cfg.COLOR_BUTTON_BG
        border_color = cfg.COLOR_BUTTON_BORDER
        if btn["rect"].collidepoint(mouse_pos):
            bg_color = cfg.COLOR_BUTTON_HOVER_BG
            border_color = cfg.COLOR_BUTTON_SELECTED_BORDER
        
        pygame.draw.rect(screen, bg_color, btn["rect"])
        pygame.draw.rect(screen, border_color, btn["rect"], 3)
        
        # MODIFIED: Use scaler for font size
        btn_text_surf = util.render_text_surface(btn["text"], scaler.font_size_medium, cfg.COLOR_TEXT)
        if btn_text_surf:
            btn_text_rect = btn_text_surf.get_rect(center=btn["rect"].center)
            screen.blit(btn_text_surf, btn_text_rect)

# MODIFIED: Accepter scaler (though primarily uses layout)
def check_pause_menu_click(event, mouse_pos, scaler: util.Scaler):
    if not pause_menu_buttons_layout: return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for btn in pause_menu_buttons_layout: # Layout contains scaled rects
            if btn["rect"].collidepoint(mouse_pos):
                return btn["action"] # Action is already string or cfg constant
    return None

game_over_buttons_layout = []

# MODIFIED: Accepter scaler
def initialize_game_over_layout(scaler: util.Scaler):
    global game_over_buttons_layout
    game_over_buttons_layout = []
    options = [
        {"text": "Recommencer", "action": "retry"},
        {"text": "Menu Principal", "action": cfg.STATE_MENU}, # Using cfg constant
        {"text": "Quitter le Jeu", "action": cfg.STATE_QUIT}  # Using cfg constant
    ]
    # MODIFIED: Use scaler for dimensions
    btn_width = scaler.scale_value(250) # Example base width: 250
    btn_height = scaler.scale_value(50)  # Example base height: 50
    spacing = scaler.scale_value(20)     # Example base spacing: 20
    num_buttons = len(options)
    total_height = num_buttons * btn_height + (num_buttons - 1) * spacing
    start_y = (scaler.actual_h / 2) + scaler.scale_value(60) # Example base offset: 60

    for i, opt in enumerate(options):
        rect = pygame.Rect((scaler.actual_w - btn_width) / 2, start_y + i * (btn_height + spacing), btn_width, btn_height)
        game_over_buttons_layout.append({"text": opt["text"], "rect": rect, "action": opt["action"]})

# MODIFIED: Accepter scaler
def draw_game_over_screen(screen, final_score, scaler: util.Scaler):
    if not game_over_buttons_layout:
        initialize_game_over_layout(scaler) # Pass scaler

    # MODIFIED: Use scaler for dimensions
    overlay = pygame.Surface((scaler.actual_w, scaler.actual_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    # MODIFIED: Use scaler for font size and positions
    go_text_surf = util.render_text_surface("GAME OVER", scaler.font_size_xlarge, cfg.COLOR_RED)
    score_text_surf = util.render_text_surface(f"Score Final: {final_score}", scaler.font_size_large, cfg.COLOR_WHITE)

    if go_text_surf:
        go_rect = go_text_surf.get_rect(center=(scaler.actual_w // 2, scaler.actual_h // 2 - scaler.scale_value(60)))
        screen.blit(go_text_surf, go_rect)
    if score_text_surf:
        score_rect = score_text_surf.get_rect(center=(scaler.actual_w // 2, scaler.actual_h // 2 + scaler.scale_value(0)))
        screen.blit(score_text_surf, score_rect)
    
    mouse_pos = pygame.mouse.get_pos()
    for btn in game_over_buttons_layout: # Layout contains scaled rects
        bg_color = cfg.COLOR_BUTTON_BG
        border_color = cfg.COLOR_BUTTON_BORDER
        if btn["rect"].collidepoint(mouse_pos):
            bg_color = cfg.COLOR_BUTTON_HOVER_BG
            border_color = cfg.COLOR_BUTTON_SELECTED_BORDER
        
        pygame.draw.rect(screen, bg_color, btn["rect"])
        pygame.draw.rect(screen, border_color, btn["rect"], 3)
        
        # MODIFIED: Use scaler for font size
        btn_text_surf = util.render_text_surface(btn["text"], scaler.font_size_medium, cfg.COLOR_TEXT)
        if btn_text_surf:
            btn_text_rect = btn_text_surf.get_rect(center=btn["rect"].center)
            screen.blit(btn_text_surf, btn_text_rect)

# MODIFIED: Accepter scaler (though primarily uses layout)
def check_game_over_menu_click(event, mouse_pos, scaler: util.Scaler):
    if not game_over_buttons_layout: return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for btn in game_over_buttons_layout: # Layout contains scaled rects
            if btn["rect"].collidepoint(mouse_pos):
                return btn["action"] # Action is already string or cfg constant
    return None

# MODIFIED: Accepter scaler
def draw_tutorial_message(screen, message, game_state, scaler: util.Scaler):
    if not message or not hasattr(game_state, 'tutorial_message_timer') or game_state.tutorial_message_timer <= 0:
        return
        
    font_to_use = scaler.font_size_medium
    msg_surf = util.render_text_surface(message, font_to_use, cfg.COLOR_WHITE, background_color=(20,20,80, 200))
    if msg_surf:
        pos_x = (scaler.actual_w - msg_surf.get_width()) // 2
        # Positionner au-dessus du menu de construction
        pos_y = scaler.actual_h - scaler.ui_build_menu_height - msg_surf.get_height() - scaler.scale_value(cfg.BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y)
        screen.blit(msg_surf, (pos_x, pos_y))
