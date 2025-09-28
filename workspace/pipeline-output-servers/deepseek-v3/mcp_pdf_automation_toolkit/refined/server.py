import sys
from PyPDF2 import PdfMerger, PdfReader
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("pdf_automation")

@mcp.tool()
def merge_pdfs(file_paths: list, output_path: str) -> str:
    """
    Merge multiple PDF files into a single PDF file.

    Args:
        file_paths: A list of file paths to the PDFs to be merged.
        output_path: The file path where the merged PDF will be saved.

    Returns:
        A success/error message indicating the result of the merge operation.
    """
    try:
        if not file_paths:
            return "Error: No PDF files provided for merging"
        merger = PdfMerger()
        for path in file_paths:
            with open(path, 'rb') as f:
                merger.append(PdfReader(f))
        with open(output_path, 'wb') as f:
            merger.write(f)
        merger.close()
        return f"Successfully merged PDFs to {output_path}"
    except FileNotFoundError as e:
        return f"Error: File not found - {str(e)}"
    except Exception as e:
        return f"Error merging PDFs: {str(e)}"

@mcp.tool()
def extract_pages(source_path: str, pages: list, output_path: str) -> str:
    """
    Extract specific pages from a PDF file and save them as a new PDF.

    Args:
        source_path: The file path of the source PDF.
        pages: A list of page numbers to extract.
        output_path: The file path where the extracted pages will be saved.

    Returns:
        A success/error message indicating the result of the extraction.
    """
    try:
        if not pages:
            return "Error: No pages specified for extraction"
        merger = PdfMerger()
        with open(source_path, 'rb') as f:
            merger.append(PdfReader(f), pages=pages)
        with open(output_path, 'wb') as f:
            merger.write(f)
        merger.close()
        return f"Successfully extracted pages to {output_path}"
    except FileNotFoundError as e:
        return f"Error: File not found - {str(e)}"
    except Exception as e:
        return f"Error extracting pages: {str(e)}"

@mcp.tool()
def search_pdfs(directory: str, pattern: str) -> list:
    """
    Search for PDF files in a specified directory that match a given pattern.

    Args:
        directory: The directory path to search in.
        pattern: The pattern to match PDF filenames against.

    Returns:
        A list of file paths that match the pattern.
    """
    import os
    import fnmatch
    try:
        if not os.path.isdir(directory):
            return [f"Error: Directory not found - {directory}"]
        pdf_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files
    except Exception as e:
        return [f"Error searching PDFs: {str(e)}"]

@mcp.tool()
def merge_pdfs_ordered(file_paths: list, order: list, output_path: str, fuzzy_match: bool = False) -> str:
    """
    Merge PDF files in a specified order, supporting exact and fuzzy matching.

    Args:
        file_paths: A list of file paths to the PDFs to be merged.
        order: The order in which to merge the PDFs.
        output_path: The file path where the merged PDF will be saved.
        fuzzy_match: Whether to use fuzzy matching for the order.

    Returns:
        A success/error message indicating the result of the merge operation.
    """
    try:
        if not file_paths or not order:
            return "Error: No PDF files or order specified for merging"
        merger = PdfMerger()
        if fuzzy_match:
            from fuzzywuzzy import process
            for file_order in order:
                best_match = process.extractOne(file_order, file_paths)
                if not best_match:
                    return f"Error: No match found for {file_order}"
                with open(best_match[0], 'rb') as f:
                    merger.append(PdfReader(f))
        else:
            for file_order in order:
                # Validate that the file exists before attempting to read it
                if file_order not in file_paths:
                    return f"Error: {file_order} is not in the provided file_paths list"
                with open(file_order, 'rb') as f:
                    merger.append(PdfReader(f))
        with open(output_path, 'wb') as f:
            merger.write(f)
        merger.close()
        return f"Successfully merged PDFs in order to {output_path}"
    except FileNotFoundError as e:
        return f"Error: File not found - {str(e)}"
    except Exception as e:
        return f"Error merging PDFs in order: {str(e)}"

@mcp.tool()
def find_related_pdfs(target_path: str, directory: str, content_similarity_threshold: float = 0.7) -> list:
    """
    Analyze a target PDF file and find related PDFs based on filename patterns and content.

    Args:
        target_path: The file path of the target PDF.
        directory: The directory path to search for related PDFs.
        content_similarity_threshold: The threshold for content similarity.

    Returns:
        A list of file paths to related PDFs.
    """
    try:
        import os
        import fitz  # PyMuPDF
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        if not os.path.isfile(target_path):
            return [f"Error: Target file not found - {target_path}"]
        if not os.path.isdir(directory):
            return [f"Error: Directory not found - {directory}"]

        # Get target content
        target_doc = fitz.open(target_path)
        target_text = "".join([page.get_text() for page in target_doc])

        # Get all PDFs in directory
        pdf_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.pdf'):
                	pdf_files.append(os.path.join(root, file))

        # Compare content
        related_pdfs = []
        vectorizer = TfidfVectorizer()
        target_vec = vectorizer.fit_transform([target_text])
        for pdf in pdf_files:
            doc = fitz.open(pdf)
            text = "".join([page.get_text() for page in doc])
            text_vec = vectorizer.transform([text])
            similarity = cosine_similarity(target_vec, text_vec)[0][0]
            if similarity >= content_similarity_threshold:
                related_pdfs.append(pdf)
        return related_pdfs
    except Exception as e:
        return [f"Error finding related PDFs: {str(e)}"]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()