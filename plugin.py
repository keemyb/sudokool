from abc import ABCMeta, abstractmethod

class Plugin(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        '''
        Here we set the properties of our plugin.
        minSize: the minimum size of puzzle your plugin will work on
        maxSize: the maximum size of puzzle your plugin will work on
        rank: how early you plugin will be executed. The "harder" your solution is,
              the higher rank it should have. This is for two reasons, the first
              being that "easier" solving methods will be faster to execute, and
              the second is that it is better to show the easier solutions first,
              moving to harder ones if they are necessary.
        '''

        self.minSize = None
        self.maxSize = None
        self.rank = 0

    @abstractmethod
    def solve(self, puzzle):
        '''
        This is the method that will be called when it is your plugins time.
        '''

        pass

    def cleanup(self, puzzle):
        '''
        This method does not have to be implemented, but it will be called every
        time the puzzle is changed. This is to give you a chance to keep any
        data structures you use for solving up to date.
        '''

        pass
