# game_functions.py

import pygame
import random
import os
import game_config as cfg
import utility_functions as util
import objects
import ui_functions  # We will use the more complete versions of these now
import wave_definitions


class GameState:
    """Classe pour encapsuler l'état global du jeu pour un accès facile."""

    def __init__(self, scaler: util.Scaler):
        self.scaler = scaler
        self.screen = None
        self.clock = None
        # self.running_game = True # This should be managed by the gamemode loop, not GameState
        self.game_over_flag = False
        self.game_paused = False
        self.is_tutorial = False

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
        self.buildable_area_rect_pixels = pygame.Rect(0, 0, 0, 0)
        # update_buildable_area_rect() is called in init_new_game

        # Listes d'objets actifs
        self.buildings = []  # Includes "fundations"
        self.turrets = []
        self.enemies = []
        self.projectiles = []
        self.particle_effects = []  # For explosions etc.

        self.selected_item_to_place_type = None
        self.placement_preview_sprite = None  # Store original unscaled sprite
        self.is_placement_valid_preview = False

        self.ui_icons = {}
        self.last_error_message = ""
        self.error_message_timer = 0.0
        self.tutorial_message = ""
        self.tutorial_message_timer = 0.0
        self.score = 0

        self.all_wave_definitions = {}  # Initialized properly in init_new_game
        self.max_waves = 0
        self.all_waves_completed = False
        # print("GameState __init__ finished, scaler:", self.scaler)

    def init_new_game(self, screen, clock, is_tutorial=False):
        # Call __init__ to reset all attributes, passing the existing scaler
        self.__init__(self.scaler)  # This line is crucial and correctly placed.
        self.screen = screen
        self.clock = clock
        self.is_tutorial = is_tutorial

        self.game_paused = False  # Explicitly ensure not paused on new game
        self.game_over_flag = False  # Explicitly ensure not game over

        self.load_ui_icons()
        self.update_buildable_area_rect()  # Now this uses self.scaler correctly

        # Place initial foundations
        initial_bottom_row_idx = self.grid_height_tiles - 1
        for c in range(self.grid_initial_width_tiles):
            grid_r, grid_c = initial_bottom_row_idx, c
            if 0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles:
                if self.game_grid[grid_r][grid_c] is None:
                    pixel_pos = util.convert_grid_to_pixels(
                        (grid_r, grid_c),
                        (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
                        self.scaler
                    )
                    try:
                        foundation_obj = objects.Building("fundations", pixel_pos, (grid_r, grid_c), self.scaler)
                        self.game_grid[grid_r][grid_c] = foundation_obj
                        self.buildings.append(foundation_obj)
                    except Exception as e:
                        if cfg.DEBUG_MODE: print(f"ERROR placing initial foundation: {e}")

        if hasattr(wave_definitions, 'load_waves'):
            self.all_wave_definitions = wave_definitions.load_waves()
            self.max_waves = len(self.all_wave_definitions) if self.all_wave_definitions else 0
        else:
            self.all_wave_definitions = {}
            self.max_waves = 0
            if cfg.DEBUG_MODE: print("AVERTISSEMENT: wave_definitions.load_waves() non trouvé lors de init_new_game.")

        self.set_time_for_first_wave()
        self.update_resource_production_consumption()

        if cfg.DEBUG_MODE:
            print(f"GAME_STATE: Initialized for {'TUTORIAL' if self.is_tutorial else 'MAIN GAME'} mode.")
            print(f"  Initial buildable_area_rect_pixels: {self.buildable_area_rect_pixels}")

    def load_ui_icons(self):
        self.ui_icons['money'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, "icon_money.png"))
        self.ui_icons['iron'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, "icon_iron.png"))
        self.ui_icons['energy'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, "icon_energy.png"))
        self.ui_icons['heart_full'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, "heart_full.png"))
        self.ui_icons['heart_empty'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, "heart_empty.png"))

    def update_buildable_area_rect(self):
        tile_size = self.scaler.tile_size
        # ui_build_menu_height is a DIMENSION, used to calculate the grid's bottom position
        ui_menu_height_bottom_dim = self.scaler.ui_build_menu_height
        current_grid_pixel_width = self.grid_width_tiles * tile_size
        current_grid_pixel_height = self.grid_height_tiles * tile_size

        # X position of the grid: origin of usable area + scaled offset for the grid from that origin
        final_grid_start_x = self.scaler.screen_origin_x + self.scaler.scaled_grid_offset_x

        # Y position of the grid:
        # The grid's bottom edge should align with the top of the build menu.
        # The build menu's top edge (within usable area) is:
        # (self.scaler.screen_origin_y + self.scaler.usable_h) - ui_menu_height_bottom_dim
        grid_bottom_y_abs = (self.scaler.screen_origin_y + self.scaler.usable_h) - ui_menu_height_bottom_dim
        final_grid_start_y = grid_bottom_y_abs - current_grid_pixel_height

        self.buildable_area_rect_pixels = pygame.Rect(
            final_grid_start_x,
            final_grid_start_y,
            current_grid_pixel_width, current_grid_pixel_height
        )

        if cfg.DEBUG_MODE:
            print(f"GameState DEBUG: Grid Rect Updated: {self.buildable_area_rect_pixels}")
            print(
                f"  Scaler: screen_origin_x={self.scaler.screen_origin_x}, screen_origin_y={self.scaler.screen_origin_y}")
            print(f"  Scaler: usable_w={self.scaler.usable_w}, usable_h={self.scaler.usable_h}")
            print(f"  Scaler: scaled_grid_offset_x={self.scaler.scaled_grid_offset_x}")
            print(f"  Final Grid Start X: {final_grid_start_x}, Final Grid Start Y: {final_grid_start_y}")
            print(
                f"  UI Menu Height (dim): {ui_menu_height_bottom_dim}, Grid Pixel Height: {current_grid_pixel_height}")
            print(f"  Grid Bottom Y Absolute: {grid_bottom_y_abs}")

    # --- DRAWING METHODS ---
    def draw_game_world(self):
        self.screen.fill(cfg.COLOR_BACKGROUND)  # This fills the entire actual screen

        # Draw a rectangle representing the usable area if margins are active
        if self.scaler.screen_margin_h > 0 and cfg.DEBUG_MODE:
            usable_debug_rect = pygame.Rect(self.scaler.screen_origin_x, self.scaler.screen_origin_y,
                                            self.scaler.usable_w, self.scaler.usable_h)
            pygame.draw.rect(self.screen, (50, 0, 0), usable_debug_rect, 1)  # Dark red border for usable area

        ui_functions.draw_base_grid(self.screen, self, self.scaler)

        all_game_objects_to_draw = []
        for obj_list in [self.buildings, self.turrets, self.enemies, self.projectiles, self.particle_effects]:
            for obj in obj_list:
                if obj and obj.active and hasattr(obj, 'rect'):
                    all_game_objects_to_draw.append(obj)

        all_game_objects_to_draw.sort(key=lambda obj: obj.rect.bottom)

        for obj in all_game_objects_to_draw:
            obj.draw(self.screen)
            if cfg.DEBUG_MODE:
                if isinstance(obj, objects.Enemy) and hasattr(obj, 'hitbox'):
                    util.draw_debug_rect(self.screen, obj.hitbox, cfg.COLOR_GREEN, 1)
                elif hasattr(obj, 'rect'):
                    util.draw_debug_rect(self.screen, obj.rect, cfg.COLOR_YELLOW, 1)

        ui_functions.draw_placement_preview(self.screen, self, self.scaler)

    def draw_game_ui_elements(self):
        if not self.game_paused and not self.game_over_flag:
            ui_functions.draw_top_bar_ui(self.screen, self, self.scaler)
            ui_functions.draw_build_menu_ui(self.screen, self, self.scaler)

            if self.last_error_message and self.error_message_timer > 0:
                ui_functions.draw_error_message(self.screen, self.last_error_message, self, self.scaler)
            if self.tutorial_message and self.tutorial_message_timer > 0:
                ui_functions.draw_tutorial_message(self.screen, self.tutorial_message, self, self.scaler)

        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen, self.scaler)
        elif self.game_over_flag:
            ui_functions.draw_game_over_screen(self.screen, self.score, self.scaler)

    def get_reinforced_row_index(self):
        return self.current_expansion_up_tiles + (cfg.BASE_GRID_INITIAL_HEIGHT_TILES - 1)

    def set_time_for_first_wave(self):
        self.time_to_next_wave_seconds = cfg.WAVE_INITIAL_PREP_TIME_SEC
        self.current_wave_number = 0

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        if cfg.DEBUG_MODE: print(f"Game Paused: {self.game_paused}")

    def trigger_game_over(self):
        if not self.game_over_flag:
            self.game_over_flag = True
            if cfg.DEBUG_MODE: print("GAME_STATE: Game Over triggered.")

    def show_error_message(self, message, duration=2.5):
        self.last_error_message = message
        self.error_message_timer = duration

    def show_tutorial_message(self, message, duration=5.0):
        self.tutorial_message = message
        self.tutorial_message_timer = duration

    def update_ui_message_timers(self, delta_time):
        if self.error_message_timer > 0:
            self.error_message_timer -= delta_time
            if self.error_message_timer <= 0: self.last_error_message = ""
        if self.tutorial_message_timer > 0:
            self.tutorial_message_timer -= delta_time
            if self.tutorial_message_timer <= 0: self.tutorial_message = ""

    def update_timers_and_waves(self, delta_time):
        if self.game_over_flag or self.game_paused or self.all_waves_completed:
            if self.all_waves_completed and not self.enemies and not self.wave_in_progress:
                pass
            return

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
        self.time_since_last_spawn_in_wave = 0.0
        if not self.enemies_in_current_wave_to_spawn:
            self.wave_in_progress = False
            self.enemies_in_wave_remaining = 0
            if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                self.all_waves_completed = True
            else:
                self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC

    def spawn_enemy(self, enemy_type_id, variant_data=None):
        # Les positions de spawn Y doivent être dans la zone Y utilisable de l'écran
        # Min Y for spawn: top of usable area + top_bar_height + some padding
        min_y_spawn_on_screen = self.scaler.screen_origin_y + self.scaler.ui_top_bar_height + self.scaler.scale_value(
            cfg.BASE_ENEMY_SPAWN_Y_PADDING)
        # Max Y for spawn: bottom of usable area - build_menu_height - some padding
        max_y_spawn_on_screen = (
                                            self.scaler.screen_origin_y + self.scaler.usable_h) - self.scaler.ui_build_menu_height - self.scaler.scale_value(
            cfg.BASE_ENEMY_SPAWN_Y_PADDING)

        spawn_y_on_screen = 0
        if min_y_spawn_on_screen >= max_y_spawn_on_screen:  # Failsafe if usable space is too small
            spawn_y_on_screen = self.scaler.screen_origin_y + self.scaler.usable_h // 2  # Center Y of usable area
            if cfg.DEBUG_MODE: print(
                f"WARN: Enemy spawn Y range invalid ({min_y_spawn_on_screen} >= {max_y_spawn_on_screen}). Spawning at usable center Y.")
        else:
            spawn_y_on_screen = random.randint(min_y_spawn_on_screen, max_y_spawn_on_screen)

        # Spawn X à droite de la zone utilisable
        spawn_x_on_screen = self.scaler.screen_origin_x + self.scaler.usable_w + self.scaler.scale_value(
            cfg.BASE_ENEMY_SPAWN_X_OFFSET)

        new_enemy = objects.Enemy((spawn_x_on_screen, spawn_y_on_screen), enemy_type_id, variant_data, self.scaler)
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
                        self.selected_item_to_place_type = None
                        self.placement_preview_sprite = None
                    else:
                        self.selected_item_to_place_type = clicked_ui_item_id
                        item_stats = objects.get_item_stats(self.selected_item_to_place_type)
                        sprite_name_for_preview = None
                        path_prefix = None

                        if objects.is_building_type(self.selected_item_to_place_type):
                            path_prefix = cfg.BUILDING_SPRITE_PATH
                            if self.selected_item_to_place_type == "miner" and cfg.STAT_SPRITE_VARIANTS_DICT in item_stats:
                                sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_VARIANTS_DICT].get("single")
                            if not sprite_name_for_preview:
                                sprite_name_for_preview = item_stats.get(cfg.STAT_SPRITE_DEFAULT_NAME)
                        elif objects.is_turret_type(self.selected_item_to_place_type):
                            path_prefix = cfg.TURRET_SPRITE_PATH
                            sprite_name_for_preview = item_stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME)

                        if sprite_name_for_preview and path_prefix:
                            preview_sprite_orig = util.load_sprite(os.path.join(path_prefix, sprite_name_for_preview))
                            self.placement_preview_sprite = preview_sprite_orig
                            if not self.placement_preview_sprite: self.placement_preview_sprite = None
                        else:
                            self.placement_preview_sprite = None
                    return
                elif self.selected_item_to_place_type:
                    self.try_place_item_on_grid(mouse_pos_pixels)
            elif event.button == 3:
                self.selected_item_to_place_type = None
                self.placement_preview_sprite = None

        if self.selected_item_to_place_type:
            is_valid, _ = self.check_placement_validity(self.selected_item_to_place_type, mouse_pos_pixels)
            self.is_placement_valid_preview = is_valid
        else:
            self.is_placement_valid_preview = False

    def check_placement_validity(self, item_type, mouse_pixel_pos):
        grid_r, grid_c = util.convert_pixels_to_grid(mouse_pixel_pos,
                                                     (self.buildable_area_rect_pixels.x,
                                                      self.buildable_area_rect_pixels.y),
                                                     self.scaler)

        if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
            return False, (grid_r, grid_c)

        existing_item = self.game_grid[grid_r][grid_c]
        item_stats = objects.get_item_stats(item_type)
        placement_requirement_met = False

        if item_type == "frame":
            if existing_item is None:
                placement_requirement_met = True
        elif item_type in ["generator", "storage", "gatling_turret", "mortar_turret"]:
            if existing_item is not None and existing_item.type == "frame":
                placement_requirement_met = True
        elif item_type == "miner":
            if existing_item is None:
                if grid_r + 1 < self.grid_height_tiles:
                    item_below = self.game_grid[grid_r + 1][grid_c]
                    if item_below and (item_below.type == "fundations" or item_below.type == "miner"):
                        placement_requirement_met = True
        else:
            if cfg.DEBUG_MODE: print(f"AVERTISSEMENT: Règle de placement non définie pour {item_type}")
            return False, (grid_r, grid_c)

        if not placement_requirement_met:
            return False, (grid_r, grid_c)

        cost_money = item_stats.get(cfg.STAT_COST_MONEY, 0)
        cost_iron = item_stats.get(cfg.STAT_COST_IRON, 0)
        if self.money < cost_money: return False, (grid_r, grid_c)
        if self.iron_stock < cost_iron: return False, (grid_r, grid_c)

        power_prod_impact = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        power_conso_impact = item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)
        if power_conso_impact > 0 and power_prod_impact == 0 and item_type != "storage":
            if self.electricity_produced < (self.electricity_consumed + power_conso_impact):
                return False, (grid_r, grid_c)

        return True, (grid_r, grid_c)

    def try_place_item_on_grid(self, mouse_pixel_pos):
        item_type = self.selected_item_to_place_type
        if not item_type: return

        is_valid, (grid_r, grid_c) = self.check_placement_validity(item_type, mouse_pixel_pos)

        if not is_valid:
            if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles):
                self.show_error_message("Hors de la zone constructible.")
            else:
                item_stats_for_error = objects.get_item_stats(item_type)
                existing_item_for_error = self.game_grid[grid_r][grid_c]
                req_met_error, req_type_msg_error = self.get_placement_requirement_message(item_type,
                                                                                           existing_item_for_error,
                                                                                           grid_r, grid_c)
                if not req_met_error:
                    self.show_error_message(f"Doit être placé sur : {req_type_msg_error}")
                elif self.money < item_stats_for_error.get(cfg.STAT_COST_MONEY, 0):
                    self.show_error_message(
                        f"Pas assez d'argent! ({item_stats_for_error.get(cfg.STAT_COST_MONEY, 0)}$)")
                elif self.iron_stock < item_stats_for_error.get(cfg.STAT_COST_IRON, 0):
                    self.show_error_message(f"Pas assez de fer! ({item_stats_for_error.get(cfg.STAT_COST_IRON, 0)} Fe)")
                else:
                    power_prod = item_stats_for_error.get(cfg.STAT_POWER_PRODUCTION, 0)
                    power_cons = item_stats_for_error.get(cfg.STAT_POWER_CONSUMPTION, 0)
                    if power_cons > 0 and power_prod == 0 and item_type != "storage":
                        if self.electricity_produced < (self.electricity_consumed + power_cons):
                            self.show_error_message("Pas assez d'énergie disponible!")
                        else:
                            self.show_error_message("Placement invalide (condition non remplie).")
                    else:
                        self.show_error_message("Placement invalide (condition non remplie).")
            if cfg.DEBUG_MODE: print(f"Invalid placement attempt for {item_type} at ({grid_r},{grid_c})")
            return

        item_stats = objects.get_item_stats(item_type)
        self.money -= item_stats.get(cfg.STAT_COST_MONEY, 0)
        self.iron_stock -= item_stats.get(cfg.STAT_COST_IRON, 0)

        pixel_pos = util.convert_grid_to_pixels(
            (grid_r, grid_c),
            (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
            self.scaler
        )

        existing_item = self.game_grid[grid_r][grid_c]
        if existing_item and existing_item.type == "frame" and item_type != "frame":
            if existing_item in self.buildings:
                existing_item.active = False

        new_item = None
        if objects.is_turret_type(item_type):
            new_item = objects.Turret(item_type, pixel_pos, (grid_r, grid_c), self.scaler)
            self.turrets.append(new_item)
        elif objects.is_building_type(item_type):
            new_item = objects.Building(item_type, pixel_pos, (grid_r, grid_c), self.scaler)
            self.buildings.append(new_item)

        if new_item:
            self.game_grid[grid_r][grid_c] = new_item
            new_item.update_sprite_based_on_context(self.game_grid, grid_r, grid_c, self.scaler)

            for dr_n, dc_n in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = grid_r + dr_n, grid_c + dc_n
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                    neighbor = self.game_grid[nr][nc]
                    if neighbor and hasattr(neighbor, 'update_sprite_based_on_context'):
                        neighbor.update_sprite_based_on_context(self.game_grid, nr, nc, self.scaler)

            if item_type == "miner" and grid_r + 1 < self.grid_height_tiles:
                item_below = self.game_grid[grid_r + 1][grid_c]
                if item_below and item_below.type == "miner" and hasattr(item_below, 'update_sprite_based_on_context'):
                    item_below.update_sprite_based_on_context(self.game_grid, grid_r + 1, grid_c, self.scaler)

            self.check_and_apply_adjacency_bonus(new_item, grid_r, grid_c)
            if new_item.type == "storage":
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = grid_r + dr, grid_c + dc
                    if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                        neighbor_item = self.game_grid[nr][nc]
                        if neighbor_item and neighbor_item.type == "storage":
                            self.check_and_apply_adjacency_bonus(neighbor_item, nr, nc)

            self.update_resource_production_consumption()
            if cfg.DEBUG_MODE: print(f"Placed {item_type} at ({grid_r},{grid_c})")
        else:
            if cfg.DEBUG_MODE: print(f"ERREUR: Échec de création de l'objet de type {item_type}")
            self.money += item_stats.get(cfg.STAT_COST_MONEY, 0)
            self.iron_stock += item_stats.get(cfg.STAT_COST_IRON, 0)

    def get_placement_requirement_message(self, item_type, existing_item, grid_r, grid_c):
        placement_requirement_met = False
        required_base_type_msg = "Unknown requirement"

        if item_type == "frame":
            if existing_item is None:
                placement_requirement_met = True
            else:
                required_base_type_msg = "Case vide"
        elif item_type in ["generator", "storage", "gatling_turret", "mortar_turret"]:
            if existing_item is not None and existing_item.type == "frame":
                placement_requirement_met = True
            else:
                required_base_type_msg = "'Structure (frame)'"
        elif item_type == "miner":
            if existing_item is None:
                if grid_r + 1 < self.grid_height_tiles:
                    item_below = self.game_grid[grid_r + 1][grid_c]
                    if item_below and (item_below.type == "fundations" or item_below.type == "miner"):
                        placement_requirement_met = True
                    else:
                        required_base_type_msg = "'Fondation renforcée' ou autre 'Mineur' (en dessous)"
                else:
                    required_base_type_msg = "Bord de la grille (nécessite support en dessous)"
            else:
                required_base_type_msg = "Case vide"
        else:
            return False, "Type d'objet inconnu pour placement"
        return placement_requirement_met, required_base_type_msg

    def check_and_apply_adjacency_bonus(self, item, r, c):
        if not item or not hasattr(item, 'apply_adjacency_bonus_effect'): return
        if item.type == "storage":
            adjacent_similar_items_count = 0
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and \
                        self.game_grid[nr][nc] and self.game_grid[nr][nc].type == "storage":
                    adjacent_similar_items_count += 1
            item.apply_adjacency_bonus_effect(adjacent_similar_items_count)

    def try_expand_build_area(self, direction):
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
                for r_idx in range(1, self.grid_height_tiles):
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

            self.update_buildable_area_rect()

            for r_val in range(self.grid_height_tiles):
                for c_val in range(self.grid_width_tiles):
                    item_obj = self.game_grid[r_val][c_val]
                    if item_obj:
                        item_obj.rect.topleft = util.convert_grid_to_pixels((r_val, c_val),
                                                                            (self.buildable_area_rect_pixels.x,
                                                                             self.buildable_area_rect_pixels.y),
                                                                            self.scaler)
                        if hasattr(item_obj, 'update_sprite_based_on_context'):
                            item_obj.update_sprite_based_on_context(self.game_grid, r_val, c_val, self.scaler)

            self.update_resource_production_consumption()
            self.show_error_message("Zone de base étendue!")
            if cfg.DEBUG_MODE: print(f"Expanded grid to {self.grid_width_tiles}x{self.grid_height_tiles}")
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$)")

    def update_resource_production_consumption(self):
        total_electricity_produced = 0
        total_electricity_consumed = 0
        total_iron_storage_increase = 0
        all_constructs = self.buildings + self.turrets

        for item in all_constructs:
            if not item.active: continue
            item_stats = objects.get_item_stats(item.type)
            total_electricity_produced += item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
            total_electricity_consumed += item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0)

            if isinstance(item, objects.Building) and item.type == "storage":
                base_storage = item_stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
                bonus_storage = getattr(item, 'current_adjacency_bonus_value', 0)
                total_iron_storage_increase += (base_storage + bonus_storage)

        is_globally_powered = total_electricity_produced >= total_electricity_consumed
        effective_iron_production_pm = 0

        for item in all_constructs:
            if not item.active: continue
            item_stats = objects.get_item_stats(item.type)

            is_generator = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0) > 0
            is_neutral_power_wise = item.type in ["frame", "fundations", "storage"]
            item_consumes_power_to_function = item_stats.get(cfg.STAT_POWER_CONSUMPTION,
                                                             0) > 0 and not is_generator and not is_neutral_power_wise

            item_is_functionally_powered = True
            if item_consumes_power_to_function and not is_globally_powered:
                item_is_functionally_powered = False

            if hasattr(item, 'set_active_state'):
                item.set_active_state(item_is_functionally_powered)
            elif hasattr(item, 'is_functional'):
                item.is_functional = item_is_functionally_powered

            is_producing_this_tick = False
            if hasattr(item, 'is_functional'):
                is_producing_this_tick = item.is_functional
            elif hasattr(item, 'is_powered'):
                is_producing_this_tick = item.is_powered
            else:
                is_producing_this_tick = item_is_functionally_powered

            if is_producing_this_tick:
                if isinstance(item, objects.Building) and item.type == "miner":
                    effective_iron_production_pm += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)

        self.electricity_produced = total_electricity_produced
        self.electricity_consumed = total_electricity_consumed
        self.iron_production_per_minute = effective_iron_production_pm
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + total_iron_storage_increase

    def update_resources_per_tick(self, delta_time):
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)

    def update_game_logic(self, delta_time):
        if self.game_over_flag or self.game_paused:
            return

        self.total_time_elapsed_seconds += delta_time
        self.update_ui_message_timers(delta_time)
        self.update_timers_and_waves(delta_time)
        self.update_resources_per_tick(delta_time)

        power_available_overall = self.electricity_produced >= self.electricity_consumed

        for turret in self.turrets:
            if turret.active: turret.update(delta_time, self.enemies, power_available_overall, self, self.scaler)
        for building in self.buildings:
            if building.active: building.update(delta_time, self, self.scaler)
        for proj in self.projectiles:
            if proj.active: proj.update(delta_time, self, self.scaler)
        for enemy in self.enemies:
            if enemy.active:
                enemy.update(delta_time, self, self.scaler)
                base_line_x = self.buildable_area_rect_pixels.left
                if enemy.active and enemy.rect.right < base_line_x:
                    self.city_take_damage(enemy.get_city_damage())
                    enemy.active = False
                    if self.city_hp > 0 and cfg.DEBUG_MODE: print(
                        f"Ville touchée par {enemy.type_id}! HP restants: {self.city_hp}")  # Changed enemy.type to enemy.type_id

        for effect in self.particle_effects:
            if effect.active: effect.update(delta_time, self, self.scaler)

        self.handle_collisions()
        self.cleanup_inactive_objects()

        if self.city_hp <= 0 and not self.game_over_flag:
            self.trigger_game_over()

    def city_take_damage(self, amount):
        if self.game_over_flag or amount <= 0: return
        self.city_hp -= amount
        if self.city_hp < 0: self.city_hp = 0

    def handle_collisions(self):
        projectiles_to_remove_after_loop = set()
        enemies_hit_this_frame_by_projectile = {}

        for proj in self.projectiles:
            if not proj.active: continue

            offscreen_buffer = self.scaler.scale_value(cfg.BASE_PROJECTILE_OFFSCREEN_BUFFER)  # Using a config constant
            # Adjusted off-screen check to use usable_area + buffer
            usable_rect_with_buffer = pygame.Rect(
                self.scaler.screen_origin_x - offscreen_buffer,
                self.scaler.screen_origin_y - offscreen_buffer,
                self.scaler.usable_w + 2 * offscreen_buffer,
                self.scaler.usable_h + 2 * offscreen_buffer
            )
            if not usable_rect_with_buffer.colliderect(
                    proj.rect):  # Check if projectile is outside this extended usable area
                projectiles_to_remove_after_loop.add(proj)
                continue

            for enemy in self.enemies:
                if not enemy.active: continue

                is_mortar_shell_impact = hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell and proj.has_impacted
                is_standard_projectile = not (hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell)

                if is_standard_projectile and proj in projectiles_to_remove_after_loop:
                    continue
                if is_standard_projectile and proj.id in enemies_hit_this_frame_by_projectile and \
                        enemy.id in enemies_hit_this_frame_by_projectile[proj.id]:
                    continue

                if proj.rect.colliderect(enemy.hitbox):
                    if not is_mortar_shell_impact:
                        enemy.take_damage(proj.damage)

                    proj.on_hit(self)

                    if is_standard_projectile:
                        projectiles_to_remove_after_loop.add(proj)
                        if proj.id not in enemies_hit_this_frame_by_projectile:
                            enemies_hit_this_frame_by_projectile[proj.id] = set()
                        enemies_hit_this_frame_by_projectile[proj.id].add(enemy.id)

                        if not enemy.active:
                            self.money += enemy.get_money_value()
                            self.score += enemy.get_score_value()
                            self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)
                        break
                    elif not enemy.active and is_mortar_shell_impact:
                        pass

        for proj_to_remove in projectiles_to_remove_after_loop:
            if proj_to_remove in self.projectiles:
                proj_to_remove.active = False

    def trigger_aoe_damage(self, center_pos, scaled_radius, damage):
        if hasattr(objects, 'ParticleEffect'):
            # explosion_effect = objects.ParticleEffect(center_pos, "mortar_explosion", self.scaler)
            # self.particle_effects.append(explosion_effect)
            pass

        radius_sq = scaled_radius ** 2
        for enemy in self.enemies:
            if not enemy.active: continue

            distance_sq = (enemy.hitbox.centerx - center_pos[0]) ** 2 + (enemy.hitbox.centery - center_pos[1]) ** 2
            if distance_sq < radius_sq:
                enemy.take_damage(damage)
                if not enemy.active:
                    self.money += enemy.get_money_value()
                    self.score += enemy.get_score_value()
                    self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)

    def cleanup_inactive_objects(self):
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particle_effects = [eff for eff in self.particle_effects if eff.active]
        self.buildings = [b for b in self.buildings if b.active]
        self.turrets = [t for t in self.turrets if t.active]

    def update_tutorial_specific_logic(self, event):
        if not self.is_tutorial: return
        if cfg.DEBUG_MODE and event.type not in [pygame.MOUSEMOTION, pygame.ACTIVEEVENT]:
            pass

    def update_tutorial_progression(self, delta_time):
        if not self.is_tutorial: return
        pass