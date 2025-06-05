import pygame
import random
import math


"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.mixer.init()
score = 0

volume = 0.5  # Default volume

# Load sounds
humiliation_sound = pygame.mixer.Sound(
    "resources/sounds/misc/humiliation.wav"
)  # 1 line
multi_kill_sound = pygame.mixer.Sound("resources/sounds/misc/multikill.wav")  # 2 lines
mega_kill_sound = pygame.mixer.Sound("resources/sounds/misc/megakill.wav")  # 3 lines
ultra_kill_sound = pygame.mixer.Sound("resources/sounds/misc/ultrakill.wav")
monster_kill_sound = pygame.mixer.Sound("resources/sounds/misc/monsterkill.wav")
godlike_sound = pygame.mixer.Sound("resources/sounds/misc/godlike.wav")
holyshit_sound = pygame.mixer.Sound("resources/sounds/misc/holyshit.wav")
killing_spree_sound = pygame.mixer.Sound("resources/sounds/misc/killingspree.wav")
ludacriss_kill_sound = pygame.mixer.Sound("resources/sounds/misc/ludacrisskill.wav")
rampage_sound = pygame.mixer.Sound("resources/sounds/misc/rampage.wav")
unstoppable_sound = pygame.mixer.Sound("resources/sounds/misc/unstoppable.wav")
wicked_sick_sound = pygame.mixer.Sound("resources/sounds/misc/wickedsick.wav")
oneandonly_sound = pygame.mixer.Sound("resources/sounds/misc/oneandonly.wav")
prepare_sound = pygame.mixer.Sound("resources/sounds/misc/prepare.wav")
firstblood_sound = pygame.mixer.Sound("resources/sounds/misc/firstblood.wav")
tap_sound = pygame.mixer.Sound("resources/sounds/misc/tap.wav")
gogamble_sound = pygame.mixer.Sound("resources/sounds/misc/gogamble.wav")
dangit_sound = pygame.mixer.Sound("resources/sounds/misc/dangit.wav")
jackpot_sound = pygame.mixer.Sound("resources/sounds/misc/jackpot.wav")
coinhandle_sound = pygame.mixer.Sound("resources/sounds/misc/coinhandle.wav")

pygame.font.init()


def set_all_sounds_volume(vol):
    humiliation_sound.set_volume(vol)
    multi_kill_sound.set_volume(vol)
    mega_kill_sound.set_volume(vol)
    ultra_kill_sound.set_volume(vol)
    monster_kill_sound.set_volume(vol)
    godlike_sound.set_volume(vol)
    holyshit_sound.set_volume(vol)
    killing_spree_sound.set_volume(vol)
    ludacriss_kill_sound.set_volume(vol)
    rampage_sound.set_volume(vol)
    unstoppable_sound.set_volume(vol)
    wicked_sick_sound.set_volume(vol)
    oneandonly_sound.set_volume(vol)
    prepare_sound.set_volume(vol)
    firstblood_sound.set_volume(vol)
    tap_sound.set_volume(vol)
    gogamble_sound.set_volume(vol)
    dangit_sound.set_volume(vol)
    jackpot_sound.set_volume(vol)
    coinhandle_sound.set_volume(vol)
    pygame.mixer.music.set_volume(vol)


# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


# SHAPE FORMATS

S = [
    [".....", ".....", "..00.", ".00..", "....."],
    [".....", "..0..", "..00.", "...0.", "....."],
]

Z = [
    [".....", ".....", ".00..", "..00.", "....."],
    [".....", "..0..", ".00..", ".0...", "....."],
]

I = [
    ["..0..", "..0..", "..0..", "..0..", "....."],
    [".....", "0000.", ".....", ".....", "....."],
]

O = [[".....", ".....", ".00..", ".00..", "....."]]

J = [
    [".....", ".0...", ".000.", ".....", "....."],
    [".....", "..00.", "..0..", "..0..", "....."],
    [".....", ".....", ".000.", "...0.", "....."],
    [".....", "..0..", "..0..", ".00..", "....."],
]

L = [
    [".....", "...0.", ".000.", ".....", "....."],
    [".....", "..0..", "..0..", "..00.", "....."],
    [".....", ".....", ".000.", ".0...", "....."],
    [".....", ".00..", "..0..", "..0..", "....."],
]

T = [
    [".....", "..0..", ".000.", ".....", "....."],
    [".....", "..0..", "..00.", "..0..", "....."],
    [".....", ".....", ".000.", "..0..", "....."],
    [".....", "..0..", ".00..", "..0..", "....."],
]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
]
# index 0 - 6 represent shape


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)
    ]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:

            return True
    return False


def get_shape():
    global shapes, shape_colors

    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - (label.get_width() / 2),
            top_left_y + play_height / 2 - label.get_height() / 2,
        ),
    )


def game_statistics(score, lines_cleared, survival_time):
    run = True
    win.fill((0, 0, 0))

    # Statistics display
    title_font = pygame.font.SysFont("impact", 60)
    stats_font = pygame.font.SysFont("comicsans", 40)

    title_text = title_font.render("GAME OVER", 1, (255, 0, 0))
    time_text = stats_font.render(
        f"Survival Time: {survival_time:.1f}s", 1, (255, 255, 255)
    )
    lines_text = stats_font.render(
        f"Lines Cleared: {lines_cleared}", 1, (255, 255, 255)
    )
    score_text = stats_font.render(f"Final Score: {score}", 1, (255, 255, 255))
    slot_text = stats_font.render("Try Your Luck! Triple your score?", 1, (255, 215, 0))

    win.blit(title_text, (s_width // 2 - title_text.get_width() // 2, 100))
    win.blit(time_text, (s_width // 2 - time_text.get_width() // 2, 200))
    win.blit(lines_text, (s_width // 2 - lines_text.get_width() // 2, 250))
    win.blit(score_text, (s_width // 2 - score_text.get_width() // 2, 300))
    win.blit(slot_text, (s_width // 2 - slot_text.get_width() // 2, 400))

    # Button to play slot machine
    button_font = pygame.font.SysFont("comicsans", 30)
    slot_button = button_font.render("SPIN THE SLOTS!", 1, (255, 255, 255))
    exit_button = button_font.render("EXIT GAME", 1, (255, 255, 255))

    slot_button_rect = pygame.Rect(s_width // 2 - 150, 450, 300, 50)
    exit_button_rect = pygame.Rect(s_width // 2 - 150, 520, 300, 50)

    pygame.draw.rect(win, (0, 128, 0), slot_button_rect)
    pygame.draw.rect(win, (128, 0, 0), exit_button_rect)

    win.blit(
        slot_button,
        (
            slot_button_rect.x
            + slot_button_rect.width // 2
            - slot_button.get_width() // 2,
            slot_button_rect.y
            + slot_button_rect.height // 2
            - slot_button.get_height() // 2,
        ),
    )
    win.blit(
        exit_button,
        (
            exit_button_rect.x
            + exit_button_rect.width // 2
            - exit_button.get_width() // 2,
            exit_button_rect.y
            + exit_button_rect.height // 2
            - exit_button.get_height() // 2,
        ),
    )

    pygame.display.update()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if slot_button_rect.collidepoint(mouse_pos):
                    return play_slot_machine(score)
                if exit_button_rect.collidepoint(mouse_pos):
                    return score

    return score


def play_slot_machine(score):
    # Slot machine symbols and odds
    symbols = ["🍒", "🍊", "🍋", "🍇", "💎", "7️⃣"]
    slot_values = {
        "🍒": 0,  # Loss
        "🍊": 1,  # Keep score
        "🍋": 1.5,  # 1.5x multiplier
        "🍇": 4,  # 4x multiplier
        "💎": 25,  # 25x multiplier
        "7️⃣": 100,  # 100x multiplier
    }

    # Probabilities (weighted selection)
    weights = [40, 30, 15, 10, 4, 1]

    run = True
    spinning = False
    result = None
    spin_start_time = 0
    spin_duration = 1000
    slots = [random.choices(symbols, weights)[0] for _ in range(3)]

    spin_sound_playing = False

    # Cheat button variables
    cheat_clicks = 0
    cheat_activated = True

    bet_amount = 100
    bet_options = [100, 200, 500, 1000]

    font = pygame.font.SysFont("segoe ui symbol", 80)  # Font that supports emoji
    title_font = pygame.font.SysFont("impact", 40)
    button_font = pygame.font.SysFont("comicsans", 30)

    gogamble_sound.play()

    while run:
        win.fill((0, 0, 0))

        # Draw title
        title_text = title_font.render("TETRIS SLOT MACHINE", 1, (255, 215, 0))
        win.blit(title_text, (s_width // 2 - title_text.get_width() // 2, 100))

        # Draw score
        score_font = pygame.font.SysFont("comicsans", 30)
        score_text = score_font.render(f"Current Score: {score}", 1, (255, 255, 255))
        win.blit(score_text, (s_width // 2 - score_text.get_width() // 2, 160))

        # Draw slot machine
        slot_rect = pygame.Rect(s_width // 2 - 200, 220, 400, 150)
        pygame.draw.rect(win, (50, 50, 50), slot_rect)
        pygame.draw.rect(win, (150, 150, 150), slot_rect, 5)

        # Draw slots
        current_time = pygame.time.get_ticks()
        if spinning and current_time - spin_start_time < spin_duration:
            # Play spinning sound once when spin starts
            if not spin_sound_playing:
                coinhandle_sound.play()
                spin_sound_playing = True

            # Animate spinning
            if current_time % 100 < 50:  # Change symbols every 100ms
                slots = [random.choices(symbols, weights)[0] for _ in range(3)]
        elif spinning:

            # Spinning finished, determine result
            spinning = False
            old_score = score

            # If cheat was activated, ensure a jackpot
            if cheat_activated:
                # Force 3 diamonds for a 3x multiplier
                slots = ["7️⃣", "7️⃣", "7️⃣"]
                cheat_activated = False

            # Determine outcome based on symbols
            if slots[0] == slots[1] == slots[2]:  # All three match
                multiplier = slot_values[slots[0]]
                new_score = score + int(bet_amount * multiplier)
                sounds = [
                    rampage_sound,
                    godlike_sound,
                    holyshit_sound,
                    unstoppable_sound,
                ]
                if multiplier > 1:
                    result = f"JACKPOT! {multiplier}x MULTIPLIER!"
                    jackpot_sound.play()
                    random.choice(sounds).play()
                elif multiplier == 1:

                    result = "Got your score back!"
                    random.choice(sounds).play()
                else:

                    result = "You lost everything!"

                score = new_score
            else:
                # Find the most common symbol
                from collections import Counter

                symbol_counts = Counter(slots)
                most_common = symbol_counts.most_common(1)[0][0]
                count = symbol_counts[most_common]

                if count == 2:  # Two of the same
                    multiplier = slot_values[most_common] * 0.5  # Half the multiplier
                    new_score = score + int(bet_amount * multiplier)
                    if multiplier >= 1:
                        jackpot_sound.play()
                        result = f"Two matches! {multiplier}x your betS!"
                    else:
                        dangit_sound.play()
                        result = "You lost half your bet!"
                    score = new_score
                else:
                    dangit_sound.play()
                    result = "No matches. Try again?"  # Lose 20% on no match

        # Draw slot symbols
        for i, symbol in enumerate(slots):
            symbol_text = font.render(symbol, 1, (255, 255, 255))
            win.blit(
                symbol_text,
                (
                    slot_rect.x + 70 + i * 120 - symbol_text.get_width() // 2,
                    slot_rect.y + slot_rect.height // 2 - symbol_text.get_height() // 2,
                ),
            )

        # Draw result
        if result:
            result_font = pygame.font.SysFont("comicsans", 35)
            result_text = result_font.render(result, 1, (255, 215, 0))
            win.blit(result_text, (s_width // 2 - result_text.get_width() // 2, 390))

            new_score_text = result_font.render(
                f"New Score: {score}", 1, (255, 255, 255)
            )
            win.blit(
                new_score_text, (s_width // 2 - new_score_text.get_width() // 2, 430)
            )

        # Draw buttons
        button_font = pygame.font.SysFont("comicsans", 30)

        spin_button_text = button_font.render("SPIN AGAIN", 1, (255, 255, 255))
        exit_button_text = button_font.render("TAKE SCORE & EXIT", 1, (255, 255, 255))
        cheat_button_text = button_font.render("LUCKY SPIN", 1, (255, 255, 255))
        deposit_button_text = button_font.render("DEPOSIT +1000", 1, (255, 255, 255))

        # Cheat button
        cheat_button_rect = pygame.Rect(50, 480, 180, 50)

        deposit_button_rect = pygame.Rect(570, 480, 180, 50)

        spin_button_rect = pygame.Rect(s_width // 2 - 150, 480, 300, 50)
        exit_button_rect = pygame.Rect(s_width // 2 - 150, 625, 300, 50)

        if not spinning:
            pygame.draw.rect(win, (0, 128, 0), spin_button_rect)
            win.blit(
                spin_button_text,
                (
                    spin_button_rect.x
                    + spin_button_rect.width // 2
                    - spin_button_text.get_width() // 2,
                    spin_button_rect.y
                    + spin_button_rect.height // 2
                    - spin_button_text.get_height() // 2,
                ),
            )
            # Draw cheat button (only when not spinning)
            pygame.draw.rect(
                win, (128, 0, 128), cheat_button_rect
            )  # Purple for the cheat button
            win.blit(
                cheat_button_text,
                (
                    cheat_button_rect.x
                    + cheat_button_rect.width // 2
                    - cheat_button_text.get_width() // 2,
                    cheat_button_rect.y
                    + cheat_button_rect.height // 2
                    - cheat_button_text.get_height() // 2,
                ),
            )

            # Draw deposit button
            pygame.draw.rect(win, (0, 128, 128), deposit_button_rect)
            win.blit(
                deposit_button_text,
                (
                    deposit_button_rect.x
                    + deposit_button_rect.width // 2
                    - deposit_button_text.get_width() // 2,
                    deposit_button_rect.y
                    + deposit_button_rect.height // 2
                    - deposit_button_text.get_height() // 2,
                ),
            )

            # Draw bet amount buttons
            for i, bet in enumerate(bet_options):
                bet_button_rect = pygame.Rect(50 + i * 150, 550, 100, 50)
                pygame.draw.rect(win, (128, 128, 0), bet_button_rect)
                bet_text = button_font.render(f"BET {bet}", 1, (255, 255, 255))
                win.blit(
                    bet_text,
                    (
                        bet_button_rect.x
                        + bet_button_rect.width // 2
                        - bet_text.get_width() // 2,
                        bet_button_rect.y
                        + bet_button_rect.height // 2
                        - bet_text.get_height() // 2,
                    ),
                )

            # If cheat was activated, ensure a jackpot
            if cheat_activated:
                # Force 3 diamonds for a 3x multiplier
                score += 1000
                slots = ["💎", "💎", "💎"]
                cheat_activated = False

        pygame.draw.rect(win, (128, 0, 0), exit_button_rect)
        win.blit(
            exit_button_text,
            (
                exit_button_rect.x
                + exit_button_rect.width // 2
                - exit_button_text.get_width() // 2,
                exit_button_rect.y
                + exit_button_rect.height // 2
                - exit_button_text.get_height() // 2,
            ),
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not spinning
            ):
                mouse_pos = pygame.mouse.get_pos()
                if spin_button_rect.collidepoint(mouse_pos):
                    if score >= bet_amount:
                        score -= bet_amount
                        spinning = True
                        spin_start_time = current_time
                        slots = [random.choices(symbols, weights)[0] for _ in range(3)]
                        result = None
                        tap_sound.play()
                    else:
                        result = "Not enough points to spin!"
                if exit_button_rect.collidepoint(mouse_pos):
                    return score
                elif cheat_button_rect.collidepoint(mouse_pos) and not spinning:
                    cheat_activated = True
                    spinning = True
                    spin_start_time = current_time
                    result = None
                elif deposit_button_rect.collidepoint(mouse_pos):
                    score += 1000
                    result = "DEPOSIT ADDED! +1000 POINTS!"
                    coinhandle_sound.play()
                else:
                    for i, bet in enumerate(bet_options):
                        bet_button_rect = pygame.Rect(50 + i * 150, 550, 100, 50)
                        if bet_button_rect.collidepoint(mouse_pos):
                            bet_amount = bet
                            result = f"Bet amount set to {bet} points"
                            tap_sound.play()

    return score


def create_popup(text, size=75, color=(255, 0, 0), duration=2000):
    """Creates a popup message with better visibility and blood-like effect"""
    # Create main text with a bold impact font
    font = pygame.font.SysFont("impact", size, bold=True)
    label = font.render(text, True, color)

    # Create a glow effect surface (slightly larger)
    glow_size = int(size * 1.05)
    glow_font = pygame.font.SysFont("impact", glow_size, bold=True)
    glow = glow_font.render(
        text,
        True,
        (min(color[0] + 50, 255), min(color[1] + 20, 255), min(color[2] + 20, 255)),
    )

    return {
        "surface": label,
        "glow": glow,
        "position": (s_width // 2 - label.get_width() // 2, s_height // 2 - 100),
        "start_time": pygame.time.get_ticks(),
        "duration": duration,
        "scale": 0.1,  # Start small, grow larger
        "alpha": 255,  # Full opacity
    }


def draw_popups(surface, popups):
    """Draws popups with enhanced visibility and effects"""
    current_time = pygame.time.get_ticks()
    completed = []

    for i, popup in enumerate(popups):
        elapsed = current_time - popup["start_time"]

        # Remove expired popups
        if elapsed > popup["duration"]:
            completed.append(i)
            continue

        # Calculate animation progress (0.0 to 1.0)
        progress = elapsed / popup["duration"]

        # More dynamic scaling effect
        if progress < 0.15:
            # Rapid grow
            scale = min(1.2, popup["scale"] + progress * 7.5)
        elif progress < 0.3:
            # Slightly shrink back
            scale = max(1.0, 1.2 - (progress - 0.15) * 1.3)
        else:
            # Pulsate slightly
            scale = 1.0 + 0.05 * abs(math.sin(progress * 6))

        # Alpha effect (fade out at the end)
        if progress > 0.7:
            alpha = int(popup["alpha"] * (1 - (progress - 0.7) / 0.3))
        else:
            alpha = popup["alpha"]

        # Create scaled copies with current scale
        scaled_surface = pygame.transform.scale(
            popup["surface"],
            (
                int(popup["surface"].get_width() * scale),
                int(popup["surface"].get_height() * scale),
            ),
        )

        scaled_glow = pygame.transform.scale(
            popup["glow"],
            (
                int(popup["glow"].get_width() * scale * 1.05),
                int(popup["glow"].get_height() * scale * 1.05),
            ),
        )

        # Apply alpha
        scaled_surface.set_alpha(alpha)
        scaled_glow.set_alpha(int(alpha * 0.7))

        # Position (centered)
        pos_x = (
            popup["position"][0]
            - (scaled_surface.get_width() - popup["surface"].get_width()) // 2
        )
        pos_y = (
            popup["position"][1]
            - (scaled_surface.get_height() - popup["surface"].get_height()) // 2
        )
        glow_x = pos_x - (scaled_glow.get_width() - scaled_surface.get_width()) // 2
        glow_y = pos_y - (scaled_glow.get_height() - scaled_surface.get_height()) // 2

        # Draw multi-layered shadow for "bloody" effect - offset in different directions
        for offset in [(4, 4), (3, 5), (5, 3), (2, 6)]:
            shadow = scaled_surface.copy()
            shadow_alpha = min(255, int(alpha * (0.5 - offset[0] * 0.05)))
            shadow.fill((10, 0, 0, shadow_alpha), None, pygame.BLEND_RGBA_MULT)
            surface.blit(shadow, (pos_x + offset[0], pos_y + offset[1]))

        # Draw glow effect first
        surface.blit(scaled_glow, (glow_x, glow_y))

        # Draw the actual text on top
        surface.blit(scaled_surface, (pos_x, pos_y))

    # Remove completed popups (in reverse order to avoid index issues)
    for i in sorted(completed, reverse=True):
        popups.pop(i)


def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(
            surface, (128, 128, 128), (sx, sy + i * 30), (sx + play_width, sy + i * 30)
        )  # horizontal lines
        for j in range(col):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (sx + j * 30, sy),
                (sx + j * 30, sy + play_height),
            )  # vertical lines


def draw_score(surface, score):
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render(f"Score: {score}", 1, (255, 255, 255))

    # Position the score below the "Tetris" title
    sx = top_left_x - 190
    sy = top_left_y + 200

    surface.blit(label, (sx, sy))


def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Next Shape", 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                pygame.draw.rect(
                    surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0
                )

    surface.blit(label, (sx + 10, sy - 30))


def draw_held_shape(held_piece, surface):
    # Render the held piece next to the playfield, similar to draw_next_shape logic
    if held_piece:
        font = pygame.font.SysFont("comicsans", 30)
        label = font.render("Held", 1, (255, 255, 255))
        sx = top_left_x + play_width + 50
        sy = top_left_y + play_height / 2 - 100 + 200
        surface.blit(label, (sx + 10, sy - 30))
        held_format = held_piece.shape[held_piece.rotation % len(held_piece.shape)]
        for i, line in enumerate(held_format):
            for j, column in enumerate(line):
                if column == "0":
                    pygame.draw.rect(
                        surface, held_piece.color, (sx + j * 30, sy + i * 30, 30, 30), 0
                    )


def draw_window(surface, score=0):
    surface.fill((0, 0, 0))
    # Tetris Title
    font = pygame.font.SysFont("comicsans", 60)
    label = font.render("TETRIS", 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    draw_score(surface, score)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (top_left_x + j * 30, top_left_y + i * 30, 30, 30),
                0,
            )

    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(
        surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5
    )
    # pygame.display.update()


held_piece = None
can_hold = True


def main():
    global grid
    global held_piece, can_hold

    # Add a list to store active popups
    active_popups = []

    pause_screen = pygame.display.set_mode((800, 700))

    locked_positions = {}  # (x,y):(255,0,0)
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    fall_speed = 0.27
    score = 0
    first_piece = True

    # Track statistics
    start_time = pygame.time.get_ticks()
    total_lines_cleared = 0

    while run:

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 4:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005

        # PIECE FALLING CODE
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_ESCAPE:
                    action = pause_menu(pause_screen)
                    if action == "resume":
                        pass
                    elif action == "new_game":
                        main()
                        return
                    elif action == "exit":
                        run = False
                        pygame.display.quit()
                        quit()
                elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    if can_hold:
                        if held_piece == None:
                            held_piece = current_piece
                            current_piece = next_piece
                            next_piece = get_shape()
                            can_hold = False
                        else:
                            held_piece, current_piece = current_piece, held_piece
                            held_piece.x = 5
                            held_piece.y = 0
                            can_hold = False
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(
                        current_piece.shape
                    )
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(
                            current_piece.shape
                        )

                if event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    print(convert_shape_format(current_piece))  # todo fix

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # IF PIECE HIT GROUND
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            can_hold = True
            tap_sound.play()
            if first_piece:
                firstblood_sound.play()
                active_popups.append(create_popup("FIRST BLOOD!", color=(220, 20, 60)))
                first_piece = False

            # call four times to check for multiple clear rows
            lines_cleared = clear_rows(grid, locked_positions)
            total_lines_cleared += lines_cleared
            if lines_cleared > 0:
                # Score calculation based on lines cleared
                if lines_cleared == 1:
                    score += 100
                    humiliation_sound.play()
                    active_popups.append(
                        create_popup("HUMILIATION!", color=(255, 100, 100))
                    )
                elif lines_cleared == 2:
                    score += 300
                    multi_kill_sound.play()
                    active_popups.append(
                        create_popup("MULTI KILL!", color=(255, 50, 50))
                    )
                elif lines_cleared == 3:
                    score += 500
                    mega_kill_sound.play()
                    active_popups.append(
                        create_popup("MEGA KILL!", color=(255, 20, 20))
                    )
                elif lines_cleared == 4:
                    score += 800
                    ultra_kill_sound.play()
                    active_popups.append(create_popup("ULTRA KILL!", color=(200, 0, 0)))
                pass

        draw_window(win, score)
        draw_next_shape(next_piece, win)
        draw_held_shape(held_piece, win)
        pygame.display.update()

        # Check if user lost
        if check_lost(locked_positions):
            run = False
    survival_time = (pygame.time.get_ticks() - start_time) / 1000.0

    draw_text_middle("You Lost", 40, (255, 255, 255), win)
    oneandonly_sound.play()
    pygame.display.update()
    pygame.time.delay(2000)

    final_score = game_statistics(score, total_lines_cleared, survival_time)


def main_menu():
    run = True
    global volume
    dragging = False

    # Slider dimensions
    slider_x = 200
    slider_y = 600
    slider_width = 400
    slider_height = 8
    knob_radius = 15

    set_all_sounds_volume(volume)

    while run:
        win.fill((0, 0, 0))
        # Title text
        title_font = pygame.font.SysFont("comicsans", 80)
        title_label = title_font.render("TETRIS", 1, (255, 255, 255))
        win.blit(title_label, (s_width / 2 - title_label.get_width() / 2, 150))

        # Instructions text
        # Instructions text
        font = pygame.font.SysFont("comicsans", 40)
        label1 = font.render("Are you ready to play?", 1, (255, 255, 255))
        label2 = font.render("Press SPACE to start", 1, (255, 255, 255))
        label3 = font.render("Press ESC to exit", 1, (255, 255, 255))

        win.blit(label1, (s_width / 2 - label1.get_width() / 2, 300))
        win.blit(label2, (s_width / 2 - label2.get_width() / 2, 360))
        win.blit(label3, (s_width / 2 - label3.get_width() / 2, 420))

        # Play a sound when menu first loads (optional)
        if hasattr(main_menu, "first_run") and not main_menu.first_run:
            main_menu.first_run = False
            prepare_sound.play()

        # Draw volume slider
        pygame.draw.rect(
            win, (180, 180, 180), (slider_x, slider_y, slider_width, slider_height)
        )
        knob_x = int(slider_x + volume * slider_width)
        pygame.draw.circle(
            win, (255, 215, 0), (knob_x, slider_y + slider_height // 2), knob_radius
        )
        # Volume label
        vol_font = pygame.font.SysFont("comicsans", 24)
        vol_label = vol_font.render(f"Volume: {int(volume*100)}%", 1, (255, 255, 255))
        win.blit(vol_label, (slider_x + slider_width + 30, slider_y - 20))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()
                elif event.key == pygame.K_ESCAPE:
                    run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if (
                    knob_x - knob_radius <= mx <= knob_x + knob_radius
                    and slider_y - knob_radius <= my <= slider_y + knob_radius
                ):
                    dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, _ = pygame.mouse.get_pos()
                # Clamp knob position
                mx = max(slider_x, min(slider_x + slider_width, mx))
                volume = (mx - slider_x) / slider_width
                set_all_sounds_volume(volume)
    pygame.quit()


def pause_menu(surface):
    global volume
    paused = True
    font = pygame.font.SysFont("comicsans", 50)
    resume_text = font.render("Resume", True, (255, 255, 255))
    new_game_text = font.render("New Game", True, (255, 255, 255))
    exit_text = font.render("Exit", True, (255, 255, 255))
    # Simple button rectangles for demonstration
    resume_rect = resume_text.get_rect(center=(400, 250))
    new_game_rect = new_game_text.get_rect(center=(400, 350))
    exit_rect = exit_text.get_rect(center=(400, 450))

    # Slider dimensions (same as main menu)
    slider_x = 200
    slider_y = 520
    slider_width = 400
    slider_height = 8
    knob_radius = 15
    dragging = False

    while paused:
        surface.fill((0, 0, 0))

        # Draw pause menu buttons
        surface.blit(resume_text, resume_rect)
        surface.blit(new_game_text, new_game_rect)
        surface.blit(exit_text, exit_rect)

        # Draw volume slider
        pygame.draw.rect(
            surface, (180, 180, 180), (slider_x, slider_y, slider_width, slider_height)
        )
        knob_x = int(slider_x + volume * slider_width)
        pygame.draw.circle(
            surface, (255, 215, 0), (knob_x, slider_y + slider_height // 2), knob_radius
        )
        # Volume label
        vol_font = pygame.font.SysFont("comicsans", 24)
        vol_label = vol_font.render(f"Volume: {int(volume*100)}%", 1, (255, 255, 255))
        surface.blit(vol_label, (slider_x + slider_width + 30, slider_y - 20))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if resume_rect.collidepoint(event.pos):
                    return "resume"
                if new_game_rect.collidepoint(event.pos):
                    return "new_game"
                if exit_rect.collidepoint(event.pos):
                    return "exit"
                mx, my = pygame.mouse.get_pos()
                if (
                    knob_x - knob_radius <= mx <= knob_x + knob_radius
                    and slider_y - knob_radius <= my <= slider_y + knob_radius
                ):
                    dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, _ = pygame.mouse.get_pos()
                mx = max(slider_x, min(slider_x + slider_width, mx))
                volume = (mx - slider_x) / slider_width
                set_all_sounds_volume(volume)


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Tetris")

main_menu()  # start game
