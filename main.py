import os
import json
import cv2
from dotenv import load_dotenv
from preprocess import correct_skew
from extract_ocr import extract_text_ocr
from parse_with_LLM import parse_with_gemini
from extract_pdf import pdf_to_images, is_pdf_file, is_image_file, get_file_type

# Load environment variables
load_dotenv()

def ensure_api_key():
    """
    Ensure the Gemini API key is set.
    """
    if "GEMINI_API_KEY" not in os.environ:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

def process_single_image(image_path, output_dir, prompt, add_spaces=True):
    """Process a single image file"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}")
            return None
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

    angle, corrected_image = correct_skew(image)
    print(f"Corrected skew angle: {angle}")

    corrected_image_dir = os.path.join(output_dir, 'corrected_images')
    os.makedirs(corrected_image_dir, exist_ok=True)

    corrected_image_path = os.path.join(corrected_image_dir, f"corrected_{os.path.basename(image_path)}")
    cv2.imwrite(corrected_image_path, corrected_image)
    print(f"Corrected image saved to {corrected_image_path}")

    with open(corrected_image_path, 'rb') as img_file:
        extracted_text = extract_text_ocr(img_file, add_spaces, max_tokens=16000)

        if not extracted_text.strip():
            print(f"OCR failed or no text extracted from {image_path}. Skipping...")
            return None

        prompt_ending = '\n' if extracted_text[-1] != '\n' else ''
        full_prompt = prompt + '\n' + extracted_text + prompt_ending

        try:
            gemini_response = parse_with_gemini(full_prompt)
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return None

        base_name = os.path.basename(image_path)
        output_file_name = f"{os.path.splitext(base_name)[0]}.json"
        output_file_path = os.path.join(output_dir, output_file_name)

        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(gemini_response, json_file, indent=4, ensure_ascii=False)

        print(f"Output saved to {output_file_path}")
        return output_file_path

def process_file(file_path, output_dir, prompt, add_spaces=True):
    """Process either PDF or image file"""
    ensure_api_key()
    
    file_type = get_file_type(file_path)
    
    if file_type == 'image':
        print(f"Processing image: {os.path.basename(file_path)}")
        return process_single_image(file_path, output_dir, prompt, add_spaces)
    
    elif file_type == 'pdf':
        print(f"Processing PDF: {os.path.basename(file_path)}")
        
        # Convert PDF to images
        temp_image_dir = os.path.join(output_dir, 'temp_pdf_images')
        os.makedirs(temp_image_dir, exist_ok=True)
        
        image_paths = pdf_to_images(file_path, temp_image_dir)
        
        if not image_paths:
            print(f"Failed to convert PDF to images: {file_path}")
            return None
        
        results = []
        for i, image_path in enumerate(image_paths):
            print(f"\nProcessing page {i+1}/{len(image_paths)}")
            result = process_single_image(image_path, output_dir, prompt, add_spaces)
            if result:
                results.append(result)
        
        # Clean up temporary images
        try:
            import shutil
            shutil.rmtree(temp_image_dir)
            print(f"Cleaned up temporary images")
        except Exception as e:
            print(f"Warning: Could not clean up temp directory: {e}")
        
        return results
    
    else:
        print(f"Unsupported file type: {file_path}")
        return None

# Keep backward compatibility
def process_image(image_path, output_dir, prompt, add_spaces=True, ocr=True):
    """Backward compatibility wrapper"""
    return process_file(image_path, output_dir, prompt, add_spaces)

if __name__ == "__main__":
    # Example usage
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_image = os.path.join(base_dir, 'gmindia-challlenge-012024-datas', 'banquepopulaire', 'avril6BP.jpg')
    output_directory = os.path.join(base_dir, 'output')
    prompt = "Extract relevant available data from the following bank statement text, and return in JSON format."
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    process_image(input_image, output_directory, prompt)

