from copy import deepcopy

def puzzleSummary(puzzle, maxLevel, printPuzzle, printCandidateValues, printHistory, number = None):

    puzzle.initialiseIntersections()
    preSolved = deepcopy(puzzle)
    postSolved = puzzle

    solveReport = postSolved.solve(maxLevel)

    numberOfPreSolvedValues = preSolved.getNumberOfFilledLocations()
    numberOfPostSolvedValues = postSolved.getNumberOfFilledLocations()

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