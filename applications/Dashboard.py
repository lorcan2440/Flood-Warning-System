# pylint: disable=import-error
import __init__  # noqa

from floodsystem.dash_app import app


def run():
    app.run_server(port=8888, debug=True)


if __name__ == '__main__':
    run()
