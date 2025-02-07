document.getElementById('testButton').addEventListener('click', function() {
    fetch('/api/test')
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').textContent = data.result;
        })
        .catch(error => {
            document.getElementById('result').textContent = 'Error: ' + error;
        });
});
