import os

EXPORT_ROOT = r"D:/instagram-some.to.one-2025-12-10-nebyAnA5"

SPECIAL_MAP = {
    "749124079818075": "Charvi",
    "17976709496683018": "Charvi",
}

AUTO_LOCAL_TIME = True

DIV_SELECTOR = "div.pam._3-95._2ph-._a6-g.uiBoxWhite.noborder"


def resolve_paths(export_root: str):
    export_root = os.path.abspath(export_root)
    your_ig_activity = os.path.join(export_root, "your_instagram_activity")
    inbox_dir = os.path.join(your_ig_activity, "messages", "inbox")
    personal_info_json = os.path.join(
        export_root,
        "personal_information",
        "personal_information",
        "personal_information.json",
    )
    return {
        "EXPORT_ROOT": export_root,
        "YOUR_IG_ACTIVITY": your_ig_activity,
        "INBOX_DIR": inbox_dir,
        "PERSONAL_INFO_JSON": personal_info_json,
    }
