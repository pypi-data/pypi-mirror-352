import unittest
from balajiwork import info
from io import StringIO
import sys

class TestInfo(unittest.TestCase):
    def test_info_output(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        info()
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue().strip(), "balaji.work")

if __name__ == "__main__":
    unittest.main()
