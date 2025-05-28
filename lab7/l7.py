

class IncorrectTriangleSides(Exception):

    #исключение для некорректных сторон треугольника.

    pass

def get_triangle_type(a, b, c):

    #:param a: длина стороны a
    #:param b: длина стороны b
    #:param c: длина стороны c
    #:return: строка с типом треугольника: 'equilateral', 'isosceles' или 'nonequilateral'
    #:raises IncorrectTriangleSides: если стороны не образуют треугольник

    # Проверка, что стороны положительные
    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("Стороны треугольника должны быть положительными.")

    # Проверка условия существования треугольника
    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        raise IncorrectTriangleSides("Стороны не образуют треугольник.")

    # Определение типа треугольника
    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"
