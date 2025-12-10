import os
import json


def get_profile_photo_path(export_root, personal_info_json):
    if not os.path.exists(personal_info_json):
        return None

    try:
        with open(personal_info_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    users = data.get("profile_user") or []
    if not users:
        return None

    user = users[0]
    media_map = user.get("media_map_data", {})
    photo = media_map.get("Profile Photo")
    if not photo:
        return None

    uri = photo.get("uri")
    if not uri:
        return None

    full_path = os.path.normpath(os.path.join(export_root, uri))
    if os.path.exists(full_path):
        return full_path

    return None
