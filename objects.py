# objects.py
import pygame
import random
import math
import os
import game_config as cfg
import utility_functions as util

# --- Définitions des Stats des Objets ---
BUILDING_STATS = {
    "frame": {
        cfg.STAT_COST_MONEY: 10,
        cfg.STAT_SPRITE_DEFAULT_NAME: "frame.png",
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            "default": "frame.png",
            "reinforced": "frame2.png",
            "turret_platform": "frame3.png"
        }
    },
    "foundation": {
        cfg.STAT_COST_MONEY: 0,
        cfg.STAT_SPRITE_DEFAULT_NAME: "fundations.png",  # Assumes this is the correct filename
        "is_reinforced_foundation": True
    },
    "generator": {
        cfg.STAT_COST_MONEY: 150,
        cfg.STAT_POWER_PRODUCTION: 10,
        cfg.STAT_SPRITE_DEFAULT_NAME: "battery.png",
    },
    "miner": {
        cfg.STAT_COST_MONEY: 200, cfg.STAT_COST_IRON: 50,
        cfg.STAT_POWER_CONSUMPTION: 2,
        cfg.STAT_IRON_PRODUCTION_PM: 2,
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            "single": "miner.png",
            "stacked_bottom": "miner_stacked_bottom.png",
            "stacked_middle": "miner_stacked_middle.png",
            "stacked_top": "miner_stacked_top.png",
        },
        cfg.STAT_SPRITE_DEFAULT_NAME: "miner.png",
    },
    "storage": {
        cfg.STAT_COST_MONEY: 100,
        cfg.STAT_IRON_STORAGE_INCREASE: 250,
        cfg.STAT_ADJACENCY_BONUS_VALUE: 50,
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            "single": "storage.png",
        },
        cfg.STAT_SPRITE_DEFAULT_NAME: "storage.png",
    }
}

ENEMY_STATS = {
    1: {
        cfg.STAT_HP_MAX: 50,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 60,
        cfg.STAT_DAMAGE_TO_CITY: 10,
        cfg.STAT_SCORE_POINTS_VALUE: 10,
        cfg.STAT_MONEY_DROP_VALUE: 5,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_basic_sketch.png", # Assurez-vous que les noms de fichiers sont corrects
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.8, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.2,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.8, 0.8)
    },
    2: {
        cfg.STAT_HP_MAX: 30,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 120,
        cfg.STAT_DAMAGE_TO_CITY: 5,
        cfg.STAT_SCORE_POINTS_VALUE: 15,
        cfg.STAT_MONEY_DROP_VALUE: 7,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_fast.png", # Assurez-vous que les noms de fichiers sont corrects
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.7, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.0,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.7, 0.9)
    },
    3: {
        cfg.STAT_HP_MAX: 200,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 30,
        cfg.STAT_DAMAGE_TO_CITY: 25,
        cfg.STAT_SCORE_POINTS_VALUE: 50,
        cfg.STAT_MONEY_DROP_VALUE: 20,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_tank.png", # Assurez-vous que les noms de fichiers sont corrects
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 1.3, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.6,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.9, 0.9)
    },
    # ... Ajoutez d'autres types d'ennemis si nécessaire
}

TURRET_STATS = {
    "machine_gun_turret": {  # Anciennement "gatling_turret"
        cfg.STAT_ID: "machine_gun_turret",
        cfg.STAT_COST_MONEY: 175, cfg.STAT_COST_IRON: 40,
        cfg.STAT_POWER_CONSUMPTION: 6,
        cfg.STAT_RANGE_PIXELS: 150,  # Base range
        cfg.STAT_FIRE_RATE_PER_SEC: 10,
        cfg.STAT_PROJECTILE_TYPE_ID: "machine_gun_beam",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "gun.png",
    },
    "mortar_turret": {
        cfg.STAT_ID: "mortar_turret",
        cfg.STAT_COST_MONEY: 120, cfg.STAT_COST_IRON: 50,
        cfg.STAT_POWER_CONSUMPTION: 8,
        cfg.STAT_MIN_RANGE_PIXELS: 100,
        cfg.STAT_MAX_RANGE_PIXELS: 400,
        cfg.STAT_FIRE_RATE_PER_SEC: 0.4,
        cfg.STAT_PROJECTILE_TYPE_ID: "mortar_shell",
        cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS: 180,
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "mortar.png",
    },
    "flamethrower_turret": {
        cfg.STAT_ID: "flamethrower_turret",
        cfg.STAT_COST_MONEY: 220, cfg.STAT_COST_IRON: 60,
        cfg.STAT_POWER_CONSUMPTION: 7,
        cfg.STAT_RANGE_PIXELS: 80,  # Range of flame particles
        cfg.STAT_FLAMETHROWER_DURATION_SEC: 4.0,  # How long it fires
        cfg.STAT_FLAMETHROWER_COOLDOWN_SEC: 2.0,  # Cooldown after firing
        cfg.STAT_PROJECTILE_TYPE_ID: "flame_particle",  # The particles it emits
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_FLAMETHROWER_CHARGE_SPRITE_NAME: "flame2.png",
        cfg.STAT_FLAMETHROWER_DISCHARGE_SPRITE_NAME: "flame.png",
    },
    "sniper_turret": {
        cfg.STAT_ID: "sniper_turret",
        cfg.STAT_COST_MONEY: 300, cfg.STAT_COST_IRON: 70,
        cfg.STAT_POWER_CONSUMPTION: 4,
        cfg.STAT_RANGE_PIXELS: 700,
        cfg.STAT_FIRE_RATE_PER_SEC: 0.3,
        cfg.STAT_PROJECTILE_TYPE_ID: "sniper_bullet",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "sniper.png",
    }
}

PROJECTILE_STATS = {
    "bullet": {  # Generic bullet, might be unused if specific types replace it
        cfg.STAT_ID: "bullet",
        cfg.STAT_DAMAGE_AMOUNT: 10,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 600,
        cfg.STAT_SPRITE_DEFAULT_NAME: "bullet.png",  # or a specific default like cfg.DEFAULT_BULLET_SPRITE_NAME
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 3.0,
    },
    "mortar_shell": {
        cfg.STAT_ID: "mortar_shell",
        cfg.STAT_DAMAGE_AMOUNT: 50,
        cfg.STAT_AOE_RADIUS_PIXELS: 50,
        cfg.STAT_SPRITE_DEFAULT_NAME: "mortar_shell.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 7.0,
    },
    "sniper_bullet": {
        cfg.STAT_ID: "sniper_bullet",
        cfg.STAT_DAMAGE_AMOUNT: 150,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 1000,
        cfg.STAT_SPRITE_DEFAULT_NAME: "sniper_bullet_placeholder.png",  # Create this asset
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 2.0,
    },
    "flame_particle": {
        cfg.STAT_ID: "flame_particle",
        cfg.STAT_DAMAGE_AMOUNT: 5,  # Damage per particle
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 100,  # Relatively slow, short range
        cfg.STAT_SPRITE_DEFAULT_NAME: "flame_particle_placeholder.png",  # Small flame particle sprite
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 0.5,  # Short lifetime
        cfg.STAT_AOE_RADIUS_PIXELS: 10,  # Small AOE or direct hit only
    },
    "machine_gun_beam": {
        cfg.STAT_ID: "machine_gun_beam",
        cfg.STAT_DAMAGE_AMOUNT: 3,
        cfg.STAT_PROJECTILE_IS_BEAM: True,  # Special flag for beam type
        cfg.STAT_PROJECTILE_BEAM_COLOR: cfg.COLOR_YELLOW,  # Color of the beam
        cfg.STAT_PROJECTILE_BEAM_DURATION_SEC: 0.07,  # Visual duration of the beam line
    }
}


# --- Fonctions utilitaires ---
def get_item_stats(item_type_string):
    if item_type_string in BUILDING_STATS: return BUILDING_STATS[item_type_string]
    if item_type_string in TURRET_STATS: return TURRET_STATS[item_type_string]
    if item_type_string in PROJECTILE_STATS: return PROJECTILE_STATS[item_type_string]
    return {}


def is_building_type(item_type_string): return item_type_string in BUILDING_STATS


def is_turret_type(item_type_string): return item_type_string in TURRET_STATS


# --- Classe de Base GameObject ---
class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.active = True
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.sprite = None
        self.original_sprite = None
        self.scaler = None

    def draw(self, surface):
        if self.active and self.sprite:
            surface.blit(self.sprite, self.rect.topleft)

    def update(self, delta_time, game_state_ref, scaler: util.Scaler):
        if self.scaler is None and scaler is not None:
            self.scaler = scaler


# --- Bâtiments ---
class Building(GameObject):  # Unchanged from previous version with frame logic
    _id_counter = 0

    def __init__(self, building_type, pixel_pos_topleft, grid_pos_tuple, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler
        Building._id_counter += 1
        self.id = Building._id_counter
        self.type = building_type
        self.grid_pos = grid_pos_tuple
        self.stats = BUILDING_STATS.get(self.type, {})
        self.is_reinforced_frame = False
        self.is_turret_platform = False
        self.cost_money = self.stats.get(cfg.STAT_COST_MONEY, 0)
        self.cost_iron = self.stats.get(cfg.STAT_COST_IRON, 0)
        self.power_production = self.stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        self.iron_production_pm = self.stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
        self.iron_storage_increase = self.stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
        self.adjacency_bonus_per_unit = self.stats.get(cfg.STAT_ADJACENCY_BONUS_VALUE, 0)
        self.current_adjacency_bonus_value = 0
        self.is_reinforced_foundation = self.stats.get("is_reinforced_foundation", False)
        self.sprites_dict = {}
        if cfg.STAT_SPRITE_VARIANTS_DICT in self.stats:
            for key, sprite_name in self.stats[cfg.STAT_SPRITE_VARIANTS_DICT].items():
                path = os.path.join(cfg.BUILDING_SPRITE_PATH, sprite_name)
                self.sprites_dict[key] = util.load_sprite(path)
        default_sprite_name_from_stats = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME)
        if self.type == "frame" and "default" in self.sprites_dict:
            self.original_sprite = self.sprites_dict["default"]
        elif "single" in self.sprites_dict and self.sprites_dict["single"]:
            self.original_sprite = self.sprites_dict["single"]
        elif default_sprite_name_from_stats:
            self.original_sprite = util.load_sprite(
                os.path.join(cfg.BUILDING_SPRITE_PATH, default_sprite_name_from_stats))
        else:
            self.original_sprite = None
        if self.original_sprite:
            self.sprite = util.scale_sprite_to_tile(self.original_sprite, self.scaler)
        else:
            if cfg.DEBUG_MODE: print(f"AVERTISSEMENT: Aucun sprite original trouvé pour {self.type}")
            tile_size = self.scaler.get_tile_size();
            self.sprite = pygame.Surface((tile_size, tile_size));
            self.sprite.fill(cfg.COLOR_MAGENTA)
        self.rect = self.sprite.get_rect(topleft=pixel_pos_topleft);
        self.is_functional = True

    def set_as_reinforced_frame(self, is_reinforced: bool):
        if self.type == "frame": self.is_reinforced_frame = is_reinforced; self._update_frame_sprite()

    def set_as_turret_platform(self, is_platform: bool):
        if self.type == "frame": self.is_turret_platform = is_platform; self._update_frame_sprite()

    def _update_frame_sprite(self):
        if self.type != "frame": return
        new_sprite_key = "default"
        if self.is_turret_platform and "turret_platform" in self.sprites_dict:
            new_sprite_key = "turret_platform"
        elif self.is_reinforced_frame and "reinforced" in self.sprites_dict:
            new_sprite_key = "reinforced"
        sprite_to_use = self.sprites_dict.get(new_sprite_key)
        if sprite_to_use:
            if self.original_sprite is not sprite_to_use: self.original_sprite = sprite_to_use; self.sprite = util.scale_sprite_to_tile(
                self.original_sprite, self.scaler)
        elif cfg.DEBUG_MODE:
            print(f"AVERTISSEMENT: Sprite pour frame state '{new_sprite_key}' non trouvé.")

    def update_sprite_based_on_context(self, game_grid_ref, grid_r, grid_c, scaler: util.Scaler):
        if self.type == "miner":
            above_is_miner, below_is_miner = False, False;
            row, col = grid_r, grid_c
            if row > 0 and game_grid_ref[row - 1][col] and game_grid_ref[row - 1][
                col].type == "miner": above_is_miner = True
            if row < len(game_grid_ref) - 1 and game_grid_ref[row + 1][col] and game_grid_ref[row + 1][
                col].type == "miner": below_is_miner = True
            chosen_sprite_key = "single"
            if above_is_miner and below_is_miner:
                chosen_sprite_key = "stacked_middle"
            elif below_is_miner:
                chosen_sprite_key = "stacked_top"
            elif above_is_miner:
                chosen_sprite_key = "stacked_bottom"
            if chosen_sprite_key in self.sprites_dict and self.original_sprite is not self.sprites_dict[
                chosen_sprite_key]:
                self.original_sprite = self.sprites_dict[chosen_sprite_key];
                self.sprite = util.scale_sprite_to_tile(self.original_sprite, scaler)
        elif self.type == "storage":
            pass

    def apply_adjacency_bonus_effect(self, adjacent_similar_items_count):
        if self.type == "storage" and self.adjacency_bonus_per_unit > 0: self.current_adjacency_bonus_value = adjacent_similar_items_count * self.adjacency_bonus_per_unit

    def set_active_state(self, is_powered):
        self.is_functional = is_powered

    def update(self, delta_time, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler)


# --- Tourelles ---
class Turret(GameObject):
    _id_counter = 0

    def __init__(self, turret_type, pixel_pos_center, grid_pos_tuple, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler
        Turret._id_counter += 1
        self.id = Turret._id_counter
        self.type = turret_type
        self.grid_pos = grid_pos_tuple
        self.stats = TURRET_STATS.get(self.type, {})

        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        self.range = self.scaler.scale_value(self.stats.get(cfg.STAT_RANGE_PIXELS, 0))
        self.min_range = self.scaler.scale_value(self.stats.get(cfg.STAT_MIN_RANGE_PIXELS, 0))
        self.max_range = self.scaler.scale_value(self.stats.get(cfg.STAT_MAX_RANGE_PIXELS, 0))

        self.fire_rate_per_sec = self.stats.get(cfg.STAT_FIRE_RATE_PER_SEC, 0)
        if self.fire_rate_per_sec > 0:
            self.cooldown_time_seconds = 1.0 / self.fire_rate_per_sec
        else:  # For turrets like flamethrower with different mechanics
            self.cooldown_time_seconds = float('inf')
        self.current_cooldown = 0.0

        self.projectile_type = self.stats.get(cfg.STAT_PROJECTILE_TYPE_ID, None)
        self.projectile_initial_speed = self.scaler.scale_value(
            self.stats.get(cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS, 0))

        base_sprite_name = self.stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME, "placeholder.png")
        self.original_turret_base_sprite = util.load_sprite(os.path.join(cfg.TURRET_SPRITE_PATH, base_sprite_name))

        self.is_flamethrower = (self.type == "flamethrower_turret")
        self.flame_duration_timer = 0.0
        self.flame_cooldown_timer = 0.0
        self.is_flaming_active = False
        self.original_flame_charge_sprite = None
        self.original_flame_discharge_sprite = None
        self.original_gun_sprite = None  # General gun sprite

        if self.is_flamethrower:
            self.flame_duration_max = self.stats.get(cfg.STAT_FLAMETHROWER_DURATION_SEC, 4.0)
            self.flame_cooldown_max = self.stats.get(cfg.STAT_FLAMETHROWER_COOLDOWN_SEC, 2.0)
            charge_sprite_name = self.stats.get(cfg.STAT_FLAMETHROWER_CHARGE_SPRITE_NAME)
            discharge_sprite_name = self.stats.get(cfg.STAT_FLAMETHROWER_DISCHARGE_SPRITE_NAME)
            if charge_sprite_name:
                self.original_flame_charge_sprite = util.load_sprite(
                    os.path.join(cfg.TURRET_SPRITE_PATH, charge_sprite_name))
            if discharge_sprite_name:
                self.original_flame_discharge_sprite = util.load_sprite(
                    os.path.join(cfg.TURRET_SPRITE_PATH, discharge_sprite_name))
            self.original_gun_sprite = self.original_flame_charge_sprite  # Start with charge sprite
        else:
            gun_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NAME, "placeholder.png")
            self.original_gun_sprite = util.load_sprite(os.path.join(cfg.TURRET_SPRITE_PATH, gun_sprite_name))

        if self.original_turret_base_sprite:
            scaled_base_w = int(self.scaler.tile_size * 0.8)
            scaled_base_h = int(self.scaler.tile_size * 0.8)
            self.turret_base_sprite_scaled = util.scale_sprite_to_size(self.original_turret_base_sprite, scaled_base_w,
                                                                       scaled_base_h)
        else:
            s = int(self.scaler.tile_size * 0.8)
            self.turret_base_sprite_scaled = pygame.Surface((s, s), pygame.SRCALPHA);
            self.turret_base_sprite_scaled.fill(cfg.COLOR_CYAN + (180,))

        self.gun_sprite_scaled_original = None
        if self.original_gun_sprite:
            gun_orig_w, gun_orig_h = self.original_gun_sprite.get_size()
            target_gun_h_factor = 0.8 if self.is_flamethrower else 0.5
            target_gun_h = self.scaler.tile_size * target_gun_h_factor
            scale_factor = target_gun_h / gun_orig_h if gun_orig_h > 0 else 1
            target_gun_w = gun_orig_w * scale_factor
            self.gun_sprite_scaled_original = util.scale_sprite_to_size(self.original_gun_sprite,
                                                                        int(max(1, target_gun_w)),
                                                                        int(max(1, target_gun_h)))

        if not self.gun_sprite_scaled_original:
            w_fb, h_fb = int(self.scaler.tile_size * 0.6), int(self.scaler.tile_size * 0.3)
            self.gun_sprite_scaled_original = pygame.Surface((w_fb, h_fb), pygame.SRCALPHA);
            self.gun_sprite_scaled_original.fill(cfg.COLOR_GREEN + (180,))

        self.gun_sprite_rotated = self.gun_sprite_scaled_original

        self.rect = self.turret_base_sprite_scaled.get_rect(center=pixel_pos_center)

        if self.gun_sprite_scaled_original:
            pivot_x_factor = 0.5 if self.is_flamethrower else 0.25
            self.gun_pivot_offset_in_gun_sprite = (self.gun_sprite_scaled_original.get_width() * pivot_x_factor,
                                                   self.gun_sprite_scaled_original.get_height() // 2)
        else:
            self.gun_pivot_offset_in_gun_sprite = (0, 0)

        self.target_enemy = None
        self.current_angle_deg = 0
        self.is_functional = True

    def _update_gun_sprite_visuals(self):
        if self.original_gun_sprite:
            gun_orig_w, gun_orig_h = self.original_gun_sprite.get_size()
            target_gun_h_factor = 0.8 if self.is_flamethrower else 0.5
            target_gun_h = self.scaler.tile_size * target_gun_h_factor
            scale_factor = target_gun_h / gun_orig_h if gun_orig_h > 0 else 1
            target_gun_w = gun_orig_w * scale_factor
            self.gun_sprite_scaled_original = util.scale_sprite_to_size(self.original_gun_sprite,
                                                                        int(max(1, target_gun_w)),
                                                                        int(max(1, target_gun_h)))
            self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
        else:
            w_fb, h_fb = int(self.scaler.tile_size * 0.6), int(self.scaler.tile_size * 0.3)
            self.gun_sprite_scaled_original = pygame.Surface((w_fb, h_fb), pygame.SRCALPHA);
            self.gun_sprite_scaled_original.fill(cfg.COLOR_GREEN + (180,))
            self.gun_sprite_rotated = self.gun_sprite_scaled_original  # Rotate this fallback if needed

    def find_target(self, enemies_list):
        self.target_enemy = None
        closest_dist_sq = float('inf')
        # Le rect de la tourelle (self.rect) est pour sa base, centrée sur la case.
        # Les calculs de distance se font à partir du centre de cette base.
        turret_center_x, turret_center_y = self.rect.centerx, self.rect.centery

        for enemy in enemies_list:
            if not enemy.active or not hasattr(enemy, 'rect'):  # S'assurer que l'ennemi est actif et a un rect
                continue

            # Distance au carré pour éviter sqrt pour la performance
            dist_sq = (enemy.rect.centerx - turret_center_x) ** 2 + (enemy.rect.centery - turret_center_y) ** 2

            target_in_range = False
            # self.range, self.min_range, self.max_range sont déjà des valeurs scalées (en pixels)
            # stockées lors de l'initialisation de la tourelle.

            if self.type == "mortar_turret":
                if self.min_range ** 2 <= dist_sq <= self.max_range ** 2:
                    target_in_range = True
            else:  # Pour les autres tourelles (machine_gun, flamethrower, sniper) qui ont un STAT_RANGE_PIXELS
                if dist_sq <= self.range ** 2:
                    target_in_range = True

            if target_in_range and dist_sq < closest_dist_sq:
                # Prioriser l'ennemi le plus avancé (le plus à gauche) si les distances sont similaires ?
                # Pour l'instant, juste le plus proche.
                closest_dist_sq = dist_sq
                self.target_enemy = enemy

        # Optionnel: si aucun ennemi n'est trouvé, s'assurer que target_enemy est bien None
        # if closest_dist_sq == float('inf'):
        #    self.target_enemy = None # Déjà fait au début de la fonction

    def update(self, delta_time, enemies_list, is_powered_globally, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler)
        self.set_active_state(is_powered_globally)

        if not self.active or not self.is_functional:
            self.target_enemy = None
            if self.is_flamethrower and self.is_flaming_active:
                self.is_flaming_active = False
                self.flame_cooldown_timer = self.flame_cooldown_max  # Start full cooldown
                self.original_gun_sprite = self.original_flame_charge_sprite
                self._update_gun_sprite_visuals()  # Update to charge sprite
            return

        # Target acquisition
        if not self.target_enemy or not self.target_enemy.active or not hasattr(self.target_enemy, 'rect'):
            self.find_target(enemies_list)

        # Aiming
        if self.target_enemy and hasattr(self.target_enemy, 'rect'):
            dx = self.target_enemy.rect.centerx - self.rect.centerx
            dy = self.target_enemy.rect.centery - self.rect.centery
            self.current_angle_deg = math.degrees(math.atan2(-dy, dx))
            if self.gun_sprite_scaled_original:  # Check if gun sprite exists
                self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original,
                                                                  self.current_angle_deg)
        elif not self.is_flamethrower:  # If not a flamethrower and no target, stop aiming logic for this frame
            self.target_enemy = None  # Clear target if it became invalid
            # Optionally, keep last angle or reset to a default for non-flamethrowers
            # self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
            return  # No target, no shooting for standard turrets

        # Firing logic
        if self.is_flamethrower:
            if self.is_flaming_active:
                self.flame_duration_timer -= delta_time
                if self.flame_duration_timer <= 0:
                    self.is_flaming_active = False
                    self.flame_cooldown_timer = self.flame_cooldown_max
                    self.original_gun_sprite = self.original_flame_charge_sprite
                    self._update_gun_sprite_visuals()
                else:
                    self.current_cooldown -= delta_time
                    if self.current_cooldown <= 0:
                        self.shoot(game_state_ref)  # Flamethrower shoots particles
                        self.current_cooldown = 0.1  # Interval between particle bursts
            else:  # Cooldown or ready to fire
                self.flame_cooldown_timer -= delta_time
                if self.flame_cooldown_timer <= 0 and self.target_enemy:  # Ready and has a target
                    self.is_flaming_active = True
                    self.flame_duration_timer = self.flame_duration_max
                    self.original_gun_sprite = self.original_flame_discharge_sprite
                    self._update_gun_sprite_visuals()
                    self.current_cooldown = 0  # Shoot first burst immediately
        else:  # Standard turrets (machine gun, mortar, sniper)
            self.current_cooldown -= delta_time
            if self.current_cooldown <= 0 and self.target_enemy:
                self.shoot(game_state_ref)
                self.current_cooldown = self.cooldown_time_seconds

    def shoot(self, game_state_ref):
        if not self.projectile_type: return  # Should not happen if stats are well defined
        if not self.target_enemy and not (self.is_flamethrower and self.is_flaming_active): return

        pivot_screen_x, pivot_screen_y = self.rect.centerx, self.rect.centery
        cannon_length_from_pivot = self.gun_sprite_scaled_original.get_width() - self.gun_pivot_offset_in_gun_sprite[0]
        proj_origin_x = pivot_screen_x + math.cos(math.radians(self.current_angle_deg)) * cannon_length_from_pivot
        proj_origin_y = pivot_screen_y - math.sin(math.radians(self.current_angle_deg)) * cannon_length_from_pivot
        proj_origin = (proj_origin_x, proj_origin_y)

        if self.is_flamethrower:
            num_flame_particles = 3
            for _ in range(num_flame_particles):
                dispersion = random.uniform(-15, 15)
                flame_angle = self.current_angle_deg + dispersion
                new_proj = Projectile("flame_particle", proj_origin, flame_angle, self.scaler)
                game_state_ref.projectiles.append(new_proj)
            return  # Flamethrower shoot is done

        # Ensure target exists for non-flamethrower types before proceeding
        if not self.target_enemy or not self.target_enemy.active: return

        if self.type == "mortar_turret":
            fire_solution = calculate_mortar_fire_solution(
                self.rect.center, self.target_enemy.rect.center,
                self.projectile_initial_speed, self.scaler.gravity)
            if fire_solution:
                launch_angle_rad_vertical, _ = fire_solution
                angle_horizontal_rad = math.radians(self.current_angle_deg)
                vy_physics = self.projectile_initial_speed * math.sin(launch_angle_rad_vertical)
                horizontal_speed_component = self.projectile_initial_speed * math.cos(launch_angle_rad_vertical)
                vx = horizontal_speed_component * math.cos(angle_horizontal_rad);
                vy_pygame = -vy_physics
                new_proj = Projectile(self.projectile_type, proj_origin, 0, self.scaler, initial_vx=vx,
                                      initial_vy=vy_pygame)
                game_state_ref.projectiles.append(new_proj)
        elif self.projectile_type == "machine_gun_beam":
            if self.target_enemy and self.target_enemy.active:
                damage_per_shot = PROJECTILE_STATS["machine_gun_beam"].get(cfg.STAT_DAMAGE_AMOUNT, 0)
                self.target_enemy.take_damage(damage_per_shot)
                if not self.target_enemy.active and hasattr(game_state_ref, 'money'):
                    game_state_ref.money += self.target_enemy.get_money_value()
                    game_state_ref.score += self.target_enemy.get_score_value()
                beam_projectile = Projectile(
                    self.projectile_type, proj_origin, self.current_angle_deg,
                    self.scaler, target_pos_for_beam=self.target_enemy.rect.center)
                game_state_ref.projectiles.append(beam_projectile)
        else:  # Sniper etc.
            new_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg, self.scaler)
            game_state_ref.projectiles.append(new_proj)

    def set_active_state(self, is_powered):  # Power state
        self.is_functional = is_powered

    def draw(self, surface):
        if not self.active: return
        if self.turret_base_sprite_scaled:
            surface.blit(self.turret_base_sprite_scaled, self.rect.topleft)
        if self.gun_sprite_rotated:
            # Simplified draw: center rotated gun on turret base center
            gun_display_rect = self.gun_sprite_rotated.get_rect(center=self.rect.center)
            surface.blit(self.gun_sprite_rotated, gun_display_rect.topleft)
        if cfg.DEBUG_MODE:
            pygame.draw.circle(surface, cfg.COLOR_RED, self.rect.center, 3)


class Projectile(GameObject):
    _id_counter = 0

    def __init__(self, projectile_type, origin_xy_pixels, angle_deg, scaler: util.Scaler,
                 initial_vx=None, initial_vy=None, target_pos_for_beam=None):
        super().__init__()
        self.scaler = scaler
        Projectile._id_counter += 1
        self.id = Projectile._id_counter
        self.type = projectile_type
        self.stats = PROJECTILE_STATS.get(self.type, {})

        self.damage = self.stats.get(cfg.STAT_DAMAGE_AMOUNT, 0)
        self.speed = self.scaler.scale_value(self.stats.get(cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS, 0))
        self.aoe_radius = self.scaler.scale_value(self.stats.get(cfg.STAT_AOE_RADIUS_PIXELS, 0))
        self.lifetime_seconds = self.stats.get(cfg.STAT_PROJECTILE_LIFETIME_SEC, 5.0)
        self.gravity_scaled = self.scaler.gravity

        self.is_beam = self.stats.get(cfg.STAT_PROJECTILE_IS_BEAM, False)
        self.beam_color = self.stats.get(cfg.STAT_PROJECTILE_BEAM_COLOR, cfg.COLOR_YELLOW)
        self.beam_target_pos = target_pos_for_beam
        self.origin_pos = origin_xy_pixels

        self.sprite = None
        self.original_sprite = None
        self.sprite_scaled_original = None

        if not self.is_beam:
            sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
            default_bullet_fallback_path = os.path.join(cfg.PROJECTILE_SPRITE_PATH,
                                                        getattr(cfg, 'DEFAULT_BULLET_SPRITE_NAME', "bullet.png"))

            self.original_sprite = util.load_sprite(
                os.path.join(cfg.PROJECTILE_SPRITE_PATH, sprite_name),
                specific_fallback_path=default_bullet_fallback_path
            )

            if self.original_sprite:
                base_proj_w = self.original_sprite.get_width()
                base_proj_h = self.original_sprite.get_height()
                target_h = self.scaler.tile_size * 0.2  # Example: 20% of tile height
                scale_f = target_h / base_proj_h if base_proj_h > 0 else 1
                target_w = base_proj_w * scale_f
                self.sprite_scaled_original = util.scale_sprite_to_size(self.original_sprite, int(max(1, target_w)),
                                                                        int(max(1, target_h)))
            else:
                fallback_size_px = self.scaler.scale_value(cfg.BASE_PROJECTILE_FALLBACK_SIZE)
                self.sprite_scaled_original = pygame.Surface((fallback_size_px, fallback_size_px), pygame.SRCALPHA)
                self.sprite_scaled_original.fill(cfg.COLOR_MAGENTA)

        self.is_mortar_shell = (self.type == "mortar_shell")
        if self.is_mortar_shell:
            self.vx = initial_vx if initial_vx is not None else 0
            self.vy_physics = -initial_vy if initial_vy is not None else 0
            self.sprite = self.sprite_scaled_original
        elif not self.is_beam and self.sprite_scaled_original:
            self.angle_rad = math.radians(angle_deg)
            self.vx = self.speed * math.cos(self.angle_rad)
            self.vy_physics = self.speed * math.sin(self.angle_rad)
            self.sprite = pygame.transform.rotate(self.sprite_scaled_original, angle_deg)

        if self.sprite:
            self.rect = self.sprite.get_rect(center=origin_xy_pixels)
        elif self.is_beam:
            self.rect = pygame.Rect(origin_xy_pixels[0] - 1, origin_xy_pixels[1] - 1, 2, 2)
        else:
            fb_size = self.scaler.scale_value(cfg.BASE_PROJECTILE_FALLBACK_SIZE)
            self.rect = pygame.Rect(origin_xy_pixels[0] - fb_size // 2, origin_xy_pixels[1] - fb_size // 2, fb_size,
                                    fb_size)
        self.has_impacted = False

    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):  # Logic identical
        if not self.active: return
        self.lifetime_seconds -= delta_time
        if self.lifetime_seconds <= 0:
            if self.is_mortar_shell and not self.has_impacted: self.on_hit(game_state_ref)
            self.active = False;
            return
        if self.is_beam:
            pass
        elif self.is_mortar_shell:
            self.rect.x += self.vx * delta_time;
            self.rect.y += -self.vy_physics * delta_time
            self.vy_physics -= self.gravity_scaled * delta_time
            if self.sprite_scaled_original:
                angle_rad = math.atan2(self.vy_physics, self.vx)
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, math.degrees(-angle_rad))
        else:
            self.rect.x += self.vx * delta_time; self.rect.y += -self.vy_physics * delta_time
        off_buf = self.scaler.scale_value(cfg.BASE_PROJECTILE_OFFSCREEN_BUFFER)
        usable_buf_rect = pygame.Rect(self.scaler.screen_origin_x - off_buf, self.scaler.screen_origin_y - off_buf,
                                      self.scaler.usable_w + 2 * off_buf, self.scaler.usable_h + 2 * off_buf)
        if not usable_buf_rect.colliderect(self.rect): self.active = False

    def on_hit(self, game_state_ref):  # Logic identical
        if self.is_mortar_shell and self.aoe_radius > 0 and hasattr(game_state_ref,
                                                                    'trigger_aoe_damage') and not self.has_impacted:
            game_state_ref.trigger_aoe_damage(self.rect.center, self.aoe_radius, self.damage)
            self.has_impacted = True
        self.active = False

    def draw(self, surface):  # Logic identical
        if not self.active: return
        if self.is_beam:
            if self.beam_target_pos and self.origin_pos:
                beam_duration = self.stats.get(cfg.STAT_PROJECTILE_BEAM_DURATION_SEC, 0.1)
                # Make beam fade or flicker based on remaining lifetime vs total beam duration for effect
                if self.lifetime_seconds > beam_duration * 0.1:  # Visible most of its short life
                    pygame.draw.line(surface, self.beam_color, self.origin_pos, self.beam_target_pos, 2)  # Thickness 2
        elif self.sprite:
            surface.blit(self.sprite, self.rect.topleft)


# --- Ennemis ---
class Enemy(GameObject):  # Unchanged from previous version with GLOBAL_ENEMY_SPRITE_SCALE_MULTIPLIER
    _id_counter = 0

    def __init__(self, initial_pos_xy_on_screen, enemy_type_id, variant_data, scaler: util.Scaler):
        super().__init__();
        self.scaler = scaler;
        Enemy._id_counter += 1;
        self.id = Enemy._id_counter
        self.type_id = enemy_type_id;
        self.stats = ENEMY_STATS.get(self.type_id, ENEMY_STATS[1])
        self.max_hp = self.stats.get(cfg.STAT_HP_MAX, 10);
        self.current_hp = self.max_hp
        self.speed_pixels_sec = self.scaler.scale_value(self.stats.get(cfg.STAT_MOVE_SPEED_PIXELS_SEC, 30))
        self.city_damage = self.stats.get(cfg.STAT_DAMAGE_TO_CITY, 1)
        self.score_value = self.stats.get(cfg.STAT_SCORE_POINTS_VALUE, 0)
        self.money_value = self.stats.get(cfg.STAT_MONEY_DROP_VALUE, 0)
        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(os.path.join(cfg.ENEMY_SPRITE_PATH, sprite_name))
        min_s, max_s = self.stats.get(cfg.STAT_SIZE_MIN_SCALE_FACTOR, 1.0), self.stats.get(
            cfg.STAT_SIZE_MAX_SCALE_FACTOR, 1.0)
        random_type_specific_scale_factor = random.uniform(min_s, max_s)
        global_scale_mult = getattr(cfg, 'GLOBAL_ENEMY_SPRITE_SCALE_MULTIPLIER', 1.0)
        final_random_scale_factor = random_type_specific_scale_factor * global_scale_mult
        if self.original_sprite:
            base_w, base_h = self.original_sprite.get_size()
            target_ref_w, target_ref_h = base_w * final_random_scale_factor, base_h * final_random_scale_factor
            scaled_w, scaled_h = max(1, self.scaler.scale_value(target_ref_w)), max(1, self.scaler.scale_value(
                target_ref_h))
            self.sprite = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)
        else:
            default_base_size = cfg.BASE_ENEMY_FALLBACK_SIZE
            scaled_fallback_size = max(1, self.scaler.scale_value(default_base_size * global_scale_mult))
            self.sprite = pygame.Surface((scaled_fallback_size, scaled_fallback_size), pygame.SRCALPHA);
            self.sprite.fill(cfg.COLOR_RED + (180,))
        if self.sprite:
            self.rect = self.sprite.get_rect(center=initial_pos_xy_on_screen)
        else:
            fb_base_size = cfg.BASE_ENEMY_FALLBACK_SIZE;
            fb_size = max(1, self.scaler.scale_value(fb_base_size * global_scale_mult))
            self.rect = pygame.Rect(initial_pos_xy_on_screen[0] - fb_size // 2,
                                    initial_pos_xy_on_screen[1] - fb_size // 2, fb_size, fb_size)
        hitbox_scale_w_stat, hitbox_scale_h_stat = self.stats.get(cfg.STAT_HITBOX_SCALE_FACTORS_WH, (0.8, 0.8))
        hitbox_width, hitbox_height = int(self.rect.width * hitbox_scale_w_stat), int(
            self.rect.height * hitbox_scale_h_stat)
        self.hitbox = pygame.Rect(0, 0, max(1, hitbox_width), max(1, hitbox_height));
        self.hitbox.center = self.rect.center



    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):  # Logic identical
        if not self.active: return
        self.rect.x -= self.speed_pixels_sec * delta_time;
        self.hitbox.center = self.rect.center
        if self.rect.right < self.scaler.screen_origin_x - self.scaler.scale_value(
            cfg.BASE_ENEMY_OFFSCREEN_DESPAWN_BUFFER): self.active = False

    def take_damage(self, amount):  # Logic identical
        if not self.active: return
        self.current_hp -= amount
        if self.current_hp <= 0: self.current_hp = 0; self.active = False

    def get_city_damage(self):
        return self.city_damage  # Logic identical

    def get_score_value(self):
        return self.score_value  # Logic identical

    def get_money_value(self):
        return self.money_value  # Logic identical

    def draw(self, surface):  # Logic identical
        super().draw(surface)
        if self.active and self.current_hp < self.max_hp and self.max_hp > 0:
            hp_bar_bg_color = getattr(cfg, 'COLOR_HP_BAR_BACKGROUND', cfg.COLOR_GREY_DARK)
            hp_bar_fill_color = getattr(cfg, 'COLOR_HP_FULL', cfg.COLOR_GREEN)
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio < 0.3:
                hp_bar_fill_color = getattr(cfg, 'COLOR_HP_CRITICAL', cfg.COLOR_RED)
            elif hp_ratio < 0.6:
                hp_bar_fill_color = getattr(cfg, 'COLOR_HP_LOW', cfg.COLOR_ORANGE)
            bar_w, bar_h, bar_offset_y = self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_WIDTH), self.scaler.scale_value(
                cfg.BASE_ENEMY_HP_BAR_HEIGHT), self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_OFFSET_Y)
            bg_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - bar_h - bar_offset_y, bar_w, bar_h)
            hp_fill_w = int(bar_w * hp_ratio);
            hp_rect = pygame.Rect(bg_rect.left, bg_rect.top, hp_fill_w, bar_h)
            pygame.draw.rect(surface, hp_bar_bg_color, bg_rect);
            pygame.draw.rect(surface, hp_bar_fill_color, hp_rect)


# --- Calcul de Trajectoire pour Mortier --- (Logic identical)
def calculate_mortar_fire_solution(turret_pos_pixels, target_pos_pixels, projectile_initial_speed_pixels,
                                   gravity_pixels_s2):
    dx_pixels = target_pos_pixels[0] - turret_pos_pixels[0];
    dy_physics = -(target_pos_pixels[1] - turret_pos_pixels[1])
    v0 = projectile_initial_speed_pixels;
    g = abs(gravity_pixels_s2)
    if abs(dx_pixels) < 1.0:
        if dy_physics > 0 and v0 ** 2 >= 2 * g * dy_physics:
            if (v0 ** 2 - 2 * g * dy_physics) < 0: return None
            time_to_target = (v0 - math.sqrt(max(0, v0 ** 2 - 2 * g * dy_physics))) / g
            return math.pi / 2, time_to_target
        return None
    discriminant = v0 ** 4 - g * (g * dx_pixels ** 2 + 2 * dy_physics * v0 ** 2)
    if discriminant < 0: return None
    sqrt_discriminant = math.sqrt(discriminant)
    try:
        if g * dx_pixels == 0: return None
        tan_theta_high = (v0 ** 2 + sqrt_discriminant) / (g * dx_pixels)
    except ZeroDivisionError:
        return None
    chosen_angle_rad = math.atan(tan_theta_high)
    cos_chosen_angle = math.cos(chosen_angle_rad)
    if abs(cos_chosen_angle) < 1e-6:
        if dy_physics > 0 and v0 ** 2 >= 2 * g * dy_physics:
            time_to_target = (v0 - math.sqrt(max(0, v0 ** 2 - 2 * g * dy_physics))) / g
            return math.pi / 2, time_to_target
        return None
    try:
        time_of_flight = dx_pixels / (v0 * cos_chosen_angle)
    except ZeroDivisionError:
        return None
    if time_of_flight < 0: return None
    return chosen_angle_rad, time_of_flight


# --- Effets de Particules --- (Logic identical)
class ParticleEffect(GameObject):
    def __init__(self, position_xy_abs, animation_frames_list_original, frame_duration, scaler: util.Scaler):
        super().__init__();
        self.scaler = scaler;
        self.frames = []
        if animation_frames_list_original:
            for f_original in animation_frames_list_original:
                if isinstance(f_original, pygame.Surface):
                    scaled_w = self.scaler.scale_value(f_original.get_width())
                    scaled_h = self.scaler.scale_value(f_original.get_height())
                    self.frames.append(util.scale_sprite_to_size(f_original, scaled_w, scaled_h))
        self.frame_duration = frame_duration;
        self.current_frame_index = 0;
        self.time_on_current_frame = 0
        if self.frames:
            self.sprite = self.frames[0]; self.rect = self.sprite.get_rect(center=position_xy_abs)
        else:
            self.sprite = None; self.rect = pygame.Rect(position_xy_abs[0], position_xy_abs[1], 0,
                                                        0); self.active = False

    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):
        if not self.active or not self.frames: return
        self.time_on_current_frame += delta_time
        if self.time_on_current_frame >= self.frame_duration:
            self.time_on_current_frame %= self.frame_duration
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                self.active = False
            else:
                self.sprite = self.frames[self.current_frame_index]
                if self.sprite: self.rect = self.sprite.get_rect(center=self.rect.center)