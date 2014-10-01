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
    if printChangedCandidates:
        for key in postSolved.solvingCandidatesDict.iterkeys():
            if postSolved.solvingCandidatesDict[key] != preSolved.solvingCandidatesDict[key]:
                changedCandidatesString += "\n" + str(key) + " " + str(preSolved.solvingCandidatesDict[key]) + " " + str(postSolved.solvingCandidatesDict[key])

    history = ""
    if printHistory:
        if verbose:
            history = "\n" + "\n".join(postSolved.log)
        else:
            history = "\n" + str(postSolved.history)

    return number + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + history + changedCandidatesString + printPuzzle + "\n"