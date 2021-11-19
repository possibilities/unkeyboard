def to_pairs(dictionary):
    pairs = []
    for key in dictionary.keys():
        pairs.append([key, dictionary[key]])
    return pairs
