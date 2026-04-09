"""Internal API - simulates a sensitive internal service."""

from flask import Flask, request, jsonify

app = Flask(__name__)

INTERNAL_KEY = "s3cret-internal-key-2024"

FAKE_USERS = [
    {"id": 1, "username": "admin", "email": "admin@corp.local", "role": "superadmin", "password_hash": "$2b$12$LJ3m5...fakehash1"},
    {"id": 2, "username": "jdoe", "email": "jdoe@corp.local", "role": "developer", "password_hash": "$2b$12$9Kp2...fakehash2"},
    {"id": 3, "username": "analyst", "email": "analyst@corp.local", "role": "analyst", "password_hash": "$2b$12$Xm7q...fakehash3"},
    {"id": 4, "username": "dbadmin", "email": "dbadmin@corp.local", "role": "dba", "password_hash": "$2b$12$Rn4w...fakehash4"},
    {"id": 5, "username": "svc-account", "email": "svc@corp.local", "role": "service", "password_hash": "$2b$12$Hp8t...fakehash5"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "internal-api"})


@app.route("/admin/users", methods=["GET"])
def admin_users():
    key = request.headers.get("X-Internal-Key", "")
    if key != INTERNAL_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"users": FAKE_USERS})


@app.route("/admin/config", methods=["GET"])
def admin_config():
    key = request.headers.get("X-Internal-Key", "")
    if key != INTERNAL_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({
        "db_host": "internal-db",
        "db_port": 3306,
        "db_user": "root",
        "db_password": "rootpass",
        "db_name": "secrets",
        "api_version": "1.0.0",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
