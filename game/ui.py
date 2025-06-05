import pygame
from .config import Config

# Renderer and AssetManager are passed in constructor


# --- UI Manager (Menus, Game Over) ---
class UIManager:
    def __init__(
        self, surface, renderer, asset_manager
    ):  # renderer is Renderer, asset_manager is AssetManager
        self.surface, self.renderer, self.assets = surface, renderer, asset_manager
        self.volume_slider_dragging = False
        self._main_menu_sound_played = (
            False  # Instance variable to track sound for main menu
        )

    def _draw_volume_slider(self, y_pos, width=300):
        slider_x = Config.S_WIDTH // 2 - width // 2
        slider_height = 10
        knob_radius = 12

        # Draw slider bar
        pygame.draw.rect(
            self.surface,
            (100, 100, 100),
            (slider_x, y_pos, width, slider_height),
            border_radius=5,
        )
        pygame.draw.rect(
            self.surface,
            (180, 180, 180),
            (slider_x, y_pos, width, slider_height),
            2,
            border_radius=5,
        )

        # Draw knob
        knob_x_pos = slider_x + int(self.assets.volume * width)
        knob_center_y = y_pos + slider_height // 2

        knob_rect = pygame.Rect(0, 0, knob_radius * 2, knob_radius * 2)
        knob_rect.center = (knob_x_pos, knob_center_y)

        pygame.draw.circle(
            self.surface, (255, 215, 0), (knob_x_pos, knob_center_y), knob_radius
        )  # Gold knob
        pygame.draw.circle(
            self.surface, (255, 255, 255), (knob_x_pos, knob_center_y), knob_radius, 2
        )  # White border

        self.renderer.draw_text(
            f"Volume: {int(self.assets.volume*100)}%",
            24,
            (220, 220, 220),
            slider_x + width + 70,
            knob_center_y,
            center_y=True,
        )
        # Return clickable area for the knob and slider properties for event handling
        return knob_rect, slider_x, width

    def _handle_volume_slider_events(self, event, knob_rect, slider_x, slider_width):
        mouse_pos = pygame.mouse.get_pos()
        # Check click on the wider slider bar area as well for initiating drag
        slider_bar_rect = pygame.Rect(
            slider_x,
            knob_rect.centery - knob_rect.height,
            slider_width,
            knob_rect.height * 2,
        )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if knob_rect.collidepoint(mouse_pos) or slider_bar_rect.collidepoint(
                mouse_pos
            ):
                self.volume_slider_dragging = True
                # Immediately update volume if clicked on bar
                new_volume = max(
                    0.0, min(1.0, (mouse_pos[0] - slider_x) / slider_width)
                )
                self.assets.set_volume(new_volume)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.volume_slider_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.volume_slider_dragging:
            new_volume = max(0.0, min(1.0, (mouse_pos[0] - slider_x) / slider_width))
            self.assets.set_volume(new_volume)

    def main_menu(self):
        if not self._main_menu_sound_played:
            self.assets.play_sound("prepare")
            self._main_menu_sound_played = (
                True  # Ensure it plays only once per UIManager instance or app session
            )

        running, clock = True, pygame.time.Clock()
        title_font_size = 90
        option_font_size = 26

        # Simple button rects for hover/click feedback if desired later
        start_rect = pygame.Rect(Config.S_WIDTH / 2 - 150, 360, 300, 50)
        exit_rect = pygame.Rect(Config.S_WIDTH / 2 - 150, 430, 300, 50)

        while running:
            self.surface.fill((10, 10, 30))  # Dark blue background
            self.renderer.draw_text(
                "TETRIS",
                title_font_size,
                (255, 255, 255),
                Config.S_WIDTH / 2,
                180,
                "impact",
                True,
                True,
            )
            self.renderer.draw_text(
                "Are you ready to play?",
                option_font_size - 5,
                (200, 200, 255),
                Config.S_WIDTH / 2,
                280,
                center_x=True,
                center_y=True,
            )

            # Draw buttons (text for now, can be enhanced with rects)
            pygame.draw.rect(self.surface, (0, 100, 200), start_rect, border_radius=5)
            self.renderer.draw_text(
                "Press SPACE to Start",
                option_font_size,
                (255, 255, 255),
                start_rect.centerx,
                start_rect.centery,
                center_x=True,
                center_y=True,
            )

            pygame.draw.rect(self.surface, (150, 0, 50), exit_rect, border_radius=5)
            self.renderer.draw_text(
                "Press ESC to Exit",
                option_font_size,
                (255, 255, 255),
                exit_rect.centerx,
                exit_rect.centery,
                center_x=True,
                center_y=True,
            )

            knob_r, sx, sw = self._draw_volume_slider(Config.S_HEIGHT - 100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"  # Signal to exit application
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.assets.play_sound("tap")
                        return "start_game"
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
                self._handle_volume_slider_events(event, knob_r, sx, sw)

            pygame.display.update()
            clock.tick(30)
        return "exit"  # Default return if loop broken unexpectedly

    def _create_menu_buttons(self, items, start_y, font_size=40, padding=70):
        buttons = []
        font = self.assets.get_font("comicsans", font_size, bold=True)
        for i, (text, action) in enumerate(items):
            label = font.render(text, True, (220, 220, 255))  # Light blue text

            # Create a rect for the button for collision detection and drawing
            rect_width = 300
            rect_height = 50
            rect = pygame.Rect(0, 0, rect_width, rect_height)
            rect.center = (Config.S_WIDTH // 2, start_y + i * padding)

            buttons.append(
                {"label_surface": label, "rect": rect, "action": action, "text": text}
            )
        return buttons

    def pause_menu(self):
        paused, clock = True, pygame.time.Clock()

        # Create a semi-transparent overlay for the pause screen
        overlay = pygame.Surface((Config.S_WIDTH, Config.S_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha for transparency

        buttons = self._create_menu_buttons(
            [
                ("Resume", "resume"),
                ("New Game", "new_game"),
                ("Exit to Main Menu", "exit_game"),
            ],
            start_y=Config.S_HEIGHT // 2 - 100,
            font_size=35,
        )

        while paused:
            self.surface.blit(overlay, (0, 0))  # Draw overlay first

            self.renderer.draw_text(
                "PAUSED",
                70,
                (255, 255, 255),
                Config.S_WIDTH / 2,
                Config.S_HEIGHT // 2 - 200,
                "impact",
                True,
                True,
            )

            mouse_pos = pygame.mouse.get_pos()
            for btn in buttons:
                button_color = (50, 50, 100)  # Default button color
                if btn["rect"].collidepoint(mouse_pos):
                    button_color = (80, 80, 150)  # Hover color

                pygame.draw.rect(
                    self.surface, button_color, btn["rect"], border_radius=5
                )
                pygame.draw.rect(
                    self.surface, (150, 150, 200), btn["rect"], 2, border_radius=5
                )  # Border

                # Center text on button
                text_surf = btn["label_surface"]
                text_rect = text_surf.get_rect(center=btn["rect"].center)
                self.surface.blit(text_surf, text_rect)

            knob_r, sx, sw = self._draw_volume_slider(Config.S_HEIGHT - 100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit_game"  # Or "quit_application" if you want to close everything
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Escape to resume
                        self.assets.play_sound("tap")
                        return "resume"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in buttons:
                        if btn["rect"].collidepoint(event.pos):
                            self.assets.play_sound("tap")
                            return btn["action"]
                self._handle_volume_slider_events(event, knob_r, sx, sw)

            pygame.display.update()
            clock.tick(30)
        return "resume"  # Default if loop breaks

    def game_over_screen(
        self, score, lines, time_survived_str
    ):  # time_survived is now string
        running, clock = True, pygame.time.Clock()

        buttons = self._create_menu_buttons(
            [
                ("Try Slots!", "play_slots"),
                ("Play Again", "new_game"),
                ("Main Menu", "main_menu"),
            ],
            start_y=Config.S_HEIGHT // 2 + 50,
            font_size=30,
            padding=60,
        )

        while running:
            self.surface.fill((30, 0, 0))  # Dark red background for game over
            self.renderer.draw_text(
                "GAME OVER",
                80,
                (200, 0, 0),
                Config.S_WIDTH // 2,
                100,
                "impact",
                True,
                True,
            )

            stats_y_start = 180
            self.renderer.draw_text(
                f"Survival Time: {time_survived_str}",
                30,
                (220, 220, 220),
                Config.S_WIDTH // 2,
                stats_y_start,
                center_x=True,
            )
            self.renderer.draw_text(
                f"Lines Cleared: {lines}",
                30,
                (220, 220, 220),
                Config.S_WIDTH // 2,
                stats_y_start + 40,
                center_x=True,
            )
            self.renderer.draw_text(
                f"Final Score: {score}",
                45,
                (255, 220, 0),
                Config.S_WIDTH // 2,
                stats_y_start + 90,
                "impact",
                True,
                True,
            )

            mouse_pos = pygame.mouse.get_pos()
            for btn in buttons:
                button_color = (100, 20, 20)
                if btn["rect"].collidepoint(mouse_pos):
                    button_color = (150, 30, 30)

                pygame.draw.rect(
                    self.surface, button_color, btn["rect"], border_radius=5
                )
                pygame.draw.rect(
                    self.surface, (200, 100, 100), btn["rect"], 2, border_radius=5
                )

                text_surf = btn["label_surface"]
                text_rect = text_surf.get_rect(center=btn["rect"].center)
                self.surface.blit(text_surf, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return score, "exit_game"  # Return score and action
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in buttons:
                        if btn["rect"].collidepoint(event.pos):
                            self.assets.play_sound("tap")
                            return (
                                score,
                                btn["action"],
                            )  # Return score and selected action

            pygame.display.update()
            clock.tick(30)
        return score, "main_menu"  # Default return
