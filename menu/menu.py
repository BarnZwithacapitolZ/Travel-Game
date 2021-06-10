import pygame
from pygame.locals import *
from config import *

from generalFunctions import *
from menuFunctions import *
from hudFunctions import *
from transitionFunctions import *
from menuComponents import *

from clickManager import *
import abc
import random
import copy

vec = pygame.math.Vector2


class Menu:
    def __init__(self, game):
        pygame.font.init()

        self.open = False
        self.game = game
        self.renderer = game.renderer
        self.components = [] # Components to render to the screen

        self.clicked = False

        self.loadingImage = Image(self, "loading1", (100, 72), ((config["graphics"]["displayWidth"] / 2) - 50, (config["graphics"]["displayHeight"] / 2) - 36))

    
    def setOpen(self, hudOpen):
        self.open = hudOpen


    def getOpen(self):
        return self.open


    def getComponents(self):
        return self.components


    def add(self, component):
        self.components.append(component)


    def remove(self, obj):
        if obj in self.components:
            self.components.remove(obj)
            del obj


    def clickButton(self):  
        click = random.randint(1, 2)
        self.game.audioLoader.playSound("click%i" % click)    


    def resize(self):
        for component in self.components:
            component.resize() # force redraw

            if isinstance(component, InputBox):
                component.resizeIndicator()
                

    def display(self):  
        for component in list(self.components): # we use list so we can delete from the array whilst looping through it (without causing flicking with double blits)
            component.draw()

            # only if the menu is open do we want to allow for interactions
            if self.open:
                self.events(component)
                self.animate(component)


    def animate(self, component):
        if hasattr(component, 'rect'):
            if len(component.animations) > 0:
                for function, animation in list(component.animations.items()):
                    if animation[0] == 'onMouseOver':
                        function(component, self, function, **animation[1])
                        # component.dirty = True

                    if animation[0] == 'onMouseOut':
                        function(component, self, function, **animation[1])
                        # component.dirty = True

                    if animation[0] == 'onLoad':
                        function(component, self, function, **animation[1])
                        # component.dirty = True


    def events(self, component):
        mx, my = pygame.mouse.get_pos()
        difference = self.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        if hasattr(component, 'rect'): # check the component has been drawn (if called before next tick)
            if len(component.events) > 0:
                for e in list(component.events):
                    if e['event'] == 'onMouseClick':
                        if component.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
                            self.clickButton()
                            self.game.clickManager.setClicked(False)
                            e['function'](component, self, e, **e['kwargs'])
                            # component.dirty = True

                    if e['event'] == 'onMouseOver':
                        if component.rect.collidepoint((mx, my)) and not component.mouseOver:
                            component.mouseOver = True
                            e['function'](component, self, e, **e['kwargs'])
                            component.dirty = True

                    if e['event'] == 'onMouseOut':
                        if not component.rect.collidepoint((mx, my)) and component.mouseOver:
                            component.mouseOver = False
                            e['function'](component, self, e, **e['kwargs'])
                            component.dirty = True

                    if e['event'] == 'onKeyPress':
                        if self.game.textHandler.getPressed():
                            self.game.textHandler.setPressed(False)
                            e['function'](component, self, e, **e['kwargs'])
                            component.dirty = True


    # define where key events will be called
    def keyEvents(self):
        pass
                            

    def setClicked(self, clicked):
        if self.open:
            self.clicked = clicked


    def close(self):
        for component in self.components:
            del component
        self.components = []
        self.open = False


    def transition(self):
        self.open = True

        test = Rectangle(self, BLACK, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), 255)
        test.addAnimation(transitionFadeOut, 'onLoad')
        self.add(test)


    def slideTransitionY(self, pos, half, speed = -40, callback = None, direction = 'up'):
        transition = Rectangle(self, TRUEBLACK, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), pos)
        transition.addAnimation(slideTransitionY, 'onLoad', speed = speed, half = half, callback = callback, transitionDirection = direction)
        self.add(transition)


    def slideTransitionX(self, pos, half, speed = -70, callback = None):
        transition = Rectangle(self, TRUEBLACK, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), pos)
        transition.addAnimation(slideTransitionX, 'onLoad', speed = speed, half = half, callback = callback)
        self.add(transition)


    def loadingScreen(self):
        self.loadingImage.setImageName("loading1")
        self.loadingImage.dirty = True
        loadingText = Label(self, "Loading", 30, Color("white"), (config["graphics"]["displayWidth"] / 2 - 58, config["graphics"]["displayHeight"] / 2 + 45))

        self.add(self.loadingImage)
        self.add(loadingText)


    def updateLoadingScreen(self):
        if self.loadingImage.getImageName() == "loading1":
            self.loadingImage.setImageName("loading2")
        else:
            self.loadingImage.setImageName("loading1")
        self.loadingImage.dirty = True  


class MainMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.currentLevel = vec(0, 0)
        self.currentCustomLevel = vec(0, 0)  # some level selection have multiple rows, cols
        self.builtInMaps = list(self.game.mapLoader.getBuiltInMaps().keys())
        self.customMaps = list(self.game.mapLoader.getCustomMaps().keys())
        self.currentMaps = self.builtInMaps
        self.levels = {}
        self.backgroundColor = GREEN
        
        self.builtInLevelSize = 3.5
        self.customLevelSize = 2.2

        self.setLevelSize(self.builtInLevelSize)
        self.spacing = 20

        self.transitioning = False

    def getBackgroundColor(self):
        return self.backgroundColor

    def getLevels(self):
        return self.levels

    def getCurrentLevel(self):
        if self.levelSelectOpen:
            return self.currentLevel
        elif self.customLevelSelect:
            return self.currentCustomLevel

    def getTransitioning(self):
        return self.transitioning

    # If either of the level selection screens are open
    def getLevelSelectOpen(self):
        if self.levelSelectOpen or self.customLevelSelectOpen:
            return True
        return False
    
    def setTransitioning(self, transitioning):
        self.transitioning = transitioning

    def setLevelSize(self, scaler=5):  # larger scaler = larger image
        self.levelWidth = config["graphics"]["displayWidth"] - (config["graphics"]["displayWidth"] / scaler)
        self.levelHeight = config["graphics"]["displayHeight"] - (config["graphics"]["displayHeight"] / scaler)

    def updateCustomMaps(self):
        # self.builtInMaps = list(self.game.mapLoader.getBuiltInMaps().keys())
        self.customMaps = list(self.game.mapLoader.getCustomMaps().keys())
        currentIndex = (self.currentCustomLevel.y * self.getLevelSelectCols()) + self.currentCustomLevel.x

        if currentIndex >= len(self.customMaps):
            currentIndex -= 1
            cy = int(currentIndex / 4)
            cx = (currentIndex % 4)
            self.currentCustomLevel = vec(cx, cy)            

    def main(self, transition = False):
        self.open = True
        self.levelSelectOpen = False
        self.customLevelSelectOpen = False
        self.backgroundColor = GREEN

        sidebar = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0))

        # x = (config["graphics"]["displayWidth"] / 2) - 180
        x = 100

        title1 = Label(self, "Transport", 70, Color("white"), (x, 80), GREEN)
        title2 = Label(self, "The", 30, Color("white"), (x, title1.y + 70), GREEN)
        title3 = Label(self, "Public", 70, Color("white"), (x, title2.y + 30), GREEN)

        title1.setItalic(True)
        title2.setItalic(True)
        title3.setItalic(True)

        cont = Label(self, "Continue", 50,  BLACK, (x, 290), GREEN)
        editor = Label(self, "Level editor", 50, BLACK, (x, cont.y + 60), GREEN)
        options = Label(self, "Options", 50, BLACK, (x, editor.y + 60), GREEN)
        end = Label(self, "Quit", 50, BLACK, (x, options.y + 60), GREEN)

        # test = Image(self, "button", (50, 50), (10, 10))
        # test2 = Label(self, "hi", 20, BLACK, (15, 15))
        # test.add(test2)
        # test.addEvent(hoverImage, 'onMouseOver', image = "buttonSelected")
        # test.addEvent(hoverImage, 'onMouseOut', image = "button")
        # self.add(test)

        # test = FillRectangle(self, (0, 0, 0, 0), (40, 40), (20, 20))
        # test2 = Label(self, "hi", 20, Color("white"), (0, 0))
        # test.add(test2)
        # self.add(test)

        # test = DifficultyMeter(self, RED, BLACK, 4, 2, 2, (15, 15), (20, 20))
        # self.add(test)

        cont.addEvent(openLevelSelect, 'onMouseClick')
        cont.addEvent(hoverOver, 'onMouseOver', x = x + 10)
        cont.addEvent(hoverOut, 'onMouseOut', x = x)

        editor.addEvent(openMapEditor, 'onMouseClick')
        editor.addEvent(hoverOver, 'onMouseOver', x = x + 10)
        editor.addEvent(hoverOut, 'onMouseOut', x = x)

        options.addEvent(hoverOver, 'onMouseOver', x = x + 10)
        options.addEvent(hoverOut, 'onMouseOut', x = x)

        end.addEvent(closeGame, 'onMouseClick')
        end.addEvent(hoverOver, 'onMouseOver', x = x + 10)
        end.addEvent(hoverOut, 'onMouseOut', x = x)

        # self.add(sidebar)
        # self.add(otherbar)

        self.add(title1)
        self.add(title2)
        self.add(title3)
        self.add(cont)
        self.add(editor)
        self.add(options)
        self.add(end)

        if transition:
            # set the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                menu.remove(obj)
        
            self.slideTransitionY((0, 0), 'second', speed = 40, callback = callback, direction = 'down')

    def changeCurrentLevel(self, change=vec(0, 0)):
        currentLevel = self.getCurrentLevel()
        if ((change.x > 0 and currentLevel.x < self.getLevelSelectCols() - 1) 
                or (change.y > 0 and currentLevel.y < self.getLevelSelectRows() - 1)
                or (change.x < 0 and currentLevel.x > 0)
                or (change.y < 0 and currentLevel.y > 0)):
            currentLevel += change
            return True
        return False

    def createLevel(self, x, y, count, maps, offset=vec(0, 0)):
        if x >= 0 and y >= 0 and x < len(maps[0]) and y < len(maps):
            level = Map(self, maps[y][x], count, (self.levelWidth, self.levelHeight), ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + ((self.levelWidth + self.spacing) * x) - offset.x, (config["graphics"]["displayHeight"] - self.levelHeight) / 2 + ((self.levelHeight + self.spacing) * y) - offset.y))
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
                level.addAnimation(transitionX, 'onLoad', speed = -30, transitionDirection = "right", x = level.x - (self.levelWidth + self.spacing), callback = callback)
            self.setTransitioning(True)

    def levelBackward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, x):
                obj.x = x
                menu.setTransitioning(False)
        
            for index, level in self.getLevels().items():
                level.addAnimation(transitionX, 'onLoad', speed = 30, transitionDirection = "left", x = level.x + (self.levelWidth + self.spacing), callback = callback)
            self.setTransitioning(True)

    def levelUpward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, y):
                obj.y = y
                menu.setTransitioning(False)

            for index, level in self.getLevels().items():
                level.addAnimation(transitionY, 'onLoad', speed = 30, transitionDirection = "down", y = level.y + (self.levelHeight + self.spacing), callback = callback)
            self.setTransitioning(True)

    def levelDownward(self, change=vec(0, 0)):
        if not self.getTransitioning() and self.changeCurrentLevel(change):
            self.setLevelsClickable(self.getCurrentLevel())

            def callback(obj, menu, y):
                obj.y = y
                menu.setTransitioning(False)
            
            for index, level in self.getLevels().items():
                level.addAnimation(transitionY, 'onLoad', speed = -30, transitionDirection = "up", y = level.y - (self.levelHeight + self.spacing), callback = callback)
            self.setTransitioning(True)

    def setLevelsClickable(self, currentLevel=vec(0, 0)):
        for index, level in self.levels.items():
            currentIndex = (currentLevel.y * self.getLevelSelectCols()) + currentLevel.x
            if index == currentIndex:
                level.removeEvent(levelForward, 'onMouseClick', change=vec(1, 0))
                level.removeEvent(levelBackward, 'onMouseClick', change=vec(-1, 0))
                level.removeEvent(levelUpward, 'onMouseClick', change=vec(0, -1))
                level.removeEvent(levelDownward, 'onMouseClick', change=vec(0, 1))

                if not level.getLevelData()["locked"]["isLocked"]:
                    level.addEvent(loadLevel, 'onMouseClick', level = level.getLevel())

                else:
                    level.addEvent(unlockLevel, 'onMouseClick', level = level)

                if currentIndex < len(self.levels) - 1:
                    self.levels[currentIndex + 1].removeEvent(levelForward, 'onMouseClick', change=vec(1, 0))
                    self.levels[currentIndex + 1].removeEvent(levelBackward, 'onMouseClick', change=vec(-1, 0))
                    self.levels[currentIndex + 1].removeEvent(levelUpward, 'onMouseClick', change=vec(0, -1))
                    self.levels[currentIndex + 1].removeEvent(levelDownward, 'onMouseClick', change=vec(0, 1))
                    self.levels[currentIndex + 1].addEvent(levelForward, 'onMouseClick', change=vec(1, 0))

                if currentIndex < len(self.levels) - 4:
                    self.levels[currentIndex + 4].removeEvent(levelForward, 'onMouseClick', change=vec(1, 0))
                    self.levels[currentIndex + 4].removeEvent(levelBackward, 'onMouseClick', change=vec(-1, 0))
                    self.levels[currentIndex + 4].removeEvent(levelUpward, 'onMouseClick', change=vec(0, -1))
                    self.levels[currentIndex + 4].removeEvent(levelDownward, 'onMouseClick', change=vec(0, 1))
                    self.levels[currentIndex + 4].addEvent(levelDownward, 'onMouseClick', change=vec(0, 1))

                if currentIndex > 0:
                    self.levels[currentIndex - 1].removeEvent(levelForward, 'onMouseClick', change=vec(1, 0))
                    self.levels[currentIndex - 1].removeEvent(levelBackward, 'onMouseClick', change=vec(-1, 0))
                    self.levels[currentIndex - 1].removeEvent(levelUpward, 'onMouseClick', change=vec(0, -1))
                    self.levels[currentIndex - 1].removeEvent(levelDownward, 'onMouseClick', change=vec(0, 1))
                    self.levels[currentIndex - 1].addEvent(levelBackward, 'onMouseClick', change=vec(-1, 0))

                if currentIndex - 3 > 0:
                    self.levels[currentIndex - 4].removeEvent(levelForward, 'onMouseClick', change=vec(1, 0))
                    self.levels[currentIndex - 4].removeEvent(levelBackward, 'onMouseClick', change=vec(-1, 0))
                    self.levels[currentIndex - 4].removeEvent(levelUpward, 'onMouseClick', change=vec(0, -1))
                    self.levels[currentIndex - 4].removeEvent(levelDownward, 'onMouseClick', change=vec(0, 1))
                    self.levels[currentIndex - 4].addEvent(levelUpward, 'onMouseClick', change=vec(0, -1))

                text = "Level Complete!" if level.getLevelData()["completion"]["completed"] else "Level Incomplete"
                image = "buttonGreen" if level.getLevelData()["completion"]["completed"] else "buttonRed"
                self.levelCompleteText.setText(text)
                self.levelComplete.setImageName(image)
                self.levelCompleteText.dirty = True
                self.levelComplete.dirty = True

            else:
                # Remove click event
                level.removeEvent(loadLevel, 'onMouseClick', level = level.getLevel())
                level.removeEvent(unlockLevel, 'onMouseClick', level = level)

    def getArrangedMaps(self, maps, cols, arrangedMaps=None):
        arrangedMaps = [] if arrangedMaps is None else arrangedMaps 
        for i in range(0, len(maps), cols):
            arrangedMaps.append(maps[i : i + cols])
        return arrangedMaps

    def getLevelSelectCols(self):
        if len(self.currentMaps) <= 0:
            return

        return len(self.currentMaps[0])

    def getLevelSelectRows(self):
        if len(self.currentMaps) <= 0:
            return

        return len(self.currentMaps)

    def setLevelSelectMaps(self, maps, cols, currentLevel=vec(0, 0)):
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

        offset = vec((self.levelWidth + self.spacing) * currentLevel.x, (self.levelHeight + self.spacing) * currentLevel.y)
        count = 0

        for y, row in enumerate(mapsBefore):
            for x, level in enumerate(row):
                count = self.createLevel(x, y, count, mapsBefore, offset)
        
        offset = vec(0, 0)  # Reset offset

        for y, row in enumerate(mapsAfter):
            if y > 0 and len(mapsAfter[-1]) < cols:
                offset.x = (self.levelWidth + self.spacing) * (cols - len(mapsAfter[0]))

            for x, level in enumerate(row):
                count = self.createLevel(x, y, count, mapsAfter, offset)

    def customLevelSelect(self, transition=False):
        self.open = True
        self.levelSelectOpen = False
        self.customLevelSelectOpen = True
        self.backgroundColor = GREY  # Change this?
        self.setLevelSize(self.customLevelSize)
        cols = 4
        self.currentMaps = self.getArrangedMaps(self.customMaps, cols)

        self.setLevelSelectMaps(self.customMaps, cols, self.currentCustomLevel)
        self.setLevelsClickable(self.currentCustomLevel)

    def levelSelect(self, transition=False):
        self.open = True
        self.customLevelSelectOpen = False
        self.levelSelectOpen = True
        self.backgroundColor = BLACK
        self.levels = {}
        self.setLevelSize(self.builtInLevelSize)
        cols = len(self.builtInMaps)
        self.currentMaps = self.getArrangedMaps(self.builtInMaps, cols)

        mainMenu = Image(self, "button", (25, 25), ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing, 21))
        mainMenuText = Label(self, "Main Menu", 20, CREAM, ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing + 30, 27))
        
        custom = Image(self, "button", (25, 25), (mainMenuText.x + mainMenuText.getFontSize()[0] + 10, 21))
        customText = Label(self, "Custom Levels", 20, CREAM, (mainMenuText.x + mainMenuText.getFontSize()[0] + 40, 27))

        self.levelComplete = Image(self, "buttonRed", (25, 25), ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing, config["graphics"]["displayHeight"] - 42))
        self.levelCompleteText = Label(self, "Level Incomplete", 20, CREAM, ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing + 30, config["graphics"]["displayHeight"] - 36))

        key = Image(self, "keyCream", (25, 25), (config["graphics"]["displayWidth"] - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) - self.spacing - 75, 21))
        keyTextBackground = Rectangle(self, CREAM, (40, 25), (config["graphics"]["displayWidth"] - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) - self.spacing - 40, 21), shapeBorderRadius = [5, 5, 5, 5])
        self.keyText = Label(self, str(config["player"]["keys"]), 20, BLACK, (config["graphics"]["displayWidth"] - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) - self.spacing - 20, 27))
        self.keyText.setPos((self.keyText.x - (self.keyText.getFontSize()[0] / 2), self.keyText.y))

        levelNext = Image(self, "buttonArrowRight", (25, 25), (config["graphics"]["displayWidth"] - ((config["graphics"]["displayWidth"] - self.levelWidth) / 2) - self.spacing - 25, config["graphics"]["displayHeight"] - 42))
        levelBack = Image(self, "buttonArrowLeft", (25, 25), (levelNext.x - 25 - 10, config["graphics"]["displayHeight"] - 42))

        mainMenu.addEvent(hoverImage, 'onMouseOver', image = "buttonSelected")
        mainMenu.addEvent(hoverImage, 'onMouseOut', image = "button")
        custom.addEvent(hoverImage, 'onMouseOver', image = "buttonSelected")
        custom.addEvent(hoverImage, 'onMouseOut', image = "button")
        levelNext.addEvent(hoverImage, 'onMouseOver', image = "buttonArrowRightSelected")
        levelNext.addEvent(hoverImage, 'onMouseOut', image = "buttonArrowRight")
        levelBack.addEvent(hoverImage, 'onMouseOver', image = "buttonArrowLeftSelected")
        levelBack.addEvent(hoverImage, 'onMouseOut', image = "buttonArrowLeft")

        mainMenu.addEvent(openMainMenu, 'onMouseClick')
        custom.addEvent(showCustomLevelSelect, 'onMouseClick')
        mainMenuText.addEvent(openMainMenu, 'onMouseClick')

        levelNext.addEvent(levelForward, 'onMouseClick')
        levelBack.addEvent(levelBackward, 'onMouseClick')

        self.add(self.levelComplete)
        self.add(self.levelCompleteText)
        self.add(mainMenu)
        self.add(mainMenuText)
        self.add(custom)
        self.add(customText)
        self.add(key)
        self.add(keyTextBackground)
        self.add(self.keyText)
        self.add(levelNext)
        self.add(levelBack)

        # Add the maps after eveything else in the menu has been loaded
        self.setLevelSelectMaps(self.builtInMaps, cols, self.currentLevel)
        self.setLevelsClickable(self.currentLevel)

        if transition:
            # set the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                menu.remove(obj)
        
            self.slideTransitionY((0, 0), 'second', callback = callback)


class OptionMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    def closeTransition(self):
        self.game.spriteRenderer.getHud().setOpen(True)
        # self.game.mapEditor.getMessageSystem().setOpen(True)
        self.game.mapEditor.getHud().setOpen(True)

        def callback(obj, menu, y):
            menu.game.paused = False
            menu.close()

        for component in self.components:
            if transitionY not in component.getAnimations():
                component.addAnimation(transitionY, 'onLoad', speed = -40, transitionDirection = "up", y = -config["graphics"]["displayHeight"], callback = callback)


    def main(self, pausedSurface=True, transition=False):
        self.open = True
        
        self.game.paused = True
        self.game.spriteRenderer.getHud().setOpen(False)
        # self.game.mapEditor.getMessageSystem().setOpen(False) 
        self.game.mapEditor.getHud().setOpen(False)

        if pausedSurface:
            self.game.spriteRenderer.createPausedSurface()
            self.game.mapEditor.createPausedSurface()

        x = 100

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)

        paused = Label(self, "Paused", 70, Color("white"), (x, 100))

        options = Label(self, "Options", 50,  Color("white"), (x, 200))
        levelSelect = Label(self, "Level Selection", 50, Color("white"), (x, 260))
        mainMenu = Label(self, "Main Menu", 50, Color("white"), (x, 320))
        close = Label(self, "Close", 30, Color("white"), (x, 440))

        options.addEvent(showOptions, 'onMouseClick')
        options.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        options.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        levelSelect.addEvent(showLevelSelect, 'onMouseClick')
        levelSelect.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        levelSelect.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        mainMenu.addEvent(showMainMenu, 'onMouseClick')
        mainMenu.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        mainMenu.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        close.addEvent(unpause, 'onMouseClick')
        close.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        close.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        # background.add(paused)
        self.add(background)
        self.add(paused)
        self.add(options)
        self.add(levelSelect)
        self.add(mainMenu)
        self.add(close)

        if transition:
            def callback(obj, menu, y):
                obj.y = y

            for component in self.components:
                y = component.y
                component.setPos((component.x, component.y - config["graphics"]["displayHeight"]))
                component.addAnimation(transitionY, 'onLoad', speed = 40, transitionDirection = 'down', y = y, callback = callback)


    def options(self):
        self.open = True

        x = 100

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)

        options = Label(self, "Options", 70, Color("white"), (x, 100))

        graphics = Label(self, "Graphics", 50, Color("white"), (x, 200))
        controls = Label(self, "Controls", 50, Color("white"), (x, 260))
        back = Label(self, "Back", 30,  Color("white"), (x, 440))

        graphics.addEvent(showGraphics, 'onMouseClick')
        graphics.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        graphics.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        back.addEvent(showMain, 'onMouseClick')
        back.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        back.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        self.add(background)
        self.add(options)
        self.add(graphics)
        self.add(controls)
        self.add(back)


    def graphics(self):
        self.open = True

        x = 100

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)

        graphics = Label(self, "Graphics", 70, Color("white"), (x, 100))

        aliasText = "On" if config["graphics"]["antiAliasing"] else "Off"
        fullscreenText = "On" if self.game.fullscreen else "Off"
        scanlinesText = "On" if config["graphics"]["scanlines"]["enabled"] else "Off"
        scalingText = "Smooth" if config["graphics"]["smoothscale"] else "Harsh"
        vsyncText = "On" if config["graphics"]["vsync"] else "Off"

        # antiAlias = Label(self, "AntiAliasing: " + aliasText, 50, Color("white"), (x, 200))
        fullscreen = Label(self, "Fullscreen: " + fullscreenText, 50, Color("white"), (x, 200))
        scanlines = Label(self, "Scanlines: " + scanlinesText, 50, Color("white"), (x, 260))
        scaling = Label(self, "Scaling: " + scalingText, 50, Color("white"), (x, 320))
        vsync = Label(self, "Vsync: " + vsyncText, 50, Color("white"), (x + 500, 200))
        back = Label(self, "Back", 30,  Color("white"), (x, 440))

        fullscreen.addEvent(toggleFullscreen, 'onMouseClick')
        fullscreen.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        fullscreen.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        scanlines.addEvent(toggleScanlines, 'onMouseClick')
        scanlines.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        scanlines.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        scaling.addEvent(toggleScalingMode, 'onMouseClick')
        scaling.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        scaling.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))

        vsync.addEvent(toggleVsync, 'onMouseClick')
        vsync.addEvent(hoverOver, 'onMouseOver', x = x + 500 + 10, color = BLACK)
        vsync.addEvent(hoverOut, 'onMouseOut', x = x + 500, color = Color("white"))

        back.addEvent(showOptions, 'onMouseClick')
        back.addEvent(hoverOver, 'onMouseOver', x = x + 10, color = BLACK)
        back.addEvent(hoverOut, 'onMouseOut', x = x, color = Color("white"))
        
        self.add(background)
        self.add(graphics)
        self.add(fullscreen)
        self.add(scanlines)
        self.add(scaling)
        self.add(vsync)
        self.add(back)


class GameMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.startScreenOpen = False
        self.endScreenOpen = False


    def closeTransition(self):
        self.game.audioLoader.playSound("swoopOut")
        self.game.spriteRenderer.getHud().setOpen(True)

        def callback(obj, menu, x):
            menu.game.paused = False
            menu.game.spriteRenderer.getHud().slideHudIn()
            menu.game.spriteRenderer.gridLayer2.createPerson(menu.game.spriteRenderer.getAllDestination()) # add the first player
            menu.close()

        for component in self.components:
            component.addAnimation(transitionX, 'onLoad', speed = -40, transitionDirection = "right", x = -400, callback = callback)


    # Anything used by both the completed and game over end screens
    def endScreen(self):
        self.open = True
        self.endScreenOpen = True
        self.startScreenOpen = False

        self.game.paused = True
        self.game.spriteRenderer.getHud().setOpen(False)

        self.game.spriteRenderer.createPausedSurface()


    def endScreenGameOver(self, transition=False):
        self.endScreen()

        width = config["graphics"]["displayWidth"] / 2
        x = width - (width / 2)

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)
        failed = Label(self, "Level Failed!", 45, Color("white"), (((x + width) / 2 - 30), 100))
               
        scoreText = Label(self, "Highest Score", 25, Color("white"), (width - 87, 210))
        self.score = DifficultyMeter(self, YELLOW, Color("White"), 3, self.game.spriteRenderer.getLevelData()["score"], 5, (40, 40), (width - 50, scoreText.y + scoreText.getFontSize()[1] + 10), shapeBorderRadius = [5, 5, 5, 5])
        self.score.setPos((width - (self.score.getFullSize()[0] / 2), self.score.y))

        keyTextBackground = Rectangle(self, Color("white"), (60, 35), (width - 30, self.score.y + self.score.height + 30), shapeBorderRadius = [5, 5, 5, 5])
        self.keyText = Label(self, str(config["player"]["keys"]), 25, BLACK, (width - 20, keyTextBackground.y + 10))
        self.keyText.setPos((width - (self.keyText.getFontSize()[0] / 2), self.keyText.y))
        self.keyTextDifference = Label(self, "+0", 25, Color("white"), (keyTextBackground.x + keyTextBackground.width + 10, self.keyText.y))
        key = Image(self, "keyWhite", (35, 35), (keyTextBackground.x - 35 - 10, keyTextBackground.y))

        levelSelect = Label(self, "Level Selection", 25, Color("white"), ((width - 100), config["graphics"]["displayHeight"] - 100))
        levelSelect.setPos((width - (levelSelect.getFontSize()[0] / 2), levelSelect.y))
        retry = Label(self, "Retry", 25, Color("white"), (width - 100, levelSelect.y - 10))
        retry.setPos((width - (retry.getFontSize()[0] / 2), levelSelect.y - 20 - retry.getFontSize()[1]))

        levelSelect.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        levelSelect.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        levelSelect.addEvent(showLevelSelect, 'onMouseClick')

        retry.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        retry.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        retry.addEvent(loadLevel, 'onMouseClick', level = self.game.mapLoader.getMap(self.game.spriteRenderer.getLevel()))

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
            def callback(obj, menu, y):
                obj.y = y

            for component in self.components:
                y = component.y
                component.setPos((component.x, component.y - config["graphics"]["displayHeight"]))
                component.addAnimation(transitionY, 'onLoad', speed = 40, transitionDirection = 'down', y = y, callback = callback)

            self.game.audioLoader.playSound("swoopIn")    


    def endScreenComplete(self, transition=False):
        self.endScreen()
        self.game.spriteRenderer.setLevelComplete() # Complete the level
        previousKeys, self.keyDifference, self.previousScore = self.game.spriteRenderer.setLevelScore() # Set the score

        width = config["graphics"]["displayWidth"] / 2
        x = width - (width / 2)   
    
        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)
        success = Label(self, "Level Compelte!", 45, Color("white"), (((x + width) / 2 - 50), 100))
       
        scoreText = Label(self, "Highest Score", 25, Color("white"), (width - 87, 210))
        self.score = DifficultyMeter(self, YELLOW, Color("White"), 3, self.previousScore, 5, (40, 40), (width - 50, scoreText.y + scoreText.getFontSize()[1] + 10), shapeBorderRadius = [5, 5, 5, 5])
        self.score.setPos((width - (self.score.getFullSize()[0] / 2), self.score.y))

        keyTextBackground = Rectangle(self, Color("white"), (60, 35), (width - 30, self.score.y + self.score.height + 30), shapeBorderRadius = [5, 5, 5, 5])
        self.keyText = Label(self, str(previousKeys), 25, BLACK, (width - 20, keyTextBackground.y + 10))
        self.keyText.setPos((width - (self.keyText.getFontSize()[0] / 2), self.keyText.y))
        self.keyTextDifference = Label(self, "+" + str(self.keyDifference), 25, Color("white"), (keyTextBackground.x + keyTextBackground.width + 10, self.keyText.y))
        key = Image(self, "keyWhite", (35, 35), (keyTextBackground.x - 35 - 10, keyTextBackground.y))
        
        levelSelect = Label(self, "Level Selection", 25, Color("white"), ((width - 100), config["graphics"]["displayHeight"] - 100))
        levelSelect.setPos((width - (levelSelect.getFontSize()[0] / 2), levelSelect.y))
        retry = Label(self, "Retry", 25, Color("white"), (width - 100, levelSelect.y - 10))
        retry.setPos((width - (retry.getFontSize()[0] / 2), levelSelect.y - 20 - retry.getFontSize()[1]))

        levelSelect.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        levelSelect.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        levelSelect.addEvent(showLevelSelect, 'onMouseClick')

        retry.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        retry.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        retry.addEvent(loadLevel, 'onMouseClick', level = self.game.mapLoader.getMap(self.game.spriteRenderer.getLevel()))

        self.add(background)
        self.add(success)
        self.add(scoreText)
        self.add(self.score)
        self.add(key)
        self.add(keyTextBackground)
        self.add(self.keyText)
        self.add(self.keyTextDifference)
        self.add(levelSelect)
        self.add(retry)

        if transition:
            def callback(obj, menu, y):
                obj.y = y
                if menu.keyDifference > 0:
                    menu.keyText.addAnimation(increaseKeys, 'onLoad')
                    menu.keyTextDifference.addAnimation(decreaseKeys, 'onLoad')

                if menu.previousScore + menu.keyDifference > menu.previousScore:
                    menu.score.addAnimation(increaseMeter, 'onLoad', fromAmount = menu.previousScore, toAmount = menu.previousScore + self.keyDifference)
                

            for component in self.components:
                y = component.y
                component.setPos((component.x, component.y - config["graphics"]["displayHeight"]))
                component.addAnimation(transitionY, 'onLoad', speed = 40, transitionDirection = 'down', y = y, callback = callback)
    
            self.game.audioLoader.playSound("swoopIn")    


    def startScreen(self):
        self.open = True
        self.startScreenOpen = True
        self.endScreenOpen = False

        # show this before the game is unpaused so we don't need this
        self.game.paused = True
        self.game.spriteRenderer.getHud().setOpen(False)
        # self.game.mapEditor.getHud().setOpen(False)

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        totalText = "Transport " + str(self.game.spriteRenderer.getTotalToComplete()) + " people!"

        background = Rectangle(self, GREEN, (width, height), (x - 400, y))
        total = Label(self, totalText, 45, Color("white"), (((x + width) / 2 - 110) - 400, (y + height) / 2 + 20))
        play = Label(self, "Got it!", 25, Color("white"), (((config["graphics"]["displayWidth"] / 2) - 40) - 400, (config["graphics"]["displayHeight"] / 2) + 20))


        def callback(obj, menu, x):
            obj.x = x

        background.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = x, callback = callback)
        total.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = ((x + width) / 2 - 110), callback = callback)
        play.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = ((config["graphics"]["displayWidth"] / 2) - 40), callback = callback)

        play.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        play.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        play.addEvent(unpause, 'onMouseClick')

        self.add(background)
        self.add(total)
        self.add(play)

        self.game.audioLoader.playSound("swoopIn")    


# Anything that all the game huds will use
class GameHudLayout(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    @abc.abstractmethod
    def updateLayerText(self):
        return


    @abc.abstractmethod
    def setCompletedText(self):
        return


    @abc.abstractmethod
    def updateSlowDownMeter(self, amount):
        return


    @abc.abstractmethod
    def setLifeAmount(self):
        return


class GameHud(GameHudLayout):
    def __init__(self, renderer, spacing=(1.5, 1.5)):
        super().__init__(renderer)
        self.hearts = []
        self.spacing = spacing

        self.hudX = 15
        self.hudY = 15


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
        
        self.pause.addAnimation(transitionX, 'onLoad', speed = speed, transitionDirection = "left", x = self.hudX, callback = callbackX)
        self.layers.addAnimation(transitionX, 'onLoad', speed = speed, transitionDirection = "left", x = self.hudX, callback = callbackX)
        self.home.addAnimation(transitionX, 'onLoad', speed = speed, transitionDirection = "left", x = self.hudX, callback = callbackX)

        self.completed.addAnimation(transitionY, 'onLoad', speed = speed, transitionDirection = "down", y = self.hudY, callback = callbackY)
        self.completedAmount.addAnimation(transitionY, 'onLoad', speed = speed, transitionDirection = "down", y = self.hudY + 13, callback = callbackY)
        self.lives.addAnimation(transitionY, 'onLoad', speed = speed, transitionDirection = "down", y = self.hudY - 4, callback = callbackY)
        self.slowDownMeter.addAnimation(transitionY, 'onLoad', speed = speed, transitionDirection = "down", y = self.hudY + 10, callback = callbackY)


    def slideRestartIn(self):
        self.restart.dirty = True # Make sure its resized
        self.add(self.restart)

        def callback(obj, menu, x):
            obj.x = x

        self.restart.addAnimation(transitionX, 'onLoad', speed = 5, transitionDirection = "left", x = self.hudX, callback = callback)


    def slideRestartOut(self):
        def callback(obj, menu, x):
            obj.x = x
            menu.remove(obj)

        self.restart.addAnimation(transitionX, 'onLoad', speed = -5, transitionDirection = "right", x = self.hudX - 100, callback = callback)


    def togglePauseGame(self, selected = False):
        self.game.spriteRenderer.togglePaused() 

        pauseImage = "play" if self.game.spriteRenderer.getPaused() else "pause"
        pauseImageSelected = "playSelected" if self.game.spriteRenderer.getPaused() else "pauseSelected"
        pauseImage += "White" if self.game.spriteRenderer.getDarkMode() else ""
        self.slideRestartIn() if self.game.spriteRenderer.getPaused() else self.slideRestartOut()
        
        self.pause.setImageName(pauseImageSelected if selected else pauseImage)
        self.pause.clearEvents()
        self.pause.addEvent(hoverImage, 'onMouseOver', image = pauseImageSelected)
        self.pause.addEvent(hoverImage, 'onMouseOut', image = pauseImage)
        self.pause.addEvent(pauseGame, 'onMouseClick')
        self.pause.dirty = True

        
    def main(self, transition = False):
        self.open = True

        meterWidth = self.game.spriteRenderer.getSlowDownMeterAmount()
        levelData = self.game.spriteRenderer.getLevelData()
        darkMode = self.game.spriteRenderer.getDarkMode()

        layersImage = "layersWhite" if darkMode else "layers"
        layersSelectedImage = "layersSelected"
        homeImage = "homeWhite" if darkMode else "home"
        homeSelectedImage = "homeSelected"
        pauseImage = "pauseWhite" if darkMode else "pause"
        pauseSelectedImage = "pauseSelected"
        playImage = "playWhite" if darkMode else "play"
        playSelectedImage = "playSelected"
        walkingImage = "walkingWhite" if darkMode else "walking"
        restartImage = "restartWhite" if darkMode else "restart"
        restartSelectedImage = "restartSelected"
        self.textColor = Color("white") if darkMode else BLACK

        self.home = Image(self, homeImage, (50, 50), (self.hudX - 100, 500))
        self.layers = Image(self, layersImage, (50, 50), (self.hudX - 100, 440))
        self.pause = Image(self, pauseImage, (50, 50), (self.hudX - 100, 380))
        self.restart = Image(self, restartImage, (50, 50), (self.hudX - 100, 320))

        self.slowDownMeter = Meter(self, Color("white"), self.textColor, GREEN, (meterWidth, 20), (meterWidth, 20), (config["graphics"]["displayWidth"] - (100 + meterWidth), self.hudY + 10 - 100), 2)

        self.completed = Timer(self, self.textColor, YELLOW, 0, self.game.spriteRenderer.getTotalToComplete(), (40, 40), (config["graphics"]["displayWidth"] - 85, self.hudY - 100), 5)
        self.lives = Timer(self, self.textColor, GREEN, 100, self.game.spriteRenderer.getLives(), (48, 48), (config["graphics"]["displayWidth"] - 89, self.hudY - 4 - 100), 5)
        self.completedAmount = Label(self, str(self.game.spriteRenderer.getCompleted()), 20, self.textColor, (self.completed.x + 14.5, self.completed.y + 13)) 

        self.restart.addEvent(hoverImage, 'onMouseOver', image = restartSelectedImage)
        self.restart.addEvent(hoverImage, 'onMouseOut', image = restartImage)
        self.restart.addEvent(loadLevel, 'onMouseClick', level = self.game.mapLoader.getMap(self.game.spriteRenderer.getLevel()))

        self.pause.addEvent(hoverImage, 'onMouseOver', image = pauseSelectedImage)
        self.pause.addEvent(hoverImage, 'onMouseOut', image = pauseImage)
        self.pause.addEvent(pauseGame, 'onMouseClick')

        self.layers.addEvent(hoverImage, 'onMouseOver', image = layersSelectedImage)
        self.layers.addEvent(hoverImage, 'onMouseOut', image = layersImage)
        self.layers.addEvent(changeGameLayer, 'onMouseClick')

        self.home.addEvent(hoverImage, 'onMouseOver', image = homeSelectedImage)
        self.home.addEvent(hoverImage, 'onMouseOut', image = homeImage)
        self.home.addEvent(goHome, 'onMouseClick')

        self.add(self.home)
        if len(self.game.spriteRenderer.getConnectionTypes()) > 1: self.add(self.layers)
        else: 
            self.restart.setPos((self.pause.x, self.pause.y))
            self.pause.setPos((self.layers.x, self.layers.y))
        self.add(self.pause)

        self.add(self.slowDownMeter)
        self.add(self.lives)
        self.add(self.completed)
        self.add(self.completedAmount)

        if transition:
            # set the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                menu.game.spriteRenderer.runStartScreen()
                menu.remove(obj)
        
            self.slideTransitionY((0, 0), 'second', callback = callback)


    def setLifeAmount(self):
        if hasattr(self, 'lives'):
            def callback(obj, menu):
                if menu.game.spriteRenderer.getLives() <= 0:
                    menu.game.spriteRenderer.runEndScreen() # run end screen game over :(

            self.lives.addAnimation(increaseTimer, 'onLoad', speed = -0.2, finish = self.game.spriteRenderer.getLives() * self.lives.getStep(), direction = "backwards", callback = callback)


    def setCompletedAmount(self):
        if hasattr(self, 'completed'):
            def callback(obj, menu):
                if menu.game.spriteRenderer.getCompleted() >= menu.game.spriteRenderer.getTotalToComplete():
                    menu.game.spriteRenderer.runEndScreen(True) # run end screen game complete!

            self.completed.addAnimation(increaseTimer, 'onLoad', speed = 0.2, finish = self.game.spriteRenderer.getCompleted() * self.completed.getStep(), callback = callback)
            self.completedAmount.setText(str(self.game.spriteRenderer.getCompleted()))
            width, height = self.completedAmount.getFontSizeScaled()[0] / self.renderer.getScale(), self.completedAmount.getFontSizeScaled()[1] / self.renderer.getScale()
            self.completedAmount.setPos(((self.completed.x + (self.completed.width / 2)) - width / 2, ((self.completed.y + (self.completed.height / 2)) - height / 2) + 1))
            self.completedAmount.dirty = True


class EditorHud(GameHudLayout):
    def __init__(self, renderer):
        super().__init__(renderer)

        # Locations of each option
        self.fileLocation = 20
        self.textY = 12
        self.editLocation = self.fileLocation + 75 # 90
        self.addLocation = self.editLocation + 75 # 90
        self.deleteLocation = self.addLocation + 65 # 170
        self.runLocation = self.deleteLocation + 100 # 280


    def updateLayerText(self):
        if hasattr(self, 'currentLayer'):
            self.currentLayer.setText("layer " + str(self.game.mapEditor.getLayer()))


    def closeDropdowns(self):
        self.game.textHandler.setActive(False) # we always want to disable text inputs when we close the menus
        self.close()
        self.main()


    def main(self, transition = False):
        self.open = True
        self.fileDropdownOpen = False
        self.editDropdownOpen = False
        self.addDropdownOpen = False
        self.deleteDropdownOpen = False

        self.game.mapEditor.setAllowEdits(True)

        topbar = Rectangle(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))

        fileSelect = Label(self, "File", 25, Color("white"), (self.fileLocation, self.textY), BLACK)
        edit = Label(self, "Edit", 25, Color("white"), (self.editLocation, self.textY), BLACK)
        add = Label(self, "Add", 25, Color("white"), (self.addLocation, self.textY), BLACK)
        delete = Label(self, "Delete", 25, Color("white"), (self.deleteLocation, self.textY), BLACK)
        run = Label(self, "Run", 25, Color("white"), (self.runLocation, self.textY), BLACK)

        layers = Image(self, "layersWhite", (25, 25), (880, self.textY - 3))
        self.currentLayer = Label(self, "layer " + str(self.game.mapEditor.getLayer()), 25, Color("white"), (915, self.textY), BLACK)

        layers.addEvent(hoverImage, 'onMouseOver', image = "layersSelected")
        layers.addEvent(hoverImage, 'onMouseOut', image = "layersWhite")
        layers.addEvent(changeEditorLayer, 'onMouseClick')

        self.add(topbar)
        self.add(layers)
        self.add(self.currentLayer)

        fileSelect.addEvent(toggleFileDropdown, 'onMouseClick')
        edit.addEvent(toggleEditDropdown, 'onMouseClick')
        add.addEvent(toggleAddDropdown, 'onMouseClick')
        delete.addEvent(toggleDeleteDropdown, 'onMouseClick')
        run.addEvent(runMap, 'onMouseClick')

        labels = [fileSelect, edit, add, delete, run]
        for label in labels:
            label.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label)


        if transition:
            # Show the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                menu.remove(obj)
        
            self.slideTransitionY((0, 0), 'second', callback = callback)


    def editDropdown(self):
        self.open = True
        self.editDropdownOpen = True
        self.editSizeDropdownOpen = False

        self.game.mapEditor.setAllowEdits(False)

        box = Rectangle(self, BLACK, (200, 150), (self.editLocation, 40), 0, [0, 0, 10, 10])

        textX = self.editLocation + 10

        size = Label(self, "Map Size", 25, Color("white"), (textX, 50), BLACK)
        undo = Label(self, "Undo", 25, Color("white") if len(self.game.mapEditor.getLevelChanges()) > 1 else GREY, (textX, 85), BLACK)
        redo = Label(self, "Redo", 25, Color("white") if len(self.game.mapEditor.getPoppedLevelChanges()) >= 1 else GREY, (textX, 120), BLACK)
        
        self.add(box)

        size.addEvent(toggleEditSizeDropdown, 'onMouseClick')

        if len(self.game.mapEditor.getLevelChanges()) > 1:
            undo.addEvent(undoChange, 'onMouseClick')
            undo.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            undo.addEvent(hoverColor, 'onMouseOut', color = Color("white"))

        if len(self.game.mapEditor.getPoppedLevelChanges()) >= 1:
            redo.addEvent(redoChange, 'onMouseClick')
            redo.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            redo.addEvent(hoverColor, 'onMouseOut', color = Color("white"))

        labels = [size]
        for label in labels:
            label.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label)

        self.add(undo)
        self.add(redo)


    def editSizeDropdown(self):
        self.open = True
        self.editSizeDropdownOpen = True

        self.game.mapEditor.setAllowEdits(False)

        currentWidth = self.game.mapEditor.getLevelData()["width"]
        currentHeight = self.game.mapEditor.getLevelData()["height"]

        size0Selected = True if currentWidth == 16 and currentHeight == 9 else False
        size1Selected = True if currentWidth == 18 and currentHeight == 10 else False
        size2Selected = True if currentWidth == 20 and currentHeight == 11 else False
        size3Selected = True if currentWidth == 22 and currentHeight == 12 else False

        boxX = self.editLocation + 200
        textX = boxX + 10

        box = Rectangle(self, BLACK, (110, 150), (boxX, 85))
        size0Box = Rectangle(self, GREEN, (110, 33), (boxX, 90))
        size1Box = Rectangle(self, GREEN, (110, 33), (boxX, 126))
        size2Box = Rectangle(self, GREEN, (110, 33), (boxX, 161))
        size3Box = Rectangle(self, GREEN, (110, 33), (boxX, 195))

        size0 = Label(self, "16 x 9", 25, Color("white"), (textX, 95), GREEN if size0Selected else BLACK)
        size1 = Label(self, "18 x 10", 25, Color("white"), (textX, 130), GREEN if size1Selected else BLACK)
        size2 = Label(self, "20 x 11", 25, Color("white"), (textX, 165), GREEN if size2Selected else BLACK)
        size3 = Label(self, "22 x 12", 25, Color("white"), (textX, 200), GREEN if size3Selected else BLACK)

        size0.addEvent(setSize0, 'onMouseClick')
        size1.addEvent(setSize1, 'onMouseClick')
        size2.addEvent(setSize2, 'onMouseClick')
        size3.addEvent(setSize3, 'onMouseClick')

        self.add(box)
        if size0Selected: self.add(size0Box)
        elif size1Selected: self.add(size1Box)
        elif size2Selected: self.add(size2Box)
        elif size3Selected: self.add(size3Box)

        labels = [(size0, size0Selected), (size1, size1Selected), (size2, size2Selected), (size3, size3Selected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverColor, 'onMouseOver', color = BLACK)
            else:
                label[0].addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label[0].addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label[0])


    def addDropdown(self):
        self.open = True
        self.addDropdownOpen = True
        self.addStopDropdownOpen = False
        self.addTransportDropdownOpen = False
        self.addDestinationDropdownOpen = False

        self.game.mapEditor.setAllowEdits(False)

        clickType = self.game.mapEditor.getClickManager().getClickType()
        connectionSelected = True if clickType == EditorClickManager.ClickType.CONNECTION else False 
        stopSelected = True if clickType == EditorClickManager.ClickType.STOP else False 
        transportSelected = True if clickType == EditorClickManager.ClickType.TRANSPORT else False 
        destinationSelected = True if clickType == EditorClickManager.ClickType.DESTINATION else False

        box = Rectangle(self, BLACK, (200, 150), (self.addLocation, 40), 0, [0, 0, 10, 10])
        connectionBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 45))
        stopBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 81))
        transportBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 116))
        destinationBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 151))

        textX = self.addLocation + 10 # x position of text within box

        connection = Label(self, "Connection", 25, Color("white"), (textX, 50), GREEN if connectionSelected else BLACK)
        stop = Label(self, "Stop", 25, Color("white"), (textX, 85), GREEN if stopSelected else BLACK)
        transport = Label(self, "Transport", 25, Color("white"), (textX, 120), GREEN if transportSelected else BLACK)
        destination = Label(self, "Location", 25, Color("white"), (textX, 155), GREEN if destinationSelected else BLACK)

        connection.addEvent(addConnection, 'onMouseClick')
        stop.addEvent(toggleAddStopDropdown, 'onMouseClick')
        transport.addEvent(toggleAddTransportDropdown, 'onMouseClick')
        destination.addEvent(toggleAddDestinationDropdown, 'onMouseClick')

        self.add(box)
        if connectionSelected: self.add(connectionBox)
        elif stopSelected: self.add(stopBox)
        elif transportSelected: self.add(transportBox)
        elif destinationSelected: self.add(destinationBox)

        labels = [(connection, connectionSelected), (stop, stopSelected), (transport, transportSelected), (destination, destinationSelected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverColor, 'onMouseOver', color = BLACK)
            else:
                label[0].addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label[0].addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label[0])


    def addStopDropdown(self):
        self.open = True
        self.addStopDropdownOpen = True

        self.game.mapEditor.setAllowEdits(False)

        addType = self.game.mapEditor.getClickManager().getAddType()
        metroSelected = True if addType == "metro" else False
        busSelected = True if addType == "bus" else False
        tramSelected = True if addType == "tram" else False

        boxX = self.addLocation + 200
        textX = boxX + 10

        box = Rectangle(self, BLACK, (200, 114), (boxX, 85))
        metroBox = Rectangle(self, GREEN, (200, 33), (boxX, 90))
        busBox = Rectangle(self, GREEN, (200, 33), (boxX, 126))
        tramBox = Rectangle(self, GREEN, (200, 33), (boxX, 161))

        metroStation = Label(self, "Metro Station", 25, Color("white"), (textX, 95), GREEN if metroSelected else BLACK)
        busStop = Label(self, "Bus Stop", 25, Color("white"), (textX, 130), GREEN if busSelected else BLACK)
        tramStop = Label(self, "Tram Stop", 25, Color("white"), (textX, 165), GREEN if tramSelected else BLACK)

        self.add(box)
        if metroSelected: self.add(metroBox)
        elif busSelected: self.add(busBox)
        elif tramSelected: self.add(tramBox)

        metroStation.addEvent(addMetro, 'onMouseClick')
        busStop.addEvent(addBus, 'onMouseClick')
        tramStop.addEvent(addTram, 'onMouseClick')

        labels = [(metroStation, metroSelected), (busStop, busSelected), (tramStop, tramSelected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverColor, 'onMouseOver', color = BLACK)
            else:
                label[0].addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label[0].addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label[0])


    def addTransportDropdown(self):
        self.open = True
        self.addTransportDropdownOpen = True

        self.game.mapEditor.setAllowEdits(False)

        addType = self.game.mapEditor.getClickManager().getAddType()
        metroSelected = True if addType == "metro" else False
        busSelected = True if addType == "bus" else False
        tramSelected = True if addType == "tram" else False
        taxiSelected = True if addType == "taxi" else False

        boxX = self.addLocation + 200
        textX = boxX + 10

        box = Rectangle(self, BLACK, (110, 150), (boxX, 120))
        metroBox = Rectangle(self, GREEN, (110, 33), (boxX, 125))
        busBox = Rectangle(self, GREEN, (110, 33), (boxX, 161))
        tramBox = Rectangle(self, GREEN, (110, 33), (boxX, 196))
        taxiBox = Rectangle(self, GREEN, (110, 33), (boxX, 231))

        metro = Label(self, "Metro", 25, Color("white"), (textX, 130), GREEN if metroSelected else BLACK)
        bus = Label(self, "Bus", 25, Color("white"), (textX, 165), GREEN if busSelected else BLACK)
        tram = Label(self, "Tram", 25, Color("white"), (textX, 200), GREEN if tramSelected else BLACK)
        taxi = Label(self, "Taxi", 25, Color("white"), (textX, 235), GREEN if taxiSelected else BLACK)

        self.add(box)
        if metroSelected: self.add(metroBox)
        elif busSelected: self.add(busBox)
        elif tramSelected: self.add(tramBox)
        elif taxiSelected: self.add(taxiBox)

        metro.addEvent(addMetro, 'onMouseClick')
        bus.addEvent(addBus, 'onMouseClick')
        tram.addEvent(addTram, 'onMouseClick')
        taxi.addEvent(addTaxi, 'onMouseClick')

        labels = [(metro, metroSelected), (bus, busSelected), (tram, tramSelected), (taxi, taxiSelected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverColor, 'onMouseOver', color = BLACK)
            else:
                label[0].addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label[0].addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label[0])


    def addDestinationDropdown(self):
        self.open = True
        self.addDestinationDropdownOpen = True

        self.game.mapEditor.setAllowEdits(False)

        addType = self.game.mapEditor.getClickManager().getAddType()
        airportSelected = True if addType == 'airport' else False
        officeSelected = True if addType == 'office' else False
        houseSelected = True if addType == 'house' else False
        # TO DO: Add other types of transportation    

        boxX = self.addLocation + 200
        textX = boxX + 10

        box = Rectangle(self, BLACK, (200, 114), (boxX, 155))
        airportBox = Rectangle(self, GREEN, (200, 33), (boxX, 160))
        officeBox = Rectangle(self, GREEN, (200, 33), (boxX, 196))
        houseBox = Rectangle(self, GREEN, (200, 33), (boxX, 228))
        
        airport = Label(self, "Airport", 25, Color("white"), (textX, 165), GREEN if airportSelected else BLACK)
        office = Label(self, "Office", 25, Color("white"), (textX, 200), GREEN if officeSelected else BLACK)
        house = Label(self, "House", 25, Color("white"), (textX, 233), GREEN if houseSelected else BLACK)

        self.add(box)
        if airportSelected: self.add(airportBox)
        elif officeSelected: self.add(officeBox)
        elif houseSelected: self.add(houseBox)

        airport.addEvent(addAirport, 'onMouseClick')
        office.addEvent(addOffice, 'onMouseClick')
        house.addEvent(addHouse, 'onMouseClick')

        labels = [(airport, airportSelected), (office, officeSelected), (house, houseSelected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverColor, 'onMouseOver', color = BLACK)
            else:
                label[0].addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label[0].addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label[0])


    def deleteDropdown(self):
        self.open = True
        self.deleteDropdownOpen = True

        self.game.mapEditor.setAllowEdits(False)

        clickType = self.game.mapEditor.getClickManager().getClickType()
        connectionSelected = True if clickType == EditorClickManager.ClickType.DCONNECTION else False 
        stopSelected = True if clickType == EditorClickManager.ClickType.DSTOP else False 
        transportSelected = True if clickType == EditorClickManager.ClickType.DTRANSPORT else False
        destinationSelected = True if clickType == EditorClickManager.ClickType.DDESTINATION else False

        box = Rectangle(self, BLACK, (200, 150), (self.deleteLocation, 40), 0, [0, 0, 10, 10])
        connectionBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 45))
        stopBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 81))
        transportBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 116))
        destinationBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 151))

        textX = self.deleteLocation + 10

        connection = Label(self, "Connection", 25, Color("white"), (textX, 50), GREEN if connectionSelected else BLACK)
        stop = Label(self, "Stop", 25, Color("white"), (textX, 85), GREEN if stopSelected else BLACK)
        transport = Label(self, "Transport", 25, Color("white"), (textX, 120), GREEN if transportSelected else BLACK)
        destination = Label(self, "Destination", 25, Color("white"), (textX, 155), GREEN if destinationSelected else BLACK)

        connection.addEvent(deleteConnection, 'onMouseClick')
        stop.addEvent(deleteStop, 'onMouseClick')
        transport.addEvent(deleteTransport, 'onMouseClick')
        destination.addEvent(deleteDestination, 'onMouseClick')

        self.add(box)
        if connectionSelected: self.add(connectionBox)
        elif stopSelected: self.add(stopBox)
        elif transportSelected: self.add(transportBox)
        elif destinationSelected: self.add(destinationBox)

        labels = [(connection, connectionSelected), (stop, stopSelected), (transport, transportSelected), (destination, destinationSelected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverColor, 'onMouseOver', color = BLACK)
            else:
                label[0].addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label[0].addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label[0])


    def fileDropdown(self):
        self.open = True
        self.fileDropdownOpen = True
        self.saveBoxOpen = False
        self.loadBoxOpen = False
        self.confirmBoxOpen = False

        self.game.mapEditor.setAllowEdits(False)

        box = Rectangle(self, BLACK, (130, 220), (self.fileLocation, 40), 0, [0, 0, 10, 10])

        textX = self.fileLocation + 10
        
        new = Label(self, "New", 25, Color("white"), (textX, 50), BLACK)
        load = Label(self, "Open", 25, Color("white"), (textX, 85), BLACK)
        save = Label(self, "Save", 25, Color("white") if self.game.mapEditor.getDeletable() else GREY, (textX, 120), BLACK) 
        saveAs = Label(self, "Save as", 25, Color("white") if self.game.mapEditor.getDeletable() else GREY, (textX, 155), BLACK)

        # Must be already saved and be a deletable map
        delete = Label(self, "Delete", 25, Color("white") if self.game.mapEditor.getSaved() and self.game.mapEditor.getDeletable() else GREY, (textX, 190), BLACK)
        close = Label(self, "Exit", 25, Color("white"), (textX, 225), BLACK)

        new.addEvent(newMap, 'onMouseClick')
        load.addEvent(toggleLoadDropdown, 'onMouseClick')
        close.addEvent(closeMapEditor, 'onMouseClick')

        if self.game.mapEditor.getDeletable():
            save.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            save.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            save.addEvent(toggleSaveBox, 'onMouseClick')
            saveAs.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            saveAs.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            saveAs.addEvent(toggleSaveAsBox, 'onMouseClick')

            if self.game.mapEditor.getSaved(): 
                delete.addEvent(hoverColor, 'onMouseOver', color = GREEN)
                delete.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
                delete.addEvent(toggleConfirmBox, 'onMouseClick')                   

        self.add(box)
        self.add(save)
        self.add(saveAs)
        self.add(delete)

        # Add each of the labels
        labels = [new, load, close]
        for label in labels:
            label.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            label.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            self.add(label)


    def loadDropdown(self):
        self.open = True
        self.loadBoxOpen = True

        self.game.mapEditor.setAllowEdits(False)

        boxX = self.fileLocation + 130
        textX = boxX + 10
        y = 95
        maxWidth = 130 # min width
        maps = []
        for mapName, path in self.game.mapLoader.getMaps().items():
            m = Label(self, mapName, 25, Color("white"), (textX, y), BLACK)
            m.addEvent(hoverColor, 'onMouseOver', color = GREEN)
            m.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
            m.addEvent(loadEditorMap, 'onMouseClick')
            if m.getFontSize()[0] > maxWidth:
                maxWidth = m.getFontSize()[0]
            maps.append(m)
            y += 30

        box = Rectangle(self, BLACK, (maxWidth + 20, 20 + (30 * len(self.game.mapLoader.getMaps()))), (boxX, 85))
        self.add(box)

        for m in maps:
            self.add(m)


    def saveBox(self):
        self.open = True
        self.saveBoxOpen = True

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        box = Rectangle(self, GREEN, (width, height), (x, y))
        title = Label(self, "Map name", 30, Color("white"), ((x + 20) - box.x, (y + 20) - box.y), GREEN)
        self.inputBox = Rectangle(self, Color("white"), (width - 40, 50), (x + 20, y + 80))
        mapName = InputBox(self, 30, BLACK, self.inputBox, self.inputBox.width - 50, (x + 40, y + 92)) # we pass through the background instead of defining it in the InputBox so we can customize it better (e.g with image ect)
        saveBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 120 - box.x, (y + height) - 70 - box.y))
        save = Label(self, "Save", 25, Color("white"), ((x + width) - 100, (y + height) - 55), BLACK)
        cancelBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 240 - box.x, (y + height) - 70 - box.y))
        cancel = Label(self, "Cancel", 23, Color("white"), ((x + width) - 229, (y + height) - 55), BLACK)

        self.inputBox.addEvent(hoverColor, 'onKeyPress', color = Color("white"))

        save.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        save.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        save.addEvent(saveMap, 'onMouseClick')

        cancel.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        cancel.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        cancel.addEvent(toggleSaveBox, 'onMouseClick')

        box.add(title)
        box.add(saveBox)
        box.add(cancelBox)
        self.add(box)
        self.add(self.inputBox)
        self.add(mapName)
        self.add(save)
        self.add(cancel)


    def confirmBox(self):
        self.open = True
        self.confirmBoxOpen = True

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        box = Rectangle(self, GREEN, (width, height), (x, y))
        title = Label(self, "Delete", 30, Color("white"), ((x + 20) - box.x, (y + 20) - box.y), GREEN)
        title.setUnderline(True)
        confirm1 = Label(self, "Are you sure you want to", 30, Color("white"), ((x + 40) - box.x, (y + 82) - box.y), GREEN)
        confirm2 = Label(self, "delete this map?", 30, Color("white"), ((x + 40) - box.x, (y + 115) - box.y), GREEN)

        confirmBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 120 - box.x, (y + height) - 70 - box.y))
        confirm = Label(self, "Yes", 25, Color("white"), ((x + width) - 93, (y + height) - 55), BLACK)
        cancelBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 240 - box.x, (y + height) - 70 - box.y))
        cancel = Label(self, "Cancel", 23, Color("white"), ((x + width) - 229, (y + height) - 55), BLACK)

        confirm.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        confirm.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        confirm.addEvent(deleteMap, 'onMouseClick')

        cancel.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        cancel.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        cancel.addEvent(toggleConfirmBox, 'onMouseClick')

        box.add(title)
        box.add(confirm1)
        box.add(confirm2)
        box.add(confirmBox)
        box.add(cancelBox)
        self.add(box)
        self.add(confirm)
        self.add(cancel)


class PreviewHud(GameHudLayout):
    def __init__(self, renderer, spacing):
        super().__init__(renderer)
        self.spacing = spacing


    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeter'):
            self.slowDownMeter.setAmount((amount, 20))
            self.slowDownMeter.dirty = True


    def main(self, transition = False):
        self.open = True

        meterWidth = self.game.spriteRenderer.getSlowDownMeterAmount()

        topbar = Rectangle(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        stop = Label(self, "Stop", 25, Color("white"), (20, 10), BLACK)
        self.slowDownMeter = Meter(self, Color("white"), Color("white"), GREEN, (meterWidth, 20), (meterWidth, 20), (config["graphics"]["displayWidth"] - (100 + meterWidth), 12), 2)
        completed = Image(self, "walkingWhite", (30, 30), (config["graphics"]["displayWidth"] - 68, 7))
        self.completedText = Label(self, str(self.game.spriteRenderer.getCompleted()), 25, Color("white"), (config["graphics"]["displayWidth"] - 40, 14), BLACK)   

        stop.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        stop.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        stop.addEvent(stopMap, 'onMouseClick')

        self.add(topbar)
        self.add(stop)
        self.add(self.slowDownMeter)
        self.add(completed)
        self.add(self.completedText)


    def setCompletedAmount(self):
        if hasattr(self, 'completedText'):
            self.completedText.setText(str(self.game.spriteRenderer.getCompleted()))
            self.completedText.dirty = True
        

class MessageHud(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.messages = []

    def addMessage(self, message):
        self.messages.append(message)

    def removeMessage(self, message):
        self.messages.remove(message)

    def addMessage(self, message):
        if message in self.messages:
            return

        messageBox = MessageBox(self, message, (25, 25))
        messageBox.addAnimation(transitionMessageDown, 'onLoad', speed = 4, transitionDirection = "down", y = messageBox.marginY)
        self.add(messageBox)
        messageBox.addMessages()
        self.messages.append(message)

        if sum(isinstance(component, MessageBox) for component in self.components) > 0:
            for component in self.components:
                if isinstance(component, MessageBox):
                    if transitionMessageDown not in component.getAnimations():
                        component.addAnimation(transitionMessageDown, 'onLoad', speed = 4, transitionDirection = "down", y = (component.y + messageBox.height) + component.marginY)

    def main(self):
        self.open = True
        