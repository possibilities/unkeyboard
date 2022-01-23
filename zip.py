def zip(*lists):
    zipped = []
    for list in lists:
        for index, item in enumerate(list):
            try:
                zipped[index]
            except Exception:
                zipped.append([])
            zipped[index].append(item)
    return zipped
