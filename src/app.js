const express = require('express');
const path = require('path');
const postRoutes = require('./routes/postRoutes');

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, '../public'))); // Раздача статики из папки public

// Подключение маршрутов
app.use('/api/posts', postRoutes);

app.listen(port, () => {
    console.log(`Сервер запущен на порту ${port}`);
});