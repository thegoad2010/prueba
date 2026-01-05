import PyPDF2
from langdetect import detect
import re

def extract_text_metadata(filepath):
    """
    Extracts text and metadata from PDF.
    Returns: dict with text, language, title, author, pages
    """
    text = ""
    title = None
    author = None
    
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            metadata = reader.metadata
            
            if metadata:
                title = metadata.get('/Title')
                author = metadata.get('/Author')
            
            # If metadata missing, try to infer from first page text (simplistic)
            
            full_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
            
            text = "\n".join(full_text)
            
            # Simple cleanup: remove multiple newlines, etc.
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            language = 'en' # Default
            try:
                if len(text) > 50:
                    language = detect(text)
            except:
                pass
                
            return {
                'text': text,
                'language': language,
                'title': title,
                'author': author,
                'pages': len(reader.pages)
            }
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None
