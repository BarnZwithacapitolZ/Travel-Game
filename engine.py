import pygame
import os
import json
import threading
import pygame._sdl2
from config import (
    config, ASSETSFOLDER, AUDIOFOLDER, MUSICFOLDER, MODIFIEDMUSICFOLDER,
    MAPSFOLDER, RED, BLACK, TRUEBLACK, SCANLINES)
from utils import vec
from pydub import AudioSegment


class Renderer:
    def __init__(self, game):
        self.game = game
        self.width = config["graphics"]["displayWidth"]
        self.height = config["graphics"]["displayHeight"]
        self.windowWidth = config["graphics"]["displayWidth"]
        self.windowHeight = config["graphics"]["displayHeight"]

        # we can use these variables to set the resolution on fullscreen
        self.monitorWidth = pygame.display.Info().current_w
        self.monitorHeight = pygame.display.Info().current_h

        self.screen = pygame.display.set_mode(
            (self.windowWidth, self.windowHeight),
            pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=int(self.game.vsync))
        # self.screen.set_alpha(None)
        self.gameDisplay = pygame.Surface((self.width, self.height))

        # control the scale of whats on screen
        self.scale = 1
        # used to control the fixed scale, i.e to make
        # things bigger on screen seperate from screen size
        self.fixedScale = 1
        self.diff = vec(0, 0)
        self.offset = vec(0, 0)
        self.surfaces = []
        self.dirtySurfaces = []

        self.fpsFont = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.fontImage = self.fpsFont.render(
            str(int(self.game.clock.get_fps())), False, RED)
        self.createScanlines()

    # Prepare the gamedisplay for blitting to,
    # this means overriding it with a new color
    def prepareSurface(self, color):
        self.gameDisplay.fill(color)

    def drawScanlines(self, surface):
        step = 5
        for i in range(0, int(self.height), step):
            pos1 = (0, i)
            pos2 = (int(self.width), i)
            pygame.draw.line(surface, BLACK, pos1, pos2, 1)

    def createScanlines(self):
        self.scanlines = pygame.Surface((self.width, self.height)).convert()
        self.scanlines.fill(SCANLINES)
        self.drawScanlines(self.scanlines)
        self.scanlines.set_alpha(
            config["graphics"]["scanlines"]["opacity"], pygame.RLEACCEL)

    # Add a surface to the gameDisplay
    def addSurface(self, surface, rect, method=None):
        self.surfaces.append((surface, rect, method))

    def addDirtySurface(self, surface):
        self.dirtySurfaces.append(surface)

    def setWidth(self, width):
        self.width = width

    def setHeight(self, height):
        self.height = height

    def setFixedScale(self, fixedScale):
        self.fixedScale = fixedScale

    def getScale(self):
        return self.scale

    def getFixedScale(self):
        return self.fixedScale

    def getDifference(self):
        return self.diff

    def getHeight(self):
        return self.height

    def getWindowWidth(self):
        return self.windowWidth

    def getWindowHeight(self):
        return self.windowHeight

    def setFullscreen(self):
        self.setScale((self.monitorWidth, self.monitorHeight), True)

    def unsetFullscreen(self):
        self.setScale((
            config["graphics"]["displayWidth"],
            config["graphics"]["displayHeight"]))

    def setScale(self, size, fullscreen=False):
        size = list(size)
        if size[0] < config["graphics"]["minDisplayWidth"]:
            size[0] = config["graphics"]["minDisplayWidth"]

        if size[1] < config["graphics"]['minDisplayHeight']:
            size[1] = config["graphics"]["minDisplayHeight"]

        self.scale = min(
            size[1] / config["graphics"]["displayHeight"],
            size[0] / config["graphics"]["displayWidth"]) * self.fixedScale

        self.width = (config["graphics"]["displayWidth"] * self.scale)
        self.height = (config["graphics"]["displayHeight"] * self.scale)
        self.windowWidth = size[0]
        self.windowHeight = size[1]
        self.diff.x = (self.windowWidth - self.width) / 2
        self.diff.y = (self.windowHeight - self.height) / 2

        if fullscreen:
            self.screen = pygame.display.set_mode(
                (int(self.windowWidth), int(self.windowHeight)),
                pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF,
                vsync=int(self.game.vsync))

        elif not fullscreen:
            self.screen = pygame.display.set_mode(
                (int(self.windowWidth), int(self.windowHeight)),
                pygame.RESIZABLE | pygame.DOUBLEBUF,
                vsync=int(self.game.vsync))

        # .convert()
        self.gameDisplay = pygame.Surface((self.width, self.height))

        self.game.spriteRenderer.resize()
        self.game.mapEditor.resize()
        self.game.optionMenu.resize()
        self.game.mainMenu.resize()
        self.createScanlines()

    # on tick function
    def render(self):
        for surface in self.surfaces:
            if surface[2]:
                surface[2](self.gameDisplay)
            else:
                self.gameDisplay.blit(surface[0], surface[1])

        # Only show FPS in debug mode.
        if config["game"]["debug"]:
            self.gameDisplay.blit(self.fontImage, (950, 10))

        if not self.game.mainMenu.getLevelSelectOpen():
            if config["graphics"]["scanlines"]["enabled"]:
                self.gameDisplay.blit(self.scanlines, (0, 0))
                pygame.draw.rect(
                    self.gameDisplay, TRUEBLACK, (
                        -30 * self.scale, -30 * self.scale,
                        (config["graphics"]["displayWidth"] + 60) * self.scale,
                        (config["graphics"]["displayHeight"] + 60)
                        * self.scale), int(30 * self.scale),
                    border_radius=int(80 * self.scale))

        self.screen.blit(
            self.gameDisplay,
            (0 + self.getDifference()[0], 0 + self.getDifference()[1]))
        # self.screen.blit(pygame.transform.smoothscale(self.gameDisplay,
        # (int(self.width), int(self.height))), (0, 0))

        # pygame.display.update(self.dirtySurfaces) #self.screen.get_rect() ?
        pygame.display.update()

        self.surfaces = []
        self.dirtySurfaces = []

        self.fontImage = self.fpsFont.render(
            str(int(self.game.clock.get_fps())), False, RED)


class ImageLoader:
    def __init__(self, game):
        self.game = game
        self.images = {}
        self.loadAllImages()

    def loadAllImages(self):
        for key, data in config["images"].items():
            i = pygame.image.load(os.path.join(ASSETSFOLDER, data["image"]))
            i = i.convert_alpha() if data["alpha"] else i.convert()

            self.images[key] = {"image": i, "data": data}

    def getImage(self, key, scale=tuple()):
        image = self.images[key]["image"]
        data = self.images[key]["data"]

        if scale:  # if there is a scale
            if config["graphics"]["smoothscale"]:
                image = pygame.transform.smoothscale(
                    image, (
                        int(scale[0] * self.game.renderer.getScale()),
                        int(scale[1] * self.game.renderer.getScale())))

            else:
                image = pygame.transform.scale(image, (
                    int(scale[0] * self.game.renderer.getScale()),
                    int(scale[1] * self.game.renderer.getScale())))
            image = image.convert_alpha() if data["alpha"] else image.convert()

        return image

    @staticmethod
    def flipImage(image, xbool, ybool):
        return pygame.transform.flip(image, xbool, ybool)

    @staticmethod
    def rotateImage(image, angle):
        return pygame.transform.rotate(image, angle)

    @staticmethod
    def changeImageColor(image, newColor, oldColor=None):
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                pixel = image.get_at((x, y))
                if pixel == oldColor or oldColor is None:
                    newColor.a = pixel.a
                    image.set_at((x, y), newColor)


class AudioLoader:
    def __init__(self, game):
        self.game = game
        self.numChannels = 8
        pygame.mixer.set_num_channels(self.numChannels)

        # Keep track of all the music and sounds available in the game.
        self.sounds = {}
        self.music = {}

        # Keep track of the current music track playing by key.
        self.currentTrack = None

        self.masterBuffer = 1.0
        self.musicBuffer = 1.0

        # Keep track of the current time offset for the current audio playing.
        self.musicOffset = 0.0

        # Control the music playback speed when fastforward or slowmotion.
        self.speedUp = 1.1
        self.slowDown = 0.9

        # The length to fade in/out an audio track
        self.fadeLength = 300

        # Keep track of which threads are alive
        # TODO: threading class would be better here!!!!!!
        self.threads = []

        # Default audio
        self.defaultTrack = "track1"

        # Load all the music and sounds and set their volumes.
        self.setChannels()
        self.loadAllSounds()
        self.loadAllMusic()
        self.setMasterVolume(config["audio"]["volume"]["master"]["current"])

    def getSound(self, key):
        return self.sounds[key]

    def getMusic(self, key):
        return self.music[key]['path']

    def getChannelBusy(self, chan=0):
        return self.channels[chan].get_busy()

    def getKey(self, key):
        if key is None:
            return self.defaultTrack
        return key

    def addMusic(self, key, path, volume=1):
        self.music[key] = {
            'path': path,
            'volume': volume
        }

    def playSound(self, key, chan=0, loops=0):
        if key not in self.sounds:
            return

        self.channels[chan].play(self.sounds[key], loops=loops)

    def stopSound(self, chan=0):
        self.channels[chan].stop()

    def fadeOutSound(self, duration, chan=0):
        self.channels[chan].fadeout(duration)

    # Implement a custom loop music method to ensure we maintain sped up or
    # slowed down music after loop.
    def loopMusic(self):
        if pygame.mixer.music.get_busy():
            return

        # Reset the offset and play the track again
        self.musicOffset = 0.0
        if self.game.clickManager.getSpaceBar():
            self.slowDownMusic()
        elif self.game.clickManager.getSpeedUp():
            self.speedUpMusic()
        else:
            self.playMusic(self.currentTrack)

    # Disable fade option allows us to disable fading between tracks
    def playMusic(self, key=None, loop=0, start=0.0, disableFade=False):
        key = self.getKey(key)

        if (key not in self.music
                or (key == self.currentTrack and not disableFade)):
            return

        # If the music channel is already busy we want to fade out the
        # existing track and play the new one
        fadeIn = False
        if pygame.mixer.music.get_busy() and not disableFade:
            pygame.mixer.music.fadeout(self.fadeLength)
            fadeIn = True

        self.currentTrack = key
        pygame.mixer.music.load(self.music[key]["path"])
        self.musicBuffer = 1.0 / self.music[key]["volume"]
        self.setMusicVolume(config["audio"]["volume"]["music"]["current"])
        pygame.mixer.music.play(
            loop, start, self.fadeLength * 2 if fadeIn else 0)

    def setOffsetByPos(self, speedUp=False, slowDown=False):
        pos = pygame.mixer.music.get_pos()

        if speedUp:
            pos *= self.speedUp
        elif slowDown:
            pos /= self.slowDown

        self.musicOffset += pos / 1000  # Milliseconds to seconds

    def speedUpMusic(self):
        # Ensure there is a 'fast' version of the track
        currentTrack = self.currentTrack
        fastTrack = self.currentTrack + "Fast"
        if fastTrack not in self.music:
            return

        self.setOffsetByPos()
        self.playMusic(
            fastTrack, start=self.musicOffset / self.speedUp,
            disableFade=True)
        self.currentTrack = currentTrack  # Reset current track to original

    def slowDownMusic(self):
        # Ensure there is a 'slow' version of the track
        currentTrack = self.currentTrack
        slowTrack = self.currentTrack + "Slow"
        if slowTrack not in self.music:
            return

        self.setOffsetByPos()
        self.playMusic(
            slowTrack, start=self.musicOffset * self.speedUp,
            disableFade=True)
        self.currentTrack = currentTrack  # Reset current track to original

    def restoreMusic(self, speedUp=False, slowDown=False):
        self.setOffsetByPos(speedUp, slowDown)
        self.playMusic(
            self.currentTrack, start=self.musicOffset,
            disableFade=True)

    def setChannels(self):
        # Channel 0 reserved for hud sounds.
        # Channel 1 reserved for game sounds.
        # Channel 2 reserved for extra game sounds.
        self.channels = [
            pygame.mixer.Channel(i) for i in range(self.numChannels)]

    # Set the master volume for both music and sounds
    def setMasterVolume(self, volume=1):
        self.masterBuffer = 1.0 / volume if volume > 0 else None
        self.setSoundVolume(config["audio"]["volume"]["sounds"]["current"])
        self.setMusicVolume(config["audio"]["volume"]["music"]["current"])

    # Set the sound volume relative to the master volume.
    def setSoundVolume(self, volume=1):
        for channel in self.channels:
            amount = (
                volume / self.masterBuffer if self.masterBuffer is not None
                else 0.0)
            channel.set_volume(amount)

    # Set the music volume relative to the master volume.
    def setMusicVolume(self, volume=1):
        amount = (
            (volume / self.musicBuffer) / self.masterBuffer
            if self.masterBuffer is not None else 0.0)
        pygame.mixer.music.set_volume(amount)

    # Get all the sounds from the config file.
    def loadAllSounds(self):
        for key, audio in config["audio"]["sounds"].items():
            a = pygame.mixer.Sound(os.path.join(AUDIOFOLDER, audio["file"]))
            a.set_volume(audio["volume"])
            self.sounds[key] = a

    # Get all the music from the config file.
    def loadAllMusic(self):
        for key, audio in config["audio"]["music"].items():
            path = os.path.join(MUSICFOLDER, audio["file"])
            self.addMusic(key, path, audio["volume"])

            # When we load a audio file we want to check that a
            # modified version of that file already exists.
            if not os.path.exists(MODIFIEDMUSICFOLDER):
                continue

            fastAudioPath = os.path.join(MODIFIEDMUSICFOLDER, key + "Fast.mp3")
            slowAudioPath = os.path.join(MODIFIEDMUSICFOLDER, key + "Slow.mp3")

            if os.path.exists(fastAudioPath) and os.path.exists(slowAudioPath):
                self.addMusic(key + "Fast", fastAudioPath, audio["volume"])
                self.addMusic(key + "Slow", slowAudioPath, audio["volume"])

    # Check if modified versions of the sound exist
    def checkModifiedAudio(self, key=None):
        key = self.getKey(key)

        if key + "Fast" not in self.music or key + "Slow" not in self.music:
            if len(self.threads) <= 0:
                # Thread must be a daemon so that it dies when the
                # program is closed.
                thread = threading.Thread(
                    target=self.createModifiedAudio,
                    args=(key,), daemon=True)
                thread.start()
                self.threads.append(thread)
            return False
        return True

    def createModifiedAudio(self, key):
        audio = AudioSegment.from_file(self.getMusic(key), format='mp3')
        fastAudio = AudioLoader.changeAudioSpeed(audio, self.speedUp)
        slowAudio = AudioLoader.changeAudioSpeed(audio, self.slowDown)

        if not os.path.exists(MODIFIEDMUSICFOLDER):
            os.makedirs(MODIFIEDMUSICFOLDER)

        fastAudioPath = os.path.join(MODIFIEDMUSICFOLDER, key + "Fast.mp3")
        slowAudioPath = os.path.join(MODIFIEDMUSICFOLDER, key + "Slow.mp3")

        fastAudio.export(fastAudioPath, format='mp3')
        slowAudio.export(slowAudioPath, format='mp3')

        # Add the modified tracks to the same volume as the original.
        self.addMusic(key + "Fast", fastAudioPath, self.music[key]['volume'])
        self.addMusic(key + "Slow", slowAudioPath, self.music[key]['volume'])

        # Reset thread count
        self.threads = []

    # Change the playback speed of a given sound and return a new sound.
    @staticmethod
    def changeAudioSpeed(audio, speed=1.0):
        # How many samples to play per second.
        alteredSound = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        })
        # Convert back from altered frame rate to standard frame rate.
        return alteredSound.set_frame_rate(audio.frame_rate)


class MapLoader:
    def __init__(self):
        self.maps = {}
        self.builtInMaps = {}
        self.splashScreenMaps = {}
        self.customMaps = {}

        self.loadAllMaps()

    def getMaps(self):
        return self.maps

    def getBuiltInMaps(self):
        return self.builtInMaps

    def getSplashScreenMaps(self):
        return self.splashScreenMaps

    def getCustomMaps(self):
        return self.customMaps

    def getMap(self, key):
        return self.maps[key]

    def getMapData(self, key):
        level = self.maps[key]
        with open(level) as f:
            return json.load(f)

    def getLongestMapLength(self):
        longest = 0
        for mapName in self.maps:
            if len(mapName) > longest:
                longest = len(mapName)
        return longest

    def addMap(self, mapName, path, mapDict):
        mapDict[mapName] = path
        self.maps[mapName] = path

    def removeMap(self, mapName):
        del self.maps[mapName]

    def removeCustomMap(self, mapName):
        del self.customMaps[mapName]

    def removeBuiltInMap(self, mapName):
        del self.builtInMaps[mapName]

    def loadMaps(self, maps, mapDict):
        for key, level in maps.items():
            m = os.path.join(MAPSFOLDER, level)
            self.maps[key] = m
            mapDict[key] = m

    def loadAllMaps(self):
        # Load built-in levels
        self.loadMaps(config["maps"]["builtIn"], self.builtInMaps)

        # Load splash-screen levels (for main menu)
        self.loadMaps(config["maps"]["splashScreen"], self.splashScreenMaps)

        # Load custom levels
        self.loadMaps(config["maps"]["custom"], self.customMaps)

    def checkMapExists(self, mapName):
        if mapName in self.maps:
            return True
        return False

    def saveMap(self, mapName, mapData):
        with open(self.getMap(mapName), "w") as f:
            json.dump(mapData, f)


class RegionLoader:
    def __init__(self):
        self.regions = {}
        self.currentRegion = None

        self.loadAllRegions()

    def getRegions(self):
        return self.regions

    def getRegion(self, key):
        return self.regions[key]

    def getRegionMaps(self, key):
        return self.regions[key]["maps"]

    def getCurrentRegion(self):
        return self.currentRegion

    def setCurrentRegion(self, region):
        if region not in self.regions:
            return
        self.currentRegion = region

    def loadAllRegions(self):
        for key, region in config["regions"].items():
            self.regions[key] = region
