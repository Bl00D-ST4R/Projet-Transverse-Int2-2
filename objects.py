# objects.py
import pygame
import random
import math
import game_config as cfg
import utility_functions as util

# --- Définitions des Stats des Objets ---
# (Identical to original, no changes needed here as they are BASE values)
BUILDING_STATS = {
    "frame": {
        cfg.STAT_COST_MONEY: 10,
        cfg.STAT_SPRITE_DEFAULT_NAME: "frame.png",
    },
    "fundations": {
        cfg.STAT_COST_MONEY: 0,
        cfg.STAT_SPRITE_DEFAULT_NAME: "fundations.png",
        "is_reinforced": True
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
        cfg.STAT_RANGE_PIXELS: 200, # Base range
        cfg.STAT_FIRE_RATE_PER_SEC: 5,
        cfg.STAT_PROJECTILE_TYPE_ID: "bullet",
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "gun_sketch.png",
    },
    "mortar_turret": {
        cfg.STAT_COST_MONEY: 250, cfg.STAT_COST_IRON: 75,
        cfg.STAT_POWER_CONSUMPTION: 8,
        cfg.STAT_MIN_RANGE_PIXELS: 100, # Base min range
        cfg.STAT_MAX_RANGE_PIXELS: 450, # Base max range
        cfg.STAT_FIRE_RATE_PER_SEC: 0.5,
        cfg.STAT_PROJECTILE_TYPE_ID: "mortar_shell",
        cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS: 180, # Base speed
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "mortar_sketch.png",
    }
}

PROJECTILE_STATS = {
    "bullet": {
        cfg.STAT_DAMAGE_AMOUNT: 10,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 600, # Base speed
        cfg.STAT_SPRITE_DEFAULT_NAME: "bullet.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 3.0,
    },
    "mortar_shell": {
        cfg.STAT_DAMAGE_AMOUNT: 50,
        cfg.STAT_AOE_RADIUS_PIXELS: 50, # Base radius
        cfg.STAT_SPRITE_DEFAULT_NAME: "mortar_shell.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 7.0,
    }
}

ENEMY_STATS = {
    1: {
        cfg.STAT_HP_MAX: 50,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 60, # Base speed
        cfg.STAT_DAMAGE_TO_CITY: 10,
        cfg.STAT_SCORE_POINTS_VALUE: 10,
        cfg.STAT_MONEY_DROP_VALUE: 5,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_basic_sketch.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.8, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.2,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.8, 0.8)
    },
    2: {
        cfg.STAT_HP_MAX: 30,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 120, # Base speed
        cfg.STAT_DAMAGE_TO_CITY: 5,
        cfg.STAT_SCORE_POINTS_VALUE: 15,
        cfg.STAT_MONEY_DROP_VALUE: 7,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_fast.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.7, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.0,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.7, 0.9)
    },
    3: {
        cfg.STAT_HP_MAX: 200,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 30, # Base speed
        cfg.STAT_DAMAGE_TO_CITY: 25,
        cfg.STAT_SCORE_POINTS_VALUE: 50,
        cfg.STAT_MONEY_DROP_VALUE: 20,
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_tank.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 1.3, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.6,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.9, 0.9)
    },
}

# --- Fonctions utilitaires ---
def get_item_stats(item_type_string):
    if item_type_string in BUILDING_STATS: return BUILDING_STATS[item_type_string]
    if item_type_string in TURRET_STATS: return TURRET_STATS[item_type_string]
    return {}

def is_building_type(item_type_string): return item_type_string in BUILDING_STATS
def is_turret_type(item_type_string): return item_type_string in TURRET_STATS
def is_frame_type(item_type_string): return item_type_string == "frame"
def is_reinforced_foundation_type(item_type_string): return item_type_string == "fundations"

# --- Classe de Base ---
class GameObject(pygame.sprite.Sprite):
    def __init__(self): # Scaler will be added in subclasses
        super().__init__()
        self.active = True
        self.rect = pygame.Rect(0,0,0,0)
        self.sprite = None
        self.original_sprite = None # Stores the unscaled loaded sprite
        # self.scaler = None # Will be set by subclasses

    def draw(self, surface):
        if self.active and self.sprite:
            surface.blit(self.sprite, self.rect.topleft)

    # MODIFIED: Update signature to accept scaler
    def update(self, delta_time, game_state_ref, scaler: util.Scaler):
        # self.scaler = scaler # Store if needed for future access, though usually passed or already on self
        pass

# --- Bâtiments ---
class Building(GameObject):
    _id_counter = 0
    # MODIFIED: Accept scaler
    def __init__(self, building_type, pixel_pos_topleft, grid_pos_tuple, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler # Store the scaler
        Building._id_counter += 1
        self.id = Building._id_counter
        self.type = building_type
        self.grid_pos = grid_pos_tuple
        self.stats = BUILDING_STATS.get(self.type, {})

        self.cost_money = self.stats.get(cfg.STAT_COST_MONEY, 0)
        self.cost_iron = self.stats.get(cfg.STAT_COST_IRON, 0)
        self.power_production = self.stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        self.iron_production_pm = self.stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
        self.iron_storage_increase = self.stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
        self.adjacency_bonus_per_unit = self.stats.get(cfg.STAT_ADJACENCY_BONUS_VALUE, 0)
        self.current_adjacency_bonus_value = 0
        self.is_reinforced = self.stats.get("is_reinforced", False)

        self.sprites_dict = {} # Stores original, unscaled sprites
        if cfg.STAT_SPRITE_VARIANTS_DICT in self.stats:
            for key, sprite_name in self.stats[cfg.STAT_SPRITE_VARIANTS_DICT].items():
                path = cfg.BUILDING_SPRITE_PATH + sprite_name
                self.sprites_dict[key] = util.load_sprite(path) # Load unscaled

        default_sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        if "single" in self.sprites_dict and self.sprites_dict["single"]:
            self.original_sprite = self.sprites_dict["single"] # Unscaled
        else:
             self.original_sprite = util.load_sprite(cfg.BUILDING_SPRITE_PATH + default_sprite_name) # Unscaled

        # MODIFIED: Use scaler for scaling
        self.sprite = util.scale_sprite_to_tile(self.original_sprite, self.scaler)
        if not self.sprite:
            tile_size = self.scaler.get_tile_size()
            self.sprite = pygame.Surface((tile_size, tile_size)); self.sprite.fill(cfg.COLOR_BLUE)

        self.rect = self.sprite.get_rect(topleft=pixel_pos_topleft)
        self.is_internally_active = True

    # MODIFIED: update_sprite_based_on_context needs scaler
    def update_sprite_based_on_context(self, game_grid_ref, grid_r, grid_c, scaler: util.Scaler):
        new_sprite_key = "single"
        row, col = grid_r, grid_c

        if self.type == "miner":
            above_is_miner = False
            below_is_miner = False
            if row > 0 and len(game_grid_ref) > row - 1 and len(game_grid_ref[row-1]) > col and \
               game_grid_ref[row - 1][col] and game_grid_ref[row - 1][col].type == "miner":
                above_is_miner = True
            if row < len(game_grid_ref) - 1 and len(game_grid_ref) > row + 1 and len(game_grid_ref[row+1]) > col and \
               game_grid_ref[row + 1][col] and game_grid_ref[row + 1][col].type == "miner":
                below_is_miner = True

            if above_is_miner and below_is_miner: new_sprite_key = "stacked_middle"
            elif below_is_miner: new_sprite_key = "stacked_top"
            elif above_is_miner: new_sprite_key = "stacked_bottom"
            else: new_sprite_key = "single"
        elif self.type == "storage":
             pass

        sprite_to_use = self.sprites_dict.get(new_sprite_key)
        if sprite_to_use:
            self.original_sprite = sprite_to_use # Set the unscaled original
        else:
            default_sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
            self.original_sprite = util.load_sprite(cfg.BUILDING_SPRITE_PATH + default_sprite_name) # Unscaled

        # MODIFIED: Use passed scaler
        self.sprite = util.scale_sprite_to_tile(self.original_sprite, scaler)

    def apply_adjacency_bonus_effect(self, adjacent_similar_items_count):
        if self.type == "storage" and self.adjacency_bonus_per_unit > 0:
            self.current_adjacency_bonus_value = adjacent_similar_items_count * self.adjacency_bonus_per_unit

    def set_active_state(self, is_powered):
        self.is_internally_active = is_powered

    # MODIFIED Building update to match GameObject signature (accept scaler)
    def update(self, delta_time, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler)
        # Add any building-specific update logic here if needed


# --- Tourelles ---
class Turret(GameObject):
    _id_counter = 0
    # MODIFIED: Accept scaler
    def __init__(self, turret_type, pixel_pos_topleft, grid_pos_tuple, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler # Store the scaler
        Turret._id_counter += 1
        self.id = Turret._id_counter
        self.type = turret_type
        self.grid_pos = grid_pos_tuple
        self.stats = TURRET_STATS.get(self.type, {})

        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        # MODIFIED: Scale BASE values using scaler
        self.range = self.scaler.scale_value(self.stats.get(cfg.STAT_RANGE_PIXELS, 0))
        self.min_range = self.scaler.scale_value(self.stats.get(cfg.STAT_MIN_RANGE_PIXELS, 0))
        self.max_range = self.scaler.scale_value(self.stats.get(cfg.STAT_MAX_RANGE_PIXELS, 0))
        self.fire_rate_per_sec = self.stats.get(cfg.STAT_FIRE_RATE_PER_SEC, 1)
        self.cooldown_time_seconds = 1.0 / self.fire_rate_per_sec if self.fire_rate_per_sec > 0 else float('inf')
        self.current_cooldown = 0.0
        self.projectile_type = self.stats.get(cfg.STAT_PROJECTILE_TYPE_ID, None)
        self.projectile_initial_speed = self.scaler.scale_value(self.stats.get(cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS, 0)) # Scaled

        base_sprite_name = self.stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME, "placeholder.png")
        gun_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NAME, "placeholder.png")
        self.original_base_sprite = util.load_sprite(cfg.TURRET_SPRITE_PATH + base_sprite_name) # Unscaled
        self.original_gun_sprite = util.load_sprite(cfg.TURRET_SPRITE_PATH + gun_sprite_name)   # Unscaled

        # MODIFIED: Use scaler for scaling
        self.base_sprite = util.scale_sprite_to_tile(self.original_base_sprite, self.scaler)
        if self.original_gun_sprite:
            self.gun_sprite_scaled_original = util.scale_sprite_to_tile(self.original_gun_sprite, self.scaler)
            self.gun_sprite_rotated = self.gun_sprite_scaled_original
        else:
            tile_size = self.scaler.get_tile_size()
            self.gun_sprite_scaled_original = pygame.Surface((tile_size, tile_size // 2))
            self.gun_sprite_scaled_original.fill(cfg.COLOR_GREEN)
            self.gun_sprite_rotated = self.gun_sprite_scaled_original

        if not self.base_sprite:
            tile_size = self.scaler.get_tile_size()
            self.base_sprite = pygame.Surface((tile_size,tile_size)); self.base_sprite.fill(cfg.COLOR_BLUE)

        self.rect = self.base_sprite.get_rect(topleft=pixel_pos_topleft)

        if self.gun_sprite_scaled_original:
            self.gun_pivot_offset = (self.gun_sprite_scaled_original.get_width() // 2, self.gun_sprite_scaled_original.get_height() // 2)
        else:
            tile_size = self.scaler.get_tile_size()
            self.gun_pivot_offset = (tile_size // 2, tile_size // 4)

        self.target_enemy = None
        self.current_angle_deg = 0
        self.is_internally_active = True # Controlled by power

    def set_active_state(self, is_powered):
        self.is_internally_active = is_powered

    def find_target(self, enemies_list):
        self.target_enemy = None
        closest_dist_sq = float('inf')
        turret_center_x, turret_center_y = self.rect.centerx, self.rect.centery

        for enemy in enemies_list:
            if not enemy.active or not hasattr(enemy, 'rect'): continue
            dist_sq = (enemy.rect.centerx - turret_center_x)**2 + (enemy.rect.centery - turret_center_y)**2
            target_in_range = False
            # self.range, self.min_range, self.max_range are already scaled
            if self.type == "mortar_turret":
                if self.min_range**2 <= dist_sq <= self.max_range**2: target_in_range = True
            else: # Gatling, etc.
                if dist_sq <= self.range**2: target_in_range = True
            
            if target_in_range and dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                self.target_enemy = enemy

    # MODIFIED: Update signature to accept scaler (though not directly used here, passed to super and shoot)
    def update(self, delta_time, enemies_list, is_powered_globally, game_state_ref, scaler: util.Scaler):
        super().update(delta_time, game_state_ref, scaler) # Pass scaler to GameObject.update
        self.set_active_state(is_powered_globally) # Turret's own power state
        if not self.active or not self.is_internally_active: # GameObject.active and Turret's power state
            self.target_enemy = None
            return

        if self.current_cooldown > 0: self.current_cooldown -= delta_time

        if not self.target_enemy or not self.target_enemy.active or not hasattr(self.target_enemy, 'rect'):
            self.find_target(enemies_list) # Uses self.range etc which are scaled

        if self.target_enemy and hasattr(self.target_enemy, 'rect'):
            dx = self.target_enemy.rect.centerx - self.rect.centerx
            dy = self.target_enemy.rect.centery - self.rect.centery
            self.current_angle_deg = math.degrees(math.atan2(-dy, dx))
            if self.gun_sprite_scaled_original: # This is already scaled
                self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
            
            if self.current_cooldown <= 0:
                self.shoot(game_state_ref) # shoot will pass self.scaler to Projectile
                self.current_cooldown = self.cooldown_time_seconds
        else: # No valid target found or current target became invalid
            self.target_enemy = None


    def shoot(self, game_state_ref): # game_state_ref has game_state_ref.scaler
        if not self.target_enemy or not self.projectile_type or not hasattr(self.target_enemy, 'rect'): return

        scaled_tile_size = self.scaler.get_tile_size() # For consistent offset scaling

        proj_origin_x = self.rect.centerx + math.cos(math.radians(self.current_angle_deg)) * (scaled_tile_size // 3)
        proj_origin_y = self.rect.centery - math.sin(math.radians(self.current_angle_deg)) * (scaled_tile_size // 3)
        proj_origin = (proj_origin_x, proj_origin_y)

        # self.projectile_initial_speed is already scaled
        # cfg.BASE_GRAVITY_PHYSICS is base, Projectile will scale it
        if self.type == "mortar_turret":
            fire_solution = calculate_mortar_fire_solution(
                self.rect.center,
                self.target_enemy.rect.center,
                self.projectile_initial_speed, # Already scaled
                cfg.BASE_GRAVITY_PHYSICS * self.scaler.general_scale # Pass scaled gravity
            )
            if fire_solution:
                launch_angle_rad_vertical, _ = fire_solution
                angle_horizontal_rad = math.radians(self.current_angle_deg) # Turret's current facing
                
                # Decompose initial velocity based on launch_angle_rad_vertical (for elevation)
                # and angle_horizontal_rad (for turret's horizontal aiming)
                # V0_vertical_plane = self.projectile_initial_speed * math.sin(launch_angle_rad_vertical)
                # V0_horizontal_plane_projection = self.projectile_initial_speed * math.cos(launch_angle_rad_vertical)
                
                # vx = V0_horizontal_plane_projection * math.cos(angle_horizontal_rad)
                # vz (sideways) = V0_horizontal_plane_projection * math.sin(angle_horizontal_rad) - not used for 2D X,Y
                # vy_physics = V0_vertical_plane 
                
                # Simpler: The fire_solution gives an angle in the 2D vertical plane towards the target.
                # We need to project this onto the game's X and Y based on turret's facing.
                # For mortar, the current_angle_deg represents the horizontal aiming.
                # The launch_angle_rad_vertical is the elevation.
                
                # Total speed V0 is self.projectile_initial_speed
                # Speed in the horizontal plane (ground speed if no elevation) = V0 * cos(elevation_angle)
                # Speed in the vertical direction (upwards) = V0 * sin(elevation_angle)
                
                vy_physics = self.projectile_initial_speed * math.sin(launch_angle_rad_vertical) # Upwards component
                horizontal_speed_component = self.projectile_initial_speed * math.cos(launch_angle_rad_vertical)
                
                vx = horizontal_speed_component * math.cos(angle_horizontal_rad) # X component of horizontal speed
                # vy_for_horizontal_aim = horizontal_speed_component * math.sin(angle_horizontal_rad) # Y component of horizontal speed if mortar could aim up/down screen for horizontal
                                                                                              # This is not how it usually works. Mortar aims at a ground point.
                                                                                              # The atan2 for current_angle_deg already determined the horizontal plane direction.
                
                vy_pygame = -vy_physics # Pygame Y is inverted from physics Y
                # MODIFIED: Pass self.scaler to Projectile
                new_proj = Projectile(self.projectile_type, proj_origin, 0, self.scaler, initial_vx=vx, initial_vy=vy_pygame)
                if hasattr(game_state_ref, 'projectiles'): game_state_ref.projectiles.append(new_proj)
        else: # Gatling
            # MODIFIED: Pass self.scaler to Projectile
            new_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg, self.scaler)
            if hasattr(game_state_ref, 'projectiles'): game_state_ref.projectiles.append(new_proj)


    def draw(self, surface): # Drawing uses already scaled sprites
        if self.active and self.base_sprite: surface.blit(self.base_sprite, self.rect.topleft)
        if self.active and self.gun_sprite_rotated and isinstance(self.gun_sprite_rotated, pygame.Surface):
                gun_rect = self.gun_sprite_rotated.get_rect(center=self.rect.center)
                surface.blit(self.gun_sprite_rotated, gun_rect.topleft)


# --- Projectiles ---
class Projectile(GameObject):
    _id_counter = 0
    # MODIFIED: Accept scaler
    def __init__(self, projectile_type, origin_xy_pixels, angle_deg, scaler: util.Scaler, initial_vx=None, initial_vy=None):
        super().__init__()
        self.scaler = scaler # Store the scaler
        Projectile._id_counter += 1
        self.id = Projectile._id_counter
        self.type = projectile_type
        self.stats = PROJECTILE_STATS.get(self.type, {})

        self.damage = self.stats.get(cfg.STAT_DAMAGE_AMOUNT, 0)
        # MODIFIED: Scale BASE values using scaler
        self.speed = self.scaler.scale_value(self.stats.get(cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS, 0))
        self.aoe_radius = self.scaler.scale_value(self.stats.get(cfg.STAT_AOE_RADIUS_PIXELS, 0)) # Scaled AoE radius
        self.lifetime_seconds = self.stats.get(cfg.STAT_PROJECTILE_LIFETIME_SEC, 5.0)
        
        # Calculate scaled gravity for this projectile instance
        self.gravity_scaled = cfg.BASE_GRAVITY_PHYSICS * self.scaler.general_scale


        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(cfg.PROJECTILE_SPRITE_PATH + sprite_name) # Unscaled

        if self.original_sprite:
            # MODIFIED: Scale the base size of the projectile sprite using scaler
            base_proj_w = self.original_sprite.get_width()
            base_proj_h = self.original_sprite.get_height()
            # Example: scale to 50% of its original size, then apply general game scaling
            scaled_w = self.scaler.scale_value(base_proj_w * 0.5)
            scaled_h = self.scaler.scale_value(base_proj_h * 0.5)
            self.sprite_scaled_original = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)
        else:
            # Fallback scaled size
            fallback_size = self.scaler.scale_value(10)
            self.sprite_scaled_original = pygame.Surface((fallback_size, fallback_size))
            self.sprite_scaled_original.fill(cfg.COLOR_YELLOW)

        self.is_mortar_shell = (self.type == "mortar_shell")
        if self.is_mortar_shell:
            # initial_vx, initial_vy are already scaled as they come from Turret.shoot's calculation
            # which used scaled projectile_initial_speed and scaled gravity.
            self.vx = initial_vx if initial_vx is not None else 0
            self.vy_physics = -initial_vy if initial_vy is not None else 0 # Convert Pygame Y to physics Y
            self.sprite = self.sprite_scaled_original # Mortar shell might not rotate initially or based on trajectory
        else: # Gatling bullet
            self.angle_rad = math.radians(angle_deg)
            self.vx = self.speed * math.cos(self.angle_rad) # self.speed is scaled
            self.vy_physics = self.speed * math.sin(self.angle_rad) # Up/down in physics coords, this is correct for atan2 style angle
            if self.sprite_scaled_original:
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, angle_deg) # Rotate scaled sprite
            else: self.sprite = None

        if self.sprite: self.rect = self.sprite.get_rect(center=origin_xy_pixels)
        else: self.rect = pygame.Rect(origin_xy_pixels[0]-5, origin_xy_pixels[1]-5, 10, 10) # Fallback rect

    # MODIFIED: Update signature to accept scaler
    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None): # scaler is on self.scaler
        if not self.active: return
        self.lifetime_seconds -= delta_time
        if self.lifetime_seconds <= 0: self.active = False; return

        if self.is_mortar_shell:
            self.rect.x += self.vx * delta_time
            self.rect.y += -self.vy_physics * delta_time # Convert physics Y change to Pygame Y change
            # Use scaled gravity for this projectile
            self.vy_physics -= self.gravity_scaled * delta_time # Update physics Y velocity
            if self.sprite_scaled_original: # If has a base sprite to rotate
                current_angle_rad_physics = math.atan2(self.vy_physics, self.vx) # Angle of current velocity vector
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, math.degrees(current_angle_rad_physics))
        else: # Gatling bullet
            self.rect.x += self.vx * delta_time
            # For gatling, vy_physics was set based on angle_deg, so -vy_physics for pygame Y
            self.rect.y += -self.vy_physics * delta_time


        # Check screen bounds using self.scaler
        # Add a buffer for projectiles that might start/end slightly off-screen (like mortar)
        offscreen_buffer = self.scaler.scale_value(200)
        if self.rect.right < -offscreen_buffer or \
           self.rect.left > self.scaler.actual_w + offscreen_buffer or \
           self.rect.bottom < -offscreen_buffer or \
           self.rect.top > self.scaler.actual_h + offscreen_buffer:
            self.active = False


    def on_hit(self, game_state_ref): # game_state_ref has game_state_ref.scaler
        self.active = False
        if self.is_mortar_shell and self.aoe_radius > 0 and hasattr(game_state_ref, 'trigger_aoe_damage'):
            # self.aoe_radius is already scaled from __init__
            game_state_ref.trigger_aoe_damage(self.rect.center, self.aoe_radius, self.damage)

# --- Ennemis ---
class Enemy(GameObject):
    _id_counter = 0
    # MODIFIED: Accept scaler
    def __init__(self, initial_pos_xy_ref, enemy_type_id, variant_data, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler # Store the scaler
        Enemy._id_counter += 1
        self.id = Enemy._id_counter
        self.type_id = enemy_type_id
        self.stats = ENEMY_STATS.get(self.type_id, ENEMY_STATS[1]) # Fallback to type 1 if not found

        self.max_hp = self.stats.get(cfg.STAT_HP_MAX, 10)
        self.current_hp = self.max_hp
        # MODIFIED: Scale BASE speed using scaler
        self.speed_pixels_sec = self.scaler.scale_value(self.stats.get(cfg.STAT_MOVE_SPEED_PIXELS_SEC, 30))
        self.city_damage = self.stats.get(cfg.STAT_DAMAGE_TO_CITY, 1)
        self.score_value = self.stats.get(cfg.STAT_SCORE_POINTS_VALUE, 0)
        self.money_value = self.stats.get(cfg.STAT_MONEY_DROP_VALUE, 0)

        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(cfg.ENEMY_SPRITE_PATH + sprite_name) # Unscaled

        min_s = self.stats.get(cfg.STAT_SIZE_MIN_SCALE_FACTOR, 1.0)
        max_s = self.stats.get(cfg.STAT_SIZE_MAX_SCALE_FACTOR, 1.0)
        random_scale_factor = random.uniform(min_s, max_s)

        if self.original_sprite:
            # MODIFIED: Apply random scale factor and then the general game scale
            base_w = self.original_sprite.get_width()
            base_h = self.original_sprite.get_height()
            
            # Target size in reference pixels after random_scale_factor
            target_ref_w = base_w * random_scale_factor
            target_ref_h = base_h * random_scale_factor

            # Scale this reference target size to actual screen pixels
            scaled_w = self.scaler.scale_value(target_ref_w)
            scaled_h = self.scaler.scale_value(target_ref_h)
            
            self.sprite = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)
        else:
            default_size = self.scaler.scale_value(30) # Fallback scaled size
            self.sprite = pygame.Surface((default_size, default_size)); self.sprite.fill(cfg.COLOR_RED)

        # MODIFIED: Scale the reference initial position
        scaled_initial_pos = self.scaler.scale_value(initial_pos_xy_ref)
        if self.sprite: self.rect = self.sprite.get_rect(center=scaled_initial_pos)
        else: self.rect = pygame.Rect(scaled_initial_pos[0]-15, scaled_initial_pos[1]-15, 30, 30) # Fallback rect

        hitbox_scale_w, hitbox_scale_h = self.stats.get(cfg.STAT_HITBOX_SCALE_FACTORS_WH, (0.8,0.8))
        # Hitbox is relative to the (already scaled) self.rect
        hitbox_width = int(self.rect.width * hitbox_scale_w)
        hitbox_height = int(self.rect.height * hitbox_scale_h)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.hitbox.center = self.rect.center

    # MODIFIED: Update signature to accept scaler (though not directly used here as speed is pre-scaled)
    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None): # scaler is on self.scaler
        if not self.active: return
        self.rect.x -= self.speed_pixels_sec * delta_time # Uses pre-scaled speed
        self.hitbox.center = self.rect.center
        # Check if off-screen to the left (relative to game world, not just scaler.actual_w)
        if self.rect.right < 0: # A simple check, could be more sophisticated
            self.active = False

    def take_damage(self, amount):
        if not self.active: return
        self.current_hp -= amount
        if self.current_hp <= 0: self.current_hp = 0; self.active = False

    def get_city_damage(self): return self.city_damage
    def get_score_value(self): return self.score_value
    def get_money_value(self): return self.money_value

    def draw(self, surface): # Uses self.scaler for health bar
        super().draw(surface) # Draws self.sprite which is already scaled
        if self.active and self.current_hp < self.max_hp and self.max_hp > 0 :
            hp_bar_bg_color = getattr(cfg, 'COLOR_HP_BAR_BACKGROUND', cfg.COLOR_GREY_DARK)
            hp_bar_fill_color = getattr(cfg, 'COLOR_HP_FULL', cfg.COLOR_GREEN)
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio < 0.3: hp_bar_fill_color = getattr(cfg, 'COLOR_HP_CRITICAL', cfg.COLOR_RED)
            elif hp_ratio < 0.6: hp_bar_fill_color = getattr(cfg, 'COLOR_HP_LOW', cfg.COLOR_ORANGE)
            
            # MODIFIED: Use self.scaler to scale health bar dimensions from BASE values
            base_bar_w = 30 # Example base width
            base_bar_h = 5  # Example base height
            base_bar_offset_y = 3 # Example base offset
            
            bar_w = self.scaler.scale_value(base_bar_w)
            bar_h = self.scaler.scale_value(base_bar_h)
            bar_offset_y = self.scaler.scale_value(base_bar_offset_y)

            bg_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - bar_h - bar_offset_y, bar_w, bar_h)
            hp_fill_w = int(bar_w * hp_ratio)
            hp_rect = pygame.Rect(bg_rect.left, bg_rect.top, hp_fill_w, bar_h)
            pygame.draw.rect(surface, hp_bar_bg_color, bg_rect)
            pygame.draw.rect(surface, hp_bar_fill_color, hp_rect)

# --- Calcul de Trajectoire pour Mortier ---
# This function uses values already passed as scaled (speed, gravity)
def calculate_mortar_fire_solution(turret_pos_pixels, target_pos_pixels, projectile_initial_speed_pixels, gravity_pixels_s2):
    dx_pixels = target_pos_pixels[0] - turret_pos_pixels[0]
    # dy_physics: positive is up. Pygame Y is inverted.
    dy_physics = -(target_pos_pixels[1] - turret_pos_pixels[1]) # Target Y relative to Turret Y in physics coords

    v0 = projectile_initial_speed_pixels # Already scaled
    g = abs(gravity_pixels_s2)           # Already scaled and made positive

    # Handle vertical shot (dx_pixels is very small)
    if abs(dx_pixels) < 1.0: # Effectively dx = 0
        # Equation for vertical motion: dy = v0y*t - 0.5*g*t^2 and vy = v0y - g*t
        # If shooting straight up (theta = pi/2), v0y = v0.
        # To hit dy_physics: dy_physics = v0*t - 0.5*g*t^2. This is a quadratic in t.
        # Or, easier: v_final_y^2 = v0y^2 - 2*g*dy_physics. If v_final_y is 0 at apex.
        # This formula calculates angle, so for vertical shot, angle is pi/2.
        # We need time of flight if possible.
        # If target is directly above (dy_physics > 0) and reachable:
        if dy_physics > 0 and v0**2 >= 2 * g * dy_physics:
            # Time to reach dy_physics on the way up: (v0 - sqrt(v0^2 - 2*g*dy_physics)) / g
             # This discriminant must be positive.
            if (v0**2 - 2*g*dy_physics) < 0: return None # Should be caught by v0**2 >= 2*g*dy_physics
            time_to_target = (v0 - math.sqrt(max(0, v0**2 - 2*g*dy_physics))) / g # max(0,...) for safety
            return math.pi / 2, time_to_target # Angle is 90 degrees
        return None # Cannot hit if directly below or too high above

    # Quadratic term for tan(theta): (g * dx^2 / (2 * v0^2)) * tan^2(theta) - dx * tan(theta) + (dy + g * dx^2 / (2 * v0^2)) = 0
    # Simpler approach from Wikipedia (Trajectory of a projectile):
    # tan(theta) = (v0^2 +- sqrt(v0^4 - g*(g*dx^2 + 2*dy*v0^2))) / (g*dx)
    discriminant = v0**4 - g * (g * dx_pixels**2 + 2 * dy_physics * v0**2)

    if discriminant < 0:
        return None # Target is out of range

    sqrt_discriminant = math.sqrt(discriminant)
    
    # Two possible angles, usually prefer the higher trajectory for mortars for obstacle clearance,
    # or lower for faster time. Let's use the one that gives a positive time of flight (often higher angle).
    # The formula gives two solutions for tan(theta). We want the solution that makes sense.
    # tan_theta_high for higher trajectory (often preferred for mortars)
    try:
        if g * dx_pixels == 0: return None # Avoid division by zero if dx is huge and g is tiny or vice-versa
        tan_theta_high = (v0**2 + sqrt_discriminant) / (g * dx_pixels)
        # tan_theta_low = (v0**2 - sqrt_discriminant) / (g * dx_pixels) # Lower trajectory
    except ZeroDivisionError: # Should be caught by abs(dx_pixels) < 1.0 if g is non-zero
        return None

    chosen_angle_rad = math.atan(tan_theta_high) # This is the launch angle in the vertical plane of the shot

    # Time of flight: t = dx / (v0 * cos(theta))
    cos_chosen_angle = math.cos(chosen_angle_rad)
    if abs(cos_chosen_angle) < 1e-6: # Avoid division by zero if angle is near pi/2
        # This case should have been handled by dx_pixels ~ 0, but as a safeguard
        if dy_physics > 0 and v0**2 >= 2 * g * dy_physics: # Can it reach vertically?
             time_to_target = (v0 - math.sqrt(max(0, v0**2 - 2*g*dy_physics))) / g
             return math.pi/2, time_to_target
        return None

    try:
        time_of_flight = dx_pixels / (v0 * cos_chosen_angle)
    except ZeroDivisionError: # Should be caught by abs(cos_chosen_angle)
        return None
        
    if time_of_flight < 0 : # Shot would go backwards in time, physically impossible or wrong angle choice
        # Try the other angle if this happens, though tan_theta_high usually works for positive dx
        # tan_theta_low = (v0**2 - sqrt_discriminant) / (g * dx_pixels)
        # chosen_angle_rad_low = math.atan(tan_theta_low)
        # cos_chosen_angle_low = math.cos(chosen_angle_rad_low)
        # if abs(cos_chosen_angle_low) > 1e-6:
        #    time_of_flight_low = dx_pixels / (v0 * cos_chosen_angle_low)
        #    if time_of_flight_low >=0:
        #        return chosen_angle_rad_low, time_of_flight_low
        return None # No valid positive time of flight found

    return chosen_angle_rad, time_of_flight


# --- Effets de Particules ---
class ParticleEffect(GameObject):
    # MODIFIED: Accept scaler
    def __init__(self, position_xy, animation_frames_list, frame_duration, scaler: util.Scaler):
        super().__init__()
        self.scaler = scaler # Store the scaler
        self.frames = [] # Will store scaled frames

        if animation_frames_list: # This list should contain unscaled pygame.Surface objects
            for f_original in animation_frames_list:
                if isinstance(f_original, pygame.Surface):
                     # MODIFIED: Scale with scaler. Assuming effect frames are meant to be tile-sized or a specific base size.
                     # If they have their own intrinsic base size, scale_sprite_to_size might be better.
                     # For now, let's assume they are related to TILE_SIZE for simplicity.
                     self.frames.append(util.scale_sprite_to_tile(f_original, self.scaler))
        
        self.frame_duration = frame_duration
        self.current_frame_index = 0
        self.time_on_current_frame = 0

        if self.frames:
            self.sprite = self.frames[0] # First scaled frame
            self.rect = self.sprite.get_rect(center=position_xy)
        else:
            self.sprite = None
            self.rect = pygame.Rect(position_xy[0], position_xy[1], 0, 0) # No size if no frames
            self.active = False # No frames, so not active

    # MODIFIED: Update signature to accept scaler (though not directly used here if frames are pre-scaled)
    def update(self, delta_time, game_state_ref=None, scaler: util.Scaler = None): # scaler is on self.scaler
        if not self.active or not self.frames: return

        self.time_on_current_frame += delta_time
        if self.time_on_current_frame >= self.frame_duration:
            self.time_on_current_frame -= self.frame_duration # Or use modulo: self.time_on_current_frame %= self.frame_duration
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                self.active = False # Animation finished
            else:
                self.sprite = self.frames[self.current_frame_index] # Next scaled frame
                if self.sprite: # Update rect if sprite changes (e.g. different sized frames, though unlikely if all scaled to tile)
                    current_center = self.rect.center
                    self.rect = self.sprite.get_rect(center=current_center)
