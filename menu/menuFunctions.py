
import pygame
from pygame.locals import *
from config import *


def closeMenu(obj, menu):
    menu.close()

def unpause(obj, menu):
    menu.close()
    menu.game.paused = False
    menu.game.hud.open = True

def closeGame(obj, menu):
    menu.close()
    menu.game.playing = False


def showMain(obj, menu):
    menu.close()
    menu.main()

def showOptions(obj, menu):
    menu.close()
    menu.options()

def showGraphics(obj, menu):
    menu.close()
    menu.graphics()



def toggleDropdown(obj, menu):
    if not menu.dropdownOpen:
        menu.dropdown()
    else:
        menu.close()
        menu.main()


def toggleOption1(obj, menu):
    if not menu.option1Open:
        menu.option1()
    else:
        menu.close()
        menu.main()
        menu.dropdown()


def toggleOption2(obj, menu):
    if not menu.option2Open:
        menu.option2()
    else:
        menu.close()
        menu.main()
        menu.dropdown()

def toggleAlias(obj, menu):
    toggle = not config["graphics"]['antiAliasing']
    config["graphics"]['antiAliasing'] = toggle

    text = "On" if toggle else "Off"

    obj.setText("AntiAliasing: " + text)

    dump(config)


def toggleFullscreen(obj, menu):
    menu.game.fullscreen = not menu.game.fullscreen

    text = "On" if menu.game.fullscreen else "Off"

    if menu.game.fullscreen: menu.renderer.setFullscreen()
    else: menu.renderer.unsetFullscreen()

    obj.setText("Fullscreen: " + text)

    config["graphics"]["fullscreen"] = menu.game.fullscreen
    dump(config)



def hoverGreen(obj, menu):
    obj.setColor((0, 169, 132))

def hoverWhite(obj, menu):
    obj.setColor(Color("white"))

def hoverBlack(obj, menu):
    obj.setColor(BLACK)


def hoverOver(obj, menu):
    obj.addAnimation(hoverOverAnimation, 'onMouseOver')
    obj.setColor(Color("white"))

def hoverOut(obj, menu):
    obj.addAnimation(hoverOutAnimation, 'onMouseOut')
    obj.setColor(BLACK)


def hoverOverAnimation(obj, menu, animation):
    obj.x += 3

    if obj.x > 110:
        obj.animations.remove(animation)


def hoverOutAnimation(obj, menu, animation):
    obj.x -= 3

    if obj.x < 100:
        obj.animations.remove(animation)



##### Option-Meny Functions #####

# Game option menu
def showMainMenu(obj, menu):
    menu.close()
    menu.game.paused = False
    menu.game.spriteRenderer.setRendering(False) # Close the hud
    menu.game.mapEditor.setRendering(False)
    menu.game.mainMenu.main()



##### Main-Menu Functions #####
def continueGame(obj, menu):
    menu.game.spriteRenderer.createLevel("grid.json")
    menu.game.spriteRenderer.setRendering(True) #Load the hud
    closeMenu(obj, menu)

def openMapEditor(obj, menu):
    menu.game.mapEditor.createLevel()
    menu.game.mapEditor.setRendering(True)
    closeMenu(obj, menu)


def loadMap(obj, menu):
    mapName = obj.getText() + '.json'
    menu.game.spriteRenderer.createLevel(mapName)
    menu.game.spriteRenderer.setRendering(True)
    closeMenu(obj, menu)

    

##### Hud Functions #####
 
# Layer Functions
def showLayers(obj, menu):
    obj.setImageName("layersSelected")

def hideLayers(obj, menu):
    obj.setImageName("layers")

def changeLayer(obj, menu):
    current = menu.game.spriteRenderer.getLayer()
    current += 1 if current < 4 else -3
    menu.game.spriteRenderer.showLayer(current)

# Home button functions
def showHome(obj, menu):
    obj.setImageName("homeSelected")


def hideHome(obj, menu):
    obj.setImageName("home")


def goHome(obj, menu):
    menu.game.paused = not menu.game.paused
    menu.game.hud.open = not menu.game.hud.open # To Do: fix
    menu.game.optionMenu.main()



#### Editor Hud Function ####
def clearMap(obj, menu):
    menu.game.mapEditor.createLevel()
