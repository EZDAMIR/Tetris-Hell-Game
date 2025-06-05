import pygame
import random
from collections import Counter
from .config import Config

# Renderer and AssetManager are passed in constructor


# --- Slot Machine ---
class SlotMachine:
    def __init__(
        self, surface, renderer, asset_manager, initial_score
    ):  # renderer is Renderer, asset_manager is AssetManager
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
        self.spin_duration, self.slots_display = 1000, [  # Spin duration in ms
            random.choices(self.symbols, weights=self.weights, k=1)[0] for _ in range(3)
        ]
        self.spin_sound_playing, self.cheat_activated = False, False
        self.bet_amount, self.bet_options = 100, [100, 200, 500, 1000]
        self.slot_font = self.assets.get_font(
            "segoe ui symbol", 80
        )  # Cache font for symbols

    def _handle_spin_result(self):
        self.spinning, self.spin_sound_playing = False, False
        if self.cheat_activated:
            self.slots_display, self.cheat_activated = ["7️⃣", "7️⃣", "7️⃣"], False

        s1, s2, s3 = self.slots_display[0], self.slots_display[1], self.slots_display[2]

        if s1 == s2 == s3:  # Three of a kind
            symbol = s1
            multiplier = self.slot_values.get(symbol, 0)
            winnings = int(self.bet_amount * multiplier)
            self.score += winnings
            if multiplier > 0:
                self.result_message = f"JACKPOT! {multiplier}x WIN!"
                self.assets.play_sound("jackpot")
                if multiplier >= 25:  # Big win sound
                    self.assets.play_sound(random.choice(["godlike", "holyshit"]))
                elif multiplier >= 4:
                    self.assets.play_sound(random.choice(["rampage", "unstoppable"]))
            else:  # Multiplier is 0 (e.g. for Cherries if they pay 0 for 3)
                self.result_message = "No win this time."
                self.assets.play_sound("dangit")

        else:  # Check for two of a kind (simple check, not all slot machine paylines)
            counts = Counter(self.slots_display)
            payout_made = False
            for symbol, count in counts.items():
                if count == 2:
                    # Simplified: any two match gives a small payout (e.g., 0.5x or specific value)
                    # For this example, let's say two of any non-7, non-Diamond pays back half bet
                    # and two 7s or two Diamonds pay 1x bet.
                    two_match_multiplier = 0
                    if symbol == "7️⃣" or symbol == "💎":
                        two_match_multiplier = 1.0
                    elif self.slot_values.get(symbol, 0) > 0:  # Any other paying symbol
                        two_match_multiplier = 0.5

                    if two_match_multiplier > 0:
                        winnings = int(self.bet_amount * two_match_multiplier)
                        self.score += winnings
                        self.result_message = (
                            f"Two {symbol}! {two_match_multiplier:.1f}x bet!"
                        )
                        self.assets.play_sound("tap")  # Smaller win sound
                        payout_made = True
                        break
            if not payout_made:
                self.result_message = "No matches. Try again?"
                self.assets.play_sound("dangit")

    def _draw_ui(self):
        self.surface.fill((20, 0, 40))  # Dark purple background
        self.renderer.draw_text(
            "TETRIS SLOT MACHINE",
            40,
            (255, 215, 0),
            Config.S_WIDTH // 2,
            80,
            "impact",
            True,
        )
        self.renderer.draw_text(
            f"Current Score: {self.score}",
            30,
            (255, 255, 255),
            Config.S_WIDTH // 2,
            130,
            center_x=True,
        )

        # Slot display area
        slot_area_x = Config.S_WIDTH // 2 - 225
        slot_area_y = 180
        slot_width = 140
        slot_spacing = 10

        for i, sym_char in enumerate(self.slots_display):
            rect_x = slot_area_x + i * (slot_width + slot_spacing)
            slot_rect = pygame.Rect(rect_x, slot_area_y, slot_width, 140)
            pygame.draw.rect(
                self.surface, (40, 40, 60), slot_rect
            )  # Darker slot background
            pygame.draw.rect(self.surface, (180, 180, 200), slot_rect, 4)  # Border

            sym_surf = self.slot_font.render(
                sym_char, True, (255, 255, 220)
            )  # Off-white symbols
            self.surface.blit(
                sym_surf,
                (
                    slot_rect.centerx - sym_surf.get_width() // 2,
                    slot_rect.centery - sym_surf.get_height() // 2,
                ),
            )

        if self.result_message:
            self.renderer.draw_text(
                self.result_message,
                35,
                (255, 215, 0),
                Config.S_WIDTH // 2,
                360,
                center_x=True,
            )
            self.renderer.draw_text(  # Display new score below result message
                f"Score: {self.score}",
                30,
                (255, 255, 255),
                Config.S_WIDTH // 2,
                400,
                center_x=True,
            )

        # Buttons
        btn_y_start = 450
        btn_height = 50
        btn_width_main = 280
        btn_width_side = 180

        self.spin_btn_rect = pygame.Rect(
            Config.S_WIDTH // 2 - btn_width_main // 2,
            btn_y_start,
            btn_width_main,
            btn_height,
        )
        self.exit_btn_rect = pygame.Rect(
            Config.S_WIDTH // 2 - btn_width_main // 2,
            btn_y_start + 140,
            btn_width_main,
            btn_height,
        )

        # Side buttons (Cheat, Deposit)
        self.cheat_btn_rect = pygame.Rect(
            self.spin_btn_rect.left - btn_width_side - 20,
            btn_y_start,
            btn_width_side,
            btn_height,
        )
        self.deposit_btn_rect = pygame.Rect(
            self.spin_btn_rect.right + 20, btn_y_start, btn_width_side, btn_height
        )

        # Bet selection buttons
        bet_btn_y = btn_y_start + 70
        bet_btn_width = 100
        num_bet_options = len(self.bet_options)
        total_bet_btns_width = (
            num_bet_options * bet_btn_width + (num_bet_options - 1) * 10
        )
        bet_start_x = Config.S_WIDTH // 2 - total_bet_btns_width // 2

        self.bet_button_rects = []
        for i, bet in enumerate(self.bet_options):
            bet_r = pygame.Rect(
                bet_start_x + i * (bet_btn_width + 10),
                bet_btn_y,
                bet_btn_width,
                btn_height,
            )
            self.bet_button_rects.append(bet_r)
            color = (
                (0, 150, 0) if self.bet_amount == bet else (100, 100, 0)
            )  # Highlight selected bet
            pygame.draw.rect(self.surface, color, bet_r, border_radius=5)
            pygame.draw.rect(
                self.surface, (200, 200, 150), bet_r, 2, border_radius=5
            )  # Border
            self.renderer.draw_text(
                f"{bet}",
                28,
                (255, 255, 255),
                bet_r.centerx,
                bet_r.centery,
                center_x=True,
                center_y=True,
            )
        self.renderer.draw_text(
            f"Current Bet: {self.bet_amount}",
            18,
            (255, 255, 255),
            Config.S_WIDTH // 2,
            bet_btn_y - 25,
            center_x=True,
        )

        if not self.spinning:
            # Spin Button
            pygame.draw.rect(
                self.surface, (0, 180, 0), self.spin_btn_rect, border_radius=5
            )
            pygame.draw.rect(
                self.surface, (100, 255, 100), self.spin_btn_rect, 3, border_radius=5
            )
            self.renderer.draw_text(
                "SPIN!",
                30,
                (255, 255, 255),
                self.spin_btn_rect.centerx,
                self.spin_btn_rect.centery,
                center_x=True,
                center_y=True,
            )

            # Cheat Button
            pygame.draw.rect(
                self.surface, (128, 0, 128), self.cheat_btn_rect, border_radius=5
            )
            pygame.draw.rect(
                self.surface, (200, 100, 200), self.cheat_btn_rect, 3, border_radius=5
            )
            self.renderer.draw_text(
                "LUCKY 7s",
                24,
                (255, 255, 255),
                self.cheat_btn_rect.centerx,
                self.cheat_btn_rect.centery,
                center_x=True,
                center_y=True,
            )

            # Deposit Button
            pygame.draw.rect(
                self.surface, (0, 128, 128), self.deposit_btn_rect, border_radius=5
            )
            pygame.draw.rect(
                self.surface, (100, 200, 200), self.deposit_btn_rect, 3, border_radius=5
            )
            self.renderer.draw_text(
                "+1000 PTS",
                24,
                (255, 255, 255),
                self.deposit_btn_rect.centerx,
                self.deposit_btn_rect.centery,
                center_x=True,
                center_y=True,
            )
        else:  # Dim spin button while spinning
            pygame.draw.rect(
                self.surface, (50, 100, 50), self.spin_btn_rect, border_radius=5
            )
            self.renderer.draw_text(
                "SPINNING...",
                30,
                (150, 150, 150),
                self.spin_btn_rect.centerx,
                self.spin_btn_rect.centery,
                center_x=True,
                center_y=True,
            )

        # Exit Button
        pygame.draw.rect(self.surface, (180, 0, 0), self.exit_btn_rect, border_radius=5)
        pygame.draw.rect(
            self.surface, (255, 100, 100), self.exit_btn_rect, 3, border_radius=5
        )
        self.renderer.draw_text(
            "TAKE SCORE & EXIT",
            28,
            (255, 255, 255),
            self.exit_btn_rect.centerx,
            self.exit_btn_rect.centery,
            center_x=True,
            center_y=True,
        )

    def play(self):
        self.assets.play_sound("gogamble")
        running, clock = True, pygame.time.Clock()
        self.result_message = "Place your bet and spin!"  # Initial message

        while running:
            time_now = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()  # Ensure pygame quits properly
                    exit()  # Exit the script
                if (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                ):  # Left click
                    if not self.spinning:  # Only process clicks if not spinning
                        if self.spin_btn_rect.collidepoint(mouse_pos):
                            if self.score >= self.bet_amount:
                                self.score -= self.bet_amount
                                self.spinning = True
                                self.spin_start_time = time_now
                                # Initial random display before "spinning" animation
                                self.slots_display = [
                                    random.choices(
                                        self.symbols, weights=self.weights, k=1
                                    )[0]
                                    for _ in range(3)
                                ]
                                self.result_message = None  # Clear previous result
                                self.spin_sound_playing = (
                                    False  # Reset for next spin sound
                                )
                                self.assets.play_sound(
                                    "coinhandle"
                                )  # Sound for starting spin
                            else:
                                self.result_message = "Not enough points to spin!"
                                self.assets.play_sound("dangit")

                        elif self.cheat_btn_rect.collidepoint(mouse_pos):
                            # Cheat spin doesn't require bet, for fun
                            self.cheat_activated = True
                            self.spinning = True
                            self.spin_start_time = time_now
                            self.result_message = None
                            self.spin_sound_playing = False
                            self.assets.play_sound("coinhandle")

                        elif self.deposit_btn_rect.collidepoint(mouse_pos):
                            self.score += 1000
                            self.result_message = "DEPOSIT ADDED! +1000 POINTS!"
                            self.assets.play_sound("jackpot")  # Use a positive sound

                        else:  # Check bet buttons
                            for i, bet_r in enumerate(self.bet_button_rects):
                                if bet_r.collidepoint(mouse_pos):
                                    self.bet_amount = self.bet_options[i]
                                    self.result_message = (
                                        f"Bet set to {self.bet_amount}"
                                    )
                                    self.assets.play_sound("tap")
                                    break

                    # Exit button can be clicked even if spinning (though usually not)
                    if self.exit_btn_rect.collidepoint(mouse_pos):
                        return self.score  # Return current score and exit slot machine

            if self.spinning:
                if (
                    not self.spin_sound_playing
                    and (time_now - self.spin_start_time) < self.spin_duration - 200
                ):  # Play during spin, not at the very end
                    # self.assets.play_sound("coinhandle") # Already played at start
                    self.spin_sound_playing = True  # Prevent replaying

                if time_now - self.spin_start_time < self.spin_duration:
                    # Animate slots by changing symbols rapidly
                    if (
                        time_now - self.spin_start_time
                    ) % 100 < 50:  # Change every 100ms for visual effect
                        self.slots_display = [
                            random.choices(self.symbols, weights=self.weights, k=1)[0]
                            for _ in range(3)
                        ]
                else:  # Spin duration ended
                    self._handle_spin_result()  # Determine outcome

            self._draw_ui()
            pygame.display.update()
            clock.tick(30)  # FPS for slot machine screen
        return self.score  # Should be unreachable if exit button works
