import os
import json
from pathlib import Path


def find_simplify_json_files(start_path):
    """Recursively find all *_simplify.json files in the given directory and its subdirectories."""
    json_files = []
    print(f"Searching for *_simplify.json files in: {start_path}")
    
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('_simplify.json'):
                full_path = os.path.join(root, file)
                json_files.append(full_path)
                print(f"Found file: {full_path}")
    
    print(f"Total files found: {len(json_files)}")
    return json_files


def read_json_file(file_path):
    """Read and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Successfully read file: {file_path}")
            return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def main():
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Path to inbox directory
    inbox_path = os.path.join(script_dir, 'messages', 'inbox')
    
    if not os.path.exists(inbox_path):
        print(f"Error: Could not find inbox directory at: {inbox_path}")
        return
    
    print(f"Found inbox directory at: {inbox_path}")
    
    # Find all simplify.json files
    json_files = find_simplify_json_files(inbox_path)
    
    if not json_files:
        print("No *_simplify.json files found!")
        return
    
    # Combine all messages into the required format
    combined_data = {"users": []}
    
    for file_path in json_files:
        data = read_json_file(file_path)
        if data and 'messages' in data:
            combined_data['users'].append({
                "messages": data['messages']
            })
        else:
            print(f"Warning: Invalid data structure in {file_path}")
    
    # Write the combined data to summary_chat.json
    output_path = os.path.join(script_dir, 'summary_chat.json')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully created {output_path}")
        print(f"Combined {len(combined_data['users'])} user message groups")
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == '__main__':
    main()
