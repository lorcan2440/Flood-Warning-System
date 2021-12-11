# pylint: disable=import-error
import __init__  # noqa

import sys

print('Loading datasets...')  # noqa
from floodsystem.dash_app import app, run_with_timeout  # noqa

HOST = '127.0.0.1'
PORT = 8050


def run(debug=True):
    app.run_server(host=HOST, port=PORT, debug=debug)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        timeout = float(sys.argv[1])
        run_with_timeout(app, timeout, host=HOST, port=PORT)
    else:
        run()
