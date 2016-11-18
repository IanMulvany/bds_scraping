"""
deals with pushing doi info into and off of the doi queue index in elastic search.
"""
from common_functions import get_item_by_key
from common_functions import index_populated
from simple_settings import settings
from exceptions import NoRedirectException
from exceptions import NoContentInIndexException
from elasticsearch import Elasticsearch

DOI_QUEUE = settings.DOI_QUEUE
ES_HOST = settings.ES_HOST
ES_PORT = settings.ES_PORT

ES = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
doi_queue = DOI_QUEUE

def push_doi_to_queue(item, doi_queue_index):
    # type: (str, str) -> bool
    """
    we need to change the ISSN retriveal here to strip the ISSN from being a list item
    """
    request_body = {}
    request_body = get_item_by_key(item, "ISSN", request_body)
    request_body["ISSN"] = request_body["ISSN"][0] # pop the ISSN value out of being a list into a simple type!
    request_body = get_item_by_key(item, "DOI", request_body)
    doi = request_body["DOI"]
    doi_to_queue(doi, doi_queue_index, request_body)
    return True

def doi_to_queue(doi, doi_queue_index, body):
    # type: (str, str, str) -> bool
    ES.index(index=doi_queue_index, doc_type="doi_queue", body=body, id=doi)
    return True

def get_dois(issn, doi_queue_index):
    # type: (str, str) -> List[str]
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
                    "must": {"term" : {"ISSN": issn}
                            }
                        }
                    }
                }
            }
        }

    dois = []
    if index_populated(doi_queue_index):
        response = ES.search(index=doi_queue_index, body=query)
        items = response["hits"]["hits"]
        for item in items:
            dois.append(item["_id"]) # the doi is the id!
        return dois
    else:
        raise NoContentInIndexException("there is not content in this index")

def remove_doi_from_queue(doi, doi_queue_index):
    # type(str, str) -> bool
    """
    removes a specific item with the doi as it's is from the given index
    """
    ES.delete(index=doi_queue_index, id=doi, doc_type="doi_queue") # not sure if this is right, bit it looks right
    return True
