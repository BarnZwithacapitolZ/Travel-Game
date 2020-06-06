import pygame
import sys
import os

#insert directory paths
sys.path.insert(0, 'menu')
sys.path.insert(0, 'sprites')

from config import *
from engine import *
from menu import *
from sprites import *
from menuComponents import *


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

        self.renderer = Renderer()
        self.clickManager = ClickManager(self)
        self.imageLoader = ImageLoader()
        self.mainMenu = MainMenu(self)
        self.optionMenu = OptionMenu(self)
        self.hud = Hud(self)

        self.spriteRenderer = SpriteRenderer(self)

        if self.fullscreen:
            self.renderer.setFullscreen()

        self.setCaption()
        self.setIcon()

    def setCaption(self):
        pygame.display.set_caption(config["game"]["gameTitle"])

    def setIcon(self):
        icon = self.imageLoader.getImage(config["game"]["icon"])
        pygame.display.set_icon(icon)


    def __quit(self):
        self.playing = False


    def __events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__quit()

            if e.type == pygame.VIDEORESIZE:
                self.renderer.setScale(e.size, self.fullscreen)
                self.spriteRenderer.resize()
                self.optionMenu.resize()
                self.mainMenu.resize()
                self.hud.resize()
               

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE and not self.mainMenu.open:
                    self.paused = not self.paused

                    self.hud.open = not self.hud.open
                    if self.paused: self.optionMenu.main()
                    else: self.optionMenu.close()

                if e.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen

                    if self.fullscreen: self.renderer.setFullscreen()
                    else: self.renderer.unsetFullscreen()

                if not self.paused:
                    if pygame.key.name(e.key) == config["controls"]["layer1"]:
                        self.spriteRenderer.showLayer(1)

                    if pygame.key.name(e.key) == config["controls"]["layer2"]:
                        self.spriteRenderer.showLayer(2)

                    if pygame.key.name(e.key) == config["controls"]["layer3"]:
                        self.spriteRenderer.showLayer(3)

                    if pygame.key.name(e.key) == config["controls"]["layer4"]:
                        self.spriteRenderer.showLayer(4)


            if e.type == pygame.MOUSEBUTTONDOWN:
                self.optionMenu.setClicked(True)
                self.mainMenu.setClicked(True)
                self.hud.setClicked(True)
                self.clickManager.setClicked(True)
            else:
                self.optionMenu.setClicked(False)
                self.mainMenu.setClicked(False)
                self.hud.setClicked(False)
                self.clickManager.setClicked(False)


    def run(self):
        self.spriteRenderer.createLevel()

        #main menu
        self.mainMenu.main()
        self.hud.main()

        # Game loop
        while self.playing:
            self.renderer.prepareSurface(CREAM)
            self.__events()
            self.dt = self.clock.tick(60) / 1000
            self.__update()
            self.__draw()

            # print(self.clock.get_fps())
            # print(pygame.mouse.get_pos())

        self.running = False

    def __update(self):
        if not self.paused and not self.mainMenu.open:
            self.spriteRenderer.update()


    def __draw(self):
        #add sprites
        self.spriteRenderer.render()

        #add menus when not paused
        if not self.mainMenu.open: self.hud.display()
        if self.paused: self.optionMenu.display()
        if self.mainMenu.open: self.mainMenu.display()

        # render everything
        self.renderer.render()



if __name__ == "__main__":
    g = Game()

    while g.running:
        g.run()
    pygame.quit()
