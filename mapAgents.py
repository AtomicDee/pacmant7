# mapAgents.py
# parsons/11-nov-2017
#
# Version 1.0
#
# A simple map-building to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is an extension of the above code written by Simon
# Parsons, based on the code in pacmanAgents.py

from pacman import Directions
from game import Agent
from game import Actions
import api
import random
import game
import util
import sys
import math
import numpy as np
import itertools

#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:

    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

#
# An agent that creates a map.
#
# As currently implemented, the map places a % for each section of
# wall, a * where there is food, and a space character otherwise. That
# makes the display look nice. Other values will probably work better
# for decision making.
#
class MapAgent(Agent):

    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        print "Running init!"
        self.last_move = Directions.STOP
    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         self.map.display()

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def outcome_prob(self, legal, direction) :
        probability = 0
        for d in legal :
            if d == direction :
                probability = 0.8
            else :
                probability = 0.1
        return probability

    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):
        self.updateFoodInMap(state)
        self.map.prettyDisplay()
        pacman = api.whereAmI(state)

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        utility = 0
        utility_n = 0
        best_direction = legal[0]

        for direction in legal :
            vec = Actions.directionToVector(direction)
            loc = (pacman[0] + int(vec[0]), pacman[1] + int(vec[1]))
            map_value = self.map.getValue(loc[0], loc[1])
            print 'Direction : ', direction, 'Vec : ', vec, 'Map Value : ', map_value
            # set a score value to the next grid point
            if map_value == '%' :
                next_value = 0
            elif map_value == ' ' :
                next_value = 1
            elif map_value == '*' :
                next_value = 10
            elif map_value == '-' :
                next_value = -100

            print 'Next Value : ', next_value
            probability = self.outcome_prob(legal, direction)
            print 'Pribability : ', probability
            utility_n = probability * next_value
            print 'Utility : ', utility, 'Utility New : ', utility_n
            if utility_n > utility :
                best_direction = direction
                utility = utility_n
                print 'Best Direction : ', best_direction
            print 'Legal : ', legal

        if abs(utility) < 1 and (self.last_move in legal) :
            return api.makeMove(self.last_move, legal)

        return api.makeMove(best_direction, legal)

class MDPAgent(Agent):

    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        print "Running init!"
        self.last_move = Directions.STOP
    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         self.map.display()

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        self.utilmap = Grid(width, height)

    # Functions to get the height and the width of the grid.
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def outcome_prob(self, legal, direction) :
        probability = 0
        for d in legal :
            if d == direction :
                probability = 0.8
            elif d == Actions.reverseDirection(direction) :
                probability = 0
            else :
                probability = 0.1
        return probability

    def getReward(self, loc) :
        map_value = self.map.getValue(int(loc[0]), int(loc[1]))
        # return reward based on contents of passed location
        if map_value == '%' :
            reward = 0.0
        elif map_value == ' ' :
            reward = 1.0
        elif map_value == '*' :
            reward = 10.0
        elif map_value == '-' :
            reward = -100.0
        return reward

    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):
        self.updateFoodInMap(state)
        self.map.prettyDisplay()
        self.utilmap.prettyDisplay()
        pacman = api.whereAmI(state)

        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        maxU = -500
        best_direction = Directions.STOP
        # checks each next legal direction
        for i in range(1000) :
            for x,y in itertools.product(range(self.map.getWidth()),range(self.map.getHeight()))
                for direction in legal :
                    print direction, i
                    vec = Actions.directionToVector(direction)
                    loc = (x + int(vec[0]), y + int(vec[1]))
                    values = self.utilmap.getValue(loc[0], loc[1])

                    # vectors and locations for either side of the current direction
                    side_a = [vec[1],vec[0]]
                    loc_a = (x + side_a[0], y + side_a[1])

                    side_b = [-side_a[0], -side_a[1]]
                    loc_b = (x + side_b[0], y + side_b[1])

                    # get rewards of all three potential directions
                    rewards = [self.getReward(loc), self.getReward(loc_a), self.getReward(loc_b)]

                    # Calculate U here
                    U = (rewards[0]*0.8) + (rewards[1]*0.1) + (rewards[2]*0.1)
                    if U > maxU :
                        maxU = U
                        best_direction = direction

                    # set U
                    self.utilmap.setValue(loc[0], loc[1], U)
                    # print best_direction, '   ', U


        self.utilmap.setValue(pacman[0],pacman[1], -1)
        return api.makeMove(best_direction, legal)
