

import l7
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestTriangleType(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(5, 5, 5), "equilateral")

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(5, 5, 3), "isosceles")

    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(4, 5, 6), "nonequilateral")

    def test_invalid_negative(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 2)

    def test_invalid_zero(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 4, 5)

    def test_invalid_triangle_inequality(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 10)

if __name__ == "__main__":
    unittest.main()
