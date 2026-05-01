from flask import Flask, jsonify, render_template, request, redirect
from flask_cors import CORS
import docker

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost"}})

try:
    client = docker.from_env()
except Exception as e:
    print(f"Error de conexión: {e}")
    client = None

@app.route('/')
def home():
    #Login

    return redirect("http://localhost/projects")

@app.route('/projects', methods=['GET'])
def list_projects():

    # Simulamos una lista de proyectos para mostrar en la plantilla
    proyectos = []
    
    proyectos = [
        {'id': 1, 'name': 'Sitio Web E-commerce', 'description': 'Tienda en línea con Flask', 'url': 'http://ecommerce.username.localhost:8000'},
        {'id': 2, 'name': 'App de Notas', 'description': 'Gestor de tareas pendientes', 'url': 'http://notes.username.localhost:8000'},
    ]
    

    return render_template('projects.html', projects=proyectos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)