import pygame as pyg
import random as rd
import utility_functions as ufunc
import gamemodes

# Initialize Pygame
pyg.init()

# Define global variables
screen = None
running = True

def initialize_game():
    """Initializes the game window and basic settings."""
    global screen
    screen = pyg.display.set_mode((1280, 720))  # Example resolution
    pyg.display.set_caption("FLAK 88 - Lgbtverse")
    print("Game initialized.")

def game_loop():
    """Main game loop that handles backend logic."""
    global running
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False

        # Call the menu function and handle its return value
        choice = ufunc.menu()
        if choice == 0:
            quit_game()
        elif choice == 1:
            gamemodes.mode_1()
        elif choice == 2:
            gamemodes.mode_2()
        elif choice == 3:
            gamemodes.tutorial()
        elif choice == 4:
            animation_lore()

        # Update the display
        pyg.display.flip()

def animation_lore():
    """Displays a short animation or story summary."""
    print("Playing animation/lore...")
    # Example animation logic
    for i in range(100):
        screen.fill((0, 0, 0))  # Black background
        pyg.display.flip()
        pyg.time.delay(10)
    print("Animation finished. Returning to menu.")

def quit_game():
    """Handles quitting the game."""
    global running
    print("Quitting the game...")
    running = False
    pyg.quit()

# Main execution
if __name__ == "__main__":
    initialize_game()
    game_loop()