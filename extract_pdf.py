import pypdfium2 as pdfium 
import tiktoken
import fitz  # PyMuPDF
from PIL import Image
import os
import tempfile
from pathlib import Path
import io

def num_tokens(text, model="gpt-3.5-turbo-0613"):
	"""Return the number of tokens used by a list of messages."""
	try:
		encoding = tiktoken.encoding_for_model(model)
	except KeyError:
		print("Warning: model not found. Using cl100k_base encoding.")
		encoding = tiktoken.get_encoding("cl100k_base")

	num_tokens = len(encoding.encode(text))
	return num_tokens


def limit_tokens (text, max_tokens=16000):
	num_of_tokens = num_tokens(text)
	if num_of_tokens > max_tokens:
		return text[:max_tokens]
	else:
		return text

def extract_text_pdf(feed: str, multiple_pages: bool = False, max_page_count: int=2, page_num: int = 1, max_tokens: int = 16000) -> str:
	""" 	This function makes use of the PyPDFium2 library to extract the text from a pdf file	"""
	if multiple_pages == False:
		pdf = pdfium.PdfDocument(feed)
		text = pdf[page_num - 1].get_textpage().get_text_range()
		return limit_tokens (text, max_tokens=max_tokens)
	else:
		data = []
		pdf = pdfium.PdfDocument(feed)
		for i in range (min(len(pdf), max_page_count)):
			data.append (pdf[i].get_textpage().get_text_range())
		text = "\n".join(data)
		return limit_tokens (text, max_tokens=max_tokens)

def pdf_to_images(pdf_path, output_dir=None, dpi=300):
    """
    Convert PDF pages to images using PyMuPDF
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save images
        dpi (int): Resolution for conversion
    
    Returns:
        list: List of image file paths
    """
    try:
        doc = fitz.open(pdf_path)
        image_paths = []
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = os.path.dirname(pdf_path)
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Set the matrix for higher resolution
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)
            
            # Save as image
            base_name = Path(pdf_path).stem
            image_filename = f"{base_name}_page_{page_num + 1}.jpg"
            image_path = os.path.join(output_dir, image_filename)
            
            pix.save(image_path)
            image_paths.append(image_path)
            
            print(f"✅ Converted page {page_num + 1}/{doc.page_count} to {image_filename}")
        
        doc.close()
        return image_paths
        
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        return []

def is_pdf_file(file_path):
    """Check if file is a PDF"""
    return Path(file_path).suffix.lower() == '.pdf'

def is_image_file(file_path):
    """Check if file is an image"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif'}
    return Path(file_path).suffix.lower() in image_extensions

def get_file_type(file_path):
    """Determine file type"""
    if is_pdf_file(file_path):
        return 'pdf'
    elif is_image_file(file_path):
        return 'image'
    else:
        return 'unknown'

# Test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)
    
    if not is_pdf_file(pdf_path):
        print(f"Not a PDF file: {pdf_path}")
        sys.exit(1)
    
    print(f"Converting PDF: {pdf_path}")
    images = pdf_to_images(pdf_path)
    
    if images:
        print(f"\n✅ Successfully converted {len(images)} pages:")
        for img in images:
            print(f"  - {img}")
    else:
        print("❌ Failed to convert PDF")