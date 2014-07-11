from sudoku import sudoku
from operator import add
from copy import deepcopy

def solver(puzzle, maxLevel, breakdown, history = None):
    methods = [puzzle.nakedSingle, puzzle.hiddenSingle, puzzle.nakedTwin]

    #puzzle is complete if gridSize ^ 2 values are filled
    if reduce(add, [1 for value in puzzle.values.itervalues() if value != 0], 0) == puzzle.gridSize ** 2:
        if breakdown:
            return False, [entry[0] for entry in history if history != None], [entry[2] for entry in history if history != None]
        else:
            return False, [entry[0] for entry in history if history != None], ""

    if maxLevel > len(methods):
        maxLevel = len(methods)

    #if solver is run for the first time, solve using first method
    if history == None:
        methods[0]()
        if breakdown:
            history = [(0, puzzle.changes, str(puzzle))]
        else:
            history = [(0, puzzle.changes)]
        return solver(puzzle, maxLevel, breakdown, history)
    
    #if last attempt was successful, go back to first level

    lastMethod = history[-1][0]
    if history[-1][1] == True:
        nextMethod = 0
    #or if unsuccessful, increase level or exit if highest level was tried
    else:
        if lastMethod == maxLevel - 1:
            if breakdown:
                return False, [entry[0] for entry in history if history != None], [entry[2] for entry in history if history != None]
            else:
                return False, [entry[0] for entry in history if history != None], ""
        else:
            nextMethod = lastMethod + 1

    methods[nextMethod]()
    if breakdown:
        history.append((nextMethod, puzzle.changes, str(puzzle)))
    else:
        history.append((nextMethod, puzzle.changes))
    
    return solver(puzzle, maxLevel, breakdown, history)

def puzzleSummary(puzzle, maxLevel, printPuzzle, breakdown, printGhostValues, no = None):

    preSolved = puzzle
    postSolved = deepcopy(preSolved)

    solveReport = solver(postSolved, maxLevel, breakdown)

    numberOfPreSolvedValues = reduce(add, [1 for value in preSolved.values.itervalues() if value != 0], 0)
    numberOfPostSolvedValues = reduce(add, [1 for value in postSolved.values.itervalues() if value != 0], 0)

    if no == None:
        no = 1

    if printPuzzle:
        printPuzzle = str(preSolved) + "\n" + str(postSolved) + "\n"
    else:
        printPuzzle = ""

    changedGhostsString = ""
    if printGhostValues:
        for key in postSolved.ghostValues.iterkeys():
            if postSolved.ghostValues[key] != preSolved.ghostValues[key]:
                changedGhostsString += "\n" + str(key) + " " + str(preSolved.ghostValues[key]) + " " + str(postSolved.ghostValues[key])

    return str(no) + " " + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + "\n" + str(solveReport[1]) + str(solveReport[2]) + str(changedGhostsString) + "\n" + printPuzzle + "\n" * 2