import json
import logging
logger = logging.getLogger(__name__)
import os

from elasticsearch import Elasticsearch, TransportError
from elasticsearch.client import SnapshotClient
import elasticsearch_dsl

from django.conf import settings

from .repo_models import ELASTICSEARCH_CLASSES
from .repo_models import ELASTICSEARCH_CLASSES_BY_MODEL
from .repo_models import MODEL_REPO_MODELS

INDEX_PREFIX = 'encyc'

MAX_SIZE = 10000
DEFAULT_PAGE_SIZE = 20

SUCCESS_STATUSES = [200, 201]


class Docstore():

    def __init__(self, hosts=settings.DOCSTORE_HOST, connection=None):
        self.hosts = hosts
        if connection:
            self.es = connection
        else:
            self.es = Elasticsearch(hosts, timeout=settings.DOCSTORE_TIMEOUT)
    
    def index_name(self, model):
        return '{}{}'.format(INDEX_PREFIX, model)
    
    def __repr__(self):
        return "<%s.%s %s:%s*>" % (
            self.__module__, self.__class__.__name__, self.hosts, INDEX_PREFIX
        )
    
    def print_configs(self):
        print('CONFIG_FILES:           %s' % settings.CONFIG_FILES)
        print('')
        print('DOCSTORE_HOST:          %s' % settings.DOCSTORE_HOST)
        print('')
    
    def health(self):
        return self.es.cluster.health()
    
    def start_test(self):
        try:
            self.es.cluster.health()
        except TransportError:
            logger.critical('Elasticsearch cluster unavailable')
            print('CRITICAL: Elasticsearch cluster unavailable')
            sys.exit(1)
    
    def index_exists(self, indexname):
        """
        """
        return self.es.indices.exists(index=indexname)
    
    def status(self):
        """Returns status information from the Elasticsearch cluster.
        
        >>> docstore.Docstore().status()
        {
            u'indices': {
                u'ddrpublic-dev': {
                    u'total': {
                        u'store': {
                            u'size_in_bytes': 4438191,
                            u'throttle_time_in_millis': 0
                        },
                        u'docs': {
                            u'max_doc': 2664,
                            u'num_docs': 2504,
                            u'deleted_docs': 160
                        },
                        ...
                    },
                    ...
                }
            },
            ...
        }
        """
        return self.es.indices.stats()
    
    def index_names(self):
        """Returns list of index names
        """
        return [name for name in self.status()['indices'].keys()]
     
    def exists(self, model, document_id):
        """
        @param model:
        @param document_id:
        """
        return self.es.exists(
            index=self.index_name(model),
            id=document_id
        )
    
    def get(self, model, document_id, fields=None):
        """Get a single document by its id.
        
        @param model:
        @param document_id:
        @param fields: boolean Only return these fields
        @returns: repo_models.elastic.ESObject or None
        """
        ES_Class = ELASTICSEARCH_CLASSES_BY_MODEL[model]
        return ES_Class.get(
            id=document_id,
            index=self.index_name(model),
            using=self.es,
            ignore=404,
        )

    def count(self, doctypes=[], query={}):
        """Executes a query and returns number of hits.
        
        The "query" arg must be a dict that conforms to the Elasticsearch query DSL.
        See docstore.search_query for more info.
        
        @param doctypes: list Type of object ('collection', 'entity', 'file')
        @param query: dict The search definition using Elasticsearch Query DSL
        @returns raw ElasticSearch query output
        """
        logger.debug('count(doctypes=%s, query=%s' % (doctypes, query))
        if not query:
            raise Exception(
                "Can't do an empty search. Give me something to work with here."
            )
        
        indices = ','.join(
            ['{}{}'.format(INDEX_PREFIX, m) for m in doctypes]
        )
        doctypes = ','.join(doctypes)
        logger.debug(json.dumps(query))
        
        return self.es.count(
            index=indices,
            body=query,
        )

    def search(self, doctypes=[], query={}, sort=[], fields=[], from_=0, size=MAX_SIZE):
        """Executes a query, get a list of zero or more hits.
        
        The "query" arg must be a dict that conforms to the Elasticsearch query DSL.
        See docstore.search_query for more info.
        
        @param doctypes: list Type of object ('collection', 'entity', 'file')
        @param query: dict The search definition using Elasticsearch Query DSL
        @param sort: list of (fieldname,direction) tuples
        @param fields: str
        @param from_: int Index of document from which to start results
        @param size: int Number of results to return
        @returns raw ElasticSearch query output
        """
        logger.debug(
            'search(doctypes=%s, query=%s, sort=%s, fields=%s, from_=%s, size=%s' % (
                doctypes, query, sort, fields, from_, size
        ))
        if not query:
            raise Exception(
                "Can't do an empty search. Give me something to work with here."
            )
        
        indices = ','.join(
            ['{}{}'.format(INDEX_PREFIX, m) for m in doctypes]
        )
        doctypes = ','.join(doctypes)
        logger.debug(json.dumps(query))
        _clean_dict(sort)
        sort_cleaned = _clean_sort(sort)
        fields = ','.join(fields)

        results = self.es.search(
            index=indices,
            body=query,
            #sort=sort_cleaned,  # TODO figure out sorting
            from_=from_,
            size=size,
            #_source_include=fields,  # TODO figure out fields
        )
        return results


def make_index_name(text):
    """Takes input text and generates a legal Elasticsearch index name.
    
    I can't find documentation of what constitutes a legal ES index name,
    but index names must work in URLs so we'll say alnum plus _, ., and -.
    
    @param text
    @returns name
    """
    LEGAL_NONALNUM_CHARS = ['-', '_', '.']
    SEPARATORS = ['/', '\\',]
    name = []
    if text:
        text = os.path.normpath(text)
        for n,char in enumerate(text):
            if char in SEPARATORS:
                char = '-'
            if n and (char.isalnum() or (char in LEGAL_NONALNUM_CHARS)):
                name.append(char.lower())
            elif char.isalnum():
                name.append(char.lower())
    return ''.join(name)

def doctype_fields(es_class):
    """List content fields in DocType subclass (i.e. appear in _source).
    
    TODO move to ddr-cmdln
    """
    return es_class._doc_type.mapping.to_dict()['properties'].keys()

def _clean_dict(data):
    """Remove null or empty fields; ElasticSearch chokes on them.
    
    >>> d = {'a': 'abc', 'b': 'bcd', 'x':'' }
    >>> _clean_dict(d)
    >>> d
    {'a': 'abc', 'b': 'bcd'}
    
    @param data: Standard DDR list-of-dicts data structure.
    """
    if data and isinstance(data, dict):
        for key in data.keys():
            if not data[key]:
                del(data[key])

def _clean_sort( sort ):
    """Take list of [a,b] lists, return comma-separated list of a:b pairs
    
    >>> _clean_sort( 'whatever' )
    >>> _clean_sort( [['a', 'asc'], ['b', 'asc'], 'whatever'] )
    >>> _clean_sort( [['a', 'asc'], ['b', 'asc']] )
    'a:asc,b:asc'
    """
    cleaned = ''
    if sort and isinstance(sort,list):
        all_lists = [1 if isinstance(x, list) else 0 for x in sort]
        if not 0 in all_lists:
            cleaned = ','.join([':'.join(x) for x in sort])
    return cleaned
        
def publishable(page, force=False):
    """Determines which paths represent publishable paths and which do not.
    
    @param page
    @returns list of dicts, e.g. [{'path':'/PATH/TO/OBJECT', 'action':'publish'}]
    """
    pass

def aggs_dict(aggregations):
    """Simplify aggregations data in search results
    
    input
    {
        u'format': {
            u'buckets': [{u'doc_count': 2, u'key': u'ds'}],
            u'doc_count_error_upper_bound': 0,
            u'sum_other_doc_count': 0
        },
        u'rights': {
            u'buckets': [{u'doc_count': 3, u'key': u'cc'}],
            u'doc_count_error_upper_bound': 0, u'sum_other_doc_count': 0
        },
    }
    output
    {
        u'format': {u'ds': 2},
        u'rights': {u'cc': 3},
    }
    """
    return {
        fieldname: {
            bucket['key']: bucket['doc_count']
            for bucket in data['buckets']
        }
        for fieldname,data in aggregations.items()
    }

def search_query(text='', must=[], should=[], mustnot=[], aggs={}):
    pass
