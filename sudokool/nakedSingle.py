from plugin import Plugin

class nakedSingle(Plugin):

    def __init__(self):
        self.name = "Naked Single"
        self.description ='''
        This plugin looks in every intersection (e.g. row, column, subGrid) and
        places a number if only one can exist in that intersection.
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 0

    def solve(self, puzzle):
        successString = "Naked Single: {0} was set to {1}"

        for location in puzzle.emptyLocations():
            candidates = puzzle.allSolvingCandidates(location)
            if len(candidates) == 1:
                nakedSingle = candidates.pop()

                puzzle.setValue(location, nakedSingle)

                puzzle.addToLog(successString, location, nakedSingle)
