import argparse
import pandas as pd
import json
from faas_metric import compute_faas

def main():
    parser = argparse.ArgumentParser(description="Compute FAAS metric from CSV input.")
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV file')
    parser.add_argument('--output', type=str, required=False, help='Path to output JSON file')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    wer_list = df['wer'].tolist()
    speaker_metadata = df.drop(columns=['wer']).to_dict(orient='records')

    faas_score = compute_faas(wer_list, speaker_metadata)
    result = {"faas_score": faas_score}

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"FAAS score written to {args.output}")
    else:
        print("FAAS Score:", faas_score)
