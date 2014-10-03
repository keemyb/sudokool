import kivy
kivy.require('1.8.0')

from sudoku import Sudoku
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from kivy.core.window import Window

from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty

class Input(Button):
    pass

class ModifiedCell(Label):
    pass

class ConstantCell(Label):
    pass

class EmptyCell(GridLayout):
    pass

class Candidate(Label):
    pass

class GameScreen(Screen):
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
        if Window.size[0] > Window.size[1]:
            cols = None
            rows = 1
        else:
            cols = 1
            rows = None
        self.ids.gameScreenGrid.cols = cols
        self.ids.gameScreenGrid.rows = rows

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

        for cell in self.ids.puzzleView.cells:
            cell.size = cellWidth, cellWidth
            cell.font_size = cellWidth*.8
            if self.sudoku.isEmpty(cell.location):
                for candidate in cell.candidates:
                    candidate.size = [candidateWidth]*2
                    candidate.font_size = candidateWidth*.8

        print "play", self.ids.puzzleView.width
        print "screen", self.ids.gameScreenGrid.width

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

    def on_sudoku(self, caller, sudoku):
        self.current = "game"
        self.initialisePuzzleView()
        self.initialiseInputGrid()
        self.on_screenSizeChange(self, Window.size)

    def initialiseInputGrid(self):
        self.ids.buttonGrid.cols = self.sudoku.subGridsInRow()
        self.ids.buttonGrid.buttons = []
        for value in self.sudoku.possibleValues():
            newInputButton = self.newInputButton(value)

            self.ids.buttonGrid.add_widget(newInputButton)
            self.ids.buttonGrid.buttons.append(newInputButton)

    def newInputButton(self, value):
        button = Input()
        button.text = str(value)
        button.value = value
        button.font_size = button.size[0]*0.8
        return button

    def initialisePuzzleView(self):
        self.ids.puzzleView.cols = self.sudoku.unitSize()
        self.ids.puzzleView.cells = []
        for location in self.sudoku.locations():
            if self.sudoku.isConstant(location):
                newCell = self.newFilledCell(location, True)
            elif self.sudoku.isModified(location):
                newCell = self.newFilledCell(location, False)
            else:
                newCell = self.newEmptyCell(location)

            newCell.location = location
            newCell.size = [self.cellWidth()]*2

            self.ids.puzzleView.add_widget(newCell)
            self.ids.puzzleView.cells.append(newCell)

    def newFilledCell(self, location, constant):
        if constant:
            cell = ConstantCell()
        else:
            cell = ModifiedCell()

        cell.font_size = self.cellWidth()*0.8

        cell.text = str(self.sudoku.getValue(location))
        # cell.size_hint = [1]*2

        return cell

    def newEmptyCell(self, location):
        cell = EmptyCell()

        cell.cols = self.sudoku.subGridsInRow()
        cell.candidates = []

        for candidate in self.sudoku.allSolvingCandidates(location):
            candidateLabel = Candidate()
            candidateLabel.size = [self.candidateWidth()]*2
            candidateLabel.text = str(candidate)
            candidateLabel.font_size = self.candidateWidth()*.8
            cell.add_widget(candidateLabel)
            cell.candidates.append(candidateLabel)
        return cell

class SudokoolApp(App):

    def build(self):
        self.game = Game(app=self)
        return self.game

if __name__ == "__main__":
    SudokoolApp().run()
