import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")
st.header("")

# Hide Streamlit default UI
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- Login Section ---
st.title("🛞 Tire Usage Monitoring Application System (TUMAS) - Batik Air")

users = {
    "admin": "1234",
    "engineer": "abcd",
    "user": "tumas"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# --- Sidebar Menu ---
menu = ["🏠 Home", "🔍 Search", "📊 Summary"]
page = st.sidebar.radio("Navigate", menu)

# --- Home Page ---
if page == "🏠 Home":
    st.subheader("Welcome to the Tire Usage Monitoring Application System (TUMAS)")

    st.markdown("""
        This system helps track **aircraft tire usage**, including serial numbers, installation dates,
        and removal history, allowing engineers to monitor tire performance effectively.
    """)

# --- Search Page ---
elif page == "🔍 Search":
    st.subheader("🔍 Search Tire by Serial Number (SN)")
    FILE = "TUMAS-DATABASE.xlsx"

    try:
        # ✅ Read Excel with correct header and clean columns
        df = pd.read_excel(FILE, sheet_name="Sheet1", header=0)
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace('"', '', regex=False)
            .str.replace("'", '', regex=False)
            .str.replace('\n', ' ', regex=False)
        )

        st.write("✅ Columns detected:", [repr(c) for c in df.columns.tolist()])

    except Exception as e:
        st.error(f"⚠️ Could not load tire database: {e}")
        df = pd.DataFrame()

    # Only continue if the file was loaded
    if not df.empty:
        serial = st.text_input("Enter Tire Serial Number (SN):")

        if serial:
            if "SN" not in df.columns:
                st.error("❌ 'SN' column not found in your file. Please check your Excel header.")
            else:
                result = df[df["SN"].astype(str).str.contains(serial.strip(), case=False, na=False)]
                if not result.empty:
                    st.success(f"✅ Found {len(result)} matching record(s):")
                    st.dataframe(result)
                else:
                    st.warning("⚠️ No matching tire serial number found.")
        else:
            st.info("ℹ️ Please enter a serial number to search.")

# --- Summary Page ---
elif page == "📊 Summary":
    st.subheader("📊 Tire Summary Dashboard")

    FILE = "TUMAS-DATABASE.xlsx"

    try:
        df = pd.read_excel(FILE, sheet_name="Sheet1", header=0)
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace('"', '', regex=False)
            .str.replace("'", '', regex=False)
            .str.replace('\n', ' ', regex=False)
        )

        if "Ex-Aircraft" in df.columns:
            summary = df["Ex-Aircraft"].value_counts()
            fig = go.Figure(go.Bar(
                x=summary.index,
                y=summary.values,
                marker=dict(color="#C42454")
            ))
            fig.update_layout(title="Tires by Aircraft", xaxis_title="Aircraft", yaxis_title="Count")
            st.plotly_chart(fig)
        else:
            st.warning("⚠️ 'Ex-Aircraft' column not found in the dataset.")
    except Exception as e:
        st.error(f"⚠️ Could not load summary data: {e}")

# --- Logout Button ---
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
