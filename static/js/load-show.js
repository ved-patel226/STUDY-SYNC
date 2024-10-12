document.addEventListener('DOMContentLoaded', function () {
    const loadShow = document.querySelector('.load-show');
    const loader = document.querySelector('l-bouncy');
    const screenOverlay = document.querySelector('#screen');
    const body = document.body;

    loadShow.addEventListener('click', function () {
        loader.style.display = 'block';
        screenOverlay.style.display = 'block';
        
        body.classList.add('overflow-hidden');
        
        setTimeout(() => {
            loader.style.display = 'none';
            screenOverlay.style.display = 'none';
            body.classList.remove('overflow-hidden');
        }, 100000);
    });
});
