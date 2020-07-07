import pygame
from pygame.locals import *
from config import *
from menuFunctions import *
from transitionFunctions import *
from menuComponents import *
from clickManager import *
import abc

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
    

    def resize(self):
        for component in self.components:
            component.dirty = True # force redraw

            if isinstance(component, InputBox):
                component.resizeIndicator()
                

    def display(self):    
        for component in self.components:
            component.draw()

            if self.open:
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
        sidebar = Shape(self, (0, 169, 132), (config["graphics"]["displayWidth"] / 2, config["graphics"]["displayHeight"]), (0, 0))
        otherbar = Shape(self, CREAM, (config["graphics"]["displayWidth"] / 2, config["graphics"]["displayHeight"]), (config["graphics"]["displayWidth"] / 2, 0))

        title1 = Label(self, "Transport", 70, Color("white"), (100, 100))
        title2 = Label(self, "The", 30, Color("white"), (100, 170))
        title3 = Label(self, "Public", 70, Color("white"), (100, 200))

        title1.setItalic(True)
        title2.setItalic(True)
        title3.setItalic(True)

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
        # self.add(otherbar)

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


    def closeTransition(self):
        self.game.spriteRenderer.getHud().setOpen(True)
        self.game.mapEditor.getHud().setOpen(True)

        for component in self.components:
            component.addAnimation(transitionLeftUnpause, 'onLoad')


    def main(self):
        self.open = True
        
        self.game.paused = True
        self.game.spriteRenderer.getHud().setOpen(False)
        self.game.mapEditor.getHud().setOpen(False)

        sidebar = Shape(self, (0, 169, 132), (500, config["graphics"]["displayHeight"]), (-500, 0))

        paused = Label(self, "Paused", 70, BLACK, (-400, 100))

        options = Label(self, "Options", 50,  BLACK, (-400, 200))
        new = Label(self, "New Game", 50,  BLACK, (-400, 260))
        save = Label(self, "Save Game", 50,  BLACK, (-400, 320))
        mainMenu = Label(self, "Main Menu", 50, BLACK, (-400, 380))
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
        animateComponents = [paused, options, new, save, mainMenu, close]
        for component in animateComponents:
            component.addAnimation(transitionRight, 'onLoad')


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



# Anything that all the game huds will use
class GameHudLayout(Menu):
    def __init__(self, renderer):
        super().__init__(renderer)

    @abc.abstractmethod
    def updateLayerText(self):
        return

    

class GameHud(GameHudLayout):
    def __init__(self, renderer):
        super().__init__(renderer)

    def main(self):
        self.open = True
        self.dropdownOpen = False
        
        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        dropdown = Label(self, self.game.spriteRenderer.getLevel(), 25, BLACK, (20, 10)) # Should be white
        home = Image(self, "home", Color("white"), (50, 50), (20, 500))
        layers = Image(self, "layers", Color("white"), (50, 50), (20, 440))
        

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayers, 'onMouseOut')
        layers.addEvent(changeGameLayer, 'onMouseClick')

        home.addEvent(showHome, 'onMouseOver')
        home.addEvent(hideHome, 'onMouseOut')
        home.addEvent(goHome, 'onMouseClick')


        # self.add(topbar)
        self.add(dropdown)
        self.add(home)
        self.add(layers)




class EditorHud(GameHudLayout):
    def __init__(self, renderer):
        super().__init__(renderer)


    def updateLayerText(self):
        if hasattr(self, 'currentLayer'):
            self.currentLayer.setText("layer " + str(self.game.mapEditor.getLayer()))


    def main(self):
        self.open = True
        self.fileDropdownOpen = False
        self.addDropdownOpen = False
        self.deleteDropdownOpen = False

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))

        fileSelect = Label(self, "File", 25, Color("white"), (20, 10))
        add = Label(self, "Add", 25, Color("white"), (90, 10))
        delete = Label(self, "Delete", 25, Color("white"), (170, 10))
        run = Label(self, "Run", 25, Color("white"), (280, 10))

        layers = Image(self, "layersWhite", Color("white"), (25, 25), (880, 10))
        self.currentLayer = Label(self, "layer " + str(self.game.mapEditor.getLayer()), 25, Color("white"), (915, 10))

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayersWhite, 'onMouseOut')
        layers.addEvent(changeEditorLayer, 'onMouseClick')

        self.add(topbar)
        self.add(layers)
        self.add(self.currentLayer)

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


        clickType = self.game.mapEditor.getClickManager().getClickType()
        connectionSelected = True if clickType == EditorClickManager.ClickType.DCONNECTION else False 
        stopSelectd = True if clickType == EditorClickManager.ClickType.DSTOP else False 
        transportSelected = True if clickType == EditorClickManager.ClickType.DTRANSPORT else False

        box = Shape(self, BLACK, (200, 114), (170, 40))
        connectionBox = Shape(self, GREEN, (200, 33), (170, 45))
        stopBox = Shape(self, GREEN, (200, 33), (170, 81))
        transportBox = Shape(self, GREEN, (200, 33), (170, 116))

        connection = Label(self, "Connection", 25, Color("white"), (180, 50))
        stop = Label(self, "Stop", 25, Color("white"), (180, 85))
        transport = Label(self, "Transport", 25, Color("white"), (180, 120))

        connection.addEvent(deleteConnection, 'onMouseClick')
        stop.addEvent(deleteStop, 'onMouseClick')
        transport.addEvent(deleteTransport, 'onMouseClick')

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


    def fileDropdown(self):
        self.open = True
        self.fileDropdownOpen = True
        self.saveBoxOpen = False
        self.loadBoxOpen = False
        self.confirmBoxOpen = False

        box = Shape(self, BLACK, (130, 220), (20, 40))
        new = Label(self, "New", 25, Color("white"), (30, 50))
        load = Label(self, "Open", 25, Color("white"), (30, 85))
        save = Label(self, "Save", 25, Color("white") if self.game.mapEditor.getDeletable() else GREY, (30, 120)) 
        saveAs = Label(self, "Save as", 25, Color("white") if self.game.mapEditor.getDeletable() else GREY, (30, 155))

        # Must be already saved and be a deletable map
        delete = Label(self, "Delete", 25, Color("white") if self.game.mapEditor.getSaved() and self.game.mapEditor.getDeletable() else GREY, (30, 190))
        close = Label(self, "Exit", 25, Color("white"), (30, 225))

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


    


class PreviewHud(GameHudLayout):
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
        