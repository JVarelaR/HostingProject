import {dialog} from './open_dialog.js';

async function enviarCrearProyecto(projectData) {
    const loadingElement = document.getElementById('loading-indicator');
    const submitButton = document.querySelector('#formularioCrearProyecto button[type="submit"]');
    const closeButton = document.getElementById('closeProjectDialog');

    // Mensaje Cargando
    if (submitButton && loadingElement) {
        submitButton.classList.add('hidden');
        loadingElement.classList.remove('hidden');
        loadingElement.style.display = 'flex';
    }

    if (closeButton) closeButton.disabled = true;

    try {
        const response = await fetch('/projects/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}`);
        }

        const result = await response.json();
        alert(`Proyecto creado. Identificadores: ${result.ids.join(', ')}`);
        dialog.close();

    } catch (error) {
        alert('Hubo un error: ' + error.message);
    } finally {
        // Restaurar estado del botón
        if (submitButton && loadingElement) {
            loadingElement.classList.add('hidden'); // Oculta carga
            loadingElement.style.display = 'none';
            submitButton.classList.remove('hidden'); // Muestra el botón original
        }

        if (closeButton) closeButton.disabled = false;
    }
}




//Uso con formulario
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#formularioCrearProyecto');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const data = {
                nombre: formData.get('name'),           
                descripcion: formData.get('description'), 
                repo_url: formData.get('url'),          
                puerto: parseInt(formData.get('puerto')),
                tipoDespliegue: formData.get('docker_type')
            };

            await enviarCrearProyecto(data);
        });
    } else {
        console.warn('Formulario #formularioCrearProyecto no encontrado');
    }
});
