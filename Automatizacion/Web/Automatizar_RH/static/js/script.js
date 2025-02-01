document.addEventListener("DOMContentLoaded", function() {
    const logOutput = document.getElementById("log-output");
    const eventSource = new EventSource("/logs");

    eventSource.onmessage = function(event) {
        logOutput.textContent += event.data + "\n";
        logOutput.scrollTop = logOutput.scrollHeight; // Auto-scroll hacia abajo
    };

    eventSource.onerror = function() {
        console.error("Error en la conexión de logs.");
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
