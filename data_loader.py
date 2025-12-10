import os
import pandas as pd
from parsers import extract_messages_from_html
from config import BASE_DIR

def build_dataframe():
    rows = []
    for entry in os.scandir(BASE_DIR):
        if not entry.is_dir():
            continue
        raw_conv = entry.name
        for root, dirs, files in os.walk(entry.path):
            for name in files:
                if not name.lower().endswith(".html"):
                    continue
                file_path = os.path.join(root, name)
                with open(file_path, "r", encoding="utf-8") as f:
                    html = f.read()
                rows.extend(extract_messages_from_html(html, raw_conv))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["date"] = df["timestamp"].dt.date
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.to_period("M")
    df["dow"] = df["timestamp"].dt.dayofweek
    df["hour"] = df["timestamp"].dt.hour
    df["word_count"] = df["text"].str.split().str.len().fillna(0).astype(int)
    return df
