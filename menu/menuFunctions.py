
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


def showMainMenu(obj, menu):
    menu.close()
    menu.game.paused = False
    menu.game.mainMenu.main()

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



def showLayers(obj, menu):
    obj.setImageName("layersSelected")


def hideLayers(obj, menu):
    obj.setImageName("layers")

def changeLayer(obj, menu):
    current = menu.game.spriteRenderer.getLayer()
    current += 1 if current < 4 else -3
    menu.game.spriteRenderer.showLayer(current)