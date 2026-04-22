import fitz
import sys

def read_pdf(pdf_path, txt_path):
    try:
        doc = fitz.open(pdf_path)
        with open(txt_path, 'w', encoding='utf-8') as f:
            for page in doc:
                f.write(page.get_text())
        print(f"Successfully extracted text to {txt_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_pdf(sys.argv[1], sys.argv[2])
