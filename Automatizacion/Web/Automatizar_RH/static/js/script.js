// script.js
document.addEventListener("DOMContentLoaded", function() {
    // 1. Manejo del formulario y loader
    const form = document.getElementById("process-form");
    const loader = document.getElementById("loader");
    
    if (form && loader) {
        form.addEventListener("submit", async function(event) {
            event.preventDefault(); // Previene el envío tradicional
            loader.style.display = "block"; // Muestra el loader
            
            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                });

                if (response.ok) {
                    window.location.href = "/results"; // Redirige si es exitoso
                } else {
                    alert("Error en el proceso");
                    loader.style.display = "none";
                }
            } catch (error) {
                console.error("Error:", error);
                loader.style.display = "none";
            }
        });
    }

    // 2. Manejo del drag and drop
    const dropzone = document.getElementById("dropzone");
    const fileInput1 = document.getElementById("form_data_file");
    const fileInput2 = document.getElementById("local_db_file");

    if (dropzone) {
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
    }

    // 3. Manejo del botón de limpieza
    const cleanupBtn = document.getElementById("cleanup-btn");
    if (cleanupBtn) {
        cleanupBtn.addEventListener("click", function() {
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
    }

    // 4. Manejo del stream de logs (si existe el contenedor)
    const logOutput = document.getElementById("log-output");
    if (logOutput) {
        const eventSource = new EventSource("/logs");
        
        eventSource.onmessage = function(event) {
            logOutput.textContent += event.data + "\n";
            logOutput.scrollTop = logOutput.scrollHeight;
        };

        eventSource.onerror = function() {
            console.error("Error en la conexión con el stream de logs.");
            eventSource.close();
        };
    }
});