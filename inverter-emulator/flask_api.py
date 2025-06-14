# inverter-emulator/flask_api.py

from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# Simple user database
USERS = {
    "admin": "admin123",
    "viewer": "viewer123"
}
# Roles: admin can GET/POST; viewer can only GET
ROLES = {
    "admin": ["GET", "POST"],
    "viewer": ["GET"]
}

# Folder to store “uploaded firmware”
UPLOAD_FOLDER = "/usr/src/app/firmware_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory inverter config
INVERTER_CONFIG = {
    "inverter_id": "INV001",
    "max_power_kw": 5.0,
    "firmware_version": "1.0.0"
}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username
    return None

@auth.get_user_roles
def get_user_roles(user):
    return [user]

@app.before_request
def check_role_permissions():
    user = auth.current_user()
    if not user:
        return
    allowed_methods = ROLES.get(user, [])
    if request.method not in allowed_methods:
        abort(403)

@app.route("/api/health", methods=["GET"])
@auth.login_required
def health_check():
    return jsonify({"status": "OK"})

@app.route("/api/config", methods=["GET", "POST"])
@auth.login_required
def get_set_config():
    if request.method == "GET":
        return jsonify(INVERTER_CONFIG)
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            abort(400, "Invalid JSON payload")
        # Only update specific keys
        for key in ("inverter_id", "max_power_kw"):
            if key in data:
                INVERTER_CONFIG[key] = data[key]
        return jsonify({"message": "Configuration updated", "config": INVERTER_CONFIG})

@app.route("/api/firmware", methods=["POST"])
@auth.login_required
def upload_firmware():
    if "file" not in request.files:
        abort(400, "No file part in request")
    file = request.files["file"]
    if file.filename == "":
        abort(400, "No selected file")
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    # “Install” firmware by updating version string
    INVERTER_CONFIG["firmware_version"] = filename
    return jsonify({
        "message": f"Firmware '{filename}' uploaded successfully",
        "firmware_version": INVERTER_CONFIG["firmware_version"]
    })

if __name__ == "__main__":
    # Run over HTTPS using our self-signed certs
    app.run(host="0.0.0.0", port=5000,
            ssl_context=("certs/api.crt", "certs/api.key"))
