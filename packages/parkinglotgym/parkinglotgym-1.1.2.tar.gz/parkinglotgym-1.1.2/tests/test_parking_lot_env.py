import unittest
import numpy as np
from parkinglotgym.parking_lot_env import ParkingLotEnv

class TestParkingLotEnv(unittest.TestCase):
    def setUp(self):
        # Simple layout for testing with vehicles of length 2
        self.layout = (
            ".AA.B\n"
            "....B"
        )
        self.env = ParkingLotEnv(self.layout)
        self.initial_obs, _ = self.env.reset()
    
    def test_reset(self):
        """Test that reset returns the environment to its initial state"""
        self.env.step((2, 2))
        
        # Reset the environment
        obs, _ = self.env.reset()
        
        # Check that the observation is the same as the initial one
        np.testing.assert_array_equal(obs, self.initial_obs)
    
    def test_step_valid_move(self):
        """Test that step works with a valid move"""
        obs, reward, done, truncated, _ = self.env.step((2, 1))

        self.assertEqual(reward, -1)
        expected_obs = np.array([[0, 0, 2, 2, 3], [0, 0, 0, 0, 3]])
        np.testing.assert_array_equal(obs, expected_obs)
        self.assertNotEqual(np.array_equal(obs, self.initial_obs), True)
    
    def test_step_invalid_move(self):
        """Test that step handles invalid moves correctly"""
        obs, reward, _, _, _ = self.env.step((2, 4))

        np.testing.assert_equal(reward, -2)
        np.testing.assert_array_equal(obs, self.initial_obs)
    
    def test_available_moves(self):
        """Test that available moves are correctly reported"""
        _, info = self.env.reset()

        available_moves = info['available_moves']
        self.assertEqual({2: (-1, 1)}, available_moves)
    
    def test_puzzle_solved(self):
        """Test that the environment correctly identifies when the puzzle is solved"""
        # Create a simple layout that can be solved in one move
        # This layout has vehicle B at the exit
        solved_layout = (
            "C.AA.\n"
            "C..BB"
        )
        env = ParkingLotEnv(solved_layout)

        obs, reward, done, truncated, info = env.step((2, 1))

        self.assertTrue(done)

        self.assertEqual(reward, 0)

if __name__ == '__main__':
    unittest.main() 