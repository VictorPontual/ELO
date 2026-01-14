document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Formulário de cadastro enviado');
        });
        
        const passwordFields = form.querySelectorAll('input[type="password"]');
        if (passwordFields.length === 2) {
            passwordFields[1].addEventListener('blur', function() {
                if (passwordFields[0].value !== passwordFields[1].value) {
                    this.setCustomValidity('As senhas não coincidem');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
    }
});
