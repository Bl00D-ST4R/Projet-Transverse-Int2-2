# game_functions.py
import pygame
import random # random was in the original full version, might not be needed in simplified
import game_config as cfg
import utility_functions as util
import objects
import ui_functions
# import wave_definitions # Not strictly needed for the simplified UI test

class GameState:
    """Classe pour encapsuler l'état global du jeu pour un accès facile. (Simplified)"""
    def __init__(self, scaler: util.Scaler):
        self.scaler = scaler
        self.screen = None # Will be set by main.py
        self.clock = None  # Will be set by main.py
        
        # Simplified attributes for UI testing
        self.money = cfg.INITIAL_MONEY # Example, for top bar display
        self.iron_stock = cfg.INITIAL_IRON # Example
        self.iron_production_per_minute = 0 # Example
        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY # Example
        self.electricity_produced = 0 # Example
        self.electricity_consumed = 0 # Example
        self.city_hp = cfg.INITIAL_CITY_HP # Example
        self.max_city_hp = cfg.INITIAL_CITY_HP # Example
        self.current_wave_number = 0 # Example
        self.time_to_next_wave_seconds = 0.0 # Example
        self.wave_in_progress = False # Example
        self.game_over_flag = False # Example
        self.all_waves_completed = False # Example
        self.score = 0 # Example

        self.grid_width_tiles = cfg.BASE_GRID_INITIAL_WIDTH_TILES
        self.grid_height_tiles = cfg.BASE_GRID_INITIAL_HEIGHT_TILES
        self.current_expansion_up_tiles = 0 # Needed for get_reinforced_row_index if draw_base_grid uses it
        self.grid_initial_width_tiles = cfg.BASE_GRID_INITIAL_WIDTH_TILES # Needed for get_reinforced_row_index

        self.buildable_area_rect_pixels = pygame.Rect(0,0,0,0)
        self.game_grid = [[None for _ in range(self.grid_width_tiles)] for _ in range(self.grid_height_tiles)]
        
        self.selected_item_to_place_type = None # For build menu interaction
        self.placement_preview_sprite = None
        self.is_placement_valid_preview = False
        self.ui_icons = {} # Assurez-vous que ui_icons est initialisé ici
        self.buildings = [] # For initial foundations

        # For error/tutorial messages if draw_game_ui_elements uses them
        self.last_error_message = ""
        self.error_message_timer = 0.0
        self.tutorial_message = ""
        self.tutorial_message_timer = 0.0
        self.game_paused = False # For pause screen

    # AJOUTER CETTE MÉTHODE SI ELLE MANQUE OU LA CORRIGER :
    def load_ui_icons(self):
        """Charge les sprites originaux pour les icônes UI. Le scaling se fait au dessin."""
        if cfg.DEBUG_MODE: print("GameState DEBUG: Chargement des icônes UI...")
        try:
            self.ui_icons['money'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_money.png")
            self.ui_icons['iron'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_iron.png")
            self.ui_icons['energy'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_energy.png")
            self.ui_icons['heart_full'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_full.png")
            self.ui_icons['heart_empty'] = util.load_sprite(cfg.UI_SPRITE_PATH + "heart_empty.png")
            # Ajoutez d'autres icônes ici si nécessaire pour le build menu, etc.
            # Exemple:
            # self.ui_icons['icon_frame'] = util.load_sprite(cfg.UI_SPRITE_PATH + "icon_frame.png")
            if cfg.DEBUG_MODE: print(f"  money icon loaded: {isinstance(self.ui_icons.get('money'), pygame.Surface)}")
        except Exception as e:
            if cfg.DEBUG_MODE: print(f"ERREUR lors du chargement des icônes UI: {e}")

    def init_new_game(self, screen, clock):
        self.__init__(self.scaler) # Re-initialize with the existing scaler
        self.screen = screen
        self.clock = clock
        self.load_ui_icons() # CET APPEL EST CORRECT
        self.update_buildable_area_rect() # CRUCIAL: Call after scaler is set and screen known

        # Place initial "fundations" (simplified for now, just to see them)
        initial_bottom_row = cfg.BASE_GRID_INITIAL_HEIGHT_TILES - 1
        for c in range(cfg.BASE_GRID_INITIAL_WIDTH_TILES):
            grid_r, grid_c = initial_bottom_row, c
            if 0 <= grid_r < self.grid_height_tiles and 0 <= grid_c < self.grid_width_tiles:
                if self.game_grid[grid_r][grid_c] is None:
                    pixel_pos = util.convert_grid_to_pixels(
                        (grid_r, grid_c),
                        (self.buildable_area_rect_pixels.x, self.buildable_area_rect_pixels.y),
                        self.scaler
                    )
                    # Assuming "fundations" type and object exist for this test
                    try:
                        # Ensure objects.Building and "fundations" type are defined
                        # and can be instantiated for this to work.
                        if hasattr(objects, 'Building'):
                            fundation_obj = objects.Building("fundations", pixel_pos, (grid_r, grid_c), self.scaler)
                            self.game_grid[grid_r][grid_c] = fundation_obj
                            self.buildings.append(fundation_obj)
                        else:
                             if cfg.DEBUG_MODE: print(f"Warning: objects.Building class not found for initial fundation.")
                    except Exception as e:
                        if cfg.DEBUG_MODE: print(f"Error placing initial fundation for test: {e}")

    def update_buildable_area_rect(self):
        tile_size = self.scaler.tile_size
        ui_menu_height_bottom = self.scaler.ui_build_menu_height

        current_grid_pixel_width = self.grid_width_tiles * tile_size
        current_grid_pixel_height = self.grid_height_tiles * tile_size

        # Y position of the TOP of the grid, such that its BOTTOM is just above the bottom UI
        dynamic_grid_offset_y = self.scaler.actual_h - ui_menu_height_bottom - current_grid_pixel_height
        grid_offset_x_runtime = self.scaler.grid_offset_x # Should be 0

        self.buildable_area_rect_pixels = pygame.Rect(
            grid_offset_x_runtime,
            dynamic_grid_offset_y,
            current_grid_pixel_width,
            current_grid_pixel_height
        )
        if cfg.DEBUG_MODE:
            print(f"GS DEBUG: Buildable Area: {self.buildable_area_rect_pixels}")
            print(f"  Grid TopY={dynamic_grid_offset_y}, Grid H={current_grid_pixel_height}, Grid Bottom={dynamic_grid_offset_y + current_grid_pixel_height}")
            print(f"  Screen H={self.scaler.actual_h}, BottomMenuH={ui_menu_height_bottom}, Top of BottomMenu={self.scaler.actual_h - ui_menu_height_bottom}")
    
    # Keep get_reinforced_row_index if draw_base_grid still uses it for coloring
    def get_reinforced_row_index(self):
        return self.current_expansion_up_tiles + (cfg.BASE_GRID_INITIAL_HEIGHT_TILES - 1)

    def draw_game_world(self):
        """Dessine le fond et les éléments du monde du jeu (grille, bâtiments)."""
        self.screen.fill(cfg.COLOR_BACKGROUND) # Fill with game background color

        # Dessiner la grille
        ui_functions.draw_base_grid(self.screen, self, self.scaler)

        # Dessiner les bâtiments (initial foundations for now)
        # Sorting by bottom y for pseudo-3D not critical for this UI fix
        for building in self.buildings:
            if hasattr(building, 'active') and building.active: # Ensure building is active and has draw method
                if hasattr(building, 'draw'):
                    building.draw(self.screen) 
                else:
                    if cfg.DEBUG_MODE: print(f"Warning: Building {building} has no draw method.")
            elif not hasattr(building, 'active') and hasattr(building, 'draw'): # If no active attribute, assume drawable
                building.draw(self.screen)


        # Dessiner la preview de placement (draw_placement_preview)
        # This needs selected_item_to_place_type, placement_preview_sprite, buildable_area_rect_pixels,
        # grid_height_tiles, grid_width_tiles, is_placement_valid_preview to be correctly set/updated
        # by a simplified handle_player_input or other logic if interaction is tested.
        # For a pure drawing test without interaction, this might not show anything unless these are pre-set.
        ui_functions.draw_placement_preview(self.screen, self, self.scaler)


    def draw_game_ui_elements(self):
        """Dessine les éléments UI statiques (barres) et modaux (pause/game over)."""
        # Ces fonctions vont dessiner DIRECTEMENT sur self.screen
        ui_functions.draw_top_bar_ui(self.screen, self, self.scaler)
        ui_functions.draw_build_menu_ui(self.screen, self, self.scaler)

        # Dessiner les messages (erreur, tutoriel)
        if self.last_error_message and self.error_message_timer > 0:
             ui_functions.draw_error_message(self.screen, self.last_error_message, self, self.scaler)
        if self.tutorial_message and self.tutorial_message_timer > 0:
            ui_functions.draw_tutorial_message(self.screen, self.tutorial_message, self, self.scaler)
        
        # Dessiner les écrans modaux (pause, game over) par-dessus si actifs
        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen, self.scaler)
        elif self.game_over_flag:
            ui_functions.draw_game_over_screen(self.screen, self.score, self.scaler)

    # Stubbed methods
    def update_game_logic(self, delta_time): # Stub for now
        if self.game_paused or self.game_over_flag: return
        
        # Minimal timer updates for error/tutorial messages if they are to be tested
        if self.error_message_timer > 0:
            self.error_message_timer -= delta_time
            if self.error_message_timer <= 0: self.last_error_message = ""
        if self.tutorial_message_timer > 0:
            self.tutorial_message_timer -= delta_time
            if self.tutorial_message_timer <=0: self.tutorial_message = ""
        pass

    def handle_player_input(self, event, mouse_pos): # Stub for now
        # If you want to test build menu interaction and placement preview,
        # a simplified version of the original handle_player_input's
        # selection logic would be needed here to set:
        # self.selected_item_to_place_type
        # self.placement_preview_sprite
        # self.is_placement_valid_preview
        pass

    def toggle_pause(self): # Keep for testing pause screen
        self.game_paused = not self.game_paused
        if cfg.DEBUG_MODE: print(f"Game Paused: {self.game_paused}")

    # Minimal function for error messages to be testable with draw_game_ui_elements
    def show_error_message(self, message, duration=2.5):
        self.last_error_message = message
        self.error_message_timer = duration

    def show_tutorial_message(self, message, duration=5.0):
        self.tutorial_message = message
        self.tutorial_message_timer = duration

    # Other methods from the original GameState are removed for this simplified version.
    # Methods like update_timers_and_waves, resource updates, enemy spawning,
    # collisions, expansions, etc., are not part of this UI-focused test.
    
    # Minimal get_next_expansion_cost to prevent errors if ui_functions.draw_build_menu_ui calls it
    def get_next_expansion_cost(self, direction):
        if direction == "up":
            return int(cfg.BASE_EXPANSION_COST_UP * (cfg.EXPANSION_COST_INCREASE_FACTOR_UP ** getattr(self, 'current_expansion_up_tiles', 0)))
        elif direction == "side":
            return int(cfg.BASE_EXPANSION_COST_SIDE * (cfg.EXPANSION_COST_INCREASE_FACTOR_SIDE ** getattr(self, 'current_expansion_sideways_steps', 0)))
        return "Max" # Fallback
