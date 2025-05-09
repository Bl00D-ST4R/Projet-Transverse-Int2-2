# utility_functions.py
import pygame
import os
import game_config as cfg

class Scaler:
    def __init__(self, actual_screen_width, actual_screen_height,
                 ref_width=cfg.REF_WIDTH, ref_height=cfg.REF_HEIGHT):
        self.actual_w = actual_screen_width
        self.actual_h = actual_screen_height
        self.ref_w = ref_width
        self.ref_h = ref_height

        if self.ref_w == 0 or self.ref_h == 0: # Avoid division by zero
            self.scale_x_factor = 1.0
            self.scale_y_factor = 1.0
        else:
            self.scale_x_factor = self.actual_w / self.ref_w
            self.scale_y_factor = self.actual_h / self.ref_h
        
        self.general_scale_factor = min(self.scale_x_factor, self.scale_y_factor)

        # Pre-calculate frequently used scaled dimensions
        self.tile_size = self._scale_dim(cfg.BASE_TILE_SIZE)
        self.ui_top_bar_height = self._scale_dim(cfg.BASE_UI_TOP_BAR_HEIGHT)
        self.ui_build_menu_height = self._scale_dim(cfg.BASE_UI_BUILD_MENU_HEIGHT)
        self.ui_build_menu_button_w = self._scale_dim(cfg.BASE_UI_BUILD_MENU_BUTTON_SIZE_W)
        self.ui_build_menu_button_h = self._scale_dim(cfg.BASE_UI_BUILD_MENU_BUTTON_SIZE_H)
        self.ui_build_menu_button_padding = self._scale_dim(cfg.BASE_UI_BUILD_MENU_BUTTON_PADDING)
        self.ui_icon_size_default = self._scale_dim(cfg.BASE_UI_ICON_SIZE_DEFAULT)
        self.ui_general_padding = self._scale_dim(cfg.BASE_UI_GENERAL_PADDING)
        self.grid_offset_x = self._scale_dim(cfg.BASE_GRID_OFFSET_X) # Will be 0

        self.font_size_small = self._scale_dim(cfg.BASE_FONT_SIZE_SMALL)
        self.font_size_medium = self._scale_dim(cfg.BASE_FONT_SIZE_MEDIUM)
        self.font_size_large = self._scale_dim(cfg.BASE_FONT_SIZE_LARGE)
        self.font_size_xlarge = self._scale_dim(cfg.BASE_FONT_SIZE_XLARGE)
        self.font_size_title = self._scale_dim(cfg.BASE_FONT_SIZE_TITLE)
        
        self.gravity = cfg.BASE_GRAVITY_PHYSICS * self.general_scale_factor

        if cfg.DEBUG_MODE:
            print(f"SCALER INFO: Actual Screen: {self.actual_w}x{self.actual_h}, Ref: {self.ref_w}x{self.ref_h}")
            print(f"SCALER INFO: Scale X: {self.scale_x_factor:.3f}, Scale Y: {self.scale_y_factor:.3f}, General Scale: {self.general_scale_factor:.3f}")
            print(f"SCALER INFO: TileSize: {self.tile_size}")
            print(f"SCALER INFO: TopBarH: {self.ui_top_bar_height}, BuildMenuH: {self.ui_build_menu_height}")
            print(f"SCALER INFO: Base TopBarH: {cfg.BASE_UI_TOP_BAR_HEIGHT}, Base BuildMenuH: {cfg.BASE_UI_BUILD_MENU_HEIGHT}")

    def _scale_dim(self, base_value):
        scaled = base_value * self.general_scale_factor
        return max(1, int(scaled)) if base_value != 0 else 0

    def scale_value(self, base_value):
        if isinstance(base_value, (int, float)):
            return self._scale_dim(base_value)
        if isinstance(base_value, (tuple, list)):
             scaled_list = [self._scale_dim(v) for v in base_value]
             return tuple(scaled_list)
        return base_value

    def get_tile_size(self): return self.tile_size

# Caches
sprite_cache = {}
font_cache = {}
sound_cache = {}
FAILSAFE_SPRITE_PATH = os.path.join(cfg.TURRET_SPRITE_PATH, "mortar_sketch.png")

def load_sprite(path, use_alpha=True):
    cache_key = path
    if cache_key in sprite_cache:
        return sprite_cache[cache_key]
    full_path = os.path.join(path)
    image = None
    try:
        image = pygame.image.load(full_path)
    except (pygame.error, FileNotFoundError) as e:
        if cfg.DEBUG_MODE: print(f"AVERTISSEMENT: Impossible de charger '{full_path}': {e}. Tentative secours.")
        try:
            if not os.path.exists(FAILSAFE_SPRITE_PATH):
                raise FileNotFoundError(f"FAILSAFE '{FAILSAFE_SPRITE_PATH}' introuvable!")
            if FAILSAFE_SPRITE_PATH in sprite_cache: image = sprite_cache[FAILSAFE_SPRITE_PATH]
            else:
                img_fs = pygame.image.load(FAILSAFE_SPRITE_PATH)
                image = img_fs.convert_alpha() if use_alpha else img_fs.convert()
                sprite_cache[FAILSAFE_SPRITE_PATH] = image
        except (pygame.error, FileNotFoundError) as e_fs:
            if cfg.DEBUG_MODE: print(f"ERREUR: Échec chargement '{full_path}' ET secours '{FAILSAFE_SPRITE_PATH}': {e_fs}")
            ph_size = (32,32) # Fixed small size for error placeholder
            placeholder = pygame.Surface(ph_size, pygame.SRCALPHA if use_alpha else 0); placeholder.fill(cfg.COLOR_MAGENTA)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0,0), (ph_size[0]-1, ph_size[1]-1), 2)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0,ph_size[1]-1), (ph_size[0]-1,0), 2)
            sprite_cache[cache_key] = placeholder
            if FAILSAFE_SPRITE_PATH not in sprite_cache: sprite_cache[FAILSAFE_SPRITE_PATH] = placeholder
            return placeholder
    if image and (path not in sprite_cache or sprite_cache[path] is not image):
        image = image.convert_alpha() if use_alpha else image.convert()
        sprite_cache[cache_key] = image
    return sprite_cache.get(cache_key, sprite_cache.get(FAILSAFE_SPRITE_PATH))

def scale_sprite_to_tile(original_sprite, scaler: Scaler):
    if not original_sprite or not scaler: return None
    try: return pygame.transform.scale(original_sprite, (scaler.tile_size, scaler.tile_size))
    except: return original_sprite

def scale_sprite_to_size(original_sprite, target_width, target_height):
    if not original_sprite: return None
    tw, th = max(1, int(target_width)), max(1, int(target_height))
    try: return pygame.transform.scale(original_sprite, (tw, th))
    except: return original_sprite

def get_font(scaled_size, font_name=cfg.FONT_NAME_DEFAULT):
    key = (font_name, scaled_size)
    if key not in font_cache:
        try: font_cache[key] = pygame.font.Font(font_name, scaled_size)
        except:
            try: font_cache[key] = pygame.font.SysFont("arial", scaled_size)
            except: font_cache[key] = pygame.font.Font(None, scaled_size)
    return font_cache[key]

def render_text_surface(text, scaled_size, color, font_name=cfg.FONT_NAME_DEFAULT, antialias=True, background_color=None):
    font = get_font(scaled_size, font_name)
    try: return font.render(text, antialias, color, background_color) if background_color else font.render(text, antialias, color)
    except pygame.error as e:
        if cfg.DEBUG_MODE: print(f"ERREUR: font.render échoué pour '{text}' taille {scaled_size}: {e}")
        return None
    except Exception as e_generic:
        if cfg.DEBUG_MODE: print(f"ERREUR INATTENDUE: font.render pour '{text}' taille {scaled_size}: {e_generic}")
        return None

def load_sound(path): # Inchangé
    if path in sound_cache: return sound_cache[path]
    full_path = os.path.join(path)
    try:
        sound = pygame.mixer.Sound(full_path); sound_cache[path] = sound; return sound
    except: return None
def play_sound(sound_object, loops=0, volume=1.0): # Inchangé
    if sound_object and pygame.mixer.get_init(): sound_object.set_volume(volume); sound_object.play(loops)

def convert_grid_to_pixels(grid_pos_tuple, grid_origin_xy_pixels, scaler: Scaler):
    row, col = grid_pos_tuple
    tile_size = scaler.tile_size
    return (col * tile_size + grid_origin_xy_pixels[0], row * tile_size + grid_origin_xy_pixels[1])

def convert_pixels_to_grid(pixel_pos_tuple, grid_origin_xy_pixels, scaler: Scaler):
    px, py = pixel_pos_tuple
    tile_size = scaler.tile_size
    if tile_size == 0: return -1, -1
    relative_px = px - grid_origin_xy_pixels[0]
    relative_py = py - grid_origin_xy_pixels[1]
    if relative_px < 0 or relative_py < 0: return -1, -1
    return (int(relative_py // tile_size), int(relative_px // tile_size))

def draw_debug_rect(surface, rect, color=cfg.COLOR_RED, width=1):
    if rect: pygame.draw.rect(surface, color, rect, width)

def draw_debug_text(surface, text, position_xy, scaler: Scaler, color=cfg.COLOR_WHITE):
    text_surf = render_text_surface(text, scaler.font_size_small, color)
    if text_surf: surface.blit(text_surf, position_xy)
