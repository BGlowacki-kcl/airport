var backButton = document.getElementById('backButton');

backButton.addEventListener('click', function(e) {
    e.preventDefault();
    history.back();
});