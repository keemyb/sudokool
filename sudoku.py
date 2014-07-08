# -*- coding: cp1252 -*-

#subGridsx = amount of subgrids in X plane

class sudoku():
        
    def __init__(self, gridSize, subGridsX, subGridsY, data):
        self.gridSize = gridSize
        self.subGridsX = subGridsX
        self.subGridsY = subGridsY
        self.data = {position + 1 : int(data[position]) for position in range(gridSize ** 2)}
        self.ghostData = {}
        self.intersectionGroups = self.getSubGridGroups() + self.getRowGroups() + self.getColumnGroups()
        # self.setOfPossibleNumbers = set(xrange(1, self.gridSize + 1))
        # self.changes = False
        # self.intersectionTypes = {"subGrid":[self.subGridStartLocations, self.getSubGridMembers],
        # "row":[self.rowStartLocations, self.getRowMembers],
        # "column":[self.columnStartLocations, self.getColumnMembers]}

##        try:
##            if gridSize % subGridsX != 0 or gridSize % subGridsY != 0:
##                #return "invalid dimensions"
##                raise Exception("invalid dimensions")
##            if gridSize != (subGridsX * subGridsY):
##                #return "invalid dimensions"
##                raise Exception("invalid dimensions")
##        except:
##            return ValueError

        #self.populateGhosts()            
        
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

            if self.data[position] == 0:
                string += "  "
            else:
                string += str(self.data[position]) + " "

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

    def populateGhosts(self):
        for i in xrange(self.gridSize): # subGrid
            existingValues = []    

            for location, value in self.getSubGridMembers((i * self.gridSize) + 1).iteritems():
                if value != 0:
                    existingValues.append(int(value)) # int for diff

            for location, value in self.getSubGridMembers((i * self.gridSize) + 1).iteritems():
                if self.resolveMember(location) == 0:
                    setOfNonExistingValues = self.setOfPossibleNumbers.difference(set(existingValues))
                    self.ghostData[location] = list(setOfNonExistingValues)

        for i in xrange(self.gridSize): #columns
            existingValues = []
            reference = ((i / self.subGridsY) * self.gridSize) + ((i + 1) % self.subGridsY)

            for location, value in self.getColumnMembers(reference).iteritems():
                if value != 0:
                    existingValues.append(int(value))

            for location, value in self.getColumnMembers(reference).iteritems():
                if self.resolveMember(location) == 0:
                    setOfExistingGhostValues = set(self.ghostData[location])
                    setOfNonExistingValues = self.setOfPossibleNumbers.difference(set(existingValues))
                    self.ghostData[location] = list(setOfExistingGhostValues.intersection(setOfNonExistingValues))

        for i in xrange(self.gridSize): #rows
            existingValues = []
            reference = ((((i + self.subGridsX) / self.subGridsX) - 1) * self.gridSize * self.subGridsX) + \
                        ((i % self.subGridsX) * self.subGridsY) + 1

            for location, value in self.getRowMembers(reference).iteritems():
                if value != 0:
                    existingValues.append(int(value))            

            for location, value in self.getRowMembers(reference).iteritems():
                if self.resolveMember(location) == 0:
                    setOfExistingGhostValues = set(self.ghostData[location])
                    setOfNonExistingValues = self.setOfPossibleNumbers.difference(set(existingValues))
                    self.ghostData[location] = list(setOfExistingGhostValues.intersection(setOfNonExistingValues))

    def updateGhosts(self):
        for location, value in self.ghostData.iteritems():
            if value == []:
                del self.ghostData[location]

    def nakedSingle(self):
        self.populateGhosts()
        self.changes = False
        ghostKeysToDelete = []

        for location, value in self.ghostData.iteritems():
            if len(value) == 1:
                self.data[location] = value[0]
                ghostKeysToDelete.append(location)
                self.changes = True

        if self.changes:
            for location in ghostKeysToDelete:
                del self.ghostData[location]
            self.populateGhosts()

        return self.changes

    def hiddenSingle(self):
        self.populateGhosts()
        self.changes = False

        for intersectionType in self.intersectionTypes.itervalues():

            for startLocation in intersectionType[0]:
                members = intersectionType[1](startLocation)

                unresolvedLocations = sorted([key for key in members.iterkeys() if
                                    (key in self.ghostData.keys())])
                
                for location in unresolvedLocations:
                    surroundingLocations = []
                    for surroundingLocation in unresolvedLocations:
                        if surroundingLocation != location:
                            surroundingLocations.append(surroundingLocation)
                            
                    surroundingGhosts = []
                    for surroundingLocation in surroundingLocations:
                        if surroundingLocation != location:
                            for ghostValue in self.ghostData[surroundingLocation]:
                                surroundingGhosts.append(ghostValue)

                    setOfSurroundingGhosts = set(surroundingGhosts)                
                    locationGhosts = [ghostValue for ghostValue in self.ghostData[location]]
                    setOfLocationGhosts = set(locationGhosts)

                    setOfUniqueGhosts = setOfLocationGhosts - setOfSurroundingGhosts

                    if len(setOfUniqueGhosts) == 1:
                        self.data[location] = setOfUniqueGhosts.pop()
                        del self.ghostData[location]
                        self.changes = True
                        self.populateGhosts()
                        unresolvedLocations = sorted([key for key in members.iterkeys() if
                                                      (key in self.ghostData.keys())])

    def nakedTwin(self):
        self.populateGhosts()
        self.changes = False

        for intersectionType in self.intersectionTypes.itervalues():

            for startLocation in intersectionType[0]:
                
                members = intersectionType[1](startLocation)

                unresolvedLocations = sorted([key for key in members.iterkeys() if
                        (key in self.ghostData.keys())])

                for locationOne in unresolvedLocations:

                    for locationTwo in unresolvedLocations:

                        if locationOne != locationTwo and len(unresolvedLocations) > 2:

                            if len(self.ghostData[locationOne]) == 2 and self.ghostData[locationOne] == self.ghostData[locationTwo]:
                                for location in unresolvedLocations:

                                    if location != locationOne and location != locationTwo:

                                        for ghostValue in self.ghostData[locationOne]:

                                            if ghostValue in self.ghostData[location]:

                                                self.changes = True
                                                self.ghostData[location].remove(ghostValue)
                                                ##self.populateGhosts()