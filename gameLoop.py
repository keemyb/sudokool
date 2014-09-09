import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from sudoku import Sudoku
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

class screen(BoxLayout):

    def __init__(self, horizontalFormat = True, **kwargs):
        super(screen, self).__init__(**kwargs)
        
        if horizontalFormat:
            self.orientation = "horizontal"
        else:
            self.orientation = "vertical"
        self.add_widget(puzzle())
        self.add_widget(inputs())

class puzzle(GridLayout):
    
    def __init__(self, **kwargs):
        super(puzzle, self).__init__(**kwargs)  
        
        self.cols = sudoku.unitSize()
        
        for location in self.locations:
            if sudoku.isEmpty(location):
                self.add_widget(candidates(location))
            else:
                value = str(sudoku.getLocationValue(location))
                self.add_widget(Label(text = value, font_size = 40))

class candidates(GridLayout):
    
    def __init__(self, location, userCandidates = False, **kwargs):
        super(candidates, self).__init__(**kwargs)
        
        self.cols = sudoku.getSubGridsX()
        
        if userCandidates:
            if sudoku.hasUserCandidates(location):
                for candidate in sudoku.userCandidates(location):
                    self.add_widget(Label(text = str(candidate)))
        else:
            if sudoku.hasSolvingCandidates(location):
                for candidate in sudoku.solvingCandidates(location):
                    self.add_widget(Label(text = str(candidate)))           
        
class inputs(GridLayout):
    
    def __init__(self, **kwargs):
        super(inputs, self).__init__(**kwargs)  
        
        self.cols = sudoku.getSubGridsX()
        
        for value in sudoku.possibleValues():
            self.add_widget(Button(text = str(value)))

class SudokuApp(App):

    def build(self):
        return screen(False)

string9 = "003020600\
900305001\
001806400\
008102900\
700000008\
006708200\
002609500\
800203009\
005010300"
sudoku = Sudoku(string9)

# string16 = "B07805E0300AD0CG\
# 004007000C0FA002\
# A000000000043700\
# 0050009F00000008\
# 0400B8000E079300\
# 00E37C0000FDB004\
# 9F07005D03000080\
# 500D0F3024A8C0G0\
# 08000000B0000GD5\
# 00D000000800F0E0\
# 00A090F0067000BC\
# 000C0AB0000E7240\
# 7A090B1000500630\
# D0CEF070A0000800\
# 0000E0A00D005000\
# 0635G9C00B00E000"

# sudoku = Sudoku(string16)
sudoku.initialiseIntersections()

if __name__ == '__main__':
    SudokuApp().run()