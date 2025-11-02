import pygame
from src import config
from src.game import Game

def main():
    try:
        # Validate configuration at startup
        config.validate()
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running the game: {e}")
        pygame.quit()

if __name__ == '__main__':
    main()
