# game_functions.py
import pygame
import random
import os
import game_config as cfg
import utility_functions as util
import objects
import ui_functions
import wave_definitions


class GameState:
    # ... (__init__ et la plupart des méthodes inchangées par rapport à votre dernière version) ...
    def __init__(self, scaler: util.Scaler):
        self.scaler = scaler;
        self.screen = None;
        self.clock = None
        self.game_over_flag = False;
        self.game_paused = False;
        self.is_tutorial = False
        self.total_time_elapsed_seconds = 0.0;
        self.time_to_next_wave_seconds = 0.0
        self.current_wave_number = 0;
        self.wave_in_progress = False
        self.enemies_in_current_wave_to_spawn = [];
        self.time_since_last_spawn_in_wave = 0.0
        self.enemies_in_wave_remaining = 0
        self.money = cfg.INITIAL_MONEY;
        self.iron_stock = cfg.INITIAL_IRON
        self.iron_production_per_minute = 0;
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY
        self.electricity_produced = 0;
        self.electricity_consumed = 0
        self.iron_production_per_tick_display = 0.0
        self.city_hp = cfg.INITIAL_CITY_HP;
        self.max_city_hp = cfg.INITIAL_CITY_HP
        self.grid_width_tiles = cfg.BASE_GRID_INITIAL_WIDTH_TILES
        self.grid_height_tiles = cfg.BASE_GRID_INITIAL_HEIGHT_TILES
        self.current_expansion_up_tiles = 0;
        self.current_expansion_sideways_steps = 0
        self.grid_initial_width_tiles = cfg.BASE_GRID_INITIAL_WIDTH_TILES
        self.game_grid = [[None for _ in range(self.grid_width_tiles)] for _ in range(self.grid_height_tiles)]
        self.buildable_area_rect_pixels = pygame.Rect(0, 0, 0, 0)
        self.buildings = [];
        self.turrets = [];
        self.enemies = [];
        self.projectiles = [];
        self.particle_effects = []
        self.selected_item_to_place_type = None;
        self.placement_preview_sprite = None
        self.is_placement_valid_preview = False
        self.ui_icons = {};
        self.last_error_message = "";
        self.error_message_timer = 0.0
        self.tutorial_message = "";
        self.tutorial_message_timer = 0.0;
        self.score = 0
        self.all_wave_definitions = {};
        self.max_waves = 0;
        self.all_waves_completed = False

    def init_new_game(self, screen, clock, is_tutorial=False):
        self.__init__(self.scaler)  # Réinitialise tous les attributs
        self.screen = screen;
        self.clock = clock;
        self.is_tutorial = is_tutorial
        self.load_ui_icons();
        self.update_buildable_area_rect()
        initial_bottom_row_idx = self.grid_height_tiles - 1
        for c in range(self.grid_initial_width_tiles):
            grid_r, grid_c = initial_bottom_row_idx, c
            if 0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles and self.game_grid[grid_r][
                grid_c] is None:
                pixel_pos = util.convert_grid_to_pixels((grid_r, grid_c), (
                self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y), self.scaler)
                try:
                    foundation_obj = objects.Building("foundation", pixel_pos, (grid_r, grid_c), self.scaler)
                    self.game_grid[grid_r][grid_c] = foundation_obj;
                    self.buildings.append(foundation_obj)
                except Exception as e:
                    if cfg.DEBUG_MODE: print(f"ERROR placing initial foundation: {e}")
        if hasattr(wave_definitions, 'load_waves'):
            self.all_wave_definitions = wave_definitions.load_waves()
            self.max_waves = len(self.all_wave_definitions) if self.all_wave_definitions else 0
        else:
            self.all_wave_definitions = {}; self.max_waves = 0; print(
                "AVERTISSEMENT: wave_definitions.load_waves() non trouvé.")
        self.set_time_for_first_wave();
        self.update_resource_production_consumption()
        if cfg.DEBUG_MODE: print(f"GAME_STATE: Initialized for {'TUTORIAL' if self.is_tutorial else 'MAIN GAME'} mode.")

    def load_ui_icons(self):
        money_icon_file = getattr(cfg, 'ICON_FILENAME_MONEY', "icon_money.png")
        iron_icon_file = getattr(cfg, 'ICON_FILENAME_IRON', "icon_iron.png")
        energy_icon_file = getattr(cfg, 'ICON_FILENAME_ENERGY', "icon_energy.png")
        heart_full_file = getattr(cfg, 'ICON_FILENAME_HEART_FULL', "heart_full.png")
        heart_empty_file = getattr(cfg, 'ICON_FILENAME_HEART_EMPTY', "heart_empty.png")  # Garder si utilisé

        self.ui_icons['money'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, money_icon_file))
        self.ui_icons['iron'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, iron_icon_file))
        self.ui_icons['energy'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, energy_icon_file))
        self.ui_icons['heart_full'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, heart_full_file))
        self.ui_icons['heart_empty'] = util.load_sprite(os.path.join(cfg.UI_SPRITE_PATH, heart_empty_file))


    def update_buildable_area_rect(self):
        tile_size = self.scaler.tile_size
        menu_h = self.scaler.ui_build_menu_height
        grid_w_px, grid_h_px = self.grid_width_tiles * tile_size, self.grid_height_tiles * tile_size
        start_x = self.scaler.screen_origin_x + self.scaler.scaled_grid_offset_x
        grid_bottom_abs = self.scaler.screen_origin_y + self.scaler.usable_h - menu_h
        start_y = grid_bottom_abs - grid_h_px
        self.buildable_area_rect_pixels = pygame.Rect(start_x, start_y, grid_w_px, grid_h_px)

    def draw_game_world(self):
        self.screen.fill(cfg.COLOR_BACKGROUND)
        if cfg.DEBUG_MODE:
            usable_rect = self.scaler.get_usable_rect()
            debug_surf = pygame.Surface(usable_rect.size, pygame.SRCALPHA)
            debug_surf.fill((50, 0, 0, 30));
            self.screen.blit(debug_surf, usable_rect.topleft)
            pygame.draw.rect(self.screen, (255, 0, 0, 100), usable_rect, 1)

        ui_functions.draw_base_grid(self.screen, self, self.scaler)

        buildings_to_draw = sorted([b for b in self.buildings if b.active and hasattr(b, 'rect')],
                                   key=lambda o: o.rect.bottom)
        for building in buildings_to_draw:
            building.draw(self.screen)
            if cfg.DEBUG_MODE: util.draw_debug_rect(self.screen, building.rect, cfg.COLOR_BLUE, 1)

        turrets_to_draw = sorted([t for t in self.turrets if t.active and hasattr(t, 'rect')],
                                 key=lambda o: o.rect.bottom)
        for turret in turrets_to_draw:
            turret.draw(self.screen)
            if cfg.DEBUG_MODE: util.draw_debug_rect(self.screen, turret.rect, cfg.COLOR_CYAN, 1)

        other_objects = []
        for lst_attr in ['enemies', 'projectiles', 'particle_effects']:
            for obj in getattr(self, lst_attr, []):
                if obj and obj.active and hasattr(obj, 'rect'): other_objects.append(obj)
        other_objects.sort(key=lambda o: o.rect.bottom)
        for obj in other_objects:
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
            if self.last_error_message and self.error_message_timer > 0: ui_functions.draw_error_message(self.screen,
                                                                                                         self.last_error_message,
                                                                                                         self,
                                                                                                         self.scaler)
            if self.tutorial_message and self.tutorial_message_timer > 0: ui_functions.draw_tutorial_message(
                self.screen, self.tutorial_message, self, self.scaler)
        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen, self.scaler)
        elif self.game_over_flag:
            ui_functions.draw_game_over_screen(self.screen, self.score, self.scaler)

    def get_reinforced_row_index(self):
        return self.current_expansion_up_tiles + (cfg.BASE_GRID_INITIAL_HEIGHT_TILES - 1)

    def set_time_for_first_wave(self):
        self.time_to_next_wave_seconds = cfg.WAVE_INITIAL_PREP_TIME_SEC; self.current_wave_number = 0

    def toggle_pause(self):
        self.game_paused = not self.game_paused; print(f"Game Paused: {self.game_paused}")

    def trigger_game_over(self):
        if not self.game_over_flag: self.game_over_flag = True; print("GAME_STATE: Game Over triggered.")

    def show_error_message(self, msg, dur=2.5):
        self.last_error_message = msg; self.error_message_timer = dur

    def show_tutorial_message(self, msg, dur=5.0):
        self.tutorial_message = msg; self.tutorial_message_timer = dur

    def update_ui_message_timers(self, dt):
        if self.error_message_timer > 0: self.error_message_timer -= dt;
        if self.error_message_timer <= 0: self.last_error_message = ""
        if self.tutorial_message_timer > 0: self.tutorial_message_timer -= dt;
        if self.tutorial_message_timer <= 0: self.tutorial_message = ""

    def update_timers_and_waves(self, delta_time):
        if self.game_over_flag or self.game_paused or self.all_waves_completed:
            if self.all_waves_completed and not self.enemies and not self.wave_in_progress: pass
            return
        if not self.wave_in_progress:
            self.time_to_next_wave_seconds -= delta_time
            if self.time_to_next_wave_seconds <= 0: self.start_next_wave()
        else:
            self.time_since_last_spawn_in_wave += delta_time
            if self.enemies_in_current_wave_to_spawn:
                delay_needed, enemy_type_id, enemy_variant = self.enemies_in_current_wave_to_spawn[0]
                if self.time_since_last_spawn_in_wave >= delay_needed:
                    self.spawn_enemy(enemy_type_id, enemy_variant)
                    self.enemies_in_current_wave_to_spawn.pop(0);
                    self.time_since_last_spawn_in_wave = 0
            elif not self.enemies:
                self.wave_in_progress = False;
                self.enemies_in_wave_remaining = 0
                if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                    self.all_waves_completed = True;
                    print("TOUTES LES VAGUES TERMINÉES!")
                else:
                    self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC

    def start_next_wave(self):
        self.current_wave_number += 1
        if self.current_wave_number > self.max_waves and self.max_waves > 0:
            self.wave_in_progress = False;
            self.all_waves_completed = True;
            print("Fin des vagues.");
            return
        print(f"Starting Wave {self.current_wave_number}")
        self.wave_in_progress = True
        self.enemies_in_current_wave_to_spawn = list(self.all_wave_definitions.get(self.current_wave_number, []))
        self.enemies_in_wave_remaining = len(self.enemies_in_current_wave_to_spawn)
        self.time_since_last_spawn_in_wave = 0.0
        if not self.enemies_in_current_wave_to_spawn:
            self.wave_in_progress = False;
            self.enemies_in_wave_remaining = 0
            if self.current_wave_number >= self.max_waves and self.max_waves > 0:
                self.all_waves_completed = True
            else:
                self.time_to_next_wave_seconds = cfg.WAVE_TIME_BETWEEN_WAVES_SEC

    def spawn_enemy(self, enemy_type_id, variant_data=None):
        game_area_top_y = self.scaler.screen_origin_y + self.scaler.ui_top_bar_height
        game_area_bottom_y = self.scaler.screen_origin_y + self.scaler.usable_h - self.scaler.ui_build_menu_height
        game_h = game_area_bottom_y - game_area_top_y
        spawn_y = game_area_top_y + game_h // 2
        if game_h > self.scaler.scale_value(cfg.BASE_ENEMY_SPAWN_Y_PADDING) * 2:
            min_y_off = int(game_h * cfg.ENEMY_SPAWN_MIN_Y_PERCENTAGE)
            max_y_off = int(game_h * cfg.ENEMY_SPAWN_MAX_Y_PERCENTAGE)
            actual_min_y = game_area_top_y + min_y_off + self.scaler.scale_value(cfg.BASE_ENEMY_SPAWN_Y_PADDING)
            actual_max_y = game_area_top_y + max_y_off - self.scaler.scale_value(cfg.BASE_ENEMY_SPAWN_Y_PADDING)
            if actual_min_y < actual_max_y:
                spawn_y = random.randint(actual_min_y, actual_max_y)
            elif cfg.DEBUG_MODE:
                print(f"WARN: Spawn Y range invalid after padding. Min:{actual_min_y}, Max:{actual_max_y}")
        elif cfg.DEBUG_MODE:
            print("WARN: Game area height too small for spawn padding.")
        spawn_x = self.scaler.screen_origin_x + self.scaler.usable_w + self.scaler.scale_value(
            cfg.BASE_ENEMY_SPAWN_X_OFFSET)
        new_enemy = objects.Enemy((spawn_x, spawn_y), enemy_type_id, variant_data, self.scaler)
        self.enemies.append(new_enemy)

    def handle_player_input(self, event, mouse_pos_pixels):
        if self.game_over_flag or self.game_paused: return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_item = ui_functions.check_build_menu_click(self, mouse_pos_pixels, self.scaler)
                if clicked_item:
                    if clicked_item.startswith("expand_"):
                        self.try_expand_build_area(clicked_item.split("_")[1]);
                        self.selected_item_to_place_type = None;
                        self.placement_preview_sprite = None
                    else:
                        self.selected_item_to_place_type = clicked_item
                        item_stats = objects.get_item_stats(clicked_item)
                        s_name, p_prefix = None, None
                        if objects.is_building_type(clicked_item):
                            p_prefix = cfg.BUILDING_SPRITE_PATH
                            if clicked_item == "miner" and cfg.STAT_SPRITE_VARIANTS_DICT in item_stats: s_name = \
                            item_stats[cfg.STAT_SPRITE_VARIANTS_DICT].get("single")
                            if not s_name: s_name = item_stats.get(cfg.STAT_SPRITE_DEFAULT_NAME)
                        elif objects.is_turret_type(clicked_item):
                            p_prefix = cfg.TURRET_SPRITE_PATH;
                            s_name = item_stats.get(cfg.STAT_TURRET_BASE_SPRITE_NAME)
                        if s_name and p_prefix:
                            self.placement_preview_sprite = util.load_sprite(os.path.join(p_prefix, s_name))
                        else:
                            self.placement_preview_sprite = None
                    return
                elif self.selected_item_to_place_type:
                    self.try_place_item_on_grid(mouse_pos_pixels)
            elif event.button == 3:
                self.selected_item_to_place_type = None; self.placement_preview_sprite = None
        if self.selected_item_to_place_type:
            is_valid, _, _ = self.check_placement_validity(self.selected_item_to_place_type, mouse_pos_pixels)
            self.is_placement_valid_preview = is_valid
        else:
            self.is_placement_valid_preview = False

    def check_placement_validity(self, item_type_to_place, mouse_pixel_pos):
        grid_r, grid_c = util.convert_pixels_to_grid(mouse_pixel_pos, (
        self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y), self.scaler)
        if not (0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles): return False, (
        grid_r, grid_c), "Hors de la zone."

        item_on_grid = self.game_grid[grid_r][grid_c]
        item_below = self.game_grid[grid_r + 1][grid_c] if grid_r + 1 < self.grid_height_tiles else None
        stats_to_place = objects.get_item_stats(item_type_to_place)
        placement_requirement_met = False
        error_message = "Placement non autorisé."

        if item_type_to_place == "frame":
            can_place_on_empty_with_support = False
            is_first_row_on_empty_grid_part = (
                        item_on_grid is None and item_below is None and grid_r == self.grid_height_tiles - 1)

            if item_on_grid is None:
                if is_first_row_on_empty_grid_part:
                    can_place_on_empty_with_support = True
                elif item_below and isinstance(item_below, objects.Building) and \
                        (item_below.type == "frame" or item_below.type == "miner" or \
                         item_below.type == "generator" or item_below.type == "storage"):
                    can_place_on_empty_with_support = True

            can_replace_foundation = False
            if item_on_grid and isinstance(item_on_grid, objects.Building) and \
                    item_on_grid.type == "foundation" and getattr(item_on_grid, 'is_reinforced_foundation', False):
                can_replace_foundation = True

            if can_place_on_empty_with_support or can_replace_foundation:
                placement_requirement_met = True
            elif item_on_grid is not None and not can_replace_foundation:
                error_message = "Case non vide (et non remplaçable par frame)."
            elif item_on_grid is None and not can_place_on_empty_with_support:
                error_message = "Structure nécessite autre structure en dessous (ou 1ère rangée)."

        elif item_type_to_place == "miner":
            error_message = "Mine: condition non remplie."
            if item_on_grid and isinstance(item_on_grid, objects.Building) and \
                    item_on_grid.type == "frame" and getattr(item_on_grid, 'is_reinforced_frame', False):
                placement_requirement_met = True
            elif item_on_grid is None and item_below and isinstance(item_below,
                                                                    objects.Building) and item_below.type == "miner":
                placement_requirement_met = True

            if not placement_requirement_met:
                if item_on_grid is None and not (
                        item_below and isinstance(item_below, objects.Building) and item_below.type == "miner"):
                    error_message = "Mine sur case vide nécessite autre mine en dessous."
                elif item_on_grid and not (
                        isinstance(item_on_grid, objects.Building) and item_on_grid.type == "frame" and getattr(
                        item_on_grid, 'is_reinforced_frame', False)):
                    error_message = "Mine doit être sur une frame renforcée (si case occupée)."
                else:
                    error_message = "Mine sur frame renforcée OU au-dessus d'une autre mine."

        elif objects.is_turret_type(item_type_to_place):
            if item_on_grid and isinstance(item_on_grid, objects.Building) and item_on_grid.type == "frame":
                already_has_turret_at_pos = any(
                    turret.grid_pos == (grid_r, grid_c) for turret in self.turrets if turret.active)
                if not already_has_turret_at_pos:
                    placement_requirement_met = True
                else:
                    error_message = "Une tourelle existe déjà sur cette structure."
            else:
                error_message = "Tourelle doit être placée sur une structure (frame)."
        elif item_type_to_place in ["generator", "storage"]:
            if item_on_grid and isinstance(item_on_grid, objects.Building) and item_on_grid.type == "frame":
                placement_requirement_met = True
            else:
                error_message = f"{item_type_to_place.capitalize()} doit remplacer une structure (frame)."
        else:
            error_message = f"Type d'objet inconnu pour placement: {item_type_to_place}"

        if not placement_requirement_met: return False, (grid_r, grid_c), error_message

        cost_money = stats_to_place.get(cfg.STAT_COST_MONEY, 0);
        # cost_iron = stats_to_place.get(cfg.STAT_COST_IRON, 0) # Iron cost for building is removed
        if self.money < cost_money: return False, (grid_r, grid_c), f"Pas assez d'argent (${cost_money})"
        # if self.iron_stock < cost_iron: return False, (grid_r, grid_c), f"Pas assez de fer ({cost_iron} Fe)" # MODIFIED: Removed iron check for placement

        power_prod_impact = stats_to_place.get(cfg.STAT_POWER_PRODUCTION, 0);
        power_conso_impact = stats_to_place.get(cfg.STAT_POWER_CONSUMPTION, 0)
        if power_conso_impact > 0 and power_prod_impact == 0 and item_type_to_place != "storage":
            if self.electricity_produced < (self.electricity_consumed + power_conso_impact):
                return False, (grid_r, grid_c), "Pas assez d'énergie!"
        return True, (grid_r, grid_c), "OK"

    def try_place_item_on_grid(self, mouse_pixel_pos):
        item_type_to_place = self.selected_item_to_place_type;
        if not item_type_to_place: return
        is_valid, (grid_r, grid_c), error_msg_placement = self.check_placement_validity(item_type_to_place,
                                                                                        mouse_pixel_pos)
        if not is_valid:
            self.show_error_message(error_msg_placement)
            if cfg.DEBUG_MODE: print(
                f"Placement invalide pour {item_type_to_place} à ({grid_r},{grid_c}): {error_msg_placement}")
            return
        stats_to_place = objects.get_item_stats(item_type_to_place)
        self.money -= stats_to_place.get(cfg.STAT_COST_MONEY, 0);
        # self.iron_stock -= stats_to_place.get(cfg.STAT_COST_IRON, 0) # MODIFIED: Removed iron deduction for placement

        pixel_pos_for_new_item = util.convert_grid_to_pixels((grid_r, grid_c), (
        self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y), self.scaler)
        if objects.is_turret_type(item_type_to_place):
            tile_center_x = self.buildable_area_rect_pixels.x + grid_c * self.scaler.tile_size + self.scaler.tile_size // 2
            tile_center_y = self.buildable_area_rect_pixels.y + grid_r * self.scaler.tile_size + self.scaler.tile_size // 2
            pixel_pos_for_new_item = (tile_center_x, tile_center_y)
        item_on_grid_before_placement = self.game_grid[grid_r][grid_c]
        newly_created_item = None

        if item_type_to_place == "frame":
            newly_created_item = objects.Building(item_type_to_place, pixel_pos_for_new_item, (grid_r, grid_c),
                                                  self.scaler)
            self.buildings.append(newly_created_item)
            if item_on_grid_before_placement and isinstance(item_on_grid_before_placement, objects.Building) and \
                    item_on_grid_before_placement.type == "foundation" and getattr(item_on_grid_before_placement,
                                                                                   'is_reinforced_foundation', False):
                newly_created_item.set_as_reinforced_frame(True)
                if item_on_grid_before_placement in self.buildings: item_on_grid_before_placement.active = False
            else:
                newly_created_item.set_as_reinforced_frame(False)
            self.game_grid[grid_r][grid_c] = newly_created_item

        elif objects.is_turret_type(item_type_to_place):
            newly_created_item = objects.Turret(item_type_to_place, pixel_pos_for_new_item, (grid_r, grid_c),
                                                self.scaler)
            self.turrets.append(newly_created_item)
            if item_on_grid_before_placement and isinstance(item_on_grid_before_placement,
                                                            objects.Building) and item_on_grid_before_placement.type == "frame":
                item_on_grid_before_placement.set_as_turret_platform(True)

        elif item_type_to_place == "miner":
            newly_created_item = objects.Building(item_type_to_place, pixel_pos_for_new_item, (grid_r, grid_c),
                                                  self.scaler)
            self.buildings.append(newly_created_item)
            if item_on_grid_before_placement and isinstance(item_on_grid_before_placement, objects.Building) and \
                    item_on_grid_before_placement.type == "frame":
                item_on_grid_before_placement.active = False
                if cfg.DEBUG_MODE: print(f"Frame à ({grid_r},{grid_c}) remplacée par un mineur.")
            self.game_grid[grid_r][grid_c] = newly_created_item

        elif item_type_to_place in ["generator", "storage"]:
            newly_created_item = objects.Building(item_type_to_place, pixel_pos_for_new_item, (grid_r, grid_c),
                                                  self.scaler)
            self.buildings.append(newly_created_item)
            if item_on_grid_before_placement and isinstance(item_on_grid_before_placement,
                                                            objects.Building) and item_on_grid_before_placement.type == "frame":
                item_on_grid_before_placement.active = False
            self.game_grid[grid_r][grid_c] = newly_created_item

        if newly_created_item:
            if hasattr(newly_created_item,
                       'update_sprite_based_on_context'): newly_created_item.update_sprite_based_on_context(
                self.game_grid, grid_r, grid_c, self.scaler)
            for dr_n, dc_n in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = grid_r + dr_n, grid_c + dc_n
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                    neighbor = self.game_grid[nr][nc]
                    if neighbor and hasattr(neighbor,
                                            'update_sprite_based_on_context'): neighbor.update_sprite_based_on_context(
                        self.game_grid, nr, nc, self.scaler)
            if hasattr(newly_created_item, 'apply_adjacency_bonus_effect'):
                self.check_and_apply_adjacency_bonus(newly_created_item, grid_r, grid_c)
                if newly_created_item.type == "storage":
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = grid_r + dr, grid_c + dc
                        if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                            neighbor_item = self.game_grid[nr][nc]
                            if neighbor_item and neighbor_item.type == "storage": self.check_and_apply_adjacency_bonus(
                                neighbor_item, nr, nc)
            self.update_resource_production_consumption()
            if cfg.DEBUG_MODE: print(f"Placed {item_type_to_place} at ({grid_r},{grid_c})")
        else:
            if cfg.DEBUG_MODE: print(f"ERREUR: Échec de création de l'objet {item_type_to_place} après validation.")
            self.money += stats_to_place.get(cfg.STAT_COST_MONEY, 0);
            # self.iron_stock += stats_to_place.get(cfg.STAT_COST_IRON, 0) # MODIFIED: Removed iron refund

    def get_placement_requirement_message(self, item_type, existing_item_on_grid, grid_r_coord, grid_c_coord):
        _, _, msg = self.check_placement_validity(item_type, util.convert_grid_to_pixels((grid_r_coord, grid_c_coord), (
        self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y), self.scaler))
        return msg != "OK", msg

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
        if cost_expansion == "Max": self.show_error_message("Expansion max atteinte."); return
        if not isinstance(cost_expansion, (int, float)) or cost_expansion <= 0: self.show_error_message(
            "Coût d'expansion invalide."); return
        if self.money >= cost_expansion:
            self.money -= cost_expansion
            if direction == "up":
                self.current_expansion_up_tiles += 1;
                new_row = [None for _ in range(self.grid_width_tiles)];
                self.game_grid.insert(0, new_row);
                self.grid_height_tiles += 1
                for r_idx in range(1, self.grid_height_tiles):
                    for c_idx in range(self.grid_width_tiles):
                        item_obj = self.game_grid[r_idx][c_idx]
                        if item_obj: item_obj.grid_pos = (item_obj.grid_pos[0] + 1, item_obj.grid_pos[1])
            elif direction == "side":
                self.current_expansion_sideways_steps += 1;
                tiles_to_add = cfg.BASE_GRID_EXPANSION_SIDEWAYS_TILES_PER_STEP
                for r_idx in range(self.grid_height_tiles): self.game_grid[r_idx].extend(
                    [None for _ in range(tiles_to_add)])
                self.grid_width_tiles += tiles_to_add
            self.update_buildable_area_rect()
            for r_val in range(self.grid_height_tiles):
                for c_val in range(self.grid_width_tiles):
                    item_obj = self.game_grid[r_val][c_val]
                    if item_obj:
                        item_obj.rect.topleft = util.convert_grid_to_pixels((r_val, c_val), (
                        self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y), self.scaler)
                        if hasattr(item_obj, 'update_sprite_based_on_context'): item_obj.update_sprite_based_on_context(
                            self.game_grid, r_val, c_val, self.scaler)
            self.update_resource_production_consumption();
            self.show_error_message("Zone de base étendue!")
            if cfg.DEBUG_MODE: print(f"Expanded grid to {self.grid_width_tiles}x{self.grid_height_tiles}")
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$)")

    def update_resource_production_consumption(self):
        total_electricity_produced, total_electricity_consumed, total_iron_storage_increase = 0, 0, 0
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
            is_neutral_power = item.type in ["frame", "foundation", "storage"]
            consumes_power_to_function = item_stats.get(cfg.STAT_POWER_CONSUMPTION,
                                                        0) > 0 and not is_generator and not is_neutral_power
            item_is_functionally_powered = True
            if consumes_power_to_function and not is_globally_powered: item_is_functionally_powered = False
            if hasattr(item, 'set_active_state'): item.set_active_state(item_is_functionally_powered)
            if item_is_functionally_powered and isinstance(item, objects.Building) and item.type == "miner":
                effective_iron_production_pm += item_stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
        self.electricity_produced = total_electricity_produced
        self.electricity_consumed = total_electricity_consumed
        self.iron_production_per_minute = effective_iron_production_pm
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + total_iron_storage_increase
        self.iron_production_per_tick_display = self.iron_production_per_minute / 60.0

    def update_resources_per_tick(self, delta_time):
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)

    def update_game_logic(self, delta_time):
        if self.game_over_flag or self.game_paused: return
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
                        f"Ville touchée par {getattr(enemy, 'type_id', 'unknown')}! HP restants: {self.city_hp}")
        for effect in self.particle_effects:
            if effect.active: effect.update(delta_time, self, self.scaler)
        self.handle_collisions();
        self.cleanup_inactive_objects()
        if self.city_hp <= 0 and not self.game_over_flag: self.trigger_game_over()

    def city_take_damage(self, amount):
        if self.game_over_flag or amount <= 0: return
        self.city_hp -= amount
        if self.city_hp < 0: self.city_hp = 0

    def handle_collisions(self):
        projectiles_to_remove_after_loop, enemies_hit_this_frame_by_projectile = set(), {}
        for proj in self.projectiles:
            if not proj.active: continue
            for enemy in self.enemies:
                if not enemy.active: continue
                is_mortar_shell_impact = hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell and getattr(proj,
                                                                                                               'has_impacted',
                                                                                                               False)
                is_standard_projectile = not (hasattr(proj, 'is_mortar_shell') and proj.is_mortar_shell)
                if proj.type == "machine_gun_beam": continue
                if is_standard_projectile and proj in projectiles_to_remove_after_loop: continue
                if is_standard_projectile and proj.id in enemies_hit_this_frame_by_projectile and enemy.id in \
                        enemies_hit_this_frame_by_projectile[proj.id]: continue
                if proj.rect.colliderect(enemy.hitbox):
                    if not is_mortar_shell_impact: enemy.take_damage(proj.damage)
                    proj.on_hit(self)
                    if is_standard_projectile:
                        projectiles_to_remove_after_loop.add(proj)
                        if proj.id not in enemies_hit_this_frame_by_projectile: enemies_hit_this_frame_by_projectile[
                            proj.id] = set()
                        enemies_hit_this_frame_by_projectile[proj.id].add(enemy.id)
                        if not enemy.active:
                            self.money += enemy.get_money_value();
                            self.score += enemy.get_score_value()
                            self.enemies_in_wave_remaining = max(0, self.enemies_in_wave_remaining - 1)
                        break
        for proj_to_remove in projectiles_to_remove_after_loop:
            if proj_to_remove in self.projectiles: proj_to_remove.active = False

    def trigger_aoe_damage(self, center_pos, scaled_radius, damage):
        radius_sq = scaled_radius ** 2
        for enemy in self.enemies:
            if not enemy.active: continue
            distance_sq = (enemy.hitbox.centerx - center_pos[0]) ** 2 + (enemy.hitbox.centery - center_pos[1]) ** 2
            if distance_sq < radius_sq:
                enemy.take_damage(damage)
                if not enemy.active:
                    self.money += enemy.get_money_value();
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
        if cfg.DEBUG_MODE and event.type not in [pygame.MOUSEMOTION, pygame.ACTIVEEVENT]: pass

    def update_tutorial_progression(self, delta_time):
        if not self.is_tutorial: return
        pass

    def get_next_expansion_cost(self, direction):
        if direction == "up":
            if self.current_expansion_up_tiles >= cfg.BASE_GRID_MAX_EXPANSION_UP_TILES: return "Max"
            return int(
                cfg.BASE_EXPANSION_COST_UP * (cfg.EXPANSION_COST_INCREASE_FACTOR_UP ** self.current_expansion_up_tiles))
        elif direction == "side":
            if self.current_expansion_sideways_steps >= cfg.BASE_GRID_MAX_EXPANSION_SIDEWAYS_STEPS: return "Max"
            return int(cfg.BASE_EXPANSION_COST_SIDE * (
                        cfg.EXPANSION_COST_INCREASE_FACTOR_SIDE ** self.current_expansion_sideways_steps))
        return "N/A"