import kivy
kivy.require('1.8.0')

from sudoku import Sudoku
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.core.window import Window

from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty

class ModifiedCell(BoxLayout):
    pass

class EmptyCell(GridLayout):
    pass

class ConstantCell(BoxLayout):
    pass

class Candidate(Label):
    pass

class PlayScreen(Screen):
    pass

class SelectScreen(Screen):
    pass

class Game(ScreenManager):
    app = ObjectProperty(None)
    sudoku = ObjectProperty(None)
    selected = NumericProperty(0)
    changeValues = BooleanProperty(True)
    displaySolvingCandidates = BooleanProperty(False)
    solveMode = BooleanProperty(False)
    autoUpdateUserCandidates = BooleanProperty(True)
    highlightOccourences = BooleanProperty(True)
    highlightClashes = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.current = "select"
        Window.bind(size=self.on_screenSizeChange)
        self.bind(sudoku=self.on_sudoku)
        # self.bind(changeValues=self.on_changeValues)
        # self.bind(displaySolvingCandidates=self.on_displaySolvingCandidates)
        # self.bind(solveMode=self.on_solveMode)
        # self.bind(autoUpdateUserCandidates=self.on_autoUpdateUserCandidates)
        # self.bind(highlightOccourences=self.on_highlightOccourences)
        # self.bind(highlightClashes=self.on_highlightClashes)

    def on_screenSizeChange(self, caller, size):
        self.resizeCells()

    def newSudoku(self, size):
        # sudoku = Sudoku(size=size)
        sudoku = Sudoku("009003201470002030800000074020000300000000710000794000000300000000925000000018500")
        sudoku.initialiseCandidates()
        return sudoku

    def resizeCells(self):
        if self.sudoku is None:
            return

        cellWidth = self.cellWidth()
        candidateWidth = self.candidateWidth()

        for cell in self.ids.playGrid.cells:
            cell.size = cellWidth, cellWidth
            cell.text_size = [cellWidth*.8]*2
            if self.sudoku.isEmpty(cell.location):
                for candidate in cell.candidates:
                    candidate.size = [candidateWidth]*2
                    candidate.text_size = [candidateWidth*.8]*2

    def cellWidth(self):
        windowWidth = min(Window.size)
        cellWidth = windowWidth/float(self.sudoku.unitSize())

        return cellWidth

    def candidateWidth(self):
        cellWidth = self.cellWidth()
        candidateWidth = cellWidth/float(self.sudoku.subGridsInRow())

        return candidateWidth

    def setSudoku(self, size):
        self.sudoku = self.newSudoku(size)

    # def getSudoku(self):
    #     return self.sudoku

    def on_sudoku(self, caller, sudoku):
        self.current = "play"
        self.initialiseGrid()

    def initialiseGrid(self):
        self.ids.playGrid.cols = self.sudoku.unitSize()
        self.ids.playGrid.cells = []
        for location in self.sudoku.locations():
            if self.sudoku.isConstant(location):
                newCell = self.newFilledCell(location, True)
            elif self.sudoku.isModified(location):
                newCell = self.newFilledCell(location, False)
            else:
                newCell = self.newEmptyCell(location)

            self.ids.playGrid.add_widget(newCell)
            self.ids.playGrid.cells.append(newCell)

    def newFilledCell(self, location, constant):
        if constant:
            cell = ConstantCell()
        else:
            cell = ModifiedCell()
        cell.location = location
        cell.size = [self.cellWidth()]*2

        valueLabel = Label()
        valueLabel.text = str(self.sudoku.getValue(location))
        valueLabel.size_hint = [1]*2

        cell.add_widget(valueLabel)
        return cell

    def newEmptyCell(self, location):
        cell = EmptyCell()
        cell.location = location
        cell.size = [self.cellWidth()]*2
        cell.cols = self.sudoku.subGridsInRow()
        cell.candidates = []

        for candidate in self.sudoku.allSolvingCandidates(location):
            candidateLabel = Candidate()
            candidateLabel.size = [self.candidateWidth()]*2
            candidateLabel.text = str(candidate)
            cell.add_widget(candidateLabel)
            cell.candidates.append(candidateLabel)
        return cell

class SudokoolApp(App):

    def build(self):
        self.game = Game(app=self)
        return self.game

if __name__ == "__main__":
    SudokoolApp().run()
