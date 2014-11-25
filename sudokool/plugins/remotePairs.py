from sudokool.plugin import Plugin

class remotePairs(Plugin):
    '''Remote Pairs

    This plugin looks for a chain of locked pairs that are linked
    together remotely. (A locked pair is a set of two locations in
    the same row, column or subGrid, that have two identical
    candidates).

    The intersection of these ends is then checked to see if it
    contains one candidate in the locked pair. If this is the case
    then that candidate is removed.

    Only chains of an even length need to be analysed. If a candidate
    is the right value for a cell, then the next cell in the chain
    cannot contain that value, and this pattern alternates.
    So it follows that the two ends of the chain will have different
    values.
    '''

    def __init__(self):
        self.name = "Remote Pairs"
        self.minSize = None
        self.maxSize = None
        self.rank = 170
        self.lockedChains = []
        self.lockedPairs = []

    def solve(self, puzzle):

        self.generateLockedChains(puzzle)

        successString = "Remote Pair: {0} has been removed from {1}, as it can be seen by the remote pair {2}, part of the locked chain {3}"

        for lockedChainGroup in self.lockedChains:
            lockedChain, candidates = lockedChainGroup[0], lockedChainGroup[1]

            remotePairs = []
            steps = xrange(3, len(lockedChain), 2)
            for step in steps:
                for i in xrange(len(lockedChain) - step):
                    remotePairs.append((lockedChain[i], lockedChain[i+step]))

            for remotePair in remotePairs:
                locationOne, locationTwo = remotePair[0], remotePair[1]

                locationOneNeighbours = puzzle.combinedNeighbours(locationOne, *lockedChain)
                locationTwoNeighbours = puzzle.combinedNeighbours(locationTwo, *lockedChain)
                remotePairNeighbours = (set(locationOneNeighbours) &
                                        set(locationTwoNeighbours))

                for neighbour in remotePairNeighbours:

                    removedCandidates = puzzle.removeSolvingCandidates(neighbour, *candidates)

                    if removedCandidates:

                        puzzle.addToLog(successString, removedCandidates, neighbour, remotePair, lockedChain)

    def cleanup(self, puzzle):
        self.cleanupLockedPairs(puzzle)
        self.cleanupLockedChains(puzzle)

    def cleanupLockedPairs(self, puzzle):
        if not self.lockedPairs:
            return

        for group in self.lockedPairs:
            pair = group[0]

            if all(puzzle.isEmpty(location) for location in pair):
                continue
            if group in self.lockedPairs:
                self.lockedPairs.remove(group)
                break

    def cleanupLockedChains(self, puzzle):
        if not self.lockedChains:
            return

        for chainGroup in self.lockedChains:
            if not self.validLockedChain(puzzle, chainGroup):
                if chainGroup in self.lockedChains:
                    self.lockedChains.remove(chainGroup)

    def validLockedChain(self, puzzle, chainGroup):
        if chainGroup not in self.lockedChains:
            return False

        chain, candidates = chainGroup[0], chainGroup[1]

        for location in chain:
            if not puzzle.isEmpty(location):
                return False
            if candidates != puzzle.allSolvingCandidates(location):
                return False
        return True

    def generateLockedPairs(self, puzzle):

        if self.lockedPairs:
            return

        for pair in puzzle.nLocations(puzzle.emptyLocations(), 2):
            alignment = puzzle.alignment(*pair)
            if not alignment:
                continue

            locationOneCandidates = puzzle.allSolvingCandidates(pair[0])
            if len(locationOneCandidates) != 2:
                continue

            locationTwoCandidates = puzzle.allSolvingCandidates(pair[1])
            if locationTwoCandidates != locationOneCandidates:
                continue

            lockedPair = (sorted(pair), locationOneCandidates)

            if lockedPair in self.lockedPairs:
                continue

            self.lockedPairs.append(lockedPair)

    def generateLockedChains(self, puzzle):

        if self.lockedChains:
            return

        self.generateLockedPairs(puzzle)

        for pairGroup in self.lockedPairs:

            pair, candidates = pairGroup[0], pairGroup[1]
            chain = pair[:]

            lastChain = None
            while lastChain != chain:

                firstLink, lastLink = chain[0], chain[-1]
                lastChain = chain[:]

                for prospectivePairGroup in self.lockedPairs:

                    prospectivePair = prospectivePairGroup[0]
                    prospectiveCandidates = prospectivePairGroup[1]

                    if prospectiveCandidates != candidates:
                        continue

                    if all(location in chain for location in prospectivePair):
                        continue

                    if any(location == firstLink for location in prospectivePair):
                        if prospectivePair[0] in chain:
                            chain.insert(0, prospectivePair[1])
                            break
                        else:
                            chain.insert(0, prospectivePair[0])
                            break

                    if any(location == lastLink for location in prospectivePair):
                        if prospectivePair[0] in chain:
                            chain.append(prospectivePair[1])
                            break
                        else:
                            chain.append(prospectivePair[0])
                            break

            if len(chain) < 3:
                continue

            chainIsASubset = False
            for existingChainGroup in self.lockedChains[:]:
                existingChain = existingChainGroup[0]
                existingChainCandidates = existingChainGroup[1]

                if existingChainCandidates != candidates:
                    continue

                # if all locations in the current chain already exist in another,
                # it is a subset and will not be added. We break here as the
                # larger chain does not need to be purged.
                if all(location in existingChain for location in chain):
                    chainIsASubset = True
                    break

                # if all locations in the existing chain exist in the current chain,
                # the existing chain will be removed.
                if all(location in chain for location in existingChain):
                    if existingChainGroup in self.lockedChains:
                        self.lockedChains.remove(existingChainGroup)

            if not chainIsASubset:
                self.lockedChains.append((chain, candidates))
