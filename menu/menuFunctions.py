
import pygame
from pygame.locals import *
from config import *
from clickManager import *
from transitionFunctions import *


def closeMenu(obj, menu, animation):
    for component in menu.components:
        component.addAnimation(animation, 'onLoad')


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

    


##### Main-Menu Functions #####
def continueGame(obj, menu):
    menu.game.spriteRenderer.createLevel(menu.game.mapLoader.getMap("London"))
    menu.game.spriteRenderer.setRendering(True) #Load the hud
    closeMenu(obj, menu, transitionLeft)


def closeGame(obj, menu):
    menu.close()
    menu.game.playing = False


def openMapEditor(obj, menu):
    menu.game.mapEditor.createLevel()
    menu.game.mapEditor.setRendering(True)
    addConnection(obj, menu) # Set the default hud option to adding a connection
    closeMenu(obj, menu, transitionLeft)


def loadMap(obj, menu):
    path = menu.game.mapLoader.getMap(obj.getText())
    menu.game.spriteRenderer.createLevel(path)
    menu.game.spriteRenderer.setRendering(True)
    closeMenu(obj, menu, transitionLeft)

    

##### Option-Menu Functions #####

# Game option menu
def showMainMenu(obj, menu):
    menu.close()
    menu.game.paused = False
    menu.game.spriteRenderer.setRendering(False) # Always close the Game
    menu.game.mapEditor.setRendering(False) # Always close the Editor
    menu.game.textHandler.setActive(False) # Always close any open inputs
    menu.game.mainMenu.main()


def unpause(obj, menu):
    menu.closeTransition()


def showOptions(obj, menu):
    menu.close()
    menu.options()


def showGraphics(obj, menu):
    menu.close()
    menu.graphics()


# Show the main menu of the option menu (for back buttons)
def showMain(obj, menu):
    menu.close()
    menu.main()


# Toggle anti-aliasing
def toggleAlias(obj, menu):
    toggle = not config["graphics"]['antiAliasing']
    config["graphics"]['antiAliasing'] = toggle

    text = "On" if toggle else "Off"

    obj.setText("AntiAliasing: " + text)

    dump(config)


# Toggle fullscreen
def toggleFullscreen(obj, menu):
    menu.game.fullscreen = not menu.game.fullscreen

    text = "On" if menu.game.fullscreen else "Off"

    if menu.game.fullscreen: menu.renderer.setFullscreen()
    else: menu.renderer.unsetFullscreen()

    obj.setText("Fullscreen: " + text)

    config["graphics"]["fullscreen"] = menu.game.fullscreen
    dump(config)





##### Hud Functions #####
 
# Layer Functions
def showLayers(obj, menu):
    obj.setImageName("layersSelected")

def hideLayers(obj, menu):
    obj.setImageName("layers")

def hideLayersWhite(obj, menu):
    obj.setImageName("layersWhite")

def changeGameLayer(obj, menu):
    current = menu.game.spriteRenderer.getLayer()
    current += 1 if current < 4 else -3
    menu.game.spriteRenderer.showLayer(current)

# Home button functions
def showHome(obj, menu):
    obj.setImageName("homeSelected")


def hideHome(obj, menu):
    obj.setImageName("home")


def goHome(obj, menu):
    menu.game.optionMenu.main()



#### Editor Hud Function ####

def clearMenu(obj, menu):
    menu.close()
    menu.main()

def closeMapEditor(obj, menu):
    menu.game.textHandler.setActive(False)
    showMainMenu(obj, menu)


def toggleFileDropdown(obj, menu):
    if not menu.fileDropdownOpen:
        clearMenu(obj, menu)
        menu.fileDropdown()
    else:
        clearMenu(obj, menu)


def newMap(obj, menu):
    menu.game.mapEditor.createLevel() # no level creates an empty, clear map    
    clearMenu(obj, menu)


def runMap(obj, menu):
    level = menu.game.mapEditor.getLevelData()
    menu.game.mapEditor.setRendering(False)

    menu.game.spriteRenderer.createLevel(level, True)
    menu.game.spriteRenderer.setRendering(True) #Load the hud


def deleteMap(obj, menu):
    if menu.game.mapEditor.getSaved() and menu.game.mapEditor.getDeletable():
        menu.game.mapEditor.deleteLevel()
        closeMapEditor(obj, menu)


def changeEditorLayer(obj, menu):
    current = menu.game.mapEditor.getLayer()
    current += 1 if current < 4 else -3
    menu.game.mapEditor.showLayer(current)
    menu.updateLayerText()



def loadEditorMap(obj, menu):
    path = menu.game.mapLoader.getMap(obj.getText())
    menu.game.mapEditor.createLevel(path)
    clearMenu(obj, menu)


def toggleAddDropdown(obj, menu):
    if not menu.addDropdownOpen:
        clearMenu(obj, menu)
        menu.addDropdown()
    else:
        clearMenu(obj, menu)


def toggleDeleteDropdown(obj, menu):
    if not menu.deleteDropdownOpen:
        clearMenu(obj, menu)
        menu.deleteDropdown()
    else:
        clearMenu(obj, menu)


def toggleLoadDropdown(obj, menu):
    if not menu.loadBoxOpen:
        menu.loadDropdown()
    else:
        clearMenu(obj, menu)
        menu.fileDropdown()


def toggleSaveBox(obj, menu):
    if not menu.saveBoxOpen:
        if menu.game.mapEditor.getSaved():
            menu.game.mapEditor.saveLevel()
            closeMapEditor(obj, menu)
        else:
            menu.game.textHandler.setActive(True)
            menu.saveBox()
    else:
        menu.game.textHandler.setActive(False)
        clearMenu(obj, menu)
        menu.fileDropdown()


def toggleSaveAsBox(obj, menu):
    if not menu.saveBoxOpen:
        menu.game.textHandler.setActive(True)
        menu.saveBox()
    else:
        menu.game.textHandler.setActive(False)
        clearMenu(obj, menu)
        menu.fileDropdown()


def toggleConfirmBox(obj, menu):
    if not menu.confirmBoxOpen:
        if menu.game.mapEditor.getLevelData()["mapName"] != "":
            menu.confirmBox()
    else:
        clearMenu(obj, menu)
        menu.fileDropdown()


def saveMap(obj, menu):
    # Make sure the input is not blank
    text = menu.game.textHandler.getText()
    text = text.replace(" ", "")

    # No input
    if len(text) <= 0 or menu.game.mapLoader.checkMapExists(text):
        # Maybe show some text explaining the error?
        menu.inputBox.setColor(RED)
        menu.inputBox.dirty = True
    else:
        # Save and close
        menu.game.mapEditor.saveLevelAs()
        closeMapEditor(obj, menu)


def addTransport(obj, menu):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.TRANSPORT)
    clearMenu(obj, menu)


def addConnection(obj, menu):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.CONNECTION)
    clearMenu(obj, menu)


def addStop(obj, menu):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.STOP)
    clearMenu(obj, menu)


def deleteTransport(obj, menu):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DTRANSPORT)
    clearMenu(obj, menu)


def deleteConnection(obj, menu):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DCONNECTION)
    clearMenu(obj, menu)


def deleteStop(obj, menu):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DSTOP)
    clearMenu(obj, menu)


#### Preview Hud Functions ####
def stopMap(obj, menu):
    level = menu.game.spriteRenderer.getLevelData()
    menu.game.spriteRenderer.setRendering(False) # Close the hud

    menu.game.mapEditor.createLevel(level)
    menu.game.mapEditor.setRendering(True)