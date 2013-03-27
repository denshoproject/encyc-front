DEFAULT = 'Densho Encyclopedia contributors.'


def surname_givenname(parsed):
    """
    >>> surname_givenname(  ['Scheiber','Harry'] )
    'Scheiber, Harry'
    >>> surname_givenname(  ['Endo','Kenny Butthead'] )
    'Endo, Kenny Butthead'
    """
    return ', '.join(parsed)
def surname_givenname_initials(parsed):
    """
    >>> surname_givenname_initials(  ['Scheiber','Harry'] )
    'Scheiber, Harry'
    >>> surname_givenname_initials(  ['Endo','Kenny Butthead'] )
    'Endo, Kenny B.'
    """
    surname = parsed[0]
    givens = []
    for n,g in enumerate(parsed[1].split(' ')):
        if n:
            givens.append('{0}.'.format(g[0]))
        else:
            givens.append(g)
    givens = ' '.join(givens)
    return ', '.join([surname, givens])
def givenname_surname(parsed):
    """
    >>> givenname_surname(  ['Scheiber','Harry'] )
    'Harry Scheiber'
    >>> givenname_surname(  ['Endo','Kenny Butthead'] )
    'Kenny Butthead Endo'
    """
    parsed.reverse()
    return ' '.join(parsed)
def surname_initials(parsed):
    """
    >>> surname_initials(  ['Scheiber','Harry'] )
    'Scheiber, H.'
    >>> surname_initials(  ['Endo','Kenny Butthead'] )
    'Endo, K. B.'
    """
    givens = ['{0}.'.format(g[0]) for g in parsed[1].split(' ')]
    givens = ' '.join(givens)
    surname = parsed[0]
    return ', '.join([surname, givens])
def surname_initials_cse(parsed):
    """
    >>> surname_initials_cse(  ['Scheiber','Harry'] )
    'Scheiber H'
    >>> surname_initials_cse(  ['Endo','Kenny Butthead'] )
    'Endo K B'
    """
    givens = [g[0] for g in parsed[1].split(' ')]
    givens = ' '.join(givens)
    surname = parsed[0]
    return ' '.join([surname, givens])

def format_authors_apa(authors):
    """Takes output of mediawiki.find_author_info() and formats in APA style.
    
    >>> a = [['Scheiber', 'Jane']]
    >>> b = [['Scheiber','Jane'], ['Scheiber','Harry']]
    >>> c = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    >>> d = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    >>> format_authors_apa(a)
    'Scheiber, Jane.'
    >>> format_authors_apa(b)
    'Scheiber, Jane, and Scheiber, Harry.'
    >>> format_authors_apa(c)
    'Scheiber, Jane, Scheiber, Harry, and Endo, Kenny B.'
    >>> format_authors_apa(d)
    'Scheiber, Jane, Scheiber, Harry, Endo, Kenny B., and Doe, John.'
    
    source: http://www.umuc.edu/library/libhow/mla_examples.cfm
    """
    cite = DEFAULT
    if authors:
        if len(authors) == 1:
            cite = surname_givenname(authors[0])
        elif len(authors) > 1:
            names = [surname_givenname_initials(n) for n in authors]
            # last two names separated by ampersand
            last = names.pop()
            names.append('') # to add that last comma
            commas = ', '.join(names) # there will be a space after last comma
            cite = 'and '.join([ commas, last ])
        if cite and not (cite[-1] == '.'):
            cite = '{0}.'.format(cite)
    return cite

def format_authors_bibtex(authors):
    """Takes output of mediawiki.find_author_info() and formats BibTeX style.
    
    >>> a = [['Scheiber', 'Jane']]
    >>> b = [['Scheiber','Jane'], ['Scheiber','Harry']]
    >>> c = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    >>> d = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    >>> format_authors_bibtex(a)
    'Scheiber, J.'
    >>> format_authors_bibtex(b)
    'Scheiber, J. and Scheiber, H.'
    >>> format_authors_bibtex(c)
    'Scheiber, J. and Scheiber, H. and Endo, K. B.'
    >>> format_authors_bibtex(d)
    'Scheiber, J. and Scheiber, H. and Endo, K. B. and Doe, J.'
    
    source: http://en.wikibooks.org/wiki/LaTeX/Bibliography_Management
    """
    cite = DEFAULT
    if authors:
        if len(authors):
            names = [surname_initials(n) for n in authors]
            cite = ' and '.join(names)
        if cite and not (cite[-1] == '.'):
            cite = '{0}.'.format(cite)
    return cite

def format_authors_chicago(authors):
    """Takes output of mediawiki.find_author_info() and formats Chicago style.
    
    >>> a = [['Scheiber', 'Jane']]
    >>> b = [['Scheiber','Jane'], ['Scheiber','Harry']]
    >>> c = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    >>> d = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    >>> format_authors_chicago(a)
    'Jane Scheiber.'
    >>> format_authors_chicago(b)
    'Jane Scheiber and Harry Scheiber.'
    >>> format_authors_chicago(c)
    'Jane Scheiber, Harry Scheiber and Kenny Butthead Endo.'
    >>> format_authors_chicago(d)
    'Jane Scheiber et al.'
    
    source: http://ilrb.cf.ac.uk/citingreferences/mhra/page13.html
    """
    cite = DEFAULT
    if authors:
        if len(authors) == 1:
            cite = givenname_surname(authors[0])
        elif len(authors) < 4:
            names = [givenname_surname(n) for n in authors]
            # last two names separated by 'and'
            last = names.pop()
            commas = ', '.join(names) # there will be a space after last comma
            cite = ' and '.join([ commas, last ])
        elif len(authors) >= 4:
            cite = '{0} et al'.format(givenname_surname(authors[0]))
        if cite and not (cite[-1] == '.'):
            cite = '{0}.'.format(cite)
    return cite

def format_authors_cse(authors):
    """Takes output of mediawiki.find_author_info() and formats CSE/CBE style.
    
    >>> a0 = [['Coffman', 'Tom']]
    >>> a = [['Scheiber', 'Jane']]
    >>> b = [['Scheiber','Jane'], ['Scheiber','Harry']]
    >>> c = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    >>> d = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    >>> format_authors_cse(a0)
    'Coffman T.'
    >>> format_authors_cse(a)
    'Scheiber J.'
    >>> format_authors_cse(b)
    'Scheiber J, Scheiber H.'
    >>> format_authors_cse(c)
    'Scheiber J, Scheiber H, Endo K B.'
    >>> format_authors_cse(d)
    'Scheiber J, Scheiber H, Endo K B, Doe J.'
    
    source: http://ilrb.cf.ac.uk/citingreferences/mhra/page13.html
    """
    cite = DEFAULT
    if authors:
        if len(authors):
            names = [surname_initials_cse(n) for n in authors]
            cite = ', '.join(names)
        if cite and not (cite[-1] == '.'):
            cite = '{0}.'.format(cite)
    return cite

def format_authors_mhra(authors):
    """Takes output of mediawiki.find_author_info() and formats MHRA style.
    
    >>> a = [['Scheiber', 'Jane']]
    >>> b = [['Scheiber','Jane'], ['Scheiber','Harry']]
    >>> c = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    >>> d = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    >>> format_authors_mhra(a)
    'Jane Scheiber.'
    >>> format_authors_mhra(b)
    'Jane Scheiber and Harry Scheiber.'
    >>> format_authors_mhra(c)
    'Jane Scheiber, Harry Scheiber and Kenny Butthead Endo.'
    >>> format_authors_mhra(d)
    'Jane Scheiber and others.'
    
    source: http://ilrb.cf.ac.uk/citingreferences/mhra/page13.html
    """
    cite = DEFAULT
    if authors:
        if len(authors) == 1:
            cite = givenname_surname(authors[0])
        elif len(authors) < 4:
            names = [givenname_surname(n) for n in authors]
            # last two names separated by 'and'
            last = names.pop()
            commas = ', '.join(names) # there will be a space after last comma
            cite = ' and '.join([ commas, last ])
        elif len(authors) >= 4:
            cite = '{0} and others'.format(givenname_surname(authors[0]))
        if cite and not (cite[-1] == '.'):
            cite = '{0}.'.format(cite)
    return cite

def format_authors_mla(authors):
    """Takes output of mediawiki.find_author_info() and formats MLA style.
    
    >>> a = [['Scheiber', 'Jane']]
    >>> b = [['Scheiber','Jane'], ['Scheiber','Harry']]
    >>> c = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    >>> d = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    >>> format_authors_mla(a)
    'Scheiber, Jane.'
    >>> format_authors_mla(b)
    'Scheiber, Jane, and Harry Scheiber.'
    >>> format_authors_mla(c)
    'Scheiber, Jane, Harry Scheiber, and Kenny Butthead Endo.'
    >>> format_authors_mla(d)
    'Scheiber, Jane, et al.'
    
    source: http://www.umuc.edu/library/libhow/mla_examples.cfm
    """
    cite = DEFAULT
    if authors:
        if len(authors) == 1:
            cite = surname_givenname(authors[0])
        elif len(authors) < 4:
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
            cite = '{0}, et al'.format(surname_givenname(authors[0]))
        if cite:
            cite = '{0}.'.format(cite)
    return cite

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# Kenny Endo asserts that he is the only one who can be called a "taiko artist".
