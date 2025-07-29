"""
PDF Processing System
====================

A comprehensive PDF content extraction and intelligent splitting system.

Features:
- Text extraction with white text filtering
- Image extraction and conversion (CMYK to RGB support)
- Page-to-image conversion (300 DPI PNG)
- Intelligent section splitting with TOC analysis
- High-performance selective extraction modes
- CLI interface with comprehensive options

Author: goliathuy
Version: 1.0.1
"""

__version__ = "1.0.1"
__author__ = "goliathuy"
__email__ = "aug1381-goliathuy@yahoo.com"
__description__ = "Comprehensive PDF content extraction and intelligent splitting system"

from .extract_pdf_content import (
    extract_text,
    extract_images,
    convert_pages_to_images,
    split_pdf_into_equal_parts,
    split_pdf_by_sections,
    combine_images_to_pdf,
    main,
    PDFProcessingError,
)

__all__ = [
    "extract_text",
    "extract_images", 
    "convert_pages_to_images",
    "split_pdf_into_equal_parts",
    "split_pdf_by_sections",
    "combine_images_to_pdf",
    "main",
    "PDFProcessingError",
]
