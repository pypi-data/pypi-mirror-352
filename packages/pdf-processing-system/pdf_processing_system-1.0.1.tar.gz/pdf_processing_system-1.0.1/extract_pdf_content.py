import fitz  # PyMuPDF
import os
import json
import datetime
import math
import re
import logging
import sys
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors."""

    pass


class ProgressIndicator:
    """Simple progress indicator for console output."""

    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.description = description

    def update(self, increment: int = 1):
        """Update progress and display."""
        self.current_item += increment
        percentage = (self.current_item / self.total_items) * 100
        bar_length = 30
        filled_length = int(bar_length * self.current_item // self.total_items)
        bar = "#" * filled_length + "-" * (bar_length - filled_length)

        # Use simple ASCII characters for Windows console compatibility
        try:
            progress_line = f"\r{self.description}: |{bar}| {percentage:.1f}% ({self.current_item}/{self.total_items})"
            # Ensure we can encode to the console's encoding
            sys.stdout.write(
                progress_line.encode(sys.stdout.encoding, errors="replace").decode(
                    sys.stdout.encoding
                )
            )
            sys.stdout.flush()
        except (UnicodeEncodeError, AttributeError):
            # Fallback for Windows console encoding issues
            print(
                f"{self.description}: {percentage:.1f}% ({self.current_item}/{self.total_items})"
            )

        if self.current_item >= self.total_items:
            print()  # New line when complete


def validate_pdf_file(pdf_path: str) -> bool:
    """Validate that the PDF file exists and is readable."""
    if not os.path.exists(pdf_path):
        raise PDFProcessingError(f"PDF file not found: {pdf_path}")

    if not pdf_path.lower().endswith(".pdf"):
        raise PDFProcessingError(f"File is not a PDF: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()

        if page_count == 0:
            raise PDFProcessingError(f"PDF file has no pages: {pdf_path}")

        logger.info(f"PDF validation successful: {page_count} pages found")
        return True

    except Exception as e:
        raise PDFProcessingError(f"Cannot open PDF file: {pdf_path}. Error: {str(e)}")


def extract_text(pdf_path: str, color_threshold: int = 15000000) -> str:
    """Extract text from PDF with page separators and filter out white text."""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]

        text_dict = page.get_text("dict")

        page_text = ""
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        color = span.get("color", 0)

                        # Skip white text (color close to white/very light)
                        if color > color_threshold:  # Adjust threshold as needed
                            continue

                        page_text += text

        if page_text.strip():  # Only add non-empty pages
            full_text += f"\n--- PAGE {page_num + 1} ---\n"
            full_text += page_text + "\n"

    doc.close()
    return full_text


def save_text(text: str, output_dir: str, filename: str = "extracted_text.txt"):
    """Save extracted text to file."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    logger.info(f"Text saved to: {filepath}")


def extract_images(pdf_path: str, output_dir: str) -> List[Dict]:
    """Extract all images from PDF and return metadata."""
    doc = fitz.open(pdf_path)
    image_metadata = []

    images_dir = os.path.join(output_dir, "extracted_images")
    os.makedirs(images_dir, exist_ok=True)

    image_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            try:
                # Get the image
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                # Skip if image is too small or has unsupported format
                if pix.width < 10 or pix.height < 10:
                    pix = None
                    continue

                # Convert CMYK to RGB if necessary
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                else:  # CMYK
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix1.tobytes("png")
                    pix1 = None

                # Save image
                image_count += 1
                img_filename = f"image_{image_count:03d}_page_{page_num + 1}.png"
                img_filepath = os.path.join(images_dir, img_filename)

                with open(img_filepath, "wb") as img_file:
                    img_file.write(img_data)

                # Store metadata
                image_metadata.append(
                    {
                        "filename": img_filename,
                        "page": page_num + 1,
                        "width": pix.width,
                        "height": pix.height,
                        "filepath": img_filepath,
                    }
                )

                pix = None

            except Exception as e:
                logger.warning(
                    f"Error extracting image {img_index} from page {page_num + 1}: {e}"
                )

    doc.close()
    logger.info(f"Extracted {image_count} images to: {images_dir}")
    return image_metadata


def save_json(
    text: str,
    image_metadata: List[Dict],
    output_dir: str,
    page_images_metadata: Optional[List[Dict]] = None,
    filename: str = "extracted_content.json",
):
    """Save extracted content as JSON."""
    os.makedirs(output_dir, exist_ok=True)

    if page_images_metadata is None:
        page_images_metadata = []

    content_data = {
        "extraction_date": datetime.datetime.now().isoformat(),
        "text": text,
        "embedded_images": image_metadata,
        "page_images": page_images_metadata,
        "summary": {
            "total_embedded_images": len(image_metadata),
            "total_page_images": len(page_images_metadata),
            "text_length": len(text),
        },
    }

    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content_data, f, indent=2, ensure_ascii=False)

    logger.info(f"JSON data saved to: {filepath}")


def split_pdf_into_equal_parts(
    pdf_path: str, num_parts: int = 4, output_dir: Optional[str] = None
) -> str:
    """Split PDF into equal parts by page count."""
    if output_dir is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"processed_data/equal_parts_{timestamp}"

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_per_part = math.ceil(total_pages / num_parts)

    logger.info(
        f"Splitting {total_pages} pages into {num_parts} parts ({pages_per_part} pages each)"
    )

    progress = ProgressIndicator(num_parts, "Splitting PDF into parts")

    for part_num in range(num_parts):
        start_page = part_num * pages_per_part
        end_page = min(start_page + pages_per_part - 1, total_pages - 1)

        # Skip if no pages in this part
        if start_page >= total_pages:
            break

        # Create new PDF for this part
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)

        # Save the part
        part_filename = f"part_{part_num + 1}_pages_{start_page + 1}-{end_page + 1}.pdf"
        part_filepath = os.path.join(output_dir, part_filename)
        new_doc.save(part_filepath)
        new_doc.close()

        logger.info(
            f"Part {part_num + 1}: Pages {start_page + 1}-{end_page + 1} saved to {part_filename}"
        )
        progress.update()

    doc.close()
    logger.info(f"All parts saved in: {output_dir}")
    return output_dir


def parse_toc_structure(text: str, config: Optional[Dict] = None) -> List[Dict]:
    """Parse the Table of Contents to extract section information from config or detect from text."""
    toc_sections = []

    # Load sections from config if available
    if config and "sections" in config:
        for title, page_info in config["sections"].items():
            toc_sections.append(
                {
                    "title": title,
                    "start_page": page_info["start"],
                    "end_page": page_info["end"],
                }
            )
    else:
        # Fallback: try to detect sections from the text or return empty
        # This allows for PDFs without predefined sections (like resumes)
        logger.info("No sections defined in config - skipping section-based splitting")

    return toc_sections

    return toc_sections


def fuzzy_match_section_titles(text: str, toc_sections: List[Dict]) -> List[Dict]:
    """Use fuzzy string matching to find section titles in the content and refine page numbers."""
    refined_sections = []

    # Split text into pages
    pages = text.split("--- PAGE")

    for section in toc_sections:
        section_title = section["title"]
        best_match_page = section["start_page"]
        best_match_ratio = 0

        # Search around the expected page range for better matches
        search_start = max(1, section["start_page"] - 2)
        search_end = min(len(pages), section["start_page"] + 5)

        for page_idx in range(search_start, search_end):
            if page_idx < len(pages):
                page_content = pages[page_idx]

                # Extract page number and content
                page_lines = page_content.strip().split("\n")
                if len(page_lines) > 0:
                    page_text = " ".join(page_lines[1:])  # Skip the page number line

                    # Check for fuzzy matches
                    words = page_text.split()
                    for i in range(len(words) - len(section_title.split()) + 1):
                        text_snippet = " ".join(
                            words[i : i + len(section_title.split())]
                        )
                        ratio = SequenceMatcher(
                            None, section_title.lower(), text_snippet.lower()
                        ).ratio()

                        if (
                            ratio > best_match_ratio and ratio > 0.6
                        ):  # Minimum 60% match
                            best_match_ratio = ratio
                            best_match_page = page_idx

        # Add refined section
        refined_section = section.copy()
        refined_section["detected_page"] = best_match_page
        refined_section["match_confidence"] = best_match_ratio
        refined_sections.append(refined_section)

    return refined_sections


def split_pdf_by_sections(
    pdf_path: str, sections: List[Dict], output_dir: Optional[str] = None
) -> Tuple[str, List[Dict]]:
    """Split PDF based on detected sections."""
    if output_dir is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"processed_data/sections_{timestamp}"

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    logger.info(f"Splitting {total_pages} pages into {len(sections)} sections")
    logger.info(f"Section-based split output: {output_dir}")

    section_info = []
    progress = ProgressIndicator(len(sections), "Processing sections")

    for i, section in enumerate(sections):
        # Use detected page if available and confident, otherwise use original
        if section.get("match_confidence", 0) > 0.7:
            start_page = section["detected_page"]
            logger.info(
                f"Using detected page {start_page} for '{section['title']}' (confidence: {section['match_confidence']:.2f})"
            )
        else:
            start_page = section["start_page"]
            logger.info(
                f"Using original page {start_page} for '{section['title']}' (low confidence match)"
            )

        # Calculate end page
        if i < len(sections) - 1:
            next_section = sections[i + 1]
            if next_section.get("match_confidence", 0) > 0.7:
                end_page = next_section["detected_page"] - 1
            else:
                end_page = next_section["start_page"] - 1
        else:
            end_page = total_pages

        # Ensure valid page range
        start_page = max(1, min(start_page, total_pages))
        end_page = max(start_page, min(end_page, total_pages))

        # Create new PDF for this section
        new_doc = fitz.open()
        new_doc.insert_pdf(
            doc, from_page=start_page - 1, to_page=end_page - 1
        )  # PyMuPDF uses 0-based indexing

        # Clean filename from section title
        clean_title = re.sub(r"[^\w\s-]", "", section["title"]).strip()
        clean_title = re.sub(r"[-\s]+", "_", clean_title)

        section_filename = f"{i+1:02d}_{clean_title}_pages_{start_page}-{end_page}.pdf"
        section_filepath = os.path.join(output_dir, section_filename)
        new_doc.save(section_filepath)
        new_doc.close()

        section_info.append(
            {
                "section_number": i + 1,
                "title": section["title"],
                "start_page": start_page,
                "end_page": end_page,
                "filename": section_filename,
                "match_confidence": section.get("match_confidence", 0),
            }
        )

        logger.info(
            f"Section {i+1}: '{section['title']}' - Pages {start_page}-{end_page} -> {section_filename}"
        )
        progress.update()

    # Validate section overlaps before processing
    overlaps = validate_section_overlaps(section_info)
    if overlaps:
        logger.warning(f"Found {len(overlaps)} section overlaps:")
        for overlap in overlaps:
            logger.warning(
                f"  {overlap['section1']} and {overlap['section2']} overlap on pages {overlap['overlap_pages']}"
            )

    doc.close()

    # Save section information to JSON
    section_info_path = os.path.join(output_dir, "section_info.json")
    with open(section_info_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "split_date": datetime.datetime.now().isoformat(),
                "total_sections": len(section_info),
                "sections": section_info,
                "overlaps": overlaps,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    logger.info(f"Section information saved to: {section_info_path}")
    return output_dir, section_info


def validate_section_overlaps(sections: List[Dict]) -> List[Dict]:
    """
    Validate that sections don't overlap inappropriately.

    Args:
        sections: List of section dictionaries with start_page and end_page

    Returns:
        List of overlap issues found
    """
    overlaps = []

    for i, section1 in enumerate(sections):
        for j, section2 in enumerate(sections[i + 1 :], i + 1):
            # Check if sections overlap
            if (
                section1["start_page"] <= section2["end_page"]
                and section2["start_page"] <= section1["end_page"]
            ):

                overlap_start = max(section1["start_page"], section2["start_page"])
                overlap_end = min(section1["end_page"], section2["end_page"])

                overlaps.append(
                    {
                        "section1": section1["title"],
                        "section2": section2["title"],
                        "section1_range": f"{section1['start_page']}-{section1['end_page']}",
                        "section2_range": f"{section2['start_page']}-{section2['end_page']}",
                        "overlap_pages": f"{overlap_start}-{overlap_end}",
                        "overlap_size": overlap_end - overlap_start + 1,
                    }
                )

    return overlaps


def optimize_memory_usage() -> Dict:
    """
    Get memory usage statistics and provide optimization recommendations.

    Returns:
        Dictionary with memory usage information
    """
    import psutil
    import gc

    # Force garbage collection
    gc.collect()

    # Get current process memory usage
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    memory_stats = {
        "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
        "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
        "percent": process.memory_percent(),
        "available_mb": psutil.virtual_memory().available / 1024 / 1024,
    }

    return memory_stats


def create_processing_summary(
    output_dir: str,
    section_info: List[Dict],
    image_count: int,
    text_length: int,
    page_image_count: int = 0,
) -> str:
    """Create a comprehensive processing summary."""
    summary_data = {
        "processing_completed": datetime.datetime.now().isoformat(),
        "output_directory": output_dir,
        "statistics": {
            "total_sections": len(section_info),
            "total_embedded_images": image_count,
            "total_page_images": page_image_count,
            "total_text_length": text_length,
            "sections_with_high_confidence": sum(
                1 for s in section_info if s.get("match_confidence", 0) > 0.8
            ),
            "average_confidence": (
                sum(s.get("match_confidence", 0) for s in section_info)
                / len(section_info)
                if section_info
                else 0
            ),
        },
        "sections_summary": [
            {
                "title": section["title"],
                "pages": f"{section['start_page']}-{section['end_page']}",
                "page_count": section["end_page"] - section["start_page"] + 1,
                "confidence": round(section.get("match_confidence", 0), 3),
            }
            for section in section_info
        ],
    }

    try:
        memory_stats = optimize_memory_usage()
        summary_data["memory_usage"] = memory_stats
    except ImportError:
        logger.warning("psutil not available for memory monitoring")

    # Save summary
    summary_path = os.path.join(output_dir, "processing_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Processing summary saved to: {summary_path}")
    # Print summary to console
    print("\n" + "=" * 60)
    print("PDF PROCESSING SUMMARY")
    print("=" * 60)
    print(f"📁 Output Directory: {output_dir}")
    print(f"📄 Total Sections: {summary_data['statistics']['total_sections']}")
    print(f"🖼️  Embedded Images: {summary_data['statistics']['total_embedded_images']}")
    print(f"📸 Page Images: {summary_data['statistics']['total_page_images']}")
    print(
        f"📝 Text Length: {summary_data['statistics']['total_text_length']:,} characters"
    )
    print(
        f"🎯 Average Confidence: {summary_data['statistics']['average_confidence']:.1%}"
    )
    print(
        f"✅ High Confidence Sections: {summary_data['statistics']['sections_with_high_confidence']}"
    )

    if "memory_usage" in summary_data:
        print(f"💾 Memory Usage: {summary_data['memory_usage']['rss_mb']:.1f} MB")

    print("\nSections:")
    for section in summary_data["sections_summary"]:
        confidence_icon = (
            "🎯"
            if section["confidence"] > 0.8
            else "⚠️" if section["confidence"] > 0.6 else "❓"
        )
        print(
            f"  {confidence_icon} {section['title']}: Pages {section['pages']} ({section['page_count']} pages, {section['confidence']:.1%} confidence)"
        )

    print("=" * 60)

    return summary_path


def convert_pages_to_images(
    pdf_path: str, output_dir: str, dpi: int = 300, image_format: str = "png"
) -> List[Dict]:
    """
    Convert each PDF page to an image file.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save page images
        dpi: DPI resolution for image conversion (default: 300)
        image_format: Image format to save (png, jpg, jpeg)

    Returns:
        List of dictionaries containing page image metadata
    """
    doc = fitz.open(pdf_path)
    page_images_metadata = []

    # Create subdirectory for page images
    pages_dir = os.path.join(output_dir, "page_images")
    os.makedirs(pages_dir, exist_ok=True)

    total_pages = len(doc)
    logger.info(f"Converting {total_pages} pages to images at {dpi} DPI...")

    progress = ProgressIndicator(total_pages, "Converting pages to images")

    # Calculate zoom factor for desired DPI
    # Standard PDF resolution is 72 DPI, so zoom = desired_dpi / 72
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(total_pages):
        try:
            page = doc[page_num]

            # Render page as image
            pix = page.get_pixmap(matrix=mat)

            # Generate filename
            page_filename = f"page_{page_num + 1:03d}.{image_format.lower()}"
            page_filepath = os.path.join(pages_dir, page_filename)

            # Save image
            if image_format.lower() in ["jpg", "jpeg"]:
                pix.save(page_filepath, jpg_quality=95)
            else:
                pix.save(page_filepath)

            # Store metadata
            page_images_metadata.append(
                {
                    "filename": page_filename,
                    "page_number": page_num + 1,
                    "width": pix.width,
                    "height": pix.height,
                    "dpi": dpi,
                    "format": image_format.lower(),
                    "filepath": page_filepath,
                    "file_size_bytes": os.path.getsize(page_filepath),
                }
            )

            pix = None  # Clean up memory
            progress.update()

        except Exception as e:
            logger.warning(f"Error converting page {page_num + 1} to image: {e}")
            progress.update()

    doc.close()
    logger.info(
        f"Converted {len(page_images_metadata)} pages to images in: {pages_dir}"
    )
    return page_images_metadata


def main(pdf_path: Optional[str] = None, config: Optional[Dict] = None, **kwargs):
    """
    Main processing function with configurable parameters.

    Args:
        pdf_path: Path to PDF file (default: hardcoded file)
        config: Configuration dictionary
        **kwargs: Additional processing options (output_dir, num_parts, skip_images, skip_sections)
    """
    # Use default PDF file if none provided
    if pdf_path is None:
        # Use sample PDF file for testing
        pdf_path = "samples/sample-pdf-with-images.pdf"

    # Load default config if none provided
    if config is None:
        config = {}

    try:
        validate_pdf_file(pdf_path)
    except PDFProcessingError as e:
        logger.error(e)
        return  # Create timestamp for output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_dir = kwargs.get("output_dir", "processed_data")

    # Always create timestamped subdirectories unless explicitly disabled
    if kwargs.get("skip_timestamps", False):
        output_dir = base_output_dir
    else:
        # Create timestamped subdirectory
        timestamped_dirname = f"extraction_{timestamp}"
        output_dir = os.path.join(base_output_dir, timestamped_dirname)

    logger.info("Starting PDF processing...")
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("")
    try:
        # Check for extraction-only modes
        if (
            kwargs.get("skip_images")
            and kwargs.get("skip_page_images")
            and kwargs.get("skip_splitting")
        ):
            # TEXT-ONLY mode
            logger.info("1. Extracting text (TEXT-ONLY mode)...")
            color_threshold = config.get("processing", {}).get(
                "white_text_threshold", 15000000
            )
            text = extract_text(pdf_path, color_threshold)
            save_text(text, output_dir)

            # Create minimal JSON for text-only
            logger.info("\n2. Saving text-only JSON metadata...")
            save_json(text, [], output_dir, [])

            logger.info(f"\nText-only extraction complete!")
            logger.info(f"Text content saved in: {output_dir}")

            return {
                "output_dir": output_dir,
                "text_length": len(text),
                "mode": "text-only",
            }

        elif (
            not kwargs.get("skip_images")
            and kwargs.get("skip_page_images")
            and kwargs.get("skip_splitting")
        ):
            # IMAGES-ONLY mode
            logger.info("1. Extracting embedded images (IMAGES-ONLY mode)...")
            # Still need text for processing but don't save separately
            color_threshold = config.get("processing", {}).get(
                "white_text_threshold", 15000000
            )
            text = extract_text(pdf_path, color_threshold)
            image_metadata = extract_images(pdf_path, output_dir)

            # Create minimal JSON for images-only
            logger.info("\n2. Saving images-only JSON metadata...")
            save_json("", image_metadata, output_dir, [])

            logger.info(f"\nImages-only extraction complete!")
            logger.info(f"Images saved in: {output_dir}")

            return {
                "output_dir": output_dir,
                "image_count": len(image_metadata),
                "mode": "images-only",
            }

        elif (
            kwargs.get("skip_images")
            and not kwargs.get("skip_page_images")
            and kwargs.get("skip_splitting")
        ):
            # PAGE-IMAGES-ONLY mode
            logger.info("1. Converting pages to images (PAGE-IMAGES-ONLY mode)...")
            # Still need text for processing but don't save separately
            color_threshold = config.get("processing", {}).get(
                "white_text_threshold", 15000000
            )
            text = extract_text(pdf_path, color_threshold)

            dpi = kwargs.get(
                "page_image_dpi",
                config.get("processing", {}).get("page_image_dpi", 300),
            )
            image_format = kwargs.get(
                "page_image_format",
                config.get("processing", {}).get("page_image_format", "png"),
            )
            page_images_metadata = convert_pages_to_images(
                pdf_path, output_dir, dpi=dpi, image_format=image_format
            )

            # Create minimal JSON for page-images-only
            logger.info("\n2. Saving page-images-only JSON metadata...")
            save_json("", [], output_dir, page_images_metadata)

            logger.info(f"\nPage-images-only conversion complete!")
            logger.info(f"Page images saved in: {output_dir}")

            return {
                "output_dir": output_dir,
                "page_image_count": len(page_images_metadata),
                "mode": "page-images-only",
            }

        # FULL PROCESSING MODE (with selective options)
        # Extract text
        logger.info("1. Extracting text...")
        color_threshold = config.get("processing", {}).get(
            "white_text_threshold", 15000000
        )
        text = extract_text(pdf_path, color_threshold)
        save_text(text, output_dir)
        # Extract images (unless disabled)
        image_metadata = []
        if not kwargs.get("skip_images", False):
            logger.info("\n2. Extracting images...")
            image_metadata = extract_images(pdf_path, output_dir)
        else:
            logger.info("\n2. Skipping image extraction (disabled)")

        # Convert pages to images (unless disabled)
        page_images_metadata = []
        if not kwargs.get("skip_page_images", False):
            logger.info("\n3. Converting pages to images...")
            dpi = kwargs.get(
                "page_image_dpi",
                config.get("processing", {}).get("page_image_dpi", 300),
            )
            image_format = kwargs.get(
                "page_image_format",
                config.get("processing", {}).get("page_image_format", "png"),
            )
            page_images_metadata = convert_pages_to_images(
                pdf_path, output_dir, dpi=dpi, image_format=image_format
            )
        else:
            logger.info(
                "\n3. Skipping page-to-image conversion (disabled)"
            )  # Save combined JSON
        logger.info("\n4. Saving JSON metadata...")
        save_json(text, image_metadata, output_dir, page_images_metadata)

        # Split PDF into equal parts (unless disabled)
        split_output_dir = None
        if not kwargs.get("skip_equal_parts", False):
            num_parts = kwargs.get(
                "num_parts", config.get("processing", {}).get("default_equal_parts", 4)
            )
            logger.info(f"\n5. Splitting PDF into {num_parts} equal parts...")
            equal_parts_dir = os.path.join(output_dir, "equal_parts")
            split_output_dir = split_pdf_into_equal_parts(
                pdf_path, num_parts=num_parts, output_dir=equal_parts_dir
            )
        else:
            logger.info("\n5. Skipping equal parts splitting (disabled)")

        # Section-based splitting (unless disabled)
        section_info = []
        section_output_dir = None
        if not kwargs.get("skip_sections", False):
            # Load TOC structure from config
            toc_sections = parse_toc_structure(text, config)

            # Only proceed with section splitting if sections are defined
            if toc_sections:
                # Fuzzy match section titles to refine TOC
                refined_sections = fuzzy_match_section_titles(text, toc_sections)

                # Split PDF by detected sections
                logger.info("\n6. Splitting PDF by detected sections...")
                section_output_dir, section_info = split_pdf_by_sections(
                    pdf_path, refined_sections, output_dir
                )
            else:
                logger.info(
                    "\n6. No sections defined - skipping section-based splitting..."
                )
                section_info = []
        else:
            logger.info("\n6. Skipping section-based splitting (disabled)")

        # Create comprehensive processing summary
        logger.info("\n7. Creating processing summary...")
        summary_path = create_processing_summary(
            output_dir,
            section_info,
            len(image_metadata),
            len(text),
            len(page_images_metadata),
        )

        logger.info(f"\nProcessing complete!")
        logger.info(f"Content extraction saved in: {output_dir}")
        logger.info(f"PDF parts saved in: {split_output_dir}")
        if section_output_dir:
            logger.info(f"Section-based PDF saved in: {section_output_dir}")
        logger.info(f"Processing summary: {summary_path}")

        return {
            "output_dir": output_dir,
            "split_output_dir": split_output_dir,
            "section_output_dir": section_output_dir,
            "summary_path": summary_path,
            "embedded_image_count": len(image_metadata),
            "page_image_count": len(page_images_metadata),
            "text_length": len(text),
            "section_count": len(section_info),
        }
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        raise PDFProcessingError(f"Processing failed: {str(e)}")


def combine_images_to_pdf(images_dir: str, output_dir: str) -> dict:
    """
    Combine all page images from a directory into a single PDF file.

    Args:
        images_dir (str): Directory containing page images (PNG format)
        output_dir (str): Path where the combined PDF will be saved

    Returns:
        dict: Metadata about the PDF creation process
    """
    try:
        import glob

        # Find all PNG files in the directory
        image_pattern = os.path.join(images_dir, "page_*.png")
        image_files = sorted(glob.glob(image_pattern))

        if not image_files:
            raise PDFProcessingError(f"No page images found in {images_dir}")

        logger.info(f"Found {len(image_files)} page images to combine")
        logger.info(f"Creating PDF: {output_dir}")

        # Create a new PDF document
        pdf_doc = fitz.open()  # Create new empty PDF

        # Progress indicator
        progress = ProgressIndicator(len(image_files), "Combining images to PDF")

        # Add each image as a page in the PDF
        for i, image_path in enumerate(image_files):
            try:
                # Open the image
                img_doc = fitz.open(image_path)

                # Convert image to PDF page
                pdf_bytes = img_doc.convert_to_pdf()
                img_pdf = fitz.open("pdf", pdf_bytes)

                # Insert the page into our main PDF
                pdf_doc.insert_pdf(img_pdf)

                # Clean up
                img_doc.close()
                img_pdf.close()

                progress.update()

            except Exception as e:
                logger.warning(f"Failed to add image {image_path}: {str(e)}")
                continue

        # Save the combined PDF
        pdf_doc.save(output_dir)
        pdf_doc.close()

        # Get file size
        file_size = os.path.getsize(output_dir)
        file_size_mb = file_size / (1024 * 1024)

        logger.info(f"Combined PDF created successfully: {output_dir}")
        logger.info(f"PDF size: {file_size_mb:.2f} MB")
        logger.info(f"Total pages: {len(image_files)}")

        return {
            "output_file": output_dir,
            "page_count": len(image_files),
            "file_size_mb": round(file_size_mb, 2),
            "source_images": len(image_files),
            "creation_time": datetime.datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error combining images to PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to combine images to PDF: {str(e)}")


if __name__ == "__main__":
    main()
