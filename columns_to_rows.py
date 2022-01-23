def columns_to_rows(columns):
    rows = [[] for index in range(len(columns[0]))]
    for column_index, column in enumerate(columns):
        for row_index, item in enumerate(column):
            rows[row_index].append(item)
    return rows
