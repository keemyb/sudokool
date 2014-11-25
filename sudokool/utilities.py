from sudoku import Sudoku
from copy import deepcopy

def puzzleSummary(puzzle, maxLevel, printPuzzle, printChangedCandidates, printHistory, number=None, verbose=True):

    puzzle.initialiseIntersections()
    preSolved = deepcopy(puzzle)
    postSolved = puzzle

    postSolved.solve(maxLevel)

    numberOfPreSolvedValues = len(preSolved.filledLocations())
    numberOfPostSolvedValues = len(postSolved.filledLocations())

    if number is None:
        number = ""
    else:
        number = str(number) + " "

    if not postSolved.isValid():
        valid = "\n" + "Puzzle Invalid" + "\n"
    else:
        valid = "\n"

    if printPuzzle:
        printPuzzle = "\n" + str(preSolved) + valid + str(postSolved) + "\n"
    else:
        printPuzzle = valid

    changedCandidatesString = ""
    if printChangedCandidates and not postSolved.isComplete():
        for key in postSolved.solvingCandidatesDict.iterkeys():
            if postSolved.solvingCandidatesDict[key] != preSolved.solvingCandidatesDict[key] and postSolved.solvingCandidatesDict[key]:
                changedCandidatesString += "\n" + str(key) + " " + str(preSolved.solvingCandidatesDict[key]) + " " + str(postSolved.solvingCandidatesDict[key])

    history = ""
    if printHistory:
        if verbose:
            history = "\n" + "\n".join(postSolved.log)
        else:
            history = "\n" + str(postSolved.history)

    return number + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + history + changedCandidatesString + printPuzzle + "\n"

def fromTextPuzzleSummary(textfile, seperator, maxLevel, n, specific, showModified, showSolved, printPuzzle, printGhostValues, printHistory):

    fileToRead = open(textfile, "r")
    currentPuzzle = ""
    puzzles = []

    for line in fileToRead:
        if len(puzzles) <= n:
            if line == seperator:
                puzzles.append(currentPuzzle)
                currentPuzzle = ""
            else:
                currentPuzzle += line.strip()
    if len(currentPuzzle) == len(puzzles[0]):
        puzzles.append(currentPuzzle)

    if specific:
        puzzles = [puzzles[n - 1]]
        no = n
    else:
        no = 1

    results = ""

    for puzzleString in puzzles:
        puzzle = Sudoku(puzzleString, True)
        results += puzzleSummary(puzzle, maxLevel, printPuzzle, printGhostValues, printHistory, no)
        no += 1

    return results

def fromTextToPuzzle(textfile, seperator, n):
    fileToRead = open(textfile, "r")
    currentPuzzle = ""
    puzzles = []

    for line in fileToRead:
        if len(puzzles) <= n:
            if line == seperator:
                puzzles.append(currentPuzzle)
                currentPuzzle = ""
            else:
                currentPuzzle += line.strip()
    if len(currentPuzzle) == len(puzzles[0]):
        puzzles.append(currentPuzzle)

    puzzle = puzzles[n - 1]
    return Sudoku(puzzle, True)

def visualizer(puzzle, *groups):
    wholeString = ""

    for group in groups:
        gridSize = puzzle.gridSize
        subGridsX = puzzle.subGridsX
        subGridsY = puzzle.subGridsY
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

            if position not in group:
                string += "  "
            else:
                string += "0 "

            if position % gridSize == 0:
                string += vPipe + "\n"

            if position == gridSize ** 2:
                string += hPipeString

        wholeString += string

    return wholeString

def visualizeEdges(puzzle):
    string = ""
    vPipe = "="
    hPipe = "="
    # first line to accommodate vertical pipe and following spaces (minus one to account for last v pipe)
    # second line for numbers (and following spaces)
    horizontalDivider = (hPipe * ((len(vPipe) + 1) * (puzzle.subGridsX + 1) - 1) +
                   hPipe * (puzzle.gridSize * 2) +
                   "\n")

    def isFirstLocationOnLine(location):
        if (location - 1) % (puzzle.gridSize * puzzle.subGridsX) == 0:
            return True
        return False

    def isFirstLocationInRowInSubGrid(location):
        if (location - 1) % puzzle.subGridsY == 0:
            return True
        return False

    def isLastLocationInRow(location):
        if location % puzzle.gridSize == 0:
            return True
        return False

    def isLastLocation(location):
        if location == puzzle.gridSize ** 2:
            return True
        return False

    edges = puzzle.edges

    for location in puzzle.locations():

        if isFirstLocationOnLine(location):
            string += horizontalDivider

        if isFirstLocationInRowInSubGrid(location):
            string += vPipe + " "

        if edges[location] == (False,)*4:
            cornerLocation = 5
        elif edges[location][0] and edges[location][1]:
            cornerLocation = 9
        elif edges[location][1] and edges[location][2]:
            cornerLocation = 3
        elif edges[location][2] and edges[location][3]:
            cornerLocation = 1
        elif edges[location][3] and edges[location][0]:
            cornerLocation = 7
        elif edges[location][0]:
            cornerLocation = 8
        elif edges[location][1]:
            cornerLocation = 6
        elif edges[location][2]:
            cornerLocation = 2
        elif edges[location][3]:
            cornerLocation = 4

        string += str(cornerLocation) + " "

        if isLastLocationInRow(location):
            string += vPipe + "\n"

        if isLastLocation(location):
            string += horizontalDivider

    return string
