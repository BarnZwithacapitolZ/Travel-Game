import pygame
from pygame.locals import *
from config import *
from menuFunctions import *
from menuComponents import *
from clickManager import *

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

    def add(self, obj):
        self.components.append(obj)
    

    def resize(self):
        height = self.renderer.getHeight()

        for component in self.components:
            component.dirty = True # force redraw

            if isinstance(component, Label):
                component.setFont(height)
            if isinstance(component, InputBox):
                component.resizeIndicator()
                

    def display(self):    
        if self.open:
            for component in self.components:
                component.draw()
                
                self.events(component)
                self.animate(component)


    def animate(self, component):
        if hasattr(component, 'rect'):
            if len(component.animations) > 0:
                for animation in component.animations:
                    if animation[1] == 'onMouseOver':
                        animation[0](component, self, animation)
                        # component.dirty = True

                    if animation[1] == 'onMouseOut':
                        animation[0](component, self, animation)
                        # component.dirty = True

                    if animation[1] == 'onLoad':
                        animation[0](component, self, animation)
                        # component.dirty = True

                        

    def events(self, component):
        mx, my = pygame.mouse.get_pos()
        #apply difference from screen size
        mx -= self.renderer.getDifference()[0]
        my -= self.renderer.getDifference()[1]

        if hasattr(component, 'rect'): # check the component has been drawn (if called before next tick)
            if len(component.events) > 0:
                for event in component.events:
                    if event[1] == 'onMouseClick':
                        if component.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
                            self.game.clickManager.setClicked(False)
                            event[0](component, self)
                            component.dirty = True

                    if event[1] == 'onMouseOver':
                        if component.rect.collidepoint((mx, my)) and not component.mouseOver:
                            component.mouseOver = True
                            event[0](component, self)
                            component.dirty = True

                    if event[1] == 'onMouseOut':
                        if not component.rect.collidepoint((mx, my)) and component.mouseOver:
                            component.mouseOver = False
                            event[0](component, self)
                            component.dirty = True

                    if event[1] == 'onKeyPress':
                        if self.game.textHandler.getPressed():
                            self.game.textHandler.setPressed(False)
                            event[0](component, self)
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




class MainMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)

    def main(self):
        self.open = True
        sidebar = Shape(self, (0, 169, 132), (500, config["graphics"]["displayHeight"]), (0, 0))

        title1 = Label(self, "Transport", 70, Color("white"), (100, 100))
        title2 = Label(self, "The", 30, Color("white"), (100, 170))
        title3 = Label(self, "Public", 70, Color("white"), (100, 200))

        cont = Label(self, "Continue", 50,  BLACK, (100, 320))
        editor = Label(self, "Level editor", 50, BLACK, (100, 380))
        end = Label(self, "Quit", 50, BLACK, (100, 440))


        cont.addEvent(continueGame, 'onMouseClick')
        cont.addEvent(hoverOver, 'onMouseOver')
        cont.addEvent(hoverOut, 'onMouseOut')

        editor.addEvent(hoverOver, 'onMouseOver')
        editor.addEvent(hoverOut, 'onMouseOut')
        editor.addEvent(openMapEditor, 'onMouseClick')

        end.addEvent(closeGame, 'onMouseClick')
        end.addEvent(hoverOver, 'onMouseOver')
        end.addEvent(hoverOut, 'onMouseOut')

        self.add(sidebar)

        self.add(title1)
        self.add(title2)
        self.add(title3)
        self.add(cont)
        self.add(editor)
        self.add(end)

        # Temporarily load in the existing maps
        y = 100
        for mapName, path in self.game.mapLoader.getMaps().items():
            m = Label(self, mapName, 30, BLACK, (600, y))
            m.addEvent(loadMap, 'onMouseClick')
            self.add(m)
            y += 40
    


class OptionMenu(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    def main(self):
        self.open = True
        sidebar = Shape(self, (0, 169, 132), (500, config["graphics"]["displayHeight"]), (0, 0))

        paused = Label(self, "Paused", 70, BLACK, (100, 100))

        options = Label(self, "Options", 50,  BLACK, (100, 200))
        new = Label(self, "New Game", 50,  BLACK, (100, 260))
        save = Label(self, "Save Game", 50,  BLACK, (100, 320))
        mainMenu = Label(self, "Main Menu", 50, BLACK, (100, 380))
        close = Label(self, "Close", 30, BLACK, (100, 440))

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

        # self.add(background)
        self.add(sidebar)
        self.add(paused)
        self.add(options)
        self.add(new)
        self.add(save)
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

    

class GameHud(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    def main(self):
        self.open = True
        self.dropdownOpen = False
        
        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        dropdown = Label(self, self.game.spriteRenderer.getLevel(), 25, BLACK, (20, 10)) # Should be white
        home = Image(self, "home", Color("white"), (50, 50), (20, 500))
        layers = Image(self, "layers", Color("white"), (50, 50), (80, 500))
        

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayers, 'onMouseOut')
        layers.addEvent(changeGameLayer, 'onMouseClick')

        home.addEvent(showHome, 'onMouseOver')
        home.addEvent(hideHome, 'onMouseOut')
        home.addEvent(goHome, 'onMouseClick')

        # dropdown.addEvent(toggleDropdown, 'onMouseClick')
        # dropdown.addEvent(hoverGreen, 'onMouseOver')
        # dropdown.addEvent(hoverWhite, 'onMouseOut')


        # self.add(topbar)
        self.add(dropdown)
        self.add(home)
        self.add(layers)


    def dropdown(self):
        self.open = True
        self.dropdownOpen = True
        self.option1Open = False
        self.option2Open = False

        background = Shape(self, (0, 169, 132), (150, 100), (400, 40))
        option1 = Label(self, "option 1", 25, Color("white"), (420, 60))
        option2 = Label(self, "option 2", 25, Color("white"), (420, 100))

        option1.addEvent(toggleOption1, 'onMouseClick')
        option1.addEvent(hoverBlack, 'onMouseOver')
        option1.addEvent(hoverWhite, 'onMouseOut')

        option2.addEvent(toggleOption2, 'onMouseClick')
        option2.addEvent(hoverBlack, 'onMouseOver')
        option2.addEvent(hoverWhite, 'onMouseOut')


        self.add(background)
        self.add(option1)
        self.add(option2)



    def option1(self):
        self.open = True
        self.option1Open = True


        optionBackground = Shape(self, (0, 169, 132), (150, 35), (550, 55))
        optionText = Label(self, "something", 25, Color("white"), (560, 60))

        optionText.addEvent(hoverBlack, 'onMouseOver')
        optionText.addEvent(hoverWhite, 'onMouseOut')


        self.add(optionBackground)
        self.add(optionText)

    def option2(self):
        self.open = True
        self.option2Open = True


        optionBackground = Shape(self, (0, 169, 132), (150, 35), (550, 95))
        optionText = Label(self, "another", 25, Color("white"), (560, 100))

        optionText.addEvent(hoverBlack, 'onMouseOver')
        optionText.addEvent(hoverWhite, 'onMouseOut')


        self.add(optionBackground)
        self.add(optionText)


class EditorHud(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)


    def main(self):
        self.open = True
        self.fileDropdownOpen = False
        self.addDropdownOpen = False
        self.deleteDropdownOpen = False

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        layers = Image(self, "layers", Color("white"), (50, 50), (15, 500))


        fileSelect = Label(self, "File", 25, Color("white"), (20, 10))
        add = Label(self, "Add", 25, Color("white"), (90, 10))
        delete = Label(self, "Delete", 25, Color("white"), (170, 10))
        run = Label(self, "Run", 25, Color("white"), (280, 10))

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayers, 'onMouseOut')
        layers.addEvent(changeEditorLayer, 'onMouseClick')

        self.add(topbar)

        fileSelect.addEvent(toggleFileDropdown, 'onMouseClick')
        add.addEvent(toggleAddDropdown, 'onMouseClick')
        delete.addEvent(toggleDeleteDropdown, 'onMouseClick')
        run.addEvent(runMap, 'onMouseClick')


        labels = [fileSelect, add, delete, run]
        for label in labels:
            label.addEvent(hoverGreen, 'onMouseOver')
            label.addEvent(hoverWhite, 'onMouseOut')
            self.add(label)


    def addDropdown(self):
        self.open = True
        self.addDropdownOpen = True

        clickType = self.game.mapEditor.getClickManager().getClickType()
        connectionSelected = True if clickType == EditorClickManager.ClickType.CONNECTION else False 
        stopSelectd = True if clickType == EditorClickManager.ClickType.STOP else False 
        transportSelected = True if clickType == EditorClickManager.ClickType.TRANSPORT else False 

        box = Shape(self, BLACK, (200, 114), (90, 40))
        connectionBox = Shape(self, GREEN, (200, 33), (90, 45))
        stopBox = Shape(self, GREEN, (200, 33), (90, 81))
        transportBox = Shape(self, GREEN, (200, 33), (90, 116))

        connection = Label(self, "Connection", 25, Color("white"), (100, 50))
        stop = Label(self, "Stop", 25, Color("white"), (100, 85))
        transport = Label(self, "Transport", 25, Color("white"), (100, 120))

        connection.addEvent(addConnection, 'onMouseClick')
        stop.addEvent(addStop, 'onMouseClick')
        transport.addEvent(addTransport, 'onMouseClick')

        self.add(box)
        if connectionSelected: self.add(connectionBox)
        if stopSelectd: self.add(stopBox)
        if transportSelected: self.add(transportBox)

        labels = [(connection, connectionSelected), (stop, stopSelectd), (transport, transportSelected)]
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

        box = Shape(self, BLACK, (200, 114), (170, 40))


        connection = Label(self, "Connection", 25, Color("white"), (180, 50))
        stop = Label(self, "Stop", 25, Color("white"), (180, 85))
        transport = Label(self, "Transport", 25, Color("white"), (180, 120))

        connection.addEvent(deleteConnection, 'onMouseClick')
        stop.addEvent(deleteStop, 'onMouseClick')
        transport.addEvent(deleteTransport, 'onMouseClick')

        self.add(box)

        labels = [connection, stop, transport]
        for label in labels:
            label.addEvent(hoverGreen, 'onMouseOver')
            label.addEvent(hoverWhite, 'onMouseOut')
            self.add(label)


    def fileDropdown(self):
        self.open = True
        self.fileDropdownOpen = True
        self.saveBoxOpen = False
        self.loadBoxOpen = False
        self.confirmBoxOpen = False

        box = Shape(self, BLACK, (130, 220), (20, 40))
        new = Label(self, "New", 25, Color("white"), (30, 50))
        load = Label(self, "Open", 25, Color("white"), (30, 85))
        save = Label(self, "Save", 25, Color("white"), (30, 120))
        saveAs = Label(self, "Save as", 25, Color("white"), (30, 155))

        delete = Label(self, "Delete", 25, Color("white") if self.game.mapEditor.getSaved() and self.game.mapEditor.getDeletable() else GREY, (30, 190))
        close = Label(self, "Exit", 25, Color("white"), (30, 225))

        new.addEvent(newMap, 'onMouseClick')
        load.addEvent(toggleLoadDropdown, 'onMouseClick')
        save.addEvent(toggleSaveBox, 'onMouseClick')
        saveAs.addEvent(toggleSaveAsBox, 'onMouseClick')
        close.addEvent(closeMapEditor, 'onMouseClick')

        if self.game.mapEditor.getSaved() and self.game.mapEditor.getDeletable():
            delete.addEvent(hoverGreen, 'onMouseOver')
            delete.addEvent(hoverWhite, 'onMouseOut')
            delete.addEvent(toggleConfirmBox, 'onMouseClick')

        self.add(box)
        self.add(delete)

        # Add each of the labels
        labels = [new, load, save, saveAs, close]
        for label in labels:
            label.addEvent(hoverGreen, 'onMouseOver')
            label.addEvent(hoverWhite, 'onMouseOut')
            self.add(label)


    def loadDropdown(self):
        self.open = True
        self.loadBoxOpen = True

        width = 130
        if self.game.mapLoader.getLongestMapLength() * 15 > width:
            width = self.game.mapLoader.getLongestMapLength() * 15

        # make width equal to the longest map name
        box = Shape(self, BLACK, (width, 20 + (30 * len(self.game.mapLoader.getMaps()))), (150, 85))

        self.add(box)

        # Temporarily load in the existing maps
        y = 95
        for mapName, path in self.game.mapLoader.getMaps().items():
            m = Label(self, mapName, 25, Color("white"), (160, y))
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


    


class PreviewHud(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)

    def main(self):
        self.open = True

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        stop = Label(self, "Stop", 25, Color("white"), (20, 10))

        stop.addEvent(hoverGreen, 'onMouseOver')
        stop.addEvent(hoverWhite, 'onMouseOut')
        stop.addEvent(stopMap, 'onMouseClick')

        self.add(topbar)
        self.add(stop)
        