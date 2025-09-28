from PIL import Image
import pytesseract
import mimetypes
import docx
import fitz  # PyMuPDF

def extract_text_from_file(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type and mime_type.startswith("image"):
        return pytesseract.image_to_string(Image.open(file_path))

    if mime_type == "application/pdf":
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        return text

    if mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    return ""
