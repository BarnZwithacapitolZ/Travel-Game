from menu import Menu
from config import (
    config, BLACK, WHITE, GREY, GREEN, YELLOW,
    BACKGROUNDCOLORS, DEFAULTBACKGROUND)
from utils import overrides
import generalFunctions as gf
import menuFunctions as mf
import hudFunctions as hf
import transitionFunctions as tf
from menuComponents import (
    Image, Label, InputBox, Rectangle, Meter, Timer, MessageBox, ControlKey)
from clickManager import EditorClickManager
import abc


# Anything that all the game huds will use
class GameHudLayout(Menu):
    def __init__(self, game):
        super().__init__(game)

    @abc.abstractmethod
    def getHudButtonHoverOver(self):
        return

    @abc.abstractmethod
    def updateLayerText(self):
        return

    @abc.abstractmethod
    def updateSlowDownMeter(self, amount):
        return

    @abc.abstractmethod
    def setLifeAmount(self):
        return

    @abc.abstractmethod
    def toggleFastForward(self, selected=False):
        return

    @abc.abstractmethod
    def togglePauseGame(self, selected=False):
        return


class GameHud(GameHudLayout):
    def __init__(self, spriteRenderer, spacing=(1.5, 1.5)):
        super().__init__(spriteRenderer.game)
        self.spriteRenderer = spriteRenderer

        self.hearts = []
        self.spacing = spacing

        # TODO Currently preview hud has no buttons but if we add buttons to it
        # we will want to make this an attribute of the preview hud too
        self.hudButtonHoverOver = False

        self.hudX = 15
        self.hudY = 15

    @overrides(GameHudLayout)
    def getHudButtonHoverOver(self):
        return self.hudButtonHoverOver

    def setHudButtonHoverOver(self, hudButtonHoverOver):
        self.hudButtonHoverOver = hudButtonHoverOver

    @overrides(GameHudLayout)
    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeter'):
            self.slowDownMeter.setAmount((amount, 20))
            self.slowDownMeter.dirty = True

    def slideHudIn(self):
        def callbackX(obj, menu, x):
            obj.x = x

        def callbackY(obj, menu, y):
            obj.y = y

        speed = 5

        self.fastForward.addAnimation(
            tf.transitionX, 'onLoad', speed=speed, transitionDirection="left",
            x=self.hudX, callback=callbackX)
        self.pause.addAnimation(
            tf.transitionX, 'onLoad', speed=speed, transitionDirection="left",
            x=self.hudX, callback=callbackX)
        self.layers.addAnimation(
            tf.transitionX, 'onLoad', speed=speed, transitionDirection="left",
            x=self.hudX, callback=callbackX)
        self.home.addAnimation(
            tf.transitionX, 'onLoad', speed=speed, transitionDirection="left",
            x=self.hudX, callback=callbackX)

        self.lives.addAnimation(
            tf.transitionY, 'onLoad', speed=speed, transitionDirection="down",
            y=self.hudY, callback=callbackY)
        self.completed.addAnimation(
            tf.transitionY, 'onLoad', speed=speed, transitionDirection="down",
            y=self.hudY + 4, callback=callbackY)
        self.completedAmount.addAnimation(
            tf.transitionY, 'onLoad', speed=speed, transitionDirection="down",
            y=self.hudY + 17, callback=callbackY)
        self.slowDownMeter.addAnimation(
            tf.transitionY, 'onLoad', speed=speed, transitionDirection="down",
            y=self.hudY + 14, callback=callbackY)

    def slideRestartIn(self):
        self.restart.dirty = True  # Make sure its resized
        self.add(self.restart)

        def callback(obj, menu, x):
            obj.x = x

        self.restart.addAnimation(
            tf.transitionX, 'onLoad', speed=5, transitionDirection="left",
            x=self.hudX, callback=callback)

    def slideRestartOut(self):
        def callback(obj, menu, x):
            obj.x = x
            menu.remove(obj)

        self.restart.addAnimation(
            tf.transitionX, 'onLoad', speed=-5, transitionDirection="right",
            x=self.hudX - 100, callback=callback)

    @overrides(GameHudLayout)
    def togglePauseGame(self, selected=False):
        self.spriteRenderer.togglePaused()

        pauseImage = (
            "play" if self.spriteRenderer.getPaused() else "pause")
        pauseImageSelected = (
            "playSelected" if self.spriteRenderer.getPaused()
            else "pauseSelected")
        pauseImage += "White" if self.spriteRenderer.getDarkMode() else ""
        (self.slideRestartIn() if self.spriteRenderer.getPaused()
            else self.slideRestartOut())

        self.pause.setImageName(pauseImageSelected if selected else pauseImage)
        self.pause.clearEvents()
        self.pause.addEvent(
            hf.hoverOverHudButton, 'onMouseOver', image=pauseImageSelected)
        self.pause.addEvent(
            hf.hoverOutHudButton, 'onMouseOut', image=pauseImage)
        self.pause.addEvent(hf.pauseGame, 'onMouseClick')
        self.pause.dirty = True

    @overrides(GameHudLayout)
    def toggleFastForward(self, selected=False):
        if not hasattr(self, 'fastForward') or self.hudButtonHoverOver:
            return

        fastForwardImage = (
            "fastForwardWhite" if self.spriteRenderer.getDarkMode()
            else "fastForward")

        self.fastForward.setImageName(
            "fastForwardSelected" if selected else fastForwardImage)
        self.fastForward.dirty = True

    def main(self, transition=False):
        self.open = True

        meterWidth = self.spriteRenderer.getSlowDownMeterAmount()
        darkMode = self.spriteRenderer.getDarkMode()
        lives = self.spriteRenderer.getLives()

        layersImage = "layersWhite" if darkMode else "layers"
        layersSelectedImage = "layersSelected"
        homeImage = "homeWhite" if darkMode else "home"
        homeSelectedImage = "homeSelected"
        pauseImage = "pauseWhite" if darkMode else "pause"
        pauseSelectedImage = "pauseSelected"
        restartImage = "restartWhite" if darkMode else "restart"
        restartSelectedImage = "restartSelected"
        fastForwardImage = "fastForwardWhite" if darkMode else "fastForward"
        fastForwardSelectedImage = "fastForwardSelected"
        self.textColor = WHITE if darkMode else BLACK

        self.home = Image(self, homeImage, (50, 50), (self.hudX - 100, 500))
        self.layers = Image(
            self, layersImage, (50, 50), (self.hudX - 100, 440))
        self.pause = Image(self, pauseImage, (50, 50), (self.hudX - 100, 320))
        self.restart = Image(
            self, restartImage, (50, 50), (self.hudX - 100, 260))
        self.fastForward = Image(
            self, fastForwardImage, (50, 50), (self.hudX - 100, 380))

        # Show the total amount of lives the user has left
        self.lives = Timer(
            self, self.textColor, GREEN, 100,
            lives if lives is not None else 1, (48, 48), (
                config["graphics"]["displayWidth"] - (48 + self.hudX),
                self.hudY - 104), 5)
        # Show how many people have currently completed the map
        self.completed = Timer(
            self, self.textColor, YELLOW, 0,
            self.spriteRenderer.getTotalToComplete(), (40, 40), (
                config["graphics"]["displayWidth"] - (40 + self.hudX + 4),
                self.hudY - 100), 5)
        # Show the figure (Int) for how many people have completed the map
        self.completedAmount = Label(
            self, str(self.spriteRenderer.getCompleted()), 20,
            self.textColor, (self.completed.x + 14.5, self.completed.y + 13))

        # TODO: do I want the slow down meter????
        self.slowDownMeter = Meter(
            self, WHITE, self.textColor, GREEN, (meterWidth, 20),
            (meterWidth, 20), (config["graphics"]["displayWidth"] - (
                meterWidth + self.lives.width + (self.hudX * 2)),
                self.hudY + 10 - 100), 2)

        self.fastForward.addEvent(
            hf.hoverOverHudButton, 'onMouseOver',
            image=fastForwardSelectedImage)
        self.fastForward.addEvent(
            hf.hoverOutHudButton, 'onMouseOut', image=fastForwardImage)
        self.fastForward.addEvent(hf.fastForwardGame, 'onMouseLongClick')

        self.restart.addEvent(
            hf.hoverOverHudButton, 'onMouseOver', image=restartSelectedImage)
        self.restart.addEvent(
            hf.hoverOutHudButton, 'onMouseOut', image=restartImage)
        self.restart.addEvent(
            mf.loadLevel, 'onMouseClick', level=self.game.mapLoader.getMap(
                self.spriteRenderer.getLevel()))

        self.pause.addEvent(
            hf.hoverOverHudButton, 'onMouseOver', image=pauseSelectedImage)
        self.pause.addEvent(
            hf.hoverOutHudButton, 'onMouseOut', image=pauseImage)
        self.pause.addEvent(hf.pauseGame, 'onMouseClick')

        self.layers.addEvent(
            hf.hoverOverHudButton, 'onMouseOver', image=layersSelectedImage)
        self.layers.addEvent(
            hf.hoverOutHudButton, 'onMouseOut', image=layersImage)
        self.layers.addEvent(hf.changeGameLayer, 'onMouseClick')

        self.home.addEvent(
            hf.hoverOverHudButton, 'onMouseOver', image=homeSelectedImage)
        self.home.addEvent(hf.hoverOutHudButton, 'onMouseOut', image=homeImage)
        self.home.addEvent(hf.goHome, 'onMouseClick')

        self.add(self.home)
        if len(self.spriteRenderer.getConnectionTypes()) > 1:
            self.add(self.layers)

        else:
            self.restart.setPos((self.pause.x, self.pause.y))
            self.pause.setPos((self.layers.x, self.layers.y))

        self.add(self.fastForward)
        self.add(self.pause)
        self.add(self.slowDownMeter)

        # Only want to add the lives counter if there is a set amount of lives
        if lives is not None:
            self.add(self.lives)

        self.add(self.completed)
        self.add(self.completedAmount)

        if transition:
            # set the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                menu.game.spriteRenderer.runStartScreen()
                menu.remove(obj)

            self.slideTransitionY((0, 0), 'second', callback=callback)

    @overrides(GameHudLayout)
    def setLifeAmount(self):
        if hasattr(self, 'lives'):
            # Only if the animation is finished, show the game over screen
            def callback(obj, menu):
                if menu.game.spriteRenderer.getLives() <= 0:
                    # Run end screen game over :(
                    menu.game.spriteRenderer.runEndScreen()

            self.lives.addAnimation(
                tf.increaseTimer, 'onLoad', speed=-0.2, finish=(
                    self.spriteRenderer.getLives()
                    * self.lives.getStep()), direction="backwards",
                callback=callback)

    def setCompletedAmount(self):
        if hasattr(self, 'completed'):
            # Only if the animation has finished, show the game complete screen
            def callback(obj, menu):
                if (menu.game.spriteRenderer.getCompleted()
                        >= menu.game.spriteRenderer.getTotalToComplete()):
                    # Run end screen game complete!
                    menu.game.spriteRenderer.runEndScreen(True)

            self.completed.addAnimation(
                tf.increaseTimer, 'onLoad', speed=0.2, finish=(
                    self.spriteRenderer.getCompleted()
                    * self.completed.getStep()), callback=callback)
            self.completedAmount.setText(
                str(self.spriteRenderer.getCompleted()))

            width = (
                self.completedAmount.getFontSizeScaled()[0]
                / self.renderer.getScale())
            height = (
                self.completedAmount.getFontSizeScaled()[1]
                / self.renderer.getScale())
            self.completedAmount.setPos((
                (self.completed.x + (self.completed.width / 2)) - width / 2,
                ((self.completed.y + (self.completed.height / 2))
                    - height / 2) + 1))
            self.completedAmount.dirty = True


class EditorHud(GameHudLayout):
    def __init__(self, mapEditor):
        super().__init__(mapEditor.game)
        self.mapEditor = mapEditor

        self.textY = 12
        self.topBarHeight = 40  # Height of selection topbar
        self.boxWidth = 220  # Width of all the dropdowns
        self.padX = 15  # Padding x from box and text
        self.padY = 15  # Padding y between rows
        self.topPadY = 10  # Padding y for first row

        # Locations of each option
        self.fileLocation = 25
        self.editLocation = self.fileLocation + 75  # 90
        self.viewLocation = self.editLocation + 75
        self.addLocation = self.viewLocation + 75  # 90
        self.deleteLocation = self.addLocation + 65  # 170
        self.runLocation = self.deleteLocation + 100  # 280
        self.infoLocation = self.runLocation + 40

        # Selected map to edit
        self.selectedMap = None

    @overrides(GameHudLayout)
    def updateLayerText(self):
        if hasattr(self, 'currentLayer'):
            self.currentLayer.setText(
                self.mapEditor.getLayerName())
            self.currentLayer.dirty = True

    def closeDropdowns(self):
        # we always want to disable text inputs when we close the menus
        self.game.textHandler.setActive(False)
        self.close()
        self.main()

    def main(self, transition=False):
        self.open = True
        self.fileDropdownOpen = False
        self.editDropdownOpen = False
        self.viewDropdownOpen = False
        self.addDropdownOpen = False
        self.deleteDropdownOpen = False
        self.infoBoxOpen = False
        self.mapEditor.setAllowEdits(True)

        topbar = Rectangle(
            self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))

        # File operations
        fileSelect = Label(
            self, "File", 25, WHITE, (self.fileLocation, self.textY), BLACK)
        self.editLocation = fileSelect.getRightX() + self.padX
        # Edit the map type, size, color etc.
        edit = Label(
            self, "Edit", 25, WHITE, (self.editLocation, self.textY), BLACK)
        self.viewLocation = edit.getRightX() + self.padX
        # Toggle different layers and transport, nodes on and off
        view = Label(
            self, "View", 25, WHITE, (self.viewLocation, self.textY), BLACK)
        self.addLocation = view.getRightX() + self.padX
        # Add stuff to the map
        add = Label(
            self, "Add", 25, WHITE, (self.addLocation, self.textY), BLACK)
        self.deleteLocation = add.getRightX() + self.padX
        # Remove things from the map
        delete = Label(
            self, "Delete", 25, WHITE, (self.deleteLocation, self.textY),
            BLACK)
        self.runLocation = delete.getRightX() + self.padX
        # Run the map in no-fail mode
        run = Label(
            self, "Run", 25, WHITE, (self.runLocation, self.textY), BLACK)
        # Help button to tell players how to use the editor
        info = ControlKey(
            self, "?", 22, WHITE, (self.infoLocation, self.textY))

        self.currentLayer = Label(
            self, self.mapEditor.getLayerName(), 25, WHITE, (0, 0), BLACK)
        self.currentLayer.setPos((
            config["graphics"]["displayWidth"] - self.fileLocation
            - self.currentLayer.getFontSize()[0], self.textY))
        layers = Image(self, "layersWhite", (25, 25), (
            self.currentLayer.x - self.padX - 25, self.textY - 3))

        layers.addEvent(gf.hoverImage, 'onMouseOver', image="layersSelected")
        layers.addEvent(gf.hoverImage, 'onMouseOut', image="layersWhite")
        layers.addEvent(hf.changeEditorLayer, 'onMouseClick')

        self.add(topbar)
        self.add(layers)
        self.add(self.currentLayer)

        fileSelect.addEvent(hf.toggleFileDropdown, 'onMouseClick')
        edit.addEvent(hf.toggleEditDropdown, 'onMouseClick')
        view.addEvent(hf.toggleViewDropdown, 'onMouseClick')
        add.addEvent(hf.toggleAddDropdown, 'onMouseClick')
        delete.addEvent(hf.toggleDeleteDropdown, 'onMouseClick')
        run.addEvent(hf.runMap, 'onMouseClick')
        info.addEvent(hf.toggleInfoBox, 'onMouseClick')

        labels = [fileSelect, edit, view, add, delete, run, info]
        for label in labels:
            label.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            label.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label)

        if transition:
            # Show the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                menu.remove(obj)

            self.slideTransitionY((0, 0), 'second', callback=callback)

    def editDropdown(self):
        self.open = True
        self.editDropdownOpen = True
        self.editSizeDropdownOpen = False
        self.editBackgroundDropdownOpen = False
        self.totalToCompleteBoxOpen = False
        self.mapEditor.setAllowEdits(False)

        textX = self.editLocation + self.padX
        currentLayerName = self.mapEditor.getLayerName()

        # Change map Size
        size = Label(self, "Map Size", 25, WHITE, (
            textX, self.topBarHeight + self.topPadY), BLACK)
        # Change map background colour
        self.background = Label(
            self, f"Background \n colour \n ({currentLayerName})", 25,
            WHITE, (textX, size.getBottomY() + self.padY), BLACK)
        # Change total number of people needed to complete map
        total = Label(
            self, "Total to \n complete", 25, WHITE,
            (textX, self.background.getBottomY() + self.padY), BLACK)
        # Undo changes to map
        undo = Label(
            self, "Undo (Ctrl+Z)", 25,
            WHITE if len(self.mapEditor.getLevelChanges()) > 1 else GREY,
            (textX, total.getBottomY() + self.padY), BLACK)
        # Redo changes to map
        redo = Label(
            self, "Redo (Ctrl+Y)", 25,
            (WHITE if len(
                self.mapEditor.getPoppedLevelChanges()) >= 1 else GREY),
            (textX, undo.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK,
            (self.boxWidth, redo.getBottomY() + self.padY - self.topBarHeight),
            (self.editLocation, self.topBarHeight), 0, [0, 0, 10, 10])

        size.addEvent(hf.toggleEditSizeDropdown, 'onMouseClick')
        self.background.addEvent(
            hf.toggleEditBackgroundDropdown, 'onMouseClick')
        total.addEvent(hf.toggleTotalToCompleteBox, 'onMouseClick')

        if len(self.mapEditor.getLevelChanges()) > 1:
            undo.addEvent(hf.undoChange, 'onMouseClick')
            undo.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            undo.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)

        if len(self.mapEditor.getPoppedLevelChanges()) >= 1:
            redo.addEvent(hf.redoChange, 'onMouseClick')
            redo.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            redo.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)

        self.add(box)
        labels = [size, self.background, total]
        for label in labels:
            label.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            label.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label)

        self.add(undo)
        self.add(redo)

    def editSizeDropdown(self):
        self.open = True
        self.editSizeDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        currentWidth = self.mapEditor.getLevelData()["width"]
        currentHeight = self.mapEditor.getLevelData()["height"]

        size0Selected = (
            True if currentWidth == 16 and currentHeight == 9 else False)
        size1Selected = (
            True if currentWidth == 18 and currentHeight == 10 else False)
        size2Selected = (
            True if currentWidth == 20 and currentHeight == 11 else False)
        size3Selected = (
            True if currentWidth == 22 and currentHeight == 12 else False)

        boxX = self.editLocation + self.boxWidth
        textX = boxX + self.padX

        # 16 X 9 map size
        size0 = Label(
            self, ("- " if size0Selected else "") + "16 x 9", 25,
            GREEN if size0Selected else WHITE,
            (textX, self.topBarHeight + self.topPadY), BLACK)
        # 18 X 10 map size
        size1 = Label(
            self, ("- " if size1Selected else "") + "18 x 10", 25,
            GREEN if size1Selected else WHITE,
            (textX, size0.getBottomY() + self.padY), BLACK)
        # 20 X 11 map size
        size2 = Label(
            self, ("- " if size2Selected else "") + "20 x 11", 25,
            GREEN if size2Selected else WHITE,
            (textX, size1.getBottomY() + self.padY), BLACK)
        # 22 X 12 map size
        size3 = Label(
            self, ("- " if size3Selected else "") + "22 x 12", 25,
            GREEN if size3Selected else WHITE,
            (textX, size2.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                size3.getBottomY() + self.padY - self.topBarHeight),
            (boxX, self.topBarHeight), 0, [0, 10, 10, 10])

        size0.addEvent(hf.setSize0, 'onMouseClick')
        size1.addEvent(hf.setSize1, 'onMouseClick')
        size2.addEvent(hf.setSize2, 'onMouseClick')
        size3.addEvent(hf.setSize3, 'onMouseClick')

        self.add(box)
        labels = [
            (size0, size0Selected), (size1, size1Selected),
            (size2, size2Selected), (size3, size3Selected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def editBackgroundDrodown(self):
        self.open = True
        self.editBackgroundDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        boxX = self.editLocation + self.boxWidth
        textX = boxX + self.padX

        currentLayer = self.mapEditor.getCurrentLayer()
        levelData = self.mapEditor.getLevelData()

        currentBackground = DEFAULTBACKGROUND  # Default
        # Check the background data actually exists in the map
        if ("backgrounds" in levelData
                and "layer " + str(currentLayer) in levelData["backgrounds"]):
            currentBackground = self.mapEditor.getLevelData()["backgrounds"][
                "layer " + str(currentLayer)]

        y = self.background.y + self.padY
        backgrounds = []
        for colorName, colorData in BACKGROUNDCOLORS.items():
            color = colorData["color"]
            darkMode = colorData["darkMode"]

            current = (
                True if tuple(color) == tuple(currentBackground) else False)
            b = Label(
                self, ("- " if current else "") + colorName, 25,
                GREEN if current else WHITE, (textX, y), BLACK)

            if not current:
                b.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                b.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
                b.addEvent(
                    hf.setBackgroundColor, 'onMouseClick', layer=currentLayer,
                    color=color, darkMode=darkMode)

            backgrounds.append(b)
            y = b.getBottomY() + self.padY

        box = Rectangle(self, BLACK, (self.boxWidth, y - self.background.y), (
            boxX, self.background.y), 0, [0, 10, 10, 10])

        self.add(box)
        for background in backgrounds:
            self.add(background)

    def totalToCompleteBox(self):
        self.open = True
        self.totalToCompleteBoxOpen = True

        width = self.boxWidth * 2
        height = 240

        box, confirm, cancel = self.createConfirmBox(
            width, height, "Total to complete", padX=self.padX, padY=self.padY)

        padCenterX = 100
        totalText = Label(
            self, "Total:", 30, WHITE, (padCenterX, box.height / 2 - 15))
        inputBox = Rectangle(self, WHITE, (120, 50), (
            box.getRightX() - padCenterX - 120,
            box.getBottomY() - (height / 2) - 30))

        levelData = self.mapEditor.getLevelData()
        total = 8
        if "total" in levelData:
            total = levelData['total']

        self.total = Label(
            self, total, 30, BLACK,
            (inputBox.x + self.padX, inputBox.y + self.padY))

        upArrowBox = Rectangle(
            self, BLACK, (inputBox.width / 4, inputBox.height / 2),
            (inputBox.getRightX() - (inputBox.width / 4) - inputBox.x, 0))
        downArrowBox = Rectangle(
            self, BLACK, (inputBox.width / 4, inputBox.height / 2),
            (inputBox.getRightX() - (inputBox.width / 4) - inputBox.x,
                inputBox.height / 2))
        upArrow = Image(self, "arrowWhite", (25, 25), (
            upArrowBox.getRightX() - (upArrowBox.width / 2) - 12.5
            + inputBox.x, upArrowBox.y + inputBox.y))
        downArrow = Image(self, "arrowWhite", (25, 25), (
            downArrowBox.getRightX() - (downArrowBox.width / 2) - 12.5
            + inputBox.x, downArrowBox.y + inputBox.y))
        upArrow.rotateImage(90)
        downArrow.rotateImage(270)

        upArrow.addEvent(gf.hoverImage, 'onMouseOver', image="arrowGreen")
        upArrow.addEvent(gf.hoverImage, 'onMouseOut', image="arrowWhite")
        upArrow.addEvent(hf.incrementTotalToComplete, 'onMouseClick')

        downArrow.addEvent(gf.hoverImage, 'onMouseOver', image="arrowGreen")
        downArrow.addEvent(gf.hoverImage, 'onMouseOut', image="arrowWhite")
        downArrow.addEvent(hf.decrementTotalToComplete, 'onMouseClick')

        confirm.addEvent(hf.setTotalToComplete, 'onMouseClick')
        cancel.addEvent(hf.toggleTotalToCompleteBox, 'onMouseClick')

        box.add(totalText)
        inputBox.add(upArrowBox)
        inputBox.add(downArrowBox)
        self.add(box)
        self.add(inputBox)
        self.add(self.total)
        self.add(upArrow)
        self.add(downArrow)
        self.add(confirm)
        self.add(cancel)

    def viewDropdown(self):
        self.open = True
        self.viewDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        currentLayer = self.mapEditor.getCurrentLayer()
        transportSelected = self.mapEditor.getShowTransport()
        layer1Selected = True if currentLayer == 1 else False
        layer2Selected = True if currentLayer == 2 else False
        layer3Selected = True if currentLayer == 3 else False
        layer4Selected = True if currentLayer == 4 else False

        textX = self.viewLocation + self.padX

        # Toggle show the transport on or off
        transport = Label(
            self, ("- " if transportSelected else "") + "Transport", 25,
            GREEN if transportSelected else WHITE,
            (textX, self.topBarHeight + self.topPadY), BLACK)
        # Show layer 1
        layer1 = Label(self, (
            ("- " if layer1Selected else "")
            + self.mapEditor.getLayerName(1)), 25,
            GREEN if layer1Selected else WHITE,
            (textX, transport.getBottomY() + self.padY), BLACK)
        # Show layer 2
        layer2 = Label(self, (
            ("- " if layer2Selected else "") + self.mapEditor.getLayerName(2)),
            25, GREEN if layer2Selected else WHITE,
            (textX, layer1.getBottomY() + self.padY), BLACK)
        # Show layer 3
        layer3 = Label(self, (
            ("- " if layer3Selected else "") + self.mapEditor.getLayerName(3)),
            25, GREEN if layer3Selected else WHITE,
            (textX, layer2.getBottomY() + self.padY), BLACK)
        # Show layer 4
        layer4 = Label(self, (
            ("- " if layer4Selected else "") + self.mapEditor.getLayerName(4)),
            25, GREEN if layer4Selected else WHITE,
            (textX, layer3.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                layer4.getBottomY() + self.padY - self.topBarHeight),
            (self.viewLocation, self.topBarHeight), 0, [0, 0, 10, 10])

        transport.addEvent(hf.toggleTransport, 'onMouseClick')
        layer1.addEvent(hf.changeEditorLayer, 'onMouseClick', current=1)
        layer2.addEvent(hf.changeEditorLayer, 'onMouseClick', current=2)
        layer3.addEvent(hf.changeEditorLayer, 'onMouseClick', current=3)
        layer4.addEvent(hf.changeEditorLayer, 'onMouseClick', current=4)

        self.add(box)
        labels = [
            (transport, transportSelected), (layer1, layer1Selected),
            (layer2, layer2Selected), (layer3, layer3Selected),
            (layer4, layer4Selected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def addDropdown(self):
        self.open = True
        self.addDropdownOpen = True
        self.addStopDropdownOpen = False
        self.addTransportDropdownOpen = False
        self.addDestinationDropdownOpen = False
        self.addSpecialsDropdownOpen = False
        self.mapEditor.setAllowEdits(False)

        clickType = self.mapEditor.getClickManager().getClickType()
        connectionSelected = (
            True if clickType == EditorClickManager.ClickType.CONNECTION
            else False)
        stopSelected = (
            True if clickType == EditorClickManager.ClickType.STOP else False)
        transportSelected = (
            True if clickType == EditorClickManager.ClickType.TRANSPORT
            else False)
        destinationSelected = (
            True if clickType == EditorClickManager.ClickType.DESTINATION
            else False)
        specialsSelected = (
            True if clickType == EditorClickManager.ClickType.SPECIAL
            else False)

        textX = self.addLocation + self.padX

        # Add a connection to the map
        connection = Label(
            self, ("- " if connectionSelected else "") + "Connection", 25,
            GREEN if connectionSelected else WHITE,
            (textX, self.topBarHeight + self.topPadY), BLACK)
        # Add a type of stop to the map
        self.stop = Label(
            self, ("- " if stopSelected else "") + "Stop", 25,
            GREEN if stopSelected else WHITE,
            (textX, connection.getBottomY() + self.padY), BLACK)
        # Add a type of transport to the map
        self.transport = Label(
            self, ("- " if transportSelected else "") + "Transport", 25,
            GREEN if transportSelected else WHITE,
            (textX, self.stop.getBottomY() + self.padY), BLACK)
        # Add a type of destination to the map
        self.destination = Label(
            self, ("- " if destinationSelected else "") + "Location", 25,
            GREEN if destinationSelected else WHITE,
            (textX, self.transport.getBottomY() + self.padY), BLACK)
        # Add a type of special node to the map (nowalknodes etc.)
        self.specials = Label(
            self, ("- " if specialsSelected else "") + "Specials", 25,
            GREEN if specialsSelected else WHITE,
            (textX, self.destination.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                self.specials.getBottomY() + self.padY - self.topBarHeight),
            (self.addLocation, self.topBarHeight), 0, [0, 0, 10, 10])

        connection.addEvent(hf.addConnection, 'onMouseClick')
        self.stop.addEvent(hf.toggleAddStopDropdown, 'onMouseClick')
        self.transport.addEvent(hf.toggleAddTransportDropdown, 'onMouseClick')
        self.destination.addEvent(
            hf.toggleAddDestinationDropdown, 'onMouseClick')
        self.specials.addEvent(hf.toggleAddSpecialsDropdown, 'onMouseClick')

        self.add(box)
        labels = [
            (connection, connectionSelected), (self.stop, stopSelected),
            (self.transport, transportSelected),
            (self.destination, destinationSelected),
            (self.specials, specialsSelected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def addStopDropdown(self):
        self.open = True
        self.addStopDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        addType = self.mapEditor.getClickManager().getAddType()
        metroSelected = True if addType == "metro" else False
        busSelected = True if addType == "bus" else False
        tramSelected = True if addType == "tram" else False

        boxX = self.addLocation + self.boxWidth
        textX = boxX + self.padX

        # Add a metro station to the map
        metroStation = Label(
            self, ("- " if metroSelected else "") + "Metro \n Station", 25,
            GREEN if metroSelected else WHITE,
            (textX, self.stop.y + self.padY), BLACK)
        # Add a bus stop to the map
        busStop = Label(
            self, ("- " if busSelected else "") + "Bus Stop", 25,
            GREEN if busSelected else WHITE,
            (textX, metroStation.getBottomY() + self.padY), BLACK)
        # Add a tram stop to the map
        tramStop = Label(
            self, ("- " if tramSelected else "") + "Tram Stop", 25,
            GREEN if tramSelected else WHITE,
            (textX, busStop.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                tramStop.getBottomY() + self.padY - self.stop.y),
            (boxX, self.stop.y), 0, [0, 10, 10, 10])

        metroStation.addEvent(hf.addType, 'onMouseClick',
                              addType="metro", layer=1)
        busStop.addEvent(hf.addType, 'onMouseClick', addType="bus", layer=2)
        tramStop.addEvent(hf.addType, 'onMouseClick', addType="tram", layer=3)

        self.add(box)
        labels = [
            (metroStation, metroSelected), (busStop, busSelected),
            (tramStop, tramSelected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def addTransportDropdown(self):
        self.open = True
        self.addTransportDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        addType = self.mapEditor.getClickManager().getAddType()
        metroSelected = True if addType == "metro" else False
        busSelected = True if addType == "bus" else False
        tramSelected = True if addType == "tram" else False
        taxiSelected = True if addType == "taxi" else False

        boxX = self.addLocation + self.boxWidth
        textX = boxX + self.padX

        # Add a metro to the map
        metro = Label(
            self, ("- " if metroSelected else "") + "Metro", 25,
            GREEN if metroSelected else WHITE,
            (textX, self.transport.y + self.padY), BLACK)
        # Add a bus to the map
        bus = Label(
            self, ("- " if busSelected else "") + "Bus", 25,
            GREEN if busSelected else WHITE,
            (textX, metro.getBottomY() + self.padY), BLACK)
        # Add a tram to the map
        tram = Label(
            self, ("- " if tramSelected else "") + "Tram", 25,
            GREEN if tramSelected else WHITE,
            (textX, bus.getBottomY() + self.padY), BLACK)
        # Add a taxi to the map
        taxi = Label(
            self, ("- " if taxiSelected else "") + "Taxi", 25,
            GREEN if taxiSelected else WHITE,
            (textX, tram.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                taxi.getBottomY() + self.padY - self.transport.y),
            (boxX, self.transport.y), 0, [0, 10, 10, 10])

        metro.addEvent(hf.addType, 'onMouseClick', addType="metro", layer=1)
        bus.addEvent(hf.addType, 'onMouseClick', addType="bus", layer=2)
        taxi.addEvent(hf.addType, 'onMouseClick', addType="taxi", layer=2)
        tram.addEvent(hf.addType, 'onMouseClick', addType="tram", layer=3)

        self.add(box)
        labels = [
            (metro, metroSelected), (bus, busSelected), (tram, tramSelected),
            (taxi, taxiSelected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def addDestinationDropdown(self):
        self.open = True
        self.addDestinationDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        addType = self.mapEditor.getClickManager().getAddType()
        airportSelected = True if addType == 'airport' else False
        officeSelected = True if addType == 'office' else False
        houseSelected = True if addType == 'house' else False
        schoolSelected = True if addType == 'school' else False
        shopSelected = True if addType == 'shop' else False

        boxX = self.addLocation + self.boxWidth
        textX = boxX + self.padX

        # Add an airport location to the map
        airport = Label(
            self, ("- " if airportSelected else "") + "Airport", 25,
            GREEN if airportSelected else WHITE,
            (textX, self.destination.y + self.padY), BLACK)
        # Add an office location to the map
        office = Label(
            self, ("- " if officeSelected else "") + "Office", 25,
            GREEN if officeSelected else WHITE,
            (textX, airport.getBottomY() + self.padY), BLACK)
        # Add a house location to the map
        house = Label(
            self, ("- " if houseSelected else "") + "House", 25,
            GREEN if houseSelected else WHITE,
            (textX, office.getBottomY() + self.padY), BLACK)
        # Add a school location to the map
        school = Label(
            self, ("- " if schoolSelected else "") + "School", 25,
            GREEN if schoolSelected else WHITE,
            (textX, house.getBottomY() + self.padY), BLACK)
        # Add a shop location to the map
        shop = Label(
            self, ("- " if shopSelected else "") + "Shop", 25,
            GREEN if shopSelected else WHITE,
            (textX, school.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                shop.getBottomY() + self.padY - self.destination.y),
            (boxX, self.destination.y), 0, [0, 10, 10, 10])

        airport.addEvent(hf.addType, 'onMouseClick', addType='airport')
        office.addEvent(hf.addType, 'onMouseClick', addType='office')
        house.addEvent(hf.addType, 'onMouseClick', addType='house')
        school.addEvent(hf.addType, 'onMouseClick', addType='school')
        shop.addEvent(hf.addType, 'onMouseClick', addType='shop')

        self.add(box)
        labels = [
            (airport, airportSelected), (office, officeSelected),
            (house, houseSelected), (school, schoolSelected),
            (shop, shopSelected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def addSpecialsDropdown(self):
        self.open = True
        self.addSpecialsDropdownOpen = True

        addType = self.mapEditor.getClickManager().getAddType()
        noWalkNodeSelected = True if addType == 'noWalkNode' else False

        boxX = self.addLocation + self.boxWidth
        textX = boxX + self.padX

        noWalkNode = Label(
            self, ("- " if noWalkNodeSelected else "") + "No walking \n node",
            25, GREEN if noWalkNodeSelected else WHITE,
            (textX, self.specials.y + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                noWalkNode.getBottomY() + self.padY - self.specials.y),
            (boxX, self.specials.y), 0, [0, 10, 10, 10])

        noWalkNode.addEvent(hf.addType, 'onMouseClick',
                            addType="noWalkNode", layer=2)

        self.add(box)
        labels = [(noWalkNode, noWalkNodeSelected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])
        self.add(noWalkNode)

    def deleteDropdown(self):
        self.open = True
        self.deleteDropdownOpen = True
        self.mapEditor.setAllowEdits(False)

        clickType = self.mapEditor.getClickManager().getClickType()
        connectionSelected = (
            True if clickType == EditorClickManager.ClickType.DCONNECTION
            else False)
        transportSelected = (
            True if clickType == EditorClickManager.ClickType.DTRANSPORT
            else False)
        nodeSelected = (
            True if clickType == EditorClickManager.ClickType.DNODE
            else False)

        textX = self.deleteLocation + self.padX

        # Delete a connection from the map
        connection = Label(
            self, ("- " if connectionSelected else "") + "Connection", 25,
            GREEN if connectionSelected else WHITE,
            (textX, self.topBarHeight + self.topPadY), BLACK)
        # Delete a type of transport from the map
        transport = Label(
            self, ("- " if transportSelected else "") + "Transport", 25,
            GREEN if transportSelected else WHITE,
            (textX, connection.getBottomY() + self.padY), BLACK)
        # Delete a type of node from the map
        # stops, destination, specials etc.)
        node = Label(
            self, ("- " if nodeSelected else "") + "Node", 25,
            GREEN if nodeSelected else WHITE,
            (textX, transport.getBottomY() + self.padY), BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                node.getBottomY() + self.padY - self.topBarHeight),
            (self.deleteLocation, self.topBarHeight), 0, [0, 0, 10, 10])

        connection.addEvent(hf.deleteConnection, 'onMouseClick')
        transport.addEvent(hf.deleteTransport, 'onMouseClick')
        node.addEvent(hf.deleteNode, 'onMouseClick')

        self.add(box)
        labels = [
            (connection, connectionSelected), (transport, transportSelected),
            (node, nodeSelected)]
        for label in labels:
            if not label[1]:
                label[0].addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                label[0].addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label[0])

    def fileDropdown(self):
        self.open = True
        self.fileDropdownOpen = True
        self.saveBoxOpen = False
        self.loadBoxOpen = False
        self.confirmBoxOpen = False
        self.confirmExitBoxOpen = False
        self.mapEditor.setAllowEdits(False)

        textX = self.fileLocation + self.padX

        # Create a new map / reset
        new = Label(
            self, "New (Reset)", 25, WHITE,
            (textX, self.topBarHeight + self.topPadY), BLACK)
        # Load an existing map
        self.load = Label(
            self, "Open", 25, WHITE, (textX, new.getBottomY() + self.padY),
            BLACK)
        # Save a map with the new changes
        save = Label(
            self, "Save", 25,
            (WHITE if self.mapEditor.getDeletable() else GREY),
            (textX, self.load.getBottomY() + self.padY), BLACK)
        # Save a new map for the first time
        saveAs = Label(
            self, "Save as", 25,
            (WHITE if self.mapEditor.getDeletable() else GREY),
            (textX, save.getBottomY() + self.padY), BLACK)
        # Delete an existing map - Must be already saved and be a deletable map
        delete = Label(
            self, "Delete", 25, (
                WHITE if self.mapEditor.getSaved()
                and self.mapEditor.getDeletable() else GREY),
            (textX, saveAs.getBottomY() + self.padY), BLACK)
        # Close the Map Editor
        close = Label(
            self, "Exit", 25, WHITE, (textX, delete.getBottomY() + self.padY),
            BLACK)
        box = Rectangle(
            self, BLACK, (
                self.boxWidth,
                close.getBottomY() + self.padY - self.topBarHeight),
            (self.fileLocation, self.topBarHeight), 0, [0, 0, 10, 10])

        new.addEvent(hf.toggleConfirmNewMap, 'onMouseClick')
        self.load.addEvent(hf.toggleLoadDropdown, 'onMouseClick')
        close.addEvent(hf.toggleConfirmExitBox, 'onMouseClick')

        if self.mapEditor.getDeletable():
            save.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            save.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            save.addEvent(hf.toggleSaveBox, 'onMouseClick')
            saveAs.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            saveAs.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            saveAs.addEvent(hf.toggleSaveAsBox, 'onMouseClick')

            if self.mapEditor.getSaved():
                delete.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
                delete.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
                delete.addEvent(hf.toggleConfirmBox, 'onMouseClick')

        self.add(box)
        self.add(save)
        self.add(saveAs)
        self.add(delete)

        # Add each of the labels
        labels = [new, self.load, close]
        for label in labels:
            label.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            label.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            self.add(label)

    def loadDropdown(self):
        self.open = True
        self.loadBoxOpen = True
        self.mapEditor.setAllowEdits(False)

        boxX = self.fileLocation + self.boxWidth
        textX = boxX + self.padX

        y = self.load.y + self.padY
        maxWidth = self.boxWidth
        maps = []
        for mapName, path in self.game.mapLoader.getMaps().items():
            m = Label(self, mapName, 25, WHITE, (textX, y), BLACK)
            m.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
            m.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
            m.addEvent(hf.toggleConfirmLoadEditorMap, 'onMouseClick')

            if m.getFontSize()[0] + (self.padX * 2) > maxWidth:
                maxWidth = m.getFontSize()[0] + (self.padX * 2)
            maps.append(m)
            y = m.getBottomY() + self.padY

        box = Rectangle(
            self, BLACK, (maxWidth, y - self.load.y), (boxX, self.load.y), 0,
            [0, 10, 10, 10])

        self.add(box)
        for m in maps:
            self.add(m)

    def saveBox(self):
        self.open = True
        self.saveBoxOpen = True
        self.game.audioLoader.playSound("uiUnavailable", 1)

        width = config["graphics"]["displayWidth"] / 2
        height = 240

        box, save, cancel = self.createConfirmBox(
            width, height, "Map Name", ok="Save", padX=self.padX,
            padY=self.padY)

        self.inputBox = Rectangle(self, WHITE, (width - (self.padX * 2), 50), (
            box.x + self.padX, box.getBottomY() - (height / 2) - 30))
        mapName = InputBox(
            self, 30, BLACK, self.inputBox,
            self.inputBox.width - (self.padX * 2),
            (self.inputBox.x + self.padX, self.inputBox.y + self.padY))

        self.inputBox.addEvent(gf.hoverColor, 'onKeyPress', color=WHITE)
        save.addEvent(hf.saveMap, 'onMouseClick')
        cancel.addEvent(hf.toggleSaveBox, 'onMouseClick')

        self.add(box)
        self.add(self.inputBox)
        self.add(mapName)
        self.add(save)
        self.add(cancel)

    def confirmBox(self):
        self.open = True
        self.confirmBoxOpen = True
        self.game.audioLoader.playSound("uiUnavailable", 1)

        width = config["graphics"]["displayWidth"] / 2
        height = 240

        box, confirm, cancel = self.createConfirmBox(
            width, height, "Delete?", ok="Yes", padX=self.padX, padY=self.padY)

        confirmText = Label(
            self, "Are you sure you want to \n delete this map?", 30, WHITE,
            (40, 82), GREEN)

        confirm.addEvent(hf.deleteMap, 'onMouseClick')
        cancel.addEvent(hf.toggleConfirmBox, 'onMouseClick')

        box.add(confirmText)
        self.add(box)
        self.add(confirm)
        self.add(cancel)

    def confirmExitBox(self, confirmCallBack):
        self.open = True
        self.confirmExitBoxOpen = True
        self.game.audioLoader.playSound("uiUnavailable", 1)

        width = config["graphics"]["displayWidth"] / 2
        height = 240

        box, confirm, cancel = self.createConfirmBox(
            width, height, "Unsaved changes?", ok="Yes", cancel="No",
            padX=self.padX, padY=self.padY)

        confirmText = Label(
            self, "Are you sure you want to \n exit without saving? \n \
                (Any unsaved changes will \n be lost)", 30, WHITE, (40, 70),
            GREEN)

        confirm.addEvent(confirmCallBack, 'onMouseClick')
        cancel.addEvent(hf.toggleConfirmExitBox, 'onMouseClick')

        box.add(confirmText)
        self.add(box)
        self.add(confirm)
        self.add(cancel)

    def infoBox(self):
        self.open = True
        self.infoBoxOpen = True
        self.mapEditor.setAllowEdits(False)
        self.game.audioLoader.playSound("uiUnavailable", 1)

        width = config["graphics"]["displayWidth"] - (
            config["graphics"]["displayWidth"] / 3)
        height = config["graphics"]["displayHeight"] / 1.3

        box, confirm, cancel = self.createConfirmBox(
            width, height, "Help", cancel="", padX=self.padX, padY=self.padY)

        # Tell players how to change layers.
        layer = Label(
            self, "Press    to change layer", 30, WHITE, (40, 70), GREEN)
        layers = Image(self, "layersWhite", (30, 30), (140, 60))

        # Tell players how to create a connection.
        addConnection = Label(
            self, "Press    on the start and end node \n\
            to create a connection", 30, WHITE,
            (40, layer.getBottomY() + (self.padY * 2)), GREEN)
        leftClick = Image(
            self, "leftClickWhite", (45, 45),
            (130, layer.getBottomY() + (self.padY * 2) - 25))

        # Tell players how to preview all layers.
        preview = Label(self, "Press    to preview all layers", 30, WHITE, (
            40, addConnection.getBottomY() + (self.padY * 2), GREEN))
        rightClick = Image(self,  "rightClickWhite", (45, 45), (
            130, addConnection.getBottomY() + (self.padY * 2) - 25))

        # Tell users how to view the checklist.
        checklist = Label(
            self, "Press    to view the level checklist", 30, WHITE,
            (40, preview.getBottomY() + (self.padY * 2)), GREEN)
        checklistButton = ControlKey(self, "c", 30, WHITE, (
            140, preview.getBottomY() + (self.padY * 2)))

        # Tell users how to test the map
        test = Label(
            self, "Press 'Run' to test the level in \nno-death mode",
            30, WHITE, (40, checklist.getBottomY() + (self.padY * 2)), GREEN)

        confirm = Label(self, "Ok", 25, WHITE, (0, 0), BLACK)
        cw = confirm.getFontSize()[0] + (self.padX * 2)
        ch = confirm.getFontSize()[1] + (self.padY * 2)
        confirmBox = Rectangle(self, BLACK, (cw, ch), (
            box.getRightX() - self.padX - cw - box.x,
            box.getBottomY() - self.padY - ch - box.y))
        confirm.setPos((
            confirmBox.x + self.padX + box.x,
            confirmBox.y + self.padY + box.y))

        confirm.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
        confirm.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
        confirm.addEvent(hf.toggleInfoBox, 'onMouseClick')

        box.add(addConnection)
        box.add(leftClick)
        box.add(layer)
        box.add(layers)
        box.add(preview)
        box.add(rightClick)
        box.add(checklist)
        box.add(checklistButton)
        box.add(test)
        box.add(confirmBox)
        self.add(box)
        self.add(confirm)


class PreviewHud(GameHudLayout):
    def __init__(self, spriteRenderer, spacing):
        super().__init__(spriteRenderer.game)
        self.spriteRenderer = spriteRenderer
        self.spacing = spacing

    @overrides(GameHudLayout)
    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeter'):
            self.slowDownMeter.setAmount((amount, 20))
            self.slowDownMeter.dirty = True

    def main(self, transition=False):
        self.open = True

        meterWidth = self.spriteRenderer.getSlowDownMeterAmount()

        topbar = Rectangle(
            self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        stop = Label(self, "Stop", 25, WHITE, (20, 10), BLACK)
        self.slowDownMeter = Meter(
            self, WHITE, WHITE, GREEN, (meterWidth, 20), (meterWidth, 20),
            (config["graphics"]["displayWidth"] - (100 + meterWidth), 12), 2)
        completed = Image(
            self, "walkingWhite", (30, 30),
            (config["graphics"]["displayWidth"] - 68, 7))
        self.completedText = Label(
            self, str(self.spriteRenderer.getCompleted()), 25, WHITE,
            (config["graphics"]["displayWidth"] - 40, 14), BLACK)

        stop.addEvent(gf.hoverColor, 'onMouseOver', color=GREEN)
        stop.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
        stop.addEvent(hf.stopMap, 'onMouseClick')

        self.add(topbar)
        self.add(stop)
        self.add(self.slowDownMeter)
        self.add(completed)
        self.add(self.completedText)

    def setCompletedAmount(self):
        if hasattr(self, 'completedText'):
            self.completedText.setText(
                str(self.spriteRenderer.getCompleted()))
            self.completedText.dirty = True


class MessageHud(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.messages = []

    def removeMessage(self, message):
        self.messages.remove(message)

    def addMessage(self, message):
        if message in self.messages:
            return

        messageBox = MessageBox(self, message, (25, 25))
        messageBox.addAnimation(
            tf.transitionMessageDown, 'onLoad', speed=4,
            transitionDirection="down", y=messageBox.marginY)
        self.add(messageBox)
        messageBox.addMessages()
        self.messages.append(message)

        messageBoxes = sum(
            isinstance(component, MessageBox) for component in self.components)
        if messageBoxes > 0:
            for component in self.components:
                if isinstance(component, MessageBox):
                    if (tf.transitionMessageDown
                            not in component.getAnimations()):
                        component.addAnimation(
                            tf.transitionMessageDown, 'onLoad', speed=4,
                            transitionDirection="down",
                            y=((component.y + messageBox.height)
                                + component.marginY))

    def main(self):
        self.open = True
