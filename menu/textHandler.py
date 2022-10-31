import pygame
import string
from config import config


class TextHandler:
    def __init__(self):
        self.active = False
        self.lengthReached = False
        self.pointer = self.previousPointer = 0
        self.string = []

        self.keys = list(string.ascii_letters) + list(string.digits)
        self.keys.append(" ")
        self.currentKey = None

    def getActive(self):
        return self.active

    def getPressed(self):
        return False if self.currentKey is None else True

    def getCurrentKey(self):
        return self.currentKey

    def getLengthReached(self):
        return self.lengthReached

    def getPointer(self):
        return self.pointer

    def getPreviousPointer(self):
        return self.previousPointer

    def getString(self, pointer=False):
        return (
            ''.join(self.string[:self.pointer]) if pointer
            else ''.join(self.string))

    def setCurrentKey(self, currentKey):
        self.currentKey = currentKey

    def setString(self, string=[]):
        self.string = string

    def setLengthReached(self, lengthReached):
        self.lengthReached = lengthReached

    def setPointer(self, pointer):
        if pointer > len(self.string) or pointer < 0:
            return
        self.previousPointer = self.pointer
        self.pointer = pointer

    def setPreviousPointer(self, previousPointer):
        self.previousPointer = previousPointer

    def removeLast(self):
        if self.pointer > 0:
            del self.string[self.pointer - 1]
            self.setPointer(self.pointer - 1)

    # When active clear the text so its ready for input
    def setActive(self, active):
        self.active = active

        if self.active:
            self.string = []
            self.pointer = 0

    def events(self, event):
        self.setCurrentKey(event.key)

        if not self.active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.removeLast()
        else:
            if event.unicode in self.keys and not self.lengthReached:
                if self.pointer == len(self.string):
                    self.string.append(event.unicode)

                else:
                    b = self.string[:]
                    insert = self.pointer
                    b[insert:insert] = [event.unicode]
                    self.string = b

                self.setPointer(self.pointer + 1)

            if event.key == config["controls"]["left"]["current"]:
                self.setPointer(self.pointer - 1)
            elif event.key == config["controls"]["right"]["current"]:
                self.setPointer(self.pointer + 1)
