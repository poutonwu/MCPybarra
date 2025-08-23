import os
from typing import Type, Any, Literal, List, Optional

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from tavily import TavilyClient, InvalidAPIKeyError, UsageLimitExceededError

from framwork.logger import logger

class TavilySearchInput(BaseModel):
    """Input schema for the Tavily Search tool."""
    query: str = Field(description="The search query for technical information, APIs, or code examples.")
    search_depth: Literal["basic", "advanced"] = Field(
        default="basic",
        description="Search depth: 'basic' for quick results, 'advanced' for more comprehensive analysis."
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of search results to return.",
        gt=0,
        le=10,
    )
    include_domains: Optional[List[str]] = Field(
        default=None,
        description="A list of domains to specifically include in the search results (e.g. ['stackoverflow.com', 'github.com'])."
    )
    exclude_domains: Optional[List[str]] = Field(
        default=None,
        description="A list of domains to specifically exclude from the search results."
    )

class TavilySearchTool(BaseTool):
    """
    A tool that uses the Tavily API to perform web searches for technical information,
    helping to find code examples, API documentation, and best practices.
    """
    name: str = "tavily_technical_search"
    description: str = (
        "Performs a web search using the Tavily API to find technical information, code examples, or API documentation. "
        "Use this when you need external knowledge to fulfill a user's request, such as finding the correct usage of a library, "
        "understanding a technical concept, or looking for code examples."
    )
    args_schema: Type[BaseModel] = TavilySearchInput

    api_key: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("Tavily API key not found. Please set the TAVILY_API_KEY environment variable in your .env file.")

    def _format_results(self, response: dict) -> str:
        """Formats Tavily search results into a readable string."""
        output = []
        if response.get("answer"):
            output.append(f"Answer: {response['answer']}")

        if response.get("results"):
            output.append("\nDetailed Results:")
            for result in response["results"]:
                output.append(f"\nTitle: {result['title']}")
                output.append(f"URL: {result['url']}")
                output.append(f"Content: {result['content']}")
                if result.get("score"):
                    output.append(f"Score: {result['score']}")
        
        if not output:
            return "No results found."

        return "\n".join(output)

    def _run(self, query: str, search_depth: str = "basic", max_results: int = 5, include_domains: Optional[List[str]] = None, exclude_domains: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Synchronously perform a Tavily search."""
        logger.info(f"Performing synchronous Tavily search for: '{query}'")
        try:
            client = TavilyClient(api_key=self.api_key)
            # Use include_answer=True to get a direct answer if possible
            response = client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains or [],
                exclude_domains=exclude_domains or [],
                include_answer=True,
            )
            formatted_results = self._format_results(response)
            logger.info("Tavily search successful. Returning formatted results.")
            return formatted_results[:4000]
        except (InvalidAPIKeyError, UsageLimitExceededError) as e:
            error_msg = f"Tavily API error: {e}"
            logger.error(error_msg)
            return error_msg[:4000]
        except Exception as e:
            error_msg = f"An unexpected error occurred during Tavily search: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg[:4000]

    async def _arun(self, query: str, search_depth: str = "basic", max_results: int = 5, include_domains: Optional[List[str]] = None, exclude_domains: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Asynchronously perform a Tavily search."""
        logger.info(f"Performing asynchronous Tavily search for: '{query}'")
        # The Tavily Python SDK v0.3.3 does not have a native async client.
        # We will call the synchronous method here, which is a common practice in LangChain tools
        # for libraries that do not provide an async interface.
        return self._run(query, search_depth, max_results, include_domains, exclude_domains, **kwargs) 