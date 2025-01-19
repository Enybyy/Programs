// Selecciona el botón y el contenedor del loader
const button = document.getElementById("start_process");
const loaderContainer = document.getElementById("loader-container");

// Agrega un evento al botón
button.addEventListener("click", () => {
    console.log("Botón clickeado, mostrando loader...");

    // Muestra el loader
    loaderContainer.classList.add("active");

    // Simula un tiempo de espera (ej. 3 segundos)
    setTimeout(() => {
        console.log("Ocultando loader...");
        
        // Oculta el loader
        loaderContainer.classList.remove("active");
    }, 3000); // 3000 milisegundos = 3 segundos
});
