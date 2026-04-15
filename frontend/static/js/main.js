if (window.innerWidth > 992) {
    const cursor = new MouseFollower({
        skewing: 4,
    });
}

document.querySelector('.tvc-menu-burger').addEventListener('click', function() {
    this.classList.toggle('active');
    document.querySelector('.tvc-navigation-overlay').classList.toggle('active');
});


const links = document.querySelectorAll(".tvc-navigation-row a");
links.forEach((item) => {
    const navigationsText = item.text.trim()
    
    const wrappedText = navigationsText.split('').map((char) => {
        if (char === ' ') {
            return ' ';
        }
        return `<span data-cursor-stick>${char}</span>`;
    }).join('');

    item.innerHTML = wrappedText;
});


document.querySelector('.tvc-wc-stats-icon svg').addEventListener('click', function() {
    document.querySelector('.tvc-wc').classList.toggle('active');
});