import pytest
from utils.api_client import APIClient


@pytest.fixture(scope="session")
def base_url():
    return "https://qa-internship.avito.com"


@pytest.fixture(scope="session")
def api_client(base_url):
    return APIClient(base_url)
