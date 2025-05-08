# game_config.py
import pygame

# --- Configuration de la Fenêtre et du Framerate ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GAME_TITLE = "The Last Stand: 1941"
FPS = 60

# --- Système de Scaling Dynamique ---
REF_WIDTH = 1920
REF_HEIGHT = 1080
SCALE_X = SCREEN_WIDTH / REF_WIDTH
SCALE_Y = SCREEN_HEIGHT / REF_HEIGHT
GENERAL_SCALE = min(SCALE_X, SCALE_Y) # Maintien des proportions

def scale_value(value):
    if isinstance(value, (int, float)):
        return int(value * GENERAL_SCALE)
    if isinstance(value, (tuple, list)):
        return tuple(int(v * GENERAL_SCALE) for v in value)
    return value

# --- Dimensions et Positions de Base (pour REF_WIDTH x REF_HEIGHT) ---
BASE_TILE_SIZE = 90
BASE_UI_TOP_BAR_HEIGHT = 45
BASE_UI_BUILD_MENU_HEIGHT = 90
BASE_UI_BUILD_MENU_BUTTON_SIZE_W = 80
BASE_UI_BUILD_MENU_BUTTON_SIZE_H = 80
BASE_UI_ICON_SIZE_DEFAULT = 30 # Taille par défaut pour les icônes (ex: ressources)
BASE_UI_TOOLTIP_OFFSET_Y = -30
BASE_UI_TOOLTIP_PADDING_X = 10
BASE_UI_TOOLTIP_PADDING_Y = 6
BASE_UI_ERROR_MESSAGE_OFFSET_Y = 20 # Depuis le haut de la barre du haut
BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y = 10 # Depuis le haut du menu de construction

BASE_GRID_INITIAL_WIDTH_TILES = 4
BASE_GRID_INITIAL_HEIGHT_TILES = 4
BASE_GRID_MAX_EXPANSION_UP_TILES = 2
BASE_GRID_MAX_EXPANSION_SIDEWAYS_STEPS = 2
BASE_GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP = 4
BASE_GRID_OFFSET_X = 50
BASE_GRID_BOTTOM_PADDING = 10 # Padding entre bas de la grille et haut du menu construction

BASE_FONT_SIZE_SMALL = 18
BASE_FONT_SIZE_MEDIUM = 24
BASE_FONT_SIZE_LARGE = 36
BASE_FONT_SIZE_XLARGE = 48
BASE_FONT_SIZE_TITLE = 60 # Ajout pour le titre du menu principal

# --- Valeurs Scalées (utilisées directement dans le jeu) ---
TILE_SIZE = scale_value(BASE_TILE_SIZE)
UI_TOP_BAR_HEIGHT = scale_value(BASE_UI_TOP_BAR_HEIGHT)
UI_BUILD_MENU_HEIGHT = scale_value(BASE_UI_BUILD_MENU_HEIGHT)
UI_BUILD_MENU_BUTTON_SIZE = (scale_value(BASE_UI_BUILD_MENU_BUTTON_SIZE_W), scale_value(BASE_UI_BUILD_MENU_BUTTON_SIZE_H))
UI_BUILD_MENU_BUTTON_PADDING = scale_value(5)
UI_ICON_SIZE_DEFAULT = scale_value(BASE_UI_ICON_SIZE_DEFAULT)
UI_TOOLTIP_OFFSET_Y = scale_value(BASE_UI_TOOLTIP_OFFSET_Y)
UI_TOOLTIP_PADDING_X = scale_value(BASE_UI_TOOLTIP_PADDING_X)
UI_TOOLTIP_PADDING_Y = scale_value(BASE_UI_TOOLTIP_PADDING_Y)
UI_ERROR_MESSAGE_OFFSET_Y = scale_value(BASE_UI_ERROR_MESSAGE_OFFSET_Y)
UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y = scale_value(BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y)


GRID_INITIAL_WIDTH_TILES = BASE_GRID_INITIAL_WIDTH_TILES
GRID_INITIAL_HEIGHT_TILES = BASE_GRID_INITIAL_HEIGHT_TILES
GRID_MAX_EXPANSION_UP_TILES = BASE_GRID_MAX_EXPANSION_UP_TILES
GRID_MAX_EXPANSION_SIDEWAYS_STEPS = BASE_GRID_MAX_EXPANSION_SIDEWAYS_STEPS
GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP = BASE_GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP
GRID_OFFSET_X = scale_value(BASE_GRID_OFFSET_X)
GRID_BOTTOM_PADDING = scale_value(BASE_GRID_BOTTOM_PADDING)
# GRID_OFFSET_Y est calculé dynamiquement dans GameState

FONT_SIZE_SMALL = scale_value(BASE_FONT_SIZE_SMALL)
FONT_SIZE_MEDIUM = scale_value(BASE_FONT_SIZE_MEDIUM)
FONT_SIZE_LARGE = scale_value(BASE_FONT_SIZE_LARGE)
FONT_SIZE_XLARGE = scale_value(BASE_FONT_SIZE_XLARGE)
FONT_SIZE_TITLE = scale_value(BASE_FONT_SIZE_TITLE) # Ajout pour le titre

# --- Physique ---
BASE_GRAVITY_PHYSICS = 9.81 * 20 # m/s^2 de référence * facteur de conversion unités de jeu/mètre
GRAVITY = BASE_GRAVITY_PHYSICS * GENERAL_SCALE # Gravité en "unités de jeu scalées"/s^2

# --- Couleurs ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 0, 0)
COLOR_GREEN = (0, 180, 0)
COLOR_BLUE = (0, 0, 200)
COLOR_YELLOW = (255,255,0)
COLOR_ORANGE = (255, 165, 0)
COLOR_CYAN = (0,255,255)
COLOR_MAGENTA = (255,0,255)
COLOR_GREY = (128, 128, 128) # Ajout d'un gris générique

COLOR_GREY_DARK = (50, 50, 50)
COLOR_GREY_MEDIUM = (128, 128, 128)
COLOR_GREY_LIGHT = (200, 200, 200)

COLOR_TEXT = COLOR_GREY_LIGHT
COLOR_TITLE_TEXT = COLOR_WHITE # Pour le titre du menu principal
COLOR_MONEY = (255, 215, 0)
COLOR_IRON = (169, 169, 169)
COLOR_ENERGY_OK = (60, 179, 113)
COLOR_ENERGY_LOW = COLOR_ORANGE
COLOR_ENERGY_FAIL = (205, 92, 92)

COLOR_HP_FULL = COLOR_GREEN
COLOR_HP_MEDIUM = COLOR_YELLOW
COLOR_HP_LOW = COLOR_ORANGE
COLOR_HP_CRITICAL = COLOR_RED
COLOR_HP_EMPTY = COLOR_GREY_DARK
COLOR_HP_BAR_BACKGROUND = (40,40,40)

COLOR_GRID_DEFAULT = (45, 55, 65)
COLOR_GRID_REINFORCED = (65, 75, 85)
COLOR_GRID_BORDER = (80, 90, 100)
COLOR_PLACEMENT_VALID = (0, 255, 0, 100) # Vert transparent pour preview placement
COLOR_PLACEMENT_INVALID = (255, 0, 0, 100) # Rouge transparent

COLOR_BUILD_MENU_BG = (30, 35, 45)
COLOR_BUTTON_BG = (70, 80, 90)
COLOR_BUTTON_HOVER_BG = (90, 100, 110) # Ajout pour le survol des boutons
COLOR_BUTTON_BORDER = (110, 120, 130)
COLOR_BUTTON_SELECTED_BORDER = COLOR_MONEY
COLOR_BUTTON_HOVER_BORDER = (150, 160, 170) # Peut-être redondant si COLOR_BUTTON_SELECTED_BORDER est utilisé pour le survol
COLOR_TOOLTIP_BG = (30, 30, 30, 220)
COLOR_TOOLTIP_TEXT = COLOR_WHITE
COLOR_MENU_BACKGROUND = (20, 30, 50) # Fond pour les menus (principal, pause, etc.)

# --- Ressources et Paramètres de Jeu ---
INITIAL_MONEY = 1000
INITIAL_IRON = 200
BASE_IRON_CAPACITY = 500
INITIAL_CITY_HP = 100
CITY_HEARTS = 3 # Nombre de coeurs à afficher pour la vie de la ville

# --- Chemins vers les Assets ---
# MODIFIÉ: Suppression du sous-dossier "sprites/"
ASSET_PATH = "assets/"
# SPRITE_PATH = ASSET_PATH + "sprites/" # Supprimé
BUILDING_SPRITE_PATH = ASSET_PATH + "buildings/" # Ex: assets/buildings/foundation_wood.png
TURRET_SPRITE_PATH = ASSET_PATH + "turrets/"     # Ex: assets/turrets/turret_base_gatling.png
ENEMY_SPRITE_PATH = ASSET_PATH + "enemies/"       # Ex: assets/enemies/enemy_basic.png
PROJECTILE_SPRITE_PATH = ASSET_PATH + "projectiles/" # Ex: assets/projectiles/bullet.png
UI_SPRITE_PATH = ASSET_PATH + "ui/"             # Ex: assets/ui/icon_money.png
EFFECT_SPRITE_PATH = ASSET_PATH + "effects/"     # Ex: assets/effects/explosion_01.png
SOUND_PATH = ASSET_PATH + "sounds/"
MUSIC_PATH = ASSET_PATH + "music/"

# --- Polices ---
FONT_NAME_DEFAULT = None # Pygame utilisera sa police par défaut
# FONT_NAME_PRIMARY = "assets/fonts/YourFont.ttf" # Exemple si vous ajoutez une police

# --- États du Jeu ---
STATE_MENU = "main_menu" # Utilisation de chaînes pour plus de clarté
STATE_GAMEPLAY = "gameplay"
STATE_LORE = "lore_screen"
STATE_TUTORIAL = "tutorial"
STATE_OPTIONS = "options_menu"
STATE_GAME_OVER = "game_over" # Ajouté
STATE_QUIT = "quit_game"

# --- Clés pour les Dictionnaires de Stats (cohérence avec objects.py) ---
# Général
STAT_ID = "id_type"
STAT_SPRITE_DEFAULT_NAME = "sprite_default_name"
STAT_SPRITE_VARIANTS_DICT = "sprite_variants_dict"

# Bâtiments & Tourelles
STAT_COST_MONEY = "cost_money"
STAT_COST_IRON = "cost_iron"
STAT_POWER_CONSUMPTION = "power_consumption_watts"
STAT_POWER_PRODUCTION = "power_production_watts"
STAT_IRON_PRODUCTION_PM = "iron_production_per_minute"
STAT_IRON_STORAGE_INCREASE = "iron_storage_increase_capacity"
STAT_ADJACENCY_BONUS_VALUE = "adjacency_bonus_value_per_unit"

# Tourelles spécifiques
STAT_RANGE_PIXELS = "range_pixels"
STAT_MIN_RANGE_PIXELS = "min_range_pixels"
STAT_MAX_RANGE_PIXELS = "max_range_pixels"
STAT_FIRE_RATE_PER_SEC = "fire_rate_per_sec"
STAT_PROJECTILE_TYPE_ID = "projectile_type_id"
STAT_PROJECTILE_LAUNCH_SPEED_PIXELS = "projectile_launch_speed_pixels_sec"
STAT_TURRET_BASE_SPRITE_NAME = "turret_base_sprite_name"
STAT_TURRET_GUN_SPRITE_NAME = "turret_gun_sprite_name"

# Projectiles spécifiques
STAT_DAMAGE_AMOUNT = "damage_amount"
STAT_PROJECTILE_FLAT_SPEED_PIXELS = "projectile_flat_speed_pixels_sec"
STAT_AOE_RADIUS_PIXELS = "aoe_radius_pixels"
STAT_PROJECTILE_LIFETIME_SEC = "projectile_lifetime_seconds"

# Ennemis spécifiques
STAT_HP_MAX = "max_hp"
STAT_MOVE_SPEED_PIXELS_SEC = "move_speed_pixels_sec"
STAT_DAMAGE_TO_CITY = "damage_to_city_amount"
STAT_SCORE_POINTS_VALUE = "score_points_value"
STAT_MONEY_DROP_VALUE = "money_drop_value"
STAT_SIZE_MIN_SCALE_FACTOR = "size_min_scale_factor"
STAT_SIZE_MAX_SCALE_FACTOR = "size_max_scale_factor"
STAT_HITBOX_SCALE_FACTORS_WH = "hitbox_scale_factors_wh"

# --- Paramètres de Vagues (utilisés dans wave_definitions.py et game_functions.py) ---
WAVE_INITIAL_PREP_TIME_SEC = 120.0
WAVE_TIME_BETWEEN_WAVES_SEC = 150.0 # Temps de préparation entre les vagues après la première

# --- Coûts d'expansion (valeurs de base, peuvent augmenter) ---
BASE_EXPANSION_COST_UP = 500
BASE_EXPANSION_COST_SIDE = 750
EXPANSION_COST_INCREASE_FACTOR_UP = 1.5 # Le coût augmente de 50% à chaque fois
EXPANSION_COST_INCREASE_FACTOR_SIDE = 1.8

# --- Fin du fichier game_config.py ---
