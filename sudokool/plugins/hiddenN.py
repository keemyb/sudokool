from sudokool.plugin import Plugin

class __hiddenN(Plugin):

    def __init__(self):
        self.name = "Hidden N"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 0

    def solve(self, puzzle, n):
        successString = self.name + ": {0} has been removed from {1} as the " + self.name +", {2} only appears in this {3}"

        for intersectionType in puzzle.units:

            for group in puzzle.intersectionTypes[intersectionType]:

                if len(group) <= n:
                    continue

                for combination in puzzle.nLocations(group, n):

                    surroundingLocations = set(group) - set(combination)

                    combinationCandidates = puzzle.allSolvingCandidates(*combination)
                    surroundingCandidates = puzzle.allSolvingCandidates(*surroundingLocations)
                    uniqueCombinationCandidates = combinationCandidates - surroundingCandidates

                    if len(uniqueCombinationCandidates) != n:
                        continue

                    for location in combination:
                        removedCandidates = puzzle.removeSolvingCandidates(location, *surroundingCandidates)

                        if not removedCandidates:
                            continue

                        puzzle.addToLog(successString, removedCandidates, location, uniqueCombinationCandidates, intersectionType)

class hiddenSingle(__hiddenN):

    def __init__(self):
        self.name = "Hidden Single"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 3

    def solve(self, puzzle):
        return super(__hiddenN, self).solve(puzzle, 1)

class hiddenTwin(__hiddenN):

    def __init__(self):
        self.name = "Hidden Twin"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 4

    def solve(self, puzzle):
        return super(__hiddenN, self).solve(puzzle, 2)

class hiddenTriple(__hiddenN):

    def __init__(self):
        self.name = "Hidden Triple"
        self.description ='''
        pass
        '''
        self.minSize = 3
        self.maxSize = None
        self.rank = 5

    def solve(self, puzzle):
        return super(__hiddenN, self).solve(puzzle, 3)