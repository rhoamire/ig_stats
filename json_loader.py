import os
import json
import re
import pandas as pd
from datetime import datetime, timezone
from config import AUTO_LOCAL_TIME, SPECIAL_MAP




def clean_conversation_name(raw_conv: str) -> str:
    if raw_conv in SPECIAL_MAP:
        return SPECIAL_MAP[raw_conv]

    m = re.search(r"_(\d+)$", raw_conv)
    if m:
        suffix = m.group(1)
        if suffix in SPECIAL_MAP:
            return SPECIAL_MAP[suffix]
        return raw_conv[: m.start()]

    return raw_conv


def classify_message(msg):
    text = msg.get("content") or ""
    share = msg.get("share") or {}
    photos = msg.get("photos") or []
    videos = msg.get("videos") or []

    has_reel = False
    has_image = False
    attachment_text_only = False

    link = share.get("link") or ""

    if "instagram.com/reel/" in link:
        has_reel = True

    if photos or videos:
        has_image = True

    lower_text = text.lower()
    if "sent an attachment" in lower_text and not has_reel and not has_image:
        attachment_text_only = True

    if has_reel:
        mtype = "reel"
    elif has_image:
        mtype = "image"
    elif attachment_text_only:
        mtype = "attachment_text_only"
    else:
        mtype = "text"

    return mtype, has_reel, has_image, attachment_text_only, text


def to_local_time(ts_ms: int):
    ts_utc = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
    if AUTO_LOCAL_TIME:
        return ts_utc.astimezone().replace(tzinfo=None)
    return ts_utc.replace(tzinfo=None)



def build_dataframe_from_json(inbox_dir, my_name):
    rows = []

    for entry in os.scandir(inbox_dir):
        if not entry.is_dir():
            continue
        raw_conv = entry.name
        conv_name = clean_conversation_name(raw_conv)
        for root, dirs, files in os.walk(entry.path):
            for name in files:
                if not name.lower().endswith(".json"):
                    continue
                file_path = os.path.join(root, name)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                messages = data.get("messages", [])
                for msg in messages:
                    sender = msg.get("sender_name")
                    ts_ms = msg.get("timestamp_ms")
                    if ts_ms is None:
                        continue

                    ts = to_local_time(ts_ms)

                    mtype, has_reel, has_image, attachment_text_only, text = classify_message(msg)
                    direction = "me" if sender == my_name else "them"

                    rows.append(
                        {
                            "conversation": conv_name,
                            "raw_folder": raw_conv,
                            "sender": sender,
                            "direction": direction,
                            "text": text,
                            "timestamp": ts,
                            "message_type": mtype,
                            "has_reel": has_reel,
                            "has_image": has_image,
                            "attachment_text_only": attachment_text_only,
                        }
                    )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].notna().any():
        df["date"] = df["timestamp"].dt.date
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.to_period("M")
        df["dow"] = df["timestamp"].dt.dayofweek
        df["hour"] = df["timestamp"].dt.hour

    df["word_count"] = df["text"].astype(str).str.split().str.len().fillna(0).astype(int)
    return df
