# -*- coding: cp1252 -*-

#subGridsx = amount of subgrids in X plane

class sudoku():
        
    def __init__(self, gridSize, subGridsX, subGridsY, data):
        self.gridSize = gridSize
        self.subGridsX = subGridsX
        self.subGridsY = subGridsY
        self.values = {position + 1 : int(data[position]) for position in range(gridSize ** 2)}
        self.ghostValues = {}
        self.intersectionGroups = self.getSubGridGroups() + self.getRowGroups() + self.getColumnGroups()
        self.setOfPossibleNumbers = frozenset(xrange(1, self.gridSize + 1))
        self.changes = False

        self.updateGhostsAndGroups()

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)           
        
    def __repr__(self):
        pass #rebuildable representation

    def __str__(self):
        gridSize = self.gridSize
        subGridsX = self.subGridsX
        subGridsY = self.subGridsY
        string = ""
        vPipe = "="
        hPipe = "="
        # first line to accommodate vertical pipe and following spaces (minus one to account for last v pipe)
        # second line for numbers (and following spaces)
        hPipeString = hPipe * ((len(vPipe) + 1) * (subGridsX + 1) - 1) + \
        hPipe * (gridSize * 2) + \
        "\n"

        for position in xrange(1, gridSize ** 2 + 1):

            if (position - 1) % (gridSize * subGridsX) == 0:
                string += hPipeString

            if (position - 1) % subGridsY == 0 :
                string += vPipe + " "

            if self.values[position] == 0:
                string += "  "
            else:
                string += str(self.values[position]) + " "

            if position % gridSize == 0:
                string += vPipe + "\n"

            if position == gridSize ** 2:
                string += hPipeString

        return string

    def getSubGridStartLocations(self):
        subGridsX = self.subGridsX
        subGridsY = self.subGridsY
        gridSize = self.gridSize
        subGridStartLocations = []
        
        for subGrid in xrange(gridSize):
            baseLocation = (subGrid / subGridsX) * (gridSize * subGridsX)
            offset = (subGrid % subGridsX) * subGridsY
            subGridStartLocations.append(baseLocation + offset + 1)
        
        return subGridStartLocations

    def getRowStartLocations(self):
        gridSize = self.gridSize
        
        rowStartLocations = [(row * gridSize + 1) for row in xrange(gridSize)]

        return rowStartLocations

    def getColumnStartLocations(self):
        gridSize = self.gridSize

        columnStartLocations = range(1, gridSize + 1)

        return columnStartLocations

    def getSubGridGroups(self):
        gridSize = self.gridSize
        subGridsY = self.subGridsY

        subGridGroups = []

        for startLocation in self.getSubGridStartLocations():
            subGridGroup = []
            
            for position in xrange(gridSize):
                rowOffset = ((position % gridSize) / subGridsY) * gridSize
                columnOffset = (position % gridSize) % subGridsY
                subGridGroup.append(startLocation + rowOffset + columnOffset)
            
            subGridGroups.append(subGridGroup)

        return subGridGroups

    def getRowGroups(self):
        gridSize = self.gridSize

        rowGroups = []

        for startLocation in self.getRowStartLocations():
            rowGroups.append([startLocation + offset for offset in xrange(gridSize)])
            
        return rowGroups

    def getColumnGroups(self):
        gridSize = self.gridSize

        columnGroups = []

        for startLocation in self.getColumnStartLocations():
            columnGroups.append([startLocation + offset * gridSize for offset in xrange(gridSize)])

        return columnGroups

    def isValid(self):
        for location in xrange(1, self.gridSize ** 2 + 1):
            if self.values[location] != 0:
                if self.values[location] not in self.setOfPossibleNumbers:
                    return False

        intersectionGroups = self.getSubGridGroups() + self.getRowGroups() + self.getColumnGroups()
        for group in intersectionGroups:

            values = [self.values[location] for location in group if self.values[location] != 0]
            if len(values) != len(set(values)):
                return False

        return True

    def updateGhostsAndGroups(self, modifiedLocations = None):
        if modifiedLocations == []:
            return
        
        locationsToRemoveFromGroups = []
        #Exhaustive
        if modifiedLocations == None:
            for group in self.intersectionGroups:
                setOfSurroundingValues = set([self.values[value] for value in group if self.values[value] != 0])

                for location in group:
                    if self.values[location] == 0:
                        if location in self.ghostValues:
                            self.ghostValues[location] -= setOfSurroundingValues
                        else:
                            self.ghostValues[location] = set(self.setOfPossibleNumbers) - setOfSurroundingValues
                    else:
                        locationsToRemoveFromGroups.append(location)
        
        #specific
        else:
            for group in self.intersectionGroups:
                setOfSurroundingValues = set([self.values[value] for value in group if self.values[value] != 0])
                if any(location in modifiedLocations for location in group):
                    for location in group:
                        if self.values[location] == 0:
                            self.ghostValues[location] -= setOfSurroundingValues
                        else:
                            locationsToRemoveFromGroups.append(location)

        for location in locationsToRemoveFromGroups:
            for group in self.intersectionGroups:
                if location in group:
                    group.remove(location)

        #prune empty intersection groups
        self.intersectionGroups = filter(None, self.intersectionGroups)

    def nakedSingle(self):
        self.changes = False

        modifiedLocations = []

        for location, ghostValues in self.ghostValues.iteritems():
            if len(ghostValues) == 1:
                self.values[location] = ghostValues.pop()
                modifiedLocations.append(location)
                self.changes = True

        if self.changes:
            for location in modifiedLocations:
                del self.ghostValues[location]

            self.updateGhostsAndGroups(modifiedLocations)

        return self.changes

    def nakedN(self, n):
        from itertools import combinations
        self.changes = False

        for group in self.intersectionGroups:

            if len(group) > n:

                for combination in combinations(group, n):

                    if len(set([tuple(self.ghostValues[location]) for location in combination])) == n:

                        nakedNghostValues = set([tuple(self.ghostValues[location]) for location in combination])

                        for surroundingLocation in [location for location in group if location not in combination]:

                            if any(ghostValue in nakedNghostValues for ghostValue in self.ghostValues[surroundingLocation]):

                                self.ghostValues[surroundingLocation] -= nakedNghostValues
                                self.changes = True

        return self.changes

    def nakedTwin(self):

        return self.nakedN(2)

    def nakedTriplet(self):

        return self.nakedN(3)

    def hiddenSingle(self):
        self.changes = False
        modifiedLocations = []

        for group in self.intersectionGroups:
            
            for location in group:
                setsOfSurroundingGhosts = [self.ghostValues[surroundingLocation] for surroundingLocation in group if surroundingLocation != location]
                setOfSurroundingGhosts = set([ghostValue for ghostValues in setsOfSurroundingGhosts for ghostValue in ghostValues])
                setOfUniqueGhosts = self.ghostValues[location] - setOfSurroundingGhosts
                
                if len(setOfUniqueGhosts) == 1:
                    self.values[location] = setOfUniqueGhosts.pop()
                    modifiedLocations.append(location)
                    self.changes = True

        if self.changes:
            for location in modifiedLocations:
                if location in self.ghostValues:
                    del self.ghostValues[location]

            self.updateGhostsAndGroups(modifiedLocations)

        return self.changes

    def hiddenN(self, n):
        from itertools import combinations
        self.changes = False

        for group in [group for group in self.intersectionGroups if len(group) > n]:

            for combination in combinations(group, n):

                surroundingLocations = [location for location in group if location not in combination]

                setsOfCombinationGhosts = [self.ghostValues[location] for location in combination]
                setOfCombinationGhosts = set([ghostValue for ghostValueSets in setsOfCombinationGhosts for ghostValue in ghostValueSets])
                setsOfSurroundingGhosts = [self.ghostValues[surroundingLocation] for surroundingLocation in surroundingLocations]
                setOfSurroundingGhosts = set([ghostValue for ghostValueSets in setsOfSurroundingGhosts for ghostValue in ghostValueSets])
                setOfUniqueGhostsToCombination = setOfCombinationGhosts - setOfSurroundingGhosts

                if len(setOfUniqueGhostsToCombination) == n:

                    for location in combination:

                        if any(ghostValue in setOfSurroundingGhosts for ghostValue in self.ghostValues[location]):

                            self.ghostValues[location] -= setOfSurroundingGhosts
                            self.changes = True

                    for location in surroundingLocations:

                        if any(ghostValue in setOfUniqueGhostsToCombination for ghostValue in self.ghostValues[location]):

                            self.ghostValues[location] -= setOfUniqueGhostsToCombination

        return self.changes

    def hiddenTwin(self):

        return self.hiddenN(2)

    def hiddenTriplet(self):

        return self.hiddenN(3)