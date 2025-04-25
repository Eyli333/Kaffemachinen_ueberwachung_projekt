import base64
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
    machines = load_machines()
    machine = machines.get(machine_id)

    if machine:
        image_path = machine.get('image')
        if image_path:
            full_image_path = os.path.join(UPLOAD_FOLDER, image_path)
            try:
                with open(full_image_path, 'rb') as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    machine['image_base64'] = encoded_string
                    del machine['image'] # Remove the original path to avoid confusion
            except FileNotFoundError:
                machine['image_base64'] = None # Or a default encoded image
        return jsonify(machine)
    return jsonify({"error": "Machine not found"}), 404



# Delete a machine by ID
@app.route('/machines/<machine_id>/delete', methods=['POST'])
def delete_machine(machine_id):
    machines = load_machines()
    if machine_id in machines:
        del machines[machine_id]
        save_machines(machines)
        # Remove the machine's folder if it exists
        machine_folder = os.path.join(UPLOAD_FOLDER, f"machine_{machine_id}")
        if os.path.exists(machine_folder):
            for filename in os.listdir(machine_folder):
                file_path = os.path.join(machine_folder, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            os.rmdir(machine_folder)
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

        "ai_status": data.get("ai_status"),
        "ai_model": data.get("ai_model"),
        "accuracy": data.get("accuracy"),
        "loss_function": data.get("loss_function"),

        "sensorPosition1": data.get("sensorPosition1"),
        "sensorPosition2": data.get("sensorPosition2"),
        "timestamp": data.get("timestamp"),
        "data_label": data.get("data_label"),
        "data_notes": data.get("data_notes"),
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

@app.route('/upload_machine_data', methods=['POST'])
def upload_machine_data():
    if request.is_json:
        data = request.get_json()
        machine_id = str(data.get('machine_id'))
        metadata = data.get('meta', {})
        image_base64 = data.get('image_base64')
        filename = data.get('filename', 'spectrogram.png')

        if not machine_id:
            return jsonify({"error": "Missing 'machine_id' in request."}), 400

        machines = load_machines()
        machines[machine_id] = {
            "name": metadata.get("name", "default_name"),
            "status": metadata.get("status", "unknown"),
            "location": metadata.get("location", "unknown"),

            "ai_status": metadata.get("ai_status", "null"),
            "ai_model": metadata.get("ai_model", "null"),
            "accuracy": metadata.get("accuracy", "null"),
            "loss_function": metadata.get("loss_function", "null"),

            "timestamp": metadata.get("timestamp", "null"),
            "sensorPosition1": metadata.get("sensorPosition1", "null"),
            "sensorPosition2": metadata.get("sensorPosition2", "null"),
            "data_label": metadata.get("lable", "null"),
            "data_notes": metadata.get("notes", "null"),

            "image": machines.get(machine_id, {}).get('image', "") # Keep existing image path if it exists
        }

        if image_base64:
            try:
                image_data = base64.b64decode(image_base64)
                machine_folder = os.path.join(UPLOAD_FOLDER, f"machine_{machine_id}")
                os.makedirs(machine_folder, exist_ok=True)
                sanitized_filename = secure_filename(filename)
                filepath = os.path.join(machine_folder, sanitized_filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                machines[machine_id]['image'] = f"machine_{machine_id}/{sanitized_filename}"
                print(f"Image saved for machine {machine_id}")
            except Exception as e:
                print(f"Error saving image for machine {machine_id}: {e}")
        else:
            print(f"No image base64 received for machine {machine_id}")

        save_machines(machines)
        return jsonify({"message": f"Data received and updated for machine ID '{machine_id}'.", "machine_id": machine_id}), 200
    else:
        return jsonify({"error": "Request content must be JSON."}), 400

# --- Run the Flask app ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)