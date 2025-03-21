import pyautogui
import pytesseract
from PIL import ImageGrab
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI

# 📌 Set your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\mobi.ahmed\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# 📌 OpenAI API Key (Key needs to be within doiuble quotes"
client = OpenAI(
    api_key="REPLACE-WITH-OPENAI-APIKEY"
)

# 🎯 Global variables for selection box
start_x, start_y, end_x, end_y = 0, 0, 0, 0

# 📸 Click-and-drag selection using a Tkinter overlay
def capture_region():
    global start_x, start_y, end_x, end_y

    # Create a fullscreen transparent overlay
    root = tk.Tk()
    root.attributes("-alpha", 0.3)  # Make it slightly transparent
    root.attributes("-fullscreen", True)
    root.title("Select Area")

    # Create a canvas
    canvas = tk.Canvas(root, cursor="cross", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    # Start drawing
    def on_click(event):
        global start_x, start_y
        start_x, start_y = event.x, event.y
        canvas.delete("rect")  # Clear previous selection

    def on_drag(event):
        global end_x, end_y
        end_x, end_y = event.x, event.y
        canvas.delete("rect")  # Clear old rectangle
        canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", width=2, tags="rect")

    def on_release(event):
        global start_x, start_y, end_x, end_y
        root.destroy()  # Close overlay window

    # Bind mouse events
    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    # Run the overlay
    root.mainloop()

    # Ensure correct order of coordinates
    x1, y1 = min(start_x, end_x), min(start_y, end_y)
    x2, y2 = max(start_x, end_x), max(start_y, end_y)

    # Take screenshot of selected region
    return ImageGrab.grab(bbox=(x1, y1, x2, y2))

# 🔤 Extract text using OCR
def extract_text(image):
    return pytesseract.image_to_string(image)

# 💬 Send question to ChatGPT
def ask_chatgpt(question_text):
    prompt = f"Answer this exam question by choosing one of the options:\n\n{question_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# 📥 Show pop-up message
def show_popup(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)

# 🧠 Main logic
def main():
    try:
        screenshot = capture_region()
        extracted_text = extract_text(screenshot)

        if not extracted_text.strip():
            show_popup("No Text Detected", "Try again. No readable text found in the selected area.")
            return

        answer = ask_chatgpt(extracted_text)
        show_popup("ChatGPT Answer", answer)

    except Exception as e:
        show_popup("Error", str(e))

if __name__ == "__main__":
    main()
