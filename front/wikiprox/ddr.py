"""front.ddr -- Links to the DDR through Elasticsearch

from django.conf import settings
from wikiprox import ddr
hosts = settings.DDRPUBLIC_DOCSTORE_HOSTS
index = settings.DDRPUBLIC_DOCSTORE_INDEX
topics = ['Politics', 'Hawai'i']

ddr.search_topics(hosts, index, term=terms)


def search(hosts, index, model='', query='', term={}, filters={}, sort=[], fields=[], first=0, size=MAX_SIZE):
    "" "Run a query, get a list of zero or more hits.
    
    @param hosts: list of dicts containing host information.
    @param index: Name of the target index.
    @param model: Type of object ('articles', 'authors')
    @param query: User's search text
    @param term: dict
    @param filters: dict
    @param sort: list of (fieldname,direction) tuples
    @param fields: str
    @param first: int Index of document from which to start results
    @param size: int Number of results to return
    @returns raw ElasticSearch query output
    "" "

from django.conf import settings
from wikiprox import docstore
hosts = settings.DDRPUBLIC_DOCSTORE_HOSTS
index = settings.DDRPUBLIC_DOCSTORE_INDEX
models = 'collection,entity,file'
terms = {u'topics': u'242'}
terms = {u'topics': ['76', '242']}
terms = {u'topics': u'76'}
fields = ['id', 'title', 'description']
results = docstore.search(hosts, index, model=models, term=terms, fields=fields)
document_ids = [hit['_id'] for hit in results['hits']['hits']]
document_ids
"""

from django.conf import settings

from wikiprox import docstore


def _document_url(document_id):
    """
    http://DOMAIN/REPO/ORG/CID/
    http://DOMAIN/REPO/ORG/CID/EID/
    http://DOMAIN/REPO/ORG/CID/EID/ROLE/SHA1/
    """
    url = '%s/%s/' % (
        settings.DDRPUBLIC_DOCUMENT_URL,
        document_id.replace('-', '/')
    )
    return url

def _img_src(collection_id, signature_file):
    """
    Example:
    http://ddr.densho.org/media/ddr-densho-10/ddr-densho-10-1-mezzanine-c85f8d0f91-a.jpg
    """
    url = '%s/%s/%s-a.jpg' % (
        settings.DDRPUBLIC_MEDIA_URL,
        collection_id,
        signature_file
    )
    return url

def _term_documents(es, index, term_id, size):
    """
    
    @param es: Elasticsearch connection
    @param index: str Elasticsearch index name
    @param term_id: int
    @param size: int Maximum number of results to return.
    """
    # get from Elasticsearch
    doctype = 'entity'
    body = {"query": {"match": {"topics": term_id}}}
    fields = ['id', 'collection_id', 'signature_file', 'title', 'description']
    results = es.search(
        index=index, doc_type=doctype, body=body, fields=fields, size=size
    )
    # turn into nice dicts
    documents = []
    for hit in results['hits']['hits']:
        d = {}
        for key,val in hit['fields'].iteritems():
            # some str fields returned as lists of one item
            if type(val) == type([]):
                d[key] = val[0]
            else:
                d[key] = val
        documents.append(d)
    # make URLs
    for doc in documents:
        doc['url'] = _document_url(doc['id'])
        doc['img_src'] = _img_src(doc['collection_id'], doc['signature_file'])
    return documents

def _balance(results, size):
    """cycle through term IDs taking one at a time until we have enough
    
    @param results: dict of search results keyed to term IDs.
    @param size: int Maximum number of results to return.
    """
    round1 = []
    while(len(round1) < size):
        for tid in results.iterkeys():
            doc = None
            if results[tid]:
                doc = results[tid].pop()
            round1.append(doc)
    # remove empties
    round2 = [doc for doc in round1 if doc]
    return round2

def related_by_topic(hosts, index, term_ids, size, balanced=False):
    """Documents from DDR related to terms.
    
    @param hosts: list of dicts containing host information.
    @param index: str Name of the target index.
    #@param terms: list of Topic keywords.
    @param term_ids: list of Topic term IDs.
    @param size: int Maximum number of results to return.
    """
    es = docstore._get_connection(hosts)
    term_results = {
        tid: _term_documents(es, index, tid, size)
        for tid in term_ids
    }
    if balanced:
        return _balance(term_results, size)
    return term_results
