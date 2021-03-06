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

class MDPAgent(Agent):

    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        print "Running init!"
        self.last_move = Directions.STOP
        self.previous = (float('inf'),float('inf'))
        self.food = set()
        self.lastfood = float('inf')
        self.ghostlocations = []
    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         # self.map.display()

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        # print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        self.utilmap = Grid(width, height)
        self.prevmap = Grid(width, height)

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

                if (i,j) == self.previous :
                    self.map.setValue(i, j, 'p')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def updateGhosts(self, state) :
        self.ghostlocations = api.ghosts(state)
        for i in range(len(self.ghostlocations)) :
            self.map.setValue(int(self.ghostlocations[i][0]),int(self.ghostlocations[i][1]), '-')

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
        elif map_value == 'p' :
            reward = -10.0
        return reward

    def BellmanUpdate(self, state, all_directions) :
        sumpu = []
        diff = 999999
        count = 0
        # checks each next legal direction
        while abs(diff) > 0.01 :
            count += 1
            for x in range(1,self.map.getWidth()-1) :
                for y in range(1,self.map.getHeight()-1) :
                    if self.map.getValue(x,y) == '%' :
                        self.utilmap.setValue(int(x), int(y), 0.0)
                        continue
                    for direction in all_directions : # run for all directions not just legal.
                        # print direction, i
                        vec = Actions.directionToVector(direction)
                        loc = (int(x) + int(vec[0]), int(y) + int(vec[1]))

                        # vectors and locations for either side of the current direction
                        side_a = [int(vec[1]),int(vec[0])]
                        loc_a = (x + side_a[0], y + side_a[1])

                        side_b = [-side_a[0], -side_a[1]]
                        loc_b = (x + side_b[0], y + side_b[1])

                        # get rewards of all three potential directions
                        if count == 0 :
                            # if its the first iteration, get arbitrary rewards set by grid point type
                            # eg. food, wall, empty, ghost, pacman.
                            rewards = [self.getReward([int(x),int(y)]), self.getReward(loc), self.getReward(loc_a), self.getReward(loc_b)]
                        else :
                            # After initial run, take rewards from previously calculated utilities
                            rewards = [self.getReward([int(x),int(y)]), self.prevmap.getValue(loc[0], loc[1]), self.prevmap.getValue(loc_a[0], loc_a[1]), self.prevmap.getValue(loc_b[0], loc_b[1])]

                        # Calculate the sum part of Bellman eq here
                        gamma = 1
                        rewardsum = (rewards[1]*0.8) + (rewards[2]*0.1) + (rewards[3]*0.1)
                        sumpu.append(gamma*rewardsum)

                    # Calculate final U(s) value
                    U = rewards[0] + max(sumpu)
                    sumpu = []
                    # Sum each U value to calculate a difference to control while loop
                    if (x == self.map.getWidth()-2) and (y == self.map.getHeight()-2) :
                        diff = self.prevmap.getValue(int(x), int(y)) - U

                    # Set new utilmap value
                    self.utilmap.setValue(int(x), int(y), U)

            # Set previous map as the newly calculated one after the whole map is done
            self.prevmap = self.utilmap

    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):
        # print self.previous
        self.updateFoodInMap(state)
        self.updateGhosts(state)
        pacman = api.whereAmI(state)
        # self.map.prettyDisplay()

        # initialise direction variables
        legal = api.legalActions(state)
        all_directions = [Directions.NORTH, Directions.EAST, Directions.SOUTH, Directions.WEST]
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # Update utility maps
        self.BellmanUpdate(state, all_directions)

        # Update ghost location values

        # save all utilities around pacman, in legal directions
        U_all = []
        for i in range(len(legal)) :
            vec = Actions.directionToVector(legal[i])
            loc = (int(pacman[0])+int(vec[0]), int(pacman[1])+int(vec[1]))
            U_all.append(self.utilmap.getValue(loc[0], loc[1]))

        # Choose the largest utility around pacman
        ind = U_all.index(max(U_all))
        # Get corresponding move
        move = legal[ind]
        # Set pacman's last location as p - will pull a reward value of -50 to discourage
        # pacman from moving backwards
        self.map.setValue(pacman[0],pacman[1], 'p')
        self.previous = pacman
        #raw_input('Press <ENTER> to continue')

        self.map.prettyDisplay()
        self.prevmap.prettyDisplay()
        raw_input('Press ENTER to continue')
        # move
        return api.makeMove(move, legal)
