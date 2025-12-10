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
    span = msg_div.find("span")
    return span.get_text(strip=True) if span else None

def extract_text(msg_div):
    div = msg_div.find("div")
    return div.get_text(" ", strip=True) if div else ""

def extract_timestamp(msg_div):
    abbr = msg_div.find("abbr")
    if abbr and abbr.has_attr("data-utime"):
        return datetime.fromtimestamp(int(abbr["data-utime"]))
    span = msg_div.find("span", attrs={"title": True})
    if span:
        return parse_dt(span["title"])
    return None

def extract_messages_from_html(html, raw_conv_name):
    soup = BeautifulSoup(html, "html.parser")
    conv_name = clean_username(raw_conv_name)
    rows = []
    for msg_div in soup.select(DIV_SELECTOR):
        sender = extract_sender(msg_div)
        text = extract_text(msg_div)
        ts = extract_timestamp(msg_div)
        if ts is None:
            continue
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
