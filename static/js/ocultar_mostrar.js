function ocultarDiv(divId) {
            const div = document.getElementById(divId);
            gsap.to(div, {
                opacity: 0,
                duration: 0.1,
                onComplete: () => div.classList.add('hidden')
            });
        }

        function mostrarDiv(divId) {
            const div = document.getElementById(divId);
            div.classList.remove('hidden');
            gsap.to(div, {
                opacity: 1,
                duration: 0.1
            });
        }