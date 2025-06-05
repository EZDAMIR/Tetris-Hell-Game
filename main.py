import pygame

from game.config import Config
from game.assets import AssetManager
from game.renderer import Renderer
from game.popup import PopupManager
from game.ui import UIManager
from game.tetris_game import TetrisGame

# GameLogic and Piece are used by other modules, no direct import needed here if Application orchestrates.


# --- Main Application ---
class Application:
    def __init__(self):
        pygame.init()  # Initialize Pygame modules
        self.surface = pygame.display.set_mode((Config.S_WIDTH, Config.S_HEIGHT))
        pygame.display.set_caption("Tetris Deluxe")  # Changed caption

        # Initialize core components
        self.assets = AssetManager()
        self.renderer = Renderer(self.surface, self.assets)
        self.popup_manager = PopupManager(self.renderer)
        self.ui_manager = UIManager(self.surface, self.renderer, self.assets)
        self.tetris_game = TetrisGame(
            self.surface,
            self.assets,
            self.renderer,
            self.ui_manager,
            self.popup_manager,
        )
        # self.current_score = 0 # Score is managed within game states, not needed at app level like this

    def run(self):
        current_view = "main_menu"
        running = True
        last_score = 0  # To carry over score if needed, though Tetris usually resets

        while running:
            if current_view == "main_menu":
                action = self.ui_manager.main_menu()
                if action == "start_game":
                    current_view = "game"
                elif action == "exit":
                    running = False

            elif current_view == "game":
                # tetris_game.run_game() returns (next_view_string, final_score_value)
                next_view_after_game, score_from_game = self.tetris_game.run_game()
                last_score = score_from_game

                if next_view_after_game == "quit_application":
                    running = False
                elif next_view_after_game == "game":  # Play Again from Game Over
                    current_view = (
                        "game"  # Stay in game view, TetrisGame will reset itself
                    )
                else:  # e.g., "main_menu"
                    current_view = next_view_after_game

            # Add other views here if necessary (e.g., settings, high scores)

        pygame.quit()


if __name__ == "__main__":
    app = Application()
    app.run()
