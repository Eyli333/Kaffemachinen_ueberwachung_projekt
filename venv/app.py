from flask import Flask, jsonify, request, render_template, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = "machines.json"

# Fonction pour charger les données depuis le fichier JSON
def load_machines():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Fonction pour sauvegarder les données dans le fichier JSON
def save_machines(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    machines = load_machines()
    return render_template('index.html', machines=machines)

@app.route('/add', methods=['POST'])
def add_machine():
    machines = load_machines()
    data = request.form
    machine_id = str(max([int(i) for i in machines.keys()] + [0]) + 1)
    machines[machine_id] = {
        "nom": data.get("nom"),
        "etat": data.get("etat"),
        "emplacement": data.get("emplacement"),
        "niveau_eau": data.get("niveau_eau")
    }
    save_machines(machines)
    return redirect(url_for('index'))

@app.route('/machines', methods=['GET'])
def get_machines():
    machines = load_machines()
    return jsonify(machines)

@app.route('/machines/<machine_id>', methods=['GET'])
def get_machine(machine_id):
    machines = load_machines()
    machine = machines.get(machine_id)
    if machine:
        return jsonify(machine)
    else:
        return jsonify({"erreur": "Machine non trouvée"}), 404

@app.route('/machines/<machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    machines = load_machines()
    if machine_id in machines:
        del machines[machine_id]
        save_machines(machines)
        return jsonify({"message": "Machine supprimée"})
    else:
        return jsonify({"erreur": "Machine non trouvée"}), 404

if __name__ == '__main__':
    app.run(debug=True)


# {
#     "nom": "LatteLuxe",
#     "etat": "fonctionnelle",
#     "emplacement": "Open Space",
#     "niveau_eau": "plein"
# }