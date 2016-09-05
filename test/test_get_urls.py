import pytest
from scrape_bds import get_url_from_doi
from scrape_bds import NoRedirectException

def test_get_url_from_doi():
    """
    http://api.crossref.org/journals/2053-9517/works
    http://dx.doi.org/10.1177/2053951716662054
    http://bds.sagepub.com/content/3/2/2053951716662054
    """

    doi = "10.1177/2053951715621086"
    derived_url = get_url_from_doi(doi)
    print(derived_url)
    assert derived_url == "http://bds.sagepub.com/content/3/1/2053951715621086"

def test_doi_exception():
    doi = "google.com"
    with pytest.raises(NoRedirectException):
        get_url_from_doi(doi)
