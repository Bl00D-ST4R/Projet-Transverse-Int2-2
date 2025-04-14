import game_functions as gf

class Enemy:
    """Base class for all enemy types."""
    def __init__(self, enemy_type: int, enemy_id: int):
        self.enemy_type = enemy_type
        self.enemy_id = enemy_id
        self.current_hp = self.set_initial_hp()
        self.current_damage = self.set_initial_damage()

    def set_initial_hp(self):
        """Sets the initial HP based on the enemy type."""
        if self.enemy_type == 1:
            return 100  # Basic_E
        elif self.enemy_type == 2:
            return 200  # Bomber_E
        elif self.enemy_type == 3:
            return 150  # Strafer_E
        elif self.enemy_type == 4:
            return 300  # Heavy_E
        else:
            return 50  # Default for unknown types

    def set_initial_damage(self):
        """Sets the initial damage based on the enemy type."""
        if self.enemy_type == 1:
            return 10  # Basic_E
        elif self.enemy_type == 2:
            return 20  # Bomber_E
        elif self.enemy_type == 3:
            return 15  # Strafer_E
        elif self.enemy_type == 4:
            return 30  # Heavy_E
        else:
            return 5  # Default for unknown types

class Basic_E(Enemy):
    """Class for Basic Enemy."""
    def __init__(self, enemy_id: int):
        super().__init__(enemy_type=1, enemy_id=enemy_id)

class Bomber_E(Enemy):
    """Class for Bomber Enemy."""
    def __init__(self, enemy_id: int):
        super().__init__(enemy_type=2, enemy_id=enemy_id)

class Strafer_E(Enemy):
    """Class for Strafer Enemy."""
    def __init__(self, enemy_id: int):
        super().__init__(enemy_type=3, enemy_id=enemy_id)

class Heavy_E(Enemy):
    """Class for Heavy Enemy."""
    def __init__(self, enemy_id: int):
        super().__init__(enemy_type=4, enemy_id=enemy_id)

def create_enemy(enemy_type: int):
    """Creates an enemy and adds it to the global enemy list."""
    enemy_list = gf.get_list_enemy()
    enemy_id = len(enemy_list) + 1  # Generate a unique ID for the enemy
    if enemy_type == 1:
        new_enemy = Basic_E(enemy_id)
    elif enemy_type == 2:
        new_enemy = Bomber_E(enemy_id)
    elif enemy_type == 3:
        new_enemy = Strafer_E(enemy_id)
    elif enemy_type == 4:
        new_enemy = Heavy_E(enemy_id)
    else:
        new_enemy = Enemy(enemy_type, enemy_id)  # Default enemy type

    enemy_list.append(new_enemy)
    gf.set_list_enemy(enemy_list)
    print(f"Enemy {new_enemy.enemy_id} of type {new_enemy.enemy_type} created.")
