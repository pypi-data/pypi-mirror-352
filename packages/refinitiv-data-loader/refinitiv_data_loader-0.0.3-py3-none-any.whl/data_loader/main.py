import os
import json
import refinitiv.data as rd
import polars as pl
import argparse
from datetime import datetime, timedelta

def open_session() -> None:
    """Open Refinitiv session."""
    rd.open_session(
        config_name="Configuration/refinitiv-data.config.json",
    )

def get_rics(index: str) -> list[str]:
    """Load the list of RICs for a given index from JSON."""
    with open(f'naming/rics_{index}.json', 'r') as f:
        return json.load(f)

def get_fields() -> dict[str, str]:
    """Load mapping from your local field names to Refinitiv field codes."""
    with open('naming/fields.json', 'r') as f:
        return json.load(f)

def init_data(
    rics: list[str],
    fields: list[str],
    interval: str,
    start: str,
    end: str,
    debug: bool = False
) -> None:
    """
    Download full history for each RIC and write to Parquet.
    Skips any RIC that already has a file.
    """
    os.makedirs("data", exist_ok=True)
    existing = {os.path.splitext(f)[0] for f in os.listdir("data") if f.endswith(".parquet")}
    to_download = [ric for ric in rics if ric not in existing]
    if debug and existing:
        print(f"Skipping {len(existing)} RICs that already have data.")
    if not to_download:
        return

    open_session()
    field_map = get_fields()

    for i, ric in enumerate(to_download, start=1):
        if debug:
            print(f"[{i}/{len(to_download)}] Fetching {ric} from {start} to {end}…")

        # map your local names to Refinitiv codes
        codes = [field_map[f] for f in fields]

        df = rd.get_history(universe=[ric], fields=codes, interval=interval, start=start, end=end)
        df = pl.from_pandas(df)     
        df.write_parquet(f"data/{ric}.parquet")

    rd.close_session()

def update_data(
    rics: list[str],
    new_end: str,
    debug: bool = False
) -> None:
    """
    For each RIC with existing data, fetch only the new rows
    since the last date in its Parquet, then append.
    """
    os.makedirs("data", exist_ok=True)
    open_session()
    new_end_dt = datetime.fromisoformat(new_end).date()
    field_map = get_fields()

    for i, ric in enumerate(rics, start=1):
        path = f"data/{ric}.parquet"
        if not os.path.exists(path):
            if debug:
                print(f"[{i}/{len(rics)}] No existing file for {ric}, skipping.")
            continue

        df0 = pl.read_parquet(path)
        df0 = df0.with_column(
            pl.col("Date").str.strptime(pl.Date, fmt="%Y-%m-%d")
        )
        latest = df0["Date"].max()

        if debug:
            print(f"[{i}/{len(rics)}] {ric} latest = {latest}")

        if latest >= new_end_dt:
            if debug:
                print(f" → {ric} already up to {new_end}.")
            continue

        # decide which fields to request (map from your columns)
        local_cols = [c for c in df0.columns if c != "Date"]
        codes = [field_map[c] for c in local_cols]

        # fetch from the next day after `latest`
        start_iso = (latest + timedelta(days=1)).isoformat()
        new_slice = rd.get_history(
            universe=[ric],
            fields=codes,
            start=start_iso,
            end=new_end
        )
        if not isinstance(new_slice, pl.DataFrame):
            new_slice = pl.from_pandas(new_slice)

        new_slice = new_slice.with_column(
            pl.col("Date").str.strptime(pl.Date, fmt="%Y-%m-%d")
        )

        combined = pl.concat([df0, new_slice]).sort("Date")
        combined.write_parquet(path)

        if debug:
            print(f" → Appended {new_slice.height} rows for {ric}")

    rd.close_session()


def load_raw_data(rics: list[str]) -> dict:
    """Load raw data without preprocessing
    
    Args:
        rics (list[str]): Refintiv Instrument Codes
        
    Returns:
        dict: dictionary of DataFrames for each RIC
    """
    
    data = {}
    
    for i, ric in enumerate(rics):
        if os.path.exists(f"data/{ric}.parquet"):
            data[ric] = pl.read_parquet(f"data/{ric}.parquet")
        else:
            print(f"{i} / {len(rics)} | Data for {ric} not found")
    
    return data


def load_preprocessed_data(rics: list[str]) -> dict:
    """Load raw data, forward fill and remove missing values

    Args:
        rics (list[str]): Refintiv Instrument Codes

    Returns:
        dict: dictionary of DataFrames for each RIC
    """
    
    data = load_raw_data(rics)

    # preprocess
    remove = []
    for key, df in data.items():
        assert isinstance(df, pl.DataFrame), f"{key} is not a DataFrame"
        df.ffill(inplace=True)
        df.dropna(inplace=True)

    # remove erroneous data
    for key in remove: data.pop(key)

    return data

# python dataloader.py init  --index sp500 --fields TRDPRC_1,TRDVWAP --start 2020-01-01 --end 2021-12-31 --debug
# python dataloader.py update --index sp500                                             --end 2022-01-31 --debug

def main():  # This function will be the entry point
    p = argparse.ArgumentParser(description="Load Refinitiv data")
    p.add_argument("mode", choices=["init","update"], help="init or update")
    p.add_argument("--index",  required=True,                help="e.g. sp500")
    p.add_argument("--fields", required=False, default="",   help="comma-sep fields for init")
    p.add_argument("--interval", required=False, default="D",   help="e.g. H for hourly, D for daily. Note: Original default was 'H'") # Changed default to 'D' as it's more common, adjust if 'H' was intended.
    p.add_argument("--start",  required=False, default="",   help="YYYY-MM-DD (init only)")
    p.add_argument("--end",    required=True,                help="YYYY-MM-DD")
    p.add_argument("--debug",  action="store_true",          help="verbose output")
    args = p.parse_args()

    rics = get_rics(args.index)

    if args.mode == "init":
        if not args.start:
            p.error("--start is required for init mode") # Make start truly required for init
        fs = args.fields.split(",") if args.fields else []
        init_data(rics, fs, args.interval, args.start, args.end, debug=args.debug)
    else:  # This is 'update' mode
        update_data(rics, new_end=args.end, debug=args.debug)

if __name__ == "__main__":
    main()