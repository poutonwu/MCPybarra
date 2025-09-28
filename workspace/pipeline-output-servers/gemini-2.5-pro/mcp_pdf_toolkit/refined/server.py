import sys
import os
import glob
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader, PdfWriter
from thefuzz import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize FastMCP server
mcp = FastMCP("mcp_pdf_toolkit")

def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    Helper function to extract text from a PDF file.

    Args:
        pdf_path (str): The full path to the PDF file.

    Returns:
        str: The extracted text from the PDF, or an empty string if extraction fails.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text
    except Exception as e:
        # Print error for debugging purposes, but still return empty string
        print(f"Could not extract text from {pdf_path}: {e}", file=sys.stderr)
        return ""

@mcp.tool()
def merge_pdfs(pdf_paths: list[str], output_path: str) -> dict:
    """
    Merges multiple specified PDF files into a single PDF file.

    Args:
        pdf_paths (list[str]): A list containing the full paths to the PDF files to be merged.
        output_path (str): The save path for the merged PDF file.

    Returns:
        dict: A dictionary containing the operation status and a message.
              Example: {"status": "success", "message": "Files merged successfully into output.pdf"}
    """
    try:
        if not pdf_paths:
            raise ValueError("The list of PDF paths cannot be empty.")
        if not output_path.lower().endswith('.pdf'):
            raise ValueError("Output path must have a .pdf extension.")

        pdf_writer = PdfWriter()
        
        for path in pdf_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Input file not found: {path}")
            pdf_reader = PdfReader(path)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        with open(output_path, "wb") as out_file:
            pdf_writer.write(out_file)
            
        return {"status": "success", "message": f"Files merged successfully into {os.path.basename(output_path)}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def extract_pages(source_path: str, pages: list[int], output_path: str) -> dict:
    """
    Extracts specified pages from a PDF file and creates a new PDF file.

    Args:
        source_path (str): The full path to the source PDF file.
        pages (list[int]): A list of page numbers to extract (0-indexed).
        output_path (str): The save path for the new PDF file with the extracted pages.

    Returns:
        dict: A dictionary containing the operation status and a message.
              Example: {"status": "success", "message": "Extracted 3 pages into new_file.pdf"}
    """
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        if not output_path.lower().endswith('.pdf'):
            raise ValueError("Output path must have a .pdf extension.")

        pdf_reader = PdfReader(source_path)
        pdf_writer = PdfWriter()
        
        num_pages = len(pdf_reader.pages)
        for page_num in pages:
            if not 0 <= page_num < num_pages:
                raise ValueError(f"Invalid page number: {page_num}. Must be between 0 and {num_pages - 1}.")
            pdf_writer.add_page(pdf_reader.pages[page_num])
            
        with open(output_path, "wb") as out_file:
            pdf_writer.write(out_file)
            
        return {"status": "success", "message": f"Extracted {len(pages)} pages into {os.path.basename(output_path)}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def search_pdfs(directory: str, pattern: str) -> list[str]:
    """
    Searches for PDF files matching a glob pattern in a specified directory.

    Args:
        directory (str): The path to the directory to search in.
        pattern (str): The glob pattern to match filenames (e.g., '*.pdf', 'report-*.pdf').

    Returns:
        list[str]: A list containing the full paths of all matching PDF files.
    """
    try:
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        search_path = os.path.join(directory, pattern)
        return glob.glob(search_path)
    except Exception as e:
        # In case of error, return an empty list or an error message.
        # Returning a list is consistent with the return type annotation.
        print(f"Error in search_pdfs: {e}", file=sys.stderr)
        return []

@mcp.tool()
def merge_pdfs_ordered(directory: str, order_patterns: list[str], output_path: str, match_mode: str = 'exact') -> dict:
    """
    Finds and merges PDF files in a specified order from a directory based on a list of filename patterns.
    Supports both exact and fuzzy matching modes.

    Args:
        directory (str): The path to the directory to search for PDF files.
        order_patterns (list[str]): A list of filename patterns that defines the merge order.
        output_path (str): The save path for the merged PDF file.
        match_mode (str): The matching mode, either 'exact' or 'fuzzy'. Defaults to 'exact'.

    Returns:
        dict: A dictionary containing the operation status, a message, and a list of the actual files merged.
    """
    try:
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        if match_mode not in ['exact', 'fuzzy']:
            raise ValueError("match_mode must be either 'exact' or 'fuzzy'.")

        all_pdfs_in_dir = glob.glob(os.path.join(directory, '*.pdf'))
        all_pdf_filenames = [os.path.basename(p) for p in all_pdfs_in_dir]
        
        files_to_merge = []
        
        if match_mode == 'exact':
            for pattern in order_patterns:
                # Use glob to find exact matches for the pattern
                found_files = glob.glob(os.path.join(directory, pattern))
                if found_files:
                    files_to_merge.extend(sorted(found_files))
        else: # fuzzy
            for pattern in order_patterns:
                # Use thefuzz to find the best match for the pattern
                # extractOne returns (match, score) or None if no match is found
                result = process.extractOne(pattern, all_pdf_filenames)
                if result:
                    best_match, score = result
                    if score > 70: # Using a threshold of 70 for fuzzy match
                        files_to_merge.append(os.path.join(directory, best_match))

        if not files_to_merge:
            return {"status": "warning", "message": "No files found matching the patterns.", "merged_files": []}

        # Remove duplicates while preserving order
        unique_files_to_merge = sorted(set(files_to_merge), key=files_to_merge.index)
        
        merge_result = merge_pdfs(unique_files_to_merge, output_path)
        if merge_result["status"] == "success":
            return {
                "status": "success", 
                "message": "Files merged in specified order.", 
                "merged_files": unique_files_to_merge
            }
        else:
            return merge_result

    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def find_related_pdfs(target_pdf: str, search_directory: str, top_n: int = 5) -> list[dict]:
    """
    Finds PDFs in a directory that are related to a target PDF based on content similarity.
    It analyzes the text content of the target PDF and compares it against other PDFs
    in the search directory to find the most similar ones.

    Args:
        target_pdf (str): The full path to the target PDF file used as the baseline for comparison.
        search_directory (str): The path to the directory where related files will be searched.
        top_n (int): The maximum number of related PDF files to return. Defaults to 5.

    Returns:
        list[dict]: A list of related PDF files, where each element is a dictionary
                    containing the file path and a similarity score. Returns a list
                    with an error dictionary if an issue occurs.
    """
    try:
        if not os.path.exists(target_pdf):
            raise FileNotFoundError(f"Target PDF not found: {target_pdf}")
        if not os.path.isdir(search_directory):
            raise FileNotFoundError(f"Search directory not found: {search_directory}")

        target_text = _extract_text_from_pdf(target_pdf)
        if not target_text.strip():
            return [{"error": "Could not extract text from target PDF or it is empty."}]

        search_pdfs_paths = [str(p) for p in Path(search_directory).rglob("*.pdf") if str(p) != target_pdf]
        if not search_pdfs_paths:
            return []
            
        documents = [target_text]
        doc_paths_for_comparison = []

        for pdf_path in search_pdfs_paths:
            text = _extract_text_from_pdf(pdf_path)
            if text.strip():
                documents.append(text)
                doc_paths_for_comparison.append(pdf_path)

        if len(documents) < 2:
            return [] # Not enough documents to compare

        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity of the target (first doc) against all others
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Get similarity scores and pair them with file paths
        sim_scores = list(enumerate(cosine_sim[0]))
        
        # Sort by similarity score in descending order
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get the top N results
        top_results = []
        for i, score in sim_scores[:top_n]:
            top_results.append({
                "file_path": doc_paths_for_comparison[i],
                "similarity_score": round(float(score), 4)
            })
            
        return top_results

    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout
    if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()