from flask import Blueprint, request
import sys, os
from services.project_services import crear_proyecto

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects/create', methods=['POST'])
def create_project():
    data = request.get_json()
    user_id=1001 #user_id = session.get('user_id')
    username= "testuser" #username = session.get('username')
    ids = crear_proyecto(data, user_id, username)
    return {"ids": ids}
