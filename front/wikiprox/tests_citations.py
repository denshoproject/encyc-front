import citations

def test_surname_givenname():
    in0 = ['Scheiber','Harry']
    in1 = ['Endo','Kenny Butthead']
    out0 = 'Scheiber, Harry'
    out1 = 'Endo, Kenny Butthead'
    assert citations.surname_givenname(in0) == out0
    assert citations.surname_givenname(in1) == out1

def test_surname_givenname_initials():
    in0 = ['Scheiber','Harry']
    in1 = ['Endo','Kenny Butthead']
    out0 = 'Scheiber, Harry'
    out1 = 'Endo, Kenny B.'
    assert citations.surname_givenname_initials(in0) == out0
    assert citations.surname_givenname_initials(in1) == out1

def test_givenname_surname():
    in0 = ['Scheiber','Harry']
    in1 = ['Endo','Kenny Butthead']
    out0 = 'Harry Scheiber'
    out1 = 'Kenny Butthead Endo'
    assert citations.givenname_surname(in0) == out0
    assert citations.givenname_surname(in1) == out1

def test_surname_initials():
    in0 = ['Scheiber','Harry']
    in1 = ['Endo','Kenny Butthead']
    out0 = 'Scheiber, H.'
    out1 = 'Endo, K. B.'
    assert citations.surname_initials(in0) == out0
    assert citations.surname_initials(in1) == out1

def test_surname_initials_cse():
    in0 = ['Scheiber','Harry']
    in1 = ['Endo','Kenny Butthead']
    out0 = 'Scheiber H'
    out1 = 'Endo K B'
    assert citations.surname_initials_cse(in0) == out0
    assert citations.surname_initials_cse(in1) == out1

def test_format_authors_apa():
    in0 = [['Scheiber', 'Jane']]
    in1 = [['Scheiber','Jane'], ['Scheiber','Harry']]
    in2 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    in3 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    out0 = 'Scheiber, Jane.'
    out1 = 'Scheiber, Jane, and Scheiber, Harry.'
    out2 = 'Scheiber, Jane, Scheiber, Harry, and Endo, Kenny B.'
    out3 = 'Scheiber, Jane, Scheiber, Harry, Endo, Kenny B., and Doe, John.'
    assert citations.format_authors_apa(in0) == out0
    assert citations.format_authors_apa(in1) == out1
    assert citations.format_authors_apa(in2) == out2
    assert citations.format_authors_apa(in3) == out3

def test_format_authors_bibtex():
    in0 = [['Scheiber', 'Jane']]
    in1 = [['Scheiber','Jane'], ['Scheiber','Harry']]
    in2 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    in3 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    out0 = 'Scheiber, J.'
    out1 = 'Scheiber, J. and Scheiber, H.'
    out2 = 'Scheiber, J. and Scheiber, H. and Endo, K. B.'
    out3 = 'Scheiber, J. and Scheiber, H. and Endo, K. B. and Doe, J.'
    assert citations.format_authors_bibtex(in0) == out0
    assert citations.format_authors_bibtex(in1) == out1
    assert citations.format_authors_bibtex(in2) == out2
    assert citations.format_authors_bibtex(in3) == out3

def test_format_authors_chicago():
    in0 = [['Scheiber', 'Jane']]
    in1 = [['Scheiber','Jane'], ['Scheiber','Harry']]
    in2 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    in3 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    out0 = 'Jane Scheiber.'
    out1 = 'Jane Scheiber and Harry Scheiber.'
    out2 = 'Jane Scheiber, Harry Scheiber and Kenny Butthead Endo.'
    out3 = 'Jane Scheiber et al.'
    assert citations.format_authors_chicago(in0) == out0
    assert citations.format_authors_chicago(in1) == out1
    assert citations.format_authors_chicago(in2) == out2
    assert citations.format_authors_chicago(in3) == out3

def test_format_authors_cse():
    in0 = [['Coffman', 'Tom']]
    in1 = [['Scheiber', 'Jane']]
    in2 = [['Scheiber','Jane'], ['Scheiber','Harry']]
    in3 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    in4 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    out0 = 'Coffman T.'
    out1 = 'Scheiber J.'
    out2 = 'Scheiber J, Scheiber H.'
    out3 = 'Scheiber J, Scheiber H, Endo K B.'
    out4 = 'Scheiber J, Scheiber H, Endo K B, Doe J.'
    assert citations.format_authors_cse(in0) == out0
    assert citations.format_authors_cse(in1) == out1
    assert citations.format_authors_cse(in2) == out2
    assert citations.format_authors_cse(in3) == out3
    assert citations.format_authors_cse(in4) == out4

def test_format_authors_mhra():
    in0 = [['Scheiber', 'Jane']]
    in1 = [['Scheiber','Jane'], ['Scheiber','Harry']]
    in2 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    in3 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    out0 = 'Jane Scheiber.'
    out1 = 'Jane Scheiber and Harry Scheiber.'
    out2 = 'Jane Scheiber, Harry Scheiber and Kenny Butthead Endo.'
    out3 = 'Jane Scheiber and others.'
    assert citations.format_authors_mhra(in0) == out0
    assert citations.format_authors_mhra(in1) == out1
    assert citations.format_authors_mhra(in2) == out2
    assert citations.format_authors_mhra(in3) == out3

def test_format_authors_mla():
    in0 = [['Scheiber', 'Jane']]
    in1 = [['Scheiber','Jane'], ['Scheiber','Harry']]
    in2 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead']]
    in3 = [['Scheiber','Jane'], ['Scheiber','Harry'], ['Endo','Kenny Butthead'], ['Doe','John']]
    out0 = 'Scheiber, Jane.'
    out1 = 'Scheiber, Jane, and Harry Scheiber.'
    out2 = 'Scheiber, Jane, Harry Scheiber, and Kenny Butthead Endo.'
    out3 = 'Scheiber, Jane, et al.'
    assert citations.format_authors_mla(in0) == out0
    assert citations.format_authors_mla(in1) == out1
    assert citations.format_authors_mla(in2) == out2
    assert citations.format_authors_mla(in3) == out3
