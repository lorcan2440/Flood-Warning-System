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
        args = sys.argv[1:]
        TERMINATE_APP_TIME = float(args[0].strip())
        t1 = multiprocessing.Process(target=run)
        t1.start()
        time.sleep(TERMINATE_APP_TIME)

        # NOTE: use a shutdown request instead of a forceful closure:
        # https://community.plotly.com/t/shutdown-dash-app-after-n-seconds/20422
        print(f'Terminating process because script called with argument {TERMINATE_APP_TIME} seconds...')
        t1.terminate()
    else:
        run()
