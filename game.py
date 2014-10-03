import kivy
kivy.require('1.8.0')

from sudoku import Sudoku
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from kivy.core.window import Window

from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty

superWhite = .92, .97, 1, 1
offWhite = .85, .90, .93, 1
red = .84, .29, .34, 1
blue = .69, .78, .85, 1
green = .67, .75, .57, 1
brown = .87, .67, .49, 1

class toggleValueOrCandidateChange(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(toggleValueOrCandidateChange, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.states = {True: "Values",
                       False: "Candidates"}

        self.text = self.states[self.MainSwitcher.changeValues]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.changeValues = not self.MainSwitcher.changeValues
            self.text = self.states[self.MainSwitcher.changeValues]
            return True

class Input(Button):
    def __init__(self, MainSwitcher, **kwargs):
        super(Input, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.setValue(self.value)

            return True

class ModifiedCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ModifiedCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

class ConstantCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ConstantCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

class EmptyCell(GridLayout):
    def __init__(self, MainSwitcher, **kwargs):
        super(EmptyCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

class Candidate(Label):
    pass

class GameScreen(Screen):
    pass

class SelectScreen(Screen):
    pass

class Game(ScreenManager):
    app = ObjectProperty(None)
    sudoku = ObjectProperty(None)
    selected = NumericProperty(-1)
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
        self.bind(selected=self.on_selected)
        self.bind(highlightOccourences=self.on_highlightOccourences)
        # self.bind(changeValues=self.on_changeValues)
        # self.bind(displaySolvingCandidates=self.on_displaySolvingCandidates)
        # self.bind(solveMode=self.on_solveMode)
        # self.bind(autoUpdateUserCandidates=self.on_autoUpdateUserCandidates)
        # self.bind(highlightClashes=self.on_highlightClashes)

    def updateCells(self, locations=None):
        if locations is None:
            self.ids.puzzleView.clear_widgets()
            self.initialisePuzzleView()

    def on_screenSizeChange(self, caller, size):
        self.resizeCells()
        self.gameScreenGridOrient()
        if not self.solveMode:
            self.resizePlayModeGrid()

    def on_selected(self, caller, selected):
        self.on_highlightOccourences(caller, self.on_highlightOccourences)

    def on_highlightOccourences(self, caller, value):
        for cell in self.ids.puzzleView.cells:
            if self.sudoku.isFilled(cell.location):
                cell.color = superWhite
            else:
                for candidate in cell.candidates:
                    candidate.color = superWhite

        if self.highlightOccourences and self.sudoku.isFilled(self.selected):
            for cell in self.ids.puzzleView.cells:
                if self.sudoku.isFilled(cell.location):
                    if (cell.value == self.sudoku.getValue(self.selected) and
                            cell.location != self.selected):
                        cell.color = blue
                else:
                    for candidate in cell.candidates:
                        if candidate.value == self.sudoku.getValue(self.selected):
                            candidate.color = blue

    def setValue(self, value):
        if self.selected < 1:
            return
        elif self.sudoku.isConstant(self.selected):
            return
        else:
            if self.changeValues:
                self.sudoku.setValue(self.selected, value)
            else:
                self.sudoku.toggleUserCandidate(self.selected, value)
            self.updateCells()

    def resizePlayModeGrid(self):

        if Window.size[0] > Window.size[1]:
            size_hint_x = None
            size_hint_y = 1
            width = Window.size[0] - self.ids.puzzleView.width
            self.ids.playModeGrid.width = width
        else:
            size_hint_x = 1
            size_hint_y = None
            height = Window.size[1] - self.ids.puzzleView.height
            self.ids.playModeGrid.height = height

        self.ids.playModeGrid.size_hint = size_hint_x, size_hint_y

    def gameScreenGridOrient(self):

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

        self.ids.puzzleView.size = [cellWidth*self.sudoku.unitSize()]*2

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
        if self.autoUpdateUserCandidates:
            self.sudoku.initialiseUserCandidates()
        self.initialisePuzzleView()
        self.initialiseInputGrid()
        self.initialiseValueOrCandidateChangeButton()
        self.on_screenSizeChange(self, Window.size)

    def initialiseValueOrCandidateChangeButton(self):
        self.ids.playModeGrid.add_widget(toggleValueOrCandidateChange(self))

    def initialiseInputGrid(self):
        self.ids.buttonGrid.cols = self.sudoku.subGridsInRow()
        self.ids.buttonGrid.buttons = []
        for value in self.sudoku.possibleValues():
            newInputButton = self.newInputButton(value)

            self.ids.buttonGrid.add_widget(newInputButton)
            self.ids.buttonGrid.buttons.append(newInputButton)

    def newInputButton(self, value):
        button = Input(self)
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
            cell = ConstantCell(self)
        else:
            cell = ModifiedCell(self)

        cell.font_size = self.cellWidth()*0.8

        cell.value = self.sudoku.getValue(location)
        cell.text = str(cell.value)

        return cell

    def newEmptyCell(self, location):
        cell = EmptyCell(self)

        cell.cols = self.sudoku.subGridsInRow()
        cell.candidates = []

        if self.solveMode:
            for candidate in self.sudoku.allSolvingCandidates(location):
                candidateLabel = self.newCandidateLabel(candidate)

                cell.add_widget(candidateLabel)
                cell.candidates.append(candidateLabel)
        else:
            for candidate in self.sudoku.userCandidates(location):
                candidateLabel = self.newCandidateLabel(candidate)

                cell.add_widget(candidateLabel)
                cell.candidates.append(candidateLabel)


        return cell

    def newCandidateLabel(self, candidate):
        candidateLabel = Candidate()
        candidateLabel.text = str(candidate)
        candidateLabel.value = candidate

        candidateLabel.size = [self.candidateWidth()]*2
        candidateLabel.font_size = self.candidateWidth()*.8

        return candidateLabel

class SudokoolApp(App):

    def build(self):
        self.game = Game()
        return self.game

if __name__ == "__main__":
    SudokoolApp().run()
