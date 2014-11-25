from sudokool.plugin import Plugin

class __hiddenN(Plugin):
    '''Hidden N

    This plugin looks for a group of n locations in every intersection
    (e.g. row, column, subGrid) that share n candidates that are not found
    elsewhere in the intersection (a hidden n). If a hidden n is found, all
    other candidates are removed from the group.
    '''
    def __init__(self):
        self.name = "Hidden N"
        self.minSize = None
        self.maxSize = None
        self.rank = 0

    def solve(self, puzzle, n):
        successString = self.name + ": {0} has been removed from {1} as the " + self.name +", {2} only appears in this {3}"

        for intersectionType in puzzle.units:

            for group in puzzle.intersectionTypes[intersectionType]:

                # If the number of locations in a group is not greater than n,
                # there is nothing to look for.
                if len(group) <= n:
                    continue

                for combination in puzzle.nLocations(group, n):

                    surroundingLocations = set(group) - set(combination)

                    combinationCandidates = puzzle.allSolvingCandidates(*combination)
                    surroundingCandidates = puzzle.allSolvingCandidates(*surroundingLocations)

                    uniqueCombinationCandidates = combinationCandidates - surroundingCandidates

                    # if there are n candidates that can only be found in the
                    # combination, we have found a hidden n
                    if len(uniqueCombinationCandidates) != n:
                        continue

                    for location in combination:

                        # Removing every candidate that is found outside the
                        # group to all locations in the hidden n.
                        removedCandidates = puzzle.removeSolvingCandidates(location, *surroundingCandidates)

                        if not removedCandidates:
                            continue

                        puzzle.addToLog(successString, removedCandidates, location, uniqueCombinationCandidates, intersectionType)

class hiddenSingle(__hiddenN):
    '''Hidden Single

    This plugin looks for one location in every intersection
    (e.g. row, column, subGrid) that has a candidate not found elsewhere
    (a hidden single). If this is found, all other candidates are removed
    from this location.

    Note that a hidden single when found is NOT set, and so must be placed
    by another solving method such as naked single. This is because this
    implementation uses a generic hidden n algorithm, and so only removes
    candidates.
    '''

    def __init__(self):
        self.name = "Hidden Single"
        self.minSize = None
        self.maxSize = None
        self.rank = 10

    def solve(self, puzzle):
        return super(self.__class__, self).solve(puzzle, 1)

class hiddenTwin(__hiddenN):
    '''Hidden Twin

    This plugin looks for a group of 3 locations in every intersection
    (e.g. row, column, subGrid) that share 3 candidates that are not found
    elsewhere in the intersection (a hidden triple). If one is found, all
    other candidates are removed from the group.
    '''

    def __init__(self):
        self.name = "Hidden Twin"
        self.minSize = None
        self.maxSize = None
        self.rank = 30

    def solve(self, puzzle):
        return super(self.__class__, self).solve(puzzle, 2)

class hiddenTriple(__hiddenN):
    '''Hidden Triple

    This plugin looks for a group of 3 locations in every intersection
    (e.g. row, column, subGrid) that share 3 candidates that are not found
    elsewhere in the intersection (a hidden triple). If one is found, all
    other candidates are removed from the group.
    '''

    def __init__(self):
        self.name = "Hidden Triple"
        self.minSize = 3
        self.maxSize = None
        self.rank = 70

    def solve(self, puzzle):
        return super(self.__class__, self).solve(puzzle, 3)