# Задание 1

a = input("Введите числа:")
#Разделение массива
sp = list(a.split(' '))
# Перевод в числа
result = list(map(int, sp))
# Поиск и вывод минимального числа
minimal = min(result)
print(minimal)

# задание 2

for i in result:
    if i <= 50 and i >=1:
        print("Число водит в интервал - ", i)

