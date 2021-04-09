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

class Menu:
    def __init__(self, game):
        pygame.font.init()

        self.open = False
        self.game = game
        self.renderer = game.renderer
        self.components = []

        self.clicked = False

        self.loadingImage = Image(self, "loading1", (100, 72), ((config["graphics"]["displayWidth"] / 2) - 50, (config["graphics"]["displayHeight"] / 2) - 36))

    
    def setOpen(self, hudOpen):
        self.open = hudOpen


    def getOpen(self):
        return self.open


    def getComponents(self):
        return self.components


    def add(self, obj):
        self.components.append(obj)


    def remove(self, obj):
        if obj in self.components:
            self.components.remove(obj)
            del obj


    def clickButton(self):  
        click = random.randint(1, 2)
        self.game.audioLoader.playSound("click%i" % click)    


    def resize(self):
        for component in self.components:
            component.dirty = True # force redraw

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
        self.currentLevel = 0
        self.maps = list(self.game.mapLoader.getMaps().keys())
        self.levels = {}
        self.backgroundColor = GREEN

        scaler = 5 # larger scaler = larger image
        self.levelWidth = config["graphics"]["displayWidth"] - (config["graphics"]["displayWidth"] / scaler)
        self.levelHeight = config["graphics"]["displayHeight"] - (config["graphics"]["displayHeight"] / scaler)
        self.spacing = 20

        self.transitioning = False


    def getBackgroundColor(self):
        return self.backgroundColor


    def getLevels(self):
        return self.levels


    def getCurrentLevel(self):
        return self.currentLevel


    def getTransitioning(self):
        return self.transitioning

    
    def setTransitioning(self, transitioning):
        self.transitioning = transitioning


    def updateMaps(self):
        self.maps = list(self.game.mapLoader.getMaps().keys())

        if self.currentLevel >= len(self.maps):
            self.currentLevel = len(self.maps) - 1


    def main(self, transition = False):
        self.open = True
        self.levelSelectOpen = False
        self.backgroundColor = GREEN

        sidebar = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0))

        x = (config["graphics"]["displayWidth"] / 2) - 180

        title1 = Label(self, "Transport", 70, Color("white"), (x, 80))
        title2 = Label(self, "The", 30, Color("white"), (x, title1.y + 70))
        title3 = Label(self, "Public", 70, Color("white"), (x, title2.y + 30))

        title1.setItalic(True)
        title2.setItalic(True)
        title3.setItalic(True)

        cont = Label(self, "Continue", 50,  BLACK, (x, 290))
        editor = Label(self, "Level editor", 50, BLACK, (x, cont.y + 60))
        options = Label(self, "Options", 50, BLACK, (x, editor.y + 60))
        end = Label(self, "Quit", 50, BLACK, (x, options.y + 60))


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


    def increaseCurrentLevel(self):
        if self.currentLevel < len(self.maps) - 1:
            self.currentLevel += 1
            return True
        return False


    def decreaseCurrentLevel(self):
        if self.currentLevel > 0:
            self.currentLevel -= 1
            return True
        return False


    def createLevel(self, levelInt, offset):
        if levelInt >= 0 and levelInt < len(self.maps):
            level = Map(self, self.maps[levelInt], levelInt, (self.levelWidth, self.levelHeight), ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + offset, (config["graphics"]["displayHeight"] - self.levelHeight) / 2))
            self.add(level)
            self.levels[levelInt] = level        

            # Update the loading screen when the level has loaded
            self.updateLoadingScreen()


    def setLevelsClickable(self):
        for index, level in self.levels.items():
            if index == self.currentLevel:
                # if the level is not locked make clicking it load the map
                level.removeEvent(levelForward, 'onMouseClick')
                level.removeEvent(levelBackward, 'onMouseClick')

                if not level.getLevelData()["locked"]:
                    level.addEvent(loadLevel, 'onMouseClick', level = level.getLevel())

                if self.currentLevel < len(self.levels) - 1:
                    self.levels[index + 1].removeEvent(levelForward, 'onMouseClick')
                    self.levels[index + 1].removeEvent(levelBackward, 'onMouseClick')
                    self.levels[index + 1].addEvent(levelForward, 'onMouseClick')
                if self.currentLevel > 0:
                    self.levels[index - 1].removeEvent(levelForward, 'onMouseClick')
                    self.levels[index - 1].removeEvent(levelBackward, 'onMouseClick')
                    self.levels[index - 1].addEvent(levelBackward, 'onMouseClick')

                # Set the completed button
                text = "Level Complete!" if level.getLevelData()["completion"]["completed"] else "Level Incomplete"
                image = "buttonGreen" if level.getLevelData()["completion"]["completed"] else "buttonRed"
                self.levelCompleteText.setText(text)
                self.levelComplete.setImageName(image)
                self.levelCompleteText.dirty = True
                self.levelComplete.dirty = True
            else:
                # Remove click event
                level.removeEvent(loadLevel, 'onMouseClick', level = level.getLevel())


    def levelSelect(self, transition = False):
        self.open = True
        self.levelSelectOpen = True
        # self.backgroundColor = (128, 128, 128)
        self.backgroundColor = BLACK
        self.levels = {}

        back = Image(self, "button", (25, 25), ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing, 21))
        backText = Label(self, "Main Menu", 20, CREAM, ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing + 30, 27))
        
        custom = Image(self, "button", (25, 25), (backText.x + backText.getFontSize()[0] + 10, 21))
        customText = Label(self, "Custom Levels", 20, CREAM, (backText.x + backText.getFontSize()[0] + 40, 27))

        self.levelComplete = Image(self, "buttonRed", (25, 25), ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing, config["graphics"]["displayHeight"] - 42))
        self.levelCompleteText = Label(self, "Level Incomplete", 20, CREAM, ((config["graphics"]["displayWidth"] - self.levelWidth) / 2 + self.spacing + 30, config["graphics"]["displayHeight"] - 36))

        back.addEvent(hoverImage, 'onMouseOver', image = "buttonSelected")
        back.addEvent(hoverImage, 'onMouseOut', image = "button")
        custom.addEvent(hoverImage, 'onMouseOver', image = "buttonSelected")
        custom.addEvent(hoverImage, 'onMouseOut', image = "button")

        back.addEvent(openMainMenu, 'onMouseClick')
        backText.addEvent(openMainMenu, 'onMouseClick')

        self.add(self.levelComplete)
        self.add(self.levelCompleteText)
        self.add(back)
        self.add(backText)
        self.add(custom)
        self.add(customText)


        #### Adds the maps after eveything else in the menu has been loaded

        # Load levels before current level
        for i, level in enumerate(reversed(self.maps[:self.currentLevel])):
            self.createLevel(self.currentLevel - (i + 1), -((self.levelWidth + self.spacing) * (i +1)))
        
        # Load current level and levels after current level
        for i, level in enumerate(self.maps[self.currentLevel:]):
            self.createLevel(self.currentLevel + i, (self.levelWidth + self.spacing) * i)

        self.setLevelsClickable()


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


    def main(self, pausedSurface = True, transition = False):
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
        mainMenu = Label(self, "Main Menu", 50, Color("white"), (x, 260))
        close = Label(self, "Close", 30, Color("white"), (x, 440))

        options.addEvent(showOptions, 'onMouseClick')
        options.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        options.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        mainMenu.addEvent(showLevelSelect, 'onMouseClick')
        mainMenu.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        mainMenu.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        close.addEvent(unpause, 'onMouseClick')
        close.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        close.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        self.add(background)
        self.add(paused)
        self.add(options)
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

        graphics = Label(self, "Graphics", 50, Color("white"), (x, 200))
        controls = Label(self, "Controls", 50, Color("white"), (x, 260))
        back = Label(self, "Back", 30,  Color("white"), (x, 440))

        graphics.addEvent(showGraphics, 'onMouseClick')
        graphics.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        graphics.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        back.addEvent(showMain, 'onMouseClick')
        back.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        back.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        self.add(background)
        self.add(graphics)
        self.add(controls)
        self.add(back)


    def graphics(self):
        self.open = True

        x = 100

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)

        aliasText = "On" if config["graphics"]["antiAliasing"] else "Off"
        fullscreenText = "On" if self.game.fullscreen else "Off"
        scanlinesText = "On" if config["graphics"]["scanlines"]["enabled"] else "Off"

        antiAlias = Label(self, "AntiAliasing: " + aliasText, 50, Color("white"), (x, 200))
        fullscreen = Label(self, "Fullscreen: " + fullscreenText, 50, Color("white"), (x, 260))
        scanlines = Label(self, "Scanlines: " + scanlinesText, 50, Color("white"), (x, 320))
        back = Label(self, "Back", 30,  Color("white"), (x, 440))

        antiAlias.addEvent(toggleAlias, 'onMouseClick')
        antiAlias.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        antiAlias.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        fullscreen.addEvent(toggleFullscreen, 'onMouseClick')
        fullscreen.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        fullscreen.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        scanlines.addEvent(toggleScanlines, 'onMouseClick')
        scanlines.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        scanlines.addEvent(hoverOut, 'onMouseOut', color = Color("white"))

        back.addEvent(showOptions, 'onMouseClick')
        back.addEvent(hoverOver, 'onMouseOver', color = BLACK)
        back.addEvent(hoverOut, 'onMouseOut', color = Color("white"))
        
        self.add(background)
        self.add(antiAlias)
        self.add(fullscreen)
        self.add(scanlines)
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
            menu.game.spriteRenderer.gridLayer2.addPerson(menu.game.spriteRenderer.getAllDestination()) # add the first player
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


    def endScreenGameOver(self):
        self.endScreen()

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)
        text = Label(self, "Level Failed!", 45, Color("white"), (((x + width) / 2 - 30), (y + height) / 2 + 20))
        ok = Label(self, "Level Selection", 25, Color("white"), (((config["graphics"]["displayWidth"] / 2) - 110), (config["graphics"]["displayHeight"] / 2) + 20))

        ok.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        ok.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        ok.addEvent(showLevelSelect, 'onMouseClick')


        self.add(background)
        self.add(text)
        self.add(ok)
    

    def endScreenComplete(self):
        self.endScreen()
        self.game.spriteRenderer.setLevelComplete() # Complete the level
        self.game.spriteRenderer.setLevelScore() # Set the score

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        background = Rectangle(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), alpha = 150)
        text = Label(self, "Level Compelte!", 45, Color("white"), (((x + width) / 2 - 50), (y + height) / 2 + 20))
        ok = Label(self, "Level Selection", 25, BLACK, (((config["graphics"]["displayWidth"] / 2) - 110), (config["graphics"]["displayHeight"] / 2) + 20))

        ok.addEvent(hoverColor, 'onMouseOver', color = Color("white"))
        ok.addEvent(hoverColor, 'onMouseOut', color = BLACK)
        ok.addEvent(showLevelSelect, 'onMouseClick')


        self.add(background)
        self.add(text)
        self.add(ok)


    def startScreen(self, transition = False):
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

        background = Rectangle(self, GREEN, (width, height), (x - config["graphics"]["displayWidth"], y))
        total = Label(self, totalText, 45, Color("white"), (((x + width) / 2 - 110) - config["graphics"]["displayWidth"], (y + height) / 2 + 20))
        play = Label(self, "Got it!", 25, Color("white"), (((config["graphics"]["displayWidth"] / 2) - 40) - config["graphics"]["displayWidth"], (config["graphics"]["displayHeight"] / 2) + 20))


        def callback(obj, menu, x):
            obj.x = x

        # background.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = x, callback = callback)
        # total.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = ((x + width) / 2 - 110), callback = callback)
        # play.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = ((config["graphics"]["displayWidth"] / 2) - 40), callback = callback)

        play.addEvent(hoverColor, 'onMouseOver', color = BLACK)
        play.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        play.addEvent(unpause, 'onMouseClick')

        self.add(background)
        self.add(total)
        self.add(play)

        self.game.audioLoader.playSound("swoopIn")    

        if transition:
            # set the up transition
            def callback(obj, menu, animation):
                obj.removeAnimation(animation)
                # menu.game.spriteRenderer.runStartScreen()
                menu.animateX()
                menu.remove(obj)
        
            self.slideTransitionY((0, 0), 'second', callback = callback)


    def animateX(self):
        def callback(obj, menu, x):
            obj.x = x

        for component in self.components:
            component.addAnimation(transitionX, 'onLoad', speed = 60, transitionDirection = 'left', x = component.x + config["graphics"]["displayWidth"], callback = callback)


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

    

class GameHud(GameHudLayout):
    def __init__(self, renderer, spacing = (1.5, 1.5)):
        super().__init__(renderer)
        self.hearts = []
        self.spacing = spacing

    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeterAmount'):
            self.slowDownMeterAmount.setSize((amount, 20))
            self.slowDownMeterAmount.dirty = True


    def main(self, transition = False):
        self.open = True

        hudX = 15
        hudY = 15

        meterWidth = self.game.spriteRenderer.getSlowDownMeterAmount()
        levelData = self.game.spriteRenderer.getLevelData()
        darkMode = self.game.spriteRenderer.getDarkMode()

        layersImage = "layersWhite" if darkMode else "layers"
        layersSelectedImage = "layersSelected"
        homeImage = "homeWhite" if darkMode else "home"
        homeSelectedImage = "homeSelected"
        walkingImage = "walkingWhite" if darkMode else "walking"
        self.textColor = Color("white") if darkMode else BLACK

        home = Image(self, homeImage, (50, 50), (hudX, 500))
        layers = Image(self, layersImage, (50, 50), (hudX, 440))
        slowDownMeter = Rectangle(self, Color("white"), (meterWidth, 20), (config["graphics"]["displayWidth"] - (100 + meterWidth), hudY + 10))
        slowDownMeterOutline = Rectangle(self, self.textColor, (meterWidth, 20), (config["graphics"]["displayWidth"] - (100 + meterWidth), hudY + 10), 2)
        self.slowDownMeterAmount = Rectangle(self, GREEN, (meterWidth, 20), (config["graphics"]["displayWidth"] - (100 + meterWidth), hudY + 10))

        self.completed = Timer(self, self.textColor, YELLOW, 0, self.game.spriteRenderer.getTotalToComplete(), (40, 40), (config["graphics"]["displayWidth"] - 85, hudY), 5)
        self.lives = Timer(self, self.textColor, GREEN, 100, self.game.spriteRenderer.getLives(), (48, 48), (config["graphics"]["displayWidth"] - 89, hudY - 4), 5)
        self.completedAmount = Label(self, str(self.game.spriteRenderer.getCompleted()), 20, self.textColor, (self.completed.x + 14.5, self.completed.y + 13)) 

        layers.addEvent(hoverLayers, 'onMouseOver', image = layersSelectedImage)
        layers.addEvent(hoverLayers, 'onMouseOut', image = layersImage)
        layers.addEvent(changeGameLayer, 'onMouseClick')

        home.addEvent(hoverHome, 'onMouseOver', image = homeSelectedImage)
        home.addEvent(hoverHome, 'onMouseOut', image = homeImage)
        home.addEvent(goHome, 'onMouseClick')

        self.add(home)

        if len(self.game.spriteRenderer.getConnectionTypes()) > 1:
            self.add(layers)

        self.add(slowDownMeter)
        self.add(self.slowDownMeterAmount)
        self.add(slowDownMeterOutline)
        self.add(self.lives)
        self.add(self.completed)
        self.add(self.completedAmount)


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

        fileSelect = Label(self, "File", 25, Color("white"), (self.fileLocation, self.textY))
        edit = Label(self, "Edit", 25, Color("white"), (self.editLocation, self.textY))
        add = Label(self, "Add", 25, Color("white"), (self.addLocation, self.textY))
        delete = Label(self, "Delete", 25, Color("white"), (self.deleteLocation, self.textY))
        run = Label(self, "Run", 25, Color("white"), (self.runLocation, self.textY))

        layers = Image(self, "layersWhite", (25, 25), (880, self.textY - 3))
        self.currentLayer = Label(self, "layer " + str(self.game.mapEditor.getLayer()), 25, Color("white"), (915, self.textY))

        layers.addEvent(hoverLayers, 'onMouseOver', image = "layersSelected")
        layers.addEvent(hoverLayers, 'onMouseOut', image = "layersWhite")
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

        size = Label(self, "Map Size", 25, Color("white"), (textX, 50))
        undo = Label(self, "Undo", 25, Color("white") if len(self.game.mapEditor.getLevelChanges()) > 1 else GREY, (textX, 85))
        redo = Label(self, "Redo", 25, Color("white") if len(self.game.mapEditor.getPoppedLevelChanges()) >= 1 else GREY, (textX, 120))
        
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

        size0 = Label(self, "16 x 9", 25, Color("white"), (textX, 95))
        size1 = Label(self, "18 x 10", 25, Color("white"), (textX, 130))
        size2 = Label(self, "20 x 11", 25, Color("white"), (textX, 165))
        size3 = Label(self, "22 x 12", 25, Color("white"), (textX, 200))

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
        stopSelectd = True if clickType == EditorClickManager.ClickType.STOP else False 
        transportSelected = True if clickType == EditorClickManager.ClickType.TRANSPORT else False 
        destinationSelected = True if clickType == EditorClickManager.ClickType.DESTINATION else False

        box = Rectangle(self, BLACK, (200, 150), (self.addLocation, 40), 0, [0, 0, 10, 10])
        connectionBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 45))
        stopBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 81))
        transportBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 116))
        destinationBox = Rectangle(self, GREEN, (200, 33), (self.addLocation, 151))

        textX = self.addLocation + 10 # x position of text within box

        connection = Label(self, "Connection", 25, Color("white"), (textX, 50))
        stop = Label(self, "Stop", 25, Color("white"), (textX, 85))
        transport = Label(self, "Transport", 25, Color("white"), (textX, 120))
        destination = Label(self, "Location", 25, Color("white"), (textX, 155))

        connection.addEvent(addConnection, 'onMouseClick')
        stop.addEvent(toggleAddStopDropdown, 'onMouseClick')
        transport.addEvent(toggleAddTransportDropdown, 'onMouseClick')
        destination.addEvent(toggleAddDestinationDropdown, 'onMouseClick')

        self.add(box)
        if connectionSelected: self.add(connectionBox)
        elif stopSelectd: self.add(stopBox)
        elif transportSelected: self.add(transportBox)
        elif destinationSelected: self.add(destinationBox)

        labels = [(connection, connectionSelected), (stop, stopSelectd), (transport, transportSelected), (destination, destinationSelected)]
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

        metroStation = Label(self, "Metro Station", 25, Color("white"), (textX, 95))
        busStop = Label(self, "Bus Stop", 25, Color("white"), (textX, 130))
        tramStop = Label(self, "Tram Stop", 25, Color("white"), (textX, 165))

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

        metro = Label(self, "Metro", 25, Color("white"), (textX, 130))
        bus = Label(self, "Bus", 25, Color("white"), (textX, 165))
        tram = Label(self, "Tram", 25, Color("white"), (textX, 200))
        taxi = Label(self, "Taxi", 25, Color("white"), (textX, 235))

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
        
        airport = Label(self, "Airport", 25, Color("white"), (textX, 165))
        office = Label(self, "Office", 25, Color("white"), (textX, 200))
        house = Label(self, "House", 25, Color("white"), (textX, 233))

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
        stopSelectd = True if clickType == EditorClickManager.ClickType.DSTOP else False 
        transportSelected = True if clickType == EditorClickManager.ClickType.DTRANSPORT else False
        destinationSelected = True if clickType == EditorClickManager.ClickType.DDESTINATION else False

        box = Rectangle(self, BLACK, (200, 150), (self.deleteLocation, 40), 0, [0, 0, 10, 10])
        connectionBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 45))
        stopBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 81))
        transportBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 116))
        destinationBox = Rectangle(self, GREEN, (200, 33), (self.deleteLocation, 151))

        textX = self.deleteLocation + 10

        connection = Label(self, "Connection", 25, Color("white"), (textX, 50))
        stop = Label(self, "Stop", 25, Color("white"), (textX, 85))
        transport = Label(self, "Transport", 25, Color("white"), (textX, 120))
        destination = Label(self, "Destination", 25, Color("white"), (textX, 155))

        connection.addEvent(deleteConnection, 'onMouseClick')
        stop.addEvent(deleteStop, 'onMouseClick')
        transport.addEvent(deleteTransport, 'onMouseClick')
        destination.addEvent(deleteDestination, 'onMouseClick')

        self.add(box)
        if connectionSelected: self.add(connectionBox)
        elif stopSelectd: self.add(stopBox)
        elif transportSelected: self.add(transportBox)
        elif destinationSelected: self.add(destinationBox)

        labels = [(connection, connectionSelected), (stop, stopSelectd), (transport, transportSelected), (destination, destinationSelected)]
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
        
        new = Label(self, "New", 25, Color("white"), (textX, 50))
        load = Label(self, "Open", 25, Color("white"), (textX, 85))
        save = Label(self, "Save", 25, Color("white") if self.game.mapEditor.getDeletable() else GREY, (textX, 120)) 
        saveAs = Label(self, "Save as", 25, Color("white") if self.game.mapEditor.getDeletable() else GREY, (textX, 155))

        # Must be already saved and be a deletable map
        delete = Label(self, "Delete", 25, Color("white") if self.game.mapEditor.getSaved() and self.game.mapEditor.getDeletable() else GREY, (textX, 190))
        close = Label(self, "Exit", 25, Color("white"), (textX, 225))

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
            m = Label(self, mapName, 25, Color("white"), (textX, y))
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
        title = Label(self, "Map name", 30, Color("white"), (x + 20, y + 20))
        self.inputBox = Rectangle(self, Color("white"), (width - 40, 50), (x + 20, y + 80))
        mapName = InputBox(self, 30, BLACK, self.inputBox, self.inputBox.width - 50, (x + 40, y + 92)) # we pass through the background instead of defining it in the InputBox so we can customize it better (e.g with image ect)
        saveBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 120, (y + height) - 70))
        save = Label(self, "Save", 25, Color("white"), ((x + width) - 100, (y + height) - 55))
        cancelBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 240, (y + height) - 70))
        cancel = Label(self, "Cancel", 23, Color("white"), ((x + width) - 229, (y + height) - 55))

        self.inputBox.addEvent(hoverColor, 'onKeyPress', color = Color("white"))

        save.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        save.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        save.addEvent(saveMap, 'onMouseClick')

        cancel.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        cancel.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        cancel.addEvent(toggleSaveBox, 'onMouseClick')

        self.add(box)
        self.add(title)
        self.add(self.inputBox)
        self.add(mapName)
        self.add(saveBox)
        self.add(save)
        self.add(cancelBox)
        self.add(cancel)


    def confirmBox(self):
        self.open = True
        self.confirmBoxOpen = True

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        box = Rectangle(self, GREEN, (width, height), (x, y))
        title = Label(self, "Delete", 30, Color("white"), (x + 20, y + 20))
        title.setUnderline(True)
        confirm1 = Label(self, "Are you sure you want to", 30, Color("white"), (x + 40, y + 92))
        confirm2 = Label(self, "delete this map?", 30, Color("white"), (x + 40, y + 125))

        confirmBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 120, (y + height) - 70))
        confirm = Label(self, "Yes", 25, Color("white"), ((x + width) - 93, (y + height) - 55))
        cancelBox = Rectangle(self, BLACK, (100, 50), ((x + width) - 240, (y + height) - 70))
        cancel = Label(self, "Cancel", 23, Color("white"), ((x + width) - 229, (y + height) - 55))


        confirm.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        confirm.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        confirm.addEvent(deleteMap, 'onMouseClick')

        cancel.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        cancel.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        cancel.addEvent(toggleConfirmBox, 'onMouseClick')

        self.add(box)
        self.add(title)
        self.add(confirm1)
        self.add(confirm2)
        self.add(confirmBox)
        self.add(confirm)
        self.add(cancelBox)
        self.add(cancel)


class PreviewHud(GameHudLayout):
    def __init__(self, renderer, spacing):
        super().__init__(renderer)
        self.spacing = spacing


    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeterAmount'):
            self.slowDownMeterAmount.setSize((amount, 20))
            self.slowDownMeterAmount.dirty = True


    def main(self, transition = False):
        self.open = True

        meterWidth = self.game.spriteRenderer.getSlowDownMeterAmount()

        topbar = Rectangle(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        stop = Label(self, "Stop", 25, Color("white"), (20, 10))
        slowDownMeter = Rectangle(self, Color("white"), (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 12))
        slowDownMeterOutline = Rectangle(self, Color("white"), (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 12), 2)
        self.slowDownMeterAmount = Rectangle(self, GREEN, (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 12))
        completed = Image(self, "walkingWhite", (30, 30), (config["graphics"]["displayWidth"] - 68, 7))
        self.completedText = Label(self, str(self.game.spriteRenderer.getCompleted()), 25, Color("white"), (config["graphics"]["displayWidth"] - 40, 14))   

        stop.addEvent(hoverColor, 'onMouseOver', color = GREEN)
        stop.addEvent(hoverColor, 'onMouseOut', color = Color("white"))
        stop.addEvent(stopMap, 'onMouseClick')

        self.add(topbar)
        self.add(stop)
        self.add(slowDownMeter)
        self.add(self.slowDownMeterAmount)
        self.add(slowDownMeterOutline)
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

    # def addMessage(self, message):
    #     # add the message to the top of the stack
    #     # message is displayed in a message box object
    #     # message box object has animation to come from top right hand corner; starts timer in message box object
    #     # shift down all other boxes in the messages
    #     def callback(obj, menu, y):
    #         obj.y = y

    #     maxCharLimit = 25
    #     curWord = 0
    #     finalMessage = ['']
    #     for word in message.split():
    #         if len(finalMessage[curWord]) + len(word) < maxCharLimit:
    #             finalMessage[curWord] += word + ' '
    #         else:
    #             finalMessage.append(word + ' ')
    #             curWord += 1

    #     messages = []
    #     x, y = 30, 30,
    #     biggestWidth, totalHeight = 0, 0
    #     for msg in finalMessage:
    #         m = Label(self, msg, 25, BLACK, (0, 0)) # first we siet the x and y to 0 since we don't know the width yet
    #         width, height = m.getFontSize()
    #         m.setPos((config["graphics"]["displayWidth"] - (width + x), (y + totalHeight) - 100))
    #         m.addAnimation(transitionY, 'onLoad', speed = 4, transitionDirection = "down", y = y + totalHeight, callback = callback)
    #         totalHeight += height

    #         if width > biggestWidth:
    #             biggestWidth = width

    #         messages.append(m)

    #     box = Rectangle(self, Color("white"), (biggestWidth + 10, totalHeight + 10), ((config["graphics"]["displayWidth"] - (biggestWidth + x)) - 5, (y - 5) - 100), 'rect', 0, [10, 10, 10, 10])
    #     box.addAnimation(transitionY, 'onLoad', speed = 4, transitionDirection = "down", y = y - 5, callback = callback)

    #     self.add(box)
    #     for msg in messages:
    #         self.add(msg)


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
        