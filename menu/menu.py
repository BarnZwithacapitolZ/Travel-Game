import pygame
from pygame.locals import *
from config import *
from menuFunctions import *
from transitionFunctions import *
from menuComponents import *
from clickManager import *
import abc
import random

class Menu:
    def __init__(self, game):
        pygame.font.init()
        # self.font = pygame.freetype.Font(font, 30)

        self.open = False
        self.game = game
        self.renderer = game.renderer
        self.components = []


        # print(pygame.display.get_surface())
        self.clicked = False

    
    def setOpen(self, hudOpen):
        self.open = hudOpen

    def getOpen(self):
        return self.open

    def add(self, obj):
        self.components.append(obj)

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
        #apply difference from screen size
        mx -= self.renderer.getDifference()[0]
        my -= self.renderer.getDifference()[1]

        if hasattr(component, 'rect'): # check the component has been drawn (if called before next tick)
            if len(component.events) > 0:
                for function, event in list(component.events.items()):
                    if event[0] == 'onMouseClick':
                        if component.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
                            self.clickButton()
                            self.game.clickManager.setClicked(False)
                            function(component, self, **event[1])
                            component.dirty = True

                    if event[0] == 'onMouseOver':
                        if component.rect.collidepoint((mx, my)) and not component.mouseOver:
                            component.mouseOver = True
                            function(component, self, **event[1])
                            component.dirty = True

                    if event[0] == 'onMouseOut':
                        if not component.rect.collidepoint((mx, my)) and component.mouseOver:
                            component.mouseOver = False
                            function(component, self, **event[1])
                            component.dirty = True

                    if event[0] == 'onKeyPress':
                        if self.game.textHandler.getPressed():
                            self.game.textHandler.setPressed(False)
                            function(component, self, **event[1])
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

        test = Shape(self, BLACK, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0), 255)
        test.addAnimation(transitionFadeOut, 'onLoad')
        self.add(test)


class MainMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)

    def main(self):
        self.open = True
        # sidebar = Shape(self, GREEN, (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]), (0, 0))
        sidebar = Image(self, "example", Color("white"), (config["graphics"]["displayWidth"], config["graphics"]["displayHeight"], 50), (0, 0))

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


        cont.addEvent(continueGame, 'onMouseClick')
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

        self.add(sidebar)
        # self.add(otherbar)

        self.add(title1)
        self.add(title2)
        self.add(title3)
        self.add(cont)
        self.add(editor)
        self.add(options)
        self.add(end)

        # Temporarily load in the existing maps
        # y = 100
        # for mapName, path in self.game.mapLoader.getMaps().items():
        #     m = Label(self, mapName, 30, BLACK, (600, y))
        #     m.addEvent(loadMap, 'onMouseClick')
        #     self.add(m)
        #     y += 40
    


class OptionMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    def closeTransition(self):
        self.game.spriteRenderer.getHud().setOpen(True)
        # self.game.mapEditor.getMessageSystem().setOpen(True)
        self.game.mapEditor.getHud().setOpen(True)

        for component in self.components:
            # Can't add animation until previous opening animations stopped
            if (transitionRight, 'onLoad') not in component.getAnimations() and (transitionRightBackground, 'onLoad') not in component.getAnimations():
                component.addAnimation(transitionLeftUnpause, 'onLoad')


    def main(self):
        self.open = True
        
        self.game.paused = True
        self.game.spriteRenderer.getHud().setOpen(False)
        # self.game.mapEditor.getMessageSystem().setOpen(False) 
        self.game.mapEditor.getHud().setOpen(False)

        sidebar = Shape(self, GREEN, (500, config["graphics"]["displayHeight"]), (-500, 0))

        paused = Label(self, "Paused", 70, BLACK, (-400, 100))

        options = Label(self, "Options", 50,  BLACK, (-400, 200))
        # new = Label(self, "New Game", 50,  BLACK, (-400, 260))
        # save = Label(self, "Save Game", 50,  BLACK, (-400, 320))
        mainMenu = Label(self, "Main Menu", 50, BLACK, (-400, 260))
        close = Label(self, "Close", 30, BLACK, (-400, 440))

        options.addEvent(showOptions, 'onMouseClick')
        options.addEvent(hoverOver, 'onMouseOver')
        options.addEvent(hoverOut, 'onMouseOut')

        # save.addEvent(hoverOver, 'onMouseOver')
        # save.addEvent(hoverOut, 'onMouseOut')

        mainMenu.addEvent(showMainMenu, 'onMouseClick')
        mainMenu.addEvent(hoverOver, 'onMouseOver')
        mainMenu.addEvent(hoverOut, 'onMouseOut')

        close.addEvent(unpause, 'onMouseClick')
        close.addEvent(hoverOver, 'onMouseOver')
        close.addEvent(hoverOut, 'onMouseOut')

        sidebar.addAnimation(transitionRightBackground, 'onLoad')
        animateComponents = [paused, options, mainMenu, close]
        for component in animateComponents:
            component.addAnimation(transitionRight, 'onLoad')


        self.add(sidebar)
        self.add(paused)
        self.add(options)
        # self.add(new)
        # self.add(save)
        self.add(mainMenu)
        self.add(close)
        

    def options(self):
        self.open = True

        sidebar = Shape(self, (0, 169, 132), (500, config["graphics"]["displayHeight"]), (0, 0))

        graphics = Label(self, "Graphics", 50, BLACK, (100, 200))
        controls = Label(self, "Controls", 50, BLACK, (100, 260))
        back = Label(self, "Back", 50,  BLACK, (100, 380))

        graphics.addEvent(showGraphics, 'onMouseClick')
        graphics.addEvent(hoverOver, 'onMouseOver')
        graphics.addEvent(hoverOut, 'onMouseOut')

        back.addEvent(showMain, 'onMouseClick')
        back.addEvent(hoverOver, 'onMouseOver')
        back.addEvent(hoverOut, 'onMouseOut')

        self.add(sidebar)
        self.add(graphics)
        self.add(controls)
        self.add(back)


    def graphics(self):
        self.open = True
        sidebar = Shape(self, (0, 169, 132), (500, config["graphics"]["displayHeight"]), (0, 0))

        aliasText = "On" if config["graphics"]["antiAliasing"] else "Off"
        fullscreenText = "On" if self.game.fullscreen else "Off"

        antiAlias = Label(self, "AntiAliasing: " + aliasText, 50, BLACK, (100, 200))
        fullscreen = Label(self, "Fullscreen: " + fullscreenText, 50, BLACK, (100, 260))
        back = Label(self, "Back", 50,  BLACK, (100, 380))

        antiAlias.addEvent(toggleAlias, 'onMouseClick')
        antiAlias.addEvent(hoverOver, 'onMouseOver')
        antiAlias.addEvent(hoverOut, 'onMouseOut')

        fullscreen.addEvent(toggleFullscreen, 'onMouseClick')
        fullscreen.addEvent(hoverOver, 'onMouseOver')
        fullscreen.addEvent(hoverOut, 'onMouseOut')

        back.addEvent(showOptions, 'onMouseClick')
        back.addEvent(hoverOver, 'onMouseOver')
        back.addEvent(hoverOut, 'onMouseOut')
        
        self.add(sidebar)
        self.add(antiAlias)
        self.add(fullscreen)
        self.add(back)


class LevelSelectMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)

    def main(self):
        return


class GameOpeningMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    def closeTransition(self):
        self.game.audioLoader.playSound("swoopOut")
        self.game.spriteRenderer.getHud().setOpen(True)

        def callback(obj, menu, x):
            menu.game.paused = False
            menu.close()

        for component in self.components:
            component.addAnimation(transitionX, 'onLoad', speed = -40, transitionDirection = "right", x = -400, callback = callback)


    def main(self):
        self.open = True

        # show this before the game is unpaused so we don't need this
        self.game.paused = True
        self.game.spriteRenderer.getHud().setOpen(False)
        # self.game.mapEditor.getHud().setOpen(False)

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        totalText = "Transport " + str(self.game.spriteRenderer.getTotalToComplete()) + " people!"

        background = Shape(self, GREEN, (width, height), (x - 400, y))
        total = Label(self, totalText, 45, Color("white"), (((x + width) / 2 - 110) - 400, (y + height) / 2 + 20))
        play = Label(self, "Got it!", 25, Color("white"), (((config["graphics"]["displayWidth"] / 2) - 40) - 400, (config["graphics"]["displayHeight"] / 2) + 20))

        # total.setItalic(True)

        def callback(obj, menu, x):
            obj.x = x

        background.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = x, callback = callback)
        total.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = ((x + width) / 2 - 110), callback = callback)
        play.addAnimation(transitionX, 'onLoad', speed = 40, transitionDirection = "left", x = ((config["graphics"]["displayWidth"] / 2) - 40), callback = callback)


        play.addEvent(hoverBlack, 'onMouseOver')
        play.addEvent(hoverWhite, 'onMouseOut')
        play.addEvent(playGame, 'onMouseClick')

        animateComponents = [background, total, play]


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
    def setCompletedText(self, text):
        return

    @abc.abstractmethod
    def updateSlowDownMeter(self, amount):
        return

    

class GameHud(GameHudLayout):
    def __init__(self, renderer):
        super().__init__(renderer)

    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeterAmount'):
            self.slowDownMeterAmount.setSize((amount, 20))
            self.slowDownMeterAmount.dirty = True

    def main(self):
        self.open = True
        self.dropdownOpen = False
        
        meterWidth = self.game.spriteRenderer.getSlowDownMeterAmount()

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        dropdown = Label(self, self.game.spriteRenderer.getLevel(), 25, BLACK, (20, 10)) # Should be white
        home = Image(self, "home", Color("white"), (50, 50), (20, 500))
        layers = Image(self, "layers", Color("white"), (50, 50), (20, 440))
        slowDownMeter = Shape(self, Color("white"), (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 26))
        slowDownMeterOutline = Shape(self, BLACK, (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 26), 'rect', 2)
        self.slowDownMeterAmount = Shape(self, GREEN, (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 26))
        completed = Image(self, "walking", Color("white"), (40, 40), (config["graphics"]["displayWidth"] - 75, 26))
        self.completedText = Label(self, str(self.game.spriteRenderer.getCompleted()), 25, BLACK, (config["graphics"]["displayWidth"] - 40, 43))   

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayers, 'onMouseOut')
        layers.addEvent(changeGameLayer, 'onMouseClick')

        home.addEvent(showHome, 'onMouseOver')
        home.addEvent(hideHome, 'onMouseOut')
        home.addEvent(goHome, 'onMouseClick')

        # self.add(topbar)
        # self.add(dropdown)
        self.add(home)
        self.add(layers)
        self.add(slowDownMeter)
        self.add(self.slowDownMeterAmount)
        self.add(slowDownMeterOutline)
        self.add(completed)
        self.add(self.completedText)


    def setCompletedText(self, text):
        if hasattr(self, 'completedText'):
            self.completedText.setText(text)
            self.completedText.setColor(YELLOW)
            self.completedText.addAnimation(successAnimationUp, 'onLoad')
            self.completedText.dirty = True


class EditorHud(GameHudLayout):
    def __init__(self, renderer):
        super().__init__(renderer)

        # Locations of each option
        self.fileLocation = 20
        self.editLocation = self.fileLocation + 70 # 90
        self.addLocation = self.editLocation + 70 # 90
        self.deleteLocation = self.addLocation + 75 # 170
        self.runLocation = self.deleteLocation + 100 # 280


    def updateLayerText(self):
        if hasattr(self, 'currentLayer'):
            self.currentLayer.setText("layer " + str(self.game.mapEditor.getLayer()))


    def closeDropdowns(self):
        self.close()
        self.main()


    def main(self):
        self.open = True
        self.fileDropdownOpen = False
        self.editDropdownOpen = False
        self.addDropdownOpen = False
        self.deleteDropdownOpen = False

        self.game.mapEditor.setAllowEdits(True)

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))

        fileSelect = Label(self, "File", 25, Color("white"), (self.fileLocation, 10))
        edit = Label(self, "Edit", 25, Color("white"), (self.editLocation, 10))
        add = Label(self, "Add", 25, Color("white"), (self.addLocation, 10))
        delete = Label(self, "Delete", 25, Color("white"), (self.deleteLocation, 10))
        run = Label(self, "Run", 25, Color("white"), (self.runLocation, 10))

        layers = Image(self, "layersWhite", Color("white"), (25, 25), (880, 10))
        self.currentLayer = Label(self, "layer " + str(self.game.mapEditor.getLayer()), 25, Color("white"), (915, 10))

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayersWhite, 'onMouseOut')
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
            label.addEvent(hoverGreen, 'onMouseOver')
            label.addEvent(hoverWhite, 'onMouseOut')
            self.add(label)


    def editDropdown(self):
        self.open = True
        self.editDropdownOpen = True
        self.editSizeDropdownOpen = False

        self.game.mapEditor.setAllowEdits(False)

        box = Shape(self, BLACK, (200, 150), (self.editLocation, 40), 'rect', 0, [0, 0, 10, 10])

        textX = self.editLocation + 10

        size = Label(self, "Map Size", 25, Color("white"), (textX, 50))
        
        self.add(box)

        size.addEvent(toggleEditSizeDropdown, 'onMouseClick')

        labels = [size]
        for label in labels:
            label.addEvent(hoverGreen, 'onMouseOver')
            label.addEvent(hoverWhite, 'onMouseOut')
            self.add(label)


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

        box = Shape(self, BLACK, (110, 150), (boxX, 85))
        size0Box = Shape(self, GREEN, (110, 33), (boxX, 90))
        size1Box = Shape(self, GREEN, (110, 33), (boxX, 126))
        size2Box = Shape(self, GREEN, (110, 33), (boxX, 161))
        size3Box = Shape(self, GREEN, (110, 33), (boxX, 195))

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
                label[0].addEvent(hoverBlack, 'onMouseOver')
            else:
                label[0].addEvent(hoverGreen, 'onMouseOver')
            label[0].addEvent(hoverWhite, 'onMouseOut')
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

        box = Shape(self, BLACK, (200, 150), (self.addLocation, 40), 'rect', 0, [0, 0, 10, 10])
        connectionBox = Shape(self, GREEN, (200, 33), (self.addLocation, 45))
        stopBox = Shape(self, GREEN, (200, 33), (self.addLocation, 81))
        transportBox = Shape(self, GREEN, (200, 33), (self.addLocation, 116))
        destinationBox = Shape(self, GREEN, (200, 33), (self.addLocation, 151))

        textX = self.addLocation + 10 # x position of text within box

        connection = Label(self, "Connection", 25, Color("white"), (textX, 50))
        stop = Label(self, "Stop", 25, Color("white"), (textX, 85))
        transport = Label(self, "Transport", 25, Color("white"), (textX, 120))
        destination = Label(self, "Destination", 25, Color("white"), (textX, 155))

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
                label[0].addEvent(hoverBlack, 'onMouseOver')
            else:
                label[0].addEvent(hoverGreen, 'onMouseOver')
            label[0].addEvent(hoverWhite, 'onMouseOut')
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

        box = Shape(self, BLACK, (200, 114), (boxX, 85))
        metroBox = Shape(self, GREEN, (200, 33), (boxX, 90))
        busBox = Shape(self, GREEN, (200, 33), (boxX, 126))
        tramBox = Shape(self, GREEN, (200, 33), (boxX, 161))

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
                label[0].addEvent(hoverBlack, 'onMouseOver')
            else:
                label[0].addEvent(hoverGreen, 'onMouseOver')
            label[0].addEvent(hoverWhite, 'onMouseOut')
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

        box = Shape(self, BLACK, (110, 150), (boxX, 120))
        metroBox = Shape(self, GREEN, (110, 33), (boxX, 125))
        busBox = Shape(self, GREEN, (110, 33), (boxX, 161))
        tramBox = Shape(self, GREEN, (110, 33), (boxX, 196))
        taxiBox = Shape(self, GREEN, (110, 33), (boxX, 231))

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
                label[0].addEvent(hoverBlack, 'onMouseOver')
            else:
                label[0].addEvent(hoverGreen, 'onMouseOver')
            label[0].addEvent(hoverWhite, 'onMouseOut')
            self.add(label[0])



    def addDestinationDropdown(self):
        self.open = True
        self.addDestinationDropdownOpen = True

        self.game.mapEditor.setAllowEdits(False)

        addType = self.game.mapEditor.getClickManager().getAddType()
        airportSelected = True if addType == 'airport' else False
        officeSelected = True if addType == 'office' else False
        # TO DO: Add other types of transportation    

        boxX = self.addLocation + 200
        textX = boxX + 10

        box = Shape(self, BLACK, (200, 114), (boxX, 155))
        airportBox = Shape(self, GREEN, (200, 33), (boxX, 160))
        officeBox = Shape(self, GREEN, (200, 33), (boxX, 196))
        
        airport = Label(self, "Airport", 25, Color("white"), (textX, 165))
        office = Label(self, "Office", 25, Color("white"), (textX, 200))

        self.add(box)
        if airportSelected: self.add(airportBox)
        elif officeSelected: self.add(officeBox)

        airport.addEvent(addAirport, 'onMouseClick')
        office.addEvent(addOffice, 'onMouseClick')

        labels = [(airport, airportSelected), (office, officeSelected)]
        for label in labels:
            if label[1]:
                label[0].addEvent(hoverBlack, 'onMouseOver')
            else:
                label[0].addEvent(hoverGreen, 'onMouseOver')
            label[0].addEvent(hoverWhite, 'onMouseOut')
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

        box = Shape(self, BLACK, (200, 150), (self.deleteLocation, 40), 'rect', 0, [0, 0, 10, 10])
        connectionBox = Shape(self, GREEN, (200, 33), (self.deleteLocation, 45))
        stopBox = Shape(self, GREEN, (200, 33), (self.deleteLocation, 81))
        transportBox = Shape(self, GREEN, (200, 33), (self.deleteLocation, 116))
        destinationBox = Shape(self, GREEN, (200, 33), (self.deleteLocation, 151))

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
                label[0].addEvent(hoverBlack, 'onMouseOver')
            else:
                label[0].addEvent(hoverGreen, 'onMouseOver')
            label[0].addEvent(hoverWhite, 'onMouseOut')
            self.add(label[0])


    def fileDropdown(self):
        self.open = True
        self.fileDropdownOpen = True
        self.saveBoxOpen = False
        self.loadBoxOpen = False
        self.confirmBoxOpen = False

        self.game.mapEditor.setAllowEdits(False)

        box = Shape(self, BLACK, (130, 220), (self.fileLocation, 40), 'rect', 0, [0, 0, 10, 10])

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
            save.addEvent(hoverGreen, 'onMouseOver')
            save.addEvent(hoverWhite, 'onMouseOut')
            save.addEvent(toggleSaveBox, 'onMouseClick')
            saveAs.addEvent(hoverGreen, 'onMouseOver')
            saveAs.addEvent(hoverWhite, 'onMouseOut')
            saveAs.addEvent(toggleSaveAsBox, 'onMouseClick')

            if self.game.mapEditor.getSaved(): 
                delete.addEvent(hoverGreen, 'onMouseOver')
                delete.addEvent(hoverWhite, 'onMouseOut')
                delete.addEvent(toggleConfirmBox, 'onMouseClick')                   

        self.add(box)
        self.add(save)
        self.add(saveAs)
        self.add(delete)

        # Add each of the labels
        labels = [new, load, close]
        for label in labels:
            label.addEvent(hoverGreen, 'onMouseOver')
            label.addEvent(hoverWhite, 'onMouseOut')
            self.add(label)


    def loadDropdown(self):
        self.open = True
        self.loadBoxOpen = True

        self.game.mapEditor.setAllowEdits(False)

        width = 130
        if self.game.mapLoader.getLongestMapLength() * 15 > width:
            width = self.game.mapLoader.getLongestMapLength() * 15

        boxX = self.fileLocation + 130
        textX = boxX + 10

        # make width equal to the longest map name
        box = Shape(self, BLACK, (width, 20 + (30 * len(self.game.mapLoader.getMaps()))), (boxX, 85))

        self.add(box)

        # Temporarily load in the existing maps
        y = 95
        for mapName, path in self.game.mapLoader.getMaps().items():
            m = Label(self, mapName, 25, Color("white"), (textX, y))
            m.addEvent(hoverGreen, 'onMouseOver')
            m.addEvent(hoverWhite, 'onMouseOut')
            m.addEvent(loadEditorMap, 'onMouseClick')
            self.add(m)
            y += 30


    def saveBox(self):
        self.open = True
        self.saveBoxOpen = True

        width = config["graphics"]["displayWidth"] / 2
        height = 240
        x = width - (width / 2)
        y = config["graphics"]["displayHeight"] / 2 - (height / 2)

        box = Shape(self, GREEN, (width, height), (x, y))
        title = Label(self, "Map name", 30, Color("white"), (x + 20, y + 20))
        self.inputBox = Shape(self, Color("white"), (width - 40, 50), (x + 20, y + 80))
        mapName = InputBox(self, 30, BLACK, (x + 40, y + 92), 20)
        saveBox = Shape(self, BLACK, (100, 50), ((x + width) - 120, (y + height) - 70))
        save = Label(self, "Save", 25, Color("white"), ((x + width) - 100, (y + height) - 55))
        cancelBox = Shape(self, BLACK, (100, 50), ((x + width) - 240, (y + height) - 70))
        cancel = Label(self, "Cancel", 23, Color("white"), ((x + width) - 229, (y + height) - 55))

        self.inputBox.addEvent(hoverWhite, 'onKeyPress')

        save.addEvent(hoverGreen, 'onMouseOver')
        save.addEvent(hoverWhite, 'onMouseOut')
        save.addEvent(saveMap, 'onMouseClick')

        cancel.addEvent(hoverGreen, 'onMouseOver')
        cancel.addEvent(hoverWhite, 'onMouseOut')
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

        box = Shape(self, GREEN, (width, height), (x, y))
        title = Label(self, "Delete", 30, Color("white"), (x + 20, y + 20))
        title.setUnderline(True)
        confirm1 = Label(self, "Are you sure you want to", 30, Color("white"), (x + 40, y + 92))
        confirm2 = Label(self, "this map?", 30, Color("white"), (x + 40, y + 125))

        confirmBox = Shape(self, BLACK, (100, 50), ((x + width) - 120, (y + height) - 70))
        confirm = Label(self, "Yes", 25, Color("white"), ((x + width) - 93, (y + height) - 55))
        cancelBox = Shape(self, BLACK, (100, 50), ((x + width) - 240, (y + height) - 70))
        cancel = Label(self, "Cancel", 23, Color("white"), ((x + width) - 229, (y + height) - 55))


        confirm.addEvent(hoverGreen, 'onMouseOver')
        confirm.addEvent(hoverWhite, 'onMouseOut')
        confirm.addEvent(deleteMap, 'onMouseClick')

        cancel.addEvent(hoverGreen, 'onMouseOver')
        cancel.addEvent(hoverWhite, 'onMouseOut')
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
    def __init__(self, renderer):
        super().__init__(renderer)


    def updateSlowDownMeter(self, amount):
        if hasattr(self, 'slowDownMeterAmount'):
            self.slowDownMeterAmount.setSize((amount, 20))
            self.slowDownMeterAmount.dirty = True


    def main(self):
        self.open = True

        meterWidth = self.game.spriteRenderer.getSlowDownMeterAmount()

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        stop = Label(self, "Stop", 25, Color("white"), (20, 10))
        slowDownMeter = Shape(self, Color("white"), (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 12))
        slowDownMeterOutline = Shape(self, Color("white"), (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 12), 'rect', 2)
        self.slowDownMeterAmount = Shape(self, GREEN, (meterWidth, 20), (config["graphics"]["displayWidth"] - (80 + meterWidth), 12))
        completed = Image(self, "walkingWhite", Color("white"), (30, 30), (config["graphics"]["displayWidth"] - 68, 7))
        self.completedText = Label(self, str(self.game.spriteRenderer.getCompleted()), 25, Color("white"), (config["graphics"]["displayWidth"] - 40, 14))   

        stop.addEvent(hoverGreen, 'onMouseOver')
        stop.addEvent(hoverWhite, 'onMouseOut')
        stop.addEvent(stopMap, 'onMouseClick')

        self.add(topbar)
        self.add(stop)
        self.add(slowDownMeter)
        self.add(self.slowDownMeterAmount)
        self.add(slowDownMeterOutline)
        self.add(completed)
        self.add(self.completedText)


    def setCompletedText(self, text):
        if hasattr(self, 'completedText'):
            self.completedText.setText(text)
            self.completedText.dirty = True
        


class MessageHud(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.messages = []

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

    #     box = Shape(self, Color("white"), (biggestWidth + 10, totalHeight + 10), ((config["graphics"]["displayWidth"] - (biggestWidth + x)) - 5, (y - 5) - 100), 'rect', 0, [10, 10, 10, 10])
    #     box.addAnimation(transitionY, 'onLoad', speed = 4, transitionDirection = "down", y = y - 5, callback = callback)

    #     self.add(box)
    #     for msg in messages:
    #         self.add(msg)


    def addMessage(self, message):
        messageBox = MessageBox(self, message, (25, 25))
        messageBox.addAnimation(transitionMessageDown, 'onLoad', speed = 4, transitionDirection = "down", y = messageBox.marginY)
        self.add(messageBox)
        messageBox.addMessages()

        if sum(isinstance(component, MessageBox) for component in self.components) > 0:
            for component in self.components:
                if isinstance(component, MessageBox):
                    if transitionMessageDown not in component.getAnimations():
                        component.addAnimation(transitionMessageDown, 'onLoad', speed = 4, transitionDirection = "down", y = (component.y + messageBox.height) + component.marginY)

     
    def main(self):
        self.open = True
        