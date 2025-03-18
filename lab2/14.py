# 1.4
x = input("Введите числа, разделенные пробелами: ")

# для хранения чисел
split = []
# хранения текущего числа
current_number = ''

# Перебираем каждый символ в введенной строке
for char in x:
    if char == ' ':  
        if current_number:  # Проверяем, не пустое ли текущее число
            split.append(current_number)  # Добавляем число в массив
            current_number = ''  # Очищаем переменную для следующего числа
    else:
        current_number += char  # Добавляем символ к текущему числу

# Добавляем последнее число, если оно есть
if current_number:
    split.append(current_number)

sum_of_numbers = 0
count_of_numbers = 0

# Используем цикл while для подсчета суммы и количества чисел
i = 0
while i < len(split):
    sum_of_numbers += int(split[i])  # Добавляем текущее число к сумме
    count_of_numbers += 1  
    i += 1  

print(f"Сумма: {sum_of_numbers}, Количество: {count_of_numbers}")