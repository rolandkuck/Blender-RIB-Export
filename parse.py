import string

class ParseError(object):
    pass


def find_pos(input, pos, predicate):
    while predicate(input[pos]):
        pos += 1
        if pos >= len(input):
            break
    return pos

class LineAssembler(object):
    def __init__(self):
        self.result = []
        self.linecache = []

    def insert(self, token):
        self.linecache.append(token)

    def flush(self):
        if len(self.linecache) != 0:
            self.result.append(self.linecache)
        self.linecache = []

    def retrieve(self):
        self.flush()
        return self.result


class Name(object):
    delimiter = string.whitespace+'"[]#'
    def detect(self, input, pos):
        return input[pos] not in self.delimiter
    def tokenize(self, input, pos, la):
        start = pos
        pos = find_pos(input, pos, lambda x: x not in self.delimiter)
        name = input[start:pos]
        try:
            value = float(name)
        except:
            la.flush()
            value = name
        la.insert(value)
        return pos 

class Whitespace(object):
    delimiter = string.whitespace
    def detect(self, input, pos):
        return input[pos] in self.delimiter
    def tokenize(self, input, pos, la):
        pos = find_pos(input, pos, lambda x: x in self.delimiter)
        return pos

class Comment(object):
    delimiter = string.whitespace
    def detect(self, input, pos):
        return input[pos] == '#'
    def tokenize(self, input, pos, la):
        pos = find_pos(input, pos, lambda x: x != '\n')
        return pos

class String(object):
    def detect(self, input, pos):
        return input[pos] == '"'
    def tokenize(self, input, pos, la):
        pos += 1
        if pos >= len(input):
            raise ParseError()
        start = pos
        pos = find_pos(input, pos, lambda x: x != '"')
        la.insert(input[start:pos])
        return pos+1

class Array(object):
    def detect(self, input, pos):
        return input[pos] in '[]'
    def tokenize(self, input, pos, la):
        la.insert(input[pos])
        return pos+1


def parse(input):
    la = LineAssembler()
    tokenizers = [ Whitespace(), Name(), String(), Array(), Comment() ]
    pos = 0
    while True:
        if pos >= len(input):
            break
        for t in tokenizers:
            if t.detect(input, pos):
                pos = t.tokenize(input, pos, la)
                break
    return la.retrieve()
