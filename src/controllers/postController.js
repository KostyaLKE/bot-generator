const openaiService = require('../services/openaiService');
const { createPrompt } = require('../utils/promptHelper');

async function generatePosts(req, res) {
    try {
        const { newsText, socialNetworks, otherName } = req.body;
        const prompt = createPrompt(newsText, socialNetworks, otherName);
        const generatedTexts = await openaiService.generateText(prompt);

        const result = {};
        // ... (Остальная часть логики обработки ответа от OpenAI - как в предыдущем варианте)
        if (socialNetworks.includes("twitter")) {
            result["Twitter"] = generatedTexts.shift()?.trim() || "Нет ответа для Twitter.";
        }
        if (socialNetworks.includes("youtube")) {
            result["YouTube"] = generatedTexts.shift()?.trim() || "Нет ответа для YouTube.";
        }
        if (socialNetworks.includes("tiktok")) {
            result["TikTok"] = generatedTexts.shift()?.trim() || "Нет ответа для TikTok.";
        }
        if (socialNetworks.includes("instagram")) {
            result["Instagram"] = generatedTexts.shift()?.trim() || "Нет ответа для Instagram.";
        }
        if (socialNetworks.includes("telegram")) {
            result["Telegram"] = generatedTexts.shift()?.trim() || "Нет ответа для Telegram.";
        }
        if (socialNetworks.includes("facebook")) {
            result["Facebook"] = generatedTexts.shift()?.trim() || "Нет ответа для Facebook.";
        }
        if (socialNetworks.includes("other")) {
            result[otherName] = generatedTexts.shift()?.trim() || `Нет ответа для ${otherName}.`;
        }

        res.json(result);
    } catch (error) {
        console.error('Ошибка в postController:', error);
        res.status(500).json({ error: 'Ошибка при генерации текста.' });
    }
}


module.exports = {
    generatePosts,
};