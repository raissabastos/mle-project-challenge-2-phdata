# test_client.py
import requests
import pandas as pd
import pathlib
import time
import json

BASE = pathlib.Path(__file__).parent.parent
CSV = BASE / "data" / "future_unseen_examples.csv"
URL = "http://127.0.0.1:8000/predict"

def main(n=5, pretty=True):
    df = pd.read_csv(CSV, dtype={"zipcode": str})
    samples = df.head(n).to_dict(orient="records")

    payload = {"instances": samples}
    print(f"Sending {len(samples)} instances to {URL}")

    resp = requests.post(URL, json=payload, timeout=30)

    print(f"Status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(resp.text)
        return


    # Print results overview
    preds = data.get("predictions", [])
    if preds:
        print("Predictions Overview:")
        for item in preds:
            idx = item.get("input_index")
            pred = item.get("prediction")
            print(f"  Sample {idx}: {pred}")
    else:
        print("No prediction returned.")

if __name__ == "__main__":
    main(5)
