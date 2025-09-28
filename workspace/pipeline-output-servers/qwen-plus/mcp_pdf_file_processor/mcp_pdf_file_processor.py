import sys
import os
import re
import asyncio
from mcp.server.fastmcp import FastMCP
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import logging
import json

# Initialize FastMCP server
mcp = FastMCP("mcp_pdf_file_processor")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add proxy support if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

async def validate_pdf_path(file_path: str) -> bool:
    """Validate if the PDF file path is safe and accessible."""
    try:
        # Check for path traversal attempts
        if ".." in file_path or not os.path.isabs(file_path):
            logger.error(f"Invalid file path: {file_path}")
            return False
        
        # Check if file exists (for input files)
        if os.path.exists(file_path):
            if not os.path.isfile(file_path):
                logger.error(f"Path exists but is not a file: {file_path}")
                return False
            if not file_path.lower().endswith('.pdf'):
                logger.error(f"File is not a PDF: {file_path}")
                return False
            
        # For output files, check if directory exists
        else:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                logger.info(f"Creating directory: {directory}")
                os.makedirs(directory, exist_ok=True)
                
        return True
    except Exception as e:
        logger.error(f"Error validating file path {file_path}: {str(e)}")
        return False

@mcp.tool()
async def merge_pdfs(input_files: list, output_file: str) -> str:
    """
    Merge multiple PDF files into a single PDF file.

    Args:
        input_files: List of paths to the PDF files to be merged.
        output_file: Path where the merged PDF will be saved.

    Returns:
        A JSON string containing the operation status, merged file path (if successful), or error message (if failed).

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: If the merging process fails.
    """
    try:
        # Validate inputs
        if not isinstance(input_files, list) or len(input_files) < 2:
            raise ValueError("At least two input files are required for merging")
            
        if not await validate_pdf_path(output_file):
            raise ValueError(f"Invalid output file path: {output_file}")
            
        for file_path in input_files:
            if not await validate_pdf_path(file_path):
                raise ValueError(f"Invalid input file path: {file_path}")
            if not os.path.exists(file_path):
                raise ValueError(f"Input file does not exist: {file_path}")
        
        # Create PDF writer object
        pdf_writer = PdfWriter()
        
        # Add pages from each PDF to the writer
        for file_path in input_files:
            try:
                pdf_reader = PdfReader(file_path)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
            except Exception as e:
                raise RuntimeError(f"Failed to read PDF file {file_path}: {str(e)}") from e
        
        # Write the output file
        try:
            with open(output_file, 'wb') as out_file:
                pdf_writer.write(out_file)
        except Exception as e:
            raise RuntimeError(f"Failed to write merged PDF to {output_file}: {str(e)}") from e
        
        # Verify the output file was created
        if not os.path.exists(output_file):
            raise RuntimeError(f"Merged PDF file was not created at {output_file}")
        
        result = {
            "status": "success",
            "merged_file": output_file
        }
        
    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}", exc_info=True)
        result = {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}"
        }
    
    return json.dumps(result)

@mcp.tool()
async def extract_pages(input_file: str, page_numbers: list, output_file: str) -> str:
    """
    Extract specific pages from a PDF file and save them as a new PDF.

    Args:
        input_file: Path to the source PDF file.
        page_numbers: List of page numbers to extract (1-based index).
        output_file: Path where the extracted pages will be saved.

    Returns:
        A JSON string containing the operation status, extracted file path (if successful), or error message (if failed).

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: If the extraction process fails.
    """
    try:
        # Validate inputs
        if not await validate_pdf_path(input_file):
            raise ValueError(f"Invalid input file path: {input_file}")
            
        if not os.path.exists(input_file):
            raise ValueError(f"Input file does not exist: {input_file}")
            
        if not isinstance(page_numbers, list) or len(page_numbers) < 1:
            raise ValueError("At least one page number must be specified for extraction")
            
        if not all(isinstance(p, int) and p > 0 for p in page_numbers):
            raise ValueError("All page numbers must be positive integers")
            
        if not await validate_pdf_path(output_file):
            raise ValueError(f"Invalid output file path: {output_file}")
        
        # Read the input PDF
        try:
            pdf_reader = PdfReader(input_file)
            total_pages = len(pdf_reader.pages)
        except Exception as e:
            raise RuntimeError(f"Failed to read input PDF {input_file}: {str(e)}") from e
        
        # Validate page numbers are within document range
        invalid_pages = [p for p in page_numbers if p > total_pages or p < 1]
        if invalid_pages:
            raise ValueError(f"Some page numbers are out of range (document has {total_pages} pages): {invalid_pages}")
        
        # Create PDF writer and add selected pages
        pdf_writer = PdfWriter()
        for page_num in page_numbers:
            try:
                page = pdf_reader.pages[page_num - 1]  # Convert to 0-based index
                pdf_writer.add_page(page)
            except Exception as e:
                raise RuntimeError(f"Failed to extract page {page_num}: {str(e)}") from e
        
        # Write the output file
        try:
            with open(output_file, 'wb') as out_file:
                pdf_writer.write(out_file)
        except Exception as e:
            raise RuntimeError(f"Failed to write extracted pages to {output_file}: {str(e)}") from e
        
        # Verify the output file was created
        if not os.path.exists(output_file):
            raise RuntimeError(f"Extracted PDF file was not created at {output_file}")
        
        result = {
            "status": "success",
            "extracted_file": output_file
        }
        
    except Exception as e:
        logger.error(f"Error extracting pages: {str(e)}", exc_info=True)
        result = {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}"
        }
    
    return json.dumps(result)

@mcp.tool()
async def search_pdfs(directory: str, pattern: str) -> str:
    """
    Search for PDF files matching a specific pattern in a given directory.

    Args:
        directory: Path to the directory to search in.
        pattern: Regular expression pattern to match PDF filenames.

    Returns:
        A JSON string containing the operation status, list of matched files (if successful), or error message (if failed).

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: If the search process fails.
    """
    try:
        # Validate inputs
        if not os.path.isdir(directory):
            raise ValueError(f"Invalid directory: {directory}")
            
        try:
            re.compile(pattern)  # Validate regex pattern
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern: {pattern}. Error: {str(e)}") from e
        
        # Find all PDF files in the directory
        matches = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and filename.lower().endswith('.pdf') and re.search(pattern, filename):
                matches.append(file_path)
        
        result = {
            "status": "success",
            "matches": matches
        }
        
    except Exception as e:
        logger.error(f"Error searching PDFs: {str(e)}", exc_info=True)
        result = {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}"
        }
    
    return json.dumps(result)

@mcp.tool()
async def merge_pdfs_ordered(directory: str, order_pattern: str, output_file: str, exact_match: bool = False) -> str:
    """
    Merge PDF files in a specific order based on a pattern.

    Args:
        directory: Path to the directory containing PDF files.
        order_pattern: Pattern to determine the merge order (exact filename or partial match).
        output_file: Path where the merged PDF will be saved.
        exact_match: Boolean indicating whether to use exact match (True) or partial match (False).

    Returns:
        A JSON string containing the operation status, merged file path, matched files (if successful), or error message (if failed).

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: If the merging process fails.
    """
    try:
        # Validate inputs
        if not os.path.isdir(directory):
            raise ValueError(f"Invalid directory: {directory}")
            
        if not await validate_pdf_path(output_file):
            raise ValueError(f"Invalid output file path: {output_file}")
            
        # Find all PDF files in the directory
        all_pdfs = [os.path.join(directory, f) for f in os.listdir(directory) 
                   if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith('.pdf')]
        
        # Determine files to merge based on match type
        if exact_match:
            matched_files = [f for f in all_pdfs if os.path.basename(f) == order_pattern]
        else:
            matched_files = [f for f in all_pdfs if order_pattern in os.path.basename(f)]
        
        if not matched_files:
            raise ValueError(f"No files found matching the pattern: {order_pattern}")
        
        # Sort files alphabetically to ensure consistent ordering
        matched_files.sort()
        
        # Merge the files
        pdf_writer = PdfWriter()
        
        for file_path in matched_files:
            try:
                pdf_reader = PdfReader(file_path)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
            except Exception as e:
                raise RuntimeError(f"Failed to read PDF file {file_path}: {str(e)}") from e
        
        # Write the output file
        try:
            with open(output_file, 'wb') as out_file:
                pdf_writer.write(out_file)
        except Exception as e:
            raise RuntimeError(f"Failed to write merged PDF to {output_file}: {str(e)}") from e
        
        # Verify the output file was created
        if not os.path.exists(output_file):
            raise RuntimeError(f"Merged PDF file was not created at {output_file}")
        
        result = {
            "status": "success",
            "merged_file": output_file,
            "matched_files": matched_files
        }
        
    except Exception as e:
        logger.error(f"Error merging PDFs in order: {str(e)}", exc_info=True)
        result = {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}"
        }
    
    return json.dumps(result)

@mcp.tool()
async def find_related_pdfs(target_file: str, search_directory: str) -> str:
    """
    Find PDF files related to a target PDF based on filename patterns and content similarity.

    Args:
        target_file: Path to the target PDF file.
        search_directory: Path to the directory to search for related files.

    Returns:
        A JSON string containing the operation status, related files (if successful), or error message (if failed).

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: If the search process fails.
    """
    try:
        # Validate inputs
        if not await validate_pdf_path(target_file):
            raise ValueError(f"Invalid target file path: {target_file}")
            
        if not os.path.exists(target_file):
            raise ValueError(f"Target file does not exist: {target_file}")
            
        if not os.path.isdir(search_directory):
            raise ValueError(f"Invalid search directory: {search_directory}")
        
        # Extract filename without extension for pattern matching
        target_filename = os.path.basename(target_file)
        target_basename = os.path.splitext(target_filename)[0]
        
        # Find filename matches (files containing the target basename)
        filename_matches = []
        for filename in os.listdir(search_directory):
            file_path = os.path.join(search_directory, filename)
            if os.path.isfile(file_path) and file_path.lower().endswith('.pdf') and target_basename in filename:
                filename_matches.append(file_path)
        
        # Find content matches by analyzing text similarity
        content_matches = []
        
        # Extract text from target PDF
        target_text = ""
        try:
            with pdfplumber.open(target_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        target_text += text + " "
        except Exception as e:
            logger.warning(f"Failed to extract text from target PDF {target_file}: {str(e)}")
        
        # If we could extract text from the target, search for similar content
        if target_text.strip():
            target_words = set(target_text.lower().split())
            
            for file_path in filename_matches:
                if file_path == target_file:
                    continue  # Skip the target file itself
                
                try:
                    file_text = ""
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                file_text += text + " "
                    
                    if file_text.strip():
                        file_words = set(file_text.lower().split())
                        # Calculate simple Jaccard similarity
                        intersection = len(target_words.intersection(file_words))
                        union = len(target_words.union(file_words))
                        
                        if union > 0:
                            similarity = intersection / union
                            # Consider as match if similarity is above threshold
                            if similarity > 0.1:  # Adjust threshold as needed
                                content_matches.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to analyze content of {file_path}: {str(e)}")
        
        # Combine results (filename matches that aren't already in content matches)
        combined_matches = list(set(filename_matches + content_matches))
        
        result = {
            "status": "success",
            "related_files": combined_matches,
            "filename_matches": filename_matches,
            "content_matches": content_matches
        }
        
    except Exception as e:
        logger.error(f"Error finding related PDFs: {str(e)}", exc_info=True)
        result = {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}"
        }
    
    return json.dumps(result)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()