# from flask import Flask, jsonify, request, render_template, redirect, url_for
# import json
# import os

# app = Flask(__name__)

# DATA_FILE = "machines.json"

# # Function to load machines from the JSON file
# def load_machines():
#     if not os.path.exists(DATA_FILE):
#         with open(DATA_FILE, 'w') as f:
#             json.dump({}, f)
#     with open(DATA_FILE, 'r') as f:
#         return json.load(f)

# # Function to render the machine detail page
# @app.route('/machines/<machine_id>/view')
# def view_machine(machine_id):
#     machines = load_machines()
#     machine = machines.get(machine_id)
#     if not machine:
#         return "Machine not found", 404
#     return render_template('machine_detail.html', id=machine_id, machine=machine)

# # Function to save machines to the JSON file
# def save_machines(data):
#     with open(DATA_FILE, 'w') as f:
#         json.dump(data, f, indent=4)

# # Function to render the index page
# @app.route('/')
# def index():
#     machines = load_machines()
#     return render_template('index.html', machines=machines)

# # Function to add a machine
# @app.route('/add', methods=['POST'])
# def add_machine():
#     machines = load_machines()
#     data = request.form
#     machine_id = str(max([int(i) for i in machines.keys()] + [0]) + 1)
#     machines[machine_id] = {
#         "name": data.get("name"),
#         "status": data.get("status"),
#         "location": data.get("location"),
#         "water_level": data.get("water_level")
#     }
#     save_machines(machines)
#     return redirect(url_for('index'))

# # Function to get the machines list
# @app.route('/machines', methods=['GET'])
# def get_machines():
#     machines = load_machines()
#     return jsonify(machines)

# # Function to get a machine by ID
# @app.route('/machines/<machine_id>', methods=['GET'])
# def get_machine(machine_id):
#     machines = load_machines()
#     machine = machines.get(machine_id)
#     if machine:
#         return jsonify(machine)
#     else:
#         return jsonify({"error": "Machine not found"}), 404

# # Function to delete a machine by ID
# @app.route('/machines/<machine_id>', methods=['DELETE'])
# def delete_machine(machine_id):
#     machines = load_machines()
#     if machine_id in machines:
#         del machines[machine_id]
#         save_machines(machines)
#         return jsonify({"message": "Machine deleted"})
#     else:
#         return jsonify({"error": "Machine not found"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)


# # {
# #     "name": "LatteLuxe",
# #     "status": "working",
# #     "location": "Open Space",
# #     "water_level": "full"
# # }


import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"