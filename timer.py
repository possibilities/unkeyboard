import time


def timer():
    start = time.time()
    last_split = time.time()

    def _time_elapsed(name):
        nonlocal last_split
        print(name + ": " + str(time.time() - last_split))
        last_split = time.time()

    def _total_time():
        print("Total: " + str(time.time() - start))

    return [_time_elapsed, _total_time]
