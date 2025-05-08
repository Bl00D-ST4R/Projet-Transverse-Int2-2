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
        self.grid_width_tiles = cfg.GRID_INITIAL_WIDTH_TILES # CORRIGÉ: Utiliser le nom de cfg
        self.grid_height_tiles = cfg.GRID_INITIAL_HEIGHT_TILES # CORRIGÉ: Utiliser le nom de cfg
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
        self.turrets = [] # Contient les instances de Turret
        self.enemies = [] # Contient les instances d'Enemy
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


    def get_next_expansion_cost(self, direction):
        """Calcule le coût de la prochaine expansion sans l'effectuer."""
        # Logique de coût dupliquée de try_expand_build_area (ou centraliser cette logique)
        # MODIFIABLE: Coûts d'expansion (doivent être cohérents avec try_expand_build_area)
        cost_up_base = 500 
        cost_side_base = 1000
        
        cost = 0
        if direction == "up":
            if self.current_expansion_up_tiles < cfg.GRID_MAX_EXPANSION_UP_TILES:
                cost = cost_up_base * (self.current_expansion_up_tiles + 1)
            else:
                return "Max" # Ou un indicateur que c'est max
        elif direction == "side":
            if self.current_expansion_sideways_steps < cfg.GRID_MAX_EXPANSION_SIDEWAYS_STEPS:
                cost = cost_side_base * (self.current_expansion_sideways_steps + 1)
            else:
                return "Max"
        return cost

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
        dynamic_grid_offset_y = cfg.SCREEN_HEIGHT - current_grid_pixel_height - cfg.UI_BUILD_MENU_HEIGHT - cfg.scale_value(10) # Ajoutez une petite marge si nécessaire

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
        print(f"Game Paused: {self.game_paused}") # Debug print

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
                # La liste contient (delay_after_last_spawn, enemy_type_id, enemy_variant)
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
        # Copier la définition de vague car on la modifie en la parcourant (pop)
        self.enemies_in_current_wave_to_spawn = list(self.all_wave_definitions.get(self.current_wave_number, []))
        self.time_since_last_spawn_in_wave = 0.0
        if not self.enemies_in_current_wave_to_spawn: # Vague vide ?
            self.wave_in_progress = False
            self.time_to_next_wave_seconds = wave_definitions.TIME_BETWEEN_WAVES_SECONDS


    def spawn_enemy(self, enemy_type_id, variant_data=None):
        # TODO: Déterminer la position de spawn (généralement hors écran à droite)
        # La hauteur de spawn pourrait être aléatoire ou basée sur des "chemins"
        # Assurez-vous que la zone de spawn Y est au-dessus du menu de construction et dans des limites raisonnables
        min_spawn_y = self.buildable_area_rect_pixels.y - cfg.scale_value(100) # Un peu au-dessus de la zone de construction
        max_spawn_y = cfg.SCREEN_HEIGHT - cfg.UI_BUILD_MENU_HEIGHT - cfg.scale_value(50) # Un peu au-dessus du menu
        spawn_y_ref = random.randint(max(cfg.scale_value(50), int(min_spawn_y)), int(max_spawn_y)) # Position Y de référence

        spawn_x_ref = cfg.SCREEN_WIDTH + cfg.scale_value(50) # Hors écran à droite

        new_enemy = objects.Enemy((spawn_x_ref, spawn_y_ref), enemy_type_id, variant_data)
        self.enemies.append(new_enemy)
        # print(f"Spawned enemy: {enemy_type_id} at ({spawn_x_ref}, {spawn_y_ref})") # Debug print


    def handle_player_input(self, event, mouse_pos_pixels):
        if self.game_over_flag: return
        if self.game_paused: # Ne pas gérer les clics si le jeu est en pause (sauf pour le menu pause)
             # TODO: Ajouter logique pour cliquer sur le menu pause si nécessaire
             return


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic gauche
                # 1. Vérifier si clic sur le menu de construction UI
                clicked_ui_item_id = ui_functions.check_build_menu_click(self, mouse_pos_pixels)

                if clicked_ui_item_id:
                    if clicked_ui_item_id.startswith("expand_"):
                        action = clicked_ui_item_id.split("_")[1] # "up" ou "side"
                        self.try_expand_build_area(action)
                        self.selected_item_to_place_type = None # Désélectionner après action
                        self.placement_preview_sprite = None # Enlever la preview aussi
                    else: # C'est un bâtiment/tourelle à placer
                        self.selected_item_to_place_type = clicked_ui_item_id
                        item_stats = objects.get_item_stats(self.selected_item_to_place_type)
                        # Charger le sprite de prévisualisation
                        # CORRIGÉ: Utiliser la bonne clé pour le sprite par défaut et gérer les variants
                        if item_stats:
                            sprite_name_for_preview = None
                            path_prefix = None

                            # Déterminer le chemin du préfixe en fonction du type d'item
                            if objects.is_building_type(self.selected_item_to_place_type):
                                path_prefix = cfg.BUILDING_SPRITE_PATH
                                # Pour les bâtiments avec variants (comme miner), utiliser le sprite 'single' pour la preview
                                if cfg.STAT_SPRITE_VARIANTS_DICT in item_stats and "single" in item_stats[cfg.STAT_SPRITE_VARIANTS_DICT]:
                                     sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_VARIANTS_DICT]["single"]
                                elif cfg.STAT_SPRITE_DEFAULT_NAME in item_stats:
                                     sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_DEFAULT_NAME]

                            elif objects.is_turret_type(self.selected_item_to_place_type):
                                path_prefix = cfg.TURRET_SPRITE_PATH
                                # Tourelles n'ont généralement pas de variants de placement ? Utiliser le sprite par défaut
                                if cfg.STAT_SPRITE_DEFAULT_NAME in item_stats:
                                     sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_DEFAULT_NAME]

                            else: # Fallback pour tout autre type d'item non géré explicitement
                                path_prefix = cfg.SPRITE_PATH
                                if cfg.STAT_SPRITE_DEFAULT_NAME in item_stats:
                                     sprite_name_for_preview = item_stats[cfg.STAT_SPRITE_DEFAULT_NAME]


                            if sprite_name_for_preview and path_prefix:
                                self.placement_preview_sprite = util.scale_sprite_to_tile(util.load_sprite(path_prefix + sprite_name_for_preview))
                                if self.placement_preview_sprite:
                                    self.placement_preview_sprite.set_alpha(150) # Rendre semi-transparent
                                else:
                                     print(f"Warning: Could not load preview sprite {path_prefix + sprite_name_for_preview}") # Debug
                                     self.placement_preview_sprite = None
                            else:
                                print(f"Warning: No valid sprite name or path prefix for preview of {self.selected_item_to_place_type}") # Debug
                                self.placement_preview_sprite = None
                        else:
                            print(f"Warning: No stats found for {self.selected_item_to_place_type}, cannot create preview.") # Debug
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
            # Autoriser placement tourelle si l'objet existant est une fondation
            if objects.is_turret_type(item_type) and objects.is_foundation_type(existing_item.type):
                pass # Autorisé (la tourelle remplacera la fondation dans la grille logique pour la simplicité)
            else:
                 # Autoriser miner si l'objet existant est un miner (pour empiler)
                 if item_type == "miner" and existing_item.type == "miner":
                     pass # Autorisé
                 else:
                    return False, (grid_r, grid_c) # Case occupée par autre chose

        # TODO: Implémenter toutes les RÈGLES DE PLACEMENT ici
        # (mineurs sur fondation renforcée, bonus stockage adjacency check est ailleurs, etc.)
        # Exemple spécifique pour mineur:
        if item_type == "miner":
            # Fondations renforcées sont la première ligne du bas de la zone 4xH initiale
            # La position Y de la "première ligne du bas" change si on étend vers le haut
            # CORRIGÉ: Utiliser GRID_INITIAL_HEIGHT_TILES et GRID_INITIAL_WIDTH_TILES
            base_bottom_row_index = cfg.GRID_INITIAL_HEIGHT_TILES - 1 + self.current_expansion_up_tiles

            is_on_reinforced_foundation_spot = (grid_r == base_bottom_row_index and \
                                                0 <= grid_c < cfg.GRID_INITIAL_WIDTH_TILES)

            is_on_another_miner = False
            # Check la case juste en dessous (grid_r + 1) dans la grille logique
            # Le joueur place *sur* la case cible (grid_r, grid_c), donc on vérifie celle *en dessous*
            # if grid_r > 0 and self.game_grid[grid_r - 1][grid_c] and \
            #    self.game_grid[grid_r - 1][grid_c].type == "miner": # L'original vérifiait au-dessus ? Bug ?
            #    is_on_another_miner = True
            # Correction: Vérifier la case *directement en dessous* dans le monde du jeu (grid_r + 1)
            # if grid_r + 1 < self.grid_height_tiles and self.game_grid[grid_r + 1][grid_c] and \
            #    self.game_grid[grid_r + 1][grid_c].type == "miner":
            #    is_on_another_miner = True
            # Re-Correction: L'empilement de mineurs se fait VERS LE HAUT dans la grille logique.
            # donc un miner en (r, c) est posé *sur* un miner existant en (r+1, c).
            # La check correcte est donc bien si (r+1, c) est un miner existant.
            if grid_r + 1 < self.grid_height_tiles and self.game_grid[grid_r + 1][grid_c] and \
               self.game_grid[grid_r + 1][grid_c].type == "miner":
               is_on_another_miner = True


            if not (is_on_reinforced_foundation_spot or is_on_another_miner):
                 # Si la case est déjà occupée par un miner, la check 'existing_item' plus haut a déjà géré ce cas positivement.
                 # Cette condition gère uniquement le cas où la case est vide, et n'est ni une fondation renforcée, ni au-dessus d'un miner.
                 if not existing_item or existing_item.type != "miner": # Vérifie qu'on ne bloque pas l'empilement sur un miner existant (déjà géré au-dessus)
                     return False, (grid_r, grid_c)


        # Vérifier ressources (argent, fer)
        item_stats = objects.get_item_stats(item_type)
        if self.money < item_stats.get(cfg.STAT_COST_MONEY, 0):
             self.show_error_message("Pas assez d'argent!") # Ajout message
             return False, (grid_r, grid_c)
        if self.iron_stock < item_stats.get(cfg.STAT_COST_IRON, 0):
             self.show_error_message("Pas assez de fer!") # Ajout message
             return False, (grid_r, grid_c)

        # Vérifier électricité
        # CORRIGÉ: Logique électrique avec production/consommation séparées
        power_prod_impact = item_stats.get(cfg.STAT_POWER_PRODUCTION, 0)
        power_conso_impact = item_stats.get(cfg.STAT_POWER_CONSUMPTION, 0) # C'est une valeur positive

        projected_prod = self.electricity_produced + power_prod_impact
        projected_conso = self.electricity_consumed + power_conso_impact

        # Si la production projetée est inférieure à la consommation projetée (après avoir ajouté le coût/bénéfice de l'item)
        # Et si l'item n'est pas un générateur (on doit toujours pouvoir construire un générateur pour résoudre un problème d'énergie)
        # et si l'item n'est pas un stockage (les stockages n'utilisent pas d'énergie et n'en produisent pas)
        # et si l'item n'est pas une fondation (les fondations n'utilisent pas d'énergie)
        is_power_producer = item_type in objects.BUILDING_STATS and objects.BUILDING_STATS[item_type].get(cfg.STAT_POWER_PRODUCTION, 0) > 0
        is_storage = item_type == "storage"
        is_foundation = objects.is_foundation_type(item_type)


        if projected_prod < projected_conso and not is_power_producer and not is_storage and not is_foundation:
             self.show_error_message("Pas assez d'énergie disponible!") # Ajout message
             return False, (grid_r, grid_c)


        # TODO: Ajouter d'autres règles de placement si nécessaire (ex: ne pas construire trop près du bord gauche initial)


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

            # Gérer le remplacement de la fondation si une tourelle est placée dessus
            existing_item = self.game_grid[grid_r][grid_c]
            if existing_item and objects.is_foundation_type(existing_item.type) and objects.is_turret_type(item_type):
                 # Si on remplace une fondation, on la retire de la liste des bâtiments
                 # TODO: S'assurer que la fondation n'a pas d'effets secondaires à annuler
                 if existing_item in self.buildings:
                     self.buildings.remove(existing_item)
                 # La nouvelle tourelle remplacera la fondation dans game_grid et sera ajoutée à la liste des tourelles

            # Créer et ajouter l'objet
            if objects.is_turret_type(item_type):
                new_item = objects.Turret(item_type, (grid_r, grid_c))
                self.turrets.append(new_item)
            else: # C'est un bâtiment (inclut les fondations si elles étaient plaçables)
                new_item = objects.Building(item_type, (grid_r, grid_c))
                self.buildings.append(new_item)

            self.game_grid[grid_r][grid_c] = new_item
            new_item.update_sprite_based_on_context(self.game_grid, grid_r, grid_c) # Pour sprites contextuels (mine empilée etc), passe coords


            # Vérifier et appliquer les bonus d'adjacence après placement
            # Appliquer le bonus au nouvel item (ex: un stockage placé à côté d'autres)
            self.check_and_apply_adjacency_bonus(new_item, grid_r, grid_c)
            # Et potentiellement vérifier/appliquer le bonus aux voisins si le nouvel item en donne un (ex: un stockage qui augmente la capacité des stockages adjacents)
            # La logique actuelle dans check_and_apply_adjacency_bonus pour 'storage' ne regarde que si *lui-même* est adjacent à d'autres.
            # Pour que placer un stockage affecte ses voisins existants, il faut appeler la check_and_apply_adjacency_bonus sur les voisins aussi.
            # Exemple pour stockage: si on place un stockage, vérifier aussi les voisins 'storage'
            if item_type == "storage":
                 for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                     nr, nc = grid_r + dr, grid_c + dc
                     if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles:
                          neighbor_item = self.game_grid[nr][nc]
                          if neighbor_item and neighbor_item.type == "storage":
                              # Recalculer et appliquer le bonus au stockage voisin
                              self.check_and_apply_adjacency_bonus(neighbor_item, nr, nc)


            self.update_resource_production_consumption()
            # Optionnel: Désélectionner après placement réussi
            # self.selected_item_to_place_type = None
            # self.placement_preview_sprite = None
            print(f"Placed {item_type} at ({grid_r},{grid_c})") # Debug print
        else:
            # Le message d'erreur est déjà défini dans check_placement_validity
            # self.show_error_message("Placement invalide!")
            print(f"Invalid placement attempt for {item_type} at ({grid_r},{grid_c})") # Debug print


    def check_and_apply_adjacency_bonus(self, item, r, c):
        """Vérifie et met à jour l'item (ex: un stockage) pour les bonus d'adjacence."""
        if not item or not hasattr(item, 'apply_adjacency_bonus_effect'):
            return

        # La logique de bonus est spécifique à chaque type d'item.
        # Pour l'exemple du stockage :
        if item.type == "storage":
            adjacent_similar_items_count = 0
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]: # Voisins directs (haut, bas, gauche, droite)
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_height_tiles and 0 <= nc < self.grid_width_tiles and \
                   self.game_grid[nr][nc] and self.game_grid[nr][nc].type == "storage":
                    adjacent_similar_items_count +=1
            # Appeler la méthode de l'objet stockage pour appliquer le bonus
            # Le bonus appliqué doit être ajouté au bonus de base du type d'item (stockage par défaut + bonus d'adjacence)
            # TODO: S'assurer que la logique dans Building/Turret.apply_adjacency_bonus_effect gère cela correctement
            # Par exemple, un stockage pourrait avoir BASE_STORAGE_INCREASE et ADJACENCY_BONUS_PER_STORAGE
            # Et la méthode additionnerait BASE + (ADJACENCY_BONUS_PER_STORAGE * count)
            # Pour l'instant, le code semble appliquer la *valeur totale* du bonus d'adjacence.
            item.apply_adjacency_bonus_effect(adjacent_similar_items_count) # Passe le COUNT de voisins similaires

            # Mettre à jour le sprite si le bonus le change (ex: apparence différente pour plusieurs stockages connectés)
            item.update_sprite_based_on_context(self.game_grid, r, c) # Passe la grille et ses propres coords


    def try_expand_build_area(self, direction): # "up" ou "side"
        # MODIFIABLE: Coûts d'expansion
        cost_up = cfg.EXPANSION_COST_UP_BASE * (self.current_expansion_up_tiles + 1) # CORRIGÉ: Utiliser les cfg
        cost_side = cfg.EXPANSION_COST_SIDE_BASE * (self.current_expansion_sideways_steps + 1) # CORRIGÉ: Utiliser les cfg

        can_expand = False
        cost_expansion = 0

        if direction == "up" and self.current_expansion_up_tiles < cfg.MAX_EXPANSION_UP_TILES:
            cost_expansion = cost_up
            can_expand = True
        elif direction == "side" and self.current_expansion_sideways_steps < cfg.MAX_EXPANSION_SIDEWAYS_STEPS:
            cost_expansion = cost_side
            can_expand = True

        if not can_expand:
            self.show_error_message("Expansion max atteinte.")
            return

        if self.money >= cost_expansion:
            self.money -= cost_expansion
            new_grid_w = self.grid_width_tiles
            new_grid_h = self.grid_height_tiles

            if direction == "up":
                self.current_expansion_up_tiles += 1
                new_grid_h += 1 # Ajoute une rangée. On considère qu'on étend "vers le haut" logiquement,
                                # mais on ajoute la rangée en bas de la structure de données et on décale l'offset Y de dessin.
                                # Ou on insère au début et on décale tout.
                                # Pour simplifier : on étend la grille vers le bas de la structure de données,
                                # mais la zone de construction s'étend visuellement vers le haut car GRID_OFFSET_Y est recalculé.

                # Ajoute des nouvelles rangées en bas de la structure game_grid
                # On ajoute une rangée *au début* de la liste pour qu'elle apparaisse *en haut* visuellement
                # Et on décale tous les objets existants vers le bas de la grille logique.
                # C'est plus complexe et moins intuitif que d'ajouter en bas et décaler l'offset Y comme fait initialement.
                # Restons sur l'ajout en bas de la structure et le décalage de l'offset Y pour la simplicité.
                new_rows = [[None for _ in range(self.grid_width_tiles)] for _ in range(1)]
                self.game_grid.append(new_rows[0]) # Ajoute la nouvelle rangée en bas logique
                self.grid_height_tiles = new_grid_h

                # TODO: Si on change la logique pour insérer en haut de la liste, il faudrait décaler les coordonnées (r, c)
                # de tous les objets existants dans self.buildings et self.turrets (r -> r+1).
                # Avec la logique actuelle (ajouter en bas de liste game_grid et ajuster offset Y),
                # les coordonnées (r,c) des objets existants restent valides.

            elif direction == "side":
                self.current_expansion_sideways_steps += 1
                new_grid_w += cfg.EXPANSION_SIDEWAYS_TILES_PER_STEP
                for r_idx in range(self.grid_height_tiles):
                    self.game_grid[r_idx].extend([None for _ in range(cfg.EXPANSION_SIDEWAYS_TILES_PER_STEP)])
                self.grid_width_tiles = new_grid_w

            self.update_buildable_area_rect() # Crucial pour redessiner correctement
            self.show_error_message("Zone de base étendue!")
            print(f"Expanded grid to {self.grid_width_tiles}x{self.grid_height_tiles}") # Debug print
        else:
            self.show_error_message(f"Pas assez d'argent ({cost_expansion}$ nécessaires)")


    def update_resource_production_consumption(self):
        self.electricity_produced = 0
        self.electricity_consumed = 0
        self.iron_production_per_minute = 0
        temp_iron_storage_capacity_from_buildings = 0

        # NOTE: La logique pour désactiver les bâtiments/tourelles si l'énergie est insuffisante
        # peut être gérée ici en parcourant les objets APRES avoir calculé total_produced/consumed
        # ou dans la méthode .update() de chaque objet en leur passant l'état global de l'énergie.
        # Pour l'instant, on compte simplement la production/consommation totale des objets marqués comme 'active'.

        for building in self.buildings:
            # CORRIGÉ: Utiliser le flag général 'active' pour l'instant
            # TODO: Ajouter une logique de priorité ou de simple désactivation si l'énergie est globalement négative
            if not building.active: continue

            # Accéder directement aux stats définies dans objects
            stats = objects.BUILDING_STATS.get(building.type, {})
            self.electricity_produced += stats.get(cfg.STAT_POWER_PRODUCTION, 0)
            # CORRIGÉ: Consommation est maintenant un stat séparé et positif
            self.electricity_consumed += stats.get(cfg.STAT_POWER_CONSUMPTION, 0)

            # CORRIGÉ: Utiliser la clé correcte pour la production de fer par minute
            self.iron_production_per_minute += stats.get(cfg.STAT_IRON_PRODUCTION_PM, 0)
            # CORRIGÉ: Utiliser la clé correcte pour l'augmentation de stockage
            temp_iron_storage_capacity_from_buildings += stats.get(cfg.STAT_IRON_STORAGE_INCREASE, 0)
            # Ajouter le bonus d'adjacence effectif du bâtiment (calculé dans check_and_apply_adjacency)
            if hasattr(building, 'current_adjacency_bonus_value'):
                 temp_iron_storage_capacity_from_buildings += building.current_adjacency_bonus_value


        for turret in self.turrets:
            # CORRIGÉ: Utiliser le flag général 'active' pour l'instant
            # TODO: Ajouter une logique de priorité ou de simple désactivation si l'énergie est globalement négative
            if not turret.active: continue

            # Accéder directement aux stats définies dans objects
            stats = objects.TURRET_STATS.get(turret.type, {})
            # CORRIGÉ: Consommation est maintenant un stat séparé et positif
            self.electricity_consumed += stats.get(cfg.STAT_POWER_CONSUMPTION, 0)

        self.iron_storage_capacity = cfg.BASE_IRON_CAPACITY + temp_iron_storage_capacity_from_buildings

        # TODO: Mettre à jour l'état actif des bâtiments/tourelles si l'énergie globale est insuffisante
        # (Logique plus avancée: prioriser certains bâtiments, etc.)
        # Pour l'instant, on suppose que tout fonctionne si prod >= conso globalement, mais les objets devraient
        # avoir une méthode 'check_power_status(power_available_globally)' appelée dans leur update()

    def update_resources_per_tick(self, delta_time):
        if self.game_paused or self.game_over_flag: return

        # Production de fer
        # Production par minute / 60 secondes * delta_time en secondes
        iron_gain = (self.iron_production_per_minute / 60.0) * delta_time
        self.iron_stock = min(self.iron_stock + iron_gain, self.iron_storage_capacity)


    def update_game_logic(self, delta_time):
        if self.game_over_flag or self.game_paused:
            return

        # 1. Mettre à jour les timers et la logique des vagues
        self.update_timers_and_waves(delta_time)

        # 2. Mettre à jour les ressources (production/consommation sur la durée)
        self.update_resources_per_tick(delta_time)

        # --- LOGIQUE DE JEU ACTEURS ---
        # Déterminer si l'énergie globale est suffisante pour alimenter les consommateurs
        power_available_overall = (self.electricity_produced >= self.electricity_consumed)
        # TODO: Refactoriser pour que chaque objet (Building/Turret) gère son état 'active' basé sur cette info.
        # Par exemple, passer `power_available_overall` à leur méthode `update()`.

        # 3. Mettre à jour les tourelles (ciblage, tir)
        # Les tourelles ont besoin de la liste d'ennemis et de l'état d'énergie globale
        for turret in self.turrets:
             # turret.update(delta_time, self.enemies, power_available_overall, self) # Ancienne signature si l'énergie est passée
             turret.update(delta_time, self.enemies, self) # Nouvelle signature si la tourelle check self.electricity_produced/consumed ou un flag global

        # 4. Mettre à jour les projectiles (mouvement)
        # Les projectiles ont besoin de l'état du jeu pour déclencher des effets (AoE) ou toucher des ennemis
        for proj in self.projectiles:
            proj.update(delta_time, self) # Passe self (game_state) pour les interactions (collisions, AoE)

        # 5. Mettre à jour les ennemis (mouvement, future IA d'attaque)
        for enemy in self.enemies:
            enemy.update(delta_time)
            # Vérifier si l'ennemi a atteint la base (le bord gauche de la zone de construction)
            if enemy.rect.right < self.buildable_area_rect_pixels.left: # Utiliser la limite gauche de la zone constructible
                self.city_take_damage(enemy.get_city_damage())
                enemy.active = False # Marquer pour suppression
                self.show_error_message("La ville a subi des dégâts!")
                # TODO: Ajouter un effet visuel ou sonore

        # 6. Gérer les collisions
        self.handle_collisions()

        # 7. Mettre à jour les effets de particules (animations, durée de vie)
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
        if self.game_over_flag: return # Ne prend pas de dégâts si déjà game over
        if amount <= 0: return # Pas de dégâts positifs

        self.city_hp -= amount
        if self.city_hp < 0:
            self.city_hp = 0
        print(f"City took {amount} damage. HP: {self.city_hp}") # Debug print
        # TODO: Effet visuel/sonore sur la ville ou l'UI de vie

    def handle_collisions(self):
        # Projectiles vs Ennemis
        # Itérer sur des copies des listes si on modifie les originaux pendant l'itération
        # Utiliser une gestion de groupe Pygame serait plus efficace pour les collisions
        # pygame.sprite.groupcollide(projectiles_group, enemies_group, True, False) par exemple
        # Ici, on itère manuellement

        projectiles_to_remove = []
        enemies_hit_this_tick = set() # Pour éviter de frapper le même ennemi plusieurs fois avec un projectile non-AoE dans la même frame

        for proj in self.projectiles:
             if not proj.active: continue
             # Optimisation: Vérifier d'abord si le projectile est dans la zone de jeu (ou proche)
             if proj.rect.right < 0 or proj.rect.left > cfg.SCREEN_WIDTH or \
                proj.rect.bottom < 0 or proj.rect.top > cfg.SCREEN_HEIGHT:
                 proj.active = False # Le projectile est sorti de l'écran
                 continue # Passe au projectile suivant

             for enemy in self.enemies:
                 if not enemy.active or enemy in enemies_hit_this_tick: continue

                 # Utiliser la hitbox de l'ennemi pour la collision
                 if proj.rect.colliderect(enemy.hitbox):
                     # Appliquer les dégâts
                     enemy.take_damage(proj.damage)
                     # Déclencher l'effet à l'impact (peut créer AoE, particules, etc.)
                     # proj.on_hit(self) # La méthode on_hit est responsable de créer l'AoE via trigger_aoe_damage

                     # Si le projectile n'est PAS un projectile AoE ou explosif, il est consommé
                     if not proj.is_aoe: # Assumer un attribut ou une méthode sur le projectile
                          proj.active = False # Désactiver le projectile après le premier hit
                          projectiles_to_remove.append(proj)
                          enemies_hit_this_tick.add(enemy) # Marquer l'ennemi comme touché par CE type de projectile ce tick
                          # Si un projectile est consommé au premier hit, on peut break l'itération sur les ennemis pour ce projectile
                          break # Sortir de la boucle des ennemis pour ce projectile


                     # Si l'ennemi est tué par le coup (même par AoE potentiellement)
                     if not enemy.active: # Ennemi tué
                         self.money += enemy.get_money_value()
                         self.score += enemy.get_score_value()
                         # TODO: Ajouter des effets de mort (particules, son)

        # Ajouter les projectiles AoE / explosifs sont gérés dans leur propre méthode on_hit()
        # Les projectiles marqués comme inactive (consommés) seront nettoyés plus tard.

    def trigger_aoe_damage(self, center_pos, radius, damage):
        """Appelé par un projectile (ex: mortier) ou un ennemi pour infliger des dégâts de zone."""
        # SPRITE: Créer une animation d'explosion ici (ajouter à self.particle_effects)
        # exemple: self.particle_effects.append(objects.ExplosionEffect(center_pos)) # Nécessite une classe ExplosionEffect

        scaled_radius = cfg.scale_value(radius) # Si radius est en unités de référence
        radius_sq = scaled_radius ** 2

        # Appliquer les dégâts aux ennemis dans le rayon
        for enemy in self.enemies:
            if not enemy.active: continue
            # Distance entre le centre de l'explosion et le centre de la hitbox de l'ennemi
            distance_sq = (enemy.hitbox.centerx - center_pos[0])**2 + (enemy.hitbox.centery - center_pos[1])**2

            if distance_sq < radius_sq:
                # TODO: Réduction des dégâts avec la distance ? damage = damage * (1.0 - sqrt(distance_sq) / scaled_radius) ?
                enemy.take_damage(damage)
                if not enemy.active: # Ennemi tué par l'AoE
                    self.money += enemy.get_money_value()
                    self.score += enemy.get_score_value()
                    # TODO: Effets de mort

        # Ajouter l'effet visuel de l'explosion AU CENTRE de l'AoE
        self.particle_effects.append(objects.ExplosionEffect(center_pos)) # Supposons que ExplosionEffect existe et s'ajoute à la liste

    def cleanup_inactive_objects(self):
        # Utiliser des comprehensions de liste est une façon simple et efficace de filtrer
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.particle_effects = [eff for eff in self.particle_effects if eff.active]
        # Les bâtiments/tourelles ne sont pas détruits dans ce modèle pour l'instant, donc pas de nettoyage pour eux.

    def draw_game_world(self):
        # 1. Dessiner le fond (si image ou couleur unie)
        self.screen.fill(cfg.COLOR_DARK_GREY_BLUE) # Couleur de fond temporaire définie dans cfg ?

        # 2. Dessiner la zone de la grille constructible (le sol/terrain)
        ui_functions.draw_base_grid(self.screen, self)

        # 3. Dessiner les bâtiments
        # Trier les bâtiments par coordonnée Y pour un meilleur rendu visuel (ceux du bas devant ceux du haut)
        self.buildings.sort(key=lambda b: b.rect.bottom) # Trie inplace
        for building in self.buildings:
            building.draw(self.screen)

        # 4. Dessiner les tourelles (base et canon)
        # Trier aussi les tourelles par Y (leurs bases)
        self.turrets.sort(key=lambda t: t.rect.bottom)
        for turret in self.turrets:
            turret.draw(self.screen) # La méthode draw de la tourelle doit dessiner la base puis le canon/tourelle pivotant

        # 5. Dessiner les ennemis
        # Trier les ennemis par Y pour un meilleur rendu (ceux du bas devant ceux du haut)
        self.enemies.sort(key=lambda e: e.rect.bottom)
        for enemy in self.enemies:
            enemy.draw(self.screen)
            # DEBUG: util.draw_debug_rect(self.screen, enemy.hitbox, cfg.COLOR_GREEN) # Si COLOR_GREEN est défini dans cfg

        # 6. Dessiner les projectiles (devant les ennemis ?) L'ordre dépend de l'effet souhaité
        for proj in self.projectiles:
            proj.draw(self.screen)

        # 7. Dessiner les effets de particules (explosions) - généralement par-dessus tout
        for effect in self.particle_effects:
            effect.draw(self.screen)

        # 8. Dessiner la prévisualisation du placement (doit être par-dessus la grille mais sous l'UI)
        ui_functions.draw_placement_preview(self.screen, self)


    def draw_game_ui_elements(self):
        # Dessiner les éléments UI statiques ou d'information
        ui_functions.draw_top_bar_ui(self.screen, self) # Barre d'info en haut
        ui_functions.draw_build_menu_ui(self.screen, self) # Menu de construction en bas

        # Dessiner les éléments UI temporaires ou d'état
        if self.last_error_message and self.error_message_timer > 0:
            ui_functions.draw_error_message(self.screen, self.last_error_message)

        # Les écrans de pause et de game over doivent être dessinés PAR-DESSUS tout le reste du jeu et de l'UI standard
        # Cette méthode est appelée APRÈS draw_game_world, donc c'est le bon endroit.
        if self.game_paused:
            ui_functions.draw_pause_screen(self.screen)

        if self.game_over_flag:
            ui_functions.draw_game_over_screen(self.screen, self.score)

# Instance globale de l'état du jeu (ou passée en argument)
# Pour un accès plus facile depuis les objets, on peut la rendre accessible.
# Cependant, il est souvent mieux de passer `game_state` explicitement aux fonctions/méthodes qui en ont besoin.
# game_state_instance = GameState() # Sera créé dans main.py
