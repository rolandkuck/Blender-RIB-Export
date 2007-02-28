class RIB(object):
    def __init__(self, hout):
        self.hout = hout
    def output(self, token):
        pass
    def close(self):
        print >> self.hout, "WorldBegin"
