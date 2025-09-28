import sys
import os
import asyncio
from typing import List
import PyPDF2
from glob import glob
from fuzzywuzzy import process
import textdistance
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_automated_pdf_tool")

@mcp.tool()
def merge_pdfs(file_paths: List[str], output_path: str) -> None:
    """
    Merge multiple PDF files into a single file.

    Args:
        file_paths (List[str]): A list of file paths to the PDF files to be merged.
        output_path (str): The path where the merged PDF will be saved.

    Returns:
        None

    Example:
        merge_pdfs(["file1.pdf", "file2.pdf"], "merged.pdf")
    """
    try:
        merger = PyPDF2.PdfMerger()
        for file_path in file_paths:
            merger.append(file_path)
        merger.write(output_path)
        merger.close()
    except Exception as e:
        raise ValueError(f"Failed to merge PDFs: {str(e)}")

@mcp.tool()
def extract_pages(file_path: str, page_numbers: List[int], output_path: str) -> None:
    """
    Extract specific pages from a PDF file and save them as a new PDF file.

    Args:
        file_path (str): The path to the input PDF file.
        page_numbers (List[int]): A list of page numbers to extract.
        output_path (str): The path where the new PDF file will be saved.

    Returns:
        None

    Example:
        extract_pages("input.pdf", [1, 2, 3], "output.pdf")
    """
    try:
        reader = PyPDF2.PdfReader(file_path)
        writer = PyPDF2.PdfWriter()
        for page_number in page_numbers:
            if page_number < 1 or page_number > len(reader.pages):
                raise ValueError(f"Page number {page_number} is out of range.")
            writer.add_page(reader.pages[page_number - 1])
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
    except Exception as e:
        raise ValueError(f"Failed to extract pages: {str(e)}")

@mcp.tool()
def search_pdfs(directory: str, pattern: str) -> List[str]:
    """
    Search for PDF files matching a specific pattern in a given directory.

    Args:
        directory (str): The directory to search in.
        pattern (str): The filename pattern to match (e.g., '*.pdf').

    Returns:
        List[str]: A list of file paths matching the pattern.

    Example:
        search_pdfs("./", "*.pdf")
    """
    try:
        return glob(os.path.join(directory, pattern))
    except Exception as e:
        raise ValueError(f"Failed to search PDFs: {str(e)}")

@mcp.tool()
def merge_pdfs_ordered(file_paths: List[str], order: List[str], fuzzy_match: bool = False, output_path: str = "output.pdf") -> None:
    """
    Merge PDF files in a specified order based on a given pattern. Supports exact and fuzzy matching.

    Args:
        file_paths (List[str]): A list of file paths to the PDF files to be merged.
        order (List[str]): A list defining the order in which the PDF files should be merged.
        fuzzy_match (bool): Whether to allow fuzzy matching of patterns (default: False).
        output_path (str): The path where the merged PDF will be saved.

    Returns:
        None

    Example:
        merge_pdfs_ordered(["file1.pdf", "file2.pdf"], ["file2", "file1"], True, "output.pdf")
    """
    try:
        ordered_files = []
        if fuzzy_match:
            for pattern in order:
                match, _ = process.extractOne(pattern, file_paths)
                ordered_files.append(match)
        else:
            for pattern in order:
                match = next((file for file in file_paths if pattern in file), None)
                if match:
                    ordered_files.append(match)
        merge_pdfs(ordered_files, output_path)
    except Exception as e:
        raise ValueError(f"Failed to merge PDFs in ordered manner: {str(e)}")

@mcp.tool()
def find_related_pdfs(target_file: str, directory: str, similarity_threshold: float = 0.8) -> List[str]:
    """
    Analyze the contents of a target PDF file and identify related PDF files based on filename patterns and content similarity.

    Args:
        target_file (str): The path to the target PDF file.
        directory (str): The directory to search for related files.
        similarity_threshold (float): A threshold for determining content similarity (default: 0.8).

    Returns:
        List[str]: A list of file paths to related PDF files.

    Example:
        find_related_pdfs("target.pdf", "./", 0.8)
    """
    try:
        target_content = ""
        with open(target_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            target_content = "\n".join([page.extract_text() for page in reader.pages])

        related_files = []
        for file_path in search_pdfs(directory, "*.pdf"):
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                content = "\n".join([page.extract_text() for page in reader.pages])
                similarity = textdistance.jaccard.similarity(target_content, content)
                if similarity >= similarity_threshold:
                    related_files.append(file_path)
        return related_files
    except Exception as e:
        raise ValueError(f"Failed to find related PDFs: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    mcp.run()