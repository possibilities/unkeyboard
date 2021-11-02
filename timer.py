import time


def timer():
    start = time.time()
    last_split = time.time()

    def _time_elapsed(name):
        nonlocal last_split
        elapsed = time.time() - last_split
        print("%s %ss" % (name, "{:.2f}".format(elapsed)))
        last_split = time.time()

    def _total_time():
        total_elapsed = time.time() - start
        print("Total elapsed: %ss" % ("{:.2f}".format(total_elapsed)))

    return [_time_elapsed, _total_time]
