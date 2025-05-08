# game_functions.py
import pygame
import random
import game_config as cfg
import utility_functions as util # CORRIGÉ: Nom du module
import objects
import ui_functions
import wave_definitions

class GameState:
    """Classe pour encapsuler l'état global du jeu pour un accès facile."""
    def __init__(self):
        self.screen = None # Sera défini dans main.py
        self.clock = None # Sera défini dans main.py
        self.running_game = True
        self.game_over_flag = False
        self.game_paused = False

        # Temps et Vagues
        self.total_time_elapsed_seconds = 0.0
        self.time_to_next_wave_seconds = 0.0
        self.current_wave_number = 0
        self.wave_in_progress = False
        #enemies_in_current_wave_to_spawn: Liste de (delay_after_last_spawn, enemy_type_id, enemy_variant)
        self.enemies_in_current_wave_to_spawn = []
        self.time_since_last_spawn_in_wave = 0.0
        self.enemies_in_wave_remaining = 0 # Pour affichage UI

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
        self.grid_initial_width_tiles = cfg.GRID_INITIAL_WIDTH_TILES # Stocker pour la logique de fondation renforcée

        self.game_grid = [[None for _ in range(self.grid_width_tiles)] for _ in range(self.grid_height_tiles)]
        self.buildable_area_rect_pixels = pygame.Rect(0,0,0,0)
        self.reinforced_foundation_row_index_visual = 0 # Sera mis à jour
        self.update_buildable_area_rect() 

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
        cost = "Max" # Par défaut
        if direction == "up":
            if self.current_expansion_up_tiles < cfg.GRID_MAX_EXPANSION_UP_TILES:
                # Le coût augmente avec chaque expansion réussie
                cost = int(cfg.BASE_EXPANSION_COST_UP * (cfg.EXPANSION_COST_INCREASE_FACTOR_UP ** self.current_expansion_up_tiles))
            # else: cost reste "Max"
        elif direction == "side":
            if self.current_expansion_sideways_steps < cfg.GRID_MAX_EXPANSION_SIDEWAYS_STEPS:
                cost = int(cfg.BASE_EXPANSION_COST_SIDE * (cfg.EXPANSION_COST_INCREASE_FACTOR_SIDE ** self.current_expansion_sideways_steps))
            # else: cost reste "Max"
        return cost

    def init_new_game(self, screen, clock):
        self.__init__() 
        self.screen = screen
        self.clock = clock
        self.load_ui_icons()
        self.set_time_for_first_wave()
        self.update_resource_production_consumption()
        ui_functions.initialize_build_menu_layout(self) # Initialiser le layout du menu de construction
        ui_functions.initialize_pause_menu_layout() # Initialiser le layout du menu pause
        ui_functions.initialize_game_over_layout() # Initialiser le layout du game over


    def load_ui_icons(self):
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
            cfg.GRID_OFFSET_X,
            dynamic_grid_offset_y,
            width_pixels,
            height_pixels
        )
        # La rangée "renforcée" est la dernière rangée de la zone de construction initiale.
        # Sa position visuelle est toujours (cfg.INITIAL_GRID_HEIGHT_TILES - 1) si 0,0 est en haut à gauche
        # et que la grille s'étend vers le bas dans la structure de données.
        # Si la grille s'étend "visuellement" vers le haut, mais que les nouvelles rangées sont ajoutées en
        # début de liste self.game_grid, alors l'index visuel change.
        # Si les nouvelles rangées sont ajoutées à la fin de game_grid et que dynamic_grid_offset_y diminue:
        # La rangée renforcée est la (cfg.INITIAL_GRID_HEIGHT_TILES -1)ème rangée *à partir du bas de la zone initiale*.
        # Donc son index dans la grille actuelle est `self.grid_height_tiles - 1 - self.current_expansion_up_tiles`.
        # Ou plus simplement, si la zone initiale a H lignes (0 à H-1), la ligne renforcée est H-1.
        # Si on ajoute E lignes en haut (visuellement), la grille totale a H+E lignes.
        # L'ancienne ligne H-1 est maintenant à l'index E + (H-1) depuis le nouveau haut.
        self.reinforced_foundation_row_index_visual = self.current_expansion_up_tiles + (cfg.GRID_INITIAL_HEIGHT_TILES - 1)


    def set_time_for_first_wave(self):
        self.time_to_next_wave_seconds = cfg.WAVE_INITIAL_PREP_TIME_SEC
        self.current_wave_number = 0 

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        print(f"Game Paused: {self.game_paused}") 

    def show_error_message(self, message, duration=2.5): # Durée par défaut un peu plus longue
        self.last_error_message = message
        self.error_message_timer = duration

    def show_tutorial_message(self, message, duration=5.0):
        self.tutorial_message = message
        self.tutorial_message_timer = duration

    def update_timers_and_waves(self, delta_time):
        if self.game_over_flag or self.game_paused or self.all_waves_completed:
            if self.all_waves_completed and not self.enemies and not self.wave_in_progress:
                 # Gérer condition de victoire si toutes les vagues sont finies et plus d'ennemis
                 # self.game_over_flag = True # Ou un flag de victoire
                 # self.show_error_message("VICTOIRE! Toutes vagues terminées!", 10)
                 pass # La logique de victoire peut être gérée ailleurs
            return

        # Timer pour les messages
        if self.error_message_timer > 0:
            self.error_message_timer -= delta_time
            if self.error_message_timer <= 0:
                self.last_error_message = ""
        if self.tutorial_message_timer > 0:
            self.tutorial_message_timer -= delta_time
            if self.tutorial_message_timer <=0:
                self.tutorial_message = ""


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
                    # La condition de victoire sera gérée plus haut ou dans la boucle principale
                else:
                    self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC


    def start_next_wave(self):
        self.current_wave_number += 1
        if self.current_wave_number > self.max_waves and self.max_waves > 0:
            print("Plus de vagues définies.")
            self.wave_in_progress = False
            self.all_waves_completed = True
            return

        print(f"Starting Wave {self.current_wave_number}")
        self.wave_in_progress = True
        self.enemies_in_current_wave_to_spawn = list(self.all_wave_definitions.get(self.current_wave_number, []))
        self.enemies_in_wave_remaining = len(self.enemies_in_current_wave_to_spawn) # Total à spawner pour cette vague
        self.time_since_last_spawn_in_wave = 0.0
        if not self.enemies_in_current_wave_to_spawn: 
            self.wave_in_progress = False
            self.enemies_in_wave_remaining = 0
            if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                 self.all_waves_completed = True
            else:
                 self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC


    def spawn_enemy(self, enemy_type_id, variant_data=None):
        # Spawn Y: entre le haut de l'écran et un peu au-dessus du menu de construction
        min_spawn_y_ref = self.buildable_area_rect_pixels.top - cfg.scale_value(100) # Peut être négatif, ok
        max_spawn_y_ref = self.buildable_area_rect_pixels.bottom + cfg.scale_value(100) # Un peu sous la zone
        
        # S'assurer que le spawn est dans les limites de l'écran verticalement (approximatif)
        screen_top_margin = cfg.UI_TOP_BAR_HEIGHT + cfg.scale_value(10)
        screen_bottom_margin = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - cfg.scale_value(10)

        spawn_y_ref = random.randint(
            max(screen_top_margin, int(min_spawn_y_ref)),
            min(screen_bottom_margin, int(max_spawn_y_ref))
        )
        spawn_x_ref = cfg.SCREEN_WIDTH + cfg.scale_value(random.randint(30, 100)) # Spawn un peu variable à droite

        new_enemy = objects.Enemy((spawn_x_ref, spawn_y_ref), enemy_type_id, variant_data)
        self.enemies.append(new_enemy)


    def handle_player_input(self, event, mouse_pos_pixels):
        if self.game_over_flag: 
            ui_functions.check_game_over_menu_click(event, mouse_pos_pixels) # Laisser gérer les clics sur le menu GO
            return
        if self.game_paused: 
             action = ui_functions.check_pause_menu_click(event, mouse_pos_pixels)
             if action == "resume": self.toggle_pause()
             elif action == "restart": self.init_new_game(self.screen, self.clock) # Redémarre la partie
             elif action == "main_menu": self.running_game = False # Signal pour retourner au menu principal
             elif action == "quit_game": pygame.event.post(pygame.event.Event(pygame.QUIT)) # Quitte le jeu
             return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                clicked_ui_item_id = ui_functions.check_build_menu_click(self, mouse_pos_pixels)

                if clicked_ui_item_id:
                    if clicked_ui_item_id.startswith("expand_"):
                        action_type = clicked_ui_item_id.split("_")[1] 
                        self.try_expand_build_area(action_type)
                        self.selected_item_to_place_type = None 
                        self.placement_preview_sprite = None 
                    else: 
                        self.selected_item_to_place_type = clicked_ui_item_id
                        item_stats = objects.get_item_stats(self.selected_item_to_place_type)
                        if item_stats:
                            sprite_name_for_preview = None
                            path_prefix = None

                            if objects.is_building_type(self.selected_item_to_place_type):
                                path_prefix = cfg.BUILDING_SPRITE_PATH
                                if cfg.STAT_SPRITE_VARIANTS_DICT in item_stats and "single" in item_stats[cfg.STAT_SPRITE_VARIANTS_DICT]:
                                     sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_VARIANTS_DICT]["single"]
                                elif cfg.STAT_SPRITE_DEFAULT_NAME in item_stats:
                                     sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_DEFAULT_NAME]
                            elif objects.is_turret_type(self.selected_item_to_place_type):
                                path_prefix = cfg.TURRET_SPRITE_PATH
                                # Pour les tourelles, la preview est souvent la base.
                                sprite_name_for_preview = item_stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME)

                            if sprite_name_for_preview and path_prefix:
                                loaded_sprite = util.load_sprite(path_prefix + sprite_name_for_preview)
                                self.placement_preview_sprite = util.scale_sprite_to_tile(loaded_sprite)
                                if self.placement_preview_sprite:
                                    self.placement_preview_sprite.set_alpha(150)
                                else: self.placement_preview_sprite = None
                            else: self.placement_preview_sprite = None
                        else: self.placement_preview_sprite = None
                    return 

                elif self.selected_item_to_place_type:
                    self.try_place_item_on_grid(mouse_pos_pixels)

            elif event.button == 3: 
                self.selected_item_to_place_type = None
                self.placement_preview_sprite = None

        if self.selected_item_to_place_type and self.placement_preview_sprite:
            is_valid, _ = self.check_placement_validity(self.selected_item_to_place_type, mouse_pos_pixels)
            self.is_placement_valid_preview = is_valid


    def check_placement_validity(self, item_type, mouse_pixel_pos):
        grid_r, grid_c = util.convert_pixels_to_grid(mouse_pixel_pos, 
                                                    (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y))

        if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
            return False, (grid_r, grid_c)

        existing_item = self.game_grid[grid_r][grid_c]
        if existing_item:
            if objects.is_turret_type(item_type) and objects.is_foundation_type(existing_item.type):
                pass 
            elif item_type == "miner" and existing_item.type == "miner":
                 pass 
            else:
                self.show_error_message("Case déjà occupée.")
                return False, (grid_r, grid_c)

        if item_type == "miner":
            # La rangée renforcée est `self.reinforced_foundation_row_index_visual`
            is_on_reinforced_spot = (grid_r == self.reinforced_foundation_row_index_visual and \
                                     0 <= grid_c < self.grid_initial_width_tiles) # Utiliser la largeur initiale stockée

            is_on_another_miner = False
            if grid_r + 1 < self.grid_height_tiles and self.game_grid[grid_r + 1][grid_c] and \
               self.game_grid[grid_r + 1][grid_c].type == "miner":
               is_on_another_miner = True

            if not (is_on_reinforced_spot or is_on_another_miner):
                 if not existing_item or existing_item.type != "miner":
                     self.show_error_message("Mineur doit être sur fondation renforcée ou autre mineur.")
                     return False, (grid_r, grid_c)

        item_stats = objects.get_item_stats(item_type)
        cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
        cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)

        if self.money < cost_money:
             self.show_error_message(f"Pas assez d'argent! ({cost_money}$)")
             return False, (grid_r, grid_c)
        if self.iron_stock < cost_iron:
             self.show_error_message(f"Pas assez de fer! ({cost_iron} Fe)")
             return False, (grid_r, grid_c)

        power_prod_impact = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        power_conso_impact = item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        projected_prod = self.electricity_produced + power_prod_impact
        projected_conso = self.electricity_consumed + power_conso_impact
        is_power_neutral_or_producer = item_type == "generator" or item_type == "storage" or item_type == "foundation"

        if projected_prod < projected_conso and not is_power_neutral_or_producer:
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

            existing_item = self.game_grid[grid_r][grid_c]
            if existing_item and objects.is_foundation_type(existing_item.type) and objects.is_turret_type(item_type):
                 if existing_item in self.buildings:
                     existing_item.active = False # Marquer pour suppression si on veut une logique de suppression propre
                     self.buildings.remove(existing_item)

            new_item_obj = None
            if objects.is_turret_type(item_type):
                new_item_obj = objects.Turret(item_type, (grid_r, grid_c))
                # S'assurer que la position de la tourelle est correcte par rapport à la grille
                new_item_obj.rect.topleft = util.convert_grid_to_pixels((grid_r, grid_c), 
                                                                        (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y))
                self.turrets.append(new_item_obj)
            else: 
                new_item_obj = objects.Building(item_type, (grid_r, grid_c))
                new_item_obj.rect.topleft = util.convert_grid_to_pixels((grid_r, grid_c),
                                                                        (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y))
                self.buildings.append(new_item_obj)

            self.game_grid[grid_r][grid_c] = new_item_obj
            # Mettre à jour le sprite du nouvel item et des voisins potentiels
            new_item_obj.update_sprite_based_on_context(self.game_grid) # La méthode dans Building doit gérer ses propres coords

            # Mettre à jour les sprites des voisins affectés (surtout pour les mineurs)
            for dr_n, dc_n in [(0,1), (0,-1), (1,0), (-1,0)]:
                 nr, nc = grid_r + dr_n, grid_c + dc_n
                 if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                      neighbor = self.game_grid[nr][nc]
                      if neighbor and hasattr(neighbor, 'update_sprite_based_on_context'):
                          neighbor.update_sprite_based_on_context(self.game_grid)


            self.check_and_apply_adjacency_bonus(new_item_obj, grid_r, grid_c)
            if item_type == "storage":
                 for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                     nr, nc = grid_r + dr, grid_c + dc
                     if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                          neighbor_item = self.game_grid[nr][nc]
                          if neighbor_item and neighbor_item.type == "storage":
                              self.check_and_apply_adjacency_bonus(neighbor_item, nr, nc)

            self.update_resource_production_consumption()
            print(f"Placed {item_type} at ({grid_r},{grid_c})")
        else:
            print(f"Invalid placement attempt for {item_type} at ({grid_r},{grid_c})")


    def check_and_apply_adjacency_bonus(self, item, r, c):
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
        cost_expansion = self.get_next_expansion_cost(direction)

        if cost_expansion == "Max":
            self.show_error_message("Expansion max atteinte.")
            return
        
        if not isinstance(cost_expansion, (int, float)) or cost_expansion <= 0:
            self.show_error_message("Coût d'expansion invalide.") # Sécurité
            return

        if self.money >= cost_expansion:
            self.money -= cost_expansion
            
            if direction == "up":
                self.current_expansion_up_tiles += 1
                # Ajoute une nouvelle rangée AU DEBUT de la grille logique
                new_row = [None for _ in range(self.grid_width_tiles)]
                self.game_grid.insert(0, new_row)
                self.grid_height_tiles += 1
                # Décaler les coordonnées grid_pos de tous les bâtiments/tourelles existants
                for bld in self.buildings: bld.grid_pos = (bld.grid_pos[0] + 1, bld.grid_pos[1])
                for tur in self.turrets: tur.grid_pos = (tur.grid_pos[0] + 1, tur.grid_pos[1])

            elif direction == "side":
                self.current_expansion_sideways_steps += 1
                tiles_to_add = cfg.GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP
                for r_idx in range(self.grid_height_tiles):
                    self.game_grid[r_idx].extend([None for _ in range(tiles_to_add)])
                self.grid_width_tiles += tiles_to_add

            self.update_buildable_area_rect() 
            self.update_resource_production_consumption() # Mettre à jour si l'expansion affecte des bonus
            self.show_error_message("Zone de base étendue!")
            print(f"Expanded grid to {self.grid_width_tiles}x{self.grid_height_tiles}")
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$)")


    def update_resource_production_consumption(self):
        self.electricity_produced = 0
        self.electricity_consumed = 0
        self.iron_production_per_minute = 0
        temp_iron_storage_capacity_from_buildings = 0

        all_constructs = self.buildings + self.turrets
        is_globally_powered = True # Optimiste

        # D'abord, calculer production et consommation totales
        for item in all_constructs:
            if not item.active: continue # Ne pas compter les items "détruits" (si implémenté)
            
            item_stats = {}
            if isinstance(item, objects.Building): item_stats = objects.BUILDING_STATS.get(item.type, {})
            elif isinstance(item, objects.Turret): item_stats = objects.TURRET_STATS.get(item.type, {})

            self.electricity_produced += item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
            self.electricity_consumed += item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
            
            if isinstance(item, objects.Building):
                self.iron_production_per_minute += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
                temp_iron_storage_capacity_from_buildings += item_stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
                if hasattr(item, 'current_adjacency_bonus_value'):
                     temp_iron_storage_capacity_from_buildings += item.current_adjacency_bonus_value
        
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + temp_iron_storage_capacity_from_buildings
        is_globally_powered = self.electricity_produced >= self.electricity_consumed

        # Ensuite, mettre à jour l'état de chaque item en fonction de l'énergie globale
        # Et recalculer les productions/consommations effectives si des items sont désactivés
        effective_electricity_produced = 0
        effective_electricity_consumed = 0
        effective_iron_production_pm = 0
        # La capacité de stockage n'est pas affectée par le manque d'énergie

        for item in all_constructs:
            if not item.active: continue 
            
            item_stats = {}
            if isinstance(item, objects.Building): item_stats = objects.BUILDING_STATS.get(item.type, {})
            elif isinstance(item, objects.Turret): item_stats = objects.TURRET_STATS.get(item.type, {})

            # Les générateurs produisent toujours, les fondations et stockages sont toujours "actifs" (pas de conso)
            is_generator = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0) > 0
            is_neutral = item.type == "foundation" or item.type == "storage" # Pas de conso/prod d'énergie pour eux
            
            item_is_powered = is_globally_powered or is_generator or is_neutral
            item.set_active_state(item_is_powered) # Méthode dans Building/Turret

            if item_is_powered:
                effective_electricity_produced += item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
                effective_electricity_consumed += item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
                if isinstance(item, objects.Building):
                     effective_iron_production_pm += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
        
        # Mettre à jour les totaux effectifs
        self.electricity_produced = effective_electricity_produced
        self.electricity_consumed = effective_electricity_consumed
        self.iron_production_per_minute = effective_iron_production_pm



    def update_resources_per_tick(self, delta_time):
        if self.game_paused or self.game_over_flag: return
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)


    def update_game_logic(self, delta_time):
        if self.game_over_flag or self.game_paused:
            return

        self.update_timers_and_waves(delta_time)
        self.update_resources_per_tick(delta_time)
        
        # Mettre à jour production/consommation AVANT que les tourelles/bâtiments ne s'updatent
        # pour qu'ils aient l'état d'énergie correct
        self.update_resource_production_consumption() 
        is_globally_powered = self.electricity_produced >= self.electricity_consumed

        for turret in self.turrets:
             turret.update(delta_time, self.enemies, is_globally_powered, self)

        # Les bâtiments peuvent avoir une logique d'update (ex: animations, auto-réparation?)
        for building in self.buildings:
             # building.update(delta_time, self) # Si les bâtiments ont une logique d'update
             # Pour l'instant, set_active_state est géré dans update_resource_production_consumption
             pass


        for proj in self.projectiles:
            proj.update(delta_time, self) 

        for enemy in self.enemies:
            enemy.update(delta_time, self) # Passer game_state si l'ennemi interagit (ex: attaquer des bâtiments)
            if hasattr(self.buildable_area_rect_pixels, 'left') and enemy.rect.right < self.buildable_area_rect_pixels.left:
                self.city_take_damage(enemy.get_city_damage())
                enemy.active = False 
                # self.show_error_message("La ville a subi des dégâts!") # Peut être trop fréquent
                if self.city_hp > 0: # N'afficher que si la ville n'est pas déjà détruite
                    print(f"Ville touchée! HP restants: {self.city_hp}")


        self.handle_collisions()
        for effect in self.particle_effects:
             effect.update(delta_time, self)

        self.cleanup_inactive_objects()

        if self.city_hp <= 0 and not self.game_over_flag:
            self.game_over_flag = True
            print("GAME OVER - City HP reached 0")
            self.show_error_message("GAME OVER", 10) # Message de game over visible

    def city_take_damage(self, amount):
        if self.game_over_flag: return
        if amount <= 0: return 

        self.city_hp -= amount
        if self.city_hp < 0:
            self.city_hp = 0
        # print(f"City took {amount} damage. HP: {self.city_hp}") 

    def handle_collisions(self):
        projectiles_to_remove_after_loop = set() # Utiliser un set pour éviter doublons
        enemies_hit_this_frame_by_projectile = {} # {proj_id: set(enemy_id)}

        for proj in self.projectiles:
             if not proj.active: continue
             if proj.rect.right < 0 or proj.rect.left > cfg.SCREEN_WIDTH or \
                proj.rect.bottom < 0 or proj.rect.top > cfg.SCREEN_HEIGHT + cfg.scale_value(100): # Marge pour mortiers
                 projectiles_to_remove_after_loop.add(proj)
                 continue 

             for enemy in self.enemies:
                 if not enemy.active: continue
                 
                 # Vérifier si ce projectile a déjà touché cet ennemi dans cette frame (pour projectiles non AoE)
                 if not proj.is_mortar_shell and proj.id in enemies_hit_this_frame_by_projectile and \
                    enemy.id in enemies_hit_this_frame_by_projectile[proj.id]:
                    continue


                 if proj.rect.colliderect(enemy.hitbox):
                     enemy.take_damage(proj.damage)
                     proj.on_hit(self) # Gère AoE et désactivation du projectile si besoin

                     if not proj.is_mortar_shell : # Projectiles directs sont consommés au premier hit
                         projectiles_to_remove_after_loop.add(proj)
                         if proj.id not in enemies_hit_this_frame_by_projectile:
                             enemies_hit_this_frame_by_projectile[proj.id] = set()
                         enemies_hit_this_frame_by_projectile[proj.id].add(enemy.id)
                         # Si un projectile direct touche, il est consommé, on peut sortir de la boucle des ennemis pour CE projectile
                         break 
                     
                     if not enemy.active: 
                         self.money += enemy.get_money_value()
                         self.score += enemy.get_score_value()
                         self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining -1)
                         # TODO: ParticleEffect pour mort d'ennemi
        
        for proj_to_remove in projectiles_to_remove_after_loop:
            if proj_to_remove in self.projectiles: # S'assurer qu'il est toujours là
                 proj_to_remove.active = False # Marquer pour nettoyage


    def trigger_aoe_damage(self, center_pos, radius, damage):
        # ExplosionEffect doit être défini dans objects.py
        # if hasattr(objects, 'ExplosionEffect'):
        #     self.particle_effects.append(objects.ExplosionEffect(center_pos)) 
        # else:
        #     print("Warning: ExplosionEffect class not found for AoE.")

        radius_sq = radius ** 2 # radius est déjà scalé par le projectile

        for enemy in self.enemies:
            if not enemy.active: continue
            distance_sq = (enemy.hitbox.centerx - center_pos[0])**2 + (enemy.hitbox.centery - center_pos[1])**2
            if distance_sq < radius_sq:
                enemy.take_damage(damage)
                if not enemy.active: 
                    self.money += enemy.get_money_value()
                    self.score += enemy.get_score_value()
                    self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining -1)


    def cleanup_inactive_objects(self):
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particle_effects = [eff for eff in self.particle_effects if eff.active]
        # Bâtiments et tourelles ne sont pas "détruits" de cette manière actuellement

    def draw_game_world(self):
        # 1. Dessiner le fond (si image ou couleur unie)
        # CORRIGÉ: Utiliser getattr pour un fallback si la couleur n'est pas définie
        background_color = getattr(cfg, 'COLOR_DARK_GREY_BLUE', cfg.COLOR_MAGENTA) # Default to Magenta
        self.screen.fill(background_color)

        # 2. Dessiner la zone de la grille constructible (le sol/terrain)
        ui_functions.draw_base_grid(self.screen, self)

        # 3. Dessiner les bâtiments
        # Trier pour le rendu (optionnel, mais peut améliorer l'effet de profondeur si sprites se chevauchent)
        # self.buildings.sort(key=lambda b: b.rect.bottom) 
        for building in self.buildings:
            building.draw(self.screen)

        # 4. Dessiner les tourelles
        # self.turrets.sort(key=lambda t: t.rect.bottom)
        for turret in self.turrets:
            turret.draw(self.screen)

        # 5. Dessiner les ennemis
        # self.enemies.sort(key=lambda e: e.rect.bottom)
        for enemy in self.enemies:
            enemy.draw(self.screen)
            if cfg.DEBUG_MODE: # Si vous avez un flag de debug
                 util.draw_debug_rect(self.screen, enemy.hitbox, cfg.COLOR_GREEN, 1)


        # 6. Dessiner les projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)

        # 7. Dessiner les effets de particules
        for effect in self.particle_effects:
            effect.draw(self.screen)

        # 8. Dessiner la prévisualisation du placement
        ui_functions.draw_placement_preview(self.screen, self)


    def draw_game_ui_elements(self):
        ui_functions.draw_top_bar_ui(self.screen, self) 
        ui_functions.draw_build_menu_ui(self.screen, self) 

        if self.last_error_message and self.error_message_timer > 0:
            ui_functions.draw_error_message(self.screen, self.last_error_message, self)
        
        if self.tutorial_message and self.tutorial_message_timer > 0:
            ui_functions.draw_tutorial_message(self.screen, self.tutorial_message, self)


        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen)

        if self.game_over_flag: # S'assurer que le score est bien passé
            ui_functions.draw_game_over_screen(self.screen, self.score)
