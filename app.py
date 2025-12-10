import streamlit as st
from data_loader import build_dataframe
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
)
from plots import (
    plot_messages_per_month,
    plot_top_users_by_messages,
    plot_domination_balance,
    plot_heatmap,
)

st.set_page_config(page_title="Instagram Chat Stats", layout="wide")

@st.cache_data(show_spinner=True)
def load_df():
    return build_dataframe()

st.title("Instagram Chat Stats")

df = load_df()

if df.empty:
    st.warning("No messages parsed. Check BASE_DIR and DIV_SELECTOR.")
    st.stop()

section = st.sidebar.selectbox(
    "View",
    [
        "Global timeline",
        "Per-user time stats",
        "Word stats",
        "Conversation domination",
        "Longest conversations",
        "Daily/weekly pattern",
    ],
)

if section == "Global timeline":
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
