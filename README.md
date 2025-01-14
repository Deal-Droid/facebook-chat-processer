# Facebook Chat History Processor

A Python script for processing Facebook chat history files, specifically designed to handle Thai language encoding and create simplified chat summaries.

## Features

- Decodes Thai Unicode text to readable format
- Simplifies chat structure by removing unnecessary metadata
- Combines multiple chat files into a single summary
- Detailed logging of all processing steps
- Progress tracking and error reporting

## Prerequisites

- Python 3.7 or higher
- Facebook chat history export files (from Facebook Page)

## Installation

1. Clone this repository or download the script:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Directory Structure

Your directory should look like this:
```
your-working-directory/
├── prepare-fb-chat-history.py
├── messages/
│   └── inbox/
│       ├── chat1_xxx/
│       │   └── message_1.json
│       └── chat2_xxx/
│           └── message_1.json
└── logs/
    └── fb_processing_[timestamp].log
```

## Usage

### Basic Usage

Run the script with a directory path that contains the `messages/inbox` folder:

```bash
python prepare-fb-chat-history.py /path/to/your/folder
```

Or run from the current directory:

```bash
python prepare-fb-chat-history.py .
```

### Command Line Options

```bash
python prepare-fb-chat-history.py -h
```

This will show all available command line options.

## Processing Steps

1. **Thai Text Decoding** (`step1_decode_thai`)
   - Input: Original JSON files from Facebook
   - Output: `*_thai.json` files
   - Function: Converts Unicode-escaped Thai text to readable Thai characters

2. **Chat Simplification** (`step2_simplify_chat`)
   - Input: `*_thai.json` files
   - Output: `*_simplify.json` files
   - Function: Removes metadata and keeps only essential message content

3. **Summary Creation** (`step3_summary_chat`)
   - Input: All `*_simplify.json` files
   - Output: `summary_chat.json`
   - Function: Combines all chat histories into a single structured file

## Output Files

1. `*_thai.json`: Decoded Thai text files
2. `*_simplify.json`: Simplified chat structure files
3. `summary_chat.json`: Final combined chat history
4. `logs/fb_processing_[timestamp].log`: Processing log file

## Log Files

Log files are created in the `logs` directory with timestamps. They contain:
- Processing steps and progress
- Error messages and warnings
- Statistics about processed files and messages

## Error Handling

The script includes comprehensive error handling:
- File not found errors
- JSON parsing errors
- Thai text decoding errors
- Each error is logged with details in the log file

## Statistics

After processing, the script provides statistics including:
- Number of files processed
- Number of files that failed
- Total messages processed

## Sample Output Structure

```json
{
  "users": [
    {
      "messages": [
        {
          "from": "user",
          "content": "message text"
        },
        {
          "from": "admin",
          "content": "response text"
        }
      ]
    }
  ]
}
```

## Troubleshooting

1. **Missing inbox directory**
   - Ensure your Facebook data export is properly extracted
   - Verify the path to the `messages/inbox` directory

2. **Encoding errors**
   - Check if the original files are corrupted
   - Verify the Facebook data export was completed successfully

3. **Processing errors**
   - Check the log files for detailed error messages
   - Verify file permissions in the working directory

## Contributing

Feel free to submit issues and enhancement requests!

