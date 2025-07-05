# pip install pytesseract pillow pdf2image



from PIL import Image
import pytesseract
import tkinter as tk
from tkinter import filedialog, messagebox, END, Scrollbar
from pdf2image import convert_from_path
import os

# --- CONFIGURATION (Set these for Windows) ---
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# poppler_path = r'C:\path\to\poppler\bin'

# --- FUNCTIONS ---

def select_pdf():
    file_path = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )
    return file_path

def extract_text_from_pdf(pdf_path):
    try:
        # Convert PDF to image list (1 image per page)
        images = convert_from_path(pdf_path)  # Add poppler_path=poppler_path if needed

        extracted_pages = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang='ben')
            extracted_pages.append(f"📄 পৃষ্ঠা {i + 1}:\n{text.strip()}\n{'-' * 60}\n")

        return "\n".join(extracted_pages)
    except Exception as e:
        return f"PDF to text OCR Error: {str(e)}"

def show_result_window(full_text):
    result_window = tk.Tk()
    result_window.title("📄 Extracted Bangla Text from PDF")
    result_window.geometry("1000x800")
    result_window.attributes("-topmost", True)

    label = tk.Label(result_window, text="নিচে PDF থেকে বাংলা পাঠ্যটি দেখানো হয়েছে:", font=("SolaimanLipi", 14))
    label.pack(pady=10)

    frame = tk.Frame(result_window)
    frame.pack(fill="both", expand=True)

    scrollbar = Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_box = tk.Text(frame, wrap='word', yscrollcommand=scrollbar.set, font=("SolaimanLipi", 14))
    text_box.pack(side="left", fill="both", expand=True)
    text_box.insert(END, full_text if full_text else "(কোনো পাঠ্য পাওয়া যায়নি)")
    text_box.config(state='normal')

    scrollbar.config(command=text_box.yview)

    def copy_text():
        result_window.clipboard_clear()
        result_window.clipboard_append(text_box.get("1.0", END))
        messagebox.showinfo("✅ কপি হয়েছে", "সকল পাঠ্য ক্লিপবোর্ডে কপি করা হয়েছে!")

    copy_button = tk.Button(result_window, text="📋 কপি করুন", command=copy_text,
                            font=("SolaimanLipi", 12), bg="#4CAF50", fg="white")
    copy_button.pack(pady=5)

    result_window.mainloop()

# --- MAIN FUNCTION ---

def main():
    print("📂 Opening file dialog to select a PDF...")
    pdf_path = select_pdf()

    if not pdf_path:
        print("❌ No PDF selected.")
        return

    print(f"📖 Processing PDF: {pdf_path}")
    extracted_text = extract_text_from_pdf(pdf_path)

    print("📝 Extracted Text:")
    print(extracted_text or "(No text found)")

    print("💬 Showing result window...")
    show_result_window(extracted_text)

# --- RUN THE PROGRAM ---
if __name__ == "__main__":
    main()
