import streamlit as st
import os
import json
import tempfile
import time
from datetime import datetime
from PIL import Image
import pandas as pd
from main import process_file
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🏦 Bank Statement OCR",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .result-section {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_environment():
    """Check if all required environment variables and dependencies are set up"""
    issues = []
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        issues.append("❌ GEMINI_API_KEY not found in environment variables")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        issues.append("❌ .env file not found. Please create one with your API key")
    
    return issues

def format_json_display(data):
    """Format JSON data for better display"""
    if isinstance(data, dict):
        return json.dumps(data, indent=2, ensure_ascii=False)
    return str(data)

def extract_key_metrics(json_data):
    """Extract key metrics from the JSON data for display"""
    metrics = {}
    
    if isinstance(json_data, dict):
        metrics['Bank'] = json_data.get('bank', 'Unknown')
        metrics['Account Number'] = json_data.get('account_number', 'Unknown')
        metrics['Statement Date'] = json_data.get('statement_date', 'Unknown')
        
        # Transaction count
        transactions = json_data.get('transactions', [])
        metrics['Transaction Count'] = len(transactions) if isinstance(transactions, list) else 0
        
        # Balance information
        account_details = json_data.get('account_details', {})
        if isinstance(account_details, dict):
            balance = account_details.get('balance') or account_details.get('closing_balance')
            if balance:
                metrics['Balance'] = f"€{balance:,.2f}" if isinstance(balance, (int, float)) else str(balance)
        
        # Total credits and debits
        if isinstance(transactions, list):
            total_credits = sum(t.get('credit', 0) for t in transactions if isinstance(t.get('credit'), (int, float)))
            total_debits = sum(t.get('debit', 0) for t in transactions if isinstance(t.get('debit'), (int, float)))
            
            if total_credits > 0:
                metrics['Total Credits'] = f"€{total_credits:,.2f}"
            if total_debits > 0:
                metrics['Total Debits'] = f"€{total_debits:,.2f}"
    
    return metrics

def create_transactions_dataframe(json_data):
    """Create a pandas DataFrame from transactions for table display"""
    if not isinstance(json_data, dict):
        return None
    
    transactions = json_data.get('transactions', [])
    if not isinstance(transactions, list) or not transactions:
        return None
    
    # Convert transactions to DataFrame
    df = pd.DataFrame(transactions)
    
    # Reorder columns for better display
    preferred_columns = ['date', 'description', 'debit', 'credit', 'balance']
    columns = [col for col in preferred_columns if col in df.columns]
    other_columns = [col for col in df.columns if col not in preferred_columns]
    df = df[columns + other_columns]
    
    # Format numeric columns
    for col in ['debit', 'credit', 'balance']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"€{x:,.2f}" if isinstance(x, (int, float)) and x != 0 else "")
    
    return df

def main():
    # Header
    st.markdown('<h1 class="main-header">🏦 Bank Statement OCR & Data Extraction</h1>', unsafe_allow_html=True)
    
    # Check environment setup
    env_issues = check_environment()
    if env_issues:
        st.error("⚠️ Setup Issues Detected:")
        for issue in env_issues:
            st.error(issue)
        
        with st.expander("🔧 Setup Instructions"):
            st.markdown("""
            **To fix these issues:**
            
            1. **Create a `.env` file** in the project root directory
            2. **Add your Gemini API key**:
               ```
               GEMINI_API_KEY=your_api_key_here
               ```
            3. **Get your API key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
            4. **Restart the Streamlit app**
            """)
        return
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("## 📋 How to Use")
        st.markdown("""
        1. **Upload** a bank statement (image or PDF)
        2. **Customize** the extraction prompt (optional)
        3. **Click Process** to extract data
        4. **View** results and download JSON
        """)
        
        st.markdown("## 🏦 Supported Banks")
        banks = [
            "Banque Populaire", "Caisse d'Épargne", "Crédit Agricole",
            "Crédit du Nord", "Crédit Mutuel", "La Poste", "LCL",
            "Qonto", "Société Générale"
        ]
        for bank in banks:
            st.markdown(f"• {bank}")
        
        st.markdown("## 📁 Supported Formats")
        st.markdown("• **Images**: JPG, PNG, TIFF, BMP")
        st.markdown("• **Documents**: PDF")
        
        st.markdown("## ⚡ Processing Info")
        st.info("Processing typically takes 5-15 seconds per document")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Bank Statement")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a bank statement file",
            type=['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'pdf'],
            help="Upload an image or PDF of your bank statement"
        )
        
        # Custom prompt
        st.markdown("### 🎯 Extraction Prompt")
        default_prompt = """Extract all relevant banking information from this statement including:
- Bank name and contact details
- Account holder information
- Account details (number, IBAN, balance)
- All transactions with dates, descriptions, and amounts
- Statement period and dates

Format the output as structured JSON with clear field names."""
        
        custom_prompt = st.text_area(
            "Customize the extraction prompt:",
            value=default_prompt,
            height=150,
            help="Modify this prompt to focus on specific information you need"
        )
        
        # Processing button
        process_button = st.button(
            "🚀 Process Bank Statement",
            type="primary",
            disabled=uploaded_file is None
        )
    
    with col2:
        st.markdown("### 👁️ Preview")
        
        if uploaded_file is not None:
            # Display file info
            st.info(f"**File:** {uploaded_file.name}")
            st.info(f"**Size:** {uploaded_file.size:,} bytes")
            
            # Show image preview (if it's an image)
            if uploaded_file.type.startswith('image/'):
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Bank Statement", use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
            else:
                st.info("📄 PDF file uploaded - preview not available")
        else:
            st.markdown("""
            <div class="upload-section">
                <h3>📁 No file uploaded yet</h3>
                <p>Please upload a bank statement to see the preview here</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Processing section
    if process_button and uploaded_file is not None:
        st.markdown("---")
        st.markdown("## 🔄 Processing Results")
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_file_path = tmp_file.name
            
            # Update progress
            progress_bar.progress(20)
            status_text.text("📁 File saved temporarily...")
            time.sleep(0.5)
            
            # Create output directory
            output_dir = "streamlit_output"
            os.makedirs(output_dir, exist_ok=True)
            
            progress_bar.progress(40)
            status_text.text("🔍 Starting OCR and AI processing...")
            time.sleep(0.5)
            
            # Process the file
            start_time = time.time()
            result_file = process_file(
                file_path=temp_file_path,
                output_dir=output_dir,
                prompt=custom_prompt
            )
            processing_time = time.time() - start_time
            
            progress_bar.progress(80)
            status_text.text("📊 Parsing results...")
            time.sleep(0.5)
            
            # Load and display results
            with open(result_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            progress_bar.progress(100)
            status_text.text("✅ Processing completed!")
            
            # Display success message
            st.success(f"🎉 Successfully processed in {processing_time:.1f} seconds!")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "💳 Transactions", "📄 Full JSON", "💾 Download"])
            
            with tab1:
                st.markdown("### 📈 Key Metrics")
                metrics = extract_key_metrics(json_data)
                
                # Display metrics in columns
                if metrics:
                    metric_cols = st.columns(min(len(metrics), 4))
                    for i, (key, value) in enumerate(metrics.items()):
                        with metric_cols[i % 4]:
                            st.metric(key, value)
                
                # Display account information
                if isinstance(json_data, dict):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🏦 Bank Information")
                        bank_info = {
                            "Bank": json_data.get('bank', 'Unknown'),
                            "Statement Date": json_data.get('statement_date', 'Unknown'),
                            "Statement Period": json_data.get('statement_period', 'Unknown')
                        }
                        for key, value in bank_info.items():
                            st.text(f"{key}: {value}")
                    
                    with col2:
                        st.markdown("#### 👤 Account Information")
                        account_details = json_data.get('account_details', {})
                        client_info = json_data.get('client_info', {})
                        
                        info_to_show = {
                            "Account Number": json_data.get('account_number', 'Unknown'),
                            "Client Name": client_info.get('name', 'Unknown') if isinstance(client_info, dict) else 'Unknown',
                            "IBAN": account_details.get('iban', 'Unknown') if isinstance(account_details, dict) else 'Unknown'
                        }
                        
                        for key, value in info_to_show.items():
                            st.text(f"{key}: {value}")
            
            with tab2:
                st.markdown("### 💳 Transaction Details")
                df = create_transactions_dataframe(json_data)
                
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                    st.info(f"📊 Total transactions: {len(df)}")
                else:
                    st.warning("No transactions found in the processed data")
            
            with tab3:
                st.markdown("### 📄 Complete JSON Output")
                st.json(json_data)
            
            with tab4:
                st.markdown("### 💾 Download Results")
                
                # Prepare download data
                json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"bank_statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col2:
                    if df is not None and not df.empty:
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📊 Download CSV",
                            data=csv_data,
                            file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                st.info("💡 **Tip:** Save these files for your records or import into accounting software")
            
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Processing failed")
            st.error(f"Error processing file: {str(e)}")
            
            with st.expander("🔍 Error Details"):
                st.code(str(e))
                st.markdown("""
                **Common solutions:**
                - Check if your API key is valid
                - Ensure the image is clear and readable
                - Try a different file format
                - Check your internet connection
                """)
        
        finally:
            # Clean up temporary file
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🏦 <strong>Bank Statement OCR & Data Extraction System</strong></p>
        <p>Powered by Tesseract OCR and Google Gemini AI</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()