const express = require('express');
const router = express.Router();
const postController = require('../controllers/postController');

router.post('/generate', postController.generatePosts);

module.exports = router;