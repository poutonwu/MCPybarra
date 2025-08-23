from framwork.tool.langchain_file_saver import LangchainFileSaverTool
from framwork.tool.langchain_file_reader import LangchainFileReaderTool
from framwork.tool.tavily_search import TavilySearchTool
from framwork.tool.web_content_extractor import WebContentExtractorTool
from framwork.tool.context7_docs_tool import context7_docs_tool

# Instantiate tools for easy import
save_file_tool = LangchainFileSaverTool()
read_file_tool = LangchainFileReaderTool()
tavily_search_tool = TavilySearchTool(api_key=None)
web_content_extractor_tool = WebContentExtractorTool()

# All tools that can be used by the agent
__all__ = [
    "LangchainFileSaverTool",
    "LangchainFileReaderTool",
    "TavilySearchTool",
    "WebContentExtractorTool",
    "save_file_tool",
    "read_file_tool",
    "tavily_search_tool",
    "web_content_extractor_tool",
    "context7_docs_tool"
]
