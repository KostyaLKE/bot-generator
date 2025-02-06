const { OpenAI } = require('openai');
require('dotenv').config();

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

async function generateText(prompt) {
    try {
        const completion = await openai.chat.completions.create({
          messages: [{ role: 'user', content: prompt }],
          model: 'gpt-3.5-turbo',
        });
        //Изменения тут
        return completion.choices[0].message.content.split("---");
    } catch (error) {
        console.error('Ошибка при обращении к OpenAI API:', error);
        throw error; // Пробрасываем ошибку наверх
    }
}

module.exports = {
    generateText,
};