from flask import Flask, jsonify, render_template, request, redirect
from flask_cors import CORS
import docker
from routes.project_routes import projects_bp

app = Flask(__name__)
# Permitir CORS desde cualquier origen (o especificar localhost:*, localhost, etc.)
CORS(app, 
     resources={r"/*": {"origins": ["http://localhost", "http://localhost:*", "http://127.0.0.1", "http://127.0.0.1:*"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])

app.register_blueprint(projects_bp)

# Logging para debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.debug(f"Request: {request.method} {request.path}")
    logger.debug(f"Remote addr: {request.remote_addr}")

@app.route('/')
def home():
    #Login

    return redirect("http://localhost/projects")

@app.route('/projects', methods=['GET'])
def list_projects():

    # Simulamos una lista de proyectos para mostrar en la plantilla
    proyectos = []
    """
    proyectos = [
        {'id': 1, 'name': 'Sitio Web E-commerce', 'description': 'Tienda en línea con Flask', 'url': 'http://ecommerce.username.localhost:8000'},
        {'id': 2, 'name': 'App de Notas', 'description': 'Gestor de tareas pendientes', 'url': 'http://notes.username.localhost:8000'},
    ]
    """

    return render_template('projects.html', projects=proyectos)

if __name__ == '__main__':
    # Mostrar todas las rutas registradas
    logger.debug("Rutas registradas:")
    for rule in app.url_map.iter_rules():
        logger.debug(f"  {rule.rule} - Métodos: {rule.methods}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)