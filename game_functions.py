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
    def __init__(self, scaler: util.Scaler): # Accepts and stores scaler
        self.scaler = scaler
        self.screen = None
        self.clock = None
        self.running_game = True
        self.game_over_flag = False
        self.game_paused = False
        self.is_tutorial = False # MODIFIED: Added is_tutorial flag initialization

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
        self.grid_width_tiles = cfg.BASE_GRID_INITIAL_WIDTH_TILES
        self.grid_height_tiles = cfg.BASE_GRID_INITIAL_HEIGHT_TILES
        self.current_expansion_up_tiles = 0
        self.current_expansion_sideways_steps = 0
        self.grid_initial_width_tiles = cfg.BASE_GRID_INITIAL_WIDTH_TILES 

        self.game_grid = [[None for _ in range(self.grid_width_tiles)] for _ in range(self.grid_height_tiles)]
        self.buildable_area_rect_pixels = pygame.Rect(0,0,0,0)
        # self.update_buildable_area_rect() # Called after scaler is set, and now in init_new_game

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
            if self.current_expansion_up_tiles < cfg.BASE_GRID_MAX_EXPANSION_UP_TILES: 
                cost = int(cfg.BASE_EXPANSION_COST_UP * (cfg.EXPANSION_COST_INCREASE_FACTOR_UP ** self.current_expansion_up_tiles))
        elif direction == "side":
            if self.current_expansion_sideways_steps < cfg.BASE_GRID_MAX_EXPANSION_SIDEWAYS_STEPS: 
                cost = int(cfg.BASE_EXPANSION_COST_SIDE * (cfg.EXPANSION_COST_INCREASE_FACTOR_SIDE ** self.current_expansion_sideways_steps))
        return cost

    # MODIFIED: Added is_tutorial parameter with a default value
    def init_new_game(self, screen, clock, is_tutorial=False):
        self.__init__(self.scaler) # Re-initialize with the existing scaler
        self.screen = screen
        self.clock = clock
        self.is_tutorial = is_tutorial # MODIFIED: Set the is_tutorial flag

        # Ensure these flags are explicitly reset after __init__ for clarity, though __init__ does it.
        self.game_paused = False
        self.game_over_flag = False
        
        self.load_ui_icons() # Loads original sprites
        self.update_buildable_area_rect() # Crucial to set rect before placing foundations

        # Place initial foundations
        initial_bottom_row = self.grid_height_tiles - 1 # Use current grid_height_tiles after __init__
        for c in range(self.grid_initial_width_tiles): # Use initial width for foundations
            grid_r, grid_c = initial_bottom_row, c
            if 0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles:
                 if self.game_grid[grid_r][grid_c] is None:
                     try:
                         pixel_pos = util.convert_grid_to_pixels(
                             (grid_r, grid_c),
                             (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
                             self.scaler
                         )
                         # Ensure "fundations" type exists or use a valid default like "frame" if it's a base
                         foundation_obj = objects.Building("fundations", pixel_pos, (grid_r, grid_c), self.scaler)
                         self.game_grid[grid_r][grid_c] = foundation_obj
                         self.buildings.append(foundation_obj)
                     except Exception as e:
                         if cfg.DEBUG_MODE: print(f"ERROR placing initial foundation at ({grid_r},{grid_c}): {e}")
                 # else: # Removed warning for already occupied as it might be intended in some restart scenarios
                     # if cfg.DEBUG_MODE: print(f"WARNING: Initial foundation spot ({grid_r},{grid_c}) was already occupied.")

        self.set_time_for_first_wave()
        self.update_resource_production_consumption()

        if self.is_tutorial:
            if cfg.DEBUG_MODE: print("GAME_STATE: Initialized for TUTORIAL mode.")
            # Here you could add tutorial-specific initializations,
            # e.g., different starting money, pre-placed items for a scenario, first tutorial message.
            # self.show_tutorial_message("Bienvenue au tutoriel!", duration=10)
        else:
            if cfg.DEBUG_MODE: print("GAME_STATE: Initialized for MAIN GAME mode.")


    def load_ui_icons(self):
        self.ui_icons['money'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_money.png")
        self.ui_icons['iron'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_iron.png")
        self.ui_icons['energy'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_energy.png") 
        self.ui_icons['heart_full'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_full.png")
        self.ui_icons['heart_empty'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_empty.png")


    def update_buildable_area_rect(self):
        tile_size = self.scaler.tile_size
        ui_menu_height_bottom = self.scaler.ui_build_menu_height

        current_grid_pixel_width = self.grid_width_tiles * tile_size
        current_grid_pixel_height = self.grid_height_tiles * tile_size
        
        dynamic_grid_offset_y = self.scaler.actual_h - ui_menu_height_bottom - current_grid_pixel_height
        grid_offset_x_runtime = self.scaler.grid_offset_x

        self.buildable_area_rect_pixels = pygame.Rect(
            grid_offset_x_runtime,
            dynamic_grid_offset_y,
            current_grid_pixel_width,
            current_grid_pixel_height
        )
        # Debug prints removed for brevity, but were useful.

    def get_reinforced_row_index(self):
        # This logic depends on how expansions shift the grid.
        # If new rows are added at index 0 (pushing existing rows down),
        # the reinforced row index (relative to current grid[0][0]) changes.
        # Assuming cfg.BASE_GRID_INITIAL_HEIGHT_TILES refers to the count when grid[0] is top-most.
        # And current_expansion_up_tiles is how many rows were added "above" original top.
        # If expansion adds rows at index 0:
        return self.current_expansion_up_tiles + (cfg.BASE_GRID_INITIAL_HEIGHT_TILES - 1)


    def set_time_for_first_wave(self):
        self.time_to_next_wave_seconds = cfg.WAVE_INITIAL_PREP_TIME_SEC
        self.current_wave_number = 0 # Ensure wave number is reset

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        if cfg.DEBUG_MODE: print(f"Game Paused: {self.game_paused}")

    # MODIFIED: Added explicit method to trigger game over
    def trigger_game_over(self):
        if not self.game_over_flag:
            self.game_over_flag = True
            if cfg.DEBUG_MODE: print("GAME_STATE: Game Over triggered.")
            # Potential: save score, play sound, etc.

    def show_error_message(self, message, duration=2.5):
        self.last_error_message = message
        self.error_message_timer = duration

    def show_tutorial_message(self, message, duration=5.0):
        self.tutorial_message = message
        self.tutorial_message_timer = duration

    # MODIFIED: Added dedicated method for UI message timers
    def update_ui_message_timers(self, delta_time):
        if self.error_message_timer > 0:
            self.error_message_timer -= delta_time
            if self.error_message_timer <= 0: self.last_error_message = ""
        if self.tutorial_message_timer > 0:
            self.tutorial_message_timer -= delta_time
            if self.tutorial_message_timer <=0: self.tutorial_message = ""

    def update_timers_and_waves(self, delta_time):
        # MODIFIED: Message timer updates are moved to update_ui_message_timers
        # This guard is now only for wave progression logic
        if self.game_over_flag or self.game_paused or self.all_waves_completed:
            if self.all_waves_completed and not self.enemies and not self.wave_in_progress:
                 pass # Specific handling for post-completion state
            return

        if not self.wave_in_progress:
            self.time_to_next_wave_seconds -= delta_time
            if self.time_to_next_wave_seconds <= 0:
                self.start_next_wave()
        else: # Wave is in progress
            self.time_since_last_spawn_in_wave += delta_time
            if self.enemies_in_current_wave_to_spawn:
                delay_needed, enemy_type_id, enemy_variant = self.enemies_in_current_wave_to_spawn[0]
                if self.time_since_last_spawn_in_wave >= delay_needed:
                    self.spawn_enemy(enemy_type_id, enemy_variant)
                    self.enemies_in_current_wave_to_spawn.pop(0)
                    self.time_since_last_spawn_in_wave = 0 # Reset for next spawn in sequence
            elif not self.enemies: # No more enemies to spawn AND no active enemies on field
                self.wave_in_progress = False
                self.enemies_in_wave_remaining = 0 # Should already be 0 or close
                if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                    self.all_waves_completed = True
                    if cfg.DEBUG_MODE: print("TOUTES LES VAGUES TERMINÉES!")
                else:
                    self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC


    def start_next_wave(self):
        self.current_wave_number += 1
        if self.current_wave_number > self.max_waves and self.max_waves > 0:
            self.wave_in_progress = False
            self.all_waves_completed = True
            if cfg.DEBUG_MODE: print("Fin des vagues définies.")
            return

        if cfg.DEBUG_MODE: print(f"Starting Wave {self.current_wave_number}")
        self.wave_in_progress = True
        self.enemies_in_current_wave_to_spawn = list(self.all_wave_definitions.get(self.current_wave_number, []))
        self.enemies_in_wave_remaining = len(self.enemies_in_current_wave_to_spawn)
        self.time_since_last_spawn_in_wave = 0.0 # Reset for the new wave
        if not self.enemies_in_current_wave_to_spawn: # Wave has no enemies defined
            self.wave_in_progress = False
            self.enemies_in_wave_remaining = 0
            if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                 self.all_waves_completed = True
            else: # Prepare for next wave if this empty wave wasn't the last
                 self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC

    def spawn_enemy(self, enemy_type_id, variant_data=None):
        # Spawn position logic (simplified, adjust as needed)
        min_y_ref = self.scaler.ui_top_bar_height + self.scaler.scale_value(20) # Below top bar
        max_y_ref = self.scaler.actual_h - self.scaler.ui_build_menu_height - self.scaler.scale_value(20) # Above build menu

        if min_y_ref >= max_y_ref: # Failsafe if UI elements are too large
            spawn_y_ref = self.scaler.actual_h // 2
        else:
            spawn_y_ref = random.randint(min_y_ref, max_y_ref)
        
        # Spawn enemies off-screen to the right
        spawn_x_ref = self.scaler.actual_w + self.scaler.scale_value(50)

        # Create enemy using reference coordinates; Enemy class constructor should handle scaling to actual pixels
        new_enemy = objects.Enemy((spawn_x_ref, spawn_y_ref), enemy_type_id, variant_data, self.scaler)
        self.enemies.append(new_enemy)


    def handle_player_input(self, event, mouse_pos_pixels):
        if self.game_over_flag or self.game_paused: return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                clicked_ui_item_id = ui_functions.check_build_menu_click(self, mouse_pos_pixels, self.scaler)
                if clicked_ui_item_id:
                    if clicked_ui_item_id.startswith("expand_"):
                        action_type = clicked_ui_item_id.split("_")[1]
                        self.try_expand_build_area(action_type)
                        self.selected_item_to_place_type = None # Deselect after expansion attempt
                        self.placement_preview_sprite = None 
                    else: 
                        self.selected_item_to_place_type = clicked_ui_item_id
                        item_stats = objects.get_item_stats(self.selected_item_to_place_type)
                        sprite_name_for_preview = None
                        path_prefix = None

                        if objects.is_building_type(self.selected_item_to_place_type):
                            path_prefix = cfg.BUILDING_SPRITE_PATH
                            # Handle specific sprite cases like 'miner'
                            if self.selected_item_to_place_type == "miner" and cfg.STAT_SPRITE_VARIANTS_DICT in item_stats:
                                sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_VARIANTS_DICT].get("single") # Assuming 'single' variant for preview
                            if not sprite_name_for_preview: # Fallback to default sprite
                                sprite_name_for_preview = item_stats.get(cfg.STAT_SPRITE_DEFAULT_NAME)
                        elif objects.is_turret_type(self.selected_item_to_place_type):
                            path_prefix = cfg.TURRET_SPRITE_PATH
                            sprite_name_for_preview = item_stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME) # Turrets might have base/barrel, use base for preview

                        if sprite_name_for_preview and path_prefix:
                            preview_sprite_orig = util.load_sprite(path_prefix + sprite_name_for_preview)
                            self.placement_preview_sprite = preview_sprite_orig 
                            if not self.placement_preview_sprite: self.placement_preview_sprite = None # Ensure it's None if load fails
                        else: self.placement_preview_sprite = None
                    return # Handled UI click, no further action on this mouse down
                elif self.selected_item_to_place_type: # If an item is selected and click was not on UI
                    self.try_place_item_on_grid(mouse_pos_pixels)
            elif event.button == 3: # Right-click to deselect
                self.selected_item_to_place_type = None
                self.placement_preview_sprite = None 

        # Update placement preview validity based on current mouse position if an item is selected
        if self.selected_item_to_place_type:
            is_valid, _ = self.check_placement_validity(self.selected_item_to_place_type, mouse_pos_pixels)
            self.is_placement_valid_preview = is_valid
        else:
             self.is_placement_valid_preview = False # No item selected, so no valid preview

    def check_placement_validity(self, item_type, mouse_pixel_pos):
        grid_r, grid_c = util.convert_pixels_to_grid(mouse_pixel_pos,
                                                    (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
                                                    self.scaler)

        if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
            # Don't show error message for simply being outside, preview will indicate
            return False, (grid_r, grid_c)

        existing_item = self.game_grid[grid_r][grid_c]
        item_stats = objects.get_item_stats(item_type)
        placement_requirement_met = False
        required_base_type_msg = "Unknown requirement" # For error message

        if item_type == "frame":
            if existing_item is None: placement_requirement_met = True
            else: required_base_type_msg = "Case vide"
        elif item_type in ["generator", "storage", "gatling_turret", "mortar_turret"]:
            if existing_item is not None and existing_item.type == "frame": placement_requirement_met = True
            else: required_base_type_msg = "'Structure (frame)'"
        elif item_type == "miner":
            # Miner needs empty spot AND foundation/miner below
            if existing_item is None:
                if grid_r + 1 < self.grid_height_tiles:
                     item_below = self.game_grid[grid_r + 1][grid_c]
                     if item_below and (item_below.type == "fundations" or item_below.type == "miner"):
                         placement_requirement_met = True
                     else: required_base_type_msg = "'Fondation renforcée' ou autre 'Mineur' (en dessous)"
                else: required_base_type_msg = "Bord de la grille (nécessite support en dessous)" # Edge case
            else: required_base_type_msg = "Case vide"
        else:
             if cfg.DEBUG_MODE: print(f"AVERTISSEMENT: Règle de placement inconnue pour {item_type}")
             # self.show_error_message(f"Type d'objet inconnu: {item_type}") # Avoid error for unknown, rely on preview
             return False, (grid_r, grid_c)

        if not placement_requirement_met:
            # self.show_error_message(f"Doit être placé sur : {required_base_type_msg}") # Show on actual placement attempt
            return False, (grid_r, grid_c)

        # Check costs (only show error on actual placement attempt, not for preview)
        cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
        cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
        if self.money < cost_money: return False, (grid_r, grid_c)
        if self.iron_stock < cost_iron: return False, (grid_r, grid_c)

        # Check power (only show error on actual placement attempt)
        power_prod_impact = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        power_conso_impact = item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        # If item consumes power (and is not a producer itself, and not storage which is power-neutral)
        if power_conso_impact > 0 and power_prod_impact == 0 and item_type != "storage":
            if self.electricity_produced < (self.electricity_consumed + power_conso_impact):
                 return False, (grid_r, grid_c)

        return True, (grid_r, grid_c)


    def try_place_item_on_grid(self, mouse_pixel_pos):
        item_type = self.selected_item_to_place_type
        if not item_type: return

        is_valid, (grid_r, grid_c) = self.check_placement_validity(item_type, mouse_pixel_pos)

        # Re-check conditions specifically for error messages if placement fails
        if not is_valid:
            # Determine specific reason for invalidity to show targeted error message
            if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
                self.show_error_message("Hors de la zone constructible.")
            else:
                item_stats_for_error = objects.get_item_stats(item_type)
                existing_item_for_error = self.game_grid[grid_r][grid_c]
                req_met_error, req_type_msg_error = self.get_placement_requirement_message(item_type, existing_item_for_error, grid_r, grid_c)
                if not req_met_error:
                    self.show_error_message(f"Doit être placé sur : {req_type_msg_error}")
                elif self.money < item_stats_for_error.get(cfg.STAT_COST_MONEY, 0):
                    self.show_error_message(f"Pas assez d'argent! ({item_stats_for_error.get(cfg.STAT_COST_MONEY, 0)}$)")
                elif self.iron_stock < item_stats_for_error.get(cfg.STAT_COST_IRON, 0):
                    self.show_error_message(f"Pas assez de fer! ({item_stats_for_error.get(cfg.STAT_COST_IRON, 0)} Fe)")
                else: # Check power last if other conditions met
                    power_prod = item_stats_for_error.get(cfg.STAT_POWER_PRODUCTION, 0)
                    power_cons = item_stats_for_error.get(cfg.STAT_POWER_CONSUMPTION, 0)
                    if power_cons > 0 and power_prod == 0 and item_type != "storage":
                        if self.electricity_produced < (self.electricity_consumed + power_cons):
                            self.show_error_message("Pas assez d'énergie disponible!")
                        else:
                            self.show_error_message("Placement invalide (raison inconnue).") # Fallback
                    else:
                        self.show_error_message("Placement invalide (raison inconnue).") # Fallback
            if cfg.DEBUG_MODE: print(f"Invalid placement attempt for {item_type} at ({grid_r},{grid_c})")
            return


        # If is_valid is true, proceed with placement
        item_stats = objects.get_item_stats(item_type)
        self.money -= item_stats.get(cfg.STAT_COST_MONEY, 0)
        self.iron_stock -= item_stats.get(cfg.STAT_COST_IRON, 0)

        pixel_pos = util.convert_grid_to_pixels(
            (grid_r, grid_c),
            (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
            self.scaler
        )

        existing_item = self.game_grid[grid_r][grid_c]
        if existing_item and existing_item.type == "frame" and item_type != "frame": # Building on a frame
             if existing_item in self.buildings:
                 existing_item.active = False # Mark for removal/deactivation
                 self.buildings.remove(existing_item) # Or handle through cleanup_inactive_objects

        new_item = None
        if objects.is_turret_type(item_type):
            new_item = objects.Turret(item_type, pixel_pos, (grid_r, grid_c), self.scaler)
            self.turrets.append(new_item)
        elif objects.is_building_type(item_type):
            new_item = objects.Building(item_type, pixel_pos, (grid_r, grid_c), self.scaler)
            self.buildings.append(new_item)

        if new_item:
             self.game_grid[grid_r][grid_c] = new_item
             new_item.update_sprite_based_on_context(self.game_grid, grid_r, grid_c, self.scaler) # Update new item

             # Update neighbors
             for dr_n, dc_n in [(0,1), (0,-1), (1,0), (-1,0)]:
                 nr, nc = grid_r + dr_n, grid_c + dc_n
                 if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                      neighbor = self.game_grid[nr][nc]
                      if neighbor and hasattr(neighbor, 'update_sprite_based_on_context'):
                          neighbor.update_sprite_based_on_context(self.game_grid, nr, nc, self.scaler)
             
             # Specific update for miner affecting item below it (if also a miner)
             if item_type == "miner" and grid_r + 1 < self.grid_height_tiles:
                 item_below = self.game_grid[grid_r + 1][grid_c]
                 if item_below and item_below.type == "miner" and hasattr(item_below, 'update_sprite_based_on_context'):
                     item_below.update_sprite_based_on_context(self.game_grid, grid_r + 1, grid_c, self.scaler)


             self.check_and_apply_adjacency_bonus(new_item, grid_r, grid_c) # For the new item
             # If new item is storage, also re-check bonuses for its storage neighbors
             if new_item.type == "storage": 
                 for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                     nr, nc = grid_r + dr, grid_c + dc
                     if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                          neighbor_item = self.game_grid[nr][nc]
                          if neighbor_item and neighbor_item.type == "storage":
                              self.check_and_apply_adjacency_bonus(neighbor_item, nr, nc)

             self.update_resource_production_consumption()
             if cfg.DEBUG_MODE: print(f"Placed {item_type} at ({grid_r},{grid_c})")
        else: # Should not happen if logic is correct
             if cfg.DEBUG_MODE: print(f"ERREUR: Échec de création de l'objet de type {item_type}")
             self.money += item_stats.get(cfg.STAT_COST_MONEY, 0) 
             self.iron_stock += item_stats.get(cfg.STAT_COST_IRON, 0)

    # Helper for try_place_item_on_grid to get specific error messages
    def get_placement_requirement_message(self, item_type, existing_item, grid_r, grid_c):
        placement_requirement_met = False
        required_base_type_msg = "Unknown requirement"

        if item_type == "frame":
            if existing_item is None: placement_requirement_met = True
            else: required_base_type_msg = "Case vide"
        elif item_type in ["generator", "storage", "gatling_turret", "mortar_turret"]:
            if existing_item is not None and existing_item.type == "frame": placement_requirement_met = True
            else: required_base_type_msg = "'Structure (frame)'"
        elif item_type == "miner":
            if existing_item is None:
                if grid_r + 1 < self.grid_height_tiles:
                     item_below = self.game_grid[grid_r + 1][grid_c]
                     if item_below and (item_below.type == "fundations" or item_below.type == "miner"):
                         placement_requirement_met = True
                     else: required_base_type_msg = "'Fondation renforcée' ou autre 'Mineur' (en dessous)"
                else: required_base_type_msg = "Bord de la grille (nécessite support en dessous)"
            else: required_base_type_msg = "Case vide"
        else:
            return False, "Type d'objet inconnu pour placement"
        return placement_requirement_met, required_base_type_msg


    def check_and_apply_adjacency_bonus(self, item, r, c):
        if not item or not hasattr(item, 'apply_adjacency_bonus_effect'): return
        if item.type == "storage": # Only storage has adjacency bonus currently
            adjacent_similar_items_count = 0
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]: # Check 4 directions
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and \
                   self.game_grid[nr][nc] and self.game_grid[nr][nc].type == "storage":
                    adjacent_similar_items_count +=1
            item.apply_adjacency_bonus_effect(adjacent_similar_items_count)


    def try_expand_build_area(self, direction):
        cost_expansion = self.get_next_expansion_cost(direction)
        if cost_expansion == "Max":
            self.show_error_message("Expansion max atteinte.")
            return
        if not isinstance(cost_expansion, (int, float)) or cost_expansion <= 0: # Should be caught by "Max"
            self.show_error_message("Coût d'expansion invalide.") # Should not happen if get_next_expansion_cost is robust
            return

        if self.money >= cost_expansion:
            self.money -= cost_expansion
            if direction == "up":
                self.current_expansion_up_tiles += 1
                new_row = [None for _ in range(self.grid_width_tiles)]
                self.game_grid.insert(0, new_row) # Add new row at the top
                self.grid_height_tiles += 1
                # Shift grid_pos for all existing items
                for r_idx in range(1, self.grid_height_tiles): # Start from 1 as row 0 is new
                    for c_idx in range(self.grid_width_tiles):
                        item_obj = self.game_grid[r_idx][c_idx]
                        if item_obj:
                            item_obj.grid_pos = (item_obj.grid_pos[0] + 1, item_obj.grid_pos[1])
            elif direction == "side":
                self.current_expansion_sideways_steps += 1
                tiles_to_add = cfg.BASE_GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP 
                for r_idx in range(self.grid_height_tiles):
                    self.game_grid[r_idx].extend([None for _ in range(tiles_to_add)])
                self.grid_width_tiles += tiles_to_add

            self.update_buildable_area_rect() # Recalculate grid pixel rect based on new dimensions/offsets

            # Update pixel positions and sprites of all items due to potential shift of buildable_area_rect
            for r in range(self.grid_height_tiles):
                 for c in range(self.grid_width_tiles):
                      item_obj = self.game_grid[r][c]
                      if item_obj:
                           item_obj.rect.topleft = util.convert_grid_to_pixels((r, c),
                                                                            (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
                                                                            self.scaler) 
                           if hasattr(item_obj, 'update_sprite_based_on_context'): # Re-check context
                               item_obj.update_sprite_based_on_context(self.game_grid, r, c, self.scaler) 

            self.update_resource_production_consumption() # Expansion might affect resource view or enable new placements
            self.show_error_message("Zone de base étendue!")
            if cfg.DEBUG_MODE: print(f"Expanded grid to {self.grid_width_tiles}x{self.grid_height_tiles}")
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$)")

    def update_resource_production_consumption(self):
        total_electricity_produced = 0
        total_electricity_consumed = 0
        # total_iron_production_pm = 0 # This was not used directly, effective is calculated
        total_iron_storage_increase = 0
        all_constructs = self.buildings + self.turrets # Combine for easier iteration

        # First pass: sum potential production/consumption and storage
        for item in all_constructs:
            if not item.active_in_world: continue # Skip items marked for removal or inactive
            item_stats = objects.get_item_stats(item.type)
            total_electricity_produced += item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
            total_electricity_consumed += item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
            
            if isinstance(item, objects.Building) and item.type == "storage":
                base_storage = item_stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
                bonus_storage = getattr(item, 'current_adjacency_bonus_value', 0) # If bonus applied
                total_iron_storage_increase += (base_storage + bonus_storage)

        # Determine if there's a global power deficit
        is_globally_powered = total_electricity_produced >= total_electricity_consumed
        effective_iron_production_pm = 0

        # Second pass: set functional active state and calculate effective production
        for item in all_constructs:
            if not item.active_in_world: continue
            item_stats = objects.get_item_stats(item.type)
            
            is_generator = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0) > 0
            is_neutral_power_wise = item.type in ["frame", "fundations", "storage"] # These don't consume to function
            item_consumes_power_to_function = item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0) > 0 and not is_generator and not is_neutral_power_wise
            
            item_is_functionally_powered = True # Assume powered
            if item_consumes_power_to_function and not is_globally_powered:
                item_is_functionally_powered = False # Shut down if power deficit and it needs power

            item.set_active_state(item_is_functionally_powered) # Update visual/functional state

            if item_is_functionally_powered: # Only count production if item is powered
                if isinstance(item, objects.Building) and item.type == "miner":
                     effective_iron_production_pm += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)

        self.electricity_produced = total_electricity_produced
        self.electricity_consumed = total_electricity_consumed
        self.iron_production_per_minute = effective_iron_production_pm
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + total_iron_storage_increase


    def update_resources_per_tick(self, delta_time):
        # This method is fine, but called from update_game_logic which already has pause/game_over guards
        # if self.game_paused or self.game_over_flag: return # Redundant if called from guarded context
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)

    def update_game_logic(self, delta_time):
        # MODIFIED: Call update_ui_message_timers here for active game state
        if self.game_over_flag or self.game_paused:
            # update_ui_message_timers is called by gamemodes.py in these states
            return

        self.total_time_elapsed_seconds += delta_time
        self.update_ui_message_timers(delta_time) # Update message timers
        self.update_timers_and_waves(delta_time)  # Update wave progression
        self.update_resources_per_tick(delta_time)
        
        power_available_overall = self.electricity_produced >= self.electricity_consumed # Re-check for turrets/buildings update

        for turret in self.turrets:
             turret.update(delta_time, self.enemies, power_available_overall, self, self.scaler) 
        for building in self.buildings: # Buildings might have updates (e.g., animations, passive effects)
            building.update(delta_time, self, self.scaler) 
        for proj in self.projectiles:
            proj.update(delta_time, self, self.scaler) 
        for enemy in self.enemies:
            enemy.update(delta_time, self, self.scaler) 
            base_line_x = self.buildable_area_rect_pixels.left 
            # MODIFIED: Check enemy.active before processing city damage
            if enemy.active and enemy.rect.right < base_line_x:
                self.city_take_damage(enemy.get_city_damage())
                enemy.active = False # Mark for cleanup
                if self.city_hp > 0 and cfg.DEBUG_MODE: print(f"Ville touchée! HP restants: {self.city_hp}")
        for effect in self.particle_effects:
             effect.update(delta_time, self, self.scaler) 

        self.handle_collisions()
        self.cleanup_inactive_objects()
        
        if self.city_hp <= 0 and not self.game_over_flag:
            self.trigger_game_over() # MODIFIED: Use the new method

    def city_take_damage(self, amount):
        if self.game_over_flag or amount <= 0: return # No damage if game over or no damage amount
        self.city_hp -= amount
        if self.city_hp < 0: self.city_hp = 0
        # Game over check is now in update_game_logic using trigger_game_over

    def handle_collisions(self):
        projectiles_to_remove_after_loop = set()
        # To prevent one non-AOE projectile from hitting multiple enemies in the same frame due to fast movement/overlap
        enemies_hit_this_frame_by_projectile = {} # Key: proj.id, Value: set of enemy.id

        for proj in self.projectiles:
             if not proj.active: continue

             # Optional: Off-screen check for projectiles if they don't have self-destruct timers
             if proj.rect.right < -self.scaler.scale_value(50) or proj.rect.left > self.scaler.actual_w + self.scaler.scale_value(50) or \
                proj.rect.bottom < -self.scaler.scale_value(50) or proj.rect.top > self.scaler.actual_h + self.scaler.scale_value(100): 
                 projectiles_to_remove_after_loop.add(proj)
                 continue

             for enemy in self.enemies:
                 if not enemy.active: continue
                 
                 is_mortar_shell_impact = hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell and proj.has_impacted
                 is_standard_projectile = not (hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell)

                 # If standard projectile has already hit an enemy this frame, skip (it should be marked for removal)
                 if is_standard_projectile and proj in projectiles_to_remove_after_loop:
                     continue
                 # If this specific enemy has already been hit by this specific standard projectile (rare, but defensive)
                 if is_standard_projectile and proj.id in enemies_hit_this_frame_by_projectile and \
                    enemy.id in enemies_hit_this_frame_by_projectile[proj.id]:
                     continue

                 if proj.rect.colliderect(enemy.hitbox):
                     if not is_mortar_shell_impact: # Mortar damage is handled by its on_hit (AOE)
                         enemy.take_damage(proj.damage)
                     
                     proj.on_hit(self) # Projectile handles its own behavior (e.g., AOE for mortar, self-destruct)

                     if is_standard_projectile: # Standard projectiles are removed on first hit
                         projectiles_to_remove_after_loop.add(proj)
                         if proj.id not in enemies_hit_this_frame_by_projectile:
                             enemies_hit_this_frame_by_projectile[proj.id] = set()
                         enemies_hit_this_frame_by_projectile[proj.id].add(enemy.id)
                         
                         if not enemy.active: # If enemy died from this hit
                            self.money += enemy.get_money_value()
                            self.score += enemy.get_score_value()
                            self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)
                         break # Standard projectile hit one enemy, its job is done for this frame
                     elif not enemy.active and is_mortar_shell_impact: # Enemy died from AOE (handled in trigger_aoe_damage)
                         # Money/score for AOE kills are handled in trigger_aoe_damage
                         pass


        for proj_to_remove in projectiles_to_remove_after_loop:
             if proj_to_remove in self.projectiles: # Check if not already removed
                 proj_to_remove.active = False # Mark for cleanup

    def trigger_aoe_damage(self, center_pos, scaled_radius, damage): 
        if hasattr(objects, 'ParticleEffect'): # Check if ParticleEffect class exists
            # Example: Create a generic explosion particle effect
            # You might want specific effect types ('mortar_explosion', 'bomb_explosion')
            # effect = objects.ParticleEffect(center_pos, "explosion_generic", self.scaler, duration=0.5, particle_count=20)
            # self.particle_effects.append(effect)
            pass # Placeholder for particle effect creation

        radius_sq = scaled_radius ** 2
        for enemy in self.enemies:
            if not enemy.active: continue # Skip already dead/inactive enemies
            
            # Calculate distance from enemy center to explosion center
            distance_sq = (enemy.hitbox.centerx - center_pos[0])**2 + (enemy.hitbox.centery - center_pos[1])**2
            if distance_sq < radius_sq: # If enemy is within AOE radius
                enemy.take_damage(damage)
                if not enemy.active: # If enemy died from AOE damage
                    self.money += enemy.get_money_value()
                    self.score += enemy.get_score_value()
                    self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)

    def cleanup_inactive_objects(self):
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particle_effects = [eff for eff in self.particle_effects if eff.active]
        # Consider buildings/turrets if they can be destroyed or sold and marked inactive
        # self.buildings = [b for b in self.buildings if b.active_in_world]
        # self.turrets = [t for t in self.turrets if t.active_in_world]


    def draw_game_world(self):
        background_color = getattr(cfg, 'COLOR_BACKGROUND', cfg.COLOR_MAGENTA)
        self.screen.fill(background_color)
        ui_functions.draw_base_grid(self.screen, self, self.scaler)
        
        # Combine all drawable game objects
        all_game_objects = [obj for obj in (self.buildings + self.turrets + self.enemies + self.projectiles + self.particle_effects) if hasattr(obj, 'rect') and obj.active_in_world] # Check active_in_world
        # Sort by rect.bottom for pseudo-3D layering, then by a secondary tie-breaker if needed (e.g., object type for consistency)
        all_game_objects.sort(key=lambda obj: (obj.rect.bottom, isinstance(obj, objects.Enemy))) # Enemies drawn over projectiles if at same y

        for obj in all_game_objects:
            obj.draw(self.screen) 
            if cfg.DEBUG_MODE:
                 if isinstance(obj, objects.Enemy) and hasattr(obj, 'hitbox'):
                     util.draw_debug_rect(self.screen, obj.hitbox, cfg.COLOR_GREEN, 1)
                 elif isinstance(obj, objects.Projectile): # and not obj.has_impacted: # Only draw non-impacted projectiles
                     util.draw_debug_rect(self.screen, obj.rect, cfg.COLOR_YELLOW, 1)
                 elif isinstance(obj, (objects.Building, objects.Turret)):
                     util.draw_debug_rect(self.screen, obj.rect, cfg.COLOR_BLUE, 1)


        ui_functions.draw_placement_preview(self.screen, self, self.scaler)


    def draw_game_ui_elements(self):
        ui_functions.draw_top_bar_ui(self.screen, self, self.scaler) 
        ui_functions.draw_build_menu_ui(self.screen, self, self.scaler) 
        
        if self.last_error_message and self.error_message_timer > 0:
             ui_functions.draw_error_message(self.screen, self.last_error_message, self, self.scaler)
        if self.tutorial_message and self.tutorial_message_timer > 0:
            ui_functions.draw_tutorial_message(self.screen, self.tutorial_message, self, self.scaler)
        
        # MODIFIED: Use elif to prevent drawing pause and game over screens simultaneously
        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen, self.scaler) 
        elif self.game_over_flag: # Only draw game over if not paused (pause takes precedence if both were true)
            ui_functions.draw_game_over_screen(self.screen, self.score, self.scaler)

    # MODIFIED: Added stub methods for tutorial logic called by gamemodes.py
    def update_tutorial_specific_logic(self, event):
        if not self.is_tutorial: return
        # Placeholder for tutorial-specific event handling (e.g., checking for specific key presses, clicks on highlighted UI)
        if cfg.DEBUG_MODE and event.type not in [pygame.MOUSEMOTION, pygame.ACTIVEEVENT]: # Avoid spam
             # print(f"GAME_STATE (Tutorial): update_tutorial_specific_logic received event {event.type}")
             pass


    def update_tutorial_progression(self, delta_time):
        if not self.is_tutorial: return
        # Placeholder for tutorial progression logic
        # (e.g., checking if player completed a task, advancing to next tutorial step, showing new messages)
        # Example:
        # if self.tutorial_step == 1 and self.money > cfg.INITIAL_MONEY + 50:
        #     self.tutorial_step = 2
        #     self.show_tutorial_message("Good job! Now try building a turret.", 10)
        pass
