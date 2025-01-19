// Esperamos a que el DOM se cargue
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el formulario y el loader
    const form = document.getElementById('process-form');
    const loader = document.getElementById('loader');
  
    // Inicialmente, ocultar el loader
    loader.style.display = 'none';
  
    // Escuchar el evento submit del formulario
    form.addEventListener('submit', function(event) {
      // Prevenir el comportamiento predeterminado (para hacer pruebas sin enviar datos aún)
      event.preventDefault();
  
      // Mostrar el loader
      loader.style.display = 'flex';
  
      // Aquí es donde realizarías la lógica de enviar el formulario
      // Si usas fetch o AJAX, esta es la parte donde enviarías el formulario sin recargar la página.
  
      // Simular un retraso para mostrar el loader (por ejemplo, 3 segundos)
      setTimeout(function() {
        // Aquí es donde después de procesar, ocultarías el loader
        loader.style.display = 'none';
  
        // Ahora puedes simular que el formulario fue procesado y se redirige a otra página (si es necesario)
        // window.location.href = '/resultados'; // redirigir a la página de resultados (si es necesario)
      }, 3000); // El tiempo simulado de procesamiento
    });
});
