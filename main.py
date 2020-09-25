import pygame
import sys
import os

#insert directory paths
sys.path.insert(0, 'menu')
sys.path.insert(0, 'sprites')

from config import *
from engine import *
from spriteRenderer import *
from menu import *
from sprites import *
from menuComponents import *
from mapEditor import *

import cProfile


class Game:
    def __init__(self):
        pygame.key.set_repeat(500, 100)
        pygame.font.init()
        pygame.event.set_allowed([QUIT, VIDEORESIZE, KEYDOWN, MOUSEBUTTONDOWN])

        self.playing = True
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.fullscreen = config["graphics"]["fullscreen"]

        # Engine
        self.renderer = Renderer(self)
        self.spriteRenderer = SpriteRenderer(self)
        self.clickManager = ClickManager(self)
        self.textHandler = TextHandler()

        # Loaders
        self.imageLoader = ImageLoader()
        self.mapLoader = MapLoader()
        self.audioLoader = AudioLoader()
        
        # Map editor 
        self.mapEditor = MapEditor(self)

        # Menu's
        self.mainMenu = MainMenu(self)
        self.optionMenu = OptionMenu(self)


        if self.fullscreen:
            self.renderer.setFullscreen()

        self.setCaption()
        self.setIcon()
        self.setCursor()

    # Set the games caption (name)
    def setCaption(self):
        pygame.display.set_caption(config["game"]["gameTitle"])

    # Set the games icon
    def setIcon(self):
        icon = self.imageLoader.getImage(config["game"]["icon"])
        pygame.display.set_icon(icon)

    # Set the games cursor (cursor class?)
    def setCursor(self):
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)


    def getPaused(self):
        return self.paused


    def __quit(self):
        self.playing = False


    def __events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__quit()

            if e.type == pygame.VIDEORESIZE:
                self.renderer.setScale(e.size, self.fullscreen)
                self.spriteRenderer.resize()
                self.mapEditor.resize()
                self.optionMenu.resize()
                self.mainMenu.resize()               

            if e.type == pygame.KEYDOWN:
                self.textHandler.events(e)
                self.textHandler.setPressed(True)

                if e.key == pygame.K_ESCAPE and not self.mainMenu.open: 
                    if not self.paused: self.optionMenu.main()
                    else: self.optionMenu.closeTransition()


                # if the game is not paused and the main menu isnt open and no text inputs are open
                if not self.paused and not self.mainMenu.open and not self.textHandler.getActive():
                    # Show / Hide the different layers depending on key press
                    if pygame.key.name(e.key) == config["controls"]["layer1"]:
                        self.spriteRenderer.showLayer(1)
                        self.mapEditor.showLayer(1)

                    elif pygame.key.name(e.key) == config["controls"]["layer2"]:
                        self.spriteRenderer.showLayer(2)
                        self.mapEditor.showLayer(2)

                    elif pygame.key.name(e.key) == config["controls"]["layer3"]:
                        self.spriteRenderer.showLayer(3)
                        self.mapEditor.showLayer(3)

                    elif pygame.key.name(e.key) == config["controls"]["layer4"]:
                        self.spriteRenderer.showLayer(4)
                        self.mapEditor.showLayer(4)
            else:
                self.textHandler.setPressed(False)

            self.clickManager.setClicked(True) if e.type == pygame.MOUSEBUTTONDOWN else self.clickManager.setClicked(False)


    def run(self):
        #main menu
        self.mainMenu.main()

        # Game loop
        while self.playing:
            self.renderer.prepareSurface(CREAM)
            self.__events()
            self.dt = self.clock.tick() / 1000

            # Prevent game from updating if window is being moved?
            if self.dt >= 0.05:
                continue

            self.__update()
            self.__draw()

        self.running = False

    def __update(self):
        if not self.paused and not self.mainMenu.open:
            self.spriteRenderer.update()
            self.mapEditor.update()


    def __draw(self):
        #add sprites
        self.spriteRenderer.render()
        self.mapEditor.render()

        #add menus when not paused
        if self.paused: self.optionMenu.display() #To Do: Different option menus for sprite renderer and level editor
        if self.mainMenu.open: self.mainMenu.display()

        # render everything
        self.renderer.render()



if __name__ == "__main__":
    g = Game()
    g.run()
    # cProfile.run('g.run()')
    pygame.quit()
