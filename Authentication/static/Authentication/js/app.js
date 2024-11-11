document.querySelectorAll('.change-content-button').forEach(button => {
    button.addEventListener('click', function() {
        var headline = this.getAttribute('data-headline');
        var text = this.getAttribute('data-text');  
        var image = this.getAttribute('data-image');

        document.getElementById('headline').textContent = "Find out more about " + headline;
        document.getElementById('functionality-text').textContent = text;
        document.getElementById('functionality-image').src = image;
        
        document.getElementById('about-functionality').scrollIntoView({ behavior: 'smooth' });
    })
})