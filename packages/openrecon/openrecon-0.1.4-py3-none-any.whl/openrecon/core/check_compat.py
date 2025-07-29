#!/usr/bin/env python3
import json
import sys

def check_payload_file(payload_file):
    """
    Check if a payload file is compatible with the SQL injection scanner.
    Returns True if compatible, False otherwise.
    """
    try:
        # Try to load the file as JSON
        with open(payload_file, 'r') as f:
            payloads = json.load(f)
        
        # Check if the file contains a list
        if not isinstance(payloads, list):
            print("Error: Payload file must contain a JSON array of strings")
            return False
        
        # Check if all entries are strings
        for i, payload in enumerate(payloads):
            if not isinstance(payload, str):
                print(f"Error: Entry {i} is not a string: {payload}")
                return False
        
        print(f"Success: Payload file is compatible. Contains {len(payloads)} payloads.")
        
        # Print a few samples
        if len(payloads) > 0:
            print("\nSample payloads:")
            for i in range(min(5, len(payloads))):
                print(f"  {i+1}. {payloads[i]}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_payload_compatibility.py payload_file.json")
        return
    
    payload_file = sys.argv[1]
    check_payload_file(payload_file)

if __name__ == "__main__":
    main()