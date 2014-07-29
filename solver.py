from sudoku import Sudoku
from operator import add
from copy import deepcopy

class SolvingSudoku(Sudoku):

    def __init__():
        pass

def solver(puzzle, maxLevel, history = None):
    methods = [puzzle.nakedSingle, puzzle.hiddenSingle, puzzle.nakedTwin, puzzle.hiddenTwin, puzzle.nakedTriplet, puzzle.hiddenTriplet]#, puzzle.xWing]

    #puzzle is complete if gridSize ^ 2 values are filled
    if reduce(add, [1 for value in puzzle.values.itervalues() if value != 0], 0) == puzzle.gridSize ** 2:
        return True, [entry[0] for entry in history if history != None]

    if maxLevel > len(methods) or maxLevel < 1:
        maxLevel = len(methods)

    #if solver is run for the first time, solve using first method
    if history == None:
        methods[0]()
        history = [(0, puzzle.changes)]
        return solver(puzzle, maxLevel, history)
    
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
    history.append((nextMethod, puzzle.changes))
    
    return solver(puzzle, maxLevel, history)

def puzzleSummary(puzzle, maxLevel, printPuzzle, printGhostValues, printHistory, no = None):

    puzzle.initialiseIntersections("subGrid", "row", "column")
    preSolved = deepcopy(puzzle)
    postSolved = puzzle

    solveReport = solver(postSolved, maxLevel)

    numberOfPreSolvedValues = reduce(add, [1 for value in preSolved.values.itervalues() if value != 0], 0)
    numberOfPostSolvedValues = reduce(add, [1 for value in postSolved.values.itervalues() if value != 0], 0)

    if no == None:
        no = ""
    else:
        no = str(no) + " "

    if not postSolved.isValid():
        valid = "\n" + "Puzzle Invalid"
    else:
        valid = "\n"

    if printPuzzle:
        printPuzzle = "\n" + str(preSolved) + valid + str(postSolved) + "\n"
    else:
        printPuzzle = valid

    changedGhostsString = ""
    if printGhostValues:
        for key in postSolved.ghostValues.iterkeys():
            if postSolved.ghostValues[key] != preSolved.ghostValues[key]:
                changedGhostsString += "\n" + str(key) + " " + str(preSolved.ghostValues[key]) + " " + str(postSolved.ghostValues[key])

    history = ""
    if printHistory:
        history = "\n" + str(solveReport[1])

    return no + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + history + changedGhostsString + printPuzzle + "\n"