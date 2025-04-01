from flask import Flask, request, jsonify
import random
import operator
app = Flask(__name__)


# 1) GET-задание: /number/get/
@app.route('/number/get/', methods=['GET'])
def get_number():
    # Получаем параметр 'param' из запроса
    param = request.args.get('param', type=int)
    
    # Проверяем, что параметр был передан и является числом
    if param is None:
        return jsonify({'error': 'Параметр "param" обязателен и должен быть числом.'}), 400

    # Генерируем случайное число
    random_number = random.randint(1, 100)  # Генерируем случайное число от 1 до 100

    # Умножаем случайное число на значение параметра
    result = random_number * param

    # Возвращаем результат в формате JSON
    return jsonify({'random_number': random_number, 'result': result})


# 2) POST-задание: /number/post/
@app.route('/number/post/', methods=['POST'])
def post_number():
    # Получаем JSON-данные из тела запроса
    data = request.get_json()

    # Проверяем, что данные существуют и содержат ключ jsonParam
    if not data or 'jsonParam' not in data:
        return jsonify({'error': 'Требуется JSON с полем "jsonParam".'}), 400

    json_param = data['jsonParam']

    # Проверяем, что jsonParam — число
    if not isinstance(json_param, (int, float)):
        return jsonify({'error': '"jsonParam" должен быть числом.'}), 400

    # Генерируем случайное число
    random_number = random.randint(1, 100)

    # Словарь операций ключ — символ операции, значение — функция
    operations = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv  
    }

    # Случайным образом выбираем одну операцию
    operation_symbol = random.choice(list(operations.keys()))
    operation_func = operations[operation_symbol]

    # Применяем выбранную операцию к числам
    try:
        result = operation_func(random_number, json_param)
    except ZeroDivisionError:
        # Обработка деления на ноль
        return jsonify({'error': 'Деление на ноль.'}), 400

    # Возвращаем JSON с деталями
    return jsonify({
        'random_number': random_number,
        'json_param': json_param,
        'operation': operation_symbol,
        'result': result
    })


@app.route('/number/delete/', methods=['DELETE'])
def delete_number():
    
    import operator

    # Словарь доступных операций
    operations = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv
    }

    # Генерация двух случайных чисел
    a = random.randint(1, 100)
    b = random.randint(1, 100)

    # Выбор случайной операции
    op_symbol = random.choice(list(operations.keys()))
    op_func = operations[op_symbol]

    # Попытка выполнить операцию
    try:
        result = op_func(a, b)
    except ZeroDivisionError:
        return jsonify({'error': 'Деление на ноль.'}), 400

    # Возвращаем JSON-ответ
    return jsonify({
        'number1': a,
        'number2': b,
        'operation': op_symbol,
        'result': result
    })

# РАЗДЕЛ 2
# 1- 2 ) Отправить запрос GET и POST /number с параметром запроса

@app.route('/number', methods=['GET', 'POST', 'DELETE'])
def number_route():
    if request.method == 'GET':
        
        param = request.args.get('param', type=int)
        if param is None:
            return jsonify({'error': 'Параметр "param" обязателен и должен быть числом.'}), 400

        random_number = random.randint(1, 100)
        operation = random.choice(['+', '-', '*', '/'])

        return jsonify({
            'param': param,
            'random_number': random_number,
            'operation': operation
        })

    elif request.method == 'POST':
        
        data = request.get_json()

        if not data or 'jsonParam' not in data:
            return jsonify({'error': 'Ожидается JSON с полем "jsonParam".'}), 400

        json_param = data['jsonParam']

        if not isinstance(json_param, (int, float)):
            return jsonify({'error': '"jsonParam" должен быть числом.'}), 400

        random_number = random.randint(1, 100)
        operation = random.choice(['+', '-', '*', '/'])

        return jsonify({
            'json_param': json_param,
            'random_number': random_number,
            'operation': operation
        })

    elif request.method == 'DELETE':
        
        random_number = random.randint(1, 100)
        operation = random.choice(['+', '-', '*', '/'])

        return jsonify({
            'random_number': random_number,
            'operation': operation
        })





if __name__ == '__main__':
    app.run(debug=True)