import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Type
import asyncio

from langchain_core.tools import BaseTool
from framwork.logger import logger

class WebContentExtractorInput(BaseModel):
    """Input for the Web Content Extractor Tool."""
    url: str = Field(description="The URL of the webpage to extract content from.")

class WebContentExtractorTool(BaseTool):
    """
    A tool to fetch and extract the main textual content from a given webpage URL.
    It ignores robots.txt and mimics a web browser.
    """
    name: str = "web_content_extractor"
    description: str = (
        "Extracts the main textual content from a given webpage URL. "
        "Useful for reading articles, documentation, or other web pages found through a search."
    )
    args_schema: Type[BaseModel] = WebContentExtractorInput

    async def _arun(self, url: str) -> str:
        """Asynchronously fetches and extracts content from a URL, 优化token占用。"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
                logger.info(f"Fetching content from URL: {url}")
                response = await client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type:
                    logger.warning(f"Content from {url} is not HTML ({content_type}). Returning raw text.")
                    return response.text

                soup = BeautifulSoup(response.content, "html.parser")

                # Remove more useless elements
                for element in soup([
                    "script", "style", "header", "footer", "nav", "aside", "form", "input", "button", "iframe", "noscript", "svg", "canvas", "figure", "img", "video", "audio", "picture"
                ]):
                    element.decompose()

                # 优先提取主内容区域
                main_content = None
                for selector in ["article", "main", "section", "div#content", "div.main-content", "div#main", "div.article", "div.post", "div.entry-content"]:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break
                if main_content:
                    text = main_content.get_text(separator="\n")
                else:
                    text = soup.get_text(separator="\n")

                # 清理文本：去除多余空行和空白
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = '\n'.join(lines)

                # 限制最大输出长度
                max_chars = 5000
                if len(text) > max_chars:
                    text = text[:max_chars] + "\n...内容已截断"

                # 优先返回标题+前几段正文
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                if title:
                    text = f"标题: {title}\n\n{text}"

                logger.info(f"Successfully extracted content from {url}.")
                return text if text else "未能提取有意义的正文内容。"

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error occurred while fetching {url}: {e.response.status_code} - {e.response.reason_phrase}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except httpx.RequestError as e:
            error_msg = f"An error occurred while requesting {url}: {e}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"An unexpected error occurred while extracting content from {url}: {e}"
            logger.error(error_msg, exc_info=True)
            return f"Error: {error_msg}"

    def _run(self, url: str) -> str:
        """Synchronously wraps the async _arun method."""
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(self._arun(url))
        except RuntimeError:
            return asyncio.run(self._arun(url)) 