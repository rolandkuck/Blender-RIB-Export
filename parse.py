
def parse(input):
    tokens = []
    while True:
        split_list = input.split(None, 1) 
        token = split_list[0]
        tokens.append((token, None))
        if len(split_list) > 1:
            input = split_list[1]
        else:
            return tokens
