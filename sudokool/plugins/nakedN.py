from sudokool.plugin import Plugin

class __nakedN(Plugin):
    '''Naked N

    This plugin looks for n cells in every intersection that have n, and only n
    candidates in common. If these are found, these n candidates are removed
    from every other location in the intersection.
    '''

    def __init__(self):
        self.name = "Naked N"
        self.minSize = None
        self.maxSize = None
        self.rank = 0

    def solve(self, puzzle, n):

        successString = self.name + ": {0} have been removed from {1} as it shares a {2} with the " + self.name + ", {3}"

        for intersectionType in puzzle.units:

            for group in puzzle.intersectionTypes[intersectionType]:

                # If the number of locations in a group is not greater than n,
                # there is nothing to look for.
                if len(group) <= n:
                    continue

                for combination in puzzle.nLocations(group, n):

                    # Trying every n sized group combination to see if they have
                    # n candidates in common (which means they will have the
                    # same candidates).
                    nakedNcandidates = puzzle.allSolvingCandidates(*combination)

                    if len(nakedNcandidates) != n:
                        continue

                    surroundingLocations = [location for location in group if location not in combination]

                    for surroundingLocation in surroundingLocations:

                        # Removing every candidate from the surrounding
                        # locations that could be found in the naked n group.
                        removedCandidates = puzzle.removeSolvingCandidates(surroundingLocation, *nakedNcandidates)

                        if removedCandidates:

                            puzzle.addToLog(successString, removedCandidates, location, puzzle.alignment(*combination)[0], combination)

class nakedTwin(__nakedN):
    '''Naked Twin

    This plugin looks for 2 cells in every intersection that have 2, and only 2
    candidates in common. If these are found, these 2 candidates are removed
    from every other location in the intersection.
    '''

    def __init__(self):
        self.name = "Naked Twin"
        self.minSize = None
        self.maxSize = None
        self.rank = 20

    def solve(self, puzzle):
        return super(nakedTwin, self).solve(puzzle, 2)

class nakedTriple(__nakedN):
    '''Naked Triple

    This plugin looks for 3 cells in every intersection that have 3, and only 3
    candidates in common. If these are found, these 3 candidates are removed
    from every other location in the intersection.
    '''

    def __init__(self):
        self.name = "Naked Triple"
        self.minSize = 3
        self.maxSize = None
        self.rank = 60

    def solve(self, puzzle):
        return super(nakedTriple, self).solve(puzzle, 3)
