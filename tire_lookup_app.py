import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")
st.header("")

# Hide Streamlit default menu and footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users = {
    "admin": "1234",
    "engineer": "5678",
    "guest": "0000"
}

if not st.session_state.logged_in:
    st.title("🔒 TUMAS Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in users and password == users[username]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()

# --- MAIN APP CONTENT ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Search", "About"])

if page == "Search":
    st.title("🛞 Tyre Usage Monitoring Application System (TUMAS)")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")

        search_term = st.text_input("🔍 Search by Part No, Serial No, or Description").strip()

        if search_term:
            result = df[df.apply(
                lambda row: search_term.lower() in str(row.values).lower(), axis=1
            )]

            if not result.empty:
                st.success(f"✅ Found {len(result)} matching record(s).")

                # --- Show clean table ---
                st.markdown("""
                    <div style="background-color:white; border-radius:10px; padding:10px;">
                        <h4 style="color:#5C246E; text-align:center;">Search Results</h4>
                    </div>
                """, unsafe_allow_html=True)

                # Display result table
                st.dataframe(
                    result.reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.warning("No matching records found.")
        else:
            st.info("Enter a search term above to find data.")

elif page == "About":
    st.title("ℹ️ About TUMAS")
    st.markdown("""
        **Tyre Usage Monitoring Application System (TUMAS)**  
        Developed as part of the Batik Air Technical Services internship project.  
        This system helps monitor and track aircraft tyre usage history efficiently.
    """)
    st.image("icon-192x192.png", width=100)
    st.markdown("""
        **Developer:** Nahimudin Ibrahim bin Hyder Ali  
        **Division:** Technical Services Engineer (Support Shop)  
        **Organization:** Batik Air  
        **Version:** Prototype 1.0
    """)

# --- FOOTER ---
st.markdown("""
<hr>
<div style="text-align:center; color:gray; font-size:13px;">
    © 2025 Batik Air | Developed by Nahimudin Ibrahim bin Hyder Ali
</div>
""", unsafe_allow_html=True)
