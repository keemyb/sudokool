# -*- coding: cp1252 -*-

#subGridsx = amount of subgrids in X plane

class sudoku():
        
    def __init__(self, gridSize, subGridsX, subGridsY, data):
        self.gridSize = gridSize
        self.subGridsX = subGridsX
        self.subGridsY = subGridsY
        self.data = {}
        self.ghostData = {}

##        try:
##            if gridSize % subGridsX != 0 or gridSize % subGridsY != 0:
##                #return "invalid dimensions"
##                raise Exception("invalid dimensions")
##            if gridSize != (subGridsX * subGridsY):
##                #return "invalid dimensions"
##                raise Exception("invalid dimensions")
##        except:
##            return ValueError

        for zeroBasedIndex in xrange(gridSize**2): #named zero index as xrange starts from zero
            position = self.indexToStorageLocation(zeroBasedIndex)           
            self.data[zeroBasedIndex + 1] = data[position-1]            
        
    def __repr__(self):
        pass #rebuildable representation

    def __str__(self):
        gridSize = self.getGridSize()
        subGridsX = self.getSubGridsX()
        subGridsY = self.getSubGridsY()
        string = ""

        for zeroBasedIndex in xrange(gridSize**2):

            position = self.indexToStorageLocation(zeroBasedIndex)
            
            if zeroBasedIndex % (gridSize * subGridsX) == 0:
                string += "\n" + (gridSize + (subGridsX * (subGridsY - 1)) + (subGridsX + 1) * 2) * "=" # horizontal tiles           
            if zeroBasedIndex % gridSize == 0 and zeroBasedIndex % (gridSize * subGridsX) == 0: #new line after horizontal dividers
                string += "\n"
            elif zeroBasedIndex % gridSize == 0 and zeroBasedIndex % (gridSize * subGridsX) != 0: # new line after last number in row
                string += "||" + "\n"
            if (position - 1) % subGridsY == 0: # pipe before first row in subGrid
                string += "||"

            if (zeroBasedIndex + 1) % subGridsY == 0: #last number in subGrid row
                string += str(self.data[position])
            else:
                string += str(self.data[position]) + " "

            if (zeroBasedIndex + 1) % (gridSize * subGridsX) == 0: # pipe after last number in row
                string += "||"

        string += "\n" + (gridSize + (subGridsX * (subGridsY - 1)) + (subGridsX + 1) * 2) * "=" # remaining horizontal tiles

        return string

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
        
        firstSubGridInRow = ((subGridRow - 1) * subGridsY) + 1
        lastSubGridInRow = firstSubGridInRow + subGridsY
        subGridsInRow = range(firstSubGridInRow, lastSubGridInRow)
        print subGridsInRow

        for i in subGridsInRow:
            firstMemberInSubGrid = ((i - 1) * gridSize) + 1
            firstRowMemberInSubGrid = firstMemberInSubGrid + ((rowInSubGrid - 1) * subGridsX)

            j = subGridsX
            while j != 0:
                reference = (firstRowMemberInSubGrid + j) - 1
                rowMembers.append(reference)
                resolvedMembers.append(self.getData()[reference])
                j -= 1
            
        return dict(zip(rowMembers,resolvedMembers))

    def getColMembers(self, location):
        gridSize = self.getGridSize()
        subGridsX = self.getSubGridsX()
        subGridsY = self.getSubGridsY()
        columnInSubGrid = self.getColumnInSubGrid(location)

        columnMembers = []
        resolvedMembers = []
        subGridsInColumn = []

        subGridColumn = self.getSubGrid(location) % subGridsY
        if subGridColumn == 0:
            subGridColumn = subGridsY

        firstSubGridInColumn = subGridColumn
        for i in xrange(subGridsY):
            subGridsInColumn.append(firstSubGridInColumn + (subGridsX * i))

        for i in subGridsInColumn:
            firstMemberInSubGrid = ((i - 1) * gridSize) + 1
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
        setOfPossibleNumbers = set(xrange(1, self.gridSize + 1))
        for i in xrange(self.gridSize): # subGrid
            existingValues = []    

            for location, value in self.getSubGridMembers((i * self.gridSize) + 1).iteritems():
                if value != '0':
                    existingValues.append(int(value)) # int for diff

            for location, value in self.getSubGridMembers((i * self.gridSize) + 1).iteritems():
                if self.resolveMember(location) == '0':
                    setOfNonExistingValues = setOfPossibleNumbers.difference(set(existingValues))
                    self.ghostData[location] = list(setOfNonExistingValues)

        for i in xrange(self.gridSize): #columns
            existingValues = []
            reference = ((i / self.subGridsY) * self.gridSize) + ((i + 1) % self.subGridsY)

            for location, value in self.getColMembers(reference).iteritems():
                if value != '0':
                    existingValues.append(int(value))

            for location, value in self.getColMembers(reference).iteritems():
                if self.resolveMember(location) == '0':
                    setOfExistingGhostValues = set(self.ghostData[location])
                    setOfNonExistingValues = setOfPossibleNumbers.difference(set(existingValues))
                    self.ghostData[location] = list(setOfExistingGhostValues.intersection(setOfNonExistingValues))

        for i in xrange(self.gridSize): #rows
            existingValues = []
            reference = ((((i + self.subGridsX) / self.subGridsX) - 1) * self.gridSize * self.subGridsX) + \
                        ((i % self.subGridsX) * self.subGridsY) + 1

            for location, value in self.getRowMembers(reference).iteritems():
                if value != '0':
                    existingValues.append(int(value))            

            for location, value in self.getRowMembers(reference).iteritems():
                if self.resolveMember(location) == '0':
                    setOfExistingGhostValues = set(self.ghostData[location])
                    setOfNonExistingValues = setOfPossibleNumbers.difference(set(existingValues))
                    self.ghostData[location] = list(setOfExistingGhostValues.intersection(setOfNonExistingValues))

    def oneGhostLeft(self):
        self.populateGhosts()
        keysToDelete = []

        for location, value in self.ghostData.iteritems():
            if len(value) == 1:
                self.data[location] = str(value[0])
                keysToDelete.append(location)

        if len(keysToDelete) > 0:
            for location in keysToDelete:
                del self.ghostData[location]
            self.populateGhosts()
            self.oneGhostLeft()
        else:
            return
