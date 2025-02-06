// public/script.js

document.getElementById('generate-button').addEventListener('click', function() {
    // ... (другой код) ...
    const newsText = document.getElementById('news-text').value;
    const selectedSocialNetworks = document.querySelectorAll('input[name="social"]:checked');
    const socialNetworks = Array.from(selectedSocialNetworks).map(cb => cb.value);
    const otherName = document.getElementById('otherName').value;
    const action = document.getElementById('action-select').value;

    // ... (другой код, если нужен) ...

    const formData = new FormData(); // Используем FormData
    formData.append('newsText', newsText);
    socialNetworks.forEach(network => {
        formData.append('socialNetworks', network);
    });
    formData.append('otherName', otherName);
    formData.append('action', action);


    fetch('/api/text/generate', { // Убедись, что URL правильный
        method: 'POST',
        body: formData, // Отправляем FormData
    })
    .then(response => response.json())
    .then(data => {
        // ... (обработка ответа от сервера) ...
        if (data.error) {
             // Обработка ошибок
            displayError(data.error);
        } else {
            displayResults(data); // Отображение результатов
        }

    })
    .catch(error => {
        console.error('Error:', error);
        displayError("Произошла ошибка при отправке запроса.");
    });
});

function displayResults(results) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = ''; // Очищаем предыдущие результаты

    for (const network in results) {
        const resultItem = document.createElement('div');
        resultItem.classList.add('result-item');

        const networkHeader = document.createElement('h3');
        networkHeader.textContent = network;
        resultItem.appendChild(networkHeader);

        const textParagraph = document.createElement('p');
        textParagraph.textContent = results[network];
        resultItem.appendChild(textParagraph);

        resultsContainer.appendChild(resultItem);
    }
}
function displayError(message) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = ''; // Очистить предыдущие результаты

    const errorDiv = document.createElement('div');
    errorDiv.classList.add('error-message');
    errorDiv.textContent = message;
    resultsContainer.appendChild(errorDiv);
}


// Обработчик изменения селекта
document.getElementById('action-select').addEventListener('change', function() {
  const youtubeLinkInput = document.getElementById('youtube_link_input');
  if (this.value === 'edit_youtube_video') {
    youtubeLinkInput.style.display = 'block';
  } else {
    youtubeLinkInput.style.display = 'none';
  }
});