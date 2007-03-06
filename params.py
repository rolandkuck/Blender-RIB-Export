class Float(object):
    def __init__(self, value):
        self.value = value
    def inline(self, name):
        return [ "uniform float %s" % str(name), [float(self.value)] ]
