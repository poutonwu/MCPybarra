import os
import re
import sys
import json
from typing import List
from mcp.server.fastmcp import FastMCP
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from rapidfuzz import process, fuzz

class PDFTool:
    @staticmethod
    def validate_pdf_path(pdf_file: str) -> None:
        """Validate if the given file path is a valid PDF."""
        if not os.path.exists(pdf_file):
            raise ValueError(f"File not found: {pdf_file}")
        if not pdf_file.lower().endswith('.pdf'):
            raise ValueError(f"Invalid file format (expected .pdf): {pdf_file}")

    @staticmethod
    def validate_directory(directory: str) -> None:
        """Validate if the directory exists."""
        if not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")


def merge_pdfs(pdf_files: List[str]) -> str:
    """
    Merges multiple PDF files into a single file.

    Args:
        pdf_files: List of paths to the PDF files. Required.

    Returns:
        Path to the merged PDF file.

    Raises:
        ValueError: If any input file is invalid or missing.

    Example:
        merge_pdfs(pdf_files=["file1.pdf", "file2.pdf"])
    """
    try:
        merger = PdfMerger()
        for pdf in pdf_files:
            PDFTool.validate_pdf_path(pdf)
            merger.append(pdf)

        output_path = "merged_output.pdf"
        merger.write(output_path)
        merger.close()
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error merging PDFs: {str(e)}")


def extract_pages(pdf_file: str, pages: List[int], output_path: str) -> str:
    """
    Extracts specific pages from a PDF file and saves them as a new file.

    Args:
        pdf_file: Path to the source PDF file. Required.
        pages: List of page numbers to extract. Required.
        output_path: Path where the new PDF file will be saved. Required.

    Returns:
        Path to the new PDF file containing the extracted pages.

    Raises:
        ValueError: If the input file is invalid or output path is incorrect.

    Example:
        extract_pages(pdf_file="source.pdf", pages=[1, 3, 5], output_path="extracted_pages.pdf")
    """
    try:
        PDFTool.validate_pdf_path(pdf_file)
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        for page_num in pages:
            if page_num < 1 or page_num > len(reader.pages):
                raise ValueError(f"Invalid page number: {page_num}")
            writer.add_page(reader.pages[page_num - 1])

        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)

        return output_path
    except Exception as e:
        raise RuntimeError(f"Error extracting pages: {str(e)}")


def search_pdfs(directory: str, pattern: str) -> List[str]:
    """
    Searches for PDF files matching a specific pattern in a given directory.

    Args:
        directory: Directory path to search within. Required.
        pattern: Pattern to match PDF filenames. Required.

    Returns:
        List of paths to the matching PDF files.

    Raises:
        ValueError: If the directory is invalid.

    Example:
        search_pdfs(directory="/path/to/files", pattern="report*.pdf")
    """
    try:
        PDFTool.validate_directory(directory)
        regex = re.compile(pattern.replace("*", ".*"))
        matching_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf') and regex.match(file):
                    matching_files.append(os.path.join(root, file))

        return matching_files
    except Exception as e:
        raise RuntimeError(f"Error searching PDFs: {str(e)}")


def merge_pdfs_ordered(pdf_files: List[str], order_pattern: str, fuzzy_match: bool = False) -> str:
    """
    Merges PDF files following a specified order, supporting both exact and fuzzy matching.

    Args:
        pdf_files: List of paths to the PDF files. Required.
        order_pattern: Pattern defining the merge order. Required.
        fuzzy_match: Whether to use fuzzy matching for ordering. Optional, default is False.

    Returns:
        Path to the merged PDF file.

    Raises:
        ValueError: If any input file is invalid or order cannot be determined.

    Example:
        merge_pdfs_ordered(pdf_files=["file1.pdf", "file2.pdf"], order_pattern="file?.pdf", fuzzy_match=True)
    """
    try:
        merger = PdfMerger()
        sorted_files = []

        for pdf in pdf_files:
            PDFTool.validate_pdf_path(pdf)

            # Match filenames against the order pattern
            if fuzzy_match:
                score = process.extractOne(order_pattern, [os.path.basename(pdf)], scorer=fuzz.ratio)[1]
                if score >= 70:  # Threshold for fuzzy match
                    sorted_files.append((pdf, score))
            elif re.match(order_pattern.replace("?", "."), os.path.basename(pdf)):
                sorted_files.append((pdf, 100))

        if not sorted_files:
            raise ValueError("No files matched the order pattern.")

        # Sort files by match score
        sorted_files.sort(key=lambda x: x[1], reverse=True)
        ordered_files = [file for file, _ in sorted_files]

        for pdf in ordered_files:
            merger.append(pdf)

        output_path = "ordered_merged_output.pdf"
        merger.write(output_path)
        merger.close()
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error merging PDFs in order: {str(e)}")


def find_related_pdfs(target_pdf: str, content_similarity_threshold: float = 0.8) -> List[str]:
    """
    Finds related PDF files based on the content and filename patterns of a target PDF file.

    Args:
        target_pdf: Path to the target PDF file. Required.
        content_similarity_threshold: Threshold for content similarity. Optional, default is 0.8.

    Returns:
        List of paths to related PDF files.

    Raises:
        ValueError: If the target PDF file is invalid.

    Example:
        find_related_pdfs(target_pdf="target_report.pdf", content_similarity_threshold=0.8)
    """
    try:
        PDFTool.validate_pdf_path(target_pdf)
        target_reader = PdfReader(target_pdf)
        target_text = "".join(page.extract_text() or "" for page in target_reader.pages)

        related_files = []
        directory = os.path.dirname(target_pdf)

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf') and file != os.path.basename(target_pdf):
                    current_pdf = os.path.join(root, file)
                    current_reader = PdfReader(current_pdf)
                    current_text = "".join(page.extract_text() or "" for page in current_reader.pages)

                    # Compare text similarity using RapidFuzz
                    similarity = fuzz.ratio(target_text, current_text) / 100.0
                    if similarity >= content_similarity_threshold:
                        related_files.append(current_pdf)

        return related_files
    except Exception as e:
        raise RuntimeError(f"Error finding related PDFs: {str(e)}")

# Initialize MCP server
mcp = FastMCP("mcp_pdf_automation_tool")

# Register tools
@mcp.tool()
def merge_pdfs_tool(pdf_files: List[str]) -> str:
    return merge_pdfs(pdf_files)

@mcp.tool()
def extract_pages_tool(pdf_file: str, pages: List[int], output_path: str) -> str:
    return extract_pages(pdf_file, pages, output_path)

@mcp.tool()
def search_pdfs_tool(directory: str, pattern: str) -> List[str]:
    return search_pdfs(directory, pattern)

@mcp.tool()
def merge_pdfs_ordered_tool(pdf_files: List[str], order_pattern: str, fuzzy_match: bool = False) -> str:
    return merge_pdfs_ordered(pdf_files, order_pattern, fuzzy_match)

@mcp.tool()
def find_related_pdfs_tool(target_pdf: str, content_similarity_threshold: float = 0.8) -> List[str]:
    return find_related_pdfs(target_pdf, content_similarity_threshold)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8-sig')
    mcp.run()