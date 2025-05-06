# game_config.py
import pygame # Nécessaire pour certaines constantes Pygame si utilisées (ex: K_ESCAPE)

# --- Configuration de la Fenêtre et du Framerate ---
# MODIFIABLE: Résolution de l'écran souhaitée par défaut
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GAME_TITLE = "The Last Stand: 1941" # MODIFIABLE: Titre de votre jeu
FPS = 60 # Frames par seconde cibles

# --- Système de Scaling Dynamique ---
# RÉSOLUTION DE RÉFÉRENCE: Les valeurs de base (BASE_*) sont définies pour cette résolution.
# Tout sera mis à l'échelle par rapport à cela.
REF_WIDTH = 1920
REF_HEIGHT = 1080

# Calcul des facteurs d'échelle.
# Si la résolution actuelle est différente de la résolution de référence,
# ces facteurs seront différents de 1.0.
SCALE_X = SCREEN_WIDTH / REF_WIDTH
SCALE_Y = SCREEN_HEIGHT / REF_HEIGHT

# GENERAL_SCALE: Facteur d'échelle principal appliqué à la plupart des éléments visuels.
# Option 1: min(SCALE_X, SCALE_Y) - Conserve les proportions, peut créer des bandes noires/blanches (letterboxing/pillarboxing).
# Option 2: SCALE_X ou SCALE_Y - Peut étirer si les ratios d'aspect diffèrent. Pour un jeu 2D, SCALE_X est souvent utilisé.
# MODIFIABLE: Choisissez la stratégie de scaling qui convient le mieux à vos assets.
# Si vos assets sont conçus pour 1920x1080, utiliser min() est plus sûr pour éviter la distorsion.
GENERAL_SCALE = min(SCALE_X, SCALE_Y)
# GENERAL_SCALE = SCALE_X # Alternative

# Fonction utilitaire pour appliquer GENERAL_SCALE
def scale_value(value):
    """Applique GENERAL_SCALE à une valeur numérique ou à chaque élément d'un tuple/liste."""
    if isinstance(value, (int, float)):
        return int(value * GENERAL_SCALE)
    if isinstance(value, (tuple, list)):
        # S'assurer que les tuples de petite taille comme les couleurs ne sont pas scalés si non désiré.
        # Pour les dimensions, c'est OK. Pour les couleurs (R,G,B), non.
        # Cette fonction est principalement pour les dimensions/positions.
        return tuple(int(v * GENERAL_SCALE) for v in value)
    return value # Retourne la valeur originale si ce n'est pas un type attendu.

# --- Valeurs de Base (définies pour REF_WIDTH x REF_HEIGHT) ---
# Ces valeurs seront scalées pour obtenir les dimensions utilisées dans le jeu.
BASE_TILE_SIZE = 90         # Taille d'une case de la grille en pixels de référence
BASE_UI_TOP_BAR_HEIGHT = 45
BASE_UI_BUILD_MENU_HEIGHT = 90
BASE_UI_BUILD_MENU_BUTTON_SIZE_W = 80 # Largeur d'un bouton du menu de construction
BASE_UI_BUILD_MENU_BUTTON_SIZE_H = 80 # Hauteur d'un bouton

BASE_INITIAL_GRID_WIDTH_TILES = 4    # Largeur initiale de la grille en nombre de cases
BASE_INITIAL_GRID_HEIGHT_TILES = 4   # Hauteur initiale
BASE_MAX_EXPANSION_UP_TILES = 2      # Nombre de cases max ajoutées en hauteur
BASE_MAX_EXPANSION_SIDEWAYS_STEPS = 2 # Nombre d'étapes d'expansion latérale
BASE_EXPANSION_SIDEWAYS_TILES_PER_STEP = 4 # Cases ajoutées en largeur par étape

BASE_GRID_OFFSET_X = 50 # Marge à gauche de la grille en pixels de référence
# BASE_GRID_OFFSET_Y est calculé dynamiquement pour être au-dessus du menu du bas.

BASE_FONT_SIZE_SMALL = 18
BASE_FONT_SIZE_MEDIUM = 24
BASE_FONT_SIZE_LARGE = 36
BASE_FONT_SIZE_XLARGE = 48


# --- Valeurs Scalées (utilisées directement dans le jeu) ---
TILE_SIZE = scale_value(BASE_TILE_SIZE)
UI_TOP_BAR_HEIGHT = scale_value(BASE_UI_TOP_BAR_HEIGHT)
UI_BUILD_MENU_HEIGHT = scale_value(BASE_UI_BUILD_MENU_HEIGHT)
UI_BUILD_MENU_BUTTON_SIZE = (scale_value(BASE_UI_BUILD_MENU_BUTTON_SIZE_W), scale_value(BASE_UI_BUILD_MENU_BUTTON_SIZE_H))

INITIAL_GRID_WIDTH_TILES = BASE_INITIAL_GRID_WIDTH_TILES # Nombre de tiles, non scalé
INITIAL_GRID_HEIGHT_TILES = BASE_INITIAL_GRID_HEIGHT_TILES
MAX_EXPANSION_UP_TILES = BASE_MAX_EXPANSION_UP_TILES
MAX_EXPANSION_SIDEWAYS_STEPS = BASE_MAX_EXPANSION_SIDEWAYS_STEPS
EXPANSION_SIDEWAYS_TILES_PER_STEP = BASE_EXPANSION_SIDEWAYS_TILES_PER_STEP

GRID_OFFSET_X = scale_value(BASE_GRID_OFFSET_X)
# GRID_OFFSET_Y sera calculé dynamiquement dans GameState en fonction de la hauteur de la grille et du menu.
# On peut définir une valeur de base pour le padding au-dessus du menu du bas.
BASE_GRID_BOTTOM_PADDING = 10 # Padding de référence entre la grille et le menu du bas
GRID_BOTTOM_PADDING = scale_value(BASE_GRID_BOTTOM_PADDING)
# GRID_OFFSET_Y = SCREEN_HEIGHT - (INITIAL_GRID_HEIGHT_TILES * TILE_SIZE) - UI_BUILD_MENU_HEIGHT - GRID_BOTTOM_PADDING

FONT_SIZE_SMALL = scale_value(BASE_FONT_SIZE_SMALL)
FONT_SIZE_MEDIUM = scale_value(BASE_FONT_SIZE_MEDIUM)
FONT_SIZE_LARGE = scale_value(BASE_FONT_SIZE_LARGE)
FONT_SIZE_XLARGE = scale_value(BASE_FONT_SIZE_XLARGE)


# --- Physique ---
# MODIFIABLE: Gravité. Ajuster pour le feeling du jeu.
# Cette valeur de base est pour la résolution de référence.
BASE_GRAVITY_PHYSICS = 9.81 * 20 # Ex: 20 "unités de jeu" par mètre de référence
GRAVITY = BASE_GRAVITY_PHYSICS * GENERAL_SCALE # Gravité en pixels/s^2 scalée


# --- Couleurs (non scalées) ---
# MODIFIABLE: Définissez vos couleurs ici.
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 0, 0) # Un rouge moins agressif
COLOR_GREEN = (0, 180, 0) # Un vert moins agressif
COLOR_BLUE = (0, 0, 200)
COLOR_GREY_DARK = (50, 50, 50)
COLOR_GREY_MEDIUM = (128, 128, 128)
COLOR_GREY_LIGHT = (200, 200, 200)

COLOR_TEXT = COLOR_GREY_LIGHT
COLOR_MONEY = (255, 215, 0) # Or
COLOR_IRON = (169, 169, 169) # Gris acier
COLOR_ENERGY_OK = (60, 179, 113) # Vert moyen
COLOR_ENERGY_LOW = (255, 165, 0) # Orange
COLOR_ENERGY_FAIL = (205, 92, 92)  # Rouge indien

COLOR_HP_FULL = COLOR_GREEN
COLOR_HP_EMPTY = COLOR_GREY_DARK
COLOR_HP_BAR_BACKGROUND = (40,40,40)

COLOR_GRID_DEFAULT = (45, 55, 65)
COLOR_GRID_REINFORCED = (65, 75, 85)
COLOR_GRID_BORDER = (80, 90, 100)
COLOR_BUILD_MENU_BG = (30, 35, 45)
COLOR_BUTTON_BG = (70, 80, 90)
COLOR_BUTTON_BORDER = (110, 120, 130)
COLOR_BUTTON_SELECTED_BORDER = (255, 215, 0) # Or pour sélection
COLOR_BUTTON_HOVER_BORDER = (150, 160, 170)


# --- Ressources et Paramètres de Jeu (logiques, non directement scalés) ---
# MODIFIABLE:
INITIAL_MONEY = 1000
INITIAL_IRON = 200
BASE_IRON_CAPACITY = 500 # Capacité de stockage de fer initiale
INITIAL_CITY_HP = 100
CITY_HEARTS = 3 # Nombre de cœurs pour représenter les HP de la ville visuellement


# --- Chemins vers les Assets ---
# MODIFIABLE: Adaptez si votre structure de dossiers est différente.
ASSET_PATH = "assets/" # Chemin principal vers le dossier assets
SPRITE_PATH = ASSET_PATH + "sprites/"
BUILDING_SPRITE_PATH = SPRITE_PATH + "buildings/"
TURRET_SPRITE_PATH = SPRITE_PATH + "turrets/"
ENEMY_SPRITE_PATH = SPRITE_PATH + "enemies/"
PROJECTILE_SPRITE_PATH = SPRITE_PATH + "projectiles/"
UI_SPRITE_PATH = SPRITE_PATH + "ui/"
EFFECT_SPRITE_PATH = SPRITE_PATH + "effects/" # Pour explosions, etc.
SOUND_PATH = ASSET_PATH + "sounds/"
MUSIC_PATH = ASSET_PATH + "music/"


# --- Polices ---
# MODIFIABLE: Nom de la police par défaut (None pour la police système de Pygame)
# ou chemin vers un fichier .ttf (ex: "assets/fonts/MyCoolFont.ttf")
FONT_NAME_DEFAULT = None
# Les tailles de police sont définies plus haut (FONT_SIZE_SMALL, etc.) et sont scalées.


# --- États du Jeu (pour la machine d'état dans main.py) ---
STATE_MENU = 0
STATE_GAMEPLAY = 1
STATE_QUIT = 99 # Utiliser une valeur distincte pour quitter
STATE_LORE = 3
STATE_TUTORIAL = 4
STATE_OPTIONS = 5 # Si vous ajoutez un menu d'options


# --- Clés pour les Dictionnaires de Stats (utilisées dans objects.py) ---
# Garder ces clés cohérentes aide à éviter les typos.
STAT_HP = "hp"
STAT_COST_MONEY = "cost_money"
STAT_COST_IRON = "cost_iron"
STAT_POWER = "power_consumption" # Négatif pour consommation, positif pour production
STAT_POWER_PROD = "power_production" # Alternative plus explicite pour production
STAT_IRON_PROD = "iron_production_pm" # Par minute
STAT_IRON_STORAGE = "iron_storage_increase"
STAT_ADJACENCY_BONUS = "adjacency_bonus_value" # Valeur du bonus par unité adjacente

STAT_SPRITE = "sprite_default_name" # Nom du fichier sprite de base
STAT_SPRITES = "sprite_variants_dict" # Dictionnaire de sprites contextuels {key: "name.png"}

STAT_RANGE = "range_pixels"
STAT_MIN_RANGE = "min_range_pixels"
STAT_MAX_RANGE = "max_range_pixels"
STAT_FIRE_RATE = "fire_rate_per_sec" # Tirs par seconde
STAT_PROJ_TYPE = "projectile_type_id"
STAT_PROJ_SPEED = "projectile_launch_speed_pixels" # Vitesse initiale du projectile (pour mortier)
STAT_PROJ_FLAT_SPEED = "projectile_flat_speed_pixels" # Vitesse pour tirs directs

STAT_AOE_RADIUS = "aoe_radius_pixels"
STAT_DAMAGE = "damage_amount"

STAT_SPEED = "move_speed_pixels_sec" # Pour les ennemis
STAT_CITY_DAMAGE = "damage_to_city"
STAT_SCORE_VALUE = "score_points_value"
STAT_MONEY_VALUE = "money_drop_value"

STAT_SIZE_MIN_SCALE = "size_min_scale_factor" # Pour les ennemis (facteur d'échelle)
STAT_SIZE_MAX_SCALE = "size_max_scale_factor" # Pour les ennemis (facteur d'échelle)
STAT_HITBOX_SCALE_FACTORS = "hitbox_scale_factors_wh" # (width_scale, height_scale) par rapport au rect du sprite

# Clés pour les sprites de tourelle
STAT_TURRET_BASE_SPRITE = "base_sprite_name"
STAT_TURRET_GUN_SPRITE = "gun_sprite_name"

# --- Fin du fichier game_config.py ---
