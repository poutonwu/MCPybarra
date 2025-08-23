import pytest
from pydantic import ValidationError
import json
from mcp_server_tavily.server import SearchBase, GeneralSearch, AnswerSearch, NewsSearch


class TestSearchBase:
    def test_base_model_required_fields(self):
        """Test that query is required for SearchBase."""
        # Should raise error when query is missing
        with pytest.raises(ValidationError):
            SearchBase()
        
        # Should work with just query provided
        model = SearchBase(query="test query")
        assert model.query == "test query"
        assert model.max_results == 5  # default value
        # include_domains and exclude_domains are None by default in the model
        # but get converted to [] when used
        assert model.include_domains is None
        assert model.exclude_domains is None
    
    def test_max_results_validation(self):
        """Test max_results validation rules."""
        # Valid values
        model = SearchBase(query="test", max_results=1)
        assert model.max_results == 1
        
        model = SearchBase(query="test", max_results=19)
        assert model.max_results == 19
        
        # Too small
        with pytest.raises(ValidationError):
            SearchBase(query="test", max_results=0)
        
        # Too large
        with pytest.raises(ValidationError):
            SearchBase(query="test", max_results=20)
    
    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            (None, []),  # None -> empty list
            ([], []),  # Empty list -> empty list
            (["example.com"], ["example.com"]),  # List with single item
            (["example.com", "test.org"], ["example.com", "test.org"]),  # List with multiple items
            ("example.com", ["example.com"]),  # Single string -> list with single item
            ("example.com,test.org", ["example.com", "test.org"]),  # Comma-separated string
            (" example.com , test.org ", ["example.com", "test.org"]),  # Whitespace in comma-separated string
            ('["example.com", "test.org"]', ["example.com", "test.org"]),  # JSON string array
            ("", []),  # Empty string -> empty list
            (" ", []),  # Whitespace string -> empty list
        ],
    )
    def test_parse_domains_list(self, input_value, expected_output):
        """Test that domain list parsing works correctly for various input formats."""
        # Test include_domains
        model = SearchBase(query="test", include_domains=input_value)
        assert model.include_domains == expected_output
        
        # Test exclude_domains
        model = SearchBase(query="test", exclude_domains=input_value)
        assert model.exclude_domains == expected_output


class TestGeneralSearch:
    def test_general_search_defaults(self):
        """Test GeneralSearch default values."""
        model = GeneralSearch(query="test query")
        assert model.query == "test query"
        assert model.search_depth == "basic"  # default for GeneralSearch
        assert model.max_results == 5
        assert model.include_domains is None
        assert model.exclude_domains is None
    
    def test_search_depth_validation(self):
        """Test search_depth validation."""
        # Valid values
        model = GeneralSearch(query="test", search_depth="basic")
        assert model.search_depth == "basic"
        
        model = GeneralSearch(query="test", search_depth="advanced")
        assert model.search_depth == "advanced"
        
        # Invalid value
        with pytest.raises(ValidationError):
            GeneralSearch(query="test", search_depth="super_advanced")


class TestAnswerSearch:
    def test_answer_search_defaults(self):
        """Test AnswerSearch default values."""
        model = AnswerSearch(query="test query")
        assert model.query == "test query"
        assert model.search_depth == "advanced"  # default for AnswerSearch
        assert model.max_results == 5
        assert model.include_domains is None
        assert model.exclude_domains is None


class TestNewsSearch:
    def test_news_search_defaults(self):
        """Test NewsSearch default values."""
        model = NewsSearch(query="test query")
        assert model.query == "test query"
        assert model.days is None
        assert model.max_results == 5
        assert model.include_domains is None
        assert model.exclude_domains is None
    
    def test_days_validation(self):
        """Test days validation."""
        # Valid values
        model = NewsSearch(query="test", days=1)
        assert model.days == 1
        
        model = NewsSearch(query="test", days=365)
        assert model.days == 365
        
        # Too small
        with pytest.raises(ValidationError):
            NewsSearch(query="test", days=0)
        
        # Too large
        with pytest.raises(ValidationError):
            NewsSearch(query="test", days=366)