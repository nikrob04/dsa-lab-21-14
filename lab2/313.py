import random

# 1 Заполняем массив случайными элементами
N = int(input("Введите количество элементов в массиве: "))
array = [random.randint(1, 30) for _ in range(N)] 

# 2 Находим индексы повторяющихся элементов
indices = {}
for index, value in enumerate(array):
    if value in indices:
        indices[value].append(index)  # Добавляем индекс к сущ значению
    else:
        indices[value] = [index]  # Создаем новый список индексов

# Выводим индексы повторяющихся элементов
found_duplicates = False
for value, index_list in indices.items():
    if len(index_list) > 1: 
        found_duplicates = True
        print(f"Элемент {value} повторяется на индексах: {index_list}")

if not found_duplicates:
    print("Повторяющихся элементов нет.")

# 3. Заменяем все элементы массива их удвоенными значениями
for i in range(N):
    if array[i] < 15:
        array[i] *= 2 

print("Полученный массив:", array)