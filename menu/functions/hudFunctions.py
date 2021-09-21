
from config import RED
from clickManager import EditorClickManager
import generalFunctions as gf
import menuFunctions as mf

# ----General hud functions----


def hoverOverHudButton(obj, menu, event, image=None):
    menu.setHudButtonHoverOver(True)
    if image is not None:
        gf.hoverImage(obj, menu, event, image=image)


def hoverOutHudButton(obj, menu, event, image=None):
    menu.setHudButtonHoverOver(False)
    if image is not None:
        gf.hoverImage(obj, menu, event, image=image)


# Change the layer showing on the screen
def changeGameLayer(obj, menu, event):
    current = menu.game.spriteRenderer.getCurrentLayer()
    connectionTypes = menu.game.spriteRenderer.getConnectionTypes()

    if len(connectionTypes) <= 1:
        return

    current += 1 if current < 4 else -3

    while "layer " + str(current) not in connectionTypes:
        current += 1

    menu.game.spriteRenderer.showLayer(current)


# Show the option menu
def goHome(obj, menu, event):
    menu.game.optionMenu.main(True, True)


# Pause the game and change the pause icon
def pauseGame(obj, menu, event):
    menu.togglePauseGame(True)


# Speed up the game so you don't have to wait for things to move
def fastForwardGame(obj, menu, event):
    menu.game.clickManager.setSpeedUp(True)


# ----Editor Hud Function----

def closeMapEditor(obj, menu, event):
    menu.game.textHandler.setActive(False)
    mf.showMainMenu(obj, menu, event)


def toggleFileDropdown(obj, menu, event):
    if not menu.fileDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.fileDropdown()

    else:
        gf.clearMenu(obj, menu)


def newMap(obj, menu, event):
    # no level creates an empty, clear map
    menu.mapEditor.createLevel(clearChanges=True)
    menu.mapEditor.getClickManager().clearNodes()
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.CONNECTION)
    gf.clearMenu(obj, menu)


def runMap(obj, menu, event):
    level = menu.mapEditor.getLevelData()
    menu.mapEditor.setRendering(False)

    # run the map in debug mode
    menu.game.spriteRenderer.createLevel(level, True)
    # Load the hud
    menu.game.spriteRenderer.setRendering(True)


def deleteMap(obj, menu, event):
    if menu.mapEditor.getSaved() and menu.mapEditor.getDeletable():
        menu.mapEditor.deleteLevel()
        closeMapEditor(obj, menu, event)


def changeEditorLayer(obj, menu, event, current=False):
    if not current:
        current = menu.mapEditor.getCurrentLayer()
        current += 1 if current < 4 else -3
    menu.mapEditor.showLayer(current)
    menu.updateLayerText()
    gf.clearMenu(obj, menu)


def loadEditorMap(obj, menu, event):
    menu.game.audioLoader.playSound("playerSuccess", 2)
    path = menu.game.mapLoader.getMap(obj.getText())
    menu.mapEditor.createLevel(path, clearChanges=True)
    gf.clearMenu(obj, menu)


def toggleEditDropdown(obj, menu, event):
    if not menu.editDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.editDropdown()

    else:
        gf.clearMenu(obj, menu)


def toggleViewDropdown(obj, menu, event):
    if not menu.viewDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.viewDropdown()

    else:
        gf.clearMenu(obj, menu)


def toggleAddDropdown(obj, menu, event):
    if not menu.addDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.addDropdown()

    else:
        gf.clearMenu(obj, menu)


def toggleDeleteDropdown(obj, menu, event):
    if not menu.deleteDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.deleteDropdown()

    else:
        gf.clearMenu(obj, menu)


def toggleLoadDropdown(obj, menu, event):
    if not menu.loadBoxOpen:
        gf.clearMenu(obj, menu)
        menu.fileDropdown()
        menu.loadDropdown()

    else:
        gf.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleSaveBox(obj, menu, event):
    if not menu.saveBoxOpen:
        # if the level has been saved before,
        # we don't need to let them choose a name just save it
        if menu.mapEditor.getSaved():
            menu.mapEditor.saveLevel()
            closeMapEditor(obj, menu, event)

        else:
            menu.game.textHandler.setActive(True)
            gf.clearMenu(obj, menu)
            menu.fileDropdown()
            menu.saveBox()

    else:
        menu.game.textHandler.setActive(False)
        gf.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleSaveAsBox(obj, menu, event):
    if not menu.saveBoxOpen:
        menu.game.textHandler.setActive(True)
        gf.clearMenu(obj, menu)
        menu.fileDropdown()
        menu.saveBox()

    else:
        menu.game.textHandler.setActive(False)
        gf.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleConfirmBox(obj, menu, event):
    if not menu.confirmBoxOpen:
        if menu.mapEditor.getLevelData()["mapName"] != "":
            gf.clearMenu(obj, menu)
            menu.fileDropdown()
            menu.confirmBox()

    else:
        gf.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleConfirmExitBox(obj, menu, event):
    if not menu.confirmExitBoxOpen:
        if len(menu.mapEditor.getLevelChanges()) > 1:
            gf.clearMenu(obj, menu)
            menu.fileDropdown()
            menu.confirmExitBox()

        else:
            closeMapEditor(obj, menu, event)

    else:
        gf.clearMenu(obj, menu)
        menu.fileDropdown()


def toggleTotalToCompleteBox(obj, menu, event):
    if not menu.totalToCompleteBoxOpen:
        menu.game.textHandler.setActive(True)
        gf.clearMenu(obj, menu)
        menu.editDropdown()
        menu.totalToCompleteBox()

    else:
        menu.game.textHandler.setActive(False)
        gf.clearMenu(obj, menu)
        menu.editDropdown()


def toggleTransport(obj, menu, event):
    menu.mapEditor.setShowTransport(not menu.mapEditor.getShowTransport())
    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)
    gf.clearMenu(obj, menu)


def saveMap(obj, menu, event):
    # Make sure the input is not blank
    text = menu.game.textHandler.getString()
    text = text.replace(" ", "")

    # issue with map itself
    if not menu.mapEditor.canSaveLevel()[0]:
        menu.mapEditor.getMessageSystem().addMessage(
            menu.mapEditor.canSaveLevel()[1])
    # No input
    elif len(text) <= 0:
        menu.inputBox.setColor(RED)
        menu.inputBox.dirty = True
        menu.mapEditor.getMessageSystem().addMessage(
            "Map name cannot be empty!")
    # name already exists
    elif menu.game.mapLoader.checkMapExists(text):
        menu.inputBox.setColor(RED)
        menu.inputBox.dirty = True
        menu.mapEditor.getMessageSystem().addMessage(
            "Map name already exists!")

    else:
        # Save and close
        menu.mapEditor.saveLevelAs()
        closeMapEditor(obj, menu, event)


def incrementTotalToComplete(obj, menu, event):
    total = int(menu.total.getText())

    # TODO: make a cap for total needed to complete level
    if total + 1 <= 20:
        menu.total.setText(total + 1)
        menu.total.dirty = True


def decrementTotalToComplete(obj, menu, event):
    total = int(menu.total.getText())

    if total - 1 >= 1:
        menu.total.setText(total - 1)
        menu.total.dirty = True


def toggleEditSizeDropdown(obj, menu, event):
    if not menu.editSizeDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.editDropdown()
        menu.editSizeDropdown()

    else:
        gf.clearMenu(obj, menu)
        menu.editDropdown()


def toggleEditBackgroundDropdown(obj, menu, event):
    if not menu.editBackgroundDropdownOpen:
        gf.clearMenu(obj, menu)
        menu.editDropdown()
        menu.editBackgroundDrodown()

    else:
        gf.clearMenu(obj, menu)
        menu.editDropdown()


def toggleAddStopDropdown(obj, menu, event):
    if not menu.addStopDropdownOpen:
        gf.clearMenu(obj, menu)
        addStop(obj, menu, event)
        menu.addDropdown()
        menu.addStopDropdown()

    else:
        gf.clearMenu(obj, menu)
        menu.addDropdown()


def toggleAddTransportDropdown(obj, menu, event):
    if not menu.addTransportDropdownOpen:
        gf.clearMenu(obj, menu)
        addTransport(obj, menu, event)
        menu.addDropdown()
        menu.addTransportDropdown()

    else:
        gf.clearMenu(obj, menu)
        menu.addDropdown()


def toggleAddDestinationDropdown(obj, menu, event):
    if not menu.addDestinationDropdownOpen:
        gf.clearMenu(obj, menu)
        addDestination(obj, menu, event)
        menu.addDropdown()
        menu.addDestinationDropdown()

    else:
        gf.clearMenu(obj, menu)
        menu.addDropdown()


def toggleAddSpecialsDropdown(obj, menu, event):
    if not menu.addSpecialsDropdownOpen:
        gf.clearMenu(obj, menu)
        addSpecials(obj, menu, event)
        menu.addDropdown()
        menu.addSpecialsDropdown()

    else:
        gf.clearMenu(obj, menu)
        menu.addDropdown()


# Setting the different map sizes
def setSize0(obj, menu, event):
    menu.mapEditor.setMapSize((16, 9))

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level
    gf.clearMenu(obj, menu)


def setSize1(obj, menu, event):
    menu.mapEditor.setMapSize((18, 10))

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level
    gf.clearMenu(obj, menu)


def setSize2(obj, menu, event):
    menu.mapEditor.setMapSize((20, 11))

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level
    gf.clearMenu(obj, menu)


def setSize3(obj, menu, event):
    menu.mapEditor.setMapSize((22, 12))

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level
    gf.clearMenu(obj, menu)


def setBackgroundColor(obj, menu, event, layer, color, darkMode=False):
    menu.mapEditor.setBackgroundColor(layer, color, darkMode)

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level
    gf.clearMenu(obj, menu)


def setTotalToComplete(obj, menu, event):
    total = int(menu.total.getText())
    menu.mapEditor.setTotalToComplete(total)
    menu.game.textHandler.setActive(False)
    gf.clearMenu(obj, menu)


def undoChange(obj, menu, event):
    menu.mapEditor.undoChange()

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level

    # change the color of the undo / redo buttons
    gf.clearMenu(obj, menu)
    menu.editDropdown()


def redoChange(obj, menu, next):
    menu.mapEditor.redoChange()

    level = menu.mapEditor.getLevelData()
    layer = menu.mapEditor.getCurrentLayer()
    menu.mapEditor.createLevel(level, layer=layer)  # Reload the level

    # change the color of the undo / redo buttons
    gf.clearMenu(obj, menu)
    menu.editDropdown()


def addConnection(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.CONNECTION)
    gf.clearMenu(obj, menu)


def addStop(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.STOP)


def addTransport(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.TRANSPORT)


def addDestination(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.DESTINATION)


def addSpecials(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.SPECIAL)


# ----Adding different stop and transport types----

def addMetro(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("metro")
    gf.clearMenu(obj, menu)


def addBus(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("bus")
    gf.clearMenu(obj, menu)


def addTram(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("tram")
    gf.clearMenu(obj, menu)


def addTaxi(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("taxi")
    gf.clearMenu(obj, menu)


# ----Adding different destination types----

def addAirport(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("airport")
    gf.clearMenu(obj, menu)


def addOffice(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("office")
    gf.clearMenu(obj, menu)


def addHouse(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("house")
    gf.clearMenu(obj, menu)


# ----Adding special node types----

def addNoWalkNode(obj, menu, event):
    menu.mapEditor.getClickManager().setAddType("noWalkNode")
    gf.clearMenu(obj, menu)


def deleteTransport(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.DTRANSPORT)
    gf.clearMenu(obj, menu)


def deleteConnection(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.DCONNECTION)
    gf.clearMenu(obj, menu)


def deleteStop(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.DSTOP)
    gf.clearMenu(obj, menu)


def deleteDestination(obj, menu, event):
    menu.mapEditor.getClickManager().setClickType(
        EditorClickManager.ClickType.DDESTINATION)
    gf.clearMenu(obj, menu)


# ----Preview Hud Functions----

def stopMap(obj, menu, event):
    level = menu.game.spriteRenderer.getLevelData()
    menu.game.spriteRenderer.setRendering(False)  # Close the hud

    menu.game.mapEditor.createLevel(level)
    menu.game.mapEditor.setRendering(True)
