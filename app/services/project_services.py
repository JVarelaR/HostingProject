import subprocess, os
from .docker_services import crear_contenedor

def crear_proyecto(data, user_id, username):
    repo = data["repo_url"]
    nombre = data["nombre"]
    puerto = data["puerto"]
    tipoDespliegue = data["tipoDespliegue"]

    # 1. Definir rutas y nombres
    # Usamos username para la ruta física y para las etiquetas de Traefik
    rutaRepo = os.path.abspath(f"./tmp/{username}_{nombre}")
    imagen = None

    # 2. Clonar repo
    try:
        if os.path.exists(rutaRepo):
            subprocess.run(["rm", "-rf", rutaRepo]) # Limpiar si ya existe
        subprocess.run(["git", "clone", repo, rutaRepo], check=True)
    except Exception as e:
        return {"error": f"Fallo al clonar repositorio: {e}"}

    # 3. Construir imagen (Solo para Dockerfile)
    if tipoDespliegue == 'dockerfile':
        imagen = f"{username}_{nombre}".lower()
        subprocess.run(["docker", "build", "-t", imagen, rutaRepo], check=True)

    # 4. Levantar infraestructura en Docker
    # Esta función ahora devuelve una LISTA de IDs (TEXT[])
    ids_obtenidos = crear_contenedor(tipoDespliegue, nombre, username, imagen, puerto, rutaRepo)

    #TODO 5. Guardar en DB (Proyecto con IDs de contenedores asociados y user_id)

    return ids_obtenidos