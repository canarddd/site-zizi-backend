from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# Stockage en mémoire des tailles par prénom
data = defaultdict(list)

@app.route('/taille', methods=['POST'])
def ajouter_taille():
    contenu = request.get_json()
    prenom = contenu.get('prenom')
    taille = contenu.get('taille')
    if not prenom or taille is None:
        return jsonify({"error": "Paramètres manquants"}), 400
    try:
        taille = float(taille)
    except ValueError:
        return jsonify({"error": "Taille non valide"}), 400

    data[prenom].append(taille)
    return jsonify({"message": f"Taille ajoutée pour {prenom}"}), 200

@app.route('/stats', methods=['GET'])
def stats():
    stats_liste = []
    for prenom, tailles in data.items():
        count = len(tailles)
        avg = sum(tailles) / count if count > 0 else 0
        stats_liste.append({
            "prenom": prenom,
            "count": count,
            "avgTaille": round(avg, 1)  # arrondi à 1 décimale pour le front
        })

    # Trie par nombre d'utilisations décroissant
    stats_liste.sort(key=lambda x: x["count"], reverse=True)
    return jsonify(stats_liste)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
