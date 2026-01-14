document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle (if needed later)
    console.log('ELO System loaded');
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('header nav ul li a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#3498db';
        }
    });
});
