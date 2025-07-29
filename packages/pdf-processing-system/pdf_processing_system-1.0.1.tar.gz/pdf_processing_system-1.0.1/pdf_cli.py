#!/usr/bin/env python3
"""
Command-line interface for PDF extractor.
"""

import argparse
import os
import sys
import json
from extract_pdf_content import (
    main as extract_main,
    validate_pdf_file,
    PDFProcessingError,
)


def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    else:
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Advanced PDF Content Extractor with Intelligent Section Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_cli.py document.pdf                    # Process with default settings
  python pdf_cli.py document.pdf --parts 6          # Split into 6 equal parts
  python pdf_cli.py document.pdf --output ./results  # Custom output directory with timestamp
  python pdf_cli.py document.pdf --output ./results --no-timestamps  # Exact output directory

  # Single component extraction (fastest)
  python pdf_cli.py document.pdf --text-only        # Extract only text content
  python pdf_cli.py document.pdf --images-only      # Extract only embedded images
  python pdf_cli.py document.pdf --page-images-only # Convert only pages to images

  # Skip specific components
  python pdf_cli.py document.pdf --no-images        # Skip embedded image extraction
  python pdf_cli.py document.pdf --no-page-images   # Skip page-to-image conversion
  python pdf_cli.py document.pdf --no-splitting     # Skip all PDF splitting
  python pdf_cli.py document.pdf --no-sections      # Skip section splitting only
  python pdf_cli.py document.pdf --no-equal-parts   # Skip equal parts splitting only
  # Other options
  python pdf_cli.py document.pdf --config my_config.json  # Use custom config
  python pdf_cli.py --test                          # Run unit tests
  python pdf_cli.py --batch batch_files.txt         # Process multiple files
  python pdf_cli.py --analyze document.pdf          # Analyze PDF structure only
  
  # Combine page images into PDF
  python pdf_cli.py --combine-images ./page_images/ --output ./results  # Combine images to PDF""",
    )

    parser.add_argument("pdf_file", nargs="?", help="Path to the PDF file to process")
    parser.add_argument("--output", "-o", help="Output directory for processed files")
    parser.add_argument(
        "--parts", "-p", type=int, help="Number of equal parts to split into"
    )

    # Individual component control
    parser.add_argument(
        "--no-images", action="store_true", help="Skip embedded image extraction"
    )
    parser.add_argument(
        "--no-page-images", action="store_true", help="Skip page-to-image conversion"
    )
    parser.add_argument(
        "--no-splitting",
        action="store_true",
        help="Skip PDF splitting (both equal parts and sections)",
    )
    parser.add_argument(
        "--no-sections",
        action="store_true",
        help="Skip intelligent section splitting only",
    )
    parser.add_argument(
        "--no-equal-parts", action="store_true", help="Skip equal parts splitting only"
    )

    # Extraction-only modes
    parser.add_argument(
        "--text-only", action="store_true", help="Extract only text content (fastest)"
    )
    parser.add_argument(
        "--images-only", action="store_true", help="Extract only embedded images"
    )
    parser.add_argument(
        "--page-images-only", action="store_true", help="Convert only pages to images"
    )
    
    # PDF creation from images
    parser.add_argument(
        "--combine-images", 
        help="Combine page images from a directory into a single PDF (provide directory path)"
    )

    # Other options
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Skip automatic timestamped subdirectories",
    )
    parser.add_argument(
        "--config", "-c", default="config.json", help="Path to configuration file"
    )
    parser.add_argument("--test", action="store_true", help="Run unit tests")
    parser.add_argument(
        "--validate", "-v", action="store_true", help="Only validate the PDF file"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )
    parser.add_argument(
        "--memory-stats", action="store_true", help="Show memory usage statistics"
    )
    parser.add_argument(
        "--batch",
        help="Process multiple PDF files from a text file (one file path per line)",
    )
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze PDF structure and metadata only"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actual processing",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "xml"],
        default="text",
        help="Output format for extracted content",
    )
    parser.add_argument(
        "--threshold", type=int, help="White text color threshold (override config)"
    )
    parser.add_argument(
        "--verbose-errors",
        action="store_true",
        help="Include detailed error tracebacks in batch processing",
    )

    return parser.parse_args()


def run_tests():
    """Run unit tests."""
    import unittest
    import test_pdf_extractor

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_pdf_extractor)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


def validate_only(pdf_file):
    """Only validate the PDF file."""
    try:
        validate_pdf_file(pdf_file)
        print(f"✅ PDF file '{pdf_file}' is valid and ready for processing.")
        return 0
    except PDFProcessingError as e:
        print(f"❌ PDF validation failed: {e}")
        return 1


def combine_images_command(images_dir, output_dir=None):
    """Combine page images from a directory into a single PDF."""
    try:
        from extract_pdf_content import combine_images_to_pdf
        
        # Validate input directory
        if not os.path.exists(images_dir):
            print(f"❌ Error: Images directory '{images_dir}' not found.")
            return 1
        
        if not os.path.isdir(images_dir):
            print(f"❌ Error: '{images_dir}' is not a directory.")
            return 1
        
        # Determine output file path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_pdf = os.path.join(output_dir, "combined_pages.pdf")
        else:
            # Default to same directory as images
            output_pdf = os.path.join(os.path.dirname(images_dir), "combined_pages.pdf")
        
        print(f"🔄 Combining page images from: {images_dir}")
        print(f"📄 Output PDF: {output_pdf}")
        
        # Combine images to PDF
        result = combine_images_to_pdf(images_dir, output_pdf)
        
        print(f"✅ Successfully created PDF with {result['page_count']} pages")
        print(f"📊 File size: {result['file_size_mb']} MB")
        print(f"📁 Saved to: {result['output_file']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error combining images to PDF: {e}")
        return 1


def show_memory_stats():
    """Show current memory usage statistics."""
    try:
        from extract_pdf_content import optimize_memory_usage

        stats = optimize_memory_usage()

        print("Memory Usage Statistics:")
        print(f"  RSS (Resident Set Size): {stats['rss_mb']:.1f} MB")
        print(f"  VMS (Virtual Memory Size): {stats['vms_mb']:.1f} MB")
        print(f"  Memory Percentage: {stats['percent']:.1f}%")
        print(f"  Available Memory: {stats['available_mb']:.1f} MB")

    except ImportError:
        print(
            "Memory monitoring requires 'psutil' package. Install with: pip install psutil"
        )


def process_batch(batch_file, config, **kwargs):
    """Process multiple PDF files from a batch file with detailed error categorization."""
    import datetime
    import traceback

    # Error categorization structure
    error_categories = {
        "file_not_found": [],
        "permission_denied": [],
        "pdf_corruption": [],
        "validation_errors": [],
        "processing_errors": [],
        "memory_errors": [],
        "unknown_errors": [],
    }

    success_results = []

    if not os.path.exists(batch_file):
        print(f"❌ Batch file not found: {batch_file}")
        return 1

    try:
        with open(batch_file, "r") as f:
            pdf_files = [line.strip() for line in f.readlines() if line.strip()]

        if not pdf_files:
            print("❌ No PDF files found in the batch file.")
            return 1

        print(f"🚀 Starting batch processing of {len(pdf_files)} PDF files...")
        batch_start_time = datetime.datetime.now()

        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_file}")
            file_start_time = datetime.datetime.now()

            # Check if file exists
            if not os.path.exists(pdf_file):
                error_info = {
                    "file": pdf_file,
                    "error": "File not found",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                error_categories["file_not_found"].append(error_info)
                print(f"  ❌ File not found: {pdf_file}")
                continue

            # Check file permissions
            try:
                with open(pdf_file, "rb") as test_file:
                    test_file.read(1)  # Try to read one byte
            except PermissionError:
                error_info = {
                    "file": pdf_file,
                    "error": "Permission denied - cannot access file",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                error_categories["permission_denied"].append(error_info)
                print(f"  ❌ Permission denied: {pdf_file}")
                continue
            except Exception as e:
                error_info = {
                    "file": pdf_file,
                    "error": f"File access error: {str(e)}",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                error_categories["unknown_errors"].append(error_info)
                print(f"  ❌ File access error: {pdf_file} - {e}")
                continue

            try:
                # Validate PDF before processing
                validate_pdf_file(pdf_file)

                # Process the PDF
                result = extract_main(pdf_path=pdf_file, config=config, **kwargs)

                if result:
                    processing_time = (
                        datetime.datetime.now() - file_start_time
                    ).total_seconds()
                    success_info = {
                        "file": pdf_file,
                        "processing_time_seconds": processing_time,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "output_dir": result.get("output_dir", "N/A"),
                        "image_count": result.get("image_count", 0),
                        "text_length": result.get("text_length", 0),
                        "section_count": result.get("section_count", 0),
                    }
                    success_results.append(success_info)
                    print(
                        f"  ✅ Successfully processed: {pdf_file} ({processing_time:.1f}s)"
                    )
                else:
                    error_info = {
                        "file": pdf_file,
                        "error": "Processing returned no result",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "processing_time_seconds": (
                            datetime.datetime.now() - file_start_time
                        ).total_seconds(),
                    }
                    error_categories["processing_errors"].append(error_info)
                    print(f"  ❌ Processing failed (no result): {pdf_file}")

            except PDFProcessingError as e:
                error_type = (
                    "pdf_corruption"
                    if "corrupt" in str(e).lower() or "invalid" in str(e).lower()
                    else "validation_errors"
                )
                error_info = {
                    "file": pdf_file,
                    "error": str(e),
                    "error_type": "PDFProcessingError",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "processing_time_seconds": (
                        datetime.datetime.now() - file_start_time
                    ).total_seconds(),
                }
                error_categories[error_type].append(error_info)
                print(f"  ❌ PDF validation/processing error: {pdf_file} - {e}")

            except MemoryError as e:
                error_info = {
                    "file": pdf_file,
                    "error": f"Memory error: {str(e)}",
                    "error_type": "MemoryError",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "processing_time_seconds": (
                        datetime.datetime.now() - file_start_time
                    ).total_seconds(),
                }
                error_categories["memory_errors"].append(error_info)
                print(f"  ❌ Memory error: {pdf_file} - {e}")

            except Exception as e:
                # Categorize other exceptions
                error_message = str(e).lower()
                if "memory" in error_message or "out of memory" in error_message:
                    category = "memory_errors"
                elif (
                    "corrupt" in error_message
                    or "damaged" in error_message
                    or "invalid pdf" in error_message
                ):
                    category = "pdf_corruption"
                else:
                    category = "unknown_errors"

                error_info = {
                    "file": pdf_file,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "processing_time_seconds": (
                        datetime.datetime.now() - file_start_time
                    ).total_seconds(),
                    "traceback": (
                        traceback.format_exc()
                        if kwargs.get("verbose_errors", False)
                        else None
                    ),
                }
                error_categories[category].append(error_info)
                print(f"  ❌ {type(e).__name__}: {pdf_file} - {e}")

        # Generate detailed batch summary
        batch_end_time = datetime.datetime.now()
        total_processing_time = (batch_end_time - batch_start_time).total_seconds()

        print(f"\n" + "=" * 60)
        print(f"📊 BATCH PROCESSING SUMMARY")
        print(f"=" * 60)
        print(f"⏱️  Total Processing Time: {total_processing_time:.1f} seconds")
        print(f"📁 Total Files: {len(pdf_files)}")
        print(f"✅ Successfully Processed: {len(success_results)}")
        print(f"❌ Failed: {sum(len(errors) for errors in error_categories.values())}")

        if success_results:
            avg_processing_time = sum(
                r["processing_time_seconds"] for r in success_results
            ) / len(success_results)
            total_images = sum(r["image_count"] for r in success_results)
            total_text_length = sum(r["text_length"] for r in success_results)
            print(
                f"📈 Average Processing Time: {avg_processing_time:.1f} seconds per file"
            )
            print(f"🖼️  Total Images Extracted: {total_images}")
            print(f"📝 Total Text Characters: {total_text_length:,}")

        # Display error breakdown
        print(f"\n📋 ERROR BREAKDOWN:")
        for category, errors in error_categories.items():
            if errors:
                category_name = category.replace("_", " ").title()
                print(f"  {category_name}: {len(errors)} files")
                for error in errors[:3]:  # Show first 3 errors of each type
                    print(f"    - {os.path.basename(error['file'])}: {error['error']}")
                if len(errors) > 3:
                    print(f"    ... and {len(errors) - 3} more files")

        # Save detailed error report if there were errors
        total_errors = sum(len(errors) for errors in error_categories.values())
        if total_errors > 0:
            error_report_path = (
                f"batch_error_report_{batch_start_time.strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                error_report = {
                    "batch_start_time": batch_start_time.isoformat(),
                    "batch_end_time": batch_end_time.isoformat(),
                    "total_processing_time_seconds": total_processing_time,
                    "total_files": len(pdf_files),
                    "successful_files": len(success_results),
                    "failed_files": total_errors,
                    "error_categories": error_categories,
                    "success_results": success_results,
                }

                with open(error_report_path, "w", encoding="utf-8") as f:
                    json.dump(error_report, f, indent=2, ensure_ascii=False)
                print(f"\n📄 Detailed error report saved: {error_report_path}")
            except Exception as e:
                print(f"\n⚠️  Could not save error report: {e}")

        return 0 if total_errors == 0 else 1

    except Exception as e:
        print(f"❌ Critical error during batch processing: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1


def analyze_pdf_structure(pdf_path):
    """Analyze the structure of a PDF file without extracting content."""
    from extract_pdf_content import validate_pdf_file

    try:
        validate_pdf_file(pdf_path)

        import fitz

        doc = fitz.open(pdf_path)

        # Get basic PDF info
        page_count = len(doc)
        metadata = doc.metadata
        toc = doc.get_toc()

        # Sample some pages to check for images and text
        sample_pages = min(5, page_count)
        pages_with_images = 0
        pages_with_text = 0
        text_sample = ""

        for i in range(sample_pages):
            page = doc[i]

            # Check for images
            if page.get_images():
                pages_with_images += 1

            # Check for text
            text = page.get_text()
            if text.strip():
                pages_with_text += 1
                if len(text_sample) < 500:  # Get a small sample
                    text_sample += text[:100] + "...\n"

        # Estimate content distribution
        if sample_pages > 0:
            image_percentage = (pages_with_images / sample_pages) * 100
            text_percentage = (pages_with_text / sample_pages) * 100
        else:
            image_percentage = text_percentage = 0

        # Print analysis
        print("\n📊 PDF Structure Analysis")
        print("=" * 50)
        print(f"📄 File: {pdf_path}")
        print(f"📚 Pages: {page_count}")

        if metadata:
            print("\n📝 Metadata:")
            for key, value in metadata.items():
                if value:
                    print(f"  {key}: {value}")

        if toc:
            print(f"\n📑 Table of Contents: {len(toc)} entries")
            for entry in toc[:5]:  # Show first 5 entries
                print(f"  {'  ' * (entry[0]-1)}- {entry[1]} (Page {entry[2]})")
            if len(toc) > 5:
                print(f"  ... and {len(toc) - 5} more entries")
        else:
            print("\n❌ No Table of Contents found")

        print("\n📊 Content Analysis:")
        print(f"  Estimated images coverage: {image_percentage:.1f}%")
        print(f"  Estimated text coverage: {text_percentage:.1f}%")

        print("\n📄 Text Sample:")
        if text_sample:
            lines = text_sample.split("\n")
            for line in lines[:3]:
                if line.strip():
                    print(f"  {line}")
        else:
            print("  No text found in sample pages")

        # Check if text might be white or hidden
        has_potential_hidden_text = False
        if sample_pages > 0:
            for i in range(min(3, sample_pages)):
                page = doc[i]
                dict_text = page.get_text("dict")

                for block in dict_text.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                color = span.get("color", 0)
                                if color > 15000000:  # Possible white text
                                    has_potential_hidden_text = True
                                    break

        if has_potential_hidden_text:
            print("\n⚠️ Warning: Document may contain hidden (white) text!")

        print("\n🔍 Processing Recommendations:")

        if not toc and page_count > 20:
            print("  • Consider using custom section detection (no TOC found)")

        if image_percentage > 70:
            print("  • Document is image-heavy - OCR may be needed for text")

        if has_potential_hidden_text:
            print("  • Enable white text filtering when extracting text")

        if page_count > 100:
            print("  • Consider splitting into smaller parts for processing")

        doc.close()
        return 0

    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback

        print(traceback.format_exc())
        return 1


def main():
    """Main CLI function."""
    args = parse_arguments()    # Handle special commands
    if args.test:
        return run_tests()
    
    # Handle combine images to PDF
    if args.combine_images:
        return combine_images_command(args.combine_images, args.output)

    if args.memory_stats:
        show_memory_stats()
        if not args.pdf_file:
            return 0

    # Validate required arguments
    if not args.pdf_file:
        print("Error: PDF file argument is required (unless using --test)")
        return 1

    if not os.path.exists(args.pdf_file):
        print(f"Error: PDF file '{args.pdf_file}' not found.")
        return 1

    # Handle validation-only mode
    if args.validate:
        return validate_only(args.pdf_file)
    # Load configuration
    config = load_config(args.config)

    # Configure logging based on quiet flag
    if args.quiet:
        import logging

        logging.getLogger().setLevel(logging.WARNING)
    try:
        # Build kwargs for the main function
        kwargs = {
            "skip_images": args.no_images,
            "skip_sections": args.no_sections,
            "skip_timestamps": args.no_timestamps,
            "skip_page_images": args.no_page_images,
            "skip_splitting": args.no_splitting,
            "skip_equal_parts": args.no_equal_parts,
        }

        # Handle extraction-only modes
        if args.text_only:
            kwargs.update(
                {
                    "skip_images": True,
                    "skip_page_images": True,
                    "skip_splitting": True,
                    "skip_sections": True,
                    "skip_equal_parts": True,
                }
            )
        elif args.images_only:
            kwargs.update(
                {
                    "skip_page_images": True,
                    "skip_splitting": True,
                    "skip_sections": True,
                    "skip_equal_parts": True,
                    "text_only_mode": False,  # Still need text for processing but don't save separately
                }
            )
        elif args.page_images_only:
            kwargs.update(
                {
                    "skip_images": True,
                    "skip_splitting": True,
                    "skip_sections": True,
                    "skip_equal_parts": True,
                    "text_only_mode": False,  # Still need text for processing but don't save separately
                }
            )

        # Handle skip_splitting override (affects both equal parts and sections)
        if args.no_splitting:
            kwargs["skip_sections"] = True
            kwargs["skip_equal_parts"] = True

        if args.output:
            kwargs["output_dir"] = args.output

        if args.parts:
            kwargs["num_parts"] = args.parts

        print(f"Processing PDF: {args.pdf_file}")
        print(f"Configuration: {args.config}")

        if args.output:
            print(f"Output directory: {args.output}")
        if args.parts:
            print(f"Equal parts: {args.parts}")

        # Display extraction mode information
        if args.text_only:
            print("Mode: TEXT-ONLY extraction (fastest)")
        elif args.images_only:
            print("Mode: IMAGES-ONLY extraction")
        elif args.page_images_only:
            print("Mode: PAGE-IMAGES-ONLY conversion")
        else:
            print("Mode: Full processing with selective options")

            if args.no_images:
                print("  Embedded image extraction: DISABLED")

            if args.no_page_images:
                print("  Page-to-image conversion: DISABLED")

            if args.no_splitting:
                print("  PDF splitting (all types): DISABLED")
            elif args.no_sections:
                print("  Section-based splitting: DISABLED")
            elif args.no_equal_parts:
                print("  Equal parts splitting: DISABLED")

            if args.no_timestamps:
                print("  Automatic timestamped subdirectories: DISABLED")

        # Call the main function with parameters
        result = extract_main(pdf_path=args.pdf_file, config=config, **kwargs)

        # Display results if available
        if result:
            print(f"\n📊 Processing Results:")
            print(f"   📁 Output Directory: {result.get('output_dir', 'N/A')}")
            print(f"   🖼️  Images Extracted: {result.get('image_count', 0)}")
            print(f"   📝 Text Length: {result.get('text_length', 0):,} characters")
            print(f"   📄 Sections Created: {result.get('section_count', 0)}")

        print("\n✅ PDF processing completed successfully!")
        return 0

    except PDFProcessingError as e:
        print(f"❌ PDF processing failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
