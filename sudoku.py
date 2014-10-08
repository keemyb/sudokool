

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

    def __init__(self, data=None, size=None, difficulty=None, horizontalFormat=True):
        if data is None and size is None:
            raise ValueError("No data or size info given")

        self.horizontalFormat = horizontalFormat
        self.calculateDimensions(data, size, horizontalFormat)
        self.generatePossibleValues()

        generateSudoku = False
        if data is None:
            data = "0"*self.unitSize()**2
            generateSudoku = True

        self.processData(data)

        self.solvingCandidatesDict = {location : set([]) for location in self.locations()}
        self.userCandidatesDict = {location : set([]) for location in self.locations()}
        self.log = []
        self.history = []

        self.undoStack = []
        self.redoStack = []

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

        if generateSudoku:
            self.generateSudoku(difficulty)

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

    def calculateDimensions(self, data, size, horizontalFormat):
        # gridSize is the (nearest) square root of the length of the data.
        # It is the nearest square as we cannot guarantee how many values will be
        # provided
        if data is not None:
            self.gridSize = int(len(data) ** 0.5)
        else:
            self.gridSize = size

        # If the amount of values provided is not a square number the puzzle will be invalid.
        # The amount of values is compared to self.gridSize, the nearest square of the number
        # of values provided.
        if data is not None:
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

    def generateMask(self, difficulty=None):
        from random import random
        from random import shuffle

        rotate = random() > 0.5

        if difficulty is None:
            difficulty = 0.5

        valuesInHardPuzzle = round((26/81.0) * len(self.locations()))
        valuesInEasyPuzzle = round((32/81.0) * len(self.locations()))

        variableValues = valuesInEasyPuzzle - valuesInHardPuzzle

        valuesToUse = valuesInHardPuzzle + variableValues * (1-difficulty)

        firstRowIndices = range(1, self.unitSize()/2 + 1)
        firstQuadrantIndices = firstRowIndices[:]

        for row in xrange(1, self.unitSize()/2):
            for index in firstRowIndices:
                firstQuadrantIndices.append(index + row * self.unitSize())

        selectedMiddleLocations = []
        if self.unitSize() % 2 == 1:
            middleStripIndices = range(self.unitSize()/2 + 1, (self.unitSize()**2 - 1)/2 + 2, self.unitSize())
            shuffle(middleStripIndices)
            for i in xrange(2):
                selectedMiddleLocations.append(middleStripIndices[i])

        selectedQuadrantLocations = []
        shuffle(firstQuadrantIndices)
        while len(selectedQuadrantLocations) < ((valuesToUse - len(selectedMiddleLocations)) / 4.0):
            newLocation = firstQuadrantIndices[0]
            firstQuadrantIndices.remove(newLocation)
            selectedQuadrantLocations.append(newLocation)

        if rotate and (self.unitSize() % 2 == 1):
            mask = selectedQuadrantLocations + selectedMiddleLocations

            for location in mask[:]:
                mask += self.rotate090(location)

        else:
            mask = selectedQuadrantLocations
            if self.unitSize() % 2 == 1:
                xOffset = self.unitSize() / 2 + 1
                yOffset = (self.unitSize() / 2 + 1) * self.unitSize()

            else:
                xOffset = self.unitSize() / 2
                yOffset = (self.unitSize() ** 2) / 2

            offsets = xOffset, yOffset, xOffset + yOffset

            for location in mask[:]:
                for offset in offsets:
                    mask.append(location + offset)

            mask += selectedMiddleLocations
            for location in selectedMiddleLocations:
                mask += self.rotate090(location)

        return mask

    def rotate090(self, location, center=None):
        if center is None:
            center = (self.unitSize()**2 - 1)/2 + 1
        newLocations = []

        centerCoordinates = (self.getColumn(center), self.getRow(center))

        coordinates = (self.getColumn(location) - centerCoordinates[1],
                       self.getRow(location) - centerCoordinates[0])
        coordinates090 = (-coordinates[1], coordinates[0])
        coordinates180 = (-coordinates090[1], coordinates090[0])
        coordinates270 = (-coordinates180[1], coordinates180[0])

        for coordinates in (coordinates090, coordinates180, coordinates270):
            xDifference = coordinates[0]
            yDifference = coordinates[1] * self.unitSize()
            newLocation = center + xDifference + yDifference
            newLocations.append(newLocation)

        return newLocations

    def generateSudoku(self, difficulty):
        from collections import defaultdict
        from random import sample

        while True:

            mask = self.generateMask(difficulty)

            previouslyTriedValues = defaultdict(set)

            modifiedLocations = []

            while True:

                if all(self.isFilled(location) for location in mask):
                    self.brute()
                    if self.isComplete():
                        for location in self.locations():
                            if location not in mask:
                                self.clearLocation(location)
                        valuesString = "".join([str(self.getValue(location)) if self.isFilled(location) else "0" for location in self.locations()])
                        self.__init__(valuesString)
                        return
                    else:
                        for location in self.locations():
                            self.clearLocation(location)
                        break

                for location in mask:

                    if location in modifiedLocations:
                        continue

                    neighbours = self.allCombinedNeighbours(location)

                    possibleValues = self.setOfPossibleValues - self.getValues(*neighbours)
                    possibleValues -= previouslyTriedValues[location]

                    if possibleValues:
                        if len(modifiedLocations) % 2 == 0:
                            newValue = sample(possibleValues,1)[0]
                        else:
                            newValue = possibleValues.pop()
                        self.setValue(location, newValue)
                        previouslyTriedValues[location].add(newValue)
                        modifiedLocations.append(location)
                        break
                    else:
                        superBreak = False

                        if modifiedLocations:
                            incorrectLocation = modifiedLocations[-1]
                            self.clearLocation(incorrectLocation)

                            modifiedLocations = modifiedLocations[:-1]
                            # Atleast one of the previous locations are incorrect,
                            # so we may need to choose a previously chosen value again
                            del previouslyTriedValues[location]
                            break
                        else:
                            # if there are no modified locations, there are no solutions.
                            superBreak = True

                        if superBreak:
                            break


    def processData(self, data):
        self.values = {location: data[location - 1] for location in self.locations()}
        for location, value in self.values.iteritems():
            try:
                # As we take in numbers via a string, we must try and turn them
                # back into integers again. If this can't be done it may be
                # because either the value is not a possible values, or for
                # sudokus larger than 9x9, that letters have to be used as values
                self.values[location] = int(value)
            except ValueError:
                # if the value is unacceptable, treat it as empty. This allows
                # the user to use any delimiter that is not a value for simplicity.
                if value not in self.setOfPossibleValues:
                    self.values[location] = 0

        self.constants = [location for location in self.locations() if self.isFilled(location)]




    def isValid(self):
        self.initialiseCandidates()

        for location in self.locations():

            # checking clashes only in diagonal locations and subgrid starts
            # to get every locations
            if (location % (self.unitSize() + 1) == 1 or
                    location in self.getSubGridStartLocations()):
                if self.isClashing(location):
                    return False

            if self.isEmpty(location):
                if len(self.allSolvingCandidates(location)) == 0:
                    return False
            else:
                if self.getValue(location) not in self.setOfPossibleValues:
                    return False

        return True

    def isComplete(self):
        numberOfLocations = len(self.locations())
        numberOfFilledLocations = len(self.filledLocations())
        if numberOfFilledLocations == numberOfLocations:
            return True
        return False

    def solve(self, maxLevel=None, maxSuccessfulSolveOperations=None, bruteForceOnFail=False):

        if maxSuccessfulSolveOperations == 0:
            return

        if self.isComplete():
            return

        if (maxLevel is None or
                maxLevel > len(self.solvingMethods) or
                maxLevel < 1):
            # maxLevel is the lenght minus 1 as lists are zero indexed, so the
            # first method has an index 0
            maxLevel = len(self.solvingMethods) - 1

        #if solver is run for the first time, solve using first method
        if not self.history:
            self.changes = False
            nextMethod = 0
        #if last attempt was successful, go back to first level
        elif self.changes:
            nextMethod = 0
        #or if unsuccessful, increase level
        else:
            lastMethod = self.history[-1]
            nextMethod = lastMethod + 1

        if nextMethod <= maxLevel:
            self.solvingMethods[nextMethod]()
            self.history.append(nextMethod)
            if maxSuccessfulSolveOperations and self.changes:
                maxSuccessfulSolveOperations -= 1
            return self.solve(maxLevel, maxSuccessfulSolveOperations)
        else:
            #no more methods
            if bruteForceOnFail:
                self.brute()
            return




    def testProspectiveChange(self, candidatesToRemove=None, valuesToAdd=None, solveDepth=None):
        from copy import deepcopy

        prospectivePuzzle = deepcopy(self)

        if candidatesToRemove is not None:
            for location, candidates in candidatesToRemove.iteritems():
                prospectivePuzzle.removeSolvingCandidates(location, *candidates)

        if valuesToAdd is not None:
            for location, value in valuesToAdd.iteritems():
                del prospectivePuzzle.candidates[location]
                prospectivePuzzle.values[location] = value

        prospectivePuzzle.updatePuzzle()
        if solveDepth:
            prospectivePuzzle.solve(solveDepth)

        return prospectivePuzzle.isValid()

    def applyProspectiveChange(self, candidatesToRemove=None, valuesToAdd=None):
        if candidatesToRemove is not None:
            for location, candidates in candidatesToRemove.iteritems():
                self.removeSolvingCandidates(location, *candidates)

        if valuesToAdd is not None:
            for location, value in valuesToAdd.iteritems():
                del self.solvingCandidatesDict[location]
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

        for location in self.emptyLocations():

            neighbours = self.allCombinedNeighbours(location)

            surroundingValues = self.getValues(*neighbours)

            self.solvingCandidatesDict[location] = self.setOfPossibleValues - surroundingValues

        self.hasCandidates = True

    def updateSolvingCandidates(self):

        for location in self.solvingCandidatesDict.iterkeys():

            neighbours = self.allCombinedNeighbours(location)

            surroundingValues = self.getValues(*neighbours)

            self.solvingCandidatesDict[location] -= surroundingValues

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

            locationCandidates = self.allSolvingCandidates(location)

            for candidate in locationCandidates:

                for method in self.neighbourMethods.itervalues():

                    candidateCount = 1
                    prospectiveLocation = None

                    for neighbour in method(location):
                        neighbourCandidates = self.allSolvingCandidates(neighbour)

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

                yWingCandidate = self.commonSolvingCandidates(*yWingLocations[1:])

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

        commonCandidates = self.commonSolvingCandidates(*pair)
        if not commonCandidates:
            return False

        firstLocationCandidates = self.allSolvingCandidates(pair[0])
        secondLocationCandidates = self.allSolvingCandidates(pair[1])

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

                xyzWingCandidate = self.commonSolvingCandidates(firstArm, secondArm)

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
            candidates = self.allSolvingCandidates(location)
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

            locationOneCandidates = self.allSolvingCandidates(pair[0])
            if len(locationOneCandidates) != 2:
                continue

            locationTwoCandidates = self.allSolvingCandidates(pair[1])
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

        self.updateUnits()
        self.updateSolvingCandidates()
        self.updatePointerGroups()
        self.updateXWingGroups()
        self.updateSwordfishGroups()
        self.updateConjugatePairs()
        self.updateConjugateChains()
        self.updateYWingGroups()
        self.updateXYZWingGroups()
        self.updateLockedPairs()
        self.updateLockedChains()

    def updateUnits(self):
        for intersectionType in self.units:
            for group in self.intersectionTypes[intersectionType]:
                for location in group[:]:
                    if self.isFilled(location):
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
            if len(self.allSolvingCandidates(location)) <= 1:
                return False
            if candidate not in self.solvingCandidatesDict[location]:
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
                if len(self.allSolvingCandidates(location)) != 2:
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
                numberOfCandidates = len(self.allSolvingCandidates(location))
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
            if candidates != self.allSolvingCandidates(location):
                return False
        return True




    def isEmpty(self, location):
        if self.values[location] not in self.setOfPossibleValues:
            return True

        return False

    def isFilled(self, location):
        if self.values[location] in self.setOfPossibleValues:
            return True

        return False

    def isConstant(self, location):
        if location in self.constants:
            return True

        return False

    def isModified(self, location):
        if self.isConstant(location) or self.isEmpty(location):
            return False

        return True

    def isClashing(self, location):
        locationValue = self.getValue(location)

        neighbours = self.allCombinedNeighbours(location)
        for neighbour in neighbours:
            if self.isEmpty(neighbour):
                continue
            neighbourValue = self.getValue(neighbour)
            if neighbourValue == locationValue:
                return True

        return False

    def clashesWith(self, location):
        clashes = []
        locationValue = self.getValue(location)

        neighbours = self.allCombinedNeighbours(location)
        for neighbour in neighbours:
            if self.isEmpty(neighbour):
                continue
            neighbourValue = self.getValue(neighbour)
            if neighbourValue == locationValue:
                clashes.append(neighbour)

        return clashes

    def isValidInput(self, value):
        if value in self.setOfPossibleValues:
            return True

        return False

    def possibleValues(self):
        return sorted(self.setOfPossibleValues)

    def locations(self):
        return range(1, self.gridSize ** 2 + 1)

    def emptyLocations(self):
        return [location for location in self.locations() if self.isEmpty(location)]

    def filledLocations(self):
        return [location for location in self.locations() if self.isFilled(location)]

    def modifiedLocations(self):
        return [location for location in self.locations() if self.isModified(location)]

    def clashingLocations(self):
        clashingLocations = set([])

        for location in self.locations():
            locationValue = self.getValue(location)

            neighbours = self.allCombinedNeighbours(location)
            for neighbour in neighbours:
                if self.isEmpty(neighbour):
                    continue
                neighbourValue = self.getValue(neighbour)
                if locationValue == neighbourValue:
                    clashingLocations.add(location)
                    clashingLocations.add(neighbour)

        return clashingLocations

    def nLocations(self, unit, n):
        from itertools import combinations

        return combinations(unit, n)

    def setValue(self, location, value):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(value):
            raise Exception("value is not vaild")

        self.values[location] = value
        self.changes = True
        self.solvingCandidatesDict[location].clear()

    def getValue(self, location):
        return self.values[location]

    def getValues(self, *locations):
        return set([self.values[location] for location in locations])

    def clearLocation(self, location):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        removedValue = 0
        removedCandidates = []

        if self.isModified(location):
            removedValue = self.getValue(location)
        else:
            removedCandidates = list(self.allSolvingCandidates(location))

        self.values[location] = 0
        self.userCandidatesDict[location] = set([])

        if removedValue or removedCandidates:
            self.changes = True

    def allSolvingCandidates(self, *locations):
        return set([]).union(*[self.solvingCandidatesDict[location] for location in locations])

    def commonSolvingCandidates(self, *locations):
        return set.intersection(*[self.solvingCandidatesDict[location] for location in locations])

    def userCandidates(self, location):
        return self.userCandidatesDict[location]

    def removeSolvingCandidates(self, location, *candidates):

        removedCandidates = []

        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        for candidate in candidates:

            if not self.isValidInput(candidate):
                raise Exception("candidate is not vaild")

            if candidate in self.allSolvingCandidates(location):
                self.solvingCandidatesDict[location].remove(candidate)
                removedCandidates.append(candidate)

        if removedCandidates:
            self.changes = True

        return removedCandidates

    def addSolvingCandidates(self, location, *candidates):

        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        for candidate in candidates:
            if not self.isValidInput(candidate):
                raise Exception("candidate is not vaild")

            self.solvingCandidatesDict[location].add(candidate)

        self.changes = True


    def toggleUserCandidate(self, location, candidate):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(candidate):
            raise Exception("candidate is not vaild")

        if not self.isEmpty(location):
            self.clearLocation(location)

        if candidate in self.userCandidatesDict[location]:
            self.userCandidatesDict[location].remove(candidate)
        else:
            self.userCandidatesDict[location].add(candidate)

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




    def brute(self):
        self.initialiseIntersections()

        from collections import defaultdict

        previouslyTriedValues = defaultdict(set)

        modifiedLocations = []

        while True:

            if self.isComplete() and self.isValid():
                return

            for location in self.emptyLocations():

                if self.isConstant(location) or location in modifiedLocations:
                    continue

                neighbours = self.allCombinedNeighbours(location)

                possibleValues = self.setOfPossibleValues - self.getValues(*neighbours)
                possibleValues -= previouslyTriedValues[location]

                if possibleValues:
                    newValue = possibleValues.pop()
                    self.setValue(location, newValue)
                    previouslyTriedValues[location].add(newValue)
                    modifiedLocations.append(location)
                    break
                else:
                    if modifiedLocations:
                        incorrectLocation = modifiedLocations[-1]
                        self.clearLocation(incorrectLocation)

                        modifiedLocations = modifiedLocations[:-1]
                        # Atleast one of the previous locations are incorrect,
                        # so we may need to choose a previously chosen value again
                        del previouslyTriedValues[location]
                        break
                    else:
                        # if there are no modified locations, there are no solutions.
                        return

    def nakedSingle(self):
        self.initialiseIntersections()

        self.changes = False

        successString = "Naked Single: {0} was set to {1}"

        for location in self.emptyLocations():
            candidates = self.allSolvingCandidates(location)
            if len(candidates) == 1:
                nakedSingle = candidates.pop()

                self.setValue(location, nakedSingle)

                self.addToLog(successString, location, nakedSingle)

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def nakedN(self, n):
        self.initialiseIntersections()

        self.changes = False

        name = "Naked " + self.multiples[n - 1]
        successString = name + ": {0} have been removed from {1} as it shares a {2} with the " + name + ", {3}"

        for intersectionType in self.units:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in self.nLocations(group, n):

                    nakedNcandidates = self.allSolvingCandidates(*combination)

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
        successString = name + ": {0} has been removed from {1} as the " + name +", {2} only appears in this {3}"

        for intersectionType in self.units:

            for group in self.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in self.nLocations(group, n):

                    surroundingLocations = set(group) - set(combination)

                    combinationCandidates = self.allSolvingCandidates(*combination)
                    surroundingCandidates = self.allSolvingCandidates(*surroundingLocations)
                    uniqueCombinationCandidates = combinationCandidates - surroundingCandidates

                    if len(uniqueCombinationCandidates) != n:
                        continue

                    for location in combination:
                        removedCandidates = self.removeSolvingCandidates(location, *surroundingCandidates)

                        if not removedCandidates:
                            continue

                        self.addToLog(successString, removedCandidates, location, uniqueCombinationCandidates, intersectionType)

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

        name = "Pointing " + self.multiples[n - 1]
        successString = name + ": {0} has been removed from {1}, as it shares a {2} with the " + name + " {3}"

        for pointerGroup in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = pointerGroup[0], pointerGroup[1]

            subGridNeighbours = self.subGridNeighbours(combination[0], *combination)
            subGridNeighbourCandidates = self.allSolvingCandidates(*subGridNeighbours)

            commonPointerCandidates = self.commonSolvingCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in subGridNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            linearNeighbours = self.neighbourMethods[pointerType](combination[0], *combination)

            for location in linearNeighbours:

                removedCandidates = self.removeSolvingCandidates(location, *uniquePointerCandidates)

                if removedCandidates:

                    self.addToLog(successString, removedCandidates, location, pointerType, combination)

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

        name = "Box Line Reduction (" + self.multiples[n - 1] + ")"
        successString = name + ": {0} has been removed from {1}, as it is part of a subGrid where {2} can only be placed along it's {3}"

        for pointerGroup in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = pointerGroup[0], pointerGroup[1]

            linearNeighbours = self.neighbourMethods[pointerType](combination[0], *combination)
            linearNeighbourCandidates = self.allSolvingCandidates(*linearNeighbours)

            commonPointerCandidates = self.commonSolvingCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in linearNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            subGridNeighbours = self.subGridNeighbours(combination[0], *combination)

            for location in subGridNeighbours:
                removedCandidates = self.removeSolvingCandidates(location, *uniquePointerCandidates)

                if removedCandidates:

                    self.addToLog(successString, removedCandidates, location, commonPointerCandidates, pointerType)

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

        successString = "X-Wing: {0} has been removed from {1}, as it is in alignment with the X-Wing, {2}"

        from collections import defaultdict
        from itertools import chain

        xWings = defaultdict(list)

        for group in self.intersectionTypes["xWing"]:

            commonXWingCandidates = self.commonSolvingCandidates(*group)

            if len(commonXWingCandidates) == 0:
                continue

            rowCandidates = (self.allSolvingCandidates(*self.rowNeighbours(group[0], *group)) |
                             self.allSolvingCandidates(*self.rowNeighbours(group[2], *group)))
            columnCandidates = (self.allSolvingCandidates(*self.columnNeighbours(group[0], *group)) |
                                self.allSolvingCandidates(*self.columnNeighbours(group[1], *group)))

            for candidate in commonXWingCandidates:
                if (candidate not in rowCandidates or candidate not in columnCandidates):
                    xWings[group].append(candidate)

        for group, candidates in xWings.iteritems():

            for location in self.xWingNeighbours(group):

                removedCandidates = self.removeSolvingCandidates(location, *candidates)

                if removedCandidates:

                    # Needs to be more verbose, showing where the alignment occours
                    self.addToLog(successString, removedCandidates, location, group)

        if self.changes:
            self.updatePuzzle()

        return self.changes




    def swordfish(self):
        self.initialiseIntersections("swordfish")

        self.changes = False

        successString = "Swordfish: {0} has been removed from {1}, as it is in alignment with the Swordfish, {2}"

        from collections import defaultdict

        swordfishes = defaultdict(list)

        for group in self.intersectionTypes["swordfish"]:

            commonCandidates = self.commonSolvingCandidates(*group)

            if len(commonCandidates) == 0:
                continue

            rowCandidates = defaultdict(set)
            for neighbour in self.swordfishRowNeighbours(group):
                rowCandidates[self.getRow(neighbour)].union(self.allSolvingCandidates(neighbour))

            columnCandidates = defaultdict(set)
            for neighbour in self.swordfishColumnNeighbours(group):
                columnCandidates[self.getColumn(neighbour)].union(self.allSolvingCandidates(neighbour))

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
                    self.addToLog(successString, removedCandidates, location, group)

        if self.changes:
            self.updatePuzzle()

        return self.changes




    def simpleColouring(self):

        self.initialiseIntersections("conjugateChains")

        self.changes = False

        for chainGroup in self.intersectionTypes["conjugateChains"]:
            chain, candidate = chainGroup[0], chainGroup[1]
            colourOne, colourTwo = chain[::2], chain[1::2]

            simpleColouringMethods = (self.chainOnOff,
                                      self.simpleColourCase2,
                                      self.simpleColourCase4,
                                      self.simpleColourCase5)

            for method in simpleColouringMethods:
                method(chain, colourOne, colourTwo, candidate)

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def chainOnOff(self, chain, colourOne, colourTwo, candidate):
        """Tests to see if one colour being ON is valid, if it is invalid
           the other colour must be the solution."""

        successString = "Chain ON/OFF: {0} has been removed from locations {1}, as it is part of an invalid colour"

        for testColour in (colourOne, colourTwo):
            if not self.validConjugateChain((chain, candidate)):
                break

            candidatesToRemove = {location: [candidate] for location in testColour}

            # We are looking for a contradiction, so if the prospective change
            # checks out we haven't learnt anything new.
            if self.testProspectiveChange(candidatesToRemove):
                continue

            for correctColour in (colourOne, colourTwo):
                if testColour != correctColour:
                    candidatesToRemove = {location: [candidate] for location in correctColour}
                    self.applyProspectiveChange(candidatesToRemove)
                    self.changes = True
                    self.addToLog(successString, candidate, [location for location in correctColour])
                    return

    def simpleColourCase2(self, chain, colourOne, colourTwo, candidate):
        """If two locations are in the same colour and unit, this colour must
           be OFF, and the other colour must be ON."""

        successString = "Simple Colouring Case 2: locations {0} have been set to {1}, as it shares a unit with a chain where two colours are the same"

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
                self.addToLog(successString, [location for location in correctColour], candidate)
                return

    def simpleColourCase4(self, chain, colourOne, colourTwo, candidate):
        """If two locations are in the same unit and have different colours,
           all other locations in the unit must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        successString = "Simple Colouring Case 4: {0} has been removed from {1}, as these locations are in the same unit as one of two locations that must be ON"

        for pair in self.nLocations(chain, 2):
            if not self.validConjugateChain((chain, candidate)):
                break

            for alignment in self.alignment(*pair):
                if ((pair[0] in colourOne and pair[1] in colourTwo) or
                    (pair[1] in colourOne and pair[0] in colourTwo)):
                    for location in self.neighbourMethods[alignment](pair[0], *pair):

                        removedCandidates = self.removeSolvingCandidates(location, candidate)

                        if removedCandidates:
                            self.addToLog(successString, candidate, location)

    def simpleColourCase5(self, chain, colourOne, colourTwo, candidate):
        """If a location can see two locations in a chain that have different
           colours, this location must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        successString = "Simple Colouring Case 5: {0} has been removed from {1}, as this location can see both {2}, locations of different colours"

        for location in self.emptyLocations():
            if location in chain:
                continue

            if candidate not in self.allSolvingCandidates(location):
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
                        self.addToLog(successString, candidate, location, pair)




    def yWing(self):
        self.initialiseIntersections("yWing")

        self.changes = False

        successString = "Y-Wing: {0} has been removed from {1}, as it can be seen by {2}, part of a Y-Wing"

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
                    self.addToLog(successString, yWingCandidate, location, (firstArm, secondArm))

        if self.changes:
            self.updatePuzzle()

        return self.changes

    def xyzWing(self):
        self.initialiseIntersections("xyzWing")

        self.changes = False

        successString = "XYZ-Wing: {0} has been removed from {1}, as it can be seen by {2}, an XYZ-Wing"

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
                    self.addToLog(successString, xyzWingCandidate, location, xyzWingLocations)

        if self.changes:
            self.updatePuzzle()

        return self.changes




    def remotePairs(self):
        self.initialiseIntersections("lockedChains")

        self.changes = False

        successString = "Remote Pair: {0} has been removed from {1}, as it can be seen by the remote pair {2}, part of the locked chain {3}"

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

                        self.addToLog(successString, removedCandidates, neighbour, remotePair, lockedChain)

        if self.changes:
            self.updatePuzzle()

        return self.changes
