def make_fuzzy_string(st):
    rv = "%"
    for letter in st:
        rv.append(letter + '%')

    return rv
