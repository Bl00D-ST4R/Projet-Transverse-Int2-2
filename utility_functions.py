# utility_func.py
import pygame
import os
import game_config as cfg # Contient les valeurs scalées et les chemins

# --- Cache pour les ressources chargées ---
sprite_cache = {}
font_cache = {}
sound_cache = {} # Ajout pour les sons

# --- Chargement et Gestion des Sprites ---
def load_sprite(path, use_alpha=True):
    """
    Charge un sprite depuis le chemin donné.
    Utilise un cache pour éviter de recharger les mêmes images.
    La mise à l'échelle est gérée au niveau de l'objet ou du dessin.
    """
    if path in sprite_cache:
        return sprite_cache[path]
    
    # Construit le chemin complet. `path` est supposé être relatif au dossier principal du jeu
    # ou un chemin déjà complet (ex: cfg.BUILDING_SPRITE_PATH + "name.png")
    full_path = os.path.join(path) 
    try:
        image = pygame.image.load(full_path)
        if use_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        
        sprite_cache[path] = image
        return image
    except pygame.error as e:
        print(f"ERREUR: Impossible de charger le sprite '{full_path}': {e}")
        # SPRITE: Créer un sprite placeholder en cas d'erreur
        # Utilise TILE_SIZE de cfg, qui est déjà scalé
        placeholder_size = (cfg.TILE_SIZE, cfg.TILE_SIZE)
        placeholder = pygame.Surface(placeholder_size)
        placeholder.fill(cfg.COLOR_RED) # Couleur vive pour indiquer une erreur
        pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, 0), (placeholder_size[0]-1, placeholder_size[1]-1), 2)
        pygame.draw.line(placeholder, cfg.COLOR_BLACK, (0, placeholder_size[1]-1), (placeholder_size[0]-1, 0), 2)
        sprite_cache[path] = placeholder # Mettre en cache le placeholder pour ce chemin
        return placeholder

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
            font_cache[key] = pygame.font.SysFont("arial", size)
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
    
    full_path = os.path.join(path) # Assure la compatibilité des chemins
    try:
        # pygame.mixer.Sound peut échouer si le mixer n'est pas initialisé
        # L'initialisation du mixer se fait généralement une fois au début du jeu (main.py)
        sound = pygame.mixer.Sound(full_path)
        sound_cache[path] = sound
        return sound
    except pygame.error as e:
        print(f"ERREUR: Impossible de charger le son '{full_path}': {e}")
        return None # Retourne None si le chargement échoue

def play_sound(sound_object, loops=0, volume=1.0):
    """Joue un objet Sound chargé, si disponible."""
    if sound_object and pygame.mixer.get_init(): # Vérifie si le mixer est initialisé
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
    
    # Coordonnées relatives à l'origine de la grille
    relative_px = px - grid_origin_xy_pixels[0]
    relative_py = py - grid_origin_xy_pixels[1]
    
    # Si le clic est à gauche ou au-dessus de l'origine de la grille
    if relative_px < 0 or relative_py < 0:
        return -1, -1 # Indique une position invalide ou hors grille

    grid_col = relative_px // cfg.TILE_SIZE
    grid_row = relative_py // cfg.TILE_SIZE
    
    return grid_row, grid_col

# --- Utilitaires de Dessin ---
def draw_debug_rect(surface, rect, color=cfg.COLOR_RED, width=1):
    """Dessine le contour d'un rectangle pour le débogage, si le rect est valide."""
    if rect: # S'assurer que rect n'est pas None
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
    # Petit test si on exécute ce fichier directement
    pygame.init()
    pygame.mixer.init() # Important pour tester les sons
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Test Utility Functions")

    print(f"TILE_SIZE configuré: {cfg.TILE_SIZE}")
    print(f"GRID_OFFSET_X: {cfg.GRID_OFFSET_X}, GRID_OFFSET_Y: {cfg.GRID_OFFSET_Y}")

    # Test de chargement de sprite (créez un dummy.png dans assets/sprites/ui/)
    # SPRITE: Assurez-vous d'avoir un fichier assets/sprites/ui/dummy.png pour ce test
    # ou commentez cette partie.
    try:
        dummy_sprite_path = os.path.join(cfg.UI_SPRITE_PATH, "dummy.png")
        if not os.path.exists(dummy_sprite_path):
             # Créer un dummy.png si absent pour le test
            surf = pygame.Surface((32,32)); surf.fill((0,255,0))
            pygame.image.save(surf, dummy_sprite_path)
            print(f"Création d'un fichier {dummy_sprite_path} pour le test.")

        test_sprite_orig = load_sprite(dummy_sprite_path)
        test_sprite_scaled_tile = scale_sprite_to_tile(test_sprite_orig)
        test_sprite_custom_scaled = scale_sprite_to_size(test_sprite_orig, cfg.scale_value(50), cfg.scale_value(70))
        print(f"Sprite original chargé: {test_sprite_orig.get_size() if test_sprite_orig else 'Erreur'}")
        print(f"Sprite scalé TILE: {test_sprite_scaled_tile.get_size() if test_sprite_scaled_tile else 'Erreur'}")
        print(f"Sprite scalé custom: {test_sprite_custom_scaled.get_size() if test_sprite_custom_scaled else 'Erreur'}")
    except Exception as e_test:
        print(f"Erreur dans le test de sprite: {e_test}")


    # Test de police
    test_text_surf = render_text_surface("Test Utility", cfg.FONT_SIZE_MEDIUM, cfg.COLOR_TEXT)
    print(f"Surface de texte créée: {test_text_surf.get_size() if test_text_surf else 'Erreur'}")

    # Test de son (créez un dummy.wav dans assets/sounds/)
    # SOUND: Assurez-vous d'avoir un fichier assets/sounds/dummy.wav pour ce test
    # ou commentez cette partie.
    try:
        dummy_sound_path = os.path.join(cfg.ASSET_PATH, "sounds", "dummy.wav")
        # Si vous n'avez pas de .wav, pygame peut ne pas le lire.
        # Un simple clic sonore suffirait.
        # if not os.path.exists(dummy_sound_path):
        #     print(f"Créez un fichier {dummy_sound_path} (ex: un court .wav) pour tester le son.")
        
        test_sound = load_sound(dummy_sound_path)
        if test_sound:
            print(f"Son chargé. Essayez de le jouer (vous devriez l'entendre).")
            play_sound(test_sound)
        else:
            print("Chargement du son de test échoué (ou fichier non trouvé).")

    except Exception as e_sound_test:
        print(f"Erreur dans le test de son: {e_sound_test}")


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                grid_origin = (cfg.GRID_OFFSET_X, cfg.GRID_OFFSET_Y) # Utiliser le GRID_OFFSET_Y calculé dynamiquement
                grid_r, grid_c = convert_pixels_to_grid(event.pos, grid_origin)
                pixel_x, pixel_y = convert_grid_to_pixels((grid_r, grid_c), grid_origin)
                print(f"Clic à {event.pos} -> Grille ({grid_r}, {grid_c}) -> Pixel d'origine de case ({pixel_x}, {pixel_y})")


        screen.fill(cfg.COLOR_BLACK)
        if test_text_surf:
            screen.blit(test_text_surf, (50, 50))
        if test_sprite_scaled_tile:
            screen.blit(test_sprite_scaled_tile, (100,100))
        
        # Dessiner une grille de débogage pour tester les conversions
        grid_origin_test = (cfg.GRID_OFFSET_X, cfg.GRID_OFFSET_Y)
        for r in range(cfg.INITIAL_GRID_HEIGHT_TILES):
            for c in range(cfg.INITIAL_GRID_WIDTH_TILES):
                px, py = convert_grid_to_pixels((r,c), grid_origin_test)
                rect = pygame.Rect(px, py, cfg.TILE_SIZE, cfg.TILE_SIZE)
                draw_debug_rect(screen, rect, cfg.COLOR_GREY)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()
