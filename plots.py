import matplotlib.pyplot as plt

def plot_messages_per_month(series):
    fig, ax = plt.subplots(figsize=(12, 4))
    x = [str(p) for p in series.index]
    ax.plot(x, series.values, marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Messages")
    ax.tick_params(axis="x", rotation=90)
    fig.tight_layout()
    return fig

def plot_top_users_by_messages(series, top_n=20):
    top = series.sort_values(ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top.index, top.values)
    ax.invert_yaxis()
    ax.set_xlabel("Messages")
    ax.set_ylabel("User")
    for bar, value in zip(ax.patches, top.values):
        ax.text(bar.get_width() + max(top.values) * 0.01, bar.get_y() + bar.get_height() / 2, str(value), va="center")
    fig.tight_layout()
    return fig

def plot_domination_balance(dom_df, top_n=20, mode="me"):
    df = dom_df[dom_df["total"] > 50].copy()
    if mode == "me":
        sorted_df = df.sort_values("balance", ascending=False).head(top_n)
    else:
        sorted_df = df.sort_values("balance").head(top_n)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(sorted_df.index, sorted_df["balance"])
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("Balance (me_share - them_share)")
    ax.set_ylabel("User")
    fig.tight_layout()
    return fig

def plot_heatmap(heat_df):
    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(heat_df.values, aspect="auto")
    ax.set_yticks(range(len(heat_df.index)))
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][: len(heat_df.index)])
    ax.set_xticks(range(24))
    ax.set_xticklabels(range(24))
    ax.set_xlabel("Hour")
    ax.set_ylabel("Day of week")
    fig.colorbar(im, ax=ax, label="Messages")
    fig.tight_layout()
    return fig

def plot_top_reel_spammers(spammers_df, mode="me", top_n=15):
    if spammers_df.empty:
        return None
    df = spammers_df.copy()
    if mode == "me":
        df = df.sort_values("balance", ascending=False).head(top_n)
        title = "Conversations where I send more reels"
        values = df["balance"]
    else:
        df = df.sort_values("balance").head(top_n)
        title = "Conversations where they send more reels"
        values = df["balance"] * -1  # positive bar length

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df.index, values)
    ax.invert_yaxis()
    ax.set_xlabel("Reel difference (me - them)")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_attachment_share(per_conv_df, top_n=15):
    if per_conv_df.empty:
        return None
    df = per_conv_df.sort_values("any_attachment_share", ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df.index, df["any_attachment_share"])
    ax.invert_yaxis()
    ax.set_xlabel("Share of messages that are attachments")
    ax.set_title("Most attachment-heavy conversations")
    fig.tight_layout()
    return fig
