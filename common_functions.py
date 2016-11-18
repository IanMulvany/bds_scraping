from simple_settings import settings 
from elasticsearch import Elasticsearch

ES = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

def get_item_by_key(item, item_key, request_body):
    ## type: (Dict[Any, Any], str, Dict[Any, Any]) -> Dict[Any, Any]
    "data may be missing in the crossref deposit, so if it's missing we pass back a nul value"
    try:
        # we manage to extract a new value, and we extend the request_body dict
        item_value = item[item_key]
        request_body[item_key] = item_value
        return request_body
    except:
        request_body[item_key] = None # what's the python value for null?
        return request_body

def index_populated(index):
    # type: (str) -> bool
    """
    check if there are documents in a specific index
    """
    response = ES.indices.stats(index=index, metric="docs")
    doc_count = response["indices"][index]["total"]["docs"]["count"]
    return bool(doc_count) #TODO: learn what this does?
