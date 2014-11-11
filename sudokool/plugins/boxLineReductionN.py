from sudokool.plugin import Plugin

class __boxLineReductionN(Plugin):

    def __init__(self):
        self.name = "Box Line Reduction N"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 0
        self.pointers = []

    def solve(self, puzzle):
        self.generatePointerGroups(puzzle)

        successString = self.name + ": {0} has been removed from {1}, as it is part of a subGrid where {2} can only be placed along it's {3}"

        for pointerGroup in self.pointers:
            combination, pointerType = pointerGroup[0], pointerGroup[1]

            linearNeighbours = puzzle.neighbourMethods[pointerType](combination[0], *combination)
            linearNeighbourCandidates = puzzle.allSolvingCandidates(*linearNeighbours)

            commonPointerCandidates = puzzle.commonSolvingCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in linearNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            subGridNeighbours = puzzle.subGridNeighbours(combination[0], *combination)

            for location in subGridNeighbours:
                removedCandidates = puzzle.removeSolvingCandidates(location, *uniquePointerCandidates)

                if removedCandidates:

                    puzzle.addToLog(successString, removedCandidates, location, commonPointerCandidates, pointerType)

    def generatePointerGroups(self, puzzle, n):
        if self.pointers:
            return

        for subGrid in puzzle.intersectionTypes["subGrid"]:
            for combination in puzzle.nLocations(subGrid, n):

                if "row" in puzzle.alignment(*combination):
                    self.pointers.append((combination, "row"))
                elif "column" in puzzle.alignment(*combination):
                    self.pointers.append((combination, "column"))

    def cleanup(self, puzzle):
        if not self.pointers:
            return

        for group in self.pointers:
            combination = group[0]
            for location in combination:
                if puzzle.isEmpty(location):
                    continue
                if group in self.pointers:
                    self.pointers.remove(group)

class boxLineReductionPair(__boxLineReductionN):

    def __init__(self):
        self.name = "Box Line Reduction Pair"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 50
        self.pointers = []

    def solve(self, puzzle):
        return super(boxLineReductionPair, self).solve(puzzle)

    def generatePointerGroups(self, puzzle):
        return super(boxLineReductionPair, self).generatePointerGroups(puzzle, 2)

    def cleanup(self, puzzle):
        return super(boxLineReductionPair, self).cleanup(puzzle)

class boxLineReductionTriplet(__boxLineReductionN):

    def __init__(self):
        self.name = "Box Line Reduction Triplet"
        self.description ='''
        pass
        '''
        self.minSize = 3
        self.maxSize = None
        self.rank = 100
        self.pointers = []

    def solve(self, puzzle):
        return super(boxLineReductionTriplet, self).solve(puzzle)

    def generatePointerGroups(self, puzzle):
        return super(boxLineReductionTriplet, self).generatePointerGroups(puzzle, 3)

    def cleanup(self, puzzle):
        return super(boxLineReductionTriplet, self).cleanup(puzzle)

class boxLineReductionQuad(__boxLineReductionN):

    def __init__(self):
        self.name = "Box Line Reduction Quad"
        self.description ='''
        pass
        '''
        self.minSize = 4
        self.maxSize = None
        self.rank = 110
        self.pointers = []

    def solve(self, puzzle):
        return super(boxLineReductionQuad, self).solve(puzzle)

    def generatePointerGroups(self, puzzle):
        return super(boxLineReductionQuad, self).generatePointerGroups(puzzle, 4)

    def cleanup(self, puzzle):
        return super(boxLineReductionQuad, self).cleanup(puzzle)
