const express = require('express');
const fetch = require('node-fetch');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('.')); // Phục vụ các tệp tĩnh như index.html

// API Key cho Gemini API (nhúng trong backend, không để lộ trong JavaScript)
const GEMINI_API_KEY = "AIzaSyAAQQI-5F6bXNOExuIlxlJ2AEdOOcDSDAA";

// Hệ thống hướng dẫn cho AI
const systemPrompt = "Bạn là một AI hướng dẫn, được thiết kế để giúp trẻ em học tập và giải quyết vấn đề bằng cách cung cấp gợi ý hoặc hướng dẫn từng bước. Không cung cấp đáp án cuối cùng. Thay vào đó, hãy đưa ra các bước, câu hỏi gợi mở hoặc mẹo để trẻ tự tìm ra câu trả lời. Sử dụng ngôn ngữ đơn giản, thân thiện, vui vẻ và khuyến khích. Trả lời bằng tiếng Việt.";

// API endpoint để xử lý tin nhắn
app.post('/chat', async (req, res) => {
    const { message } = req.body;

    if (!message) {
        return res.status(400).json({ error: 'Vui lòng gửi câu hỏi!' });
    }

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            { "text": systemPrompt },
                            { "text": "Câu hỏi: " + message }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                    "responseMimeType": "text/plain"
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Lỗi HTTP: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();

        if (data && data.candidates && data.candidates.length > 0 && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts.length > 0) {
            const reply = data.candidates[0].content.parts[0].text;
            res.json({ reply });
        } else {
            throw new Error('Phản hồi từ API không chứa nội dung hợp lệ.');
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server chạy trên http://localhost:${port}`);
});