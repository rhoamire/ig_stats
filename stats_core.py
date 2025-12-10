import pandas as pd

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
