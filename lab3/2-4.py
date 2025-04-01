import requests
import random

# Базовый URL — замени на свой
base_url = "http://127.0.0.1:5000/number"

# --- 1. GET запрос ---
param = random.randint(1, 10)
get_response = requests.get(base_url, params={"param": param}).json()

get_num = get_response["random_number"]
get_op = get_response["operation"]

print("GET →", get_num, get_op)

# --- 2. POST запрос ---
json_param = random.randint(1, 10)
post_response = requests.post(base_url, json={"jsonParam": json_param}).json()

post_num = post_response["random_number"]
post_op = post_response["operation"]

print("POST →", post_num, post_op)

# --- 3. DELETE запрос ---
delete_response = requests.delete(base_url).json()

delete_num = delete_response["random_number"]
delete_op = delete_response["operation"]

print("DELETE →", delete_num, delete_op)

# --- 4. Функция выполнения операций ---
def apply(a, b, op):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        return a / b

# --- 5. Последовательный расчёт ---
step1 = apply(get_num, json_param, get_op)
final_result = apply(step1, delete_num, post_op)

print("\nВыражение:")
print(f"Шаг 1: {get_num} {get_op} {json_param} = {step1}")
print(f"Шаг 2: {step1} {post_op} {delete_num} = {final_result}")
print("\nИтоговое значение (int):", int(final_result))
