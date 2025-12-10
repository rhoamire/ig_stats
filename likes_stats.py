# likes_stats.py
import os
import json
from collections import Counter
from datetime import datetime


def _load(path):
    if not os.path.exists(path):
        print("XXXXXX")
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# ------------------------------------------------------------
# Liked Posts
# ------------------------------------------------------------

def load_liked_posts(export_root):
    """Return list of liked posts with (creator, timestamp, link)."""

    path = os.path.join(
        export_root,
        "your_instagram_activity",
        "likes",
        "liked_posts.json",
    )

    data = _load(path) or {}
    items = data.get("likes_media_likes", [])

    results = []

    for item in items:
        creator = item.get("title")  # username
        sld = item.get("string_list_data", [])
        if not sld:
            continue
        entry = sld[0]
        ts = entry.get("timestamp")
        link = entry.get("href")

        results.append({
            "creator": creator,
            "timestamp": ts,
            "link": link,
            "date": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
        })

    return results


def liked_per_creator(liked_items, top_n=50):
    counts = Counter([x["creator"] for x in liked_items])
    return counts.most_common(top_n)


# ------------------------------------------------------------
# Saved Posts
# ------------------------------------------------------------

def load_saved_posts(export_root):
    """Return list of saved posts with (creator, timestamp, link)."""

    base = os.path.join(
        export_root,
        "your_instagram_activity",
        "saved",
    )

    saved_posts_path = os.path.join(base, "saved_posts.json")
    saved_collections_path = os.path.join(base, "saved_collections.json")

    results = []

    # ---- saved_posts.json (simple) ----
    sp = _load(saved_posts_path) or {}
    for item in sp.get("saved_saved_media", []):
        creator = item.get("title")
        sm = item.get("string_map_data", {})
        meta = sm.get("Saved on", {})
        ts = meta.get("timestamp")
        link = meta.get("href")

        if ts:
            results.append({
                "creator": creator,
                "timestamp": ts,
                "link": link,
                "date": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            })

    # ---- saved_collections.json (each entry is a saved post) ----
    sc = _load(saved_collections_path) or {}
    for item in sc.get("saved_saved_collections", []):
        sm = item.get("string_map_data", {})
        name_field = sm.get("Name", {})
        creator = name_field.get("value")
        meta = sm.get("Added Time") or sm.get("Creation Time") or {}

        ts = meta.get("timestamp")
        link = name_field.get("href")  # link to reel

        if ts and creator:
            results.append({
                "creator": creator,
                "timestamp": ts,
                "link": link,
                "date": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            })

    return results


def saved_per_creator(saved_items, top_n=50):
    counts = Counter([x["creator"] for x in saved_items])
    return counts.most_common(top_n)
