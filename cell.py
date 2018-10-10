#import board
#import math
# h=3 w=9
# 01  2  3  4  5  6  7  8  9 
# 1         ->
# 2
# 3
# 4  |
# 5  V
# 6
# 7
# 8
# 9
# Cell Ref = col, line (c,l) from top left like the terminal coordinate.
# point 0 is outside the grid, and will be the origin, it is based on the center of the terminal
#     0.x = termcenter.x - 45
#     0.y = termcenter.y -19

# each cell will need to have a local origin, based on 0.x and 0.y, and (c,l)
# this local point is the top left cross of each cells, this will be used to draw cells and edit them
# 0(1,1) = 0.x+0*10 , 0.y + 0*4
# 0(1,2) = 0.x+1*10
# 0(2,1) =         , 0.y + 1*4

# usable surface of cell is 3*9, the step to compute each local origin add one for the borders
# 0(c,l) = 0.x+(c-1)*10 , 0.y+(L-1)*4

class Cell(object):
    def __init__(self, line, column, origin, value=0):
        self.line = line
        self.column = column
        self.value = value
        self.hints = [0,0,0,0,0,0,0,0,0]
        self.origin = origin
        self.is_active=False  #currently selected cell
        self.is_neihgboor=False #is in the LOS of the active cell (line/col/square)        
        self.is_static=False #if was setup by the game, different color, non editable
        self.is_invalid=False

    def get_local_origin(self):
        (lin_o, col_o) = self.origin
        c = col_o + (self.column - 1) * 10
        l = lin_o + (self.line - 1) * 4        
        return l, c

    def hints_count(self):
        count=0
        for hint in self.hints:
            if hint != 0 : count +=1
        return count

    def set_active(self):
        self.is_active=True

    def set_inactive(self):
        #useless as all is done in board, I thought classes where... classes. meh
        self.is_active=False
    
    def clear_cell(self):
        self.value=0
        self.hints = [0,0,0,0,0,0,0,0,0]
        self.is_active=False
        self.is_neihgboor=False
        self.is_static=False
        self.is_invalid=False

    def __str__(self):
        line=str(self.line) + "," + str(self.column)+":"+str(self.is_active)
        return line






empty_template=[
    "         ",
    "         ",
    "         "
]
