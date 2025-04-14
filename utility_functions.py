import pygame as pyg

# Global variable for running state
running = True

def get_running():
    """Getter for the running state."""
    global running
    return running

def set_running(state):
    """Setter for the running state."""
    global running
    running = state

def menu():
    """
    Displays the menu interface and handles user input.
    """
    global running
    pyg.init()
    screen = pyg.display.set_mode((1280, 720))
    pyg.display.set_caption("Menu - FLAK 88")

    font = pyg.font.Font(None, 36)
    options = ["Spacebar : Quit", "1 : Game Mode 1", "2 : Game Mode 2", "3 : Tutorial", "4 : Story/Animation"]
    selected_option = -1

    while running:
        screen.fill((0, 0, 0))  # Black background

        # Render menu options
        for i, option in enumerate(options):
            text = font.render(option, True, (255, 255, 255))
            screen.blit(text, (50, 50 + i * 50))

        pyg.display.flip()

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                set_running(False)
                return 0 # Quit the game
            elif event.type == pyg.KEYDOWN:
                if event.key == pyg.K_SPACE:
                    return 0  # Quit
                elif event.key == pyg.K_1:
                    return 1  # Game Mode 1
                elif event.key == pyg.K_2:
                    return 2  # Game Mode 2
                elif event.key == pyg.K_3:
                    return 3  # Settings
                elif event.key == pyg.K_4:
                    return 4  # Story/Animation

    pyg.quit()



def load_sprite(file_path):
    """
    Loads a sprite from the specified file path.
    
    Args:
        file_path (str): The path to the sprite image file.
    
    Returns:
        pygame.Surface: The loaded sprite as a Pygame surface.
    
    Raises:
        FileNotFoundError: If the file cannot be found at the specified path.
    """
    try:
        sprite = pyg.image.load(file_path).convert_alpha()  # Load image with transparency
        print(f"Sprite loaded successfully from {file_path}")
        return sprite
    except FileNotFoundError:
        show_error(f"Sprite file not found: {file_path}")
        raise
    except Exception as e:
        show_error(f"Error loading sprite: {e}")
        raise

def show_sprite(screen, sprite, x, y):
    """
    Displays a sprite on the screen at the specified coordinates.
    
    Args:
        screen (pygame.Surface): The Pygame screen where the sprite will be displayed.
        sprite (pygame.Surface): The sprite to display.
        x (int): The x-coordinate for the sprite.
        y (int): The y-coordinate for the sprite.
    """
    try:
        screen.blit(sprite, (x, y))  # Draw the sprite on the screen
        print(f"Sprite displayed at ({x}, {y})")
    except Exception as e:
        show_error(f"Error displaying sprite: {e}")
        raise

def return_menu():
    """
    Closes the current game window and returns to the main menu.
    """
    print("Returning to the main menu...")
    pyg.quit()
    menu()

def show_error(error_code):
    """
    Prints an error message to the console.
    Args:
        error_code (str or int): The error code to display.
    """
    print(f"Error: {error_code}")