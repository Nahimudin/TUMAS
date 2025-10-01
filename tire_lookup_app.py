import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

# --- Helper to load logo as base64 ---
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Logo file '{img_path}' not found.")
        return ""

logo_base64 = get_base64_image("batik_logo_transparent.png")

# ✅ Build manifest as Python dict (using GitHub URLs for icons)
manifest_dict = {
    "name": "Tire Usage Monitoring System",
    "short_name": "TUMS",
    "start_url": "/?v=2",   # bump version to force refresh
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#5C246E",
    "orientation": "portrait",
    "icons": [
        {
            "src": "https://raw.githubusercontent.com/Nahimudin/TUMAS/main/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "https://raw.githubusercontent.com/Nahimudin/TUMAS/main/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# ✅ Convert to JSON safely
manifest_json = json.dumps(manifest_dict)

# ✅ Inject manifest dynamically into <head>
st.markdown(
    f"""
    <script>
        const manifest = {manifest_json};
        const blob = new Blob([JSON.stringify(manifest)], {{type: 'application/json'}});
        const manifestURL = URL.createObjectURL(blob);
        const manifestTag = document.createElement('link');
        manifestTag.rel = 'manifest';
        manifestTag.href = manifestURL;
        document.head.appendChild(manifestTag);
    </script>
    """,
    unsafe_allow_html=True
)
st.title("TUMAS - Batik Air")
st.write("✅ This version includes a custom app icon for Android Home Screen.")
st.write("Try adding this app to your Home Screen and check if the Batik Air logo shows.")
# --- Load user database from Excel ---
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
    # Header
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <img src="data:image/png;base64,{logo_base64}" width="120">
            <h3 style='color:white;'>Welcome, {st.session_state.username} 👋</h3>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["Search", "About", "🔒 Logout"], horizontal=True)

    # Logout
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

    # SEARCH PAGE
    elif page == "Search":
        st.subheader("🔍 Search Tire by Serial Number (S/N)")
        FILE = "TUMA dummy database.xlsx"

        try:
            df = pd.read_excel(FILE, sheet_name="Sheet1", header=1)
            df.columns = df.columns.str.strip().str.replace("\n"," ").str.replace("  "," ")
            df = df.rename(columns={df.columns[0]: "Installed Date"})
        except Exception as e:
            st.error(f"⚠️ Could not load tire database: {e}")
            df = pd.DataFrame()

        serial = st.text_input("Enter Tire Serial Number:")

        if serial:
            if not df.empty:
                result = df[df["S/N"].astype(str).str.contains(serial.strip(), case=False, na=False)]
                if not result.empty:
                    st.success(f"✅ Found {len(result)} record(s) for Serial: {serial.upper()}")
                    for _, row in result.iterrows():
                        max_cycles = 300
                        usage = min((row.get('Cycles Since Installed',0)/max_cycles)*100,100) if pd.notna(row.get('Cycles Since Installed')) else 0

                        if usage >= 90:
                            donut_color = "#FF0000"
                        elif usage >= 70:
                            donut_color = "#F5D104"
                        else:
                            donut_color = "#28A745"

                        col1, col2 = st.columns([2,1])
                        with col1:
                            st.markdown(f"""
                                <div class="result-card">
                                    <h3 style="color:#5C246E;">{row.get('Description','N/A')}</h3>
                                    <p><b style="color:#5C246E;">📌 Tire On:</b> <span style="color:#000000;">{row.get('Tire On','N/A')}</span></p>
                                    <p><b style="color:#5C246E;">🔧 Serial No:</b> <span style="color:#000000;">{row.get('S/N','N/A')}</span></p>
                                    <p><b style="color:#5C246E;">📆 Installed Date:</b> <span style="color:#000000;">{row.get('Installed Date','N/A')}</span></p>
                                    <p><b style="color:#5C246E;">🔄 Cycles Since Installed:</b> <span style="color:#000000;">{row.get('Cycles Since Installed','0')}</span></p>
                                    <p><b style="color:#5C246E;">♻️ Retread:</b> <span style="color:#000000;">{row.get('Retread','N/A')}</span></p>
                                    <p><b style="color:#5C246E;">📝 Remark:</b> <span style="color:#000000;">{row.get('Remark','None')}</span></p>
                                    <p><b style="color:#5C246E;">📊 Usage:</b> <span style="color:#000000;">{usage:.1f}% of {max_cycles} cycles</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                        with col2:
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
    {{
      values: [1],
      type: 'pie',
      marker: {{ colors: ['black'] }},
      textinfo: 'none',
      hoverinfo: 'skip',
      showlegend: false,
      sort: false
    }},
    {{
      values: [0, 100],
      type: 'pie',
      hole: 0.7,
      marker: {{ colors: [donutColor, '#FFFFFF'] }},
      textinfo: 'none',
      hoverinfo: 'skip',
      showlegend: false,
      sort: false
    }}
  ];

  var layout = {{
    annotations: [{{ text: '0%', x:0.5, y:0.5, font:{{size:20, color:'white'}}, showarrow:false }}],
    margin: {{t:0,b:0,l:0,r:0}},
    height: 250,
    width: 250,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  }};

  Plotly.newPlot(chartDiv, data, layout, {{displayModeBar:false}}).then(function() {{
    var max = Math.round(Math.min(Math.max(usage,0),100));
    var frames = [];
    for (var i = 0; i <= max; i++) {{
      frames.push({{
        name: 'f' + i,
        data: [
          {{ values: [1] }},
          {{ values: [i, 100 - i] }}
        ],
        layout: {{
          annotations: [{{ text: i + '%', x:0.5, y:0.5, font:{{size:20, color:'white'}}, showarrow:false }}]
        }}
      }});
    }}

    var totalDuration = 800;
    var frameDuration = Math.max(8, Math.floor(totalDuration / Math.max(1, frames.length)));

    Plotly.animate(chartDiv, frames, {{
      transition: {{ duration: frameDuration, easing: 'cubic-in-out' }},
      frame: {{ duration: frameDuration, redraw: true }},
      mode: 'immediate'
    }});
  }});
}})();
</script>
"""
                            components.html(html, height=320)
                else:
                    st.error("❌ No tire found with that Serial Number.")
            else:
                st.error("❌ Tire database is empty.")
        else:
            st.info("ℹ️ Please enter a Serial Number above to search for tire details.")

    # ABOUT PAGE
    elif page == "About":
        st.markdown(f"""
            <div class="about-card">
                <img src="data:image/png;base64,{logo_base64}" width="150" style="display:block; margin:auto;">
                <h2 style="text-align:center; font-family: Arial, sans-serif; color:#5C246E;">About TUMS</h2>
                <p style="font-size:16px; color:#444444; text-align:justify;">
                    The <b>Tire Usage Monitoring System (TUMS)</b> is a digital solution developed for 
                    <b>Batik Air Technical Services • Support Workshop</b>. Its main purpose is to 
                    maximize the usage of aircraft tires by tracking cycles, retreads, and replacement 
                    history in a structured way.
                </p>
                <p style="font-size:16px; color:#444444; text-align:justify;">
                    This system was built as part of an <b>Internship Project (2025)</b> with the goal 
                    of modernizing tire management and reducing unnecessary replacements.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    © 2025 Batik Air • Technical Services • Support Workshop <br>
    Developed for Internship Project (TUMS)
</div>
""", unsafe_allow_html=True)

