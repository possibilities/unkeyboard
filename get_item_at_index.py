def get_item_at_index(list, index):
    if index < 0:
        return None
    try:
        return list[index]
    except Exception:
        return None
