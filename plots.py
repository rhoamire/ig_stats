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
