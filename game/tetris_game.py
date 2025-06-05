import pygame
from .config import Config
from .game_logic import GameLogic
from .slot_machine import SlotMachine

# Piece is used by GameLogic.
# AssetManager, Renderer, UIManager, PopupManager are passed in constructor.


# --- Tetris Game Class ---
class TetrisGame:
    def __init__(self, surface, assets, renderer, ui_manager, popup_manager):
        self.surface = surface
        self.assets = assets  # AssetManager instance
        self.renderer = renderer  # Renderer instance
        self.ui_manager = ui_manager  # UIManager instance
        self.popup_manager = popup_manager  # PopupManager instance

        self.game_logic = GameLogic()
        self.clock = pygame.time.Clock()
        self._reset_game_state()

    def _reset_game_state(self):
        self.game_logic = GameLogic()
        self.score = 0
        self.fall_time = 0
        self.level_time = 0  # Time accumulator for increasing fall speed
        self.fall_speed = 0.35  # Initial fall speed (seconds per step)
        self.min_fall_speed = 0.05  # Fastest possible fall speed
        self.speed_increase_interval = 15  # Increase speed every X seconds
        self.speed_increase_amount = 0.015  # Amount to decrease fall_speed by

        self.current_piece = self.game_logic.get_random_piece()
        self.next_piece = self.game_logic.get_random_piece()
        self.held_piece = None
        self.can_hold = True
        self.first_piece_placed = False

        self.popup_manager.popups.clear()  # Clear any existing popups

        self.start_time_ticks = pygame.time.get_ticks()  # For survival time
        self.total_lines_cleared = 0
        self.pause_start_time = 0
        self.paused_duration = 0  # Accumulate total paused time

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit_application"

            if event.type == pygame.KEYDOWN:
                if (
                    not self.current_piece
                ):  # No piece to control (should not happen in active game)
                    continue

                if event.key == pygame.K_ESCAPE:
                    self.pause_start_time = pygame.time.get_ticks()
                    action = self.ui_manager.pause_menu()  # Show pause menu
                    self.paused_duration += (
                        pygame.time.get_ticks() - self.pause_start_time
                    )

                    if action == "new_game":
                        return "new_game"
                    if action == "exit_game":
                        return "main_menu"  # Exit to main menu from pause
                    # If "resume", action is None or "resume", game continues
                    if action == "resume":
                        self.assets.play_sound("tap")

                elif event.key == pygame.K_LEFT:
                    self.current_piece.x -= 1
                    if not self.game_logic.valid_space(self.current_piece):
                        self.current_piece.x += 1  # Revert if invalid
                    else:
                        self.assets.play_sound("tap")

                elif event.key == pygame.K_RIGHT:
                    self.current_piece.x += 1
                    if not self.game_logic.valid_space(self.current_piece):
                        self.current_piece.x -= 1  # Revert
                    else:
                        self.assets.play_sound("tap")

                elif event.key == pygame.K_DOWN:  # Soft drop
                    self.current_piece.y += 1
                    if not self.game_logic.valid_space(self.current_piece):
                        self.current_piece.y -= 1  # Revert
                        return (
                            "lock_piece"  # Attempt to lock if soft drop hits something
                        )
                    else:
                        self.score += 1  # Small score for soft drop
                        self.fall_time = 0  # Reset fall timer for responsiveness
                        # No sound for soft drop to avoid noise

                elif event.key == pygame.K_UP:  # Rotate
                    original_rotation = self.current_piece.rotation
                    self.current_piece.rotation = (
                        self.current_piece.rotation + 1
                    ) % len(self.current_piece.shape_format)
                    if not self.game_logic.valid_space(self.current_piece):
                        # Try wall kicks (simple ones)
                        kicks = [
                            (0, 0),
                            (-1, 0),
                            (1, 0),
                            (-2, 0),
                            (2, 0),
                            (0, -1),
                            (0, -2),
                        ]  # Basic kicks
                        kicked = False
                        for dx, dy in kicks:
                            self.current_piece.x += dx
                            self.current_piece.y += dy
                            if self.game_logic.valid_space(self.current_piece):
                                kicked = True
                                self.assets.play_sound("tap")
                                break
                            self.current_piece.x -= dx  # Revert kick
                            self.current_piece.y -= dy
                        if not kicked:
                            self.current_piece.rotation = (
                                original_rotation  # Revert rotation fully
                            )
                    else:
                        self.assets.play_sound("tap")

                elif event.key == pygame.K_SPACE:  # Hard drop
                    drop_distance = 0
                    while self.game_logic.valid_space(self.current_piece):
                        self.current_piece.y += 1
                        drop_distance += 1
                    self.current_piece.y -= 1  # Move back to last valid position
                    if drop_distance > 0:
                        self.score += drop_distance * 2  # Score for hard drop
                    self.assets.play_sound(
                        "firstblood"
                    )  # Use a distinct sound for hard drop
                    return "lock_piece"

                elif event.key in [
                    pygame.K_LSHIFT,
                    pygame.K_RSHIFT,
                    pygame.K_c,
                ]:  # Hold piece
                    self._hold_piece()
        return None  # No special action from input

    def _hold_piece(self):
        if self.can_hold and self.current_piece:  # Ensure there's a current piece
            self.assets.play_sound("tap")
            # Reset position of the piece being held before swapping
            self.current_piece.x = Config.GRID_COLS // 2
            self.current_piece.y = 1  # Standard spawn y
            self.current_piece.rotation = 0

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

            # Reset new current_piece's position and check validity
            if self.current_piece:
                self.current_piece.x = Config.GRID_COLS // 2
                self.current_piece.y = 1  # Standard spawn y
                self.current_piece.rotation = 0
                if not self.game_logic.valid_space(self.current_piece):
                    # This could be a game over condition if new piece from hold is invalid
                    # For now, rely on the main loop's check_lost or next lock attempt
                    pass
            self.can_hold = False

    def _update_game_state(self):  # Returns True if piece should be locked
        if not self.current_piece:
            return False  # Should not happen

        self.fall_time += self.clock.get_rawtime()
        self.level_time += self.clock.get_rawtime()

        # Increase game speed over time
        if self.level_time / 1000 > self.speed_increase_interval:
            self.level_time = 0  # Reset timer for next speed increase
            if self.fall_speed > self.min_fall_speed:
                self.fall_speed = max(
                    self.min_fall_speed, self.fall_speed - self.speed_increase_amount
                )

        if self.fall_time / 1000 >= self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not self.game_logic.valid_space(self.current_piece):
                self.current_piece.y -= 1  # Revert move
                return True  # Signal to lock piece
        return False  # Piece still falling or move was valid

    def _handle_piece_locked(self):  # Returns True if game over after lock
        if not self.current_piece:
            return False

        self.game_logic.lock_piece(self.current_piece)
        # Sound for locking piece (hard drop has its own sound)
        # self.assets.play_sound("tap") # Already played by hard drop or move validation

        if not self.first_piece_placed:
            self.assets.play_sound("firstblood")
            self.popup_manager.create_popup(
                "FIRST BLOOD!", color=(220, 20, 60), size=60
            )
            self.first_piece_placed = True

        lines = self.game_logic.clear_rows()
        self.total_lines_cleared += lines
        if lines > 0:
            base_scores = {1: 100, 2: 300, 3: 500, 4: 800}  # Standard Tetris scoring
            self.score += base_scores.get(lines, 0) * (
                self.total_lines_cleared // 10 + 1
            )  # Basic level multiplier

            line_sounds = {
                1: "humiliation",
                2: "multi_kill",
                3: "mega_kill",
                4: "ultra_kill",
            }
            line_popups = {1: "SINGLE!", 2: "DOUBLE!", 3: "TRIPLE!", 4: "TETRIS!"}
            line_colors = {
                1: (150, 150, 255),
                2: (100, 255, 100),
                3: (255, 150, 50),
                4: (255, 50, 255),
            }
            popup_size = 50 + lines * 10  # Larger popups for more lines

            self.assets.play_sound(line_sounds.get(lines, "tap"))
            self.popup_manager.create_popup(
                line_popups.get(lines, f"{lines} LINES!"),
                color=line_colors.get(lines, (200, 200, 200)),
                size=popup_size,
            )

        self.current_piece = self.next_piece
        self.next_piece = self.game_logic.get_random_piece()
        self.can_hold = True

        # Check if the new piece is immediately invalid (game over)
        if self.current_piece and not self.game_logic.valid_space(self.current_piece):
            return True  # Game Over

        # Also check general game over condition (stack too high)
        if self.game_logic.check_lost():
            return True  # Game Over

        return False  # Game continues

    def run_game(self):
        self._reset_game_state()  # Ensure fresh state for each game run
        running = True

        while running:
            self.clock.tick(60)  # Target FPS

            input_action = self._handle_input()

            if input_action == "quit_application":
                return "quit_application", self.score
            if input_action == "new_game":
                self._reset_game_state()  # Full reset for new game
                continue  # Restart game loop immediately
            if input_action == "main_menu":
                return "main_menu", self.score

            should_lock_piece = False
            if (
                input_action == "lock_piece"
            ):  # From hard drop or soft drop hitting bottom
                should_lock_piece = True

            if not should_lock_piece:  # If not locked by input, check natural fall
                should_lock_piece = self._update_game_state()

            if should_lock_piece:
                if self._handle_piece_locked():  # If game over after locking
                    running = False  # Exit game loop for game over sequence
                    # No break here, let it draw one last frame then go to game over

            # Drawing
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

            # Check for game over if not already triggered by piece lock
            if running and self.game_logic.check_lost():
                running = False

                # --- Game Over Sequence ---
        self.assets.play_sound("oneandonly")  # Game over sound
        # Final draw before showing game over screen
        self.renderer.draw_main_tetris_window(
            self.game_logic.grid,
            self.score,
            None,
            self.next_piece,
            self.held_piece,
            self.game_logic,
        )
        self.renderer.draw_text_middle(
            "GAME OVER", 60, (255, 0, 0), "impact", True, y_offset=-20
        )
        self.popup_manager.draw_popups(self.surface)
        pygame.display.update()
        pygame.time.delay(2500)  # Pause to show final state

        # Calculate survival time accurately considering pauses
        total_elapsed_ticks = (
            pygame.time.get_ticks() - self.start_time_ticks - self.paused_duration
        )
        time_survived_seconds = total_elapsed_ticks / 1000.0
        time_survived_str = f"{time_survived_seconds:.1f}s"

        final_score_val, next_action_after_game_over = self.ui_manager.game_over_screen(
            self.score, self.total_lines_cleared, time_survived_str
        )

        if next_action_after_game_over == "play_slots":
            slot_machine = SlotMachine(
                self.surface, self.renderer, self.assets, final_score_val
            )
            final_score_val = slot_machine.play()  # Score can change after slots
            return "main_menu", final_score_val  # Always go to main menu after slots
        elif next_action_after_game_over == "new_game":
            return "game", 0  # Signal to start a new game, score resets
        elif next_action_after_game_over == "main_menu":
            return "main_menu", final_score_val

        return (
            "quit_application",
            final_score_val,
        )  # Default or if "exit_game" from game over
