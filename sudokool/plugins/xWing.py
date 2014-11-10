from sudokool.plugin import Plugin

class xWing(Plugin):

    def __init__(self):
        self.name = "X-Wing"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 12
        self.xWingGroups = []

    def solve(self, puzzle):
        self.generateXWingGroups(puzzle)

        successString = "X-Wing: {0} has been removed from {1}, as it is in alignment with the X-Wing, {2}"

        from collections import defaultdict

        xWings = defaultdict(list)

        for group in self.xWingGroups:

            commonXWingCandidates = puzzle.commonSolvingCandidates(*group)

            if len(commonXWingCandidates) == 0:
                continue

            rowCandidates = (puzzle.allSolvingCandidates(*puzzle.rowNeighbours(group[0], *group)) |
                             puzzle.allSolvingCandidates(*puzzle.rowNeighbours(group[2], *group)))
            columnCandidates = (puzzle.allSolvingCandidates(*puzzle.columnNeighbours(group[0], *group)) |
                                puzzle.allSolvingCandidates(*puzzle.columnNeighbours(group[1], *group)))

            for candidate in commonXWingCandidates:
                if (candidate not in rowCandidates or candidate not in columnCandidates):
                    xWings[group].append(candidate)

        for group, candidates in xWings.iteritems():

            for location in self.xWingNeighbours(puzzle, group):

                removedCandidates = puzzle.removeSolvingCandidates(location, *candidates)

                if removedCandidates:

                    # Needs to be more verbose, showing where the alignment occours
                    puzzle.addToLog(successString, removedCandidates, location, group)

    def generateXWingGroups(self, puzzle):
        if self.xWingGroups:
            return

        # gridSize: gridSize * 2 are the indices for the row groups
        # we use the indices from intersection groups instead of row groups,
        # as the row groups in intersection groups will be pre-pruned.
        for firstRowIndex, firstRow in enumerate(puzzle.intersectionTypes["row"]):
            if len(firstRow) < 2:
                continue

            for firstRowGroup in puzzle.nLocations(firstRow, 2):

                    for secondRow in puzzle.intersectionTypes["row"][firstRowIndex + 1:]:
                        if len(secondRow) < 2:
                            continue

                        for secondRowGroup in puzzle.nLocations(secondRow, 2):
                                if "subGrid" in puzzle.alignment(firstRowGroup[0], secondRowGroup[1]):
                                    continue

                                if "column" in puzzle.alignment(firstRowGroup[0], secondRowGroup[0]) and \
                                   "column" in puzzle.alignment(firstRowGroup[1], secondRowGroup[1]):
                                    self.xWingGroups.append((firstRowGroup + secondRowGroup))

    def cleanup(self, puzzle):
        if not self.xWingGroups:
            return

        for group in self.xWingGroups:
            for location in group:
                if puzzle.isEmpty(location):
                    continue
                if location not in group:
                    continue
                if group in self.xWingGroups:
                    self.xWingGroups.remove(group)

    def xWingNeighbours(self, puzzle, xWing):
        return (puzzle.rowNeighbours(xWing[0], *xWing) +
                puzzle.rowNeighbours(xWing[2], *xWing) +
                puzzle.columnNeighbours(xWing[0], *xWing) +
                puzzle.columnNeighbours(xWing[1], *xWing))
