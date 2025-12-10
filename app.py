import os
import importlib
import streamlit as st
import pandas as pd
import config
import identity
import json_loader
import profile_loader
import likes_stats

from stats_core import (
    messages_per_month,
    user_time_stats,
    words_per_user,
    direction_word_stats,
    per_conversation_message_length_diff,
    domination_stats,
    heatmap_data,
    longest_conversations_by_messages,
    longest_conversations_by_duration,
    most_active_day,
    global_user_stats,
    media_stats_overall,
    media_stats_per_conversation,
    reel_spammer_stats,
    attachment_heavy_stats,
)

from plots import (
    plot_messages_per_month,
    plot_top_users_by_messages,
    plot_domination_balance,
    plot_heatmap,
    plot_top_reel_spammers,
    plot_attachment_share,
)


# -------------------------------------------------------------
# Streamlit config
# -------------------------------------------------------------
st.set_page_config(page_title="Instagram Chat Stats", layout="wide")


# -------------------------------------------------------------
# Dynamic export path handling
# -------------------------------------------------------------
def set_export_root(export_root: str):
    export_root = os.path.abspath(export_root)

    config.EXPORT_ROOT = export_root
    config.YOUR_IG_ACTIVITY = os.path.join(export_root, "your_instagram_activity")
    config.INBOX_DIR = os.path.join(config.YOUR_IG_ACTIVITY, "messages", "inbox")
    config.PERSONAL_INFO_JSON = os.path.join(
        export_root,
        "personal_information",
        "personal_information",
        "personal_information.json",
    )
    config.PROFILE_MEDIA_ROOT = os.path.join(export_root, "media", "profile")

    importlib.reload(identity)
    importlib.reload(json_loader)
    importlib.reload(profile_loader)
    importlib.reload(likes_stats)


@st.cache_data(show_spinner=True)
def load_df_for_root(export_root: str):
    set_export_root(export_root)

    my_name, my_username = identity.detect_identity(
        config.INBOX_DIR,
        config.PERSONAL_INFO_JSON
    )

    df = json_loader.build_dataframe_from_json(config.INBOX_DIR, my_name)
    return df, my_name


# -------------------------------------------------------------
# UI — Export directory input
# -------------------------------------------------------------
st.title("Instagram Chat Stats")

default_root = getattr(config, "EXPORT_ROOT", "")

export_root = st.sidebar.text_input(
    "Instagram export root folder",
    value=default_root,
    help="Folder containing: your_instagram_activity, media, personal_information, etc.",
)

if not export_root or not os.path.isdir(export_root):
    st.error("Please enter a valid export root directory.")
    st.stop()

df, my_name = load_df_for_root(export_root)

if df.empty:
    st.warning("No messages parsed. Wrong export folder?")
    st.stop()


# -------------------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------------------
section = st.sidebar.selectbox(
    "View",
    [
        "My stats",
        "Global timeline",
        "Per-user time stats",
        "Word stats",
        "Conversation domination",
        "Longest conversations",
        "Daily/weekly pattern",
        "Media & attachments",
        "Likes & Saves Insights",
    ],
)


# -------------------------------------------------------------
# SECTION: MY STATS
# -------------------------------------------------------------
if section == "My stats":
    st.subheader("My stats")

    stats = global_user_stats(df)

    # Profile card
    pc1, pc2 = st.columns([1, 3])
    with pc1:
        profile_path = profile_loader.get_profile_photo_path(
            config.EXPORT_ROOT, config.PERSONAL_INFO_JSON
        )
        if profile_path and os.path.exists(profile_path):
            st.image(profile_path, width="content")
        else:
            st.write("🧑‍💻")

    with pc2:
        st.markdown(f"### {my_name}")
        st.write(f"Conversations in this export: **{stats['conversations']}**")
        if stats["top_contact"]:
            st.write(
                f"Top contact: **{stats['top_contact']}** ({stats['top_contact_count']} messages)"
            )

    st.markdown("---")

    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total messages", stats["total_messages"])
        st.metric("Conversations", stats["conversations"])
    with col2:
        st.metric("Messages sent (me)", stats["my_messages"])
        st.metric("Messages received", stats["their_messages"])
    with col3:
        st.metric("My share", f"{stats['my_share'] * 100:.1f}%")
        if stats["messages_per_day"] is not None:
            st.metric("Avg msgs/day", f"{stats['messages_per_day']:.1f}")

    st.markdown("---")

    # Media stats
    st.markdown("### Media sent vs received")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Reels sent", stats["my_reels"])
    with m2:
        st.metric("Reels received", stats["their_reels"])
    with m3:
        st.metric("Images sent", stats["my_images"])
    with m4:
        st.metric("Images received", stats["their_images"])

    st.markdown("---")

    # Timeline stats
    if stats["first_message"]:
        st.write(f"**First message:** {stats['first_message']}")
        st.write(f"**Latest message:** {stats['last_message']}")
        st.write(f"**Active days:** {stats['active_days']}")


# -------------------------------------------------------------
# SECTION: GLOBAL TIMELINE
# -------------------------------------------------------------
elif section == "Global timeline":
    st.subheader("Messages per month")
    mpm = messages_per_month(df)
    fig = plot_messages_per_month(mpm)
    st.pyplot(fig)

    day, count = most_active_day(df)
    if day:
        st.write(f"Most active day: **{day}** with **{count}** messages")


# -------------------------------------------------------------
# SECTION: PER-USER TIME STATS
# -------------------------------------------------------------
elif section == "Per-user time stats":
    st.subheader("Per-user time stats")

    uts = user_time_stats(df)
    uts = uts.sort_values("total_msgs", ascending=False).head(50)

    # Convert index (conversation name) into a column
    uts = uts.reset_index().rename(columns={"index": "conversation"})

    # Add Rank column starting from 1
    uts.insert(0, "Rank", range(1, len(uts) + 1))

    # Highlight top 3 rows
    def highlight_top3(row):
        rank = row["Rank"]
        if rank == 1:
            return ["font-weight: bold; color: gold"] * len(row)
        elif rank == 2:
            return ["font-weight: bold; color: silver"] * len(row)
        elif rank == 3:
            return ["font-weight: bold; color: #cd7f32"] * len(row)
        return [""] * len(row)

    st.dataframe(
        uts.style.apply(highlight_top3, axis=1),
        hide_index=True
    )




# -------------------------------------------------------------
# SECTION: WORD STATS
# -------------------------------------------------------------
elif section == "Word stats":
    st.subheader("Top users by total words")
    wpu = words_per_user(df)
    fig = plot_top_users_by_messages(wpu, top_n=20)
    st.pyplot(fig)

    st.subheader("You vs them word stats")
    st.dataframe(direction_word_stats(df))

    st.subheader("Per-conversation avg message length diff")
    diff = per_conversation_message_length_diff(df)
    st.dataframe(diff.sort_values("me_minus_them", ascending=False).head(20))


# -------------------------------------------------------------
# SECTION: DOMINATION
# -------------------------------------------------------------
elif section == "Conversation domination":
    st.subheader("Who texts more: you vs them")
    dom = domination_stats(df)

    mode = st.radio("View", ["Convos where I text more", "Convos where they text more"])
    fig = plot_domination_balance(dom, top_n=20, mode="me" if "I text" in mode else "them")
    st.pyplot(fig)

    st.dataframe(dom.sort_values("balance", ascending=False).head(50))


# -------------------------------------------------------------
# SECTION: LONGEST CONVERSATIONS
# -------------------------------------------------------------
elif section == "Longest conversations":
    st.subheader("By total messages")
    top_msgs = longest_conversations_by_messages(df, top_n=20)
    st.pyplot(plot_top_users_by_messages(top_msgs, top_n=20))

    st.subheader("By duration (days)")
    st.dataframe(longest_conversations_by_duration(df, top_n=20))


# -------------------------------------------------------------
# SECTION: DAILY / WEEKLY PATTERN
# -------------------------------------------------------------
elif section == "Daily/weekly pattern":
    st.subheader("Message heatmap (day × hour)")
    fig = plot_heatmap(heatmap_data(df))
    st.pyplot(fig)


# -------------------------------------------------------------
# SECTION: MEDIA & ATTACHMENTS
# -------------------------------------------------------------
elif section == "Media & attachments":
    st.subheader("Media and attachment stats")

    overall, by_dir = media_stats_overall(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total messages", overall["total_msgs"])
    with col2:
        st.metric("Total reels", overall["reels"])
    with col3:
        st.metric("Total images", overall["images"])
    with col4:
        st.metric("Any attachments", overall["any_attachment"])

    st.markdown("### Me vs Them (attachment breakdown)")
    st.dataframe(by_dir)

    st.markdown("### Attachment-heavy conversations")
    st.dataframe(
        media_stats_per_conversation(df)
            .sort_values("any_attachment_share", ascending=False)
            .head(20)
    )

    st.markdown("### Top reel spammers")
    spammers = reel_spammer_stats(df)
    mode = st.radio(
        "Reel view",
        ["I send more reels", "They send more reels"],
        horizontal=True
    )
    fig_spam = plot_top_reel_spammers(
        spammers,
        mode="me" if "I send" in mode else "them",
        top_n=15
    )
    if fig_spam:
        st.pyplot(fig_spam)

    st.markdown("### Most attachment-heavy conversations (chart)")
    attach_stats = attachment_heavy_stats(df)
    fig_attach = plot_attachment_share(attach_stats, top_n=15)
    if fig_attach:
        st.pyplot(fig_attach)


# -------------------------------------------------------------
# SECTION: LIKES & SAVES INSIGHTS (NEW)
# -------------------------------------------------------------
elif section == "Likes & Saves Insights":
    st.subheader("Likes & Saves Insights")

    liked = likes_stats.load_liked_posts(export_root)
    saved = likes_stats.load_saved_posts(export_root)

    st.write(f"**Total liked posts:** {len(liked)}")
    st.write(f"**Total saved posts:** {len(saved)}")

    st.markdown("---")
    st.markdown("### Top creators you like the most")

    top_liked = likes_stats.liked_per_creator(liked)

    df_top_liked = pd.DataFrame(top_liked, columns=["creator", "likes"])

    # Make index start at 1
    df_top_liked.index = df_top_liked.index + 1

    # Add gold/silver/bronze coloring
    def highlight_top3(row):
        idx = row.name
        if idx == 1:
            return ["font-weight: bold; color: gold"] * len(row)
        if idx == 2:
            return ["font-weight: bold; color: silver"] * len(row)
        if idx == 3:
            return ["font-weight: bold; color: #cd7f32"] * len(row)  # bronze
        return [""] * len(row)

    st.dataframe(df_top_liked.style.apply(highlight_top3, axis=1))

    st.markdown("---")
    st.markdown("### Creators whose posts you save the most")

    top_saved = likes_stats.saved_per_creator(saved)

    df_top_saved = pd.DataFrame(top_saved, columns=["creator", "saves"])
    df_top_saved.index = df_top_saved.index + 1

    # Reuse same styling
    st.dataframe(df_top_saved.style.apply(highlight_top3, axis=1))
