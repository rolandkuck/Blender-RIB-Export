
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
        raise AttributeError(name)

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
                self.hout.split()
            except:
                self.hout.output(str(token))

    def close(self):
        self.hout.close()


class MotionRIB(RIB):

    def __init__(self, hout, timescale, shutter_open, shutter_close):
        super(MotionRIB, self).__init__(hout)
        self.timescale = timescale
        self.shutter_open = shutter_open
        self.shutter_close = shutter_close
        self.motion_interval = map(lambda x: x/(self.timescale-1.), range(0,self.timescale))
        self.frame_count = 0
        self.frame_mod = 0
        self.frame_list = []
        self.in_frame = False

    def output(self, name, *tokens):
        if name == "FrameBegin":
            self.frame_begin()
        elif name == "FrameEnd":
            self.frame_end()
        else:
            if self.in_frame:
                self.frame_list[self.frame_mod].append((name, tokens))
            else:
                super(MotionRIB, self).output(name, *tokens)

    def frame_begin(self):
        self.in_frame = True
        self.frame_list.append([])

    def frame_end(self):
        self.in_frame = False
        if (self.frame_mod+1) != self.timescale:
            self.frame_mod += 1
            return
        super(MotionRIB, self).output("Shutter", self.shutter_open+self.frame_count, self.shutter_close + self.frame_count)
        motion_interval = map(lambda x: x+self.frame_count, self.motion_interval)
        super(MotionRIB, self).output("FrameBegin", self.frame_count)
        for i in xrange(0, len(self.frame_list[0])):
            for j in xrange(1, self.timescale):
                if self.frame_list[j][i] != self.frame_list[0][i]:
                    break
            else:
                name, tokens = self.frame_list[0][i] 
                super(MotionRIB, self).output(name, *tokens)
                break
            super(MotionRIB, self).output("MotionBegin", motion_interval)
            for j in xrange(0, self.timescale):
                name, tokens = self.frame_list[j][i] 
                super(MotionRIB, self).output(name, *tokens)
            super(MotionRIB, self).output("MotionEnd")
        super(MotionRIB, self).output("FrameEnd")
        self.frame_count += 1
        self.frame_mod = 1
        self.frame_list = self.frame_list[-1:]



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


def main():
    import sys
    hout = RIB(sys.stdout)
    hout.RiFormat(800, 600, 1.0)
    hout.RiScreenWindow(-1, 1, -0.75, 0.75)
    hout.RiFrameBegin(0)
    hout.RiProjection("perspective", "fov", [49.1343426412])
    hout.RiClipping(0.10000000149, 100.0)
    hout.RiScale(1., 1., -1.)
    hout.RiConcatTransform([ 0.685880541801, -0.317370116711, 0.654861867428, -0.0,
                             0.727633714676, 0.312468618155, -0.610665559769, 0.0,
                            -0.0108167678118, 0.89534330368, 0.445245355368, -0.0,
                            -0.338183164597, -0.376693725586, -11.2523422241, 1.0, ])
    hout.RiWorldBegin()
    hout.RiCoordinateSystem("Lamp")
    hout.RiAttributeBegin()
    hout.RiTransform ([ -0.290864646435, 0.95517116785, -0.0551890581846, 0.0,
                        -0.771100819111, -0.19988335669, 0.604524731636, 0.0,
                         0.566393196583, 0.21839119494, 0.794672250748, 0.0,
                         4.07624530792, 1.00545394421, 5.90386199951, 1.0, ])
    hout.RiAttributeEnd()
    hout.RiCoordinateSystem("Cube")
    hout.RiAttributeBegin()
    hout.RiTransform ([ 1.0, 0.0, 0.0, 0.0,
                        0.0, 1.0, 0.0, 0.0,
                        0.0, 0.0, 1.0, 0.0,
                        0.0, 0.0, 0.0, 1.0, ])
    hout.RiPointsPolygons([ 4, 4, 4, 4, 4, 4, ],
                          [ 0, 1, 2, 3, 4, 7, 6,
                            5, 0, 4, 5, 1, 1, 5,
                            6, 2, 2, 6, 7, 3, 4, 0, 3, 7, ],
                          "P", [ 1.0, 0.999999940395, -1.0, 1.0,
                                -1.0, -1.0, -1.00000011921, -0.999999821186,
                                -1.0, -0.999999642372, 1.00000035763, -1.0,
                                1.00000047684, 0.999999463558, 1.0, 0.999999344349,
                                -1.00000059605, 1.0, -1.00000035763, -0.999999642372,
                                1.0, -0.999999940395, 1.0, 1.0, ])
    hout.RiAttributeEnd()
    hout.RiCoordinateSystem("Camera")
    hout.RiAttributeBegin()
    hout.RiTransform ([ 0.685880541801, 0.727633774281, -0.0108167808503, 0.0,
                        -0.317370116711, 0.312468618155, 0.895343244076, 0.0,
                        0.654861867428, -0.610665619373, 0.445245355368, 0.0,
                        7.48113155365, -6.50763988495, 5.34366512299, 1.0, ])
    hout.RiAttributeEnd()
    hout.RiWorldEnd()
    hout.RiFrameEnd()
    hout.close()

if __name__ == "__main__":
    main()
