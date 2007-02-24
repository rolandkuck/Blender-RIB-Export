import string

def parse(input):
    tokens = []
    name = ''
    for c in input:
        if c in string.whitespace:
            if name != '':
                tokens.append( (name, None) )
                name = ''
        else:
            name += c
    tokens.append( (name, None) )
    return tokens
