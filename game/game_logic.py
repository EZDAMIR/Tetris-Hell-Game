import random
from .config import Config
from .piece import Piece


# --- Game Logic (Grid, Validation, etc.) ---
class GameLogic:
    def __init__(self):
        self.grid = self._create_empty_grid()
        self.locked_positions = {}

    def _create_empty_grid(self):
        return [
            [(0, 0, 0) for _ in range(Config.GRID_COLS)]
            for _ in range(Config.GRID_ROWS)
        ]

    def update_grid_from_locked(self):
        self.grid = self._create_empty_grid()
        for (c, r), color in self.locked_positions.items():
            if 0 <= r < Config.GRID_ROWS and 0 <= c < Config.GRID_COLS:
                self.grid[r][c] = color
        return self.grid

    def convert_shape_format(self, piece):
        positions = []
        shape_matrix = piece.get_current_shape_matrix()
        for i, line in enumerate(shape_matrix):
            for j, column_char in enumerate(list(line)):
                if column_char == "0":
                    positions.append((piece.x + j, piece.y + i))
        # Adjust positions based on the 5x5 matrix representation
        # where (0,0) in the matrix corresponds to the piece's (x,y)
        # and the actual shape is offset within the matrix.
        # The offset (-2, -4) seems to be specific to how shapes are defined and drawn.
        return [(pos[0] - 2, pos[1] - 4) for pos in positions]

    def valid_space(self, piece):
        formatted_shape = self.convert_shape_format(piece)
        for x, y in formatted_shape:
            if not (0 <= x < Config.GRID_COLS and 0 <= y < Config.GRID_ROWS):
                if y >= Config.GRID_ROWS:  # Piece is too low
                    return False
                if (
                    x < 0 or x >= Config.GRID_COLS
                ):  # Piece is horizontally out of bounds
                    return False
                # Allow pieces to be above the screen (y < 0) during spawn
            elif (
                y >= 0 and (x, y) in self.locked_positions
            ):  # Check collision with locked pieces only if inside grid
                return False
        return True

    def check_lost(self):
        # Game is lost if any locked piece is above the visible play area (e.g., at row 0 or -1)
        # Assuming row 0 is the topmost visible row.
        for _, r_coord in self.locked_positions.keys():
            if r_coord < 1:  # If any part of a locked piece is in row 0 or above
                return True
        return False

    def clear_rows(self):
        rows_cleared_count = 0
        # Iterate from bottom to top to correctly handle shifting
        r = Config.GRID_ROWS - 1
        while r >= 0:
            is_row_full = True
            for c in range(Config.GRID_COLS):
                if (c, r) not in self.locked_positions:
                    is_row_full = False
                    break

            if is_row_full:
                rows_cleared_count += 1
                # Remove the full row by deleting its blocks from locked_positions
                for c in range(Config.GRID_COLS):
                    if (c, r) in self.locked_positions:
                        del self.locked_positions[(c, r)]

                # Shift all rows above it down
                # Create a new dictionary for updated positions to avoid modification during iteration issues
                new_locked_positions = {}
                for (lc, lr), color in self.locked_positions.items():
                    if lr < r:  # If the block was above the cleared row
                        new_locked_positions[(lc, lr + 1)] = color  # Move it down
                    else:  # Block was below or not affected
                        new_locked_positions[(lc, lr)] = color
                self.locked_positions = new_locked_positions
                # Don't decrement r here, so the same row index is checked again (as it now contains the row from above)
            else:
                r -= 1  # Move to check the row above

        if rows_cleared_count > 0:
            self.update_grid_from_locked()  # Rebuild the grid array
        return rows_cleared_count

    def lock_piece(self, piece):
        shape_pos = self.convert_shape_format(piece)
        for pos in shape_pos:
            # Only lock parts of the piece that are within the grid boundaries
            if 0 <= pos[0] < Config.GRID_COLS and 0 <= pos[1] < Config.GRID_ROWS:
                self.locked_positions[pos] = piece.color
            elif (
                pos[1] < 0
            ):  # If part of the piece is above the screen when locking (game over)
                # This scenario should ideally be caught by check_lost or valid_space before locking
                pass  # Or handle game over explicitly here if needed
        self.update_grid_from_locked()

    def get_random_piece(self):
        # Start pieces at y=1, consistent with previous logic.
        # The convert_shape_format handles the offset for drawing.
        return Piece(Config.GRID_COLS // 2, 1, random.choice(Config.SHAPES))
