
import pygame
from pygame.locals import *
from config import *
from clickManager import *

import generalFunctions as generalFunctions
import menuFunctions as menuFunctions
from transitionFunctions import *


##### Hud Functions #####
 
# hover over layer change image
def showLayers(obj, menu, event):
    obj.setImageName("layersSelected")


# hover out layer change image
def hideLayers(obj, menu, event):
    obj.setImageName("layers")


# hver over layer change image to white version
def hideLayersWhite(obj, menu, event):
    obj.setImageName("layersWhite")


# Change the layer showing on the screen
def changeGameLayer(obj, menu, event):
    current = menu.game.spriteRenderer.getLayer()
    current += 1 if current < 4 else -3
    menu.game.spriteRenderer.showLayer(current)


# hover over home button change image
def showHome(obj, menu, event):
    obj.setImageName("homeSelected")


# hover out home button change image
def hideHome(obj, menu, event):
    obj.setImageName("home")


# Show the option menu
def goHome(obj, menu, event):
    menu.game.optionMenu.main()




#### Editor Hud Function ####

def closeMapEditor(obj, menu, event):
    menu.game.textHandler.setActive(False)
    menuFunctions.showMainMenu(obj, menu, event)


def toggleFileDropdown(obj, menu, event):
    if not menu.fileDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)


def newMap(obj, menu, event):
    menu.game.mapEditor.createLevel() # no level creates an empty, clear map    
    menu.game.mapEditor.getClickManager().clearNodes()
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.CONNECTION)
    generalFunctions.clearMenu(obj, menu)


def runMap(obj, menu, event):
    level = menu.game.mapEditor.getLevelData()
    menu.game.mapEditor.setRendering(False)

    menu.game.spriteRenderer.createLevel(level, True) # run the map in debug mode
    menu.game.spriteRenderer.setRendering(True) #Load the hud


def deleteMap(obj, menu, event):
    if menu.game.mapEditor.getSaved() and menu.game.mapEditor.getDeletable():
        menu.game.mapEditor.deleteLevel()
        closeMapEditor(obj, menu, event)


def changeEditorLayer(obj, menu, event):
    current = menu.game.mapEditor.getLayer()
    current += 1 if current < 4 else -3
    menu.game.mapEditor.showLayer(current)
    menu.updateLayerText()



def loadEditorMap(obj, menu, event):
    path = menu.game.mapLoader.getMap(obj.getText())
    menu.game.mapEditor.createLevel(path)
    generalFunctions.clearMenu(obj, menu)


def toggleEditDropdown(obj, menu, event):
    if not menu.editDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        menu.editDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)


def toggleAddDropdown(obj, menu, event):
    if not menu.addDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        menu.addDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)


def toggleDeleteDropdown(obj, menu, event):
    if not menu.deleteDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        menu.deleteDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)


def toggleLoadDropdown(obj, menu, event):
    if not menu.loadBoxOpen:
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()
        menu.loadDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleSaveBox(obj, menu, event):
    if not menu.saveBoxOpen:
        # if the level has been saved before, we don't need to let them choose a name just save it
        if menu.game.mapEditor.getSaved():
            menu.game.mapEditor.saveLevel()
            closeMapEditor(obj, menu, event)
        else:
            menu.game.textHandler.setActive(True)
            generalFunctions.clearMenu(obj, menu)
            menu.fileDropdown()
            menu.saveBox()
    else:
        menu.game.textHandler.setActive(False)
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleSaveAsBox(obj, menu, event):
    if not menu.saveBoxOpen:
        menu.game.textHandler.setActive(True)
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()
        menu.saveBox()
    else:
        menu.game.textHandler.setActive(False)
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleConfirmBox(obj, menu, event):
    if not menu.confirmBoxOpen:
        if menu.game.mapEditor.getLevelData()["mapName"] != "":
            generalFunctions.clearMenu(obj, menu)
            menu.fileDropdown()
            menu.confirmBox()
    else:
        generalFunctions.clearMenu(obj, menu)
        menu.fileDropdown()


def saveMap(obj, menu, event):
    # Make sure the input is not blank
    text = menu.game.textHandler.getText()
    text = text.replace(" ", "")

    # issue with map itself
    if not menu.game.mapEditor.canSaveLevel()[0]:
        menu.game.mapEditor.getMessageSystem().addMessage(menu.game.mapEditor.canSaveLevel()[1])
    # No input
    elif len(text) <= 0:
        menu.inputBox.setColor(RED)
        menu.inputBox.dirty = True
        menu.game.mapEditor.getMessageSystem().addMessage("Map name cannot be empty!")
    # name already exists
    elif menu.game.mapLoader.checkMapExists(text):
        menu.inputBox.setColor(RED)
        menu.inputBox.dirty = True
        menu.game.mapEditor.getMessageSystem().addMessage("Map name already exists!")
    else:
        # Save and close
        menu.game.mapEditor.saveLevelAs()
        closeMapEditor(obj, menu, event)


def toggleEditSizeDropdown(obj, menu, event):
    if not menu.editSizeDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        menu.editDropdown()
        menu.editSizeDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)
        menu.editDropdown()


def toggleAddStopDropdown(obj, menu, event):
    if not menu.addStopDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        addStop(obj, menu, event)
        menu.addDropdown()
        menu.addStopDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)
        menu.addDropdown()


def toggleAddTransportDropdown(obj, menu, event):
    if not menu.addTransportDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        addTransport(obj, menu, event)
        menu.addDropdown()
        menu.addTransportDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)
        menu.addDropdown()


def toggleAddDestinationDropdown(obj, menu, event):
    if not menu.addDestinationDropdownOpen:
        generalFunctions.clearMenu(obj, menu)
        addDestination(obj, menu, event)
        menu.addDropdown()
        menu.addDestinationDropdown()
    else:
        generalFunctions.clearMenu(obj, menu)
        menu.addDropdown()


# Setting the different map sizes
def setSize0(obj, menu, event):
    menu.game.mapEditor.setMapSize((16, 9))

    level = menu.game.mapEditor.getLevelData()
    menu.game.mapEditor.createLevel(level) #reload the level
    generalFunctions.clearMenu(obj, menu)
    

def setSize1(obj, menu, event):
    menu.game.mapEditor.setMapSize((18, 10))

    level = menu.game.mapEditor.getLevelData()
    menu.game.mapEditor.createLevel(level) #reload the level
    generalFunctions.clearMenu(obj, menu)


def setSize2(obj, menu, event):
    menu.game.mapEditor.setMapSize((20, 11))

    level = menu.game.mapEditor.getLevelData()
    menu.game.mapEditor.createLevel(level) #reload the level
    generalFunctions.clearMenu(obj, menu)

    

def setSize3(obj, menu, event):
    menu.game.mapEditor.setMapSize((22, 12))

    level = menu.game.mapEditor.getLevelData()
    menu.game.mapEditor.createLevel(level) #reload the level
    generalFunctions.clearMenu(obj, menu)
    


def addConnection(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.CONNECTION)
    generalFunctions.clearMenu(obj, menu)


def addStop(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.STOP)


def addTransport(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.TRANSPORT)


def addDestination(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DESTINATION)



#### Adding different stop and transport  types ####
def addMetro(obj, menu, event):
    menu.game.mapEditor.getClickManager().setAddType("metro")
    generalFunctions.clearMenu(obj, menu)


def addBus(obj, menu, event):
    menu.game.mapEditor.getClickManager().setAddType("bus")
    generalFunctions.clearMenu(obj, menu)


def addTram(obj, menu, event):
    menu.game.mapEditor.getClickManager().setAddType("tram")
    generalFunctions.clearMenu(obj, menu)

def addTaxi(obj, menu, event):
    menu.game.mapEditor.getClickManager().setAddType("taxi")
    generalFunctions.clearMenu(obj, menu)


#### Adding different destination types ####
def addAirport(obj, menu, event):
    menu.game.mapEditor.getClickManager().setAddType("airport")
    generalFunctions.clearMenu(obj, menu)


def addOffice(obj, menu, event):
    menu.game.mapEditor.getClickManager().setAddType("office")
    generalFunctions.clearMenu(obj, menu)






def deleteTransport(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DTRANSPORT)
    generalFunctions.clearMenu(obj, menu)


def deleteConnection(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DCONNECTION)
    generalFunctions.clearMenu(obj, menu)


def deleteStop(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DSTOP)
    generalFunctions.clearMenu(obj, menu)


def deleteDestination(obj, menu, event):
    menu.game.mapEditor.getClickManager().setClickType(EditorClickManager.ClickType.DDESTINATION)
    generalFunctions.clearMenu(obj, menu)



    #### Preview Hud Functions ####
def stopMap(obj, menu, event):
    level = menu.game.spriteRenderer.getLevelData()
    menu.game.spriteRenderer.setRendering(False) # Close the hud

    menu.game.mapEditor.createLevel(level)
    menu.game.mapEditor.setRendering(True)