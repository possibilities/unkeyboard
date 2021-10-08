import time


def create_timer():
    start = time.time()
    last_split = time.time()

    def _time_elapsed(name):
        nonlocal last_split
        print(name + ": " + str(time.time() - last_split))
        last_split = time.time()

    def _total_time():
        print("total: " + str(time.time() - start))

    return [_time_elapsed, _total_time]
