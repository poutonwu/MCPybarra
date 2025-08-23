import httpx
import asyncio
from typing import Dict, Any, Optional, List, Type
import re

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from framwork.logger import logger

class Context7DocsToolInput(BaseModel):
    """Input for the Context7 Docs tool."""
    library_name: str = Field(description="The name of the library to get documentation for, e.g., 'react', 'nextjs', 'mongodb'.")
    topic: Optional[str] = Field(None, description="Optional specific topic to narrow down the documentation, e.g., 'hooks', 'routing'.")
    tokens: Optional[int] = Field(3000, description="The maximum number of tokens to return, defaults to 3000.")

class Context7DocsTool(BaseTool):
    """
    A tool for fetching high-quality, up-to-date technical documentation for software libraries and frameworks.
    It directly queries the Context7 API, which aggregates documentation from official sources,
    making it a reliable alternative to general web searches for API usage and technical specifications.
    """
    name: str = "context7_docs_tool"
    description: str = (
        "A specialized tool to fetch high-quality, up-to-date technical documentation for a specific software library, "
        "framework, or API. Use this as a primary choice when you need to understand how to use a library's functions, "
        "classes, or concepts (e.g., 'hooks' in 'react', 'routing' in 'nextjs'). "
        "This tool is generally more reliable than a web search for API documentation. "
        "Provide a library name (e.g., 'react', 'mongodb', 'pandas') and an optional topic."
    )
    args_schema: Type[BaseModel] = Context7DocsToolInput
    api_base_url: str = "https://context7.com/api/v1"

    async def _resolve_library_id(self, client: httpx.AsyncClient, library_name: str) -> str:
        """
        Asynchronously resolves a library name to a Context7-compatible ID.
        """
        try:
            if library_name.startswith('/') and '/' in library_name[1:]:
                return library_name

            search_url = f"{self.api_base_url}/search"
            params = {"query": library_name}
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json()

            results: List[Dict[str, Any]] = search_results.get("results")
            if not results:
                return f"Unable to resolve any library for '{library_name}'."

            best_match = results[0]
            library_id = best_match.get("id")

            if not library_id:
                return f"Could not extract library ID for '{library_name}' from search results."

            return f"/{library_id}"

        except httpx.HTTPStatusError as e:
            return f"HTTP error while resolving library ID: {e.response.status_code}"
        except Exception as e:
            return f"An unexpected error occurred while resolving library ID: {e}"

    async def _get_library_docs(self, client: httpx.AsyncClient, library_id: str, topic: Optional[str], tokens: int) -> str:
        """
        Asynchronously fetches library documentation from the Context7 API.
        """
        try:
            if library_id.startswith("/"):
                library_id = library_id[1:]

            docs_url = f"{self.api_base_url}/{library_id}"
            params = {"type": "txt"}
            if topic:
                params["topic"] = topic
            if tokens:
                params["tokens"] = str(tokens)

            headers = {"X-Context7-Source": "mcp-server"}
            response = await client.get(docs_url, params=params, headers=headers)
            response.raise_for_status()

            doc_text = response.text
            if not doc_text or doc_text in ("No content available", "No context data available"):
                return "No documentation content is available for the specified library or topic."

            return doc_text

        except httpx.HTTPStatusError as e:
            return f"HTTP error while fetching documentation: {e.response.status_code}"
        except Exception as e:
            return f"An unexpected error occurred while fetching documentation: {e}"
    
    def _run(self, library_name: str, topic: Optional[str] = None, tokens: int = 3000, **kwargs: Any) -> str:
        """Synchronously wraps the async _arun method."""
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(self._arun(library_name=library_name, topic=topic, tokens=tokens, **kwargs))
        except RuntimeError:
            return asyncio.run(self._arun(library_name=library_name, topic=topic, tokens=tokens, **kwargs))
        
    async def _arun(self, library_name: str, topic: Optional[str] = None, tokens: int = 3000, **kwargs: Any) -> str:
        """Asynchronously executes the tool to fetch documentation."""
        logger.info(f"Running Context7 Docs Tool for library: '{library_name}', topic: '{topic}'")
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                library_id = await self._resolve_library_id(client, library_name)
                if not library_id.startswith("/"):
                    logger.warning(f"Could not resolve library ID for '{library_name}': {library_id}")
                    return library_id[:4000]

                docs = await self._get_library_docs(client, library_id, topic, tokens)
                
                # Regex to find all documentation sections with language and code
                pattern = re.compile(
                    r"TITLE:(.*?)"
                    r"DESCRIPTION:(.*?)"
                    r"SOURCE:(.*?)"
                    r"LANGUAGE: (.*?)\n"
                    r"CODE:\n```(.*?)```", 
                    re.DOTALL | re.IGNORECASE
                )
                
                matches = pattern.finditer(docs)
                python_docs = []
                
                for match in matches:
                    language = match.group(4).strip().lower()
                    if language.lower() == "python":
                        # Reconstruct the documentation block for Python code
                        title = match.group(1).strip()
                        description = match.group(2).strip()
                        source = match.group(3).strip()
                        code = match.group(5).strip()
                        
                        python_doc_block = (
                            f"TITLE: {title}\n"
                            f"DESCRIPTION: {description}\n"
                            f"SOURCE: {source}\n"
                            f"LANGUAGE: python\n"
                            f"CODE:\n```{code}```"
                        )
                        python_docs.append(python_doc_block)

                if not python_docs:
                    logger.info(f"No Python code snippets found for '{library_name}'. Returning a notification.")
                    return "No Python-specific documentation or code examples were found in the results."

                logger.info(f"Successfully filtered and found {len(python_docs)} Python code snippets for '{library_name}'.")
                return "\n\n----------------------------------------\n\n".join(python_docs)[:4000]
                
        except Exception as e:
            error_msg = f"An unexpected error occurred in Context7DocsTool: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg[:4000]

context7_docs_tool = Context7DocsTool()

async def main():
    """Example usage of the tool."""
    tool = Context7DocsTool()

    print("--- Fetching React 'hooks' documentation ---")
    docs_content = await tool.ainvoke({"library_name": "react", "topic": "hooks"})
    print(docs_content[:1000] + "..." if len(docs_content) > 1000 else docs_content)

    print("\n" + "="*50 + "\n")

    print("--- Fetching general Next.js documentation ---")
    docs_content_next = await tool.ainvoke({"library_name": "nextjs"})
    print(docs_content_next[:1000] + "..." if len(docs_content_next) > 1000 else docs_content_next)

if __name__ == "__main__":
    asyncio.run(main())