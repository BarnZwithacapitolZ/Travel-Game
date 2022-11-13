import random
import numpy
from node import NodeType
from pygame.locals import BLEND_MIN
from config import HOVERGREY, LAYERCOLORS
from utils import overrides, vec, checkKeyExist, getMousePos
from enum import Enum, auto
from sprite import Sprite
from entity import Particle, Decorators, StatusIndicator


class Person(Sprite):
    newid = 0

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

        # Return a list of types which allow the person to move
        @classmethod
        def aslist(cls):
            return [
                cls.UNASSIGNED, cls.WAITING, cls.BOARDING, cls.WALKING,
                cls.FLAG]

    def __init__(
            self, spriteRenderer, groups, spawnDestinations, possibleSpawns,
            possibleDestinations, clickManagers=[]):
        super().__init__(spriteRenderer, groups, clickManagers)
        self.clickManager = self.clickManagers[0]
        self.transportClickManager = self.clickManagers[1]
        self.width, self.height = 20, 20

        Person.newid += 1
        self.id = Person.newid

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

        # Defines which layer the person can 'walk' on.
        self.startingConnectionType = "layer 2"

        # Defines which layer the person is currently on.
        self.currentConnectionType = self.currentNode.connectionType

        # -10, -20 # Move it back 10 pixels x, 20 pixels y
        self.offset = vec(-10, -15)
        self.pos = (
            self.currentNode.pos + self.offset) - self.currentNode.offset
        self.vel = vec(0, 0)

        self.speed = 20
        self.path = []

        self.travellingOn = None

        self.active = True
        self.status = Person.Status.UNASSIGNED

        self.imageName = "personGrey"  # Default Name

        self.timer = random.randint(70, 100)
        self.timerReached = False

        self.statusIndicator = StatusIndicator(self.groups, self)
        self.outline = Decorators((
            self.spriteRenderer.allSprites,
            self.spriteRenderer.aboveEntities), self, [self.clickManager])
        self.outline.addDecorator('outline')
        self.outline.addDecorator(
            'destination', {'destination': self.destination})

        self.decorators = Decorators(self.groups, self, [self.clickManager])
        self.decorators.addDecorator('timer')
        self.decorators.addDecorator('timerOutline')
        self.decorators.addDecorator('timerTime')
        self.decorators.addDecorator('path', {'path': self.path})

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
                if node.getSubType() in person.getPossibleSpawns():
                    possiblePlayerTypes[person].setdefault(
                        'spawns', []).append(node)

                elif node.getSubType() in person.getPossibleDestinations():
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
                indexes = [j for j, _ in enumerate(weights) if j != i]
                for k in indexes:
                    weights[k] += (occurances * 10) / (
                        len(finalPlayerTypes) - 1)

        return finalPlayerTypes, weights

    def spawnAnimation(self):
        Particle((
            self.spriteRenderer.allSprites,
            self.spriteRenderer.belowEntities), self)
        self.game.audioLoader.playSound("playerSpawn", 1)

    def getId(self):
        return self.id

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

    def getPossibleDestinations(self):
        return self.possibleDestinations

    def getDestination(self):
        return self.destination

    def getTravellingOn(self):
        return self.travellingOn

    def getActive(self):
        return self.active

    def setActive(self, active):
        self.active = active

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

        # If the destination is one of the persons possible destinations
        # and not the node the player is currently on
        for destination in destinations:
            if (destination.getSubType() in self.possibleDestinations
                    and destination.getNumber() != self.spawn.getNumber()):
                possibleDestinations.append(destination)

        # Its a better destination if its a different type from the spawn
        for destination in possibleDestinations:
            if destination.getSubType() != self.spawn.getSubType():
                betterDestinations.append(destination)

        if len(betterDestinations) > 0:
            possibleDestinations = betterDestinations

        destination = random.randint(0, len(possibleDestinations) - 1)
        self.destination = possibleDestinations[destination]

    def setSpawn(self, spawns=[]):
        sequence = checkKeyExist(
            self.spriteRenderer.getLevelData(), ['options', 'setSpawn'], [])

        # Loop back around
        if self.spriteRenderer.getSequence() >= len(sequence):
            self.spriteRenderer.setSequence(0)

        # for spawn in spawns:
        #     if spawn.getSubType() in self.possibleSpawns:
        #         possibleSpawns.append(spawn)

        if len(sequence) > 0:
            # If a sequence number doesn't match a spawn location set it to -1
            sequence = [s.getNumber() if s.getNumber() == sequence[
                self.spriteRenderer.getSequence()] else -1 for s in spawns]
        # get the index of any nonegative sequence number, or randomly allocate
        i = next((
            i for i, x in enumerate(sequence) if x != -1),
            random.randint(0, len(spawns) - 1))

        self.spawn = spawns[i]
        self.spriteRenderer.setSequence(self.spriteRenderer.getSequence() + 1)

    def setImageName(self):
        color = LAYERCOLORS[int(self.currentConnectionType[-1])]['name']
        newName = "person" + color.capitalize()

        if self.imageName != newName:
            self.imageName = newName
            self.dirty = True

    @overrides(Sprite)
    def kill(self):
        self.currentNode.removePerson(self)
        self.currentNode.getPersonHolder().removePerson(self)

        if self.travellingOn is not None:
            self.travellingOn.removePerson(self)

        self.spriteRenderer.getGridLayer(
            self.currentConnectionType).removePerson(self)

        self.spriteRenderer.setTotalPeople(
            self.spriteRenderer.getTotalPeople() - 1)

        self.game.clickManager.resetMouseOver()

        # Call the sprite kill methods that deleted the sprite from memory
        super().kill()

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

        self.path.clear()

    def complete(self):
        self.game.audioLoader.playSound("playerSuccess", 1)
        self.spriteRenderer.addToCompleted()
        self.kill()

    # Switch the person and their status indicator from one
    # layer to a new layer
    def switchLayer(self, oldLayer, newLayer):
        self.removeFromLayer(oldLayer)
        self.addToLayer(newLayer)
        self.currentConnectionType = self.currentNode.connectionType
        self.setImageName()

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
        self.statusIndicator.rect.topleft = self.getTopLeft(
            self.statusIndicator)

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.imageName, (
            self.width * self.spriteRenderer.getFixedScale(),
            self.height * self.spriteRenderer.getFixedScale()))

        self.rect = self.image.get_rect()
        self.rect.topleft = self.getTopLeft(self)

    @overrides(Sprite)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Sprite)
    def events(self):
        if self.game.mainMenu.getOpen():
            return
        mx, my = getMousePos(self.game)

        # If the mouse is clicked, but not on a person,
        # unset the person from the clickmanager (no one clicked)
        # Unlick event
        if (not self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and not self.spriteRenderer.getHud().getHudButtonHoverOver()):
            self.clickManager.setNode(None)
            self.clickManager.setPerson(None)

        # Click event
        elif (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and (
                    self.spriteRenderer.getCurrentLayerString()
                    == self.currentNode.getConnectionType()
                    or self.spriteRenderer.getCurrentLayer() == 4)
                and self.game.clickManager.getMouseOver() == self):
            # Click off the transport (if selected)
            if self.transportClickManager.getTransport() is not None:
                self.transportClickManager.setTransport(None)

            # The person holder currently open
            holder = (
                self.spriteRenderer.getPersonHolderClickManager()
                .getPersonHolder())
            if holder is not None and self not in holder.getPeople():
                holder.closeHolder(True)

            # Must clear the node before setting the
            # person so that path remains clear
            self.clickManager.setNode(None)
            self.clickManager.setPerson(self)
            self.game.clickManager.setClicked(False)

            # Don't let the user manipulate the players state
            # if the game is paused
            if self.spriteRenderer.getPaused():
                return

            elif self.status == Person.Status.UNASSIGNED:
                self.game.audioLoader.playSound("uiStartSelect", 2)
                # People can wait at stops and destinations only
                if (self.currentNode.getType() == NodeType.STOP
                        or self.currentNode.getType()
                        == NodeType.DESTINATION):
                    self.status = Person.Status.WAITING

                elif self.currentNode.getType() == NodeType.REGULAR:
                    self.status = Person.Status.FLAG

            elif self.status == Person.Status.WAITING:
                # toggle between waiting for a bus and flagging a taxi
                # or if its a desintation on layer 2
                if (self.currentNode.getSubType() == NodeType.BUSSTOP
                        or (self.currentNode.getType()
                            == NodeType.DESTINATION
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

            elif (self.status == Person.Status.BOARDING
                    or self.status == Person.Status.BOARDINGTAXI):
                self.game.audioLoader.playSound("uiCancel", 2)
                self.status = Person.Status.UNASSIGNED

            elif self.status == Person.Status.MOVING:
                self.game.audioLoader.playSound("uiStartSelect", 2)
                self.status = Person.Status.DEPARTING

            elif self.status == Person.Status.DEPARTING:
                self.game.audioLoader.playSound("uiCancel", 2)
                self.status = Person.Status.MOVING

        # Hover over event
        elif (self.rect.collidepoint((mx, my)) and not self.mouseOver
                and (
                    self.spriteRenderer.getCurrentLayerString()
                    == self.currentNode.getConnectionType()
                    or self.spriteRenderer.getCurrentLayer() == 4)
                and self.game.clickManager.isTop(self)
                and self.canClick):
            self.mouseOver = True
            self.game.clickManager.setMouseOver(self)
            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.dirty = False

        # Hover out event
        elif not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.game.clickManager.setMouseOver(None)
            self.dirty = True

    @overrides(Sprite)
    def update(self):
        if not hasattr(self, 'rect'):
            return

        # mouse over and click events first
        if self.active:
            self.events()

        self.vel = vec(0, 0)

        # Everything beyond here will NOT be called if the
        # spriteRenderer is paused
        if self.spriteRenderer.getPaused():
            return

        # We don't want to decrease the timer if there are no lives,
        # since then there is no "challenge"
        if self.spriteRenderer.getLives() is not None:
            self.timer -= self.game.dt * self.spriteRenderer.getDt()

        if self.timer <= 20 and self.timer > 0:
            # So that it is only called once
            if not self.timerReached:
                self.game.audioLoader.playSound("playerAlert", 1)
            self.timerReached = True

        elif self.timer <= 0:
            self.game.audioLoader.playSound("playerFailure", 1)
            self.spriteRenderer.removeLife()
            self.kill()

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
            self.rect.topleft = self.getTopLeft(self)


class Manager(Person):
    def __init__(self, renderer, groups, spawnDestinations, clickManagers=[]):
        super().__init__(
            renderer, groups, spawnDestinations, Manager.getPossibleSpawns(),
            Manager.getPossibleDestinations(), clickManagers)
        # self.imageName = "manager"

    @staticmethod
    def getPossibleSpawns():
        return (NodeType.HOUSE, NodeType.OFFICE)

    @staticmethod
    def getPossibleDestinations():
        return (NodeType.OFFICE, NodeType.HOUSE)

    # Office, airport
    # has a very high budget so can afford taxis etc.


class Commuter(Person):
    def __init__(
            self, renderer, groups, spawnDestinations, clickManagers=[]):
        super().__init__(
            renderer, groups, spawnDestinations, Commuter.getPossibleSpawns(),
            Commuter.getPossibleDestinations(), clickManagers)
        # self.imageName = "person"

    @staticmethod
    def getPossibleSpawns():
        return (NodeType.HOUSE, NodeType.AIRPORT)

    @staticmethod
    def getPossibleDestinations():
        return (NodeType.AIRPORT, NodeType.HOUSE)

    # Office, home?
    # has a small budget so cant rly afford many taxis etc.
