from sudoku import Sudoku
from operator import add
from copy import deepcopy

def solver(puzzle, maxLevel, history = None):
    methods = [puzzle.nakedSingle, puzzle.hiddenSingle, puzzle.nakedTwin, puzzle.hiddenTwin, \
    puzzle.pointingPair, puzzle.pointingTriplet, \
    puzzle.boxLineReduction2, puzzle.boxLineReduction3, \
    puzzle.nakedTriplet, puzzle.hiddenTriplet, \
    puzzle.xWing]
    # methods = [puzzle.nakedSingle, puzzle.pointingPair, puzzle.pointingTriplet]
    # methods = [puzzle.boxLineReduction2]

    #puzzle is complete if gridSize ^ 2 values are filled
    if reduce(add, [1 for location in puzzle.values if not puzzle.isEmpty(location)], 0) == puzzle.gridSize ** 2:
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

def puzzleSummary(puzzle, maxLevel, printPuzzle, printCandidateValues, printHistory, number = None):

    puzzle.initialiseIntersections()
    preSolved = deepcopy(puzzle)
    postSolved = puzzle

    solveReport = solver(postSolved, maxLevel)

    numberOfPreSolvedValues = reduce(add, [1 for location in preSolved.values if not preSolved.isEmpty(location)], 0)
    numberOfPostSolvedValues = reduce(add, [1 for location in postSolved.values if not postSolved.isEmpty(location)], 0)

    if number == None:
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
    if printCandidateValues:
        for key in postSolved.candidates.iterkeys():
            if postSolved.candidates[key] != preSolved.candidates[key]:
                changedCandidatesString += "\n" + str(key) + " " + str(preSolved.candidates[key]) + " " + str(postSolved.candidates[key])

    history = ""
    if printHistory:
        history = "\n" + str(solveReport[1])

    return number + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + history + changedCandidatesString + printPuzzle + "\n"