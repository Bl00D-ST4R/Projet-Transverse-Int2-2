# ui_functions.py
import pygame
import game_config as cfg
from utility_functions import Scaler  # MODIFIÉ: S'assurer que c'est bien importé
import utility_functions as util  # Gardez l'alias util si vous l'utilisez ailleurs
import objects  # Import nécessaire pour get_item_stats si utilisé ailleurs
import math  # Ajouté car scaler._scale_dim_floor/font utilise math.floor/round
import os  # For os.path.join in initialize_build_menu_layout

# --- Constantes spécifiques à l'UI (si non déjà dans cfg) ---
TOOLTIP_BG_COLOR = (30, 30, 30, 220)  # Fond semi-transparent pour les tooltips
TOOLTIP_TEXT_COLOR = cfg.COLOR_WHITE

# --- Menu Principal ---

main_menu_options = [
    {"text": "Jouer", "action": cfg.STATE_GAMEPLAY, "key": pygame.K_1},
    {"text": "Tutoriel", "action": cfg.STATE_TUTORIAL, "key": pygame.K_2},
    # {"text": "Lore",            "action": cfg.STATE_LORE,     "key": pygame.K_3},
    {"text": "Quitter", "action": cfg.STATE_QUIT, "key": pygame.K_3},
]

main_menu_rendered_rects = {}


def initialize_main_menu_layout(scaler: Scaler):
    global main_menu_rendered_rects
    main_menu_rendered_rects = {}
    if cfg.DEBUG_MODE: print("Layout menu principal initialisé (sera calculé au dessin).")


def draw_main_menu(screen, scaler: Scaler):
    global main_menu_rendered_rects
    main_menu_rendered_rects = {}

    screen.fill(cfg.COLOR_MENU_BACKGROUND)  # Full screen background

    usable_center_x, usable_center_y = scaler.get_center_of_usable_area()

    title_surf = util.render_text_surface(cfg.GAME_TITLE, scaler.font_size_title, cfg.COLOR_TITLE_TEXT)

    # Position title relative to the top of the usable area
    title_y_abs = scaler.screen_origin_y + scaler.scale_value(cfg.BASE_MAIN_MENU_TITLE_Y_OFFSET)
    title_rect = title_surf.get_rect(center=(usable_center_x, title_y_abs))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()
    num_options = len(main_menu_options)

    button_height_approx = scaler.scale_value(cfg.BASE_MAIN_MENU_BUTTON_HEIGHT)
    button_spacing = scaler.scale_value(cfg.BASE_MAIN_MENU_BUTTON_SPACING)
    total_menu_height = num_options * button_height_approx + (num_options - 1) * button_spacing

    # Center menu vertically within the usable area, below the title
    # start_y_buttons_area = title_rect.bottom + scaler.scale_value(cfg.BASE_MAIN_MENU_START_Y_OFFSET_FROM_TITLE)
    # available_height_for_buttons = (scaler.screen_origin_y + scaler.usable_h) - start_y_buttons_area
    # current_y_center = start_y_buttons_area + (available_height_for_buttons - total_menu_height) // 2 + button_height_approx // 2

    # Simpler: position buttons starting at a certain offset from usable area center, or below title
    buttons_start_y_abs = title_rect.bottom + scaler.scale_value(cfg.BASE_MAIN_MENU_START_Y_OFFSET_FROM_TITLE)
    current_y_center = buttons_start_y_abs + button_height_approx // 2

    for index, option in enumerate(main_menu_options):
        key_char = pygame.key.name(option["key"])
        display_key_char = key_char[1] if key_char.startswith("[") and key_char.endswith("]") and len(key_char) == 3 and \
                                          key_char[1].isdigit() else key_char.upper()

        option_text = f"({display_key_char}) {option['text']}"
        text_surf_orig = util.render_text_surface(option_text, scaler.font_size_large, cfg.COLOR_TEXT)
        text_rect = text_surf_orig.get_rect(center=(usable_center_x, current_y_center))

        is_hovered = text_rect.collidepoint(mouse_pos)
        text_color_current = cfg.COLOR_BUTTON_HOVER_TEXT if is_hovered else cfg.COLOR_TEXT

        if is_hovered:
            final_text_surf = util.render_text_surface(option_text, scaler.font_size_large, text_color_current)
        else:
            final_text_surf = text_surf_orig

        screen.blit(final_text_surf, text_rect.topleft)
        main_menu_rendered_rects[option["action"]] = text_rect
        current_y_center += button_height_approx + button_spacing


def check_main_menu_click(event, mouse_pos, scaler: Scaler):
    # This function relies on main_menu_rendered_rects, which are already screen absolute
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for action, rect in main_menu_rendered_rects.items():
            if rect and rect.collidepoint(mouse_pos):
                if cfg.DEBUG_MODE: print(f"Menu action sélectionnée par clic: {action}")
                return action
    if event.type == pygame.KEYDOWN:
        for option in main_menu_options:
            if event.key == option["key"]:
                if cfg.DEBUG_MODE: print(
                    f"Menu action sélectionnée par clavier ({pygame.key.name(event.key)}): {option['action']}")
                return option["action"]
    return None


def draw_lore_screen(screen, scaler: Scaler):
    screen.fill(cfg.COLOR_MENU_BACKGROUND)  # Full screen background
    lore_text = [
        "Année 1941. L'ennemi déferle du ciel.",
        "Votre mission: construire et défendre la dernière ligne.",
        "Protégez la ville à tout prix.",
        "",
        "Appuyez sur Espace ou clic pour continuer..."
    ]
    usable_center_x, _ = scaler.get_center_of_usable_area()
    current_y_abs = scaler.screen_origin_y + scaler.scale_value(cfg.BASE_LORE_SCREEN_START_Y)
    line_spacing = scaler.scale_value(cfg.BASE_LORE_SCREEN_LINE_SPACING)

    for line in lore_text:
        surf = util.render_text_surface(line, scaler.font_size_medium, cfg.COLOR_TEXT)
        rect = surf.get_rect(center=(usable_center_x, current_y_abs))
        screen.blit(surf, rect)
        current_y_abs += line_spacing


# --- Fonctions d'Affichage Générales (en jeu) ---

def draw_top_bar_ui(screen, game_state, scaler: Scaler):
    if scaler.ui_top_bar_height <= 0:
        if cfg.DEBUG_MODE: print(f"DEBUG: Top bar not drawn, height <= 0: {scaler.ui_top_bar_height}")
        return

    top_bar_rect = pygame.Rect(
        scaler.screen_origin_x,
        scaler.screen_origin_y,
        scaler.usable_w,
        scaler.ui_top_bar_height
    )
    bg_color = getattr(cfg, 'COLOR_UI_TOP_BAR_BG', (100, 100, 100))
    pygame.draw.rect(screen, bg_color, top_bar_rect)

    padding_x = scaler.ui_general_padding
    padding_y_center_abs = scaler.screen_origin_y + scaler.ui_top_bar_height // 2  # Y center within the bar on screen
    text_color_default = getattr(cfg, 'COLOR_UI_TEXT_ON_GREY', cfg.COLOR_BLACK)
    icon_text_spacing = scaler.scale_value(cfg.BASE_UI_ICON_TEXT_SPACING)

    current_x_abs = scaler.screen_origin_x + padding_x

    # Money
    money_icon = game_state.ui_icons.get('money')
    if money_icon:
        scaled_icon = util.scale_sprite_to_size(money_icon, scaler.ui_icon_size_default, scaler.ui_icon_size_default)
        if scaled_icon:
            icon_rect = scaled_icon.get_rect(midleft=(current_x_abs, padding_y_center_abs))
            screen.blit(scaled_icon, icon_rect)
            current_x_abs = icon_rect.right + icon_text_spacing // 2
    money_text_surf = util.render_text_surface(f"{int(game_state.money)}", scaler.font_size_medium, cfg.COLOR_MONEY)
    if money_text_surf:
        money_rect = money_text_surf.get_rect(midleft=(current_x_abs, padding_y_center_abs))
        screen.blit(money_text_surf, money_rect)
        current_x_abs = money_rect.right + padding_x

    # Iron
    iron_icon = game_state.ui_icons.get('iron')
    if iron_icon:
        scaled_icon = util.scale_sprite_to_size(iron_icon, scaler.ui_icon_size_default, scaler.ui_icon_size_default)
        if scaled_icon:
            icon_rect = scaled_icon.get_rect(midleft=(current_x_abs, padding_y_center_abs))
            screen.blit(scaled_icon, icon_rect)
            current_x_abs = icon_rect.right + icon_text_spacing // 2
    iron_production_rate = getattr(game_state, 'iron_production_per_tick_display',
                                   game_state.iron_production_per_minute / 60.0)
    iron_text_str = f"{int(game_state.iron_stock)}/{game_state.iron_storage_capacity} (+{iron_production_rate:.1f}/s)"
    iron_text_surf = util.render_text_surface(iron_text_str, scaler.font_size_medium, cfg.COLOR_IRON)
    if iron_text_surf:
        iron_rect = iron_text_surf.get_rect(midleft=(current_x_abs, padding_y_center_abs))
        screen.blit(iron_text_surf, iron_rect)
        current_x_abs = iron_rect.right + padding_x

    # Energy
    energy_icon = game_state.ui_icons.get('energy')
    if energy_icon:
        scaled_icon = util.scale_sprite_to_size(energy_icon, scaler.ui_icon_size_default, scaler.ui_icon_size_default)
        if scaled_icon:
            icon_rect = scaled_icon.get_rect(midleft=(current_x_abs, padding_y_center_abs))
            screen.blit(scaled_icon, icon_rect)
            current_x_abs = icon_rect.right + icon_text_spacing // 2
    available_energy = game_state.electricity_produced - game_state.electricity_consumed
    energy_color = cfg.COLOR_ENERGY_OK if available_energy >= 0 else cfg.COLOR_ENERGY_FAIL
    if -cfg.ENERGY_LOW_THRESHOLD < available_energy < 0: energy_color = cfg.COLOR_ENERGY_LOW
    energy_text_surf = util.render_text_surface(
        f"{available_energy}W ({game_state.electricity_produced}P/{game_state.electricity_consumed}C)",
        scaler.font_size_medium, energy_color
    )
    if energy_text_surf:
        energy_rect = energy_text_surf.get_rect(midleft=(current_x_abs, padding_y_center_abs))
        screen.blit(energy_text_surf, energy_rect)

    # Right-aligned items (within usable area)
    right_align_x_abs = scaler.screen_origin_x + scaler.usable_w - padding_x

    # Wave Text
    wave_text_str = ""  # Logic as before
    if game_state.wave_in_progress:
        wave_text_str = f"Vague {game_state.current_wave_number}"
    elif game_state.game_over_flag:
        wave_text_str = "Game Over"
    elif game_state.all_waves_completed:
        wave_text_str = "Vagues Terminées!"
    elif game_state.current_wave_number == 0 and game_state.time_to_next_wave_seconds > 0:
        wave_text_str = f"Début {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    elif game_state.time_to_next_wave_seconds > 0:
        wave_text_str = f"Suivante {int(game_state.time_to_next_wave_seconds // 60):02}:{int(game_state.time_to_next_wave_seconds % 60):02}"
    else:
        wave_text_str = "Préparation..."

    wave_text_surf = util.render_text_surface(wave_text_str, scaler.font_size_medium, text_color_default)
    if wave_text_surf:
        wave_rect = wave_text_surf.get_rect(midright=(right_align_x_abs, padding_y_center_abs))
        screen.blit(wave_text_surf, wave_rect)
        right_align_x_abs = wave_rect.left - padding_x

    # City HP
    hp_text_str = f"Ville: {game_state.city_hp}/{game_state.max_city_hp}"
    hp_text_surf = util.render_text_surface(hp_text_str, scaler.font_size_medium, text_color_default)
    if hp_text_surf:
        hp_rect = hp_text_surf.get_rect(midright=(right_align_x_abs, padding_y_center_abs))
        screen.blit(hp_text_surf, hp_rect)
        right_align_x_abs = hp_rect.left - icon_text_spacing // 2
    heart_icon = game_state.ui_icons.get('heart_full')
    if heart_icon:
        scaled_icon = util.scale_sprite_to_size(heart_icon, scaler.ui_icon_size_default, scaler.ui_icon_size_default)
        if scaled_icon:
            icon_rect = scaled_icon.get_rect(midright=(right_align_x_abs, padding_y_center_abs))
            screen.blit(scaled_icon, icon_rect)


def draw_base_grid(screen, game_state, scaler: Scaler):
    # buildable_area_rect_pixels in GameState should already be calculated considering usable area origins
    if not hasattr(game_state, 'buildable_area_rect_pixels') or not game_state.buildable_area_rect_pixels:
        return
    grid_origin_x_abs = game_state.buildable_area_rect_pixels.left
    grid_origin_y_abs = game_state.buildable_area_rect_pixels.top
    tile_size = scaler.tile_size
    if tile_size <= 0: return

    for r in range(game_state.grid_height_tiles):
        for c in range(game_state.grid_width_tiles):
            tile_rect = pygame.Rect(
                grid_origin_x_abs + c * tile_size,
                grid_origin_y_abs + r * tile_size,
                tile_size, tile_size
            )
            is_reinforced_spot = False
            if hasattr(cfg, 'BASE_GRID_INITIAL_HEIGHT_TILES') and hasattr(game_state, 'get_reinforced_row_index'):
                # Assuming get_reinforced_row_index gives the absolute row index from original bottom
                # This logic needs careful review based on how grid expansion and indexing work
                reinforced_row_from_top = game_state.get_reinforced_row_index()  # If this is visual row index
                if r == reinforced_row_from_top and c < game_state.grid_initial_width_tiles:
                    is_reinforced_spot = True

            color_reinforced = getattr(cfg, 'COLOR_GRID_REINFORCED', (65, 75, 85))
            color_default = getattr(cfg, 'COLOR_GRID_DEFAULT', (45, 55, 65))
            color_border = getattr(cfg, 'COLOR_GRID_BORDER', (80, 90, 100))
            border_thickness = scaler.scale_value(cfg.BASE_GRID_BORDER_THICKNESS)

            tile_color = color_reinforced if is_reinforced_spot else color_default
            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, color_border, tile_rect, border_thickness)


build_menu_layout = []


def initialize_build_menu_layout(game_state, scaler: Scaler):
    global build_menu_layout
    build_menu_layout = []
    menu_item_definitions = [
        {"id": "frame", "tooltip": "Structure", "icon_name": "icon_frame.png"},
        {"id": "generator", "tooltip": "Générateur", "icon_name": "icon_generator.png"},
        {"id": "storage", "tooltip": "Stockage Fer", "icon_name": "icon_storage.png"},
        {"id": "miner", "tooltip": "Mine de Fer", "icon_name": "icon_miner.png"},
        # ANCIEN: {"id": "gatling_turret", "tooltip": "Tourelle Gatling", "icon_name": "icon_turret_gatling.png"},
        {"id": "machine_gun_turret", "tooltip": "Mitrailleuse", "icon_name": "icon_turret_machinegun.png"}, # NOUVEAU
        {"id": "mortar_turret", "tooltip": "Tourelle Mortier", "icon_name": "icon_turret_mortar.png"},
        {"id": "flamethrower_turret", "tooltip": "Lance-Flammes", "icon_name": "icon_turret_flamethrower.png"}, # NOUVEAU
        {"id": "sniper_turret", "tooltip": "Tourelle Sniper", "icon_name": "icon_turret_sniper.png"},       # NOUVEAU
        {"id": "expand_up", "tooltip": "Étendre Haut", "icon_name": "icon_expand_up.png"},
        {"id": "expand_side", "tooltip": "Étendre Côté", "icon_name": "icon_expand_side.png"},
    ]

    button_size_w = scaler.ui_build_menu_button_w
    button_size_h = scaler.ui_build_menu_button_h
    button_padding = scaler.ui_build_menu_button_padding
    menu_height = scaler.ui_build_menu_height  # This is the height of the bar itself

    # Y position of the build menu bar on the screen (top edge of the bar)
    menu_bar_top_y_abs = scaler.screen_origin_y + scaler.usable_h - menu_height

    # X position for the first button, inside the usable area
    current_button_x_abs = scaler.screen_origin_x + scaler.ui_general_padding

    # Y position for the buttons, centered vertically within the menu bar
    button_center_y_in_bar = menu_height // 2
    button_actual_y_abs = menu_bar_top_y_abs + button_center_y_in_bar - (button_size_h // 2)

    icon_padding_internal = scaler.scale_value(cfg.BASE_UI_GENERAL_PADDING)

    for item_def in menu_item_definitions:
        icon_full_path = os.path.join(cfg.UI_SPRITE_PATH, item_def["icon_name"])
        icon_surf_orig = util.load_sprite(icon_full_path)
        icon_target_w = button_size_w - (2 * icon_padding_internal)
        icon_target_h = button_size_h - (2 * icon_padding_internal)
        icon_surf_scaled = util.scale_sprite_to_size(icon_surf_orig, icon_target_w, icon_target_h)

        btn_rect = pygame.Rect(current_button_x_abs, button_actual_y_abs, button_size_w, button_size_h)
        build_menu_layout.append({
            "id": item_def["id"], "rect": btn_rect, "tooltip": item_def["tooltip"], "icon": icon_surf_scaled
        })
        current_button_x_abs += button_size_w + button_padding
    if cfg.DEBUG_MODE: print("UI DEBUG: Build menu layout initialized (usable area aware).")


def draw_build_menu_ui(screen, game_state, scaler: Scaler):
    global build_menu_layout
    # Check if scaler properties that affect layout are valid (e.g., button_w > 0)
    if not build_menu_layout or scaler.ui_build_menu_button_w == 0:
        initialize_build_menu_layout(game_state, scaler)
        if not build_menu_layout: return  # Failed to init

    menu_height_runtime = scaler.ui_build_menu_height
    if menu_height_runtime <= 0: return

    menu_rect_y_on_screen_abs = scaler.screen_origin_y + scaler.usable_h - menu_height_runtime
    menu_rect_abs = pygame.Rect(
        scaler.screen_origin_x,
        menu_rect_y_on_screen_abs,
        scaler.usable_w,
        menu_height_runtime
    )
    bg_color = cfg.COLOR_BUILD_MENU_BG
    pygame.draw.rect(screen, bg_color, menu_rect_abs)
    border_thickness = scaler.scale_value(cfg.BASE_UI_BORDER_THICKNESS)
    pygame.draw.line(screen, cfg.COLOR_GRID_BORDER, menu_rect_abs.topleft, menu_rect_abs.topright, border_thickness)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_tooltip_text = None

    for button_info in build_menu_layout:  # Button rects are screen absolute
        btn_rect = button_info["rect"]
        is_selected = (hasattr(game_state, 'selected_item_to_place_type') and
                       game_state.selected_item_to_place_type == button_info["id"])
        is_hovered = btn_rect.collidepoint(mouse_x, mouse_y)

        bg_color_btn = cfg.COLOR_BUTTON_HOVER_BG if is_hovered else cfg.COLOR_BUTTON_BG
        border_color_current = cfg.COLOR_BUTTON_HOVER_BORDER if is_hovered else \
            (cfg.COLOR_BUTTON_SELECTED_BORDER if is_selected else cfg.COLOR_BUTTON_BORDER)

        pygame.draw.rect(screen, bg_color_btn, btn_rect)
        if button_info["icon"]:
            icon_x = btn_rect.centerx - button_info["icon"].get_width() // 2
            icon_y = btn_rect.centery - button_info["icon"].get_height() // 2
            screen.blit(button_info["icon"], (icon_x, icon_y))
        pygame.draw.rect(screen, border_color_current, btn_rect, border_thickness)

        if is_hovered:  # Tooltip logic (same as before, positions relative to mouse)
            current_tooltip_base = button_info["tooltip"]
            item_id_for_stats = button_info["id"]
            if not item_id_for_stats.startswith("expand_"):
                item_stats = objects.get_item_stats(item_id_for_stats)
                cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0) if item_stats else 0
                cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0) if item_stats else 0
                current_tooltip_base += f" ($:{cost_money} Fe:{cost_iron})"
            else:
                cost = "N/A"
                if hasattr(game_state, 'get_next_expansion_cost'):
                    cost_val = game_state.get_next_expansion_cost("up" if item_id_for_stats == "expand_up" else "side")
                    cost = str(cost_val) if cost_val != "Max" else "Max"
                current_tooltip_base += f" ($:{cost})"
            hovered_tooltip_text = current_tooltip_base

    if hovered_tooltip_text:  # Tooltip drawing logic (same as before)
        tooltip_surf = util.render_text_surface(hovered_tooltip_text, scaler.font_size_small, TOOLTIP_TEXT_COLOR)
        if tooltip_surf:
            tooltip_offset_y_scaled = scaler.scale_value(cfg.BASE_UI_TOOLTIP_OFFSET_Y)
            tooltip_rect = tooltip_surf.get_rect(midbottom=(mouse_x, mouse_y + tooltip_offset_y_scaled))
            screen_boundary = screen.get_rect()  # Full screen rect for tooltip clamping
            tooltip_rect.clamp_ip(screen_boundary)
            tooltip_padding_x_scaled = scaler.scale_value(cfg.BASE_UI_TOOLTIP_PADDING_X)
            tooltip_padding_y_scaled = scaler.scale_value(cfg.BASE_UI_TOOLTIP_PADDING_Y)
            bg_rect = tooltip_rect.inflate(tooltip_padding_x_scaled * 2, tooltip_padding_y_scaled * 2)
            bg_rect.clamp_ip(screen_boundary)
            tooltip_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            tooltip_bg_surf.fill(TOOLTIP_BG_COLOR)
            screen.blit(tooltip_bg_surf, bg_rect.topleft)
            screen.blit(tooltip_surf, tooltip_rect.topleft)


def check_build_menu_click(game_state, mouse_pixel_pos, scaler: Scaler):
    # This function relies on build_menu_layout which now has screen absolute rects
    if not build_menu_layout: return None
    # Optional: check if click is within the menu bar's absolute screen rect first
    menu_bar_rect = pygame.Rect(scaler.screen_origin_x,
                                scaler.screen_origin_y + scaler.usable_h - scaler.ui_build_menu_height,
                                scaler.usable_w, scaler.ui_build_menu_height)
    if not menu_bar_rect.collidepoint(mouse_pixel_pos):  # Optimization
        return None
    for button_info in build_menu_layout:
        if button_info["rect"].collidepoint(mouse_pixel_pos):
            return button_info["id"]
    return None


def draw_placement_preview(screen, game_state, scaler: Scaler):
    # GameState's buildable_area_rect_pixels is already screen absolute
    if hasattr(game_state, 'selected_item_to_place_type') and game_state.selected_item_to_place_type and \
            hasattr(game_state, 'placement_preview_sprite') and game_state.placement_preview_sprite and \
            hasattr(game_state, 'buildable_area_rect_pixels'):
        preview_sprite_orig = game_state.placement_preview_sprite
        preview_sprite_scaled = util.scale_sprite_to_tile(preview_sprite_orig, scaler)
        if preview_sprite_scaled:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_origin_abs = (game_state.buildable_area_rect_pixels.x, game_state.buildable_area_rect_pixels.y)
            grid_r, grid_c = util.convert_pixels_to_grid((mouse_x, mouse_y), grid_origin_abs, scaler)
            if 0 <= grid_r < game_state.grid_height_tiles and 0 <= grid_c < game_state.grid_width_tiles:
                preview_x, preview_y = util.convert_grid_to_pixels((grid_r, grid_c), grid_origin_abs, scaler)
                temp_sprite = preview_sprite_scaled.copy()
                color_tint = cfg.COLOR_PLACEMENT_INVALID
                if hasattr(game_state, 'is_placement_valid_preview') and game_state.is_placement_valid_preview:
                    color_tint = cfg.COLOR_PLACEMENT_VALID
                temp_sprite.fill(color_tint + (cfg.PLACEMENT_PREVIEW_ALPHA,), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(temp_sprite, (preview_x, preview_y))


def draw_error_message(screen, message, game_state, scaler: Scaler):
    if not message or not hasattr(game_state, 'error_message_timer') or game_state.error_message_timer <= 0:
        return
    error_surf = util.render_text_surface(message, scaler.font_size_medium, cfg.COLOR_ERROR_TEXT,
                                          background_color=cfg.COLOR_ERROR_BG)
    if error_surf:
        # Centered horizontally within usable area
        pos_x_abs = scaler.screen_origin_x + (scaler.usable_w - error_surf.get_width()) // 2
        # Positioned vertically below top bar, within usable area
        pos_y_abs = scaler.screen_origin_y + scaler.ui_top_bar_height + scaler.scale_value(
            cfg.BASE_UI_ERROR_MESSAGE_OFFSET_Y)
        screen.blit(error_surf, (pos_x_abs, pos_y_abs))


# --- MODAL SCREENS (Pause, Game Over) ---
# These will draw an overlay over the usable area and center their content within it.

pause_menu_buttons_layout = []


def initialize_pause_menu_layout(scaler: Scaler):
    global pause_menu_buttons_layout
    pause_menu_buttons_layout = []
    options = [
        {"text": "Reprendre", "action": "resume"}, {"text": "Recommencer", "action": "restart_game"},
        {"text": "Menu Principal", "action": cfg.STATE_MENU}, {"text": "Quitter le Jeu", "action": cfg.STATE_QUIT}
    ]
    btn_base_width = cfg.BASE_PAUSE_MENU_BUTTON_WIDTH
    btn_base_height = cfg.BASE_PAUSE_MENU_BUTTON_HEIGHT
    spacing_base = cfg.BASE_PAUSE_MENU_SPACING
    btn_width = scaler.scale_value(btn_base_width)
    btn_height = scaler.scale_value(btn_base_height)
    spacing = scaler.scale_value(spacing_base)

    usable_center_x, usable_center_y = scaler.get_center_of_usable_area()

    # Calculate total height of buttons to help center them vertically
    num_buttons = len(options)
    total_buttons_block_height = num_buttons * btn_height + (num_buttons - 1) * spacing

    # Start Y for the block of buttons, e.g., slightly below center of usable area
    # Or below a "PAUSE" title. For simplicity, let's center block around usable_center_y + offset
    block_start_y_abs = usable_center_y - total_buttons_block_height // 2 + scaler.scale_value(
        cfg.BASE_PAUSE_MENU_BUTTON_BLOCK_Y_OFFSET)

    for i, opt in enumerate(options):
        rect_x_abs = usable_center_x - btn_width // 2
        rect_y_abs = block_start_y_abs + i * (btn_height + spacing)
        rect = pygame.Rect(rect_x_abs, rect_y_abs, btn_width, btn_height)
        pause_menu_buttons_layout.append({"text": opt["text"], "rect": rect, "action": opt["action"]})
    if cfg.DEBUG_MODE: print("UI DEBUG: Pause menu layout initialized (usable area aware).")


def draw_pause_screen(screen, scaler: Scaler):
    if not pause_menu_buttons_layout: initialize_pause_menu_layout(scaler)
    if not pause_menu_buttons_layout: return

    overlay = pygame.Surface((scaler.usable_w, scaler.usable_h), pygame.SRCALPHA)
    overlay.fill(cfg.COLOR_PAUSE_OVERLAY_BG)
    screen.blit(overlay, (scaler.screen_origin_x, scaler.screen_origin_y))

    usable_center_x, _ = scaler.get_center_of_usable_area()
    pause_title_y_abs = scaler.screen_origin_y + scaler.usable_h // 3  # Example Y for "PAUSE"

    pause_text_surf = util.render_text_surface("PAUSE", scaler.font_size_xlarge, cfg.COLOR_PAUSE_TEXT)
    if pause_text_surf:
        text_rect = pause_text_surf.get_rect(center=(usable_center_x, pause_title_y_abs))
        screen.blit(pause_text_surf, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    border_thickness = scaler.scale_value(cfg.BASE_UI_BUTTON_BORDER_THICKNESS)
    for btn_info in pause_menu_buttons_layout:  # Rects are screen absolute
        btn_rect = btn_info["rect"]
        is_hovered = btn_rect.collidepoint(mouse_pos)
        bg_color = cfg.COLOR_BUTTON_HOVER_BG if is_hovered else cfg.COLOR_BUTTON_BG
        border_color_current = cfg.COLOR_BUTTON_HOVER_BORDER if is_hovered else cfg.COLOR_BUTTON_BORDER
        pygame.draw.rect(screen, bg_color, btn_rect)
        pygame.draw.rect(screen, border_color_current, btn_rect, border_thickness)
        text_surf = util.render_text_surface(btn_info["text"], scaler.font_size_medium, cfg.COLOR_TEXT)
        if text_surf:
            screen.blit(text_surf, text_surf.get_rect(center=btn_rect.center))


def check_pause_menu_click(event, mouse_pos, scaler: Scaler):  # Relies on screen absolute rects in layout
    if not pause_menu_buttons_layout: return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for btn_info in pause_menu_buttons_layout:
            if btn_info["rect"].collidepoint(mouse_pos):
                return btn_info["action"]
    return None


game_over_buttons_layout = []


def initialize_game_over_layout(scaler: Scaler):
    global game_over_buttons_layout
    game_over_buttons_layout = []
    options = [
        {"text": "Recommencer", "action": "retry"}, {"text": "Menu Principal", "action": cfg.STATE_MENU},
        {"text": "Quitter le Jeu", "action": cfg.STATE_QUIT}
    ]
    btn_base_width = cfg.BASE_GAMEOVER_MENU_BUTTON_WIDTH
    btn_base_height = cfg.BASE_GAMEOVER_MENU_BUTTON_HEIGHT
    spacing_base = cfg.BASE_GAMEOVER_MENU_SPACING
    btn_width = scaler.scale_value(btn_base_width)
    btn_height = scaler.scale_value(btn_base_height)
    spacing = scaler.scale_value(spacing_base)

    usable_center_x, usable_center_y = scaler.get_center_of_usable_area()
    num_buttons = len(options)
    total_buttons_block_height = num_buttons * btn_height + (num_buttons - 1) * spacing

    # Position button block relative to where "GAME OVER" and score are, e.g. below them
    # This assumes GAME OVER and score text are roughly centered around usable_center_y
    block_start_y_abs = usable_center_y + scaler.scale_value(cfg.BASE_GAMEOVER_MENU_BUTTON_START_Y_OFFSET)

    for i, opt in enumerate(options):
        rect_x_abs = usable_center_x - btn_width // 2
        rect_y_abs = block_start_y_abs + i * (btn_height + spacing)
        rect = pygame.Rect(rect_x_abs, rect_y_abs, btn_width, btn_height)
        game_over_buttons_layout.append({"text": opt["text"], "rect": rect, "action": opt["action"]})
    if cfg.DEBUG_MODE: print("UI DEBUG: Game Over menu layout initialized (usable area aware).")


def draw_game_over_screen(screen, final_score, scaler: Scaler):
    if not game_over_buttons_layout: initialize_game_over_layout(scaler)
    if not game_over_buttons_layout: return

    overlay = pygame.Surface((scaler.usable_w, scaler.usable_h), pygame.SRCALPHA)
    overlay.fill(cfg.COLOR_GAMEOVER_OVERLAY_BG)
    screen.blit(overlay, (scaler.screen_origin_x, scaler.screen_origin_y))

    usable_center_x, usable_center_y = scaler.get_center_of_usable_area()

    go_text_surf = util.render_text_surface("GAME OVER", scaler.font_size_xlarge, cfg.COLOR_GAMEOVER_TEXT)
    score_text_surf = util.render_text_surface(f"Score Final: {final_score}", scaler.font_size_large,
                                               cfg.COLOR_TEXT_LIGHT)

    if go_text_surf:
        go_rect_y_rel_to_center = scaler.scale_value(cfg.BASE_GAMEOVER_TEXT_Y_OFFSET)  # Offset from center
        go_rect = go_text_surf.get_rect(center=(usable_center_x, usable_center_y - go_rect_y_rel_to_center))
        screen.blit(go_text_surf, go_rect)
    if score_text_surf:
        score_rect_y_rel_to_center = scaler.scale_value(cfg.BASE_GAMEOVER_SCORE_Y_OFFSET)  # Offset from center
        score_rect = score_text_surf.get_rect(center=(usable_center_x, usable_center_y + score_rect_y_rel_to_center))
        screen.blit(score_text_surf, score_rect)

    mouse_pos = pygame.mouse.get_pos()
    border_thickness = scaler.scale_value(cfg.BASE_UI_BUTTON_BORDER_THICKNESS)
    for btn in game_over_buttons_layout:  # Rects are screen absolute
        is_hovered = btn["rect"].collidepoint(mouse_pos)
        bg_color = cfg.COLOR_BUTTON_HOVER_BG if is_hovered else cfg.COLOR_BUTTON_BG
        border_color_current = cfg.COLOR_BUTTON_HOVER_BORDER if is_hovered else cfg.COLOR_BUTTON_BORDER
        pygame.draw.rect(screen, bg_color, btn["rect"])
        pygame.draw.rect(screen, border_color_current, btn["rect"], border_thickness)
        btn_text_surf = util.render_text_surface(btn["text"], scaler.font_size_medium, cfg.COLOR_TEXT)
        if btn_text_surf:
            screen.blit(btn_text_surf, btn_text_surf.get_rect(center=btn["rect"].center))


def check_game_over_menu_click(event, mouse_pos, scaler: Scaler):
    if not game_over_buttons_layout:
        if cfg.DEBUG_MODE: print("GAME OVER CLICK CHECK: Layout non initialisé.")
        return None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if cfg.DEBUG_MODE: print(f"GAME OVER CLICK CHECK: Clic détecté à {mouse_pos}")
        for btn in game_over_buttons_layout:
            if cfg.DEBUG_MODE: print(f"  Vérification bouton: {btn['text']}, Rect: {btn['rect']}")
            if btn["rect"].collidepoint(mouse_pos):
                if cfg.DEBUG_MODE: print(f"  ACTION CLIC: {btn['action']}")
                return btn["action"]
    return None

def draw_tutorial_message(screen, message, game_state, scaler: Scaler):
    if not message or not hasattr(game_state, 'tutorial_message_timer') or game_state.tutorial_message_timer <= 0:
        return

    font_to_use = scaler.font_size_medium
    msg_surf = util.render_text_surface(message, font_to_use, cfg.COLOR_TUTORIAL_TEXT,
                                        background_color=cfg.COLOR_TUTORIAL_BG)
    if msg_surf:
        # Centered horizontally within usable area
        pos_x_abs = scaler.screen_origin_x + (scaler.usable_w - msg_surf.get_width()) // 2

        # Positioned above build menu (which is at bottom of usable area)
        build_menu_top_y_abs = scaler.screen_origin_y + scaler.usable_h - scaler.ui_build_menu_height
        pos_y_abs = build_menu_top_y_abs - msg_surf.get_height() - \
                    scaler.scale_value(cfg.BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y)

        # Clamp to usable area (especially top)
        top_bar_bottom_y_abs = scaler.screen_origin_y + scaler.ui_top_bar_height
        if pos_y_abs < top_bar_bottom_y_abs + scaler.ui_general_padding:
            pos_y_abs = top_bar_bottom_y_abs + scaler.ui_general_padding

        # Clamp horizontal position to be within usable area fully
        pos_x_abs = max(scaler.screen_origin_x, pos_x_abs)
        pos_x_abs = min(scaler.screen_origin_x + scaler.usable_w - msg_surf.get_width(), pos_x_abs)

        screen.blit(msg_surf, (pos_x_abs, pos_y_abs))