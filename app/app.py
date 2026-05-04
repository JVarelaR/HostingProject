from flask import Flask, jsonify, render_template, request, redirect
from flask_cors import CORS
import docker, os
from routes.project_routes import projects_bp

app = Flask(__name__)
# TODO Tomar Username del usuario autenticado
app.config['DEFAULT_USERNAME'] = os.getenv('DEFAULT_USERNAME', 'testuser') # Valor por defecto para desarrollo

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
    # TODO Login

    return redirect("http://localhost/projects")

@app.route('/projects', methods=['GET'])
def list_projects():
    proyectos = []

    # TODO Listar los proyectos activos asociados al usuario logueado

    """
    # Ejemplo estático
    proyectos = [
        {'id': 1, 'name': 'Sitio Web E-commerce', 'description': 'Tienda en línea con Flask', 'url': 'http://ecommerce.username.localhost:8000'},
        {'id': 2, 'name': 'App de Notas', 'description': 'Gestor de tareas pendientes', 'url': 'http://notes.username.localhost:8000'},
    ]
    """

    try:
        docker_client = docker.from_env()
        containers = docker_client.containers.list(all=True)

        for container in containers:
            labels = container.labels or {}
            url = None

            # Extraer URL de Traefik a partir de la regla Host(`...`)
            for label_key, label_value in labels.items():
                if label_key.startswith('traefik.http.routers.') and label_key.endswith('.rule'):
                    if 'Host(' in label_value:
                        url_candidate = label_value.split('Host(', 1)[1].rstrip(')')
                        url_candidate = url_candidate.strip('`')
                        if url_candidate.startswith('http'):
                            url = url_candidate
                        else:
                            url = f'http://{url_candidate}'
                        break

            proyectos.append({
                'id': container.id,
                'name': container.name,
                'description': labels.get('proyecto_owner', container.image.tags[0] if container.image.tags else 'Sin etiqueta'),
                'url': url or 'N/A',
                'state': container.status
            })
    except Exception as e:
        logger.error(f"Error al listar contenedores Docker: {e}")
        proyectos = []

    return render_template('projects.html', projects=proyectos, username=app.config['DEFAULT_USERNAME'])

if __name__ == '__main__':
    # Mostrar todas las rutas registradas
    logger.debug("Rutas registradas:")
    for rule in app.url_map.iter_rules():
        logger.debug(f"  {rule.rule} - Métodos: {rule.methods}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)