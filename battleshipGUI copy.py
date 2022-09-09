"""
COMP.CS.100 Ohjelmointi 1 / Programming 1
Student Id: 150494524
Name:       Anh Duy Tran
Email:      anh.2.tran@tuni.fi

BATTLESHIP GAME GUI:


"""

import sys
import random
from tkinter import *
from tkinter.font import Font

#global variables for the window's width and height
WINDOW_HEIGHT = 700
WINDOW_WIDTH = 900


class GUI:
    def __init__(self) -> None:
        ##############################
        #Construct the GUI's elements#
        ##############################

        # intitialize the root window and title
        self.root = Tk()
        self.root.title("Battle Ship by Anh Duy Tran")
        self.root.config(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.__gameTitle = Label(self.root,
                                 text="BattleShip",
                                 font=Font(size=40))
        self.__gameTitle.place(x=350, y=0)

        # THE BOARD #
        self.boardLabel1 = Label(self.root,
                                 text= "           ".join("A B C D E F G H I J".split(' ')),
                                 font=Font(size=14))
        self.boardLabel1.place(x=45, y =95)
    
        self.boardLabel2 = Label(self.root,
                                 text= "           ".join("A B C D E F G H I J".split(' ')),
                                 font=Font(size=14))
        self.boardLabel2.place(x=45, y =620)

        self.boardLabel1 = Label(self.root,
                                 text= "\n\n\n".join("0 1 2 3 4 5 6 7 8 9".split(' ')),
                                 font=Font(size=14))
        self.boardLabel1.place(x=15, y =135)

        self.boardLabel1 = Label(self.root,
                                 text= "\n\n\n".join("0 1 2 3 4 5 6 7 8 9".split(' ')),
                                 font=Font(size=14))
        self.boardLabel1.place(x=530, y =135)
        

        

        # entry block for file's name
        self.entry_field_label = Label(self.root,
                                       text="Game file:")
        self.boardName = ""
        self.entry_field_label.place(x=600, y=150)

        self.__filename = Entry()
        self.__filename.place(x=600, y=170)
        
        # load button
        self.__loadButton = Button(self.root,
                                   text="Load Game",
                                   command=self.load)
        self.__loadButton.place(x=600, y=200)

        ## switch to EDIT MODE button ##
        

        # entry for the name of the ship that will be created by the program
        self.shipNameLabel = Label(self.root,
                                   text="Ship Name:")
        self.shipName = Entry()

        # begin to add a new shape
        

        #new ship properties
        self.newShape = {"name": "", "coord": []}

        #new board
        self.newEditedBoard = []

        ##quit button
        self.__quitButton = Button(self.root,
                                   text="Quit",
                                   command= lambda: self.root.destroy())
        self.__quitButton.place(x=600, y=260)

        # error / notification message
        self.message = Label(self.root,
                               text="",
                               font=Font(size=20),
                               fg="red")
        self.message.place(x=550, y=500)

        # initialize new game log file
        try:
            f = open("gameLog.txt", "w")
        except IOError:
            self.pushMessage("Can not make a new log file!")
        self.shotLog = []
        self.numberOfHit = 0
        
        # variable for the battleship game
        self.totalShotCount = 0
        self.BOARD = [[0 for i in range(10)] for j in range(10)]
        self.loaded = False

        self.ships = []
        self.activeShip = 0

        self.gameOver = False
        pass

    def init_child_class(self):
        self.buttons = [[NewButton(i, j) for i in range(10)] for j in range(10)]
        for i in range(10):
            for j in range(10):
                self.buttons[i][j].button.place(x=50 * i + 30, y=50 * j + 120)

        self.__editButton = EditButton()
        self.__editButton.button.place(x=600, y =230)
        self.Editing = False
        self.beginShapeButton = BeginShapeButton()
        self.beginNewShape = False
        self.randomColor = ""

    def load(self):
        """
        load the ship arangments from the file
        """
        self.clearBoard()
        if self.readboard(self.__filename.get()):
            self.pushMessage("Game loaded successfully", "green")
            self.boardName = self.__filename.get()
            self.loaded = True
        pass

    def convert(self, coord):
        """
        the method return the x and y coordinate from the string 
        representation

        return False if the coordinate can't be convert
        else return [x, y] components

        Example:
            A1 => [1, 1]
            B6 => [6, 2]
        """
        if len(coord) != 2:
            return False
        try:
            x = int(coord[1])
            y = ord(coord[0]) - ord("A")
            if not 0 <= x <= 9 or not 0 <= y <= 9:
                return False

        except ValueError:
            return False

        return [x, y]

    def readboard(self, filename):
        """
        BOARD scheme:
            -1 for the place that has been shot
            0 for the place that dont have ship/ship's part
            else: contains the id of the occupied ship/ship's part

        Return True if the board loaded successfully, 
        
        else, the method use the
        pushMessage method to notify an error then return False.
        """
        try:
            f = open(filename, "r")
            self.boardName = filename
            for id, line in enumerate(f):
                self.activeShip += 1
                temp = line.strip().split(';')
                if len(temp) == 1:
                    self.pushMessage("Error in ship coordinates!", "red")
                    return False

                # add the player's ship configuration
                ship = {}
                ship["name"] = temp[0]
                ship["initial"] = temp[0][0].upper()
                ship["sank"] = False
                ship["length"] = len(temp) - 1
                ship["coordinate"] = temp[1:]
                self.ships.append(ship)

                # mark the BOARD with the ship's id

                # battleship;A1;A2;A3;A4...
                # => start with the second element for the coordinates

                for j in range(1, len(temp)):
                    convertable = self.convert(temp[j])

                    if not convertable:
                        self.pushMessage("Error in ship coordinates!", "red")
                        return False

                    x, y = convertable
                    if not self.markBoard(id, x, y):
                        return False


        except IOError:
            self.pushMessage("File can not be read!", "red")
            return False

        return True

    def markBoard(self, id, x, y):
        """
        method use to change the value of the board by the board's scheme
        and check for overlapping
        """
        if not 0 <= x <= 9 or not 0 <= y <= 9:
            self.pushMessage("Error in ship coordinates!", "red")
            return False

        if self.BOARD[x][y]:
            self.pushMessage("There are overlapping ships in the input file!", "red")
            return False
        else:
            self.BOARD[x][y] = id + 1

        return True

    def clearBoard(self):
        """
        
        this method reset the object's and button's variables clear
        the error message, clear the count variables for log

        """
        # clear the board
        self.BOARD = [[0 for i in range(10)] for j in range(10)]
        
        # reset the state of the game
        self.gameOver = False

        # reset the ship's atributes container
        self.ships = []
        self.activeShip = 0

        #reset the tiles' layout
        for i in range(10):
            for j in range(10):
                self.buttons[i][j].button.config(text="")
        
        # reset the error message
        self.pushMessage("")

        # reset the count variables for log
        self.numberOfHit = 0
        self.shotLog = []

    def pushMessage(self, text, color = "red"):
        """
        this method change the text of the message Label that appears 
        on the root window with the color as the second argument.
        """
        self.message["fg"] = color
        self.message["text"] = text

    def shoot(self, x, y):
        """
        this method take the coordinates x, y and place a shot and add a count to totalShotCount

        this method is called in the NewButton class at its pressed method.
        """
        # adding to the totalShotCount variable
        self.totalShotCount += 1

        temp = chr(y + ord('A')) + str(x)
        self.shotLog.append(temp)

        # mark a missed shot
        if self.BOARD[x][y] == 0:
            self.BOARD[x][y] = -1
            return True

        # mark a hit shoot and change the atributes of the ship that been hit.
        if self.BOARD[x][y] != 0:

            self.shotLog[-1] = self.shotLog[-1] + "*"
            self.numberOfHit += 1

            id = self.BOARD[x][y] - 1
            self.ships[id]["length"] -= 1

            if self.ships[id]["length"] == 0:
                self.revealShip(id)

                # keep track of the number of ships that haven't
                # been sank, if that number == 0 then the game 
                # is over
                self.activeShip -= 1

                self.pushMessage(f"You sank a " + self.ships[id]["name"].upper() + "!", "green")

                if self.activeShip == 0:
                    self.gameOver = True
                    self.writeLog()
                    self.pushMessage(f"Congratulations! \nYou sank all enemy ships in {self.totalShotCount} shots.", "green")

            self.BOARD[x][y] = -1
        return True

    def revealShip(self, id):
        """
        this method change the titles of the board to the capital initial
        of the sunken ship.
        """
        for coord in self.ships[id]["coordinate"]:
            x, y = self.convert(coord)
            self.buttons[y][x].button["text"] = self.ships[id]["initial"]
        pass

    def writeLog(self):
        """
        this method write to the log all the shots' location.
        """
        try:
            f = open("gameLog.txt", "a")
            f.write(f"Game board: {self.boardName}\n")
            f.write("List of all the shots' location (shots that hit are marked with \"*\"):\n")
            f.write("\n".join(self.shotLog))
            f.write(f"\nGame finished in {len(self.shotLog)} hits!")
            f.write(f"\nHit percentage: {(self.numberOfHit*100)/len(self.shotLog):.2f}%\n")
            f.write("*"*30)
            f.write("\n")

            f.close()
        except IOError:
            self.pushMessage("Error while creating a log file")
        return


    def resetShape(self):
        """
        this method record the newly created ship's name and coordinates 
        to a list of string (self.newEditedBoard)

        the string is formated according to the program's encoding style
        for game board (semicolon seperated value) 
        
        Example:
            battleship;A1;A2;A3;A4
        """
        # edge case
        if not len(self.newShape["coord"]):
            return

        # if the ship name include mutiple words then put '_' to join the words
        temp = '_'.join(self.newShape["name"].split(' '))

        for coord in self.newShape["coord"]:
            temp += ";"
            converted = chr(coord[1] + ord("A")) + str(coord[0])
            temp += converted
            
        self.newEditedBoard.append(temp)

        self.newShape = {"name": "", "coord": []}
        return


class NewButton(GUI):
    """
    the general blueprint for each tile in the game board
    """
    def __init__(self, x, y) -> None:
        super().__init__()

        self.button = Button(self.root, font=Font(size=15), command=self.pressed)
        self.button.config(width=1, height=2)
        self.x = x
        self.y = y
        pass

    def pressed(self):
        ################
        # EDITING MODE #
        ################
        # 1. first, check if the user is in the Edit mode and started a new ship:
        #
        # 2. clear the message
        #
        # 3. check for missing name or occupied space
        #
        # 4. record the choosen name and coordinates for the new ship
        if self.Editing and not self.beginNewShape:
            self.pushMessage("press \"Begin Shape\" to start selecting", "red")
            return

        if self.Editing and self.beginNewShape:
            self.pushMessage("")
            
            if self.shipName.get() == "":
                self.pushMessage("New ship needs name!", "red")
                return
            if self.button["text"] != "":
                #unselect the tile
                if [self.x, self.y] in self.newShape["coord"]:
                    self.newShape["coord"].remove([self.x, self.y])
                    self.button["text"] = ""
                    return
                
                self.pushMessage("Location already occupied!", "red")
                return

            #check if the newly selected ship part is valid or not 
            # (have an adjacent side to another of its part)
            valid = True
            if len(self.newShape["coord"]) != 0:
                valid = False
                if [self.x + 1, self.y] in self.newShape["coord"]:
                    valid = True
                elif [self.x - 1, self.y] in self.newShape["coord"]:
                    valid = True
                elif [self.x, self.y + 1] in self.newShape["coord"]:
                    valid = True
                elif [self.x, self.y - 1] in self.newShape["coord"]:
                    valid = True

            if not valid:
                self.pushMessage("new ship part need to be close together!")
                return

            #edit the board content according the user input
            self.button["text"] = self.shipName.get()[0].upper()
            self.button["fg"] = self.randomColor

            # edit the new ship atributes
            self.newShape["coord"].append([self.x, self.y])
            return

        ################
        # NORMAL MODE  #
        ################
        # raise error if the game is over or the game is not loaded
        #
        # 1. clear the message
        #
        # 2. check for what text should be replace in the button:
        #           if BOARD at [x][y] is = -1  ==> location already been shot then return
        #           if BOARD at [x][y] is not zero(have a ship part)  ==> change text to "X"
        if self.gameOver:
            self.pushMessage("Game is over, \nload another game to continue playing")
            return
        elif not self.loaded:
            self.pushMessage("Game not loaded!")
            return

        self.pushMessage("")

        if self.BOARD[self.x][self.y] == -1:
            self.pushMessage("Location has already been shot at!")
            return

        if self.BOARD[self.x][self.y]:
            self.button["text"] = "X"
            self.button["fg"] = "red"
        else:
            self.button["text"] = "O"
            self.button["fg"] = "white"

        self.shoot(self.x, self.y)


class EditButton(GUI):
    def __init__(self) -> None:
        super().__init__()
        self.button = Button(self.root, text = "Edit Mode = OFF", fg = "red", command=self.pressed)
        self.GUI = GUI
        return

    def pressed(self):
        if self.beginNewShape:
            self.pushMessage("End shape to turn off Edit Mode!")
            return

        # change the state of the program 
        self.Editing = not self.Editing

        self.clearBoard()
        if self.Editing:
            
            # ENTER THE EDITTING MODE

            # begin a new shape
            self.resetShape()

            # change the button's layout
            self.button["text"] = "Edit Mode = ON"
            self.button["fg"] = "green"
            
            # re-place some more button and label to the GUI
            self.shipNameLabel.place(x=600, y = 300)
            self.shipName.place(x=600, y=320)
            self.beginShapeButton.button.place(x=600, y=350)
        else:

            # ENDING THE EDITTING MODE

            # record and reset the shape
            self.resetShape()
            try:
                # write every encoded ships name and coordinates to a new file
                f = open("newBoard.txt", "w")
                f.write("\n".join(self.newEditedBoard))
                f.close()
                self.pushMessage("Successfully created a new board!", "green")

            except IOError:
                self.pushMessage("Error while writing the gameboard!")
                return

            # change the button layout
            self.button["text"] = "Edit Mode = OFF"
            self.button["fg"] = "red"

            # clear the list of encoded string of ship's coordinates
            self.newEditedBoard = []

            # remove the editing button, label, entry element from the GUI
            self.shipNameLabel.place_forget()
            self.shipName.place_forget()
            self.beginShapeButton.button.place_forget()
        return
            

class BeginShapeButton(GUI):
    """
    A button to seperate the shape selected by the user when creating a new game board
    """
    def __init__(self) -> None:
        super().__init__()
        self.button = Button(self.root, text = "Begin Shape", command=self.pressed)
        pass

    def pressed(self):
        #change the state of the program
        self.beginNewShape = not self.beginNewShape

        if self.beginNewShape:
            # begin a new shape
            if self.shipName.get() == "":
                self.pushMessage("New ship needs name!", "red")
                self.beginNewShape = not self.beginNewShape
            else:
                self.newShape["name"] = self.shipName.get()
                self.randomColor = random.choice(["red", "green", "blue", "yellow", "cyan", "purple", "brown"])
                self.button["text"] = "End Shape"
        else:
            # end a shape
            self.button["text"] = "Begin Shape"
            self.resetShape()


def main():
    game = GUI()
    game.init_child_class()
    # immediately load the game board if the user give a 
    # useable file's name as the second argument
    if len(sys.argv) == 2:
        if game.readboard(sys.argv[1]):
            game.pushMessage("Game loaded successfully", "green")
            game.loaded = True
    if len(sys.argv) > 2:
        game.pushMessage("Wrong number of arguments")

    # start the GUI
    game.root.mainloop()

if __name__ == "__main__":
    main()
