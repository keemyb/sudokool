from sudokool.plugin import Plugin

class nakedSingle(Plugin):
    '''Naked Single

    This plugin looks for a location in every intersection
    (e.g. row, column, subGrid) that has only one candidate. If such location is
    found it's value is set to the value of the remaining candidate.
    '''

    def __init__(self):
        self.name = "Naked Single"
        self.minSize = None
        self.maxSize = None
        self.rank = 0

    def solve(self, puzzle):
        successString = "Naked Single: {0} was set to {1}"

        for location in puzzle.emptyLocations():
            candidates = puzzle.allSolvingCandidates(location)

            # If there is only one candidate, it must be the value of that cell,
            # assuming the puzzle is valid.
            if len(candidates) == 1:
                nakedSingle = candidates.pop()

                puzzle.setValue(location, nakedSingle)

                puzzle.addToLog(successString, location, nakedSingle)
