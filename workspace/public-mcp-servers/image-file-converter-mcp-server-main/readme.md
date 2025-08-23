# Image Format Converter

A simple Python tool that converts images between different formats using PIL (Python Imaging Library).

## Features

- Converts images to various formats supported by PIL
- Handles RGBA to RGB conversion for JPEG output (with white background)
- Saves converted images in a `converted` directory
- Supports common image formats including PNG, JPEG/JPG, BMP, GIF, and more

## Installation

1. Install the required dependencies:
```bash
pip install Pillow mcp
```

2. Clone or download this repository

## Usage

The tool consists of two main files:

### Server (`image_converter_server.py`)
- Implements the image conversion logic
- Handles format validation
- Creates a `converted` directory for output files
- Manages RGBA to RGB conversion for JPEG format
- Runs as a service using FastMCP

### Client (`test_server.py`)
- Connects to the conversion service
- Sends conversion requests
- Receives paths to converted images

### Example Usage

1. First, ensure you have an image to convert (e.g., `test.png` in the root directory)

2. Run the client script:
```bash
python test_server.py
```

This will:
- Start the conversion server
- Convert your image (e.g., `test.png`) to JPG format
- Save the result in the `converted` directory
- Print the path to the converted image

## Supported Formats

The converter supports all image formats available in PIL, including:
- JPEG/JPG
- PNG
- BMP
- GIF
- And more...

## Error Handling

The converter includes error handling for common issues:
- Invalid file paths
- Unsupported formats
- Missing files
- RGBA to JPEG conversion

## Directory Structure

```text
.
├── image_converter_server.py  # Server implementation
├── test_server.py            # Client implementation
├── converted/                # Output directory (created automatically)
└── test.png                  # Example input image
```

## Notes

- All converted images are saved with unique filenames using UUID
- The converter automatically handles RGBA to RGB conversion for JPEG output
- Input paths must be relative to the root directory for security
- Output files are saved in the `converted` directory with their new format extension

