from .config import Config


# --- Piece Class ---
class Piece:
    def __init__(self, column, row, shape_format):
        self.x = column
        self.y = row
        self.shape_format = shape_format
        self.color = Config.SHAPE_COLORS[Config.SHAPES.index(shape_format)]
        self.rotation = 0

    def get_current_shape_matrix(self):
        return self.shape_format[self.rotation % len(self.shape_format)]
