#!/usr/bin/env python3
"""
Demo script to showcase the Bank Statement OCR Web App
This script provides information about the web interface and how to use it.
"""

import os
import webbrowser
import time

def print_banner():
    """Print a nice banner"""
    print("=" * 60)
    print("🏦 BANK STATEMENT OCR - WEB APP DEMO")
    print("=" * 60)
    print()

def check_setup():
    """Check if the system is properly set up"""
    print("🔍 Checking system setup...")
    
    issues = []
    
    # Check if streamlit_app.py exists
    if not os.path.exists('streamlit_app.py'):
        issues.append("❌ streamlit_app.py not found")
    else:
        print("✅ Web app file found")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        issues.append("❌ .env file not found - you'll need to create one with your API key")
    else:
        print("✅ Environment file found")
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        issues.append("❌ GEMINI_API_KEY not found in environment")
    else:
        print("✅ API key configured")
    
    return issues

def show_features():
    """Show the features of the web app"""
    print("\n🌟 WEB APP FEATURES:")
    print("-" * 30)
    
    features = [
        "📤 Drag & Drop File Upload",
        "👁️ Live Document Preview", 
        "🎯 Customizable AI Prompts",
        "📊 Interactive Results Dashboard",
        "💳 Transaction Table View",
        "📄 Full JSON Output Display",
        "💾 Download as JSON/CSV",
        "🔄 Real-time Processing Progress",
        "📱 Mobile-Friendly Interface",
        "🎨 Beautiful, Professional UI"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print()

def show_usage_instructions():
    """Show how to use the web app"""
    print("📋 HOW TO USE THE WEB APP:")
    print("-" * 35)
    
    steps = [
        "1. 🚀 Launch the app using 'python run_app.py'",
        "2. 📱 Open your browser to http://localhost:8501",
        "3. 📤 Upload a bank statement (drag & drop or browse)",
        "4. 👁️ Preview your document in the right panel",
        "5. 🎯 Customize the extraction prompt if needed",
        "6. 🔄 Click 'Process Bank Statement' button",
        "7. ⏳ Watch the progress bar as it processes",
        "8. 📊 View results in Summary, Transactions, or JSON tabs",
        "9. 💾 Download your results as JSON or CSV files"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print()

def show_supported_formats():
    """Show supported file formats"""
    print("📁 SUPPORTED FILE FORMATS:")
    print("-" * 30)
    
    formats = {
        "Images": ["JPG", "JPEG", "PNG", "TIFF", "BMP"],
        "Documents": ["PDF"]
    }
    
    for category, file_types in formats.items():
        print(f"  {category}: {', '.join(file_types)}")
    
    print()

def show_sample_banks():
    """Show which banks are supported"""
    print("🏦 TESTED WITH THESE BANKS:")
    print("-" * 32)
    
    banks = [
        "Banque Populaire", "Caisse d'Épargne", "Crédit Agricole",
        "Crédit du Nord", "Crédit Mutuel", "La Poste", 
        "LCL", "Qonto", "Société Générale"
    ]
    
    for i, bank in enumerate(banks, 1):
        print(f"  {i:2d}. {bank}")
    
    print()

def offer_launch():
    """Offer to launch the web app"""
    print("🚀 READY TO START?")
    print("-" * 20)
    
    response = input("Would you like to launch the web app now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\n🎉 Launching the web app...")
        print("📱 The app will open in your browser shortly")
        print("🔗 URL: http://localhost:8501")
        print("\n💡 To stop the app later, press Ctrl+C in the terminal")
        
        # Give user time to read
        time.sleep(2)
        
        # Launch the app
        import subprocess
        import sys
        
        try:
            subprocess.run([sys.executable, "run_app.py"])
        except KeyboardInterrupt:
            print("\n👋 Demo ended by user")
        except Exception as e:
            print(f"\n❌ Error launching app: {e}")
            print("💡 Try running 'python run_app.py' manually")
    else:
        print("\n👍 No problem! You can launch it anytime with:")
        print("   python run_app.py")
        print("   or double-click run_app.bat (Windows)")

def main():
    """Main demo function"""
    print_banner()
    
    # Check setup
    issues = check_setup()
    
    if issues:
        print("\n⚠️  SETUP ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 TO FIX THESE ISSUES:")
        print("  1. Make sure you're in the project directory")
        print("  2. Create a .env file with: GEMINI_API_KEY=your_key_here")
        print("  3. Get your API key from: https://makersuite.google.com/app/apikey")
        print()
        return
    
    print("✅ System setup looks good!")
    print()
    
    # Show features and instructions
    show_features()
    show_usage_instructions()
    show_supported_formats()
    show_sample_banks()
    
    # Offer to launch
    offer_launch()

if __name__ == "__main__":
    main()