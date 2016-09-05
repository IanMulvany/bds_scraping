from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import requests as r
import json

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
    article_content = get_content_from_bds_url(url)
    return article_content

def get_article_from_doi_issn(doi, issn):
    if issn in scrape_html_issns:
        article_content = get_bds_article_from_doi(doi)
    else:
        print("I don't know how to deal with ISSN %s yet", issn)

def get_dois_from_issn(issn):
    "use the crossref api to get dois for a given issn"
    url = "http://api.crossref.org/journals/"+issn+"/works"
    response = r.get(url, headers=headers)
    data = response.json()
    dois = []
    items = data["message"]["items"]
    for item in items:
        doi = item["DOI"]
        dois.append(doi)
    print(dois)
    return dois