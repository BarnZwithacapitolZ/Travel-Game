import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math
import json

from node import *
from connection import *
from transport import *

class GridManager:
    def __init__(self, game, groups, level):
        self.game = game
        self.groups = groups
        self.level = level
        self.levelName = ""

        self.nodes = []
        self.nodePositions = []
        self.connections = []
        self.transports = []
        self.grid = []
        self.stops = []

        self.nodePositions = GridManager.setNodePositions()

        self.loadMap()


    #### Getters ####

    def getLevelName(self):
        return self.levelName


    # return the nodes, in a list to be appended to each layer
    def getNodes(self):
        return self.nodes


    # Return the connections, in a list for each layer
    def getConnections(self):
        return self.connections


    # Return the transportations, in a list for each layer
    def getTransports(self):
        return self.transports


    #### Setters ####

    #generate an 18 * 10 board of possible node positions (x and y locations) for nodes to be added to
    @staticmethod
    def setNodePositions():
        offx = 1.5 # Offset on the x coordinate
        offy = 1.5 # Offset on the y coordinate
        spacing = 50 #spacing between each node
        positions = []

        for i in range(18):
            for x in range(10):
                positions.append(((i + offx) * spacing, (x + offy) * spacing))
        return positions



    # Load the .json map data into a dictionary
    def loadMap(self):
        with open(self.level) as f:
            self.map = json.load(f)

        self.levelName = self.map["mapName"] # Get the name of the map


    # Add a node to the grid if the node is not already on the grid
    def addNode(self, connection, connectionType, currentNodes, direction):
        if connection[direction] not in currentNodes:
            n = self.addStop(connection, direction, connectionType)

            if n is None: #no stop was found at this node 
                n = Node(self.game, self.groups, connection[direction], connectionType, self.nodePositions[connection[direction]][0], self.nodePositions[connection[direction]][1])

            self.nodes.append(n)
            currentNodes.append(connection[direction])

        return currentNodes


    # Add a stop, instead of a node, to the grid 
    def addStop(self, connection, direction, connectionType):
        n = None
        for stop in self.map["stops"][connectionType]:
            if stop == connection[direction]:
                # Set the type of stop
                if connectionType == "layer 2":
                    n = BusStop(self.game, self.groups, connection[direction], connectionType, self.nodePositions[connection[direction]][0], self.nodePositions[connection[direction]][1])
                else:
                    n = MetroStation(self.game, self.groups, connection[direction], connectionType, self.nodePositions[connection[direction]][0], self.nodePositions[connection[direction]][1])
        return n
        

    # Create the grid by adding all the nodes and connections to the grid
    def createGrid(self, connectionType):
        currentNodes = []

        for connection in self.map["connections"][connectionType]:
            # Add the nodes in the connection
            currentNodes = self.addNode(connection, connectionType, currentNodes, 0)
            currentNodes = self.addNode(connection, connectionType, currentNodes, 1)

            for node in self.nodes:
                if node.getNumber() == connection[0]:
                    n1 = node
                if node.getNumber() == connection[1]:
                    n2 = node

            # Create the connection with the nodes
            c1 = Connection(self.game, connectionType, n1, n2, Connection.Direction.FORWARDS) 
            c2 = Connection(self.game, connectionType, n2, n1, Connection.Direction.BACKWARDS) 
            self.connections.append(c1) #forwards
            self.connections.append(c2) #backwards


    # Load the transportation to the grid on a specified connection 
    def loadTransport(self, connectionType, layers = None):
        if len(self.connections) <= 0:
            return 

        layers = self.groups if layers is None else layers

        # For each transportation in the map
        for transport in self.map["transport"][connectionType]:
            direction = random.randint(0, 1)
            
            # for each connection, find the connection of the transportation
            for connection in self.connections:
                # Ensure it is on the right connection going in the right direction
                if connection.getFrom().getNumber() == transport:
                    # If the connection is the same as the direction, or its an end node (so theres only one direction)
                    if connection.getDirection().value == direction or len(connection.getFrom().getConnections()) <= 1:
                        if connectionType == "layer 2":
                            t = Bus(self.game, layers, connection, connection.getDirection())
                        else:
                            t = Transport(self.game, layers, connection, connection.getDirection())
                        self.transports.append(t)
                        break
           