import pygame as pyg
import utility_functions as ufunc
import game_functions as gfunc  

def tutorial():
    """
    Tutorial game mode.
    Explains how to play and launches an easy level to teach mechanics.
    Returns to the menu after completion.
    """
    print("Starting tutorial...")
    pyg.init()
    screen = pyg.display.set_mode((1280, 720))
    pyg.display.set_caption("Tutorial - FLAK 88")

    font = pyg.font.Font(None, 36)
    enemy_kills = 0
    target_kills = 5  # Example target to complete the tutorial

    running = True
    while running:
        screen.fill((0, 0, 0))  # Black background

        # Display tutorial instructions
        text = font.render(f"Enemies killed: {enemy_kills}/{target_kills}", True, (255, 255, 255))
        screen.blit(text, (50, 50))

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                ufunc.set_running(False)
                running = False
            elif event.type == pyg.KEYDOWN:
                if event.key == pyg.K_SPACE:  # Simulate killing an enemy
                    enemy_kills += 1

        if enemy_kills >= target_kills:
            print("Tutorial completed!")
            running = False

        pyg.display.flip()
        pyg.time.delay(100)

    pyg.quit()
    ufunc.return_menu()

def mode_1():
    """
    Game Mode 1.
    Launches a window with the first game mode.
    """
    print("Starting Game Mode 1...")
    pyg.init()
    screen = pyg.display.set_mode((1280, 720))
    pyg.display.set_caption("Game Mode 1 - FLAK 88")

    running = True
    while running:
        screen.fill((0, 0, 0))  # Black background

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                ufunc.set_running(False)
                running = False

        pyg.display.flip()
        pyg.time.delay(100)

    pyg.quit()
    ufunc.return_menu()

def mode_2():
    """
    Game Mode 2.
    Launches a window with the second game mode.
    """
    print("Starting Game Mode 2...")
    pyg.init()
    screen = pyg.display.set_mode((1280, 720))
    pyg.display.set_caption("Game Mode 2 - FLAK 88")

    running = True
    while running:
        screen.fill((0, 0, 0))  # Black background

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                ufunc.set_running(False)
                running = False

        pyg.display.flip()
        pyg.time.delay(100)

    pyg.quit()
    ufunc.return_menu()
    