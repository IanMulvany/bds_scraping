import pytest
from scrape_bds import get_url_from_doi
from scrape_bds import NoRedirectException
from scrape_bds import get_dois_from_issn
from scrape_bds import BDSScrapedArticle
import responses

def check_existence_in_large_string(host_string, check_string):
    if check_string in host_string:
        return True
    else:
        return False

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
    body_json_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/crossref_api_issn_works.json", "r").read()
    responses.add(responses.GET, "http://api.crossref.org/journals/2053-9517/works",
                  body=body_json_response,
                  content_type="application/json")
    dois = get_dois_from_issn(issn)
    for doi in sample_dois:
        assert doi in dois

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_title():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = BDSScrapedArticle(test_url)
    assert test_article.title == "The literary uses of high-dimensional space"

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_abstract():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = BDSScrapedArticle(test_url)
    assert test_article.abstract == """Debates over “Big Data” shed more heat than light in the humanities, because the term ascribes new importance to statistical methods without explaining how those methods have changed. What we badly need instead is a conversation about the substantive innovations that have made statistical modeling useful for disciplines where, in the past, it truly wasn’t. These innovations are partly technical, but more fundamentally expressed in what Leo Breiman calls a new “culture” of statistical modeling. Where 20th-century methods often required humanists to squeeze our unstructured texts, sounds, or images into some special-purpose data model, new methods can handle unstructured evidence more directly by modeling it in a high-dimensional space. This opens a range of research opportunities that humanists have barely begun to discuss. To date, topic modeling has received most attention, but in the long run, supervised predictive models may be even more important. I sketch their potential by describing how Jordan Sellers and I have begun to model poetic distinction in the long 19th century—revealing an arc of gradual change much longer than received literary histories would lead us to expect."""

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_pubyear():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = BDSScrapedArticle(test_url)
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
    test_article = BDSScrapedArticle(test_url)
    assert test_article.authors == ["Ted Underwood"]

@pytest.mark.scraper
@responses.activate
def test_bds_article_scraping_conclusion():
    body_html_response = open("/Users/ian/Dropbox/workbench/scrape-bds/test/2053951715602494_test_content.html", "r").read()
    responses.add(responses.GET, "http://bds.sagepub.com/content/2/2/2053951715602494",
                  body=body_html_response,
                  content_type="txt/html")
    test_url = "http://bds.sagepub.com/content/2/2/2053951715602494"
    test_article = BDSScrapedArticle(test_url)

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
    test_article = BDSScrapedArticle(test_url)

    test_string = """But in this brief piece I’m less interested in theses about literary history than in a broader methodological point. I’ve suggested that “Big Data” is not a useful term for humanists. The problem is not just that humanists shudder when they hear the word “data,” or that we lack consensus about the scale that counts as “big,” but that the term fails to register the really important methodological shifts that have opened up boundaries between the humanities and social sciences. What we need instead is a conversation that distinguishes the humanistic applications of different modeling strategies."""

    assert check_existence_in_large_string(test_article.fulltext, test_string) == True
