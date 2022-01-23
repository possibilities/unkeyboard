def to_pairs(obj):
    pairs = []
    for key in obj.keys():
        pairs.append([key, obj[key]])
    return pairs
