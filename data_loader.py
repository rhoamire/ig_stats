import os
import pandas as pd
from bs4 import BeautifulSoup
from parsers import extract_messages_from_html
from config import BASE_DIR, DIV_SELECTOR, TIME_SHIFT_HOURS


def build_dataframe():
    print("Scanning BASE_DIR:", BASE_DIR)
    rows = []
    html_count = 0
    conv_count = 0
    msg_div_count = 0

    for entry in os.scandir(BASE_DIR):
        if not entry.is_dir():
            continue
        conv_count += 1
        raw_conv = entry.name
        print("Conversation folder:", raw_conv)
        for root, dirs, files in os.walk(entry.path):
            for name in files:
                if not name.lower().endswith(".html"):
                    continue
                html_count += 1
                file_path = os.path.join(root, name)
                print("  Found HTML:", file_path)
                with open(file_path, "r", encoding="utf-8") as f:
                    html = f.read()
                soup = BeautifulSoup(html, "html.parser")
                divs = soup.select(DIV_SELECTOR)
                msg_div_count += len(divs)
                if html_count <= 1:
                    print("  Message divs in this file:", len(divs))
                rows.extend(extract_messages_from_html(html, raw_conv))

    print("Total conv folders:", conv_count)
    print("Total HTML files:", html_count)
    print("Total message divs matched by selector:", msg_div_count)
    print("Total parsed rows:", len(rows))

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if "timestamp" in df.columns:
      df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

      if df["timestamp"].notna().any():
        if TIME_SHIFT_HOURS != 0:
          df["timestamp"] = df["timestamp"] + pd.to_timedelta(TIME_SHIFT_HOURS, unit="h")

        df["date"] = df["timestamp"].dt.date
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.to_period("M")
        df["dow"] = df["timestamp"].dt.dayofweek
        df["hour"] = df["timestamp"].dt.hour
    else:
      print("Warning: timestamps could not be parsed, time-based stats will be empty")

    if "text" in df.columns:
        df["word_count"] = df["text"].astype(str).str.split().str.len().fillna(0).astype(int)
    else:
        df["word_count"] = 0
    return df
