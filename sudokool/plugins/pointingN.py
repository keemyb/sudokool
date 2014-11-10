from sudokool.plugin import Plugin

class __pointingN(Plugin):

    def __init__(self):
        self.name = "Pointing N"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 0
        self.pointers = {}

    def solve(self, puzzle, n):
        self.generatePointerGroups(puzzle, n)

        successString = self.name + ": {0} has been removed from {1}, as it shares a {2} with the " + self.name + " {3}"

        for pointerGroup in self.intersectionTypes[("pointer", n)]:
            combination, pointerType = pointerGroup[0], pointerGroup[1]

            subGridNeighbours = puzzle.subGridNeighbours(combination[0], *combination)
            subGridNeighbourCandidates = puzzle.allSolvingCandidates(*subGridNeighbours)

            commonPointerCandidates = puzzle.commonSolvingCandidates(*combination)
            uniquePointerCandidates = set([candidate for candidate in commonPointerCandidates if candidate not in subGridNeighbourCandidates])

            if not uniquePointerCandidates:
                continue

            linearNeighbours = puzzle.neighbourMethods[pointerType](combination[0], *combination)

            for location in linearNeighbours:

                removedCandidates = puzzle.removeSolvingCandidates(location, *uniquePointerCandidates)

                if removedCandidates:

                    puzzle.addToLog(successString, removedCandidates, location, pointerType, combination)

    def generatePointerGroups(self, puzzle, n):
        if n in self.pointers:
            return

        pointers = []

        for subGrid in puzzle.intersectionTypes["subGrid"]:
            for combination in puzzle.nLocations(subGrid, n):

                if "row" in puzzle.alignment(*combination):
                    pointers.append((combination, "row"))
                elif "column" in puzzle.alignment(*combination):
                    pointers.append((combination, "column"))

        self.pointers[n] = pointers

    def cleanup(self, puzzle, n):
        if n not in self.pointers:
            return

        for group in self.pointers[n]:
            combination = group[0]
            for location in combination:
                if puzzle.isEmpty(location):
                    continue
                if group in puzzle.intersectionTypes[("pointer", n)]:
                    puzzle.intersectionTypes[("pointer", n)].remove(group)

class pointingPair(__pointingN):

    def __init__(self):
        self.name = "Pointing Pair"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 40
        self.pointers = {}

    def solve(self, puzzle):
        return super(pointingPair, self).solve(puzzle, 2)

    def generatePointerGroups(self, puzzle):
        return super(pointingPair, self).generatePointerGroups(puzzle, 2)

    def cleanup(self, puzzle):
        return super(pointingPair, self).cleanup(puzzle, 2)

class pointingTriplet(__pointingN):

    def __init__(self):
        self.name = "Pointing Triplet"
        self.description ='''
        pass
        '''
        self.minSize = 3
        self.maxSize = None
        self.rank = 80
        self.pointers = {}

    def solve(self, puzzle):
        return super(pointingTriplet, self).solve(puzzle, 3)

    def generatePointerGroups(self, puzzle):
        return super(pointingTriplet, self).generatePointerGroups(puzzle, 3)

    def cleanup(self, puzzle):
        return super(pointingTriplet, self).cleanup(puzzle, 3)

class pointingQuad(__pointingN):

    def __init__(self):
        self.name = "Pointing Quad"
        self.description ='''
        pass
        '''
        self.minSize = 4
        self.maxSize = None
        self.rank = 90
        self.pointers = {}

    def solve(self, puzzle):
        return super(pointingQuad, self).solve(puzzle, 4)

    def generatePointerGroups(self, puzzle):
        return super(pointingQuad, self).generatePointerGroups(puzzle, 4)

    def cleanup(self, puzzle):
        return super(pointingQuad, self).cleanup(puzzle, 4)
