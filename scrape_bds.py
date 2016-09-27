from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import requests as r
import json
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
CURSOR_INDEX = "cursors"

# Crossref API endpoint = http://api.crossref.org/journals/2053-9517/works

# DOI of an article is: http://dx.doi.org/10.1177/2053951716662054
# Fulltext html is: http://bds.sagepub.com/content/3/2/2053951716662054
#
# So the HTML url has the pattern http://bds.sagepub.com/content/volue/issue/doi
# Good, we can use the crossref API to progromatically extract data from the BDS journal

# Should set the user agent to decalre myself as a robot!

# set the user agent in requests
#
# def get_dois_from_issn(issn):



scrape_html_issns = ["2053-9517"]

headers = {
    'User-Agent': 'Automated BDS Scraper 1.0',
    'From': 'ian@mulvany.net'  # This is another valid field
}


class NoRedirectException(Exception):
    pass

class BDSScrapedArticle(object):
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

        self.gen_soup()
        self.scrape_title()
        self.scrape_abstract()
        self.scrape_pubyear()
        self.scrape_conclusion()
        self.scrape_fulltext()
        self.scrape_authors()

    def gen_soup(self):
        html = r.get(self.url, headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')
        self.soup = soup

    def scrape_title(self):
        title_div = self.soup.findAll("h1", { "class" : "highwire-cite-title" })[0] # assume a unique class, and that this is the first result
        self.title = title_div.contents[0] # The literary uses of high-dimensional space

    def scrape_abstract(self):
        abstract = self.soup.findAll("div", { "class" : "section abstract" }, {"id": "abstract-1"})[0] # assume a unique class, and that this is the first result
        abstract_content = abstract.getText()
        abstract_content_stripped = abstract_content.lstrip("Abstract")
        self.abstract = abstract_content_stripped

    def scrape_conclusion(self):
        conclusion = self.soup.findAll("div", { "class" : "section conclusions" })[0] # assume a unique class, and that this is the first result
        conclusion_content = conclusion.getText()
        conclusion_content_stripped = conclusion_content.lstrip("Conclusion")
        self.conclusion = conclusion_content_stripped

    def scrape_fulltext(self):
        fulltext = self.soup.findAll("div", { "class" : "fulltext-view" })[0] # assume a unique class, and that this is the first result
        fulltext_content = fulltext.getText()
        self.fulltext = fulltext_content

    def scrape_pubyear(self):
        cite_md = self.soup.findAll("span", { "class" : "highwire-cite-metadata" })[0] # assume a unique class, and that this is the first result
        cite_md_text = cite_md.getText()
        print(cite_md_text)
        pubyear = cite_md_text.rstrip().split()[-1]
        self.pubyear = pubyear

    def scrape_authors(self):
        author_group = self.soup.findAll("div", { "class" : "highwire-cite-authors" })[0] # assume a unique class, and that this is the first result
        authors = author_group.findAll("span", { "class" : "highwire-citation-author" }) # assume
        names = []
        for author in authors:
            given = author.findAll("span", {"class" :"nlm-given-names"})[0].getText()
            surname = author.findAll("span", {"class" :"nlm-surname"})[0].getText()
            names.append(given + " " + surname)
        self.authors = names

def get_url_from_doi(doi):
    """
    use requests history function to follow redirects from dx.doi.org
    pass a doi and get back the publihser url for the article (hopefully!)
    """
    dx_url = "http://dx.doi.org/" + doi
    response = r.get(dx_url, headers=headers)
    if response.history:
        for resp in response.history:
            # need to iterate through to get to the final redirect??
            #TODO: check if this iteration is required
            status, resp_url = resp.status_code, resp.url
        status, final_url = response.status_code, response.url
        return final_url
    else:
        raise NoRedirectException("doi did not result in a redirect, probably not getting to publisher conent")

def get_urls_from_issn():
    return "hi"

def get_dois_for_issn():
    """
    we need to have a stragegy for getting content through different routes, dependent on the ISSN
    that we are interested in. This could be a generic Crossref DOI lookup, or an RSS lookup.
    For now we know that we are going to be looking for a Crossref lookup for BDS.

    The most specific that we get to is looking at the DOI to content mapping route, and that depends on the ISSN.
    """
    return "hi"

def get_content_from_bds_url(url):
    return "hi"

def get_bds_article_from_doi(doi):
    url = get_bds_url_from_doi(doi)
    bds_scraped_article = BDSScrapedArticle(url)
    return bds_scraped_article

def get_article_content_from_doi_issn(doi, issn):
    if issn in scrape_html_issns:
        url = get_url_from_doi(doi)
        article_content = extract_content_from_bds_page(url)
        formated_article_content = format_article_content(article_content)
        return formated_article_content
    else:
        print("I don't know how to deal with ISSN %s yet", issn)

def ingest_articles_from_issn(issn):
    dois = get_dois_from_issn(issn)
    for doi in dois:
        article_info = get_article_from_doi_issn(doi, issn)
        print("ingesting into elastic search: ", doi)
        update_es(article_info)
        print("ingested")

def extract_dois_from_result(items):
    dois = []
    for item in items:
        print(item)
        doi = item["DOI"]
        url = item["URL"]
        journal = item["container-title"]
        author = item["author"]
        title = item["title"]
        issn = item["ISSN"]
        pub_online = item["published-print"]["date-parts"][0]
        pub_online_year = pub_online[0]
        pub_online_month = pub_online[1]
        pub_online_day = pub_online[2]
        pub_online_combined = str(pub_online_year) + "-" + str(pub_online_month) + "-" + str(pub_online_day)
        print()
        dois.append(doi)

        request_body = {
            "issn" : issn,
            "doi" : doi,
            "url" : url,
            "journal" : journal,
            "author" : author,
            "title" : title,
            "pub_online_date" : pub_online_combined,
            'timestamp': datetime.now()
        }
        res = es.index(index="crossref_md", doc_type = "pub_title", body = request_body)
    return dois

def get_cursor(issn):
    print(issn)

    query={
        "query": {
        "filtered": {
        "query": {
          "match_all": {}
        },
        "filter":  {
          "bool": {
            "must": { "term" : {"issn": issn}
            }
          }
        }
        }
        }
    }

    this_index = CURSOR_INDEX
    response = es.indices.stats(index=this_index, metric="docs")
    doc_count = response["indices"][this_index]["total"]["docs"]["count"]
    if doc_count > 0:
        response = es.search(index=this_index, body=query, sort="timestamp:desc", size=1, filter_path=['hits.hits._source.cursor'])
        hit_count = len(response) # we might have an index with values from a different issn, but no cursirs stored for the issn that we are currently looking at.
        if hit_count > 0:
            print(response)
            return_cursor = response["hits"]["hits"][0]["_source"]["cursor"]
            print(return_cursor)
            return return_cursor
        else:
            return False
    else:
        return False

def store_cursor(issn, cursor):
    this_index = CURSOR_INDEX
    request_body = {
        "issn" : issn,
        "cursor": cursor,
        'timestamp': datetime.now()
    }
    res = es.index(index=this_index, doc_type = "issn_cursor", body = request_body)
    return True

def create_es_index(indexname, mapping):
    exist = es.indices.exists(indexname)
    if not exist:
        es.indices.create(index=indexname, body=request_body)

def get_dois_from_issn(issn):
    """
        use the crossref api to get dois for a given issn
        we can also ultimatly add in pagination against the crossref api here too.
    """
    #TODO: add an a function to look at using paging, via checking for the cursor from elassticsearch
    #TODO: extend the extraction of this function to push data that we get from this query into elasticsearch, maybe use a decorator for some of this?
    cursor = get_cursor(issn)
    if cursor:
        url = "http://api.crossref.org/journals/"+issn+"/works?cursor=" + cursor
    else:
        url = "http://api.crossref.org/journals/"+issn+"/works?cursor=*"

    # first pass
    response = r.get(url, headers=headers)
    data = response.json()
    items = data["message"]["items"]
    if len(items) > 0:
        dois = extract_dois_from_result(items)
        cursor = data["message"]["next-cursor"]
    else:
        # exit here, we have no new resutl
        return []

    # now we page through the result
    while len(items) > 0:
        # we are goig to store the last cursor in our DB, as the cursor that is retuned that ends up with 0 results may give us a null result the next time we query our result set.
        last_cursor = cursor
        url = "http://api.crossref.org/journals/"+issn+"/works?cursor=" + cursor
        response = r.get(url, headers=headers)
        data = response.json()
        items = data["message"]["items"]
        dois.extend(extract_dois_from_result(items))
        cursor = data["message"]["next-cursor"]
        print(cursor)
    # we have paged through the results and we have a final cursor from our searching.
    # we now need to store that cursor for later use.
    store_cursor(issn, last_cursor)
    return(dois)


request_body = {
        'mappings': {
            'issn_cursor': {
                  "_timestamp":{
                    "enabled": "true"
                  },
                'properties': {
                    'issn': {'index': 'not_analyzed', 'type': 'string'},
                    'cursor': {'index': 'not_analyzed', 'type': 'string'},
                    'datetime': {'index': 'not_analyzed', 'format': 'dateOptionalTime', 'type': 'date'}
                }}}
    }

indexname = CURSOR_INDEX
create_es_index(indexname, request_body)
# issn = "2053-9517" # Big data and society
#  issn = "2050-084X" # elife
issn = "2158-2440" # Sage Open
dois = get_dois_from_issn(issn)
print(dois)
