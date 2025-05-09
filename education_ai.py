import os
import tkinter as tk
from tkinter import messagebox, ttk
import google.generativeai as genai
import threading
from PIL import Image, ImageTk

# Thiết lập API Key cho Gemini API
GEMINI_API_KEY = "AIzaSyDGq8ugWb_G86SW9UhrojaPsKH7C6K_Sx0"
if not GEMINI_API_KEY:
    raise ValueError("Vui lòng cung cấp GEMINI_API_KEY trong mã.")

genai.configure(api_key=GEMINI_API_KEY)

# Khởi tạo mô hình Gemini
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    raise RuntimeError(f"Không thể khởi tạo Gemini model: {str(e)}. Kiểm tra API Key và kết nối internet.")

# Hệ thống hướng dẫn cho AI
system_prompt = (
    "Bạn là một AI hướng dẫn, được thiết kế để giúp trẻ em học tập và giải quyết vấn đề bằng cách cung cấp gợi ý hoặc hướng dẫn từng bước. "
    "Không cung cấp đáp án cuối cùng. Thay vào đó, hãy đưa ra các bước, câu hỏi gợi mở hoặc mẹo để trẻ tự tìm ra câu trả lời. "
    "Sử dụng ngôn ngữ đơn giản, thân thiện, vui vẻ và khuyến khích. Trả lời bằng tiếng Việt."
)

def get_response(text):
    """Gửi câu hỏi đến Gemini API và nhận phản hồi."""
    if not text or text.strip() == "":
        return None, "Lỗi: Văn bản đầu vào rỗng. Vui lòng nhập câu hỏi hợp lệ."
    
    try:
        prompt = f"{system_prompt}\n\nCâu hỏi: {text}"
        response = model.generate_content(prompt)
        answer = response.text.strip()
        if not answer:
            return None, "Lỗi: Phản hồi từ Gemini API rỗng."
        return answer, None
    except Exception as e:
        return None, f"Lỗi khi gọi Gemini API: {str(e)}. Kiểm tra: 1) API Key có hợp lệ không; 2) Kết nối internet ổn định; 3) Giới hạn API (quota) có bị vượt không."

def send_question():
    question = input_text.get().strip()
    if not question:
        messagebox.showwarning("Cảnh báo", "Hãy nhập câu hỏi nhé! 🌟")
        return

    add_user_message(question)
    input_text.delete(0, tk.END)
    send_button.config(state='disabled')
    root.update()

    def process_question():
        answer, error = get_response(question)
        root.after(0, lambda: update_ui(answer, error, question))

    threading.Thread(target=process_question, daemon=True).start()

def add_user_message(text):
    user_frame = tk.Frame(chat_frame, bg="#FFF3E0", bd=2, relief="solid")
    user_label = tk.Label(
        user_frame,
        text=text,
        font=("Arial", 12),
        bg="#FFF3E0",
        fg="#D81B60",
        wraplength=400,
        justify="right",
        padx=15,
        pady=10
    )
    user_label.pack(anchor="e", padx=10, pady=5)
    user_frame.pack(anchor="e", fill="x", padx=20, pady=5)
    update_canvas_scroll()

def add_ai_message(text, is_error=False):
    ai_frame = tk.Frame(chat_frame, bg="#E0F7FA", bd=2, relief="solid")
    ai_label = tk.Label(
        ai_frame,
        text=text,
        font=("Arial", 12),
        bg="#E0F7FA" if not is_error else "#FFCDD2",
        fg="#0288D1" if not is_error else "#D32F2F",
        wraplength=400,
        justify="left",
        padx=15,
        pady=10
    )
    ai_label.pack(anchor="w", padx=10, pady=5)
    ai_frame.pack(anchor="w", fill="x", padx=20, pady=5)
    update_canvas_scroll()

def update_ui(suggestion, error, question):
    if error:
        add_ai_message(error, is_error=True)
    else:
        add_ai_message(suggestion)
    send_button.config(state='normal')
    update_canvas_scroll()

def update_canvas_scroll():
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1.0)

def exit_app():
    if messagebox.askokcancel("Thoát", "Bạn có muốn rời khỏi AI Tutor không? 🌈"):
        root.destroy()

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Chatbot Thông Minh - Người bạn của học sinh lớp 5")
root.geometry("600x500")
root.configure(bg="#B3E5FC")

# Tạo style cho giao diện
style = ttk.Style()
style.configure("TButton", font=("Arial", 12, "bold"), padding=8, relief="flat", background="#F06292", foreground="#FFFFFF")
style.map("TButton",
          background=[('active', '#EC407A')],
          foreground=[('active', '#FFFFFF')])
style.configure("TEntry", font=("Arial", 12), padding=10, fieldbackground="#FFFFFF", foreground="#0288D1", relief="flat")
style.configure("TScrollbar", background="#F06292", troughcolor="#B3E5FC", bordercolor="#B3E5FC")

# Tạo canvas và scrollbar
canvas = tk.Canvas(root, bg="#B3E5FC", highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview, style="TScrollbar")
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Thêm hình nền (tùy chọn)
bg_image = None
try:
    image_path = "C:\\AI_Tutor\\background.png"
    if os.path.exists(image_path):
        image = Image.open(image_path)
        bg_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=bg_image, anchor="nw")
    else:
        print("Hình nền background.png không tồn tại, bỏ qua.")
except Exception as e:
    print(f"Không thể tải hình nền: {str(e)}")

# Tạo khung chứa tin nhắn
chat_frame = tk.Frame(canvas, bg="#B3E5FC", width=560)
canvas.create_window((0, 0), window=chat_frame, anchor="nw", width=560)

# Tiêu đề
title_label = tk.Label(
    chat_frame,
    text="Chatbot Thông Minh - Người bạn thân thiết của học sinh 🤖",
    font=("Arial", 16, "bold"),
    bg="#B3E5FC",
    fg="#F06292"
)
title_label.pack(pady=10)

# Thông điệp chào mừng
welcome_label = tk.Label(
    chat_frame,
    text="Xin chào bạn! Mình là Robot Thông Minh. Mình có thể giúp bạn trả lời câu hỏi, kể chuyện vui, hoặc cùng học bài đấy! 😊",
    font=("Arial", 12),
    bg="#B3E5FC",
    fg="#0288D1",
    wraplength=500,
    justify="center"
)
welcome_label.pack(pady=10)

# Thêm thông điệp gợi ý
suggestion_label = tk.Label(
    chat_frame,
    text="Bạn muốn hỏi mình điều gì nào?",
    font=("Arial", 12, "italic"),
    bg="#B3E5FC",
    fg="#D81B60"
)
suggestion_label.pack(pady=5)

# Thêm thông điệp chào từ AI
add_ai_message("Chào bạn nhỏ! Mình sẵn sàng giúp bạn học tập nhé! Hôm nay bạn muốn học gì nào? 😊")

# Khung nhập câu hỏi
input_frame = tk.Frame(root, bg="#B3E5FC", bd=2, relief="solid")
input_frame.pack(side="bottom", fill="x", padx=10, pady=5)
input_text = ttk.Entry(
    input_frame,
    font=("Arial", 12),
    style="TEntry",
    foreground="#0288D1"
)
input_text.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
send_button = ttk.Button(
    input_frame,
    text="Gửi 🌟",
    style="TButton",
    command=send_question,
    cursor="hand2"
)
send_button.pack(side="right", padx=5, pady=5)

# Chân trang
footer_frame = tk.Frame(root, bg="#B3E5FC")
footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)
footer_label = tk.Label(
    footer_frame,
    text="© 2023 ChatBot Thông Minh - Bố Bình Béo",
    font=("Arial", 10),
    bg="#B3E5FC",
    fg="#0288D1"
)
footer_label.pack()
api_note_label = tk.Label(
    footer_frame,
    text="Kết nối với thời gian thực với Google API",
    font=("Arial", 8, "italic"),
    bg="#B3E5FC",
    fg="#D81B60"
)
api_note_label.pack()

# Giữ tham chiếu để hình nền không bị garbage collected
root.bg_image = bg_image

# Chạy ứng dụng
root.protocol("WM_DELETE_WINDOW", exit_app)
root.mainloop()