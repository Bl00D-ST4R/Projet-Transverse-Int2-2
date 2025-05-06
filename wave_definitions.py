# wave_definitions.py
import game_config as cfg # Pour les clés de stats si besoin (mais surtout pour les ID d'ennemis)

# --- Constantes de Temps pour les Vagues ---
# MODIFIABLE: Temps en secondes avant le début de la première vague
INITIAL_PREPARATION_TIME_SECONDS = 120.0 # 2 minutes

# MODIFIABLE: Temps en secondes entre la fin d'une vague (tous ennemis tués/passés)
# et le début du compte à rebours pour la suivante.
TIME_BETWEEN_WAVES_SECONDS = 150.0 # 2 minutes 30 secondes

# --- Définition des Ennemis (Rappel des ID depuis ENEMY_STATS dans objects.py) ---
# ENEMY_ID_BASIC = 1
# ENEMY_ID_FAST = 2
# ENEMY_ID_TANK = 3
# ... (Référez-vous à objects.py pour les ID exacts que vous avez définis)

# --- Structure d'une Vague ---
# Chaque vague est un dictionnaire où la clé est le numéro de la vague (commençant à 1).
# La valeur est une liste de "groupes d'ennemis" à faire spawner.
# Chaque groupe d'ennemis est une liste de tuples:
#   (delay_after_previous_group_or_start_seconds, enemy_type_id, count, spawn_interval_seconds, variant_data)
#
#   - delay_after_previous_group_or_start_seconds: Temps d'attente avant de commencer à spawner ce groupe.
#                                                   Pour le premier groupe de la vague, c'est le délai après le début de la vague.
#                                                   Pour les suivants, c'est le délai après la fin du spawn du groupe précédent.
#   - enemy_type_id: L'ID du type d'ennemi (défini dans objects.ENEMY_STATS).
#   - count: Nombre d'ennemis de ce type à faire spawner dans ce groupe.
#   - spawn_interval_seconds: Délai entre chaque spawn d'ennemi au sein de ce groupe.
#   - variant_data: Un dictionnaire optionnel pour des variations spécifiques (non utilisé pour l'instant, mais prévu).
#                   Ex: {"speed_multiplier": 1.2, "hp_multiplier": 1.5}

# Cette structure est une suggestion. On peut la simplifier.
# Version simplifiée pour la fonction `load_waves` actuelle dans `game_functions.py` :
# `game_state.enemies_in_current_wave_to_spawn` attend une liste de :
#   (delay_after_last_spawn_seconds, enemy_type_id, variant_data_optionnel)
#
# On va donc générer cette liste aplatie.

# --- Définitions des Vagues Prédéfinies ---

WAVE_DEFINITIONS_PRESET = {
    1: [ # Vague 1
        # Groupe 1: 5 ennemis basiques, espacés de 2 secondes, commençant après 3 secondes.
        {"delay_start_group": 3.0, "enemy_id": 1, "count": 5, "interval": 2.0, "variant": None},
    ],
    2: [ # Vague 2
        {"delay_start_group": 2.0, "enemy_id": 1, "count": 8, "interval": 1.5, "variant": None},
        {"delay_start_group": 5.0, "enemy_id": 2, "count": 3, "interval": 2.5, "variant": None}, # Groupe 2, 5s APRÈS LA FIN DU GROUPE 1
    ],
    3: [ # Vague 3
        {"delay_start_group": 1.0, "enemy_id": 1, "count": 10, "interval": 1.0, "variant": None},
        {"delay_start_group": 3.0, "enemy_id": 2, "count": 5, "interval": 1.5, "variant": None},
        {"delay_start_group": 4.0, "enemy_id": 3, "count": 1, "interval": 0.0, "variant": None}, # Un tank
    ],
    4: [ # Vague 4
        {"delay_start_group": 0.5, "enemy_id": 2, "count": 10, "interval": 0.8, "variant": None}, # Beaucoup de rapides
        {"delay_start_group": 5.0, "enemy_id": 1, "count": 7, "interval": 1.2, "variant": None},
    ],
    5: [ # Vague 5 - Boss wave?
        {"delay_start_group": 2.0, "enemy_id": 3, "count": 2, "interval": 5.0, "variant": None}, # Deux tanks espacés
        {"delay_start_group": 3.0, "enemy_id": 1, "count": 15, "interval": 0.7, "variant": None}, # Swarm de basiques
        {"delay_start_group": 2.0, "enemy_id": 2, "count": 8, "interval": 1.0, "variant": None},
    ],
    # MODIFIABLE: Ajoutez autant de vagues que vous le souhaitez.
    # Exemple avec des variants (si vous implémentez cette logique dans la classe Enemy):
    # 6: [
    #     {"delay_start_group": 2.0, "enemy_id": 1, "count": 5, "interval": 1.0, "variant": {"hp_multiplier": 1.5, "color_tint": (200,100,100)}},
    #     {"delay_start_group": 3.0, "enemy_id": 3, "count": 1, "interval": 0.0, "variant": {"speed_multiplier": 0.7, "is_elite": True}},
    # ],
}


def load_waves():
    """
    Traite les WAVE_DEFINITIONS_PRESET pour les mettre dans le format attendu par game_functions:
    une liste de (delay_since_last_spawn_in_wave, enemy_type_id, variant_data).
    Retourne un dictionnaire {wave_number: flattened_spawn_list}.
    """
    processed_waves = {}
    for wave_num, groups in WAVE_DEFINITIONS_PRESET.items():
        flattened_spawn_list_for_wave = []
        current_wave_time = 0.0 # Temps écoulé depuis le début du spawn de cette vague

        for group_info in groups:
            delay_start_group = group_info["delay_start_group"]
            enemy_id = group_info["enemy_id"]
            count = group_info["count"]
            interval = group_info["interval"]
            variant = group_info.get("variant", None) # Utilise .get pour variant optionnel

            # Le délai du groupe est par rapport à la fin du groupe précédent ou au début de la vague.
            # Pour la liste aplatie, on veut le délai depuis le DERNIER spawn.
            # Le premier spawn du groupe se fait après delay_start_group
            
            # Le premier ennemi du groupe
            if not flattened_spawn_list_for_wave: # Premier groupe de la vague
                # Le délai du premier ennemi est simplement le délai de démarrage du groupe.
                flattened_spawn_list_for_wave.append( (delay_start_group, enemy_id, variant) )
            else:
                # Pour les groupes suivants, le delay_start_group est relatif à la *fin* du groupe précédent.
                # La liste aplatie attend un délai depuis le *dernier spawn effectué*.
                # Ceci nécessite de savoir quand le dernier spawn du groupe précédent a eu lieu.
                # Pour simplifier, on va considérer que delay_start_group est le temps additionnel à attendre
                # après que le dernier ennemi du groupe précédent ait été programmé.
                # Cette logique est un peu délicate à aplatir directement.
                
                # Approche plus simple pour l'aplatissage :
                # On calcule le temps de spawn absolu pour chaque ennemi, puis on en déduit les deltas.
                # Ou, la fonction dans game_functions gère les "groupes".
                # Pour l'instant, on suit la structure de `game_state.enemies_in_current_wave_to_spawn`

                # Si on veut `delay_after_last_spawn_seconds`:
                # Le premier ennemi de CE groupe attend `delay_start_group` après que le groupe précédent ait fini de spawner.
                # Ce n'est pas ce que la structure actuelle de game_functions attend directement.

                # Changeons la signification de `delay_start_group` pour être le temps *depuis le début de la vague*
                # pour simplifier le calcul de la liste aplatie.
                # OU: on garde la structure de `game_functions` qui attend (delay_after_last_spawn, type, variant)
                # et on construit cette liste.

                # Ce premier ennemi du groupe attend `delay_start_group` après le *dernier spawn programmé*
                flattened_spawn_list_for_wave.append( (delay_start_group, enemy_id, variant) )


            # Les ennemis suivants dans le même groupe
            for i in range(1, count): # Commence à 1 car le premier est déjà ajouté
                flattened_spawn_list_for_wave.append( (interval, enemy_id, variant) )
        
        processed_waves[wave_num] = flattened_spawn_list_for_wave
        
    return processed_waves

# --- Fonctions pour des Vagues Générées Procéduralement (Optionnel) ---
# def generate_procedural_wave(wave_number, difficulty_factor):
#     """
#     Génère une vague d'ennemis de manière procédurale.
#     Pourrait être utilisé pour un mode infini.
#     """
#     spawn_list = []
#     # ... Logique pour déterminer les types d'ennemis, leur nombre, timing ...
#     # en fonction de wave_number et difficulty_factor.
#     # Exemple:
#     # num_basic = 5 + wave_number
#     # num_fast = wave_number // 2
#     # for _ in range(num_basic):
#     #     spawn_list.append( (random.uniform(0.5, 2.0), ENEMY_ID_BASIC, None) )
#     # for _ in range(num_fast):
#     #     spawn_list.append( (random.uniform(1.0, 3.0), ENEMY_ID_FAST, None) )
#     # random.shuffle(spawn_list) # Mélanger l'ordre de spawn
#     return spawn_list


if __name__ == '__main__':
    # Test de la fonction load_waves
    print("Test des définitions de vagues:")
    
    # Simuler les ID d'ennemis si objects.py n'est pas directement importable ici sans Pygame
    class MockEnemyStats:
        ENEMY_ID_BASIC = 1
        ENEMY_ID_FAST = 2
        ENEMY_ID_TANK = 3
    
    # Actualiser WAVE_DEFINITIONS_PRESET pour utiliser ces mocks si besoin pour le test standalone
    # (ou s'assurer que les IDs numériques sont corrects)

    loaded_wave_data = load_waves()
    for wave_num, spawn_list in loaded_wave_data.items():
        print(f"\nVague {wave_num}:")
        total_delay_this_wave = 0
        for i, (delay, enemy_id, variant) in enumerate(spawn_list):
            total_delay_this_wave += delay
            print(f"  - Spawn {i+1}: Après {delay:.1f}s (temps total vague: {total_delay_this_wave:.1f}s), Type: {enemy_id}, Variant: {variant}")
    
    print(f"\nINITIAL_PREPARATION_TIME_SECONDS: {INITIAL_PREPARATION_TIME_SECONDS}")
    print(f"TIME_BETWEEN_WAVES_SECONDS: {TIME_BETWEEN_WAVES_SECONDS}")
