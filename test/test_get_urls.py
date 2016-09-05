import pytest
from scrape_bds import get_url_from_doi
from scrape_bds import NoRedirectException
from scrape_bds import get_dois_from_issn
import responses

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

@responses.activate
def test_dois_from_issn():
    issn = "2053-9517"
    sample_dois = ["10.1177/2053951715621086", "10.1177/2053951715611145", "10.1177/2053951715606164"]
    body_json_rsponse = open("/Users/ian/Dropbox/workbench/scrape-bds/test/crossref_api_issn_works.json", "r").read()
    responses.add(responses.GET, "http://api.crossref.org/journals/2053-9517/works",
                  body=body_json_rsponse,
                  content_type="application/json")
    dois = get_dois_from_issn(issn)
    for doi in sample_dois:
        assert doi in dois
