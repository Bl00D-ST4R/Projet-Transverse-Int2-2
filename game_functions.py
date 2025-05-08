# game_functions.py
import pygame
import random
import game_config as cfg
import utility_functions as util 
import objects
import ui_functions
import wave_definitions

class GameState:
    """Classe pour encapsuler l'état global du jeu pour un accès facile."""
    def __init__(self):
        self.screen = None 
        self.clock = None 
        self.running_game = True
        self.game_over_flag = False
        self.game_paused = False

        # Temps et Vagues
        self.total_time_elapsed_seconds = 0.0
        self.time_to_next_wave_seconds = 0.0
        self.current_wave_number = 0
        self.wave_in_progress = False
        self.enemies_in_current_wave_to_spawn = []
        self.time_since_last_spawn_in_wave = 0.0
        self.enemies_in_wave_remaining = 0 

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
        self.grid_width_tiles = cfg.GRID_INITIAL_WIDTH_TILES
        self.grid_height_tiles = cfg.GRID_INITIAL_HEIGHT_TILES
        self.current_expansion_up_tiles = 0
        self.current_expansion_sideways_steps = 0
        self.grid_initial_width_tiles = cfg.GRID_INITIAL_WIDTH_TILES 

        # La grille stocke les objets ou None. Initialiser avec la taille de base.
        self.game_grid = [[None for _ in range(cfg.GRID_INITIAL_WIDTH_TILES)] for _ in range(cfg.GRID_INITIAL_HEIGHT_TILES)]
        self.buildable_area_rect_pixels = pygame.Rect(0,0,0,0)
        self.reinforced_foundation_row_index_visual = 0 # Sera mis à jour par update_buildable_area_rect
        self.update_buildable_area_rect() # Appel initial pour définir le rect et reinforced_row

        self.selected_item_to_place_type = None 
        self.placement_preview_sprite = None 
        self.is_placement_valid_preview = False

        # Listes d'objets actifs
        self.buildings = [] 
        self.turrets = [] 
        self.enemies = [] 
        self.projectiles = [] 
        self.particle_effects = [] 

        # UI
        self.ui_icons = {} 
        self.last_error_message = ""
        self.error_message_timer = 0.0
        self.tutorial_message = ""
        self.tutorial_message_timer = 0.0

        # Score
        self.score = 0

        # Initialisation des données de vagues
        self.all_wave_definitions = wave_definitions.load_waves()
        self.max_waves = len(self.all_wave_definitions)
        self.all_waves_completed = False


    def get_next_expansion_cost(self, direction):
        cost = "Max" 
        if direction == "up":
            if self.current_expansion_up_tiles < cfg.GRID_MAX_EXPANSION_UP_TILES:
                cost = int(cfg.BASE_EXPANSION_COST_UP * (cfg.EXPANSION_COST_INCREASE_FACTOR_UP ** self.current_expansion_up_tiles))
        elif direction == "side":
            if self.current_expansion_sideways_steps < cfg.GRID_MAX_EXPANSION_SIDEWAYS_STEPS:
                cost = int(cfg.BASE_EXPANSION_COST_SIDE * (cfg.EXPANSION_COST_INCREASE_FACTOR_SIDE ** self.current_expansion_sideways_steps))
        return cost

    def init_new_game(self, screen, clock):
        """Réinitialise l'état pour une nouvelle partie."""
        self.__init__() 
        self.screen = screen
        self.clock = clock
        self.load_ui_icons()

        # --- Placer les fondations initiales ---
        # La grille est déjà créée dans __init__ avec la taille initiale
        initial_bottom_row = cfg.GRID_INITIAL_HEIGHT_TILES - 1
        for c in range(cfg.GRID_INITIAL_WIDTH_TILES):
            grid_r, grid_c = initial_bottom_row, c
            # Vérifier les limites (devrait être ok ici mais bonne pratique)
            if 0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles:
                 if self.game_grid[grid_r][grid_c] is None:
                     try:
                         # Créer un objet 'fundations' (type de bâtiment)
                         foundation_obj = objects.Building("fundations", (grid_r, grid_c))
                         # Corriger sa position pixel basée sur le rect de la zone constructible
                         foundation_obj.rect.topleft = util.convert_grid_to_pixels((grid_r, grid_c),
                                                                                    (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y))
                         self.game_grid[grid_r][grid_c] = foundation_obj
                         self.buildings.append(foundation_obj)
                         print(f"Placed initial foundation at ({grid_r},{grid_c})") 
                     except Exception as e:
                         print(f"ERROR placing initial foundation at ({grid_r},{grid_c}): {e}")
                 else:
                     print(f"WARNING: Initial foundation spot ({grid_r},{grid_c}) was already occupied.")


        self.set_time_for_first_wave()
        self.update_resource_production_consumption() # Calcul initial après placement des fondations
        ui_functions.initialize_build_menu_layout(self) 
        ui_functions.initialize_pause_menu_layout() 
        ui_functions.initialize_game_over_layout() 

    def load_ui_icons(self):
        # Utilise util.load_sprite qui gère les erreurs et placeholders
        self.ui_icons['money'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_money.png")
        self.ui_icons['iron'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_iron.png")
        self.ui_icons['energy'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_energy.png")
        self.ui_icons['heart_full'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_full.png")
        self.ui_icons['heart_empty'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_empty.png")

    def update_buildable_area_rect(self):
        width_pixels = self.grid_width_tiles * cfg.TILE_SIZE
        height_pixels = self.grid_height_tiles * cfg.TILE_SIZE
        current_grid_pixel_height = self.grid_height_tiles * cfg.TILE_SIZE
        dynamic_grid_offset_y = cfg.SCREEN_HEIGHT - current_grid_pixel_height - cfg.UI_BUILD_MENU_HEIGHT - cfg.GRID_BOTTOM_PADDING

        self.buildable_area_rect_pixels = pygame.Rect(
            cfg.GRID_OFFSET_X, dynamic_grid_offset_y, width_pixels, height_pixels
        )
        # Calcul de l'index de la rangée visuelle qui correspond à la dernière rangée initiale
        # Si on insère en haut (index 0) de self.game_grid lors de l'expansion "up"
        self.reinforced_foundation_row_index_visual = self.current_expansion_up_tiles + (cfg.GRID_INITIAL_HEIGHT_TILES - 1)
        # Si on ajoutait en bas de self.game_grid, l'index serait cfg.GRID_INITIAL_HEIGHT_TILES - 1

    def set_time_for_first_wave(self):
        self.time_to_next_wave_seconds = cfg.WAVE_INITIAL_PREP_TIME_SEC
        self.current_wave_number = 0 

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        print(f"Game Paused: {self.game_paused}") 

    def show_error_message(self, message, duration=2.5): 
        self.last_error_message = message
        self.error_message_timer = duration

    def show_tutorial_message(self, message, duration=5.0):
        self.tutorial_message = message
        self.tutorial_message_timer = duration

    def update_timers_and_waves(self, delta_time):
        if self.game_over_flag or self.game_paused or self.all_waves_completed:
            if self.all_waves_completed and not self.enemies and not self.wave_in_progress:
                 pass # Logique de victoire gérée ailleurs
            return

        if self.error_message_timer > 0:
            self.error_message_timer -= delta_time
            if self.error_message_timer <= 0: self.last_error_message = ""
        if self.tutorial_message_timer > 0:
            self.tutorial_message_timer -= delta_time
            if self.tutorial_message_timer <=0: self.tutorial_message = ""

        if not self.wave_in_progress:
            self.time_to_next_wave_seconds -= delta_time
            if self.time_to_next_wave_seconds <= 0:
                self.start_next_wave()
        else: 
            self.time_since_last_spawn_in_wave += delta_time
            if self.enemies_in_current_wave_to_spawn:
                delay_needed, enemy_type_id, enemy_variant = self.enemies_in_current_wave_to_spawn[0]
                if self.time_since_last_spawn_in_wave >= delay_needed:
                    self.spawn_enemy(enemy_type_id, enemy_variant)
                    self.enemies_in_current_wave_to_spawn.pop(0)
                    self.time_since_last_spawn_in_wave = 0 
            elif not self.enemies: 
                self.wave_in_progress = False
                self.enemies_in_wave_remaining = 0
                if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                    self.all_waves_completed = True
                    print("TOUTES LES VAGUES TERMINÉES!")
                else:
                    self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC

    def start_next_wave(self):
        self.current_wave_number += 1
        if self.current_wave_number > self.max_waves and self.max_waves > 0:
            self.wave_in_progress = False
            self.all_waves_completed = True
            print("Fin des vagues définies.")
            return

        print(f"Starting Wave {self.current_wave_number}")
        self.wave_in_progress = True
        self.enemies_in_current_wave_to_spawn = list(self.all_wave_definitions.get(self.current_wave_number, []))
        self.enemies_in_wave_remaining = len(self.enemies_in_current_wave_to_spawn) 
        self.time_since_last_spawn_in_wave = 0.0
        if not self.enemies_in_current_wave_to_spawn: 
            self.wave_in_progress = False
            self.enemies_in_wave_remaining = 0
            if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                 self.all_waves_completed = True
            else:
                 self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC

    def spawn_enemy(self, enemy_type_id, variant_data=None):
        min_spawn_y_ref = self.buildable_area_rect_pixels.top - cfg.scale_value(100)
        max_spawn_y_ref = self.buildable_area_rect_pixels.bottom + cfg.scale_value(100) 
        screen_top_margin = cfg.UI_TOP_BAR_HEIGHT + cfg.scale_value(10)
        screen_bottom_margin = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - cfg.scale_value(10)
        spawn_y_ref = random.randint(max(screen_top_margin, int(min_spawn_y_ref)), min(screen_bottom_margin, int(max_spawn_y_ref)))
        spawn_x_ref = cfg.SCREEN_WIDTH + cfg.scale_value(random.randint(30, 100)) 
        new_enemy = objects.Enemy((spawn_x_ref, spawn_y_ref), enemy_type_id, variant_data)
        self.enemies.append(new_enemy)

    def handle_player_input(self, event, mouse_pos_pixels):
        # La gestion des clics Pause/Game Over est faite dans la boucle principale (main.py ou gamemodes.py)
        if self.game_over_flag or self.game_paused: return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic Gauche
                clicked_ui_item_id = ui_functions.check_build_menu_click(self, mouse_pos_pixels)
                if clicked_ui_item_id:
                    if clicked_ui_item_id.startswith("expand_"):
                        action_type = clicked_ui_item_id.split("_")[1]
                        self.try_expand_build_area(action_type)
                        self.selected_item_to_place_type = None
                        self.placement_preview_sprite = None
                    else: # Sélection d'un item constructible
                        self.selected_item_to_place_type = clicked_ui_item_id
                        
                        # Déterminer quel sprite utiliser pour la preview
                        item_stats = objects.get_item_stats(self.selected_item_to_place_type)
                        sprite_name_for_preview = None
                        path_prefix = None

                        if objects.is_building_type(self.selected_item_to_place_type):
                            path_prefix = cfg.BUILDING_SPRITE_PATH
                            # Pour les mineurs, utiliser le sprite 'single' si possible pour la preview
                            if self.selected_item_to_place_type == "miner" and cfg.STAT_SPRITE_VARIANTS_DICT in item_stats:
                                sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_VARIANTS_DICT].get("single")
                            if not sprite_name_for_preview: # Fallback pour autres bâtiments ou si 'single' absent
                                sprite_name_for_preview = item_stats.get(cfg.STAT_SPRITE_DEFAULT_NAME)
                                
                        elif objects.is_turret_type(self.selected_item_to_place_type):
                            path_prefix = cfg.TURRET_SPRITE_PATH
                            # Utiliser la base de la tourelle pour la preview
                            sprite_name_for_preview = item_stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME)

                        # Charger et préparer le sprite de preview
                        if sprite_name_for_preview and path_prefix:
                            loaded_sprite = util.load_sprite(path_prefix + sprite_name_for_preview)
                            self.placement_preview_sprite = util.scale_sprite_to_tile(loaded_sprite)
                            if self.placement_preview_sprite:
                                self.placement_preview_sprite.set_alpha(150)
                            else: self.placement_preview_sprite = None # Échec du chargement/scale
                        else: self.placement_preview_sprite = None # Nom ou préfixe manquant
                    return # Action sur l'UI terminée

                elif self.selected_item_to_place_type: # Si clic en dehors de l'UI et item sélectionné
                    self.try_place_item_on_grid(mouse_pos_pixels)

            elif event.button == 3: # Clic Droit
                self.selected_item_to_place_type = None
                self.placement_preview_sprite = None

        # Mise à jour de la validité de la preview si un item est sélectionné
        if self.selected_item_to_place_type and self.placement_preview_sprite:
            is_valid, _ = self.check_placement_validity(self.selected_item_to_place_type, mouse_pos_pixels)
            self.is_placement_valid_preview = is_valid
        else: # Pas d'item sélectionné, pas de preview valide
             self.is_placement_valid_preview = False


    def check_placement_validity(self, item_type, mouse_pixel_pos):
        # Utiliser l'offset Y dynamique de la zone constructible
        grid_origin_y = self.buildable_area_rect_pixels.y
        grid_r, grid_c = util.convert_pixels_to_grid(mouse_pixel_pos, (cfg.GRID_OFFSET_X, grid_origin_y))

        if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
            self.show_error_message("Hors de la zone constructible.")
            return False, (grid_r, grid_c)

        existing_item = self.game_grid[grid_r][grid_c]
        item_stats = objects.get_item_stats(item_type)
        
        # --- Nouvelles Règles de Placement ---
        placement_requirement_met = False
        required_base_type = "None" # Pour message d'erreur

        if item_type == "frame":
            # Peut être placé sur une case vide seulement
            if existing_item is None:
                placement_requirement_met = True
            else: required_base_type = "Case vide"
        elif item_type in ["generator", "storage", "gatling_turret", "mortar_turret"]:
            # Doit être placé sur un "frame" existant
            if existing_item is not None and existing_item.type == "frame":
                placement_requirement_met = True
            else: required_base_type = "'Structure (frame)'"
        elif item_type == "miner":
            # Doit être placé sur une case vide au-dessus d'une "fundations" ou d'un autre "miner"
            if existing_item is None: # La case cible doit être vide
                # Vérifier la case EN DESSOUS (r+1)
                if grid_r + 1 < self.grid_height_tiles:
                     item_below = self.game_grid[grid_r + 1][grid_c]
                     if item_below and (item_below.type == "fundations" or item_below.type == "miner"):
                         placement_requirement_met = True
                     else: required_base_type = "'Fondation renforcée' ou autre 'Mineur'"
                else: required_base_type = "'Fondation renforcée' ou autre 'Mineur'" # Cas bord inférieur grille
            else: required_base_type = "Case vide" # Ne peut pas placer sur une case déjà occupée
        else:
             print(f"AVERTISSEMENT: Règle de placement inconnue pour {item_type}")
             self.show_error_message(f"Type d'objet inconnu: {item_type}")
             return False, (grid_r, grid_c)

        if not placement_requirement_met:
            self.show_error_message(f"Doit être placé sur : {required_base_type}")
            return False, (grid_r, grid_c)


        # --- Vérifications Communes (Ressources, Énergie) ---
        cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
        cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
        if self.money < cost_money:
             self.show_error_message(f"Pas assez d'argent! ({cost_money}$)")
             return False, (grid_r, grid_c)
        if self.iron_stock < cost_iron:
             self.show_error_message(f"Pas assez de fer! ({cost_iron} Fe)")
             return False, (grid_r, grid_c)

        # Vérification énergie
        power_prod_impact = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        power_conso_impact = item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        # Ne vérifier l'énergie que si l'item consomme et ne produit pas (ou neutre)
        if power_conso_impact > 0 and power_prod_impact == 0 and item_type != "storage": # Storage est neutre
            if self.electricity_produced < (self.electricity_consumed + power_conso_impact):
                 self.show_error_message("Pas assez d'énergie disponible!")
                 return False, (grid_r, grid_c)

        return True, (grid_r, grid_c)

    def try_place_item_on_grid(self, mouse_pixel_pos):
        item_type = self.selected_item_to_place_type
        if not item_type: return

        is_valid, (grid_r, grid_c) = self.check_placement_validity(item_type, mouse_pixel_pos)

        if is_valid:
            item_stats = objects.get_item_stats(item_type)
            self.money -= item_stats.get(cfg.STAT_COST_MONEY, 0)
            self.iron_stock -= item_stats.get(cfg.STAT_COST_IRON, 0)

            # Gérer le remplacement du 'frame' si on place un item dessus
            existing_item = self.game_grid[grid_r][grid_c]
            if existing_item and existing_item.type == "frame" and item_type != "frame":
                 if existing_item in self.buildings:
                     existing_item.active = False # Marquer comme inactif
                     self.buildings.remove(existing_item)
                 # La case sera écrasée par le nouvel item dans self.game_grid ci-dessous

            # Créer le nouvel item
            new_item = None
            if objects.is_turret_type(item_type):
                new_item = objects.Turret(item_type, (grid_r, grid_c))
                self.turrets.append(new_item)
            elif objects.is_building_type(item_type): # frame, generator, storage, miner, fundations(si plaçable)
                new_item = objects.Building(item_type, (grid_r, grid_c))
                self.buildings.append(new_item)
            
            if new_item:
                 # Mettre à jour la position pixel de l'objet
                 new_item.rect.topleft = util.convert_grid_to_pixels((grid_r, grid_c),
                                                                     (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y))
                 self.game_grid[grid_r][grid_c] = new_item
                 
                 # Mettre à jour le sprite du nouvel item et des voisins (contextuel)
                 new_item.update_sprite_based_on_context(self.game_grid)
                 # Mettre à jour les voisins directs (surtout utile pour les mineurs)
                 for dr_n, dc_n in [(0,1), (0,-1), (1,0), (-1,0)]:
                     nr, nc = grid_r + dr_n, grid_c + dc_n
                     if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                          neighbor = self.game_grid[nr][nc]
                          if neighbor and hasattr(neighbor, 'update_sprite_based_on_context'):
                              neighbor.update_sprite_based_on_context(self.game_grid)

                 # Gérer bonus d'adjacence (ex: pour storage)
                 self.check_and_apply_adjacency_bonus(new_item, grid_r, grid_c)
                 if new_item.type == "storage":
                     for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                         nr, nc = grid_r + dr, grid_c + dc
                         if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                              neighbor_item = self.game_grid[nr][nc]
                              if neighbor_item and neighbor_item.type == "storage":
                                  self.check_and_apply_adjacency_bonus(neighbor_item, nr, nc)

                 self.update_resource_production_consumption() # Recalculer prod/conso
                 print(f"Placed {item_type} at ({grid_r},{grid_c})")
            else:
                 print(f"ERREUR: Échec de création de l'objet de type {item_type}")
                 # Rembourser?
                 self.money += item_stats.get(cfg.STAT_COST_MONEY, 0)
                 self.iron_stock += item_stats.get(cfg.STAT_COST_IRON, 0)

        else:
            # L'erreur est déjà affichée par check_placement_validity
            print(f"Invalid placement attempt for {item_type} at ({grid_r},{grid_c})")


    def check_and_apply_adjacency_bonus(self, item, r, c):
        # ... (Inchangé) ...
        if not item or not hasattr(item, 'apply_adjacency_bonus_effect'):
            return
        if item.type == "storage":
            adjacent_similar_items_count = 0
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and \
                   self.game_grid[nr][nc] and self.game_grid[nr][nc].type == "storage":
                    adjacent_similar_items_count +=1
            item.apply_adjacency_bonus_effect(adjacent_similar_items_count)
            item.update_sprite_based_on_context(self.game_grid)


    def try_expand_build_area(self, direction):
        # ... (La logique d'expansion qui insère au début et décale les grid_pos est correcte) ...
        cost_expansion = self.get_next_expansion_cost(direction)

        if cost_expansion == "Max":
            self.show_error_message("Expansion max atteinte.")
            return
        if not isinstance(cost_expansion, (int, float)) or cost_expansion <= 0:
            self.show_error_message("Coût d'expansion invalide.")
            return

        if self.money >= cost_expansion:
            self.money -= cost_expansion
            if direction == "up":
                self.current_expansion_up_tiles += 1
                new_row = [None for _ in range(self.grid_width_tiles)]
                self.game_grid.insert(0, new_row)
                self.grid_height_tiles += 1
                # Décaler les coordonnées grid_pos de tous les objets existants
                for bld in self.buildings: bld.grid_pos = (bld.grid_pos[0] + 1, bld.grid_pos[1])
                for tur in self.turrets: tur.grid_pos = (tur.grid_pos[0] + 1, tur.grid_pos[1])
            elif direction == "side":
                self.current_expansion_sideways_steps += 1
                tiles_to_add = cfg.GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP
                for r_idx in range(self.grid_height_tiles):
                    self.game_grid[r_idx].extend([None for _ in range(tiles_to_add)])
                self.grid_width_tiles += tiles_to_add

            self.update_buildable_area_rect()
            # Mettre à jour la position pixel de tous les objets après expansion
            for r in range(self.grid_height_tiles):
                 for c in range(self.grid_width_tiles):
                      item = self.game_grid[r][c]
                      if item:
                           item.rect.topleft = util.convert_grid_to_pixels((r, c),
                                                                             (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y))

            self.update_resource_production_consumption()
            self.show_error_message("Zone de base étendue!")
            print(f"Expanded grid to {self.grid_width_tiles}x{self.grid_height_tiles}")
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$)")


    def update_resource_production_consumption(self):
        # ... (La logique de calcul et de mise à jour de l'état actif est correcte) ...
        total_electricity_produced = 0
        total_electricity_consumed = 0
        total_iron_production_pm = 0
        total_iron_storage_increase = 0

        all_constructs = self.buildings + self.turrets

        for item in all_constructs:
            if not item.active: continue
            item_stats = objects.get_item_stats(item.type)
            total_electricity_produced += item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
            total_electricity_consumed += item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
            if isinstance(item, objects.Building):
                total_iron_production_pm += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
                total_iron_storage_increase += item_stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
                if hasattr(item, 'current_adjacency_bonus_value'):
                     total_iron_storage_increase += item.current_adjacency_bonus_value

        is_globally_powered = total_electricity_produced >= total_electricity_consumed

        effective_electricity_produced = 0
        effective_electricity_consumed = 0
        effective_iron_production_pm = 0

        for item in all_constructs:
            if not item.active: continue
            item_stats = objects.get_item_stats(item.type)
            is_generator = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0) > 0
            is_neutral = item.type in ["frame", "fundations", "storage"]

            item_is_powered = is_globally_powered or is_generator or is_neutral
            item.set_active_state(item_is_powered)

            if item_is_powered:
                effective_electricity_produced += item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
                effective_electricity_consumed += item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
                if isinstance(item, objects.Building):
                     effective_iron_production_pm += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)

        self.electricity_produced = effective_electricity_produced
        self.electricity_consumed = effective_electricity_consumed
        self.iron_production_per_minute = effective_iron_production_pm
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + total_iron_storage_increase


    def update_resources_per_tick(self, delta_time):
        # ... (Inchangé) ...
        if self.game_paused or self.game_over_flag: return
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)


    def update_game_logic(self, delta_time):
        # ... (La structure générale est correcte, s'assure que les appels sont bons) ...
        if self.game_over_flag or self.game_paused:
            return

        self.update_timers_and_waves(delta_time)
        # Les ressources sont mises à jour à chaque tick AVANT les actions qui pourraient en dépendre
        self.update_resources_per_tick(delta_time)
        # L'état de l'énergie et l'état actif des bâtiments sont mis à jour
        self.update_resource_production_consumption()
        # L'état actif est maintenant connu pour chaque objet
        is_globally_powered = self.electricity_produced >= self.electricity_consumed # On peut recalculer ici ou utiliser la valeur mise à jour

        # Update Tourelles (elles utilisent leur propre self.is_internally_active maintenant)
        for turret in self.turrets:
             turret.update(delta_time, self.enemies, is_globally_powered, self) # Passe l'état global power

        # Update Bâtiments (si nécessaire)
        for building in self.buildings:
             # building.update(delta_time, self) # Décommenter si update nécessaire
             pass

        # Update Projectiles
        for proj in self.projectiles:
            proj.update(delta_time, self)

        # Update Ennemis
        for enemy in self.enemies:
            enemy.update(delta_time, self)
            # Vérifier si l'ennemi atteint la base (bord gauche de l'écran ou zone spécifique)
            # Utiliser le bord gauche de la zone constructible comme limite
            base_line_x = self.buildable_area_rect_pixels.left if hasattr(self.buildable_area_rect_pixels, 'left') else 0
            if enemy.rect.right < base_line_x:
                self.city_take_damage(enemy.get_city_damage())
                enemy.active = False
                if self.city_hp > 0:
                    print(f"Ville touchée! HP restants: {self.city_hp}")


        # Update Effets
        for effect in self.particle_effects:
             effect.update(delta_time, self)

        # Collisions (après que tout a bougé)
        self.handle_collisions()

        # Nettoyage
        self.cleanup_inactive_objects()

        # Vérifier Game Over
        if self.city_hp <= 0 and not self.game_over_flag:
            self.game_over_flag = True
            print("GAME OVER - City HP reached 0")
            # self.show_error_message("GAME OVER", 10) # Optionnel


    def city_take_damage(self, amount):
        # ... (Inchangé) ...
        if self.game_over_flag: return
        if amount <= 0: return
        self.city_hp -= amount
        if self.city_hp < 0: self.city_hp = 0


    def handle_collisions(self):
        # ... (La logique de collision semble correcte) ...
        projectiles_to_remove_after_loop = set()
        enemies_hit_this_frame_by_projectile = {}

        for proj in self.projectiles:
             if not proj.active: continue
             if proj.rect.right < 0 or proj.rect.left > cfg.SCREEN_WIDTH or \
                proj.rect.bottom < 0 or proj.rect.top > cfg.SCREEN_HEIGHT + cfg.scale_value(100):
                 projectiles_to_remove_after_loop.add(proj)
                 continue

             for enemy in self.enemies:
                 if not enemy.active: continue

                 is_mortar = hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell
                 if not is_mortar and proj.id in enemies_hit_this_frame_by_projectile and \
                    enemy.id in enemies_hit_this_frame_by_projectile[proj.id]:
                    continue

                 if proj.rect.colliderect(enemy.hitbox):
                     enemy.take_damage(proj.damage)
                     # on_hit peut déclencher AoE via trigger_aoe_damage
                     # et devrait marquer le projectile comme inactif si nécessaire
                     proj.on_hit(self)

                     if not is_mortar: # Projectiles directs consommés
                         projectiles_to_remove_after_loop.add(proj)
                         if proj.id not in enemies_hit_this_frame_by_projectile:
                             enemies_hit_this_frame_by_projectile[proj.id] = set()
                         enemies_hit_this_frame_by_projectile[proj.id].add(enemy.id)
                         break # Le projectile direct a touché, passe au suivant

                     if not enemy.active:
                         self.money += enemy.get_money_value()
                         self.score += enemy.get_score_value()
                         self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)

        for proj_to_remove in projectiles_to_remove_after_loop:
             proj_to_remove.active = False # Marquer pour nettoyage


    def trigger_aoe_damage(self, center_pos, radius, damage):
        # ... (La logique AoE est correcte) ...
        # Exemple: Ajouter un effet visuel
        if hasattr(objects, 'ParticleEffect') and hasattr(cfg, 'EXPLOSION_FRAMES'): # Vérifier si les assets/config existent
            # explosion_frames = [util.load_sprite(cfg.EFFECT_SPRITE_PATH + f) for f in cfg.EXPLOSION_FRAMES]
            # self.particle_effects.append(objects.ParticleEffect(center_pos, explosion_frames, 0.05)) # 50ms par frame
             pass # Implémenter le chargement des frames d'explosion

        radius_sq = radius ** 2
        for enemy in self.enemies:
            if not enemy.active: continue
            distance_sq = (enemy.hitbox.centerx - center_pos[0])**2 + (enemy.hitbox.centery - center_pos[1])**2
            if distance_sq < radius_sq:
                enemy.take_damage(damage)
                if not enemy.active:
                    self.money += enemy.get_money_value()
                    self.score += enemy.get_score_value()
                    self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)


    def cleanup_inactive_objects(self):
        # ... (Inchangé) ...
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particle_effects = [eff for eff in self.particle_effects if eff.active]


    def draw_game_world(self):
        # ... (La logique de dessin est correcte) ...
        background_color = getattr(cfg, 'COLOR_BACKGROUND', cfg.COLOR_BLACK) # Utiliser COLOR_BACKGROUND si défini
        self.screen.fill(background_color)

        ui_functions.draw_base_grid(self.screen, self)

        # Créer une liste de tous les objets à dessiner pour tri par Y
        all_drawable_objects = self.buildings + self.turrets + self.enemies
        all_drawable_objects.sort(key=lambda obj: obj.rect.bottom)

        for obj in all_drawable_objects:
             obj.draw(self.screen)
             # Debug Hitbox Ennemi
             # if isinstance(obj, objects.Enemy) and hasattr(cfg, 'DEBUG_MODE') and cfg.DEBUG_MODE:
             #     util.draw_debug_rect(self.screen, obj.hitbox, cfg.COLOR_GREEN, 1)

        # Dessiner projectiles et effets par-dessus
        for proj in self.projectiles:
            proj.draw(self.screen)
        for effect in self.particle_effects:
            effect.draw(self.screen)

        ui_functions.draw_placement_preview(self.screen, self)


    def draw_game_ui_elements(self):
        # ... (Inchangé) ...
        ui_functions.draw_top_bar_ui(self.screen, self)
        ui_functions.draw_build_menu_ui(self.screen, self)

        if self.last_error_message and self.error_message_timer > 0:
            ui_functions.draw_error_message(self.screen, self.last_error_message, self)
        if self.tutorial_message and self.tutorial_message_timer > 0:
            ui_functions.draw_tutorial_message(self.screen, self.tutorial_message, self)

        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen)
        if self.game_over_flag:
            ui_functions.draw_game_over_screen(self.screen, self.score)
