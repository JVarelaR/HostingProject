import subprocess, os, shutil
from .docker_services import crear_contenedor

def crear_proyecto(data, user_id, username):
    repo = data["repo_url"]
    nombre = data["nombre"]
    puerto = data["puerto"]
    tipoDespliegue = data["tipoDespliegue"]

    # 1. Definir rutas y nombres
    # Usamos username para la ruta física y para las etiquetas de Traefik
    rutaRepo = os.path.abspath(f"/tmp/hosting/{username}_{nombre}")
    imagen = None

    try:
        # 2. Clonar repo
        if os.path.exists(rutaRepo):
            shutil.rmtree(rutaRepo)  # Limpiar si ya existe
        subprocess.run(["git", "clone", repo, rutaRepo], check=True)
    except Exception as e:
        return {"error": f"Fallo al clonar repositorio: {str(e)}"}

    try:
        # 3. Construir imagen (Solo para Dockerfile)
        if tipoDespliegue == 'dockerfile':
            imagen = f"{username}_{nombre}".lower()
            subprocess.run([
                "docker", "build", 
                "--no-cache", 
                "-t", imagen, 
                rutaRepo
            ], check=True)
    except Exception as e:
        return {"error": f"Fallo al construir imagen Docker: {str(e)}"}

    try:
        # 4. Levantar infraestructura en Docker
        ids_obtenidos = crear_contenedor(tipoDespliegue, nombre, username, imagen, puerto, rutaRepo) # Devuelve una LISTA de IDs o un string de error
        
        if isinstance(ids_obtenidos, str) and ids_obtenidos.startswith("Error"):
            return {"error": ids_obtenidos}
        
        #TODO 5. Guardar en DB (Proyecto con IDs de contenedores asociados y user_id)

        return ids_obtenidos
    except Exception as e:
        return {"error": f"Fallo al crear contenedor: {str(e)}"}