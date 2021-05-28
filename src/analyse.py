import argparse
import logging
import os

import pandas as pd


def main(data):

    logging.info("Application 'analyse' started.")

    path_info = os.path.join(data, "info.json")
    path_result = os.path.join(data, "result.csv")

    df = pd.read_json(path_info, orient="records")
    logging.info(f"Information read from '{path_info}'.")

    df = df[
        (df["price"] < 100) & (df["potentiel"] > 10) & (df["gauge"] < 2)
    ].sort_values("potentiel")

    df.to_csv(path_result, index=False)

    logging.info("Application 'analyse' terminated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to the data directory.")
    parser.add_argument("--logs", help="Path to the logs directory.")
    args = parser.parse_args()

    path_app_logs = os.path.join(args.logs, "analyse.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: %(levelname)s: %(message)s",
    )

    try:
        main(data=args.data)
    except Exception:
        logging.exception("Fatal error in main.", exc_info=True)
        raise
