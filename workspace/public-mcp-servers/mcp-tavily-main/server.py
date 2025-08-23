from typing import Annotated
from mcp.server import Server
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field
from tavily import TavilyClient, InvalidAPIKeyError, UsageLimitExceededError

from typing import Literal

import json
import asyncio
from pydantic import field_validator
import os

class SearchBase(BaseModel):
    """Base parameters for Tavily search."""
    query: Annotated[str, Field(description="Search query")]
    max_results: Annotated[
        int,
        Field(
            default=5,
            description="Maximum number of results to return",
            gt=0,
            lt=20,
        ),
    ]
    include_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of domains to specifically include in the search results (e.g. ['example.com', 'test.org'] or 'example.com')",
        ),
    ]
    exclude_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of domains to specifically exclude from the search results (e.g. ['example.com', 'test.org'] or 'example.com')",
        ),
    ]

    @field_validator('include_domains', 'exclude_domains', mode='before')
    @classmethod
    def parse_domains_list(cls, v):
        """Parse domain lists from various input formats.
        
        Handles:
        - None -> []
        - String JSON arrays -> list
        - Single domain string -> [string]
        - Comma-separated string -> list of domains
        - List of domains -> unchanged
        """
        if v is None:
            return []
        if isinstance(v, list):
            return [domain.strip() for domain in v if domain.strip()]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            try:
                # Try to parse as JSON string
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [domain.strip() for domain in parsed if domain.strip()]
                return [parsed.strip()]  # Single value from JSON
            except json.JSONDecodeError:
                # Not JSON, check if comma-separated
                if ',' in v:
                    return [domain.strip() for domain in v.split(',') if domain.strip()]
                return [v]  # Single domain
        return []

class GeneralSearch(SearchBase):
    """Parameters for general web search."""
    search_depth: Annotated[
        Literal["basic", "advanced"],
        Field(
            default="basic",
            description="Depth of search - 'basic' or 'advanced'",
        ),
    ]

class AnswerSearch(SearchBase):
    """Parameters for search with answer."""
    search_depth: Annotated[
        Literal["basic", "advanced"],
        Field(
            default="advanced",
            description="Depth of search - 'basic' or 'advanced'",
        ),
    ]

class NewsSearch(SearchBase):
    """Parameters for news search."""
    days: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of days back to search (default is 3)",
            gt=0,
            le=365,
        ),
    ]

async def serve(api_key: str) -> None:
    """Run the Tavily MCP server.

    Args:
        api_key: Tavily API key
    """
    # Ensure we don't have any lingering tasks
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task() and task.get_name().startswith('tavily_'):
            task.cancel()
    
    server = Server("mcp-tavily")
    client = TavilyClient(api_key=api_key)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="tavily_web_search",
                description="""Performs a comprehensive web search using Tavily's AI-powered search engine. 
                Excels at extracting and summarizing relevant content from web pages, making it ideal for research, 
                fact-finding, and gathering detailed information. Can run in either 'basic' mode for faster, simpler searches 
                or 'advanced' mode for more thorough analysis. Basic is cheaper and good for most use cases. 
                Supports filtering results by including or excluding specific domains.
                Use include_domains/exclude_domains parameters to filter by specific websites.
                Returns multiple search results with AI-extracted relevant content.""",
                inputSchema=GeneralSearch.model_json_schema(),
            ),
            Tool(
                name="tavily_answer_search",
                description="""Performs a web search using Tavily's AI search engine and generates a direct answer to the query, 
                along with supporting search results. Best used for questions that need concrete answers backed by current web sources. 
                Uses advanced search depth by default for comprehensive analysis.

                Features powerful source control through domain filtering:
                - For academic research: exclude_domains=["wikipedia.org"] for more scholarly sources
                - For financial analysis: include_domains=["wsj.com", "bloomberg.com", "ft.com"]
                - For technical documentation: include_domains=["docs.python.org", "developer.mozilla.org"]
                - For scientific papers: include_domains=["nature.com", "sciencedirect.com"]
                - Can combine includes and excludes to fine-tune your sources

                Particularly effective for factual queries, technical questions, and queries requiring synthesis of multiple sources.""",
                inputSchema=AnswerSearch.model_json_schema(),
            ),
            Tool(
                name="tavily_news_search",
                description="""Searches recent news articles using Tavily's specialized news search functionality. 
                Ideal for current events, recent developments, and trending topics. Can filter results by recency 
                (number of days back to search) and by including or excluding specific news domains.

                Powerful domain filtering for news sources:
                - For mainstream news: include_domains=["reuters.com", "apnews.com", "bbc.com"]
                - For financial news: include_domains=["bloomberg.com", "wsj.com", "ft.com"]
                - For tech news: include_domains=["techcrunch.com", "theverge.com"]
                - To exclude paywalled content: exclude_domains=["wsj.com", "ft.com"]
                - To focus on specific regions: include_domains=["bbc.co.uk"] for UK news

                Returns news articles with publication dates and relevant excerpts.""",
                inputSchema=NewsSearch.model_json_schema(),
            ),
        ]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name="tavily_web_search",
                description="Search the web using Tavily's AI-powered search engine",
                arguments=[
                    PromptArgument(
                        name="query",
                        description="Search query",
                        required=True,
                    ),
                    PromptArgument(
                        name="include_domains",
                        description="Optional list of domains to specifically include (e.g., 'wsj.com,bloomberg.com' for financial sources, 'nature.com,sciencedirect.com' for scientific sources)",
                        required=False,
                    ),
                    PromptArgument(
                        name="exclude_domains",
                        description="Optional list of domains to exclude from results (e.g., 'wikipedia.org' to exclude Wikipedia, or 'wsj.com,ft.com' to exclude paywalled sources)",
                        required=False,
                    ),
                ],
            ),
            Prompt(
                name="tavily_answer_search",
                description="Search the web and get an AI-generated answer with supporting evidence",
                arguments=[
                    PromptArgument(
                        name="query",
                        description="Search query",
                        required=True,
                    ),
                    PromptArgument(
                        name="include_domains",
                        description="Optional comma-separated list of domains to include",
                        required=False,
                    ),
                    PromptArgument(
                        name="exclude_domains",
                        description="Optional comma-separated list of domains to exclude",
                        required=False,
                    ),
                ],
            ),
            Prompt(
                name="tavily_news_search",
                description="Search recent news articles with Tavily's news search",
                arguments=[
                    PromptArgument(
                        name="query",
                        description="Search query",
                        required=True,
                    ),
                    PromptArgument(
                        name="days",
                        description="Number of days back to search",
                        required=False,
                    ),
                    PromptArgument(
                        name="include_domains",
                        description="Optional comma-separated list of domains to include",
                        required=False,
                    ),
                    PromptArgument(
                        name="exclude_domains",
                        description="Optional comma-separated list of domains to exclude",
                        required=False,
                    ),
                ],
            ),
        ]

    def format_results(response: dict) -> str:
        """Format Tavily search results into a readable string."""
        output = []
        
        # Add domain filter information if present
        if response.get("included_domains") or response.get("excluded_domains"):
            filters = []
            if response.get("included_domains"):
                filters.append(f"Including domains: {', '.join(response['included_domains'])}")
            if response.get("excluded_domains"):
                filters.append(f"Excluding domains: {', '.join(response['excluded_domains'])}")
            output.append("Search Filters:")
            output.extend(filters)
            output.append("")  # Empty line for separation
        
        if response.get("answer"):
            output.append(f"Answer: {response['answer']}")
            output.append("\nSources:")
            # Add immediate source references for the answer
            for result in response["results"]:
                output.append(f"- {result['title']}: {result['url']}")
            output.append("")  # Empty line for separation
        
        output.append("Detailed Results:")
        for result in response["results"]:
            output.append(f"\nTitle: {result['title']}")
            output.append(f"URL: {result['url']}")
            output.append(f"Content: {result['content']}")
            if result.get("published_date"):
                output.append(f"Published: {result['published_date']}")
            
        return "\n".join(output)

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            if name == "tavily_web_search":
                args = GeneralSearch(**arguments)
                response = client.search(
                    query=args.query,
                    max_results=args.max_results,
                    search_depth=args.search_depth,
                    include_domains=args.include_domains or [],  # Convert None to empty list
                    exclude_domains=args.exclude_domains or [],  # Convert None to empty list
                )
            elif name == "tavily_answer_search":
                args = AnswerSearch(**arguments)
                response = client.search(
                    query=args.query,
                    max_results=args.max_results,
                    search_depth=args.search_depth,
                    include_answer=True,
                    include_domains=args.include_domains or [],  # Convert None to empty list
                    exclude_domains=args.exclude_domains or [],  # Convert None to empty list
                )
            elif name == "tavily_news_search":
                args = NewsSearch(**arguments)
                response = client.search(
                    query=args.query,
                    max_results=args.max_results,
                    topic="news",
                    days=args.days if args.days is not None else 3,
                    include_domains=args.include_domains or [],
                    exclude_domains=args.exclude_domains or [],
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
                
            # Add domain filter information to response for formatting
            if args.include_domains:
                response["included_domains"] = args.include_domains
            if args.exclude_domains:
                response["excluded_domains"] = args.exclude_domains
                
        except (InvalidAPIKeyError, UsageLimitExceededError) as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=str(e)))
        except ValueError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        return [TextContent(
            type="text",
            text=format_results(response),
        )]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        if not arguments or "query" not in arguments:
            raise McpError(ErrorData(code=INVALID_PARAMS, message="Query is required"))

        try:
            # Parse domain filters if provided
            include_domains = None
            exclude_domains = None
            if "include_domains" in arguments:
                include_domains = SearchBase.parse_domains_list(arguments["include_domains"])
            if "exclude_domains" in arguments:
                exclude_domains = SearchBase.parse_domains_list(arguments["exclude_domains"])

            if name == "tavily_web_search":
                response = client.search(
                    query=arguments["query"],
                    include_domains=include_domains or [],  # Convert None to empty list
                    exclude_domains=exclude_domains or [],  # Convert None to empty list
                )
            elif name == "tavily_answer_search":
                response = client.search(
                    query=arguments["query"],
                    include_answer=True,
                    search_depth="advanced",
                    include_domains=include_domains or [],
                    exclude_domains=exclude_domains or [],
                )
            elif name == "tavily_news_search":
                days = arguments.get("days")
                response = client.search(
                    query=arguments["query"],
                    topic="news",
                    days=int(days) if days else 3,
                    include_domains=include_domains or [],
                    exclude_domains=exclude_domains or [],
                )
            else:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown prompt: {name}"))

            # Add domain filter information to response for formatting
            if include_domains:
                response["included_domains"] = include_domains
            if exclude_domains:
                response["excluded_domains"] = exclude_domains

        except (InvalidAPIKeyError, UsageLimitExceededError) as e:
            return GetPromptResult(
                description=f"Failed to search: {str(e)}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=str(e)),
                    )
                ],
            )

        return GetPromptResult(
            description=f"Search results for: {arguments['query']}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=format_results(response)),
                )
            ],
        )

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(read_stream, write_stream, options, raise_exceptions=True)
        finally:
            # Clean up any lingering tasks
            for task in asyncio.all_tasks():
                if task is not asyncio.current_task() and task.get_name().startswith('tavily_'):
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=0.1)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass

if __name__ == "__main__":
    import asyncio
    import argparse
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="give a model the ability to perform AI-powered web searches using Tavily"
    )

    args = parser.parse_args()

    # Check for API key in args first, then environment
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        parser.error("Tavily API key must be provided either via --api-key or TAVILY_API_KEY environment variable")

        
    asyncio.run(serve(api_key))
