document.addEventListener('DOMContentLoaded', function() {
    console.log('ELO System loaded');
    
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('header nav ul li a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#3498db';
        }
    });
});
