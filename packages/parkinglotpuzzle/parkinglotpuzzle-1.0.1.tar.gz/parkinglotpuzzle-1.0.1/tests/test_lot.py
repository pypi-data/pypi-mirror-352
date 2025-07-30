import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parkinglotpuzzle.lot import Lot

class TestLot(unittest.TestCase):
    def setUp(self):
        """Set up a valid layout for tests that need it."""
        self.valid_layout = """
        ....O
        FF..O
        .AA..
        ..BB.
        .CC..
        .DD..
        """
        self.lot = Lot(self.valid_layout)

    def test_width_consistency(self):
        """Test that inconsistent width raises ValueError."""
        invalid_width = """
        FF.AA
        ..DD
        ..BB.
        .CC..
        .EE..
        """
        with self.assertRaises(ValueError) as context:
            Lot(invalid_width)
        self.assertIn("All rows must have the same width", str(context.exception))

    def test_main_car_existence(self):
        """Test that missing main car 'A' raises ValueError."""
        no_main_car = """
        DD..E
        ..BBE
        ..CC.
        .SS..
        .FF..
        """
        with self.assertRaises(ValueError) as context:
            Lot(no_main_car)
        self.assertIn("Main vehicle named A must exist.", str(context.exception))

    def test_single_length_vehicle(self):
        """Test that single length vehicles raise ValueError."""
        single_length = """
        FF...
        ..AA.
        ..BB.
        D....
        .CC..
        """
        with self.assertRaises(ValueError) as context:
            Lot(single_length)
        self.assertEqual("Vehicle D cannot have length 1", str(context.exception))

    def test_vehicle_on_single_line(self):
        """Test that vehicles not on a single line raise ValueError."""
        not_on_line = """
        FF..A
        ..AA.
        .BBB.
        .CC..
        .DD..
        """
        with self.assertRaises(ValueError) as context:
            Lot(not_on_line)
        self.assertIn("Vehicle A must be on same line.", str(context.exception))

    def test_vehicle_continuity(self):
        """Test that discontinuous vehicles raise ValueError."""
        not_continuous = """
        FF...
        ..AA.
        B.BB.
        .C...
        .CC..
        """
        with self.assertRaises(ValueError) as context:
            Lot(not_continuous)
        self.assertEqual("Vehicle B must be continuous.", str(context.exception))

    def test_query_legal_moves(self):
        """Test querying legal moves for vehicles."""
        moves = self.lot.query_legal_moves()
        
        # Test horizontal vehicles
        self.assertEqual(moves['F'], (0, 2))
        self.assertEqual(moves['A'], (1, 2))
        self.assertEqual(moves['B'], (2, 1))
        
        # Test vertical vehicles
        self.assertEqual(moves['C'], (1, 2))

    def test_move_horizontal(self):
        """Test moving horizontal vehicles."""
        # Move R right by 1
        self.lot.move('F', 1)
        
        # Check new positions
        self.assertEqual(self.lot._grid[1][1], 'F', "F should be at position (3,0)")
        self.assertEqual(self.lot._grid[1][2], 'F', "F should be at position (4,0)")
        
        # Check old position is cleared
        self.assertEqual(self.lot._grid[1][0], '.', "Original position should be empty")

    def test_move_vertical(self):
        """Test moving vertical vehicles."""
        # Move C down by 1
        self.lot.move('O', 3)
        
        # Check new positions
        self.assertEqual(self.lot._grid[3][4], 'O', "O should be at position (3, 4)")
        self.assertEqual(self.lot._grid[4][4], 'O', "O should be at position (4, 4)")
        
        # Check old position is cleared
        self.assertEqual(self.lot._grid[0][4], '.', "Original position should be empty")
        self.assertEqual(self.lot._grid[1][4], '.', "Original position should be empty")

    def test_move_backward(self):
        """Test moving vertical vehicles backward."""
        # Move D up by 1
        self.lot.move('D', -1)
        
        # Check new positions
        self.assertEqual(self.lot._grid[5][0], 'D', "D should be at position (5, 0)")
        self.assertEqual(self.lot._grid[5][1], 'D', "D should be at position (5, 1)")
        
        # Check old position is cleared
        self.assertEqual(self.lot._grid[5][2], '.', "Original position should be empty")

    def test_invalid_moves(self):
        """Test various invalid move scenarios."""
        # Test zero move
        with self.assertRaises(ValueError) as context:
            self.lot.move('R', 0)
        self.assertEqual(str(context.exception), "Move cannot be 0")

        # Test moving too far
        with self.assertRaises(ValueError) as context:
            self.lot.move('A', 3)
        self.assertIn("cannot move 3 spaces forward", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.lot.move('A', -2)
        self.assertIn("cannot move -2 spaces backward", str(context.exception))

        # Test moving non-existent vehicle
        with self.assertRaises(ValueError) as context:
            self.lot.move('X', 1)
        self.assertIn("does not exist", str(context.exception))

    def test_str_representation(self):
        """Test string representation of the grid."""
        expected_lines = [line.strip() for line in self.valid_layout.split('\n') if line.strip()]
        actual_lines = str(self.lot).split('\n')
        self.assertEqual(actual_lines, expected_lines)

    def test_query_vehicles(self):
        """Test that query_vehicles returns a copy of the vehicles dictionary."""
        vehicles = self.lot.query_vehicles()
        
        self.assertEqual(set(vehicles.keys()), {'A', 'B', 'C', 'D', 'F', 'O'})

    def test_dimensions(self):
        """Test that dimensions returns the correct width and height."""
        width, height = self.lot.dimensions()
        
        self.assertEqual(width, 5)
        self.assertEqual(height, 6)

    def test_is_solved(self):
        """Test the is_solved method for both solved and unsolved states."""
        self.assertFalse(self.lot.is_solved(), "Initial state should not be solved")

        solved_layout = """
        ....O
        FF..O
        ...AA
        ..BB.
        .CC..
        .DD..
        """
        solved_lot = Lot(solved_layout)
        self.assertTrue(solved_lot.is_solved(), "Car A at rightmost edge should be solved")

        almost_solved_layout = """
        ....O
        FF..O
        ..AA.
        ..BB.
        .CC..
        .DD..
        """
        almost_solved_lot = Lot(almost_solved_layout)
        self.assertFalse(almost_solved_lot.is_solved(), "Car A not at rightmost edge should not be solved")

    def test_board_load_from_file(self):
        """Test loading a board from file with specific number of moves to solve."""
        # Test loading a board that can be solved in 60 moves
        os.environ["is_test"] = "true"
        lot = Lot(60)
        
        # The expected board layout for 60 moves from rush.txt
        expected_board = "IBB#..I..LDDJAAL..J.KEEMFFK..MGGHHHM"
        expected_grid = [
            expected_board[i:i+6] for i in range(0, len(expected_board), 6)
        ]
        
        actual_grid = lot.grid()
        self.assertEqual(actual_grid, expected_grid, 
                        f"Expected board {expected_grid}, but got {actual_grid}")
        
        width, height = lot.dimensions()
        self.assertEqual(width, 6, "Width should be 6")
        self.assertEqual(height, 6, "Height should be 6")

if __name__ == '__main__':
    unittest.main() 