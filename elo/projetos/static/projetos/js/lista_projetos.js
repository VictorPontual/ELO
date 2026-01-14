document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('table');
    
    if (table) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function() {
                console.log('Projeto clicado:', this.cells[0].textContent);
            });
        });
        
        console.log('Lista de projetos carregada');
    }
});
