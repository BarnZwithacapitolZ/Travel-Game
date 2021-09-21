import pygame
import random
import math
import numpy
import node as NODE
from pygame.locals import BLEND_MIN
from config import YELLOW, BLACK, WHITE, HOVERGREY
from enum import Enum, auto

vec = pygame.math.Vector2


class Person(pygame.sprite.Sprite):
    # Players different status's
    class Status(Enum):
        UNASSIGNED = auto()
        WALKING = auto()
        WAITING = auto()
        BOARDING = auto()
        BOARDINGTAXI = auto()
        MOVING = auto()
        DEPARTING = auto()
        FLAG = auto()

    def __init__(
            self, spriteRenderer, groups, clickManager, transportClickManager,
            spawnDestinations, possibleSpawns, possibleDestinations):
        self.groups = groups
        super().__init__(self.groups)
        self.spriteRenderer = spriteRenderer
        self.clickManager = clickManager
        self.transportClickManager = transportClickManager
        self.game = self.spriteRenderer.game
        self.width = 20
        self.height = 20

        # List of possible destinations that the player can have
        # (different player types might have different
        # destinatiosn that they go to)
        self.possibleSpawns = possibleSpawns
        self.possibleDestinations = possibleDestinations
        self.spawnDestinations = spawnDestinations
        self.destination = None
        self.spawn = None

        self.setSpawn(self.spawnDestinations)
        self.setDestination(self.spawnDestinations)

        self.currentNode = self.spawn

        # always start on the second layer
        self.startingConnectionType = "layer 2"
        self.currentConnectionType = self.currentNode.connectionType

        # -10, -20 # Move it back 10 pixels x, 20 pixels y
        self.offset = vec(-10, -15)
        self.pos = (
            self.currentNode.pos + self.offset) - self.currentNode.offset
        self.vel = vec(0, 0)

        self.speed = 20
        self.budget = 20
        self.path = []

        self.travellingOn = None

        self.mouseOver = False
        self.clicked = False
        self.canClick = True
        self.status = Person.Status.UNASSIGNED

        self.dirty = True

        self.imageName = "person"

        self.statusIndicator = StatusIndicator(self.game, self.groups, self)

        self.timer = random.randint(70, 100)
        self.timerReached = False
        self.rad = 5
        self.step = 15

        self.entities = []

        # Switch to the layer that the player spawned on
        self.switchLayer(
            self.startingConnectionType, self.currentConnectionType)

        # Add the person to the node after they have switched to the correct
        # layer to stop it adding the player back when
        # removed if in personHolder
        self.currentNode.addPerson(self)
        self.currentNode.getPersonHolder().addPerson(self)
        self.spawnAnimation()

    # static function to check which player types can spawn on the map
    # dependent on the desitations available
    @staticmethod
    def checkPeopleTypes(peopleTypes, previousPeopleTypes, spawnDestinations):
        possiblePlayerTypes = {}
        finalPlayerTypes = []

        for person in peopleTypes:
            possiblePlayerTypes[person] = {}
            for node in spawnDestinations:
                if isinstance(node, person.getPossibleSpawns()):
                    possiblePlayerTypes[person].setdefault(
                        'spawns', []).append(node)

                elif isinstance(node, person.getPossibleDestinations()):
                    possiblePlayerTypes[person].setdefault(
                        'destinations', []).append(node)

        for person, spawnDestinations in possiblePlayerTypes.items():
            # if there is more than one spawn node,
            # we know there are two different types (spawn and destination)
            if ('spawns' in spawnDestinations
                    and len(spawnDestinations['spawns']) > 1):
                finalPlayerTypes.append(person)
                continue

            elif ('spawns' in spawnDestinations
                    and 'destinations' in spawnDestinations):
                finalPlayerTypes.append(person)
                continue

        # no players can spawn
        if len(finalPlayerTypes) <= 0:
            return [], []

        weights = numpy.full(
            shape=len(finalPlayerTypes),
            fill_value=100 / len(finalPlayerTypes), dtype=numpy.int)

        # If there is only ever one player type that can spawn it will always
        # be 100% weight
        if len(finalPlayerTypes) > 1:
            for i in range(len(finalPlayerTypes)):
                occurances = previousPeopleTypes.count(finalPlayerTypes[i])
                weights[i] -= (occurances * 10)
                indexes = [j for j, x in enumerate(weights) if j != i]
                for k in indexes:
                    weights[k] += (occurances * 10) / (
                        len(finalPlayerTypes) - 1)

        return finalPlayerTypes, weights

    def spawnAnimation(self):
        Particle(self.game, (
            self.spriteRenderer.allSprites,
            self.spriteRenderer.entities), self)

        self.game.audioLoader.playSound("playerSpawn", 1)

    # Return the current status (Status) of the person
    def getStatus(self):
        return self.status

    # Return the status value (int) of the person
    def getStatusValue(self):
        return self.status.value

    # Return the current node that the person is at
    def getCurrentNode(self):
        return self.currentNode

    # Return the current connection type of the person
    def getCurrentConnectionType(self):
        return self.currentConnectionType

    # Return the connection type that the person started at
    def getStartingConnectionType(self):
        return self.startingConnectionType

    def getMouseOver(self):
        return self.mouseOver

    def getPossibleDestinations(self):
        return self.possibleDestinations

    def getBudget(self):
        return self.budget

    def getDestination(self):
        return self.destination

    def getTravellingOn(self):
        return self.travellingOn

    def getEntities(self):
        return self.entities

    def getCanClick(self):
        return self.canClick

    def setCanClick(self, canClick):
        self.canClick = canClick

    def setClicked(self, clicked):
        self.clicked = clicked

    # Set the persons status
    def setStatus(self, status):
        self.status = status

    # Set the current node that the person is at
    def setCurrentNode(self, node):
        self.currentNode = node

    def setPosition(self, pos):
        self.pos = pos
        self.dirty = True

    def setTravellingOn(self, travellingOn):
        self.travellingOn = travellingOn

    def setDestination(self, destinations=[]):
        possibleDestinations = []
        betterDestinations = []
        for destination in destinations:
            # If the destination is one of the persons possible destinations
            # and not the node the player is currently on
            if (isinstance(destination, self.possibleDestinations)
                    and destination.getNumber() != self.spawn.getNumber()):
                possibleDestinations.append(destination)

        for desintation in possibleDestinations:
            if not isinstance(desintation, type(self.spawn)):
                betterDestinations.append(desintation)

        if len(betterDestinations) > 0:
            possibleDestinations = betterDestinations

        destination = random.randint(0, len(possibleDestinations) - 1)
        self.destination = possibleDestinations[destination]

    def setSpawn(self, spawns=[]):
        possibleSpawns = []
        for spawn in spawns:
            if isinstance(spawn, self.possibleSpawns):
                possibleSpawns.append(spawn)

        spawn = random.randint(0, len(possibleSpawns) - 1)
        self.spawn = possibleSpawns[spawn]

    def setEntities(self, entities):
        self.entities = entities

    def remove(self):
        self.currentNode.removePerson(self)
        self.currentNode.getPersonHolder().removePerson(self)

        self.spriteRenderer.getGridLayer(
            self.currentConnectionType).removePerson(self)

        self.kill()
        self.statusIndicator.kill()

        self.spriteRenderer.setTotalPeople(
            self.spriteRenderer.getTotalPeople() - 1)

    def addEntity(self, entity):
        self.entities.append(entity)

    # Add a node to the persons path
    def addToPath(self, node):
        self.path.append(node)

    # Remove a node from the persons path
    def removeFromPath(self, node):
        self.path.remove(node)

    # Clear the players path by removing all nodes
    # TODO: FIX PLAYER WALKING BACK TO CURRENT NODE WHEN NEW PATH IS ASSINGNED
    def clearPath(self, newPath):
        # Always remove the player from the first current node when walking
        # ( > 1 path)
        if len(newPath) > 1:
            self.currentNode.getPersonHolder().removePerson(self)

        # When clicking on the same node with no previous path, either switch
        # to the new layer or do nothing (remove path)
        elif len(newPath) == 1 and len(self.path) <= 0:
            if (newPath[0].getConnectionType()
                    == self.currentNode.getConnectionType()):
                del newPath[0]

            else:
                self.currentNode.getPersonHolder().removePerson(self)

        if len(self.path) <= 0 or len(newPath) <= 0:
            return

        # The new path is going in the same direction, so we delete its
        # starting node since the player has already passed this
        if self.path[0] in newPath and self.path[0] != self.currentNode:
            del newPath[0]

        self.path = []

    def complete(self):
        self.game.audioLoader.playSound("playerSuccess", 1)
        self.spriteRenderer.addToCompleted()
        self.remove()

    # Switch the person and their status indicator from one
    # layer to a new layer
    def switchLayer(self, oldLayer, newLayer):
        self.removeFromLayer(oldLayer)
        self.addToLayer(newLayer)
        self.currentConnectionType = self.currentNode.connectionType

        if (self.spriteRenderer.getCurrentLayerString()
                == self.currentConnectionType):
            self.spriteRenderer.resetPeopleClicks()

        if len(self.path) <= 0:
            self.currentNode.getPersonHolder().removePerson(self, True)
            self.currentNode.getPersonHolder().addPerson(self)

    def addToLayer(self, layer=None):
        layerName = layer if layer is not None else self.currentConnectionType
        layer = self.spriteRenderer.getSpriteLayer(layerName)
        layer.add(self)
        layer.add(self.statusIndicator)

        gridLayer = self.spriteRenderer.getGridLayer(layerName)
        gridLayer.addPerson(self)

    def removeFromLayer(self, layer=None):
        layerName = layer if layer is not None else self.currentConnectionType
        layer = self.spriteRenderer.getSpriteLayer(layerName)
        layer.remove(self)
        layer.remove(self.statusIndicator)

        gridLayer = self.spriteRenderer.getGridLayer(layerName)
        gridLayer.removePerson(self)

    # Move the status indicator above the plerson so follow the
    # persons movement
    def moveStatusIndicator(self):
        if not hasattr(self.statusIndicator, 'rect'):
            return

        self.statusIndicator.pos = self.pos + self.statusIndicator.offset
        self.statusIndicator.rect.topleft = (
            self.statusIndicator.pos * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

    # Visualize the players path by drawing the connection between each node
    # in the path
    def drawPath(self, surface):
        if len(self.path) <= 0:
            return

        start = self.path[0]
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        thickness = 3

        for previous, current in zip(self.path, self.path[1:]):
            posx = ((previous.pos - previous.offset) + vec(10, 10)) * scale
            posy = ((current.pos - current.offset) + vec(10, 10)) * scale

            pygame.draw.line(
                surface, YELLOW, posx, posy, int(thickness * scale))

        # Connection from player to the first node in the path
        startx = ((self.pos - self.offset) + vec(10, 10)) * scale
        starty = ((start.pos - start.offset) + vec(10, 10)) * scale
        pygame.draw.line(
            surface, YELLOW, startx, starty, int(thickness * scale))

    def drawTimerOutline(self, surface):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        thickness = 4

        start = (self.pos - self.offset) + vec(7, -10)
        middle = (self.pos + vec(30, -40))
        end = middle + vec(30, 0)

        pygame.draw.lines(
            surface, YELLOW, False,
            [start * scale, middle * scale, end * scale],
            int(thickness * scale))

    def drawTimerTime(self, surface=None):
        textColor = (
            WHITE if self.spriteRenderer.getDarkMode() else BLACK)

        self.fontImage = self.timerFont.render(
            str(round(self.timer, 1)), True, textColor)

        rect = ((
            self.pos + vec(32, -35)) * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        if surface is None:
            self.game.renderer.addSurface(self.fontImage, (rect))
        else:
            surface.blit(self.fontImage, (rect))

    # Draw how long is left at each stop
    def drawTimer(self, surface):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        length = 20

        # Arc Indicator
        offx = 0.01
        step = self.timer / (length / 2) + 0.02
        for x in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.pos.x - 4) * scale, (self.pos.y - 4) * scale,
                    (self.width + 8) * scale, (self.height + 8) * scale),
                math.pi / 2 + offx, math.pi / 2 + math.pi * step,
                int(4 * scale))

            offx += 0.01

    def drawDestination(self, surface):
        if self.destination is None:
            return

        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        thickness = 4

        pos = (self.destination.pos - vec(self.rad, self.rad)) * scale
        size = vec(
            self.destination.width + (self.rad * 2),
            self.destination.height + (self.rad * 2)) * scale
        rect = pygame.Rect(pos, size)

        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.topleft + (vec(0, 10) * scale), rect.topleft,
                rect.topleft + (vec(10, 0) * scale)], int(thickness * scale))
        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.topright + (vec(-10, 0) * scale), rect.topright,
                rect.topright + (vec(0, 10) * scale)], int(thickness * scale))
        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.bottomleft + (vec(0, -10) * scale), rect.bottomleft,
                rect.bottomleft + (vec(10, 0) * scale)],
            int(thickness * scale))
        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.bottomright + (vec(-10, 0) * scale), rect.bottomright,
                rect.bottomright + (vec(0, -10) * scale)],
            int(thickness * scale))

    def drawOutline(self, surface):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        offx = 0.01
        for x in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.pos.x) * scale, (self.pos.y) * scale,
                    (self.width) * scale, (self.height) * scale),
                math.pi / 2 + offx, math.pi / 2, int(3.5 * scale))

            offx += 0.02

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.imageName, (
            self.width * self.spriteRenderer.getFixedScale(),
            self.height * self.spriteRenderer.getFixedScale()))

        self.rect = self.image.get_rect()

        self.rect.topleft = (
            self.pos * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        # do I need the fixed scale to change here?
        self.timerFont = pygame.font.Font(
            pygame.font.get_default_font(),
            int(15 * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale()))

    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    def drawPaused(self, surface):
        self.makeSurface()

        # Want to draw the timer behind the transport
        if self.timer <= 20:
            self.drawTimer(surface)

        surface.blit(self.image, (self.rect))

    def draw(self):
        self.makeSurface()
        self.game.renderer.addSurface(self.image, (self.rect))

        if self.mouseOver or self.clickManager.getPerson() == self:
            self.drawTimerTime()
            self.drawDestination(self.game.renderer.gameDisplay)
            self.game.renderer.addSurface(None, None, self.drawTimerOutline)

        # Visualize the players path
        if self.clickManager.getPerson() == self:
            self.drawPath(self.game.renderer.gameDisplay)
            self.game.renderer.addSurface(None, None, self.drawOutline)

        if self.timer <= 20:
            if not self.timerReached:
                self.game.audioLoader.playSound("playerAlert", 1)
            self.timerReached = True
            self.game.renderer.addSurface(None, None, self.drawTimer)

    def events(self):
        self.vel = vec(0, 0)

        mx, my = pygame.mouse.get_pos()
        difference = self.game.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        # If the mouse is clicked, but not on a person,
        # unset the person from the clickmanager (no one clicked)
        # Unlick event
        if (not self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and not self.spriteRenderer.getHud().getHudButtonHoverOver()):
            self.clickManager.setPerson(None)

        # Click event
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()):
            if self.currentNode.getMouseOver():
                return

            # Click off the transport (if selected)
            if self.transportClickManager.getTransport() is not None:
                self.transportClickManager.setTransport(None)

            # The person holder currently open
            holder = (
                self.spriteRenderer.getPersonHolderClickManager()
                .getPersonHolder())

            if (holder is not None and self not in holder.getPeople()):
                holder.closeHolder(True)

            # Set the person to be moved
            self.clickManager.setPerson(self)
            self.game.clickManager.setClicked(False)

            # Don't let the user manipulate the players state
            # if the game is paused
            if self.spriteRenderer.getPaused():
                return

            if self.status == Person.Status.UNASSIGNED:
                self.game.audioLoader.playSound("uiStartSelect", 2)
                if (isinstance(self.currentNode, NODE.Stop)
                        or isinstance(self.currentNode, NODE.Destination)):
                    self.status = Person.Status.WAITING

                elif isinstance(self.currentNode, NODE.Node):
                    self.status = Person.Status.FLAG

            elif self.status == Person.Status.WAITING:
                # toggle between waiting for a bus and flagging a taxi
                # or if its a desintation on layer 2
                if (isinstance(self.currentNode, NODE.BusStop)
                        or (isinstance(self.currentNode, NODE.Destination)
                            and self.currentNode.getConnectionType()
                            == "layer 2")):
                    self.game.audioLoader.playSound("uiIncreaseSelect", 2)
                    self.status = Person.Status.FLAG

                else:
                    self.game.audioLoader.playSound("uiCancel", 2)
                    self.status = Person.Status.UNASSIGNED

            elif self.status == Person.Status.FLAG:
                self.game.audioLoader.playSound("uiCancel", 2)
                self.status = Person.Status.UNASSIGNED

            elif self.status == Person.Status.BOARDING:
                self.game.audioLoader.playSound("uiCancel", 2)
                self.status = Person.Status.UNASSIGNED

            elif self.status == Person.Status.MOVING:
                self.game.audioLoader.playSound("uiStartSelect", 2)
                self.status = Person.Status.DEPARTING

            elif self.status == Person.Status.DEPARTING:
                self.game.audioLoader.playSound("uiStartSelect", 2)
                self.status = Person.Status.MOVING

        # Hover over event
        if self.rect.collidepoint((mx, my)) and not self.mouseOver:
            # hover over a node when person is hovered over,
            # unset the hover on the node
            if self.currentNode.getMouseOver():
                self.currentNode.setMouseOver(False)

            # hover over a transport when person is hovered over,
            # unset the hover on the transport
            for transport in self.currentNode.getTransports():
                if transport.getMouseOver():
                    transport.setMouseOver(False)

            if self.travellingOn is not None:
                self.travellingOn.setMouseOver(False)

            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.mouseOver = True

        # Hover out event
        if not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.dirty = True

    def update(self):
        if not hasattr(self, 'rect'):
            return

        # mouse over and click events first
        if self.canClick:
            self.events()

        self.rad += self.step * self.game.dt * self.spriteRenderer.getDt()

        # Increase the radius of the selector showing the destination
        if self.rad > 10 and self.step > 0 or self.rad <= 5 and self.step < 0:
            self.step = -self.step

        # Everything beyond here will NOT be called if the
        # spriteRenderer is paused
        if self.spriteRenderer.getPaused():
            return

        self.timer -= self.game.dt * self.spriteRenderer.getDt()

        if self.timer <= 0:
            self.game.audioLoader.playSound("playerFailure", 1)
            self.spriteRenderer.removeLife()
            self.remove()

        if self.currentNode.getNumber() == self.destination.getNumber():
            self.complete()

        if len(self.path) > 0:
            path = self.path[0]

            dxy = (path.pos - path.offset) - self.pos + self.offset
            dis = dxy.length()

            if dis > 1:
                self.status = Person.Status.WALKING
                self.vel = (
                    dxy / dis * float(self.speed) * self.game.dt
                    * self.spriteRenderer.getDt())
                self.moveStatusIndicator()

            else:
                self.currentNode.removePerson(self)
                self.currentNode = path
                self.currentNode.addPerson(self)
                self.path.remove(path)

                # No more nodes in the path, the person is no longer walking
                # and is unassigned
                if len(self.path) <= 0:
                    self.status = Person.Status.UNASSIGNED
                    self.currentNode.getPersonHolder().addPerson(self)

                if (self.currentConnectionType
                        != self.currentNode.connectionType):
                    self.switchLayer(
                        self.currentConnectionType,
                        self.currentNode.connectionType)

            self.pos += self.vel
            self.rect.topleft = (
                self.pos * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())


class Manager(Person):
    def __init__(
            self, renderer, groups, clickManager, transportClickManager,
            spawnDestinations):
        super().__init__(
            renderer, groups, clickManager, transportClickManager,
            spawnDestinations, Manager.getPossibleSpawns(),
            Manager.getPossibleDestinations())
        self.budget = 40
        self.imageName = "manager"

    @staticmethod
    def getPossibleSpawns():
        return (NODE.House, NODE.Office)

    @staticmethod
    def getPossibleDestinations():
        return (NODE.Office, NODE.House)

    # Office, airport
    # has a very high budget so can afford taxis etc.


class Commuter(Person):
    def __init__(
            self, renderer, groups, clickManager, transportClickManager,
            spawnDestinations):
        super().__init__(
            renderer, groups, clickManager, transportClickManager,
            spawnDestinations, Commuter.getPossibleSpawns(),
            Commuter.getPossibleDestinations())
        self.budget = 12
        self.imageName = "person"

    @staticmethod
    def getPossibleSpawns():
        return (NODE.House, NODE.Airport)

    @staticmethod
    def getPossibleDestinations():
        return (NODE.Airport, NODE.House)

    # Office, home?
    # has a small budget so cant rly afford many taxis etc.


class StatusIndicator(pygame.sprite.Sprite):
    def __init__(self, game, groups, currentPerson):
        self.groups = groups
        super().__init__(self.groups)
        self.game = game
        self.currentPerson = currentPerson
        self.spriteRenderer = self.currentPerson.spriteRenderer

        self.width = 10
        self.height = 10

        self.offset = vec(-2.5, -10)
        self.pos = self.currentPerson.pos + self.offset

        self.dirty = True

        if self.spriteRenderer.getDarkMode():
            self.images = [
                None, "walkingWhite", "waitingWhite", "boardingWhite",
                "boardingWhite", None, "departingWhite", "flagWhite"]

        else:
            self.images = [
                None, "walking", "waiting", "boarding", "boarding", None,
                "departing", "flag"]
        self.currentState = self.currentPerson.getStatusValue() - 1

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(
            self.images[self.currentState], (
                self.width * self.spriteRenderer.getFixedScale(),
                self.height * self.spriteRenderer.getFixedScale()))

        self.rect = self.image.get_rect()

        self.rect.topleft = (
            self.pos * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

    def makeSurface(self):
        if self.images[self.currentState] is None:
            return False

        if self.dirty or self.image is None:
            self.__render()
        return True

    def drawPaused(self, surface):
        if self.makeSurface():
            surface.blit(self.image, (self.rect))

    def draw(self):
        if self.makeSurface():
            self.game.renderer.addSurface(self.image, (self.rect))

    def update(self):
        if (self.currentPerson.getStatusValue() - 1) != self.currentState:
            self.dirty = True
            self.currentState = self.currentPerson.getStatusValue() - 1


class Particle(pygame.sprite.Sprite):
    def __init__(self, game, groups, currentPerson, color=YELLOW):
        self.groups = groups
        super().__init__(self.groups)
        self.game = game
        self.currentPerson = currentPerson
        self.spriteRenderer = self.currentPerson.spriteRenderer
        self.color = color
        self.start, self.end = 100, 0
        self.rad = 0
        self.dirty = True
        self.alpha = self.start

        self.currentPerson.addEntity(self)

    def __render(self):
        self.dirty = False

        self.pos = ((
            self.currentPerson.pos - vec(self.rad, self.rad))
            * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        self.size = (vec(
            self.currentPerson.width + (self.rad * 2),
            self.currentPerson.height + (self.rad * 2))
            * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        self.image = pygame.Surface((self.size)).convert()

        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        pygame.draw.ellipse(self.image, self.color, pygame.Rect(
            0, 0, *self.size))

        self.image.set_alpha(self.alpha, pygame.RLEACCEL)

    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))

    def draw(self):
        self.makeSurface()
        self.game.renderer.addSurface(self.image, (self.rect))

    def update(self):
        self.rad += 60 * self.game.dt * self.spriteRenderer.getDt()
        self.alpha -= 120 * self.game.dt * self.spriteRenderer.getDt()

        if self.alpha < self.end:
            self.kill()
            if len(self.currentPerson.getEntities()) < 3:
                Particle(self.game, self.groups, self.currentPerson)
            else:
                self.currentPerson.setEntities([])

        self.dirty = True
