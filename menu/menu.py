from tkinter.tix import MAIN
import pygame
from config import (
    config, BLACK, TRUEBLACK, WHITE, GREEN, CREAM, YELLOW, dump)
import generalFunctions as gf
import menuFunctions as mf
import transitionFunctions as tf
from menuComponents import (
    Image, Label, InputBox, Rectangle, DifficultyMeter, Map, Slider,
    ControlLabel, Region)
from clickManager import ControlClickManager
from utils import vec, overrides
from enum import Enum, auto
import random
import copy


class Menu:
    def __init__(self, game):
        pygame.font.init()

        self.open = False
        self.game = game
        self.renderer = game.renderer
        self.components = []  # Components to render to the screen
        self.backgroundColor = WHITE

        self.clicked = False

        # TODO: Do we want these to be associative attributes???!?
        self.loadingImage = Image(
            self, "loading1", (100, 72), (
                (config["graphics"]["displayWidth"] / 2) - 50,
                (config["graphics"]["displayHeight"] / 2) - 36))
        self.loadingText = Label(
            self, "Loading", 30, WHITE, (
                config["graphics"]["displayWidth"] / 2 - 58,
                config["graphics"]["displayHeight"] / 2 + 45))

    def getOpen(self):
        return self.open

    def getComponents(self):
        return self.components

    def getBackgroundColor(self):
        return self.backgroundColor

    def setOpen(self, hudOpen):
        self.open = hudOpen

    # Add a single, or multiple items to the menu interface.
    def add(self, components):
        if type(components) == list:
            for component in components:
                self.components.append(component)

        else:
            self.components.append(components)

    def remove(self, obj):
        if obj in self.components:
            self.components.remove(obj)
            del obj

    def clickButton(self):
        click = random.randint(1, 2)
        self.game.audioLoader.playSound("click%i" % click)

    def resize(self):
        for component in self.components:
            component.resize()  # force redraw

            if isinstance(component, InputBox):
                component.resizeIndicator()

    def update(self):
        for component in self.components:
            component.update()

    def display(self):
        # We use list so we can delete from the array whilst looping through
        # it (without causing flicking with double blits)
        # We use the reversed list so that the items added first (bottom)
        # are the last in the event loop
        allComponents = zip(
            list(self.components), reversed(list(self.components)))
        for component, tangibleComponent in allComponents:
            component.draw()

            # only if the menu is open do we want to allow for interactions
            if self.open:
                self.events(tangibleComponent)
                self.animate(tangibleComponent)

    def animate(self, component):
        if hasattr(component, 'rect'):
            if len(component.animations) > 0:
                for function, animation in list(component.animations.items()):
                    if animation[0] == 'onMouseOver':
                        function(component, self, function, **animation[1])

                    if animation[0] == 'onMouseOut':
                        function(component, self, function, **animation[1])

                    if animation[0] == 'onLoad':
                        function(component, self, function, **animation[1])

    def events(self, component):
        mx, my = pygame.mouse.get_pos()
        difference = self.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        # Check the component has been drawn (if called before next tick)
        if not hasattr(component, 'rect') or len(component.events) <= 0:
            return

        for e in list(component.events):
            if e['event'] == 'onMouseClick':
                if (component.rect.collidepoint((mx, my))
                        and self.game.clickManager.getClicked()):
                    self.clickButton()
                    self.game.clickManager.setClicked(False)
                    e['function'](component, self, e, **e['kwargs'])

            elif e['event'] == 'onMouseLongClick':
                if (component.rect.collidepoint((mx, my))
                        and pygame.mouse.get_pressed()[0]
                        and not self.game.clickManager.getLongClicked()):
                    self.clickButton()
                    self.game.clickManager.setLongClicked(True)
                    # Not clicking, but longclicking
                    self.game.clickManager.setClicked(False)
                    component.clicked = True
                    e['function'](component, self, e, **e['kwargs'])

            elif e['event'] == 'onMouseLongClickOut':
                if (component.rect.collidepoint((mx, my))
                        and not pygame.mouse.get_pressed()[0]
                        and self.game.clickManager.getLongClicked()):
                    self.game.clickManager.setLongClicked(False)
                    component.clicked = False
                    e['function'](component, self, e, **e['kwargs'])

            elif e['event'] == 'onMouseOver':
                if (component.rect.collidepoint((mx, my))
                        and not component.mouseOver):
                    component.mouseOver = True
                    e['function'](component, self, e, **e['kwargs'])
                    component.dirty = True

            elif e['event'] == 'onMouseOut':
                if (not component.rect.collidepoint((mx, my))
                        and component.mouseOver):
                    component.mouseOver = False
                    e['function'](component, self, e, **e['kwargs'])
                    component.dirty = True

            elif e['event'] == 'onKeyPress':
                if self.game.textHandler.getPressed():
                    e['function'](component, self, e, **e['kwargs'])
                    # Reset the key since we only want the function to
                    # be called once
                    self.game.textHandler.setCurrentKey(None)
                    component.dirty = True

    def setClicked(self, clicked):
        if self.open:
            self.clicked = clicked

    def close(self):
        for component in self.components:
            del component
        self.components = []
        self.open = False

    # Create a black rectangle at screen size and animate it in the Y axis
    def slideTransitionY(
            self, pos, half, speed=-40, callback=None, direction='up'):
        transition = Rectangle(
            self, TRUEBLACK, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), pos)
        transition.addAnimation(
            tf.slideTransitionY, 'onLoad', speed=speed, half=half,
            callback=callback, transitionDirection=direction)
        self.add(transition)

    # Create a black rectangle at screen size and animate it in the X axis
    def slideTransitionX(self, pos, half, speed=-70, callback=None):
        transition = Rectangle(
            self, TRUEBLACK, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), pos)
        transition.addAnimation(
            tf.slideTransitionX, 'onLoad', speed=speed, half=half,
            callback=callback)
        self.add(transition)

    # Create a loading screen for inbetween the slide transition animations
    def loadingScreen(self):
        # Reset the loading image and text back to the defaults
        self.loadingImage.setImageName("loading1")
        self.loadingText.setText("Loading")

        # Update the components
        self.loadingImage.dirty = True
        self.loadingText.dirty = True

        self.add(self.loadingImage)
        self.add(self.loadingText)

    # Update the loading screen to show progress
    def updateLoadingScreen(self):
        if self.loadingImage.getImageName() == "loading1":
            self.loadingImage.setImageName("loading2")

        else:
            self.loadingImage.setImageName("loading1")

        if len(self.loadingText.getText()) >= 10:
            self.loadingText.setText("Loading")
        else:
            self.loadingText.setText(self.loadingText.getText() + ".")

        # Update the components.
        self.loadingImage.dirty = True
        self.loadingText.dirty = True

    # Slide up all the components on the screen to display height
    def closeTransition(self, callback=gf.defaultCloseCallback):
        self.spriteRenderer.getHud().setOpen(True)
        self.mapEditor.getHud().setOpen(True)

        for component in self.components:
            if tf.transitionY not in component.getAnimations():
                dirty = True if isinstance(component, Slider) else False

                component.addAnimation(
                    tf.transitionY, 'onLoad', speed=-40,
                    transitionDirection="up",
                    y=-config["graphics"]["displayHeight"], callback=callback,
                    dirty=dirty)

        self.game.audioLoader.playSound("swoopOut")

    # Slide down all the components on the screen from display height
    def openTransition(self, callback=gf.defaultSlideYCallback):
        for component in self.components:
            y = component.y
            component.setPos((
                component.x,
                component.y - config["graphics"]["displayHeight"]))
            component.addAnimation(
                tf.transitionY, 'onLoad', speed=40,
                transitionDirection='down', y=y, callback=callback)

        self.game.audioLoader.playSound("swoopIn")


class MainMenu(Menu):
    class LevelSelect(Enum):
        LEVELSELECT = auto()
        CUSTOMLEVELSELECT = auto()
        REGIONSELECT = auto()

    def __init__(self, game):
        super().__init__(game)

        self.currentRegion = vec(
            config["player"]["currentRegion"][0],
            config["player"]["currentRegion"][1])
        self.currentLevel = vec(0, 0)
        self.currentCustomLevel = vec(
            config["player"]["currentCustomLevel"][0],
            config["player"]["currentCustomLevel"][1])
        self.currentLevelSelect = MainMenu.LevelSelect.REGIONSELECT
        self.regions = list(self.game.regionLoader.getRegions().keys())
        self.builtInMaps = list(self.game.mapLoader.getBuiltInMaps().keys())
        self.splashScreenMaps = list(
            self.game.mapLoader.getSplashScreenMaps().keys())
        self.customMaps = list(self.game.mapLoader.getCustomMaps().keys())
        self.currentMaps = self.builtInMaps
        self.levels = {}
        self.backgroundColor = GREEN

        self.builtInLevelSize = 3.5
        self.customLevelSize = 2.2

        self.setLevelSize(self.builtInLevelSize)
        self.spacing = 30

        self.transitioning = False

        # Default to level selection screens being closed
        self.levelSelectOpen = False
        self.customLevelSelectOpen = False

    @overrides(Menu)
    def getOpen(self):
        if self.open or self.game.optionMenu.optionsOpen:
            return True
        return False

    def getLevels(self):
        return self.levels

    def getCurrentLevel(self):
        if self.regionSelectOpen:
            return self.currentRegion
        elif self.levelSelectOpen:
            return self.currentLevel
        elif self.customLevelSelectOpen:
            return self.currentCustomLevel
        return vec(0, 0)  # Default

    def getCurrentLevelSelect(self):
        return self.currentLevelSelect

    def getTransitioning(self):
        return self.transitioning

    # If either of the level selection screens are open
    def getLevelSelectOpen(self):
        if (self.levelSelectOpen or self.customLevelSelectOpen
                or self.regionSelectOpen):
            return True
        return False

    def setTransitioning(self, transitioning):
        self.transitioning = transitioning

    def setLevelSize(self, scaler=5):  # larger scaler = larger image
        self.levelWidth = config["graphics"]["displayWidth"] - (
            config["graphics"]["displayWidth"] / scaler)
        self.levelHeight = config["graphics"]["displayHeight"] - (
            config["graphics"]["displayHeight"] / scaler)

    def updateCustomMaps(self):
        self.customMaps = list(self.game.mapLoader.getCustomMaps().keys())
        currentIndex = ((
            self.currentCustomLevel.y * self.getLevelSelectCols())
            + self.currentCustomLevel.x)

        if currentIndex >= len(self.customMaps):
            currentIndex -= 1
            cy = int(currentIndex / 4)
            cx = (currentIndex % 4)
            self.currentCustomLevel = vec(cx, cy)

    def main(self, transition=False, reload=True):
        self.open = True
        self.levelSelectOpen = False
        self.customLevelSelectOpen = False
        self.regionSelectOpen = False
        x = 100

        title = Label(
            self, "Transport \n The \n Public", 70, BLACK, (x - 500, 40))
        title.setItalic(True)

        cont = Label(self, "Continue", 50,  BLACK, (x - 500, 280))
        editor = Label(
            self, "Level editor", 50, BLACK, (x - 540, cont.y + 60))
        options = Label(self, "Options", 50, BLACK, (x - 580, editor.y + 60))
        end = Label(self, "Quit", 50, BLACK, (x - 620, options.y + 60))

        cont.addEvent(mf.openRegionSelect, 'onMouseClick')
        editor.addEvent(mf.openMapEditor, 'onMouseClick')
        options.addEvent(mf.openOptionsMenu, 'onMouseClick')
        end.addEvent(mf.closeGame, 'onMouseClick')

        labels = [title, cont, editor, options, end]
        for i, label in enumerate(labels):
            # Stop the title from having a hover event
            if i > 0:
                label.addEvent(gf.hoverOver, 'onMouseOver', x=x + 10)
                label.addEvent(gf.hoverOut, 'onMouseOut', x=x)

            label.addAnimation(
                tf.transitionX, 'onLoad', speed=12, transitionDirection="left",
                x=x, callback=gf.defaultSlideXCallback)
            self.add(label)

        # We don't always want to reload the map,
        # such as when we are accessing the option menu through the main menu.
        if reload:
            self.game.spriteRenderer.createLevel(
                self.game.mapLoader.getMap(self.splashScreenMaps[-1]), True)
            self.game.spriteRenderer.setRendering(True)
            self.game.spriteRenderer.setFixedScale(1.4)
            self.game.spriteRenderer.calculateOffset()
            self.game.spriteRenderer.resize()
            self.game.paused = False

        if transition:
            self.slideTransitionY(
                (0, 0), 'second', speed=40, callback=gf.defaultSlideCallback,
                direction='down')

    def saveCurrentLevel(self, currentLevel):
        # We don't need to save default level select so we just return.
        if self.levelSelectOpen:
            return
        elif self.regionSelectOpen:
            config["player"]["currentRegion"] = [
                currentLevel.x, currentLevel.y]
        elif self.customLevelSelectOpen:
            config["player"]["currentCustomLevel"] = [
                currentLevel.x, currentLevel.y]
        dump(config)

    def changeCurrentLevel(self, change=vec(0, 0)):
        currentLevel = self.getCurrentLevel()
        if ((change.x > 0 and currentLevel.x < self.getLevelSelectCols() - 1)
                or (change.y > 0
                    and currentLevel.y < self.getLevelSelectRows() - 1)
                or (change.x < 0 and currentLevel.x > 0)
                or (change.y < 0 and currentLevel.y > 0)):
            currentLevel += change
            self.saveCurrentLevel(currentLevel)
            return True
        return False

    def createLevel(self, x, y, count, maps, offset=vec(0, 0), region=False):
        if x >= 0 and y >= 0 and x < len(maps[0]) and y < len(maps):
            pos = (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + ((self.levelWidth + self.spacing) * x) - offset.x,
                (config["graphics"]["displayHeight"] - self.levelHeight) / 2
                + ((self.levelHeight + self.spacing) * y) - offset.y)

            selector = Region if region else Map
            level = selector(
                self, maps[y][x], (self.levelWidth, self.levelHeight), pos)

            self.add(level)
            self.levels[count] = level

            # Update the loading screen when the level has loaded
            self.updateLoadingScreen()

            return count + 1

    def levelForward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, x):
                obj.x = x
                menu.setTransitioning(False)

            for index, level in self.getLevels().items():
                level.addAnimation(
                    tf.transitionX, 'onLoad', speed=-30,
                    transitionDirection="right",
                    x=level.x - (self.levelWidth + self.spacing),
                    callback=callback)
            self.setTransitioning(True)

    def levelBackward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, x):
                obj.x = x
                menu.setTransitioning(False)

            for index, level in self.getLevels().items():
                level.addAnimation(
                    tf.transitionX, 'onLoad', speed=30,
                    transitionDirection="left",
                    x=level.x + (self.levelWidth + self.spacing),
                    callback=callback)
            self.setTransitioning(True)

    def levelUpward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, y):
                obj.y = y
                menu.setTransitioning(False)

            for index, level in self.getLevels().items():
                level.addAnimation(
                    tf.transitionY, 'onLoad', speed=30,
                    transitionDirection="down",
                    y=level.y + (self.levelHeight + self.spacing),
                    callback=callback)
            self.setTransitioning(True)

    def levelDownward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, y):
                obj.y = y
                menu.setTransitioning(False)

            for index, level in self.getLevels().items():
                level.addAnimation(
                    tf.transitionY, 'onLoad', speed=-30,
                    transitionDirection="up",
                    y=level.y - (self.levelHeight + self.spacing),
                    callback=callback)
            self.setTransitioning(True)

    def removeLevelClickable(self, level):
        level.removeEvent(
            mf.levelForward, 'onMouseClick', change=vec(1, 0))
        level.removeEvent(
            mf.levelBackward, 'onMouseClick', change=vec(-1, 0))
        level.removeEvent(
            mf.levelUpward, 'onMouseClick', change=vec(0, -1))
        level.removeEvent(
            mf.levelDownward, 'onMouseClick', change=vec(0, 1))

    def setLevelsClickable(self, currentLevel=vec(0, 0)):
        for index, level in self.levels.items():
            currentIndex = (
                (currentLevel.y * self.getLevelSelectCols()) + currentLevel.x)
            if index == currentIndex:
                self.removeLevelClickable(level)

                # If the level is not locked we can load and play it!
                if not level.getLevelData()["locked"]["isLocked"]:
                    if isinstance(level, Map):
                        level.addEvent(
                            mf.loadLevel, 'onMouseClick',
                            path=level.getLevelPath(),
                            data=level.getLevelData())

                    elif isinstance(level, Region):
                        # We have an instance of a region!
                        level.addEvent(
                            mf.openLevelSelect, 'onMouseClick',
                            region=level.getName())

                # Otherwise we need to check if the level can be unlocked
                else:
                    level.addEvent(mf.unlockLevel, 'onMouseClick', level=level)

                if currentIndex < len(self.levels) - 1:
                    self.removeLevelClickable(self.levels[currentIndex + 1])
                    self.levels[currentIndex + 1].addEvent(
                        mf.levelForward, 'onMouseClick', change=vec(1, 0))

                if currentIndex < len(self.levels) - 4:
                    self.removeLevelClickable(self.levels[currentIndex + 4])
                    self.levels[currentIndex + 4].addEvent(
                        mf.levelDownward, 'onMouseClick', change=vec(0, 1))

                if currentIndex > 0:
                    self.removeLevelClickable(self.levels[currentIndex - 1])
                    self.levels[currentIndex - 1].addEvent(
                        mf.levelBackward, 'onMouseClick', change=vec(-1, 0))

                if currentIndex - 3 > 0:
                    self.removeLevelClickable(self.levels[currentIndex - 4])
                    self.levels[currentIndex - 4].addEvent(
                        mf.levelUpward, 'onMouseClick', change=vec(0, -1))

                # Only default level selection page needs completion checking.
                if (self.currentLevelSelect
                        != MainMenu.LevelSelect.LEVELSELECT):
                    continue

                text = (
                    "Level Complete!"
                    if level.getLevelData()["completion"]["completed"]
                    else "Level Incomplete")
                image = (
                    "buttonGreen"
                    if level.getLevelData()["completion"]["completed"]
                    else "buttonRed")
                self.levelCompleteText.setText(text)
                self.levelComplete.setImageName(image)
                self.levelCompleteText.dirty = True
                self.levelComplete.dirty = True

            else:
                # Remove click event
                if isinstance(level, Map):
                    level.removeEvent(
                        mf.loadLevel, 'onMouseClick',
                        path=level.getLevelPath(), data=level.getLevelData())

                else:
                    # Remove region stuff here!
                    level.removeEvent(
                        mf.openLevelSelect, 'onMouseClick',
                        region=level.getName())

                level.removeEvent(mf.unlockLevel, 'onMouseClick', level=level)

    # Split the list of maps into a 2d list with each sublist being
    # the length of cols.
    def getArrangedMaps(self, maps, cols, arrangedMaps=None):
        arrangedMaps = [] if arrangedMaps is None else arrangedMaps
        for i in range(0, len(maps), cols):
            arrangedMaps.append(maps[i: i + cols])
        return arrangedMaps

    def getLevelSelectCols(self):
        if len(self.currentMaps) <= 0:
            return
        return len(self.currentMaps[0])

    def getLevelSelectRows(self):
        if len(self.currentMaps) <= 0:
            return
        return len(self.currentMaps)

    def setLevelSelectMaps(
            self, maps, cols, currentLevel=vec(0, 0), region=False):
        self.levels = {}
        split = (currentLevel.y * cols) + currentLevel.x
        before = maps[:int(split)]
        after = maps[int(split):]
        mapsMiddle, mapsAfter = [], []

        mapsBefore = self.getArrangedMaps(before, cols)

        if len(mapsBefore) > 0 and len(mapsBefore[-1]) < cols:
            difference = cols - len(mapsBefore[-1])
            difference = min(difference, len(after))
            middle = copy.copy(after)

            for i in range(0, difference):
                mapsMiddle.append(middle[i])
                after.remove(middle[i])

            mapsAfter.append(mapsMiddle)

        mapsAfter = self.getArrangedMaps(after, cols, mapsAfter)

        offset = vec(
            (self.levelWidth + self.spacing) * currentLevel.x,
            (self.levelHeight + self.spacing) * currentLevel.y)
        count = 0

        # Add the maps before the currently selected map.
        for y, row in enumerate(mapsBefore):
            for x, _ in enumerate(row):
                count = self.createLevel(
                    x, y, count, mapsBefore, offset, region)

        offset = vec(0, 0)  # Reset offset

        # Add the maps after and including the currently selected map.
        for y, row in enumerate(mapsAfter):
            if y > 0 and len(mapsAfter[-1]) < cols:
                offset.x = (
                    (self.levelWidth + self.spacing)
                    * (cols - len(mapsAfter[0])))

            for x, _ in enumerate(row):
                count = self.createLevel(
                    x, y, count, mapsAfter, offset, region)

    def customLevelSelect(self, transition=False):
        self.open = True
        self.customLevelSelectOpen = True
        self.levelSelectOpen = False
        self.regionSelectOpen = False
        self.currentLevelSelect = MainMenu.LevelSelect.CUSTOMLEVELSELECT
        self.backgroundColor = CREAM  # Change this?
        self.setLevelSize(self.customLevelSize)
        self.spacing = 20
        cols = 4
        self.currentMaps = self.getArrangedMaps(self.customMaps, cols)

        # Add the levels first this time so that the menu appears above them.
        self.setLevelSelectMaps(self.customMaps, cols, self.currentCustomLevel)
        self.setLevelsClickable(self.currentCustomLevel)

        background = Rectangle(
            self, GREEN, (self.levelWidth, 60), (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2, 0),
            shapeBorderRadius=[0, 0, 20, 20], alpha=150)
        mainMenu = Image(
            self, "button", (25, 25), (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + self.spacing, 21))
        mainMenuText = Label(
            self, "Main Menu", 20, CREAM, (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + self.spacing + 30, 27))
        levelSelect = Image(
            self, "button", (25, 25), (
                mainMenuText.x + mainMenuText.getFontSize()[0] + 10, 21))
        levelSelectText = Label(
            self, "Level Selection", 20, CREAM, (
                mainMenuText.x + mainMenuText.getFontSize()[0] + 40, 27))

        mainMenu.addEvent(gf.hoverImage, 'onMouseOver', image="buttonSelected")
        mainMenu.addEvent(gf.hoverImage, 'onMouseOut', image="button")
        levelSelect.addEvent(
            gf.hoverImage, 'onMouseOver', image="buttonSelected")
        levelSelect.addEvent(gf.hoverImage, 'onMouseOut', image="button")

        mainMenu.addEvent(mf.openMainMenu, 'onMouseClick')
        mainMenuText.addEvent(mf.openMainMenu, 'onMouseClick')

        region = self.game.regionLoader.getCurrentRegion()
        levelSelect.addEvent(mf.openLevelSelect, 'onMouseClick', region=region)
        levelSelectText.addEvent(
            mf.openLevelSelect, 'onMouseClick', region=region)

        self.add(background)
        self.add(mainMenu)
        self.add(mainMenuText)
        self.add(levelSelect)
        self.add(levelSelectText)

        if transition:
            self.slideTransitionY(
                (0, 0), 'second', callback=gf.defaultSlideCallback)

    def levelSelect(self, region, transition=False):
        self.open = True
        self.levelSelectOpen = True
        self.customLevelSelectOpen = False
        self.regionSelectOpen = False
        self.currentLevelSelect = MainMenu.LevelSelect.LEVELSELECT
        self.backgroundColor = BLACK
        self.setLevelSize(self.builtInLevelSize)
        self.spacing = 30

        # Reset back to the start of the level select for the specific region.
        self.currentLevel = vec(0, 0)

        # Set current region so we can return to this specific level select.
        self.game.regionLoader.setCurrentRegion(region)

        maps = self.game.regionLoader.getRegionMaps(region)

        cols = len(maps)
        self.currentMaps = self.getArrangedMaps(maps, cols)

        back = Image(
            self, "button", (25, 25), (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + self.spacing, 21))
        backText = Label(
            self, "Back", 20, CREAM, (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + self.spacing + 30, 27))

        self.levelComplete = Image(
            self, "buttonRed", (25, 25), (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + self.spacing, config["graphics"]["displayHeight"] - 42))
        self.levelCompleteText = Label(
            self, "Level Incomplete", 20, CREAM, (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2
                + self.spacing + 30, config["graphics"]["displayHeight"] - 36))

        key = Image(
            self, "keyCream", (25, 25), (config["graphics"]["displayWidth"] - (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2)
                - self.spacing - 75, 21))
        keyTextBackground = Rectangle(
            self, CREAM, (40, 25), (config["graphics"]["displayWidth"] - (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2)
                - self.spacing - 40, 21), shapeBorderRadius=[5, 5, 5, 5])

        self.keyText = Label(
            self, str(config["player"]["keys"]), 20, BLACK, (
                config["graphics"]["displayWidth"]
                - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2)
                - self.spacing - 20, 27))
        self.keyText.setPos((
            self.keyText.x - (self.keyText.getFontSize()[0] / 2),
            self.keyText.y))

        levelNext = Image(
            self, "buttonArrow", (25, 25), (
                config["graphics"]["displayWidth"]
                - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2)
                - self.spacing - 25, config["graphics"]["displayHeight"] - 42))
        levelNext.flipImage(True, False)
        levelBack = Image(
            self, "buttonArrow", (25, 25),
            (levelNext.x - 25 - 10, config["graphics"]["displayHeight"] - 42))

        back.addEvent(gf.hoverImage, 'onMouseOver', image="buttonSelected")
        back.addEvent(gf.hoverImage, 'onMouseOut', image="button")
        levelNext.addEvent(
            gf.hoverImage, 'onMouseOver', image="buttonArrowSelected")
        levelNext.addEvent(
            gf.hoverImage, 'onMouseOut', image="buttonArrow")
        levelBack.addEvent(
            gf.hoverImage, 'onMouseOver', image="buttonArrowSelected")
        levelBack.addEvent(
            gf.hoverImage, 'onMouseOut', image="buttonArrow")

        back.addEvent(mf.openRegionSelect, 'onMouseClick')
        backText.addEvent(mf.openRegionSelect, 'onMouseClick')
        levelNext.addEvent(mf.levelForward, 'onMouseClick', change=vec(1, 0))
        levelBack.addEvent(mf.levelBackward, 'onMouseClick', change=vec(-1, 0))

        self.add(self.levelComplete)
        self.add(self.levelCompleteText)
        self.add(back)
        self.add(backText)
        self.add(key)
        self.add(keyTextBackground)
        self.add(self.keyText)
        self.add(levelNext)
        self.add(levelBack)

        # Add the maps after eveything else in the menu has been loaded
        self.setLevelSelectMaps(maps, cols, self.currentLevel)
        self.setLevelsClickable(self.currentLevel)

        if transition:
            self.slideTransitionY(
                (0, 0), 'second', callback=gf.defaultSlideCallback)

    def regionSelect(self, transition=False):
        self.open = True
        self.regionSelectOpen = True
        self.levelSelectOpen = False
        self.customLevelSelectOpen = False
        self.currentLevelSelect = MainMenu.LevelSelect.REGIONSELECT
        self.backgroundColor = BLACK

        # Exact level sizing
        self.levelWidth = 350
        self.levelHeight = 420
        self.spacing = 50

        cols = len(self.regions)
        self.currentMaps = self.getArrangedMaps(self.regions, cols)

        # Add the regions after eveything else in the menu has been loaded
        self.setLevelSelectMaps(self.regions, cols, self.currentRegion, True)
        self.setLevelsClickable(self.currentRegion)

        mainMenu = Image(
            self, "button", (25, 25), (
                ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) - 100
                + self.spacing, 21))
        mainMenuText = Label(
            self, "Main Menu", 20, CREAM, (
                ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) - 100
                + self.spacing + 30, 27))

        custom = Image(
            self, "button", (25, 25), (
                mainMenuText.x + mainMenuText.getFontSize()[0] + 10, 21))
        customText = Label(
            self, "Custom Levels", 20, CREAM, (
                mainMenuText.x + mainMenuText.getFontSize()[0] + 40, 27))

        key = Image(
            self, "keyCream", (25, 25), (config["graphics"]["displayWidth"] - (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2) + 100
                - self.spacing - 75, 21))
        keyTextBackground = Rectangle(
            self, CREAM, (40, 25), (config["graphics"]["displayWidth"] - (
                (config["graphics"]["displayWidth"] - self.levelWidth) / 2) + 100
                - self.spacing - 40, 21), shapeBorderRadius=[5, 5, 5, 5])

        self.keyText = Label(
            self, str(config["player"]["keys"]), 20, BLACK, (
                config["graphics"]["displayWidth"]
                - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) + 100
                - self.spacing - 20, 27))
        self.keyText.setPos((
            self.keyText.x - (self.keyText.getFontSize()[0] / 2),
            self.keyText.y))

        levelNext = Image(
            self, "buttonArrow", (25, 25), (
                config["graphics"]["displayWidth"]
                - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2)
                - self.spacing - 25, config["graphics"]["displayHeight"] - 42))
        levelNext.flipImage(True, False)
        levelBack = Image(
            self, "buttonArrow", (25, 25),
            (levelNext.x - 25 - 10, config["graphics"]["displayHeight"] - 42))

        custom.addEvent(gf.hoverImage, 'onMouseOver', image="buttonSelected")
        custom.addEvent(gf.hoverImage, 'onMouseOut', image="button")
        mainMenu.addEvent(gf.hoverImage, 'onMouseOver', image="buttonSelected")
        mainMenu.addEvent(gf.hoverImage, 'onMouseOut', image="button")
        levelNext.addEvent(
            gf.hoverImage, 'onMouseOver', image="buttonArrowSelected")
        levelNext.addEvent(
            gf.hoverImage, 'onMouseOut', image="buttonArrow")
        levelBack.addEvent(
            gf.hoverImage, 'onMouseOver', image="buttonArrowSelected")
        levelBack.addEvent(
            gf.hoverImage, 'onMouseOut', image="buttonArrow")

        custom.addEvent(mf.showCustomLevelSelect, 'onMouseClick')
        customText.addEvent(mf.showCustomLevelSelect, 'onMouseClick')
        mainMenu.addEvent(mf.openMainMenu, 'onMouseClick')
        mainMenuText.addEvent(mf.openMainMenu, 'onMouseClick')
        levelNext.addEvent(mf.levelForward, 'onMouseClick', change=vec(1, 0))
        levelBack.addEvent(mf.levelBackward, 'onMouseClick', change=vec(-1, 0))

        self.add(mainMenu)
        self.add(mainMenuText)
        self.add(custom)
        self.add(customText)
        self.add(key)
        self.add(keyTextBackground)
        self.add(self.keyText)
        self.add(levelNext)
        self.add(levelBack)

        if transition:
            self.slideTransitionY(
                (0, 0), 'second', callback=gf.defaultSlideCallback)


class OptionMenu(Menu):
    def __init__(self, game, spriteRenderer, mapEditor):
        super().__init__(game)
        self.spriteRenderer = spriteRenderer
        self.mapEditor = mapEditor

        # If the option menu is accessed through the main menu
        self.optionsOpen = False  # True = accessed through the main menu
        self.x = 100

    def setOptionsOpen(self, optionsOpen):
        self.optionsOpen = optionsOpen

    def main(self, pausedSurface=True, transition=False):
        self.open = True
        # If we access through main we know its not from the main menu
        self.optionsOpen = False
        self.game.paused = True
        self.spriteRenderer.getHud().setOpen(False)
        self.mapEditor.getHud().setOpen(False)

        if pausedSurface:
            self.spriteRenderer.createPausedSurface()
            self.mapEditor.createPausedSurface()

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)

        paused = Label(self, "Paused", 70, WHITE, (self.x, 100))

        options = Label(self, "Options", 50,  WHITE, (self.x, 200))
        levelSelect = Label(self, "Level Selection", 50, WHITE, (self.x, 260))
        mainMenu = Label(self, "Main Menu", 50, WHITE, (self.x, 320))
        close = Label(self, "Close", 30, WHITE, (self.x, 440))

        options.addEvent(mf.showOptions, 'onMouseClick')
        options.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        options.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        levelSelect.addEvent(mf.showLevelSelect, 'onMouseClick')
        levelSelect.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        levelSelect.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        mainMenu.addEvent(mf.showMainMenu, 'onMouseClick')
        mainMenu.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        mainMenu.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        close.addEvent(mf.unpause, 'onMouseClick')
        close.addEvent(gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        close.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        # background.add(paused)
        self.add(background)
        self.add(paused)
        self.add(options)
        self.add(levelSelect)
        self.add(mainMenu)
        self.add(close)

        if transition:
            self.openTransition()

    def options(self, transition=False):
        self.open = True

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)

        options = Label(self, "Options", 70, WHITE, (self.x, 100))

        graphics = Label(self, "Graphics", 50, WHITE, (self.x, 200))
        controls = Label(self, "Controls", 50, WHITE, (self.x, 260))
        audio = Label(self, "Audio", 50, WHITE, (self.x, 320))
        back = Label(
            self, "Back" if not self.optionsOpen else "Main Menu", 30,
            WHITE, (self.x, 440))

        graphics.addEvent(mf.showGraphics, 'onMouseClick')
        graphics.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        graphics.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        controls.addEvent(mf.showControls, 'onMouseClick')
        controls.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        controls.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        audio.addEvent(mf.showAudio, 'onMouseClick')
        audio.addEvent(gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        audio.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        back.addEvent(gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        back.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        if not self.optionsOpen:
            back.addEvent(mf.showMain, 'onMouseClick')

        # Accessed through main menu
        else:
            back.addEvent(mf.closeOptionsMenu, 'onMouseClick')

        self.add(background)
        self.add(options)
        self.add(graphics)
        self.add(controls)
        self.add(audio)
        self.add(back)

        if transition:
            self.openTransition()

    def audio(self):
        self.open = True

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)

        audio = Label(self, "Audio", 70, WHITE, (self.x, 100))
        master = Label(self, "Master Volume:", 50, WHITE, (self.x, 200))
        sound = Label(self, "Sound Volume:", 50, WHITE, (self.x, 280))
        music = Label(self, "Music Volume:", 50, WHITE, (self.x, 360))
        self.masterVolume = Slider(
            self, WHITE, config["audio"]["volume"]["master"]["current"],
            mf.setMasterVolume, (300, 30), (self.x + 450, 205))
        self.soundVolume = Slider(
            self, WHITE, config["audio"]["volume"]["sounds"]["current"],
            mf.setSoundVolume, (300, 30), (self.x + 450, 285))
        self.musicVolume = Slider(
            self, WHITE, config["audio"]["volume"]["music"]["current"],
            mf.setMusicVolume, (300, 30), (self.x + 450, 365))
        back = Label(self, "Back", 30,  WHITE, (self.x, 440))
        reset = Label(self, "Reset Default", 30, WHITE, (self.x + 450, 440))

        back.addEvent(mf.showOptions, 'onMouseClick')
        back.addEvent(gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        back.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        reset.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 450 + 10, color=BLACK)
        reset.addEvent(gf.hoverOut, 'onMouseOut', x=self.x + 450, color=WHITE)
        reset.addEvent(mf.resetAudio, 'onMouseClick')

        self.add(background)
        self.add(audio)
        self.add(master)
        self.add(sound)
        self.add(music)
        self.add(self.masterVolume)
        self.add(self.soundVolume)
        self.add(self.musicVolume)
        self.add(back)
        self.add(reset)

    def checkForExistingControl(self, key, currentName):
        if hasattr(self, 'controlKeys'):
            duplicates = [
                v for v in self.controlKeys.values() if v.getKeyInt() == key
                and v.getKeyName() != currentName]
            return duplicates[0] if len(duplicates) > 0 else False
        return False

    def checkForExistingControls(self):
        if hasattr(self, 'controlKeys'):
            seen = set()
            duplicates = set(
                k for k, v in self.controlKeys.items() if v.getKeyInt()
                in seen or seen.add(v.getKeyInt()))
            # If we find duplicates, return to the state when we loaded the
            # controls (so change nothing)
            if len(duplicates) > 0:
                for key, controlKey in self.controlKeys.items():
                    config["controls"][key]["current"] \
                        = controlKey.getInitialKeyInt()
                dump(config)

    # Check the if the user is midway through selecting a control key
    def checkKeySelection(self):
        if (hasattr(self, 'controlClickManager')
                and self.controlClickManager.getControlKey() is not None):
            return True
        return False

    def controls(self):
        self.open = True
        self.controlClickManager = ControlClickManager(self.game)
        self.controlKeys = {}

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)

        controls = Label(self, "Controls", 70, WHITE, (self.x, 100))

        layer1 = ControlLabel(
            self, "Layer 1:", "layer1", 40, WHITE, (self.x, 200))
        layer2 = ControlLabel(
            self, "Layer 2:", "layer2", 40, WHITE, (self.x, 250))
        layer3 = ControlLabel(
            self, "Layer 3:", "layer3", 40, WHITE, (self.x, 300))
        layer4 = ControlLabel(
            self, "Layer 4:", "layer4", 40, WHITE, (self.x, 350))
        pause = ControlLabel(
            self, "Pause:", "pause", 40, WHITE, (self.x + 400, 200))
        slowdown = ControlLabel(
            self, "Slowdown:", "slowdown", 40, WHITE, (self.x + 400, 250))
        fastforward = ControlLabel(
            self, "Fastforward:", "fastforward", 40, WHITE,
            (self.x + 400, 300))
        back = Label(self, "Back", 30,  WHITE, (self.x, 440))
        reset = Label(self, "Reset Default", 30, WHITE, (self.x + 400, 440))

        layer1.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        layer1.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)
        layer1.addEvent(mf.clearKeyText, 'onMouseClick')

        layer2.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        layer2.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)
        layer2.addEvent(mf.clearKeyText, 'onMouseClick')

        layer3.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        layer3.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)
        layer3.addEvent(mf.clearKeyText, 'onMouseClick')

        layer4.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        layer4.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)
        layer4.addEvent(mf.clearKeyText, 'onMouseClick')

        pause.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 400 + 10, color=BLACK)
        pause.addEvent(gf.hoverOut, 'onMouseOut', x=self.x + 400, color=WHITE)
        pause.addEvent(mf.clearKeyText, 'onMouseClick')

        slowdown.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 400 + 10, color=BLACK)
        slowdown.addEvent(
            gf.hoverOut, 'onMouseOut', x=self.x + 400, color=WHITE)
        slowdown.addEvent(mf.clearKeyText, 'onMouseClick')

        fastforward.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 400 + 10, color=BLACK)
        fastforward.addEvent(
            gf.hoverOut, 'onMouseOut', x=self.x + 400, color=WHITE)
        fastforward.addEvent(mf.clearKeyText, 'onMouseClick')

        back.addEvent(gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        back.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)
        back.addEvent(mf.showOptions, 'onMouseClick')

        reset.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 400 + 10, color=BLACK)
        reset.addEvent(gf.hoverOut, 'onMouseOut', x=self.x + 400, color=WHITE)
        reset.addEvent(mf.resetControls, 'onMouseClick')

        allControls = [
            layer1, layer2, layer3, layer4, pause, slowdown, fastforward]

        self.add(background)
        self.add(controls)

        for control in allControls:
            self.add(control)
            self.controlKeys[control.getKeyName()] = control

        self.add(back)
        self.add(reset)

    def graphics(self):
        self.open = True

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)

        graphics = Label(self, "Graphics", 70, WHITE, (self.x, 100))

        fullscreenText = "On" if self.game.fullscreen else "Off"
        scanlinesText = (
            "On" if config["graphics"]["scanlines"]["enabled"] else "Off")
        scalingText = (
            "Smooth" if config["graphics"]["smoothscale"] else "Harsh")
        vsyncText = "On" if config["graphics"]["vsync"] else "Off"

        fullscreen = Label(
            self, "Fullscreen: " + fullscreenText, 50, WHITE, (self.x, 200))
        scanlines = Label(
            self, "Scanlines: " + scanlinesText, 50, WHITE, (self.x, 260))
        scaling = Label(
            self, "Scaling: " + scalingText, 50, WHITE, (self.x, 320))
        vsync = Label(
            self, "Vsync: " + vsyncText, 50, WHITE, (self.x + 500, 200))
        back = Label(self, "Back", 30,  WHITE, (self.x, 440))

        fullscreen.addEvent(mf.toggleFullscreen, 'onMouseClick')
        fullscreen.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        fullscreen.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        scanlines.addEvent(mf.toggleScanlines, 'onMouseClick')
        scanlines.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        scanlines.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        scaling.addEvent(mf.toggleScalingMode, 'onMouseClick')
        scaling.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        scaling.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        vsync.addEvent(mf.toggleVsync, 'onMouseClick')
        vsync.addEvent(
            gf.hoverOver, 'onMouseOver', x=self.x + 500 + 10, color=BLACK)
        vsync.addEvent(gf.hoverOut, 'onMouseOut', x=self.x + 500, color=WHITE)

        back.addEvent(mf.showOptions, 'onMouseClick')
        back.addEvent(gf.hoverOver, 'onMouseOver', x=self.x + 10, color=BLACK)
        back.addEvent(gf.hoverOut, 'onMouseOut', x=self.x, color=WHITE)

        self.add(background)
        self.add(graphics)
        self.add(fullscreen)
        self.add(scanlines)
        self.add(scaling)
        self.add(vsync)
        self.add(back)


class GameMenu(Menu):
    def __init__(self, spriteRenderer):
        super().__init__(spriteRenderer.game)
        self.spriteRenderer = spriteRenderer
        self.startScreenOpen = False
        self.endScreenOpen = False

    def closeTransition(self):
        self.game.audioLoader.playSound("swoopOut")
        self.spriteRenderer.getHud().setOpen(True)

        def callback(obj, menu, x):
            menu.game.paused = False
            menu.game.spriteRenderer.getHud().slideHudIn()
            # Add the first player
            menu.game.spriteRenderer.gridLayer2.createPerson(
                menu.game.spriteRenderer.getAllDestination())
            menu.close()

        for component in self.components:
            component.addAnimation(
                tf.transitionX, 'onLoad', speed=-40,
                transitionDirection="right", x=-400, callback=callback)

    # Anything used by both the completed and game over end screens
    def endScreen(self):
        self.open = True
        self.endScreenOpen = True
        self.startScreenOpen = False

        self.game.paused = True
        self.spriteRenderer.getHud().setOpen(False)

        self.spriteRenderer.createPausedSurface()

    def endScreenGameOver(self, transition=False):
        self.endScreen()

        width = config["graphics"]["displayWidth"] / 2
        x = width - (width / 2)

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)
        failed = Label(
            self, "Level Failed!", 45, WHITE, (((x + width) / 2 - 30), 100))

        scoreText = Label(self, "Highest Score", 25, WHITE, (width - 87, 210))
        self.score = DifficultyMeter(
            self, YELLOW, WHITE, 3,
            self.spriteRenderer.getLevelData()["score"], 5, (40, 40),
            (width - 50, scoreText.y + scoreText.getFontSize()[1] + 10),
            shapeBorderRadius=[5, 5, 5, 5])
        self.score.setPos(
            (width - (self.score.getFullSize()[0] / 2), self.score.y))

        keyTextBackground = Rectangle(
            self, WHITE, (60, 35),
            (width - 30, self.score.y + self.score.height + 30),
            shapeBorderRadius=[5, 5, 5, 5])
        self.keyText = Label(
            self, str(config["player"]["keys"]), 25, BLACK,
            (width - 20, keyTextBackground.y + 10))
        self.keyText.setPos(
            (width - (self.keyText.getFontSize()[0] / 2), self.keyText.y))
        self.keyTextDifference = Label(
            self, "+0", 25, WHITE, (
                keyTextBackground.x + keyTextBackground.width + 10,
                self.keyText.y))
        key = Image(
            self, "keyWhite", (35, 35),
            (keyTextBackground.x - 35 - 10, keyTextBackground.y))

        levelSelect = Label(
            self, "Level Selection", 25, WHITE, (
                (width - 100), config["graphics"]["displayHeight"] - 100))
        levelSelect.setPos(
            (width - (levelSelect.getFontSize()[0] / 2), levelSelect.y))
        retry = Label(
            self, "Retry", 25, WHITE, (width - 100, levelSelect.y - 10))
        retry.setPos((
            width - (retry.getFontSize()[0] / 2),
            levelSelect.y - 20 - retry.getFontSize()[1]))

        levelSelect.addEvent(gf.hoverColor, 'onMouseOver', color=BLACK)
        levelSelect.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
        levelSelect.addEvent(mf.showLevelSelect, 'onMouseClick')

        retry.addEvent(gf.hoverColor, 'onMouseOver', color=BLACK)
        retry.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)

        # Get the name of the current level so we can restart it.
        levelName = self.spriteRenderer.getLevel()
        retry.addEvent(
            mf.loadLevel, 'onMouseClick',
            path=self.game.mapLoader.getMap(levelName),
            data=self.game.mapLoader.getMapData(levelName))

        self.add(background)
        self.add(failed)
        self.add(scoreText)
        self.add(self.score)
        self.add(key)
        self.add(keyTextBackground)
        self.add(self.keyText)
        self.add(self.keyTextDifference)
        self.add(levelSelect)
        self.add(retry)

        if transition:
            self.openTransition()

    def endScreenComplete(self, transition=False):
        self.endScreen()
        self.spriteRenderer.setLevelComplete()  # Complete the level
        # Set the score
        (previousKeys,
            self.keyDifference,
            self.previousScore) = self.spriteRenderer.setLevelScore()

        width = config["graphics"]["displayWidth"] / 2
        x = width - (width / 2)

        background = Rectangle(
            self, GREEN, (
                config["graphics"]["displayWidth"],
                config["graphics"]["displayHeight"]), (0, 0), alpha=150)
        success = Label(
            self, "Level Compelte!", 45, WHITE, (((x + width) / 2 - 50), 100))

        scoreText = Label(self, "Highest Score", 25, WHITE, (width - 87, 210))
        self.score = DifficultyMeter(
            self, YELLOW, WHITE, 3, self.previousScore, 5, (40, 40),
            (width - 50, scoreText.y + scoreText.getFontSize()[1] + 10),
            shapeBorderRadius=[5, 5, 5, 5])
        self.score.setPos((
            width - (self.score.getFullSize()[0] / 2), self.score.y))

        keyTextBackground = Rectangle(
            self, WHITE, (60, 35),
            (width - 30, self.score.y + self.score.height + 30),
            shapeBorderRadius=[5, 5, 5, 5])
        self.keyText = Label(
            self, str(previousKeys), 25, BLACK, (
                width - 20, keyTextBackground.y + 10))
        self.keyText.setPos(
            (width - (self.keyText.getFontSize()[0] / 2), self.keyText.y))
        self.keyTextDifference = Label(
            self, "+" + str(self.keyDifference), 25, WHITE, (
                keyTextBackground.x + keyTextBackground.width + 10,
                self.keyText.y))
        key = Image(
            self, "keyWhite", (35, 35), (
                keyTextBackground.x - 35 - 10, keyTextBackground.y))

        levelSelect = Label(
            self, "Level Selection", 25, WHITE, (
                (width - 100), config["graphics"]["displayHeight"] - 100))
        levelSelect.setPos(
            (width - (levelSelect.getFontSize()[0] / 2), levelSelect.y))
        retry = Label(
            self, "Retry", 25, WHITE, (width - 100, levelSelect.y - 10))
        retry.setPos((
            width - (retry.getFontSize()[0] / 2),
            levelSelect.y - 20 - retry.getFontSize()[1]))

        levelSelect.addEvent(gf.hoverColor, 'onMouseOver', color=BLACK)
        levelSelect.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
        levelSelect.addEvent(mf.showLevelSelect, 'onMouseClick')

        retry.addEvent(gf.hoverColor, 'onMouseOver', color=BLACK)
        retry.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)

        # Get the name of the current level so we can restart it.
        levelName = self.spriteRenderer.getLevel()
        retry.addEvent(
            mf.loadLevel, 'onMouseClick',
            path=self.game.mapLoader.getMap(levelName),
            data=self.game.mapLoader.getMapData(levelName))

        self.add(background)
        self.add(success)
        self.add(scoreText)
        self.add(self.score)
        self.add(key)
        self.add(keyTextBackground)
        self.add(self.keyText)
        self.add(self.keyTextDifference)

        if transition and self.keyDifference <= 0:
            self.add(levelSelect)
            self.add(retry)

        if transition:
            def callback(obj, menu, y):
                obj.y = y
                menu.game.audioLoader.playSound("levelComplete", 1)

                if menu.keyDifference > 0:
                    menu.keyText.addAnimation(
                        tf.increaseKeys, 'onLoad',
                        levelSelectButton=levelSelect, retryButton=retry)
                    menu.keyTextDifference.addAnimation(
                        tf.decreaseKeys, 'onLoad')

                currentScore = menu.previousScore + menu.keyDifference
                if currentScore > menu.previousScore:
                    menu.score.addAnimation(
                        tf.increaseMeter, 'onLoad',
                        fromAmount=menu.previousScore,
                        toAmount=menu.previousScore + self.keyDifference)

            self.openTransition(callback)

    def startScreen(self):
        self.open = True
        self.startScreenOpen = True
        self.endScreenOpen = False

        # show this before the game is unpaused so we don't need this
        self.game.paused = True
        self.spriteRenderer.getHud().setOpen(False)

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        totalText = (
            "Transport " + str(self.spriteRenderer.getTotalToComplete())
            + " people!")

        background = Rectangle(self, GREEN, (width, height), (x - 400, y))
        total = Label(
            self, totalText, 45, WHITE, (
                ((x + width) / 2 - 110) - 400, (y + height) / 2 + 20))
        play = Label(
            self, "Got it!", 25, WHITE, (
                ((config["graphics"]["displayWidth"] / 2) - 40) - 400,
                (config["graphics"]["displayHeight"] / 2) + 20))

        background.addAnimation(
            tf.transitionX, 'onLoad', speed=40, transitionDirection="left",
            x=x, callback=gf.defaultSlideXCallback)
        total.addAnimation(
            tf.transitionX, 'onLoad', speed=40, transitionDirection="left",
            x=((x + width) / 2 - 110), callback=gf.defaultSlideXCallback)
        play.addAnimation(
            tf.transitionX, 'onLoad', speed=40, transitionDirection="left",
            x=((config["graphics"]["displayWidth"] / 2) - 40),
            callback=gf.defaultSlideXCallback)

        play.addEvent(gf.hoverColor, 'onMouseOver', color=BLACK)
        play.addEvent(gf.hoverColor, 'onMouseOut', color=WHITE)
        play.addEvent(mf.unpause, 'onMouseClick')

        self.add(background)
        self.add(total)
        self.add(play)

        self.game.audioLoader.playSound("swoopIn")
