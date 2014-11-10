from sudokool.plugin import Plugin

class __nakedN(Plugin):

    def __init__(self):
        self.name = "Naked N"
        self.description ='''
        This plugin looks for n cells in every intersection that have n, and 
        only n candidates in common. If these are found, these n candidates are
        removed from every intersection all n cells have in common.
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
        This plugin looks for 2 cells in every intersection that have 2, and 
        only 2 candidates in common. If these are found, these 2 candidates are
        removed from every intersection both cells have in common. 
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
        This plugin looks for 3 cells in every intersection that have 3, and 
        only 3 candidates in common. If these are found, these 3 candidates are
        removed from every intersection all 3 cells have in common. 
        '''
        self.minSize = 3
        self.maxSize = None
        self.rank = 2

    def solve(self, puzzle):
        return super(__nakedN, self).solve(puzzle, 3)
