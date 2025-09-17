import requests
import pandas as pd
import pathlib
import time
import json

BASE = pathlib.Path(__file__).parent.parent
CSV = BASE / "data" / "future_unseen_examples.csv"
URL_PREDICT = "http://localhost:8000/predict"
URL_EXPLAIN = "http://localhost:8000/explain/permutation"

def main(n=5, pretty=True):
    df = pd.read_csv(CSV, dtype={"zipcode": str})
    samples = df.head(n).to_dict(orient="records")

    payload = {"instances": samples}
    print(f"Sending {len(samples)} instances to {URL_PREDICT}")

    # --- Request to /predict ---
    t0 = time.time()
    resp = requests.post(URL_PREDICT, json=payload, timeout=30)
    dt = time.time() - t0

    print(f"Status: {resp.status_code} (latency {dt:.3f}s)")

    try:
        data = resp.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(resp.text)
        return

    # JSON
    if pretty:
        print(json.dumps(data, indent=2))

    # --- Request to /explain/permutation ---
    print(f"\nSending same {len(samples)} instances to {URL_EXPLAIN}")
    try:
        resp_explain = requests.post(URL_EXPLAIN, json=payload, timeout=60)
        print(f"/explain/permutation → status {resp_explain.status_code}")
        if pretty:
            print(json.dumps(resp_explain.json(), indent=2))
    except Exception as e:
        print("Failed to get explanation:", e)

if __name__ == "__main__":
    main(5)
