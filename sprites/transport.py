import pygame
import random
import decimal
import math
import personHolder
import node as NODE
import person as PERSON
from config import HOVERGREY, YELLOW
from pygame.locals import BLEND_MIN
from utils import overrides, vec
from enum import Enum
from sprite import Sprite


class TransportType(Enum):
    METRO = "metro"
    BUS = "bus"
    TRAM = "tram"
    TAXI = "taxi"


class Transport(Sprite):
    def __init__(
            self, spriteRenderer, groups, currentConnection, running,
            clickManagers=[]):
        super().__init__(spriteRenderer, groups, clickManagers)
        self.currentConnection = currentConnection
        self.currentNode = self.currentConnection.getFrom()
        self.currentNode.addTransport(self)
        self.width, self.height = 30, 30

        self.offset = vec(-5, -5)  # -5 is half the offset of the connector
        self.vel = vec(0, 0)
        self.pos = (
            self.currentConnection.getFrom().pos
            - self.currentConnection.getFrom().offset) + self.offset

        self.speed = float(decimal.Decimal(random.randrange(50, 60)))

        self.type = TransportType.METRO

        self.running = running
        self.moving = self.running
        self.timer = 0
        self.timerLength = 300

        self.clickManager = self.clickManagers[0]
        self.personClickManager = self.clickManagers[1]

        # People travelling in the transport
        self.people = []
        self.personHolder = personHolder.PersonHolder(
            self.groups, self,
            self.spriteRenderer.getPersonHolderClickManager())

        self.imageName = "train"
        self.stopType = [NODE.NodeType.METROSTATION, NODE.NodeType.DESTINATION]
        self.boardingType = PERSON.Person.Status.BOARDING

        self.path = []

        # store the first node in the path, before it might be removed
        self.firstPathNode = None

    def getPeople(self):
        return self.people

    def getMoving(self):
        return self.moving

    def getCurrentNode(self):
        return self.currentNode

    def getConnectionType(self):
        if self.currentNode is None:
            return

        return self.currentNode.getConnectionType()

    def setSpeed(self, speed):
        self.speed = speed

    def setMoving(self, moving):
        self.moving = moving

    def setMouseOver(self, mouseOver):
        self.mouseOver = mouseOver
        self.dirty = True

    # Check if a given node is one the transport can stop at
    def checkIsStopType(self, node):
        if (node.getType() in self.stopType
                or node.getSubType() in self.stopType):
            return True
        return False

    # Switch to the next connection in the path,
    # so the player keeps following it
    def setNextPathConnection(self, path):
        if len(self.path) > 1:
            fromNode = path.getConnections()[0].getFrom().getNumber()
            toNode = self.path[1].getNumber()

            for connection in path.getConnections():
                if (connection.getFrom().getNumber() == fromNode
                        and connection.getTo().getNumber() == toNode):
                    self.currentConnection = connection
                    break

            self.currentNode.removeTransport(self)
            self.currentNode = self.currentConnection.getFrom()
            self.currentNode.addTransport(self)

        if (self.firstPathNode is not None and path.getNumber()
                != self.firstPathNode.getNumber()):
            self.firstPathNode = None
        self.path.remove(path)

    def setFirstPathNode(self, path):
        # if there is nodes in the path and the firstpathnode isn't already
        # set and the transport is at a station
        if len(path) >= 1 and self.firstPathNode is None and not self.moving:
            self.firstPathNode = path[0]

        else:
            self.firstPathNode = None

    # Set the connection that the transport will follow next
    def setConnection(self, nextNode):
        totalConnections = []
        possibleConnections = []

        for connection in nextNode.getConnections():
            if (connection.getConnectionType()
                    == self.currentConnection.getConnectionType()):
                totalConnections.append(connection)

        if len(totalConnections) <= 1:
            self.currentConnection = totalConnections[0]

        else:
            for connection in totalConnections:
                fromInt = connection.getFrom().getNumber()
                toInt = connection.getTo().getNumber()
                currentFromInt = self.currentConnection.getFrom().getNumber()
                currentToInt = self.currentConnection.getTo().getNumber()

                if not (fromInt == currentFromInt and toInt == currentToInt
                        or fromInt == currentToInt
                        and toInt == currentFromInt):
                    possibleConnections.append(connection)

            self.currentConnection = possibleConnections[
                random.randint(0, len(possibleConnections) - 1)]

        self.currentNode.removeTransport(self)
        self.currentNode = self.currentConnection.getFrom()
        self.currentNode.addTransport(self)

    # Set the next connection for the transport to follow
    def setNextConnection(self):
        nextNode = self.currentConnection.getTo()

        # If the transport is moving, set its next connection to the
        # next upcoming node
        if self.moving:
            self.setConnection(nextNode)

        # and len(self.currentNode.getPeople()) > 0
        if self.checkIsStopType(self.currentNode):
            # Remove anyone departing before we add new people
            self.removePeople()

            # Set people waiting for the transportation to departing
            self.setPeopleBoarding()

            self.moving = False
            self.timer += 100 * self.game.dt * self.spriteRenderer.getDt()

            # Leaving the station
            if self.timer > self.timerLength:
                self.moving = True
                self.timer = 0

                # Add the people boarding to the transportation
                self.addPeople()

    # Set people waiting at the stop to boarding the transportation
    def setPeopleBoarding(self):
        # If theres no one at the stop, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            # If they're waiting for the train
            if person.getStatus() == PERSON.Person.Status.WAITING:
                person.setStatus(self.boardingType)

    def addToPath(self, node):
        self.path.append(node)

    def clearPath(self, newPath):
        # We want the transport to keep moving in the direction of the
        # selected same node, only if the transport is moving in the
        # first place.
        if len(newPath) == 1 and self.moving:
            connections = self.currentConnection.getTo().getConnections()
            for connection in connections:
                if (connection.getFrom().getNumber()
                        == self.currentConnection.getTo().getNumber()
                        and connection.getTo().getNumber()
                        == newPath[0].getNumber()):
                    self.currentConnection = connection
                    break

            self.currentNode.removeTransport(self)
            self.currentNode = self.currentConnection.getFrom()
            self.currentNode.addTransport(self)

        if len(self.path) <= 0 or len(newPath) <= 0:
            # if the node the transport is currently heading towards is in the
            # new path, then we dont need the first node
            if self.currentConnection.getTo() in newPath:
                del newPath[0]

            return

        if self.path[0] in newPath and self.path[0] != self.currentNode:
            del newPath[0]

        self.path = []

    # Add a person to the transport
    def addPerson(self, person):
        if person in self.people:
            return

        self.people.append(person)

    # Remove a person from the transport
    def removePerson(self, person):
        if person not in self.people:
            return

        self.people.remove(person)

    # Add multiple people who are departing on the transportation
    def addPeople(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in list(self.currentNode.getPeople()):
            # Only remove people from the station once the train is moving
            if person.getStatus() == self.boardingType:
                self.currentNode.removePerson(person)
                self.currentNode.getPersonHolder().removePerson(person)

                self.addPerson(person)
                self.personHolder.addPerson(person)

                person.setStatus(PERSON.Person.Status.MOVING)
                person.setTravellingOn(self)

    # Remove multiple people who are departing from the transportation
    def removePeople(self):
        if len(self.people) <= 0:
            return

        for person in list(self.people):
            if person.getStatus() == PERSON.Person.Status.DEPARTING:
                person.pos = ((
                    self.currentNode.pos - self.currentNode.offset)
                    + person.offset)

                person.rect.topleft = self.getTopLeft(person)

                person.moveStatusIndicator()

                self.removePerson(person)
                self.personHolder.removePerson(person)

                playerNode = self.currentNode
                # Add the player to the top node (on the highest layer)
                # if not the current layer
                if (self.currentNode.getConnectionType()
                        != self.spriteRenderer.getCurrentLayerString()):
                    playerNode = self.spriteRenderer.getTopNode(
                        self.currentNode)

                # Set the person to unassigned so they can be moved
                person.setStatus(PERSON.Person.Status.UNASSIGNED)

                # Set the persons current node to the node they're at
                person.setCurrentNode(playerNode)

                playerNode.addPerson(person)
                playerNode.getPersonHolder().addPerson(person)
                person.switchLayer(
                    self.currentNode.getConnectionType(),
                    playerNode.getConnectionType())
                person.setTravellingOn(None)

    # Move all the people within the transport relative to its location
    def movePeople(self):
        if len(self.people) <= 0:
            return

        if not self.personHolder.getOpen():
            for person in list(self.people):
                person.pos.x = self.pos.x + self.width + person.offset.x
                person.pos.y = self.pos.y + person.offset.y

                person.rect.topleft = self.getTopLeft(person)
                person.moveStatusIndicator()

        # Move the people inside the person holder if it is open
        else:
            self.personHolder.movePeople()

    def movePersonHolder(self):
        if not hasattr(self.personHolder, 'rect'):
            return

        if self.personHolder.getOpen():
            self.personHolder.drawerPos.x = (
                self.pos.x + self.width + self.personHolder.offset.x)
            self.personHolder.drawerPos.y = (
                self.pos.y + self.personHolder.drawerOffset.y)
            self.personHolder.rect.topleft = (
                (self.personHolder.drawerPos + self.spriteRenderer.offset)
                * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())

        else:
            self.personHolder.pos.x = (
                self.pos.x + self.width + self.personHolder.offset.x)
            self.personHolder.pos.y = self.pos.y + self.personHolder.offset.y
            self.personHolder.rect.topleft = self.getTopLeft(self.personHolder)

    # Draw how long is left at each stop
    def drawTimer(self, surface):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        offset = self.spriteRenderer.offset

        # Arc Indicator
        offx = 0.01
        step = self.timer / (self.timerLength / 2) + 0.02
        for x in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.pos.x - 4 + offset.x) * scale,
                    (self.pos.y - 4 + offset.y) * scale,
                    (self.width + 8) * scale, (self.height + 8) * scale),
                math.pi / 2 + offx, math.pi / 2 + math.pi * step,
                int(8 * scale))

            offx += 0.01

    # Visualize the players path by drawing the connection between each node
    # in the path
    def drawPath(self, surface):
        if len(self.path) <= 0:
            return

        start = self.path[0]
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        offset = self.spriteRenderer.offset
        thickness = 3

        for previous, current in zip(self.path, self.path[1:]):
            posx = (
                ((previous.pos - previous.offset) + vec(10, 10) + offset)
                * scale)
            posy = (
                ((current.pos - current.offset) + vec(10, 10) + offset)
                * scale)

            pygame.draw.line(surface, YELLOW, posx, posy, int(
                thickness * scale))

        # Connection from player to the first node in the path
        startx = ((self.pos - self.offset) + vec(10, 10) + offset) * scale
        starty = ((start.pos - start.offset) + vec(10, 10) + offset) * scale
        pygame.draw.line(surface, YELLOW, startx, starty, int(
            thickness * scale))

    def drawOutline(self, surface):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        offset = self.spriteRenderer.offset

        offx = 0.01
        for x in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.pos.x - 2 + offset.x) * scale,
                    (self.pos.y - 2 + offset.y) * scale,
                    (self.width + 4) * scale, (self.height + 4) * scale),
                math.pi / 2 + offx, math.pi / 2, int(4 * scale))

            offx += 0.02

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
    def drawPaused(self, surface):
        self.makeSurface()

        # Want to draw the timer behind the transport
        if self.timer > 0:
            self.drawTimer(surface)

        surface.blit(self.image, (self.rect))

    @overrides(Sprite)
    def draw(self):
        self.makeSurface()
        self.game.renderer.addSurface(self.image, (self.rect))

        if self.timer > 0:
            # Draw the time indicator
            self.drawTimer(self.game.renderer.gameDisplay)

        if self.clickManager.getTransport() == self:
            self.drawPath(self.game.renderer.gameDisplay)
            self.game.renderer.addSurface(None, None, self.drawOutline)

    @overrides(Sprite)
    def events(self):
        if self.game.mainMenu.getOpen():
            return
        mx, my = self.getMousePos()

        # Click off event
        if (not self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and not self.spriteRenderer.getHud().getHudButtonHoverOver()):
            self.clickManager.setTransport(None)

        # Click event
        elif (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and (
                    self.spriteRenderer.getCurrentLayerString()
                    == self.currentNode.getConnectionType()
                    or self.spriteRenderer.getCurrentLayer() == 4)
                and self.game.clickManager.getMouseOver() == self):
            # Click off the person (if selected)
            if self.personClickManager.getPerson() is not None:
                self.personClickManager.setPerson(None)

            # Close the currently open holder (if one is open)
            holder = (
                self.spriteRenderer.getPersonHolderClickManager()
                .getPersonHolder())

            if holder is not None:
                holder.closeHolder(True)

            # Set the transport to be moved
            self.game.audioLoader.playSound("uiStartSelect", 2)
            self.clickManager.setTransport(self)
            self.game.clickManager.setClicked(False)

        # Hover over event
        elif (self.rect.collidepoint((mx, my)) and not self.mouseOver
                and (
                    self.spriteRenderer.getCurrentLayerString()
                    == self.currentNode.getConnectionType()
                    or self.spriteRenderer.getCurrentLayer() == 4)
                and self.game.clickManager.isTop(self)):
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
        if not hasattr(self, 'rect') or not self.running:
            return

        self.events()

        # Everything beyond here will NOT be called if the
        # spriteRenderer is paused
        if self.spriteRenderer.getPaused():
            return

        # Reset velocity to prevent infinate movement
        self.vel = vec(0, 0)

        connectionLength = self.currentConnection.getLength().length()
        currentDis = self.currentConnection.getDistance()

        # if the path is set follow it, only if the transport is
        # not stopped at a stop
        if len(self.path) > 0 and self.moving:
            path = self.path[0]

            dxy = (path.pos - path.offset) - self.pos + self.offset
            dis = dxy.length()

            if dis >= 0.5 and self.moving:
                # Speed up when leaving a stop, only if it is the first node
                # in the players path
                if (dis >= currentDis - 15 and dis <= connectionLength - 0.5
                        and self.checkIsStopType(self.currentNode)
                        and self.currentNode == self.firstPathNode):
                    self.vel = ((
                        -(self.currentConnection.getLength() + dxy)
                        * (self.speed / 12)) * self.game.dt
                        * self.spriteRenderer.getDt())

                # Slow down when reaching a stop, only if it is the last node
                # in the players path
                elif (dis <= 15
                        and self.checkIsStopType(
                            self.currentConnection.getTo())
                        and len(self.path) <= 1):
                    self.vel = ((
                        dxy * (self.speed / 10)) * self.game.dt
                        * self.spriteRenderer.getDt())

                else:
                    self.vel = (
                        dxy / dis * float(self.speed) * self.game.dt
                        * self.spriteRenderer.getDt())

                self.movePeople()
                self.movePersonHolder()

            else:
                # set the current connection to be one of the paths
                # connections (just pick a random one)
                self.setNextPathConnection(path)

            self.pos += self.vel
            self.rect.topleft = self.getTopLeft(self)

        else:
            dxy = ((
                self.currentConnection.getTo().pos
                - self.currentConnection.getTo().offset)
                - self.pos + self.offset)
            dis = dxy.length()

            if dis >= 0.5 and self.moving:  # Move towards the node
                # Speed up when leaving a stop
                if (dis >= currentDis - 15 and dis <= connectionLength - 0.5
                        and self.checkIsStopType(self.currentNode)):
                    self.vel = ((
                        -(self.currentConnection.getLength() + dxy)
                        * (self.speed / 12)) * self.game.dt
                        * self.spriteRenderer.getDt())

                # Slow down when reaching a stop
                elif (dis <= 15
                        and self.checkIsStopType(
                            self.currentConnection.getTo())):
                    self.vel = ((
                        dxy * (self.speed / 10)) * self.game.dt
                        * self.spriteRenderer.getDt())

                else:
                    self.vel = (
                        dxy / dis * float(self.speed) * self.game.dt
                        * self.spriteRenderer.getDt())

                self.movePeople()
                self.movePersonHolder()

            else:
                self.setNextConnection()
                self.pos = ((
                    self.currentConnection.getFrom().pos
                    - self.currentConnection.getFrom().offset) + self.offset)

            self.pos += self.vel
            self.rect.topleft = self.getTopLeft(self)


class Taxi(Transport):
    def __init__(
            self, spriteRenderer, groups, currentConnection, running,
            clickManagers=[]):
        super().__init__(
            spriteRenderer, groups, currentConnection, running, clickManagers)
        self.imageName = "taxi"
        self.stopType = NODE.NodeType.aslist()
        self.boardingType = PERSON.Person.Status.BOARDINGTAXI

        # self.timerLength = 200 # To Do: choose a value length

        self.hasStopped = False

    @overrides(Transport)
    def setPeopleBoarding(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            # If they're waiting for the taxi
            if person.getStatus() == PERSON.Person.Status.FLAG:
                person.setStatus(self.boardingType)

    def checkPeopleBoarding(self):
        # Set people waiting for the transportation to departing
        self.setPeopleBoarding()

        self.moving = False
        self.timer += 100 * self.game.dt * self.spriteRenderer.getDt()

        # Leaving the station
        if self.timer > self.timerLength:
            self.moving = True
            self.timer = 0

            # Add the people boarding to the transportation
            self.addPeople()

    @overrides(Transport)
    def setNextConnection(self):
        nextNode = self.currentConnection.getTo()

        # If the transport is moving, set its next connection to the
        # next upcoming node
        if self.moving:
            self.setConnection(nextNode)
            self.hasStopped = False

        if (self.checkIsStopType(self.currentNode)
                and self.checkTaxiStop(self.currentNode) or self.hasStopped):
            self.checkPeopleBoarding()

        if (self.checkIsStopType(self.currentNode)
                and self.checkPersonStop(self.currentNode)):
            # Remove anyone departing before we add new people
            self.removePeople()

            # Check again if there is anyone waiting for a taxi after we have
            # dropped off the previous user
            if (self.checkIsStopType(self.currentNode)
                    and self.checkTaxiStop(self.currentNode)):
                self.checkPeopleBoarding()

    # Check if there is a person on the node flagging the taxi down
    def checkTaxiStop(self, node):
        # only stop if there is someone flagging the taxi down, dont stop if
        # the taxi is already carrying someone
        if len(node.getPeople()) <= 0 or len(self.people) >= 1:
            return False

        for person in node.getPeople():
            if (person.getStatus() == PERSON.Person.Status.FLAG
                    or person.getStatus() == self.boardingType):
                self.hasStopped = True
                return True

        return False

    # Check if the person travelling on the taxi wants to leave the taxi
    def checkPersonStop(self, node):
        # People can't get off at no walk nodes
        if (len(self.people) <= 0
                or node.getSubType() == NODE.NodeType.NOWALKNODE):
            return False

        for person in self.people:
            if person.getStatus() == PERSON.Person.Status.DEPARTING:
                self.hasStopped = True
                return True
        return False

    @overrides(Transport)
    def update(self):
        if not hasattr(self, 'rect') or not self.running:
            return

        self.events()

        # Everything beyond here will NOT be called if the
        # spriteRenderer is paused
        if self.spriteRenderer.getPaused():
            return

        self.vel = vec(0, 0)

        connectionLength = self.currentConnection.getLength().length()
        currentDis = self.currentConnection.getDistance()

        if len(self.path) > 0 and self.moving:
            path = self.path[0]

            dxy = (path.pos - path.offset) - self.pos + self.offset
            dis = dxy.length()

            if dis >= 0.5 and self.moving:
                # speed up when leaving a stop
                if (dis >= currentDis - 15 and dis <= connectionLength - 0.5
                        and self.checkIsStopType(self.currentNode)
                        and self.currentNode == self.firstPathNode):

                    if (self.checkTaxiStop(self.currentNode)
                            or self.checkPersonStop(self.currentNode)
                            or self.hasStopped):
                        self.vel = ((
                            -(self.currentConnection.getLength() + dxy)
                            * (self.speed / 12)) * self.game.dt
                            * self.spriteRenderer.getDt())

                    else:
                        self.vel = (
                            dxy / dis * float(self.speed) * self.game.dt
                            * self.spriteRenderer.getDt())

                # slow down when reaching a node
                elif (dis <= 15
                        and self.checkIsStopType(
                            self.currentConnection.getTo())
                        and len(self.path) <= 1):

                    if (self.checkTaxiStop(self.currentConnection.getTo())
                            or self.checkPersonStop(
                                self.currentConnection.getTo())):
                        self.vel = (
                            (dxy * (self.speed / 10)) * self.game.dt
                            * self.spriteRenderer.getDt())

                    else:
                        self.vel = (
                            dxy / dis * float(self.speed) * self.game.dt
                            * self.spriteRenderer.getDt())

                else:
                    self.vel = (
                        dxy / dis * float(self.speed) * self.game.dt
                        * self.spriteRenderer.getDt())

                self.movePeople()
                self.movePersonHolder()

            else:
                self.setNextPathConnection(path)

            self.pos += self.vel
            self.rect.topleft = self.getTopLeft(self)

        else:
            dxy = ((
                self.currentConnection.getTo().pos
                - self.currentConnection.getTo().offset)
                - self.pos + self.offset)
            dis = dxy.length()

            if dis >= 0.5 and self.moving:  # Move towards the node
                # speed up when leaving
                if (dis >= currentDis - 15 and dis <= connectionLength - 0.5
                        and self.checkIsStopType(self.currentNode)):

                    if (self.checkTaxiStop(self.currentNode)
                            or self.checkPersonStop(self.currentNode)
                            or self.hasStopped):
                        self.vel = ((
                            -(self.currentConnection.getLength() + dxy)
                            * (self.speed / 12)) * self.game.dt
                            * self.spriteRenderer.getDt())

                    else:
                        self.vel = (
                            dxy / dis * float(self.speed) * self.game.dt
                            * self.spriteRenderer.getDt())

                # slow down when stopping
                elif (dis <= 15
                        and self.checkIsStopType(
                            self.currentConnection.getTo())):
                    if (self.checkTaxiStop(self.currentConnection.getTo())
                            or self.checkPersonStop(
                                self.currentConnection.getTo())):
                        self.vel = ((
                            dxy * (self.speed / 10)) * self.game.dt
                            * self.spriteRenderer.getDt())

                    else:
                        self.vel = (
                            dxy / dis * float(self.speed) * self.game.dt
                            * self.spriteRenderer.getDt())

                else:
                    self.vel = (
                        dxy / dis * float(self.speed) * self.game.dt
                        * self.spriteRenderer.getDt())

                self.movePeople()
                self.movePersonHolder()

            else:  # At the node
                self.setNextConnection()
                self.pos = ((
                    self.currentConnection.getFrom().pos
                    - self.currentConnection.getFrom().offset) + self.offset)

            self.pos += self.vel
            self.rect.topleft = self.getTopLeft(self)


class Bus(Transport):
    def __init__(
            self, spriteRenderer, groups, currentConnection, running,
            clickManagers=[]):
        super().__init__(
            spriteRenderer, groups, currentConnection, running, clickManagers)
        self.imageName = "bus"
        self.stopType = [NODE.NodeType.BUSSTOP, NODE.NodeType.DESTINATION]


class Tram(Transport):
    def __init__(
            self, spriteRenderer, groups, currentConnection, running,
            clickManagers=[]):
        super().__init__(
            spriteRenderer, groups, currentConnection, running, clickManagers)
        self.imageName = "tram"
        self.stopType = [NODE.NodeType.TRAMSTOP, NODE.NodeType.DESTINATION]


class Metro(Transport):
    def __init__(
            self, spriteRenderer, groups, currentConnection, running,
            clickManagers=[]):
        super().__init__(
            spriteRenderer, groups, currentConnection, running, clickManagers)
