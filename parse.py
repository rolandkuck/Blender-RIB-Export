
def parse(input):
    tokens = [ ("Declare", ["squish", "uniform float"]),
               ("Option", ["limits", "bucketsize", [6, 6]]),
               ("WorldBegin", None)
             ]
    return tokens
