import json
import os
from pathlib import Path
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Set up logging
def setup_logging(log_dir: str = "logs") -> None:
    """Set up logging configuration with both file and console handlers."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"fb_processing_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

@dataclass
class ProcessingStats:
    """Class to track processing statistics."""
    files_processed: int = 0
    files_failed: int = 0
    messages_processed: int = 0
    
    def __str__(self) -> str:
        return (f"Files processed: {self.files_processed}\n"
                f"Files failed: {self.files_failed}\n"
                f"Messages processed: {self.messages_processed}")

class FacebookMessageProcessor:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.stats = ProcessingStats()
        
    def decode_thai_text(self, text: str) -> str:
        """Decode Unicode escaped Thai text to readable Thai characters."""
        if not isinstance(text, str):
            return text
        
        try:
            return text.encode('latin1').decode('utf-8')
        except Exception as e:
            logging.error(f"Error decoding text: {str(e)}")
            return text

    def process_json_content(self, data) -> dict:
        """Recursively process JSON content to decode Thai text."""
        if isinstance(data, dict):
            return {key: self.process_json_content(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.process_json_content(item) for item in data]
        elif isinstance(data, str):
            return self.decode_thai_text(data)
        return data

    def step1_decode_thai(self, json_file: Path) -> Optional[Path]:
        """Step 1: Decode Thai text in JSON file."""
        try:
            logging.info(f"Step 1: Decoding Thai text in {json_file}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            processed_data = self.process_json_content(data)
            output_path = json_file.parent / f"{json_file.stem}_thai.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            self.stats.files_processed += 1
            logging.info(f"Successfully created: {output_path}")
            return output_path
            
        except Exception as e:
            self.stats.files_failed += 1
            logging.error(f"Error in step 1 (decode_thai) for {json_file}: {str(e)}")
            return None

    def step2_simplify_chat(self, thai_json: Path) -> Optional[Path]:
        """Step 2: Simplify chat JSON structure."""
        try:
            logging.info(f"Step 2: Simplifying chat structure for {thai_json}")
            
            with open(thai_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not all(key in data for key in ['participants', 'messages']):
                raise ValueError("Invalid file structure - missing required keys")
            
            # Get participant mapping
            user = data['participants'][0]['name']
            admin = data['participants'][1]['name']
            
            output = {"messages": []}
            
            # Process messages in reverse order
            for msg in reversed(data['messages']):
                if 'photos' in msg or 'content' not in msg:
                    continue
                
                if 'replied to an ad' in msg['content']:
                    continue
                
                message = {
                    "from": "user" if msg['sender_name'] == user else "admin",
                    "content": msg['content']
                }
                
                output['messages'].append(message)
                self.stats.messages_processed += 1
            
            output_path = thai_json.parent / f"{thai_json.stem.replace('_thai', '')}_simplify.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Successfully created: {output_path}")
            return output_path
            
        except Exception as e:
            self.stats.files_failed += 1
            logging.error(f"Error in step 2 (simplify_chat) for {thai_json}: {str(e)}")
            return None

    def step3_summary_chat(self, simplified_files: List[Path]) -> Optional[Path]:
        """Step 3: Combine all simplified chat files into one summary."""
        try:
            logging.info(f"Step 3: Creating summary from {len(simplified_files)} files")
            
            combined_data = {"users": []}
            
            for file_path in simplified_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'messages' in data:
                    combined_data['users'].append({
                        "messages": data['messages']
                    })
            
            output_path = self.base_dir / 'summary_chat.json'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Successfully created summary at: {output_path}")
            logging.info(f"Combined {len(combined_data['users'])} user message groups")
            return output_path
            
        except Exception as e:
            self.stats.files_failed += 1
            logging.error(f"Error in step 3 (summary_chat): {str(e)}")
            return None

    def process_all(self) -> None:
        """Process all files through all three steps."""
        try:
            # Find all JSON files in the messages/inbox directory
            inbox_path = self.base_dir / 'messages' / 'inbox'
            if not inbox_path.exists():
                raise FileNotFoundError(f"Inbox directory not found at: {inbox_path}")
            
            # Step 1: Process all original JSON files
            logging.info("Starting Step 1: Decoding Thai text")
            thai_files = []
            for json_file in inbox_path.rglob('*.json'):
                if not json_file.name.endswith(('_thai.json', '_simplify.json')):
                    if thai_file := self.step1_decode_thai(json_file):
                        thai_files.append(thai_file)
            
            # Step 2: Process all Thai files
            logging.info("Starting Step 2: Simplifying chat structure")
            simplified_files = []
            for thai_file in thai_files:
                if simplified_file := self.step2_simplify_chat(thai_file):
                    simplified_files.append(simplified_file)
            
            # Step 3: Create summary
            logging.info("Starting Step 3: Creating summary")
            if summary_file := self.step3_summary_chat(simplified_files):
                logging.info("All processing completed successfully!")
            
            # Log final statistics
            logging.info("\nProcessing Statistics:\n" + str(self.stats))
            
        except Exception as e:
            logging.error(f"Error in main processing: {str(e)}")

def main():
    # Set up logging
    setup_logging()
    
    # Get the current directory
    current_dir = os.getcwd()
    logging.info(f"Starting processing in directory: {current_dir}")
    
    # Create processor instance and run
    processor = FacebookMessageProcessor(current_dir)
    processor.process_all()

if __name__ == "__main__":
    main()
