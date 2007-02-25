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

class Comment(object):
    delimiter = string.whitespace
    def detect(self, input, pos):
        return input[pos] == '#'
    def tokenize(self, input, pos):
        start = pos
        while input[pos] != '\n':
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

class Array(object):
    def detect(self, input, pos):
        return input[pos] in '[]'
    def tokenize(self, input, pos):
        return pos+1, input[pos]

def parse(input):
    tokens = []
    w = Whitespace()
    n = Name()
    s = String()
    a = Array()
    c = Comment()
    line = []
    pos = 0
    while True:
        if pos >= len(input):
            break
        if w.detect(input, pos):
            pos, dummy = w.tokenize(input, pos)
        if c.detect(input, pos):
            pos, dummy = c.tokenize(input, pos)
        elif s.detect(input, pos):
            pos, value = s.tokenize(input, pos)
            line.append(value)
        elif a.detect(input, pos):
            pos, value = a.tokenize(input, pos)
            line.append(value)
        elif n.detect(input, pos):
            pos, name = n.tokenize(input, pos)
            try:
                value = float(name)
                line.append(value)
            except:
                if len(line) != 0:
                    tokens.append(line)
                line = [name]
        else:
            break
    if len(line) != 0:
        tokens.append(line)
    return tokens
