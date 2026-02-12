document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.projeto-form');
    
    // Validação básica antes de enviar
    form.addEventListener('submit', function(e) {
        const titulo = document.querySelector('#id_titulo');
        
        if (!titulo.value.trim()) {
            e.preventDefault();
            alert('Por favor, preencha o título do projeto.');
            titulo.focus();
            return false;
        }
    });

    // Adicionar feedback visual aos campos obrigatórios
    const requiredFields = form.querySelectorAll('input[required], textarea[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.style.borderColor = '#e74c3c';
            } else {
                this.style.borderColor = '#27ae60';
            }
        });
    });

    // Auto-hide alerts depois de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Validação de datas (fim não pode ser antes do início)
    const inicioColeta = document.querySelector('#id_inicio_coleta');
    const fimColeta = document.querySelector('#id_fim_coleta');
    
    if (inicioColeta && fimColeta) {
        fimColeta.addEventListener('change', function() {
            if (inicioColeta.value && fimColeta.value) {
                if (new Date(fimColeta.value) < new Date(inicioColeta.value)) {
                    alert('A data de fim da coleta não pode ser anterior à data de início.');
                    fimColeta.value = '';
                }
            }
        });
    }
});
