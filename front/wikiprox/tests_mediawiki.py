from bs4 import BeautifulSoup, SoupStrainer, Comment

import mediawiki



def _runsoup(function, text):
    """Load text into BeautifulSoup, run function on it, dump to HTML, return result
    """
    soup0 = BeautifulSoup(text, 'html.parser')
    soup1 = function(soup0)
    return mediawiki.rm_tags(unicode(soup1))


def test_page_data_url():
    api_url = 'http://example.com'
    page_title = 'Testing'
    out = 'http://example.com?action=parse&format=json&page=Testing'
    assert mediawiki.page_data_url(api_url, page_title) == out

def test_lastmod_data_url():
    api_url = 'http://example.com'
    page_title = 'Testing'
    out = 'http://example.com?action=query&format=json&prop=revisions&rvprop=ids|timestamp&titles=Testing'
    assert mediawiki.lastmod_data_url(api_url, page_title) == out

def test_page_is_published():
    pagedata0 = {
        'parse': {
            'categories': [
                {u'hidden': u'', u'*': u'Published', u'sortkey': u''},
                {u'*': u'Camps', u'sortkey': u''},
            ]
        }
    }
    pagedata1 = {
        'parse': {
            'categories': [
                {u'*': u'Camps', u'sortkey': u''},
            ]
        }
    }
    assert mediawiki.page_is_published(pagedata0) == True
    assert mediawiki.page_is_published(pagedata1) == False


# page_lastmod
# parse_mediawiki_text


RM_STATICPAGE_TITLES_in0 = """<p>BEFORE</p>
<h1>HEADER</h1>
<p>AFTER</p>"""

RM_STATICPAGE_TITLES_out0 = """<p>BEFORE</p>

<p>AFTER</p>"""

def test_remove_staticpage_titles():
    assert _runsoup(
        mediawiki.remove_staticpage_titles, RM_STATICPAGE_TITLES_in0
    ) == RM_STATICPAGE_TITLES_out0


def test_remove_comments():
    # doesn't do anything right now
    pass


RM_EDIT_LINKS_in0 = """<p>BEFORE</p>
<h2>HEADER<span class="mw-editsection">...</span></h2>
<p>AFTER</p>"""

RM_EDIT_LINKS_out0 = """<p>BEFORE</p>
<h2>HEADER</h2>
<p>AFTER</p>"""

def test_remove_edit_links():
    assert _runsoup(
        mediawiki.remove_edit_links, RM_EDIT_LINKS_in0
    ) == RM_EDIT_LINKS_out0


WRAP_SECTIONS_in0 = """<p>BEFORE</p>
<h2><span class="mw-headline">HEADER0</span></h2>
<p>blah blah blah</p>
<p>blah blah blah</p>
<h2><span class="mw-headline">HEADER1</span></h2>
<p>blah blah blah</p>
<p>blah blah blah</p>
<h2><span class="mw-headline">HEADER2</span></h2>
<p>blah blah blah</p>
<p>blah blah blah</p>
<h2>HEADER2</h2>
<p>AFTER</p>"""

WRAP_SECTIONS_out0 = """<p>BEFORE</p>
<div class="section"><h2><span class="mw-headline">HEADER0</span></h2><div class="section_content">
<p>blah blah blah</p>
<p>blah blah blah</p>
</div></div><div class="section"><h2><span class="mw-headline">HEADER1</span></h2><div class="section_content">
<p>blah blah blah</p>
<p>blah blah blah</p>
</div></div><div class="section"><h2><span class="mw-headline">HEADER2</span></h2><div class="section_content">
<p>blah blah blah</p>
<p>blah blah blah</p>
</div></div><h2>HEADER2</h2>
<p>AFTER</p>"""

def test_wrap_sections():
    assert _runsoup(
        mediawiki.wrap_sections, WRAP_SECTIONS_in0
    ) == WRAP_SECTIONS_out0


RM_STATUS_MARKERS_in0 = """<p>BEFORE</p>
<div class="alert alert-success published">
<p>This page is complete and will be published to the production Encyclopedia.</p>
</div>
<p>AFTER</p>"""

RM_STATUS_MARKERS_out0 = """<p>BEFORE</p>

<p>AFTER</p>"""

def test_remove_status_markers():
    assert _runsoup(
        mediawiki.remove_status_markers, RM_STATUS_MARKERS_in0
    ) == RM_STATUS_MARKERS_out0

def test_rewrite_mediawiki_urls():
    in0 = """<a href="http://example.com/mediawiki/index.php/Page Title">Page Title</a>"""
    in1 = """<a href="http://example.com/mediawiki/Page Title">Page Title</a>"""
    in2 = """<a href="http://example.com/Page Title">Page Title</a>"""
    out = """<a href="http://example.com/Page Title">Page Title</a>"""
    assert mediawiki.rewrite_mediawiki_urls(in0) == out
    assert mediawiki.rewrite_mediawiki_urls(in1) == out
    assert mediawiki.rewrite_mediawiki_urls(in2) == out

def test_rewrite_newpage_links():
    in0 = '<a href="http://.../mediawiki/index.php?title=Nisei&amp;action=edit&amp;redlink=1">LINK</a>'
    out0 = '<a href="http://.../mediawiki/index.php/Nisei">LINK</a>'
    assert _runsoup(mediawiki.rewrite_newpage_links, in0) == out0
    
def test_rewrite_prevnext_links():
    in0 = '<a href="http://.../mediawiki/index.php?title=Test_Page&pagefrom=Another+Page">LINK</a>'
    in1 = '<a href="http://.../mediawiki/index.php?title=Test_Page&pageuntil=Another+Page">LINK</a>'
    out0 = '<a href="http://.../mediawiki/index.php/Test_Page?pagefrom=Another+Page">LINK</a>'
    out1 = '<a href="http://.../mediawiki/index.php/Test_Page?pageuntil=Another+Page">LINK</a>'
    assert _runsoup(mediawiki.rewrite_prevnext_links, in0) == out0
    assert _runsoup(mediawiki.rewrite_prevnext_links, in1) == out1

def test_extract_encyclopedia_id():
    in0 = 'en-denshopd-i37-00239-1.jpg'
    in1 = '/mediawiki/images/thumb/a/a1/en-denshopd-i37-00239-1.jpg/200px-en-denshopd-i37-00239-1.jpg'
    in2 = 'en-denshovh-ffrank-01-0025-1.jpg'
    in3 = '/mediawiki/images/thumb/8/86/en-denshovh-ffrank-01-0025-1.jpg/200px-en-denshovh-ffrank-01-0025-1.jpg'
    out0 = 'en-denshopd-i37-00239-1'
    out1 = 'en-denshopd-i37-00239-1'
    out2 = 'en-denshovh-ffrank-01-0025-1'
    out3 = 'en-denshovh-ffrank-01-0025-1'
    assert mediawiki.extract_encyclopedia_id(in0) == out0
    assert mediawiki.extract_encyclopedia_id(in1) == out1
    assert mediawiki.extract_encyclopedia_id(in2) == out2
    assert mediawiki.extract_encyclopedia_id(in3) == out3
    
## find_primary_sources


RM_PRIMARY_SOURCES_in0 = """<p>BEFORE</p>
<div><a href="/mediawiki/File:en-denshopd-i37-00239-1.jpg" class="image"><img src="/mediawiki/images/thumb/a/a1/en-denshopd-i37-00239-1.jpg/200px-en-denshopd-i37-00239-1.jpg"  /></a></div>
<div><a href="/mediawiki/File:en-denshovh-ffrank-01-0025-1.jpg" class="image"><img src="/mediawiki/images/thumb/8/86/en-denshovh-ffrank-01-0025-1.jpg/200px-en-denshovh-ffrank-01-0025-1.jpg" /></a></div>
<p>AFTER</p>"""

RM_PRIMARY_SOURCES_out0 = """<p>BEFORE</p>
<div></div>
<div></div>
<p>AFTER</p>"""

def test_remove_primary_sources():
    sources0 = [
        {'encyclopedia_id': 'en-denshopd-i37-00239-1'},
        {'encyclopedia_id': 'en-denshovh-ffrank-01-0025-1'},
    ]
    soup0 = BeautifulSoup(RM_PRIMARY_SOURCES_in0, 'html.parser')
    soup0 = mediawiki.remove_primary_sources(soup0, sources0)
    result0 = mediawiki.rm_tags(unicode(soup0))
    assert result0 == RM_PRIMARY_SOURCES_out0


FIND_DATABOXCAMPS_COORDS_in0 = """
Just some random text that contains no coordinates
"""
FIND_DATABOXCAMPS_COORDS_in1 = """
<div id="databox-Camps">
<p>
SoSUID: w-tule;
DenshoName: Tule Lake;
USGName: Tule Lake Relocation Center;
GISLat: 41.8833;
GISLng: -121.3667;
GISTGNId: 2012922;
</p>
</div>
"""

def test_find_databoxcamps_coordinates():
    out0a = (); out0b = []
    out1a = (-121.3667, 41.8833); out1b = [-121.3667, 41.8833]
    # TODO test for multiple coordinates on page
    assert mediawiki.find_databoxcamps_coordinates(
        FIND_DATABOXCAMPS_COORDS_in0
    ) in [out0a, out0b]
    assert mediawiki.find_databoxcamps_coordinates(
        FIND_DATABOXCAMPS_COORDS_in1
    ) in [out1a, out1b]


ADD_TOP_LINKS_in0 = """
<p>PARAGRAPH0</p>
<h2>HEADER1</h2>
<p>PARAGRAPH1</p>
<h2>HEADER2</h2>
<p>PARAGRAPH2</p>
<h2>HEADER3</h2>
<p>PARAGRAPH3</p>
"""
ADD_TOP_LINKS_out0 = """<p>PARAGRAPH0</p>
<h2>HEADER1</h2>
<p>PARAGRAPH1</p>
<h2>HEADER2</h2>
<p>PARAGRAPH2</p>
<div class="toplink"><a href="#top"><i class="icon-chevron-up"></i> Top</a></div><h2>HEADER3</h2>
<p>PARAGRAPH3</p><div class="toplink"><a href="#top"><i class="icon-chevron-up"></i> Top</a></div>"""

def test_add_top_links():
    assert _runsoup(
        mediawiki.add_top_links, ADD_TOP_LINKS_in0
    ) == ADD_TOP_LINKS_out0


FIND_AUTHOR_INFO_in0 = """
<div id="authorByline">
  <b>
    Authored by
    <a href="/Tom_Coffman" title="Tom Coffman">Tom Coffman</a>
  </b>
</div>
<div id="citationAuthor" style="display:none;">
  Coffman, Tom
</div>
"""
FIND_AUTHOR_INFO_in1 = """
<div id="authorByline">
  <b>
    Authored by
    <a href="/mediawiki/index.php/Jane_L._Scheiber" title="Jane L. Scheiber">Jane L. Scheiber</a>
    and
    <a href="/mediawiki/index.php/Harry_N._Scheiber" title="Harry N. Scheiber">Harry N. Scheiber</a>
  </b>
</div>
<div id="citationAuthor" style="display:none;">
  Scheiber,Jane; Scheiber,Harry
</div>
"""

def test_find_author_info():
    out0 = {
        'display': [u'Tom Coffman'],
        'parsed': [[u'Coffman', u'Tom']]
    }
    out1 = {
        'display': [u'Jane L. Scheiber', u'Harry N. Scheiber'],
        'parsed': [[u'Scheiber', u'Jane'], [u'Scheiber', u'Harry']]
    }
    assert mediawiki.find_author_info(FIND_AUTHOR_INFO_in0) == out0
    assert mediawiki.find_author_info(FIND_AUTHOR_INFO_in1) == out1

def test_rm_tags():
    in0 = """<html><body><p>Some text here.</p></body></html>"""
    out0 = """<p>Some text here.</p>"""
    assert mediawiki.rm_tags(in0) == out0
