
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
    menu.close()
    menu.levelSelect()


# load the map editor and show transition
def openMapEditor(obj, menu, event):
    def callback(obj, menu):
        menu.game.mapEditor.createLevel(clearChanges = True)
        menu.game.mapEditor.setRendering(True, True) #Load the hud
        hudFunctions.addConnection(obj, menu, event) # default option to add connection
        menu.close()
        obj.y = 0

    menu.slideTransitionY((0, config["graphics"]["displayHeight"]), 'first', callback = callback)


# load a specified map which has been clicked on
def loadMap(obj, menu, event):
    path = menu.game.mapLoader.getMap(obj.getText())
    menu.game.spriteRenderer.createLevel(path)
    menu.game.spriteRenderer.setRendering(True)

    # TODO: need to change this transition
    for component in menu.components:
        component.addAnimation(transitionLeft, 'onLoad')


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


def loadLevel(obj, menu, event, level):
    global levelName
    levelName = level

    def callback(obj, menu):
        menu.game.spriteRenderer.createLevel(levelName)
        menu.game.spriteRenderer.setRendering(True, True) #Load the hud
        menu.close()
        obj.y = 0

    menu.slideTransitionY((0, config["graphics"]["displayHeight"]), 'first', callback = callback)



###### Option-Menu Functions ######

# Exit the game and return to the main menu with transition
def showMainMenu(obj, menu, event):
    def callback(obj, menu):
        menu.game.paused = False
        menu.game.spriteRenderer.setRendering(False) # Always close the Game
        menu.game.mapEditor.setRendering(False) # Always close the Editor
        menu.game.textHandler.setActive(False) # Always close any open inputs
        menu.game.mainMenu.main(True)
        menu.close()
        obj.y = 0

    menu.slideTransitionY((0, -config["graphics"]["displayHeight"]), 'first', speed = 40, callback = callback, direction = 'down')


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
    menu.main()


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