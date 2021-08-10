
import pygame
from config import config, dump
import hudFunctions as hf

vec = pygame.math.Vector2


# load the level and show transition
def continueGame(obj, menu, event):
    def callback(obj, menu):
        menu.game.spriteRenderer.createLevel(
            menu.game.mapLoader.getMap("Test"))
        menu.game.spriteRenderer.setRendering(True, True)  # Load the hud
        menu.close()
        obj.y = 0

    menu.slideTransitionY(
        (0, config["graphics"]["displayHeight"]), 'first', callback=callback)


def openLevelSelect(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.close()
            menu.levelSelect(True)

    # menu.slideTransitionY(
    #   (0, config["graphics"]["displayHeight"]), 'first', callback = callback)
    menu.slideTransitionY(
        (0, -config["graphics"]["displayHeight"]), 'first', speed=40,
        callback=callback, direction='down')
    menu.loadingScreen()


# Navigate back to the main page of the main menu
# (from within the main menu itself)
def openMainMenu(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.close()
            menu.main(True)

    menu.slideTransitionY(
        (0, -config["graphics"]["displayHeight"]), 'first', speed=40,
        callback=callback, direction='down')


# load the map editor and show transition
def openMapEditor(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.paused = False
            menu.game.mapEditor.createLevel(clearChanges=True)
            # Load the hud
            menu.game.mapEditor.setRendering(True, True)
            # Default option to add connection
            hf.addConnection(obj, menu, event)
            menu.levelSelectOpen = False
            menu.customLevelSelectOpen = False
            menu.close()

    menu.slideTransitionY(
        (0, config["graphics"]["displayHeight"]), 'first', callback=callback)


# load a specified map which has been clicked on
def loadLevel(obj, menu, event, level):
    if hasattr(menu, 'transitioning') and menu.getTransitioning():
        return

    global levelName
    levelName = level

    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.spriteRenderer.createLevel(levelName)
            menu.game.spriteRenderer.setRendering(True, True)  # Load the hud
            menu.levelSelectOpen = False
            menu.customLevelSelectOpen = False
            menu.close()

    menu.slideTransitionY(
        (0, config["graphics"]["displayHeight"]), 'first', callback=callback)


# Check if a level can be unlocked with the amount of keys the player has,
# if it can then unlock the level, else play an error sound
def unlockLevel(obj, menu, event, level):
    if not level.getLevelData()["locked"]["isLocked"]:
        return

    if config["player"]["keys"] >= level.getLevelData()["locked"]["unlock"]:
        menu.game.audioLoader.playSound("uiSuccess", 0)
        config["player"]["keys"] -= level.getLevelData()["locked"]["unlock"]
        level.getLevelData()["locked"]["isLocked"] = False
        menu.game.mapLoader.saveMap(
            level.getLevelData()["mapName"], level.getLevelData())
        dump(config)

        # if successful update menu
        menu.keyText.setText(str(config["player"]["keys"]))
        level.addEvent(loadLevel, 'onMouseClick', level=level.getLevel())
        level.removeEvent(unlockLevel, 'onMouseClick', level=level)
        level.dirty = True
        menu.keyText.dirty = True

    else:
        menu.game.audioLoader.playSound("uiError", 0)


# Move the level scroller foward by one level
def levelForward(obj, menu, event, change=vec(0, 0)):
    menu.levelForward(change)


# Move the level scroller backwards by one level
def levelBackward(obj, menu, event, change=vec(0, 0)):
    menu.levelBackward(change)


def levelUpward(obj, menu, event, change=vec(0, 0)):
    menu.levelUpward(change)


def levelDownward(obj, menu, event, change=vec(0, 0)):
    menu.levelDownward(change)


# quit the game
def closeGame(obj, menu, event):
    menu.close()
    menu.game.playing = False


# ----Option-Menu Functions----

# Exit the game and return to the main menu with transition
def showMainMenu(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.paused = True
            # Always close the Game
            menu.game.spriteRenderer.setRendering(False)
            # Always close the Editor
            menu.game.mapEditor.setRendering(False)
            # Always close any open inputs
            menu.game.textHandler.setActive(False)
            menu.game.mainMenu.main(True)
            menu.close()

    menu.slideTransitionY(
        (0, -config["graphics"]["displayHeight"]), 'first', speed=40,
        callback=callback, direction='down')


# Exit the game and return to the level selection screen with transition
def showLevelSelect(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.paused = True
            # Always close the Game
            menu.game.spriteRenderer.setRendering(False)
            # Always close the Editor
            menu.game.mapEditor.setRendering(False)
            # Always close any open inputs
            menu.game.textHandler.setActive(False)
            menu.game.mainMenu.levelSelect(True)
            menu.close()

    menu.slideTransitionY(
        (0, -config["graphics"]["displayHeight"]), 'first', speed=40,
        callback=callback, direction='down')
    menu.loadingScreen()


def showCustomLevelSelect(obj, menu, event):
    menu.close()
    menu.customLevelSelect()


# unpause the game and hide the option menu
def unpause(obj, menu, event):
    menu.closeTransition()


# show the options screen
def showOptions(obj, menu, event):
    menu.close()
    menu.options()


# show the grahics screen
def showGraphics(obj, menu, event):
    menu.close()
    menu.graphics()


def showAudio(obj, menu, event):
    menu.close()
    menu.audio()


def setMasterVolume(slider):
    slider.menu.game.audioLoader.setMasterVolume(slider.getAmount())
    config["audio"]["volume"]["master"] = slider.getAmount()
    dump(config)


# Show the main menu of the option menu (for back buttons)
def showMain(obj, menu, event):
    menu.close()
    menu.main(False)


# Toggle anti-aliasing in the graphics menu
def toggleAlias(obj, menu, event):
    toggle = not config["graphics"]['antiAliasing']
    config["graphics"]['antiAliasing'] = toggle

    text = "On" if toggle else "Off"

    obj.setText("AntiAliasing: " + text)

    dump(config)


# Toggle fullscreen in the graphics menu
def toggleFullscreen(obj, menu, event):
    menu.game.fullscreen = not menu.game.fullscreen

    text = "On" if menu.game.fullscreen else "Off"

    if menu.game.fullscreen:
        menu.renderer.setFullscreen()

    else:
        menu.renderer.unsetFullscreen()

    obj.setText("Fullscreen: " + text)

    config["graphics"]["fullscreen"] = menu.game.fullscreen
    dump(config)


# Toggle scanlines effect on and off in the graphics menu
def toggleScanlines(obj, menu, event):
    toggle = not config["graphics"]["scanlines"]["enabled"]
    config["graphics"]["scanlines"]["enabled"] = toggle

    text = "On" if toggle else "Off"

    obj.setText("Scanlines: " + text)

    dump(config)


# Toggle between smooth and harsh scaling
def toggleScalingMode(obj, menu, event):
    toggle = not config["graphics"]["smoothscale"]
    config["graphics"]["smoothscale"] = toggle

    text = "smooth" if toggle else "harsh"

    obj.setText("Scaling: " + text)

    dump(config)
    menu.renderer.setScale(
        (menu.renderer.getWindowWidth(), menu.renderer.getWindowHeight()),
        menu.game.fullscreen)


# Toggle vsync between on and off
def toggleVsync(obj, menu, event):
    menu.game.vsync = not menu.game.vsync

    text = "On" if menu.game.vsync else "Off"

    obj.setText("Vsync: " + text)

    config["graphics"]["vsync"] = menu.game.vsync
    dump(config)

    menu.renderer.setScale(
        (menu.renderer.getWindowWidth(), menu.renderer.getWindowHeight()),
        menu.game.fullscreen)
