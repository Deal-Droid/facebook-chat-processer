import json
import os
from pathlib import Path

def convert_messages(input_file):
    """Convert a single JSON file from Facebook message format to simplified format."""
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not parse JSON file: {input_file}")
            return None
        except Exception as e:
            print(f"Error reading file {input_file}: {str(e)}")
            return None
    
    # Check if file has required structure
    if not all(key in data for key in ['participants', 'messages']):
        print(f"Warning: File {input_file} doesn't have required structure")
        return None
        
    try:
        # Get participant mapping
        user = data['participants'][0]['name']
        admin = data['participants'][1]['name']
        
        # Initialize output structure
        output = {
            "messages": []
        }
        
        # Process messages in reverse order
        for msg in reversed(data['messages']):
            # Skip messages with photos
            if 'photos' in msg:
                continue
                
            # Skip messages without content
            if 'content' not in msg:
                continue
                
            # Skip system messages
            if 'replied to an ad' in msg['content']:
                continue
                
            # Create message object
            message = {
                "from": "user" if msg['sender_name'] == user else "admin",
                "content": msg['content']
            }
            
            output['messages'].append(message)
            
        return output
        
    except Exception as e:
        print(f"Error processing file {input_file}: {str(e)}")
        return None

def process_directory(start_path):
    """Recursively process all *_thai.json files in directory and subdirectories."""
    count = 0
    errors = 0
    
    # Walk through all directories
    for root, _, files in os.walk(start_path):
        # Filter for *_thai.json files
        thai_files = [f for f in files if f.endswith('_thai.json')]
        
        for thai_file in thai_files:
            input_path = Path(root) / thai_file
            # Create output filename by replacing '_thai.json' with '_simplify.json'
            output_file = thai_file.replace('_thai.json', '_simplify.json')
            output_path = Path(root) / output_file
            
            print(f"Processing: {input_path}")
            
            # Convert file
            result = convert_messages(input_path)
            if result is not None:
                try:
                    # Write output file
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    count += 1
                    print(f"Created: {output_path}")
                except Exception as e:
                    print(f"Error writing file {output_path}: {str(e)}")
                    errors += 1
            else:
                errors += 1
    
    return count, errors

if __name__ == "__main__":
    # Get the script's directory
    script_dir = Path(__file__).parent
    
    # Get the base directory where the script is located
    print(f"Starting conversion from directory: {script_dir}")
    
    # Process all files
    successful, failed = process_directory(script_dir)
    
    # Print summary
    print("\nConversion Summary:")
    print(f"Successfully converted: {successful} files")
    print(f"Failed to convert: {failed} files")
