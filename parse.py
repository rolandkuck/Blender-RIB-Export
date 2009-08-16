# This file is part of blender-rib-export.
#
# Copyright 2007-2009 Roland Kuck <blenderrib@roland.kuck.name>
#
# blender-rib-export is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# blender-rib-export is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# blender-rib-export.  If not, see <http://www.gnu.org/licenses/>.

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
