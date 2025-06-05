import pygame
from .config import Config

# Piece, GameLogic, AssetManager are passed as arguments or in constructor


# --- Renderer ---
class Renderer:
    def __init__(self, surface, asset_manager):
        self.surface = surface
        self.assets = asset_manager  # AssetManager instance

    def draw_text(
        self,
        text,
        size,
        color,
        x,
        y,
        font_name="comicsans",
        center_x=False,
        center_y=False,
        bold=False,
    ):
        font = self.assets.get_font(font_name, size, bold=bold)
        label = font.render(text, 1, color)
        text_width, text_height = label.get_size()
        if center_x:
            x -= text_width // 2
        if center_y:
            y -= text_height // 2
        self.surface.blit(label, (x, y))

    def draw_text_middle(
        self, text, size, color, font_name="comicsans", bold=True, y_offset=0
    ):
        x = Config.TOP_LEFT_X + Config.PLAY_WIDTH / 2
        y = Config.TOP_LEFT_Y + Config.PLAY_HEIGHT / 2 + y_offset
        self.draw_text(
            text, size, color, x, y, font_name, center_x=True, center_y=True, bold=bold
        )

    def draw_grid_lines(self):
        sx, sy = Config.TOP_LEFT_X, Config.TOP_LEFT_Y
        for i in range(Config.GRID_ROWS + 1):
            pygame.draw.line(
                self.surface,
                (128, 128, 128),
                (sx, sy + i * Config.BLOCK_SIZE),
                (sx + Config.PLAY_WIDTH, sy + i * Config.BLOCK_SIZE),
            )
        for j in range(Config.GRID_COLS + 1):
            pygame.draw.line(
                self.surface,
                (128, 128, 128),
                (sx + j * Config.BLOCK_SIZE, sy),
                (sx + j * Config.BLOCK_SIZE, sy + Config.PLAY_HEIGHT),
            )

    def draw_playfield_blocks(self, grid_data):
        for r, row_data in enumerate(grid_data):
            for c, color in enumerate(row_data):
                if color != (0, 0, 0):  # Only draw non-empty blocks
                    pygame.draw.rect(
                        self.surface,
                        color,
                        (
                            Config.TOP_LEFT_X + c * Config.BLOCK_SIZE,
                            Config.TOP_LEFT_Y + r * Config.BLOCK_SIZE,
                            Config.BLOCK_SIZE,
                            Config.BLOCK_SIZE,
                        ),
                        0,
                    )

    def draw_piece(
        self, piece, game_logic
    ):  # piece is a Piece instance, game_logic is a GameLogic instance
        if not piece:
            return
        shape_pos = game_logic.convert_shape_format(piece)
        for x, y in shape_pos:
            if (
                y > -1
            ):  # Only draw parts of the piece that are at or below the top edge of the grid (y=0)
                pygame.draw.rect(
                    self.surface,
                    piece.color,
                    (
                        Config.TOP_LEFT_X + x * Config.BLOCK_SIZE,
                        Config.TOP_LEFT_Y + y * Config.BLOCK_SIZE,
                        Config.BLOCK_SIZE,
                        Config.BLOCK_SIZE,
                    ),
                    0,
                )

    def _draw_side_panel_piece(
        self, piece, title, base_sx, base_sy
    ):  # piece is a Piece instance
        if not piece:
            return
        self.draw_text(
            title, 30, (255, 255, 255), base_sx + 60, base_sy, center_x=True
        )  # Centered title
        shape_matrix = piece.get_current_shape_matrix()

        # Calculate offsets to center the 5x5 matrix in the designated area
        matrix_pixel_width = 5 * Config.BLOCK_SIZE
        matrix_pixel_height = 5 * Config.BLOCK_SIZE
        # Assuming base_sx, base_sy is top-left of a 120x120 box approx (4 blocks wide)
        # Let's try to center it better. Assume a box of 5*BLOCK_SIZE width for the piece display
        offset_x = (
            120 - matrix_pixel_width
        ) // 2  # Example: if panel area is 120px wide
        offset_y = (
            0  # (120 - matrix_pixel_height) // 2 # Example: if panel area is 120px high
        )

        for i, line in enumerate(shape_matrix):
            for j, column_char in enumerate(list(line)):
                if column_char == "0":
                    pygame.draw.rect(
                        self.surface,
                        piece.color,
                        (
                            base_sx + offset_x + j * Config.BLOCK_SIZE,
                            base_sy + offset_y + i * Config.BLOCK_SIZE + 50,
                            Config.BLOCK_SIZE,
                            Config.BLOCK_SIZE,
                        ),
                        0,
                    )

    def draw_next_shape(self, piece):  # piece is a Piece instance
        sx = Config.TOP_LEFT_X + Config.PLAY_WIDTH + 60
        sy = Config.TOP_LEFT_Y + Config.PLAY_HEIGHT / 2 - 200  # Adjusted position
        self._draw_side_panel_piece(piece, "Next Shape", sx, sy)

    def draw_held_shape(self, piece):  # piece is a Piece instance
        sx = Config.TOP_LEFT_X + Config.PLAY_WIDTH + 25  # Adjusted for centering
        sy = Config.TOP_LEFT_Y + Config.PLAY_HEIGHT / 2 + 50 + 30  # Adjusted position
        self._draw_side_panel_piece(piece, "Held", sx, sy)

    def draw_score(self, score):
        sx = Config.TOP_LEFT_X + Config.PLAY_WIDTH + 125  # Right panel
        sy = Config.TOP_LEFT_Y + 30
        self.draw_text(f"Score: {score}", 30, (255, 255, 255), sx, sy, center_x=True)

    def draw_main_tetris_window(
        self, grid_data, score, current_piece, next_piece, held_piece, game_logic
    ):  # current_piece, next_piece, held_piece are Piece instances, game_logic is a GameLogic instance
        self.surface.fill((0, 0, 0))
        self.draw_text(
            "TETRIS", 60, (255, 255, 255), Config.S_WIDTH / 2, 30, center_x=True
        )
        self.draw_score(score)
        self.draw_playfield_blocks(grid_data)
        if current_piece:
            self.draw_piece(current_piece, game_logic)
        self.draw_grid_lines()
        pygame.draw.rect(
            self.surface,
            (255, 0, 0),  # Border color
            (
                Config.TOP_LEFT_X,
                Config.TOP_LEFT_Y,
                Config.PLAY_WIDTH,
                Config.PLAY_HEIGHT,
            ),
            5,  # Border thickness
        )
        self.draw_next_shape(next_piece)
        self.draw_held_shape(held_piece)
