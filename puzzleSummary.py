from copy import deepcopy

def puzzleSummary(puzzle, maxLevel, printPuzzle, printChangedCandidates, printHistory, number=None, verbose=True):

    puzzle.initialiseIntersections()
    preSolved = deepcopy(puzzle)
    postSolved = puzzle

    solveReport = postSolved.solve(maxLevel)

    numberOfPreSolvedValues = preSolved.getNumberOfFilledLocations()
    numberOfPostSolvedValues = postSolved.getNumberOfFilledLocations()

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
    if printChangedCandidates:
        for key in postSolved.candidates.iterkeys():
            if postSolved.candidates[key] != preSolved.candidates[key]:
                changedCandidatesString += "\n" + str(key) + " " + str(preSolved.candidates[key]) + " " + str(postSolved.candidates[key])

    history = ""
    if printHistory:
        if verbose:
            # history = "\n" + str(filter(lambda x: 4 in x, solveReport))
            history = "\n" + "\n".join([str(x) for x in solveReport])
        else:
            history = "\n" + str([entry[0] for entry in solveReport])

    return number + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + history + changedCandidatesString + printPuzzle + "\n"