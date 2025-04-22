const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Hello, World!'); // Updated response message
});

const PORT = 3002; // Change to a different port
app.listen(PORT, () => {
    console.log(`Simple server is running on port ${PORT}`);
});