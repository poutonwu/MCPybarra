import pytest
import re
import inspect
from mcp_server_tavily.server import serve

# Extract the format_results function from inside the serve function
serve_source = inspect.getsource(serve)
format_results_code = re.search(r'def format_results\(response: dict\) -> str:(.*?)(?=\n    @|\n\n)', serve_source, re.DOTALL).group(0)

# Define format_results in this module's scope
exec(format_results_code, globals())


class TestFormatResults:
    def test_format_basic_results(self, web_search_response):
        """Test formatting of basic search results without filters or answer."""
        formatted = format_results(web_search_response)
        
        # Check expected sections in the output
        assert "Detailed Results:" in formatted
        
        # Check that each result is included
        for result in web_search_response["results"]:
            assert result["title"] in formatted
            assert result["url"] in formatted
            assert result["content"] in formatted
        
        # Check that filter sections are not included
        assert "Search Filters:" not in formatted
        assert "Including domains:" not in formatted
        assert "Excluding domains:" not in formatted
        
        # Check that answer section is not included
        assert "Answer:" not in formatted
    
    def test_format_results_with_answer(self, answer_search_response):
        """Test formatting of search results with an answer."""
        formatted = format_results(answer_search_response)
        
        # Check that answer is included
        assert "Answer:" in formatted
        assert answer_search_response["answer"] in formatted
        assert "Sources:" in formatted
        
        # Check that each result is included
        for result in answer_search_response["results"]:
            assert result["title"] in formatted
            assert result["url"] in formatted
            assert result["content"] in formatted
    
    def test_format_results_with_news(self, news_search_response):
        """Test formatting of news search results with published dates."""
        formatted = format_results(news_search_response)
        
        # Check expected sections in the output
        assert "Detailed Results:" in formatted
        
        # Check that each result is included with published date
        for result in news_search_response["results"]:
            assert result["title"] in formatted
            assert result["url"] in formatted
            assert result["content"] in formatted
            assert "Published:" in formatted
            assert result["published_date"] in formatted
    
    def test_format_results_with_filters(self, web_search_response):
        """Test formatting of search results with domain filters."""
        # Add domain filters to the response
        response = web_search_response.copy()
        response["included_domains"] = ["example.com"]
        response["excluded_domains"] = ["spam.com"]
        
        formatted = format_results(response)
        
        # Check that filter sections are included
        assert "Search Filters:" in formatted
        assert "Including domains: example.com" in formatted
        assert "Excluding domains: spam.com" in formatted
        
        # Check that each result is included
        for result in response["results"]:
            assert result["title"] in formatted
            assert result["url"] in formatted
            assert result["content"] in formatted
    
    def test_format_results_complete(self, answer_search_response):
        """Test formatting of complete search results with all elements."""
        # Add domain filters and published dates to the response
        response = answer_search_response.copy()
        response["included_domains"] = ["example.com"]
        response["excluded_domains"] = ["spam.com"]
        
        # Add published_date to results
        for result in response["results"]:
            result["published_date"] = "2023-09-01"
        
        formatted = format_results(response)
        
        # Check that all sections are included
        assert "Search Filters:" in formatted
        assert "Including domains: example.com" in formatted
        assert "Excluding domains: spam.com" in formatted
        assert "Answer:" in formatted
        assert response["answer"] in formatted
        assert "Sources:" in formatted
        assert "Detailed Results:" in formatted
        
        # Check that each result is included with published date
        for result in response["results"]:
            assert result["title"] in formatted
            assert result["url"] in formatted
            assert result["content"] in formatted
            assert "Published:" in formatted
            assert result["published_date"] in formatted