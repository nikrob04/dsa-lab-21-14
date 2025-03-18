# 2.13
x = input("Введите строку с одной открывающей и одной закрывающей скобкой: ")

# Ищем индексы открывающей и закрывающей скобок
open_bracket_index = x.find('(')  # открывающей скобки
close_bracket_index = x.find(')')  # закрывающей скобки

# Проверяем, найдены ли скобки и правильно ли они расположены
if open_bracket_index != -1 and close_bracket_index != -1 and open_bracket_index < close_bracket_index:
    # Извлекаем символы между скобками
    inside_brackets = x[open_bracket_index + 1:close_bracket_index]
    # Выводим результат
    print(f"Символы внутри скобок: '{inside_brackets}'")
else:
    print("Ошибка: Проверьте, чтобы в строке была одна открывающая и одна закрывающая скобка.")