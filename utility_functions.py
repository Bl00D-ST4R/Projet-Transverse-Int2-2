# utility_functions.py
import pygame
import os
import game_config as cfg # Contient les valeurs scalées et les chemins

# --- Cache pour les ressources chargées ---
sprite_cache = {}
font_cache = {}
sound_cache = {} # Ajout pour les sons

# --- Constante pour le Sprite de Secours ---
# MODIFIABLE: Chemin vers le sprite à utiliser si un autre n'est pas trouvé.
# Assurez-vous que ce fichier existe !
FAILSAFE_SPRITE_PATH = os.path.join(cfg.TURRET_SPRITE_PATH, "mortar_sketch.png") 
# Alternative: un sprite plus générique ou un placeholder dédié aux erreurs
# FAILSAFE_SPRITE_PATH = os.path.join(cfg.UI_SPRITE_PATH, "error_placeholder.png") 

# --- Chargement et Gestion des Sprites ---
def load_sprite(path, use_alpha=True):
    """
    Charge un sprite depuis le chemin donné.
    Utilise un cache pour éviter de recharger les mêmes images.
    Si le sprite n'est pas trouvé, tente de charger le sprite de secours (FAILSAFE_SPRITE_PATH).
    """
    # Clé pour le cache basée sur le chemin demandé
    cache_key = path
    if cache_key in sprite_cache:
        return sprite_cache[cache_key]
    
    full_path = os.path.join(path) 
    image = None # Initialiser à None

    try:
        image = pygame.image.load(full_path)
        print(f"INFO: Sprite chargé avec succès: '{full_path}'") # Message de succès
    except pygame.error as e:
        print(f"AVERTISSEMENT: Impossible de charger le sprite '{full_path}': {e}. Tentative avec le sprite de secours.")
        # Essayer de charger le sprite de secours
        try:
            # Utiliser une clé de cache différente pour le failsafe pour ne pas écraser
            # le cache de la requête originale si le failsafe est demandé directement plus tard.
            if FAILSAFE_SPRITE_PATH in sprite_cache:
                image = sprite_cache[FAILSAFE_SPRITE_PATH]
            else:
                failsafe_image_loaded = pygame.image.load(FAILSAFE_SPRITE_PATH)
                # Convertir le failsafe immédiatement s'il est chargé pour la première fois
                if use_alpha:
                    image = failsafe_image_loaded.convert_alpha()
                else:
                    image = failsafe_image_loaded.convert()
                sprite_cache[FAILSAFE_SPRITE_PATH] = image # Mettre en cache le failsafe traité
            print(f"INFO: Sprite de secours '{FAILSAFE_SPRITE_PATH}' chargé pour remplacer '{path}'.")
        except pygame.error as e_failsafe:
            print(f"ERREUR FATALE: Impossible de charger le sprite '{full_path}' ET le sprite de secours '{FAILSAFE_SPRITE_PATH}': {e_failsafe}")
            # Si même le failsafe échoue, on crée un placeholder simple pour éviter un crash total.
            placeholder_size = (cfg.TILE_SIZE, cfg.TILE_SIZE)
            placeholder = pygame.Surface(placeholder_size, pygame.SRCALPHA if use_alpha else 0) # Respecter use_alpha
            placeholder.fill(cfg.COLOR_MAGENTA) # Magenta vif pour indiquer une double erreur
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, 0), (placeholder_size[0]-1, placeholder_size[1]-1), 3)
            pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, placeholder_size[1]-1), (placeholder_size[0]-1, 0), 3)
            
            # Mettre en cache le placeholder pour le chemin original
            sprite_cache[cache_key] = placeholder 
            # Si le failsafe lui-même a échoué, son entrée de cache (si elle existait) reste,
            # ou si FAILSAFE_SPRITE_PATH n'était pas dans le cache, il ne le sera pas avec le placeholder.
            # C'est ok, car le placeholder est retourné pour la requête originale.
            return placeholder

    # Si l'image (originale ou failsafe) a été chargée avec succès et n'est pas encore convertie (cas original)
    if image:
        # Si 'image' est le failsafe déjà converti, cette conversion est redondante mais inoffensive.
        # Pour éviter la double conversion, on pourrait avoir un flag ou vérifier si c'est l'instance du cache.
        # Simplification : on assume que si `image` vient du premier try, il n'est pas converti.
        # Si `image` vient du cache de `FAILSAFE_SPRITE_PATH`, il est déjà converti.
        # On peut vérifier si `image` est déjà dans `sprite_cache.values()` pour voir s'il vient du cache.
        # Mais une reconversion alpha sur une image déjà alpha est généralement ok.
        if path not in sprite_cache or sprite_cache[path] is not image: # Eviter reconversion si c'est le failsafe du cache
            if use_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
        
        sprite_cache[cache_key] = image
        return image
    else:
        # Ce bloc ne devrait théoriquement pas être atteint si le placeholder est créé dans le `except e_failsafe`.
        print(f"ERREUR INATTENDUE: Aucune image n'a pu être assignée pour '{full_path}'.")
        # Création d'un placeholder ultime si on arrive ici par un chemin non prévu.
        placeholder_size = (cfg.TILE_SIZE, cfg.TILE_SIZE)
        ultimate_placeholder = pygame.Surface(placeholder_size, pygame.SRCALPHA if use_alpha else 0)
        ultimate_placeholder.fill(cfg.COLOR_BLACK) # Noir pour indiquer une erreur très grave
        sprite_cache[cache_key] = ultimate_placeholder
        return ultimate_placeholder

def scale_sprite_to_tile(original_sprite):
    """Met à l'échelle un sprite pour qu'il corresponde à cfg.TILE_SIZE."""
    if not original_sprite: return None
    try:
        return pygame.transform.scale(original_sprite, (cfg.TILE_SIZE, cfg.TILE_SIZE))
    except Exception as e:
        print(f"ERREUR: Mise à l'échelle du sprite vers TILE_SIZE échouée: {e}")
        return original_sprite # Retourne l'original si erreur

def scale_sprite_to_size(original_sprite, target_width, target_height):
    """Met à l'échelle un sprite à une largeur et hauteur spécifiques."""
    if not original_sprite: return None
    # S'assurer que target_width et target_height sont des entiers > 0
    tw = max(1, int(target_width))
    th = max(1, int(target_height))
    try:
        return pygame.transform.scale(original_sprite, (tw, th))
    except Exception as e:
        print(f"ERREUR: Mise à l'échelle du sprite vers ({tw},{th}) échouée: {e}")
        return original_sprite

# --- Chargement et Gestion des Polices ---
def get_font(size, font_name=cfg.FONT_NAME_DEFAULT):
    """
    Récupère une police de la taille spécifiée, avec gestion de cache.
    `size` est déjà la taille scalée (ex: cfg.FONT_SIZE_MEDIUM).
    """
    key = (font_name, size)
    if key not in font_cache:
        try:
            # Si font_name est None, pygame.font.Font utilise la police système par défaut.
            font_cache[key] = pygame.font.Font(font_name, size)
        except Exception as e:
            print(f"AVERTISSEMENT: Impossible de charger la police '{font_name}' en taille {size}. Utilisation d'Arial. Erreur: {e}")
            # Fallback vers une police système courante si l'autre échoue
            try:
                font_cache[key] = pygame.font.SysFont("arial", size)
            except Exception as e_sysfont:
                print(f"ERREUR FATALE: Impossible de charger la police système Arial. Erreur: {e_sysfont}")
                # Fallback ultime si SysFont échoue aussi (très rare)
                font_cache[key] = pygame.font.Font(None, size) # Police Pygame par défaut
    return font_cache[key]

def render_text_surface(text, size, color, font_name=cfg.FONT_NAME_DEFAULT, antialias=True, background_color=None):
    """
    Crée une surface Pygame avec le texte rendu.
    `size` est la taille déjà scalée.
    """
    font = get_font(size, font_name)
    if background_color:
        return font.render(text, antialias, color, background_color)
    else:
        return font.render(text, antialias, color)

# --- Chargement et Gestion des Sons (Basique) ---
def load_sound(path):
    """Charge un son, avec gestion de cache."""
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
    """Joue un objet Sound chargé, si disponible."""
    if sound_object and pygame.mixer.get_init(): 
        sound_object.set_volume(volume)
        sound_object.play(loops)
    elif not pygame.mixer.get_init():
        print("AVERTISSEMENT: Tentative de jouer un son alors que pygame.mixer n'est pas initialisé.")


# --- Fonctions de Grille (utilisent les valeurs scalées de cfg) ---
def convert_grid_to_pixels(grid_pos_tuple, grid_origin_xy_pixels):
    """
    Convertit les coordonnées de grille (row, col) en coordonnées pixels (x,y) du coin sup gauche de la case.
    `grid_origin_xy_pixels` est le coin supérieur gauche de la case (0,0) de la grille.
    """
    row, col = grid_pos_tuple
    return (col * cfg.TILE_SIZE + grid_origin_xy_pixels[0], 
            row * cfg.TILE_SIZE + grid_origin_xy_pixels[1])

def convert_pixels_to_grid(pixel_pos_tuple, grid_origin_xy_pixels):
    """
    Convertit les coordonnées pixels (x,y) en coordonnées de grille (row, col).
    `grid_origin_xy_pixels` est le coin supérieur gauche de la case (0,0) de la grille.
    """
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
    """Dessine le contour d'un rectangle pour le débogage, si le rect est valide."""
    if rect: 
        pygame.draw.rect(surface, color, rect, width)

def draw_debug_text(surface, text, position_xy, size=cfg.FONT_SIZE_SMALL, color=cfg.COLOR_WHITE):
    """Affiche un texte de débogage simple à une position donnée."""
    text_surf = render_text_surface(text, size, color)
    surface.blit(text_surf, position_xy)

# --- Fonctions Mathématiques (si besoin plus tard) ---
# Exemple:
# def clamp(value, min_val, max_val):
#     return max(min_val, min(value, max_val))

# def distance_sq(pos1_xy, pos2_xy):
#     return (pos1_xy[0] - pos2_xy[0])**2 + (pos1_xy[1] - pos2_xy[1])**2

# def distance(pos1_xy, pos2_xy):
#     return ((pos1_xy[0] - pos2_xy[0])**2 + (pos1_xy[1] - pos2_xy[1])**2)**0.5

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init() 
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Test Utility Functions")

    print(f"TILE_SIZE configuré: {cfg.TILE_SIZE}")
    # GRID_OFFSET_Y est dynamique, donc pour le test on peut utiliser une valeur fixe ou 0
    test_grid_offset_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - (cfg.GRID_INITIAL_HEIGHT_TILES * cfg.TILE_SIZE) - cfg.GRID_BOTTOM_PADDING
    print(f"GRID_OFFSET_X: {cfg.GRID_OFFSET_X}, Test GRID_OFFSET_Y: {test_grid_offset_y}")


    try:
        # Utiliser un chemin qui existe ou le failsafe pour le test
        test_sprite_path = os.path.join(cfg.BUILDING_SPRITE_PATH, "frame.png") 
        if not os.path.exists(test_sprite_path):
            test_sprite_path = FAILSAFE_SPRITE_PATH # Tenter avec le failsafe si frame.png n'existe pas
        
        print(f"Tentative de chargement du sprite de test : {test_sprite_path}")
        test_sprite_orig = load_sprite(test_sprite_path) # Doit utiliser la nouvelle logique

        test_sprite_scaled_tile = scale_sprite_to_tile(test_sprite_orig)
        test_sprite_custom_scaled = scale_sprite_to_size(test_sprite_orig, cfg.scale_value(50), cfg.scale_value(70))
        
        print(f"Sprite original chargé (peut être le failsafe): {test_sprite_orig.get_size() if test_sprite_orig else 'Erreur/Placeholder'}")
        if test_sprite_orig and test_sprite_orig.get_width() > 0 and test_sprite_orig.get_height() > 0: # S'assurer que c'est une surface valide
            print(f"Sprite scalé TILE: {test_sprite_scaled_tile.get_size() if test_sprite_scaled_tile else 'Erreur'}")
            print(f"Sprite scalé custom: {test_sprite_custom_scaled.get_size() if test_sprite_custom_scaled else 'Erreur'}")
        else:
            print("Le sprite de test (ou son failsafe/placeholder) n'a pas pu être chargé correctement.")

    except Exception as e_test:
        print(f"Erreur dans le test de sprite: {e_test}")


    test_text_surf = render_text_surface("Test Utility", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
    print(f"Surface de texte créée: {test_text_surf.get_size() if test_text_surf else 'Erreur'}")

    try:
        # Pour le son, assurez-vous d'avoir un fichier .wav ou .ogg valide
        # dummy_sound_path = os.path.join(cfg.SOUND_PATH, "your_test_sound.wav") 
        # if os.path.exists(dummy_sound_path):
        #     test_sound = load_sound(dummy_sound_path)
        #     if test_sound:
        #         print(f"Son chargé. Essayez de le jouer.")
        #         play_sound(test_sound)
        #     else:
        #         print("Chargement du son de test échoué.")
        # else:
        #     print(f"Fichier son de test non trouvé à {dummy_sound_path}.")
        print("Test de son désactivé (décommentez et fournissez un fichier si besoin).")
    except Exception as e_sound_test:
        print(f"Erreur dans le test de son: {e_sound_test}")


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
        if test_sprite_scaled_tile: # Devrait être le sprite chargé ou son failsafe/placeholder
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
