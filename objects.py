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
        cfg.STAT_COST_MONEY: cfg.FRAME_COST_MONEY,
        cfg.STAT_SPRITE_DEFAULT_NAME: "frame.png",
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            "default": "frame.png", "reinforced": "frame2.png", "turret_platform": "frame3.png"
        }
    },
    "foundation": {
        cfg.STAT_COST_MONEY: 0,
        cfg.STAT_SPRITE_DEFAULT_NAME: "fundations.png",
        "is_reinforced_foundation": True
    },
    "generator": {
        cfg.STAT_COST_MONEY: cfg.GENERATOR_COST_MONEY,
        cfg.STAT_POWER_PRODUCTION: cfg.GENERATOR_POWER_PRODUCTION,
        cfg.STAT_SPRITE_DEFAULT_NAME: "battery.png",
    },
    "miner": {
        cfg.STAT_COST_MONEY: cfg.MINER_COST_MONEY,
        # cfg.STAT_COST_IRON: cfg.MINER_COST_IRON, # Supprimé (ou mis à 0 dans game_config.py)
        cfg.STAT_POWER_CONSUMPTION: cfg.MINER_POWER_CONSUMPTION,
        cfg.STAT_IRON_PRODUCTION_PM: cfg.MINER_IRON_PRODUCTION_PM,
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            "single": "miner.png",
            "stacked_bottom": "miner_stacked_bottom.png",
            "stacked_middle": "miner_stacked_middle.png",
            "stacked_top": "miner_stacked_top.png",
        },
        cfg.STAT_SPRITE_DEFAULT_NAME: "miner.png",
    },
    "storage": {
        cfg.STAT_COST_MONEY: cfg.STORAGE_COST_MONEY,
        # No iron cost to build storage
        cfg.STAT_IRON_STORAGE_INCREASE: cfg.STORAGE_IRON_STORAGE_INCREASE,
        cfg.STAT_ADJACENCY_BONUS_VALUE: cfg.STORAGE_ADJACENCY_BONUS_VALUE,
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            "single": "storage.png",
        },
        cfg.STAT_SPRITE_DEFAULT_NAME: "storage.png",
    }
}

ENEMY_STATS = {
    1: {
        cfg.STAT_HP_MAX: cfg.ENEMY1_HP_MAX,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: cfg.ENEMY1_MOVE_SPEED_PIXELS_SEC,
        cfg.STAT_DAMAGE_TO_CITY: cfg.ENEMY1_DAMAGE_TO_CITY,
        cfg.STAT_SCORE_POINTS_VALUE: cfg.ENEMY1_SCORE_POINTS_VALUE,
        cfg.STAT_MONEY_DROP_VALUE: cfg.ENEMY1_MONEY_DROP_VALUE,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_basic_sketch.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.8, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.2,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.8, 0.8)
    },
    2: {
        cfg.STAT_HP_MAX: cfg.ENEMY2_HP_MAX,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: cfg.ENEMY2_MOVE_SPEED_PIXELS_SEC,
        cfg.STAT_DAMAGE_TO_CITY: cfg.ENEMY2_DAMAGE_TO_CITY,
        cfg.STAT_SCORE_POINTS_VALUE: cfg.ENEMY2_SCORE_POINTS_VALUE,
        cfg.STAT_MONEY_DROP_VALUE: cfg.ENEMY2_MONEY_DROP_VALUE,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_fast.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.7, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.0,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.7, 0.9)
    },
    3: {
        cfg.STAT_HP_MAX: cfg.ENEMY3_HP_MAX,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: cfg.ENEMY3_MOVE_SPEED_PIXELS_SEC,
        cfg.STAT_DAMAGE_TO_CITY: cfg.ENEMY3_DAMAGE_TO_CITY,
        cfg.STAT_SCORE_POINTS_VALUE: cfg.ENEMY3_SCORE_POINTS_VALUE,
        cfg.STAT_MONEY_DROP_VALUE: cfg.ENEMY3_MONEY_DROP_VALUE,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_tank.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 1.3, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.6,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.9, 0.9)
    },
}

TURRET_STATS = {
    "machine_gun_turret": {
        cfg.STAT_ID: "machine_gun_turret",
        cfg.STAT_COST_MONEY: cfg.MACHINE_GUN_COST_MONEY,
        cfg.STAT_IRON_COST_PER_SHOT: cfg.MACHINE_GUN_IRON_COST_PER_SHOT,
        cfg.STAT_POWER_CONSUMPTION: cfg.MACHINE_GUN_POWER_CONSUMPTION,
        cfg.STAT_RANGE_PIXELS: cfg.MACHINE_GUN_RANGE_PIXELS,
        cfg.STAT_FIRE_RATE_PER_SEC: cfg.MACHINE_GUN_FIRE_RATE_PER_SEC,
        cfg.STAT_PROJECTILE_TYPE_ID: "machine_gun_beam",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: cfg.MACHINE_GUN_SPRITE_HAS_AMMO,
        cfg.STAT_TURRET_GUN_SPRITE_NO_AMMO_NAME: cfg.MACHINE_GUN_SPRITE_NO_AMMO,
    },
    "mortar_turret": {
        cfg.STAT_ID: "mortar_turret",
        cfg.STAT_COST_MONEY: cfg.MORTAR_COST_MONEY,
        cfg.STAT_IRON_COST_PER_SHOT: cfg.MORTAR_IRON_COST_PER_SHOT,
        cfg.STAT_POWER_CONSUMPTION: cfg.MORTAR_POWER_CONSUMPTION,
        cfg.STAT_MIN_RANGE_PIXELS: cfg.MORTAR_MIN_RANGE_PIXELS,
        cfg.STAT_MAX_RANGE_PIXELS: cfg.MORTAR_MAX_RANGE_PIXELS,
        cfg.STAT_FIRE_RATE_PER_SEC: cfg.MORTAR_FIRE_RATE_PER_SEC,
        cfg.STAT_PROJECTILE_TYPE_ID: "mortar_shell",
        cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS: cfg.MORTAR_PROJECTILE_LAUNCH_SPEED_PIXELS,
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: cfg.MORTAR_SPRITE_HAS_AMMO,
        cfg.STAT_TURRET_GUN_SPRITE_NO_AMMO_NAME: cfg.MORTAR_SPRITE_NO_AMMO,
    },
    "flamethrower_turret": {
        cfg.STAT_ID: "flamethrower_turret",
        cfg.STAT_COST_MONEY: cfg.FLAMETHROWER_COST_MONEY,
        cfg.STAT_IRON_COST_PER_SHOT: cfg.FLAMETHROWER_IRON_COST_PER_PARTICLE_BURST,
        cfg.STAT_POWER_CONSUMPTION: cfg.FLAMETHROWER_POWER_CONSUMPTION,
        cfg.STAT_RANGE_PIXELS: cfg.FLAMETHROWER_RANGE_PIXELS,
        cfg.STAT_FLAMETHROWER_DURATION_SEC: cfg.FLAMETHROWER_DURATION_SEC,
        cfg.STAT_FLAMETHROWER_COOLDOWN_SEC: cfg.FLAMETHROWER_COOLDOWN_SEC,
        cfg.STAT_PROJECTILE_TYPE_ID: "flame_particle",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_FLAMETHROWER_CHARGE_SPRITE_NAME: cfg.FLAMETHROWER_SPRITE_HAS_AMMO,
        cfg.STAT_FLAMETHROWER_DISCHARGE_SPRITE_NAME: "flame.png",
        cfg.STAT_TURRET_GUN_SPRITE_NO_AMMO_NAME: cfg.FLAMETHROWER_SPRITE_NO_AMMO,
    },
    "sniper_turret": {
        cfg.STAT_ID: "sniper_turret",
        cfg.STAT_COST_MONEY: cfg.SNIPER_COST_MONEY,
        cfg.STAT_IRON_COST_PER_SHOT: cfg.SNIPER_IRON_COST_PER_SHOT,
        cfg.STAT_POWER_CONSUMPTION: cfg.SNIPER_POWER_CONSUMPTION,
        cfg.STAT_RANGE_PIXELS: cfg.SNIPER_RANGE_PIXELS,
        cfg.STAT_FIRE_RATE_PER_SEC: cfg.SNIPER_FIRE_RATE_PER_SEC,
        cfg.STAT_PROJECTILE_TYPE_ID: "sniper_bullet",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: cfg.SNIPER_SPRITE_HAS_AMMO,
        cfg.STAT_TURRET_GUN_SPRITE_NO_AMMO_NAME: cfg.SNIPER_SPRITE_NO_AMMO,
        cfg.STAT_TURRET_GUN_SPRITE_FIRING_NAME: cfg.SNIPER_SPRITE_FIRING_ANIM,
    }
}

PROJECTILE_STATS = {
    "bullet": {
        cfg.STAT_ID: "bullet",
        cfg.STAT_DAMAGE_AMOUNT: 10,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 600,
        cfg.STAT_SPRITE_DEFAULT_NAME: "bullet.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 3.0,
    },
    "mortar_shell": {
        cfg.STAT_ID: "mortar_shell",
        cfg.STAT_DAMAGE_AMOUNT: cfg.MORTAR_SHELL_DAMAGE,
        cfg.STAT_AOE_RADIUS_PIXELS: cfg.MORTAR_SHELL_AOE_RADIUS_PIXELS,
        cfg.STAT_SPRITE_DEFAULT_NAME: "mortar_shell.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: cfg.MORTAR_SHELL_LIFETIME_SEC,
    },
    "sniper_bullet": {
        cfg.STAT_ID: "sniper_bullet",
        cfg.STAT_DAMAGE_AMOUNT: cfg.SNIPER_BULLET_DAMAGE,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: cfg.SNIPER_BULLET_FLAT_SPEED_PIXELS,
        cfg.STAT_SPRITE_DEFAULT_NAME: "sniper_bullet_placeholder.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: cfg.SNIPER_BULLET_LIFETIME_SEC,
    },
    "flame_particle": {
        cfg.STAT_ID: "flame_particle",
        cfg.STAT_DAMAGE_AMOUNT: cfg.FLAME_PARTICLE_DAMAGE,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: cfg.FLAME_PARTICLE_FLAT_SPEED_PIXELS,
        cfg.STAT_SPRITE_DEFAULT_NAME: "flame_particle_placeholder.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: cfg.FLAME_PARTICLE_LIFETIME_SEC,
        cfg.STAT_AOE_RADIUS_PIXELS: cfg.FLAME_PARTICLE_AOE_RADIUS_PIXELS,
    },
    "machine_gun_beam": {
        cfg.STAT_ID: "machine_gun_beam",
        cfg.STAT_DAMAGE_AMOUNT: cfg.MACHINE_GUN_BEAM_DAMAGE_PER_SHOT,
        cfg.STAT_PROJECTILE_IS_BEAM: True,
        cfg.STAT_PROJECTILE_BEAM_COLOR: cfg.COLOR_YELLOW,
        cfg.STAT_PROJECTILE_BEAM_DURATION_SEC: cfg.MACHINE_GUN_BEAM_DURATION_SEC,
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
class Building(GameObject):
    _id_counter = 0

    def __init__(self, building_type, pixel_pos_topleft, grid_pos_tuple, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler
        Building._id_counter += 1;
        self.id = Building._id_counter
        self.type = building_type;
        self.grid_pos = grid_pos_tuple
        self.stats = BUILDING_STATS.get(self.type, {})
        self.is_reinforced_frame = False;
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
            if cfg.DEBUG_MODE: print(
                f"AVERTISSEMENT: Aucun sprite original trouvé pour {self.type}, création placeholder.")
            tile_size = self.scaler.get_tile_size()
            self.sprite = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA);
            self.sprite.fill(cfg.COLOR_MAGENTA + (180,))
        self.rect = self.sprite.get_rect(topleft=pixel_pos_topleft)
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
            if self.original_sprite is not sprite_to_use:
                self.original_sprite = sprite_to_use;
                self.sprite = util.scale_sprite_to_tile(self.original_sprite, self.scaler)
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

    def apply_adjacency_bonus_effect(self, adj_count):
        if self.type == "storage" and self.adjacency_bonus_per_unit > 0: self.current_adjacency_bonus_value = adj_count * self.adjacency_bonus_per_unit

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
        Turret._id_counter += 1;
        self.id = Turret._id_counter
        self.type = turret_type;
        self.grid_pos = grid_pos_tuple
        self.stats = TURRET_STATS.get(self.type, {})

        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        self.range = self.scaler.scale_value(self.stats.get(cfg.STAT_RANGE_PIXELS, 0))
        self.min_range = self.scaler.scale_value(self.stats.get(cfg.STAT_MIN_RANGE_PIXELS, 0))
        self.max_range = self.scaler.scale_value(self.stats.get(cfg.STAT_MAX_RANGE_PIXELS, 0))

        self.fire_rate_per_sec = self.stats.get(cfg.STAT_FIRE_RATE_PER_SEC, 0)
        if self.fire_rate_per_sec > 0:
            self.cooldown_time_seconds = 1.0 / self.fire_rate_per_sec
        else:
            self.cooldown_time_seconds = float('inf')
        self.current_cooldown = 0.0

        self.projectile_type = self.stats.get(cfg.STAT_PROJECTILE_TYPE_ID, None)
        self.projectile_initial_speed = self.scaler.scale_value(
            self.stats.get(cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS, 0))

        self.iron_cost_per_shot = self.stats.get(cfg.STAT_IRON_COST_PER_SHOT, 0)
        self.has_sufficient_iron = True
        self.original_gun_sprite_no_ammo = None
        self.original_gun_sprite_firing = None
        self.is_firing_animation = False
        self.firing_animation_timer = 0.0
        self.firing_animation_duration = 0.2

        base_sprite_name = self.stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME, "turret_base_placeholder.png")
        self.original_turret_base_sprite = util.load_sprite(os.path.join(cfg.TURRET_SPRITE_PATH, base_sprite_name))

        self.is_flamethrower = (self.type == "flamethrower_turret")
        self.flame_duration_timer = 0.0;
        self.flame_cooldown_timer = 0.0;
        self.is_flaming_active = False
        self.original_flame_charge_sprite, self.original_flame_discharge_sprite = None, None
        self.original_gun_sprite = None

        if self.is_flamethrower:
            self.flame_duration_max = self.stats.get(cfg.STAT_FLAMETHROWER_DURATION_SEC, 4.0)
            self.flame_cooldown_max = self.stats.get(cfg.STAT_FLAMETHROWER_COOLDOWN_SEC, 2.0)
            charge_name = self.stats.get(cfg.STAT_FLAMETHROWER_CHARGE_SPRITE_NAME)
            discharge_name = self.stats.get(cfg.STAT_FLAMETHROWER_DISCHARGE_SPRITE_NAME)
            if charge_name: self.original_flame_charge_sprite = util.load_sprite(
                os.path.join(cfg.TURRET_SPRITE_PATH, charge_name))
            if discharge_name: self.original_flame_discharge_sprite = util.load_sprite(
                os.path.join(cfg.TURRET_SPRITE_PATH, discharge_name))

            no_ammo_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NO_AMMO_NAME)
            if no_ammo_sprite_name:
                self.original_gun_sprite_no_ammo = util.load_sprite(
                    os.path.join(cfg.TURRET_SPRITE_PATH, no_ammo_sprite_name))
            self.original_gun_sprite = self.original_flame_charge_sprite
        else:
            gun_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NAME)
            if gun_sprite_name:
                self.original_gun_sprite = util.load_sprite(os.path.join(cfg.TURRET_SPRITE_PATH, gun_sprite_name))

            no_ammo_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NO_AMMO_NAME)
            if no_ammo_sprite_name:
                self.original_gun_sprite_no_ammo = util.load_sprite(
                    os.path.join(cfg.TURRET_SPRITE_PATH, no_ammo_sprite_name))

            if self.type == "sniper_turret":
                firing_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_FIRING_NAME)
                if firing_sprite_name:
                    self.original_gun_sprite_firing = util.load_sprite(
                        os.path.join(cfg.TURRET_SPRITE_PATH, firing_sprite_name))

        current_initial_gun_sprite = self.original_gun_sprite
        if not current_initial_gun_sprite:
            current_initial_gun_sprite = self.original_gun_sprite_no_ammo

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
        if current_initial_gun_sprite:
            gun_orig_w, gun_orig_h = current_initial_gun_sprite.get_size()

            if self.type in ["machine_gun_turret", "mortar_turret", "sniper_turret"]:
                target_gun_h_factor = 0.8
            elif self.is_flamethrower:
                target_gun_h_factor = 0.8
            else:
                target_gun_h_factor = 0.5

            target_gun_h = self.scaler.tile_size * target_gun_h_factor
            scale_factor = target_gun_h / gun_orig_h if gun_orig_h > 0 else 1.0
            target_gun_w = gun_orig_w * scale_factor
            self.gun_sprite_scaled_original = util.scale_sprite_to_size(current_initial_gun_sprite,
                                                                        int(max(1, target_gun_w)),
                                                                        int(max(1, target_gun_h)))

        if not self.gun_sprite_scaled_original:
            if cfg.DEBUG_MODE: print(
                f"AVERTISSEMENT: Echec chargement/scaling canon initial pour {self.type}. Fallback.")
            fb_w, fb_h = int(self.scaler.tile_size * 0.6), int(self.scaler.tile_size * 0.3)
            self.gun_sprite_scaled_original = pygame.Surface((fb_w, fb_h), pygame.SRCALPHA);
            self.gun_sprite_scaled_original.fill(cfg.COLOR_GREEN + (180,))

        self.gun_sprite_rotated = self.gun_sprite_scaled_original
        self.rect = self.turret_base_sprite_scaled.get_rect(center=pixel_pos_center)

        if self.gun_sprite_scaled_original:
            self.gun_pivot_offset_in_gun_sprite = (self.gun_sprite_scaled_original.get_width() // 2,
                                                   self.gun_sprite_scaled_original.get_height() // 2)
        else:
            self.gun_pivot_offset_in_gun_sprite = (0, 0)

        self.target_enemy = None;
        self.current_angle_deg = 0;
        self.is_functional = True
        self._update_gun_sprite_visuals()

    def find_target(self, enemies_list):
        self.target_enemy = None
        closest_dist_sq = float('inf')
        turret_center_x, turret_center_y = self.rect.centerx, self.rect.centery

        for enemy in enemies_list:
            if not enemy.active or not hasattr(enemy, 'rect'):
                continue

            dist_sq = (enemy.rect.centerx - turret_center_x) ** 2 + (enemy.rect.centery - turret_center_y) ** 2

            target_in_range = False
            if self.type == "mortar_turret":
                if self.min_range ** 2 <= dist_sq <= self.max_range ** 2:
                    target_in_range = True
            else:
                if dist_sq <= self.range ** 2:
                    target_in_range = True

            if target_in_range and dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                self.target_enemy = enemy

    def _update_gun_sprite_visuals(self):
        current_original_gun_to_use = None
        if self.is_firing_animation:
            current_original_gun_to_use = self.original_gun_sprite_firing
        elif self.is_flamethrower:
            if self.is_flaming_active:
                current_original_gun_to_use = self.original_flame_discharge_sprite
            elif self.has_sufficient_iron:
                current_original_gun_to_use = self.original_flame_charge_sprite
            else:
                current_original_gun_to_use = self.original_gun_sprite_no_ammo
        else:
            if self.has_sufficient_iron:
                current_original_gun_to_use = self.original_gun_sprite
            else:
                current_original_gun_to_use = self.original_gun_sprite_no_ammo

        if not current_original_gun_to_use:
            current_original_gun_to_use = self.original_gun_sprite
        if not current_original_gun_to_use:
            current_original_gun_to_use = self.original_gun_sprite_no_ammo

        rescale_needed = (self.original_gun_sprite != current_original_gun_to_use) or \
                         (self.gun_sprite_scaled_original is None) or \
                         (self.original_gun_sprite is None and current_original_gun_to_use is not None)

        if rescale_needed:
            self.original_gun_sprite = current_original_gun_to_use

            if self.original_gun_sprite:
                gun_orig_w, gun_orig_h = self.original_gun_sprite.get_size()

                if self.type in ["machine_gun_turret", "mortar_turret", "sniper_turret"]:
                    target_gun_h_factor = 0.8
                elif self.is_flamethrower:
                    target_gun_h_factor = 0.8
                else:
                    target_gun_h_factor = 0.5

                target_gun_h = self.scaler.tile_size * target_gun_h_factor
                scale_factor = target_gun_h / gun_orig_h if gun_orig_h > 0 else 1.0
                target_gun_w = gun_orig_w * scale_factor
                self.gun_sprite_scaled_original = util.scale_sprite_to_size(self.original_gun_sprite,
                                                                            int(max(1, target_gun_w)),
                                                                            int(max(1, target_gun_h)))
                self.gun_pivot_offset_in_gun_sprite = (self.gun_sprite_scaled_original.get_width() // 2,
                                                       self.gun_sprite_scaled_original.get_height() // 2)
            else:
                if cfg.DEBUG_MODE: print(
                    f"AVERTISSEMENT: current_original_gun_to_use est None dans _update_gun_sprite_visuals pour {self.type}")
                fb_w, fb_h = int(self.scaler.tile_size * 0.6), int(self.scaler.tile_size * 0.3)
                self.gun_sprite_scaled_original = pygame.Surface((fb_w, fb_h), pygame.SRCALPHA);
                self.gun_sprite_scaled_original.fill(cfg.COLOR_GREEN + (180,))
                self.gun_pivot_offset_in_gun_sprite = (
                self.gun_sprite_scaled_original.get_width() // 2, self.gun_sprite_scaled_original.get_height() // 2)

        if self.gun_sprite_scaled_original:
            self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
        else:
            self.gun_sprite_rotated = None
            if cfg.DEBUG_MODE: print(f"ERREUR: gun_sprite_scaled_original est None après update pour {self.type}")


    def update(self, delta_time, enemies_list, is_powered_globally, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler)
        self.set_active_state(is_powered_globally)

        current_iron_check = (game_state_ref.iron_stock >= self.iron_cost_per_shot) or (self.iron_cost_per_shot == 0)
        visual_update_needed = False
        if self.has_sufficient_iron != current_iron_check:
            self.has_sufficient_iron = current_iron_check;
            visual_update_needed = True

        if self.is_firing_animation:
            self.firing_animation_timer -= delta_time
            if self.firing_animation_timer <= 0:
                self.is_firing_animation = False;
                visual_update_needed = True

        if visual_update_needed and not (
                self.is_flamethrower and self.is_flaming_active) and not self.is_firing_animation:
            self._update_gun_sprite_visuals()

        if not self.active or not self.is_functional:
            if self.is_flamethrower and self.is_flaming_active:
                self.is_flaming_active = False;
                self.flame_cooldown_timer = self.flame_cooldown_max
                self._update_gun_sprite_visuals()
            return

        old_angle = self.current_angle_deg
        if not self.target_enemy or not self.target_enemy.active or not hasattr(self.target_enemy, 'rect'):
            self.find_target(enemies_list)

        aim_this_frame = False
        if self.target_enemy and hasattr(self.target_enemy, 'rect'):
            aim_this_frame = True
            dx = self.target_enemy.rect.centerx - self.rect.centerx;
            dy = self.target_enemy.rect.centery - self.rect.centery
            self.current_angle_deg = math.degrees(math.atan2(-dy, dx))
        elif self.is_flamethrower and self.is_flaming_active:
            aim_this_frame = True

        if aim_this_frame and not self.is_firing_animation:
            if self.current_angle_deg != old_angle or self.gun_sprite_rotated is None: self._update_gun_sprite_visuals()

        if not self.has_sufficient_iron and not (self.is_flamethrower and self.is_flaming_active): return

        if self.is_flamethrower:
            if self.is_flaming_active:
                self.flame_duration_timer -= delta_time
                if self.flame_duration_timer <= 0:
                    self.is_flaming_active = False;
                    self.flame_cooldown_timer = self.flame_cooldown_max
                    self._update_gun_sprite_visuals()
                else:
                    self.current_cooldown -= delta_time
                    if self.current_cooldown <= 0: self.shoot(game_state_ref); self.current_cooldown = 0.1
            else:
                self.flame_cooldown_timer -= delta_time
                if self.flame_cooldown_timer <= 0 and self.target_enemy and self.has_sufficient_iron:
                    self.is_flaming_active = True;
                    self.flame_duration_timer = self.flame_duration_max
                    self._update_gun_sprite_visuals();
                    self.current_cooldown = 0
        else:
            self.current_cooldown -= delta_time
            if self.current_cooldown <= 0 and self.target_enemy and self.has_sufficient_iron:
                self.shoot(game_state_ref);
                self.current_cooldown = self.cooldown_time_seconds
                if self.type == "sniper_turret" and self.original_gun_sprite_firing:
                    self.is_firing_animation = True;
                    self.firing_animation_timer = self.firing_animation_duration
                    self._update_gun_sprite_visuals()

        new_has_iron_after_shot = (game_state_ref.iron_stock >= self.iron_cost_per_shot) or (
                self.iron_cost_per_shot == 0)
        if self.has_sufficient_iron and not new_has_iron_after_shot and not self.is_firing_animation:
            self.has_sufficient_iron = False;
            self._update_gun_sprite_visuals()

    def shoot(self, game_state_ref):
        if not self.projectile_type: return
        if not self.target_enemy and not (self.is_flamethrower and self.is_flaming_active): return

        if self.iron_cost_per_shot > 0:
            if game_state_ref.iron_stock < self.iron_cost_per_shot:
                self.has_sufficient_iron = False
                if cfg.DEBUG_MODE: print(f"Tourelle {self.type} à court de fer pour tirer (vérification dans shoot).")
                return
            game_state_ref.iron_stock -= self.iron_cost_per_shot
            self.has_sufficient_iron = (game_state_ref.iron_stock >= self.iron_cost_per_shot) or (
                    self.iron_cost_per_shot == 0)

        pivot_screen_x, pivot_screen_y = self.rect.centerx, self.rect.centery
        cannon_length_from_pivot = 0
        if self.gun_sprite_scaled_original and self.gun_pivot_offset_in_gun_sprite:
            cannon_length_from_pivot = self.gun_sprite_scaled_original.get_width() - \
                                       self.gun_pivot_offset_in_gun_sprite[0]
        proj_origin_x = pivot_screen_x + math.cos(math.radians(self.current_angle_deg)) * cannon_length_from_pivot
        proj_origin_y = pivot_screen_y - math.sin(math.radians(self.current_angle_deg)) * cannon_length_from_pivot
        proj_origin = (proj_origin_x, proj_origin_y)

        if self.is_flamethrower:
            num_flame_particles = 3
            for _ in range(num_flame_particles):
                dispersion = random.uniform(-15, 15);
                flame_angle = self.current_angle_deg + dispersion
                new_proj = Projectile("flame_particle", proj_origin, flame_angle, self.scaler)
                game_state_ref.projectiles.append(new_proj)
            return

        if not self.target_enemy or not self.target_enemy.active: return

        if self.type == "mortar_turret":
            fire_solution = calculate_mortar_fire_solution(self.rect.center, self.target_enemy.rect.center,
                                                           self.projectile_initial_speed, self.scaler.gravity)
            if fire_solution:
                launch_angle_vert, _ = fire_solution;
                angle_horiz_rad = math.radians(self.current_angle_deg)
                vy_phys = self.projectile_initial_speed * math.sin(launch_angle_vert)
                h_speed_comp = self.projectile_initial_speed * math.cos(launch_angle_vert)
                vx = h_speed_comp * math.cos(angle_horiz_rad);
                vy_pg = -vy_phys
                new_proj = Projectile(self.projectile_type, proj_origin, 0, self.scaler, initial_vx=vx,
                                      initial_vy=vy_pg)
                game_state_ref.projectiles.append(new_proj)
        elif self.projectile_type == "machine_gun_beam":
            if self.target_enemy and self.target_enemy.active:
                dmg = PROJECTILE_STATS["machine_gun_beam"].get(cfg.STAT_DAMAGE_AMOUNT, 0)
                self.target_enemy.take_damage(dmg)
                if not self.target_enemy.active and hasattr(game_state_ref, 'money'):
                    game_state_ref.money += self.target_enemy.get_money_value();
                    game_state_ref.score += self.target_enemy.get_score_value()
                beam_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg, self.scaler,
                                       target_pos_for_beam=self.target_enemy.rect.center)
                game_state_ref.projectiles.append(beam_proj)
        else:
            new_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg, self.scaler)
            game_state_ref.projectiles.append(new_proj)

    def set_active_state(self, is_powered):
        self.is_functional = is_powered

    def draw(self, surface):
        if not self.active:
            return

        if self.turret_base_sprite_scaled:
            surface.blit(self.turret_base_sprite_scaled, self.rect.topleft)
        elif cfg.DEBUG_MODE:
            pygame.draw.circle(surface, cfg.COLOR_CYAN, self.rect.center, self.scaler.tile_size // 3, 2)

        if self.gun_sprite_rotated and self.gun_sprite_scaled_original:
            pivot_screen_pos = self.rect.center

            pivot_in_scaled_orig_x, pivot_in_scaled_orig_y = self.gun_pivot_offset_in_gun_sprite

            offset_pivot_from_center_x = pivot_in_scaled_orig_x - self.gun_sprite_scaled_original.get_width() / 2
            offset_pivot_from_center_y = pivot_in_scaled_orig_y - self.gun_sprite_scaled_original.get_height() / 2

            angle_rad_math = -math.radians(self.current_angle_deg)

            rotated_offset_x = offset_pivot_from_center_x * math.cos(
                angle_rad_math) - offset_pivot_from_center_y * math.sin(angle_rad_math)
            rotated_offset_y = offset_pivot_from_center_x * math.sin(
                angle_rad_math) + offset_pivot_from_center_y * math.cos(angle_rad_math)

            rotated_sprite_center_x = pivot_screen_pos[0] - rotated_offset_x
            rotated_sprite_center_y = pivot_screen_pos[1] - rotated_offset_y

            gun_display_rect = self.gun_sprite_rotated.get_rect(
                center=(rotated_sprite_center_x, rotated_sprite_center_y))

            surface.blit(self.gun_sprite_rotated, gun_display_rect.topleft)

            if cfg.DEBUG_MODE:
                self.gun_final_draw_pos_topleft = gun_display_rect.topleft
        elif cfg.DEBUG_MODE:
            if self.gun_sprite_scaled_original:
                temp_rotated_fallback = pygame.transform.rotate(self.gun_sprite_scaled_original,
                                                                self.current_angle_deg)
                fb_gun_rect = temp_rotated_fallback.get_rect(center=self.rect.center)
                surface.blit(temp_rotated_fallback, fb_gun_rect.topleft)
            else:
                placeholder_gun_rect = pygame.Rect(0, 0, self.scaler.tile_size * 0.5, self.scaler.tile_size * 0.2);
                placeholder_gun_rect.center = self.rect.center
                pygame.draw.rect(surface, cfg.COLOR_MAGENTA, placeholder_gun_rect)

        if cfg.DEBUG_MODE:
            pygame.draw.circle(surface, cfg.COLOR_RED, self.rect.center, 3)
            if self.gun_sprite_rotated and hasattr(self, 'gun_final_draw_pos_topleft'):
                debug_gun_rect = self.gun_sprite_rotated.get_rect(topleft=self.gun_final_draw_pos_topleft);
                pygame.draw.rect(surface, cfg.COLOR_YELLOW, debug_gun_rect, 1)


# --- Projectiles ---
class Projectile(GameObject):
    _id_counter = 0

    def __init__(self, projectile_type, origin_xy_pixels, angle_deg, scaler: util.Scaler,
                 initial_vx=None, initial_vy=None, target_pos_for_beam=None):
        super().__init__();
        self.scaler = scaler
        Projectile._id_counter += 1;
        self.id = Projectile._id_counter
        self.type = projectile_type;
        self.stats = PROJECTILE_STATS.get(self.type, {})
        self.damage = self.stats.get(cfg.STAT_DAMAGE_AMOUNT, 0)
        self.speed = self.scaler.scale_value(self.stats.get(cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS, 0))
        self.aoe_radius = self.scaler.scale_value(self.stats.get(cfg.STAT_AOE_RADIUS_PIXELS, 0))
        self.lifetime_seconds = self.stats.get(cfg.STAT_PROJECTILE_LIFETIME_SEC, 5.0)
        self.gravity_scaled = self.scaler.gravity
        self.is_beam = self.stats.get(cfg.STAT_PROJECTILE_IS_BEAM, False)
        self.beam_color = self.stats.get(cfg.STAT_PROJECTILE_BEAM_COLOR, cfg.COLOR_YELLOW)
        self.beam_target_pos = target_pos_for_beam;
        self.origin_pos = origin_xy_pixels
        self.sprite = None;
        self.original_sprite = None;
        self.sprite_scaled_original = None
        if not self.is_beam:
            sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
            fallback_path = os.path.join(cfg.PROJECTILE_SPRITE_PATH, cfg.DEFAULT_BULLET_SPRITE_NAME)
            self.original_sprite = util.load_sprite(os.path.join(cfg.PROJECTILE_SPRITE_PATH, sprite_name),
                                                    specific_fallback_path=fallback_path)
            if self.original_sprite:
                b_w, b_h = self.original_sprite.get_size()
                t_h = self.scaler.tile_size * cfg.BASE_PROJECTILE_SPRITE_SCALE_FACTOR
                s_f = t_h / b_h if b_h > 0 else 1
                t_w = b_w * s_f
                self.sprite_scaled_original = util.scale_sprite_to_size(self.original_sprite, int(max(1, t_w)),
                                                                        int(max(1, t_h)))
            else:
                fb_size_px = self.scaler.scale_value(cfg.BASE_PROJECTILE_FALLBACK_SIZE)
                self.sprite_scaled_original = pygame.Surface((fb_size_px, fb_size_px), pygame.SRCALPHA);
                self.sprite_scaled_original.fill(cfg.COLOR_MAGENTA + (180,))
        self.is_mortar_shell = (self.type == "mortar_shell")
        if self.is_mortar_shell:
            self.vx = initial_vx or 0;
            self.vy_physics = -initial_vy if initial_vy is not None else 0
            self.sprite = self.sprite_scaled_original
        elif not self.is_beam and self.sprite_scaled_original:
            self.angle_rad = math.radians(angle_deg)
            self.vx = self.speed * math.cos(self.angle_rad);
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

    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):
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
                angle_rad_traj = math.atan2(self.vy_physics, self.vx)
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, math.degrees(-angle_rad_traj))
        else:
            self.rect.x += self.vx * delta_time;
            self.rect.y += -self.vy_physics * delta_time
        off_buf = self.scaler.scale_value(cfg.BASE_PROJECTILE_OFFSCREEN_BUFFER)
        screen_bounds_with_buffer = pygame.Rect(-off_buf, -off_buf, self.scaler.actual_w + 2 * off_buf,
                                                self.scaler.actual_h + 2 * off_buf)
        if not screen_bounds_with_buffer.colliderect(self.rect): self.active = False

    def on_hit(self, game_state_ref):
        if self.is_mortar_shell and self.aoe_radius > 0 and hasattr(game_state_ref,
                                                                    'trigger_aoe_damage') and not self.has_impacted:
            game_state_ref.trigger_aoe_damage(self.rect.center, self.aoe_radius, self.damage)
            self.has_impacted = True
        self.active = False

    def draw(self, surface):
        if not self.active: return
        if self.is_beam:
            if self.beam_target_pos and self.origin_pos:
                beam_total_duration = self.stats.get(cfg.STAT_PROJECTILE_BEAM_DURATION_SEC, 0.1)
                if self.lifetime_seconds > beam_total_duration * 0.2:
                    pygame.draw.line(surface, self.beam_color, self.origin_pos, self.beam_target_pos, 2)
        elif self.sprite:
            surface.blit(self.sprite, self.rect.topleft)


# --- Ennemis ---
class Enemy(GameObject):
    _id_counter = 0

    def __init__(self, initial_pos_xy_on_screen, enemy_type_id, variant_data, scaler: util.Scaler):
        super().__init__();
        self.scaler = scaler
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
        rand_type_scale = random.uniform(min_s, max_s)
        glob_scale_mult = getattr(cfg, 'GLOBAL_ENEMY_SPRITE_SCALE_MULTIPLIER', 1.0)
        final_scale = rand_type_scale * glob_scale_mult
        if self.original_sprite:
            b_w, b_h = self.original_sprite.get_size()
            t_ref_w, t_ref_h = b_w * final_scale, b_h * final_scale
            s_w, s_h = max(1, self.scaler.scale_value(t_ref_w)), max(1, self.scaler.scale_value(t_ref_h))
            self.sprite = util.scale_sprite_to_size(self.original_sprite, s_w, s_h)
        else:
            def_base_size = cfg.BASE_ENEMY_FALLBACK_SIZE
            s_fb_size = max(1, self.scaler.scale_value(def_base_size * glob_scale_mult))
            self.sprite = pygame.Surface((s_fb_size, s_fb_size), pygame.SRCALPHA);
            self.sprite.fill(cfg.COLOR_RED + (180,))
        if self.sprite:
            self.rect = self.sprite.get_rect(center=initial_pos_xy_on_screen)
        else:
            fb_b_size = cfg.BASE_ENEMY_FALLBACK_SIZE;
            fb_s = max(1, self.scaler.scale_value(fb_b_size * glob_scale_mult))
            self.rect = pygame.Rect(initial_pos_xy_on_screen[0] - fb_s // 2, initial_pos_xy_on_screen[1] - fb_s // 2,
                                    fb_s, fb_s)
        hb_s_w, hb_s_h = self.stats.get(cfg.STAT_HITBOX_SCALE_FACTORS_WH, (0.8, 0.8))
        hb_w, hb_h = int(self.rect.width * hb_s_w), int(self.rect.height * hb_s_h)
        self.hitbox = pygame.Rect(0, 0, max(1, hb_w), max(1, hb_h));
        self.hitbox.center = self.rect.center

    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):
        if not self.active: return
        self.rect.x -= self.speed_pixels_sec * delta_time;
        self.hitbox.center = self.rect.center
        despawn_x_limit = self.scaler.screen_origin_x - self.scaler.scale_value(cfg.BASE_ENEMY_OFFSCREEN_DESPAWN_BUFFER)
        if self.rect.right < despawn_x_limit: self.active = False

    def take_damage(self, amount):
        if not self.active: return
        self.current_hp -= amount
        if self.current_hp <= 0: self.current_hp = 0; self.active = False

    def get_city_damage(self):
        return self.city_damage

    def get_score_value(self):
        return self.score_value

    def get_money_value(self):
        return self.money_value

    def draw(self, surface):
        super().draw(surface)
        if self.active and self.current_hp < self.max_hp and self.max_hp > 0:
            bar_bg_col = getattr(cfg, 'COLOR_HP_BAR_BACKGROUND', cfg.COLOR_GREY_DARK)
            bar_fill_col = getattr(cfg, 'COLOR_HP_FULL', cfg.COLOR_GREEN)
            hp_r = self.current_hp / self.max_hp
            if hp_r < 0.3:
                bar_fill_col = getattr(cfg, 'COLOR_HP_CRITICAL', cfg.COLOR_RED)
            elif hp_r < 0.6:
                bar_fill_col = getattr(cfg, 'COLOR_HP_LOW', cfg.COLOR_ORANGE)
            bar_w, bar_h, bar_off_y = self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_WIDTH), self.scaler.scale_value(
                cfg.BASE_ENEMY_HP_BAR_HEIGHT), self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_OFFSET_Y)
            bg_r = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - bar_h - bar_off_y, bar_w, bar_h)
            hp_fill_w = int(bar_w * hp_r);
            hp_r_rect = pygame.Rect(bg_r.left, bg_r.top, hp_fill_w, bar_h)
            pygame.draw.rect(surface, bar_bg_col, bg_r);
            pygame.draw.rect(surface, bar_fill_col, hp_r_rect)


# --- Calcul de Trajectoire pour Mortier ---
def calculate_mortar_fire_solution(turret_pos_pixels, target_pos_pixels, projectile_initial_speed_pixels,
                                   gravity_pixels_s2):
    dx = target_pos_pixels[0] - turret_pos_pixels[0];
    dy_phys = -(target_pos_pixels[1] - turret_pos_pixels[1])
    v0 = projectile_initial_speed_pixels;
    g = abs(gravity_pixels_s2)
    if abs(dx) < 1.0:
        if dy_phys > 0 and v0 ** 2 >= 2 * g * dy_phys:
            if (v0 ** 2 - 2 * g * dy_phys) < 0: return None
            t = (v0 - math.sqrt(max(0, v0 ** 2 - 2 * g * dy_phys))) / g;
            return math.pi / 2, t
        return None
    discriminant = v0 ** 4 - g * (g * dx ** 2 + 2 * dy_phys * v0 ** 2)
    if discriminant < 0: return None
    sqrt_disc = math.sqrt(discriminant)
    try:
        if g * dx == 0: return None
        tan_theta_high = (v0 ** 2 + sqrt_disc) / (g * dx)
    except ZeroDivisionError:
        return None
    angle_rad = math.atan(tan_theta_high)
    cos_angle = math.cos(angle_rad)
    if abs(cos_angle) < 1e-6:
        if dy_phys > 0 and v0 ** 2 >= 2 * g * dy_phys:
            t = (v0 - math.sqrt(max(0, v0 ** 2 - 2 * g * dy_phys))) / g;
            return math.pi / 2, t
        return None
    try:
        time_flight = dx / (v0 * cos_angle)
    except ZeroDivisionError:
        return None
    if time_flight < 0: return None
    return angle_rad, time_flight


# --- Effets de Particules ---
class ParticleEffect(GameObject):
    def __init__(self, position_xy_abs, animation_frames_list_original, frame_duration, scaler: util.Scaler):
        super().__init__();
        self.scaler = scaler;
        self.frames = []
        if animation_frames_list_original:
            for f_orig in animation_frames_list_original:
                if isinstance(f_orig, pygame.Surface):
                    s_w, s_h = self.scaler.scale_value(f_orig.get_width()), self.scaler.scale_value(f_orig.get_height())
                    self.frames.append(util.scale_sprite_to_size(f_orig, s_w, s_h))
        self.frame_duration = frame_duration;
        self.current_frame_index = 0;
        self.time_on_current_frame = 0
        if self.frames:
            self.sprite = self.frames[0];
            self.rect = self.sprite.get_rect(center=position_xy_abs)
        else:
            self.sprite = None;
            self.rect = pygame.Rect(position_xy_abs[0], position_xy_abs[1], 0,
                                    0);
            self.active = False

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