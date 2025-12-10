import pandas as pd

def global_user_stats(df: pd.DataFrame):
    total_msgs = len(df)
    my_mask = df["direction"] == "me"
    their_mask = df["direction"] == "them"

    my_msgs = int(my_mask.sum())
    their_msgs = int(their_mask.sum())
    conv_count = int(df["conversation"].nunique())

    if "has_reel" in df.columns:
        my_reels = int(df.loc[my_mask, "has_reel"].sum())
        their_reels = int(df.loc[their_mask, "has_reel"].sum())
    else:
        my_reels = their_reels = 0

    if "has_image" in df.columns:
        my_images = int(df.loc[my_mask, "has_image"].sum())
        their_images = int(df.loc[their_mask, "has_image"].sum())
    else:
        my_images = their_images = 0

    ts = df["timestamp"].dropna()
    if not ts.empty:
        first_msg = ts.min()
        last_msg = ts.max()
        active_days = (last_msg - first_msg).days + 1
        msgs_per_day = total_msgs / active_days if active_days > 0 else total_msgs
    else:
        first_msg = None
        last_msg = None
        active_days = None
        msgs_per_day = None

    top_contact_series = (
        df.groupby("conversation").size().sort_values(ascending=False).head(1)
    )
    if not top_contact_series.empty:
        top_contact = top_contact_series.index[0]
        top_contact_count = int(top_contact_series.iloc[0])
    else:
        top_contact = None
        top_contact_count = 0

    my_share = my_msgs / total_msgs if total_msgs else 0

    return {
        "total_messages": int(total_msgs),
        "my_messages": my_msgs,
        "their_messages": their_msgs,
        "my_share": my_share,
        "conversations": conv_count,
        "first_message": first_msg,
        "last_message": last_msg,
        "active_days": active_days,
        "messages_per_day": msgs_per_day,
        "top_contact": top_contact,
        "top_contact_count": top_contact_count,
        "my_reels": my_reels,
        "their_reels": their_reels,
        "my_images": my_images,
        "their_images": their_images,
    }



def messages_per_month(df: pd.DataFrame):
    return df.groupby("month").size().sort_index()

def messages_per_day(df: pd.DataFrame):
    return df.groupby("date").size().sort_index()

def most_active_day(df: pd.DataFrame):
    per_day = messages_per_day(df)
    if per_day.empty:
        return None, 0
    return per_day.idxmax(), per_day.max()

def user_span(df: pd.DataFrame):
    span = df.groupby("conversation")["timestamp"].agg(["min", "max"])
    span = span.rename(columns={"min": "first_message", "max": "last_message"})
    span["duration_days"] = (span["last_message"] - span["first_message"]).dt.days + 1
    return span



def messages_per_user(df: pd.DataFrame):
    return df.groupby("conversation").size().rename("total_msgs")

def user_time_stats(df: pd.DataFrame):
    msgs = messages_per_user(df)
    span = user_span(df)
    stats = msgs.to_frame().join(span)
    stats["msgs_per_day"] = stats["total_msgs"] / stats["duration_days"]
    return stats

def words_per_user(df: pd.DataFrame):
    return df.groupby("conversation")["word_count"].sum().sort_values(ascending=False)

def direction_word_stats(df: pd.DataFrame):
    return df.groupby("direction")["word_count"].agg(["mean", "sum", "count"])

def per_conversation_message_length_diff(df: pd.DataFrame):
    g = df.groupby(["conversation", "direction"])["word_count"].mean().unstack(fill_value=0)
    if "me" not in g:
        g["me"] = 0
    if "them" not in g:
        g["them"] = 0
    g["me_minus_them"] = g["me"] - g["them"]
    return g

def domination_stats(df: pd.DataFrame):
    counts = df.groupby(["conversation", "direction"]).size().unstack(fill_value=0)
    if "me" not in counts:
        counts["me"] = 0
    if "them" not in counts:
        counts["them"] = 0
    counts["total"] = counts["me"] + counts["them"]
    counts = counts[counts["total"] > 0]
    counts["me_share"] = counts["me"] / counts["total"]
    counts["them_share"] = counts["them"] / counts["total"]
    counts["balance"] = counts["me_share"] - counts["them_share"]
    return counts

def heatmap_data(df: pd.DataFrame):
    heat = df.groupby(["dow", "hour"]).size().unstack(fill_value=0)
    heat = heat.reindex(index=sorted(heat.index))
    return heat

def longest_conversations_by_messages(df: pd.DataFrame, top_n=20):
    msgs = messages_per_user(df)
    return msgs.sort_values(ascending=False).head(top_n)

def longest_conversations_by_duration(df: pd.DataFrame, top_n=20):
    stats = user_time_stats(df)
    return stats.sort_values("duration_days", ascending=False).head(top_n)



def media_stats_overall(df: pd.DataFrame):
    df = df.copy()
    df["has_any_attachment"] = df["has_reel"] | df["has_image"] | df["attachment_text_only"]

    total = len(df)
    by_dir = df.groupby("direction").agg(
        total_msgs=("direction", "size"),
        reels=("has_reel", "sum"),
        images=("has_image", "sum"),
        attachment_text_only=("attachment_text_only", "sum"),
        any_attachment=("has_any_attachment", "sum"),
    )

    for col in ["reels", "images", "attachment_text_only", "any_attachment"]:
        by_dir[col + "_share"] = by_dir[col] / by_dir["total_msgs"]

    overall = {
        "total_msgs": total,
        "reels": int(df["has_reel"].sum()),
        "images": int(df["has_image"].sum()),
        "attachment_text_only": int(df["attachment_text_only"].sum()),
        "any_attachment": int(df["has_any_attachment"].sum()),
    }

    return overall, by_dir


def media_stats_per_conversation(df: pd.DataFrame):
    df = df.copy()
    df["has_any_attachment"] = df["has_reel"] | df["has_image"] | df["attachment_text_only"]
    g = df.groupby("conversation").agg(
        total_msgs=("conversation", "size"),
        reels=("has_reel", "sum"),
        images=("has_image", "sum"),
        attachment_text_only=("attachment_text_only", "sum"),
        any_attachment=("has_any_attachment", "sum"),
    )
    for col in ["reels", "images", "attachment_text_only", "any_attachment"]:
        g[col + "_share"] = g[col] / g["total_msgs"]
    return g

def reel_spammer_stats(df: pd.DataFrame):
    if "has_reel" not in df.columns:
        return pd.DataFrame()

    reels = df[df["has_reel"]]
    g = reels.groupby(["conversation", "direction"]).size().unstack(fill_value=0)
    if "me" not in g:
        g["me"] = 0
    if "them" not in g:
        g["them"] = 0
    g = g.rename(columns={"me": "my_reels", "them": "their_reels"})
    g["total_reels"] = g["my_reels"] + g["their_reels"]
    g = g[g["total_reels"] > 0]
    g["balance"] = g["my_reels"] - g["their_reels"]
    return g


def attachment_heavy_stats(df: pd.DataFrame):
    if not {"has_reel", "has_image", "attachment_text_only"}.issubset(df.columns):
        return pd.DataFrame()

    df = df.copy()
    df["has_any_attachment"] = (
        df["has_reel"] | df["has_image"] | df["attachment_text_only"]
    )
    g = df.groupby("conversation").agg(
        total_msgs=("conversation", "size"),
        any_attachment=("has_any_attachment", "sum"),
    )
    g = g[g["total_msgs"] > 0]
    g["any_attachment_share"] = g["any_attachment"] / g["total_msgs"]
    return g

