# utility_functions.py
import pygame
import os
import game_config as cfg

# --- Scaler Class ---
class Scaler:
    def __init__(self, actual_screen_width, actual_screen_height, ref_width=cfg.REF_WIDTH, ref_height=cfg.REF_HEIGHT):
        self.actual_w = actual_screen_width
        self.actual_h = actual_screen_height
        self.ref_w = ref_width
        self.ref_h = ref_height

        self.scale_x = self.actual_w / self.ref_w
        self.scale_y = self.actual_h / self.ref_h
        
        # Choose scaling strategy (min preserves aspect ratio)
        self.general_scale = min(self.scale_x, self.scale_y)
        # Alternative: self.general_scale = self.scale_x # Might stretch height

        # Calculate runtime scaled values frequently needed
        self.tile_size = self.scale_value(cfg.BASE_TILE_SIZE)
        self.ui_top_bar_height = self.scale_value(cfg.BASE_UI_TOP_BAR_HEIGHT)
        self.ui_build_menu_height = self.scale_value(cfg.BASE_UI_BUILD_MENU_HEIGHT)
        
        # Pre-calculate font sizes
        self.font_size_small = self.scale_value(cfg.BASE_FONT_SIZE_SMALL)
        self.font_size_medium = self.scale_value(cfg.BASE_FONT_SIZE_MEDIUM)
        self.font_size_large = self.scale_value(cfg.BASE_FONT_SIZE_LARGE)
        self.font_size_xlarge = self.scale_value(cfg.BASE_FONT_SIZE_XLARGE)
        self.font_size_title = self.scale_value(cfg.BASE_FONT_SIZE_TITLE)

        print(f"INFO: Scaler initialized. Screen: {self.actual_w}x{self.actual_h}, Ref: {self.ref_w}x{self.ref_h}, General Scale: {self.general_scale:.3f}")


    def scale_value(self, base_value):
        """Applique general_scale à une valeur numérique ou à un tuple/liste."""
        if isinstance(base_value, (int, float)):
            # Ensure minimum value of 1 pixel after scaling unless base_value is 0
            scaled = base_value * self.general_scale
            return max(1, int(scaled)) if base_value != 0 else 0
        if isinstance(base_value, (tuple, list)):
            # Scale each element, ensuring minimum 1 unless original is 0
             scaled_list = [max(1, int(v * self.general_scale)) if v != 0 else 0 for v in base_value]
             return tuple(scaled_list)
        return base_value # Return original if not scalable type

    def get_tile_size(self):
        return self.tile_size

    def get_font_size(self, base_font_size_key):
        # Example: get_font_size(cfg.BASE_FONT_SIZE_MEDIUM) -> returns the scaled medium size
        # Direct access like self.font_size_medium might be simpler now.
        if base_font_size_key == cfg.BASE_FONT_SIZE_SMALL: return self.font_size_small
        if base_font_size_key == cfg.BASE_FONT_SIZE_MEDIUM: return self.font_size_medium
        if base_font_size_key == cfg.BASE_FONT_SIZE_LARGE: return self.font_size_large
        if base_font_size_key == cfg.BASE_FONT_SIZE_XLARGE: return self.font_size_xlarge
        if base_font_size_key == cfg.BASE_FONT_SIZE_TITLE: return self.font_size_title
        return self.scale_value(base_font_size_key) # Fallback if needed

# --- Cache pour les ressources chargées ---
sprite_cache = {}
font_cache = {}
sound_cache = {}

# --- Constante pour le Sprite de Secours ---
FAILSAFE_SPRITE_PATH = os.path.join(cfg.TURRET_SPRITE_PATH, "mortar_sketch.png")
# Assurez-vous que ce fichier mortar_sketch.png existe bien dans assets/turrets/

# --- Chargement et Gestion des Sprites ---
def load_sprite(path, use_alpha=True):
    """
    Charge un sprite depuis le chemin donné.
    Utilise un cache pour éviter de recharger les mêmes images.
    Si le sprite n'est pas trouvé (FileNotFoundError) ou si une erreur Pygame survient,
    tente de charger le sprite de secours (FAILSAFE_SPRITE_PATH).
    """
    cache_key = path
    if cache_key in sprite_cache:
        return sprite_cache[cache_key]

    full_path = os.path.join(path)
    image = None

    try:
        image = pygame.image.load(full_path)
    except (pygame.error, FileNotFoundError) as e:
        print(f"AVERTISSEMENT: Impossible de charger le sprite '{full_path}': {e}. Tentative avec le sprite de secours.")
        try:
            if not os.path.exists(FAILSAFE_SPRITE_PATH):
                raise FileNotFoundError(f"Le fichier sprite de secours '{FAILSAFE_SPRITE_PATH}' est aussi introuvable!")
            
            if FAILSAFE_SPRITE_PATH in sprite_cache: # Check if failsafe itself is already cached
                image = sprite_cache[FAILSAFE_SPRITE_PATH]
            else: # Load and cache failsafe
                failsafe_image_loaded = pygame.image.load(FAILSAFE_SPRITE_PATH)
                if use_alpha:
                    image = failsafe_image_loaded.convert_alpha()
                else:
                    image = failsafe_image_loaded.convert()
                sprite_cache[FAILSAFE_SPRITE_PATH] = image # Cache the converted failsafe sprite
        except (pygame.error, FileNotFoundError) as e_failsafe:
            print(f"ERREUR FATALE: Impossible de charger le sprite '{full_path}' ET le sprite de secours '{FAILSAFE_SPRITE_PATH}': {e_failsafe}")
            # MODIFIED: Use fixed placeholder size
            placeholder_size = (32, 32) 
            placeholder = pygame.Surface(placeholder_size, pygame.SRCALPHA if use_alpha else 0)
            placeholder.fill(cfg.COLOR_MAGENTA)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, 0), (placeholder_size[0]-1, placeholder_size[1]-1), 3)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, placeholder_size[1]-1), (placeholder_size[0]-1, 0), 3)
            sprite_cache[cache_key] = placeholder # Cache the placeholder for the original failed path
            if FAILSAFE_SPRITE_PATH not in sprite_cache: # Also cache placeholder for failsafe path if it also failed
                 sprite_cache[FAILSAFE_SPRITE_PATH] = placeholder
            return placeholder

    # This conversion block should only apply if 'image' was successfully loaded from 'full_path'
    # and not from the failsafe loading logic above (which already converts and caches).
    if image and (path not in sprite_cache or sprite_cache[path] is not image):
        if use_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        sprite_cache[cache_key] = image

    return sprite_cache.get(cache_key, sprite_cache.get(FAILSAFE_SPRITE_PATH))


# MODIFIED: Ces fonctions nécessitent maintenant le scaler pour les dimensions runtime
def scale_sprite_to_tile(original_sprite, scaler: Scaler):
    if not original_sprite or not scaler: return None
    try:
        tile_size = scaler.get_tile_size() # Obtenir la taille de tuile runtime
        return pygame.transform.scale(original_sprite, (tile_size, tile_size))
    except Exception as e:
        print(f"ERREUR: Mise à l'échelle vers TILE_SIZE échouée: {e}")
        return original_sprite

def scale_sprite_to_size(original_sprite, target_width, target_height):
    # Cette fonction prend déjà les dimensions cibles, pas besoin de scaler ici
    if not original_sprite: return None
    tw = max(1, int(target_width))
    th = max(1, int(target_height))
    try:
        return pygame.transform.scale(original_sprite, (tw, th))
    except Exception as e:
        print(f"ERREUR: Mise à l'échelle vers ({tw},{th}) échouée: {e}")
        return original_sprite

# Polices: get_font utilise maintenant la taille pré-scalée du scaler
def get_font(scaled_size, font_name=cfg.FONT_NAME_DEFAULT):
    key = (font_name, scaled_size) # La taille est déjà scalée
    if key not in font_cache:
        try:
            font_cache[key] = pygame.font.Font(font_name, scaled_size)
        except Exception as e: # Simplified error logging from prompt
            print(f"AVERTISSEMENT: Police '{font_name}' taille {scaled_size} non trouvée, fallback Arial. Erreur: {e}")
            try:
                font_cache[key] = pygame.font.SysFont("arial", scaled_size)
            except Exception as e_sysfont:
                print(f"ERREUR FATALE: Impossible de charger la police système Arial {scaled_size}. Erreur: {e_sysfont}")
                font_cache[key] = pygame.font.Font(None, scaled_size) # Pygame's default font
    return font_cache[key]

# render_text_surface prend aussi une taille déjà scalée
def render_text_surface(text, scaled_size, color, font_name=cfg.FONT_NAME_DEFAULT, antialias=True, background_color=None):
    font = get_font(scaled_size, font_name)
    try:
        if background_color:
            return font.render(text, antialias, color, background_color)
        else:
            return font.render(text, antialias, color)
    except pygame.error as e: # Catch specific pygame error for rendering
        print(f"ERREUR: font.render a échoué pour '{text}' taille {scaled_size}: {e}")
        return None # Retourner None si le rendu échoue
    except Exception as e_generic: # Catch any other unexpected error during render
        print(f"ERREUR INATTENDUE: font.render pour '{text}' taille {scaled_size}: {e_generic}")
        return None


# --- Chargement et Gestion des Sons (Basique) ---
def load_sound(path):
    if path in sound_cache:
        return sound_cache[path]

    full_path = os.path.join(path)
    try:
        sound = pygame.mixer.Sound(full_path)
        sound_cache[path] = sound
        return sound
    except pygame.error as e:
        print(f"ERREUR: Impossible de charger le son '{full_path}': {e}")
        return None

def play_sound(sound_object, loops=0, volume=1.0):
    if sound_object and pygame.mixer.get_init():
        sound_object.set_volume(volume)
        sound_object.play(loops)
    elif not pygame.mixer.get_init():
        print("AVERTISSEMENT: Tentative de jouer un son alors que pygame.mixer n'est pas initialisé.")

# --- Fonctions de Grille (MODIFIÉES pour utiliser scaler) ---
def convert_grid_to_pixels(grid_pos_tuple, grid_origin_xy_pixels, scaler: Scaler):
    row, col = grid_pos_tuple
    tile_size = scaler.get_tile_size() # Taille runtime
    return (col * tile_size + grid_origin_xy_pixels[0],
            row * tile_size + grid_origin_xy_pixels[1])

def convert_pixels_to_grid(pixel_pos_tuple, grid_origin_xy_pixels, scaler: Scaler):
    px, py = pixel_pos_tuple
    tile_size = scaler.get_tile_size()

    if tile_size == 0: return -1, -1 # Eviter division par zéro

    relative_px = px - grid_origin_xy_pixels[0]
    relative_py = py - grid_origin_xy_pixels[1]

    if relative_px < 0 or relative_py < 0: # Click is outside the grid's top-left boundary
        return -1, -1

    grid_col = int(relative_px // tile_size) # Utiliser int() explicitement
    grid_row = int(relative_py // tile_size)

    return grid_row, grid_col

# --- Utilitaires de Dessin ---
def draw_debug_rect(surface, rect, color=cfg.COLOR_RED, width=1):
    if rect:
        pygame.draw.rect(surface, color, rect, width)

def draw_debug_text(surface, text, position_xy, scaler: Scaler, color=cfg.COLOR_WHITE):
    # Utilise FONT_SIZE_SMALL scalée
    text_surf = render_text_surface(text, scaler.font_size_small, color)
    if text_surf:
        surface.blit(text_surf, position_xy)

# --- Fonctions Mathématiques (si besoin plus tard) ---
# (No functions here in original or target)
