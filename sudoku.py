# -*- coding: cp1252 -*-

#subGridsx = amount of subgrids in X plane
def isPrime(n):
    from math import sqrt, ceil
    if n <= 2:
        return True

    for i in xrange(2, int(ceil(sqrt(n))) + 1):
        if n % i == 0:
            return False

    return True

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

        self.candidates = {}
        self.userCandidates = {}
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
        # gridSize is the (nearest) square root of the length of the data.
        # It is the nearest square as we cannot guarantee how many values will be
        # provided
        self.gridSize = int(len(data) ** 0.5)

        # If the amount of values provided is not a square number the puzzle will be invalid.
        # The amount of values is compared to self.gridSize, the nearest square of the number
        # of values provided.
        if len(data) != self.gridSize ** 2:
            raise Exception("Incorrect number of values provided.")

        #if the gridSize is prime subGrids will equal either rows or columns
        #problems will ensue.
        if isPrime(self.gridSize):
            raise Exception("Invalid grid Size will be generated.")

        #if the gridSize is a perfect square, then the the amount of subGrids in
        #X and Y must be the square root of the gridSize.
        gridSizeRoot = (self.gridSize ** 0.5)
        if gridSizeRoot.is_integer():
            self.subGridsX = int(gridSizeRoot)
            self.subGridsY = self.subGridsX
            return

        #returns highest factor less than or equal to half the gridSize.
        factor = factors(self.gridSize)

        #if the horizontalFormat is True, there will be more subGrids in the X
        #plane than the Y
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
        self.values = {position + 1 : data[position] for position in range(self.gridSize ** 2)}
        for location, value in self.values.iteritems():
            try:
                self.values[location] = int(value)
            except ValueError:
                if value not in self.setOfPossibleValues:
                    self.values[location] = 0

        self.constants = [location for location in self.values if not self.isEmpty(location)]

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

    def isComplete(self):
        from operator import add
        if reduce(add, [1 for location in self.getLocations() if not self.isEmpty(location)], 0) == self.getGridSize() ** 2:
            return True

        return False




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




    def generateSubGridGroups(self):
        gridSize = self.gridSize
        subGridsY = self.subGridsY

        subGridGroups = []
        offsets = []

        for position in xrange(gridSize):
            rowOffset = (position / subGridsY) * gridSize
            columnOffset = (position % gridSize) % subGridsY

            offsets.append(rowOffset + columnOffset)

        for startLocation in self.getSubGridStartLocations():
            subGridGroup = [startLocation + offset for offset in offsets]
            subGridGroups.append(subGridGroup)

        return subGridGroups

    def generateRowGroups(self):
        gridSize = self.gridSize

        rowGroups = []

        for startLocation in self.getRowStartLocations():
            rowGroups.append([startLocation + offset for offset in xrange(gridSize)])

        return rowGroups

    def generateColumnGroups(self):
        gridSize = self.gridSize

        columnGroups = []

        for startLocation in self.getColumnStartLocations():
            columnGroups.append([startLocation + offset * gridSize for offset in xrange(gridSize)])

        return columnGroups




    def generatePointerGroups(self, n):
        self.initialiseIntersections()

        from itertools import combinations

        pointers = []

        for subGrid in self.intersectionTypes["subGrid"]:
            for combination in combinations(subGrid, n):

                rowsOfCombination = [self.getRow(location) for location in combination]
                if all(row == rowsOfCombination[0] for row in rowsOfCombination):
                    pointers.append((combination, "row"))

                columnsOfCombination = [self.getColumn(location) for location in combination]
                if all(column == columnsOfCombination[0] for column in columnsOfCombination):
                    pointers.append((combination, "column"))

        return pointers

    def generateXWingGroups(self):
        self.initialiseIntersections()

        xWingGroups = []

        # gridSize: gridSize * 2 are the indices for the row groups
        # we use the indices from intersection groups instead of row groups,
        # as the row groups in intersection groups will be pre-pruned.
        for firstRowIndex, firstRow in enumerate(self.intersectionTypes["row"]):
            if len(firstRow) < 2:
                continue

            for firstRowGroup in self.getNLocationsOnRow(firstRow, 2):

                    for secondRow in self.intersectionTypes["row"][firstRowIndex + 1:]:
                        if len(secondRow) < 2:
                            continue

                        for secondRowGroup in self.getNLocationsOnRow(secondRow, 2):
                                if self.getSubGrid(firstRowGroup[0]) == self.getSubGrid(secondRowGroup[1]):
                                    continue

                                if self.getColumn(firstRowGroup[0]) == self.getColumn(secondRowGroup[0]) and \
                                self.getColumn(firstRowGroup[1]) == self.getColumn(secondRowGroup[1]):
                                    xWingGroups.append((firstRowGroup + secondRowGroup))

        return xWingGroups

    def generateSwordfishGroups(self):
        self.initialiseIntersections()

        return self.generate2SwordfishGroups() + self.generate3SwordfishGroups()

    def generate2SwordfishGroups(self):

        swordfishGroups = []

        # 2 location per line swordfish
        for firstRowIndex, firstRow in enumerate(self.intersectionTypes["row"][:-3]):
            if len(firstRow) < 2:
                continue

            for firstRowGroup in self.getNLocationsOnRow(firstRow, 2):

                for secondRowIndex, secondRow in enumerate(self.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 2:
                        continue

                    for secondRowGroup in self.getNLocationsOnRow(secondRow, 2):
                        alignments = 0

                        for locationOne in firstRowGroup:
                            for locationTwo in secondRowGroup:
                                if self.getColumn(locationOne) == self.getColumn(locationTwo):
                                    alignments += 1
                                    locationsInSameColumn = (locationOne, locationTwo)

                        if alignments != 1:
                            continue

                        for thirdRow in self.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 2:
                                continue

                            for thirdRowGroup in self.getNLocationsOnRow(thirdRow, 2):
                                alignments2 = 0

                                for locationOne in thirdRowGroup:
                                    for row in (firstRowGroup, secondRowGroup):
                                        for locationTwo in [location for location in row if location not in locationsInSameColumn]:
                                            if self.getColumn(locationOne) == self.getColumn(locationTwo):
                                                alignments2 += 1

                                if alignments2 == 2:
                                    swordfishGroups.append(firstRowGroup + secondRowGroup + thirdRowGroup)

        return swordfishGroups

    def generate3SwordfishGroups(self):
        self.initialiseIntersections()

        swordfishGroups = []

        # 3 location per line swordfish
        for firstRowIndex, firstRow in enumerate(self.intersectionTypes["row"][:-3]):
            if len(firstRow) < 3:
                continue

            for firstRowGroup in self.getNLocationsOnRow(firstRow, 3):

                for secondRowIndex, secondRow in enumerate(self.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 3:
                        continue

                    for secondRowGroup in self.getNLocationsOnRow(secondRow, 3):
                        alignments = 0

                        for i in xrange(3):
                            if self.getColumn(firstRowGroup[i]) == self.getColumn(secondRowGroup[i]):
                                    alignments += 1

                        if alignments != 3:
                            continue

                        for thirdRow in self.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 3:
                                continue

                            for thirdRowGroup in self.getNLocationsOnRow(thirdRow, 3):
                                alignments2 = 0

                                for i in xrange(3):
                                    if self.getColumn(firstRowGroup[i]) == self.getColumn(thirdRowGroup[i]):
                                        alignments2 += 1

                                if alignments2 == 3:
                                    swordfishGroups.append(firstRowGroup + secondRowGroup + thirdRowGroup)

        return swordfishGroups




    def getSubGrid(self, location):
        subGridRow = (location - 1) / (self.subGridsX * self.gridSize)
        subGridRowOffset = subGridRow * self.subGridsX

        subGridColumn = (self.getColumn(location) - 1) / self.subGridsY + 1

        return subGridRowOffset + subGridColumn

    def getRow(self, location):
        return (location - 1) / self.gridSize + 1

    def getColumn(self, location):
        return (location - 1) % self.gridSize + 1




    def getSubGridNeighbours(self, location, *exclusions):
        subGridGroup = self.intersectionTypes["subGrid"][self.getSubGrid(location) - 1]
        neighbours = [neighbour for neighbour in subGridGroup if neighbour != location and self.isEmpty(neighbour)]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def getRowNeighbours(self, location, *exclusions):
        rowGroup = self.intersectionTypes["row"][self.getRow(location) - 1]
        neighbours = [neighbour for neighbour in rowGroup if neighbour != location and self.isEmpty(neighbour)]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def getColumnNeighbours(self, location, *exclusions):
        columnGroup = self.intersectionTypes["column"][self.getColumn(location) - 1]
        neighbours = [neighbour for neighbour in columnGroup if neighbour != location and self.isEmpty(neighbour)]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def getAllNeighbours(self, location, *exclusions):
        return set(self.getSubGridNeighbours(location, *exclusions) +
        self.getRowNeighbours(location, *exclusions) +
        self.getColumnNeighbours(location, *exclusions))




    def isEmpty(self, location):
        if self.values[location] not in self.setOfPossibleValues:
            return True

        return False

    def isConstant(self, location):
        if location in self.constants:
            return True

        return False

    def isValidInput(self, value):
        if value in self.setOfPossibleValues:
            return True

        return False

    def getLocations(self):
        return range(1, self.gridSize ** 2 + 1)

    def getNLocationsOnRow(self, row, n):
        from itertools import combinations

        return combinations(row, n)

    def setLocationValue(self, location, value):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(value):
            raise Exception("value is not vaild")

        self.values[location] = value

        if location in self.userCandidates:
            del self.userCandidates[location]

    def getLocationValue(self, location):
        return self.values[location]

    def clearLocation(self, location):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        self.values[location] = 0

    def getSolvingCandidates(self, *locations):
        return set([]).union(*[self.candidates[location] for location in locations])

    def getCommonCandidates(self, *locations):
        return set.intersection(*[self.candidates[location] for location in locations])

    def getUserCandidates(self, location):
        return self.userCandidates[location]

    def toggleUserCandidate(self, location, candidate):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(value):
            raise Exception("candidate is not vaild")

        if not self.isEmpty(location):
            self.clearLocation(location)

        if not self.locationHasUserCandidates(location):
            self.userCandidates[location] = [candidate]
            return

        if candidate in self.userCandidates[location]:
            self.userCandidates[location].remove(candidate)
        else:
            self.userCandidates[location].append(candidate)

    def locationHasSolvingCandidates(self, location):
        if location not in self.candidates:
            return False

        if not self.candidates[location]:
            return False

        return True

    def locationHasUserCandidates(self, location):
        if location not in self.userCandidates:
            return False

        if not self.userCandidates[location]:
            return False

        return True

    def getGridSize(self):
        return self.gridSize

    def getSubGridsX(self):
        return self.subGridsX

    def getSubGridsY(self):
        return self.subGridsY

    def getSubGridLength(self):
        return self.subGridsY

    def getSubGridHeight(self):
        return self.subGridsX

    def getPossibleValues(self):
        return sorted(self.setOfPossibleValues)

    def getNumberOfFilledLocations(self):
        from operator import add
        return reduce(add, [1 for location in self.values if not self.isEmpty(location)], 0)




    def solve(self, maxLevel, history = None):
        methods = [self.nakedSingle, self.hiddenSingle,
            self.nakedTwin, self.hiddenTwin,
            self.pointingPair, self.pointingTriplet,
            self.boxLineReduction2, self.boxLineReduction3,
            self.nakedTriplet, self.hiddenTriplet,
            self.xWing, self.swordfish]

        if self.isComplete():
            return True, [entry[0] for entry in history if history != None]

        if maxLevel > len(methods) or maxLevel < 1:
            maxLevel = len(methods)

        #if solver is run for the first time, solve using first method
        if history == None:
            methods[0]()
            history = [(0, self.changes)]
            return self.solve(maxLevel, history)
        
        #if last attempt was successful, go back to first level

        lastMethod = history[-1][0]
        if history[-1][1] == True:
            nextMethod = 0
        #or if unsuccessful, increase level or exit if highest level was tried
        else:
            if lastMethod == maxLevel - 1:
                return False, [entry[0] for entry in history if history != None]
            else:
                nextMethod = lastMethod + 1

        methods[nextMethod]()
        history.append((nextMethod, self.changes))
        
        return self.solve(maxLevel, history)




    def initialiseIntersections(self, *intersectionTypes):
        initialiseCandidates = False
        #three main intersection types needed for candidates to work
        for intersectionType in ("subGrid", "row", "column"):
            if intersectionType in self.intersectionTypes:
                continue

            initialiseCandidates = True

            typeName = intersectionType[0].capitalize() + intersectionType[1:]

            self.intersectionTypes[intersectionType] = eval("self.generate" + typeName + "Groups()")

        if initialiseCandidates:
            self.initialiseCandidates()

        if "xWing" in intersectionTypes:
            if "xWing" not in self.intersectionTypes:
                self.intersectionTypes["xWing"] = self.generateXWingGroups()

        if "swordfish" in intersectionTypes:
            if "swordfish" not in self.intersectionTypes:
                self.intersectionTypes["swordfish"] = self.generateSwordfishGroups()

        for intersectionType in intersectionTypes:
            try:
                # n variable
                currentIntersectionType = intersectionType[0]
                n = intersectionType[1]
            except:
                continue
            if currentIntersectionType == "pointer":
                if ("pointer", n) not in self.intersectionTypes:
                    self.intersectionTypes[("pointer", n)] = self.generatePointerGroups(n)

        self.updatePuzzle()

    def initialiseCandidates(self):

        for location in [location for location in self.values if self.isEmpty(location)]:

            setOfSurroundingValues = set([self.values[neighbour] for neighbour in self.getAllNeighbours(location) if not self.isEmpty(neighbour)])

            self.candidates[location] = self.setOfPossibleValues - setOfSurroundingValues




    def updatePuzzle(self):

        for intersectionType in ["subGrid", "row", "column"]:

            for group in self.intersectionTypes[intersectionType]:

                setOfSurroundingValues = set([self.values[location] for location in group])

                for location in group[:]:
                    if self.isEmpty(location):
                        self.candidates[location] -= setOfSurroundingValues
                    else:
                        group.remove(location)

        self.updatePointerGroups()
        self.updateXWingGroups()
        self.updateSwordfishGroups()        

    def updatePointerGroups(self):
        # As pointer groups uses a tuple containing the pointer name and 
        # type as the dictionary key, we must try each intersection type
        # as it is unknown what size pointer group is initialsed.
        for intersectionType in self.intersectionTypes:
            try:
                currentIntersectionType = intersectionType[0]
                n = intersectionType[1]
            except:
                continue

            if currentIntersectionType == "pointer":
                # For every pointer group, we must check if any location in it
                # has been filled (making the pointer group invalid.) In this
                # case we remove the pointer group, after checking it still
                # exists as there is a chance it may have been deleted by a
                # location discovered earlier in the same combination.
                for group in self.intersectionTypes[("pointer", n)]:
                    combination = group[0]
                    for location in combination:
                        if self.isEmpty(location):
                            continue
                        if group in self.intersectionTypes[("pointer", n)]:
                            self.intersectionTypes[("pointer", n)].remove(group)

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

    def updateSwordfishGroups(self):
        if "swordfish" not in self.intersectionTypes:
            return

        for group in self.intersectionTypes["swordfish"]:
            for location in group:
                if self.isEmpty(location):
                    continue
                if location not in group:
                    continue
                if group in self.intersectionTypes["swordfish"]:
                    self.intersectionTypes["swordfish"].remove(group)




    def nakedSingle(self):
        self.initialiseIntersections()

        self.changes = False

        for location, candidates in self.candidates.items():
            if len(candidates) == 1:
                self.values[location] = candidates.pop()
                del self.candidates[location]
                self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def nakedN(self, n):
        self.initialiseIntersections()

        self.changes = False

        from itertools import combinations

        for intersectionType in ["subGrid", "row", "column"]:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in combinations(group, n):

                    nakedNcandidates = self.getSolvingCandidates(*combination)

                    if len(nakedNcandidates) != n:
                        continue

                    surroundingLocations = [location for location in group if location not in combination]

                    for surroundingLocation in surroundingLocations:

                        if any(candidate in nakedNcandidates for candidate in self.candidates[surroundingLocation]):

                            self.candidates[surroundingLocation] -= nakedNcandidates
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

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in combinations(group, n):

                    surroundingLocations = [location for location in group if location not in combination]

                    combinationCandidates = self.getSolvingCandidates(*combination)
                    surroundingCandidates = self.getSolvingCandidates(*surroundingLocations)
                    uniqueCombinationCandidates = combinationCandidates - surroundingCandidates

                    if len(uniqueCombinationCandidates) != n:
                        continue

                    for location in combination:

                        if any(candidate in surroundingCandidates for candidate in self.candidates[location]):

                            self.candidates[location] -= surroundingCandidates
                            self.changes = True

                    for location in surroundingLocations:

                        if not self.isEmpty(location):
                            continue

                        if any(candidate in uniqueCombinationCandidates for candidate in self.candidates[location]):

                            self.candidates[location] -= uniqueCombinationCandidates
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




    def pointingN(self, n):
        self.initialiseIntersections(("pointer", n))
        self.changes = False

        for group in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = group[0], group[1]
            subGridNeighbours = self.getSubGridNeighbours(combination[0], *combination)
            subGridNeighbourCandidates = self.getSolvingCandidates(*subGridNeighbours)
            commonPointerCandidates = self.getCommonCandidates(*combination)

            if pointerType == "row":
                rowNeighbours = self.getRowNeighbours(combination[0], *combination)

                for candidate in commonPointerCandidates:
                    if candidate not in subGridNeighbourCandidates:
                        for location in rowNeighbours:
                            if candidate in self.candidates[location]:
                                self.candidates[location].remove(candidate)
                                self.changes = True

            elif pointerType == "column":
                columnNeighbours = self.getColumnNeighbours(combination[0], *combination)

                for candidate in commonPointerCandidates:
                    if candidate not in subGridNeighbourCandidates:
                        for location in columnNeighbours:
                            if candidate in self.candidates[location]:
                                self.candidates[location].remove(candidate)
                                self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def pointingPair(self):
        return self.pointingN(2)

    def pointingTriplet(self):
        return self.pointingN(3)




    def boxLineReductionN(self, n):
        self.initialiseIntersections(("pointer", n))
        self.changes = False

        for group in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = group[0], group[1]
            subGridNeighbours = self.getSubGridNeighbours(combination[0], *combination)
            commonPointerCandidates = self.getCommonCandidates(*combination)

            if pointerType == "row":
                rowNeighbours = self.getRowNeighbours(combination[0], *combination)
                rowNeighbourCandidates = self.getSolvingCandidates(*rowNeighbours)

                for candidate in commonPointerCandidates:
                    if candidate not in rowNeighbourCandidates:
                        for location in subGridNeighbours:
                            if candidate in self.candidates[location]:
                                self.candidates[location].remove(candidate)
                                self.changes = True

            elif pointerType == "column":
                columnNeighbours = self.getColumnNeighbours(combination[0], *combination)
                columnNeighbourCandidates = self.getSolvingCandidates(*columnNeighbours)

                for candidate in commonPointerCandidates:
                    if candidate not in columnNeighbourCandidates:
                        for location in subGridNeighbours:
                            if candidate in self.candidates[location]:
                                self.candidates[location].remove(candidate)
                                self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def boxLineReduction2(self):
        return self.boxLineReductionN(2)

    def boxLineReduction3(self):
        return self.boxLineReductionN(3)




    def xWing(self):
        self.initialiseIntersections("xWing")

        self.changes = False

        from collections import defaultdict
        from itertools import chain

        xWings = defaultdict(list)

        for group in self.intersectionTypes["xWing"]:

            commonXWingCandidates = self.getCommonCandidates(*group)

            if len(commonXWingCandidates) == 0:
                continue

            rowOneNeighbourCandidates = self.getSolvingCandidates(*self.getRowNeighbours(group[0], *group))
            rowTwoNeighbourCandidates = self.getSolvingCandidates(*self.getRowNeighbours(group[2], *group))
            columnOneNeighbourCandidates = self.getSolvingCandidates(*self.getColumnNeighbours(group[0], *group))
            columnTwoNeighbourCandidates = self.getSolvingCandidates(*self.getColumnNeighbours(group[1], *group))

            for candidate in commonXWingCandidates:
                if ((candidate not in rowOneNeighbourCandidates and
                    candidate not in rowTwoNeighbourCandidates)
                    or
                    (candidate not in columnOneNeighbourCandidates and
                    candidate not in columnTwoNeighbourCandidates)):
                    xWings[group].append(candidate)

        for group, candidates in xWings.iteritems():

            xWingNeighbours = (self.getRowNeighbours(group[0], *group) +
                self.getRowNeighbours(group[2], *group) +
                self.getColumnNeighbours(group[0], *group) +
                self.getColumnNeighbours(group[1], *group))

            for location in xWingNeighbours:

                for candidate in candidates:
                    if candidate in self.candidates[location]:
                        self.candidates[location].remove(candidate)
                        self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def swordfish(self):
        self.initialiseIntersections("swordfish")

        self.changes = False

        from collections import defaultdict

        swordfishes = defaultdict(list)

        for group in self.intersectionTypes["swordfish"]:

            commonCandidates = self.getCommonCandidates(*group)

            if len(commonCandidates) == 0:
                continue

            rowOneLocation = group[0]
            rowTwoLocation = group[3]

            if len(group) == 9:
                rowThreeLocation = group[6]
                columnOneLocation = group[0]
                columnTwoLocation = group[1]
                columnThreeLocation = group[2]
            else:
                sortedGroup = sorted(group, key=self.getColumn)
                rowThreeLocation = group[4]
                columnOneLocation = sortedGroup[0]
                columnTwoLocation = sortedGroup[2]
                columnThreeLocation = sortedGroup[4]

            otherRowOneCandidates = self.getSolvingCandidates(*self.getRowNeighbours(rowOneLocation, *group))
            otherRowTwoCandidates = self.getSolvingCandidates(*self.getRowNeighbours(rowTwoLocation, *group))
            otherRowThreeCandidates = self.getSolvingCandidates(*self.getRowNeighbours(rowThreeLocation, *group))
            otherColumnOneCandidates = self.getSolvingCandidates(*self.getColumnNeighbours(columnOneLocation, *group))
            otherColumnTwoCandidates = self.getSolvingCandidates(*self.getColumnNeighbours(columnTwoLocation, *group))
            otherColumnThreeCandidates = self.getSolvingCandidates(*self.getColumnNeighbours(columnThreeLocation, *group))

            for candidate in commonCandidates:
                if (candidate not in otherRowOneCandidates and
                    candidate not in otherRowTwoCandidates and
                    candidate not in otherRowThreeCandidates):
                    swordfishes[group].append((candidate, (columnOneLocation, columnTwoLocation, columnThreeLocation), "row"))
                
                elif (candidate not in otherColumnOneCandidates and
                    candidate not in otherColumnTwoCandidates and
                    candidate not in otherColumnThreeCandidates):
                    swordfishes[group].append((candidate, (rowOneLocation, rowTwoLocation, rowThreeLocation), "column"))

        for group, swordfishList in swordfishes.iteritems():
            for swordfish in swordfishList:
                candidate = swordfish[0]
                locations = swordfish[1]
                swordfishType = swordfish[2]

                swordfishNeighbours = []

                if swordfishType == "row":
                    for location in locations:
                        swordfishNeighbours += self.getColumnNeighbours(location, *group)

                if swordfishType == "column":
                    for location in locations:
                        swordfishNeighbours += self.getRowNeighbours(location, *group)                  

                for location in swordfishNeighbours:

                    if candidate in self.candidates[location]:
                        self.candidates[location].remove(candidate)
                        self.changes = True

        if self.changes:
            self.updatePuzzle()

        return self.changes
