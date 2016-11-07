from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from elasticsearch import Elasticsearch
import settings as settings

cursor_index = settings.CURSOR_INDEX
crossref_index = settings.CROSSREF_INDEX
doi_queue = settings.DOI_QUEUE
es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

def create_es_index(indexname, mapping):
    exist = es.indices.exists(indexname)
    if not exist:
        es.indices.create(index=indexname, body=request_body)

request_body = {
        'mappings': {
            'doi_queue': {
                  "_timestamp":{
                    "enabled": "true"
                  },
                'properties': {
                    'issn': {'index': 'not_analyzed', 'type': 'string'},
                    'doi': {'index': 'not_analyzed', 'type': 'string'}
                }}}
    }
indexname = doi_queue
create_es_index(indexname, request_body)

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
indexname = cursor_index
create_es_index(indexname, request_body)

request_body = {
        'mappings': {
            'crossref_md': {
                  "_timestamp":{
                    "enabled": "true"
                  },
                'properties': {
                    'DOI': {'index': 'not_analyzed', 'type': 'string'},
                    'URL': {'index': 'not_analyzed', 'type': 'string'},
                    'fulltext': {'index': 'not_analyzed', 'type': 'string'},
                    'author': {'index': 'not_analyzed', 'type': 'string'},
                    'title': {'index': 'analyzed', 'type': 'string'},
                    'ISSN': {'index': 'not_analyzed', 'type': 'string'},
                    'pub_date': {'index': 'not_analyzed', 'format': 'dateOptionalTime', 'type': 'date'}
                }}}
    }
indexname = crossref_index
create_es_index(indexname, request_body)