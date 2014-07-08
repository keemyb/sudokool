# -*- coding: cp1252 -*-

#subGridsx = amount of subgrids in X plane

class sudoku():
        
    def __init__(self, gridSize, subGridsX, subGridsY, data):
        self.gridSize = gridSize
        self.subGridsX = subGridsX
        self.subGridsY = subGridsY
        self.data = {position + 1 : int(data[position]) for position in range(gridSize ** 2)}
        self.ghostData = {}
        self.subGridStartLocations = self.getSubGridStartLocations()
        self.rowStartLocations = self.getRowStartLocations()
        # self.columnStartLocations = self.getColumnStartLocations()
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
        gridSize = self.getGridSize()
        subGridsX = self.getSubGridsX()
        subGridsY = self.getSubGridsY()
        columnStartLocations = []

        for column in xrange(self.gridSize):
            membersInLeftwardSubGrids = (column / subGridsY) * gridSize

            if (column + 1) % subGridsY != 0:
                adjustment = ((column + 1) % subGridsY)
            else:
                adjustment = 0

            columnStartLocation = membersInLeftwardSubGrids + adjustment + 1

            columnStartLocations.append(columnStartLocation)
        return sorted(columnStartLocations)

    def indexToStorageLocation(self, index):
            gridSize = self.gridSize
            subGridsX = self.subGridsX
            subGridsY = self.subGridsY
            index = index + 1

            if index % gridSize == 0: #last number in row
                subGrid = (((index - 1) / (gridSize * subGridsX)) + 1) * subGridsX
                columnInSubGrid = subGridsY
            else:
                subGrid = ((((index - 1) / (gridSize * subGridsX)) + 1) * subGridsX) - \
                          (subGridsX - ((((index % gridSize) - 1) / subGridsY) + 1))
                if index % subGridsY == 0:
                    columnInSubGrid = subGridsY
                else:
                    columnInSubGrid = index % subGridsY

            if index % (gridSize * subGridsX) == 0: #last number of last subGrid in Row
                rowInSubGrid = subGridsX
            else:
                if index % gridSize == 0:
                    rowInSubGrid = (((index) % (gridSize * subGridsX))) / gridSize
                else:
                    rowInSubGrid = ((((index) % (gridSize * subGridsX))) / gridSize) + 1

            if subGrid % subGridsX == 0: #last subGrid in row
                membersInHorzAdjSubGrids = (subGridsX - 1) * gridSize
            else:
                membersInHorzAdjSubGrids = ((subGrid % subGridsX) - 1) * gridSize

            membersInAboveSubGrids  = ((subGrid - 1)/subGridsX) * gridSize * subGridsX

            if rowInSubGrid == 1:
                membersInAboveRowsInSubGrid = 0
            else:
                membersInAboveRowsInSubGrid = (rowInSubGrid - 1) * subGridsY

            membersLeftInRowIncSelf = columnInSubGrid

            position = membersInAboveSubGrids + membersInHorzAdjSubGrids + \
                       membersInAboveRowsInSubGrid + membersLeftInRowIncSelf
                
            return position

    def getGridSize(self):
        return self.gridSize

    def getSubGridsX(self):
        return self.subGridsX

    def getSubGridsY(self):
        return self.subGridsY

    def getData(self):
        return self.data

    def getSubGrid(self, location):
        gridSize = self.getGridSize()

        if location % gridSize == 0: #last number in box
            return location / gridSize
        else:
            return (location / gridSize) + 1

    def getPositionInSubGrid(self, location):
        gridSize = self.getGridSize()

        if location % gridSize == 0: #last number in box
            return gridSize
        else:
            return location % gridSize

    def getRowInSubGrid(self, location):
        gridSize = self.getGridSize()
        subGridsY = self.getSubGridsY()
        subGridsX = self.getSubGridsX()

        if location % gridSize == 0: #last number in box
            return subGridsX
        else:
            return (((location % gridSize) - 1) / subGridsY) + 1

    def getColumnInSubGrid(self, location):
        gridSize = self.getGridSize()
        subGridsY = self.getSubGridsY()

        if location % subGridsY == 0: #last number in box
            return subGridsY
        else:
            return ((location % gridSize) % subGridsY)

    def getSubGridMembers(self, location):
        """returns locations of sub grid members, the location given is included in list"""
        gridSize = self.getGridSize()

        resolvedMembers = []

        if location % gridSize == 0:
            firstMember = (location - gridSize) + 1
        else:
            firstMember = location - (location % gridSize) + 1

        lastMember = (firstMember + gridSize) - 1
        subGridMembers = range(firstMember, lastMember + 1)

        for i in subGridMembers:
            resolvedMembers.append(self.getData()[i])

        return dict(zip(subGridMembers, resolvedMembers))

    def getRowMembers(self, location):
        gridSize = self.getGridSize()
        subGridsX = self.getSubGridsX()
        subGridsY = self.getSubGridsY()
        rowInSubGrid = self.getRowInSubGrid(location)

        rowMembers = []
        resolvedMembers = []

        subGridRow = ((self.getSubGrid(location) - 1) / subGridsX) + 1
        
        firstSubGridInRow = ((subGridRow - 1) * subGridsX) + 1
        lastSubGridInRow = firstSubGridInRow + subGridsX - 1
        subGridsInRow = range(firstSubGridInRow, lastSubGridInRow + 1)

        for subGrid in subGridsInRow:
            firstMemberInSubGrid = ((subGrid - 1) * gridSize) + 1
            firstRowMemberInSubGrid = firstMemberInSubGrid + ((rowInSubGrid - 1) * subGridsY)
            lastRowMemberInSubGrid = firstRowMemberInSubGrid + subGridsY - 1
            rowMembersInSubGrid = range(firstRowMemberInSubGrid, lastRowMemberInSubGrid + 1)

            for member in rowMembersInSubGrid:
                rowMembers.append(member)
                resolvedMembers.append(self.getData()[member])
            
        return dict(zip(rowMembers,resolvedMembers))

    def getColumnMembers(self, location):
        gridSize = self.getGridSize()
        subGridsX = self.getSubGridsX()
        subGridsY = self.getSubGridsY()
        columnInSubGrid = self.getColumnInSubGrid(location)

        columnMembers = []
        resolvedMembers = []
        subGridsInColumn = []

        if self.getSubGrid(location) % subGridsX == 0:
            subGridColumn = subGridsX
        else:
            subGridColumn = self.getSubGrid(location) % subGridsX

        firstSubGridInColumn = subGridColumn
        for i in xrange(subGridsY):
            subGridsInColumn.append(firstSubGridInColumn + (subGridsX * i))

        for subGrid in subGridsInColumn:
            firstMemberInSubGrid = ((subGrid - 1) * gridSize) + 1
            firstColumnMemberInSubGrid = firstMemberInSubGrid + columnInSubGrid - 1

            j = subGridsX
            while j != 0:
                reference = firstColumnMemberInSubGrid + subGridsY * (j - 1)
                columnMembers.append(reference)
                resolvedMembers.append(self.getData()[reference])
                j -= 1

        return dict(zip(columnMembers,resolvedMembers))

    def resolveMember(self, location):
        resolvedMember = self.getData()[location]
        return resolvedMember

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