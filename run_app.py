#!/usr/bin/env python3
"""
Simple launcher script for the Bank Statement OCR Streamlit App
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    
    print("🏦 Starting Bank Statement OCR Web App...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('streamlit_app.py'):
        print("❌ Error: streamlit_app.py not found!")
        print("Please run this script from the project root directory.")
        return 1
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your GEMINI_API_KEY")
        print("Example:")
        print("GEMINI_API_KEY=your_api_key_here")
        print()
    
    try:
        # Launch Streamlit
        print("🚀 Launching Streamlit app...")
        print("📱 The app will open in your default web browser")
        print("🔗 URL: http://localhost:8501")
        print()
        print("💡 To stop the app, press Ctrl+C in this terminal")
        print("=" * 50)
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return 1

if __name__ == "__main__":
    exit(main())