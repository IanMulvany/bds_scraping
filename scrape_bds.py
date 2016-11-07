from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import json
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from datetime import datetime
import settings as settings
import requests as r

cursor_index = settings.CURSOR_INDEX
crossref_index = settings.CROSSREF_INDEX
doi_queue = settings.DOI_QUEUE
PLOS_ISSN = settings.PLOS_ISSN
es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

# Crossref API endpoint = http://api.crossref.org/journals/2053-9517/works

# DOI of an article is: http://dx.doi.org/10.1177/2053951716662054
# Fulltext html is: http://bds.sagepub.com/content/3/2/2053951716662054
#
# So the HTML url has the pattern http://bds.sagepub.com/content/volue/issue/doi
# Good, we can use the crossref API to progromatically extract data from the BDS journal

"""
some thoughts on how to scrape new DOIs, we can basically use ES like a queue, and create
a specific index for that purpose. Here is the algorithm:

- get an ISSN - DONE
- get new DOIS via crossref and paging - DONE
- add the cursor to the issn cursor field - DONE
- for every DOI:
    - add the md to the DOI index - DONE
    - add just the issn and DOI to a "to be scraped" index, with the DOI as the item ID - DONE
- when scraping via DOI iterate over the "to be scraped" via issn - NOT DONE
- get the scrpaed content for SAGE  - NOT DONE
- get the scraped content for PLOS  - NOT DONE
- push the scraped content into es - NOT DONE
- when we have scraped a particular DOI remove that item from the "to be scraped" - NOT DONE
- split the index creation, title population and full text scraping into sepearte functions - NOT DONE
"""

# Project level TODOs
#TODO: when scraping via DOI iterate over the "to be scraped" via issn
#TODO: get the scrpaed content for SAGE
#TODO: get the scrpaed content for PLOS
#TODO: get the scrpaed content for XML
#TODO: push scraped content into es
#TODO: when we have scraped a particular DOI remove that item from the "to be scraped"
#TODO: split the index creation, title population and full text scraping into sepearte functions

scrape_sage_html_issns = ["2053-9517", "2044-6055"]

HEADERS = {
    'User-Agent': 'Automated BDS Scraper 1.0',
    'From': 'ian@mulvany.net'  # This is another valid field
}

# has_issn_filter = {
#     "query": {
#     "filtered": {
#     "query": {
#       "match_all": {}
#     },
#     "filter":  {
#       "bool": {
#         "must": {"term" : {"issn": issn}
#         }
#       }
#     }
#     }
#     }
# }

class NoRedirectException(Exception):
    pass

class NoContentInIndexException(Exception):
    pass

class SageScrapedArticle(object):
    def __init__(self, url):
        self.description = "a scraped version of a BDS research article"
        self.title = ""
        self.abstract = ""
        self.authors = ""
        self.fulltext = ""
        self.references = ""
        self.pubyear = ""
        self.conclusion = ""
        self.methods = ""
        self.url = url
        self.soup = None
        self.es_representation = {}

        self.gen_soup()
        self.scrape_title()
        self.scrape_abstract()
        self.scrape_pubyear()
        self.scrape_conclusion()
        self.scrape_fulltext()
        self.scrape_authors()
        self.prep_es_rep()

    def gen_soup(self):
        html = r.get(self.url, headers=HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')
        self.soup = soup

    def scrape_title(self):
        title_div = self.soup.findAll("h1", {"class" : "highwire-cite-title"})[0] # assume a unique class, and that this is the first result
        self.title = title_div.contents[0] # The literary uses of high-dimensional space

    def scrape_abstract(self):
        abstract = self.soup.findAll("div", {"class" : "section abstract"}, {"id": "abstract-1"})[0] # assume a unique class, and that this is the first result
        abstract_content = abstract.getText()
        abstract_content_stripped = abstract_content.lstrip("Abstract")
        self.abstract = abstract_content_stripped

    def scrape_conclusion(self):
        conclusion = self.soup.findAll("div", {"class" : "section conclusions"})[0] # assume a unique class, and that this is the first result
        conclusion_content = conclusion.getText()
        conclusion_content_stripped = conclusion_content.lstrip("Conclusion")
        self.conclusion = conclusion_content_stripped

    def scrape_fulltext(self):
        fulltext = self.soup.findAll("div", {"class" : "fulltext-view"})[0] # assume a unique class, and that this is the first result
        fulltext_content = fulltext.getText()
        self.fulltext = fulltext_content

    def scrape_pubyear(self):
        cite_md = self.soup.findAll("span", {"class" : "highwire-cite-metadata"})[0] # assume a unique class, and that this is the first result
        cite_md_text = cite_md.getText()
        print(cite_md_text)
        pubyear = cite_md_text.rstrip().split()[-1]
        self.pubyear = pubyear

    def scrape_authors(self):
        author_group = self.soup.findAll("div", {"class" : "highwire-cite-authors"})[0] # assume a unique class, and that this is the first result
        authors = author_group.findAll("span", {"class" : "highwire-citation-author"}) # assume
        names = []
        for author in authors:
            given = author.findAll("span", {"class" :"nlm-given-names"})[0].getText()
            surname = author.findAll("span", {"class" :"nlm-surname"})[0].getText()
            names.append(given + " " + surname)
        self.authors = names

    def prep_es_rep(self):
        #TODO: complete this function
        self.es_representation = {}

def get_resolved_url(doi):
    """
    use requests history function to follow redirects from dx.doi.org
    pass a doi and get back the publisher url for the article (hopefully!)
    """
    dx_url = "http://dx.doi.org/" + doi
    response = r.get(dx_url, headers=HEADERS)
    if response.history:
        for resp in response.history:
            print(resp)
            # need to iterate through to get to the final redirect??
            #TODO: check if this iteration is required
            status, resp_url = resp.status_code, resp.url
        status, final_url = response.status_code, response.url
        return final_url
    else:
        raise NoRedirectException("doi did not result in a redirect, probably not getting to publisher conent")

def scrape_sage_html(doi):
    url = get_resolved_url(doi)
    sage_scraped_article = SageScrapedArticle(url)
    formated_article_content = sage_scraped_article.es_representation
    return formated_article_content

def scrape_plos_content(doi):
    # type (string) -> bool
    #TODO: finish this function
    # not implemented yet
    return False

def get_item_by_key(item, item_key, request_body):
    # type: (str, str, Dict[str, str]) -> Dict[str, str]
    "data may be missing in the crossref deposit, so if it's missing we pass back a nul value"
    try:
        # we manage to extract a new value, and we extend the request_body dict
        item_value = item[item_key]
        request_body[item_key] = item_value
        return request_body
    except:
        request_body[item_key] = None # what's the python value for null?
        return request_body

def get_author_by_key(item, item_key, request_body):
    # type: (Dict[Any, Any], str, Dict[Any, Any]) -> Dict[Any, Any]
    try:
        authors = ""
        # we manage to extract a new value, and we extend the request_body dict
        print(item)
        print("")
        names = item[item_key]
        for name in names:
            print(name)
            first = name["given"]
            second = name["family"]
            authors = authors + first + " " + second + ", "
            print(authors)
        authors = authors.rstrip(", ")
        request_body[item_key] = authors
        print(request_body)
        return request_body
    except:
        request_body[item_key] = None # what's the python value for null?
        return request_body

def infer_earliest_pub_date(item, request_body):
    #TODO: complete this function
    #TODO: name final pub variable
    #TODO: create a proper time object to put into es
    print(item)
    keys = item.keys()
    print(keys)
    if "published-online" in keys:
        pub_date = item["published-online"]["date-parts"][0]
    elif "published-print"  in keys:
        pub_date = item["published-print"]["date-parts"][0]
    elif "issued"  in keys:
        pub_date = item["issued"]["date-parts"][0]
    elif "deposited"  in keys:
        pub_date = item["deposited"]["date-parts"][0]
    else:
        pub = None
        request_body["pub_date"] = pub
        return request_body
    year = pub_date[0]
    month = pub_date[1]
    day = pub_date[2]
    pub = str(year) + "-" + str(month) + "-" + str(day)
    print(pub)
    request_body["pub_date"] = pub
    return request_body

def map_crossref_bib_to_es(bib_item):
    request_body = {}
    request_body = get_item_by_key(bib_item, "DOI", request_body)
    request_body = get_item_by_key(bib_item, "URL", request_body)
    request_body = get_item_by_key(bib_item, "container-title", request_body)
    request_body = get_author_by_key(bib_item, "author", request_body)
    request_body = get_item_by_key(bib_item, "title", request_body)
    request_body = get_item_by_key(bib_item, "ISSN", request_body)
    request_body = get_item_by_key(bib_item, "fulltext", request_body)
    request_body = infer_earliest_pub_date(bib_item, request_body)
    return request_body

def push_doi_to_queue(item, doi_queue_index):
    request_body = {}
    request_body = get_item_by_key(item, "ISSN", request_body)
    request_body = get_item_by_key(item, "DOI", request_body)
    doi = request_body["DOI"]
    es.index(index=doi_queue_index, doc_type="doi_queue", body=request_body, id=doi)
    return True

def get_dois(issn, doi_queue_index):
    # type(string) -> Dict[string]
    """
    use our stored info in es to get the DOIs easily
    but ... what do we do if we are retreiving 50k dois?
    """
    query = {
            "query": {
                "filtered": {
                    "query": {
                        "match_all": {}
                        },
                    "filter":  {
                "bool": {
                    "must": {"term" : {"issn": issn}
                            }
                        }
                    }
                }
            }
        }

    print(doi_queue)
    dois = []
    if has_docs(doi_queue):
        print(es.__dict__)
        response = es.search(index=doi_queue_index, body=query, filter_path=['hits.hits._source.DOI'])
        items = response["hits"]["hits"]
        for item in items:
            dois.append(item["_source"]["DOI"])
        return dois
    else:
        raise NoContentInIndexException("there is not content in this index")

def remove_doi_from_queue(doi, doi_queue_index):
    # type(str, str) -> bool
    """
    removes a specific item with the doi as it's is from the given index
    """
    es.remove(index=doi_queue_index, id=doi) # not sure if this is right, bit it looks right 
    return True

def push_items_to_es(items):
    """
    send the crossref data into es, and then add a doi to the
    to be scraped queue
    """
    for item in items:
        request_body = map_crossref_bib_to_es(item)
        print(request_body)
        print(request_body) #temporary shitty debugging
        es.index(index=crossref_index, doc_type="crossref_md", body=request_body)
        push_doi_to_queue(item, doi_queue_index=doi_queue)
    return True

def get_cursor(issn):
    """
    query es and return the last cursor used via issn
    """
    query = {
        "query": {
        "filtered": {
        "query": {
          "match_all": {}
        },
        "filter":  {
          "bool": {
            "must": {"term" : {"issn": issn}
            }
          }
        }
        }
        }
    }

    if has_docs(cursor_index):
        response = es.search(index=cursor_index, body=query, sort="timestamp:desc", size=1, filter_path=['hits.hits._source.cursor'])
        hit_count = len(response) # we might have an index with values from a different issn, but no cursors stored for the issn that we are currently looking at.
        if hit_count > 0:
            return_cursor = response["hits"]["hits"][0]["_source"]["cursor"]
            return return_cursor
        else:
            return False
    else:
        raise NoContentInIndexException("the supplied index has no content!")

def store_cursor(issn, cursor):
    """
    push a paging cursor from crossref into es for retrival when we
    return to continue paging through new articles
    """
    request_body = {
        "issn" : issn,
        "cursor": cursor,
        'timestamp': datetime.now()
    }
    es.index(index=cursor_index, doc_type="issn_cursor", body=request_body) # check if we can do this without needing a return value !
    return True

def get_works_endpoint(issn):
    cursor = get_cursor(issn)
    if cursor:
        url = "http://api.crossref.org/journals/"+issn+"/works?cursor=" + cursor
    else:
        url = "http://api.crossref.org/journals/"+issn+"/works?cursor=*"
    return url

def get_items(url):
    response = r.get(url, headers=HEADERS)
    data = response.json()
    items = data["message"]["items"]
    cursor = data["message"]["next-cursor"]
    return items, cursor

def title_data_to_es(issn):
    # type: (str) -> bool
    """
    push crossref works data into a local ES
    """
    url = get_works_endpoint(issn)
    items, cursor = get_items(url)
    push_items_to_es(items)
    while len(items) > 0:
        # we didn't end up with no items, so we need to iterate down the cursor
        # we are goig to store the last cursor in our DB, as the cursor that is returned that ends up with 0 results may give us a null result the next time we query our result set.
        last_cursor = cursor
        url = "http://api.crossref.org/journals/"+issn+"/works?cursor=" + cursor
        items, cursor = get_items(url)
        push_items_to_es(items)
    # we have paged through the results and we have a final cursor from our searching.
    # we now need to store that cursor for later use.
    store_cursor(issn, last_cursor)
    return True

def has_docs(index):
    # type: (str) -> bool
    """
    check if there are documents in a specific index
    """
    response = es.indices.stats(index=index, metric="docs")
    doc_count = response["indices"][index]["total"]["docs"]["count"]
    if doc_count > 0:
        return True
    else:
        return False

def scrape_content(issn, doi, fulltext_link, resolved_url, url):
    """
    make a decision on which content scraping funtion to use
    based on our info about issn, doi, whehter there is a fulltext
    link, or other attributes.

    The returned scraped content is returned as a json representation,
    in the case of the sage content we return sage_scraped_article.es_representation
    """
    if issn in scrape_sage_html_issns:
        content = scrape_sage_html(doi)
    elif issn == PLOS_ISSN:
        content = scrape_plos_content(doi)
    else:
        # we have no scraper for this kind of content
        # Raise an error exceptoin mentioning that we have no scraper for
        # this content yet.
        return False
    return content

def push_scraped_content_into_es(scraped_content):
    """
    push scrapted content into es
    """
    #TODO: complete this fucntion
    return False

def is_scraped(doi):
    #TODO: check if this article is already in the scraped index
    return False

def scrape_content_via_doi(issn, doi):
    """
    we check if the content has already been scraped, and if not
    then we scrape the article.
    """
    if is_scraped(doi):
        # yay, we already have the fulltext!
        pass
    else:
        # where do we put the url info? I don't need
        # the fulltext link for now, I only need the doi and issn at the moment.
        #
        # fulltext_link = get_fulltext_link(doi) # don't need this for the time being
        # url = get_url(doi) # don't need this for the time being
        resolved_url = get_resolved_url(doi) # I only want to generate this when I come to scrape the resource.
        fulltext_link = ""
        url = ""
        scraped_content = scrape_content(issn, doi, fulltext_link, resolved_url, url)
        push_scraped_content_into_es(scraped_content)
        #TODO: finish the function that pushes the scraped content into es
    # we have now finised working with the DOI so we remove it from the queue
    remove_doi_from_queue(doi)

def scrape_content_via_issn(issn):
    # Type (str) -> None
    doi_queue_index = doi_queue
    dois = get_dois(issn, doi_queue_index) # this needs to pull from the queue, and not the title data!
    #TODO: ensure my scraping code is working before activating the scraping by doi
    # for doi in dois:
    #     scrape_content_via_doi(issn, doi)

ISSN = "2158-2440" # Sage Open
ISSN = "2053-9517" # BDS
ISSN = "1360-063X" # urban studies
ISSN = "2044-6055" # BMJ open - got some, but hit a bug
ISSN = "1461-7315" # new media and society / didn't work, boo
ISSN = "2221-0989" # International journal of humanities and social science - didn't work, boo

"""
{'reference-count': 0, 'subject': ['Medicine(all)'], 'prefix': 'http://id.crossref.org/prefix/10.1136', 'issued': {'date-parts': [[2015, 10]]}, 'publisher': 'BMJ', 'issue': '10', 'container-title': ['BMJ Open'], 'short-container-title': [], 'created': {'date-parts': [[2015, 10, 29]], 'timestamp': 1446087914000, 'date-time': '2015-10-29T03:05:14Z'}, 'volume': '5', 'short-title': [], 'indexed': {'date-parts': [[2015, 12, 17]], 'timestamp': 1450324943688, 'date-time': '2015-12-17T04:02:23Z'}, 'source': 'CrossRef', 'update-to': [{'label': 'Correction', 'updated': {'date-parts': [[2015, 10, 1]], 'timestamp': 1443657600000, 'date-time': '2015-10-01T00:00:00Z'}, 'type': 'correction', 'DOI': '10.1136/bmjopen-2014-006374'}], 'alternative-id': ['10.1136/bmjopen-2014-006374corr1'], 'page': 'e006374corr1', 'title': ['Correction'], 'type': 'journal-article', 'URL': 'http://dx.doi.org/10.1136/bmjopen-2014-006374corr1', 'original-title': [], 'ISSN': ['2044-6055', '2044-6055'], 'content-domain': {'crossmark-restriction': False, 'domain': []}, 'update-policy': 'http://dx.doi.org/10.1136/crossmarkpolicy', 'member': 'http://id.crossref.org/member/239', 'deposited': {'date-parts': [[2015, 10, 29]], 'timestamp': 1446087915000, 'date-time': '2015-10-29T03:05:15Z'}, 'DOI': '10.1136/bmjopen-2014-006374corr1', 'subtitle': [], 'score': 1.0}
dict_keys(['reference-count', 'subject', 'prefix', 'issued', 'publisher', 'issue', 'container-title', 'short-container-title', 'created', 'volume', 'short-title', 'indexed', 'source', 'update-to', 'alternative-id', 'page', 'title', 'type', 'URL', 'original-title', 'ISSN', 'content-domain', 'update-policy', 'member', 'deposited', 'DOI', 'subtitle', 'score'])
Traceback (most recent call last):
  File "scrape_bds.py", line 469, in <module>
    title_data_to_es(ISSN)
  File "scrape_bds.py", line 349, in title_data_to_es
    push_items_to_es(items)
  File "scrape_bds.py", line 270, in push_items_to_es
    request_body = map_crossref_bib_to_es(item)
  File "scrape_bds.py", line 253, in map_crossref_bib_to_es
    request_body = infer_earliest_pub_date(bib_item, request_body)
  File "scrape_bds.py", line 238, in infer_earliest_pub_date
    day = pub_date[2]
IndexError: list index out of range
"""

if __name__ == "__main__":
    dois = get_dois("2053-9517", doi_queue_index=doi_queue)

    #
    # # Methodological Innovations
    # # Social Science Computer Review
    # ISSN = "0959-8138" # BMJ
    # title_data_to_es(ISSN)
