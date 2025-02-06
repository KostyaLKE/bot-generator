document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.getElementById('generate-button');
    const actionSelect = document.getElementById('action-select');
    const youtubeLinkInput = document.getElementById('youtube_link_input');

    // Показываем/скрываем поле для ссылки на YouTube
    actionSelect.addEventListener('change', () => {
        if (actionSelect.value === 'edit_youtube_video') {
            youtubeLinkInput.style.display = 'block';
        } else {
            youtubeLinkInput.style.display = 'none';
        }
    });


    generateButton.addEventListener('click', async () => {
        const newsText = document.getElementById('news-text').value;
        const userImage = document.getElementById('user-image').files[0]; // Получаем файл
        const youtubeLink = document.getElementById('youtube-link').value;
        const action = actionSelect.value;
        const socialNetworks = Array.from(document.querySelectorAll('input[name="social"]:checked'))
            .map(checkbox => checkbox.value);
        const otherName = document.getElementById('otherName').value;

        const formData = new FormData(); // Используем FormData для отправки файла
        formData.append('newsText', newsText);
        formData.append('action', action);
        formData.append('youtubeLink', youtubeLink);

        // Добавляем socialNetworks как отдельные поля, т.к. FormData не поддерживает массивы напрямую
        socialNetworks.forEach(network => {
            formData.append('socialNetworks', network);
        });
        if(otherName) {
            formData.append('otherName', otherName)
        }


        if (userImage) {
            formData.append('userImage', userImage);
        }

        // Определяем URL на основе выбранного действия
        let url = '';
        if (action.startsWith('generate_text')) {
            url = '/api/text/generate';
        } else if (action.startsWith('generate_image') || action.includes('_image')) {
            url = '/api/image/generate';
        } else if (action.startsWith('generate_video') || action.includes('_video')) {
             url = '/api/video/generate';
        } else if (action === 'edit_youtube_video') {
            url = '/api/youtube/edit';
        } else {
            console.error("Неизвестное действие:", action);
            alert("Ошибка: Неизвестное действие");
            return;
        }


        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData, // Отправляем FormData
                // headers не нужны, т.к. FormData сам устанавливает Content-Type: multipart/form-data
            });

            if (!response.ok) {
                const errorData = await response.json();  // Пытаемся получить JSON с ошибкой
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`); // Выводим сообщение об ошибке
            }

            const result = await response.json();
            displayResults(result, action);

        } catch (error) {
            console.error('Ошибка:', error);
            displayError(error.message); // Показываем сообщение об ошибке пользователю
        }
    });

     function displayResults(results, action) {
        const container = document.getElementById('results-container');
        container.innerHTML = ''; // Очищаем предыдущие результаты

        // В зависимости от типа контента (текст, изображение, видео),
        // отображаем результаты по-разному.
        if (action.startsWith("generate_text") && typeof results === 'object') {
            // Обработка текстовых результатов
            for (const [socialNetwork, text] of Object.entries(results)) {
              const resultDiv = document.createElement('div');
              resultDiv.classList.add('result-item');
              resultDiv.innerHTML = `<h3>${socialNetwork}</h3><p>${text}</p>`;
              container.appendChild(resultDiv);
            }
        } else if (action.includes("_image")  && results.imageUrl) {
                // Обработка результатов с изображением
                const img = document.createElement('img');
                img.src = results.imageUrl;
                img.alt = 'Сгенерированное изображение';
                img.classList.add('result-image');
                container.appendChild(img);
                //Если есть текст
                if(results.text){
                    displayResults(results.text, "generate_text")
                }

        } else if (action.includes("_video") && results.videoUrl) {
                const video = document.createElement('video');
                video.src = results.videoUrl;
                video.controls = true;
                video.classList.add('result-video');
                container.appendChild(video);
                 //Если есть текст
                if(results.text){
                    displayResults(results.text, "generate_text")
                }
        } else if(action ==="edit_youtube_video" && results.videoUrl){
            //Отображение смонтированного видео
            const video = document.createElement('video');
                video.src = results.videoUrl;
                video.controls = true;
                video.classList.add('result-video');
                container.appendChild(video);
        }

        else {
            // Если пришел простой текст (например, сообщение об ошибке)
            container.textContent = results;
        }
    }

    function displayError(message) {
        const container = document.getElementById('results-container');
        container.innerHTML = `<div class="error-message">${message}</div>`;
    }

});