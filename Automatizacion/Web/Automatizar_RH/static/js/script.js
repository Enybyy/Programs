document.addEventListener("DOMContentLoaded", function() {
    const logOutput = document.getElementById("log-output");
    if (!logOutput) return; // Asegurarse de que existe el contenedor

    const eventSource = new EventSource("/logs");

    eventSource.onmessage = function(event) {
        // Agrega el nuevo mensaje y auto-scroll hacia abajo
        logOutput.textContent += event.data + "\n";
        logOutput.scrollTop = logOutput.scrollHeight;
    };

    eventSource.onerror = function() {
        console.error("Error en la conexión con el stream de logs.");
        eventSource.close();
    };
});

document.getElementById('cleanup-btn').addEventListener('click', function() {
    fetch('/cleanup', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            alert('¡Todos los archivos temporales han sido eliminados!');
        } else {
            alert('Error: No se pudieron eliminar los archivos');
        }
    })
    .catch(error => console.error('Error:', error));
});

document.addEventListener("DOMContentLoaded", function() {
    // Manejo del loader al enviar el formulario
    const form = document.getElementById("process-form");
    const loader = document.getElementById("loader");
    
    form.addEventListener("submit", function(event) {
        // Muestra el loader
        loader.style.display = "block";
    });
    
    // (Aquí se puede agregar más código, si es necesario, para otros eventos)
});