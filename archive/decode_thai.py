import json
import os
from pathlib import Path

def decode_thai_text(text):
    """Decode Unicode escaped Thai text to readable Thai characters."""
    if not isinstance(text, str):
        return text
    
    try:
        # Convert the Unicode escaped sequence to bytes
        decoded = text.encode('latin1').decode('utf-8')
        return decoded
    except Exception as e:
        print(f"Error decoding text: {str(e)}")
        return text

def process_json_content(data):
    """Recursively process JSON content to decode Thai text."""
    if isinstance(data, dict):
        return {key: process_json_content(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [process_json_content(item) for item in data]
    elif isinstance(data, str):
        return decode_thai_text(data)
    return data

def process_file(file_path):
    """Process a single JSON file to decode Thai text."""
    try:
        # Read the original JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process the content
        processed_data = process_json_content(data)
        
        # Create output path
        output_path = str(file_path).replace('.json', '_thai.json')
        
        # Write the processed content to new file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Successfully processed: {file_path}")
        return True
    except Exception as e:
        print(f"✗ Error processing {file_path}: {str(e)}")
        return False

def process_directory(directory_path):
    """Recursively process all JSON files in directory."""
    success_count = 0
    fail_count = 0
    total_files = 0
    
    print(f"\nStarting to process files in: {directory_path}\n")
    
    # Walk through all directories
    for root, dirs, files in os.walk(directory_path):
        # Process only JSON files and skip already processed ones
        json_files = [f for f in files if f.endswith('.json') and not f.endswith('_thai.json')]
        total_files += len(json_files)
        
        for file in json_files:
            file_path = Path(root) / file
            if process_file(file_path):
                success_count += 1
            else:
                fail_count += 1
            
    return success_count, fail_count, total_files

def main():
    # Get the current directory where the script is run
    current_dir = os.getcwd()
    
    # Ask user for the directory path or use default
    print("Thai Text Converter for Facebook Messages")
    print("=======================================")
    print(f"Current directory: {current_dir}")
    user_input = input("\nEnter the path to your messages directory (or press Enter to use current directory): ").strip()
    
    directory_path = user_input if user_input else current_dir
    
    # Verify directory exists
    if not os.path.exists(directory_path):
        print(f"\nError: Directory not found: {directory_path}")
        return
    
    print("\nProcessing files...")
    success, failed, total = process_directory(directory_path)
    
    # Print summary
    print("\nProcessing Complete!")
    print("===================")
    print(f"Total JSON files found: {total}")
    print(f"Successfully processed: {success}")
    print(f"Failed to process: {failed}")
    
    if failed > 0:
        print("\nNote: Check the error messages above for details about failed files.")
    
    print("\nProcessed files have been saved with '_thai.json' suffix.")

if __name__ == "__main__":
    main()
