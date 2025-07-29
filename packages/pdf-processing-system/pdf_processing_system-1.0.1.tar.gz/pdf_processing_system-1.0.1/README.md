﻿# PDF Processing System

A comprehensive PDF content extraction and intelligent splitting system that can process large PDF documents into manageable sections.

## Features

- **Text Extraction**: Extract text content with white text filtering
- **Image Extraction**: Extract and convert images (CMYK to RGB support)
- **Page-to-Image Conversion**: Convert each PDF page to high-quality PNG images (300 DPI)
- **Equal Parts Splitting**: Split PDFs into equal-sized parts
- **Intelligent Section Splitting**: Use Table of Contents structure for smart splitting
- **Fuzzy String Matching**: Intelligent section detection with confidence scoring
- **JSON Metadata**: Complete extraction metadata and processing logs
- **Automatic Timestamped Organization**: Default timestamped subdirectories for organized outputs
- **CLI Interface**: Command-line tool with comprehensive options and help
- **Sample Files Included**: Four sample PDFs for testing and demonstration
- **🆕 Selective Extraction**: High-performance single-function modes (text-only, images-only, page-images-only)
- **🆕 Granular Control**: Skip specific processing steps (--no-page-images, --no-splitting, --no-equal-parts)
- **🆕 Performance Optimization**: Text-only extraction in ~0.4 seconds vs ~20+ seconds full processing
- **🆕 Image-to-PDF Combination**: Combine page images back into a single PDF with full fidelity

## Sample Files

The project includes sample PDF files for testing and demonstration:

- `samples/sample-pdf-with-images.pdf` - Multi-page PDF with images (3.9MB, 10 pages) - **Default test file**
- `samples/file-example_PDF_1MB.pdf` - Standard PDF for basic testing (1MB)
- `samples/image-based-pdf-sample.pdf` - Image-heavy PDF for image extraction testing
- `samples/dummy.pdf` - Simple PDF for quick validation tests

All examples in this documentation use the sample files, ensuring you can run them immediately after installation.

## Installation

### Requirements

```bash
pip install PyMuPDF pdf2image
```

### Dependencies

- `PyMuPDF (fitz)`: PDF processing
- `pdf2image`: PDF to image conversion
- `os`, `json`, `datetime`, `math`, `re`: Built-in Python libraries
- `difflib`: Fuzzy string matching

### Installation Notes

#### Known Dependency Conflicts

During installation, you may see dependency conflict warnings like:

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
streamlit 1.32.0 requires packaging<24,>=16.8, but you have packaging 25.0 which is incompatible.
streamlit 1.32.0 requires pillow<11,>=7.1.0, but you have pillow 11.2.1 which is incompatible.
```

**This is normal and does not affect functionality.** These conflicts occur when other packages (like Streamlit) have stricter version requirements than our package. The PDF Processing System works correctly with the newer versions of these dependencies.

#### Package Installation

```bash
# Install from wheel (recommended)
pip install pdf_processing_system-1.0.0-py3-none-any.whl

# Or install from source
pip install pdf_processing_system-1.0.0.tar.gz

# Test installation
pdf-extractor --help
```

## Usage

### Basic Usage

#### Command Line Interface (Recommended)

```bash
# Default: Automatic timestamped organization (NEW DEFAULT BEHAVIOR)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results
# Creates: results/extraction_20250527_143022/

# Process without embedded images
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --no-images
# Creates: results/extraction_20250527_143055/

# When you need exact output control (legacy behavior)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --no-timestamps
# Creates: results/ (directly in the folder)

# Split into 3 equal parts with timestamped organization
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --parts 3
# Creates: results/extraction_20250527_143122/equal_parts/

# Validate PDF file
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --validate

# Combine page images into PDF
python pdf_cli.py --combine-images ./page_images --output ./results

# View help and all options
python pdf_cli.py --help
```

### Selective Extraction Modes

The PDF extractor supports selective extraction for improved performance and specific use cases:

#### High-Performance Single-Function Extraction

```bash
# Extract only text content (fastest - ~0.4 seconds vs ~20+ seconds full processing)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --text-only

# Extract only embedded images (~1-2 seconds)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --images-only

# Convert only pages to images (~4-6 seconds for 10 pages)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --page-images-only

# Combine page images back into a single PDF
python pdf_cli.py --combine-images ./page_images --output results
```

#### Granular Processing Control

```bash
# Skip page-to-image conversion (saves ~50% processing time)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --no-page-images

# Skip all PDF splitting operations
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --no-splitting

# Skip only equal-parts splitting (keep section-based splitting)
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --no-equal-parts

# Combine multiple skip options
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output results --no-page-images --no-equal-parts
```

#### Image-to-PDF Combination

Convert page images back into a single PDF with full fidelity:

```bash
# Combine page images from a directory into a single PDF
python pdf_cli.py --combine-images ./page_images --output ./results
# Creates: results/combined_pages.pdf

# Complete round-trip workflow: PDF → Images → PDF
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --page-images-only --output ./step1
python pdf_cli.py --combine-images ./step1/extraction_*/page_images --output ./step2
# Result: Original PDF reconstructed with high fidelity

# Combine images with custom output directory
python pdf_cli.py --combine-images "processed_data/page_images" --output "final_pdfs"
# Creates: final_pdfs/combined_pages.pdf
```

#### Batch Processing

Process multiple PDF files efficiently:

```bash
# Create a batch file listing PDFs (one per line)
echo "samples/sample-pdf-with-images.pdf" > batch_files.txt
echo "samples/file-example_PDF_1MB.pdf" >> batch_files.txt

# Process all files in batch
python pdf_cli.py --batch batch_files.txt --output batch_results

# Batch processing with selective extraction
python pdf_cli.py --batch batch_files.txt --output batch_results --text-only

# Include detailed error information for debugging
python pdf_cli.py --batch batch_files.txt --output batch_results --verbose-errors
```

#### Performance Comparison

| Mode | Processing Time | Output | Use Case |
|------|----------------|--------|----------|
| **Full Processing** | ~20-25 seconds | All features | Complete analysis |
| **Text Only** | ~0.4 seconds | Text file only | Quick content review |
| **Images Only** | ~1-2 seconds | Embedded images only | Image extraction |
| **Page Images Only** | ~4-6 seconds | Page PNGs only | Visual conversion |
| **Combine Images** | ~25-30 seconds | Single PDF from images | Reconstruct PDF from pages |
| **No Page Images** | ~12-15 seconds | All except page images | Skip heavy conversion |
| **No Splitting** | ~8-12 seconds | No PDF splits | Keep original structure |

### Timestamped vs Exact Output Examples

**🆕 Default Timestamped Behavior:**
```bash
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output analysis
```
**Result:**
```
analysis/
└── extraction_20250527_143022/
    ├── extracted_text.txt
    ├── page_images/
    ├── equal_parts/
    └── ... (all outputs organized here)
```

**📁 Exact Directory Control:**
```bash
python pdf_cli.py "samples/sample-pdf-with-images.pdf" --output analysis --no-timestamps
```
**Result:**
```
analysis/
├── extracted_text.txt
├── page_images/
├── equal_parts/
└── ... (outputs directly in analysis/)
```

**💡 Why Use Timestamped (Default)?**
- Multiple extractions don't overwrite each other
- Easy to compare different processing runs
- Chronological organization for project tracking
- Perfect for experimentation and iterative work

**💡 When to Use `--no-timestamps`?**
- Integration with existing scripts that expect exact paths
- When you only need one extraction result
- Automated workflows that manage their own organization

### Output Structure

#### With Timestamped Subdirectories (Default)

```
your_output_directory/
└── extraction_YYYYMMDD_HHMMSS/
    ├── extracted_text.txt
    ├── extracted_images/
    │   ├── image_001.png
    │   └── ...
    ├── page_images/
    │   ├── page_001.png
    │   ├── page_002.png
    │   └── ...
    ├── equal_parts/
    │   ├── part_1_pages_1-N.pdf
    │   ├── part_2_pages_N-M.pdf
    │   └── ...
    ├── extracted_content.json
    ├── section_info.json
    ├── processing_summary.json
    ├── 01_Section_Name_pages_X-Y.pdf
    ├── 02_Next_Section_pages_A-B.pdf
    └── ...
```

#### With `--no-timestamps` Flag

```
your_output_directory/
├── extracted_text.txt
├── extracted_images/
│   ├── image_001.png
│   └── ...
├── page_images/
│   ├── page_001.png
│   ├── page_002.png
│   └── ...
├── equal_parts/
│   ├── part_1_pages_1-N.pdf
│   ├── part_2_pages_N-M.pdf
│   └── ...
├── extracted_content.json
├── section_info.json
├── processing_summary.json
├── 01_Section_Name_pages_X-Y.pdf
├── 02_Next_Section_pages_A-B.pdf
└── ...
```

**Key improvements:**
- All outputs are contained within your specified output directory
- Equal parts PDFs are organized in an `equal_parts/` subdirectory
- No more scattered timestamped directories across different locations
- Consistent and logical organization for easy access

## Configuration

The system can be configured via the `config.json` file or by passing parameters directly to functions.

### Key Configuration Options

```json
{
  "processing": {
    "enable_page_conversion": true,
    "page_image_dpi": 300,
    "page_image_format": "png",
    "white_text_threshold": 15000000,
    "default_equal_parts": 4
  },
  "output": {
    "images_dirname": "extracted_images",
    "page_images_dirname": "page_images"
  }
}
```

### Section Definitions

The system uses predefined section definitions that can be customized:

```python
predefined_sections = {
    "Message From Founders": {"start": 3, "end": 4},
    "General Information": {"start": 5, "end": 31},
    "Sales": {"start": 32, "end": 78},
    "Business Location A": {"start": 79, "end": 92},
    "Business Location B": {"start": 93, "end": 96},
    "Miscellaneous": {"start": 97, "end": 112}
}
```

### Fuzzy Matching Threshold

Adjust the confidence threshold for section matching:

```python
# In fuzzy_match_section_titles function
similarity = SequenceMatcher(None, section_title.lower(), extracted_title.lower()).ratio()
if similarity > 0.6:  # 60% minimum threshold
```

### Text Color Filtering

Adjust the white text filtering threshold:

```python
if color > 15000000:  # Adjust threshold as needed
    continue  # Skip white/very light text
```

### Page-to-Image Settings

Configure image conversion quality and format:

```python
# In convert_pages_to_images function
dpi = 300  # High-quality output (300 DPI)
fmt = 'PNG'  # Output format
```

Or via configuration file:

```json
{
  "processing": {
    "enable_page_conversion": true,
    "page_image_dpi": 300,
    "page_image_format": "png"
  }
}
```

## API Reference

### Core Functions

#### `extract_text(pdf_path)`
Extracts text from PDF with page separators and filters out white text.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- `str`: Extracted text with page markers

#### `extract_images(pdf_path, output_dir)`
Extracts all images from PDF and saves them with metadata.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save images

**Returns:**
- `list`: Image metadata with filenames and properties

#### `convert_pages_to_images(pdf_path, output_dir)`
Converts each PDF page to a high-quality PNG image at 300 DPI.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save page images

**Returns:**
- `dict`: Page images metadata including count, DPI, format, and file list

#### `split_pdf_into_equal_parts(pdf_path, output_dir, num_parts=4)`
Splits PDF into equal-sized parts.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save split files
- `num_parts` (int): Number of parts to split into (default: 4)

**Returns:**
- `list`: Paths to created PDF parts

#### `split_pdf_by_sections(pdf_path, output_dir, toc_structure)`
Splits PDF based on Table of Contents structure.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `output_dir` (str): Directory to save section files
- `toc_structure` (dict): Section definitions with page ranges

**Returns:**
- `list`: Paths to created section files

## Examples

### Processing a Custom PDF

```python
# Modify the main function
if __name__ == "__main__":
    pdf_path = "path/to/your/document.pdf"
    
    # Extract text
    text = extract_text(pdf_path)
    
    # Create output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"processed_data/extraction_{timestamp}"
    
    # Save text
    save_text(text, output_dir)
    
    # Extract images
    image_metadata = extract_images(pdf_path, output_dir)
    
    # Convert pages to images
    page_images_metadata = convert_pages_to_images(pdf_path, output_dir)
    
    # Split into equal parts
    equal_parts_dir = f"processed_data/equal_parts_{timestamp}"
    split_pdf_into_equal_parts(pdf_path, equal_parts_dir, num_parts=4)
```

### Custom Section Definitions

```python
custom_sections = {
    "Introduction": {"start": 1, "end": 10},
    "Chapter 1": {"start": 11, "end": 25},
    "Chapter 2": {"start": 26, "end": 40},
    "Appendix": {"start": 41, "end": 50}
}

toc_structure = parse_toc_structure(pdf_path, custom_sections)
split_pdf_by_sections(pdf_path, output_dir, toc_structure)
```

## Troubleshooting

### Common Issues

1. **White Text Not Filtered**: Adjust the color threshold in `extract_text()`
2. **Section Matching Fails**: Lower the similarity threshold in fuzzy matching
3. **Memory Issues**: Process large PDFs in smaller chunks
4. **Image Conversion Errors**: Ensure proper CMYK to RGB conversion
5. **Page-to-Image Conversion Slow**: Large PDFs with many pages may take time at 300 DPI
6. **Page Images Quality Issues**: Adjust DPI setting in `convert_pages_to_images()`

### Error Handling

The system includes basic error handling for:
- File not found errors
- PDF corruption issues
- Image format conversion problems
- Page-to-image conversion failures
- Directory creation failures

## Performance Notes

- **Large PDFs**: The system can handle large documents but may require significant memory
- **Image Processing**: CMYK to RGB conversion adds processing time
- **Page-to-Image Conversion**: High DPI settings (300 DPI) create larger files and take more time
  - Typical timing: ~1-2 seconds per page at 300 DPI
  - File sizes: ~200KB-2MB per page depending on content complexity
  - Memory usage: ~10-50MB per page during conversion
- **Fuzzy Matching**: String similarity calculation scales with content size
- **🆕 Selective Extraction Performance**:
  - **Text-only**: ~0.4 seconds (50x faster than full processing)
  - **Images-only**: ~1-2 seconds (10-20x faster)
  - **Page-images-only**: ~4-6 seconds (3-5x faster)
  - **Skip page images**: ~50% time reduction
  - **Skip splitting**: ~40% time reduction
- **🆕 Memory Optimization**: Single-function modes use significantly less memory
- **🆕 Use Case Optimization**: Choose extraction mode based on specific needs for maximum efficiency

## Contributing

To contribute improvements:

1. Add error handling for edge cases
2. Implement progress bars for long operations
3. Add support for password-protected PDFs
4. Optimize memory usage for very large files
5. Add unit tests for core functions

### Testing

The project includes comprehensive unit tests for all major features:

```bash
python test_pdf_extractor.py
```

Test coverage includes:
- PDF validation and error handling
- Text extraction functionality
- Image extraction processes
- **Page-to-image conversion with DPI and format options**
- Progress indicator functionality
- Section overlap validation
- Memory optimization and document cleanup

## License

This project is for internal use and processing of business documents.
