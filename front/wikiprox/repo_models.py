# Models are defined here and not in encyc.models.elastic in order
# to prevent import looping between that class and encyc.docstore.

from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as dsl


class Author(dsl.Document):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    url_title = dsl.Keyword()  # Elasticsearch id
    public = dsl.Boolean()
    published = dsl.Boolean()
    modified = dsl.Date()
    mw_api_url = dsl.Keyword()
    title_sort = dsl.Keyword()
    title = dsl.Text()
    body = dsl.Text()
    article_titles = dsl.Keyword(multi=True)
    
    #class Index:
    #    name = ???
    # We don't define Index here because this module cannot know anything
    # about the application configs.
    # Instead we specify "index=OBJECT.index_name(model)" to Elasticsearch
    # create_index(), get(), search(), delete(), etc.
    
    class Meta:
        doc_type = 'encycauthor'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.url_title
        )

    def __str__(self):
        return self.title
    
    def __eq__(self, other):
        """Enable Pythonic sorting"""
        return self.title_sort == other.title_sort
    
    def __lt__(self, other):
        """Enable Pythonic sorting"""
        return self.title_sort < other.title_sort


class AuthorData(dsl.InnerDoc):
    display = dsl.Keyword(multi=True)
    parsed = dsl.Keyword(multi=True)
    
class Page(dsl.Document):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    url_title = dsl.Keyword()  # Elasticsearch id
    public = dsl.Boolean()
    published = dsl.Boolean()
    published_encyc = dsl.Boolean()
    published_rg = dsl.Boolean()
    modified = dsl.Date()
    mw_api_url = dsl.Keyword()
    title_sort = dsl.Keyword()
    title = dsl.Text()
    description = dsl.Text()
    body = dsl.Text()
    prev_page = dsl.Keyword()
    next_page = dsl.Keyword()
    categories = dsl.Keyword(multi=True)
    coordinates = dsl.Keyword(multi=True)
    source_ids = dsl.Keyword(multi=True)
    authors_data = dsl.Nested(AuthorData)
    
    # list of strings: ['DATABOX_NAME|dict', 'DATABOX_NAME|dict']
    # dicts are result of json.dumps(dict)
    databoxes = dsl.Keyword(multi=True)
    
    rg_rgmediatype = dsl.Keyword(multi=True)
    rg_title = dsl.Text()
    rg_creators = dsl.Keyword(multi=True)
    rg_interestlevel = dsl.Keyword(multi=True)
    rg_readinglevel = dsl.Keyword(multi=True)
    rg_theme = dsl.Keyword(multi=True)
    rg_genre = dsl.Keyword(multi=True)
    rg_pov = dsl.Keyword(multi=True)
    rg_relatedevents = dsl.Text()
    rg_availability = dsl.Keyword()
    rg_freewebversion = dsl.Keyword()
    rg_denshotopic = dsl.Keyword(multi=True)
    rg_geography = dsl.Keyword(multi=True)
    rg_facility = dsl.Keyword(multi=True)
    rg_chronology = dsl.Keyword(multi=True)
    rg_hasteachingaids = dsl.Keyword()
    rg_warnings = dsl.Text()
    #rg_primarysecondary = dsl.Keyword(multi=True)
    #rg_lexile = dsl.Keyword(multi=True)
    #rg_guidedreadinglevel = dsl.Keyword(multi=True)
    
    #class Index:
    #    name = ???
    # We don't define Index here because this module cannot know anything
    # about the application configs.
    # Instead we specify "index=OBJECT.index_name(model)" to Elasticsearch
    # create_index(), get(), search(), delete(), etc.
    
    class Meta:
        doc_type = 'encycarticle'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.url_title
        )

    def __str__(self):
        return self.title
    
    def __eq__(self, other):
        """Enable Pythonic sorting"""
        return self.title_sort == other.title_sort
    
    def __lt__(self, other):
        """Enable Pythonic sorting"""
        return self.title_sort < other.title_sort


class Source(dsl.Document):
    """
    IMPORTANT: uses Elasticsearch-DSL, not the Django ORM.
    """
    encyclopedia_id = dsl.Keyword()  # Elasticsearch id
    densho_id = dsl.Keyword()
    psms_id = dsl.Keyword()
    psms_api_uri = dsl.Keyword()
    institution_id = dsl.Keyword()
    collection_name = dsl.Keyword()
    created = dsl.Date()
    modified = dsl.Date()
    published = dsl.Boolean()
    creative_commons = dsl.Boolean()
    headword = dsl.Keyword()
    original = dsl.Keyword()
    original_size = dsl.Keyword()
    original_url = dsl.Keyword()
    original_path = dsl.Keyword()
    original_path_abs = dsl.Keyword()
    display = dsl.Keyword()
    display_size = dsl.Keyword()
    display_url = dsl.Keyword()
    display_path = dsl.Keyword()
    display_path_abs = dsl.Keyword()
    #streaming_path = dsl.Keyword()
    #rtmp_path = dsl.Keyword()
    streaming_url = dsl.Keyword()  # TODO remove
    external_url = dsl.Keyword()
    media_format = dsl.Keyword()
    aspect_ratio = dsl.Keyword()
    caption = dsl.Text()
    caption_extended = dsl.Text()
    #transcript_path = dsl.Keyword()
    transcript = dsl.Text()  # TODO remove
    courtesy = dsl.Keyword()
    filename = dsl.Keyword()
    img_path = dsl.Keyword()
    
    #class Index:
    #    name = ???
    # We don't define Index here because this module cannot know anything
    # about the application configs.
    # Instead we specify "index=OBJECT.index_name(model)" to Elasticsearch
    # create_index(), get(), search(), delete(), etc.
    
    class Meta:
        doc_type = 'encycsource'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.encyclopedia_id
        )

    def __str__(self):
        return self.encyclopedia_id
    
    def __eq__(self, other):
        """Enable Pythonic sorting"""
        return self.encyclopedia_id == other.encyclopedia_id
    
    def __lt__(self, other):
        """Enable Pythonic sorting"""
        return self.encyclopedia_id < other.encyclopedia_id


class Facet(dsl.Document):
    id = dsl.Keyword()
    links_html = dsl.Keyword()
    links_json = dsl.Keyword()
    links_children = dsl.Keyword()
    title = dsl.Text()
    description = dsl.Text()
    
    #class Index:
    #    name = ???
    # We don't define Index here because this module cannot know anything
    # about the application configs.
    # Instead we specify "index=OBJECT.index_name(model)" to Elasticsearch
    # create_index(), get(), search(), delete(), etc.
    
    class Meta:
        doc_type = 'encycfacet'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.id
        )


class Elinks(dsl.InnerDoc):
    label = dsl.Text()
    url = dsl.Text()

class Geopoint(dsl.InnerDoc):
    lat = dsl.Double()
    lng = dsl.Double()

class Location(dsl.InnerDoc):
    geopoint = dsl.Nested(Geopoint)
    label = dsl.Text()

class FacetTerm(dsl.Document):
    id = dsl.Keyword()
    facet = dsl.Keyword()
    term_id = dsl.Keyword()
    links_html = dsl.Keyword()
    links_json = dsl.Keyword()
    links_children = dsl.Keyword()
    title = dsl.Text()
    description = dsl.Text()
    # topics
    path = dsl.Text()
    parent_id = dsl.Keyword()
    ancestors = dsl.Long()
    siblings = dsl.Long()
    children = dsl.Long()
    weight = dsl.Long()
    encyc_urls = dsl.Text()
    # facility
    type = dsl.Text()
    elinks = dsl.Nested(Elinks)
    location_geopoint = dsl.Nested(Location)
    
    #class Index:
    #    name = ???
    # We don't define Index here because this module cannot know anything
    # about the application configs.
    # Instead we specify "index=OBJECT.index_name(model)" to Elasticsearch
    # create_index(), get(), search(), delete(), etc.
    
    class Meta:
        doc_type = 'encycfacetterm'
    
    def __repr__(self):
        return '<%s.%s "%s">' % (
            self.__module__,
            self.__class__.__name__,
            self.id
        )
    
    def __eq__(self, other):
        """Enable Pythonic sorting"""
        return self.term_id == other.term_id
    
    def __lt__(self, other):
        """Enable Pythonic sorting"""
        return self.term_id < other.term_id


ELASTICSEARCH_CLASSES = {
    'all': [
        {'doctype': 'author', 'class': Author},
        {'doctype': 'article', 'class': Page},
        {'doctype': 'source', 'class': Source},
        {'doctype': 'facet', 'class': Facet},
        {'doctype': 'facetterm', 'class': FacetTerm},
    ],
}

ELASTICSEARCH_CLASSES_BY_MODEL = {
    'author': Author,
    'article': Page,
    'source': Source,
    'facet': Facet,
    'facetterm': FacetTerm,
}

MODEL_REPO_MODELS = {
    'segment': {'as': 'segmentmodule', 'class': 'segment', 'module': 'repo_models.segment'},
    'collection': {'as': 'collectionmodule', 'class': 'collection', 'module': 'repo_models.collection'},
    'file': {'as': 'filemodule', 'class': 'file', 'module': 'repo_models.files'},
    'entity': {'as': 'entitymodule', 'class': 'entity', 'module': 'repo_models.entity'},
}
