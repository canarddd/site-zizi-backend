from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL)

@app.route("/ping", methods=["GET"])
def ping():
    try:
        conn = get_connection()
        if conn:
            conn.close()
            return jsonify({"connected": True})
        else:
            return jsonify({"connected": False})
    except Exception as e:
        print("Erreur DB:", e)
        return jsonify({"connected": False})

@app.route("/add", methods=["POST"])
def add():
    try:
        data = request.get_json()
        name = data["name"]
        size = float(data["size"])

        conn = get_connection()
        if conn:
            cur = conn.cursor()
            # Crée la table si elle n'existe pas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sizes (
                    name TEXT,
                    size FLOAT
                );
            """)
            cur.execute("INSERT INTO sizes (name, size) VALUES (%s, %s);", (name, size))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "no database connection"}), 500
    except Exception as e:
        print("Erreur add:", e)
        return jsonify({"status": "error"}), 500

@app.route("/all", methods=["GET"])
def all_data():
    try:
        conn = get_connection()
        if not conn:
            return jsonify([])

        cur = conn.cursor()
        # Calcul du nombre d'entrées et moyenne par prénom
        cur.execute("""
            SELECT
                name,
                COUNT(*) AS count,
                ROUND(AVG(size)::numeric, 2) AS average
            FROM sizes
            GROUP BY name
            ORDER BY average DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "name": row[0],
                "count": row[1],
                "average": float(row[2])
            })
        return jsonify(result)
    except Exception as e:
        print("Erreur all:", e)
        return jsonify([]), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
