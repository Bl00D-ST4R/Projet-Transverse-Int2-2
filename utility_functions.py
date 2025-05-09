# utility_functions.py
import pygame
import os
import math  # Importé pour math.floor et math.round
import game_config as cfg


class Scaler:
    def __init__(self, actual_screen_width, actual_screen_height,
                 ref_width=cfg.REF_WIDTH, ref_height=cfg.REF_HEIGHT):
        self.actual_w = actual_screen_width
        self.actual_h = actual_screen_height
        self.ref_w = ref_width
        self.ref_h = ref_height

        # Marges réelles en pixels
        # Ensure these are defined in game_config.py, otherwise default to a single SCREEN_MARGIN
        self.screen_margin_v = getattr(cfg, 'SCREEN_MARGIN_VERTICAL', cfg.SCREEN_MARGIN_VERTICAL)
        self.screen_margin_h = getattr(cfg, 'SCREEN_MARGIN_HORIZONTAL', cfg.SCREEN_MARGIN_HORIZONTAL)

        # Origine de la zone utilisable sur l'écran réel
        self.screen_origin_x = self.screen_margin_h
        self.screen_origin_y = self.screen_margin_v

        # Dimensions de la zone utilisable de l'écran
        self.usable_w = self.actual_w - (2 * self.screen_margin_h)
        self.usable_h = self.actual_h - (2 * self.screen_margin_v)

        if self.usable_w <= 0:  # Empêcher largeur/hauteur utilisable négative ou nulle
            if cfg.DEBUG_MODE: print(
                f"AVERTISSEMENT SCALER: Largeur utilisable ({self.usable_w}) <= 0. Marge H ({self.screen_margin_h}) trop grande pour largeur écran ({self.actual_w}). Ajustement à 1.")
            self.usable_w = 1
        if self.usable_h <= 0:
            if cfg.DEBUG_MODE: print(
                f"AVERTISSEMENT SCALER: Hauteur utilisable ({self.usable_h}) <= 0. Marge V ({self.screen_margin_v}) trop grande pour hauteur écran ({self.actual_h}). Ajustement à 1.")
            self.usable_h = 1

        if self.ref_w == 0 or self.ref_h == 0:  # Avoid division by zero
            self.scale_x_factor = 1.0
            self.scale_y_factor = 1.0
        else:
            # Les facteurs de scale sont toujours basés sur la zone UTILISABLE par rapport à la référence
            self.scale_x_factor = self.usable_w / self.ref_w
            self.scale_y_factor = self.usable_h / self.ref_h

        self.general_scale_factor = min(self.scale_x_factor, self.scale_y_factor)
        if self.general_scale_factor <= 0: self.general_scale_factor = 1.0  # Sécurité

        # Pre-calculate frequently used scaled dimensions based on general_scale_factor
        self.tile_size = self._scale_dim_floor(cfg.BASE_TILE_SIZE)
        self.ui_top_bar_height = self._scale_dim_floor(cfg.BASE_UI_TOP_BAR_HEIGHT)
        self.ui_build_menu_height = self._scale_dim_floor(cfg.BASE_UI_BUILD_MENU_HEIGHT)

        self.ui_build_menu_button_w = self._scale_dim_floor(cfg.BASE_UI_BUILD_MENU_BUTTON_SIZE_W)
        self.ui_build_menu_button_h = self._scale_dim_floor(cfg.BASE_UI_BUILD_MENU_BUTTON_SIZE_H)
        self.ui_build_menu_button_padding = self._scale_dim_floor(cfg.BASE_UI_BUILD_MENU_BUTTON_PADDING)
        self.ui_icon_size_default = self._scale_dim_floor(cfg.BASE_UI_ICON_SIZE_DEFAULT)
        self.ui_general_padding = self._scale_dim_floor(cfg.BASE_UI_GENERAL_PADDING)

        self.scaled_grid_offset_x = self._scale_dim_floor(cfg.BASE_GRID_OFFSET_X)

        self.font_size_small = self._scale_dim_font(cfg.BASE_FONT_SIZE_SMALL)
        self.font_size_medium = self._scale_dim_font(cfg.BASE_FONT_SIZE_MEDIUM)
        self.font_size_large = self._scale_dim_font(cfg.BASE_FONT_SIZE_LARGE)
        self.font_size_xlarge = self._scale_dim_font(cfg.BASE_FONT_SIZE_XLARGE)
        self.font_size_title = self._scale_dim_font(cfg.BASE_FONT_SIZE_TITLE)

        self.gravity = cfg.BASE_GRAVITY_PHYSICS * self.general_scale_factor

        if cfg.DEBUG_MODE:
            print(f"SCALER INFO: Actual Screen: {self.actual_w}x{self.actual_h}, Ref: {self.ref_w}x{self.ref_h}")
            print(f"SCALER INFO: Margin V: {self.screen_margin_v}, Margin H: {self.screen_margin_h}")
            print(
                f"SCALER INFO: Usable Area: {self.usable_w}x{self.usable_h}, Origin: ({self.screen_origin_x},{self.screen_origin_y})")
            print(
                f"SCALER INFO: Scale X factor (usable/ref): {self.scale_x_factor:.3f}, Scale Y factor (usable/ref): {self.scale_y_factor:.3f}")
            print(f"SCALER INFO: General Scale Factor: {self.general_scale_factor:.3f}")
            print(
                f"SCALER INFO: TileSize: {self.tile_size}, TopBarH: {self.ui_top_bar_height}, BuildMenuH: {self.ui_build_menu_height}")
            print(f"SCALER INFO: Scaled Grid Offset X (from BASE_GRID_OFFSET_X): {self.scaled_grid_offset_x}")

    def _scale_dim_floor(self, base_value):
        if base_value == 0: return 0
        scaled = base_value * self.general_scale_factor
        return max(1, int(math.floor(scaled)))

    def _scale_dim_font(self, base_value):
        if base_value == 0: return 0
        scaled = base_value * self.general_scale_factor
        return max(1, int(round(scaled)))

    def scale_value(self, base_value):
        if isinstance(base_value, (int, float)):
            return self._scale_dim_floor(base_value)
        if isinstance(base_value, (tuple, list)):
            scaled_list = [self._scale_dim_floor(v) for v in base_value]
            return tuple(scaled_list)
        return base_value

    def get_tile_size(self):
        return self.tile_size

    def get_usable_rect(self):
        return pygame.Rect(self.screen_origin_x, self.screen_origin_y, self.usable_w, self.usable_h)

    def get_center_of_usable_area(self):
        return (self.screen_origin_x + self.usable_w // 2, self.screen_origin_y + self.usable_h // 2)

    def get_scaled_ref_pos(self, ref_x, ref_y):
        actual_x = self.screen_origin_x + int(ref_x * self.scale_x_factor)
        actual_y = self.screen_origin_y + int(ref_y * self.scale_y_factor)
        return actual_x, actual_y

    def get_scaled_ref_dim(self, ref_width, ref_height):
        actual_width = self._scale_dim_floor(ref_width)
        actual_height = self._scale_dim_floor(ref_height)
        return actual_width, actual_height


# Caches
sprite_cache = {}
font_cache = {}
sound_cache = {}
# Ensure FAILSAFE_SPRITE_PATH is a valid path, e.g., taken from a known existing sprite in your assets
# This might need adjustment if your turret path or mortar_sketch.png changes.
FAILSAFE_SPRITE_PATH = os.path.join(cfg.ASSET_PATH, "turrets", "mortar_sketch.png")


def load_sprite(path, use_alpha=True):
    cache_key = path
    if cache_key in sprite_cache:
        return sprite_cache[cache_key]

    full_path = path
    image = None

    try:
        if not os.path.exists(full_path):
            # Try to construct path relative to ASSET_PATH if simple path fails
            # This is a common pattern if 'path' is just 'turrets/mortar_sketch.png'
            alt_full_path = os.path.join(cfg.ASSET_PATH, path)
            if os.path.exists(alt_full_path):
                full_path = alt_full_path
            else:
                raise FileNotFoundError(f"Sprite file not found: '{path}' or '{alt_full_path}'")
        image = pygame.image.load(full_path)
    except (pygame.error, FileNotFoundError) as e:
        if cfg.DEBUG_MODE: print(f"AVERTISSEMENT: Impossible de charger '{path}': {e}. Tentative secours.")
        try:
            if not os.path.exists(FAILSAFE_SPRITE_PATH):
                if cfg.DEBUG_MODE: print(f"ERREUR CRITIQUE: Fichier de secours '{FAILSAFE_SPRITE_PATH}' introuvable!")
                placeholder = pygame.Surface((32, 32), pygame.SRCALPHA if use_alpha else 0)
                placeholder.fill(cfg.COLOR_RED)
                pygame.draw.circle(placeholder, cfg.COLOR_YELLOW, (16, 16), 10)
                sprite_cache[cache_key] = placeholder
                return placeholder

            if FAILSAFE_SPRITE_PATH in sprite_cache:
                image = sprite_cache[FAILSAFE_SPRITE_PATH]
            else:
                img_fs = pygame.image.load(FAILSAFE_SPRITE_PATH)
                image = img_fs.convert_alpha() if use_alpha else img_fs.convert()
                sprite_cache[FAILSAFE_SPRITE_PATH] = image
        except (pygame.error, FileNotFoundError) as e_fs:
            if cfg.DEBUG_MODE: print(f"ERREUR: Échec chargement '{path}' ET secours '{FAILSAFE_SPRITE_PATH}': {e_fs}")
            ph_size = (32, 32)
            placeholder = pygame.Surface(ph_size, pygame.SRCALPHA if use_alpha else 0);
            placeholder.fill(cfg.COLOR_MAGENTA)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, 0), (ph_size[0] - 1, ph_size[1] - 1), 2)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, ph_size[1] - 1), (ph_size[0] - 1, 0), 2)
            sprite_cache[cache_key] = placeholder
            if FAILSAFE_SPRITE_PATH not in sprite_cache: sprite_cache[FAILSAFE_SPRITE_PATH] = placeholder
            return placeholder

    if image:
        if path not in sprite_cache or sprite_cache[path] is not image:
            image = image.convert_alpha() if use_alpha else image.convert()
            sprite_cache[cache_key] = image

    return sprite_cache.get(cache_key, sprite_cache.get(FAILSAFE_SPRITE_PATH))


def scale_sprite_to_tile(original_sprite, scaler: Scaler):
    if not original_sprite or not scaler: return None
    try:
        tile_w = max(1, scaler.tile_size)
        tile_h = max(1, scaler.tile_size)
        return pygame.transform.smoothscale(original_sprite, (tile_w, tile_h))
    except pygame.error as e:
        if cfg.DEBUG_MODE: print(f"ERREUR: scale_sprite_to_tile échoué: {e}")
        return original_sprite


def scale_sprite_to_size(original_sprite, target_width, target_height):
    if not original_sprite: return None
    tw, th = max(1, int(target_width)), max(1, int(target_height))
    try:
        return pygame.transform.smoothscale(original_sprite, (tw, th))
    except pygame.error as e:
        if cfg.DEBUG_MODE: print(f"ERREUR: scale_sprite_to_size échoué pour ({tw}x{th}): {e}")
        return original_sprite


def get_font(scaled_size, font_name=cfg.FONT_NAME_DEFAULT):
    safe_scaled_size = max(1, scaled_size)
    key = (font_name, safe_scaled_size)

    if key not in font_cache:
        try:
            font_cache[key] = pygame.font.Font(font_name, safe_scaled_size)
        except pygame.error:
            try:
                font_cache[key] = pygame.font.SysFont("arial", safe_scaled_size)
                if cfg.DEBUG_MODE: print(
                    f"AVERTISSEMENT: Police '{font_name}' non trouvée, utilisation de SysFont 'arial'.")
            except pygame.error:
                font_cache[key] = pygame.font.Font(None, safe_scaled_size)
                if cfg.DEBUG_MODE: print(
                    f"AVERTISSEMENT: SysFont 'arial' non trouvée, utilisation de la police Pygame par défaut.")
        except Exception as e_font:
            if cfg.DEBUG_MODE: print(
                f"ERREUR INATTENDUE: Chargement police '{font_name}' taille {safe_scaled_size}: {e_font}")
            font_cache[key] = pygame.font.Font(None, safe_scaled_size)
    return font_cache[key]


def render_text_surface(text, scaled_size, color, font_name=cfg.FONT_NAME_DEFAULT, antialias=True,
                        background_color=None):
    if scaled_size < 1:
        if cfg.DEBUG_MODE: print(
            f"AVERTISSEMENT: Tentative de rendu de texte avec taille < 1 ({scaled_size}). Ajustement à 1.")
        scaled_size = 1

    font = get_font(scaled_size, font_name)
    if not font:
        if cfg.DEBUG_MODE: print(
            f"ERREUR CRITIQUE: get_font a retourné None pour taille {scaled_size}, police {font_name}.")
        return None
    try:
        return font.render(text, antialias, color, background_color) if background_color else font.render(text,
                                                                                                          antialias,
                                                                                                          color)
    except pygame.error as e:
        if cfg.DEBUG_MODE: print(f"ERREUR: font.render échoué pour '{text}' taille {scaled_size}: {e}")
        return None
    except Exception as e_generic:
        if cfg.DEBUG_MODE: print(f"ERREUR INATTENDUE: font.render pour '{text}' taille {scaled_size}: {e_generic}")
        return None


def load_sound(path):
    if path in sound_cache: return sound_cache[path]
    full_path = path  # Assume path is already full or correctly relative
    try:
        sound = pygame.mixer.Sound(full_path)
        sound_cache[path] = sound
        return sound
    except pygame.error as e:
        if cfg.DEBUG_MODE: print(f"AVERTISSEMENT: Impossible de charger le son '{full_path}': {e}")
        return None


def play_sound(sound_object, loops=0, volume=1.0):
    if sound_object and pygame.mixer.get_init():
        sound_object.set_volume(volume)
        sound_object.play(loops)


def convert_grid_to_pixels(grid_pos_tuple, grid_origin_xy_pixels, scaler: Scaler):
    row, col = grid_pos_tuple
    tile_size = scaler.tile_size
    return (col * tile_size + grid_origin_xy_pixels[0], row * tile_size + grid_origin_xy_pixels[1])


def convert_pixels_to_grid(pixel_pos_tuple, grid_origin_xy_pixels, scaler: Scaler):
    px, py = pixel_pos_tuple
    tile_size = scaler.tile_size
    if tile_size == 0:
        if cfg.DEBUG_MODE: print("ERREUR: tile_size est 0 dans convert_pixels_to_grid.")
        return -1, -1

    relative_px = px - grid_origin_xy_pixels[0]
    relative_py = py - grid_origin_xy_pixels[1]

    grid_col = int(math.floor(relative_px / tile_size))
    grid_row = int(math.floor(relative_py / tile_size))

    return (grid_row, grid_col)


def draw_debug_rect(surface, rect, color=cfg.COLOR_RED, width=1):
    if rect and isinstance(rect, pygame.Rect):
        pygame.draw.rect(surface, color, rect, width)


def draw_debug_text(surface, text, position_xy, scaler: Scaler, color=cfg.COLOR_WHITE):
    text_surf = render_text_surface(text, scaler.font_size_small, color)
    if text_surf:
        surface.blit(text_surf, position_xy)