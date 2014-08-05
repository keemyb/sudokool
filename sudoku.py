# -*- coding: cp1252 -*-

#subGridsx = amount of subgrids in X plane
def factors(n):
    from math import sqrt, ceil
    factors = []

    for i in xrange(1, int(n / 2) + 1):
        if n % i == 0:
            factors.append(i)

    return factors[-1]

class Sudoku():
        
    def __init__(self, data, horizontalFormat = True):
        self.calculateDimensions(data, horizontalFormat)
        self.generatePossibleValues()
        self.processData(data)

        self.ghostValues = {}
        self.intersectionTypes = {}
        self.changes = False

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

            if self.isEmpty(position):
                string += "  "
            else:
                string += str(self.values[position]) + " "

            if position % gridSize == 0:
                string += vPipe + "\n"

            if position == gridSize ** 2:
                string += hPipeString

        return string

    def calculateDimensions(self, data, horizontalFormat):

        self.gridSize = int(len(data) ** 0.5)

        if (self.gridSize ** 0.5).is_integer():
            self.subGridsX = int(self.gridSize ** 0.5)
            self.subGridsY = self.subGridsX
            return
        
        factor = factors(self.gridSize)

        if horizontalFormat:
            self.subGridsY = factor
            self.subGridsX = self.gridSize / self.subGridsY
        else:
            self.subGridsX = factor
            self.subGridsY = self.gridSize / self.subGridsX

    def generatePossibleValues(self):
        if self.gridSize <= 9:
            self.setOfPossibleValues = set(xrange(1, self.gridSize + 1))
        else:
            self.setOfPossibleValues = set(xrange(1, 10))
            self.setOfPossibleValues.update(set([chr(value + 55) for value in xrange(10, self.gridSize + 1)]))

    def processData(self, data):
        if self.gridSize <= 9:
            self.values = {position + 1 : int(data[position]) for position in range(self.gridSize ** 2)}
        else:
            self.values = {position + 1 : data[position] for position in range(self.gridSize ** 2)}
            for location, value in self.values.iteritems():
                try:
                    self.values[location] = int(value)
                except ValueError:
                    continue

    def isValid(self):
        for location in xrange(1, self.gridSize ** 2 + 1):
            if not self.isEmpty(location):
                if self.values[location] not in self.setOfPossibleValues:
                    return False

                locationValue = self.values[location]

                for neighbour in self.getAllNeighbours(location):
                    if self.values[neighbour] == locationValue:
                        return False

        return True

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

    def generateCompleteSubGridGroups(self):
        gridSize = self.gridSize
        subGridsY = self.subGridsY

        completeSubGridGroups = []

        for startLocation in self.getSubGridStartLocations():
            subGridGroup = []
            
            for position in xrange(gridSize):
                rowOffset = ((position % gridSize) / subGridsY) * gridSize
                columnOffset = (position % gridSize) % subGridsY

                if not self.isEmpty(startLocation + rowOffset + columnOffset):
                    continue

                subGridGroup.append(startLocation + rowOffset + columnOffset)
            
            completeSubGridGroups.append(subGridGroup)

        return completeSubGridGroups

    def generateCompleteRowGroups(self):
        gridSize = self.gridSize

        completeRowGroups = []

        for startLocation in self.getRowStartLocations():
            completeRowGroups.append([startLocation + offset for offset in xrange(gridSize) if self.isEmpty(startLocation + offset)])
            
        return completeRowGroups

    def generateCompleteColumnGroups(self):
        gridSize = self.gridSize

        completeColumnGroups = []

        for startLocation in self.getColumnStartLocations():
            completeColumnGroups.append([startLocation + offset * gridSize for offset in xrange(gridSize) if self.isEmpty(startLocation + offset * gridSize)])

        return completeColumnGroups

    def generatePrunedSubGridGroups(self):
        prunedSubGridGroups = []

        for group in self.generateCompleteSubGridGroups():
            prunedSubGridGroup = []
            for location in group:
                if self.isEmpty(location):
                    prunedSubGridGroup.append(location)
            prunedSubGridGroups.append(prunedSubGridGroup)

        return prunedSubGridGroups

    def generatePrunedRowGroups(self):
        prunedRowGroups = []

        for group in self.generateCompleteRowGroups():
            prunedRowGroup = []
            for location in group:
                if self.isEmpty(location):
                    prunedRowGroup.append(location)
            prunedRowGroups.append(prunedRowGroup)

        return prunedRowGroups

    def generatePrunedColumnGroups(self):
        prunedColumnGroups = []

        for group in self.generateCompleteColumnGroups():
            prunedColumnGroup = []
            for location in group:
                if self.isEmpty(location):
                    prunedColumnGroup.append(location)
            prunedColumnGroups.append(prunedColumnGroup)

        return prunedColumnGroups

    def generateXWingGroups(self):
        self.initialiseIntersections()
        
        gridSize = self.gridSize
        subGridsX = self.subGridsX
        subGridsY = self.subGridsY

        xWingGroups = []

        # gridSize: gridSize * 2 are the indices for the row groups
        # we use the indices from intersection groups instead of row groups,
        # as the row groups in intersection groups will be pre-pruned.
        for firstRowIndex, firstRow in enumerate(self.intersectionTypes["row"]):
            if len(firstRow) < 2:
                continue

            for locationOne in firstRow:
                for locationTwo in firstRow:
                    if self.getColumn(locationOne) >= self.getColumn(locationTwo):
                        continue
                    
                    for secondRow in self.intersectionTypes["row"][firstRowIndex + 1:]:
                        if len(secondRow) < 2:
                            continue
                        
                        for locationThree in secondRow:
                            for locationFour in secondRow:
                                if self.getSubGrid(locationOne) == self.getSubGrid(locationFour):
                                    continue

                                if self.getColumn(locationOne) == self.getColumn(locationThree) and \
                                self.getColumn(locationTwo) == self.getColumn(locationFour):
                                    xWingGroups.append(tuple((locationOne, locationTwo, locationThree, locationFour)))
        
        return xWingGroups

    def getSubGrid(self, location):
        subGridRow = (location - 1) / (self.subGridsX * self.gridSize)
        subGridRowOffset = subGridRow * self.subGridsX

        subGridColumn = (self.getColumn(location) - 1) / self.subGridsY + 1

        return subGridRowOffset + subGridColumn

    def getRow(self, location):
        return (location - 1) / self.gridSize + 1

    def getColumn(self, location):
        return (location - 1) % self.gridSize + 1

    def getSubGridNeighbours(self, location):
        subGrid = self.getSubGrid(location)
        maxSize = self.gridSize - 1
        neighbours = []

        for loopingLocation in xrange(1, self.gridSize ** 2 + 1):
            if len(neighbours) > maxSize:
                break
            if loopingLocation == location:
                continue
            if subGrid == self.getSubGrid(loopingLocation):
                neighbours.append(loopingLocation)
        
        return neighbours

    def getRowNeighbours(self, location):
        row = self.getRow(location)
        maxSize = self.gridSize - 1
        neighbours = []

        for loopingLocation in xrange(1, self.gridSize ** 2 + 1):
            if len(neighbours) > maxSize:
                break
            if loopingLocation == location:
                continue
            if row == self.getRow(loopingLocation):
                neighbours.append(loopingLocation)
        
        return neighbours

    def getColumnNeighbours(self, location):
        column = self.getColumn(location)
        maxSize = self.gridSize - 1
        neighbours = []

        for loopingLocation in xrange(1, self.gridSize ** 2 + 1):
            if len(neighbours) > maxSize:
                break
            if loopingLocation == location:
                continue
            if column == self.getColumn(loopingLocation):
                neighbours.append(loopingLocation)
        
        return neighbours

    def getAllNeighbours(self, location):

        return set(self.getSubGridNeighbours(location) + \
            self.getRowNeighbours(location) + \
            self.getColumnNeighbours(location))

    def isEmpty(self, location):
        if self.values[location] not in self.setOfPossibleValues:
            return True
        
        return False

    def initialiseIntersections(self, *intersectionTypes):
        initialiseGhosts = False
        #three main intersection types needed for ghostValues to work
        for intersectionType in ("subGrid", "row", "column"):
            if intersectionType in self.intersectionTypes:
                continue

            initialiseGhosts = True

            typeName = intersectionType[0].capitalize() + intersectionType[1:]

            self.intersectionTypes[intersectionType] = eval("self.generatePruned" + typeName + "Groups()")

        if initialiseGhosts:
            self.initialiseGhosts()

        for intersectionType in intersectionTypes:

            if intersectionType in self.intersectionTypes:
                continue

            #generation methods are generateSubGridGroups, but types are specified as "subGrid"
            typeName = intersectionType[0].capitalize() + intersectionType[1:]

            self.intersectionTypes[intersectionType] = eval("self.generate" + typeName + "Groups()")

        self.updatePuzzle()

    def initialiseGhosts(self):

        for location in [location for location in self.values if self.isEmpty(location)]:

            setOfSurroundingValues = set([self.values[neighbour] for neighbour in self.getAllNeighbours(location) if not self.isEmpty(neighbour)])

            self.ghostValues[location] = self.setOfPossibleValues - setOfSurroundingValues

    def updatePuzzle(self):
        
        for intersectionType in ["subGrid", "row", "column"]:

            for group in self.intersectionTypes[intersectionType]:

                setOfSurroundingValues = set([self.values[location] for location in group if not self.isEmpty(location)])

                for location in group[:]:
                    if self.isEmpty(location):
                        self.ghostValues[location] -= setOfSurroundingValues
                    else:
                        group.remove(location)

        self.updateXWingGroups()

    def updateXWingGroups(self):
        if "xWing" not in self.intersectionTypes:
            return
        
        for group in self.intersectionTypes["xWing"]:
            for location in group:
                if self.isEmpty(location):
                    continue
                if location not in group:
                    continue
                if group in self.intersectionTypes["xWing"]:
                    self.intersectionTypes["xWing"].remove(group)

    def nakedSingle(self):
        self.initialiseIntersections()

        self.changes = False

        for location, ghostValues in self.ghostValues.items():
            if len(ghostValues) == 1:
                self.values[location] = ghostValues.pop()
                del self.ghostValues[location]
                self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def nakedN(self, n):
        self.initialiseIntersections()

        self.changes = False

        modifiedLocations = []

        from itertools import combinations

        for intersectionType in ["subGrid", "row", "column"]:

            for group in [group for group in self.intersectionTypes[intersectionType] if len(group) > n]:

                for combination in combinations(group, n):

                    if len(set([tuple(self.ghostValues[location]) for location in combination])) == n:

                        nakedNghostValues = set([tuple(self.ghostValues[location]) for location in combination])

                        for surroundingLocation in [location for location in group if location not in combination]:

                            if any(ghostValue in nakedNghostValues for ghostValue in self.ghostValues[surroundingLocation]):

                                self.ghostValues[surroundingLocation] -= nakedNghostValues
                                self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def nakedTwin(self):

        return self.nakedN(2)

    def nakedTriplet(self):

        return self.nakedN(3)

    def hiddenN(self, n):
        self.initialiseIntersections()

        self.changes = False
        
        from itertools import combinations

        for intersectionType in ["subGrid", "row", "column"]:

            for group in [group for group in self.intersectionTypes[intersectionType] if len(group) > n]:

                for combination in combinations(group, n):

                    surroundingLocations = [location for location in group if location not in combination]

                    setsOfCombinationGhosts = [self.ghostValues[location] for location in combination if self.isEmpty(location)]
                    setOfCombinationGhosts = set([ghostValue for ghostValueSets in setsOfCombinationGhosts for ghostValue in ghostValueSets])
                    setsOfSurroundingGhosts = [self.ghostValues[surroundingLocation] for surroundingLocation in surroundingLocations if self.isEmpty(surroundingLocation)]
                    setOfSurroundingGhosts = set([ghostValue for ghostValueSets in setsOfSurroundingGhosts for ghostValue in ghostValueSets])
                    setOfUniqueGhostsToCombination = setOfCombinationGhosts - setOfSurroundingGhosts

                    if len(setOfUniqueGhostsToCombination) == n:

                        for location in combination:

                            if any(ghostValue in setOfSurroundingGhosts for ghostValue in self.ghostValues[location]):

                                self.ghostValues[location] -= setOfSurroundingGhosts
                                self.changes = True

                        for location in surroundingLocations:

                            if not self.isEmpty(location):
                                continue

                            if any(ghostValue in setOfUniqueGhostsToCombination for ghostValue in self.ghostValues[location]):

                                self.ghostValues[location] -= setOfUniqueGhostsToCombination
                                self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def hiddenSingle(self):

        return self.hiddenN(1)

    def hiddenTwin(self):

        return self.hiddenN(2)

    def hiddenTriplet(self):

        return self.hiddenN(3)

    def xWing(self):
        self.initialiseIntersections("xWing")

        self.changes = False
        
        from collections import defaultdict
        from itertools import chain
        
        xWings = defaultdict(list)

        for group in self.intersectionTypes["xWing"]:

            commonXWingGhosts = set.intersection(*[self.ghostValues[location] for location in group])

            if len(commonXWingGhosts) == 0:
                continue

            rowOneNeighbourGhosts = list(chain(*[self.ghostValues[location] for location in self.getRowNeighbours(group[0]) if location not in group and self.isEmpty(location)]))
            rowTwoNeighbourGhosts = list(chain(*[self.ghostValues[location] for location in self.getRowNeighbours(group[2]) if location not in group and self.isEmpty(location)]))
            columnOneNeighbourGhosts = list(chain(*[self.ghostValues[location] for location in self.getColumnNeighbours(group[0]) if location not in group and self.isEmpty(location)]))
            columnTwoNeighbourGhosts = list(chain(*[self.ghostValues[location] for location in self.getColumnNeighbours(group[1]) if location not in group and self.isEmpty(location)]))

            for ghost in commonXWingGhosts:
                if (ghost not in rowOneNeighbourGhosts and ghost not in rowTwoNeighbourGhosts) or \
                (ghost not in columnOneNeighbourGhosts and ghost not in columnTwoNeighbourGhosts):
                    xWings[group].append(ghost)

        for group, ghosts in xWings.iteritems():

            xWingNeighbours = self.getRowNeighbours(group[0]) + self.getRowNeighbours(group[2])
            xWingNeighbours += self.getColumnNeighbours(group[0]) + self.getColumnNeighbours(group[1])
            xWingNeighbours = set([neighbour for neighbour in xWingNeighbours if self.isEmpty(neighbour) and neighbour not in group])
            
            for location in xWingNeighbours:

                for ghost in ghosts:
                    if ghost in self.ghostValues[location]:
                        self.ghostValues[location].remove(ghost)
                        self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes