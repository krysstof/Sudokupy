#Windows only
#TODO :add a condition if windows, else skip
#from colorama import init
#init()

import curses
from curses.textpad import Textbox, rectangle
import board
import cell

class Render():

    def __init__(self):
        self.win=curses.initscr()
        self.hint_edit=False
        self.game=None
        (y,x) = self.win.getmaxyx()
        
        if x <= 92 or y <= 40 :
            print("terminal too small, please resize up to 91x38 char")
            exit(1)
        curses.start_color()
        curses.use_default_colors()

        curses.noecho()
        curses.cbreak()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_GREEN)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_GREEN)

        self.win.keypad(True)


    def clear(self):
        self.win.clear()

    def print_at(self,text, line, col,args):
        #result = "\033[s\033[" + str(line) + ";" + str(col) + "H" + text +"\033[u"
        #result = "\033[" + str(int(line)) + ";" + str(int(col)) + "H" + text
        
        self.win.addstr(line,col,text,curses.color_pair(args))

    def get_terminal_center(self):
        global x, y
        try:
            (y,x) = self.win.getmaxyx()

        except: 
            return
        return (int(y/2),int(x/2))
    
    def draw_board(self, b):
        l,c=b.get_origin()
        for row in board.board_template :
            self.print_at(row, l, c, 1)
            l +=1

    def draw_value(self, cc, color):    
        (l,c)=cc.get_local_origin()    
        for row in board.big_numbers[cc.value]:
            self.print_at(row, l +1, c + 1,color)
            l +=1

    def clear_cell(self, cc, color):
        (l,c)=cc.get_local_origin()    
        for row in cell.empty_template:
            self.print_at(row, l +1, c + 1,color)
            l += 1

    def draw_hint(self, cc, color):
        (l,c)=cc.get_local_origin()
        i=0
        for j in range(1,4):
            row="  "
            if cc.hints[i] == 0 : row+="  "
            else: row+=str(i+1)+" "
            if cc.hints[i+1] == 0 : row+="  "
            else: row+=str(i+2)+" "
            if cc.hints[i+2] == 0 : row+= "  "
            else: row+=str(i+3)+" " 
            i+=3
            row+=" "
            self.print_at(row, l +1, c + 1,color)
            l +=1
   
    def draw_cell(self, cc):
        if cc.value == 0 and cc.hints_count() == 0:
            color=1
            if cc.is_active or cc.is_neihgboor:
                color=3
                if self.hint_edit and  cc.is_active : color=2
            self.clear_cell(cc, color)
        elif cc.value != 0 and not(cc.is_static):
            color=4
            if cc.is_active or cc.is_neihgboor:
                color=6
                if self.hint_edit  and cc.is_active : color=5
            if cc.is_invalid : 
                color += 3
            self.draw_value(cc, color)
        elif cc.value != 0 and cc.is_static:
            color=1
            if cc.is_active or cc.is_neihgboor:
                color=3
                if self.hint_edit and  cc.is_active : color=2
            self.draw_value(cc, color)
        else:
            color=1
            if cc.is_active or cc.is_neihgboor:
                color=3
                if self.hint_edit  and  cc.is_active: color=2
            self.draw_hint(cc, color)

    def draw_cells(self, bb):
        for l in range(1,10):    
            for c in range(1,10):        
               self. draw_cell(bb.cells[l][c])

    def render(self, bb):
        l,c = self.get_terminal_center()
        bb.set_center_coord(l,c)
        self.draw_board(bb)
        self.draw_cells(bb)
        self.win.refresh()
        self.game=bb

    def messagebox(self, text):
        tl="╔"
        line="═"
        tr="╗"
        vert="║"
        bl="╚"
        br="╝"
        l=len(text)
        self.render(self.game)
        y,x = self.get_terminal_center()
        x=x-int(l/2)

        self.print_at(tl+ line * l + line * 2 +tr , y-1,x,0)
        self.print_at(vert + " " + text + " " + vert , y,x,0)
        self.print_at(bl+ line * l + line * 2 + br , y+1,x,0)
        self.win.refresh()

        

def test_render(r):
    r.clear()

    bb = board.Board()

    bb.cells[1][1].value=1
    bb.cells[2][2].value=2
    bb.cells[2][3].value=4
    bb.cells[3][3].value=3
    bb.cells[4][4].value=4
    bb.cells[5][5].value=5
    bb.cells[6][6].value=6
    bb.cells[7][7].value=7
    bb.cells[8][8].value=8
    bb.cells[9][9].value=9

    
    bb.cells[1][3].hints=[0,0,0,1,1,0,1,0,0]
    bb.cells[2][5].hints=[1,1,1,1,1,1,1,1,1]

    bb.set_active_cell(2,2)
    r.render(bb)
    #print(bb)

    
   
#r=Render()
#test_render(r)

#r.messagebox("toto")
#r.win.getch()