import re
from datetime import datetime
from dateutil.parser import parse as parse_dt
from bs4 import BeautifulSoup
from config import DIV_SELECTOR, MY_NAME, SPECIAL_MAP


def clean_username(name):
    if name in SPECIAL_MAP:
        return SPECIAL_MAP[name]
    m = re.search(r"_(\d+)$", name)
    if m:
        return name[:m.start()]
    return name


def extract_sender(msg_div):
    h2 = msg_div.find("h2")
    return h2.get_text(strip=True) if h2 else None


def extract_text(msg_div):
    body = msg_div.find("div", class_="_3-95 _a6-p")
    if not body:
        return ""
    return body.get_text(" ", strip=True)


def extract_timestamp(msg_div):
    ts_div = msg_div.find("div", class_="_3-94 _a6-o")
    if not ts_div:
        return None
    text = ts_div.get_text(strip=True)
    try:
        return parse_dt(text)
    except Exception:
        return None


def extract_messages_from_html(html, raw_conv_name):
    soup = BeautifulSoup(html, "html.parser")
    conv_name = clean_username(raw_conv_name)
    msg_divs = soup.select(DIV_SELECTOR)
    rows = []
    for msg_div in msg_divs:
        sender = extract_sender(msg_div)
        text = extract_text(msg_div)
        ts = extract_timestamp(msg_div)
        direction = "me" if sender == MY_NAME else "them"
        rows.append(
            {
                "conversation": conv_name,
                "raw_folder": raw_conv_name,
                "sender": sender,
                "direction": direction,
                "text": text,
                "timestamp": ts,
            }
        )
    return rows
