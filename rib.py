class RIB(object):

    cmd_indent = [ "WorldBegin", "TransformBegin" ]
    cmd_deindent = [ "WorldEnd", "TransformEnd" ]

    def __init__(self, hout):
        self.hout = Formatter(hout)
        self._needs_newline = False

    class _curried_output(object):
        def __init__(self, RIB, name):
            self.RIB = RIB
            self.name = name
        def __call__(self, *tokens):
            self.RIB.output(self.name, *tokens)

    def __getattr__(self, name):
        if name[0:2] == "Ri":
            return self._curried_output(self, name[2:])

    def output(self, name, *tokens):
        if name in self.cmd_deindent:
            self.hout.indent(-1)
        if self._needs_newline:
            self.hout.newline()
        else:
            self._needs_newline = True
        self.hout.output(name)
        for t in tokens:
            self._recurse_output(t)
        if name in self.cmd_indent:
            self.hout.indent()

    def _recurse_output(self, token):
        if isinstance(token, str):
            self.hout.split()
            self.hout.output('"'+token+'"')
        else:
            try:
                first = True
                for i in token:
                    if first:
                        self.hout.output('[')
                        first = False
                    self._recurse_output(i)
                self.hout.output(']')
            except:
                self.hout.output(str(token))

    def close(self):
        self.hout.close()


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
            self._split_pos = -1

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
        self._next_level = 0
        self._split_level = 0
        self._split_pos = -1

    def indent(self, level=1):
        self._next_level += level

    def close(self):
        self._clear_cache()
