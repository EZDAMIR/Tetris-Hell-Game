import pygame
import random
import math
from collections import Counter


# --- Configuration ---
class Config:
    S_WIDTH = 800
    S_HEIGHT = 700
    PLAY_WIDTH = 300
    PLAY_HEIGHT = 600
    BLOCK_SIZE = 30

    TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
    TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT

    GRID_ROWS = 20
    GRID_COLS = 10

    # Shape formats
    S_SHAPE = [
        [".....", ".....", "..00.", ".00..", "....."],
        [".....", "..0..", "..00.", "...0.", "....."],
    ]
    Z_SHAPE = [
        [".....", ".....", ".00..", "..00.", "....."],
        [".....", "..0..", ".00..", ".0...", "....."],
    ]
    I_SHAPE = [
        ["..0..", "..0..", "..0..", "..0..", "....."],
        [".....", "0000.", ".....", ".....", "....."],
    ]
    O_SHAPE = [[".....", ".....", ".00..", ".00..", "....."]]
    J_SHAPE = [
        [".....", ".0...", ".000.", ".....", "....."],
        [".....", "..00.", "..0..", "..0..", "....."],
        [".....", ".....", ".000.", "...0.", "....."],
        [".....", "..0..", "..0..", ".00..", "....."],
    ]
    L_SHAPE = [
        [".....", "...0.", ".000.", ".....", "....."],
        [".....", "..0..", "..0..", "..00.", "....."],
        [".....", ".....", ".000.", ".0...", "....."],
        [".....", ".00..", "..0..", "..0..", "....."],
    ]
    T_SHAPE = [
        [".....", "..0..", ".000.", ".....", "....."],
        [".....", "..0..", "..00.", "..0..", "....."],
        [".....", ".....", ".000.", "..0..", "....."],
        [".....", "..0..", ".00..", "..0..", "....."],
    ]

    SHAPES = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, J_SHAPE, L_SHAPE, T_SHAPE]
    SHAPE_COLORS = [
        (0, 255, 0),
        (255, 0, 0),
        (0, 255, 255),
        (255, 255, 0),
        (255, 165, 0),
        (0, 0, 255),
        (128, 0, 128),
    ]

    SLOT_SYMBOLS = ["🍒", "🍊", "🍋", "🍇", "💎", "7️⃣"]
    SLOT_VALUES = {"🍒": 0, "🍊": 1, "🍋": 1.5, "🍇": 4, "💎": 25, "7️⃣": 100}
    SLOT_WEIGHTS = [40, 30, 15, 10, 4, 1]


# --- Asset Manager ---
class AssetManager:
    def __init__(self):
        pygame.mixer.init()
        pygame.font.init()
        self.sounds = {
            "humiliation": pygame.mixer.Sound("resources/sounds/misc/humiliation.wav"),
            "multi_kill": pygame.mixer.Sound("resources/sounds/misc/multikill.wav"),
            "mega_kill": pygame.mixer.Sound("resources/sounds/misc/megakill.wav"),
            "ultra_kill": pygame.mixer.Sound("resources/sounds/misc/ultrakill.wav"),
            "monster_kill": pygame.mixer.Sound("resources/sounds/misc/monsterkill.wav"),
            "godlike": pygame.mixer.Sound("resources/sounds/misc/godlike.wav"),
            "holyshit": pygame.mixer.Sound("resources/sounds/misc/holyshit.wav"),
            "killing_spree": pygame.mixer.Sound(
                "resources/sounds/misc/killingspree.wav"
            ),
            "ludacriss_kill": pygame.mixer.Sound(
                "resources/sounds/misc/ludacrisskill.wav"
            ),
            "rampage": pygame.mixer.Sound("resources/sounds/misc/rampage.wav"),
            "unstoppable": pygame.mixer.Sound("resources/sounds/misc/unstoppable.wav"),
            "wicked_sick": pygame.mixer.Sound("resources/sounds/misc/wickedsick.wav"),
            "oneandonly": pygame.mixer.Sound("resources/sounds/misc/oneandonly.wav"),
            "prepare": pygame.mixer.Sound("resources/sounds/misc/prepare.wav"),
            "firstblood": pygame.mixer.Sound("resources/sounds/misc/firstblood.wav"),
            "tap": pygame.mixer.Sound("resources/sounds/misc/tap.wav"),
            "gogamble": pygame.mixer.Sound("resources/sounds/misc/gogamble.wav"),
            "dangit": pygame.mixer.Sound("resources/sounds/misc/dangit.wav"),
            "jackpot": pygame.mixer.Sound("resources/sounds/misc/jackpot.wav"),
            "coinhandle": pygame.mixer.Sound("resources/sounds/misc/coinhandle.wav"),
        }
        self.volume = 0.01
        self.set_volume(self.volume)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
        pygame.mixer.music.set_volume(self.volume)

    def get_font(self, name, size, bold=False, italic=False):
        return pygame.font.SysFont(name, size, bold=bold, italic=italic)


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
        return [(pos[0] - 2, pos[1] - 4) for pos in positions]

    def valid_space(self, piece):
        formatted_shape = self.convert_shape_format(piece)
        for x, y in formatted_shape:
            if not (0 <= x < Config.GRID_COLS and 0 <= y < Config.GRID_ROWS):
                if (
                    y >= Config.GRID_ROWS
                ):  # Check if only out of bounds due to being too low
                    return False  # Invalid if below playfield
                if (
                    x < 0 or x >= Config.GRID_COLS
                ):  # Invalid if horizontally out of bounds
                    return False
                # Allow pieces to be above the screen (y < 0)
            if (
                y >= 0 and (x, y) in self.locked_positions
            ):  # Check collision with locked pieces only if inside grid
                return False
        return True

    def check_lost(self):
        for _, y in self.locked_positions:
            if y < 1:
                return True
        return False

    def clear_rows(self):
        rows_cleared_count = 0
        # Iterate from bottom to top
        for r in range(Config.GRID_ROWS - 1, -1, -1):
            is_row_full = True
            for c in range(Config.GRID_COLS):
                if (c, r) not in self.locked_positions:
                    is_row_full = False
                    break

            if is_row_full:
                rows_cleared_count += 1
                # Remove the full row
                for c in range(Config.GRID_COLS):
                    del self.locked_positions[(c, r)]
                # Shift all rows above it down
                for sr in range(r - 1, -1, -1):  # Shifted rows from r-1 down to 0
                    for sc in range(Config.GRID_COLS):
                        if (sc, sr) in self.locked_positions:
                            color = self.locked_positions.pop((sc, sr))
                            self.locked_positions[(sc, sr + 1)] = color

        if rows_cleared_count > 0:
            self.update_grid_from_locked()
        return rows_cleared_count

    def lock_piece(self, piece):
        shape_pos = self.convert_shape_format(piece)
        for pos in shape_pos:
            self.locked_positions[pos] = piece.color
        self.update_grid_from_locked()

    def get_random_piece(self):
        return Piece(Config.GRID_COLS // 2, 1, random.choice(Config.SHAPES))


# --- Renderer ---
class Renderer:
    def __init__(self, surface, asset_manager):
        self.surface = surface
        self.assets = asset_manager

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

    def draw_piece(self, piece, game_logic):
        if not piece:
            return
        shape_pos = game_logic.convert_shape_format(piece)
        for x, y in shape_pos:
            if y > -1:
                # Only draw pieces that are within the visible grid
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

    def _draw_side_panel_piece(self, piece, title, base_sx, base_sy):
        if not piece:
            return
        self.draw_text(title, 30, (255, 255, 255), base_sx + 10, base_sy - 30)
        shape_matrix = piece.get_current_shape_matrix()
        for i, line in enumerate(shape_matrix):
            for j, column_char in enumerate(list(line)):
                if column_char == "0":
                    pygame.draw.rect(
                        self.surface,
                        piece.color,
                        (
                            base_sx
                            + (j - 0) * Config.BLOCK_SIZE,  # Adjusted for 5x5 matrix
                            base_sy + (i - 0) * Config.BLOCK_SIZE,
                            Config.BLOCK_SIZE,
                            Config.BLOCK_SIZE,
                        ),
                        0,
                    )

    def draw_next_shape(self, piece):
        sx = Config.TOP_LEFT_X + Config.PLAY_WIDTH + 50
        sy = Config.TOP_LEFT_Y + Config.PLAY_HEIGHT / 2 - 150  # Adjusted position
        self._draw_side_panel_piece(piece, "Next Shape", sx, sy)

    def draw_held_shape(self, piece):
        sx = Config.TOP_LEFT_X + Config.PLAY_WIDTH + 50
        sy = Config.TOP_LEFT_Y + Config.PLAY_HEIGHT / 2 + 50  # Adjusted position
        self._draw_side_panel_piece(piece, "Held", sx, sy)

    def draw_score(self, score):
        sx = Config.TOP_LEFT_X + Config.PLAY_WIDTH + 125  # Right panel
        sy = Config.TOP_LEFT_Y + 30
        self.draw_text(f"Score: {score}", 30, (255, 255, 255), sx, sy, center_x=True)

    def draw_main_tetris_window(
        self, grid_data, score, current_piece, next_piece, held_piece, game_logic
    ):
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
            (255, 0, 0),
            (
                Config.TOP_LEFT_X,
                Config.TOP_LEFT_Y,
                Config.PLAY_WIDTH,
                Config.PLAY_HEIGHT,
            ),
            5,
        )
        self.draw_next_shape(next_piece)
        self.draw_held_shape(held_piece)


# --- Popup Manager ---
class PopupManager:
    def __init__(self, renderer):
        self.popups = []
        self.renderer = renderer

    def create_popup(self, text, size=75, color=(255, 0, 0), duration=2000):
        font = self.renderer.assets.get_font("impact", size, bold=True)
        label = font.render(text, True, color)
        glow_size = int(size * 1.05)
        glow_font = self.renderer.assets.get_font("impact", glow_size, bold=True)
        glow_color = (
            min(color[0] + 50, 255),
            min(color[1] + 20, 255),
            min(color[2] + 20, 255),
        )
        glow_label = glow_font.render(text, True, glow_color)
        popup_data = {
            "surface": label,
            "glow": glow_label,
            "position": (
                Config.S_WIDTH // 2 - label.get_width() // 2,
                Config.S_HEIGHT // 2 - 100,
            ),
            "start_time": pygame.time.get_ticks(),
            "duration": duration,
            "scale": 0.1,
            "alpha": 255,
        }
        self.popups.append(popup_data)

    def draw_popups(self, surface):
        current_time = pygame.time.get_ticks()
        self.popups = [
            p for p in self.popups if current_time - p["start_time"] <= p["duration"]
        ]

        for popup in self.popups:
            elapsed = current_time - popup["start_time"]
            progress = elapsed / popup["duration"]
            if progress < 0.15:
                scale = min(1.2, popup["scale"] + progress * 7.5)
            elif progress < 0.3:
                scale = max(1.0, 1.2 - (progress - 0.15) * 1.3)
            else:
                scale = 1.0 + 0.05 * abs(math.sin(progress * 6 * math.pi))
            alpha = (
                int(popup["alpha"] * (1 - (progress - 0.7) / 0.3))
                if progress > 0.7
                else popup["alpha"]
            )
            alpha = max(0, min(255, alpha))

            scaled_surface = pygame.transform.smoothscale(
                popup["surface"],
                (
                    int(popup["surface"].get_width() * scale),
                    int(popup["surface"].get_height() * scale),
                ),
            )
            scaled_glow = pygame.transform.smoothscale(
                popup["glow"],
                (
                    int(popup["glow"].get_width() * scale * 1.05),
                    int(popup["glow"].get_height() * scale * 1.05),
                ),
            )
            scaled_surface.set_alpha(alpha)
            scaled_glow.set_alpha(int(alpha * 0.7))

            pos_x = (
                popup["position"][0]
                - (scaled_surface.get_width() - popup["surface"].get_width()) // 2
            )
            pos_y = (
                popup["position"][1]
                - (scaled_surface.get_height() - popup["surface"].get_height()) // 2
            )
            glow_x = pos_x - (scaled_glow.get_width() - scaled_surface.get_width()) // 2
            glow_y = (
                pos_y - (scaled_glow.get_height() - scaled_surface.get_height()) // 2
            )

            for ox, oy in [(4, 4), (3, 5), (5, 3), (2, 6)]:
                shadow = scaled_surface.copy()
                shadow.fill(
                    (10, 0, 0, min(255, int(alpha * (0.5 - ox * 0.05)))),
                    None,
                    pygame.BLEND_RGBA_MULT,
                )
                surface.blit(shadow, (pos_x + ox, pos_y + oy))
            surface.blit(scaled_glow, (glow_x, glow_y))
            surface.blit(scaled_surface, (pos_x, pos_y))


# --- Slot Machine ---
class SlotMachine:
    def __init__(self, surface, renderer, asset_manager, initial_score):
        self.surface = surface
        self.renderer = renderer
        self.assets = asset_manager
        self.score = initial_score
        self.symbols, self.slot_values, self.weights = (
            Config.SLOT_SYMBOLS,
            Config.SLOT_VALUES,
            Config.SLOT_WEIGHTS,
        )
        self.spinning, self.result_message, self.spin_start_time = False, None, 0
        self.spin_duration, self.slots_display = 1000, [
            random.choices(self.symbols, self.weights)[0] for _ in range(3)
        ]
        self.spin_sound_playing, self.cheat_activated = False, False
        self.bet_amount, self.bet_options = 100, [100, 200, 500, 1000]
        self.slot_font = self.assets.get_font("segoe ui symbol", 80)  # Cache font

    def _handle_spin_result(self):
        self.spinning, self.spin_sound_playing = False, False
        if self.cheat_activated:
            self.slots_display, self.cheat_activated = ["7️⃣", "7️⃣", "7️⃣"], False

        if self.slots_display[0] == self.slots_display[1] == self.slots_display[2]:
            multiplier = self.slot_values[self.slots_display[0]]
            winnings = int(self.bet_amount * multiplier)
            self.score += winnings
            if multiplier > 1:
                self.result_message, _ = f"JACKPOT! {multiplier}x MULTIPLIER!", self.assets.play_sound("jackpot")  # type: ignore
            elif multiplier == 1:
                self.result_message = "Got your bet back!"
            else:
                self.result_message = "You lost your bet!"
            if multiplier >= 1:
                self.assets.play_sound(
                    random.choice(["rampage", "godlike", "holyshit", "unstoppable"])
                )
            elif multiplier == 0:
                self.assets.play_sound("dangit")
        else:
            counts = Counter(self.slots_display)
            most_common_symbol, count = counts.most_common(1)[0]
            if count == 2:
                multiplier = self.slot_values[most_common_symbol] * 0.5
                winnings = int(self.bet_amount * multiplier)
                self.score += winnings
                if winnings > 0:
                    self.result_message, _ = f"Two matches! {multiplier:.1f}x your bet!", self.assets.play_sound("jackpot")  # type: ignore
                else:
                    self.result_message, _ = "You lost half your bet!", self.assets.play_sound("dangit")  # type: ignore
            else:
                self.result_message, _ = "No matches. Try again?", self.assets.play_sound("dangit")  # type: ignore

    def _draw_ui(self):
        self.surface.fill((0, 0, 0))
        self.renderer.draw_text(
            "TETRIS SLOT MACHINE",
            40,
            (255, 215, 0),
            Config.S_WIDTH // 2,
            120,
            "impact",
            True,
        )
        self.renderer.draw_text(
            f"Current Score: {self.score}",
            30,
            (255, 255, 255),
            Config.S_WIDTH // 2,
            175,
            center_x=True,
        )

        slot_area = pygame.Rect(Config.S_WIDTH // 2 - 200, 220, 400, 150)
        pygame.draw.rect(self.surface, (50, 50, 50), slot_area)
        pygame.draw.rect(self.surface, (150, 150, 150), slot_area, 5)

        for i, sym_char in enumerate(self.slots_display):
            sym_surf = self.slot_font.render(sym_char, 1, (255, 255, 255))
            self.surface.blit(
                sym_surf,
                (
                    slot_area.x + 70 + i * 120 - sym_surf.get_width() // 2,
                    slot_area.centery - sym_surf.get_height() // 2,
                ),
            )

        if self.result_message:
            self.renderer.draw_text(
                self.result_message,
                35,
                (255, 215, 0),
                Config.S_WIDTH // 2,
                407,
                center_x=True,
            )
            self.renderer.draw_text(
                f"New Score: {self.score}",
                35,
                (255, 255, 255),
                Config.S_WIDTH // 2,
                447,
                center_x=True,
            )

        # Buttons
        self.spin_btn_rect = pygame.Rect(Config.S_WIDTH // 2 - 150, 480, 300, 50)
        self.exit_btn_rect = pygame.Rect(Config.S_WIDTH // 2 - 150, 625, 300, 50)
        self.cheat_btn_rect = pygame.Rect(50, 480, 180, 50)
        self.deposit_btn_rect = pygame.Rect(Config.S_WIDTH - 50 - 180, 480, 180, 50)

        if not self.spinning:
            pygame.draw.rect(self.surface, (0, 128, 0), self.spin_btn_rect)
            self.renderer.draw_text(
                "SPIN AGAIN",
                30,
                (255, 255, 255),
                self.spin_btn_rect.centerx,
                self.spin_btn_rect.centery,
                center_x=True,
                center_y=True,
            )
            pygame.draw.rect(self.surface, (128, 0, 128), self.cheat_btn_rect)
            self.renderer.draw_text(
                "LUCKY SPIN",
                30,
                (255, 255, 255),
                self.cheat_btn_rect.centerx,
                self.cheat_btn_rect.centery,
                center_x=True,
                center_y=True,
            )
            pygame.draw.rect(self.surface, (0, 128, 128), self.deposit_btn_rect)
            self.renderer.draw_text(
                "DEPOSIT +1000",
                30,
                (255, 255, 255),
                self.deposit_btn_rect.centerx,
                self.deposit_btn_rect.centery,
                center_x=True,
                center_y=True,
            )
            for i, bet in enumerate(self.bet_options):
                bet_r = pygame.Rect(50 + i * 150, 550, 100, 50)
                color = (0, 100, 0) if self.bet_amount == bet else (128, 128, 0)
                pygame.draw.rect(self.surface, color, bet_r)
                self.renderer.draw_text(
                    f"BET {bet}",
                    30,
                    (255, 255, 255),
                    bet_r.centerx,
                    bet_r.centery,
                    center_x=True,
                    center_y=True,
                )

        pygame.draw.rect(self.surface, (128, 0, 0), self.exit_btn_rect)
        self.renderer.draw_text(
            "TAKE SCORE & EXIT",
            30,
            (255, 255, 255),
            self.exit_btn_rect.centerx,
            self.exit_btn_rect.centery,
            center_x=True,
            center_y=True,
        )

    def play(self):
        self.assets.play_sound("gogamble")
        running, clock = True, pygame.time.Clock()
        while running:
            time_now = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and not self.spinning
                ):
                    if self.spin_btn_rect.collidepoint(mouse_pos):
                        if self.score >= self.bet_amount:
                            self.score -= self.bet_amount
                            self.spinning = True
                            self.spin_start_time = time_now
                            self.slots_display = [
                                random.choices(self.symbols, self.weights)[0]
                                for _ in range(3)
                            ]
                            self.result_message, self.spin_sound_playing = None, False
                            self.assets.play_sound("tap")
                        else:
                            self.result_message = "Not enough points to spin!"
                    elif self.exit_btn_rect.collidepoint(mouse_pos):
                        return self.score
                    elif self.cheat_btn_rect.collidepoint(mouse_pos):
                        self.cheat_activated, self.spinning, self.spin_start_time = (
                            True,
                            True,
                            time_now,
                        )
                        self.result_message, self.spin_sound_playing = None, False
                        self.assets.play_sound("tap")
                    elif self.deposit_btn_rect.collidepoint(mouse_pos):
                        self.score += 1000
                        self.result_message = "DEPOSIT ADDED! +1000 POINTS!"
                        self.assets.play_sound("coinhandle")
                    else:
                        for i, bet_val in enumerate(self.bet_options):
                            if pygame.Rect(50 + i * 150, 550, 100, 50).collidepoint(
                                mouse_pos
                            ):
                                self.bet_amount, self.result_message = (
                                    bet_val,
                                    f"Bet amount set to {bet_val}",
                                )
                                self.assets.play_sound("tap")
                                break

            if self.spinning:
                if not self.spin_sound_playing:
                    self.assets.play_sound("coinhandle")
                    self.spin_sound_playing = True
                if time_now - self.spin_start_time < self.spin_duration:
                    if (time_now - self.spin_start_time) % 100 < 50:
                        self.slots_display = [
                            random.choices(self.symbols, self.weights)[0]
                            for _ in range(3)
                        ]
                else:
                    self._handle_spin_result()

            self._draw_ui()
            pygame.display.update()
            clock.tick(30)
        return self.score


# --- UI Manager (Menus, Game Over) ---
class UIManager:
    def __init__(self, surface, renderer, asset_manager):
        self.surface, self.renderer, self.assets = surface, renderer, asset_manager
        self.volume_slider_dragging = False

    def _draw_volume_slider(self, y_pos):
        sx, sw, sh, kr = 200, 400, 8, 15
        pygame.draw.rect(self.surface, (180, 180, 180), (sx, y_pos, sw, sh))
        knob_x = int(sx + self.assets.volume * sw)
        knob_r = pygame.Rect(0, 0, kr * 2, kr * 2)
        knob_r.center = (knob_x, y_pos + sh // 2)
        pygame.draw.circle(self.surface, (255, 215, 0), knob_r.center, kr)
        self.renderer.draw_text(
            f"Volume: {int(self.assets.volume*100)}%",
            24,
            (255, 255, 255),
            sx + sw + 30,
            y_pos - 10,
        )
        return knob_r, sx, sw

    def _handle_volume_slider_events(self, event, knob_rect, slider_x, slider_width):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and knob_rect.collidepoint(event.pos)
        ):
            self.volume_slider_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.volume_slider_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.volume_slider_dragging:
            self.assets.set_volume((event.pos[0] - slider_x) / slider_width)

    def main_menu(self):
        if not hasattr(UIManager, "_sound_played"):
            UIManager._sound_played = True
            self.assets.play_sound("prepare")
        running, clock = True, pygame.time.Clock()
        while running:
            self.surface.fill((0, 0, 0))
            self.renderer.draw_text(
                "TETRIS",
                80,
                (255, 255, 255),
                Config.S_WIDTH / 2,
                190,
                center_x=True,
                center_y=True,
            )
            self.renderer.draw_text(
                "Are you ready to play?",
                40,
                (255, 255, 255),
                Config.S_WIDTH / 2,
                320,
                center_x=True,
                center_y=True,
            )
            self.renderer.draw_text(
                "Press SPACE to start",
                40,
                (255, 255, 255),
                Config.S_WIDTH / 2,
                380,
                center_x=True,
                center_y=True,
            )
            self.renderer.draw_text(
                "Press ESC to exit",
                40,
                (255, 255, 255),
                Config.S_WIDTH / 2,
                440,
                center_x=True,
                center_y=True,
            )
            kr, sx, sw = self._draw_volume_slider(600)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return "start_game"
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
                self._handle_volume_slider_events(event, kr, sx, sw)
            pygame.display.update()
            clock.tick(30)
        return "exit"

    def _create_menu_buttons(self, items):
        buttons = []
        font = self.assets.get_font("comicsans", 50)
        for i, (text, action) in enumerate(items):
            label = font.render(text, True, (255, 255, 255))
            rect = label.get_rect(center=(Config.S_WIDTH // 2, 250 + i * 100))
            buttons.append({"label": label, "rect": rect, "action": action})
        return buttons

    def pause_menu(self):
        paused, clock = True, pygame.time.Clock()
        buttons = self._create_menu_buttons(
            [("Resume", "resume"), ("New Game", "new_game"), ("Exit", "exit_game")]
        )
        while paused:
            self.surface.fill((0, 0, 0))
            for btn in buttons:
                self.surface.blit(btn["label"], btn["rect"])
            kr, sx, sw = self._draw_volume_slider(520)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit_game"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "resume"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in buttons:
                        if btn["rect"].collidepoint(event.pos):
                            return btn["action"]
                self._handle_volume_slider_events(event, kr, sx, sw)
            pygame.display.update()
            clock.tick(30)
        return "resume"

    def game_over_screen(self, score, lines, time):
        running, clock = True, pygame.time.Clock()
        slot_btn_rect = pygame.Rect(Config.S_WIDTH // 2 - 150, 450, 300, 50)
        exit_btn_rect = pygame.Rect(Config.S_WIDTH // 2 - 150, 520, 300, 50)
        while running:
            self.surface.fill((0, 0, 0))
            self.renderer.draw_text(
                "GAME OVER", 60, (255, 0, 0), Config.S_WIDTH // 2, 130, "impact", True
            )
            self.renderer.draw_text(
                f"Survival Time: {time:.1f}s",
                40,
                (255, 255, 255),
                Config.S_WIDTH // 2,
                220,
                center_x=True,
            )
            self.renderer.draw_text(
                f"Lines Cleared: {lines}",
                40,
                (255, 255, 255),
                Config.S_WIDTH // 2,
                270,
                center_x=True,
            )
            self.renderer.draw_text(
                f"Final Score: {score}",
                40,
                (255, 255, 255),
                Config.S_WIDTH // 2,
                320,
                center_x=True,
            )
            self.renderer.draw_text(
                "Try Your Luck?",
                20,
                (255, 215, 0),
                Config.S_WIDTH // 2,
                420,
                center_x=True,
            )
            pygame.draw.rect(self.surface, (0, 128, 0), slot_btn_rect)
            self.renderer.draw_text(
                "SPIN THE SLOTS!",
                30,
                (255, 255, 255),
                slot_btn_rect.centerx,
                slot_btn_rect.centery,
                center_x=True,
                center_y=True,
            )
            pygame.draw.rect(self.surface, (128, 0, 0), exit_btn_rect)
            self.renderer.draw_text(
                "EXIT GAME",
                30,
                (255, 255, 255),
                exit_btn_rect.centerx,
                exit_btn_rect.centery,
                center_x=True,
                center_y=True,
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return score, "exit_game"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if slot_btn_rect.collidepoint(event.pos):
                        return score, "play_slots"
                    if exit_btn_rect.collidepoint(event.pos):
                        return score, "exit_game"
            pygame.display.update()
            clock.tick(30)
        return score, "exit_game"


# --- Tetris Game Class ---
class TetrisGame:
    def __init__(self, surface, assets, renderer, ui_manager, popup_manager):
        self.surface, self.assets, self.renderer = surface, assets, renderer
        self.ui_manager, self.popup_manager = ui_manager, popup_manager
        self.game_logic = GameLogic()
        self.clock = pygame.time.Clock()
        self._reset_game_state()  # Initialize all game state variables

    def _reset_game_state(self):
        self.game_logic = GameLogic()  # New grid and locked positions
        self.score, self.fall_time, self.level_time = 0, 0, 0
        self.fall_speed = 0.27
        self.current_piece = self.game_logic.get_random_piece()
        self.next_piece = self.game_logic.get_random_piece()
        self.held_piece, self.can_hold = None, True
        self.first_piece_placed = False
        self.popup_manager.popups.clear()
        self.start_time_ticks = pygame.time.get_ticks()
        self.total_lines_cleared = 0
        self.pause_start_time = 0  # For accurate survival time calculation

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit_application"
            if event.type == pygame.KEYDOWN:
                if not self.current_piece:
                    continue
                if event.key == pygame.K_ESCAPE:
                    self.pause_start_time = pygame.time.get_ticks()
                    action = self.ui_manager.pause_menu()
                    self.start_time_ticks += (
                        pygame.time.get_ticks() - self.pause_start_time
                    )  # Adjust for pause duration
                    if action == "new_game":
                        return "new_game"
                    if action == "exit_game":
                        return "quit_application"
                elif event.key == pygame.K_LEFT:
                    self.current_piece.x -= 1
                    self._validate_move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.current_piece.x += 1
                    self._validate_move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.current_piece.y += 1
                    self._validate_move(0, 1, soft_drop=True)
                elif event.key == pygame.K_UP:
                    self._rotate_piece()
                elif event.key == pygame.K_SPACE:
                    return self._hard_drop()
                elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_c]:
                    self._hold_piece()
        return None

    def _validate_move(self, dx, dy, soft_drop=False):
        if not self.game_logic.valid_space(self.current_piece):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            if (
                dy > 0 and not soft_drop
            ):  # If move was downwards and invalid (hit something)
                return True  # Signal to lock piece
        elif soft_drop:
            self.fall_time = 0  # Reset fall timer for responsive soft drop
        return False  # Move was valid or corrected

    def _rotate_piece(self):
        original_rotation = self.current_piece.rotation
        self.current_piece.rotation = (self.current_piece.rotation + 1) % len(
            self.current_piece.shape_format
        )
        if not self.game_logic.valid_space(self.current_piece):
            self.current_piece.rotation = original_rotation  # Revert

    def _hard_drop(self):
        while self.game_logic.valid_space(self.current_piece):
            self.current_piece.y += 1
        self.current_piece.y -= 1
        return "lock_piece"

    def _hold_piece(self):
        if self.can_hold:
            if self.held_piece is None:
                self.held_piece, self.current_piece = (
                    self.current_piece,
                    self.next_piece,
                )
                self.next_piece = self.game_logic.get_random_piece()
            else:
                self.held_piece, self.current_piece = (
                    self.current_piece,
                    self.held_piece,
                )
            self.held_piece.x, self.held_piece.y = Config.GRID_COLS // 2, 0
            # Ensure new current piece is valid, if not, it might be game over or needs adjustment
            if (
                not self.game_logic.valid_space(self.current_piece)
                and self.current_piece is not None
            ):
                # This is a tricky state, could be game over if no valid spot.
                # For simplicity, we assume it will be caught by check_lost or next valid_space check.
                pass
            self.can_hold = False

    def _update_game_state(self):
        if not self.current_piece:
            return False
        self.fall_time += self.clock.get_rawtime()
        self.level_time += self.clock.get_rawtime()
        if self.level_time / 1000 > 4:
            self.level_time = 0
            self.fall_speed = max(0.12, self.fall_speed - 0.005)

        if self.fall_time / 1000 >= self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not self.game_logic.valid_space(self.current_piece):
                self.current_piece.y -= 1
                return True  # Signal to lock piece
        return False

    def _handle_piece_locked(self):
        self.game_logic.lock_piece(self.current_piece)
        self.assets.play_sound("tap")
        if not self.first_piece_placed:
            self.assets.play_sound("firstblood")
            self.popup_manager.create_popup("FIRST BLOOD!", color=(220, 20, 60))
            self.first_piece_placed = True

        lines = self.game_logic.clear_rows()
        self.total_lines_cleared += lines
        if lines > 0:
            sounds = ["humiliation", "multi_kill", "mega_kill", "ultra_kill"]
            popups = ["HUMILIATION!", "MULTI KILL!", "MEGA KILL!", "ULTRA KILL!"]
            scores = [100, 300, 500, 800]
            colors = [(255, 100, 100), (255, 50, 50), (255, 20, 20), (200, 0, 0)]
            idx = min(lines - 1, len(sounds) - 1)
            self.score += scores[idx]
            self.assets.play_sound(sounds[idx])
            self.popup_manager.create_popup(popups[idx], color=colors[idx])

        self.current_piece, self.next_piece = (
            self.next_piece,
            self.game_logic.get_random_piece(),
        )
        self.can_hold = True
        if self.current_piece and not self.game_logic.valid_space(
            self.current_piece
        ):  # New piece causes immediate game over
            return True
        return False  # Game continues

    def run_game(self):
        self._reset_game_state()
        running = True
        while running:
            action = self._handle_input()
            if action == "quit_application":
                return "quit_application", self.score
            if action == "new_game":
                self._reset_game_state()
                continue
            if action == "lock_piece" and self._handle_piece_locked():
                running = False
                break

            if self._update_game_state() and self._handle_piece_locked():
                running = False
                break

            self.renderer.draw_main_tetris_window(
                self.game_logic.grid,
                self.score,
                self.current_piece,
                self.next_piece,
                self.held_piece,
                self.game_logic,
            )
            self.popup_manager.draw_popups(self.surface)
            pygame.display.update()
            if self.game_logic.check_lost():
                running = False
            self.clock.tick(60)

        self.assets.play_sound("oneandonly")
        self.renderer.draw_text_middle(
            "You Lost", 40, (255, 255, 255), y_offset=-50
        )  # Draw on top
        self.popup_manager.draw_popups(self.surface)  # Draw any lingering popups
        pygame.display.update()
        pygame.time.delay(2000)

        time_survived = (pygame.time.get_ticks() - self.start_time_ticks) / 1000.0
        final_score, next_action = self.ui_manager.game_over_screen(
            self.score, self.total_lines_cleared, time_survived
        )
        if next_action == "play_slots":
            slot_machine = SlotMachine(
                self.surface, self.renderer, self.assets, final_score
            )
            final_score = slot_machine.play()
            return "main_menu", final_score
        return (
            "quit_application" if next_action == "exit_game" else "main_menu"
        ), final_score


# --- Main Application ---
class Application:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((Config.S_WIDTH, Config.S_HEIGHT))
        pygame.display.set_caption("Tetris Refactored")
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
        self.current_score = 0

    def run(self):
        current_view, running = "main_menu", True
        while running:
            if current_view == "main_menu":
                action = self.ui_manager.main_menu()
                if action == "start_game":
                    current_view = "game"
                elif action == "exit":
                    running = False
            elif current_view == "game":
                next_view, self.current_score = self.tetris_game.run_game()
                if next_view == "quit_application":
                    running = False
                else:
                    current_view = next_view
        pygame.quit()


if __name__ == "__main__":
    app = Application()
    app.run()
