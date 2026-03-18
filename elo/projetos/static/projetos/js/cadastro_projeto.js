document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.projeto-form');
    if (!form) {
        return;
    }
    
    // Validação básica antes de enviar
    form.addEventListener('submit', function(e) {
        const titulo = document.querySelector('#id_titulo');
        const dataEntSig = document.querySelector('#id_data_ent_sig');
        const dataLibAnalise = document.querySelector('#id_data_lib_analise');
        const dataAprovacaoInst = document.querySelector('#id_data_aprovacao_inst');
        const inicioColeta = document.querySelector('#id_inicio_coleta');
        
        if (!titulo.value.trim()) {
            e.preventDefault();
            alert('Por favor, preencha o título do projeto.');
            titulo.focus();
            return false;
        }

        if (dataEntSig && dataEntSig.value) {
            const entradaSig = new Date(dataEntSig.value);

            if (dataLibAnalise && dataLibAnalise.value && new Date(dataLibAnalise.value) <= entradaSig) {
                e.preventDefault();
                alert('A Data de Liberação para Análise deve ser posterior à Data de Entrada no SIG.');
                dataLibAnalise.focus();
                return false;
            }

            if (dataAprovacaoInst && dataAprovacaoInst.value && new Date(dataAprovacaoInst.value) <= entradaSig) {
                e.preventDefault();
                alert('A Data de Aprovação Institucional deve ser posterior à Data de Entrada no SIG.');
                dataAprovacaoInst.focus();
                return false;
            }

            if (inicioColeta && inicioColeta.value && new Date(inicioColeta.value) <= entradaSig) {
                e.preventDefault();
                alert('A data de Início da Coleta deve ser posterior à Data de Entrada no SIG.');
                inicioColeta.focus();
                return false;
            }
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
    const dataEntSig = document.querySelector('#id_data_ent_sig');
    const dataLibAnalise = document.querySelector('#id_data_lib_analise');
    const dataAprovacaoInst = document.querySelector('#id_data_aprovacao_inst');
    
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

    if (dataEntSig && dataLibAnalise) {
        dataLibAnalise.addEventListener('change', function() {
            if (dataEntSig.value && dataLibAnalise.value) {
                if (new Date(dataLibAnalise.value) <= new Date(dataEntSig.value)) {
                    alert('A Data de Liberação para Análise deve ser posterior à Data de Entrada no SIG.');
                    dataLibAnalise.value = '';
                }
            }
        });
    }

    if (dataEntSig && dataAprovacaoInst) {
        dataAprovacaoInst.addEventListener('change', function() {
            if (dataEntSig.value && dataAprovacaoInst.value) {
                if (new Date(dataAprovacaoInst.value) <= new Date(dataEntSig.value)) {
                    alert('A Data de Aprovação Institucional deve ser posterior à Data de Entrada no SIG.');
                    dataAprovacaoInst.value = '';
                }
            }
        });
    }

    if (dataEntSig && inicioColeta) {
        inicioColeta.addEventListener('change', function() {
            if (dataEntSig.value && inicioColeta.value) {
                if (new Date(inicioColeta.value) <= new Date(dataEntSig.value)) {
                    alert('A data de Início da Coleta deve ser posterior à Data de Entrada no SIG.');
                    inicioColeta.value = '';
                }
            }
        });
    }
});
