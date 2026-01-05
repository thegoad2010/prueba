import os
import PyPDF2

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def validate_pdf(filepath):
    """
    Validates PDF file:
    1. Checks page count (max 71)
    2. Checks if encrypted
    3. Checks if has extractable text
    Returns: (is_valid, error_message)
    """
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            if reader.is_encrypted:
                 # Try to decrypt with empty password just in case
                try:
                    if reader.decrypt("") == 0:
                        return False, "PDF is password protected"
                except:
                    return False, "PDF is password protected"

            if len(reader.pages) > 71:
                return False, f"PDF has {len(reader.pages)} pages. Maximum allowed is 71."
            
            # Check for extractable text in first few pages
            text = ""
            for i in range(min(3, len(reader.pages))):
                text += reader.pages[i].extract_text()
            
            if not text.strip():
                return False, "No extractable text found in PDF (scanned or image-only)."
                
            return True, None
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"
