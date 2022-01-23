def chunk(size, items):
    chunks = []
    for item in items:
        if len(chunks) == 0 or len(chunks[-1]) >= size:
            chunks.append([])
        chunks[-1].append(item)
    return chunks
