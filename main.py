import os
from copy import deepcopy
from datetime import datetime
import requests
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')

EMPTY_BOARD = [
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],
            
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],
            
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0]
        ]
global menu
menu = 0
global lastError
lastError = ""

# Game loop
def main():
    init()
    running = True
    while running:
        updateDisplay()
        running = parseCommand(input())

def init():
    if not os.path.exists("saves"):
        os.makedirs("saves")

def updateDisplay():
    global menu
    global lastError
    clear()
    if menu == 0:
        printWelcome()
    elif menu == 1:
        boardPrint()
        print(lastError)
        if lastError != "":
            lastError = ""
    elif menu == 2:
        printHelp()

def printWelcome():
    global currentSaveFile
    currentSaveFile = False
    print("#################")
    print("## Sudoku v1.0 ##")
    print("#################")
    print("#")
    print("# Start a new game, or load a save file?")
    print("# Available save files: ")
    printSaveFileNames()

    print("# load <save file> / new: ")

def printSaveFileNames():
    savefiles = []
    for (_,_,filename) in os.walk("./saves"):
        savefiles.extend(filename)

    for savefile in savefiles:
        print("# \u2055 " + savefile)
    

def parseCommand(command: str):
    global menu
    global lastError
    parts = command.split(" ")

    if command.strip() == "":
        menu = 1
        return True

    action = parts[0].lower()

    if action == "p":
        boardPlaceCell(parts[1], parts[2], parts[3])
    elif action == "d":
        boardDeleteCell(parts[1], parts[2])
    elif action == "load":
        menu = 1
        try:
            boardLoad(parts[1])
        except IndexError:
            boardLoad(False)
    elif action == "save":
        try:
            boardSave(parts[1])
        except IndexError:
            boardSave(False)
    elif action == "new":
        menu = 1
        boardNew()
    elif action in ["h", "help", "?"]:
        menu = 2
    elif action == "quit":
        return False
    else:
        lastError = "Invalid command. To list all commands, write \"?\""

    return True



def boardNew():
    global board
    global currentSaveFile
    answer = input("Do you want to start a new game? (y/n): ")
    
    if answer != "y":
        return
    if currentSaveFile:
        boardSave(currentSaveFile)
        
    board = getRandomBoard()

def boardPlaceCell(col: int, row: int, n: int):
    global lastError
    col = int(col) - 1
    row = int(row) - 1
    n = int(n)
    
    if validMove(col, row, n):
        board[row][col] = n
    else:
        lastError = "Invalid move. If you'd like to empty a cell, use the command \"r <x> <y>\""
    
def boardDeleteCell(col, row):
    col = int(col) - 1
    row = int(row) - 1

    board[row][col] = 0

# Check if move is valid
def validMove(col: int, row: int, n: int):
    # if cell is not vacant
    if board[row][col] != 0:
        return False

    #if number not in column
    for i in range(9):
        if n == board[i][col]:
            return False

    #if number not in row
    for i in range(9):
        if n == board[row][i]:
            return False

    #if number not in 3x3 cell
    firstCellInBlock = getFirstCellInBlock(col, row)
    for i in range(9):
        if n == board[firstCellInBlock[1] + i//3][firstCellInBlock[0] + i%3]:
            return False
    
    return True


# Print board
def boardPrint():
    global board
    # Print the board in a nice format
    print("    1 2 3   4 5 6   7 8 9")
    print("  +-------+-------+-------+")
    print("1 | {} {} {} | {} {} {} | {} {} {} |  p <x> <y> <t>".format(digitOrBlank(board[0][0]), digitOrBlank(board[0][1]), digitOrBlank(board[0][2]), digitOrBlank(board[0][3]), digitOrBlank(board[0][4]), digitOrBlank(board[0][5]), digitOrBlank(board[0][6]), digitOrBlank(board[0][7]), digitOrBlank(board[0][8])))
    print("2 | {} {} {} | {} {} {} | {} {} {} |  Place number t in column x row y".format(digitOrBlank(board[1][0]), digitOrBlank(board[1][1]), digitOrBlank(board[1][2]), digitOrBlank(board[1][3]), digitOrBlank(board[1][4]), digitOrBlank(board[1][5]), digitOrBlank(board[1][6]), digitOrBlank(board[1][7]), digitOrBlank(board[1][8])))
    print("3 | {} {} {} | {} {} {} | {} {} {} |".format(digitOrBlank(board[2][0]), digitOrBlank(board[2][1]), digitOrBlank(board[2][2]), digitOrBlank(board[2][3]), digitOrBlank(board[2][4]), digitOrBlank(board[2][5]), digitOrBlank(board[2][6]), digitOrBlank(board[2][7]), digitOrBlank(board[2][8])))
    print("  +-------+-------+-------+")
    print("4 | {} {} {} | {} {} {} | {} {} {} |  r <x> <y>".format(digitOrBlank(board[3][0]), digitOrBlank(board[3][1]), digitOrBlank(board[3][2]), digitOrBlank(board[3][3]), digitOrBlank(board[3][4]), digitOrBlank(board[3][5]), digitOrBlank(board[3][6]), digitOrBlank(board[3][7]), digitOrBlank(board[3][8])))
    print("5 | {} {} {} | {} {} {} | {} {} {} |  Remove number from column x row y".format(digitOrBlank(board[4][0]), digitOrBlank(board[4][1]), digitOrBlank(board[4][2]), digitOrBlank(board[4][3]), digitOrBlank(board[4][4]), digitOrBlank(board[4][5]), digitOrBlank(board[4][6]), digitOrBlank(board[4][7]), digitOrBlank(board[4][8])))
    print("6 | {} {} {} | {} {} {} | {} {} {} |".format(digitOrBlank(board[5][0]), digitOrBlank(board[5][1]), digitOrBlank(board[5][2]), digitOrBlank(board[5][3]), digitOrBlank(board[5][4]), digitOrBlank(board[5][5]), digitOrBlank(board[5][6]), digitOrBlank(board[5][7]), digitOrBlank(board[5][8])))
    print("  +-------+-------+-------+")
    print("7 | {} {} {} | {} {} {} | {} {} {} |  ?".format(digitOrBlank(board[6][0]), digitOrBlank(board[6][1]), digitOrBlank(board[6][2]), digitOrBlank(board[6][3]), digitOrBlank(board[6][4]), digitOrBlank(board[6][5]), digitOrBlank(board[6][6]), digitOrBlank(board[6][7]), digitOrBlank(board[6][8])))
    print("8 | {} {} {} | {} {} {} | {} {} {} |  Show all commands".format(digitOrBlank(board[7][0]), digitOrBlank(board[7][1]), digitOrBlank(board[7][2]), digitOrBlank(board[7][3]), digitOrBlank(board[7][4]), digitOrBlank(board[7][5]), digitOrBlank(board[7][6]), digitOrBlank(board[7][7]), digitOrBlank(board[7][8])))
    print("9 | {} {} {} | {} {} {} | {} {} {} |".format(digitOrBlank(board[8][0]), digitOrBlank(board[8][1]), digitOrBlank(board[8][2]), digitOrBlank(board[8][3]), digitOrBlank(board[8][4]), digitOrBlank(board[8][5]), digitOrBlank(board[8][6]), digitOrBlank(board[8][7]), digitOrBlank(board[8][8])))
    print("  +-------+-------+-------+")

def printHelp():
    print("## Commands ##")
    print()
    print("# p <x> <y> <t> #")
    print("Put number <t> in column <x> row <y>")
    print("Example: p 4 6 1 -> Place number 1 in column 4 row 6")
    print()
    print("# r <x> <y> #")
    print("Remove number in column <x> row <y>")
    print("Example: s 1 1 -> Remove number in column 1 row 1")
    print()
    print("# save [save file] #")
    print("Save the board in this state with file name [save file]. File name is optional.")
    print("Overwrites current save if file name is not provided.")
    print("Example: save wednesday")
    print()
    print("# load [save file] #")
    print("Load a save file. File name is optional.")
    print("Opens the load file menu if file name is not provided.")
    print("Example: load tuesday")
    print()
    print("# new #")
    print("Instantiates a new board. Saves your progress on current board.")
    print()
    print("# quit #")
    print("Quits the program.")
    print()
    print("# h / help / ? #")
    print("Displays this menu")
    print("Example: ?")
    print()
    print("Press enter to continue...")

#save board
def boardSave(filename: str):
    global currentSaveFile
    if not currentSaveFile:
        if filename:
            currentSaveFile = filename
        else:
            currentSaveFile = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    boardString = serializeBoard()
    saveFile = open("./saves/" + currentSaveFile, "w")
    saveFile.write(boardString)

#load board
def boardLoad(filename: str):
    global board
    global currentSaveFile
    if not filename:
        clear()
        printSaveFileNames()
        filename = input("Load save file: ")

    currentSaveFile = filename
    file = open("./saves/" + filename)
    boardString = file.read()
    board = deserializeBoard(boardString)

def serializeBoard():
    global board
    boardString = ""
    
    for row in board:
        for col in row:
            boardString += str(col)

    return boardString

def deserializeBoard(boardString: str):
    boardArr = []
    temp = []

    for i in range(9):
        for j in range(9):
            temp.append(int(boardString[i*9+j]))
        boardArr.append(temp.copy())
        temp.clear()

    return boardArr

def digitOrBlank(n):
    if n == 0:
        return " "
    else:
        return n

def getFirstCellInBlock(col, row):
    # UI is 1-indexed, lists are 0-indexed
    firstCellRow = row - row % 3
    firstCellCol = col - col % 3

    return (firstCellCol, firstCellRow)

def getRandomBoard():
    temp = deepcopy(EMPTY_BOARD)
    req = requests.get("http://www.cs.utep.edu/cheon/ws/sudoku/new/?size=9&level=1")
    nums = req.json()
    for square in nums["squares"]:
        temp[square["y"]][square["x"]] = square["value"]

    return temp

main()