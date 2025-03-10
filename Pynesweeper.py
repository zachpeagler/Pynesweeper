# we technically don't even need the enum, as we could use a boolean instead, but using it improves clarity at a very small cost, so we'll run with it for now.

# dependencies
from random import sample
from time import sleep
from time import time
from enum import Enum

# gamemode class (reveal or flag)
class GameMode(Enum):
    REVEAL = 1
    FLAG = 2

# cell class
class Cell:
    # initialize the cell
    def __init__(self):
        # bool for is_mine
        self.is_mine = False
        # bool for revealed
        self.is_revealed = False
        # bool for flagged
        self.is_flagged = False
        # int for number of adjacent mines
        self.adjacent_mines = 0

# game class
class MinesweeperGame:
    # initialize the game with x, y, and mines
    # also initialize game state variables (game over, victory, first move, mode, etc.)
    def __init__(self, width=10, height=10, mine_count=10):
        self.width = max(5, min(width, 30))
        self.height = max(5, min(height, 30))
        self.mine_count = max(1, min(mine_count, (self.width * self.height) - 1))
        self.board = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.game_over = False
        self.victory = False
        self.first_move = True
        self.mode = GameMode.REVEAL
        self.start_time = None
        self.end_time = None

    # function to place mines
    # 1. assign safe cells and get all non-safe cells
    # 2. assign mine positions
    # 3. calculate adjacent mine count for each cell
    # called in reveal_cell, flag_cell
    def place_mines(self, first_x, first_y):
        # "safe cells" on first guess to avoid instant losses
        safe_cells = []
        # assign first guess and surrounding cells as safe
        for y in range(max(0, first_y - 1), min(self.height, first_y + 2)):
            for x in range(max(0, first_x - 1), min(self.width, first_x + 2)):
                safe_cells.append((x, y))
        
        # get all cells, then subset so only include those that are not safe
        all_cells = [(x, y) for y in range(self.height) for x in range(self.width)]
        available_cells = [cell for cell in all_cells if cell not in safe_cells]
        
        # place mines randomly
        mine_positions = sample(available_cells, min(self.mine_count, len(available_cells)))
        for x, y in mine_positions:
            self.board[y][x].is_mine = True
        
        # calculate adjacent mine counts
        for y in range(self.height):
            for x in range(self.width):
                # only calculate if not a mine
                if not self.board[y][x].is_mine:
                    # set initial count to zero
                    count = 0
                    # temp values representing -1 to +1 in the x and y direction
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            # skip past self (0,0)
                            if dx == 0 and dy == 0:
                                continue
                            # make sure only to check against cells that exist on the board
                            if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                                # tick up count for each adjacent mine
                                if self.board[y + dy][x + dx].is_mine:
                                    count += 1
                    # set cell adjacent mine count
                    self.board[y][x].adjacent_mines = count
    # function to reveal a cell
    # this function is recursive
    # called by process move
    def reveal_cell(self, x, y):
        # if the attempted cell is not on the board, return
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        # set local cell variable to cell object from the board object
        cell = self.board[y][x]
        # if it's already revealed or flagged, return
        if cell.is_revealed or cell.is_flagged:
            return
        # if it's the first move, get the time, set the first move variable, and call the place_mines function
        if self.first_move:
            self.start_time = time()
            self.first_move = False
            self.place_mines(x, y)
        # set is_revealed to true
        cell.is_revealed = True
        # if the cell is a mine, set game_over var to true
        if cell.is_mine:
            self.game_over = True
            return
        # if cell has no adjacent mines check the surrounding cells and reveal them if they exist
        if cell.adjacent_mines == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                        self.reveal_cell(x + dx, y + dy)
        
        # last step in reveal_cell
        # check for victory
        self.check_victory()
    # flag cell function
    # called by process_move
    def flag_cell(self, x, y):
        # if the cell is not on the board, return
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        # set local cell var
        cell = self.board[y][x]
        # if it's already revealed, return
        if cell.is_revealed:
            return
        # if it's the first move, set the start time, disable first move, and place mines
        if self.first_move:
            self.start_time = time()
            self.first_move = False
            self.place_mines(x, y)
        # toggle cell being flagged
        # this handles both flagging and unflagging
        cell.is_flagged = not cell.is_flagged
    # function to check for victory
    def check_victory(self):
        # count revealed cells
        revealed_count = sum(1 for y in range(self.height) for x in range(self.width) 
                           if self.board[y][x].is_revealed)
        
        # check to see that all non-mine cells are revealed
        # if so, set victory to true, end the game, and set the end time
        if revealed_count == (self.width * self.height - self.mine_count):
            self.victory = True
            self.game_over = True
            self.end_time = time()
    # function to toggle game mode
    def toggle_mode(self):
        if self.mode == GameMode.REVEAL:
            self.mode = GameMode.FLAG
        else:
            self.mode = GameMode.REVEAL
    # function to get elapsed time
    def get_elapsed_time(self):
        if self.start_time is None:
            return 0
        if self.end_time is None:
            return int(time() - self.start_time)
        return int(self.end_time - self.start_time)
    # function to process player move
    # handles checking if the game is over and what the game mode is
    def process_move(self, x, y):
        if self.game_over:
            return
        
        if self.mode == GameMode.REVEAL:
            self.reveal_cell(x, y)
        else: 
            self.flag_cell(x, y)
    # display function
    def display(self):

        # because we're displaying it in the terminal, we have to do it line-by-line, top to bottom
        # so we can start with our game info, then move to column names and separators
        # then iterate through all the Y values, adding the row label and going through all the columns
                
        ### print game info
        print(f"Minesweeper {self.width}x{self.height} with {self.mine_count} mines")
        print(f"Mode: {'REVEAL' if self.mode == GameMode.REVEAL else 'FLAG'} (press 'm' to toggle)")
        print(f"Time: {self.get_elapsed_time()} seconds")
        print(f"Remaining flags: {self.mine_count - sum(1 for y in range(self.height) for x in range(self.width) if self.board[y][x].is_flagged)}")
        print()
        
        # print column indices
        print("   ", end="")
        for x in range(self.width):
            print(f"{x:2}", end="")
        print("\n   ", end="")
        for x in range(self.width):
            print("--", end="")
        print()
        
        ### print board
        # iterate through each cell in the board
        for y in range(self.height):
            print(f"{y:2}|", end="")
            for x in range(self.width):
                # set local cell var
                cell = self.board[y][x]
                # if cell is not revealed
                if not cell.is_revealed:
                    if cell.is_flagged:
                        print(" F", end="")
                    else:
                        print(" .", end="")
                # if cell is revealed
                else:
                    if cell.is_mine:
                        print(" *", end="")
                    elif cell.adjacent_mines == 0:
                        print("  ", end="")
                    else:
                        print(f" {cell.adjacent_mines}", end="")
            print()
        
        ### display end of game message
        if self.game_over:
            if self.victory:
                print("\nCongratulations! You swept the mines! Good job!")
            else:
                print("\nGame Over! You didn't sweep good enough! :(")
            
            # reveal mine locations
            print("\nMine locations:")
            # iterate through all cells
            for y in range(self.height):
                print(f"{y:2}|", end="")
                for x in range(self.width):
                    cell = self.board[y][x]
                    if cell.is_mine:
                        print(" *", end="")
                    else:
                        print(" .", end="")
                print()
# define main function
# this is like the control hub of the game, and is what's called on instantiation and controls the game flow
def main():
    # print welcome message
    print("Welcome to Minesweeper!")
    
    # try to get user inputs for initializing the game
    try:
        width = int(input("Enter board width (5-30): "))
        height = int(input("Enter board height (5-30): "))
        mine_count = int(input("Enter number of mines: "))
    except ValueError:
        print("Invalid input. Using default values.")
        width, height, mine_count = 10, 10, 10
    
    # set local game var to our minesweeper class
    game = MinesweeperGame(width, height, mine_count)
    
    # while the game is NOT over, display it and all associated commands
    while not game.game_over:
        # display
        game.display()
        
        # input command
        command = input("\nEnter command (x,y to play, 'm' to toggle mode, 'q' to quit): ").lower()
        
        # check for high-priority input commands (quitting and switching mode)
        if command == 'q':
            print("Thanks for playing!")
            break
        elif command == 'm':
            game.toggle_mode()
            continue
        
        # otherwise, check for x,y and process the move
        # if the format is invalid, print error code and wait
        try:
            x, y = map(int, command.split(','))
            game.process_move(x, y)
        except (ValueError, IndexError):
            print("Invalid command! Use format: x,y")
            sleep(1)
    
    # if game IS over, call game display
    game.display()
    print("\nThanks for playing!")

# call main to run the game
main()