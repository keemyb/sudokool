

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

    return factors




class Sudoku(object):
    '''A sudoku puzzle

    A sudoku can use user provided values or it can generate puzzles on the fly.

    Args:
        data (str): The values that will populate the values of the sudoku. If
                    no size has been provided than a size must be provided.
        size (int): The number of rows and columns that a sudoku will have. This
                    is unecessary if data has been provided.
        difficulty (float): A number between 0 and 1, higher difficulty values
                    generate harder sudokus.
        horizontalSubGrids (boolean): Sets the orientation of subGrids. Defaults
                    to true.
    '''

    def __init__(self, data=None, size=None, difficulty=None, horizontalSubGrids=True):
        if data is None and size is None:
            raise ValueError("No data or size info given")

        self.horizontalSubGrids = horizontalSubGrids
        self.calculateDimensions(data, size, horizontalSubGrids)
        self.generatePossibleValues()

        self.undoStack = []
        self.redoStack = []
        self.undoDepth = 0

        self.processData(data)

        if data is None:
            self.generateSudoku(difficulty)

        self.constants = [location for location in self.locations() if self.isFilled(location)]

        self.solvingCandidatesDict = {location : set([]) for location in self.locations()}
        self.userCandidatesDict = {location : set([]) for location in self.locations()}

        self.generateEdges()

        self.log = []
        self.history = []

        self.solveMode = False
        self.changes = False
        self.hasCandidates = False
        self.hasIntersections = False

        self.plugins = {}
        self.registerPlugins()

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

        string += horizontalDivider

        return string

    def calculateDimensions(self, data, size, horizontalSubGrids):
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

        listOfFactors = factors(self.gridSize)

        #if the gridsize is not a perfect square, find the two closest factors
        #so we get subgrids as close to a square as possible instead of rectangles
        closestDifference = self.gridSize
        for factorOne in listOfFactors:
            for factorTwo in listOfFactors:
                if factorOne * factorTwo != self.gridSize:
                    continue
                difference = abs(factorOne-factorTwo)
                if difference < closestDifference:
                    closestDifference = difference
                    self.subGridsX, self.subGridsY = sorted((factorOne, factorTwo))

        #if the horizontalSubGrids is True, there will be more subGrids in the X
        #plane than the Y
        if not horizontalSubGrids:
            self.subGridsX, self.subGridsY = self.subGridsY, self.subGridsX

    def generateEdges(self):
        edges = {}

        for location in self.locations():
            # The location as if it were in the first row of subgrids
            firstSubGridRowLocation = location % (self.unitSize() * self.subGridsInRow())
            if firstSubGridRowLocation == 0:
                firstSubGridRowLocation = self.unitSize() * self.subGridsInRow()

            subGridColumn = (self.getColumn(location) - 1) / self.subGridsInColumn() + 1

            # The location as if it were in the first subgrid
            firstSubGridLocation = firstSubGridRowLocation - ((subGridColumn - 1) * self.subGridsInColumn())

            #these represent if the location shares an edge with the subgrid
            top, right, bottom, left = (False,)*4
            if self.getRow(firstSubGridLocation) == 1:
                top = True
            elif self.getRow(firstSubGridLocation) == self.subGridsInRow():
                bottom = True
            if self.getColumn(firstSubGridLocation) == self.subGridsInColumn():
                right = True
            elif self.getColumn(firstSubGridLocation) == 1:
                left = True

            edges[location] = top, right, bottom, left

        self.edges = edges

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

            # making a copy of the mask while iterating to stop an infinite loop
            # as we would otherwise keep rotating rotated elements 
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
        from copy import copy

        solvable = False

        maskValues = None

        blank = self.captureState()

        while not solvable:
            #reset puzzle if still not solveable
            self.restoreState(blank)

            #generate random puzzle (solving a blank puzzle with random matrix column choices)
            self.dancingLinks(True)

            self.solution = copy(self.values)

            mask = self.generateMask()

            for location in self.locations():
                if location not in mask:

                    #setting value manually to bypass undo overhead
                    #negates the need to have constants list setup (needed by clearLocation)
                    self.values[location] = 0

            maskValues = copy(self.values)

            #try to solve, to see if the puzzle is still valid
            self.dancingLinks()

            if self.isComplete():
                solvable = True

        self.values = maskValues
        self.undoStack = []




    def processData(self, data):
        if data is None:
            self.values = {location: 0 for location in self.locations()}
            return

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

    def solve(self, currentLevel=0, maxSuccessfulSolveOperations=None, forceSolveOnFail=False):

        if maxSuccessfulSolveOperations == 0:
            return

        if self.isComplete():
            return

        self.initialiseIntersections()
        self.registerPlugins()

        availableRanks = sorted([rank for rank in self.plugins.iterkeys() if rank >= currentLevel])
        if not availableRanks:
            return

        currentLevel = availableRanks[0]
        nextMethod = self.plugins[currentLevel]

        self.changes = False
        nextMethod.solve(self)

        if self.changes:
            currentLevel = 0
        else:
            if len(availableRanks) == 1:
                #no more methods available
                if forceSolveOnFail:
                    self.dancingLinks()
                return
            else:
                currentLevel = availableRanks[1]

        return self.solve(currentLevel, maxSuccessfulSolveOperations, forceSolveOnFail)




    def registerPlugins(self):
        if self.plugins:
            return

        import plugins

        import pkgutil
        import inspect

        for loader, name, is_pkg in pkgutil.walk_packages(plugins.__path__):
            module = loader.find_module(name).load_module(name)

            for className, value in inspect.getmembers(module):
                # User Made Plugin "Base" Class with n parameter
                if className.startswith('__'):
                    continue

                # Base Plugin Class
                if className == 'Plugin':
                    continue

                class_ = getattr(module, className)
                pluginInstance = class_()

                minSize = pluginInstance.minSize
                maxSize = pluginInstance.maxSize

                # Don't register plugins not made for this size sudoku
                if minSize and self.unitSize() < minSize:
                    continue
                elif maxSize and self.unitSize() > maxSize:
                    continue

                self.plugins[pluginInstance.rank] = pluginInstance

    def showRegisteredPlugins(self):
        for rank, plugin in sorted(self.plugins.iteritems()):
            print rank, plugin.name




    def initialiseIntersections(self):
        self.solveMode = True
        #three main intersection types needed for candidates to work
        for intersectionType in self.units:
            if intersectionType in self.intersectionTypes:
                continue

            self.intersectionTypes[intersectionType] = self.generationMethods[intersectionType]()

        self.hasIntersections = True

        if not self.hasCandidates:
            self.initialiseCandidates()

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




    def updatePuzzle(self):

        self.updateUnits()
        self.updateSolvingCandidates()
        self.updateUserCandidates()

        for method in self.plugins.itervalues():
            method.cleanup(self)

    def updateUnits(self):
        for intersectionType in self.units:
            for group in self.intersectionTypes[intersectionType]:
                for location in group[:]:
                    if self.isFilled(location):
                        group.remove(location)




    def undoable(function):

        def wrapper(self, *args, **kwargs):

            self.undoDepth += 1

            if self.undoDepth == 1:
                currentState = self.captureState()
                self.addStateToUndo(currentState)

            originalFunctionOutput = function(self, *args, **kwargs)

            self.undoDepth -= 1

            return originalFunctionOutput

        return wrapper

    def undo(self):
        if not self.undoStack:
            return

        currentState = self.captureState()
        self.addStateToRedo(currentState)

        undoState = self.undoStack[-1]
        self.restoreState(undoState)

        self.undoStack = self.undoStack[:-1]

    def redo(self):
        if not self.redoStack:
            return

        currentState = self.captureState()
        self.addStateToUndo(currentState, True)

        redoState = self.redoStack[-1]
        self.restoreState(redoState)

        self.redoStack = self.redoStack[:-1]

    def captureState(self):
        from copy import copy, deepcopy
        state = []
        state.append(copy(getattr(self, "values", {})))
        state.append(deepcopy(getattr(self, "solvingCandidatesDict", {})))
        state.append(deepcopy(getattr(self, "userCandidatesDict", {})))
        state.append(deepcopy(getattr(self, "log", [])))
        state.append(deepcopy(getattr(self, "history", [])))
        state.append(copy(getattr(self, "changes", False)))
        state.append(deepcopy(getattr(self, "intersectionTypes", {})))

        return state

    def restoreState(self, state):
        self.values = state[0]
        self.solvingCandidatesDict = state[1]
        self.userCandidatesDict = state[2]
        self.log = state[3]
        self.history = state[4]
        self.changes = state[5]
        self.intersectionTypes = state[6]

    def addStateToUndo(self, state, fromRedo=False):

        self.undoStack.append(state)

        # If we are saving the state because we are redoing, we don't
        # want to erase the redo stack! The only time we should do this
        # is if the user/solver has made changes.
        if self.redoStack and not fromRedo:
            self.redoStack = []

    def addStateToRedo(self, state):

        self.redoStack.append(state)

    def solvingMethod(*intersections):

        def decorator(function):

            def wrapper(self, *args, **kwargs):

                self.initialiseIntersections(*intersections)

                self.changes = False

                function(self, *args, **kwargs)

                if self.changes:
                    self.updatePuzzle()

                return self.changes

            return wrapper

        return decorator

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

    @undoable
    def setValue(self, location, value, clear=False):
        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        if not self.isValidInput(value) and not clear:
            raise Exception("value is not vaild")

        removedValue = 0
        removedSolvingCandidates = []

        if self.isModified(location):
            removedValue = self.getValue(location)
        else:
            removedSolvingCandidates = self.allSolvingCandidates(location)

        self.values[location] = value
        self.userCandidatesDict[location].clear()
        self.solvingCandidatesDict[location].clear()

        if removedValue or removedSolvingCandidates:
            self.changes = True

    def getValue(self, location):
        return self.values[location]

    def getValues(self, *locations):
        return set([self.values[location] for location in locations])

    @undoable
    def clearLocation(self, location):

        return self.setValue(location, 0, clear=True)

    def allSolvingCandidates(self, *locations):
        return set([]).union(*[self.solvingCandidatesDict[location] for location in locations])

    def commonSolvingCandidates(self, *locations):
        return set.intersection(*[self.solvingCandidatesDict[location] for location in locations])

    def userCandidates(self, location):
        return self.userCandidatesDict[location]

    @undoable
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

    @undoable
    def addSolvingCandidates(self, location, *candidates):

        addedCandidates = []

        if self.isConstant(location):
            raise Exception("location is a constant and cannot be changed")

        for candidate in candidates:

            if not self.isValidInput(candidate):
                raise Exception("candidate is not vaild")

            if candidate not in self.allSolvingCandidates(location):
                self.solvingCandidatesDict[location].add(candidate)
                addedCandidates.append(candidate)

        if addedCandidates:
            self.changes = True

        return addedCandidates

    @undoable
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




    @undoable
    def dancingLinks(self, random=False):
        matrix = self.populateSparseMatrix()
        self.populateMatrixRows(matrix)
        self.coverFilledColumns(matrix)
        solutions = []
        self.solveMatrix(matrix, solutions, random)
        self.interpretSolution(matrix, solutions)

    def interpretSolution(self, matrix, solutions):
        if len(self.filledLocations()) + len(solutions) != self.unitSize()**2:
            return

        solution = {}

        for node in solutions:
            while node.column.info[0] != 0: #move node in solutions to location (ID 0)
                node = node.right

            for rowNeighbour in node.rowNeighbours():
                intersectionID = rowNeighbour.column.info[0]
                intersectionNo = rowNeighbour.column.info[1]
                value = rowNeighbour.column.info[2]

                if intersectionID == 1:
                    row = intersectionNo
                elif intersectionID == 2:
                    column = intersectionNo

            location = (row - 1) * self.unitSize() + column

            solution[location] = value

        self.values.update(solution)




    def solveMatrix(self, matrix, solutions, random, i=0):
        if matrix.complete():
            return

        if random and i < self.unitSize():
            columnToCover = matrix.randomColumn()
        else:
            columnToCover = matrix.smallestColumn()
        matrix.cover(columnToCover)

        for node in columnToCover.nodes():

            for rowNeighbour in node.rowNeighbours():
                matrix.cover(rowNeighbour.column)

            solutions.append(node)

            self.solveMatrix(matrix, solutions, random, i+1)

            if matrix.complete():
                return

            solutions.pop()

            for rowNeighbour in node.reverseRowNeighbours():
                matrix.uncover(rowNeighbour.column)

        matrix.uncover(columnToCover)

    def populateSparseMatrix(self):
        from toroidalLinkedList import toroidalLinkedList
        matrix = toroidalLinkedList()

        #0: locations, 1: rows, 2: columns, 3: subgrids
        for location in self.locations():
            matrix.addColumn((0, location, 0))
        for intersectionID in xrange(1, 4):
            for intersectionNumber in xrange(1, self.unitSize() + 1):
                for value in self.possibleValues():
                    matrix.addColumn((intersectionID, intersectionNumber, value))

        return matrix

    def findColumn(self, matrix, intersectionID, intersectionNumber, value):
        NoOfColumnsPerIntersection = self.unitSize() ** 2
        columnNumber = intersectionID * NoOfColumnsPerIntersection
        columnNumber += (intersectionNumber - 1) * self.unitSize()
        columnNumber += value

        column = matrix.firstColumn()
        for _ in xrange(columnNumber - 1):
            column = column.right

        return column

    def populateMatrixRows(self, matrix):
        matrixRowLinkPairs = ((0, 1), (1, 2), (2, 3), (3, 0))

        for location in self.locations():
            row = self.getRow(location)
            column = self.getColumn(location)
            subgrid = self.getSubGrid(location)

            for value in self.possibleValues():
                if value > 9:
                    value = ord(value) - 55
                matrixRow = []

                findColumnArgs = (
                    (0, 1, location),
                    (1, row, value),
                    (2, column, value),
                    (3, subgrid, value),
                    )

                for args in findColumnArgs:
                    columnForRow = self.findColumn(matrix, *args)
                    columnForRow.addData(None)
                    matrixRow.append(columnForRow.lastNode())

                for pair in matrixRowLinkPairs:
                    leftNode, rightNode = pair[0], pair[1]
                    matrixRow[leftNode].setRight(matrixRow[rightNode])

                # print len(matrixRow)

    def coverFilledColumns(self, matrix):
        columnsToCover = []

        for location in self.filledLocations():
            value = self.getValue(location)
            if value > 9:
                value = ord(value) - 55
            row = self.getRow(location)
            column = self.getColumn(location)
            subgrid = self.getSubGrid(location)

            findColumnArgs = (
                (0, 1, location),
                (1, row, value),
                (2, column, value),
                (3, subgrid, value),
                )

            for args in findColumnArgs:
                # accounting for covered columns
                columnToCover = self.findColumn(matrix, *args)
                columnsToCover.append(columnToCover)

        for columnToCover in columnsToCover:
            matrix.cover(columnToCover)




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




    def testProspectiveChange(self, candidatesToRemove=None, valuesToAdd=None, maxSuccessfulSolveOperations=0):
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
        if maxSuccessfulSolveOperations:
            prospectivePuzzle.solve(maxSuccessfulSolveOperations=maxSuccessfulSolveOperations)

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




if __name__ == "__main__":
    pass
