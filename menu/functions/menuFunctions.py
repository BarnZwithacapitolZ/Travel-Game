
import pygame
from config import config, dump
from utils import vec
import hudFunctions as hf
import menu as MENU


def openLevelSelect(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)

            menu.game.paused = True
            menu.game.spriteRenderer.setRendering(False)

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
            # Load the hud for the map editor
            menu.game.mapEditor.setRendering(True, True)

            # We never want the spriteRenderer to be rendering on the mapEditor
            menu.game.spriteRenderer.setRendering(False)

            # Default option to add connection
            hf.addConnection(obj, menu, event, False)
            # Reset to default add type (nothing)
            menu.game.mapEditor.getClickManager().setAddType("")

            menu.levelSelectOpen = False
            menu.customLevelSelectOpen = False
            menu.close()

    menu.slideTransitionY(
        (0, config["graphics"]["displayHeight"]), 'first', callback=callback)


def openOptionsMenu(obj, menu, event):
    menu.close()
    menu.game.optionMenu.setOptionsOpen(True)
    menu.game.optionMenu.options(True)


def closeOptionsMenu(obj, menu, event):
    def callback(obj, menu, y):
        menu.close()
        menu.setOptionsOpen(False)
        menu.game.mainMenu.main()

    menu.closeTransition(callback)


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
            menu.game.paused = True
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

            levelSelectType = menu.game.mainMenu.getPreviousLevelSelect()
            if levelSelectType == MENU.MainMenu.LevelSelect.LEVELSELECT:
                menu.game.mainMenu.levelSelect(True)
            elif (levelSelectType
                    == MENU.MainMenu.LevelSelect.CUSTOMLEVELSELECT):
                menu.game.mainMenu.customLevelSelect(True)

            menu.close()

    menu.slideTransitionY(
        (0, -config["graphics"]["displayHeight"]), 'first', speed=40,
        callback=callback, direction='down')
    menu.loadingScreen()


def showCustomLevelSelect(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)

            menu.close()
            menu.game.mainMenu.customLevelSelect(True)

    menu.slideTransitionY(
        (0, -config["graphics"]["displayHeight"]), 'first', speed=40,
        callback=callback, direction='down')
    menu.loadingScreen()


# unpause the game and hide the option menu
def unpause(obj, menu, event):
    menu.closeTransition()


# show the options screen
def showOptions(obj, menu, event):
    # Reset texthandler in case it is left active
    menu.game.textHandler.setActive(False)
    # Check for any duplicate controls in case of exit before entry
    menu.checkForExistingControls()

    menu.close()
    menu.options()


# show the grahics screen
def showGraphics(obj, menu, event):
    menu.close()
    menu.graphics()


def showAudio(obj, menu, event):
    menu.close()
    menu.audio()


def showControls(obj, menu, event):
    menu.close()
    menu.controls()


def setMasterVolume(slider, amount):
    slider.menu.game.audioLoader.setMasterVolume(amount)
    slider.setAmount(amount)
    config["audio"]["volume"]["master"]["current"] = amount
    dump(config)


def setSoundVolume(slider, amount):
    slider.menu.game.audioLoader.setSoundVolume(amount)
    slider.setAmount(amount)
    config["audio"]["volume"]["sounds"]["current"] = amount
    dump(config)


def setMusicVolume(slider, amount):
    slider.menu.game.audioLoader.setMusicVolume(amount)
    slider.setAmount(amount)
    config["audio"]["volume"]["music"]["current"] = amount
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


def clearKeyText(obj, menu, event):
    if menu.controlClickManager.getControlKey() is None:
        obj.setKeyText("Press new key")
        obj.setKeyTextFontSize(23)
        obj.setKeyTextBorder(False)
        obj.addEvent(setKeyText, 'onKeyPress')
        menu.controlClickManager.setControlKey(obj)
        menu.game.textHandler.setActive(True)
        obj.dirty = True

    else:
        previousKey = menu.controlClickManager.getControlKey()
        previousKey.setKeyText(pygame.key.name(previousKey.getKeyInt()))
        previousKey.setKeyTextFontSize(previousKey.getFontSizeInt())
        previousKey.setKeyTextBorder(True)
        previousKey.removeEvent(setKeyText, 'onKeyPress')
        menu.controlClickManager.setControlKey(None)
        previousKey.dirty = True

        clearKeyText(obj, menu, event)


def setKeyText(obj, menu, event):
    newKey = menu.game.textHandler.getCurrentKey()
    pressedObj = menu.checkForExistingControl(newKey, obj.getKeyName())

    obj.setKeyInt(newKey)
    obj.setKeyText(pygame.key.name(newKey))
    obj.setKeyTextFontSize(obj.getFontSizeInt())
    obj.setKeyTextBorder(True)

    config["controls"][obj.getKeyName()]["current"] = newKey
    dump(config)

    menu.game.textHandler.setActive(False)
    obj.removeEvent(setKeyText, 'onKeyPress')

    if pressedObj and obj.getKeyName() != pressedObj.getKeyName():
        clearKeyText(pressedObj, menu, event)

    # We have reached the end of the setting stream,
    # now we can save our progress by reloading the menu
    else:
        showControls(obj, menu, event)


def resetControls(obj, menu, event):
    for key, control in menu.controlKeys.items():
        newKey = config["controls"][control.getKeyName()]["default"]
        config["controls"][control.getKeyName()]["current"] = newKey
        dump(config)

        menu.game.textHandler.setActive(False)
        control.removeEvent(setKeyText, 'onKeyPress')

        showControls(obj, menu, event)


def resetAudio(obj, menu, event):
    setMasterVolume(
        menu.masterVolume, config["audio"]["volume"]["master"]["default"])
    setSoundVolume(
        menu.soundVolume, config["audio"]["volume"]["sounds"]["default"])
    setMusicVolume(
        menu.musicVolume, config["audio"]["volume"]["music"]["default"])
