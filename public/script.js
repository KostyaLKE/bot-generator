 document.getElementById('generateBtn').addEventListener('click', async () => {
    const newsText = document.getElementById('newsText').value;
    const socialNetworks = Array.from(document.querySelectorAll('input[name="social"]:checked'))
        .map(checkbox => checkbox.value);
  const otherName = document.getElementById("otherName").value
    const data = { newsText, socialNetworks, otherName };

    try {
        const response = await fetch('/api/posts/generate', { // Измененный URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        displayResult(result);

    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('result').innerText = 'Произошла ошибка при генерации.';
    }
});

function displayResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ''; // Очищаем предыдущие результаты

    for (const socialNetwork in result) {
        const postDiv = document.createElement('div');
        postDiv.innerHTML = `<strong>${socialNetwork}:</strong><p>${result[socialNetwork]}</p>`;
        resultDiv.appendChild(postDiv);
    }
}