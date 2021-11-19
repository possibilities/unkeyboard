import functools


def flow(*functions):
    functions_list = [*functions]
    functions_list.reverse()
    return functools.reduce(
        lambda f, g: lambda x: f(g(x)), functions_list, lambda x: x
    )
