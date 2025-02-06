prompt = f"Сгенерируй пост для {network_name} на основе текста: {news_text}"
try:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    generated_text = response.choices[0].text.strip()
    results[network_name] = generated_text

except openai.error.OpenAIError as e:
    print(f"OpenAI API error: {e}")
    results[network_name] = f"Ошибка при генерации текста для {network_name}: {e}"
except Exception as e:
    print(f"Unexpected error during text generation: {e}")
    results[network_name] = f"Непредвиденная ошибка при генерации текста для {network_name}: {e}"