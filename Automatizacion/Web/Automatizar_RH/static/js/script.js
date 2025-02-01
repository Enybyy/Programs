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

document.addEventListener("DOMContentLoaded", function() {
    const dropzone = document.getElementById("dropzone");
    const fileInput1 = document.getElementById("form_data_file");
    const fileInput2 = document.getElementById("local_db_file");

    dropzone.addEventListener("click", () => {
        fileInput1.click();
    });

    dropzone.addEventListener("dragover", (event) => {
        event.preventDefault();
        dropzone.style.background = "#e2e6ea";
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.style.background = "#f8f9fa";
    });

    dropzone.addEventListener("drop", (event) => {
        event.preventDefault();
        dropzone.style.background = "#f8f9fa";
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            fileInput1.files = files;
        }
    });
});
