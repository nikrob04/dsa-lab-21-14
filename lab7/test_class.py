# test_class.py

import pytest
from triangle_class import Triangle, IncorrectTriangleSides

# Позитивные тесты
def test_equilateral_triangle():
    t = Triangle(5, 5, 5)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 15

def test_isosceles_triangle():
    t = Triangle(5, 5, 3)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 13

def test_nonequilateral_triangle():
    t = Triangle(4, 5, 6)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 15

# Негативные тесты
def test_zero_side():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 4, 5)

def test_negative_side():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 3, 3)

def test_invalid_triangle_inequality():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 10)
