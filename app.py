import os
import importlib

import streamlit as st

import config
import identity
import json_loader
import profile_loader

from stats_core import (
    messages_per_month,
    messages_per_user,
    most_active_day,
    user_time_stats,
    words_per_user,
    direction_word_stats,
    per_conversation_message_length_diff,
    domination_stats,
    heatmap_data,
    longest_conversations_by_messages,
    longest_conversations_by_duration,
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

st.set_page_config(page_title="Instagram Chat Stats", layout="wide")


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


@st.cache_data(show_spinner=True)
def load_df_for_root(export_root: str):
    set_export_root(export_root)
    my_name, my_username = identity.detect_identity(
        config.INBOX_DIR, config.PERSONAL_INFO_JSON
    )
    df = json_loader.build_dataframe_from_json(config.INBOX_DIR, my_name)
    return df, my_name


st.title("Instagram Chat Stats")

default_root = getattr(config, "EXPORT_ROOT", "")

export_root = st.sidebar.text_input(
    "Instagram export root folder",
    value=default_root,
    help="Folder that contains your_instagram_activity, media, personal_information, etc.",
)

if not export_root or not os.path.isdir(export_root):
    st.error("Please enter a valid export root directory.")
    st.stop()

df, my_name = load_df_for_root(export_root)

if df.empty:
    st.warning("No messages parsed. Check that this export folder is correct.")
    st.stop()

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
    ],
)

if section == "My stats":
    st.subheader("My stats")

    stats = global_user_stats(df)

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
                f"Top contact: **{stats['top_contact']}** "
                f"({stats['top_contact_count']} messages)"
            )

    st.markdown("---")

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

    if stats["first_message"] is not None:
        st.write(f"**First message ever:** {stats['first_message']}")
        st.write(f"**Latest message:** {stats['last_message']}")
        st.write(f"**Active days:** {stats['active_days']}")


elif section == "Global timeline":
    st.subheader("Messages per month")
    mpm = messages_per_month(df)
    fig = plot_messages_per_month(mpm)
    st.pyplot(fig)
    day, count = most_active_day(df)
    if day:
        st.write(f"Most active day: **{day}** with **{count}** messages")

elif section == "Per-user time stats":
    st.subheader("Per-user time stats")
    uts = user_time_stats(df)
    st.dataframe(uts.sort_values("total_msgs", ascending=False).head(50))

elif section == "Word stats":
    st.subheader("Top users by total words")
    wpu = words_per_user(df)
    fig = plot_top_users_by_messages(wpu, top_n=20)
    st.pyplot(fig)
    st.subheader("You vs them word stats")
    dws = direction_word_stats(df)
    st.dataframe(dws)
    st.subheader("Per-conversation average message length difference")
    diff = per_conversation_message_length_diff(df)
    st.dataframe(diff.sort_values("me_minus_them", ascending=False).head(20))

elif section == "Conversation domination":
    st.subheader("Who texts more: you vs them")
    dom = domination_stats(df)
    mode = st.radio("View", ["Convos where I text more", "Convos where they text more"])
    if mode == "Convos where I text more":
        fig = plot_domination_balance(dom, top_n=20, mode="me")
    else:
        fig = plot_domination_balance(dom, top_n=20, mode="them")
    st.pyplot(fig)
    st.dataframe(dom.sort_values("balance", ascending=False).head(50))

elif section == "Longest conversations":
    st.subheader("By total messages")
    top_msgs = longest_conversations_by_messages(df, top_n=20)
    fig1 = plot_top_users_by_messages(top_msgs, top_n=20)
    st.pyplot(fig1)
    st.subheader("By duration (days)")
    top_dur = longest_conversations_by_duration(df, top_n=20)
    st.dataframe(top_dur)

elif section == "Daily/weekly pattern":
    st.subheader("Message heatmap (day vs hour)")
    heat = heatmap_data(df)
    fig = plot_heatmap(heat)
    st.pyplot(fig)

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
    per_conv = media_stats_per_conversation(df)
    st.dataframe(
        per_conv.sort_values("any_attachment_share", ascending=False).head(20)
    )

    st.markdown("### Top reel spammers")

    spammers = reel_spammer_stats(df)
    mode = st.radio(
        "View",
        ["Convos where I send more reels", "Convos where they send more reels"],
        horizontal=True,
    )
    spam_mode = "me" if "I send" in mode else "them"
    fig_spam = plot_top_reel_spammers(spammers, mode=spam_mode, top_n=15)
    if fig_spam is not None:
        st.pyplot(fig_spam)
        st.dataframe(
            spammers.sort_values("balance", ascending=False).head(20)
            if spam_mode == "me"
            else spammers.sort_values("balance").head(20)
        )
    else:
        st.info("No reels detected in this export.")

    st.markdown("### Most attachment-heavy conversations (chart)")
    attach_stats = attachment_heavy_stats(df)
    fig_attach = plot_attachment_share(attach_stats, top_n=15)
    if fig_attach is not None:
        st.pyplot(fig_attach)
    else:
        st.info("No attachments detected in this export.")
