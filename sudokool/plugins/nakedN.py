from sudokool.plugin import Plugin

class __nakedN(Plugin):

    def __init__(self):
        self.name = "Naked N"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 0

    def solve(self, puzzle, n):

        successString = self.name + ": {0} have been removed from {1} as it shares a {2} with the " + self.name + ", {3}"

        for intersectionType in puzzle.units:

            for group in puzzle.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in puzzle.nLocations(group, n):

                    nakedNcandidates = puzzle.allSolvingCandidates(*combination)

                    if len(nakedNcandidates) != n:
                        continue

                    surroundingLocations = [location for location in group if location not in combination]

                    for surroundingLocation in surroundingLocations:

                        removedCandidates = puzzle.removeSolvingCandidates(surroundingLocation, *nakedNcandidates)

                        if removedCandidates:

                            puzzle.addToLog(successString, removedCandidates, location, puzzle.alignment(*combination)[0], combination)

class nakedTwin(__nakedN):

    def __init__(self):
        self.name = "Naked Twin"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 1

    def solve(self, puzzle):
        return super(__nakedN, self).solve(puzzle, 2)

class nakedTriple(__nakedN):

    def __init__(self):
        self.name = "Naked Triple"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 2

    def solve(self, puzzle):
        return super(__nakedN, self).solve(puzzle, 3)