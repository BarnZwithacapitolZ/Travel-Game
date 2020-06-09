import pygame
from pygame.locals import *
from config import *
from menuFunctions import *
from menuComponents import *

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

            if component.type == "text":
                component.setFont(height)
                

    def display(self):    
        if self.open:
            for component in self.components:
                component.draw()
                
            self.events()
            self.animate()


    def animate(self):
        for component in self.components:
            if hasattr(component, 'rect'):
                if len(component.animations) > 0:
                    for animation in component.animations:
                        if animation[1] == 'onMouseOver':
                            animation[0](component, self, animation)
                            component.dirty = True

                        if animation[1] == 'onMouseOut':
                            animation[0](component, self, animation)
                            component.dirty = True

                        if animation[1] == 'onLoad':
                            animation[0](component, self, animation)
                            component.dirty = True

                        

    def events(self):
        mx, my = pygame.mouse.get_pos()
        #apply difference from screen size
        mx -= self.renderer.getDifference()[0]
        my -= self.renderer.getDifference()[1]

        for component in self.components:
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
        self.layersOpen = False
        
        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))
        dropdown = Label(self, "Dropdown", 25, Color("white"), (410, 10))
        home = Image(self, "home", Color("white"), (50, 50), (20, 500))
        layers = Image(self, "layers", Color("white"), (50, 50), (80, 500))
        

        layers.addEvent(showLayers, 'onMouseOver')
        layers.addEvent(hideLayers, 'onMouseOut')
        layers.addEvent(changeLayer, 'onMouseClick')

        home.addEvent(showHome, 'onMouseOver')
        home.addEvent(hideHome, 'onMouseOut')
        home.addEvent(goHome, 'onMouseClick')

        dropdown.addEvent(toggleDropdown, 'onMouseClick')
        dropdown.addEvent(hoverGreen, 'onMouseOver')
        dropdown.addEvent(hoverWhite, 'onMouseOut')


        # self.add(topbar)
        # self.add(dropdown)
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

        topbar = Shape(self, BLACK, (config["graphics"]["displayWidth"], 40), (0, 0))

        self.add(topbar)