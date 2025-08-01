import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def handle_json(json_text):
    """Extract JSON content from text response"""
    try:
        # Find the first { and last } to extract JSON
        start = json_text.find('{')
        end = json_text.rfind('}') + 1
        if start != -1 and end != 0:
            return json_text[start:end]
        return json_text
    except Exception as e:
        print(f"Error handling JSON: {e}")
        return json_text

def parse_with_gemini(input_text: str, max_tokens: int = 5000) -> dict:
    """
    This function utilizes the Gemini model to parse the input text into a JSON format
    """
    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create the prompt
        system_prompt = """You are an expert at extracting structured data from bank statements. 
        Extract all relevant information from the following bank statement text and return it in a well-structured JSON format.
        
        Include the following fields when available:
        - bank: Bank name
        - statement_date: Date of the statement
        - account_number: Account number
        - statement_period: Period covered by the statement
        - contact_info: Bank contact information (phone, address, website)
        - client_info: Customer information (name, address)
        - account_details: Account details (IBAN, BIC, balance, etc.)
        - transactions: Array of transactions with date, description, debit, credit amounts
        
        Return only valid JSON without any additional text or formatting."""
        
        full_prompt = f"{system_prompt}\n\nBank Statement Text:\n{input_text}"
        
        # Generate response
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=max_tokens,
            )
        )
        
        # Extract and parse JSON
        response_text = response.text
        json_text = handle_json(response_text)
        data = json.loads(json_text)
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        raise
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        raise

# Keep backward compatibility
def parse_with_gpt(input_text: str, max_tokens: int = 5000) -> dict:
    """Backward compatibility wrapper"""
    return parse_with_gemini(input_text, max_tokens)