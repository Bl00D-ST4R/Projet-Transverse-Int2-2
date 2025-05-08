# objects.py
import pygame
import random
import math
import game_config as cfg
import utility_functions as util # Assurez-vous que ce nom de fichier est correct

# --- Définitions des Stats des Objets ---
# Ces dictionnaires contiennent les propriétés de base pour chaque type d'objet.
# Les sprites sont chargés et scalés dans le __init__ de chaque classe.

BUILDING_STATS = {
    "foundation": {
        cfg.STAT_COST_MONEY: 50,
        # MODIFIÉ: Utilisation de frame.png comme fondation de base.
        cfg.STAT_SPRITE_DEFAULT_NAME: "frame.png",
    },
    "generator": {
        cfg.STAT_COST_MONEY: 150,
        cfg.STAT_POWER_PRODUCTION: 10, # Produit 10W
        # MODIFIÉ: Utilisation de battery.png
        cfg.STAT_SPRITE_DEFAULT_NAME: "battery.png",
    },
    "miner": {
        cfg.STAT_COST_MONEY: 200, cfg.STAT_COST_IRON: 50,
        cfg.STAT_POWER_CONSUMPTION: 2, # Consomme 2W (valeur positive)
        cfg.STAT_IRON_PRODUCTION_PM: 2, # Produit 2 fer/minute
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            # MODIFIÉ: Utilisation de miner.png pour 'single'
            "single": "miner.png",
            # SPRITE: Ces fichiers n'existent pas dans la capture, noms placeholders. Créez-les ou adaptez la logique.
            "stacked_bottom": "miner_stacked_bottom.png",
            "stacked_middle": "miner_stacked_middle.png",
            "stacked_top": "miner_stacked_top.png",
        },
        # MODIFIÉ: Sprite par défaut est miner.png
        cfg.STAT_SPRITE_DEFAULT_NAME: "miner.png",
    },
    "storage": {
        cfg.STAT_COST_MONEY: 100,
        cfg.STAT_IRON_STORAGE_INCREASE: 250,
        cfg.STAT_ADJACENCY_BONUS_VALUE: 50, # +50 capacité par stockage adjacent
        cfg.STAT_SPRITE_VARIANTS_DICT: {
            # MODIFIÉ: Utilisation de storage.png
            "single": "storage.png",
            # SPRITE: Ajouter ici les noms de fichiers pour les sprites de stockage connectés si vous en créez.
        },
        # MODIFIÉ: Utilisation de storage.png
        cfg.STAT_SPRITE_DEFAULT_NAME: "storage.png",
    }
}

TURRET_STATS = {
    "gatling_turret": {
        cfg.STAT_COST_MONEY: 100, cfg.STAT_COST_IRON: 20,
        cfg.STAT_POWER_CONSUMPTION: 5, # Valeur positive
        cfg.STAT_RANGE_PIXELS: 200, # Portée en pixels (valeur de base, scalée dans __init__)
        cfg.STAT_FIRE_RATE_PER_SEC: 5, # Tirs par seconde
        cfg.STAT_PROJECTILE_TYPE_ID: "bullet",
        # SPRITE: Asset manquant pour la base. Utilisation d'un placeholder.
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
        # MODIFIÉ: Utilisation de gun_sketch.png pour le canon.
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "gun_sketch.png",
    },
    "mortar_turret": {
        cfg.STAT_COST_MONEY: 250, cfg.STAT_COST_IRON: 75,
        cfg.STAT_POWER_CONSUMPTION: 8, # Valeur positive
        cfg.STAT_MIN_RANGE_PIXELS: 100, # Valeur de base
        cfg.STAT_MAX_RANGE_PIXELS: 450, # Valeur de base
        cfg.STAT_FIRE_RATE_PER_SEC: 0.5, # 1 tir toutes les 2 secondes
        cfg.STAT_PROJECTILE_TYPE_ID: "mortar_shell",
        cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS: 180, # Vitesse initiale du projectile (valeur de base)
        # SPRITE: Asset manquant pour la base. Utilisation d'un placeholder.
        cfg.STAT_TURRET_BASE_SPRITE_NAME: "turret_base_placeholder.png",
         # MODIFIÉ: Utilisation de mortar_sketch.png pour le canon.
        cfg.STAT_TURRET_GUN_SPRITE_NAME: "mortar_sketch.png",
    }
    # SPRITE: Si vous voulez ajouter Flamethrower ou Sniper, définissez leurs stats ici
    # en utilisant "flame.png" et "sniper_sketch.png" (et des placeholders pour leurs bases).
}

PROJECTILE_STATS = {
    "bullet": {
        cfg.STAT_DAMAGE_AMOUNT: 10,
        cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS: 600, # Vitesse du projectile (valeur de base)
        # SPRITE: Asset manquant. Nom placeholder.
        cfg.STAT_SPRITE_DEFAULT_NAME: "bullet.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 3.0,
    },
    "mortar_shell": {
        cfg.STAT_DAMAGE_AMOUNT: 50,
        # STAT_PROJECTILE_LAUNCH_SPEED_PIXELS est défini dans la tourelle mortier
        cfg.STAT_AOE_RADIUS_PIXELS: 50, # Rayon AoE (valeur de base)
        # SPRITE: Asset manquant. Nom placeholder.
        cfg.STAT_SPRITE_DEFAULT_NAME: "mortar_shell.png",
        cfg.STAT_PROJECTILE_LIFETIME_SEC: 7.0,
    }
    # SPRITE: Ajouter ici les stats pour les projectiles de flammes si vous ajoutez ce type.
}

ENEMY_STATS = {
    1: { # Ennemi Basique
        cfg.STAT_HP_MAX: 50,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 60, # Vitesse en pixels/sec de référence (valeur de base)
        cfg.STAT_DAMAGE_TO_CITY: 10,
        cfg.STAT_SCORE_POINTS_VALUE: 10,
        cfg.STAT_MONEY_DROP_VALUE: 5,
        # MODIFIÉ: Utilisation de enemy_basic_sketch.png
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_basic_sketch.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.8, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.2,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.8, 0.8) # (scale_w, scale_h) par rapport au rect du sprite
    },
    2: { # Ennemi Rapide
        cfg.STAT_HP_MAX: 30,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 120, # Valeur de base
        cfg.STAT_DAMAGE_TO_CITY: 5,
        cfg.STAT_SCORE_POINTS_VALUE: 15,
        cfg.STAT_MONEY_DROP_VALUE: 7,
        # SPRITE: Asset manquant. Nom placeholder.
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_fast.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 0.7, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.0,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.7, 0.9)
    },
    3: { # Ennemi Tank
        cfg.STAT_HP_MAX: 200,
        cfg.STAT_MOVE_SPEED_PIXELS_SEC: 30, # Valeur de base
        cfg.STAT_DAMAGE_TO_CITY: 25,
        cfg.STAT_SCORE_POINTS_VALUE: 50,
        cfg.STAT_MONEY_DROP_VALUE: 20,
         # SPRITE: Asset manquant. Nom placeholder.
        cfg.STAT_SPRITE_DEFAULT_NAME: "enemy_tank.png",
        cfg.STAT_SIZE_MIN_SCALE_FACTOR: 1.3, cfg.STAT_SIZE_MAX_SCALE_FACTOR: 1.6,
        cfg.STAT_HITBOX_SCALE_FACTORS_WH: (0.9, 0.9)
    },
}

# Fonctions utilitaires pour vérifier les types
def get_item_stats(item_type_string):
    if item_type_string in BUILDING_STATS:
        return BUILDING_STATS[item_type_string]
    if item_type_string in TURRET_STATS:
        return TURRET_STATS[item_type_string]
    return {}

def is_building_type(item_type_string):
    return item_type_string in BUILDING_STATS

def is_turret_type(item_type_string):
    return item_type_string in TURRET_STATS

def is_foundation_type(item_type_string):
    return item_type_string == "foundation"


# --- Classe de Base pour les Objets de Jeu ---
class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.active = True
        self.rect = pygame.Rect(0,0,0,0)
        self.sprite = None
        self.original_sprite = None

    def draw(self, surface):
        if self.active and self.sprite:
            surface.blit(self.sprite, self.rect.topleft)

    def update(self, delta_time, game_state_ref):
        pass


# --- Bâtiments ---
class Building(GameObject):
    _id_counter = 0
    def __init__(self, building_type, grid_pos_tuple): # (row, col)
        super().__init__()
        Building._id_counter += 1
        self.id = Building._id_counter
        self.type = building_type
        self.grid_pos = grid_pos_tuple
        self.stats = BUILDING_STATS.get(self.type, {})

        self.cost_money = self.stats.get(cfg.STAT_COST_MONEY, 0)
        self.cost_iron = self.stats.get(cfg.STAT_COST_IRON, 0)
        self.power_production = self.stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0) # Est positif
        self.iron_production_pm = self.stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
        self.iron_storage_increase = self.stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
        self.adjacency_bonus_per_unit = self.stats.get(cfg.STAT_ADJACENCY_BONUS_VALUE, 0)
        self.current_adjacency_bonus_value = 0

        self.sprites_dict = {}
        if cfg.STAT_SPRITE_VARIANTS_DICT in self.stats:
            for key, sprite_name in self.stats[cfg.STAT_SPRITE_VARIANTS_DICT].items():
                path = cfg.BUILDING_SPRITE_PATH + sprite_name
                self.sprites_dict[key] = util.load_sprite(path)
        
        default_sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        
        if "single" in self.sprites_dict and self.sprites_dict["single"]:
            self.original_sprite = self.sprites_dict["single"]
        else: 
             self.original_sprite = util.load_sprite(cfg.BUILDING_SPRITE_PATH + default_sprite_name)
        
        self.sprite = util.scale_sprite_to_tile(self.original_sprite)
        if not self.sprite: 
            self.sprite = pygame.Surface((cfg.TILE_SIZE, cfg.TILE_SIZE)); self.sprite.fill(cfg.COLOR_BLUE)

        # Le calcul de pixel_pos dépend de la logique de game_state pour cfg.GRID_OFFSET_Y
        # Si game_state.buildable_area_rect_pixels.y est utilisé, il doit être passé ou accessible
        pixel_pos = util.convert_grid_to_pixels(self.grid_pos, 
                                               (cfg.GRID_OFFSET_X, cfg.GRID_OFFSET_Y)) # Utilise cfg.GRID_OFFSET_Y comme placeholder
        self.rect = self.sprite.get_rect(topleft=pixel_pos)
        self.is_internally_active = True

    def update_sprite_based_on_context(self, game_grid_ref):
        new_sprite_key = "single" 

        if self.type == "miner":
            row, col = self.grid_pos
            above_is_miner = False
            below_is_miner = False
            # Vérifier les tuiles valides avant d'accéder à game_grid_ref
            if row > 0 and \
               len(game_grid_ref) > row - 1 and len(game_grid_ref[row-1]) > col and \
               game_grid_ref[row - 1][col] and game_grid_ref[row - 1][col].type == "miner":
                above_is_miner = True
            if row < len(game_grid_ref) - 1 and \
               len(game_grid_ref) > row + 1 and len(game_grid_ref[row+1]) > col and \
               game_grid_ref[row + 1][col] and game_grid_ref[row + 1][col].type == "miner":
                below_is_miner = True


            if above_is_miner and below_is_miner: new_sprite_key = "stacked_middle"
            elif below_is_miner: new_sprite_key = "stacked_top"
            elif above_is_miner: new_sprite_key = "stacked_bottom"
            else: new_sprite_key = "single"
        
        elif self.type == "storage":
            pass 

        if new_sprite_key in self.sprites_dict and self.sprites_dict[new_sprite_key]:
            self.original_sprite = self.sprites_dict[new_sprite_key]
            self.sprite = util.scale_sprite_to_tile(self.original_sprite)
        else: 
            default_sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
            self.original_sprite = util.load_sprite(cfg.BUILDING_SPRITE_PATH + default_sprite_name)
            self.sprite = util.scale_sprite_to_tile(self.original_sprite)


    def apply_adjacency_bonus_effect(self, adjacent_similar_items_count):
        if self.type == "storage" and self.adjacency_bonus_per_unit > 0:
            self.current_adjacency_bonus_value = adjacent_similar_items_count * self.adjacency_bonus_per_unit
            # Le print peut être conditionnel (ex: mode debug)
            # print(f"Storage {self.id} at {self.grid_pos} got bonus: {self.current_adjacency_bonus_value} from {adjacent_similar_items_count} neighbors.")

    def set_active_state(self, is_powered):
        self.is_internally_active = is_powered


# --- Tourelles ---
class Turret(GameObject):
    _id_counter = 0
    def __init__(self, turret_type, grid_pos_tuple):
        super().__init__()
        Turret._id_counter += 1
        self.id = Turret._id_counter
        self.type = turret_type
        self.grid_pos = grid_pos_tuple
        self.stats = TURRET_STATS.get(self.type, {})

        self.power_consumption = self.stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        self.range = cfg.scale_value(self.stats.get(cfg.STAT_RANGE_PIXELS, 0))
        self.min_range = cfg.scale_value(self.stats.get(cfg.STAT_MIN_RANGE_PIXELS, 0))
        self.max_range = cfg.scale_value(self.stats.get(cfg.STAT_MAX_RANGE_PIXELS, 0))
        self.fire_rate_per_sec = self.stats.get(cfg.STAT_FIRE_RATE_PER_SEC, 1)
        self.cooldown_time_seconds = 1.0 / self.fire_rate_per_sec if self.fire_rate_per_sec > 0 else float('inf')
        self.current_cooldown = 0.0
        self.projectile_type = self.stats.get(cfg.STAT_PROJECTILE_TYPE_ID, None)
        self.projectile_initial_speed = cfg.scale_value(self.stats.get(cfg.STAT_PROJECTILE_LAUNCH_SPEED_PIXELS, 0))

        base_sprite_name = self.stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME, "placeholder.png")
        gun_sprite_name = self.stats.get(cfg.STAT_TURRET_GUN_SPRITE_NAME, "placeholder.png")
        
        self.original_base_sprite = util.load_sprite(cfg.TURRET_SPRITE_PATH + base_sprite_name)
        self.original_gun_sprite = util.load_sprite(cfg.TURRET_SPRITE_PATH + gun_sprite_name)

        self.base_sprite = util.scale_sprite_to_tile(self.original_base_sprite)
        if self.original_gun_sprite: # S'assurer que le sprite du canon a été chargé
            self.gun_sprite_scaled_original = util.scale_sprite_to_tile(self.original_gun_sprite) 
            self.gun_sprite_rotated = self.gun_sprite_scaled_original
        else: # Fallback si le sprite du canon n'est pas chargé
            self.gun_sprite_scaled_original = pygame.Surface((cfg.TILE_SIZE, cfg.TILE_SIZE // 2)) # Exemple de taille
            self.gun_sprite_scaled_original.fill(cfg.COLOR_GREEN)
            self.gun_sprite_rotated = self.gun_sprite_scaled_original


        if not self.base_sprite: self.base_sprite = pygame.Surface((cfg.TILE_SIZE,cfg.TILE_SIZE)); self.base_sprite.fill(cfg.COLOR_BLUE)
        # self.gun_sprite_rotated est déjà géré par le fallback ci-dessus

        pixel_pos = util.convert_grid_to_pixels(self.grid_pos, (cfg.GRID_OFFSET_X, cfg.GRID_OFFSET_Y))
        self.rect = self.base_sprite.get_rect(topleft=pixel_pos)
        if self.gun_sprite_scaled_original:
            self.gun_pivot_offset = (self.gun_sprite_scaled_original.get_width() // 2, self.gun_sprite_scaled_original.get_height() // 2)
        else:
            self.gun_pivot_offset = (cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 4) # Fallback pivot

        self.target_enemy = None
        self.current_angle_deg = 0
        self.is_internally_active = True

    def set_active_state(self, is_powered):
        self.is_internally_active = is_powered

    def find_target(self, enemies_list):
        self.target_enemy = None
        closest_dist_sq = float('inf')
        turret_center_x, turret_center_y = self.rect.centerx, self.rect.centery

        for enemy in enemies_list:
            if not enemy.active or not hasattr(enemy, 'rect'): continue # Vérifier active et rect
            dist_sq = (enemy.rect.centerx - turret_center_x)**2 + (enemy.rect.centery - turret_center_y)**2
            
            target_in_range = False
            if self.type == "mortar_turret":
                if self.min_range**2 <= dist_sq <= self.max_range**2:
                    target_in_range = True
            else: 
                if dist_sq <= self.range**2:
                    target_in_range = True
            
            if target_in_range and dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                self.target_enemy = enemy
    
    def update(self, delta_time, enemies_list, is_powered_globally, game_state_ref):
        self.set_active_state(is_powered_globally)
        if not self.active or not self.is_internally_active:
            self.target_enemy = None
            return

        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time

        if not self.target_enemy or not self.target_enemy.active or not hasattr(self.target_enemy, 'rect'): # Vérifier aussi rect
            self.find_target(enemies_list)

        if self.target_enemy and hasattr(self.target_enemy, 'rect'): # S'assurer que la cible est valide
            dx = self.target_enemy.rect.centerx - self.rect.centerx
            dy = self.target_enemy.rect.centery - self.rect.centery
            
            self.current_angle_deg = math.degrees(math.atan2(-dy, dx))
            if self.gun_sprite_scaled_original: # Vérifier que le sprite existe avant de le transformer
                self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
            
            if self.current_cooldown <= 0:
                self.shoot(game_state_ref)
                self.current_cooldown = self.cooldown_time_seconds
        else:
            self.target_enemy = None # Réinitialiser si la cible devient invalide

    def shoot(self, game_state_ref):
        if not self.target_enemy or not self.projectile_type or not hasattr(self.target_enemy, 'rect'): return

        proj_origin_x = self.rect.centerx + math.cos(math.radians(self.current_angle_deg)) * (cfg.TILE_SIZE // 3)
        proj_origin_y = self.rect.centery - math.sin(math.radians(self.current_angle_deg)) * (cfg.TILE_SIZE // 3)
        proj_origin = (proj_origin_x, proj_origin_y)

        if self.type == "mortar_turret":
            fire_solution = calculate_mortar_fire_solution(
                self.rect.center,
                self.target_enemy.rect.center,
                self.projectile_initial_speed, 
                cfg.GRAVITY 
            )
            if fire_solution:
                launch_angle_rad_vertical, _ = fire_solution
                angle_horizontal_rad = math.radians(self.current_angle_deg)
                v_horizontal_component = self.projectile_initial_speed * math.cos(launch_angle_rad_vertical)
                
                vx = v_horizontal_component * math.cos(angle_horizontal_rad)
                vy_physics = self.projectile_initial_speed * math.sin(launch_angle_rad_vertical)
                vy_pygame = -vy_physics 
                                
                new_proj = Projectile(self.projectile_type, proj_origin, 0, initial_vx=vx, initial_vy=vy_pygame)
                if hasattr(game_state_ref, 'projectiles'): # Vérifier si game_state_ref a la liste projectiles
                    game_state_ref.projectiles.append(new_proj)
        else: 
            new_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg)
            if hasattr(game_state_ref, 'projectiles'):
                game_state_ref.projectiles.append(new_proj)

    def draw(self, surface):
        if self.active and self.base_sprite:
            surface.blit(self.base_sprite, self.rect.topleft)
        
        if self.active and self.gun_sprite_rotated:
            # S'assurer que gun_sprite_rotated est une Surface valide
            if isinstance(self.gun_sprite_rotated, pygame.Surface):
                gun_rect = self.gun_sprite_rotated.get_rect(center=self.rect.center)
                surface.blit(self.gun_sprite_rotated, gun_rect.topleft)


# --- Projectiles ---
class Projectile(GameObject):
    _id_counter = 0
    def __init__(self, projectile_type, origin_xy_pixels, angle_deg, initial_vx=None, initial_vy=None):
        super().__init__()
        Projectile._id_counter += 1
        self.id = Projectile._id_counter
        self.type = projectile_type
        self.stats = PROJECTILE_STATS.get(self.type, {})

        self.damage = self.stats.get(cfg.STAT_DAMAGE_AMOUNT, 0)
        self.speed = cfg.scale_value(self.stats.get(cfg.STAT_PROJECTILE_FLAT_SPEED_PIXELS, 0))
        self.aoe_radius = cfg.scale_value(self.stats.get(cfg.STAT_AOE_RADIUS_PIXELS, 0))
        self.lifetime_seconds = self.stats.get(cfg.STAT_PROJECTILE_LIFETIME_SEC, 5.0)

        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(cfg.PROJECTILE_SPRITE_PATH + sprite_name)
        
        if self.original_sprite:
            proj_w = cfg.scale_value(self.original_sprite.get_width() * 0.5) 
            proj_h = cfg.scale_value(self.original_sprite.get_height() * 0.5)
            self.sprite_scaled_original = util.scale_sprite_to_size(self.original_sprite, proj_w, proj_h)
        else: # Fallback si le sprite original n'est pas chargé
            self.sprite_scaled_original = pygame.Surface((cfg.scale_value(10), cfg.scale_value(10))) # Petite taille par défaut
            self.sprite_scaled_original.fill(cfg.COLOR_YELLOW) # Couleur placeholder
        
        self.is_mortar_shell = (self.type == "mortar_shell")

        if self.is_mortar_shell:
            self.vx = initial_vx if initial_vx is not None else 0
            self.vy_physics = -initial_vy if initial_vy is not None else 0 
            self.sprite = self.sprite_scaled_original
        else: 
            self.angle_rad = math.radians(angle_deg)
            self.vx = self.speed * math.cos(self.angle_rad)
            self.vy_physics = self.speed * math.sin(self.angle_rad) # Note: atan2 utilise (-dy, dx), donc sin(angle_rad) est correct pour dy pygame
            if self.sprite_scaled_original: # Vérifier que le sprite existe
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, angle_deg)
            else:
                self.sprite = None # Ou un fallback

        if self.sprite:
            self.rect = self.sprite.get_rect(center=origin_xy_pixels)
        else: # Fallback si self.sprite n'a pas été créé (ex: sprite_scaled_original était None)
            self.rect = pygame.Rect(origin_xy_pixels[0]-5, origin_xy_pixels[1]-5, 10, 10) # Petit rect par défaut


    def update(self, delta_time, game_state_ref=None):
        if not self.active: return

        self.lifetime_seconds -= delta_time
        if self.lifetime_seconds <= 0:
            self.active = False
            return

        if self.is_mortar_shell:
            self.rect.x += self.vx * delta_time
            self.rect.y += -self.vy_physics * delta_time 
            self.vy_physics -= cfg.GRAVITY * delta_time
            
            if self.sprite_scaled_original: # Vérifier avant de rotate
                current_angle_rad_physics = math.atan2(self.vy_physics, self.vx)
                self.sprite = pygame.transform.rotate(self.sprite_scaled_original, math.degrees(current_angle_rad_physics))
        else: 
            self.rect.x += self.vx * delta_time
            self.rect.y += -self.vy_physics * delta_time # dy_pygame = -vy_physics

        # Vérifier si hors écran
        # S'assurer que SCREEN_WIDTH et SCREEN_HEIGHT sont bien définis dans cfg
        if hasattr(cfg, 'SCREEN_WIDTH') and hasattr(cfg, 'SCREEN_HEIGHT'):
            screen_rect = pygame.Rect(0,0, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
            if not screen_rect.colliderect(self.rect.inflate(200,200)):
                self.active = False

    def on_hit(self, game_state_ref):
        self.active = False
        if self.is_mortar_shell and self.aoe_radius > 0:
            if hasattr(game_state_ref, 'trigger_aoe_damage'): # Vérifier la méthode
                game_state_ref.trigger_aoe_damage(self.rect.center, self.aoe_radius, self.damage)


# --- Ennemis ---
class Enemy(GameObject):
    _id_counter = 0
    def __init__(self, initial_pos_xy_ref, enemy_type_id, variant_data=None):
        super().__init__()
        Enemy._id_counter += 1
        self.id = Enemy._id_counter
        self.type_id = enemy_type_id
        self.stats = ENEMY_STATS.get(self.type_id, ENEMY_STATS[1]) # Fallback au type 1 si type_id inconnu

        self.max_hp = self.stats.get(cfg.STAT_HP_MAX, 10)
        self.current_hp = self.max_hp
        self.speed_pixels_sec = cfg.scale_value(self.stats.get(cfg.STAT_MOVE_SPEED_PIXELS_SEC, 30)) # Renommé pour clarté
        self.city_damage = self.stats.get(cfg.STAT_DAMAGE_TO_CITY, 1)
        self.score_value = self.stats.get(cfg.STAT_SCORE_POINTS_VALUE, 0)
        self.money_value = self.stats.get(cfg.STAT_MONEY_DROP_VALUE, 0)

        sprite_name = self.stats.get(cfg.STAT_SPRITE_DEFAULT_NAME, "placeholder.png")
        self.original_sprite = util.load_sprite(cfg.ENEMY_SPRITE_PATH + sprite_name)

        min_s = self.stats.get(cfg.STAT_SIZE_MIN_SCALE_FACTOR, 1.0)
        max_s = self.stats.get(cfg.STAT_SIZE_MAX_SCALE_FACTOR, 1.0)
        random_scale_factor = random.uniform(min_s, max_s)

        if self.original_sprite:
            # La taille de base du sprite est multipliée par le scale aléatoire, puis par le scale général du jeu.
            # S'assurer que GENERAL_SCALE est un float.
            scaled_w = int(self.original_sprite.get_width() * random_scale_factor * float(cfg.GENERAL_SCALE))
            scaled_h = int(self.original_sprite.get_height() * random_scale_factor * float(cfg.GENERAL_SCALE))
            self.sprite = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)
        else: # Fallback si original_sprite n'est pas chargé
            default_size = cfg.scale_value(30) # Taille par défaut pour fallback
            self.sprite = pygame.Surface((default_size, default_size))
            self.sprite.fill(cfg.COLOR_RED) 
        
        # Position initiale scalée. cfg.scale_value doit pouvoir gérer les tuples.
        scaled_initial_pos = cfg.scale_value(initial_pos_xy_ref) 
        if self.sprite:
            self.rect = self.sprite.get_rect(center=scaled_initial_pos)
        else: # Fallback si sprite n'est pas créé
            self.rect = pygame.Rect(scaled_initial_pos[0]-15, scaled_initial_pos[1]-15, 30, 30)


        # Hitbox
        hitbox_scale_w, hitbox_scale_h = self.stats.get(cfg.STAT_HITBOX_SCALE_FACTORS_WH, (0.8,0.8))
        hitbox_width = int(self.rect.width * hitbox_scale_w)
        hitbox_height = int(self.rect.height * hitbox_scale_h)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.hitbox.center = self.rect.center


    def update(self, delta_time, game_state_ref=None): 
        if not self.active: return

        self.rect.x -= self.speed_pixels_sec * delta_time # Utiliser la variable renommée
        self.hitbox.center = self.rect.center

        if self.rect.right < 0: 
            self.active = False


    def take_damage(self, amount):
        if not self.active: return
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.active = False
            # Le print peut être conditionnel
            # print(f"Enemy {self.id} (type {self.type_id}) died.")

    def get_city_damage(self): return self.city_damage
    def get_score_value(self): return self.score_value
    def get_money_value(self): return self.money_value

    def draw(self, surface):
        super().draw(surface) # Dessine le sprite principal (si self.sprite existe)
        if self.active and self.current_hp < self.max_hp and self.max_hp > 0 : # Éviter division par zéro
            # S'assurer que les couleurs sont définies dans cfg
            hp_bar_bg_color = getattr(cfg, 'COLOR_HP_BAR_BACKGROUND', cfg.COLOR_GREY_DARK)
            hp_bar_fill_color = getattr(cfg, 'COLOR_HP_FULL', cfg.COLOR_GREEN)
            
            # Changer la couleur de la barre de vie en fonction des HP restants
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio < 0.3: hp_bar_fill_color = getattr(cfg, 'COLOR_HP_CRITICAL', cfg.COLOR_RED)
            elif hp_ratio < 0.6: hp_bar_fill_color = getattr(cfg, 'COLOR_HP_LOW', cfg.COLOR_ORANGE) # Ou COLOR_HP_MEDIUM

            bar_w = cfg.scale_value(30)
            bar_h = cfg.scale_value(5)
            
            bg_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - bar_h - cfg.scale_value(3), bar_w, bar_h)
            hp_fill_w = int(bar_w * hp_ratio)
            hp_rect = pygame.Rect(bg_rect.left, bg_rect.top, hp_fill_w, bar_h)
            
            pygame.draw.rect(surface, hp_bar_bg_color, bg_rect)
            pygame.draw.rect(surface, hp_bar_fill_color, hp_rect)


# --- Calcul de Trajectoire pour Mortier ---
def calculate_mortar_fire_solution(turret_pos_pixels, target_pos_pixels, projectile_initial_speed_pixels, gravity_pixels_s2):
    dx_pixels = target_pos_pixels[0] - turret_pos_pixels[0]
    dy_physics = -(target_pos_pixels[1] - turret_pos_pixels[1]) 
    
    v0 = projectile_initial_speed_pixels
    g = abs(gravity_pixels_s2) # g doit être positif

    # Éviter division par zéro si dx_pixels est très petit
    if abs(dx_pixels) < 1.0:
        # Tir vertical
        if dy_physics > 0 : # Cible au-dessus
            if v0**2 >= 2 * g * dy_physics: # Peut atteindre la hauteur
                # Pour un tir vertical atteignant dy_physics, v_final_y^2 = v0^2 - 2*g*dy_physics
                # Si on veut que le sommet de la trajectoire soit exactement à dy_physics, v_final_y = 0 => v0^2 = 2*g*dy_physics
                # Temps pour atteindre le sommet: t = v0/g. Temps pour atteindre dy_physics peut être plus complexe.
                # Solution simplifiée: on tire à 90 degrés. Le temps de vol est calculé différemment pour ce cas.
                # t = (v0 + sqrt(v0^2 - 2*g*dy_physics)) / g  (solution la plus longue, quand on repasse par y en descendant)
                # ou t = (v0 - sqrt(v0^2 - 2*g*dy_physics)) / g (solution la plus courte, en montant)
                # Choisissons la plus courte si on suppose un impact direct.
                if (v0**2 - 2*g*dy_physics) < 0: return None # Ne devrait pas arriver si v0^2 >= 2*g*dy
                time_to_target = (v0 - math.sqrt(v0**2 - 2*g*dy_physics)) / g if (v0**2 - 2*g*dy_physics) >=0 else None
                if time_to_target is not None:
                    return math.pi / 2, time_to_target # 90 degrés
            return None 
        else: # Cible en dessous (dy_physics <= 0)
            # Tir vertical vers le bas: on pourrait utiliser -pi/2 mais la formule de trajectoire gère mal cela.
            # Pour un tir direct vers le bas, on n'a pas besoin de cette fonction complexe.
            # Si on assume un tir parabolique même vers le bas, il faut un angle < 0.
            # Ce cas est généralement mal géré par la formule standard.
             return None # Simplification: pas de tir vertical direct vers le bas avec cette formule.

    discriminant = v0**4 - g * (g * dx_pixels**2 + 2 * dy_physics * v0**2)

    if discriminant < 0:
        return None

    # tan(theta) = (v0^2 +/- sqrt(discriminant)) / (g * dx)
    # On choisit généralement la solution qui donne un angle entre 0 et pi/2 (0-90 deg)
    # si dx > 0.
    # Si dx < 0, atan va donner un angle dans [-pi/2, 0] ou [pi/2, pi].

    # Solution "high arc" (theta_high) et "low arc" (theta_low)
    # Note: La formule originale est pour (g * dx) au dénominateur.
    # Si dx est 0, géré ci-dessus.

    # Pour dx > 0:
    # theta_high = atan( (v0^2 + sqrt(discriminant)) / (g * dx_pixels) )
    # theta_low  = atan( (v0^2 - sqrt(discriminant)) / (g * dx_pixels) )

    # Pour dx < 0:
    # L'angle sera ajusté par atan2 plus tard, ou on peut utiliser abs(dx) et ajuster l'angle final.
    # Ou on laisse dx_pixels avec son signe. atan() s'en chargera.
    
    # On préfère souvent l'angle le plus bas qui atteint la cible, ou le plus haut si spécifié.
    # Prenons la solution "high arc" qui donne un angle de tir plus élevé.
    # Ou la solution qui minimise le temps de vol si les deux sont possibles (low arc).
    # Pour les mortiers, le "high arc" est plus typique.

    # Attention: si g * dx_pixels est 0, ce qui est géré.
    sqrt_discriminant = math.sqrt(discriminant)
    tan_theta_high = (v0**2 + sqrt_discriminant) / (g * dx_pixels)
    # tan_theta_low = (v0**2 - sqrt_discriminant) / (g * dx_pixels) # Optionnel

    # On choisit l'angle haut par défaut pour un mortier
    chosen_angle_rad = math.atan(tan_theta_high)

    # Ajustement si dx_pixels < 0:
    # Si dx < 0 et dy > 0 (quadrant II), atan donne <0. On veut angle > pi/2.
    # Si dx < 0 et dy < 0 (quadrant III), atan donne >0. On veut angle > pi.
    # La rotation du canon de la tourelle (current_angle_deg) gère déjà la direction horizontale.
    # Ce 'chosen_angle_rad' est l'angle d'élévation vertical par rapport à cette direction horizontale.
    # Il devrait donc toujours être positif (entre 0 et pi/2).
    # La formule originale de Wikipedia pour l'angle de lancement theta pour atteindre (x,y) est :
    # tan(theta) = (v^2 +/- sqrt(v^4 - g(gx^2 + 2yv^2))) / gx
    # Notre dy_physics est 'y' et dx_pixels est 'x'.
    # Si on prend la distance horizontale d = sqrt(dx_pixels^2), et on utilise dx_pixels pour la direction.
    # L'angle calculé ici est l'angle d'élévation.

    # Temps de vol: t = dx / (v0 * cos(theta))
    # Si cos(theta) est 0 (tir vertical à 90 deg), géré plus haut.
    cos_chosen_angle = math.cos(chosen_angle_rad)
    if abs(cos_chosen_angle) < 1e-6: # Proche de zéro
        # Ce cas devrait être couvert par le tir vertical (dx_pixels ~ 0)
        # S'il arrive ici, c'est une situation limite.
        # Récupérer le temps du cas vertical si possible.
        if dy_physics > 0 and v0**2 >= 2 * g * dy_physics:
             time_to_target = (v0 - math.sqrt(v0**2 - 2*g*dy_physics)) / g
             return math.pi/2, time_to_target
        return None 
        
    time_of_flight = dx_pixels / (v0 * cos_chosen_angle)

    # Le temps de vol doit être positif. Si dx et cos(angle) ont des signes opposés
    # (ex: dx < 0, angle > pi/2 -> cos < 0), t > 0.
    # Si dx < 0, et angle est < pi/2 (donc cos > 0), t < 0, solution invalide.
    # Cela signifie que l'angle choisi ne permet pas d'atteindre une cible derrière avec un tir "vers l'avant".
    # La direction est déjà gérée par la tourelle (angle horizontal).
    # Donc dx_pixels ici est la distance projetée dans la direction de visée.
    # Si la cible est "derrière" la tourelle par rapport à sa visée, dx_pixels sera < 0.
    # Si l'angle d'élévation est positif, cos(chosen_angle_rad) > 0. Donc t < 0.
    # La fonction `calculate_mortar_fire_solution` devrait probablement prendre
    # la distance horizontale `d = sqrt(dx^2 + dy_horizontal^2)` et `target_height_diff = dy_vertical`
    # où dx et dy_horizontal sont dans le plan du sol.
    # Pour l'instant, dx_pixels est la distance directe sur l'axe X du jeu.

    if time_of_flight < 0 :
        # Tenter avec l'autre solution d'angle (low arc) si le high arc donne t < 0.
        # Ceci est plus complexe que prévu initialement.
        # Une solution plus simple: si t < 0, la solution n'est pas valide pour un tir "en avant".
        # Le mortier ne peut pas tirer "en arrière" par dessus lui-même avec un angle positif.
        # La rotation de la tourelle devrait s'occuper de viser dans la bonne direction horizontale.
        # Donc, si la tourelle vise (current_angle_deg) et que dx_pixels (calculé à partir de cette visée)
        # et chosen_angle_rad (élévation) mènent à t < 0, alors c'est inatteignable avec cet angle.
        return None

    return chosen_angle_rad, time_of_flight


# --- Effets de Particules (Exemple: Explosion) ---
class ParticleEffect(GameObject):
    def __init__(self, position_xy, animation_frames_list, frame_duration):
        super().__init__()
        # S'assurer que animation_frames_list contient des Surfaces valides
        self.frames = []
        if animation_frames_list:
            for f_original in animation_frames_list:
                if isinstance(f_original, pygame.Surface):
                    # Les frames d'effets ne sont pas forcément scalées à TILE_SIZE
                    # Elles peuvent avoir leur propre scaling ou taille désirée.
                    # Pour l'instant, on les scale à TILE_SIZE pour l'exemple.
                    self.frames.append(util.scale_sprite_to_tile(f_original)) 
                # else: print(f"Warning: Invalid frame found in ParticleEffect: {f_original}")

        self.frame_duration = frame_duration
        self.current_frame_index = 0
        self.time_on_current_frame = 0
        
        if self.frames:
            self.sprite = self.frames[0]
            self.rect = self.sprite.get_rect(center=position_xy)
        else: # Fallback si aucune frame valide
            self.sprite = None
            self.rect = pygame.Rect(position_xy[0], position_xy[1], 0, 0)
            self.active = False # Pas d'animation à jouer

    def update(self, delta_time, game_state_ref=None):
        if not self.active or not self.frames: return

        self.time_on_current_frame += delta_time
        if self.time_on_current_frame >= self.frame_duration:
            self.time_on_current_frame -= self.frame_duration # Soustraire pour la précision
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                self.active = False 
            else:
                self.sprite = self.frames[self.current_frame_index]
                # Important: recentrer si les frames ont des tailles différentes
                if self.sprite: # S'assurer que le sprite est valide
                    current_center = self.rect.center
                    self.rect = self.sprite.get_rect(center=current_center)
