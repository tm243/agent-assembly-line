# OCR Data Loader

This module provides OCR (Optical Character Recognition) functionality for extracting text from image files.

## Features

- Supports common image formats: PNG, JPG, JPEG, TIFF, BMP, GIF
- Automatic text extraction using Tesseract OCR
- Metadata preservation (file path, image format, image dimensions)
- Integrated with the data loader factory for seamless usage

## Requirements

The OCR loader requires `pytesseract` and `Pillow` to be installed:

```bash
pip install pytesseract Pillow
```

Note: You also need to have Tesseract installed on your system:
- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
- **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage

### Direct Usage

```python
from agent_assembly_line.data_loaders.ocr_loader import OCRLoader

loader = OCRLoader()
documents = loader.load_data('/path/to/image.png')

for doc in documents:
    print(f"Extracted text: {doc.page_content}")
    print(f"Image format: {doc.metadata['image_format']}")
    print(f"Image size: {doc.metadata['image_size']}")
```

### Via Data Loader Factory

```python
from agent_assembly_line.data_loaders.data_loader_factory import DataLoaderFactory

# Automatic detection based on file extension
loader_type, source = DataLoaderFactory.guess_source_type(config_with_image_file)
loader = DataLoaderFactory.get_loader(loader_type)
documents = loader.load_data(source)

# Or explicitly request OCR loader
loader = DataLoaderFactory.get_loader('ocr')
documents = loader.load_data('/path/to/image.jpg')
```

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tiff)
- BMP (.bmp)
- GIF (.gif)

## Error Handling

The OCR loader includes robust error handling:

- **File not found**: Returns empty list silently
- **No text detected**: Returns empty list silently
- **Image processing errors**: Returns empty list silently
- **Missing dependencies**: Raises ImportError with installation instructions

## Metadata

Each extracted document includes the following metadata:

- `source`: Always set to "ocr"
- `file_path`: Full path to the processed image file
- `image_format`: Original image format (PNG, JPEG, etc.)
- `image_size`: Tuple of (width, height) in pixels

## Testing

The OCR loader includes comprehensive unit tests covering:

- Successful text extraction
- Empty text handling
- File not found scenarios
- Exception handling
- Import error handling
- Whitespace normalization

Run tests with:

```bash
python -m pytest tests/non-llm/test_ocr_loader.py -v
```