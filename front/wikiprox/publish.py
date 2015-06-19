"""
Tools for pre-rendering MediaWiki pages and saving them to Elasticsearch.
This should use the same rendering code as encyc-front views do.

Gets list of pages from MediaWiki.
Get data from API
Render HTML
Construct JSON with facets and other metadata
POST to Elasticsearch.
Get-from-API step should compare last-mod time between MW and Elasticsearch and only POST if changed.

example walkthrough:
------------------------------------------------------------------------

HOSTS = [{'host':'192.168.56.101', 'port':9200}]
INDEX = 'devencyc'

from wikiprox import elastic

elastic.delete_index(HOSTS, INDEX)
elastic.create_index(HOSTS, INDEX)

elastic.put_mappings(HOSTS, INDEX, MAPPINGS)
elastic.put_facets(HOSTS, INDEX, FACETS)

elastic.delete(HOSTS, INDEX, document_id)

elastic.post(HOSTS, INDEX, document_id, document)

index_authors()
index_categories()
index_contents()
index_page()
- include cite
index_source()
- include cite


------------------------------------------------------------------------
"""

DOCSTORE_HOSTS = [
    {'host':'192.168.56.101', 'port':9200}
]
DOCSTORE_INDEX = 'devencyc'


def index_authors():
    """
    """
    pass

def index_categories():
    """
    """
    pass

def index_contents():
    """
    """
    pass

def index_page():
    """
    TODO include cite
    """
    pass

def index_source():
    """
    TODO include cite
    """
    pass

