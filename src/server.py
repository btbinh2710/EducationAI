import http.server
import socketserver
import json
import urllib.request
import os
from dotenv import load_dotenv

# Đọc tệp .env từ thư mục gốc (C:\AI_Tutor)
load_dotenv(dotenv_path="../.env")

# Cấu hình cổng
PORT = 3000

# Lấy API Key từ biến môi trường
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Hệ thống hướng dẫn cho AI
SYSTEM_PROMPT = "Bạn là một AI hướng dẫn, được thiết kế để giúp trẻ em học tập và giải quyết vấn đề bằng cách cung cấp gợi ý hoặc hướng dẫn từng bước. Không cung cấp đáp án cuối cùng. Thay vào đó, hãy đưa ra các bước, câu hỏi gợi mở hoặc mẹo để trẻ tự tìm ra câu trả lời. Sử dụng ngôn ngữ đơn giản, thân thiện, vui vẻ và khuyến khích. Trả lời bằng tiếng Việt."

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            # Đọc dữ liệu từ yêu cầu
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message')

            if not message:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Vui lòng gửi câu hỏi!'}).encode('utf-8'))
                return

            if not GEMINI_API_KEY:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'API Key không được cấu hình!'}).encode('utf-8'))
                return

            try:
                # Gửi yêu cầu đến Gemini API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                headers = {'Content-Type': 'application/json'}
                body = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": SYSTEM_PROMPT},
                                {"text": "Câu hỏi: " + message}
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
                }

                # Gửi yêu cầu HTTP đến Gemini API
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode('utf-8'))

                if data and 'candidates' in data and len(data['candidates']) > 0 and 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content'] and len(data['candidates'][0]['content']['parts']) > 0:
                    reply = data['candidates'][0]['content']['parts'][0]['text']
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'reply': reply}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Phản hồi từ API không chứa nội dung hợp lệ.'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

# Khởi động server
Handler = ChatHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server chạy trên http://localhost:{PORT}")
    httpd.serve_forever()