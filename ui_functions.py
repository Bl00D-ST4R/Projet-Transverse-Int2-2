# ui_functions.py
import pygame
import game_config as cfg
import utility_functions as util
# import objects # Not strictly needed for this simplified UI drawing test

# --- Constantes spécifiques à l'UI (si non déjà dans cfg) ---
# TOOLTIP_BG_COLOR, TOOLTIP_TEXT_COLOR might not be used in simplified version
# but keeping them doesn't hurt.
TOOLTIP_BG_COLOR = (30, 30, 30, 220) 
TOOLTIP_TEXT_COLOR = cfg.COLOR_WHITE

# --- Fonctions d'Affichage UI Simplifiées ---

def draw_top_bar_ui(screen, game_state, scaler: util.Scaler):
    """Affiche une barre supérieure grise simple avec du texte placeholder."""
    if scaler.ui_top_bar_height <= 0:
        if cfg.DEBUG_MODE: print("UI DEBUG: Top bar height is 0, not drawing.")
        return

    top_bar_rect = pygame.Rect(0, 0, scaler.actual_w, scaler.ui_top_bar_height)
    pygame.draw.rect(screen, cfg.COLOR_GREY_MEDIUM, top_bar_rect) # Fond gris

    # Placeholder text
    font_to_use = scaler.font_size_medium
    # Ensure game_state attributes exist or provide defaults
    money = getattr(game_state, 'money', 0)
    iron_stock = getattr(game_state, 'iron_stock', 0)
    # Other attributes used by the original function might be missing in a simplified game_state
    # So, using generic placeholders for energy and wave.
    text_surf = util.render_text_surface(
        f"Argent: {money} | Fer: {iron_stock} | Energie: ... | Vague: ...",
        font_to_use,
        cfg.COLOR_UI_TEXT_ON_GREY # Texte noir sur fond gris
    )
    if text_surf:
        text_rect = text_surf.get_rect(center=(scaler.actual_w // 2, scaler.ui_top_bar_height // 2))
        screen.blit(text_surf, text_rect)
    
    if cfg.DEBUG_MODE: print(f"UI DEBUG: Drew Top Bar - Rect: {top_bar_rect}")


def draw_build_menu_ui(screen, game_state, scaler: util.Scaler):
    """Affiche une barre de menu de construction grise simple en bas."""
    menu_height = scaler.ui_build_menu_height
    if menu_height <= 0:
        if cfg.DEBUG_MODE: print("UI DEBUG: Build menu height is 0, not drawing.")
        return

    menu_rect = pygame.Rect(0, scaler.actual_h - menu_height, scaler.actual_w, menu_height)
    pygame.draw.rect(screen, cfg.COLOR_BUILD_MENU_BG, menu_rect) # Fond plus sombre
    pygame.draw.line(screen, cfg.COLOR_GRID_BORDER, menu_rect.topleft, menu_rect.topright, 2) # Ligne en haut

    # Placeholder text
    font_to_use = scaler.font_size_medium
    text_surf = util.render_text_surface(
        "Menu de Construction (Icônes Placeholder)",
        font_to_use,
        cfg.COLOR_TEXT # Texte clair sur fond sombre
    )
    if text_surf:
        text_rect = text_surf.get_rect(center=menu_rect.center)
        screen.blit(text_surf, text_rect)

    if cfg.DEBUG_MODE: print(f"UI DEBUG: Drew Build Menu - Rect: {menu_rect}")


def draw_base_grid(screen, game_state, scaler: util.Scaler):
    """Dessine la grille de construction."""
    if not hasattr(game_state, 'buildable_area_rect_pixels') or \
       not game_state.buildable_area_rect_pixels or \
       game_state.buildable_area_rect_pixels.width == 0 or \
       game_state.buildable_area_rect_pixels.height == 0:
        if cfg.DEBUG_MODE: print("UI DEBUG: Base grid rect not valid or zero size, not drawing grid lines.")
        return

    grid_origin_x = game_state.buildable_area_rect_pixels.left
    grid_origin_y = game_state.buildable_area_rect_pixels.top
    tile_size = scaler.tile_size

    # Dessiner le fond de la zone constructible (si différent du fond général)
    # pygame.draw.rect(screen, cfg.COLOR_GRID_BACKGROUND_AREA, game_state.buildable_area_rect_pixels) # Example if needed

    # Ensure grid_height_tiles and grid_width_tiles exist on game_state
    grid_height = getattr(game_state, 'grid_height_tiles', cfg.BASE_GRID_INITIAL_HEIGHT_TILES)
    grid_width = getattr(game_state, 'grid_width_tiles', cfg.BASE_GRID_INITIAL_WIDTH_TILES)


    for r in range(grid_height):
        for c in range(grid_width):
            tile_rect = pygame.Rect(
                grid_origin_x + c * tile_size,
                grid_origin_y + r * tile_size,
                tile_size, tile_size
            )
            # Déterminer si c'est une fondation renforcée
            # Simplified: uses current_expansion_up_tiles if available, otherwise 0
            current_expansion_up = getattr(game_state, 'current_expansion_up_tiles', 0)
            initial_height_base = cfg.BASE_GRID_INITIAL_HEIGHT_TILES
            
            # The logical index of the "original" bottom reinforced row, adjusted for upward expansion
            reinforced_row_logical_idx = current_expansion_up + (initial_height_base -1)

            is_reinforced_spot = False
            if r == reinforced_row_logical_idx and c < getattr(game_state, 'grid_initial_width_tiles', cfg.BASE_GRID_INITIAL_WIDTH_TILES) :
                 is_reinforced_spot = True
            
            tile_color = cfg.COLOR_GRID_REINFORCED if is_reinforced_spot else cfg.COLOR_GRID_DEFAULT
            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, cfg.COLOR_GRID_BORDER, tile_rect, 1) # Bordure de case

# --- Fonctions des menus (principal, pause, game over, lore, tutoriel message) ---
# Pour ce test, nous n'avons pas besoin de modifier les fonctions de menu si elles
# sont appelées correctement par la machine d'état dans main.py.
# Assurez-vous qu'elles utilisent le scaler pour leurs dimensions et polices.
# Exemple:
main_menu_rendered_rects = {} # Keep this if check_main_menu_click uses it.
def initialize_main_menu_layout(scaler: util.Scaler): pass # Garder vide pour ce test si besoin

def draw_main_menu(screen, scaler: util.Scaler):
    screen.fill(cfg.COLOR_MENU_BACKGROUND)
    title_surf = util.render_text_surface("MENU PRINCIPAL (TEST)", scaler.font_size_title, cfg.COLOR_WHITE)
    if title_surf: screen.blit(title_surf, (50,50)) # Simple affichage

def check_main_menu_click(event, mouse_pos, scaler: util.Scaler): return None # Désactiver pour test

# Build menu layout and click check can be stubbed as individual buttons are not drawn
build_menu_layout = []
def initialize_build_menu_layout(game_state, scaler: util.Scaler): pass 
def check_build_menu_click(game_state, mouse_pixel_pos, scaler: util.Scaler): return None

# Garder `draw_tutorial_message` si elle est appelée.
def draw_tutorial_message(screen, message, game_state, scaler: util.Scaler):
    if not message or not hasattr(game_state, 'tutorial_message_timer') or game_state.tutorial_message_timer <=0: return
    font_to_use = scaler.font_size_medium
    msg_surf = util.render_text_surface(message, font_to_use, cfg.COLOR_WHITE, background_color=(20,20,80, 200))
    if msg_surf:
        pos_x = (scaler.actual_w - msg_surf.get_width()) // 2
        # Ensure BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y is in cfg
        offset_y_base = getattr(cfg, 'BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y', 10)
        pos_y = scaler.actual_h - scaler.ui_build_menu_height - msg_surf.get_height() - scaler.scale_value(offset_y_base)
        screen.blit(msg_surf, (pos_x, pos_y))

def draw_placement_preview(screen, game_state, scaler: util.Scaler): pass # Désactiver pour test
def draw_error_message(screen, message, game_state, scaler: util.Scaler): pass # Désactiver pour test

# Pause screen stubs
pause_menu_buttons_layout = []
def initialize_pause_menu_layout(scaler: util.Scaler): pass
def draw_pause_screen(screen, scaler: util.Scaler):
    # Draw a semi-transparent overlay to indicate pause
    if scaler and hasattr(scaler, 'actual_w') and hasattr(scaler, 'actual_h'):
        overlay = pygame.Surface((scaler.actual_w, scaler.actual_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Semi-transparent black
        screen.blit(overlay, (0,0))
        pause_text_surf = util.render_text_surface("PAUSED (TEST)", scaler.font_size_xlarge, cfg.COLOR_WHITE)
        if pause_text_surf:
            text_rect = pause_text_surf.get_rect(center=(scaler.actual_w // 2, scaler.actual_h // 2))
            screen.blit(pause_text_surf, text_rect)
    else:
        if cfg.DEBUG_MODE: print("UI DEBUG: Scaler not ready for pause screen overlay.")


def check_pause_menu_click(event, mouse_pos, scaler: util.Scaler): return None

# Game Over screen stubs
game_over_buttons_layout = []
def initialize_game_over_layout(scaler: util.Scaler): pass
def draw_game_over_screen(screen, final_score, scaler: util.Scaler):
    if scaler and hasattr(scaler, 'actual_w') and hasattr(scaler, 'actual_h'):
        overlay = pygame.Surface((scaler.actual_w, scaler.actual_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) # Darker overlay
        screen.blit(overlay, (0,0))
        game_over_text_surf = util.render_text_surface(f"GAME OVER (TEST) - Score: {final_score}", scaler.font_size_xlarge, cfg.COLOR_RED)
        if game_over_text_surf:
            text_rect = game_over_text_surf.get_rect(center=(scaler.actual_w // 2, scaler.actual_h // 2))
            screen.blit(game_over_text_surf, text_rect)
    else:
        if cfg.DEBUG_MODE: print("UI DEBUG: Scaler not ready for game over screen overlay.")


def check_game_over_menu_click(event, mouse_pos, scaler: util.Scaler): return None

def draw_lore_screen(screen, scaler: util.Scaler):
    screen.fill(cfg.COLOR_MENU_BACKGROUND)
    lore_text_surf = util.render_text_surface("LORE SCREEN (TEST)", scaler.font_size_large, cfg.COLOR_WHITE)
    if lore_text_surf:
        screen.blit(lore_text_surf, (50, scaler.actual_h // 2))
