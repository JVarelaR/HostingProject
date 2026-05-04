from flask import Blueprint, request, current_app
import sys, os, logging
from services.project_services import crear_proyecto
from services.docker_services import detener_contenedor, iniciar_contenedor, eliminar_contenedor

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects/create', methods=['POST'])
def create_project():
    data = request.get_json()
    logging.info(f"Datos recibidos: {data}")
    # TODO aqui se debe obtener el user_id y username del usuario logueado desde session o token
    user_id = 1001  # user_id = session.get('user_id')
    username = current_app.config.get('DEFAULT_USERNAME', 'testuser')
    logging.info(f"Creando proyecto para user {username}: {data['nombre']}")
    result = crear_proyecto(data, user_id, username)
    
    if isinstance(result, dict) and "error" in result:
        logging.error(f"Error al crear proyecto: {result['error']}")
        return {"error": result["error"]}, 500
    
    logging.info(f"Proyecto creado exitosamente: {result}")
    return {"ids": result}

@projects_bp.route('/projects/stop', methods=['POST'])
def stop_project():
    data = request.get_json()
    tipo = data.get('tipo')
    identificador = data.get('id')
    ruta_repo = data.get('ruta_repo')
    res = detener_contenedor(tipo, identificador, ruta_repo)
    if res: return {"message": "Contenedor detenido exitosamente"}
    return {"message": "Error al detener el contenedor"}, 500

@projects_bp.route('/projects/start', methods=['POST'])
def start_project():
    data = request.get_json()
    tipo = data.get('tipo')
    identificador = data.get('id')
    ruta_repo = data.get('ruta_repo')
    res = iniciar_contenedor(tipo, identificador, ruta_repo)
    if res: return {"message": "Contenedor iniciado exitosamente"}
    return {"message": "Error al iniciar el contenedor"}, 500

@projects_bp.route('/projects/delete', methods=['POST'])
def delete_project():
    data = request.get_json()
    tipo = data.get('tipo')
    identificador = data.get('id')
    ruta_repo = data.get('ruta_repo')
    res = eliminar_contenedor(tipo, identificador, ruta_repo)
    if res: return {"message": "Contenedor eliminado exitosamente"}
    return {"message": "Error al eliminar el contenedor"}, 500