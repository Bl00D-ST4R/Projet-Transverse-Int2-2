```python
# game_functions.py
import pygame
import random
import game_config as cfg
import utility_functions as util
import objects # Importera les classes Building, Turret, Enemy, Projectile
import ui_functions # Pour afficher des messages, interagir avec le menu de construction
import wave_definitions # Pour charger les vagues prédéfinies

class GameState:
    """Classe pour encapsuler l'état global du jeu pour un accès facile."""
    def __init__(self):
        self.screen = None # Sera défini dans main.py
        self.clock = None  # Sera défini dans main.py
        self.running_game = True
        self.game_over_flag = False
        self.game_paused = False

        # Temps et Vagues
        self.total_time_elapsed_seconds = 0.0
        self.time_to_next_wave_seconds = 0.0
        self.current_wave_number = 0
        self.wave_in_progress = False
        self.enemies_in_current_wave_to_spawn = [] # Liste de (delay_after_last_spawn, enemy_type_id, enemy_variant)
        self.time_since_last_spawn_in_wave = 0.0

        # Ressources
        self.money = cfg.INITIAL_MONEY
        self.iron_stock = cfg.INITIAL_IRON
        self.iron_production_per_minute = 0
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY
        self.electricity_produced = 0
        self.electricity_consumed = 0

        # Ville
        self.city_hp = cfg.INITIAL_CITY_HP
        self.max_city_hp = cfg.INITIAL_CITY_HP

        # Grille et Construction
        self.grid_width_tiles = cfg.INITIAL_GRID_WIDTH_TILES
        self.grid_height_tiles = cfg.INITIAL_GRID_HEIGHT_TILES
        self.current_expansion_up_tiles = 0
        self.current_expansion_sideways_steps = 0
        
        # La grille stocke les objets Building ou Turret, ou None si vide
        self.game_grid = [[None for _ in range(self.grid_width_tiles)] for _ in range(self.grid_height_tiles)]
        self.buildable_area_rect_pixels = pygame.Rect(0,0,0,0) # Sera mis à jour
        self.update_buildable_area_rect() # Appel initial

        self.selected_item_to_place_type = None # ex: "miner", "gatling_turret"
        self.placement_preview_sprite = None # Sprite pour le fantôme de placement
        self.is_placement_valid_preview = False

        # Listes d'objets actifs
        self.buildings = [] # Contient les instances de Building
        self.turrets = []   # Contient les instances de Turret
        self.enemies = []   # Contient les instances d'Enemy
        self.projectiles = [] # Contient les instances de Projectile
        self.particle_effects = [] # Pour explosions, etc.

        # UI
        self.ui_icons = {} # Sera rempli avec les sprites des icônes UI
        self.last_error_message = ""
        self.error_message_timer = 0.0

        # Score
        self.score = 0
        
        # Initialisation des données de vagues
        self.all_wave_definitions = wave_definitions.load_waves()
        self.max_waves = len(self.all_wave_definitions)

    def init_new_game(self, screen, clock):
        """Réinitialise l'état pour une nouvelle partie."""
        self.__init__() # Appelle le constructeur pour tout remettre à zéro
        self.screen = screen
        self.clock = clock
        self.load_ui_icons()
        self.set_time_for_first_wave()
        self.update_resource_production_consumption() # Calcul initial


    def load_ui_icons(self):
        # SPRITE: Charger les icônes pour l'UI ici
        self.ui_icons['money'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_money.png")
        self.ui_icons['iron'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_iron.png")
        self.ui_icons['energy'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_energy.png")
        self.ui_icons['heart_full'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_full.png")
        self.ui_icons['heart_empty'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_empty.png")
        # ... ajouter d'autres icônes nécessaires (ex: pour le menu de construction)


    def update_buildable_area_rect(self):
        """Met à jour le pygame.Rect de la zone constructible basé sur la taille de la grille."""
        width_pixels = self.grid_width_tiles * cfg.TILE_SIZE
        height_pixels = self.grid_height_tiles * cfg.TILE_SIZE
        
        # Recalculer GRID_OFFSET_Y pour s'assurer qu'il est au-dessus du menu du bas
        # et prend en compte la hauteur actuelle de la grille (qui peut changer avec l'expansion vers le haut)
        current_grid_pixel_height = self.grid_height_tiles * cfg.TILE_SIZE
        dynamic_grid_offset_y = cfg.SCREEN_HEIGHT - current_grid_pixel_height - cfg.UI_BUILD_MENU_HEIGHT - cfg.scale_value(10)

        self.buildable_area_rect_pixels = pygame.Rect(
            cfg.GRID_OFFSET_X,
            dynamic_grid_offset_y,
            width_pixels,
            height_pixels
        )


    def set_time_for_first_wave(self):
        # MODIFIABLE: Temps avant la première vague
        self.time_to_next_wave_seconds = wave_definitions.INITIAL_PREPARATION_TIME_SECONDS
        self.current_wave_number = 0 # Avant la première vague


    def toggle_pause(self):
        self.game_paused = not self.game_paused
        print(f"Game Paused: {self.game_paused}")


    def show_error_message(self, message, duration=2.0):
        self.last_error_message = message
        self.error_message_timer = duration


    def update_timers_and_waves(self, delta_time):
        if self.game_over_flag or self.game_paused:
            return

        self.total_time_elapsed_seconds += delta_time

        if self.error_message_timer > 0:
            self.error_message_timer -= delta_time
            if self.error_message_timer <= 0:
                self.last_error_message = ""
        
        if not self.wave_in_progress:
            self.time_to_next_wave_seconds -= delta_time
            if self.time_to_next_wave_seconds <= 0:
                self.start_next_wave()
        else: # Wave in progress, try to spawn enemies
            self.time_since_last_spawn_in_wave += delta_time
            if self.enemies_in_current_wave_to_spawn:
                delay_needed, enemy_type_id, enemy_variant = self.enemies_in_current_wave_to_spawn[0]
                if self.time_since_last_spawn_in_wave >= delay_needed:
                    self.spawn_enemy(enemy_type_id, enemy_variant)
                    self.enemies_in_current_wave_to_spawn.pop(0)
                    self.time_since_last_spawn_in_wave = 0 # Reset timer for next spawn in this wave
            elif not self.enemies: # No enemies left to spawn and no enemies on screen
                self.wave_in_progress = False
                if self.current_wave_number >= self.max_waves:
                    # TODO: Logique de victoire ou mode infini
                    print("TOUTES LES VAGUES TERMINÉES!")
                    self.show_error_message("VICTOIRE!", 10) # Message temporaire
                    self.game_over_flag = True # Ou un autre flag pour la victoire
                else:
                    self.time_to_next_wave_seconds = wave_definitions.TIME_BETWEEN_WAVES_SECONDS


    def start_next_wave(self):
        self.current_wave_number += 1
        if self.current_wave_number > self.max_waves:
            print("Plus de vagues définies.")
            self.wave_in_progress = False
            # Potentiellement lancer un mode infini ou déclarer une victoire
            return

        print(f"Starting Wave {self.current_wave_number}")
        self.wave_in_progress = True
        # Assurez-vous que les données de vague incluent le variant
        self.enemies_in_current_wave_to_spawn = list(self.all_wave_definitions.get(self.current_wave_number, []))
        self.time_since_last_spawn_in_wave = 0.0
        if not self.enemies_in_current_wave_to_spawn: # Vague vide ?
            self.wave_in_progress = False
            self.time_to_next_wave_seconds = wave_definitions.TIME_BETWEEN_WAVES_SECONDS


    def spawn_enemy(self, enemy_type_id, variant_data=None):
        # TODO: Déterminer la position de spawn (généralement hors écran à droite)
        # La hauteur de spawn pourrait être aléatoire ou basée sur des "chemins"
        spawn_y_ref = random.randint(cfg.scale_value(50), cfg.SCREEN_HEIGHT - cfg.scale_value(200)) # Position Y de référence
        spawn_x_ref = cfg.SCREEN_WIDTH + cfg.scale_value(50) # Hors écran à droite
        
        new_enemy = objects.Enemy((spawn_x_ref, spawn_y_ref), enemy_type_id, variant_data)
        self.enemies.append(new_enemy)
        #print(f"Spawned enemy: {enemy_type_id} (Variant: {variant_data}) at ({spawn_x_ref}, {spawn_y_ref})") # Debug print


    def handle_player_input(self, event, mouse_pos_pixels):
        if self.game_over_flag: return

        # Gestion du menu de construction via UI_Functions
        # (sera appelé depuis la boucle principale du gamemode)
        # Ici, on gère les actions après qu'un item soit sélectionné ou une action cliquée

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic gauche
                # 1. Vérifier si clic sur le menu de construction UI
                clicked_ui_item_id = ui_functions.check_build_menu_click(self, mouse_pos_pixels)

                if clicked_ui_item_id:
                    if clicked_ui_item_id.startswith("expand_"):
                        action = clicked_ui_item_id.split("_")[1] # "up" ou "side"
                        self.try_expand_build_area(action)
                        self.selected_item_to_place_type = None # Désélectionner après action
                    else: # C'est un bâtiment/tourelle à placer
                        self.selected_item_to_place_type = clicked_ui_item_id
                        item_stats = objects.get_item_stats(self.selected_item_to_place_type)
                        # CORRIGÉ: Utiliser la bonne clé pour le sprite par défaut
                        if item_stats and cfg.STAT_SPRITE_DEFAULT_NAME in item_stats:
                            sprite_name = item_stats[cfg.STAT_SPRITE_DEFAULT_NAME]
                            
                            # Déterminer le chemin du préfixe en fonction du type d'item
                            if objects.is_building_type(self.selected_item_to_place_type):
                                path_prefix = cfg.BUILDING_SPRITE_PATH
                            elif objects.is_turret_type(self.selected_item_to_place_type):
                                path_prefix = cfg.TURRET_SPRITE_PATH
                            else: # Fallback ou autre type d'item non géré pour preview
                                path_prefix = cfg.SPRITE_PATH 

                            # Gérer les sprites contextuels pour la prévisualisation (plus complexe, pour l'instant sprite de base)
                            # Si l'item a des variants, on pourrait vouloir montrer un variant spécifique ou le "single"
                            if cfg.STAT_SPRITE_VARIANTS_DICT in item_stats and "single" in item_stats[cfg.STAT_SPRITE_VARIANTS_DICT]:
                                sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_VARIANTS_DICT]["single"]
                            else:
                                sprite_name_for_preview = sprite_name

                            self.placement_preview_sprite = util.scale_sprite_to_tile(util.load_sprite(path_prefix + sprite_name_for_preview))
                            if self.placement_preview_sprite:
                                self.placement_preview_sprite.set_alpha(150) # Rendre semi-transparent
                        else:
                            self.placement_preview_sprite = None
                    return # Action sur UI, ne pas essayer de placer

                # 2. Si un item est sélectionné pour placement, essayer de le placer
                elif self.selected_item_to_place_type:
                    self.try_place_item_on_grid(mouse_pos_pixels)
            
            elif event.button == 3: # Clic droit pour désélectionner/annuler placement
                self.selected_item_to_place_type = None
                self.placement_preview_sprite = None

        # Mise à jour de la prévisualisation du placement si un item est sélectionné
        if self.selected_item_to_place_type and self.placement_preview_sprite:
            is_valid, _ = self.check_placement_validity(self.selected_item_to_place_type, mouse_pos_pixels)
            self.is_placement_valid_preview = is_valid


    def check_placement_validity(self, item_type, mouse_pixel_pos):
        """Vérifie si un item peut être placé à la position donnée. Retourne (bool, (grid_r, grid_c))."""
        grid_r, grid_c = util.convert_pixels_to_grid(mouse_pixel_pos, (cfg.GRID_OFFSET_X, self.buildable_area_rect_pixels.y))

        # Hors grille ?
        if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
            return False, (grid_r, grid_c)

        # Case occupée ? (sauf tourelle sur fondation)
        existing_item = self.game_grid[grid_r][grid_c]
        if existing_item:
            if objects.is_turret_type(item_type) and objects.is_foundation_type(existing_item.type):
                pass # Autorisé (la tourelle remplacera la fondation dans la grille logique pour la simplicité)
            else:
                return False, (grid_r, grid_c) # Case occupée

        # TODO: Implémenter toutes les RÈGLES DE PLACEMENT ici
        # (mineurs sur mineurs/fondation renforcée, bonus stockage, etc.)
        # Exemple pour mineur:
        if item_type == "miner":
            # Fondations renforcées sont la première ligne du bas de la zone 4xH initiale
            # La position Y de la "première ligne du bas" change si on étend vers le haut
            base_bottom_row_index = cfg.INITIAL_GRID_HEIGHT_TILES -1 + self.current_expansion_up_tiles
            
            is_on_reinforced_foundation_spot = (grid_r == base_bottom_row_index and \
                                                 0 <= grid_c < cfg.INITIAL_GRID_WIDTH_TILES)

            is_on_another_miner = False
            if grid_r > 0 and self.game_grid[grid_r - 1][grid_c] and \
               self.game_grid[grid_r - 1][grid_c].type == "miner":
                is_on_another_miner = True
            
            if not (is_on_reinforced_foundation_spot or is_on_another_miner):
                # Afficher un message spécifique pour placement invalide des mineurs
                # self.show_error_message("Mineurs doivent être placés sur fondations renforcées ou d'autres mineurs.")
                return False, (grid_r, grid_c)
            
        # Vérifier ressources (argent, fer)
        item_stats = objects.get_item_stats(item_type)
        if self.money < item_stats.get(cfg.STAT_COST_MONEY, 0):
            # self.show_error_message("Pas assez d'argent.")
            return False, (grid_r, grid_c)
        if self.iron_stock < item_stats.get(cfg.STAT_COST_IRON, 0):
            # self.show_error_message("Pas assez de fer.")
            return False, (grid_r, grid_c)

        # Vérifier électricité
        power_impact = item_stats.get(cfg.STAT_POWER, 0)
        projected_prod = self.electricity_produced + (power_impact if power_impact > 0 else 0)
        projected_conso = self.electricity_consumed - (power_impact if power_impact < 0 else 0) # power est négatif pour conso
        if projected_prod < projected_conso and item_type != "generator": # On peut toujours construire un générateur
             # self.show_error_message("Manque d'électricité.")
             return False, (grid_r, grid_c)


        return True, (grid_r, grid_c)


    def try_place_item_on_grid(self, mouse_pixel_pos):
        item_type = self.selected_item_to_place_type
        if not item_type: return

        is_valid, (grid_r, grid_c) = self.check_placement_validity(item_type, mouse_pixel_pos)

        if is_valid:
            item_stats = objects.get_item_stats(item_type)
            
            # Déduire coûts
            self.money -= item_stats.get(cfg.STAT_COST_MONEY, 0)
            self.iron_stock -= item_stats.get(cfg.STAT_COST_IRON, 0)

            # Créer et ajouter l'objet
            if objects.is_turret_type(item_type):
                new_item = objects.Turret(item_type, (grid_r, grid_c))
                self.turrets.append(new_item)
            else: # C'est un bâtiment
                new_item = objects.Building(item_type, (grid_r, grid_c))
                self.buildings.append(new_item)
            
            self.game_grid[grid_r][grid_c] = new_item
            new_item.update_sprite_based_on_context(self.game_grid) # Pour sprites contextuels (mine empilée etc)

            # Vérifier et appliquer les bonus d'adjacence après placement
            self.check_and_apply_adjacency_bonus(new_item, grid_r, grid_c)
            if new_item.type == "storage": # Si on place un stockage, vérifier aussi les voisins
                for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nr, nc = grid_r + dr, grid_c + dc
                    if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and self.game_grid[nr][nc]:
                         # Appliquer le bonus sur le voisin ET vérifier le bonus sur l'objet qui vient d'être placé
                         # car le bonus peut dépendre des voisins existants.
                         # Si le voisin est un stockage, il pourrait bénéficier du nouveau stockage.
                         # Si le nouvel objet est un stockage, il bénéficie des stockages voisins existants.
                         # Donc on appelle la fonction pour le nouvel item (déjà fait) et pour les voisins potentiels.
                         neighbor_item = self.game_grid[nr][nc]
                         if hasattr(neighbor_item, 'apply_adjacency_bonus_effect'):
                              self.check_and_apply_adjacency_bonus(neighbor_item, nr, nc)


            self.update_resource_production_consumption()
            # Optionnel: Désélectionner après placement réussi
            # self.selected_item_to_place_type = None
            # self.placement_preview_sprite = None
            print(f"Placed {item_type} at ({grid_r},{grid_c})")
        else:
            # Le message d'erreur est affiché par check_placement_validity si on veut être plus précis
            # Pour l'instant, on utilise le message générique ici.
            self.show_error_message("Placement invalide!")
            print(f"Invalid placement for {item_type} at ({grid_r},{grid_c})")


    def check_and_apply_adjacency_bonus(self, item, r, c):
        """Vérifie et met à jour l'item (ex: un stockage) pour les bonus d'adjacence."""
        if not item or not hasattr(item, 'apply_adjacency_bonus_effect'):
            return

        # Pour le stockage, le bonus dépend du nombre de stockages voisins directs
        if item.type == "storage":
            adjacent_storage_count = 0
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and \
                   self.game_grid[nr][nc] and self.game_grid[nr][nc].type == "storage":
                    adjacent_storage_count +=1
            item.apply_adjacency_bonus_effect(adjacent_storage_count)
            item.update_sprite_based_on_context(self.game_grid) # Mettre à jour le sprite si le bonus le change


    def try_expand_build_area(self, direction): # "up" ou "side"
        # MODIFIABLE: Coûts d'expansion
        cost_up = 500 * (self.current_expansion_up_tiles + 1)
        cost_side = 1000 * (self.current_expansion_sideways_steps + 1)
        
        can_expand = False
        cost_expansion = 0
        message = ""

        if direction == "up" and self.current_expansion_up_tiles < cfg.MAX_EXPANSION_UP_TILES:
            cost_expansion = cost_up
            can_expand = True
            message = "Expansion vers le haut réussie!"
        elif direction == "side" and self.current_expansion_sideways_steps < cfg.MAX_EXPANSION_SIDEWAYS_STEPS:
            cost_expansion = cost_side
            can_expand = True
            message = "Expansion latérale réussie!"
        
        if not can_expand:
            self.show_error_message("Expansion max atteinte.")
            return

        if self.money >= cost_expansion:
            self.money -= cost_expansion
            
            if direction == "up":
                self.current_expansion_up_tiles += 1
                # Ajoute une nouvelle rangée en bas de la structure game_grid (correspondant visuellement au haut)
                new_row = [None for _ in range(self.grid_width_tiles)]
                self.game_grid.insert(0, new_row) # Insère au début de la liste des rangées
                self.grid_height_tiles += 1

                # Important: Mettre à jour les positions (r, c) de tous les objets existants
                # car leurs indices de rangée ont changé.
                # L'indice de rangée de chaque objet existant augmente de 1.
                for row in self.game_grid:
                     for item in row:
                          if item:
                               item.grid_pos = (item.grid_pos[0] + 1, item.grid_pos[1])


            elif direction == "side":
                self.current_expansion_sideways_steps += 1
                tiles_to_add = cfg.EXPANSION_SIDEWAYS_TILES_PER_STEP
                new_grid_w = self.grid_width_tiles + tiles_to_add
                for r_idx in range(self.grid_height_tiles):
                    self.game_grid[r_idx].extend([None for _ in range(tiles_to_add)]) # Ajoute à la fin de chaque rangée
                self.grid_width_tiles = new_grid_w

            self.update_buildable_area_rect() # Crucial pour redessiner correctement
            self.show_error_message(message)
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$)")


    def update_resource_production_consumption(self):
        self.electricity_produced = 0
        self.electricity_consumed = 0
        self.iron_production_per_minute = 0
        temp_iron_storage_capacity_from_buildings = 0

        # Recalculer le bonus de stockage avant de sommer les capacités
        # Cela gère les cas où l'on vend/place des stockages
        for building in self.buildings:
            if building.type == "storage":
                 self.check_and_apply_adjacency_bonus(building, building.grid_pos[0], building.grid_pos[1])


        for building in self.buildings:
            if not building.is_active: continue # Ne compte pas si inactif (ex: manque d'énergie globale)
            
            # TODO: Gérer l'état "is_active" des bâtiments individuellement
            # si on veut que certains s'éteignent si manque d'énergie.

            stats = objects.BUILDING_STATS.get(building.type, {})
            self.electricity_produced += stats.get(cfg.STAT_POWER_PROD, 0)
            # Power est négatif pour la consommation dans les stats
            if stats.get(cfg.STAT_POWER, 0) < 0:
                 self.electricity_consumed += abs(stats.get(cfg.STAT_POWER, 0))
            
            self.iron_production_per_minute += stats.get(cfg.STAT_IRON_PROD, 0)
            temp_iron_storage_capacity_from_buildings += stats.get(cfg.STAT_IRON_STORAGE, 0)
            # Ajouter le bonus d'adjacence effectif du bâtiment (calculé dans check_and_apply_adjacency)
            if hasattr(building, 'current_adjacency_bonus_value'):
                 temp_iron_storage_capacity_from_buildings += building.current_adjacency_bonus_value


        for turret in self.turrets:
            if not turret.is_active: continue
            stats = objects.TURRET_STATS.get(turret.type, {})
            if stats.get(cfg.STAT_POWER, 0) < 0:
                 self.electricity_consumed += abs(stats.get(cfg.STAT_POWER, 0))
        
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + temp_iron_storage_capacity_from_buildings

        # Mettre à jour l'état actif des bâtiments/tourelles si l'énergie globale est insuffisante
        # (Logique plus avancée: prioriser certains bâtiments, etc.)
        # Pour l'instant, on suppose que tout fonctionne si prod >= conso
        power_ok = (self.electricity_produced >= self.electricity_consumed)
        for building in self.buildings:
             building.is_active = power_ok # Logique simple: tout actif si énergie OK
             # TODO: Logique pour les générateurs qui produisent même si conso > prod
             if building.type == "generator":
                  building.is_active = True # Les générateurs sont toujours actifs


        for turret in self.turrets:
             turret.is_active = power_ok # Logique simple: tout actif si énergie OK


    def update_resources_per_tick(self, delta_time):
        if self.game_paused or self.game_over_flag: return

        # Production de fer
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)


    def update_game_logic(self, delta_time):
        if self.game_over_flag or self.game_paused:
            return

        # 1. Mettre à jour les timers et la logique des vagues
        self.update_timers_and_waves(delta_time)

        # 2. Mettre à jour les ressources (production/consommation sur la durée)
        self.update_resources_per_tick(delta_time)

        # 3. Mettre à jour les tourelles (ciblage, tir)
        # Le statut actif des tourelles est mis à jour dans update_resource_production_consumption
        # qui est appelé quand un bâtiment/tourelle est placé/vendu, ou potentiellement à chaque tick si l'énergie fluctue
        power_available_overall = (self.electricity_produced >= self.electricity_consumed) # Redondant? Déjà dans update_resource_production_consumption
        for turret in self.turrets:
            # La tourelle utilise sa propre flag is_active pour savoir si elle peut tirer
            turret.update(delta_time, self.enemies, power_available_overall, self) # Passe self (game_state) pour créer projectiles

        # 4. Mettre à jour les projectiles (mouvement)
        for proj in self.projectiles:
            proj.update(delta_time)

        # 5. Mettre à jour les ennemis (mouvement, future IA d'attaque)
        for enemy in self.enemies:
            enemy.update(delta_time)
            # Vérifier si l'ennemi a atteint la base
            if enemy.rect.right < cfg.GRID_OFFSET_X: # A dépassé le bord gauche de la zone de construction
                self.city_take_damage(enemy.get_city_damage())
                enemy.active = False # Marquer pour suppression
                self.show_error_message("La ville a subi des dégâts!")


        # 6. Gérer les collisions
        self.handle_collisions()

        # 7. Mettre à jour les effets de particules
        for effect in self.particle_effects:
            effect.update(delta_time)

        # 8. Nettoyer les objets inactifs (morts, disparus)
        self.cleanup_inactive_objects()

        # 9. Vérifier les conditions de fin de partie
        if self.city_hp <= 0 and not self.game_over_flag:
            self.game_over_flag = True
            print("GAME OVER - City HP reached 0")
            # TODO: Afficher l'écran de Game Over via ui_functions


    def city_take_damage(self, amount):
        if self.game_over_flag: return
        self.city_hp -= amount
        if self.city_hp < 0:
            self.city_hp = 0
        print(f"City took {amount} damage. HP: {self.city_hp}")
        # TODO: Effet visuel/sonore

    def handle_collisions(self):
        # Projectiles vs Ennemis
        for proj in self.projectiles[:]: # Itérer sur une copie si on modifie la liste
            if not proj.active: continue
            for enemy in self.enemies[:]:
                if not enemy.active: continue
                
                # Utiliser la hitbox de l'ennemi pour la collision
                if proj.rect.colliderect(enemy.hitbox):
                    enemy.take_damage(proj.damage)
                    proj.on_hit(self) # Le projectile peut déclencher AoE via game_state
                    proj.active = False # Le projectile disparaît après avoir touché (sauf si pénétrant)
                                        # TODO: Gérer les projectiles pénétrants si nécessaire
                    
                    if not enemy.active: # Ennemi tué
                        self.money += enemy.get_money_value()
                        self.score += enemy.get_score_value()
                    break # Le projectile ne peut toucher qu'un ennemi (sauf si AoE géré différemment par on_hit)
    
    def trigger_aoe_damage(self, center_pos, radius, damage):
        """Appelé par un projectile (ex: mortier) pour infliger des dégâts de zone."""
        # SPRITE: Créer une animation d'explosion ici (ajouter à self.particle_effects)
        # exemple: self.particle_effects.append(objects.ExplosionEffect(center_pos))
        print(f"TRIGGER AOE at {center_pos} with radius {radius} and damage {damage}") # Debug print
        
        scaled_radius = cfg.scale_value(radius) # Si radius est en unités de référence
        for enemy in self.enemies:
            if not enemy.active: continue
            # Calculer la distance entre le centre de l'AoE et le centre de la hitbox de l'ennemi
            distance_sq = (enemy.hitbox.centerx - center_pos[0])**2 + (enemy.hitbox.centery - center_pos[1])**2
            if distance_sq < scaled_radius**2:
                # TODO: Réduction des dégâts avec la distance ?
                enemy.take_damage(damage)
                if not enemy.active:
                    self.money += enemy.get_money_value()
                    self.score += enemy.get_score_value()


    def cleanup_inactive_objects(self):
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particle_effects = [eff for eff in self.particle_effects if eff.active]
        # Les bâtiments/tourelles ne sont pas détruits dans ce modèle (sauf si attaque sur base), donc pas de nettoyage pour eux ici.
        # Si la logique de destruction/vente est ajoutée, il faudra les nettoyer aussi.

    # TODO: Ajouter une méthode pour gérer la destruction/vente de bâtiments/tourelles
    # def remove_item_from_grid(self, grid_r, grid_c):
    #    item = self.game_grid[grid_r][grid_c]
    #    if item:
    #         if isinstance(item, objects.Building):
    #              self.buildings.remove(item)
    #         elif isinstance(item, objects.Turret):
    #              self.turrets.remove(item)
    #         self.game_grid[grid_r][grid_c] = None
    #         # Réappliquer les bonus d'adjacence aux voisins si l'objet retiré en donnait/en bénéficiait
    #         self.update_resource_production_consumption() # Pour simple update des totaux
    #         # Pour les bonus d'adjacence spécifiques (comme stockage), vérifier les voisins
    #         for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
    #             nr, nc = grid_r + dr, grid_c + dc
    #             if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and self.game_grid[nr][nc]:
    #                  self.check_and_apply_adjacency_bonus(self.game_grid[nr][nc], nr, nc)


    def draw_game_world(self):
        # 1. Dessiner le fond (si image ou couleur unie)
        self.screen.fill((30, 35, 40)) # Couleur de fond temporaire

        # 2. Dessiner la zone de la grille constructible
        ui_functions.draw_base_grid(self.screen, self)

        # 3. Dessiner les bâtiments
        for building in self.buildings:
            building.draw(self.screen)

        # 4. Dessiner les tourelles (base et canon)
        for turret in self.turrets:
            turret.draw(self.screen)

        # 5. Dessiner les ennemis
        for enemy in self.enemies:
            enemy.draw(self.screen)
            # DEBUG: util.draw_debug_rect(self.screen, enemy.hitbox, cfg.COLOR_GREEN)


        # 6. Dessiner les projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)
            
        # 7. Dessiner les effets de particules (explosions)
        for effect in self.particle_effects:
            effect.draw(self.screen)

        # 8. Dessiner la prévisualisation du placement
        ui_functions.draw_placement_preview(self.screen, self)


    def draw_game_ui_elements(self):
        ui_functions.draw_top_bar_ui(self.screen, self)
        ui_functions.draw_build_menu_ui(self.screen, self)
        if self.last_error_message and self.error_message_timer > 0:
            ui_functions.draw_error_message(self.screen, self.last_error_message)
        
        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen)
        
        if self.game_over_flag:
            ui_functions.draw_game_over_screen(self.screen, self.score)

# Instance globale de l'état du jeu (ou passée en argument)
# Pour un accès plus facile depuis les objets, on peut la rendre accessible.
# Cependant, il est souvent mieux de passer `game_state` explicitement aux fonctions/méthodes qui en ont besoin.
# game_state_instance = GameState() # Sera créé dans main.py
```
