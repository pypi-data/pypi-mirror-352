# ParkingLotPuzzle

[![codecov](https://codecov.io/gh/EvalVis/ParkingLot/branch/main/graph/badge.svg)](https://codecov.io/gh/EvalVis/ParkingLot)
[![PyPI version](https://badge.fury.io/py/parkinglot.svg)](https://pypi.org/project/parkinglot/)

This lib simulates a RushHour puzzle created by Nob Yoshigahara: https://en.wikipedia.org/wiki/Rush_Hour_(puzzle).

You can choose from lots of preconfigured puzzles or input your custom puzzle configuration.

Known clients: [![GitHub](https://img.shields.io/badge/GitHub-EvalVis/ParkingLot-black?style=flat&logo=github)](https://github.com/EvalVis/ParkingLot).

 ## Board definition.

 Hash (`#`) represents the walls. Vehicles cannot move into walls.

 Dot (`.`) represents the empty spaces. Cars can move freely into empty spaces.
 
 Other characters represent vehicles.
 However, for standartization using capital letters for vehicles are encouraged.
 Letter `A` represents the main vehicle.

 ## Goal of the game.
 
 Move the main vehicle (`A`) to the right side of the board: the vehicle must be on the rightmost cell.

 Example of the solved puzzle:

 ```
 ..BB..
 C.....
 C...AA
 C.EKOO
 DDEK..
 ```

## Functionality
- Create puzzle:
  - Provide a number of moves. Get a random preconfigured puzzle solvable in provided number of moves. Note that there are no puzzles solvable in 56, 57, 59 moves. Inputting these numbers will cause error.
  - Provide a custom NxM puzzle. If invalid puzzle is provided an error will be thrown.
- Get a list of vehicles and their positions on the puzzle.
- Get width and height of the puzzle.
- Show puzzle representation.
- Get a copy of the puzzle.
- Show valid moves.
- Make a valid move. Making an invalid move will throw an error and will not result in any action.
- Check if puzzle is solved.

 ## Library restriction

 Vehicles which have a length of a single cell are not allowed
 since it is not clear which direction it is facing.

## Usage

```python
from parkinglotpuzzle.lot import Lot
# Create puzzle solvable in 60 moves.
lot = Lot(60)

# Create a custom puzzle.
self.valid_layout = """
....O
FF..O
.AA..
..BB.
.CC..
.DD..
"""
lot = Lot(self.valid_layout)

print(lot.query_vehicles())
# Shows vehicles and their positions: (x, y) of each occupied cell.
# {
#     'A': [(1, 2), (2, 2)],
#     'O': [(4, 0), (4, 1)],
#     'F': [(0, 1), (1, 1)],
#     'B': [(2, 3), (3, 3)],
#     'C': [(1, 4), (2, 4)],
#     'D': [(1, 5), (2, 5)]
# }

print(lot.dimensions())
# Shows (width, height) of the puzzle.

print(lot)
# Prints the puzzle:
# ....O
# FF..O
# .AA..
# ..BB.
# .CC..
# .DD..

print(lot.grid())
# ['....O', 'FF..O', '.AA..', '..BB.', '.CC..', '.DD..']

print(lot.query_legal_moves())
# Shows legal moves. Given example, moves are:
# {
#     'A': (1, 2), # Main vehicle can move 1 step back and 2 forward. 
#     'O': (0, 4), # O vehicle cannot move back and can move 4 steps forward.
#     'F': (0, 2), # F vehicle cannot move back and can move 2 steps forward.
#     'B': (2, 1), # B vehicle can move 2 steps back and a step forward.
#     'C': (1, 2), # C vehicle can move a step back and a 2 steps forward.
#     'D': (1, 2) # D vehicle can move a step back and a 2 steps forward.
# }

# Check if puzzle is solved.
print(lot.is_solved())
#False

# Make a move which solves the puzzle.
lot.move('A', 2)

print(lot)
# ....O
# FF..O
# ...AA
# ..BB.
# .CC..
# .DD..

print(lot.is_solved())
#True
```

## Caution
Please only use `str(lot)` method when printing.
Otherwise make use of `lot.grid()` method.

If you couple to `str(lot)` and this method will change by introducing different
formatting or showing the board in a different way, your code will break.

## Game configuration database

The `rush_sample.txt` contains a modified sample from database of game configurations created by Michael Fogleman https://www.michaelfogleman.com/rush/.
Modified means o is replaced with . and x with #.

## Extra sources

A good analysis of the game: https://www.michaelfogleman.com/rush/.