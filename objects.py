# objects.py
import pygame
import random
import math
import os  # Assurez-vous qu'il est importé
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
        cfg.STAT_SPRITE_DEFAULT_NAME: "fundations.png",
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

TURRET_STATS = {
    "gatling_turret": {
        cfg.STAT_COST_MONEY: 100, cfg.STAT_COST_IRON: 20,
        cfg.STAT_POWER_CONSUMPTION: 5,
        cfg.STAT_RANGE_PIXELS: 200,
        cfg.STAT_FIRE_RATE_PER_SEC: 5,
        cfg.STAT_PROJECTILE_TYPE_ID: "bullet",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "gun_sketch.png",
    },
    "mortar_turret": {
        cfg.STAT_COST_MONEY: 250, cfg.STAT_COST_IRON: 75,
        cfg.STAT_POWER_CONSUMPTION: 8,
        cfg.STAT_MIN_RANGE_PIXELS: 100,
        cfg.STAT_MAX_RANGE_PIXELS: 450,
        cfg.STAT_FIRE_RATE_PER_SEC: 0.5,
        cfg.STAT_PROJECTILE_TYPE_ID: "mortar_shell",
        cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS: 180,
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "mortar_sketch.png",
    }
}

PROJECTILE_STATS = {
    "bullet": {
        cfg.STAT_DAMAGE_AMOUNT: 10,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 600,
        cfg.STAT_SPRITE_DEFAULT_NAME: "bullet.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 3.0,
    },
    "mortar_shell": {
        cfg.STAT_DAMAGE_AMOUNT: 50,
        cfg.STAT_AOE_RADIUS_PIXELS: 50,
        cfg.STAT_SPRITE_DEFAULT_NAME: "mortar_shell.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 7.0,
    }
}

ENEMY_STATS = {
    1: {
        cfg.STAT_HP_MAX: 50, cfg.STAT_MOVE_SPEED_PIXELS_SEC: 60, cfg.STAT_DAMAGE_TO_CITY: 10,
        cfg.STAT_SCORE_POINTS_VALUE: 10, cfg.STAT_MONEY_DROP_VALUE: 5,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_basic_sketch.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.8, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.2,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.8, 0.8)
    },
    2: {
        cfg.STAT_HP_MAX: 30, cfg.STAT_MOVE_SPEED_PIXELS_SEC: 120, cfg.STAT_DAMAGE_TO_CITY: 5,
        cfg.STAT_SCORE_POINTS_VALUE: 15, cfg.STAT_MONEY_DROP_VALUE: 7,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_fast.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.7, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.0,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.7, 0.9)
    },
    3: {
        cfg.STAT_HP_MAX: 200, cfg.STAT_MOVE_SPEED_PIXELS_SEC: 30, cfg.STAT_DAMAGE_TO_CITY: 25,
        cfg.STAT_SCORE_POINTS_VALUE: 50, cfg.STAT_MONEY_DROP_VALUE: 20,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_tank.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 1.3, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.6,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.9, 0.9)
    },
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
            tile_size = self.scaler.get_tile_size()
            self.sprite = pygame.Surface((tile_size, tile_size));
            self.sprite.fill(cfg.COLOR_MAGENTA)

        self.rect = self.sprite.get_rect(topleft=pixel_pos_topleft)
        self.is_functional = True

    def set_as_reinforced_frame(self, is_reinforced: bool):
        if self.type == "frame":
            self.is_reinforced_frame = is_reinforced
            self._update_frame_sprite()

    def set_as_turret_platform(self, is_platform: bool):
        if self.type == "frame":
            self.is_turret_platform = is_platform
            self._update_frame_sprite()

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
                self.original_sprite = sprite_to_use
                self.sprite = util.scale_sprite_to_tile(self.original_sprite, self.scaler)
        elif cfg.DEBUG_MODE:
            print(f"AVERTISSEMENT: Sprite pour frame state '{new_sprite_key}' non trouvé.")

    def update_sprite_based_on_context(self, game_grid_ref, grid_r, grid_c, scaler: util.Scaler):
        if self.type == "miner":
            above_is_miner, below_is_miner = False, False
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
                self.original_sprite = self.sprites_dict[chosen_sprite_key]
                self.sprite = util.scale_sprite_to_tile(self.original_sprite, scaler)
        elif self.type == "storage":
            pass

    def apply_adjacency_bonus_effect(self, adjacent_similar_items_count):
        if self.type == "storage" and self.adjacency_bonus_per_unit > 0:
            self.current_adjacency_bonus_value = adjacent_similar_items_count * self.adjacency_bonus_per_unit

    def set_active_state(self, is_powered):
        self.is_functional = is_powered

    def update(self, delta_time, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler)


# --- Tourelles ---
class Turret(GameObject):
    _id_counter = 0

    def __init__(self, turret_type, pixel_pos_center, grid_pos_tuple, scaler: util.Scaler):
        super().__init__();
        self.scaler = scaler;
        Turret._id_counter += 1;
        self.id = Turret._id_counter
        self.type = turret_type;
        self.grid_pos = grid_pos_tuple;
        self.stats = TURRET_STATS.get(self.type, {})
        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        self.range = scaler.scale_value(self.stats.get(cfg.STAT_RANGE_PIXELS, 0))
        self.min_range = scaler.scale_value(self.stats.get(cfg.STAT_MIN_RANGE_PIXELS, 0))
        self.max_range = scaler.scale_value(self.stats.get(cfg.STAT_MAX_RANGE_PIXELS, 0))
        self.fire_rate_per_sec = self.stats.get(cfg.STAT_FIRE_RATE_PER_SEC, 1)
        self.cooldown_time_seconds = 1.0 / self.fire_rate_per_sec if self.fire_rate_per_sec > 0 else float('inf')
        self.current_cooldown = 0.0
        self.projectile_type = self.stats.get(cfg.STAT_PROJECTILE_TYPE_ID, None)
        self.projectile_initial_speed = scaler.scale_value(self.stats.get(cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS, 0))
        base_sprite_name = self.stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME, "placeholder.png")
        gun_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NAME, "placeholder.png")
        self.original_turret_base_sprite = util.load_sprite(os.path.join(cfg.TURRET_SPRITE_PATH, base_sprite_name))
        self.original_gun_sprite = util.load_sprite(os.path.join(cfg.TURRET_SPRITE_PATH, gun_sprite_name))
        if self.original_turret_base_sprite:
            scaled_base_w, scaled_base_h = int(scaler.tile_size * 0.8), int(scaler.tile_size * 0.8)
            self.turret_base_sprite_scaled = util.scale_sprite_to_size(self.original_turret_base_sprite, scaled_base_w,
                                                                       scaled_base_h)
        else:
            s = int(scaler.tile_size * 0.8); self.turret_base_sprite_scaled = pygame.Surface((s, s),
                                                                                             pygame.SRCALPHA); self.turret_base_sprite_scaled.fill(
                cfg.COLOR_CYAN + (180,))
        if self.original_gun_sprite:
            gun_orig_w, gun_orig_h = self.original_gun_sprite.get_size()
            target_gun_h = scaler.tile_size * 0.5;
            scale_factor = target_gun_h / gun_orig_h if gun_orig_h > 0 else 1
            target_gun_w = gun_orig_w * scale_factor
            self.gun_sprite_scaled_original = util.scale_sprite_to_size(self.original_gun_sprite, int(target_gun_w),
                                                                        int(target_gun_h))
            self.gun_sprite_rotated = self.gun_sprite_scaled_original
        else:
            w, h = int(scaler.tile_size * 0.6), int(
                scaler.tile_size * 0.3); self.gun_sprite_scaled_original = pygame.Surface((w, h),
                                                                                          pygame.SRCALPHA); self.gun_sprite_scaled_original.fill(
                cfg.COLOR_GREEN + (180,)); self.gun_sprite_rotated = self.gun_sprite_scaled_original
        self.rect = self.turret_base_sprite_scaled.get_rect(center=pixel_pos_center)
        if self.gun_sprite_scaled_original:
            self.gun_pivot_offset_in_gun_sprite = (
            self.gun_sprite_scaled_original.get_width() // 4, self.gun_sprite_scaled_original.get_height() // 2)
        else:
            self.gun_pivot_offset_in_gun_sprite = (0, 0)
        self.target_enemy = None;
        self.current_angle_deg = 0;
        self.is_functional = True

    def set_active_state(self, is_powered):
        self.is_functional = is_powered

    def find_target(self, enemies_list):  # Logic identical to previous
        self.target_enemy = None;
        closest_dist_sq = float('inf')
        turret_center_x, turret_center_y = self.rect.centerx, self.rect.centery
        for enemy in enemies_list:
            if not enemy.active or not hasattr(enemy, 'rect'): continue
            dist_sq = (enemy.rect.centerx - turret_center_x) ** 2 + (enemy.rect.centery - turret_center_y) ** 2
            target_in_range = False
            if self.type == "mortar_turret":
                if self.min_range ** 2 <= dist_sq <= self.max_range ** 2: target_in_range = True
            else:
                if dist_sq <= self.range ** 2: target_in_range = True
            if target_in_range and dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq;
                self.target_enemy = enemy

    def update(self, delta_time, enemies_list, is_powered_globally, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler);
        self.set_active_state(is_powered_globally)
        if not self.active or not self.is_functional: self.target_enemy = None; return
        if self.current_cooldown > 0: self.current_cooldown -= delta_time
        if not self.target_enemy or not self.target_enemy.active or not hasattr(self.target_enemy,
                                                                                'rect'): self.find_target(enemies_list)
        if self.target_enemy and hasattr(self.target_enemy, 'rect'):
            dx, dy = self.target_enemy.rect.centerx - self.rect.centerx, self.target_enemy.rect.centery - self.rect.centery
            self.current_angle_deg = math.degrees(math.atan2(-dy, dx))
            if self.gun_sprite_scaled_original:
                self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original,
                                                                  self.current_angle_deg)
            if self.current_cooldown <= 0: self.shoot(
                game_state_ref); self.current_cooldown = self.cooldown_time_seconds
        else:
            self.target_enemy = None

    def shoot(self, game_state_ref):  # Logic identical to previous
        if not self.target_enemy or not self.projectile_type or not hasattr(self.target_enemy, 'rect'): return
        gun_length_scaled = self.gun_sprite_scaled_original.get_width() * 0.75
        proj_origin_x = self.rect.centerx + math.cos(math.radians(self.current_angle_deg)) * gun_length_scaled
        proj_origin_y = self.rect.centery - math.sin(math.radians(self.current_angle_deg)) * gun_length_scaled
        proj_origin = (proj_origin_x, proj_origin_y)
        if self.type == "mortar_turret":
            fire_solution = calculate_mortar_fire_solution(self.rect.center, self.target_enemy.rect.center,
                                                           self.projectile_initial_speed, self.scaler.gravity)
            if fire_solution:
                launch_angle_rad_vertical, _ = fire_solution;
                angle_horizontal_rad = math.radians(self.current_angle_deg)
                vy_physics = self.projectile_initial_speed * math.sin(launch_angle_rad_vertical)
                horizontal_speed_component = self.projectile_initial_speed * math.cos(launch_angle_rad_vertical)
                vx = horizontal_speed_component * math.cos(angle_horizontal_rad);
                vy_pygame = -vy_physics
                new_proj = Projectile(self.projectile_type, proj_origin, 0, self.scaler, initial_vx=vx,
                                      initial_vy=vy_pygame)
                game_state_ref.projectiles.append(new_proj)
        else:
            new_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg, self.scaler)
            game_state_ref.projectiles.append(new_proj)

    def draw(self, surface):  # Logic identical to previous
        if not self.active: return
        if self.turret_base_sprite_scaled: surface.blit(self.turret_base_sprite_scaled, self.rect.topleft)
        if self.gun_sprite_rotated:
            gun_display_rect = self.gun_sprite_rotated.get_rect(center=self.rect.center)
            surface.blit(self.gun_sprite_rotated, gun_display_rect.topleft)
        if cfg.DEBUG_MODE:
            pygame.draw.circle(surface, cfg.COLOR_RED, self.rect.center, 3)
            # if hasattr(self, 'gun_display_rect'): pygame.draw.rect(surface, cfg.COLOR_YELLOW, self.gun_display_rect, 1)


# --- Projectiles ---
class Projectile(GameObject):
    _id_counter = 0

    def __init__(self, projectile_type, origin_xy_pixels, angle_deg, scaler: util.Scaler, initial_vx=None,
                 initial_vy=None):
        super().__init__();
        self.scaler = scaler;
        Projectile._id_counter += 1;
        self.id = Projectile._id_counter
        self.type = projectile_type;
        self.stats = PROJECTILE_STATS.get(self.type, {})
        self.damage = self.stats.get(cfg.STAT_DAMAGE_AMOUNT, 0)
        self.speed = scaler.scale_value(self.stats.get(cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS, 0))
        self.aoe_radius = scaler.scale_value(self.stats.get(cfg.STAT_AOE_RADIUS_PIXELS, 0))
        self.lifetime_seconds = self.stats.get(cfg.STAT_PROJECTILE_LIFETIME_SEC, 5.0)
        self.gravity_scaled = scaler.gravity
        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(os.path.join(cfg.PROJECTILE_SPRITE_PATH, sprite_name))
        if self.original_sprite:
            base_w, base_h = self.original_sprite.get_size()
            scaled_w = scaler.scale_value(base_w * cfg.BASE_PROJECTILE_SPRITE_SCALE_FACTOR)
            scaled_h = scaler.scale_value(base_h * cfg.BASE_PROJECTILE_SPRITE_SCALE_FACTOR)
            self.sprite_scaled_original = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)
        else:
            fb_size = scaler.scale_value(cfg.BASE_PROJECTILE_FALLBACK_SIZE)
            self.sprite_scaled_original = pygame.Surface((fb_size, fb_size), pygame.SRCALPHA);
            self.sprite_scaled_original.fill(cfg.COLOR_YELLOW + (180,))
        self.is_mortar_shell = (self.type == "mortar_shell")
        if self.is_mortar_shell:
            self.vx = initial_vx if initial_vx is not None else 0;
            self.vy_physics = -initial_vy if initial_vy is not None else 0
            self.sprite = self.sprite_scaled_original
        else:
            self.angle_rad = math.radians(angle_deg);
            self.vx = self.speed * math.cos(self.angle_rad);
            self.vy_physics = self.speed * math.sin(self.angle_rad)
            if self.sprite_scaled_original:
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, angle_deg)
            else:
                self.sprite = None
        if self.sprite:
            self.rect = self.sprite.get_rect(center=origin_xy_pixels)
        else:
            fb_size = scaler.scale_value(cfg.BASE_PROJECTILE_FALLBACK_SIZE); self.rect = pygame.Rect(
                origin_xy_pixels[0] - fb_size // 2, origin_xy_pixels[1] - fb_size // 2, fb_size, fb_size)
        self.has_impacted = False

    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):  # Logic identical to previous
        if not self.active: return
        self.lifetime_seconds -= delta_time
        if self.lifetime_seconds <= 0:
            if self.is_mortar_shell and not self.has_impacted: self.on_hit(game_state_ref)
            self.active = False;
            return
        if self.is_mortar_shell:
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

    def on_hit(self, game_state_ref):  # Logic identical to previous
        if self.is_mortar_shell and self.aoe_radius > 0 and hasattr(game_state_ref,
                                                                    'trigger_aoe_damage') and not self.has_impacted:
            game_state_ref.trigger_aoe_damage(self.rect.center, self.aoe_radius, self.damage)
            self.has_impacted = True
        self.active = False


# --- Ennemis ---
class Enemy(GameObject):
    _id_counter = 0

    def __init__(self, initial_pos_xy_on_screen, enemy_type_id, variant_data, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler
        Enemy._id_counter += 1
        self.id = Enemy._id_counter
        self.type_id = enemy_type_id
        self.stats = ENEMY_STATS.get(self.type_id, ENEMY_STATS[1])

        self.max_hp = self.stats.get(cfg.STAT_HP_MAX, 10)
        self.current_hp = self.max_hp
        self.speed_pixels_sec = self.scaler.scale_value(self.stats.get(cfg.STAT_MOVE_SPEED_PIXELS_SEC, 30))
        self.city_damage = self.stats.get(cfg.STAT_DAMAGE_TO_CITY, 1)
        self.score_value = self.stats.get(cfg.STAT_SCORE_POINTS_VALUE, 0)
        self.money_value = self.stats.get(cfg.STAT_MONEY_DROP_VALUE, 0)

        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(os.path.join(cfg.ENEMY_SPRITE_PATH, sprite_name))  # os.path.join ajouté

        min_s_stat = self.stats.get(cfg.STAT_SIZE_MIN_SCALE_FACTOR, 1.0)
        max_s_stat = self.stats.get(cfg.STAT_SIZE_MAX_SCALE_FACTOR, 1.0)
        random_type_specific_scale_factor = random.uniform(min_s_stat, max_s_stat)

        # Appliquer le multiplicateur global de taille
        # Ensure GLOBAL_ENEMY_SPRITE_SCALE_MULTIPLIER is in game_config.py
        global_scale_mult = getattr(cfg, 'GLOBAL_ENEMY_SPRITE_SCALE_MULTIPLIER', 1.0)
        final_random_scale_factor = random_type_specific_scale_factor * global_scale_mult

        if self.original_sprite:
            base_w = self.original_sprite.get_width()
            base_h = self.original_sprite.get_height()

            # Taille cible en pixels de référence APRÈS le scaling aléatoire et global
            target_ref_w = base_w * final_random_scale_factor
            target_ref_h = base_h * final_random_scale_factor

            # Scaler cette taille de référence aux pixels réels de l'écran
            scaled_w = self.scaler.scale_value(target_ref_w)
            scaled_h = self.scaler.scale_value(target_ref_h)

            scaled_w = max(1, scaled_w)  # Ensure min size 1
            scaled_h = max(1, scaled_h)  # Ensure min size 1

            self.sprite = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)
        else:
            default_base_size = cfg.BASE_ENEMY_FALLBACK_SIZE  # Use config constant
            scaled_fallback_size = self.scaler.scale_value(default_base_size * global_scale_mult)
            scaled_fallback_size = max(1, scaled_fallback_size)
            self.sprite = pygame.Surface((scaled_fallback_size, scaled_fallback_size), pygame.SRCALPHA)
            self.sprite.fill(cfg.COLOR_RED + (180,))

        if self.sprite:
            self.rect = self.sprite.get_rect(center=initial_pos_xy_on_screen)
        else:
            fb_base_size = cfg.BASE_ENEMY_FALLBACK_SIZE
            fb_size = self.scaler.scale_value(fb_base_size * global_scale_mult)
            fb_size = max(1, fb_size)
            self.rect = pygame.Rect(initial_pos_xy_on_screen[0] - fb_size // 2,
                                    initial_pos_xy_on_screen[1] - fb_size // 2, fb_size, fb_size)

        hitbox_scale_w_stat, hitbox_scale_h_stat = self.stats.get(cfg.STAT_HITBOX_SCALE_FACTORS_WH, (0.8, 0.8))
        hitbox_width = int(self.rect.width * hitbox_scale_w_stat)
        hitbox_height = int(self.rect.height * hitbox_scale_h_stat)
        self.hitbox = pygame.Rect(0, 0, max(1, hitbox_width), max(1, hitbox_height))
        self.hitbox.center = self.rect.center

    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None):  # Logic identical to previous
        if not self.active: return
        self.rect.x -= self.speed_pixels_sec * delta_time
        self.hitbox.center = self.rect.center
        if self.rect.right < self.scaler.screen_origin_x - self.scaler.scale_value(
            cfg.BASE_ENEMY_OFFSCREEN_DESPAWN_BUFFER): self.active = False

    def take_damage(self, amount):  # Logic identical to previous
        if not self.active: return
        self.current_hp -= amount
        if self.current_hp <= 0: self.current_hp = 0; self.active = False

    def get_city_damage(self):
        return self.city_damage  # Logic identical to previous

    def get_score_value(self):
        return self.score_value  # Logic identical to previous

    def get_money_value(self):
        return self.money_value  # Logic identical to previous

    def draw(self, surface):  # Logic identical to previous
        super().draw(surface)
        if self.active and self.current_hp < self.max_hp and self.max_hp > 0:
            hp_bar_bg_color = getattr(cfg, 'COLOR_HP_BAR_BACKGROUND', cfg.COLOR_GREY_DARK)
            hp_bar_fill_color = getattr(cfg, 'COLOR_HP_FULL', cfg.COLOR_GREEN)
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio < 0.3:
                hp_bar_fill_color = getattr(cfg, 'COLOR_HP_CRITICAL', cfg.COLOR_RED)
            elif hp_ratio < 0.6:
                hp_bar_fill_color = getattr(cfg, 'COLOR_HP_LOW', cfg.COLOR_ORANGE)
            bar_w = self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_WIDTH)
            bar_h = self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_HEIGHT)
            bar_offset_y = self.scaler.scale_value(cfg.BASE_ENEMY_HP_BAR_OFFSET_Y)
            bg_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - bar_h - bar_offset_y, bar_w, bar_h)
            hp_fill_w = int(bar_w * hp_ratio);
            hp_rect = pygame.Rect(bg_rect.left, bg_rect.top, hp_fill_w, bar_h)
            pygame.draw.rect(surface, hp_bar_bg_color, bg_rect)
            pygame.draw.rect(surface, hp_bar_fill_color, hp_rect)


# --- Calcul de Trajectoire pour Mortier --- (Logic identical to previous)
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


# --- Effets de Particules --- (Logic identical to previous)
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