import docker, os, subprocess, shutil

client = docker.from_env()

# TODO Comprobar que el usuario es dueño de los contenedores que desea modificar

def crear_contenedor(tipo_despliegue, nombre, usuario, imagen, puerto, ruta_repo):
    project_identifier = f"{usuario}_{nombre}"

    # Verificar y crear la red si no existe
    network_name = "hosting_net"
    try:
        client.networks.get(network_name)
    except docker.errors.NotFound:
        print(f"Creando red {network_name}...")
        client.networks.create(network_name, driver="bridge")

    # Etiquetas de Traefik y gestión para el proxy inverso
    labels = {
        "traefik.enable": "true",
        "traefik.http.routers." + project_identifier + ".rule": f"Host(`{nombre}.{usuario}.localhost`)",
        "traefik.http.services." + project_identifier + ".loadbalancer.server.port": str(puerto),
        "proyecto_owner": usuario,
    }

    if tipo_despliegue == 'dockerfile':
        # Limpiar contenedor existente si hay
        try:
            existing_container = client.containers.get(project_identifier)
            existing_container.remove(force=True)
            print(f"Contenedor existente {project_identifier} eliminado.")
        except docker.errors.NotFound:
            pass  # No existe, continuar
        except Exception as e:
            print(f"Error al limpiar contenedor existente: {e}")

        try:
            print(f"Creando contenedor {project_identifier} con imagen {imagen}")
            container = client.containers.run(
                imagen,
                name=project_identifier,
                detach=True,
                network="hosting_net",
                mem_limit="256m", # Restricción de memoria exigida
                nano_cpus=500000000, # Restricción de CPU exigida
                labels=labels,
                restart_policy={"Name": "unless-stopped"}
            )
            print(f"Contenedor creado: {container.id}")
            return [container.id]
        except Exception as e:
            print(f"Error al crear contenedor: {e}")
            return f"Error al crear contenedor: {str(e)}"

    elif tipo_despliegue == 'docker-compose':
        try:
            # Detener y eliminar stack existente si hay
            print(f"Eliminando stack existente {project_identifier}")
            subprocess.run(
                ["docker-compose", "-p", project_identifier, "down", "--rmi", "all", "--volumes"],
                cwd=ruta_repo,
                check=False  # No fallar si no existe
            )
            print(f"Stack existente {project_identifier} eliminado.")

            # Levantamos el stack completo usando el identificador como nombre de proyecto
            print(f"Levantando stack {project_identifier}")
            subprocess.run(
                ["docker-compose", "-p", project_identifier, "up", "-d"],
                cwd=ruta_repo, 
                check=True
            )
            # Obtenemos los IDs de todos los contenedores creados por este proyecto
            containers = client.containers.list(all=True, filters={"label": f"com.docker.compose.project={project_identifier}"})
            print(f"Contenedores creados: {[c.id for c in containers]}")
            return [c.id for c in containers]
        except Exception as e:
            print(f"Error al crear stack docker-compose: {e}")
            return f"Error: {str(e)}"

def detener_contenedor(tipo, identificador, ruta_repo):
    #Identificador puede ser el ID del contenedor o el nombre del proyecto de Compose.

    try:
        if tipo == 'docker-compose' and ruta_repo:
            subprocess.run(["docker-compose", "-p", identificador, "stop"], cwd=ruta_repo, check=True)
        else:
            # Funciona para Dockerfile usando el primer ID de la lista
            container = client.containers.get(identificador[0] if isinstance(identificador, list) else identificador)
            container.stop()
        return True
    except Exception as e:
        print(f"Error al detener: {e}")
        return False

def iniciar_contenedor(tipo, identificador, ruta_repo):
    try:
        if tipo == 'docker-compose' and ruta_repo:
            subprocess.run(["docker-compose", "-p", identificador, "start"], cwd=ruta_repo, check=True)
        else:
            container = client.containers.get(identificador[0] if isinstance(identificador, list) else identificador)
            container.start()
        return True
    except Exception as e:
        print(f"Error al iniciar: {e}")
        return False

def eliminar_contenedor(tipo, identificador, ruta_repo):
    try:
        if tipo == 'docker-compose' and ruta_repo:
            subprocess.run(["docker-compose", "-p", identificador, "down", "--rmi", "all", "--volumes"], cwd=ruta_repo, check=True)
        else:
            target_id = identificador[0] if isinstance(identificador, list) else identificador
            container = client.containers.get(target_id)
            network = client.networks.get("hosting_net")
            network.disconnect(container, force=True)  # Desconectar antes de remover
            
            # Guardar el nombre de la imagen antes de borrar el contenedor
            image_tag = container.image.tags[0] if container.image.tags else None
            
            container.stop()
            container.remove()
            
            # Eliminar la imagen
            if image_tag:
                try:
                    client.images.remove(image=image_tag, force=True)
                except Exception as e:
                    print(f"Error al eliminar imagen {image_tag}: {e}")

        # Eliminar el repositorio físico 
        if ruta_repo and os.path.exists(ruta_repo):
            shutil.rmtree(ruta_repo)
            print(f"Repositorio eliminado en: {ruta_repo}")

        return True
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return False
    
def listar_estado_contenedores(projects_ids: list):
    # Container_ids es una lista de listas de IDs. Una lista por proyecto, cada una con los IDs de sus contenedores. Ej: [['id1', 'id2'], ['id3']])

    estados = []
    if not projects_ids: return estados

    for project_id in projects_ids:
        if not project_id: continue

        if len(project_id) == 1: # Caso Dockerfile
            try:
                container = client.containers.get(project_id[0])
                estados.append({
                    "ids": project_id,
                    "estado": container.status
                })
            except Exception:
                estados.append({"ids": project_id, "estado": "not_found"})
        
        else: # Caso Docker Compose
            estado_final = "running"
            for cid in project_id:
                try:
                    container = client.containers.get(cid)
                    if container.status != "running":
                        estado = container.status
                        break # Si encontramos un contenedor con estado diferente a "running", el estado del proyecto será ese
                except Exception:# Si el contenedor no existe, el stack está incompleto
                    estado_final = "incomplete"
                    break
            estados.append({
                "ids": project_id,
                "estado": estado_final
            })

    return estados