require('dotenv').config();
const express = require('express');
const path = require('path');
const axios = require('axios');
const app = express();

// Serve static files from the "static" directory
app.use(express.static(path.join(__dirname, 'static')));

app.use(express.json());

// Define a route for the root URL
app.get('/', (req, res) => {
    res.send('Hello, World!');
});

app.post('/api/chat', async (req, res) => {
    try {
        const response = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: "gpt-3.5-turbo",
            messages: req.body.messages,
            temperature: 0.7
        }, {
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
            }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3001; // Change to a different port
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});