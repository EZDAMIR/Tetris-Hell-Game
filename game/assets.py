import pygame


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
        if pygame.mixer.get_init():  # Check if mixer is initialized
            pygame.mixer.music.set_volume(self.volume)

    def get_font(self, name, size, bold=False, italic=False):
        return pygame.font.SysFont(name, size, bold=bold, italic=italic)
