import pygame
import sys
import wave
import os
from pydub import AudioSegment

# Insert directory paths
sys.path.insert(0, 'menu')
sys.path.insert(0, 'menu/functions')
sys.path.insert(0, 'sprites')

from config import config, MUSICFOLDER
from utils import vec
from clickManager import ClickManager
from engine import Renderer, ImageLoader, MapLoader, AudioLoader
from spriteRenderer import SpriteRenderer
from menu import MainMenu, OptionMenu
from menuComponents import TextHandler
from mapEditor import MapEditor


def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
     # convert the sound with altered frame rate to a standard frame rate
     # so that regular playback programs will work right. They often only
     # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.key.set_repeat(500, 100)
        pygame.font.init()
        pygame.event.set_allowed([
            pygame.QUIT, pygame.VIDEORESIZE, pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN])

        self.playing = True
        self.clock = pygame.time.Clock()
        self.running = True

        # Start with the game paused (menus will keep running though)
        self.paused = True

        self.fullscreen = config["graphics"]["fullscreen"]
        self.vsync = config["graphics"]["vsync"]

        # Engine
        self.renderer = Renderer(self)
        self.spriteRenderer = SpriteRenderer(self)
        self.clickManager = ClickManager(self)
        self.textHandler = TextHandler()

        # Loaders
        self.imageLoader = ImageLoader(self)
        self.mapLoader = MapLoader()
        self.audioLoader = AudioLoader(self)

        # Map editor
        self.mapEditor = MapEditor(self)

        # Menu's
        self.mainMenu = MainMenu(self)
        self.optionMenu = OptionMenu(self, self.spriteRenderer, self.mapEditor)

        if self.fullscreen:
            self.renderer.setFullscreen()

        self.setCaption()
        self.setIcon()
        self.setCursor()

        # audio = self.audioLoader.getMusic('test')

        # # currentSound = wave.open(audio, 'rb')
        # # sampleRate = currentSound.getframerate()
        # # channels = currentSound.getnchannels()
        # # signal = currentSound.readframes(-1)

        # # newSound = wave.open(path, "wb")
        # # newSound.setnchannels(channels)
        # # newSound.setsampwidth(2)
        # # newSound.setframerate(sampleRate * 1.2)
        # # newSound.writeframes(signal)
        # # newSound.close()

        # sound = AudioSegment.from_file(self.audioLoader.getMusic('test'), 'mp3')
        # fastSound = speed_change(sound, self.audioLoader.speedUp)
        # slowSound = speed_change(sound, self.audioLoader.slowDown)

        fastPath = os.path.join(MUSICFOLDER, "testFast.mp3")
        slowPath = os.path.join(MUSICFOLDER, "testSlow.mp3")

        # fastSound.export(fastPath, format="mp3")
        # slowSound.export(slowPath, format="mp3")

        self.audioLoader.addMusic("testFast", fastPath, 0.5)
        self.audioLoader.addMusic("testSlow", slowPath, 0.5)

        self.audioLoader.playMusic("test")
        # self.audioLoader.fadeOutSound(10000, 2)

        # print(pygame.font.get_fonts())

    # Set the games caption (name)
    def setCaption(self):
        pygame.display.set_caption(config["game"]["gameTitle"])

    # Set the games icon
    def setIcon(self):
        icon = self.imageLoader.getImage(config["game"]["icon"])
        pygame.display.set_icon(icon)

    # Set the games cursor (cursor class?)
    def setCursor(self):
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)

    def getPaused(self):
        return self.paused

    def __quit(self):
        self.optionMenu.checkForExistingControls()
        self.playing = False

    def __events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__quit()

            elif e.type == pygame.VIDEORESIZE:
                self.renderer.setScale(e.size, self.fullscreen)

            if e.type == pygame.KEYDOWN:
                self.textHandler.events(e)

                # Only open the option manu if the game isn't paused
                # and the main menu isn't open
                if (e.key == pygame.K_ESCAPE and not self.mainMenu.getOpen()
                        and not self.spriteRenderer.getMenu().getOpen()):
                    # Close the dropdowns first
                    if not self.mapEditor.isDropdownsClosed():
                        if not self.optionMenu.getOpen():
                            self.optionMenu.main(True, True)
                        elif (self.optionMenu.getOpen()
                                and not self.optionMenu.checkKeySelection()):
                            self.optionMenu.closeTransition()

                elif (e.key == config["controls"]["right"]["current"]
                        and self.mainMenu.getOpen()):
                    self.mainMenu.levelForward(vec(1, 0))
                elif (e.key == config["controls"]["left"]["current"]
                        and self.mainMenu.getOpen()):
                    self.mainMenu.levelBackward(vec(-1, 0))
                elif (e.key == config["controls"]["up"]["current"]
                        and self.mainMenu.getOpen()):
                    self.mainMenu.levelUpward(vec(0, -1))
                elif (e.key == config["controls"]["down"]["current"]
                        and self.mainMenu.getOpen()):
                    self.mainMenu.levelDownward(vec(0, 1))

                # Don't want to be able to pause in the main menu spash screen.
                elif (e.key == config["controls"]["pause"]["current"]
                        and not self.mainMenu.getOpen()):
                    if self.spriteRenderer.getHud().getOpen():
                        self.spriteRenderer.getHud().togglePauseGame()

                # If the game is not paused and the main menu
                # isnt open and no text inputs are open
                if (not self.paused and not self.mainMenu.getOpen()
                        and not self.textHandler.getActive()):
                    # Show / Hide the different layers depending on key press
                    if e.key == config["controls"]["layer1"]["current"]:
                        self.spriteRenderer.showLayer(1)
                        self.mapEditor.showLayer(1)
                    elif e.key == config["controls"]["layer2"]["current"]:
                        self.spriteRenderer.showLayer(2)
                        self.mapEditor.showLayer(2)
                    elif e.key == config["controls"]["layer3"]["current"]:
                        self.spriteRenderer.showLayer(3)
                        self.mapEditor.showLayer(3)
                    elif e.key == config["controls"]["layer4"]["current"]:
                        self.spriteRenderer.showLayer(4)
                        self.mapEditor.showLayer(4)

                if (e.key == pygame.K_z
                    and pygame.key.get_mods() & pygame.KMOD_CTRL
                        and not self.paused and not self.mainMenu.getOpen()):
                    self.mapEditor.undoChange()
                    level = self.mapEditor.getLevelData()
                    layer = self.mapEditor.getCurrentLayer()
                    # Reload the level
                    self.mapEditor.createLevel(level, layer=layer)

                elif (e.key == pygame.K_y
                        and pygame.key.get_mods() & pygame.KMOD_CTRL
                        and not self.paused and not self.mainMenu.getOpen()):
                    self.mapEditor.redoChange()
                    level = self.mapEditor.getLevelData()
                    layer = self.mapEditor.getCurrentLayer()
                    # Reload the level
                    self.mapEditor.createLevel(level, layer=layer)

            elif e.type == pygame.KEYUP:
                self.textHandler.setCurrentKey(None)

            # Make left click set the destination on the click manager instead
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.clickManager.setClicked(True)
                elif e.button == 3:
                    self.clickManager.setRightClicked(True)

            else:
                self.clickManager.setClicked(False)
                self.clickManager.setRightClicked(False)

    def run(self):
        # Main menu
        self.mainMenu.main()

        # Game loop
        while self.playing:
            self.__events()
            self.dt = self.clock.tick() / 1000

            # Prevent game from updating if window is being moved?
            if self.dt >= 0.05:
                continue

            self.__update()
            self.__draw()

        self.running = False

    def __update(self):
        # Loop the music and reset the offset
        self.audioLoader.loopMusic()

        if not self.paused:
            self.spriteRenderer.update()
            self.mapEditor.update()

            if self.mainMenu.getOpen():
                self.mainMenu.update()
                self.optionMenu.update()

        elif self.paused:
            self.optionMenu.update()

    def __draw(self):
        # Draw the background colors for static menus.
        # - level sections open means any level selection screen
        #   (including custom)
        if self.mainMenu.getLevelSelectOpen():
            self.renderer.prepareSurface(self.mainMenu.getBackgroundColor())

        # Add sprites
        self.spriteRenderer.render()
        self.mapEditor.render()

        # Add menus when not paused
        if self.mainMenu.getOpen():
            self.mainMenu.display()
            self.optionMenu.display()
        elif self.paused:
            self.optionMenu.display()

        # render everything
        self.renderer.render()


def main():
    g = Game()
    g.run()
    # cProfile.run('g.run()')

    # Kill everything initialised
    if pygame.mixer.get_init() is not None:
        pygame.mixer.quit()
    if pygame.font.get_init():
        pygame.font.quit()
    if pygame.get_init():
        pygame.quit()


if __name__ == "__main__":
    main()
