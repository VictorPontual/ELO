function abrirModal(projetoId) {
    const modal = document.getElementById(`modal-${projetoId}`);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function fecharModal(projetoId) {
    const modal = document.getElementById(`modal-${projetoId}`);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Adicionar event listeners quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Botões de abrir modal
    const botoesDetalhes = document.querySelectorAll('.btn-detalhes');
    botoesDetalhes.forEach(botao => {
        botao.addEventListener('click', function() {
            const projetoId = this.getAttribute('data-projeto-id');
            abrirModal(projetoId);
        });
    });
    
    // Botões de fechar modal
    const botoesFechar = document.querySelectorAll('.close');
    botoesFechar.forEach(botao => {
        botao.addEventListener('click', function() {
            const projetoId = this.getAttribute('data-projeto-id');
            fecharModal(projetoId);
        });
    });
});

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Fechar modal com tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
});
