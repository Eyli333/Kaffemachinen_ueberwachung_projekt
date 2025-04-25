from flask import Flask, jsonify, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)

# --- Configuration ---
DATA_FILE = "machines.json"
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load machine data from JSON file
def load_machines():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Save machine data to JSON file
def save_machines(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Routes ---

# Homepage showing list of machines
@app.route('/')
def index():
    machines = load_machines()
    return render_template('index.html', machines=machines)

# Render machine detail page
@app.route('/machines/<machine_id>/view')
def view_machine(machine_id):
    machines = load_machines()
    machine = machines.get(machine_id)
    if not machine:
        return "Machine not found", 404
    return render_template('machine_detail.html', id=machine_id, machine=machine)

# Get the list of all machines (JSON API)
@app.route('/machines', methods=['GET'])
def get_machines():
    return jsonify(load_machines()), 200

# Get a single machine by ID (JSON API)
@app.route('/machines/<machine_id>', methods=['GET'])
def get_machine(machine_id):
    machine = load_machines().get(machine_id)
    if machine:
        return jsonify(machine)
    return jsonify({"error": "Machine not found"}), 404

# Delete a machine by ID
@app.route('/machines/<machine_id>/delete', methods=['POST'])
def delete_machine(machine_id):
    machines = load_machines()
    if machine_id in machines:
        del machines[machine_id]
        save_machines(machines)
        return redirect(url_for('index'))
    return jsonify({"error": "Machine not found"}), 404

# Add a new machine
@app.route('/add', methods=['POST'])
def add_machine():
    machines = load_machines()
    data = request.form
    machine_id = str(max([int(i) for i in machines.keys()] + [0]) + 1)
    machines[machine_id] = {
        "name": data.get("name"),
        "status": data.get("status"),
        "location": data.get("location"),
        "water_level": data.get("water_level"),
        "image": ""  # image path will be stored here after upload
    }
    save_machines(machines)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"message": "Machine added successfully", "machine_id": machine_id}), 201
    return redirect(url_for('index'))

# Upload an image for a specific machine
@app.route('/upload_image/<machine_id>', methods=['POST'])
def upload_image(machine_id):
    machines = load_machines()

    # Check if machine ID exists
    if machine_id not in machines:
        return jsonify({"error": "Machine not found"}), 404

    # Check if the file is in the request
    if 'image' not in request.files:
        return jsonify({"error": "No image file in the request"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if image and allowed_file(image.filename):
        # Create folder for this machine if not exists
        machine_folder = os.path.join(UPLOAD_FOLDER, f"machine_{machine_id}")
        os.makedirs(machine_folder, exist_ok=True)

        # Save image with secure filename
        filename = secure_filename(image.filename)
        filepath = os.path.join(machine_folder, filename)
        image.save(filepath)

        # Save image path in the machine data
        machines[machine_id]['image'] = f"machine_{machine_id}/{filename}"
        save_machines(machines)

        image_url = url_for('static', filename=f"uploads/machine_{machine_id}/{filename}")
        return jsonify({"message": "Image uploaded successfully", "image_url": image_url}), 200

    return jsonify({"error": "Invalid file format"}), 400


# --- Run the Flask app ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
