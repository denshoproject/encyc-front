def surname_givenname(parsed):
    return ', '.join(parsed)
def givenname_surname(parsed):
    parsed.reverse()
    return ' '.join(parsed)
def surname_initials(parsed):
    givens = ['{}.'.format(g[0]) for g in parsed[1].split(' ')]
    givens = ' '.join(givens)
    surname = parsed[0]
    return ', '.join([surname, givens])
def surname_initials_cse(parsed):
    """no comma or period"""
    givens = [g[0] for g in parsed[1].split(' ')]
    givens = ' '.join(givens)
    surname = parsed[0]
    return ' '.join([surname, givens])

def format_authors_apa(authors):
    """Takes output of mediawiki.find_author_info() and formats in APA style.
    
    >>> a = [[u'Scheiber', u'Jane']]
    >>> b = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry']]
    >>> c = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead']]
    >>> d = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead'], [u'Doe',u'John']]
    >>> format_authors_mla(a)
    Scheiber, J.
    >>> format_authors_mla(b)
    Scheiber, J., & Scheiber, H.
    >>> format_authors_mla(c)
    Scheiber, J., Scheiber, H., & Endo, K. B.
    >>> format_authors_mla(d)
    Scheiber, J., Scheiber, H., Endo, K. B., & Doe, J.
    
    source: http://www.umuc.edu/library/libhow/mla_examples.cfm
    """
    cite = ''
    if authors:
        if len(authors) == 1:
            # Scheiber, J.
            cite = surname_givenname(authors[0])
        elif len(authors) > 1:
            # Scheiber, J., & Scheiber, H.
            # Scheiber, J., Scheiber, H., & Endo, K. B.
            # Scheiber, J., Scheiber, H., Endo, K. B., & Doe, J.
            names = []
            [names.append(surname_initials(n)) for n in authors]
            # last two names separated by ampersand
            last = names.pop()
            names.append('') # to add that last comma
            commas = ', '.join(names) # there will be a space after last comma
            cite = '&amp; '.join([ commas, last ])
        if cite and not (cite[-1] == '.'):
            cite = '{}.'.format(cite)
    return cite

def format_authors_chicago(authors):
    """Takes output of mediawiki.find_author_info() and formats Chicago style.
    
    >>> a = [[u'Scheiber', u'Jane']]
    >>> b = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry']]
    >>> c = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead']]
    >>> d = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead'], [u'Doe',u'John']]
    >>> format_authors_chicago(a)
    Jane Scheiber.
    >>> format_authors_chicago(b)
    Jane Scheiber and Harry Scheiber.
    >>> format_authors_chicago(c)
    Jane Scheiber, Harry Scheiber and Kenny Butthead Endo.
    >>> format_authors_chicago(d)
    Jane Scheiber et al.
    
    source: http://ilrb.cf.ac.uk/citingreferences/mhra/page13.html
    """
    cite = ''
    if authors:
        if len(authors) == 1:
            # Jane Scheiber.
            cite = givenname_surname(authors[0])
        elif len(authors) < 4:
            # Jane Scheiber and Harry Scheiber.
            # Jane Scheiber, Harry Scheiber and Kenny Butthead Endo.
            names = []
            [names.append(givenname_surname(n)) for n in authors]
            # last two names separated by 'and'
            last = names.pop()
            commas = ', '.join(names) # there will be a space after last comma
            cite = ' and '.join([ commas, last ])
        elif len(authors) >= 4:
            # Jane Scheiber et al.
            cite = '{} et al'.format(givenname_surname(authors[0]))
        if cite and not (cite[-1] == '.'):
            cite = '{}.'.format(cite)
    return cite

def format_authors_cse(authors):
    """Takes output of mediawiki.find_author_info() and formats CSE/CBE style.
    
    >>> a = [[u'Scheiber', u'Jane']]
    >>> b = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry']]
    >>> c = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead']]
    >>> d = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead'], [u'Doe',u'John']]
    >>> format_authors_chicago(a)
    Scheiber J.
    >>> format_authors_chicago(b)
    Scheiber J, Scheiber H.
    >>> format_authors_chicago(c)
    Scheiber J, Scheiber H, Endo K B.
    >>> format_authors_chicago(d)
    Scheiber J, Scheiber H, Endo K B, Doe J.
    
    source: http://ilrb.cf.ac.uk/citingreferences/mhra/page13.html
    """
    cite = ''
    if authors:
        if len(authors):
            # Scheiber J.
            # Scheiber J, Scheiber H.
            # Scheiber J, Scheiber H, Endo K B.
            # Scheiber J, Scheiber H, Endo K B, Doe J.
            names = []
            [names.append(surname_initials_cse(n)) for n in authors]
            # last two names separated by ampersand
            cite = ', '.join(names)
        if cite and not (cite[-1] == '.'):
            cite = '{}.'.format(cite)
    return cite

def format_authors_mhra(authors):
    """Takes output of mediawiki.find_author_info() and formats MHRA style.
    
    >>> a = [[u'Scheiber', u'Jane']]
    >>> b = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry']]
    >>> c = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead']]
    >>> d = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead'], [u'Doe',u'John']]
    >>> format_authors_mhra(a)
    Jane Scheiber.
    >>> format_authors_mhra(b)
    Jane Scheiber and Harry Scheiber.
    >>> format_authors_mhra(c)
    Jane Scheiber, Harry Scheiber, and Kenny Butthead Endo.
    >>> format_authors_mhra(d)
    Jane Scheiber and others.
    
    source: http://ilrb.cf.ac.uk/citingreferences/mhra/page13.html
    """
    cite = ''
    if authors:
        if len(authors) == 1:
            # Jane Scheiber.
            cite = givenname_surname(authors[0])
        elif len(authors) < 4:
            # Jane Scheiber and Harry Scheiber.
            # Jane Scheiber, Harry Scheiber, and Kenny Butthead Endo.
            names = []
            [names.append(givenname_surname(n)) for n in authors]
            # last two names separated by 'and'
            last = names.pop()
            commas = ', '.join(names) # there will be a space after last comma
            cite = ' and '.join([ commas, last ])
        elif len(authors) >= 4:
            # Jane Scheiber and others.
            cite = '{} and others'.format(givenname_surname(authors[0]))
        if cite and not (cite[-1] == '.'):
            cite = '{}.'.format(cite)
    return cite

def format_authors_mla(authors):
    """Takes output of mediawiki.find_author_info() and formats MLA style.
    
    >>> a = [[u'Scheiber', u'Jane']]
    >>> b = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry']]
    >>> c = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead']]
    >>> d = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead'], [u'Doe',u'John']]
    >>> format_authors_mla(a)
    Scheiber, Jane.
    >>> format_authors_mla(b)
    Scheiber, Jane, and Harry Scheiber.
    >>> format_authors_mla(c)
    Scheiber, Jane, Harry Scheiber, and Kenny Butthead Endo.
    >>> format_authors_mla(d)
    Scheiber, Jane, et al.
    
    source: http://www.umuc.edu/library/libhow/mla_examples.cfm
    """
    cite = ''
    if authors:
        if len(authors) == 1:
            # Scheiber, Jane.
            cite = surname_givenname(authors[0])
        elif len(authors) < 4:
            # Scheiber, Jane, and Harry Scheiber.
            # Scheiber, Jane, Harry Scheiber, and Kenny Endo.
            names = []
            # pop off the first name; it's surname,given
            l = authors
            l.reverse()
            names.append(surname_givenname(l.pop())) # first name 
            l.reverse()
            # the rest of names are "given surname"
            [names.append(givenname_surname(n)) for n in l]
            # last two names separated by "and"
            last = names.pop()
            names.append('') # to add that last comma
            commas = ', '.join(names) # there will be a space after last comma
            cite = 'and '.join([ commas, last ])
        elif len(authors) >= 4:
            # Scheiber, Jane, et al.
            cite = '{}, et al'.format(surname_givenname(authors[0]))
        if cite:
            cite = '{}.'.format(cite)
    return cite

x = """

from wikiprox.encyclopedia import format_authors_apa, format_authors_chicago, format_authors_cse, format_authors_mhra, format_authors_mla
a = [[u'Scheiber',u'Jane']]
b = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry']]
c = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead']]
d = [[u'Scheiber',u'Jane'], [u'Scheiber',u'Harry'], [u'Endo',u'Kenny Butthead'], [u'Doe',u'John']]

format_authors_apa(a)
format_authors_apa(b)
format_authors_apa(c)
format_authors_apa(d)

format_authors_chicago(a)
format_authors_chicago(b)
format_authors_chicago(c)
format_authors_chicago(d)

format_authors_cse(a)
format_authors_cse(b)
format_authors_cse(c)
format_authors_cse(d)

format_authors_mhra(a)
format_authors_mhra(b)
format_authors_mhra(c)
format_authors_mhra(d)

format_authors_mla(a)
format_authors_mla(b)
format_authors_mla(c)
format_authors_mla(d)
"""
