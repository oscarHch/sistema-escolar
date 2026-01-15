document.addEventListener('DOMContentLoaded', function() {
    // 1. Convertir a MAYÚSCULAS automáticamente
    const inputsMayuscula = document.querySelectorAll('.mayuscula');
    
    inputsMayuscula.forEach(input => {
        input.addEventListener('input', function(e) {
            this.value = this.value.toUpperCase();
        });
    });

    // 2. Mostrar/ocultar detalle de discapacidad
    const checkDiscapacidad = document.getElementById('checkDiscapacidad');
    const detalleDiscapacidad = document.getElementById('detalleDiscapacidad');
    
    // Verificamos que existan los elementos antes de usarlos (para evitar errores)
    if (checkDiscapacidad && detalleDiscapacidad) {
        const textareaDiscapacidad = detalleDiscapacidad.querySelector('textarea');

        checkDiscapacidad.addEventListener('change', function() {
            if (this.checked) {
                detalleDiscapacidad.style.display = 'block';
                textareaDiscapacidad.required = true;
            } else {
                detalleDiscapacidad.style.display = 'none';
                textareaDiscapacidad.required = false;
                textareaDiscapacidad.value = '';
            }
        });
    }
});