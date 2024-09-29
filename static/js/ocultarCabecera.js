let lastScrollTop = 0;
const header = document.querySelector('.cabecera');

window.addEventListener('scroll', function () {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop > lastScrollTop && scrollTop > 150) {
        // Desplazamiento hacia abajo después de 100px
        if (!header.classList.contains('hidden')) {
            header.classList.add('hidden');
        }
    } else if (scrollTop < lastScrollTop) {
        // Desplazamiento hacia arriba
        if (header.classList.contains('hidden')) {
            header.classList.remove('hidden');
        }
    }
    lastScrollTop = scrollTop;
});
