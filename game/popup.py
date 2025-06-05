import pygame
import math
from .config import Config

# Renderer is passed in constructor


# --- Popup Manager ---
class PopupManager:
    def __init__(self, renderer):  # renderer is a Renderer instance
        self.popups = []
        self.renderer = renderer

    def create_popup(self, text, size=75, color=(255, 0, 0), duration=2000):
        font = self.renderer.assets.get_font("impact", size, bold=True)
        label = font.render(text, True, color)

        # Glow effect
        glow_size = int(size * 1.05)  # Slightly larger font for glow
        glow_font = self.renderer.assets.get_font("impact", glow_size, bold=True)
        # Brighter/lighter version of the base color for glow
        glow_color = (
            min(color[0] + 50, 255),
            min(color[1] + 20, 255),
            min(color[2] + 20, 255),
        )
        glow_label = glow_font.render(text, True, glow_color)

        popup_data = {
            "surface": label,
            "glow": glow_label,
            "position": (  # Initial position, will be centered based on scaled size later
                Config.S_WIDTH // 2,
                Config.S_HEIGHT // 2 - 100,
            ),
            "start_time": pygame.time.get_ticks(),
            "duration": duration,
            "scale": 0.1,  # Initial scale for animation
            "alpha": 255,  # Initial alpha
        }
        self.popups.append(popup_data)

    def draw_popups(self, surface):
        current_time = pygame.time.get_ticks()
        # Remove expired popups
        self.popups = [
            p for p in self.popups if current_time - p["start_time"] <= p["duration"]
        ]

        for popup in self.popups:
            elapsed = current_time - popup["start_time"]
            progress = elapsed / popup["duration"]

            # Animation: Scale and Alpha
            # Phase 1: Grow quickly (e.g., first 15% of duration)
            if progress < 0.15:
                scale = min(1.2, popup["scale"] + progress * 7.5)  # Rapid growth
            # Phase 2: Shrink slightly to normal size (e.g., next 15%)
            elif progress < 0.3:
                scale = max(1.0, 1.2 - (progress - 0.15) * 1.33)  # Settle back to 1.0
            # Phase 3: Gentle pulse/wobble (e.g., until 70%)
            else:  # progress >= 0.3
                scale = 1.0 + 0.05 * abs(
                    math.sin(progress * 6 * math.pi)
                )  # Gentle pulsing

            # Fade out in the last 30% of duration
            alpha = popup["alpha"]
            if progress > 0.7:
                alpha = int(popup["alpha"] * (1 - (progress - 0.7) / 0.3))

            alpha = max(0, min(255, alpha))  # Clamp alpha

            # Apply scale
            scaled_width = int(popup["surface"].get_width() * scale)
            scaled_height = int(popup["surface"].get_height() * scale)
            scaled_surface = pygame.transform.smoothscale(
                popup["surface"], (scaled_width, scaled_height)
            )

            scaled_glow_width = int(
                popup["glow"].get_width() * scale * 1.05
            )  # Glow slightly larger
            scaled_glow_height = int(popup["glow"].get_height() * scale * 1.05)
            scaled_glow = pygame.transform.smoothscale(
                popup["glow"], (scaled_glow_width, scaled_glow_height)
            )

            # Apply alpha
            scaled_surface.set_alpha(alpha)
            scaled_glow.set_alpha(int(alpha * 0.7))  # Glow is a bit more transparent

            # Recalculate position to keep it centered
            pos_x = popup["position"][0] - scaled_surface.get_width() // 2
            pos_y = popup["position"][1] - scaled_surface.get_height() // 2

            glow_pos_x = popup["position"][0] - scaled_glow.get_width() // 2
            glow_pos_y = popup["position"][1] - scaled_glow.get_height() // 2

            # Simple shadow effect (multiple darker blits offset)
            shadow_alpha = int(alpha * 0.3)
            if shadow_alpha > 0:
                shadow_surface = scaled_surface.copy()
                shadow_surface.fill(
                    (0, 0, 0, shadow_alpha), special_flags=pygame.BLEND_RGBA_MULT
                )
                for offset in [(2, 2), (3, 3), (4, 4)]:  # Multiple shadow layers
                    surface.blit(shadow_surface, (pos_x + offset[0], pos_y + offset[1]))

            surface.blit(scaled_glow, (glow_pos_x, glow_pos_y))
            surface.blit(scaled_surface, (pos_x, pos_y))
