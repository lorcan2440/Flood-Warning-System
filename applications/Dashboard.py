# pylint: disable=import-error
import __init__  # noqa

import sys
import time
import multiprocessing

print('Loading datasets...')  # noqa
from floodsystem.dash_app import app  # noqa


def run():
    app.run_server(port=8888, debug=True)


if __name__ == '__main__':

    if len(sys.argv) > 1:

        TERMINATE_APP_TIME = float(sys.argv[1].strip())
        t1 = multiprocessing.Process(target=run)
        t1.start()
        time.sleep(TERMINATE_APP_TIME)
        t1.terminate()

    else:
        run()
