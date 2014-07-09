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
        self.setOfPossibleNumbers = set(xrange(1, self.gridSize + 1))
        self.changes = False

        self.populateGhosts()            
        
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

    def populateGhosts(self, modifiedLocations = None):
        if modifiedLocations == None:
            for group in self.intersectionGroups:
                setOfExistingValues = set([self.values[value] for value in group if self.values[value] != 0])

                for location in group:
                    if self.values[location] == 0:
                        if location in self.ghostValues:
                            self.ghostValues[location] -= setOfExistingValues
                        else:
                            self.ghostValues[location] = self.setOfPossibleNumbers - setOfExistingValues
        else:
            for group in self.intersectionGroups:
                for location in group:
                    if location in modifiedLocations:
                        if self.values[location] == 0:
                            self.ghostValues[location] -= setOfExistingValues


    def nakedSingle(self):
        self.changes = False

        ghostKeysToBeRemoved = []

        for location, ghostValues in self.ghostValues.iteritems():
            if len(ghostValues) == 1:
                self.values[location] = ghostValues.pop()
                ghostKeysToBeRemoved.append(location)
                self.changes = True

        if self.changes:
            for location in ghostKeysToBeRemoved:
                del self.ghostValues[location]

            self.populateGhosts(ghostKeysToBeRemoved)

        return self.changes

    def hiddenSingle(self):
        self.changes = False
        ghostKeysToBeRemoved = []

        for group in self.intersectionGroups:
            emptyLocations = (location for location in group if location in self.ghostValues)
            
            for location in emptyLocations:
                setsOfSurroundingGhosts = [self.ghostValues[surroundingLocation] for surroundingLocation in emptyLocations if surroundingLocation != location]
                setOfSurroundingGhosts = set([ghostValue for ghostValues in setsOfSurroundingGhosts for ghostValue in ghostValues])
                setOfUniqueGhosts = self.ghostValues[location] - setOfSurroundingGhosts
                
                if len(setOfUniqueGhosts) == 1:
                    self.values[location] = setOfUniqueGhosts.pop()
                    ghostKeysToBeRemoved.append(location)
                    self.changes = True

        if self.changes:
            for location in ghostKeysToBeRemoved:
                if location in self.ghostValues:
                    del self.ghostValues[location]

            self.populateGhosts(ghostKeysToBeRemoved)

        return self.changes

    def nakedTwin(self):
        self.changes = False

        modifiedLocations = []

        for group in self.intersectionGroups:
            emptyLocations = [location for location in group if location in self.ghostValues]
            
            if len(emptyLocations) > 2:
                
                for locationOne in emptyLocations:
                    
                    for locationTwo in emptyLocations:
                        
                        if locationOne != locationTwo:

                            if len(self.ghostValues[locationOne]) == 2 and self.ghostValues[locationOne] == self.ghostValues[locationTwo]:

                                for location in emptyLocations:

                                    if location != locationOne and location != locationTwo:

                                        self.ghostValues[location] -= self.ghostValues[locationOne]
                                        modifiedLocations.append(location)
                                        self.changes = True
                                        
        self.populateGhosts([modifiedLocations])
        return self.changes