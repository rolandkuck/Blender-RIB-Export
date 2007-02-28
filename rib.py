class RIB(object):

    def __init__(self, hout):
        self.hout = hout

    def output(self, token):
        pass

    def close(self):
        print >> self.hout, "WorldBegin"


class Formatter(object):

    def __init__(self, hout):
        self.hout = hout
        self._tabsize = 2
        self._width = 78
        self._level = 0
        self._split_level = 0
        self._next_level = 0
        self._split_pos = -1
        self._line = []

    def tabsize(self, t):
        self._tabsize = t

    def width(self, w):
        self._width = w

    def output(self, token):
        self._line.append(token)
        if len(self._build_line()) > self._width and len(self._line) > 1:
            next_line = self._line[self._split_pos:]
            self._line = self._line[:self._split_pos]
            self._clear_cache()
            print >> self.hout
            self._split_level = 1
            self._line = next_line

    def split(self):
        self._split_pos = len(self._line)

    def _build_line(self):
        indent = ' '*(self._level+self._split_level)*self._tabsize
        return indent +' '.join(self._line)

    def _clear_cache(self):
        print >> self.hout, self._build_line(),
        self._line = []

    def newline(self):
        self._clear_cache()
        print >> self.hout
        self._level = max(0, self._level +self._next_level)
        self._split_level = 0
        self._split_pos = -1

    def indent(self, level=1):
        self._next_level = level

    def close(self):
        self._clear_cache()
