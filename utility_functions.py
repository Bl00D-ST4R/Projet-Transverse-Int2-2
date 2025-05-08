# utility_functions.py
import pygame
import os
import game_config as cfg 

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
        # print(f"INFO: Sprite chargé avec succès: '{full_path}'") # Peut devenir bruyant
    # CORRECTION: Attraper FileNotFoundError et pygame.error
    except (pygame.error, FileNotFoundError) as e: 
        print(f"AVERTISSEMENT: Impossible de charger le sprite '{full_path}': {e}. Tentative avec le sprite de secours.")
        # Essayer de charger le sprite de secours
        try:
            if FAILSAFE_SPRITE_PATH in sprite_cache:
                image = sprite_cache[FAILSAFE_SPRITE_PATH]
            else:
                # S'assurer que le fichier failsafe existe avant de charger
                if not os.path.exists(FAILSAFE_SPRITE_PATH):
                     raise FileNotFoundError(f"Le fichier sprite de secours '{FAILSAFE_SPRITE_PATH}' est aussi introuvable!")
                
                failsafe_image_loaded = pygame.image.load(FAILSAFE_SPRITE_PATH)
                if use_alpha:
                    image = failsafe_image_loaded.convert_alpha()
                else:
                    image = failsafe_image_loaded.convert()
                sprite_cache[FAILSAFE_SPRITE_PATH] = image 
            # print(f"INFO: Sprite de secours '{FAILSAFE_SPRITE_PATH}' chargé pour remplacer '{path}'.") # Optionnel
        except (pygame.error, FileNotFoundError) as e_failsafe: # Attraper aussi FileNotFoundError pour le failsafe
            print(f"ERREUR FATALE: Impossible de charger le sprite '{full_path}' ET le sprite de secours '{FAILSAFE_SPRITE_PATH}': {e_failsafe}")
            placeholder_size = (cfg.TILE_SIZE, cfg.TILE_SIZE)
            placeholder = pygame.Surface(placeholder_size, pygame.SRCALPHA if use_alpha else 0) 
            placeholder.fill(cfg.COLOR_MAGENTA) 
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, 0), (placeholder_size[0]-1, placeholder_size[1]-1), 3)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, placeholder_size[1]-1), (placeholder_size[0]-1, 0), 3)
            sprite_cache[cache_key] = placeholder 
            if FAILSAFE_SPRITE_PATH not in sprite_cache: # Si le failsafe a échoué, mettre son placeholder aussi
                 sprite_cache[FAILSAFE_SPRITE_PATH] = placeholder
            return placeholder

    # Conversion si l'image originale a été chargée avec succès
    # et n'est pas déjà le sprite de secours récupéré du cache (qui est déjà converti)
    if image and (sprite_cache.get(path) is not image): # Vérifie si l'image est différente de ce qui pourrait déjà être dans le cache pour ce chemin (évite double conversion)
        if use_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        sprite_cache[cache_key] = image # Mettre en cache l'image traitée (originale ou secours si premier chargement)

    # Retourner l'image (originale, secours, ou placeholder)
    # Si image est None à ce stade (ne devrait pas arriver avec les placeholders), .get fournira un fallback
    return sprite_cache.get(cache_key, sprite_cache.get(FAILSAFE_SPRITE_PATH)) # Fallback au failsafe du cache si cache_key est vide

def scale_sprite_to_tile(original_sprite):
    """Met à l'échelle un sprite pour qu'il corresponde à cfg.TILE_SIZE."""
    if not original_sprite: return None
    try:
        return pygame.transform.scale(original_sprite, (cfg.TILE_SIZE, cfg.TILE_SIZE))
    except Exception as e:
        print(f"ERREUR: Mise à l'échelle du sprite vers TILE_SIZE échouée: {e}")
        return original_sprite

def scale_sprite_to_size(original_sprite, target_width, target_height):
    """Met à l'échelle un sprite à une largeur et hauteur spécifiques."""
    if not original_sprite: return None
    tw = max(1, int(target_width))
    th = max(1, int(target_height))
    try:
        return pygame.transform.scale(original_sprite, (tw, th))
    except Exception as e:
        print(f"ERREUR: Mise à l'échelle du sprite vers ({tw},{th}) échouée: {e}")
        return original_sprite

# --- Chargement et Gestion des Polices ---
def get_font(size, font_name=cfg.FONT_NAME_DEFAULT):
    key = (font_name, size)
    if key not in font_cache:
        try:
            font_cache[key] = pygame.font.Font(font_name, size)
        except Exception as e:
            print(f"AVERTISSEMENT: Impossible de charger la police '{font_name}' en taille {size}. Utilisation d'Arial. Erreur: {e}")
            try:
                font_cache[key] = pygame.font.SysFont("arial", size)
            except Exception as e_sysfont:
                print(f"ERREUR FATALE: Impossible de charger la police système Arial. Erreur: {e_sysfont}")
                font_cache[key] = pygame.font.Font(None, size) 
    return font_cache[key]

def render_text_surface(text, size, color, font_name=cfg.FONT_NAME_DEFAULT, antialias=True, background_color=None):
    font = get_font(size, font_name)
    if background_color:
        return font.render(text, antialias, color, background_color)
    else:
        return font.render(text, antialias, color)

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

# --- Fonctions de Grille (utilisent les valeurs scalées de cfg) ---
def convert_grid_to_pixels(grid_pos_tuple, grid_origin_xy_pixels):
    row, col = grid_pos_tuple
    return (col * cfg.TILE_SIZE + grid_origin_xy_pixels[0], 
            row * cfg.TILE_SIZE + grid_origin_xy_pixels[1])

def convert_pixels_to_grid(pixel_pos_tuple, grid_origin_xy_pixels):
    px, py = pixel_pos_tuple
    relative_px = px - grid_origin_xy_pixels[0]
    relative_py = py - grid_origin_xy_pixels[1]
    
    if relative_px < 0 or relative_py < 0:
        return -1, -1 

    grid_col = relative_px // cfg.TILE_SIZE
    grid_row = relative_py // cfg.TILE_SIZE
    
    return grid_row, grid_col

# --- Utilitaires de Dessin ---
def draw_debug_rect(surface, rect, color=cfg.COLOR_RED, width=1):
    if rect: 
        pygame.draw.rect(surface, color, rect, width)

def draw_debug_text(surface, text, position_xy, size=cfg.FONT_SIZE_SMALL, color=cfg.COLOR_WHITE):
    text_surf = render_text_surface(text, size, color)
    surface.blit(text_surf, position_xy)

# --- Fonctions Mathématiques (si besoin plus tard) ---

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init() 
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Test Utility Functions")

    print(f"TILE_SIZE configuré: {cfg.TILE_SIZE}")
    test_grid_offset_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - (cfg.GRID_INITIAL_HEIGHT_TILES * cfg.TILE_SIZE) - cfg.GRID_BOTTOM_PADDING
    print(f"GRID_OFFSET_X: {cfg.GRID_OFFSET_X}, Test GRID_OFFSET_Y: {test_grid_offset_y}")

    try:
        test_sprite_path = os.path.join(cfg.BUILDING_SPRITE_PATH, "frame.png") 
        if not os.path.exists(test_sprite_path):
            print(f"AVERTISSEMENT: Le fichier de test '{test_sprite_path}' n'existe pas. Tentative avec le failsafe.")
            test_sprite_path = FAILSAFE_SPRITE_PATH
        
        print(f"Tentative de chargement du sprite de test : {test_sprite_path}")
        test_sprite_orig = load_sprite(test_sprite_path)

        test_sprite_scaled_tile = scale_sprite_to_tile(test_sprite_orig)
        test_sprite_custom_scaled = scale_sprite_to_size(test_sprite_orig, cfg.scale_value(50), cfg.scale_value(70))
        
        if test_sprite_orig and test_sprite_orig.get_width() > 0 and test_sprite_orig.get_height() > 0:
             print(f"Sprite de test chargé (peut être le failsafe/placeholder): {test_sprite_orig.get_size()}")
             print(f"Sprite scalé TILE: {test_sprite_scaled_tile.get_size() if test_sprite_scaled_tile else 'Erreur'}")
             print(f"Sprite scalé custom: {test_sprite_custom_scaled.get_size() if test_sprite_custom_scaled else 'Erreur'}")
        else:
            print("Le sprite de test (ou son failsafe/placeholder) n'a pas pu être chargé correctement ou est invalide.")

    except Exception as e_test:
        print(f"Erreur dans le test de sprite: {e_test}")

    test_text_surf = render_text_surface("Test Utility", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
    print(f"Surface de texte créée: {test_text_surf.get_size() if test_text_surf else 'Erreur'}")

    print("Test de son désactivé (décommentez et fournissez un fichier si besoin).")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                grid_origin_runtime = (cfg.GRID_OFFSET_X, test_grid_offset_y) 
                grid_r, grid_c = convert_pixels_to_grid(event.pos, grid_origin_runtime)
                pixel_x, pixel_y = convert_grid_to_pixels((grid_r, grid_c), grid_origin_runtime)
                print(f"Clic à {event.pos} -> Grille ({grid_r}, {grid_c}) -> Pixel d'origine de case ({pixel_x}, {pixel_y})")

        screen.fill(cfg.COLOR_BLACK)
        if test_text_surf:
            screen.blit(test_text_surf, (cfg.scale_value(50), cfg.scale_value(50)))
        if test_sprite_scaled_tile: 
            screen.blit(test_sprite_scaled_tile, (cfg.scale_value(100),cfg.scale_value(100)))
        
        grid_origin_test_draw = (cfg.GRID_OFFSET_X, test_grid_offset_y)
        for r in range(cfg.GRID_INITIAL_HEIGHT_TILES):
            for c in range(cfg.GRID_INITIAL_WIDTH_TILES):
                px, py = convert_grid_to_pixels((r,c), grid_origin_test_draw)
                rect = pygame.Rect(px, py, cfg.TILE_SIZE, cfg.TILE_SIZE)
                draw_debug_rect(screen, rect, cfg.COLOR_GREY_MEDIUM)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()
