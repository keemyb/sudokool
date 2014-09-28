

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

    def __init__(self, data, horizontalFormat=True):
        self.horizontalFormat = horizontalFormat
        self.calculateDimensions(data, horizontalFormat)
        self.generatePossibleValues()
        self.processData(data)

        self.candidates = {}
        self.userCandidatesDict = {}
        self.log = []

        self.solveMode = False
        self.changes = False
        self.hasCandidates = False
        self.hasIntersections = False

        self.multiples = ("Single", "Pair", "Triplet", "Quadruplet")
        self.units = ("row", "column", "subGrid")

        self.intersectionTypes = {}

        self.staticGroups = {
            "row": self.generateRowGroups(),
            "column": self.generateColumnGroups(),
            "subGrid": self.generateSubGridGroups(),
            }

        self.generationMethods = {
            "row": self.generateRowGroups,
            "column": self.generateColumnGroups,
            "subGrid": self.generateSubGridGroups,
            "xWing": self.generateXWingGroups,
            "swordfish": self.generateSwordfishGroups,
            "conjugatePairs": self.generateConjugatePairs,
            "conjugateChains": self.generateConjugateChains,
            "yWing": self.generateYWingGroups,
            "xyzWing": self.generateXYZWingGroups,
            "lockedPairs": self.generateLockedPairs,
            "lockedChains": self.generateLockedChains,
            }

        self.neighbourMethods = {
            "row": self.rowNeighbours,
            "column": self.columnNeighbours,
            "subGrid": self.subGridNeighbours,
            }

        self.allNeighbourMethods = {
            "row": self.allRowNeighbours,
            "column": self.allColumnNeighbours,
            "subGrid": self.allSubGridNeighbours,
            }

        self.alignmentMethods = {
            "row": self.getRow,
            "column": self.getColumn,
            "subGrid": self.getSubGrid,
            }

        self.solvingMethods = [
            self.nakedSingle, self.hiddenSingle,
            self.nakedTwin, self.hiddenTwin,
            self.pointingPair, self.pointingTriplet,
            self.boxLineReduction2, self.boxLineReduction3,
            self.nakedTriplet, self.hiddenTriplet,
            self.xWing, self.swordfish,
            self.yWing,
            self.simpleColouring,
            self.xyzWing,
            self.remotePairs,
            ]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.values == self.values
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        pass

    def __str__(self):
        string = ""
        vPipe = "="
        hPipe = "="
        # first line to accommodate vertical pipe and following spaces (minus one to account for last v pipe)
        # second line for numbers (and following spaces)
        horizontalDivider = (hPipe * ((len(vPipe) + 1) * (self.subGridsX + 1) - 1) +
                       hPipe * (self.gridSize * 2) +
                       "\n")

        def isFirstLocationOnLine(location):
            if (location - 1) % (self.gridSize * self.subGridsX) == 0:
                return True
            return False

        def isFirstLocationInRowInSubGrid(location):
            if (location - 1) % self.subGridsY == 0:
                return True
            return False

        def isLastLocationInRow(location):
            if location % self.gridSize == 0:
                return True
            return False

        def isLastLocation(location):
            if location == self.gridSize ** 2:
                return True
            return False

        for location in self.locations():

            if isFirstLocationOnLine(location):
                string += horizontalDivider

            if isFirstLocationInRowInSubGrid(location):
                string += vPipe + " "

            if self.isEmpty(location):
                string += "  "
            else:
                string += str(self.getValue(location)) + " "

            if isLastLocationInRow(location):
                string += vPipe + "\n"

            if isLastLocation(location):
                string += horizontalDivider

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
            alphabeticalValues = set([chr(num + 55) for num in xrange(10, self.gridSize + 1)])
            self.setOfPossibleValues.update(alphabeticalValues)

    def processData(self, data):
        self.values = {position + 1 : data[position] for position in xrange(self.gridSize ** 2)}
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

            if self.isEmpty(location):
                if len(self.solvingCandidates(location)) == 0:
                    return False

            if not self.isEmpty(location):
                if self.values[location] not in self.setOfPossibleValues:
                    return False

        return True

    def isComplete(self):
        numberOfLocations = len(self.locations())
        numberOfFilledLocations = len(self.filledLocations())
        if numberOfFilledLocations == numberOfLocations:
            return True
        return False

    def solve(self, maxLevel, history=None):

        if self.isComplete():
            return [(entry[0], entry[2]) for entry in history if history is not None]

        if maxLevel > len(self.solvingMethods) or maxLevel < 1:
            maxLevel = len(self.solvingMethods)

        #if solver is run for the first time, solve using first method
        if history is None:
            log = self.solvingMethods[0]()[1]
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

        log = self.solvingMethods[nextMethod]()[1]
        history.append((nextMethod, self.changes, log))

        return self.solve(maxLevel, history)




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




    def initialiseIntersections(self, *requiredIntersections):
        self.solveMode = True
        #three main intersection types needed for candidates to work
        for intersectionType in self.units:
            if intersectionType in self.intersectionTypes:
                continue

            self.intersectionTypes[intersectionType] = self.generationMethods[intersectionType]()

        self.hasIntersections = True

        if not self.hasCandidates:
            self.initialiseCandidates()

        for intersectionType in requiredIntersections:
            if intersectionType in self.intersectionTypes:
                continue

            if intersectionType not in self.generationMethods:
                continue

            self.intersectionTypes[intersectionType] = self.generationMethods[intersectionType]()

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

        if not self.hasIntersections:
            self.initialiseIntersections()

        for location in xrange(1, self.gridSize ** 2 + 1):

            if not self.isEmpty(location):
                continue

            neighbours = [neighbour for neighbour in self.allCombinedNeighbours(location) if not self.isEmpty(neighbour)]

            surroundingValues = self.getValues(*neighbours)

            self.candidates[location] = self.setOfPossibleValues - surroundingValues

        self.hasCandidates = True


    def initialiseUserCandidates(self):

        if not self.hasIntersections:
            self.initialiseIntersections()

        for location in self.emptyLocations():

            neighbours = self.allCombinedNeighbours(location)

            surroundingValues = self.getValues(*neighbours)

            self.userCandidatesDict[location] = self.setOfPossibleValues - surroundingValues

    def updateUserCandidates(self):

        for location in self.userCandidatesDict.iterkeys():

            neighbours = self.allCombinedNeighbours(location)

            surroundingValues = self.getValues(*neighbours)

            self.userCandidatesDict[location] -= surroundingValues




    def logVariableFormatter(self, *variables):

        seperator = ", "

        formattedVariables = []

        for variable in variables:
            if hasattr(variable, "__iter__"):
                for value in variable:
                    try:
                        float(value)
                    except:
                        formattedVariables.append(variable)
                        break
                else:
                    variable = [str(value) for value in variable]
                    newVariable = str(seperator).join(variable)
                    formattedVariables.append(newVariable)
            else:
                formattedVariables.append(variable)

        return formattedVariables

    def addToLog(self, string, *variables):

        formattedVariables = self.logVariableFormatter(*variables)

        self.log.append(string.format(*formattedVariables))




    def getSubGridStartLocations(self):
        subGridStartLocations = []

        for subGrid in xrange(self.gridSize):
            baseLocation = (subGrid / self.subGridsX) * (self.gridSize * self.subGridsX)
            offset = (subGrid % self.subGridsX) * self.subGridsY
            subGridStartLocations.append(baseLocation + offset + 1)

        return subGridStartLocations

    def getRowStartLocations(self):
        rowStartLocations = [(row * self.gridSize + 1) for row in xrange(self.gridSize)]

        return rowStartLocations

    def getColumnStartLocations(self):
        columnStartLocations = range(1, self.gridSize + 1)

        return columnStartLocations

    def generateSubGridGroups(self):
        subGridGroups = []
        offsets = []

        for position in xrange(self.gridSize):
            rowOffset = (position / self.subGridsY) * self.gridSize
            columnOffset = (position % self.gridSize) % self.subGridsY

            offsets.append(rowOffset + columnOffset)

        for startLocation in self.getSubGridStartLocations():
            subGridGroup = [startLocation + offset for offset in offsets]
            subGridGroups.append(subGridGroup)

        return subGridGroups

    def generateRowGroups(self):
        rowGroups = []

        for startLocation in self.getRowStartLocations():
            rowGroups.append([startLocation + offset for offset in xrange(self.gridSize)])

        return rowGroups

    def generateColumnGroups(self):
        columnGroups = []

        for startLocation in self.getColumnStartLocations():
            columnGroups.append([startLocation + offset * self.gridSize for offset in xrange(self.gridSize)])

        return columnGroups





    def getSubGrid(self, location):
        subGridRow = (location - 1) / (self.subGridsX * self.gridSize)
        subGridRowOffset = subGridRow * self.subGridsX

        subGridColumn = (self.getColumn(location) - 1) / self.subGridsY + 1

        return subGridRowOffset + subGridColumn

    def getRow(self, location):
        return (location - 1) / self.gridSize + 1

    def getColumn(self, location):
        return (location - 1) % self.gridSize + 1

    def alignment(self, *locations):
        alignments = []

        for unit, method in self.alignmentMethods.iteritems():
            if all(method(locations[0]) == method(location) for location in locations):
                alignments.append(unit)

        return sorted(alignments)




    def subGridNeighbours(self, location, *exclusions):
        subGridGroup = self.intersectionTypes["subGrid"][self.getSubGrid(location) - 1]
        neighbours = [neighbour for neighbour in subGridGroup if neighbour != location and self.isEmpty(neighbour)]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def rowNeighbours(self, location, *exclusions):
        rowGroup = self.intersectionTypes["row"][self.getRow(location) - 1]
        neighbours = [neighbour for neighbour in rowGroup if neighbour != location and self.isEmpty(neighbour)]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def columnNeighbours(self, location, *exclusions):
        columnGroup = self.intersectionTypes["column"][self.getColumn(location) - 1]
        neighbours = [neighbour for neighbour in columnGroup if neighbour != location and self.isEmpty(neighbour)]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def combinedNeighbours(self, location, *exclusions):
        return set(self.subGridNeighbours(location, *exclusions) +
                   self.rowNeighbours(location, *exclusions) +
                   self.columnNeighbours(location, *exclusions))

    def allSubGridNeighbours(self, location, *exclusions):
        subGridGroup = self.staticGroups["subGrid"][self.getSubGrid(location) - 1]
        neighbours = [neighbour for neighbour in subGridGroup if neighbour != location]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def allRowNeighbours(self, location, *exclusions):
        rowGroup = self.staticGroups["row"][self.getRow(location) - 1]
        neighbours = [neighbour for neighbour in rowGroup if neighbour != location]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def allColumnNeighbours(self, location, *exclusions):
        columnGroup = self.staticGroups["column"][self.getColumn(location) - 1]
        neighbours = [neighbour for neighbour in columnGroup if neighbour != location]
        neighbours = [neighbour for neighbour in neighbours if neighbour not in exclusions]

        return neighbours

    def allCombinedNeighbours(self, location, *exclusions):
        return set(self.allSubGridNeighbours(location, *exclusions) +
                   self.allRowNeighbours(location, *exclusions) +
                   self.allColumnNeighbours(location, *exclusions))

    def xWingNeighbours(self, xWing):
        return (self.rowNeighbours(xWing[0], *xWing) +
                self.rowNeighbours(xWing[2], *xWing) +
                self.columnNeighbours(xWing[0], *xWing) +
                self.columnNeighbours(xWing[1], *xWing))

    def swordfishRowNeighbours(self, swordfish):

        rowNeighbours = set([]).union(*[self.rowNeighbours(location) for location in swordfish])

        rowNeighbours -= set(swordfish)

        return rowNeighbours

    def swordfishColumnNeighbours(self, swordfish):

        columnNeighbours = set([]).union(*[self.columnNeighbours(location) for location in swordfish])

        columnNeighbours -= set(swordfish)

        return columnNeighbours

    def swordfishNeighbours(self, swordfish):

        return self.swordfishRowNeighbours(swordfish).union(
            self.swordfishColumnNeighbours(swordfish))




    def generatePointerGroups(self, n):
        self.initialiseIntersections()

        pointers = []

        for subGrid in self.intersectionTypes["subGrid"]:
            for combination in self.nLocations(subGrid, n):

                if "row" in self.alignment(*combination):
                    pointers.append((combination, "row"))
                elif "column" in self.alignment(*combination):
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

            for firstRowGroup in self.nLocations(firstRow, 2):

                    for secondRow in self.intersectionTypes["row"][firstRowIndex + 1:]:
                        if len(secondRow) < 2:
                            continue

                        for secondRowGroup in self.nLocations(secondRow, 2):
                                if "subGrid" in self.alignment(firstRowGroup[0], secondRowGroup[1]):
                                    continue

                                if "column" in self.alignment(firstRowGroup[0], secondRowGroup[0]) and \
                                   "column" in self.alignment(firstRowGroup[1], secondRowGroup[1]):
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

            for firstRowGroup in self.nLocations(firstRow, 2):

                for secondRowIndex, secondRow in enumerate(self.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 2:
                        continue

                    for secondRowGroup in self.nLocations(secondRow, 2):
                        alignments = 0

                        for locationOne in firstRowGroup:
                            for locationTwo in secondRowGroup:
                                if "column" in self.alignment(locationOne, locationTwo):
                                    alignments += 1
                                    locationsInSameColumn = (locationOne, locationTwo)

                        if alignments != 1:
                            continue

                        for thirdRow in self.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 2:
                                continue

                            for thirdRowGroup in self.nLocations(thirdRow, 2):
                                alignments2 = 0

                                for locationOne in thirdRowGroup:
                                    for row in (firstRowGroup, secondRowGroup):
                                        for locationTwo in [location for location in row if location not in locationsInSameColumn]:
                                            if "column" in self.alignment(locationOne, locationTwo):
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

            for firstRowGroup in self.nLocations(firstRow, 3):

                for secondRowIndex, secondRow in enumerate(self.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 3:
                        continue

                    for secondRowGroup in self.nLocations(secondRow, 3):
                        alignments = 0

                        for i in xrange(3):
                            if "column" in self.alignment(firstRowGroup[i], secondRowGroup[i]):
                                    alignments += 1

                        if alignments != 3:
                            continue

                        for thirdRow in self.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 3:
                                continue

                            for thirdRowGroup in self.nLocations(thirdRow, 3):
                                alignments2 = 0

                                for i in xrange(3):
                                    if "column" in self.alignment(firstRowGroup[i], thirdRowGroup[i]):
                                        alignments2 += 1

                                if alignments2 == 3:
                                    swordfishGroups.append(firstRowGroup + secondRowGroup + thirdRowGroup)

        return swordfishGroups

    def generateConjugatePairs(self):
        self.initialiseIntersections()

        conjugatePairs = []

        for location in self.emptyLocations():

            locationCandidates = self.solvingCandidates(location)

            for candidate in locationCandidates:

                for method in self.neighbourMethods.itervalues():

                    candidateCount = 1
                    prospectiveLocation = None

                    for neighbour in method(location):
                        neighbourCandidates = self.solvingCandidates(neighbour)

                        if candidate in neighbourCandidates:
                            candidateCount += 1
                            prospectiveLocation = neighbour

                    if candidateCount != 2:
                        continue

                    group = (sorted((location, prospectiveLocation)), candidate)

                    if group not in conjugatePairs:
                        conjugatePairs.append(group)

        return conjugatePairs

    def generatePairChains(self, pairType):
        self.initialiseIntersections(pairType)

        chains = []

        for pairGroup in self.intersectionTypes[pairType]:

            pair, candidates = pairGroup[0], pairGroup[1]
            chain = pair[:]

            lastChain = None
            while lastChain != chain:

                firstLink, lastLink = chain[0], chain[-1]
                lastChain = chain[:]

                for prospectivePairGroup in self.intersectionTypes[pairType]:

                    prospectivePair = prospectivePairGroup[0]
                    prospectiveCandidates = prospectivePairGroup[1]

                    if prospectiveCandidates != candidates:
                        continue

                    if all(location in chain for location in prospectivePair):
                        continue

                    if any(location == firstLink for location in prospectivePair):
                        if prospectivePair[0] in chain:
                            chain.insert(0, prospectivePair[1])
                            break
                        else:
                            chain.insert(0, prospectivePair[0])
                            break

                    if any(location == lastLink for location in prospectivePair):
                        if prospectivePair[0] in chain:
                            chain.append(prospectivePair[1])
                            break
                        else:
                            chain.append(prospectivePair[0])
                            break

            if len(chain) < 3:
                continue

            chainIsASubset = False
            for existingChainGroup in chains[:]:
                existingChain = existingChainGroup[0]
                existingChainCandidates = existingChainGroup[1]

                if existingChainCandidates != candidates:
                    continue

                # if all locations in the current chain already exist in another,
                # it is a subset and will not be added. We break here as the
                # larger chain does not need to be purged.
                if all(location in existingChain for location in chain):
                    chainIsASubset = True
                    break

                # if all locations in the existing chain exist in the current chain,
                # the existing chain will be removed.
                if all(location in chain for location in existingChain):
                    if existingChainGroup in chains:
                        chains.remove(existingChainGroup)

            if not chainIsASubset:
                chains.append((chain, candidates))

        return chains

    def generateConjugateChains(self):

        return self.generatePairChains("conjugatePairs")



    def generateYWingGroups(self):
        yWings = []

        for firstPair in self.nLocations(self.emptyLocations(), 2):
            yWingResult = self.yWingPairValid(firstPair)
            if not yWingResult:
                continue

            firstAlignment = yWingResult[0]
            firstCommonCandidates = yWingResult[1]

            for secondPair in self.nLocations(self.emptyLocations(), 2):
                if secondPair == firstPair:
                    continue

                if not any(location in firstPair for location in secondPair):
                    continue

                yWingResult = self.yWingPairValid(secondPair)
                if not yWingResult:
                    continue

                secondAlignment = yWingResult[0]
                secondCommonCandidates = yWingResult[1]

                if secondAlignment == firstAlignment:
                    continue

                if secondCommonCandidates == firstCommonCandidates:
                    continue

                pivot = set(firstPair) & set(secondPair)

                yWingLocations = [(set(firstPair) - pivot).pop(),
                         (set(secondPair) - pivot).pop()]
                yWingLocations.insert(0, pivot.pop())

                yWingCandidate = self.commonCandidates(*yWingLocations[1:])

                if not yWingCandidate:
                    continue

                yWing = ([yWingLocations[0]] + sorted(yWingLocations[1:]),
                         yWingCandidate.pop())

                if yWing in yWings:
                    continue

                yWings.append(yWing)

        return yWings

    def yWingPairValid(self, pair):
        alignment = self.alignment(*pair)
        if not alignment:
            return False

        commonCandidates = self.commonCandidates(*pair)
        if not commonCandidates:
            return False

        firstLocationCandidates = self.solvingCandidates(pair[0])
        secondLocationCandidates = self.solvingCandidates(pair[1])

        if firstLocationCandidates == secondLocationCandidates:
            return False

        if len(firstLocationCandidates) != 2:
            return False

        if len(secondLocationCandidates) != 2:
            return False

        return alignment, commonCandidates, firstLocationCandidates, secondLocationCandidates

    def generateXYZWingGroups(self):
        xyzWings = []

        for firstPair in self.nLocations(self.emptyLocations(), 2):
            result = self.xyzWingPairValid(firstPair)
            if not result:
                continue

            pivot = result[0]
            firstArm = result[1]
            firstArmCandidates = result[2]

            for secondPair in self.nLocations(self.emptyLocations(), 2):
                if sorted(secondPair) == sorted(firstPair):
                    continue

                if pivot not in secondPair:
                    continue

                result = self.xyzWingPairValid(secondPair)
                if not result:
                    continue

                secondArm = result[1]
                secondArmCandidates = result[2]

                if self.alignment(pivot, firstArm, secondArm):
                    continue

                if secondArmCandidates == firstArmCandidates:
                    continue

                xyzWingCandidate = self.commonCandidates(firstArm, secondArm)

                arms = firstArm, secondArm

                xyzWing = ([pivot] + sorted(arms), xyzWingCandidate.pop())

                if xyzWing in xyzWings:
                    continue

                xyzWings.append(xyzWing)

        return xyzWings

    def xyzWingPairValid(self, pair):
        alignment = self.alignment(*pair)
        if not alignment:
            return False

        pivot, nonPivot = None, None

        for location in pair:
            candidates = self.solvingCandidates(location)
            if len(candidates) == 3:
                pivot = location
                pivotCandidates = candidates
            elif len(candidates) == 2:
                nonPivot = location
                nonPivotCandidates = candidates

        if any(location is None for location in (pivot, nonPivot)):
            return False

        if not pivotCandidates > nonPivotCandidates:
            return False

        return pivot, nonPivot, nonPivotCandidates

    def generateLockedPairs(self):
        lockedPairs = []

        for pair in self.nLocations(self.emptyLocations(), 2):
            alignment = self.alignment(*pair)
            if not alignment:
                continue

            locationOneCandidates = self.solvingCandidates(pair[0])
            if len(locationOneCandidates) != 2:
                continue

            locationTwoCandidates = self.solvingCandidates(pair[1])
            if locationTwoCandidates != locationOneCandidates:
                continue

            lockedPair = (sorted(pair), locationOneCandidates)

            if lockedPair in lockedPairs:
                continue

            lockedPairs.append(lockedPair)

        return lockedPairs

    def generateLockedChains(self):

        return self.generatePairChains("lockedPairs")




    def updatePuzzle(self):

        self.updateBaseGroupCandidates()
        self.updatePointerGroups()
        self.updateXWingGroups()
        self.updateSwordfishGroups()
        self.updateConjugatePairs()
        self.updateConjugateChains()
        self.updateYWingGroups()
        self.updateXYZWingGroups()
        self.updateLockedPairs()
        self.updateLockedChains()

    def updateBaseGroupCandidates(self):
        for intersectionType in self.units:

            for group in self.intersectionTypes[intersectionType]:

                surroundingValues = self.getValues(*group)

                for location in group[:]:
                    if self.isEmpty(location):
                        self.candidates[location] -= surroundingValues
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
            if all(self.isEmpty(location) for location in pair):
                continue
            if group in self.intersectionTypes["conjugatePairs"]:
                self.intersectionTypes["conjugatePairs"].remove(group)

    def updateConjugateChains(self):
        if "conjugateChains" not in self.intersectionTypes:
            return

        for chainGroup in self.intersectionTypes["conjugateChains"]:
            if self.validConjugateChain(chainGroup):
                continue
            if chainGroup in self.intersectionTypes["conjugateChains"]:
                self.intersectionTypes["conjugateChains"].remove(chainGroup)

    def validConjugateChain(self, chainGroup):
        chain, candidate = chainGroup[0], chainGroup[1]
        if (chain, candidate) not in self.intersectionTypes["conjugateChains"]:
            return False

        for location in chain:
            if not self.isEmpty(location):
                return False
            if len(self.solvingCandidates(location)) <= 1:
                return False
            if candidate not in self.candidates[location]:
                return False
        return True

    def updateYWingGroups(self):
        if "yWing" not in self.intersectionTypes:
            return

        for yWingGroup in self.intersectionTypes["yWing"]:
            yWingLocations = yWingGroup[0]
            for location in yWingLocations:
                if not self.isEmpty(location):
                    continue
                if len(self.solvingCandidates(location)) != 2:
                    continue
                if yWingGroup in self.intersectionTypes["yWing"]:
                    self.intersectionTypes["yWing"].remove(yWingGroup)
                    break

    def updateXYZWingGroups(self):
        if "xyzWing" not in self.intersectionTypes:
            return

        for xyzWingGroup in self.intersectionTypes["xyzWing"]:
            xyzWingLocations = xyzWingGroup[0]
            for location in xyzWingLocations:
                if not self.isEmpty(location):
                    continue
                numberOfCandidates = len(self.solvingCandidates(location))
                if numberOfCandidates not in (2,3):
                    continue
                if xyzWingGroup in self.intersectionTypes["xyzWing"]:
                    self.intersectionTypes["xyzWing"].remove(xyzWingGroup)
                    break

    def updateLockedPairs(self):
        if "lockedPairs" not in self.intersectionTypes:
            return

        for group in self.intersectionTypes["lockedPairs"]:
            pair = group[0]

            if all(self.isEmpty(location) for location in pair):
                continue
            if group in self.intersectionTypes["lockedPairs"]:
                self.intersectionTypes["lockedPairs"].remove(group)
                break

    def updateLockedChains(self):
        if "lockedChains" not in self.intersectionTypes:
            return

        for chainGroup in self.intersectionTypes["lockedChains"]:
            if not self.validLockedChain(chainGroup):
                if chainGroup in self.intersectionTypes["lockedChains"]:
                    self.intersectionTypes["lockedChains"].remove(chainGroup)

    def validLockedChain(self, chainGroup):
        if chainGroup not in self.intersectionTypes["lockedChains"]:
            return False

        chain, candidates = chainGroup[0], chainGroup[1]

        for location in chain:
            if not self.isEmpty(location):
                return False
            if candidates != self.solvingCandidates(location):
                return False
        return True




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

    def possibleValues(self):
        return sorted(self.setOfPossibleValues)

    def locations(self):
        return range(1, self.gridSize ** 2 + 1)

    def emptyLocations(self):
        if not self.hasCandidates:
            self.initialiseCandidates()

        return self.candidates.keys()

    def filledLocations(self):
        return [location for location in self.locations() if not self.isEmpty(location)]

    def nLocations(self, unit, n):
        from itertools import combinations

        return combinations(unit, n)

    def setValue(self, location, value):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(value):
            raise Exception("value is not vaild")

        self.values[location] = value

        if location in self.userCandidatesDict:
            del self.userCandidatesDict[location]

    def getValue(self, location):
        return self.values[location]

    def getValues(self, *locations):
        return set([self.values[location] for location in locations])

    def clearLocation(self, location):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        self.values[location] = 0

    def solvingCandidates(self, *locations):
        return set([]).union(*[self.candidates[location] for location in locations])

    def commonCandidates(self, *locations):
        return set.intersection(*[self.candidates[location] for location in locations])

    def userCandidates(self, location):
        return self.userCandidatesDict[location]

    def removeSolvingCandidates(self, location, *candidates):

        removedCandidates = []

        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.hasSolvingCandidates(location):
            return removedCandidates

        for candidate in candidates:

            if not self.isValidInput(candidate):
                raise Exception("candidate is not vaild")

            if candidate in self.solvingCandidates(location):
                self.candidates[location].remove(candidate)
                removedCandidates.append(candidate)

        if removedCandidates:
            self.changes = True

        return removedCandidates

    def toggleUserCandidate(self, location, candidate):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(candidate):
            raise Exception("candidate is not vaild")

        if not self.isEmpty(location):
            self.clearLocation(location)

        if not self.hasUserCandidates(location):
            self.userCandidatesDict[location] = set([candidate])
            return

        if candidate in self.userCandidatesDict[location]:
            self.userCandidatesDict[location].remove(candidate)
        else:
            self.userCandidatesDict[location].add(candidate)

    def hasSolvingCandidates(self, location):
        if location not in self.candidates:
            return False

        if not self.candidates[location]:
            return False

        return True

    def hasUserCandidates(self, location):
        if location not in self.userCandidatesDict:
            return False

        if not self.userCandidatesDict[location]:
            return False

        return True

    def unitSize(self):
        return self.gridSize

    def subGridsInRow(self):
        return self.subGridsX

    def subGridsInColumn(self):
        return self.subGridsY

    def subGridLength(self):
        return self.subGridsY

    def subGridHeight(self):
        return self.subGridsX




    def nakedSingle(self):
        self.initialiseIntersections()

        self.changes = False

        successString = "Naked Single: {0} was set to {1}"

        for location, candidates in self.candidates.items():
            if len(candidates) == 1:
                candidate = candidates.pop()

                self.values[location] = candidate
                del self.candidates[location]
                self.changes = True

                self.addToLog(successString, location, candidate)

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def nakedN(self, n):
        self.initialiseIntersections()

        self.changes = False

        name = "Naked " + self.multiples[n - 1]
        successString = "Naked %s: %s removes %s from %s"
        successString = name + ": %s have been removed from %s as it shares a %s with the " + name + ", %s"

        for intersectionType in self.units:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in self.nLocations(group, n):

                    nakedNcandidates = self.solvingCandidates(*combination)

                    if len(nakedNcandidates) != n:
                        continue

                    surroundingLocations = [location for location in group if location not in combination]

                    for surroundingLocation in surroundingLocations:

                        removedCandidates = self.removeSolvingCandidates(surroundingLocation, *nakedNcandidates)

                        if removedCandidates:

                            self.addToLog(successString, removedCandidates, location, self.alignment(*combination)[0], combination)

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

        name = "Hidden " + self.multiples[n - 1]
        if n > 1:
            successString = name + ": %s has been removed from %s as the " + name +", %s only appears in it's %s"
        else:
            successString = name + ": %s has been set to %s, as all other candidates have been removed"

        for intersectionType in self.units:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in self.nLocations(group, n):

                    surroundingLocations = [location for location in group if location not in combination]

                    combinationCandidates = self.solvingCandidates(*combination)
                    surroundingCandidates = self.solvingCandidates(*surroundingLocations)
                    uniqueCombinationCandidates = combinationCandidates - surroundingCandidates

                    if len(uniqueCombinationCandidates) != n:
                        continue

                    for location in combination:

                        removedCandidates = self.removeSolvingCandidates(location, *surroundingCandidates)

                        if not removedCandidates:
                            continue

                        if n == 1:
                            self.setValue(location, uniqueCombinationCandidates.pop())

                        if n > 1:
                            self.addToLog(successString, removedCandidates, location, self.solvingCandidates(location), intersectionType)
                        else:
                            self.addToLog(successString, location, self.getValue(location))

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

        log = []
        name = "Pointing " + self.multiples[n - 1]
        successString = name + ": %s has been removed from %s, as it shares a %s with the " + name + " %s"

        for pointerGroup in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = pointerGroup[0], pointerGroup[1]

            subGridNeighbours = self.subGridNeighbours(combination[0], *combination)
            subGridNeighbourCandidates = self.solvingCandidates(*subGridNeighbours)

            commonPointerCandidates = self.commonCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in subGridNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            linearNeighbours = self.neighbourMethods[pointerType](combination[0], *combination)

            for location in linearNeighbours:

                removedCandidates = self.removeSolvingCandidates(location, *uniquePointerCandidates)

                if removedCandidates:

                    log.append(successString % (removedCandidates, str(location), pointerType, combination))

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
            linearNeighbourCandidates = self.solvingCandidates(*linearNeighbours)

            commonPointerCandidates = self.commonCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in linearNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            subGridNeighbours = self.subGridNeighbours(combination[0], *combination)

            for location in subGridNeighbours:
                removedCandidates = self.removeSolvingCandidates(location, *uniquePointerCandidates)

                if removedCandidates:

                    log.append(successString % (removedCandidates, location, commonPointerCandidates, pointerType))

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

            commonXWingCandidates = self.commonCandidates(*group)

            if len(commonXWingCandidates) == 0:
                continue

            rowCandidates = (self.solvingCandidates(*self.rowNeighbours(group[0], *group)) |
                             self.solvingCandidates(*self.rowNeighbours(group[2], *group)))
            columnCandidates = (self.solvingCandidates(*self.columnNeighbours(group[0], *group)) |
                                self.solvingCandidates(*self.columnNeighbours(group[1], *group)))

            for candidate in commonXWingCandidates:
                if (candidate not in rowCandidates or candidate not in columnCandidates):
                    xWings[group].append(candidate)

        for group, candidates in xWings.iteritems():

            for location in self.xWingNeighbours(group):

                removedCandidates = self.removeSolvingCandidates(location, *candidates)

                if removedCandidates:

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

            commonCandidates = self.commonCandidates(*group)

            if len(commonCandidates) == 0:
                continue

            rowCandidates = defaultdict(set)
            for neighbour in self.swordfishRowNeighbours(group):
                rowCandidates[self.getRow(neighbour)].union(self.solvingCandidates(neighbour))

            columnCandidates = defaultdict(set)
            for neighbour in self.swordfishColumnNeighbours(group):
                columnCandidates[self.getColumn(neighbour)].union(self.solvingCandidates(neighbour))

            for candidate in commonCandidates:
                inAllRows = all(candidate in candidates for candidates in rowCandidates.itervalues())
                inAllColumns = all(candidate in candidates for candidates in columnCandidates.itervalues())
                notInRows = not any(candidate in candidates for candidates in rowCandidates.itervalues())
                notInColumns = not any(candidate in candidates for candidates in columnCandidates.itervalues())

                if (inAllRows and notInColumns) or (inAllColumns and notInRows):
                    swordfishes[group].append(candidate)

        for group, candidates in swordfishes.iteritems():
            neighbours = self.swordfishNeighbours(group)

            for location in neighbours:

                removedCandidates = self.removeSolvingCandidates(location, *candidates)

                if removedCandidates:
                    log.append(successString % (removedCandidates, location, group))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log




    def simpleColouring(self):

        self.initialiseIntersections("conjugateChains")

        self.changes = False

        log = []

        for chainGroup in self.intersectionTypes["conjugateChains"]:
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
            if not self.validConjugateChain((chain, candidate)):
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
            if not self.validConjugateChain((chain, candidate)):
                break

            for pair in self.nLocations(colour, 2):

                if not self.alignment(*pair):
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

        for pair in self.nLocations(chain, 2):
            if not self.validConjugateChain((chain, candidate)):
                break

            for alignment in self.alignment(*pair):
                if ((pair[0] in colourOne and pair[1] in colourTwo) or
                    (pair[1] in colourOne and pair[0] in colourTwo)):
                    for location in self.neighbourMethods[alignment](pair[0], *pair):

                        removedCandidates = self.removeSolvingCandidates(location, candidate)

                        if removedCandidates:
                            log.append(successString % (candidate, location))

        return log

    def simpleColourCase5(self, chain, colourOne, colourTwo, candidate):
        """If a location can see two locations in a chain that have different
           colours, this location must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        successString = """%s has been removed from %s, as this location can "see" both %s, locations of different colours"""

        log = []

        for location in self.emptyLocations():
            if location in chain:
                continue

            if candidate not in self.solvingCandidates(location):
                continue

            for pair in self.nLocations(chain, 2):
                if not self.validConjugateChain((chain, candidate)):
                    break

                if not (((pair[0] in colourOne and pair[1] in colourTwo) or
                        (pair[1] in colourOne and pair[0] in colourTwo))):
                    continue

                alignsWithFirstElement = self.alignment(pair[0], location)
                alignsWithSecondElement = self.alignment(pair[1], location)
                if alignsWithFirstElement and alignsWithSecondElement:

                    removedCandidates = self.removeSolvingCandidates(location, candidate)

                    if removedCandidates:
                        log.append(successString % (candidate, location, pair))

        return log




    def yWing(self):
        self.initialiseIntersections("yWing")

        self.changes = False

        log = []
        successString = "Y-Wing: %s has been removed from %s, as it can be seen by %s, part of a Y-Wing"

        for yWingGroup in self.intersectionTypes["yWing"]:
            yWingLocations = yWingGroup[0]
            yWingCandidate = yWingGroup[1]
            firstArm = yWingLocations[1]
            secondArm = yWingLocations[2]

            firstArmNeighbours = self.combinedNeighbours(firstArm)
            secondArmNeighbours = self.combinedNeighbours(secondArm)

            commonNeighbours = ((set(firstArmNeighbours) &
                                set(secondArmNeighbours)) -
                                set(yWingLocations))

            for location in commonNeighbours:

                removedCandidates = self.removeSolvingCandidates(location, yWingCandidate)

                if removedCandidates:
                    log.append(successString % (yWingCandidate, location, (firstArm, secondArm)))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log

    def xyzWing(self):
        self.initialiseIntersections("xyzWing")

        self.changes = False

        log = []

        successString = "XYZ-Wing: %s has been removed from %s, as it can be seen by %s, an XYZ-Wing"

        for xyzWingGroup in self.intersectionTypes["xyzWing"]:
            xyzWingLocations = xyzWingGroup[0]
            xyzWingCandidate = xyzWingGroup[1]
            pivot = xyzWingLocations[0]
            firstArm = xyzWingLocations[1]
            secondArm = xyzWingLocations[2]

            pivotNeighbours = self.combinedNeighbours(pivot, *xyzWingLocations)
            firstArmNeighbours = self.combinedNeighbours(firstArm, *xyzWingLocations)
            secondArmNeighbours = self.combinedNeighbours(secondArm, *xyzWingLocations)

            commonNeighbours = (set(pivotNeighbours) &
                                set(firstArmNeighbours) &
                                set(secondArmNeighbours))

            for location in commonNeighbours:

                removedCandidates = self.removeSolvingCandidates(location, xyzWingCandidate)

                if removedCandidates:
                    log.append(successString % (xyzWingCandidate, location, xyzWingLocations))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log




    def remotePairs(self):
        self.initialiseIntersections("lockedChains")

        self.changes = False

        log = []

        successString = "Remote Pair: %s has been removed from %s, as it can be seen by the remote pair %s, part of the locked chain %s"

        for lockedChainGroup in self.intersectionTypes["lockedChains"]:
            lockedChain, candidates = lockedChainGroup[0], lockedChainGroup[1]

            remotePairs = []
            steps = xrange(3, len(lockedChain), 2)
            for step in steps:
                for i in xrange(len(lockedChain) - step):
                    remotePairs.append((lockedChain[i], lockedChain[i+step]))

            for remotePair in remotePairs:
                locationOne, locationTwo = remotePair[0], remotePair[1]

                locationOneNeighbours = self.combinedNeighbours(locationOne, *lockedChain)
                locationTwoNeighbours = self.combinedNeighbours(locationTwo, *lockedChain)
                remotePairNeighbours = (set(locationOneNeighbours) &
                                        set(locationTwoNeighbours))

                for neighbour in remotePairNeighbours:

                    removedCandidates = self.removeSolvingCandidates(neighbour, *candidates)

                    if removedCandidates:

                        log.append(successString % (removedCandidates, neighbour, remotePair, lockedChain))

        if self.changes:
            self.updatePuzzle()

        return self.changes, log
