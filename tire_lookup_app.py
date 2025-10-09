import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="TUMAS", page_icon="icon-192x192.png")
st.header("")
hide_st_style = """
              <style>
              #MainMenu {visiblity: hidden;}
              footer {visiblity: hidden;}
              header {visiblity: hidden;}
             </style>
             """

# --- Helper to load logo as base64 ---
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Logo file '{img_path}' not found.")
        return ""

logo_base64 = get_base64_image("batik_logo_transparent.png")

# --- Load user database ---
USERS_FILE = "users.xlsx"
try:
    users_df = pd.read_excel(USERS_FILE)
    users_df['Username'] = users_df['Username'].astype(str).str.strip()
    users_df['Password'] = users_df['Password'].astype(str).str.strip()
    USER_CREDENTIALS = dict(zip(users_df["Username"], users_df["Password"]))
except Exception as e:
    st.error(f"⚠️ Could not load '{USERS_FILE}': {e}")
    USER_CREDENTIALS = {}

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "selected_record" not in st.session_state:
    st.session_state.selected_record = None
if "search_results" not in st.session_state:
    st.session_state.search_results = pd.DataFrame()

# --- CSS Styling ---
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #5C246E, #C42454); background-attachment: fixed; }
section[data-testid="stSidebar"] { background-color: #5C246E !important; }
section[data-testid="stSidebar"] .stRadio label { color: white !important; font-weight: bold; }
.homepage-card, .result-card, .about-card {
    background-color: white;
    border-radius: 15px;
    padding: 30px;
    max-width: 850px;
    margin: 30px auto;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.15);
}
.homepage-card { text-align: center; margin-top: 60px; }
.about-card { margin-top: 60px; }
.homepage-title { font-size: 42px; font-family: "Arial", sans-serif; color: #5C246E; margin-bottom: 10px; }
.homepage-subtitle { font-size: 20px; color: #444444; margin-bottom: 30px; }
.cta-btn { background-color: #F5D104; color: #5C246E; font-size: 18px; padding: 12px 25px; border: none; border-radius: 8px; cursor:pointer; text-decoration: none; font-weight: bold; }
.cta-btn:hover { background-color: #e1c800; }
.footer { text-align: center; color: white; font-size: 14px; margin-top: 60px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    st.markdown(f"""
        <div style="text-align:center; margin-top:80px;">
            <img src="data:image/png;base64,{logo_base64}" width="200">
            <h1 style="color:white; font-family: Arial, sans-serif;">TIRE USAGE MONITORING APPLICATION SYSTEM</h1>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            username_input = username.strip()
            password_input = password.strip()

            if username_input in USER_CREDENTIALS:
                if USER_CREDENTIALS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
            else:
                st.error("❌ Username not found")

# --- MAIN APP AFTER LOGIN ---
else:
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <img src="data:image/png;base64,{logo_base64}" width="120">
            <h3 style='color:white;'>Welcome, {st.session_state.username} 👋</h3>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["Search", "About", "🔒 Logout"], horizontal=True)

    # --- Logout ---
    if page == "🔒 Logout":
        st.warning("⚠️ Are you sure you want to log out?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Yes, Log Out"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.stop()
        with col2:
            if st.button("❌ Cancel"):
                st.stop()

    # --- SEARCH PAGE ---
    elif page == "Search":
        st.subheader("🔍 Search Tire Record")
        FILE = "TUMAS-DATABASE.xlsx"

        try:
            df = pd.read_excel(FILE, sheet_name="Sheet1", header=0)
            df.columns = (
                df.columns.astype(str)
                .str.strip()
                .str.replace('"', '', regex=False)
                .str.replace("'", '', regex=False)
                .str.replace('\n', ' ', regex=False)
            )
        except Exception as e:
            st.error(f"⚠️ Could not load tire database: {e}")
            df = pd.DataFrame()

        if st.session_state.selected_record is None:
            with st.form("search_form"):
                st.markdown("Enter one or more search criteria below:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    serial = st.text_input("🔧 Serial Number (SN)")
                with col2:
                    part_no = st.text_input("🧩 Part Number (P/No)")
                with col3:
                    wo_no = st.text_input("📄 Work Order No (W/O No)")
                submitted = st.form_submit_button("Search")

            if submitted:
                if df.empty:
                    st.error("❌ Tire database is empty or not loaded.")
                else:
                    mask = pd.Series([True] * len(df))
                    if serial:
                        mask &= df['SN'].astype(str).str.contains(serial.strip(), case=False, na=False)
                    if part_no:
                        mask &= df['P/No'].astype(str).str.contains(part_no.strip(), case=False, na=False)
                    if wo_no:
                        mask &= df['W/O No'].astype(str).str.contains(wo_no.strip(), case=False, na=False)

                    result = df[mask]
                    st.session_state.search_results = result

            if not st.session_state.search_results.empty:
                result = st.session_state.search_results
                st.success(f"✅ Found {len(result)} matching record(s).")

                show_df = result[['Date In', 'Ex-Aircraft', 'Description', 'SN', 'P/No', 'W/O No']].copy()
                show_df.reset_index(drop=True, inplace=True)

                for i, row in show_df.iterrows():
                    cols = st.columns([2, 2, 3, 2, 2, 2, 1])
                    cols[0].write(row['Date In'])
                    cols[1].write(row['Ex-Aircraft'])
                    cols[2].write(row['Description'])
                    cols[3].write(row['SN'])
                    cols[4].write(row['P/No'])
                    cols[5].write(row['W/O No'])
                    if cols[6].button("Open", key=f"open_{i}"):
                        st.session_state.selected_record = result.iloc[i]
                        st.rerun()
            else:
                st.info("ℹ️ Enter one or more search fields above to find tire details.")

        else:
            # --- Show selected record details ---
            row = st.session_state.selected_record
            max_cycles = 300
            usage = (
                min((row.get('Cycles Since Installed', 0) / max_cycles) * 100, 100)
                if pd.notna(row.get('Cycles Since Installed'))
                else 0
            )
            donut_color = "#FF0000" if usage >= 90 else "#F5D104" if usage >= 70 else "#28A745"

            st.markdown(f"""
                <div class="result-card">
                    <h3 style="color:#5C246E;">{row.get('Description','N/A')}</h3>
                    <p><b style="color:#5C246E;">📆 Date In:</b> {row.get('Date In','N/A')}</p>
                    <p><b style="color:#5C246E;">📆 Date Out:</b> {row.get('DATE OUT','N/A')}</p>
                    <p><b style="color:#5C246E;">📋 W/O No:</b> {row.get('W/O No','N/A')}</p>
                    <p><b style="color:#5C246E;">🧩 Part No:</b> {row.get('P/No','N/A')}</p>
                    <p><b style="color:#5C246E;">🔧 Serial No:</b> {row.get('SN','N/A')}</p>
                    <p><b style="color:#5C246E;">🛠️ TC Remark:</b> {row.get('TC Remark','N/A')}</p>
                    <p><b style="color:#5C246E;">📅 Removal Date:</b> {row.get('Removal Date','N/A')}</p>
                    <p><b style="color:#5C246E;">✈️ Ex-Aircraft:</b> {row.get('Ex-Aircraft','N/A')}</p>
                    <p><b style="color:#5C246E;">🔢 AJL No:</b> {row.get('AJL No','N/A')}</p>
                    <p><b style="color:#5C246E;">🔄 Cycles Since Installed:</b> {row.get('Cycles Since Installed','0')}</p>
                    <p><b style="color:#5C246E;">📊 Usage:</b> {usage:.1f}% of {max_cycles} cycles</p>
                </div>
            """, unsafe_allow_html=True)

            # Donut chart
            chart_id = f"chart_{id(row)}"
            js_usage = json.dumps(usage)
            js_color = json.dumps(donut_color)
            html = f"""
<div id="{chart_id}" style="width:100%;height:300px;"></div>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
(function() {{
  var usage = {js_usage};
  var donutColor = {js_color};
  var chartDiv = document.getElementById('{chart_id}');
  var data = [
    {{ values: [1], type: 'pie', marker: {{ colors: ['black'] }}, textinfo: 'none', hoverinfo: 'skip', showlegend: false, sort: false }},
    {{ values: [0, 100], type: 'pie', hole: 0.7, marker: {{ colors: [donutColor, '#FFFFFF'] }}, textinfo: 'none', hoverinfo: 'skip', showlegend: false, sort: false }}
  ];
  var layout = {{ annotations: [{{ text: '0%', x:0.5, y:0.5, font:{{size:20, color:'white'}}, showarrow:false }}], margin: {{t:0,b:0,l:0,r:0}}, height: 250, width: 250, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)' }};
  Plotly.newPlot(chartDiv, data, layout, {{displayModeBar:false}}).then(function() {{
    var max = Math.round(Math.min(Math.max(usage,0),100));
    var frames = [];
    for (var i = 0; i <= max; i++) {{
    frames.push({{ name: 'f'+i, data: [{{{{ values:[1] }}}}, {{{{ values:[i,100-i] }}}}], layout: {{{{ annotations:[{{{{ text:i+'%', x:0.5, y:0.5, font:{{{{size:20, color:'white'}}}}, showarrow:false }}}}] }}}} }});
    Plotly.animate(chartDiv, frames, {{ transition: {{duration:10}}, frame: {{duration:10, redraw:true}}, mode:'immediate' }});
  }});
}})();
</script>
"""
            components.html(html, height=320)

            if st.button("⬅ Back to Table"):
                st.session_state.selected_record = None
                st.rerun()

    elif page == "About":
        st.markdown(f"""
            <div class="about-card">
                <img src="data:image/png;base64,{logo_base64}" width="150" style="display:block; margin:auto;">
                <h2 style="text-align:center; font-family: Arial, sans-serif; color:#5C246E;">About TUMS</h2>
                <p style="font-size:16px; color:#444444; text-align:justify;">
                    The <b>Tire Usage Monitoring System (TUMS)</b> is a digital solution developed for 
                    <b>Batik Air Technical Services • Support Workshop</b>.
                </p>
                <p style="font-size:16px; color:#444444; text-align:justify;">
                    It tracks tire cycles, retreads, and replacement history to optimize usage and minimize waste.
                </p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    © 2025 Batik Air • Technical Services • Support Workshop <br>
    Developed for Internship Project (TUMS)
</div>
""", unsafe_allow_html=True)

