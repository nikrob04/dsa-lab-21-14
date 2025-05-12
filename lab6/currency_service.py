from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Параметры подключения к базе данных
DB_NAME = "lab6"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

@app.route('/load', methods=['POST'])
def load_currency(): #curl -X POST http://localhost:5001/load -H "Content-Type: application/json" -d "{\"currency_name\": \"USD\", \"rate\": 93.7}"

    data = request.json

    currency_name = data.get("currency_name")
    rate = data.get("rate")

    if not currency_name or rate is None:
        return jsonify({"error": "Missing currency_name or rate"}), 400

    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({"error": "Rate must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Rate must be a number"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверка на наличие валюты
        cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name.upper(),))
        existing = cursor.fetchone()

        if existing:
            return jsonify({"message": "Currency already exists"}), 409  # конфликт

        # Вставка новой валюты
        cursor.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
            (currency_name.upper(), rate)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Currency loaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    #curl -X POST http://localhost:5001/update_currency -H "Content-Type: application/json" -d "{\"currency_name\": \"USD\", \"rate\": 95.1}"
@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json

    currency_name = data.get("currency_name")
    rate = data.get("rate")

    if not currency_name or rate is None:
        return jsonify({"error": "Missing currency_name or rate"}), 400

    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({"error": "Rate must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Rate must be a number"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли валюта
        cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name.upper(),))
        existing = cursor.fetchone()

        if not existing:
            return jsonify({"error": "Currency not found"}), 404

        # Обновляем курс
        cursor.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (rate, currency_name.upper())
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Currency updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#curl -X POST http://localhost:5001/delete -H "Content-Type: application/json" -d "{\"currency_name\": \"USD\"}"

@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json

    currency_name = data.get("currency_name")
    if not currency_name:
        return jsonify({"error": "Missing currency_name"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверка, существует ли валюта
        cursor.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name.upper(),))
        existing = cursor.fetchone()

        if not existing:
            return jsonify({"error": "Currency not found"}), 404

        # Удаление валюты
        cursor.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name.upper(),))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Currency deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(port=5001)
