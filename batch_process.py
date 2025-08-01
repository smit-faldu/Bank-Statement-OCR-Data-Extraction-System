#!/usr/bin/env python3
"""
Batch processing script for bank statement OCR
Processes all images in the dataset directories
"""

import os
import json
import time
from pathlib import Path
from main import process_file
from extract_pdf import is_pdf_file, is_image_file

def get_all_files(base_dir):
    """Get all image and PDF files from the dataset directories"""
    files_list = []
    
    data_dir = Path(base_dir) / 'gmindia-challlenge-012024-datas'
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = Path(root) / file
            if is_image_file(str(file_path)) or is_pdf_file(str(file_path)):
                bank_name = Path(root).name
                file_type = 'pdf' if is_pdf_file(str(file_path)) else 'image'
                files_list.append({
                    'path': str(file_path),
                    'bank': bank_name,
                    'filename': file,
                    'type': file_type
                })
    
    return files_list

def process_batch(output_dir="output", max_files=None):
    """Process all bank statement images in batch"""
    base_dir = Path(__file__).parent
    output_path = base_dir / output_dir
    output_path.mkdir(exist_ok=True)
    
    # Get all files (images and PDFs)
    all_files = get_all_files(base_dir)
    
    if not all_files:
        print("No image or PDF files found in the dataset!")
        return
    
    if max_files:
        all_files = all_files[:max_files]
    
    # Count file types
    images = [f for f in all_files if f['type'] == 'image']
    pdfs = [f for f in all_files if f['type'] == 'pdf']
    
    print(f"Found {len(all_files)} files to process:")
    print(f"  - Images: {len(images)}")
    print(f"  - PDFs: {len(pdfs)}")
    print("=" * 60)
    
    # Process each file
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, file_info in enumerate(all_files, 1):
        print(f"\n[{i}/{len(all_files)}] Processing: {file_info['filename']}")
        print(f"Bank: {file_info['bank']} | Type: {file_info['type'].upper()}")
        
        try:
            # Create bank-specific output directory
            bank_output_dir = output_path / file_info['bank']
            bank_output_dir.mkdir(exist_ok=True)
            
            # Process the file
            prompt = f"Extract all relevant data from this {file_info['bank']} bank statement and return in structured JSON format."
            
            result = process_file(
                file_path=file_info['path'],
                output_dir=str(bank_output_dir),
                prompt=prompt
            )
            
            if result:
                successful += 1
                print(f"✅ Successfully processed: {file_info['filename']}")
            else:
                failed += 1
                print(f"❌ Failed to process: {file_info['filename']}")
            
        except Exception as e:
            failed += 1
            print(f"❌ Failed to process {file_info['filename']}: {str(e)}")
            continue
    
    # Summary
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(all_files)}")
    print(f"  - Images: {len(images)}")
    print(f"  - PDFs: {len(pdfs)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/len(all_files)*100):.1f}%")
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Average time per file: {(total_time/len(all_files)):.1f} seconds")
    print(f"Output directory: {output_path}")

def process_single_bank(bank_name, output_dir="output"):
    """Process all images from a specific bank"""
    base_dir = Path(__file__).parent
    output_path = base_dir / output_dir / bank_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    data_dir = base_dir / 'gmindia-challlenge-012024-datas' / bank_name
    
    if not data_dir.exists():
        print(f"Bank directory not found: {data_dir}")
        return
    
    all_files = [f for f in data_dir.iterdir() 
                  if f.is_file() and (is_image_file(str(f)) or is_pdf_file(str(f)))]
    
    if not all_files:
        print(f"No image or PDF files found for bank: {bank_name}")
        return
    
    # Count file types
    images = [f for f in all_files if is_image_file(str(f))]
    pdfs = [f for f in all_files if is_pdf_file(str(f))]
    
    print(f"Processing {len(all_files)} files for {bank_name}:")
    print(f"  - Images: {len(images)}")
    print(f"  - PDFs: {len(pdfs)}")
    print("=" * 50)
    
    for i, file_path in enumerate(all_files, 1):
        file_type = 'PDF' if is_pdf_file(str(file_path)) else 'Image'
        print(f"\n[{i}/{len(all_files)}] Processing: {file_path.name} ({file_type})")
        
        try:
            prompt = f"Extract all relevant data from this {bank_name} bank statement and return in structured JSON format."
            
            result = process_file(
                file_path=str(file_path),
                output_dir=str(output_path),
                prompt=prompt
            )
            
            if result:
                print(f"✅ Successfully processed: {file_path.name}")
            else:
                print(f"❌ Failed to process: {file_path.name}")
            
        except Exception as e:
            print(f"❌ Failed to process {file_path.name}: {str(e)}")

def list_available_banks():
    """List all available banks in the dataset"""
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'gmindia-challlenge-012024-datas'
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return []
    
    banks = [d.name for d in data_dir.iterdir() if d.is_dir()]
    return sorted(banks)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process bank statement images")
    parser.add_argument("--bank", help="Process only specific bank")
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--list-banks", action="store_true", help="List available banks")
    
    args = parser.parse_args()
    
    if args.list_banks:
        banks = list_available_banks()
        print("Available banks:")
        for bank in banks:
            print(f"  - {bank}")
    elif args.bank:
        process_single_bank(args.bank, args.output)
    else:
        process_batch(args.output, args.max_files)