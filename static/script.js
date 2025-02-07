import { franc, francAll } from 'https://esm.sh/franc@6';

const newsTextarea = document.getElementById('news_text');
const textInfo = document.getElementById('text-info');
const platformCheckboxes = document.querySelectorAll('.platform-checkboxes input[type="checkbox"]');
const previewDiv = document.getElementById('preview');
const correctedTextDiv = document.getElementById('corrected-text');


const platformConfig = {
  "twitter": { "max_length": 280, "prefix": "🚀 ", "suffix": " #BreakingNews" },
  "instagram": { "max_length": 150, "prefix": "📸 ", "suffix": "\n\n#news #trending #instagood" },
  "telegram": { "max_length": 400, "prefix": "🔹 ", "suffix": "\n\n📢 Подписывайтесь на канал!" },
  "facebook": { "max_length": 500, "prefix": "📰 ", "suffix": "\n\n#news #facebook" },
  "tiktok": { "max_length": 150, "prefix": "🎵 ", "suffix": "\n\n#news #foryou #fyp" },
  "youtube": { "max_length": 300, "prefix": "▶️ ", "suffix": "\n\n#news #video #youtube" },
  "pinterest": { "max_length": 500, "prefix": "📌 ", "suffix": "\n\n#news #pin #pinterest" },
};

function updateTextInfo() {
  const text = newsTextarea.value;
  const charCount = text.length;

  const detectedLanguages = francAll(text, { minLength: 3, only: ['eng', 'rus', 'ukr'] });
  let languages = [];
  if (detectedLanguages.length > 0 && detectedLanguages[0][0] !== 'und') {
    detectedLanguages.forEach(element => {
      if (element[0] === 'ukr') { languages.push('Украинский') }
      else if (element[0] === 'rus') { languages.push('Русский') }
      else if (element[0] === 'eng') { languages.push('Английский') }
    });
  }
  else { languages.push('Не определен'); }

  let infoText = `Символов: ${charCount}`;
  if (languages.length > 1) { infoText += `, Языки: ${languages.join(', ')}`; }
  else { infoText += `, Язык: ${languages[0]}`; }
  textInfo.textContent = infoText;
}

function updatePlatformLimits() {
  platformCheckboxes.forEach(checkbox => {
    const platform = checkbox.value;
    const config = platformConfig[platform];
    if (!config) return;

    let maxLength = config.max_length;
    if (config.prefix) {
      maxLength -= config.prefix.length;
    }
    if (config.suffix) {
      maxLength -= config.suffix.length;
    }

    const text = newsTextarea.value;
    const remaining = maxLength - text.length;

    let remainingSpan = checkbox.parentNode.querySelector('.remaining-chars');
    if (!remainingSpan) {
      remainingSpan = document.createElement('span');
      remainingSpan.classList.add('remaining-chars');
      checkbox.parentNode.appendChild(remainingSpan);
    }

    remainingSpan.textContent = ` (${remaining} симв.)`;

    if (remaining < 0) {
      remainingSpan.style.color = 'red';
    } else if (remaining < maxLength * 0.2) {
      remainingSpan.style.color = 'orange';
    } else {
      remainingSpan.style.color = 'green';
    }
  });
}

function updatePreview() {
  const text = newsTextarea.value;
  let previewHTML = '';

  platformCheckboxes.forEach(checkbox => {
    if (checkbox.checked) {
      const platform = checkbox.value;
      const config = platformConfig[platform];
      if (!config) return;

      let generatedText = text;
      let maxLength = config.max_length;

      if (config.prefix) {
        maxLength -= config.prefix.length;
        generatedText = config.prefix + generatedText;
      }
      if (config.suffix) {
        maxLength -= config.suffix.length;
        generatedText = generatedText + config.suffix;
      }

      generatedText = generatedText.substring(0, maxLength);

      previewHTML += `<div class="mb-2"><strong>${platform}:</strong> ${generatedText}</div>`;
    }
  });

  previewDiv.innerHTML = previewHTML;
}

async function checkSpelling(text) {
  const apiUrl = 'https://speller.yandex.net/services/spellservice.json/checkText';
  const params = new URLSearchParams();
  params.append('text', text);
  params.append('options', 518);
  params.append('format', 'plain');

  const detectedLanguages = francAll(text, { minLength: 3, only: ['eng', 'rus', 'ukr'] });
  let lang = 'ru,en';
  if (detectedLanguages.length > 0 && detectedLanguages[0][0] !== 'und') {
    if (detectedLanguages[0][0] === 'ukr') { lang = 'uk,en'; }
  }
  params.append('lang', lang);


  try {
    const response = await fetch(`${apiUrl}?${params.toString()}`);
    if (!response.ok) {
      console.error("Speller API error:", response.status, response.statusText);
      return;
    }
    const data = await response.json();

    let correctedText = text;
    for (const error of data) {
      if (error.s && error.s.length > 0) {
        const originalWord = error.word;
        const correctedWord = error.s[0];
        const regex = new RegExp(originalWord.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
        correctedText = correctedText.replace(regex, `<span class="spelling-suggestion" title="Предполагаемое исправление: ${correctedWord}">${originalWord}</span>`);
      }
    }
    if (data.length > 0) {
      correctedTextDiv.innerHTML = "<b>Исправленный текст: </b>" + correctedText;
      correctedTextDiv.style.display = 'block';
    }
    else { correctedTextDiv.style.display = 'none'; }

    return;

  } catch (error) {
    console.error("Error during spellcheck:", error);
    return;
  }
}

async function onNewsTextChange() {
  updateTextInfo();
  updatePlatformLimits();
  updatePreview();
  await checkSpelling(newsTextarea.value);
}
document.addEventListener('DOMContentLoaded', () => {
    newsTextarea.addEventListener('input', onNewsTextChange);
    platformCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', onNewsTextChange);
    });
    onNewsTextChange();
});