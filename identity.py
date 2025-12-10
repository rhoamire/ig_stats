import os
import json


def _name_from_personal_info(personal_info_json):
    if not os.path.exists(personal_info_json):
        return None, None

    try:
        with open(personal_info_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None, None

    users = data.get("profile_user") or []
    if not users:
        return None, None

    user = users[0]
    sm = user.get("string_map_data", {})

    name = None
    username = None

    if "Name" in sm:
        name = sm["Name"].get("value") or None
    if "Username" in sm:
        username = sm["Username"].get("value") or None

    return name, username


def _name_from_participants(inbox_dir):
    counts = {}

    for entry in os.scandir(inbox_dir):
        if not entry.is_dir():
            continue

        for root, dirs, files in os.walk(entry.path):
            for name in files:
                if not name.lower().endswith(".json"):
                    continue
                fp = os.path.join(root, name)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    continue

                for p in data.get("participants", []):
                    pname = p.get("name")
                    if not pname:
                        continue
                    counts[pname] = counts.get(pname, 0) + 1
            break

    if not counts:
        return None

    return max(counts, key=counts.get)


def detect_identity(inbox_dir, personal_info_json):
    name, username = _name_from_personal_info(personal_info_json)

    if not name:
        name = _name_from_participants(inbox_dir)

    if not name:
        name = "Me"

    return name, username
