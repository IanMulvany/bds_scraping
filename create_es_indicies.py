from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from elasticsearch import Elasticsearch
from simple_settings import settings

cursor_index = settings.CURSOR_INDEX
crossref_index = settings.CROSSREF_INDEX
doi_queue = settings.DOI_QUEUE
es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

def create_es_index(indexname, mapping):
    exist = es.indices.exists(indexname)
    if not exist:
        es.indices.create(index=indexname, body=mapping)

def delete_es_index(indexname):
    es.indices.delete(index=indexname)

def create_cursor_index(indexname):
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
    create_es_index(indexname, request_body)

def create_doi_queue_index(indexname):
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
    create_es_index(indexname, request_body)

def create_crossref_index(indexname):
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
    create_es_index(indexname, request_body)

if __name__ == "__main__":
    create_crossref_index(crossref_index)
    create_doi_queue_index(doi_queue)
    create_cursor_index(cursor_index)
