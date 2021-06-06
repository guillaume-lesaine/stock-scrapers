import argparse
import glob
import logging
import os

import analyse
import scrapy_get_info
import selenium_get_urls


def main(data: str, configuration: str):

    # Cleanup data directory
    if os.path.exists(data):
        data_paths = glob.glob(os.path.join(data, "*"))
        for f in data_paths:
            os.remove(f)
    else:
        os.mkdir(data)

    # Run applications
    selenium_get_urls.main(data=data, configuration=configuration)

    scrapy_get_info.main(data=data)

    analyse.main(data=data)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to the data directory.")
    parser.add_argument(
        "--configuration", help="Path to the configuration directory."
    )
    parser.add_argument("--logs", help="Path to the logs directory.")
    args = parser.parse_args()

    # Create log directory if needed
    logs_directory = os.path.dirname(args.logs)
    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    logging.basicConfig(
        filename=args.logs,
        level=logging.INFO,
        format="%(asctime)s: %(levelname)s: %(message)s",
    )

    try:
        main(data=args.data, configuration=args.configuration)
    except Exception:
        logging.exception("Fatal error in main.", exc_info=True)
        raise
