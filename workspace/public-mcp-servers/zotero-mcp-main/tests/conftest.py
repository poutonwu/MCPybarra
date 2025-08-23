"""Pytest fixtures for zotero-mcp tests"""

from typing import Any
from unittest.mock import MagicMock

import pytest
from pyzotero import zotero


@pytest.fixture
def mock_zotero(monkeypatch) -> MagicMock:
    """Fixture that returns a mocked Zotero client"""
    mock = MagicMock(spec=zotero.Zotero)

    def mock_get_zotero_client():
        return mock

    monkeypatch.setattr("zotero_mcp.get_zotero_client", mock_get_zotero_client)
    return mock


@pytest.fixture
def sample_item() -> dict[str, Any]:
    """Fixture that returns a sample Zotero item"""
    return {
        "key": "ABCD1234",
        "data": {
            "key": "ABCD1234",
            "itemType": "journalArticle",
            "title": "Test Article",
            "date": "2024",
            "creators": [
                {"firstName": "John", "lastName": "Doe"},
                {"firstName": "Jane", "lastName": "Smith"},
            ],
            "abstractNote": "This is a test abstract",
            "tags": [{"tag": "test"}, {"tag": "article"}],
            "url": "https://example.com",
            "DOI": "10.1234/test",
        },
        "meta": {"numChildren": 2},
    }


@pytest.fixture
def sample_attachment() -> dict[str, Any]:
    """Fixture that returns a sample Zotero attachment item"""
    return {
        "key": "XYZ789",
        "data": {
            "key": "XYZ789",
            "itemType": "attachment",
            "contentType": "application/pdf",
            "md5": "123456789",
        },
    }
