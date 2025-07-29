import argparse
import logging

# from pathlib import Path # TODOLATER:

import uvicorn

# Local imports
from .app import asgi_app, app  # noqa: F401

# Run Config
NUM_WORKERS = 1


if __name__ == "__main__":
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=80)
    parser.add_argument("-d", "--debug", action="store_true")  # False unless specified
    parser.add_argument("-l", "--debug_level", type=int, default=logging.DEBUG)
    parser.add_argument("-w", "--num_workers", type=int, default=NUM_WORKERS)
    parser.add_argument(
        "-s", "--use_dash_server", action="store_true"
    )  # False unless specified
    # parser.add_argument("-r", "--reset", type=bool, default=False)
    args = parser.parse_args()

    if args.debug:
        # Set env variable for Qimchi's debug level
        import os

        os.environ["QIMCHI_DEBUG_LEVEL"] = str(args.debug_level)

    # TODOLATER:
    # if args.reset:
    #     # Reset the state
    #     print("Resetting the state...")
    #     Path("state.json").unlink(missing_ok=True)

    if args.use_dash_server:
        logging.warning(
            "Qimchi is using Dash server as `-s` is set in the command. This is not recommended for production use."
            " Use Uvicorn instead."
        )
        app.run(
            host="0.0.0.0",
            port=args.port,
            debug=args.debug,  # Reload the server on changes, only in debug mode
            use_reloader=args.debug,  # Reload the server on changes, only in debug mode
        )
    else:
        uvicorn.run(
            "qimchi.__main__:asgi_app",
            host="0.0.0.0",
            port=args.port,
            log_level="error",  # NOTE: Separate from Qimchi's debug level
            reload=args.debug,  # Reload the server on changes, only in debug mode
            workers=args.num_workers,
        )
