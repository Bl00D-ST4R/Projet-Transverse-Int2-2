# game_config.py
import pygame
import os

# --- Configuration Fenêtre de Référence ---
#SCREEN_MARGIN = 100 # Marge invisible en pixels sur chaque bord de l'écran réel
SCREEN_MARGIN_VERTICAL = 100   # Marge invisible en pixels en HAUT et en BAS
SCREEN_MARGIN_HORIZONTAL = 190 # Marge invisible en pixels à GAUCHE et à DROITE
REF_WIDTH = 1920
REF_HEIGHT = 1080
GAME_TITLE = "The Last Stand: 1941"
FPS = 60

# --- Dimensions et Positions de Base (pour REF_WIDTH x REF_HEIGHT) ---
# il y a une marge de 100p c'est a dire que tout ce qui est a -100p d'un des bords de l'ecrant est invisible
BASE_TILE_SIZE = 90
BASE_UI_TOP_BAR_HEIGHT = 45
BASE_UI_BUILD_MENU_HEIGHT = 90
BASE_UI_BUILD_MENU_BUTTON_SIZE_W = 80
BASE_UI_BUILD_MENU_BUTTON_SIZE_H = 80
BASE_UI_BUILD_MENU_BUTTON_PADDING = 5
BASE_UI_ICON_SIZE_DEFAULT = 30
BASE_UI_ICON_INTERNAL_PADDING = 5 # Padding inside a button, around an icon
BASE_UI_TOOLTIP_OFFSET_Y = -30
BASE_UI_TOOLTIP_PADDING_X = 10
BASE_UI_TOOLTIP_PADDING_Y = 6
BASE_UI_ERROR_MESSAGE_OFFSET_Y = 20
BASE_UI_TUTORIAL_MESSAGE_BOTTOM_OFFSET_Y = 10
BASE_UI_GENERAL_PADDING = 15 # General padding for UI elements
BASE_UI_ICON_TEXT_SPACING = 5 # Espacement entre une icône et son texte à côté
BASE_UI_BORDER_THICKNESS = 2  # Épaisseur de bordure générale pour les éléments UI
BASE_UI_BUTTON_BORDER_THICKNESS = 2 # Spécifique aux boutons si différent

# --- Menu Principal ---
BASE_MAIN_MENU_TITLE_Y_OFFSET = 150 # Offset Y pour le titre depuis le HAUT de la zone utilisable
BASE_MAIN_MENU_BUTTON_HEIGHT = 60
BASE_MAIN_MENU_BUTTON_SPACING = 20
BASE_MAIN_MENU_START_Y_OFFSET_FROM_TITLE = 70 # Espace entre le bas du titre et le HAUT du premier bouton

# --- Écran de Lore ---
BASE_LORE_SCREEN_START_Y = 150 # Offset Y pour la première ligne de texte
BASE_LORE_SCREEN_LINE_SPACING = 40

# --- Grille ---
BASE_GRID_INITIAL_WIDTH_TILES = 4
BASE_GRID_INITIAL_HEIGHT_TILES = 4
BASE_GRID_MAX_EXPANSION_UP_TILES = 2
BASE_GRID_MAX_EXPANSION_SIDEWAYS_STEPS = 2
BASE_GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP = 4
BASE_GRID_OFFSET_X = 0 # Grid starts at the left edge of the usable area (after margin + scaled_grid_offset_x)
BASE_GRID_BORDER_THICKNESS = 1 # Épaisseur des lignes de la grille

# --- Placement Preview ---
PLACEMENT_PREVIEW_ALPHA = 128 # Transparence pour le preview (0-255)

# --- Menu Pause ---
BASE_PAUSE_MENU_BUTTON_WIDTH = 250
BASE_PAUSE_MENU_BUTTON_HEIGHT = 50
BASE_PAUSE_MENU_SPACING = 20
BASE_PAUSE_MENU_BUTTON_BLOCK_Y_OFFSET = 50 # Décalage Y du bloc de boutons par rapport au centre de la zone utilisable
BASE_PAUSE_MENU_BUTTON_START_Y_OFFSET = 70 # Offset from the "PAUSE" title to the first button

# --- Menu Game Over ---
BASE_GAMEOVER_MENU_BUTTON_WIDTH = 250
BASE_GAMEOVER_MENU_BUTTON_HEIGHT = 50
BASE_GAMEOVER_MENU_SPACING = 20
BASE_GAMEOVER_MENU_BUTTON_START_Y_OFFSET = 60 # Décalage Y du bloc de boutons par rapport au centre de la zone utilisable (below score)
BASE_GAMEOVER_TEXT_Y_OFFSET = -60 # Décalage du texte "GAME OVER" par rapport au centre (négatif pour au-dessus)
BASE_GAMEOVER_SCORE_Y_OFFSET = 0 # Décalage du texte du score par rapport au centre

# --- Font Sizes ---
BASE_FONT_SIZE_SMALL = 18
BASE_FONT_SIZE_MEDIUM = 24
BASE_FONT_SIZE_LARGE = 36
BASE_FONT_SIZE_XLARGE = 48
BASE_FONT_SIZE_TITLE = 60

# --- Physique (Base) ---
BASE_GRAVITY_PHYSICS = 9.81 * 20 # Example, adjust for gameplay feel

# --- Couleurs ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 0, 0)
COLOR_GREEN = (0, 180, 0)
COLOR_BLUE = (0, 0, 200)
COLOR_YELLOW = (255,255,0)
COLOR_ORANGE = (255, 165, 0)
COLOR_CYAN = (0,255,255)
COLOR_MAGENTA = (255,0,255) #the failsafe color
COLOR_GREY = (128, 128, 128)

COLOR_GREY_DARK = (50, 50, 50)
COLOR_GREY_MEDIUM = (128, 128, 128)
COLOR_GREY_LIGHT = (200, 200, 200)
COLOR_DARK_GREY_BLUE = (40, 50, 70)
COLOR_BACKGROUND = COLOR_DARK_GREY_BLUE

COLOR_TEXT = COLOR_GREY_LIGHT
COLOR_UI_TEXT_ON_GREY = COLOR_BLACK
COLOR_TITLE_TEXT = COLOR_WHITE
COLOR_MONEY = (255, 215, 0)
COLOR_IRON = (169, 169, 169)
COLOR_ENERGY_OK = (60, 179, 113)
COLOR_ENERGY_LOW = COLOR_ORANGE
COLOR_ENERGY_FAIL = (205, 92, 92)

COLOR_HP_FULL = COLOR_GREEN
COLOR_HP_MEDIUM = COLOR_YELLOW # Not used in current Enemy.draw, but good to have
COLOR_HP_LOW = COLOR_ORANGE
COLOR_HP_CRITICAL = COLOR_RED
COLOR_HP_EMPTY = COLOR_GREY_DARK # Not used, but good to have
COLOR_HP_BAR_BACKGROUND = (40,40,40)

COLOR_GRID_DEFAULT = (45, 55, 65)
COLOR_GRID_REINFORCED = (65, 75, 85)
COLOR_GRID_BORDER = (80, 90, 100)
COLOR_PLACEMENT_VALID = (0, 255, 0) # Alpha is handled in draw_placement_preview
COLOR_PLACEMENT_INVALID = (255, 0, 0) # Alpha is handled in draw_placement_preview

COLOR_BUILD_MENU_BG = (30, 35, 45)
COLOR_BUTTON_BG = (70, 80, 90)
COLOR_BUTTON_HOVER_BG = (90, 100, 110)
COLOR_BUTTON_BORDER = (110, 120, 130)
COLOR_BUTTON_SELECTED_BORDER = COLOR_MONEY
COLOR_BUTTON_HOVER_BORDER = (150, 160, 170) # For non-text buttons, e.g. build menu items
COLOR_BUTTON_HOVER_TEXT = COLOR_WHITE # For text-based buttons like main menu

COLOR_TOOLTIP_BG = (30, 30, 30, 220)
COLOR_TOOLTIP_TEXT = COLOR_WHITE
COLOR_MENU_BACKGROUND = (20, 30, 50)

COLOR_UI_TOP_BAR_BG = (100, 100, 100)
COLOR_ERROR_TEXT = COLOR_RED
COLOR_ERROR_BG = (50, 50, 50, 200)
COLOR_PAUSE_OVERLAY_BG = (0, 0, 0, 180)
COLOR_PAUSE_TEXT = COLOR_WHITE
COLOR_GAMEOVER_OVERLAY_BG = (0, 0, 0, 220)
COLOR_GAMEOVER_TEXT = COLOR_RED
COLOR_TEXT_LIGHT = COLOR_WHITE
COLOR_TUTORIAL_TEXT = COLOR_WHITE
COLOR_TUTORIAL_BG = (20, 20, 80, 200)


# --- Ressources et Paramètres de Jeu ---
INITIAL_MONEY = 1000
INITIAL_IRON = 200
BASE_IRON_CAPACITY = 500
INITIAL_CITY_HP = 100
CITY_HEARTS = 3 # Not currently used, but for potential visual display
ENERGY_LOW_THRESHOLD = 5 # Seuil en dessous duquel l'énergie est "low" (valeur positive)

# --- Chemins vers les Assets ---
ASSET_PATH = "assets/"
BUILDING_SPRITE_PATH = os.path.join(ASSET_PATH, "buildings/")
TURRET_SPRITE_PATH = os.path.join(ASSET_PATH, "turrets/")
ENEMY_SPRITE_PATH = os.path.join(ASSET_PATH, "enemies/")
PROJECTILE_SPRITE_PATH = os.path.join(ASSET_PATH, "projectiles/")
DEFAULT_BULLET_SPRITE_NAME = "Default_bullet_sprite.png"
UI_SPRITE_PATH = os.path.join(ASSET_PATH, "ui/")
EFFECT_SPRITE_PATH = os.path.join(ASSET_PATH, "effects/")
SOUND_PATH = os.path.join(ASSET_PATH, "sounds/")
MUSIC_PATH = os.path.join(ASSET_PATH, "music/")

# --- Polices ---
FONT_NAME_DEFAULT = None # Pygame will use its default system font

# --- États du Jeu ---
STATE_MENU = "main_menu"
STATE_GAMEPLAY = "gameplay"
STATE_LORE = "lore_screen"
STATE_TUTORIAL = "tutorial"
STATE_OPTIONS = "options_menu" # Not implemented
STATE_GAME_OVER = "game_over"
STATE_QUIT = "quit_game"

# --- Clés pour les Dictionnaires de Stats ---
# Général
STAT_ID = "id_type" # Not actively used as dict key is type string
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
BASE_PROJECTILE_SPRITE_SCALE_FACTOR = 0.5 # Factor to scale original projectile sprites
BASE_PROJECTILE_FALLBACK_SIZE = 5 # Fallback size for projectile sprites if loading fails
BASE_PROJECTILE_OFFSCREEN_BUFFER = 100 # Buffer around usable area for projectile deactivation
STAT_FLAMETHROWER_DURATION_SEC = "flamethrower_duration_seconds"
STAT_FLAMETHROWER_COOLDOWN_SEC = "flamethrower_cooldown_seconds"
STAT_FLAMETHROWER_CHARGE_SPRITE_NAME = "flamethrower_charge_sprite_name"
STAT_FLAMETHROWER_DISCHARGE_SPRITE_NAME = "flamethrower_discharge_sprite_name"
STAT_PROJECTILE_IS_BEAM = "projectile_is_beam"
STAT_PROJECTILE_BEAM_COLOR = "projectile_beam_color"
STAT_PROJECTILE_BEAM_DURATION_SEC = "projectile_beam_duration_seconds"


# Ennemis spécifiques
STAT_HP_MAX = "max_hp"
GLOBAL_ENEMY_SPRITE_SCALE_MULTIPLIER = 0.5 # Exemple: réduit tous les sprites d'ennemis à 70% de
STAT_MOVE_SPEED_PIXELS_SEC = "move_speed_pixels_sec"
STAT_DAMAGE_TO_CITY = "damage_to_city_amount"
STAT_SCORE_POINTS_VALUE = "score_points_value"
STAT_MONEY_DROP_VALUE = "money_drop_value"
STAT_SIZE_MIN_SCALE_FACTOR = "size_min_scale_factor" # Multiplier for original sprite size
STAT_SIZE_MAX_SCALE_FACTOR = "size_max_scale_factor" # Multiplier for original sprite size
STAT_HITBOX_SCALE_FACTORS_WH = "hitbox_scale_factors_wh" # (width_factor, height_factor) for hitbox relative to sprite
BASE_ENEMY_HP_BAR_WIDTH = 30
BASE_ENEMY_HP_BAR_HEIGHT = 5
BASE_ENEMY_HP_BAR_OFFSET_Y = 3
BASE_ENEMY_FALLBACK_SIZE = 20
BASE_ENEMY_SPAWN_Y_PADDING = 20 # Padding from top/bottom of usable spawn area for enemies
BASE_ENEMY_SPAWN_X_OFFSET = 50 # How far off-screen (right) enemies spawn
BASE_ENEMY_OFFSCREEN_DESPAWN_BUFFER = 50 # How far off-screen (left) enemies despawn

# --- Paramètres de Spawn des Ennemis ---
ENEMY_SPAWN_MIN_Y_PERCENTAGE = 0.15  # Pourcentage depuis le HAUT de la zone de jeu (ex: 15%)
ENEMY_SPAWN_MAX_Y_PERCENTAGE = 0.70  # Pourcentage depuis le HAUT de la zone de jeu (ex: 85%, laissant 15% en bas)

# --- Paramètres de Vagues ---
WAVE_INITIAL_PREP_TIME_SEC = 10.0 # Shortened for testing
WAVE_TIME_BETWEEN_WAVES_SEC = 20.0 # Shortened for testing

# --- Coûts d'expansion ---
BASE_EXPANSION_COST_UP = 500
BASE_EXPANSION_COST_SIDE = 750
EXPANSION_COST_INCREASE_FACTOR_UP = 1.5
EXPANSION_COST_INCREASE_FACTOR_SIDE = 1.8

DEBUG_MODE = True # Set to True to see debug prints and rects

# --- Fin du fichier game_config.py ---