import argparse
import logging
import os

import pandas as pd


def main(data: str):

    logging.info("Application 'analyse' started.")

    path_info = os.path.join(data, "info.json")
    path_result = os.path.join(data, "result.csv")

    df = pd.read_json(path_info, orient="records")
    logging.info(f"Information read from '{path_info}'.")

    df = df[
        (df["price"] < 100) & (df["potential"] > 10) & (df["gauge"] < 2)
    ].sort_values("potential", ascending=False)

    df.to_csv(path_result, index=False)

    logging.info("Application 'analyse' terminated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to the data directory.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: %(levelname)s: %(message)s",
    )

    try:
        main(data=args.data)
    except Exception:
        logging.exception("Fatal error in main.", exc_info=True)
        raise
