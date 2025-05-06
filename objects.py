# objects.py
import pygame
import random
import math
import game_config as cfg
import utility_functions as util
# game_functions est importé conditionnellement ou on passe game_state pour éviter dépendance circulaire si besoin

# --- Définitions des Stats des Objets ---
# Ces dictionnaires contiennent les propriétés de base pour chaque type d'objet.
# Les sprites sont chargés et scalés dans le __init__ de chaque classe.

BUILDING_STATS = {
    "foundation": {
        cfg.STAT_COST_MONEY: 50,
        cfg.STAT_SPRITE: "foundation_wood.png", # SPRITE: Votre image de fondation
        # Les fondations n'ont pas de HP car invulnérables
    },
    "generator": {
        cfg.STAT_COST_MONEY: 150,
        cfg.STAT_POWER_PROD: 10, # Produit 10W
        cfg.STAT_SPRITE: "generator.png", # SPRITE: Votre image de générateur
    },
    "miner": {
        cfg.STAT_COST_MONEY: 200, cfg.STAT_COST_IRON: 50,
        cfg.STAT_POWER: -2, # Consomme 2W
        cfg.STAT_IRON_PROD: 2, # Produit 2 fer/minute
        # SPRITE: Sprites pour mineur (simple, empilé bas/milieu/haut)
        cfg.STAT_SPRITES: { 
            "single": "miner_single.png",
            "stacked_bottom": "miner_stacked_bottom.png",
            "stacked_middle": "miner_stacked_middle.png",
            "stacked_top": "miner_stacked_top.png",
        },
        cfg.STAT_SPRITE: "miner_single.png", # Sprite par défaut
    },
    "storage": {
        cfg.STAT_COST_MONEY: 100,
        cfg.STAT_IRON_STORAGE: 250,
        cfg.STAT_ADJACENCY_BONUS: 50, # +50 capacité par stockage adjacent
        # SPRITE: Sprites pour stockage (simple, avec bonus N/S/E/W etc.)
        cfg.STAT_SPRITES: {
            "single": "storage_single.png",
            # "adj_N": "storage_adj_N.png", ... etc. si vous avez des sprites spécifiques
        },
        cfg.STAT_SPRITE: "storage_single.png",
    }
}

TURRET_STATS = {
    "gatling_turret": {
        cfg.STAT_COST_MONEY: 100, cfg.STAT_COST_IRON: 20,
        cfg.STAT_POWER: -5,
        cfg.STAT_RANGE: cfg.scale_value(200), # Portée en pixels (scalée)
        cfg.STAT_FIRE_RATE: 5, # Tirs par seconde
        cfg.STAT_PROJ_TYPE: "bullet",
        # SPRITE: Noms des fichiers pour la base et le canon
        "base_sprite": "turret_base_gatling.png",
        "gun_sprite": "turret_gun_gatling.png",
    },
    "mortar_turret": {
        cfg.STAT_COST_MONEY: 250, cfg.STAT_COST_IRON: 75,
        cfg.STAT_POWER: -8,
        cfg.STAT_MIN_RANGE: cfg.scale_value(100),
        cfg.STAT_MAX_RANGE: cfg.scale_value(450),
        cfg.STAT_FIRE_RATE: 0.5, # 1 tir toutes les 2 secondes
        cfg.STAT_PROJ_TYPE: "mortar_shell",
        cfg.STAT_PROJ_SPEED: cfg.scale_value(180), # Vitesse initiale du projectile (scalée)
        "base_sprite": "turret_base_mortar.png",
        "gun_sprite": "turret_gun_mortar.png",
    }
}

PROJECTILE_STATS = {
    "bullet": {
        cfg.STAT_DAMAGE: 10,
        cfg.STAT_SPEED: cfg.scale_value(600), # Vitesse du projectile (scalée)
        cfg.STAT_SPRITE: "bullet.png", # SPRITE
    },
    "mortar_shell": {
        cfg.STAT_DAMAGE: 50,
        # STAT_PROJ_SPEED est défini dans la tourelle mortier car c'est une vitesse de lancement
        cfg.STAT_AOE_RADIUS: cfg.scale_value(50), # Rayon AoE (scalé)
        cfg.STAT_SPRITE: "mortar_shell.png", # SPRITE
    }
}

ENEMY_STATS = {
    # ID Type: {stats}
    1: { # Ennemi Basique
        cfg.STAT_HP: 50,
        cfg.STAT_SPEED: cfg.scale_value(60), # Vitesse en pixels/sec de référence (scalée)
        cfg.STAT_CITY_DAMAGE: 10,
        cfg.STAT_SCORE_VALUE: 10,
        cfg.STAT_MONEY_VALUE: 5,
        cfg.STAT_SPRITE: "enemy_basic.png", # SPRITE
        cfg.STAT_SIZE_MIN: 0.8, cfg.STAT_SIZE_MAX: 1.2, # Facteurs d'échelle min/max
        cfg.STAT_HITBOX_SCALE: (0.8, 0.8) # (scale_w, scale_h) par rapport au rect du sprite
    },
    2: { # Ennemi Rapide
        cfg.STAT_HP: 30,
        cfg.STAT_SPEED: cfg.scale_value(120),
        cfg.STAT_CITY_DAMAGE: 5,
        cfg.STAT_SCORE_VALUE: 15,
        cfg.STAT_MONEY_VALUE: 7,
        cfg.STAT_SPRITE: "enemy_fast.png", # SPRITE
        cfg.STAT_SIZE_MIN: 0.7, cfg.STAT_SIZE_MAX: 1.0,
        cfg.STAT_HITBOX_SCALE: (0.7, 0.9)
    },
    3: { # Ennemi Tank
        cfg.STAT_HP: 200,
        cfg.STAT_SPEED: cfg.scale_value(30),
        cfg.STAT_CITY_DAMAGE: 25,
        cfg.STAT_SCORE_VALUE: 50,
        cfg.STAT_MONEY_VALUE: 20,
        cfg.STAT_SPRITE: "enemy_tank.png", # SPRITE
        cfg.STAT_SIZE_MIN: 1.3, cfg.STAT_SIZE_MAX: 1.6,
        cfg.STAT_HITBOX_SCALE: (0.9, 0.9)
    },
    # TODO: Ajouter d'autres types d'ennemis
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
class GameObject(pygame.sprite.Sprite): # Hériter de Sprite peut être utile pour les groupes
    def __init__(self):
        super().__init__() # Nécessaire si on utilise pygame.sprite.Group
        self.active = True # Tous les objets ont un état actif
        self.rect = pygame.Rect(0,0,0,0)
        self.sprite = None
        self.original_sprite = None # Pour rescaler si besoin

    def draw(self, surface):
        if self.active and self.sprite:
            surface.blit(self.sprite, self.rect.topleft)

    def update(self, delta_time, game_state_ref): # game_state_ref pour interdépendances
        pass # Logique de mise à jour spécifique à chaque objet


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

        # Propriétés spécifiques (initialisées depuis les stats)
        self.cost_money = self.stats.get(cfg.STAT_COST_MONEY, 0)
        self.cost_iron = self.stats.get(cfg.STAT_COST_IRON, 0)
        self.power_production = self.stats.get(cfg.STAT_POWER_PROD, 0)
        self.power_consumption = abs(self.stats.get(cfg.STAT_POWER, 0)) # Consommation est positive
        self.iron_production_pm = self.stats.get(cfg.STAT_IRON_PROD, 0)
        self.iron_storage_increase = self.stats.get(cfg.STAT_IRON_STORAGE, 0)
        self.adjacency_bonus_per_unit = self.stats.get(cfg.STAT_ADJACENCY_BONUS, 0)
        self.current_adjacency_bonus_value = 0 # Stocke le bonus de capacité effectif

        # Sprite et Position
        self.sprites_dict = {} # Pour les sprites contextuels
        if cfg.STAT_SPRITES in self.stats:
            for key, sprite_name in self.stats[cfg.STAT_SPRITES].items():
                path = cfg.BUILDING_SPRITE_PATH + sprite_name
                self.sprites_dict[key] = util.load_sprite(path)
        
        default_sprite_name = self.stats.get(cfg.STAT_SPRITE, "placeholder.png") # Fallback
        self.original_sprite = self.sprites_dict.get("single", util.load_sprite(cfg.BUILDING_SPRITE_PATH + default_sprite_name))
        
        self.sprite = util.scale_sprite_to_tile(self.original_sprite)
        if not self.sprite: # Fallback en cas d'erreur de chargement/scaling
            self.sprite = pygame.Surface((cfg.TILE_SIZE, cfg.TILE_SIZE)); self.sprite.fill(cfg.COLOR_BLUE)

        # Le game_state est nécessaire pour obtenir cfg.GRID_OFFSET_Y qui peut changer
        # On va supposer qu'il est passé ou accessible globalement pour la position initiale.
        # Idéalement, la position en pixels est calculée dans game_functions et passée ici.
        # Pour l'instant, on la recalcule, en supposant que cfg.GRID_OFFSET_Y est le Y actuel de la grille.
        pixel_pos = util.convert_grid_to_pixels(self.grid_pos, 
                                               (cfg.GRID_OFFSET_X, cfg.GRID_OFFSET_Y)) # ATTENTION: cfg.GRID_OFFSET_Y peut être stale si la grille s'est étendue par le haut et que cfg n'est pas mis à jour dynamiquement pour ce Y. Il faudrait game_state.buildable_area_rect_pixels.y
        self.rect = self.sprite.get_rect(topleft=pixel_pos)
        self.is_internally_active = True # Si le bâtiment lui-même fonctionne (ex: assez d'énergie)

    def update_sprite_based_on_context(self, game_grid_ref):
        """Change le sprite en fonction des voisins (ex: mine empilée, stockage connecté)."""
        new_sprite_key = "single" # Par défaut

        if self.type == "miner":
            # RÈGLE: Déterminer si la mine est en bas, au milieu ou en haut d'une pile
            row, col = self.grid_pos
            above_is_miner = False
            below_is_miner = False
            if row > 0 and game_grid_ref[row - 1][col] and game_grid_ref[row - 1][col].type == "miner":
                above_is_miner = True
            if row < len(game_grid_ref) - 1 and game_grid_ref[row + 1][col] and game_grid_ref[row + 1][col].type == "miner":
                below_is_miner = True

            if above_is_miner and below_is_miner: new_sprite_key = "stacked_middle"
            elif below_is_miner: new_sprite_key = "stacked_top" # Rien au-dessus, mine en dessous
            elif above_is_miner: new_sprite_key = "stacked_bottom" # Mine au-dessus, rien en dessous (ou fondation)
            else: new_sprite_key = "single"
        
        elif self.type == "storage":
            # RÈGLE: Déterminer si des stockages sont adjacents pour un sprite connecté
            # (Simplifié pour l'instant, juste un sprite "single")
            # Si vous avez des sprites "adj_N", "adj_S", etc., la logique irait ici.
            pass # new_sprite_key reste "single"

        # Appliquer le nouveau sprite
        if new_sprite_key in self.sprites_dict and self.sprites_dict[new_sprite_key]:
            self.original_sprite = self.sprites_dict[new_sprite_key]
            self.sprite = util.scale_sprite_to_tile(self.original_sprite)
        else: # Fallback si la clé de sprite n'existe pas
            default_sprite_name = self.stats.get(cfg.STAT_SPRITE, "placeholder.png")
            self.original_sprite = util.load_sprite(cfg.BUILDING_SPRITE_PATH + default_sprite_name)
            self.sprite = util.scale_sprite_to_tile(self.original_sprite)


    def apply_adjacency_bonus_effect(self, adjacent_similar_items_count):
        """Applique le bonus si l'objet le supporte (ex: stockage)."""
        if self.type == "storage" and self.adjacency_bonus_per_unit > 0:
            self.current_adjacency_bonus_value = adjacent_similar_items_count * self.adjacency_bonus_per_unit
            # Le game_state.update_resource_production_consumption() recalculera la capacité totale.
            print(f"Storage {self.id} at {self.grid_pos} got bonus: {self.current_adjacency_bonus_value} from {adjacent_similar_items_count} neighbors.")

    def set_active_state(self, is_powered):
        """Active ou désactive le bâtiment (ex: si manque d'énergie globale)."""
        self.is_internally_active = is_powered
        # TODO: Changer l'apparence du sprite si désactivé (ex: plus sombre, icône "pas d'énergie")


# --- Tourelles ---
class Turret(GameObject):
    _id_counter = 0
    def __init__(self, turret_type, grid_pos_tuple): # (row, col)
        super().__init__()
        Turret._id_counter += 1
        self.id = Turret._id_counter
        self.type = turret_type
        self.grid_pos = grid_pos_tuple
        self.stats = TURRET_STATS.get(self.type, {})

        # Propriétés
        self.power_consumption = abs(self.stats.get(cfg.STAT_POWER, 0))
        self.range = self.stats.get(cfg.STAT_RANGE, 0) # Pour Gatling
        self.min_range = self.stats.get(cfg.STAT_MIN_RANGE, 0) # Pour Mortier
        self.max_range = self.stats.get(cfg.STAT_MAX_RANGE, 0) # Pour Mortier
        self.fire_rate_per_sec = self.stats.get(cfg.STAT_FIRE_RATE, 1)
        self.cooldown_time_seconds = 1.0 / self.fire_rate_per_sec if self.fire_rate_per_sec > 0 else float('inf')
        self.current_cooldown = 0.0
        self.projectile_type = self.stats.get(cfg.STAT_PROJ_TYPE, None)
        self.projectile_initial_speed = self.stats.get(cfg.STAT_PROJ_SPEED, 0) # Pour mortier

        # Sprites (base et canon)
        base_sprite_name = self.stats.get("base_sprite", "placeholder.png")
        gun_sprite_name = self.stats.get("gun_sprite", "placeholder.png")
        
        self.original_base_sprite = util.load_sprite(cfg.TURRET_SPRITE_PATH + base_sprite_name)
        self.original_gun_sprite = util.load_sprite(cfg.TURRET_SPRITE_PATH + gun_sprite_name)

        self.base_sprite = util.scale_sprite_to_tile(self.original_base_sprite)
        # Le canon peut avoir une taille différente du tile, scaler proportionnellement à la base ou à une taille fixe.
        # Pour l'instant, on scale à la taille du tile aussi, mais cela peut nécessiter ajustement.
        self.gun_sprite_scaled_original = util.scale_sprite_to_tile(self.original_gun_sprite) 
        self.gun_sprite_rotated = self.gun_sprite_scaled_original

        if not self.base_sprite: self.base_sprite = pygame.Surface((cfg.TILE_SIZE,cfg.TILE_SIZE)); self.base_sprite.fill(cfg.COLOR_BLUE)
        if not self.gun_sprite_rotated: self.gun_sprite_rotated = pygame.Surface((cfg.TILE_SIZE,cfg.TILE_SIZE)); self.gun_sprite_rotated.fill(cfg.COLOR_GREEN)

        pixel_pos = util.convert_grid_to_pixels(self.grid_pos, (cfg.GRID_OFFSET_X, cfg.GRID_OFFSET_Y)) # Voir note sur GRID_OFFSET_Y dans Building
        self.rect = self.base_sprite.get_rect(topleft=pixel_pos)
        self.gun_pivot_offset = (self.gun_sprite_scaled_original.get_width() // 2, self.gun_sprite_scaled_original.get_height() // 2) # Point de pivot du canon

        self.target_enemy = None
        self.current_angle_deg = 0 # Angle du canon en degrés (0 = droite)
        self.is_internally_active = True # Si alimentée

    def set_active_state(self, is_powered):
        self.is_internally_active = is_powered
        # TODO: Changer apparence si non alimentée

    def find_target(self, enemies_list):
        self.target_enemy = None
        closest_dist_sq = float('inf')

        turret_center_x, turret_center_y = self.rect.centerx, self.rect.centery

        for enemy in enemies_list:
            if not enemy.active: continue

            dist_sq = (enemy.rect.centerx - turret_center_x)**2 + (enemy.rect.centery - turret_center_y)**2
            
            target_in_range = False
            if self.type == "mortar_turret":
                if self.min_range**2 <= dist_sq <= self.max_range**2:
                    target_in_range = True
            else: # Gatling
                if dist_sq <= self.range**2:
                    target_in_range = True
            
            if target_in_range and dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                self.target_enemy = enemy
    
    def update(self, delta_time, enemies_list, is_powered_globally, game_state_ref):
        self.set_active_state(is_powered_globally) # La tourelle est-elle alimentée ?
        if not self.active or not self.is_internally_active:
            self.target_enemy = None # Perd la cible si pas alimentée
            return

        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time

        if not self.target_enemy or not self.target_enemy.active:
            self.find_target(enemies_list)

        if self.target_enemy:
            # Rotation
            dx = self.target_enemy.rect.centerx - self.rect.centerx
            dy = self.target_enemy.rect.centery - self.rect.centery
            
            if self.type == "mortar_turret":
                # Pour le mortier, l'angle de tir (inclinaison) est calculé au moment du tir.
                # L'orientation horizontale suit la cible.
                self.current_angle_deg = math.degrees(math.atan2(-dy, dx)) 
                # La rotation visuelle du canon se fera avec l'angle d'inclinaison aussi
            else: # Gatling
                self.current_angle_deg = math.degrees(math.atan2(-dy, dx))
            
            self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
            
            # Tir
            if self.current_cooldown <= 0:
                self.shoot(game_state_ref) # Passe game_state pour ajouter projectile
                self.current_cooldown = self.cooldown_time_seconds
        else: # Pas de cible, le canon peut revenir à une position par défaut
            # self.current_angle_deg = 0
            # self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, self.current_angle_deg)
            pass


    def shoot(self, game_state_ref):
        if not self.target_enemy or not self.projectile_type: return

        # TODO: Vérifier si assez de fer pour munitions si implémenté
        # if game_state_ref.iron_stock < AMMO_COST[self.type]: return
        # game_state_ref.iron_stock -= AMMO_COST[self.type]

        # Point de sortie du projectile (centre de la tourelle ou bout du canon)
        # Pour simplifier: centre de la tourelle.
        proj_origin_x = self.rect.centerx + math.cos(math.radians(self.current_angle_deg)) * (cfg.TILE_SIZE // 3) # Un peu devant
        proj_origin_y = self.rect.centery - math.sin(math.radians(self.current_angle_deg)) * (cfg.TILE_SIZE // 3) # Un peu devant
        proj_origin = (proj_origin_x, proj_origin_y)


        if self.type == "mortar_turret":
            fire_solution = calculate_mortar_fire_solution(
                self.rect.center,
                self.target_enemy.rect.center, # Cible la position actuelle de l'ennemi
                self.projectile_initial_speed,
                cfg.GRAVITY 
            )
            if fire_solution:
                launch_angle_rad_vertical, _ = fire_solution # Angle par rapport à l'horizontale

                # Composantes de vitesse initiale
                # L'angle horizontal est self.current_angle_deg
                angle_horizontal_rad = math.radians(self.current_angle_deg)

                # Vitesse dans le plan horizontal (XY du jeu)
                v_horizontal_component = self.projectile_initial_speed * math.cos(launch_angle_rad_vertical)
                
                vx = v_horizontal_component * math.cos(angle_horizontal_rad)
                vy_physics = self.projectile_initial_speed * math.sin(launch_angle_rad_vertical) # Positive = vers le haut en physique

                # Convertir vy_physics en vy pour Pygame (négatif = vers le haut)
                vy_pygame = -vy_physics 
                                
                new_proj = Projectile(self.projectile_type, proj_origin, 0, initial_vx=vx, initial_vy=vy_pygame)
                game_state_ref.projectiles.append(new_proj)

                # Visuel du canon du mortier: rotation horizontale + inclinaison
                # L'inclinaison est launch_angle_rad_vertical. On le convertit en degrés.
                # Le sprite du canon est peut-être déjà orienté horizontalement.
                # Cette partie visuelle peut être complexe.
                # angle_inclinaison_deg = math.degrees(launch_angle_rad_vertical)
                # combined_rotation = self.current_angle_deg - angle_inclinaison_deg # Ou autre combinaison
                # self.gun_sprite_rotated = pygame.transform.rotate(self.gun_sprite_scaled_original, combined_rotation)

        else: # Gatling et autres tirs directs
            new_proj = Projectile(self.projectile_type, proj_origin, self.current_angle_deg)
            game_state_ref.projectiles.append(new_proj)

    def draw(self, surface):
        # Dessiner la base
        if self.active and self.base_sprite:
            surface.blit(self.base_sprite, self.rect.topleft)
        
        # Dessiner le canon rotaté
        if self.active and self.gun_sprite_rotated:
            # Calculer la position du canon pour qu'il pivote correctement
            # (son centre doit correspondre au centre de la base, ou un point de pivot défini)
            gun_rect = self.gun_sprite_rotated.get_rect(center=self.rect.center) # Simplifié: pivote au centre
            surface.blit(self.gun_sprite_rotated, gun_rect.topleft)
        
        # DEBUG: Afficher la portée
        # if self.active and self.target_enemy:
        #     if self.type == "mortar_turret":
        #         pygame.draw.circle(surface, (0,100,0,100), self.rect.center, int(self.min_range), 1)
        #         pygame.draw.circle(surface, (100,0,0,100), self.rect.center, int(self.max_range), 1)
        #     else:
        #         pygame.draw.circle(surface, (100,100,100,100), self.rect.center, int(self.range), 1)


# --- Projectiles ---
class Projectile(GameObject):
    _id_counter = 0
    def __init__(self, projectile_type, origin_xy_pixels, angle_deg, initial_vx=None, initial_vy=None):
        super().__init__()
        Projectile._id_counter += 1
        self.id = Projectile._id_counter
        self.type = projectile_type
        self.stats = PROJECTILE_STATS.get(self.type, {})

        self.damage = self.stats.get(cfg.STAT_DAMAGE, 0)
        self.speed = self.stats.get(cfg.STAT_SPEED, 0) # Pour tirs directs
        self.aoe_radius = self.stats.get(cfg.STAT_AOE_RADIUS, 0)

        sprite_name = self.stats.get(cfg.STAT_SPRITE, "placeholder.png")
        self.original_sprite = util.load_sprite(cfg.PROJECTILE_SPRITE_PATH + sprite_name)
        
        # Les projectiles n'ont pas forcément la taille d'un tile
        # On pourrait les scaler à une taille fixe ou relative à leur type.
        # Pour l'instant, on utilise leur taille originale (si petite) ou on scale légèrement.
        proj_w = cfg.scale_value(self.original_sprite.get_width() * 0.5) # Exemple: 0.5x la taille de base
        proj_h = cfg.scale_value(self.original_sprite.get_height() * 0.5)
        self.sprite_scaled_original = util.scale_sprite_to_size(self.original_sprite, proj_w, proj_h)
        
        self.is_mortar_shell = (self.type == "mortar_shell")

        if self.is_mortar_shell:
            self.vx = initial_vx if initial_vx is not None else 0
            self.vy_physics = -initial_vy if initial_vy is not None else 0 # vy_physics: positif = haut
            self.sprite = self.sprite_scaled_original # Le mortier peut tourner en vol
        else: # Tir direct
            self.angle_rad = math.radians(angle_deg)
            self.vx = self.speed * math.cos(self.angle_rad)
            self.vy_physics = self.speed * math.sin(self.angle_rad) # vy_physics: positif = haut (pour atan2)
            # Rotation du sprite pour tir direct
            self.sprite = pygame.transform.rotate(self.sprite_scaled_original, angle_deg)

        self.rect = self.sprite.get_rect(center=origin_xy_pixels)
        self.lifetime_seconds = 5.0 # Disparaît après X secondes si ne touche rien

    def update(self, delta_time, game_state_ref=None): # game_state_ref non utilisé ici
        if not self.active: return

        self.lifetime_seconds -= delta_time
        if self.lifetime_seconds <= 0:
            self.active = False
            return

        if self.is_mortar_shell:
            self.rect.x += self.vx * delta_time
            self.rect.y += -self.vy_physics * delta_time # Convertir vy_physics en Pygame dy
            self.vy_physics -= cfg.GRAVITY * delta_time # Gravité affecte la composante physique y
            
            # Rotation du sprite du mortier en vol
            current_angle_rad_physics = math.atan2(self.vy_physics, self.vx)
            self.sprite = pygame.transform.rotate(self.sprite_scaled_original, math.degrees(current_angle_rad_physics))
        else: # Tir direct
            self.rect.x += self.vx * delta_time
            self.rect.y += -self.vy_physics * delta_time # Convertir vy_physics en Pygame dy

        # Vérifier si hors écran
        screen_rect = pygame.Rect(0,0, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        if not screen_rect.colliderect(self.rect.inflate(200,200)): # Inflate pour marge
            self.active = False

    def on_hit(self, game_state_ref): # game_state_ref pour déclencher AoE
        self.active = False
        if self.is_mortar_shell and self.aoe_radius > 0:
            # Déclencher les dégâts AoE via game_state
            game_state_ref.trigger_aoe_damage(self.rect.center, self.aoe_radius, self.damage)
            # TODO: Créer une animation d'explosion (ParticleEffect)


# --- Ennemis ---
class Enemy(GameObject):
    _id_counter = 0
    def __init__(self, initial_pos_xy_ref, enemy_type_id, variant_data=None): # variant_data pour futures variations
        super().__init__()
        Enemy._id_counter += 1
        self.id = Enemy._id_counter
        self.type_id = enemy_type_id
        self.stats = ENEMY_STATS.get(self.type_id, ENEMY_STATS[1]) # Fallback au type 1

        # Propriétés de base
        self.max_hp = self.stats.get(cfg.STAT_HP, 10)
        self.current_hp = self.max_hp
        self.speed = cfg.scale_value(self.stats.get(cfg.STAT_SPEED, 30)) # Déjà scalé
        self.city_damage = self.stats.get(cfg.STAT_CITY_DAMAGE, 1)
        self.score_value = self.stats.get(cfg.STAT_SCORE_VALUE, 0)
        self.money_value = self.stats.get(cfg.STAT_MONEY_VALUE, 0)

        # Sprite et Taille
        sprite_name = self.stats.get(cfg.STAT_SPRITE, "placeholder.png")
        self.original_sprite = util.load_sprite(cfg.ENEMY_SPRITE_PATH + sprite_name)

        min_s = self.stats.get(cfg.STAT_SIZE_MIN, 1.0)
        max_s = self.stats.get(cfg.STAT_SIZE_MAX, 1.0)
        random_scale_factor = random.uniform(min_s, max_s)

        # La taille de base du sprite doit être cohérente (ex: faite pour TILE_SIZE)
        # On scale par rapport à la taille originale du sprite, puis on applique le scale général du jeu.
        scaled_w = int(self.original_sprite.get_width() * random_scale_factor * cfg.GENERAL_SCALE)
        scaled_h = int(self.original_sprite.get_height() * random_scale_factor * cfg.GENERAL_SCALE)
        self.sprite = util.scale_sprite_to_size(self.original_sprite, scaled_w, scaled_h)

        if not self.sprite: self.sprite = pygame.Surface((cfg.TILE_SIZE,cfg.TILE_SIZE)); self.sprite.fill(cfg.COLOR_RED)
        
        # La position initiale est en coordonnées de référence, la scaler.
        self.rect = self.sprite.get_rect(center=cfg.scale_value(initial_pos_xy_ref))

        # Hitbox (plus petite que le rect du sprite pour des collisions plus justes)
        hitbox_scale_w, hitbox_scale_h = self.stats.get(cfg.STAT_HITBOX_SCALE, (0.8,0.8))
        hitbox_width = int(self.rect.width * hitbox_scale_w)
        hitbox_height = int(self.rect.height * hitbox_scale_h)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.hitbox.center = self.rect.center

        # TODO: Trajectoire (pour l'instant, mouvement linéaire vers la gauche)
        # self.path_points = [...]
        # self.current_path_target_index = 0

    def update(self, delta_time, game_state_ref=None): # game_state_ref non utilisé ici pour l'instant
        if not self.active: return

        # Mouvement simple vers la gauche
        self.rect.x -= self.speed * delta_time
        self.hitbox.center = self.rect.center # Mettre à jour la hitbox avec le rect

        # Si l'ennemi sort complètement de l'écran à gauche (déjà géré par game_functions si atteint la base)
        if self.rect.right < 0: # Largement hors écran
            self.active = False


    def take_damage(self, amount):
        if not self.active: return
        self.current_hp -= amount
        # TODO: Effet visuel de dégât (flash rouge?)
        if self.current_hp <= 0:
            self.current_hp = 0
            self.active = False # Marquer pour suppression
            # TODO: Créer une animation de mort/explosion (ParticleEffect)
            print(f"Enemy {self.id} (type {self.type_id}) died.")
            # Le score/argent est géré dans game_functions lors de la détection de la mort

    def get_city_damage(self): return self.city_damage
    def get_score_value(self): return self.score_value
    def get_money_value(self): return self.money_value

    def draw(self, surface):
        super().draw(surface) # Dessine le sprite principal
        # Optionnel: Dessiner une barre de vie au-dessus de l'ennemi
        if self.active and self.current_hp < self.max_hp:
            bar_w = cfg.scale_value(30)
            bar_h = cfg.scale_value(5)
            hp_ratio = self.current_hp / self.max_hp
            
            bg_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - bar_h - cfg.scale_value(3), bar_w, bar_h)
            hp_fill_w = int(bar_w * hp_ratio)
            hp_rect = pygame.Rect(bg_rect.left, bg_rect.top, hp_fill_w, bar_h)
            
            pygame.draw.rect(surface, cfg.COLOR_HP_EMPTY, bg_rect)
            pygame.draw.rect(surface, cfg.COLOR_HP_FULL, hp_rect)


# --- Calcul de Trajectoire pour Mortier ---
def calculate_mortar_fire_solution(turret_pos_pixels, target_pos_pixels, projectile_initial_speed_pixels, gravity_pixels_s2):
    dx_pixels = target_pos_pixels[0] - turret_pos_pixels[0]
    # dy_pixels: Négatif si la cible est plus haute que la tourelle dans Pygame
    # Pour la physique, on veut dy positif si la cible est plus haute.
    dy_physics = -(target_pos_pixels[1] - turret_pos_pixels[1]) 
    
    v0 = projectile_initial_speed_pixels
    g = abs(gravity_pixels_s2) # Assurer que g est positif

    # Si la cible est directement au-dessus ou en dessous (dx très petit)
    if abs(dx_pixels) < 1.0: # Seuil pour considérer un tir vertical
        # Tir vertical vers le haut: theta = pi/2
        # Tir vertical vers le bas: theta = -pi/2 (non géré par cette formule simplifiée)
        if dy_physics > 0 : # Cible au-dessus
            # Vérifier si la cible est atteignable verticalement: v0^2 >= 2*g*dy
            if v0**2 >= 2 * g * dy_physics:
                time_to_target = (v0 + (v0**2 - 2*g*dy_physics)**0.5) / g # Temps pour atteindre y avec vitesse initiale v0
                                                                         # ou (v0 - (...)^0.5)/g pour le passage en descendant
                return math.pi / 2, time_to_target # 90 degrés
            else: return None # Inatteignable verticalement
        else: # Cible en dessous, tir vertical. Non géré de manière simple ici.
             return None


    # Terme sous la racine carrée dans la formule de l'angle de la trajectoire
    # discriminant = v0^4 - g * (g * dx^2 + 2 * dy * v0^2)
    discriminant = v0**4 - g * (g * dx_pixels**2 + 2 * dy_physics * v0**2)

    if discriminant < 0:
        return None  # Cible hors de portée (pas de solution réelle pour l'angle)

    # On choisit la solution "high arc" (angle de tir plus élevé)
    # tan(theta) = (v0^2 + sqrt(discriminant)) / (g * dx)
    # (Il y a aussi une solution "low arc" avec v0^2 - sqrt(discriminant))
    
    # Attention si dx_pixels est négatif (cible à gauche)
    # La formule standard suppose dx > 0. On ajuste l'angle après.
    
    # Calcul de tan_theta. Si dx_pixels est 0, cela cause une division par zéro. Géré au-dessus.
    tan_theta_high = (v0**2 + math.sqrt(discriminant)) / (g * dx_pixels)
    # tan_theta_low = (v0**2 - math.sqrt(discriminant)) / (g * dx_pixels)

    angle_rad_high = math.atan(tan_theta_high)
    # angle_rad_low = math.atan(tan_theta_low)

    # L'angle retourné est par rapport à l'horizontale, positif vers le haut.
    # La direction (gauche/droite) est gérée par le signe de vx dans la tourelle.
    # On prend l'angle principal (high arc).
    chosen_angle_rad = angle_rad_high

    # Temps de vol: t = dx / (v0 * cos(theta))
    if math.cos(chosen_angle_rad) == 0: # Tir vertical, cas déjà géré
        return None 
        
    time_of_flight = dx_pixels / (v0 * math.cos(chosen_angle_rad))

    if time_of_flight < 0 : # Si la cible est derrière et que l'angle donne un temps négatif, solution invalide
        return None

    return chosen_angle_rad, time_of_flight


# --- Effets de Particules (Exemple: Explosion) ---
class ParticleEffect(GameObject):
    def __init__(self, position_xy, animation_frames_list, frame_duration):
        super().__init__()
        self.frames = [util.scale_sprite_to_tile(f) for f in animation_frames_list] # Ou autre scaling
        self.frame_duration = frame_duration
        self.current_frame_index = 0
        self.time_on_current_frame = 0
        self.rect = self.frames[0].get_rect(center=position_xy) if self.frames else pygame.Rect(0,0,0,0)
        self.sprite = self.frames[0] if self.frames else None

    def update(self, delta_time, game_state_ref=None):
        if not self.active or not self.frames: return

        self.time_on_current_frame += delta_time
        if self.time_on_current_frame >= self.frame_duration:
            self.time_on_current_frame = 0
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                self.active = False # Fin de l'animation
            else:
                self.sprite = self.frames[self.current_frame_index]
                # Le rect doit être recentré si les frames ont des tailles différentes
                self.rect = self.sprite.get_rect(center=self.rect.center)

# TODO: Créer des listes d'images pour les animations d'explosion et les passer à ParticleEffect
# explosion_frames = [util.load_sprite(cfg.EFFECT_PATH + f"expl_0{i}.png") for i in range(5)]
