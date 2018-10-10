import copy
import cell
import math
from random import shuffle

class Board():
    def __init__(self):
        self.cells=[]#[[cell.Cell]*10]*10
        self.history=[]
        self.snapshot=0
        self.moves=0
        self.center_line = 0
        self.center_col = 0
        self.active_cell=None
        self.tracking_disabled=False

        for l in range(0,10):
            row=[]
            for c in range(0,10):
                row.append(cell.Cell(l, c, self.get_origin(), 0))
            self.cells.append(row)

        self.set_active_cell(5,5)

    def __str__(self):
        #unused, for debugging purpose
        result=""
        for l in range(1,10):
            line=""
            for c in range(1,10):
                line+= str(l)+","+str(c)+":" + str(self.cells[l][c].value) 
                if self.cells[l][c].is_active : line+="*"
                line+="\t"
            result+=line+"\n"
        result += str(self.active_cell.line) + " " + str(self.active_cell.column) +   "\n"
        return result   

    def set_center_coord(self,l,c):
        #renderer give this info to Board, board compute its size and gives
        #origin for all the cells
        #ideally to be used for resizing, when I understand curses
        self.center_line=l
        self.center_col=c
        for j in range (1,10):
            for i in range (1,10):
                x=1 + self.get_origin()[1] #offset from top
                y=1 + self.get_origin()[0] #offset from top
                self.cells[j][i].origin = (y,x)

    def set_active_cell(self,l,c):
        #define the selected cell on screen, compute the visible cell and flag them
        #the renderer will use this to display colors
        self.cells[l][c].set_active()
        self.active_cell=self.cells[l][c]
        for j in range (1,10):
            for i in range (1,10):
                if not(l==j and c==i):
                    self.cells[j][i].set_inactive()
        self.set_cell_neighboor(l,c)

    def set_cell_neighboor(self,l,c):
        #flag the visible cells from the active cell
        for j in range (1,10):
            for i in range (1,10):
                if l==j and c==i:
                    self.cells[j][i].is_neihgboor =False
                    continue
                if l==j or c==i :
                    self.cells[j][i].is_neihgboor =True
                else:
                    self.cells[j][i].is_neihgboor=False

    def get_origin(self):
        #meh, numbers are static, but will do for now
        l=self.center_line - 21
        c=self.center_col - 47
        return l, c

    def undo(self):
        # roll back the board to a previous version, track the depth so 
        # redo can go back
        if self.snapshot==0:
            self.history.append(copy.deepcopy(self.cells))
            self.snapshot=1
        if len(self.history)>self.snapshot :
            self.snapshot+=1
            self.cells=copy.deepcopy( self.history[-self.snapshot] )

    def redo(self):
        # roll over the history up to current version
        if self.snapshot > 1:
            self.snapshot-=1
            self.cells=copy.deepcopy(self.history[-self.snapshot])

    def track_history(self) :
        # create a copy of the current board cells
        # this should be called on each modification
        # as soon a modification is made, if some undo were made "redo" is dropped
        # and no roll back to that branch is possible.
        # it's standard undo behaviour, commenting the "Del" command will change 
        # that to a strange but interresting undo behaviour
        # Consume memory and is backed up by the save function
        if self.tracking_disabled : return
        if self.snapshot!=0:
            del self.history[:-self.snapshot]
        self.snapshot=0
        self.history.append(copy.deepcopy(self.cells))

    def input_cell_value(self, l, c, value):
        #ensure a cell coherence when inputing data
        self.track_history()
        self.cells[l][c].value=value
        self.cells[l][c].hints=[0]*9
        self.validate_board()
        
    def input_hint_value(self, l, c, value):
        #ensure a cell coherence when inputing data
        self.track_history()
        self.cells[l][c].hints[value-1] = abs(self.cells[l][c].hints[value-1] -1 )

    def validate_board(self):
        #will check the validity of every cell, marking invalid one
        for l in range(1,10):
            for c in range(1,10):
                self.validate_cell(l, c)

    def validate_cell(self, l,c):
        # for every non static cell, check value against visible
        # if the cell is not valid = a value already is present
        # this will set the cell, and only this one, invalid.
        if self.cells[l][c].is_static : 
            self.cells[l][c].is_invalid=False
            return
        list=self.get_cell_neighboors((l,c))
        val=self.cells[l][c].value
        test=False
        for pos in list:
            if pos==(l,c) : continue
            if val == self.cells[pos[0]][pos[1]].value :
                test=True
                break
        self.cells[l][c].is_invalid=test
   
    def get_row_tuples(self, pos):
        #get list of coord tuple (line, column) of the row for a cell passed in 'pos' 
        #pos is also a tuple (line, column)
        list=[]
        for i in range (1,10):
            list.append((pos[0],i))
        return list
    
    def get_col_tuples(self, pos):
        #get list of coord tuple (line, column) of the column for a cell passed in 'pos' 
        #pos is also a tuple (line, column)
        list=[]
        for i in range (1,10):
            list.append((i,pos[1]))
        return list

    def get_square_tuples(self, pos):
        #get list of coord tuple (line, column) of the square (or box) of a cell passed in 'pos' 
        #pos is also a tuple (line, column)
        list=[]
        l=3* math.ceil(pos[0]/3)-3
        c=3* math.ceil(pos[1]/3)-3
        for i in range (1,4):
            for j in  range (1,4):
                list.append((l+i,c+j))
        return list

    def get_cell_neighboors(self, pos):
        #combine the 27 set of coordinate associated to the cell coordinate 
        # tuple "pos"
        list=[]
        list.extend(self.get_row_tuples(pos))
        list.extend(self.get_col_tuples(pos))
        list.extend(self.get_square_tuples(pos))
        return list

    
    def clear_board(self):
        #wipe the board clean
        for l in range(1,10):
            for c in range(1,10):
                self.input_cell_value(l,c,0)
                self.cells[l][c].clear_cell()
                #self.input_hint_value(l,c,0)
        del self.history[0:]
        self.snapshot=0

    def convert_static(self):
        for l in range(1,10):
            for c in range(1,10):
                if self.cells[l][c].value!=0:
                    self.cells[l][c].is_static=True
                else:self.input_cell_value(l,c,0)

    def convert_non_static(self):
        for l in range(1,10):
            for c in range(1,10):
                self.cells[l][c].is_static=False
                
   
    def find_all_hints(self):
        for l in range(1,10):
            for c in range(1,10):
                if self.cells[l][c].value==0:
                    self.find_cell_hints(l,c)
    
    def find_cell_hints(self, l, c):
        list=self.get_cell_neighboors((l,c))
        hints = [1,2,3,4,5,6,7,8,9]
        for pos in list:
            #if l==pos[0] and c==pos[1]:continue
            if self.cells[pos[0]][pos[1]].value == 0 : continue
            try:
                hints.remove(self.cells[pos[0]][pos[1]].value)
            except ValueError as err:
                pass
            if hints == []:break
        self.cells[l][c].hints=[0]*9
        for hint in hints:
            self.cells[l][c].hints[hint-1]=1

    def parse_naked_singles(self):        
        has_modified=False
        for l in range(1,10):
            for c in range(1,10):
                if self.cells[l][c].hints_count()==1:
                    has_modified=True
                    self.input_cell_value(l,c,self.cells[l][c].hints.index(1)+1)
        return has_modified

    def parse_double_pairs(self):
        has_modified=False
        for l in range(1,10):
            for c in range(1,10):
                list=self.get_col_tuples((l,c))
                has_modified |=  self.parse_double_pair(l,c,list)
                list=self.get_row_tuples((l,c))
                has_modified |=  self.parse_double_pair(l,c,list)
                list=self.get_square_tuples((l,c))
                has_modified |=  self.parse_double_pair(l,c,list)
        return has_modified
        
    def parse_double_pair(self,l, c, list):
        has_modified = False
        if self.cells[l][c].hints_count()==2:
            match=(0,0)
            for pos in list :
                if pos==(l,c):continue
                if self.cells[l][c].hints == self.cells[pos[0]][pos[1]].hints :
                    match=pos
                    break
            if match!=(0,0):
                hints=self.cells[l][c].hints
                for pos in list :
                    if pos==(l,c):continue
                    if pos==match:continue
                    for i in range(0,9):
                        if hints[i]==1:
                            self.cells[pos[0]][pos[1]].hints[i]=0
                            has_modified = True
        return has_modified
    
    def parse_hidden_singles(self):
        has_modified=False
        for l in range(1,10):
            for c in range(1,10):
                if self.cells[l][c].value!=0:continue
                list=self.get_col_tuples((l,c))
                has_modified |= self.parse_hidden_single(l,c,list)
                if self.cells[l][c].value!=0:continue
                list=self.get_row_tuples((l,c))
                has_modified |= self.parse_hidden_single(l,c,list)
                if self.cells[l][c].value!=0:continue
                list=self.get_square_tuples((l,c))
                has_modified |= self.parse_hidden_single(l,c,list)
        return has_modified

    def parse_hidden_single(self,l, c, list):
        hints=[0]*9
        has_modified=False
        self.find_all_hints()
        for pos in list:
            for i in range(0,9):
                if self.cells[pos[0]][pos[1]].hints[i]>0:
                    hints[i]+=1
        result=-1
        try:
            result = hints.index(1)
        except :
            pass
        if result >= 0 and self.cells[l][c].hints[result]==1: 
            self.input_cell_value(l,c,result+1)
            has_modified=True
        return has_modified

    def parse_pointing_pairs(self):
        for box_l in range(0,3):
            for box_c in range(0,3):
                self.parse_pp_box(box_l*3+1, box_c*3+1)
    
    def parse_pp_box(self, bl, bc):
        has_modified = False
        #counting hints in the box
        box_hints=[0]*9
        for l in range(0,3):
            for c in range(0,3):
                for h in range(0,9):
                    box_hints[h]+=self.cells[l+bl][c+bc].hints[h]
    
        for l in range(bl, bl+3):
            #counting hint on a mini row
            mini_hints=[0]*9
            for c in range(bc,bc+3):
                for h in range(0,9):mini_hints[h]+=self.cells[l][c].hints[h]
                #[i for i, x in enumerate(hints) if x >= 1 or x <= 3]

            #counting hints for the rest of the row, excluding mini row
            row_hints=[0]*9
            for c in range(1,bc):
                for h in range(0,9):row_hints[h]+=self.cells[l][c].hints[h]
            for c in range(bc+3,10):
                for h in range(0,9):row_hints[h]+=self.cells[l][c].hints[h]

            # if box count = mini row count, then row must not have hints
            # if row count == 0 then all the other 6 cells in the box must not have hints
            for h in range(0,9):
                if box_hints[h]==0:continue
                if box_hints[h] == mini_hints[h]:
                    for c in range(1,bc):
                        if self.cells[l][c].hints[h]!=0:
                            has_modified=True
                            self.cells[l][c].hints[h]=0
                            row_hints[h]-=1
                    for c in range(bc+3,10):
                        if self.cells[l][c].hints[h]!=0:
                            has_modified=True
                            self.cells[l][c].hints[h]=0
                            row_hints[h]-=1
                
                if row_hints[h]==0 and box_hints[h] != mini_hints[h] and mini_hints[h] !=0: 
                    for i in range(bl, bl+3):
                        if i==l : continue #skip current row
                        for c in range(bc,bc+3):
                            if self.cells[i][c].hints[h]!=0:
                                self.cells[i][c].hints[h]=0
                                has_modified=True
                                box_hints[h] -=1
        
        ## now the same for mini columns
        box_hints=[0]*9
        for l in range(0,3):
            for c in range(0,3):
                for h in range(0,9):
                    box_hints[h]+=self.cells[l+bl][c+bc].hints[h]
        for c in range(bc, bc+3):
            #counting hint on a mini row
            mini_hints=[0]*9
            for l in range(bl,bl+3):
                for h in range(0,9):mini_hints[h]+=self.cells[l][c].hints[h]
                #[i for i, x in enumerate(hints) if x >= 1 or x <= 3]

            #counting hints for the rest of the row, excluding mini row
            col_hints=[0]*9
            for l in range(1,bl):
                for h in range(0,9):col_hints[h]+=self.cells[l][c].hints[h]
            for l in range(bl+3,10):
                for h in range(0,9):col_hints[h]+=self.cells[l][c].hints[h]

            # if box count = mini row count, then row must not have hints
            # if row count == 0 then all the other 6 cells in the box must not have hints
            for h in range(0,9):
                if box_hints[h]==0:continue
                if box_hints[h] == mini_hints[h]:
                    for l in range(1,bl):
                        if self.cells[l][c].hints[h]!=0:
                            has_modified=True
                            self.cells[l][c].hints[h]=0
                            row_hints[h]-=1
                    for l in range(bl+3,10):
                        if self.cells[l][c].hints[h]!=0:
                            has_modified=True
                            self.cells[l][c].hints[h]=0
                            row_hints[h]-=1
                
                if col_hints[h]==0 and box_hints[h]!=mini_hints[h]  and mini_hints[h] !=0:                    
                    for i in range(bl, bl+3):
                        if i==c : continue #skip current row
                        for l in range(bl,bl+3):
                            if self.cells[l][c].hints[h]!=0:
                                self.cells[l][c].hints[h]=0
                                box_hints[h] -=1
                                has_modified=True
        
        return has_modified
                
    def fill(self):
        self.tracking_disabled=True
        grid=[]
        for i in range(0,9):
            row=[0]*9
            for j in range(0,9):
                row[j]=j+1
            shuffle(row)
            grid.append(row)
        
        self.clear_board()

        for l in range(1,10):
            c=1
            fail=0
            while c < 10  and fail <100 :#sanity check
            
                self.input_cell_value(l,c,grid[l-1][0])
                if self.cells[l][c].is_invalid :                    
                    i=0
                    
                    while self.cells[l][c].is_invalid and i<len(grid[l-1]):
                        self.input_cell_value(l,c,grid[l-1][i])
                        i+=1                    
                    if not(self.cells[l][c].is_invalid): #yay
                        grid[l-1].pop(i-1)

                    else: #oh no!
                        row=[]
                        for i in grid[l-1]:
                            row.append(i)
                        for i in range(1, 10 - len(row)) :
                            row.append(self.cells[l][i].value)
                        for i in range(1, 10) :
                            self.input_cell_value(l,i,0)
                            self.cells[l][i].is_invalid=False

                        shuffle(row)

                        grid[l-1] = row
                        c=0
                        fail+= 1
                else:
                    grid[l-1].pop(0)
            
                c=c+1
        self.tracking_disabled=False
        return grid==[[],[],[],[],[],[],[],[],[]]
    
    def solve(self) :
        self.tracking_disabled=True
        self.find_all_hints()
        i=0
        while i<3:
            modify=True
            limit=0
            while modify and limit<5:
                modify |= self.parse_naked_singles()
                modify |= self.parse_double_pairs()
                modify |= self.parse_hidden_singles()
                limit+=1
            self.parse_pointing_pairs()
            self.parse_double_pairs()
            #self.parse_hidden_singles()
            i=i+1
        self.tracking_disabled=False

    def is_board_solved(self):
        solved=False
        for l in range(1,10):
            for c in range(1,10):
                solved=(self.cells[l][c].value!=0)and not(self.cells[l][c].is_invalid)
                if not(solved):return solved
        return solved

    def make_puzzle1(self):
        row=[1,2,3,4,5,6,7,8,9]
        col=[1,2,3,4,5,6,7,8,9]

        shuffle(row)
        shuffle(col)

        for i in range(0,9):
            self.input_cell_value(row[i],col[i],0)
        self.solve()

        if self.is_board_solved() : 
            self.undo()
            self.make_puzzle1()
        else:
            self.undo()
            notok=True
            while notok:                
                self.undo()
                self.solve()
                if self.is_board_solved():
                    notok=False
                else:
                    self.undo()
            self.undo()
            self.undo()

    def make_puzzle(self):
        del self.history[0:]
        self.snapshot=0
        #self.convert_static()
        self.make_puzzle1()
        del self.history[0:]
        self.snapshot=0        
        self.track_history()

        self.make_puzzle1()
        changes=0
        for l in range(1,10):
            for c in range(1,10):
                if self.history[0][l][c].value != self.cells[l][c].value:
                    changes += 1
        if changes > 0 : self.make_puzzle()
        else:
            del self.history[0:]
            self.snapshot=0
            self.convert_static()
    
    def copy_cells(self,list):
        self.cells=copy.deepcopy(list)


# static graphical information
board_lines = 38
board_col = 91
board_template=[
"      1         2         3         4         5         6         7         8         9      ",
" ╔═════════╤═════════╤═════════╦═════════╤═════════╤═════════╦═════════╤═════════╤═════════╗ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"A║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╟─────────┼─────────┼─────────╫─────────┼─────────┼─────────╫─────────┼─────────┼─────────╢ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"B║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╟─────────┼─────────┼─────────╫─────────┼─────────┼─────────╫─────────┼─────────┼─────────╢ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"C║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╠═════════╪═════════╪═════════╬═════════╪═════════╪═════════╬═════════╪═════════╪═════════╣ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"D║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╟─────────┼─────────┼─────────╫─────────┼─────────┼─────────╫─────────┼─────────┼─────────╢ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"E║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╟─────────┼─────────┼─────────╫─────────┼─────────┼─────────╫─────────┼─────────┼─────────╣ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"F║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╠═════════╪═════════╪═════════╬═════════╪═════════╪═════════╬═════════╪═════════╪═════════╣ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"G║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╟─────────┼─────────┼─────────╫─────────┼─────────┼─────────╫─────────┼─────────┼─────────╢ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"H║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╟─────────┼─────────┼─────────╫─────────┼─────────┼─────────╫─────────┼─────────┼─────────╢ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
"I║         │         │         ║         │         │         ║         │         │         ║ ",
" ║         │         │         ║         │         │         ║         │         │         ║ ",
" ╚═════════╧═════════╧═════════╩═════════╧═════════╧═════════╩═════════╧═════════╧═════════╝ ",
" ╔═════════════════════════════════════════════════════════════════════════════════════════╗ ",
" ║ Use Arrow keys to move, CTRL+arrow to skip a square. Press <Enter> to toggle input hints║ ",
" ║ PgUp: Undo  PgDown: Redo  1-9:Input number  0 or DEL: Clear the cell  F2: Save F3: Load ║ ",
" ║ <ESC>: quit--menu?                                                                      ║ ",
" ╚═════════════════════════════════════════════════════════════════════════════════════════╝ "
]

big_numbers={
1:[
"    ▄    ",
"    ▓    ",
"    ▓    "],
2  :[  
"  ▄▄▄▄▄  ",
"  ▄▄▄▄▓  ",
"  ▓▄▄▄▄  "],
3  :[  
"  ▄▄▄▄▄  ",
"  ▄▄▄▄▓  ",
"  ▄▄▄▄▓  "],
4  :[  
"  ▄   ▄  ",
"  ▓▄▄▄▓  ",
"      ▓  "],
5  :[  
"  ▄▄▄▄▄  ",
"  ▓▄▄▄▄  ",
"  ▄▄▄▄▓  "],
6  :[  
"  ▄▄▄▄▄  ",
"  ▓▄▄▄▄  ",
"  ▓▄▄▄▓  "],
7  :[  
"  ▄▄▄▄▄  ",
"      ▓  ",
"      ▓  "],
8  :[  
"  ▄▄▄▄▄  ",
"  ▓▄▄▄▓  ",
"  ▓▄▄▄▓  "],
9  :[  
"  ▄▄▄▄▄  ",
"  ▓▄▄▄▓  ",
"  ▄▄▄▄▓  "]
}