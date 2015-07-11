import json

import encyclopedia


# api_login_round1()
# api_login_round2()
# api_login()
# api_logout()

def test__all_pages():
    r_text = {
        'query': {
            'pages': {
                '1': {'pageid': 1, 'revisions': [{'timestamp': '2014-04-01T23:57:21Z'}], 'title': 'Page 1'},
                '2': {'pageid': 2, 'revisions': [{'timestamp': '2014-04-01T23:57:21Z'}], 'title': 'Page 2'},
                '3': {'pageid': 3, 'revisions': [{'timestamp': '2014-04-01T23:57:21Z'}], 'title': 'Page 3'},
            }
        }
    }
    expected = [
        {'timestamp': '2014-04-01T23:57:21Z', 'pageid': 1, 'title': 'Page 1'},
        {'timestamp': '2014-04-01T23:57:21Z', 'pageid': 3, 'title': 'Page 3'},
        {'timestamp': '2014-04-01T23:57:21Z', 'pageid': 2, 'title': 'Page 2'},
    ]
    assert encyclopedia._all_pages(json.dumps(r_text)) == expected

# all_pages()

def test__articles_a_z():
    published_pages = [
        # these will be accepted
        {'pageid': 1, 'sortkey': u'page 1', u'title': u'Page 1'},
        {'pageid': 2, 'sortkey': u'page 2', u'title': u'Page 2'},
        {'pageid': 3, 'sortkey': u'page 3', u'title': u'Page 3'},
        # the rest will be filtered out
        {'pageid': 4, 'sortkey': u'about', u'title': u'about'},
        {'pageid': 5, 'sortkey': u'author 1', u'title': u'Author 1'},
        {'pageid': 6, 'sortkey': u'author 2', u'title': u'Author 2'},
        {'pageid': 7, 'sortkey': u'author 3', u'title': u'Author 3'},
        {'pageid': 8, 'sortkey': u'categories', u'title': u'categories'},
        {'pageid': 9, 'sortkey': u'category:something', u'title': u'Category:Something'},
    ]
    author_pages = [
        {'pageid': 5, 'sortkey': u'author 1', u'title': u'Author 1'},
        {'pageid': 6, 'sortkey': u'author 2', u'title': u'Author 2'},
        {'pageid': 7, 'sortkey': u'author 3', u'title': u'Author 3'},
    ]
    non_article_pages = [
        'about',
        'categories',
    ]
    expected = [
        {'pageid': 1, 'sortkey': u'page 1', u'title': u'Page 1'},
        {'pageid': 2, 'sortkey': u'page 2', u'title': u'Page 2'},
        {'pageid': 3, 'sortkey': u'page 3', u'title': u'Page 3'},
    ]
    assert encyclopedia._articles_a_z(
        published_pages, author_pages, non_article_pages
    ) == expected

# articles_a_z()
# articles_by_category()
# article_next()
# article_prev()
# author_articles()

def test__category_members():
    r_text = {
        'query': {
            'categorymembers': [
                {'pageid': 437, 'title': 'Page 1', 'sortkeyprefix': ''},
                {'pageid': 439, 'title': 'Page 2', 'sortkeyprefix': ''},
                {'pageid': 440, 'title': 'Page 3', 'sortkeyprefix': ''},
            ]
        }
    }
    expected = [
        {'pageid': 437, 'sortkey': 'page 1', 'title': 'Page 1'},
        {'pageid': 439, 'sortkey': 'page 2', 'title': 'Page 2'},
        {'pageid': 440, 'sortkey': 'page 3', 'title': 'Page 3'},
    ]
    assert encyclopedia._category_members(json.dumps(r_text)) == expected

# category_members()
# category_article_types()
# category_authors()
# category_supplemental()
# is_article()
# is_author()

def test__namespaces():
    r_text = {
        'query': {
            'namespaces': {
                '1': {'id': 1, '*': 'Namespace1', 'canonical': 'Namespace1'},
                '2': {'id': 2, '*': 'Namespace2', 'content': 'Namespace2'},
                '3': {'id': 3, '*': '', 'content': ''},
            },
        }
    }
    expected = {
        1: 'Namespace1',
        2: 'Namespace2',
        3: 'Default',
    }
    assert encyclopedia._namespaces(json.dumps(r_text)) == expected
    

# namespaces()

#def test_namespaces_reversed():
#    assert False

def test__page_categories():
    whitelist = [
        {'title': 'Category 1'},
        {'title': 'Category 2'},
        {'title': 'Category 3'},
        {'title': 'Category 4'},
    ]
    r_text = {
        "query":{
            "pages":{
                '1': {
                    'categories': [
                        {'title': 'Category 1'},
                        {'title': 'Category 2'}
                    ]
                },
                '2': {
                    'categories': [
                        {'title': 'Category 4'}
                    ]
                },
            }
        }
    }
    expected = [u'Category 1', u'Category 2', u'Category 4']
    assert encyclopedia._page_categories(
        whitelist, json.dumps(r_text)
    ) == expected

# page_categories()

def test__published_pages():
    allpages = [
        {'pageid': 1, 'title': 'Page 1', 'revisions':[{'timestamp':'ts'}]},
        {'pageid': 2, 'title': 'Page 2', 'revisions':[{'timestamp':'ts'}]},
        {'pageid': 3, 'title': 'Page 3', 'revisions':[{'timestamp':'ts'}]},
    ]
    all_published_pages = [
        {'pageid': 1, 'title': 'Page 1'},
        {'pageid': 3, 'title': 'Page 3'},
    ]
    expected = [
        {'pageid': 1, 'title': 'Page 1', 'timestamp':'ts', 'revisions':[{'timestamp':'ts'}]},
        {'pageid': 3, 'title': 'Page 3', 'timestamp':'ts', 'revisions':[{'timestamp':'ts'}]},
    ]
    assert encyclopedia._published_pages(
        allpages, all_published_pages
    ) == expected

# published_pages()

def test__published_authors():
    publishedpages = [
        {'title': 'Page 1'},
        {'title': 'Page 2'},
        {'title': 'Page 3'},
    ]
    categoryauthors = [
        {'title': 'Page 1'},
        {'title': 'Page 3'},
        {'title': 'Page 4'},
    ]
    expected = [
        {'title': 'Page 1'},
        {'title': 'Page 3'},
    ]
    assert encyclopedia._published_authors(
        publishedpages, categoryauthors
    ) == expected

# published_authors()

def test__whatlinkshere():
    publishedpages = [
        {'title': 'Page 1'},
        {'title': 'Page 2'},
    ]
    r_text = {
        "query":{
            "backlinks":[
                {"title":"Page 1"},
                {"title":"Page 2"},
                {"title":"Page 3"}
            ]
        }
    }
    expected = ['Page 1', 'Page 2']
    assert encyclopedia._whatlinkshere(
        publishedpages, json.dumps(r_text)
    ) == expected

# what_links_here()
