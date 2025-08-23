from typing import Any, Optional
import asyncio
import PyPDF2
from PyPDF2 import PdfReader
import os
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import fnmatch
from difflib import get_close_matches
import re

# Initialize server
server = Server("pdf-tools")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available PDF manipulation tools."""
    return [
        types.Tool(
            name="merge-pdfs",
            description="Merge multiple PDF files into a single PDF",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of input PDF file paths"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for merged PDF"
                    }
                },
                "required": ["input_paths", "output_path"]
            }
        ),
        types.Tool(
            name="extract-pages",
            description="Extract specific pages from a PDF file",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Input PDF file path"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for new PDF"
                    },
                    "pages": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of page numbers to extract (1-based indexing)"
                    }
                },
                "required": ["input_path", "output_path", "pages"]
            }
        ),
        types.Tool(
            name="search-pdfs",
            description="Search for PDF files in a directory with optional pattern matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_path": {
                        "type": "string",
                        "description": "Base directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Pattern to match against filenames (e.g., 'report*.pdf')"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to search in subdirectories",
                        "default": True
                    }
                },
                "required": ["base_path"]
            }
        ),
        types.Tool(
            name="merge-pdfs-ordered",
            description="Merge PDFs in a specific order based on patterns or exact names",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_path": {
                        "type": "string",
                        "description": "Base directory containing PDFs"
                    },
                    "patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of patterns or names in desired order"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for merged PDF"
                    },
                    "fuzzy_matching": {
                        "type": "boolean",
                        "description": "Use fuzzy matching for filenames",
                        "default": True
                    }
                },
                "required": ["base_path", "patterns", "output_path"]
            }
        ),
        types.Tool(
            name="find-related-pdfs",
            description="Find a PDF and then search for related PDFs based on its content, including common substring patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_path": {
                        "type": "string",
                        "description": "Base directory to search in"
                    },
                    "target_filename": {
                        "type": "string",
                        "description": "Name of the initial PDF to analyze"
                    },
                    "pattern_matching_only": {
                        "type": "boolean", 
                        "description": "Only search for repeating substring patterns",
                        "default": False
                    },
                    "min_pattern_occurrences": {
                        "type": "integer",
                        "description": "Minimum times a pattern must appear to be considered significant",
                        "default": 2
                    }
                },
                "required": ["base_path", "target_filename"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle PDF tool execution requests."""
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "merge-pdfs":
        input_paths = arguments.get("input_paths", [])
        output_path = arguments.get("output_path")
        
        if not input_paths or not output_path:
            raise ValueError("Missing required arguments")

        merger = PyPDF2.PdfMerger()
        
        try:
            # Add each PDF to the merger
            for path in input_paths:
                with open(path, 'rb') as pdf_file:
                    merger.append(pdf_file)
            
            # Write the merged PDF
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            return [types.TextContent(
                type="text",
                text=f"Successfully merged {len(input_paths)} PDFs into {output_path}"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error merging PDFs: {str(e)}"
            )]
        finally:
            merger.close()

    elif name == "extract-pages":
        input_path = arguments.get("input_path")
        output_path = arguments.get("output_path")
        pages = arguments.get("pages", [])
        
        if not input_path or not output_path or not pages:
            raise ValueError("Missing required arguments")

        try:
            reader = PyPDF2.PdfReader(input_path)
            writer = PyPDF2.PdfWriter()

            # Convert 1-based page numbers to 0-based indices
            for page_num in pages:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: Page number {page_num} is out of range"
                    )]

            # Write the extracted pages to the output file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            return [types.TextContent(
                type="text",
                text=f"Successfully extracted {len(pages)} pages to {output_path}"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error extracting pages: {str(e)}"
            )]

    elif name == "search-pdfs":
        base_path = arguments.get("base_path")
        pattern = arguments.get("pattern", "*.pdf")
        recursive = arguments.get("recursive", True)
        
        if not base_path:
            raise ValueError("Missing base_path argument")

        # Normalize the base path to handle Windows paths
        base_path = os.path.normpath(base_path)
        found_files = []
        
        try:
            if recursive:
                for root, _, files in os.walk(base_path):
                    for filename in files:
                        # Convert both pattern and filename to lowercase for case-insensitive matching
                        if filename.lower().endswith('.pdf'):
                            # Remove the .pdf from pattern if it exists for more flexible matching
                            search_pattern = pattern.lower().replace('.pdf', '')
                            if search_pattern in filename.lower():
                                full_path = os.path.join(root, filename)
                                found_files.append(full_path)
            else:
                for file in os.listdir(base_path):
                    if file.lower().endswith('.pdf'):
                        search_pattern = pattern.lower().replace('.pdf', '')
                        if search_pattern in file.lower():
                            full_path = os.path.join(base_path, file)
                            found_files.append(full_path)

            return [types.TextContent(
                type="text",
                text=f"Found {len(found_files)} PDF files:\n" + 
                    "\n".join(f"- {f}" for f in found_files)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching for PDFs: {str(e)}\nBase path: {base_path}"
            )]

    elif name == "merge-pdfs-ordered":
        base_path = arguments.get("base_path")
        patterns = arguments.get("patterns", [])
        output_path = arguments.get("output_path")
        fuzzy_matching = arguments.get("fuzzy_matching", True)
        
        if not all([base_path, patterns, output_path]):
            raise ValueError("Missing required arguments")

        try:
            # Get all PDF files in the directory
            all_pdfs = []
            for root, _, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        all_pdfs.append(os.path.join(root, file))

            # Match files to patterns
            selected_files = []
            for pattern in patterns:
                pattern_matched = False
                
                # Try exact matches first
                exact_matches = [f for f in all_pdfs if pattern in os.path.basename(f)]
                if exact_matches:
                    selected_files.extend(exact_matches)
                    pattern_matched = True
                
                # Try fuzzy matching if enabled and no exact matches
                elif fuzzy_matching:
                    filenames = [os.path.basename(f) for f in all_pdfs]
                    matches = get_close_matches(pattern, filenames, n=3, cutoff=0.6)
                    if matches:
                        for match in matches:
                            matching_files = [f for f in all_pdfs if os.path.basename(f) == match]
                            selected_files.extend(matching_files)
                            pattern_matched = True
                
                if not pattern_matched:
                    return [types.TextContent(
                        type="text",
                        text=f"Warning: No matches found for pattern '{pattern}'"
                    )]

            # Merge the matched files
            merger = PyPDF2.PdfMerger()
            for pdf_path in selected_files:
                with open(pdf_path, 'rb') as pdf_file:
                    merger.append(pdf_file)
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)

            return [types.TextContent(
                type="text",
                text=f"Successfully merged {len(selected_files)} PDFs into {output_path}\n" +
                     "Files merged in this order:\n" +
                     "\n".join(f"- {os.path.basename(f)}" for f in selected_files)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error merging PDFs: {str(e)}"
            )]

    elif name == "find-related-pdfs":
        base_path = arguments.get("base_path")
        target_filename = arguments.get("target_filename")
        
        if not base_path or not target_filename:
            raise ValueError("Missing required arguments")

        try:
            # First, find the target PDF
            target_pdf_path = None
            for root, _, files in os.walk(base_path):
                for filename in files:
                    if target_filename.lower() in filename.lower() and filename.lower().endswith('.pdf'):
                        target_pdf_path = os.path.join(root, filename)
                        break
                if target_pdf_path:
                    break

            if not target_pdf_path:
                return [types.TextContent(
                    type="text",
                    text=f"Could not find target PDF: {target_filename}"
                )]

            # Extract text from the target PDF
            reader = PdfReader(target_pdf_path)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"

            # Process the extracted text
            search_terms = set()
            
            if arguments.get("pattern_matching_only", False):
                # Find common patterns that look like related filenames
                # Look for 2-3 letter prefixes followed by numbers and optional suffix
                pattern_regex = re.compile(r'([A-Z]{2,3}\d{3,7}(?:[-_][A-Z0-9]+)?)', re.IGNORECASE)
                potential_parts = pattern_regex.findall(extracted_text)
                
                # Count occurrences of each prefix
                prefix_counts = {}
                prefix_patterns = {}
                for part in potential_parts:
                    # Extract prefix (2-3 letters at start)
                    prefix_match = re.match(r'([A-Z]{2,3})', part, re.IGNORECASE)
                    if prefix_match:
                        prefix = prefix_match.group(1).upper()
                        if prefix not in prefix_counts:
                            prefix_counts[prefix] = 1
                            prefix_patterns[prefix] = set()
                        else:
                            prefix_counts[prefix] += 1
                        prefix_patterns[prefix].add(part)
                
                # Only keep prefixes that appear frequently enough
                min_occurrences = arguments.get("min_pattern_occurrences", 2)
                common_prefixes = {prefix for prefix, count in prefix_counts.items() 
                                if count >= min_occurrences}
                
                # Add patterns for common prefixes
                for prefix in common_prefixes:
                    search_terms.update(prefix_patterns[prefix])
                    # Also add the prefix itself to catch related files
                    search_terms.add(prefix)
            else:
                # Original word-based logic
                words = re.findall(r'\b\w+\b', extracted_text)
                search_terms.update(words)
                
                # Add pattern matching on top of word-based search
                pattern_regex = re.compile(r'([A-Z]{2,3}\d{3,7}(?:[-_][A-Z0-9]+)?)', re.IGNORECASE)
                potential_parts = pattern_regex.findall(extracted_text)
                search_terms.update(potential_parts)

            # Remove common words and very short terms
            common_words = {'THE', 'AND', 'OR', 'IN', 'ON', 'AT', 'TO', 'FOR', 'WITH', 'BY'}
            search_terms = {term for term in search_terms if 
                        len(term) > 2 and 
                        term.upper() not in common_words}

            # Search for PDFs matching any of the search terms
            found_files = set()
            for root, _, files in os.walk(base_path):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        file_lower = filename.lower()
                        
                        # Extract potential matches from filename
                        file_parts = re.findall(r'([A-Z]{2,3}\d{3,7}(?:[-_][A-Z0-9]+)?)', filename, re.IGNORECASE)
                        
                        for term in search_terms:
                            term_lower = term.lower()
                            if (term_lower in file_lower or 
                                any(part.lower() == term_lower for part in file_parts)):
                                full_path = os.path.join(root, filename)
                                found_files.add((full_path, term))
                                break

            # Format the results
            if found_files:
                result_text = f"Extracted {len(search_terms)} search terms from {os.path.basename(target_pdf_path)}.\n"
                result_text += "Search terms found: " + ", ".join(sorted(search_terms)) + "\n\n"
                result_text += "Found related PDFs:\n"
                
                # Group files by matching term
                term_groups = {}
                for file_path, term in found_files:
                    if term not in term_groups:
                        term_groups[term] = []
                    term_groups[term].append(file_path)

                # Output grouped results
                for term in sorted(term_groups.keys()):
                    result_text += f"\nFiles matching '{term}':\n"
                    for file_path in sorted(term_groups[term]):
                        result_text += f"- {file_path}\n"

                return [types.TextContent(
                    type="text",
                    text=result_text
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"No related PDFs found for terms extracted from {os.path.basename(target_pdf_path)}"
                )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error processing PDFs: {str(e)}"
            )]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the server using stdin/stdout streams."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf-tools",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())