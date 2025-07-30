import os
import random
from importlib import resources
from typing import Optional, Union, List

def _are_positions_adjacent(pos1: tuple[int, int], pos2: tuple[int, int]) -> bool:
    """Check if two positions are adjacent horizontally or vertically."""
    x1, y1 = pos1
    x2, y2 = pos2
    return (x1 == x2 and abs(y1 - y2) == 1) or (y1 == y2 and abs(x1 - x2) == 1)


def _ensure_vehicle_continuous(vehicle_id: str, positions: list[tuple[int, int]]) -> None:
    """Ensure all positions of a vehicle are adjacent to each other."""
    for i in range(len(positions) - 1):
        if not _are_positions_adjacent(positions[i], positions[i + 1]):
            raise ValueError(f"Vehicle {vehicle_id} must be continuous.")


def _ensure_vehicle_on_single_line(vehicle_id: str, positions: list[tuple[int, int]]) -> None:
    """Ensure all positions of a vehicle are on the same line (either all x or all y)."""
    x_positions = [x for x, _ in positions]
    y_positions = [y for _, y in positions]
    if not (all(x == x_positions[0] for x in x_positions) or
           all(y == y_positions[0] for y in y_positions)):
        raise ValueError(f"Vehicle {vehicle_id} must be on same line.")


class Lot:
    def __init__(self, layout_str_or_moves: Union[str, int, None] = None):
        """
        Initialize a Lot with either a layout string or a number of moves to solve.
        
        Args:
            layout_str_or_moves: Either a layout string, an integer representing the number of moves to solve,
                               or None for a random board.
        """
        if layout_str_or_moves is None or isinstance(layout_str_or_moves, int):
            # Load a random board from rush.txt
            self._init_from_file(layout_str_or_moves)
        elif isinstance(layout_str_or_moves, str):
            # Use the provided layout string
            self._init_from_layout(layout_str_or_moves)
        else:
            raise TypeError(f"Expected string representation of board, int of moves or None (for a random board), got {type(layout_str_or_moves)}")
    
    def _init_from_layout(self, layout_str: str) -> None:
        """Initialize the lot from a layout string."""
        self._grid = [line.strip() for line in layout_str.split('\n') if line.strip()]
        self._height = len(self._grid)
        self._width = len(self._grid[0])
        self._ensure_width_consistency()
        self._vehicles = self._find_vehicles()
        self._ensure_no_single_length_vehicles()
        self._ensure_each_vehicle_lined()
    
    def _init_from_file(self, moves_to_solve: Optional[int] = None) -> None:
        """
        Initialize the lot from a board in rush.txt.
        
        Args:
            moves_to_solve: If provided, select a board that can be solved in this many moves.
                           If None, select a random board.
        """
        try:
            # Try to get the file from the package resources
            is_test = os.getenv('is_test', '').lower() == 'true'
            file_name = 'rush_sample.txt' if is_test else 'rush.txt'
            try:
                resource_path = resources.files('parkinglotpuzzle').joinpath(file_name)
                
                try:
                    with resource_path.open('r') as f:
                        lines = f.readlines()
                except (AttributeError, TypeError):
                    file_path = str(resource_path)
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        
            except (FileNotFoundError, ImportError, OSError):
                file_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(file_dir, file_name)
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"{file_name} not found in package or local directory")
                
                with open(file_path, 'r') as f:
                    lines = f.readlines()
            
            eligible_boards = []
            for line in lines:
                parts = line.strip().split()
                moves, board = int(parts[0]), parts[1]
                if moves_to_solve is None or moves == moves_to_solve:
                    eligible_boards.append(board)
            
            if not eligible_boards:
                if moves_to_solve is not None:
                    raise ValueError(f"No boards found that can be solved in {moves_to_solve} moves.")
                else:
                    raise ValueError(f"No boards found in {file_name}.")
            
            # Select a random board from the eligible ones
            selected_board = random.choice(eligible_boards)
            selected_board = '\n'.join(selected_board[i:i+6] for i in range(0, len(selected_board), 6))
            
            # Initialize from the selected board
            self._init_from_layout(selected_board)
            
        except Exception as e:
            raise RuntimeError(f"Failed to load board from {file_name}: {str(e)}")

    def query_vehicles(self):
        """
        Return a copy of the vehicles dictionary.
        
        Returns:
            A dictionary mapping vehicle IDs to lists of positions.
        """
        return {vehicle_id: positions[:] for vehicle_id, positions in self._vehicles.items()}

    def dimensions(self) -> tuple[int, int]:
        """
        Return the dimensions of the parking lot.
        
        Returns:
            A tuple containing (width, height) of the parking lot.
        """
        return (self._width, self._height)

    def __str__(self) -> str:
        """Return a string representation of the grid."""
        return '\n'.join(self._grid)
    
    def grid(self) -> List[str]:
        """
        Return a copy of the grid.
        
        Returns:
            A list of strings representing the grid, where each string is a row.
        """
        return list(self._grid)
    
    def _ensure_width_consistency(self) -> None:
        if not all(len(row) == self._width for row in self._grid):
            raise ValueError("All rows must have the same width.")
    
    def _find_vehicles(self) -> dict[str, list[tuple[int, int]]]:
        if not any('A' in row for row in self._grid):
            raise ValueError("Main vehicle named A must exist.")
        vehicles = {'A': []}
        for y in range(self._height):
            for x in range(self._width):
                vehicle_id = self._grid[y][x]
                if vehicle_id == '.' or vehicle_id == "#":
                    continue
                if vehicle_id not in vehicles:
                    vehicles[vehicle_id] = []
                vehicles[vehicle_id].append((x, y))
        return vehicles
    
    def _ensure_no_single_length_vehicles(self) -> None:
        for vehicle_id, positions in self._vehicles.items():
            if len(positions) == 1:
                raise ValueError(f"Vehicle {vehicle_id} cannot have length 1")
    
    def _ensure_each_vehicle_lined(self) -> None:
        for vehicle_id, positions in self._vehicles.items():
            positions.sort()  # Sort by x, then y
            _ensure_vehicle_on_single_line(vehicle_id, positions)
            _ensure_vehicle_continuous(vehicle_id, positions)

    def query_legal_moves(self) -> dict[str, tuple[int, int]]:
        """Return a dictionary of vehicle_ids and their legal moves (backward, forward)."""
        moves = {}
        for vehicle_id, positions in self._vehicles.items():
            moves[vehicle_id] = self._get_vehicle_moves(positions)
        return moves
    
    def _get_vehicle_moves(self, positions: list[tuple[int, int]]) -> tuple[int, int]:
        """Calculate how many moves backward and forward a vehicle can make."""
        positions.sort()  # Sort by x, then y
        x_positions = [x for x, _ in positions]
        y_positions = [y for _, y in positions]
        
        # Determine if vehicle is horizontal or vertical
        is_horizontal = all(y == y_positions[0] for y in y_positions)
        
        if is_horizontal:
            # For horizontal vehicles, check left and right
            leftmost_x = min(x_positions)
            rightmost_x = max(x_positions)
            
            # Count moves left
            moves_left = 0
            for x in range(leftmost_x - 1, -1, -1):
                if self._grid[y_positions[0]][x] != '.':
                    break
                moves_left += 1
            
            # Count moves right
            moves_right = 0
            for x in range(rightmost_x + 1, self._width):
                if self._grid[y_positions[0]][x] != '.':
                    break
                moves_right += 1
                
            return moves_left, moves_right
        else:
            # For vertical vehicles, check up and down
            topmost_y = min(y_positions)
            bottommost_y = max(y_positions)
            
            # Count moves up
            moves_up = 0
            for y in range(topmost_y - 1, -1, -1):
                if self._grid[y][x_positions[0]] != '.':
                    break
                moves_up += 1
            
            # Count moves down
            moves_down = 0
            for y in range(bottommost_y + 1, self._height):
                if self._grid[y][x_positions[0]] != '.':
                    break
                moves_down += 1
                
            return moves_up, moves_down

    def move(self, vehicle_id: str, move: int) -> None:
        """Move a vehicle by the specified number of spaces. Positive moves forward, negative moves backward."""
        if move == 0:
            raise ValueError("Move cannot be 0")
            
        if vehicle_id not in self._vehicles:
            raise ValueError(f"Vehicle {vehicle_id} does not exist")
            
        positions = self._vehicles[vehicle_id]
        positions.sort()  # Sort by x, then y
        y_positions = [y for _, y in positions]
        
        # Determine if vehicle is horizontal or vertical
        is_horizontal = all(y == y_positions[0] for y in y_positions)
        
        # Get current legal moves
        legal_moves = self._get_vehicle_moves(positions)
        max_backward, max_forward = legal_moves
        
        # Validate move is legal
        if move > 0 and move > max_forward:
            raise ValueError(f"Vehicle {vehicle_id} cannot move {move} spaces forward (max {max_forward})")
        if move < 0 and abs(move) > max_backward:
            raise ValueError(f"Vehicle {vehicle_id} cannot move {move} spaces backward (max {max_backward})")
        
        # Clear only the positions that will be moved
        if is_horizontal:
            for i in range(len(positions)):
                x, y = positions[i]
                self._set_cell('.', x, y)
            new_positions = [(x + move, y) for x, y in positions]
        else:
            for i in range(len(positions)):
                x, y = positions[i]
                self._set_cell('.', x, y)
            new_positions = [(x, y + move) for x, y in positions]
        
        # Update grid and vehicle positions
        for x, y in new_positions:
            self._set_cell(vehicle_id, x, y)
        self._vehicles[vehicle_id] = new_positions

    def _set_cell(self, value, x, y):
        row = list(self._grid[y])
        row[x] = value
        self._grid[y] = ''.join(row)

    def is_solved(self) -> bool:          
        rightmost_x = max(x for x, _ in self._vehicles['A'])
        return rightmost_x == self._width - 1
