#!/usr/bin/env python3

import sys
import os
from agent_assembly_line.data_loaders.ocr_loader import OCRLoader

def main():
    if len(sys.argv) != 2:
        print("Usage: python ocr_example.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found")
        sys.exit(1)
    
    valid_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
    if not image_path.lower().endswith(valid_extensions):
        print(f"Warning: '{image_path}' may not be a supported image format")
        print(f"Supported formats: {', '.join(valid_extensions)}")
    
    try:
        loader = OCRLoader()
        print(f"Processing image: {image_path}")
        documents = loader.load_data(image_path)
        
        if documents:
            print("Text extracted:")
            print(documents[0].page_content)
            print(f"\nImage info: {documents[0].metadata['image_format']} {documents[0].metadata['image_size']}")
        else:
            print("No text found in image")
            print("This could be due to:")
            print("- Image quality too low for OCR")
            print("- Image contains no readable text")
            sys.exit(1)
            
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()