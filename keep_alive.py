from flask import Flask
from threading import Thread
from waitress import serve
import os

app = Flask('')

@app.route('/')
def home():
    return "¡El bot de fútbol está vivo y optimizado para producción!"

def run():
    # Detecta el puerto de Render de forma dinámica
    port = int(os.environ.get("PORT", 10000))
    # Usamos serve() de waitress para eliminar el Warning de desarrollo
    serve(app, host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
