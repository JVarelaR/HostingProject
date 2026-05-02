async function enviarCrearProyecto(projectData) {
    // TODO Mostrar estado de carga mientras se procesa la solicitud

    try {
        console.log('Enviando datos al servidor:', projectData);
        console.log('URL destino: /projects/create');
        
        const response = await fetch('/projects/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });

        console.log('Response received:', response.status, response.statusText);

        if (!response.ok) {
            console.error('Response status:', response.status, response.statusText);
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
            } catch (e) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
        }

        const result = await response.json();
        
        // El resultado contendrá la lista de IDs de contenedores
        console.log('Proyecto desplegado con éxito. IDs:', result.ids);
        
        alert(`Proyecto creado. Identificadores: ${result.ids.join(', ')}`);
        
        // Cerrar dialog después de crear
        dialog.close();

    } catch (error) {
        console.error('Error en la solicitud:', error);
        alert('Hubo un error al procesar el despliegue: ' + error.message);
    }
}



// --- Uso con un evento de formulario ---
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#formularioCrearProyecto');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Mapeo de datos según lo que espera tu función crear_proyecto en Python
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
