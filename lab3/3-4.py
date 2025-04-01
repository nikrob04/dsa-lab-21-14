def apply(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b
    else:
        raise ValueError("Неверная операция")


# Ввод данных от пользователя
num1 = float(input("Введите первое число: "))
op1 = input("Введите первую операцию (+, -, *, /): ")
num2 = float(input("Введите второе число: "))
op2 = input("Введите вторую операцию (+, -, *, /): ")
num3 = float(input("Введите третье число: "))

# Выполнение операций последовательно
step1 = apply(num1, num2, op1)
step2 = apply(step1, num3, op2)

# Вывод результата
print(f"\nВыражение: ({num1} {op1} {num2}) {op2} {num3}")
print(f"Результат: {step2}")
print(f"Результат (int): {int(step2)}")
