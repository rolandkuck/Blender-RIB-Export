import string

class ParseError(object):
    pass

class Name(object):
    delimiter = string.whitespace+'"[]#'
    def detect(self, input, pos):
        return input[pos] not in self.delimiter
    def tokenize(self, input, pos):
        start = pos
        while input[pos] not in self.delimiter:
            pos += 1
            if pos >= len(input):
                break
        return pos, input[start:pos]

class Whitespace(object):
    delimiter = string.whitespace
    def detect(self, input, pos):
        return input[pos] in self.delimiter
    def tokenize(self, input, pos):
        start = pos
        while input[pos] in self.delimiter:
            pos += 1
            if pos >= len(input):
                break
        return pos, ""

class String(object):
    def detect(self, input, pos):
        return input[pos] == '"'
    def tokenize(self, input, pos):
        pos += 1
        if pos >= len(input):
            raise ParseError()
        start = pos
        while input[pos] != '"':
            pos += 1
            if pos >= len(input):
                break
        return pos+1, input[start:pos]

def parse(input):
    tokens = []
    w = Whitespace()
    n = Name()
    s = String()
    name = None
    pos = 0
    while True:
        if pos >= len(input):
            break
        if w.detect(input, pos):
            pos, dummy = w.tokenize(input, pos)
        elif s.detect(input, pos):
            pos, value = s.tokenize(input, pos)
            tokens.append( (name, [value,]) )
            name = None
        elif n.detect(input, pos):
            if name != None:
                tokens.append( (name, None) )
            pos, name = n.tokenize(input, pos)
        else:
            break
    if name != None:
        tokens.append( (name, None) )
    return tokens
