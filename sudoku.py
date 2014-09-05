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

        self.solveMode = False
        self.changes = False

        self.intersectionTypes = {}

        self.multiples = ("Single", "Pair", "Triplet", "Quadruplet")
        self.units = ["row", "column", "subGrid"]

        self.staticGroups = {"row": self.generateRowGroups(),
                             "column": self.generateColumnGroups(),
                             "subGrid": self.generateSubGridGroups()}

        self.neighbourMethods = {"row": self.getRowNeighbours,
                                 "column": self.getColumnNeighbours,
                                 "subGrid": self.getSubGridNeighbours}

        self.allNeighbourMethods = {"row": self.getAllRowNeighbours,
                                    "column": self.getAllColumnNeighbours,
                                    "subGrid": self.getAllSubGridNeighbours}

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        pass

    def __str__(self):
        gridSize = self.gridSize
        subGridsX = self.subGridsX
        subGridsY = self.subGridsY
        string = ""
        vPipe = "="
        hPipe = "="
        # first line to accommodate vertical pipe and following spaces (minus one to account for last v pipe)
        # second line for numbers (and following spaces)
        hPipeString = (hPipe * ((len(vPipe) + 1) * (subGridsX + 1) - 1) +
                       hPipe * (gridSize * 2) +
                       "\n")

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
        self.initialiseIntersections()

        for location in xrange(1, self.gridSize ** 2 + 1):

            if location in xrange(1, self.gridSize ** 2 + 1, self.gridSize + 1):
                for group in self.staticGroups.itervalues():
                    for unit in group:
                        if location not in unit:
                            continue
                        values = [self.getValue(location) for location in unit if not self.isEmpty(location)]
                        if sorted(list(set(values))) != sorted(values):
                            return False

            # should be a regular criterion, should initialise intersections to check this
            if self.solveMode:
                if self.isEmpty(location):
                    if len(self.getSolvingCandidates(location)) == 0:
                        return False

            if not self.isEmpty(location):
                if self.values[location] not in self.setOfPossibleValues:
                    return False

        return True

    def isComplete(self):
        from operator import add
        numberOfLocations = self.getGridSize() ** 2
        # could use len(self.getEmptyLocations) OR sum(list comprehension, 1 for location)
        numberOfFilledLocations = reduce(add, [1 for location in self.getLocations() if not self.isEmpty(location)], 0)
        if numberOfFilledLocations == numberOfLocations:
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

        pointers = []

        for subGrid in self.intersectionTypes["subGrid"]:
            for combination in self.getNLocations(subGrid, n):

                if "row" in self.getAlignment(*combination):
                    pointers.append((combination, "row"))
                elif "column" in self.getAlignment(*combination):
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

            for firstRowGroup in self.getNLocations(firstRow, 2):

                    for secondRow in self.intersectionTypes["row"][firstRowIndex + 1:]:
                        if len(secondRow) < 2:
                            continue

                        for secondRowGroup in self.getNLocations(secondRow, 2):
                                if "subGrid" in self.getAlignment(firstRowGroup[0], secondRowGroup[1]):
                                    continue

                                if "column" in self.getAlignment(firstRowGroup[0], secondRowGroup[0]) and \
                                   "column" in self.getAlignment(firstRowGroup[1], secondRowGroup[1]):
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

            for firstRowGroup in self.getNLocations(firstRow, 2):

                for secondRowIndex, secondRow in enumerate(self.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 2:
                        continue

                    for secondRowGroup in self.getNLocations(secondRow, 2):
                        alignments = 0

                        for locationOne in firstRowGroup:
                            for locationTwo in secondRowGroup:
                                if "column" in self.getAlignment(locationOne, locationTwo):
                                    alignments += 1
                                    locationsInSameColumn = (locationOne, locationTwo)

                        if alignments != 1:
                            continue

                        for thirdRow in self.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 2:
                                continue

                            for thirdRowGroup in self.getNLocations(thirdRow, 2):
                                alignments2 = 0

                                for locationOne in thirdRowGroup:
                                    for row in (firstRowGroup, secondRowGroup):
                                        for locationTwo in [location for location in row if location not in locationsInSameColumn]:
                                            if "column" in self.getAlignment(locationOne, locationTwo):
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

            for firstRowGroup in self.getNLocations(firstRow, 3):

                for secondRowIndex, secondRow in enumerate(self.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 3:
                        continue

                    for secondRowGroup in self.getNLocations(secondRow, 3):
                        alignments = 0

                        for i in xrange(3):
                            if "column" in self.getAlignment(firstRowGroup[i], secondRowGroup[i]):
                                    alignments += 1

                        if alignments != 3:
                            continue

                        for thirdRow in self.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 3:
                                continue

                            for thirdRowGroup in self.getNLocations(thirdRow, 3):
                                alignments2 = 0

                                for i in xrange(3):
                                    if "column" in self.getAlignment(firstRowGroup[i], thirdRowGroup[i]):
                                        alignments2 += 1

                                if alignments2 == 3:
                                    swordfishGroups.append(firstRowGroup + secondRowGroup + thirdRowGroup)

        return swordfishGroups

    def generateConjugatePairs(self):
        self.initialiseIntersections()

        conjugatePairs = []

        for location in self.getEmptyLocations():

            locationCandidates = self.getSolvingCandidates(location)

            for candidate in locationCandidates:

                for method in self.neighbourMethods.itervalues():

                    candidateCount = 1
                    prospectiveLocation = None

                    for neighbour in method(location):
                        neighbourCandidates = self.getSolvingCandidates(neighbour)

                        if candidate in neighbourCandidates:
                            candidateCount += 1
                            prospectiveLocation = neighbour

                    if candidateCount != 2:
                        continue

                    group = (sorted((location, prospectiveLocation)), candidate)

                    if group not in conjugatePairs:
                        conjugatePairs.append(group)

        return conjugatePairs

    def generateChains(self):
        self.initialiseIntersections("conjugatePairs")

        chains = []

        for initialPairGroup in self.intersectionTypes["conjugatePairs"]:

            candidate = initialPairGroup[1]

            reversedInitialPairGroup = ([initialPairGroup[0][1], initialPairGroup[0][0]], candidate)

            for pairGroup in (initialPairGroup, reversedInitialPairGroup):

                chain = self.chainBuilder(pairGroup)

                if len(chain) > 2:
                    chains.append((chain, candidate))

        return chains

    def chainBuilder(self, initialPairGroup):
        pair, candidate = initialPairGroup[0], initialPairGroup[1]
        chain = pair[:]

        lastChain = None
        while lastChain != chain:

            lastLink = chain[-1]
            lastChain = chain[:]

            for prospectivePairGroup in self.intersectionTypes["conjugatePairs"]:

                prospectivePair = prospectivePairGroup[0]
                prospectiveCandidate = prospectivePairGroup[1]

                if prospectiveCandidate != candidate:
                    continue

                if all(location in chain for location in prospectivePair):
                    continue

                if any(location == lastLink for location in prospectivePair):
                    if prospectivePair[0] in chain:
                        chain.append(prospectivePair[1])
                        break
                    else:
                        chain.append(prospectivePair[0])
                        break

        return chain




    def getSubGrid(self, location):
        subGridRow = (location - 1) / (self.subGridsX * self.gridSize)
        subGridRowOffset = subGridRow * self.subGridsX

        subGridColumn = (self.getColumn(location) - 1) / self.subGridsY + 1

        return subGridRowOffset + subGridColumn

    def getRow(self, location):
        return (location - 1) / self.gridSize + 1

    def getColumn(self, location):
        return (location - 1) % self.gridSize + 1

    def getAlignment(self, *locations):
        locationMethods = (self.getRow, self.getColumn, self.getSubGrid)
        intersectionTypes = ("row", "column", "subGrid")
        intersection = []

        for methodNumber, method in enumerate(locationMethods):
            if all(method(locations[0]) == method(location) for location in locations):
                intersection.append(intersectionTypes[methodNumber])

        return intersection




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

    def getBaseNeighbours(self, location, *exclusions):
        return set(self.getSubGridNeighbours(location, *exclusions) +
                   self.getRowNeighbours(location, *exclusions) +
                   self.getColumnNeighbours(location, *exclusions))




    def getAllSubGridNeighbours(self, location, *exclusions):
        subGridGroup = self.staticGroups["subGrid"][self.getSubGrid(location) - 1]
        neighbours = [neighbour for neighbour in subGridGroup if neighbour != location]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def getAllRowNeighbours(self, location, *exclusions):
        rowGroup = self.staticGroups["row"][self.getRow(location) - 1]
        neighbours = [neighbour for neighbour in rowGroup if neighbour != location]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def getAllColumnNeighbours(self, location, *exclusions):
        columnGroup = self.staticGroups["column"][self.getColumn(location) - 1]
        neighbours = [neighbour for neighbour in columnGroup if neighbour != location]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def getAllBaseNeighbours(self, location, *exclusions):
        return set(self.getAllSubGridNeighbours(location, *exclusions) +
                   self.getAllRowNeighbours(location, *exclusions) +
                   self.getAllColumnNeighbours(location, *exclusions))




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

    def getEmptyLocations(self):
        return self.candidates.keys()

    def getNLocations(self, unit, n):
        from itertools import combinations

        return combinations(unit, n)

    def setValue(self, location, value):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(value):
            raise Exception("value is not vaild")

        self.values[location] = value

        if location in self.userCandidates:
            del self.userCandidates[location]

    def getValue(self, location):
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

        if not self.isValidInput(candidate):
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
                   self.xWing, self.swordfish,
                   self.simpleColouring]

        if self.isComplete():
            return [(entry[0], entry[2]) for entry in history if history is not None]

        if maxLevel > len(methods) or maxLevel < 1:
            maxLevel = len(methods)

        #if solver is run for the first time, solve using first method
        if history == None:
            log = methods[0]()[1]
            history = [(0, self.changes, log)]
            return self.solve(maxLevel, history)

        #if last attempt was successful, go back to first level
        lastMethod = history[-1][0]
        lastMethodSuccess = history[-1][1]
        if lastMethodSuccess:
            nextMethod = 0
        #or if unsuccessful, increase level or exit if highest level was tried
        else:
            moreMethods = (maxLevel - lastMethod) - 1
            if moreMethods:
                nextMethod = lastMethod + 1
            else:
                return [(entry[0], entry[2]) for entry in history if history is not None]

        log = methods[nextMethod]()[1]
        history.append((nextMethod, self.changes, log))

        return self.solve(maxLevel, history)




    def initialiseIntersections(self, *requiredIntersections):
        self.solveMode = True
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

        if "xWing" in requiredIntersections:
            if "xWing" not in self.intersectionTypes:
                self.intersectionTypes["xWing"] = self.generateXWingGroups()

        if "swordfish" in requiredIntersections:
            if "swordfish" not in self.intersectionTypes:
                self.intersectionTypes["swordfish"] = self.generateSwordfishGroups()

        if "conjugatePairs" in requiredIntersections:
            if "conjugatePairs" not in self.intersectionTypes:
                self.intersectionTypes["conjugatePairs"] = self.generateConjugatePairs()

        if "chains" in requiredIntersections:
            if "chains" not in self.intersectionTypes:
                self.intersectionTypes["chains"] = self.generateChains()

        for intersectionType in requiredIntersections:
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

            setOfSurroundingValues = set([self.values[neighbour] for neighbour in self.getBaseNeighbours(location) if not self.isEmpty(neighbour)])

            self.candidates[location] = self.setOfPossibleValues - setOfSurroundingValues




    def updatePuzzle(self):

        self.updateBaseGroupCandidates()
        self.updatePointerGroups()
        self.updateXWingGroups()
        self.updateSwordfishGroups()
        self.updateConjugatePairs()
        self.updateChains()

    def updateBaseGroupCandidates(self):
        for intersectionType in ["subGrid", "row", "column"]:

            for group in self.intersectionTypes[intersectionType]:

                setOfSurroundingValues = set([self.values[location] for location in group])

                for location in group[:]:
                    if self.isEmpty(location):
                        self.candidates[location] -= setOfSurroundingValues
                    else:
                        group.remove(location)

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

    def updateConjugatePairs(self):
        if "conjugatePairs" not in self.intersectionTypes:
            return

        for group in self.intersectionTypes["conjugatePairs"]:
            pair = group[0]
            for location in pair:
                if self.isEmpty(location):
                    continue
                if group in self.intersectionTypes["conjugatePairs"]:
                    self.intersectionTypes["conjugatePairs"].remove(group)
                    break

    def updateChains(self):
        if "chains" not in self.intersectionTypes:
            return

        for chainGroup in self.intersectionTypes["chains"]:
            if not self.validChain(chainGroup):
                if chainGroup in self.intersectionTypes["conjugatePairs"]:
                    self.intersectionTypes["conjugatePairs"].remove(chainGroup)

    def validChain(self, chainGroup):
        chain, candidate = chainGroup[0], chainGroup[1]
        if (chain, candidate) not in self.intersectionTypes["chains"]:
            return False

        for location in chain:
            if not self.isEmpty(location):
                return False
            if len(self.getSolvingCandidates(location)) <= 1:
                return False
            if candidate not in self.candidates[location]:
                return False
        return True




    def nakedSingle(self):
        self.initialiseIntersections()

        self.changes = False

        log = []
        successString = "Naked Single: %s was set to %s"

        for location, candidates in self.candidates.items():
            if len(candidates) == 1:
                candidate = candidates.pop()
                
                self.values[location] = candidate
                del self.candidates[location]
                self.changes = True
                
                log.append(successString % (str(location), str(candidate)))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def nakedN(self, n):
        self.initialiseIntersections()

        self.changes = False

        log = []
        name = "Naked " + self.multiples[n - 1]
        successString = "Naked %s: %s removes %s from %s"
        successString = name + ": %s have been removed from %s as it shares a %s with the " + name + ", %s"

        for intersectionType in ["subGrid", "row", "column"]:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in self.getNLocations(group, n):

                    nakedNcandidates = self.getSolvingCandidates(*combination)

                    if len(nakedNcandidates) != n:
                        continue

                    surroundingLocations = [location for location in group if location not in combination]

                    for surroundingLocation in surroundingLocations:

                        if any(candidate in nakedNcandidates for candidate in self.candidates[surroundingLocation]):

                            removedCandidates = [candidate for candidate in self.candidates[surroundingLocation] if candidate in nakedNcandidates]
                            
                            self.candidates[surroundingLocation] -= nakedNcandidates
                            self.changes = True

                            log.append(successString % (str(removedCandidates)[1:-1], location, self.getAlignment(*combination)[0], combination))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def nakedTwin(self):

        return self.nakedN(2)

    def nakedTriplet(self):

        return self.nakedN(3)




    def hiddenN(self, n):
        self.initialiseIntersections()

        self.changes = False

        log = []
        name = "Hidden " + self.multiples[n - 1]
        if n > 1:
            successString = name + ": %s has been removed from %s as the remaining candidates only appear in it's %s"
        else:
            successString = name + ": %s has been set to %s, as all other candidates have been removed"

        for intersectionType in ["subGrid", "row", "column"]:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in self.getNLocations(group, n):

                    surroundingLocations = [location for location in group if location not in combination]

                    combinationCandidates = self.getSolvingCandidates(*combination)
                    surroundingCandidates = self.getSolvingCandidates(*surroundingLocations)
                    uniqueCombinationCandidates = combinationCandidates - surroundingCandidates

                    if len(uniqueCombinationCandidates) != n:
                        continue

                    for location in combination:
                        if any(candidate in surroundingCandidates for candidate in self.candidates[location]):

                            removedCandidates = [candidate for candidate in self.candidates[location] if candidate in surroundingCandidates]

                            self.candidates[location] -= surroundingCandidates
                            
                            if n == 1:
                                self.setValue(location, uniqueCombinationCandidates.pop())

                            self.changes = True

                            if n > 1:
                                log.append(successString % (removedCandidates, location, intersectionType))
                            else:
                                log.append(successString % (location, self.getValue(location)))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def hiddenSingle(self):

        return self.hiddenN(1)

    def hiddenTwin(self):

        return self.hiddenN(2)

    def hiddenTriplet(self):

        return self.hiddenN(3)




    def pointingN(self, n):
        self.initialiseIntersections(("pointer", n))

        self.changes = False

        log = []
        name = "Pointing " + self.multiples[n - 1]
        successString = name + ": %s has been removed from %s, as it shares a %s with the " + name + " %s"

        for pointerGroup in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = pointerGroup[0], pointerGroup[1]
            
            subGridNeighbours = self.getSubGridNeighbours(combination[0], *combination)
            subGridNeighbourCandidates = self.getSolvingCandidates(*subGridNeighbours)
            
            commonPointerCandidates = self.getCommonCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in subGridNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            linearNeighbours = self.neighbourMethods[pointerType](combination[0], *combination)

            for location in linearNeighbours:
                locationCandidates = self.getSolvingCandidates(location)
                if any(candidate in locationCandidates for candidate in uniquePointerCandidates):

                    removedCandidates = [candidate for candidate in locationCandidates if candidate in uniquePointerCandidates]

                    self.candidates[location] -= uniquePointerCandidates
                    self.changes = True

                    log.append(successString % (str(removedCandidates)[1:-1], str(location), pointerType, combination))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def pointingPair(self):
        return self.pointingN(2)

    def pointingTriplet(self):
        return self.pointingN(3)




    def boxLineReductionN(self, n):
        self.initialiseIntersections(("pointer", n))

        self.changes = False

        log = []
        name = "Box Line Reduction (" + self.multiples[n - 1] + ")"
        successString = name + ": %s has been removed from %s, as it is part of a subGrid where %s can only be placed along it's %s"

        for pointerGroup in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = pointerGroup[0], pointerGroup[1]
            
            linearNeighbours = self.neighbourMethods[pointerType](combination[0], *combination)
            linearNeighbourCandidates = self.getSolvingCandidates(*linearNeighbours)

            commonPointerCandidates = self.getCommonCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in linearNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            subGridNeighbours = self.getSubGridNeighbours(combination[0], *combination)

            for location in subGridNeighbours:
                locationCandidates = self.getSolvingCandidates(location)
                if any(candidate in locationCandidates for candidate in uniquePointerCandidates):

                    removedCandidates = [candidate for candidate in locationCandidates if candidate in uniquePointerCandidates][0]

                    self.candidates[location] -= uniquePointerCandidates
                    self.changes = True

                    log.append(successString % (removedCandidates, location, removedCandidates, pointerType))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def boxLineReduction2(self):
        return self.boxLineReductionN(2)

    def boxLineReduction3(self):
        return self.boxLineReductionN(3)




    def xWing(self):
        self.initialiseIntersections("xWing")

        self.changes = False

        log = []
        successString = "X-Wing: %s has been removed from %s, as it is in alignment with the X-Wing, %s"

        from collections import defaultdict
        from itertools import chain

        xWings = defaultdict(list)

        for group in self.intersectionTypes["xWing"]:

            commonXWingCandidates = self.getCommonCandidates(*group)

            if len(commonXWingCandidates) == 0:
                continue

            rowCandidates = (self.getSolvingCandidates(*self.getRowNeighbours(group[0], *group)) |
                             self.getSolvingCandidates(*self.getRowNeighbours(group[2], *group)))
            columnCandidates = (self.getSolvingCandidates(*self.getColumnNeighbours(group[0], *group)) |
                                self.getSolvingCandidates(*self.getColumnNeighbours(group[1], *group)))

            for candidate in commonXWingCandidates:
                if (candidate not in rowCandidates or candidate not in columnCandidates):
                    xWings[group].append(candidate)

        for group, candidates in xWings.iteritems():

            xWingNeighbours = (self.getRowNeighbours(group[0], *group) +
                               self.getRowNeighbours(group[2], *group) +
                               self.getColumnNeighbours(group[0], *group) +
                               self.getColumnNeighbours(group[1], *group))

            for location in xWingNeighbours:
                locationCandidates = self.getSolvingCandidates(location)
                if any(candidate in locationCandidates for candidate in candidates):

                    removedCandidates = [candidate for candidate in locationCandidates if candidate in candidates]

                    self.candidates[location] -= set(removedCandidates)
                    self.changes = True

                    # Needs to be more verbose, showing where the alignment occours
                    log.append(successString % (removedCandidates, location, group))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log




    def swordfish(self):
        self.initialiseIntersections("swordfish")

        self.changes = False

        log = []
        successString = "Swordfish: %s has been removed from %s, as it is in alignment with the Swordfish, %s"

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

                for location in locations:
                    swordfishNeighbours += self.neighbourMethods[swordfishType](location, *group)

                for location in swordfishNeighbours:
                    locationCandidates = self.getSolvingCandidates(location)
                    if candidate in locationCandidates:

                        self.candidates[location].remove(candidate)
                        self.changes = True

                        log.append(successString % (candidate, location, group))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def simpleColouring(self):

        self.initialiseIntersections("chains")

        self.changes = False

        log = []

        for chainGroup in self.intersectionTypes["chains"]:
            chain, candidate = chainGroup[0], chainGroup[1]
            colourOne, colourTwo = chain[::2], chain[1::2]

            logStrings = ("Simple Colouring - Chain ON OFF: ",
                          "Simple Colouring - Case 2: "
                          "Simple Colouring - Case 4: "
                          "Simple Colouring - Case 5: ")

            simpleColouringMethods = (self.chainOnOff,
                                      self.simpleColourCase2,
                                      self.simpleColourCase4,
                                      self.simpleColourCase5)

            for index, method in enumerate(simpleColouringMethods):
                result = method(chain, colourOne, colourTwo, candidate)
                if result:
                    log.append(logStrings[index] + str(result))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def chainOnOff(self, chain, colourOne, colourTwo, candidate):
        """Tests to see if one colour being ON is valid, if it is invalid
           the other colour must be the solution."""

        successString = "%s has been removed from locations %s, as it is part of an invalid colour"

        for testColour in (colourOne, colourTwo):
            if not self.validChain((chain, candidate)):
                break

            candidatesToRemove = {location: candidate for location in testColour}

            # We are looking for a contradiction, so if the prospective change
            # checks out we haven't learnt anything new.
            if self.prospectiveChange(candidatesToRemove):
                continue
            
            for correctColour in (colourOne, colourTwo):
                if testColour != correctColour:
                    candidatesToRemove = {location: candidate for location in correctColour}
                    self.applyProspectiveChange(candidatesToRemove)
                    self.changes = True
                    return successString % (candidate, [location for location in correctColour])

    def simpleColourCase2(self, chain, colourOne, colourTwo, candidate):
        """If two locations are in the same colour and unit, this colour must
           be OFF, and the other colour must be ON."""

        successString = "locations %s have been set to %s, as it shares a unit with a chain where two colours are the same"

        for colour in (colourOne, colourTwo):
            if not self.validChain((chain, candidate)):
                break

            for pair in self.getNLocations(colour, 2):

                if not self.getAlignment(*pair):
                    continue

                if colour == colourOne:
                    correctColour = colourTwo
                else:
                    correctColour = colourOne

                valuesToAdd = {location: candidate for location in correctColour}
                self.applyProspectiveChange(None, valuesToAdd)
                self.changes = True
                return successString % ([location for location in correctColour], candidate)

    def simpleColourCase4(self, chain, colourOne, colourTwo, candidate):
        """If two locations are in the same unit and have different colours,
           all other locations in the unit must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        log = []

        successString = "%s has been removed from %s, as these locations are in the same unit as one of two locations that must be ON"

        for pair in self.getNLocations(chain, 2):
            if not self.validChain((chain, candidate)):
                break

            for alignment in self.getAlignment(*pair):
                if ((pair[0] in colourOne and pair[1] in colourTwo) or
                    (pair[1] in colourOne and pair[0] in colourTwo)):
                    for location in self.neighbourMethods[alignment](pair[0], *pair):
                        if candidate in self.candidates[location]:
                            self.candidates[location] -= set([candidate])
                            self.changes = True
                            log.append(successString % (candidate, location))

        return log

    def simpleColourCase5(self, chain, colourOne, colourTwo, candidate):
        """If a location can see two locations in a chain that have different
           colours, this location must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        successString = """%s has been removed from %s, as this location can "see" both %s, locations of different colours"""

        log = []

        for location in self.getEmptyLocations():
            if location in chain:
                continue

            if candidate not in self.getSolvingCandidates(location):
                continue

            for pair in self.getNLocations(chain, 2):
                if not self.validChain((chain, candidate)):
                    break

                if not (((pair[0] in colourOne and pair[1] in colourTwo) or
                        (pair[1] in colourOne and pair[0] in colourTwo))):
                    continue

                alignsWithFirstElement = self.getAlignment(pair[0], location)
                alignsWithSecondElement = self.getAlignment(pair[1], location)
                if alignsWithFirstElement and alignsWithSecondElement:
                    self.candidates[location] -= set([candidate])
                    self.changes = True
                    log.append(successString % candidate, location, pair)

        return log




    def prospectiveChange(self, candidatesToRemove=None, valuesToAdd=None):
        from copy import deepcopy

        prospectivePuzzle = deepcopy(self)

        if candidatesToRemove is not None:
            for location, candidates in candidatesToRemove.iteritems():
                prospectivePuzzle.candidates[location] -= set([candidates])

        if valuesToAdd is not None:
            for location, value in valuesToAdd.iteritems():
                del prospectivePuzzle.candidates[location]
                prospectivePuzzle.values[location] = value

        prospectivePuzzle.updatePuzzle()
        prospectivePuzzle.solve(4)

        return prospectivePuzzle.isValid()

    def applyProspectiveChange(self, candidatesToRemove=None, valuesToAdd=None):
        if candidatesToRemove is not None:
            for location, candidates in candidatesToRemove.iteritems():
                self.candidates[location] -= set([candidates])

        if valuesToAdd is not None:
            for location, value in valuesToAdd.iteritems():
                del self.candidates[location]
                self.values[location] = value

        self.updatePuzzle()
