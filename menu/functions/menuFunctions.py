
import pygame
from pygame.locals import *
from config import *
from clickManager import *
import time

import generalFunctions as generalFunctions
import hudFunctions as hudFunctions
from transitionFunctions import *


###### Main-Menu Functions ######

# load the level and show transition
def continueGame(obj, menu, event):
    def callback(obj, menu):
        menu.game.spriteRenderer.createLevel(menu.game.mapLoader.getMap("Test"))
        menu.game.spriteRenderer.setRendering(True, True) #Load the hud
        menu.close()
        obj.y = 0

    menu.slideTransitionY((0, config["graphics"]["displayHeight"]), 'first', callback = callback)


def openLevelSelect(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.close()
            menu.levelSelect(True)

    # menu.slideTransitionY((0, config["graphics"]["displayHeight"]), 'first', callback = callback)
    menu.slideTransitionY((0, -config["graphics"]["displayHeight"]), 'first', speed = 40, callback = callback, direction = 'down')
    menu.loadingScreen()


# Navigate back to the main page of the main menu (from within the main menu itself)
def openMainMenu(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.close()
            menu.main(True)

    menu.slideTransitionY((0, -config["graphics"]["displayHeight"]), 'first', speed = 40, callback = callback, direction = 'down')


# load the map editor and show transition
def openMapEditor(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.paused = False
            menu.game.mapEditor.createLevel(clearChanges = True)
            menu.game.mapEditor.setRendering(True, True) #Load the hud
            hudFunctions.addConnection(obj, menu, event) # default option to add connection
            menu.levelSelectOpen = False
            menu.close()

    menu.slideTransitionY((0, config["graphics"]["displayHeight"]), 'first', callback = callback)


# load a specified map which has been clicked on
def loadLevel(obj, menu, event, level):
    if not menu.getTransitioning():
        global levelName
        levelName = level

        def callback(obj, menu, animation):
            obj.y = 0

            if obj.rect.y == 0:
                obj.removeAnimation(animation)
                menu.game.spriteRenderer.createLevel(levelName)
                menu.game.spriteRenderer.setRendering(True, True) #Load the hud
                menu.levelSelectOpen = False
                menu.close()

        menu.slideTransitionY((0, config["graphics"]["displayHeight"]), 'first', callback = callback)


# Check if a level can be unlocked with the amount of keys the player has,
# if it can then unlock the level, else play an error sound
def unlockLevel(obj, menu, event, level):
    if not level.getLevelData()["locked"]["isLocked"]:
        return 
    
    if config["player"]["keys"] >= level.getLevelData()["locked"]["unlock"]:
        menu.game.audioLoader.playSound("uiSuccess", 0)
        config["player"]["keys"] -= level.getLevelData()["locked"]["unlock"]
        level.getLevelData()["locked"]["isLocked"] = False
        menu.game.mapLoader.saveMap(level.getLevelData()["mapName"], level.getLevelData())
        dump(config)

        # if successful update menu
        menu.keyText.setText(str(config["player"]["keys"]))
        level.addEvent(loadLevel, 'onMouseClick', level = level.getLevel())
        level.removeEvent(unlockLevel, 'onMouseClick', level = level)
        level.dirty = True
        menu.keyText.dirty = True

    else:
        menu.game.audioLoader.playSound("uiError", 0)


# Move the level scroller foward by one level
def levelForward(obj, menu, event):
    if not menu.getTransitioning() and menu.increaseCurrentLevel():
        menu.setLevelsClickable()

        def callback(obj, menu, x):
            obj.x = x
            menu.setTransitioning(False)

        for index, level in menu.getLevels().items():
            level.addAnimation(transitionX, 'onLoad', speed = -30, transitionDirection = "right", x = level.x - (menu.levelWidth + menu.spacing), callback = callback)
        menu.setTransitioning(True)


# Move the level scroller backwards by one level
def levelBackward(obj, menu, event):
    if not menu.getTransitioning() and menu.decreaseCurrentLevel():
        menu.setLevelsClickable()

        def callback(obj, menu, x):
            obj.x = x
            menu.setTransitioning(False)

        for index, level in menu.getLevels().items():
            level.addAnimation(transitionX, 'onLoad', speed = 30, transitionDirection = "left", x = level.x + (menu.levelWidth + menu.spacing), callback = callback)
        menu.setTransitioning(True)


# quit the game
def closeGame(obj, menu, event):
    menu.close()
    menu.game.playing = False


###### Option-Menu Functions ######

# Exit the game and return to the main menu with transition
def showMainMenu(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.paused = True
            menu.game.spriteRenderer.setRendering(False) # Always close the Game
            menu.game.mapEditor.setRendering(False) # Always close the Editor
            menu.game.textHandler.setActive(False) # Always close any open inputs
            menu.game.mainMenu.main(True)
            menu.close()

    menu.slideTransitionY((0, -config["graphics"]["displayHeight"]), 'first', speed = 40, callback = callback, direction = 'down')


# Exit the game and return to the level selection screen with transition
def showLevelSelect(obj, menu, event):
    def callback(obj, menu, animation):
        obj.y = 0

        if obj.rect.y == 0:
            obj.removeAnimation(animation)
            menu.game.paused = True
            menu.game.spriteRenderer.setRendering(False) # Always close the Game
            menu.game.mapEditor.setRendering(False) # Always close the Editor
            menu.game.textHandler.setActive(False) # Always close any open inputs
            menu.game.mainMenu.levelSelect(True)
            menu.close()

    menu.slideTransitionY((0, -config["graphics"]["displayHeight"]), 'first', speed = 40, callback = callback, direction = 'down')
    menu.loadingScreen()


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

    if menu.game.fullscreen: menu.renderer.setFullscreen()
    else: menu.renderer.unsetFullscreen()

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