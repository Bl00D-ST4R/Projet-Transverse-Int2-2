import pygame as pyg

# Global variables
frames = 0
time_elapsed = 0
game_running = False
pause = False
score = 0
list_enemy = []
resources = {"money": 100, "iron": 50, "other": 30}

def get_list_enemy():
    """Getter for the list of enemies."""
    global list_enemy
    return list_enemy

def set_list_enemy(new_list):
    """Setter for the list of enemies."""
    global list_enemy
    list_enemy = new_list

def init_var_game_func():
    """Initializes all key variables for the game."""
    global frames, time_elapsed, game_running, pause, score, list_enemy, resources
    frames = 0
    time_elapsed = 0
    game_running = False
    pause = False
    score = 0
    list_enemy = []
    resources = {"money": 100, "iron": 50, "other": 30}
    print("Game variables initialized.")

def compteur_temps_frame():
    """Tracks time and frames while the game is running."""
    global frames, time_elapsed, pause, game_running
    clock = pyg.time.Clock()  # Pygame clock for managing time
    while game_running and not pause:
        dt = clock.tick(60)  # Limit to 60 FPS and get the time passed in milliseconds
        frames += 1
        time_elapsed += dt / 1000  # Convert milliseconds to seconds
        if frames % 60 == 0:
            print(f"Time: {int(time_elapsed)}s, Frames: {frames}")

def toggle_pause():
    """Toggles the pause state."""
    global pause
    pause = not pause
    print(f"Pause state: {pause}")

def pause_menu():
    """Displays the in-game pause menu."""
    global pause
    toggle_pause()
    if pause:
        print("Game paused. Displaying pause menu...")
        # Logic for displaying pause menu
    else:
        print("Resuming game...")