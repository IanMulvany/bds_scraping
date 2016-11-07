import pytest
from scrape_bds import get_resolved_url
from scrape_bds import NoRedirectException
from es_doi_functions import push_doi_to_queue
from es_doi_functions import doi_to_queue
from es_doi_functions import get_dois
from es_doi_functions import remove_doi_from_queue
from scrape_bds import SageScrapedArticle
from create_es_indicies import create_doi_queue_index
from create_es_indicies import delete_es_index
import responses

def check_existence_in_large_string(host_string, check_string):
    if check_string in host_string:
        return True
    else:
        return False

# @pytest.mark.crossref
# @responses.activate
# def test_get_url_from_doi():
#     """
#     http://api.crossref.org/journals/2053-9517/works
#     http://dx.doi.org/10.1177/2053951716662054
#     http://bds.sagepub.com/content/3/2/2053951716662054
#     """
#
#     body_json_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/dx_redirect.json", "r").read()
#     #TODO: figure out how to mock the history attribute of requests using responses
#     responses.add(responses.GET, "http://dx.doi.org/10.1177/2053951715621086",
#                   body=body_json_response, history="hi",
#                   content_type="application/json")
#
#     doi = "10.1177/2053951715621086"
#     resolved_url = get_resolved_url(doi)
#     print(resolved_url)
#     assert resolved_url == "http://bds.sagepub.com/content/3/1/2053951715621086"

@pytest.mark.crossref
@responses.activate
def test_doi_exception():
    doi = "google.com"
    body_json_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/dx_redirect.json", "r").read()
    #TODO: figure out how to mock the history attribute of requests using responses
    responses.add(responses.GET, "http://dx.doi.org/google.com",
                  body=body_json_response,
                  content_type="application/json")
    with pytest.raises(NoRedirectException):
        get_resolved_url(doi)

@pytest.mark.crossref
def test_get_dois():
    """
    create a test index
    add dois to it
    retrieve them with the function we are testing
    verify
    delete test index
    """
    # test data
    print("in test func get dois")
    wrong_dois = ["a","b"]
    test_dois = ["testdoi4", "testdoi5", "testdoi3"]
    test_issn = "abc-123"
    doi_test_index = "doi_queue_test"
    # create the test index in es
    create_doi_queue_index(doi_test_index)
    # push some fake data into es
    body = {"ISSN": test_issn, "DOI": "123abc"}
    for test_doi in test_dois:
        doi_to_queue(test_doi, doi_test_index, body)
    # test our function against this data
    dois = get_dois(test_issn, doi_test_index)
    print(dois)
    for doi in dois:
        assert doi in test_dois
    # delete the test data from es
    # all we need to do is to delete the test index, we don't have to
    delete_es_index(doi_test_index)

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_title():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = SageScrapedArticle(test_url)
    assert test_article.title == "The literary uses of high-dimensional space"

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_abstract():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = SageScrapedArticle(test_url)
    assert test_article.abstract == """Debates over “Big Data” shed more heat than light in the humanities, because the term ascribes new importance to statistical methods without explaining how those methods have changed. What we badly need instead is a conversation about the substantive innovations that have made statistical modeling useful for disciplines where, in the past, it truly wasn’t. These innovations are partly technical, but more fundamentally expressed in what Leo Breiman calls a new “culture” of statistical modeling. Where 20th-century methods often required humanists to squeeze our unstructured texts, sounds, or images into some special-purpose data model, new methods can handle unstructured evidence more directly by modeling it in a high-dimensional space. This opens a range of research opportunities that humanists have barely begun to discuss. To date, topic modeling has received most attention, but in the long run, supervised predictive models may be even more important. I sketch their potential by describing how Jordan Sellers and I have begun to model poetic distinction in the long 19th century—revealing an arc of gradual change much longer than received literary histories would lead us to expect."""

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_pubyear():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = SageScrapedArticle(test_url)
    assert test_article.pubyear == "2015"

@pytest.mark.scraper
@pytest.mark.author
@responses.activate
def test_bds_article_scraping_authors():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = SageScrapedArticle(test_url)
    assert test_article.authors == ["Ted Underwood"]

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_conclusion():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = SageScrapedArticle(test_url)

    test_string = """But in this brief piece I’m less interested in theses about literary history than in a broader methodological point. I’ve suggested that “Big Data” is not a useful term for humanists. The problem is not just that humanists shudder when they hear the word “data,” or that we lack consensus about the scale that counts as “big,” but that the term fails to register the really important methodological shifts that have opened up boundaries between the humanities and social sciences. What we need instead is a conversation that distinguishes the humanistic applications of different modeling strategies."""

    assert check_existence_in_large_string(test_article.conclusion ,test_string) == True

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_fulltext():
    """
    this is the same test as the conclusion test, as the fulltext should be a superset of the conclusion content.
    """
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = SageScrapedArticle(test_url)

    test_string = """But in this brief piece I’m less interested in theses about literary history than in a broader methodological point. I’ve suggested that “Big Data” is not a useful term for humanists. The problem is not just that humanists shudder when they hear the word “data,” or that we lack consensus about the scale that counts as “big,” but that the term fails to register the really important methodological shifts that have opened up boundaries between the humanities and social sciences. What we need instead is a conversation that distinguishes the humanistic applications of different modeling strategies."""

    assert check_existence_in_large_string(test_article.fulltext, test_string) == True
