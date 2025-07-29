import json
import os
import sys

def convert_txt_to_json(input_file, output_file=None):
    """
    Converts a text file with one payload per line to a JSON file
    containing an array of payloads.
    """
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.json'
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Read all lines and filter out empty ones
            payloads = [line.strip() for line in f if line.strip()]
        
        # Write payloads to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(payloads, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted {len(payloads)} payloads from {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_payloads.py input_file.txt [output_file.json]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_txt_to_json(input_file, output_file)

if __name__ == "__main__":
    main()