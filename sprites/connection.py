import pygame
import pygame.gfxdraw
from config import BLACK, YELLOW, LAYERCOLORS, TEMPLAYERCOLORS
from utils import vec


class Connection:
    def __init__(
            self, spriteRenderer, connectionType, fromNode, toNode, temp,
            draw=False):
        # SpriteRenderer = mapEditor when on the map editor.
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.connectionType = connectionType
        self.fromNode = fromNode
        self.toNode = toNode
        self.sideColor = BLACK
        self.temp = temp
        self.draw = draw

        self.setColor()
        self.setLength()

        self.mouseOver = False

    # Return the colour of the connection
    def getColor(self):
        return self.color

    # Return the side colour of the connection
    def getSideColor(self):
        return self.sideColor

    # Return the node which the connection connects from
    def getFrom(self):
        return self.fromNode

    # Return the node which the connection connects to
    def getTo(self):
        return self.toNode

    # Return the length (as a vector) from point A to B
    def getLength(self):
        return self.length

    # Return the distance (as a float) from point A to B
    def getDistance(self):
        return self.distance

    # Return the type of connection
    def getType(self):
        return self.connectionType

    def getConnectionType(self):
        return self.connectionType

    # should the connection be drawn or not
    def getDraw(self):
        return self.draw

    # Set the colour of the connection depending on the type
    def setColor(self):
        colors = TEMPLAYERCOLORS if self.temp else LAYERCOLORS
        self.color = colors[int(self.connectionType[-1])]['color']

    # Set the length and distance of the connection from
    # point A (from) to B (to)
    def setLength(self):
        if self.fromNode is None or self.toNode is None:
            return

        self.length = (
            (self.fromNode.pos - self.fromNode.offset)
            - (self.toNode.pos - self.toNode.offset))
        self.distance = self.length.length()

    # Set point A (from)
    def setFromNode(self, fromNode):
        self.fromNode = fromNode

    # Set point B (to)
    def setToNode(self, toNode):
        self.toNode = toNode

    def updateConnections(self):
        if self.draw:
            layer = self.spriteRenderer.getGridLayer(self.connectionType)
            layer.createConnections()

            # Redraw the lines on layer 4 to reflect the deleted connection.
            if self.spriteRenderer.getCurrentLayer() == 4:
                self.spriteRenderer.setGridLayer4Lines()

    def events(self, collide):
        currentLayer = self.spriteRenderer.getCurrentLayer()
        previousLayer = self.spriteRenderer.getPreviousLayer()

        # Click event, delete the selected connection.
        if collide and self.game.clickManager.getClicked():
            if (currentLayer == 4
                    and self.connectionType != "layer " + str(previousLayer)):
                # Tell user they suck!
                self.game.audioLoader.playSound("uiError", 0)
                self.spriteRenderer.messageSystem.addMessage(
                    f"Can't delete connection from \
                    {self.spriteRenderer.getLayerName(self.connectionType)} \
                    layer when viewing \
                    {self.spriteRenderer.getLayerName(previousLayer)} layer")
                return

            self.spriteRenderer.getClickManager().deleteConnection(self)
            self.game.clickManager.setClicked(False)
            self.updateConnections()

        # Hover over event, highlight the selected connection.
        elif (collide and not self.mouseOver and (
                currentLayer != 4
                or self.connectionType == "layer " + str(previousLayer))):
            self.color = YELLOW
            self.mouseOver = True
            self.updateConnections()

        # Hover out event, un-highlight the selected connection.
        elif (not collide and self.mouseOver and (
                currentLayer != 4
                or self.connectionType == "layer " + str(previousLayer))):
            self.mouseOver = False
            self.setColor()
            self.updateConnections()

    def update(self):
        mx, my = pygame.mouse.get_pos()
        difference = self.game.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        buffer = 1

        d1 = ((
            vec(mx, my) - vec(10, 10) * scale)
            - (self.fromNode.pos - self.fromNode.offset) * scale).length()
        d2 = ((
            vec(mx, my) - vec(10, 10) * scale)
            - (self.toNode.pos - self.toNode.offset) * scale).length()

        collide = False
        # We check if the cursor is over a line
        if (d1 + d2 >= self.distance * scale - buffer
                and d1 + d2 <= self.distance * scale + buffer):
            collide = True

        self.events(collide)

    def __repr__(self):
        return (
            f"Connection(fromNode={self.fromNode}, toNode={self.toNode},"
            f"connectionType={self.connectionType})")
