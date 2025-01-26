// Limpieza automática al cerrar/recargar
window.addEventListener('beforeunload', function(e) {
    fetch('/cleanup', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    }).catch(error => console.log('Error en limpieza automática:', error));
});

// Limpieza manual
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