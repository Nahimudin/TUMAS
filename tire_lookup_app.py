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

# Now we can safely call it
logo_base64 = get_base64_image("batik_logo_transparent.png")

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

/* minimal styles for clickable HTML table to match your app look */
.tumas-table { width: 100%; border-collapse: collapse; margin: 16px 0; background: rgba(255,255,255,0.95); border-radius: 8px; overflow: hidden; }
.tumas-table th, .tumas-table td { padding: 10px 12px; text-align: left; font-size: 14px; border-bottom: 1px solid #f0f0f0; }
.tumas-table thead { background: #fafafa; }
.tumas-row-link { display:block; color: inherit; text-decoration: none; width:100%; height:100%; }
.tumas-row-link:hover { background: rgba(196,36,84,0.03); }
.tumas-tr:hover { background: rgba(0,0,0,0.02); cursor: pointer; }
.small-muted { color:#666; font-size:13px; }
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
                df.columns
                .astype(str)
                .str.strip()
                .str.replace('"', '', regex=False)
                .str.replace("'", '', regex=False)
                .str.replace('\n', ' ', regex=False)
            )
        except Exception as e:
            st.error(f"⚠️ Could not load tire database: {e}")
            df = pd.DataFrame()

        # --- FILTER FORM ---
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

        # read selected query param (if user clicked a row before)
        query_params = st.experimental_get_query_params()
        selected_param = None
        if "selected" in query_params:
            try:
                selected_param = int(query_params["selected"][0])
            except Exception:
                selected_param = None

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

                result = df[mask].reset_index(drop=True)

                if not result.empty:
                    st.success(f"✅ Found {len(result)} matching record(s).")

                    # Build HTML clickable table (rows link to ?selected=index)
                    # Keep minimal styling so design remains identical
                    table_html = "<table class='tumas-table'>"
                    table_html += "<thead><tr>"
                    table_html += "<th>SN</th><th>P/No</th><th>W/O No</th><th>Ex-Aircraft</th><th>Cycles</th>"
                    table_html += "</tr></thead><tbody>"

                    for i, row in result.iterrows():
                        sn = str(row.get('SN', ''))
                        pno = str(row.get('P/No', ''))
                        wo = str(row.get('W/O No', ''))
                        exac = str(row.get('Ex-Aircraft', ''))
                        cycles = str(row.get('Cycles Since Installed', ''))

                        # link to same page with query param 'selected'
                        link = f"?selected={i}"
                        # full row as link
                        table_html += (
                            f"<tr class='tumas-tr'>"
                            f"<td><a class='tumas-row-link' href='{link}'>{sn}</a></td>"
                            f"<td><a class='tumas-row-link' href='{link}'>{pno}</a></td>"
                            f"<td><a class='tumas-row-link' href='{link}'>{wo}</a></td>"
                            f"<td><a class='tumas-row-link' href='{link}'>{exac}</a></td>"
                            f"<td><a class='tumas-row-link' href='{link}'>{cycles}</a></td>"
                            f"</tr>"
                        )

                    table_html += "</tbody></table>"

                    st.markdown(table_html, unsafe_allow_html=True)

                    # save result in session to use after navigation
                    st.session_state._last_search_result = result

                else:
                    st.error("❌ No matching records found.")
        else:
            # if user lands with selected param (clicked previously) but hasn't re-run search in this session,
            # try to load previous result from session_state to allow showing details below the table
            if selected_param is not None and "_last_search_result" in st.session_state:
                result = st.session_state._last_search_result
            else:
                result = None

        # --- Show detailed card below the table when a row is selected ---
        # selection comes from query param ?selected=<index>
        if selected_param is not None:
            # attempt to get the matching result set from session (if present)
            rs = None
            if "_last_search_result" in st.session_state:
                rs = st.session_state._last_search_result
            else:
                # fallback: try to run a full read of the sheet and pick the global index
                # (but this is only a fallback; ideally user clicked after a search so session has result)
                try:
                    full_df = pd.read_excel(FILE, sheet_name="Sheet1", header=0)
                    full_df.columns = (
                        full_df.columns
                        .astype(str)
                        .str.strip()
                        .str.replace('"', '', regex=False)
                        .str.replace("'", '', regex=False)
                        .str.replace('\n', ' ', regex=False)
                    )
                    # if we have a full df, then selected_param should refer to result index — cannot reliably map
                    rs = None
                except Exception:
                    rs = None

            if rs is not None:
                if 0 <= selected_param < len(rs):
                    row = rs.iloc[selected_param]

                    max_cycles = 300
                    usage = min((row.get('Cycles Since Installed', 0) / max_cycles) * 100, 100) if pd.notna(row.get('Cycles Since Installed')) else 0

                    # --- Traffic-light color logic ---
                    if usage >= 90:
                        donut_color = "#FF0000"  # red
                    elif usage >= 70:
                        donut_color = "#F5D104"  # yellow
                    else:
                        donut_color = "#28A745"  # green

                    st.markdown(f"<div style='height:12px'></div>", unsafe_allow_html=True)
                    col1, col2 = st.columns([2,1])
                    with col1:
                        st.markdown(f"""
                            <div class="result-card">
                                <h3 style="color:#5C246E;">{row.get('Description','N/A')}</h3>
                                <p><b style="color:#5C246E;">📆 Date In:</b> <span style="color:#000000;">{row.get('Date In','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📆 Date Out:</b> <span style="color:#000000;">{row.get('DATE OUT','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📆 RO Repair Order No:</b> <span style="color:#000000;">{row.get('RO Repair Order No','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📆 W/O No:</b> <span style="color:#000000;">{row.get('W/O No','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📆 Part No:</b> <span style="color:#000000;">{row.get('P/No','N/A')}</span></p>
                                <p><b style="color:#5C246E;">🔧 Serial No:</b> <span style="color:#000000;">{row.get('SN','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📆 TC Remark:</b> <span style="color:#000000;">{row.get('TC Remark','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📆 Removal Date:</b> <span style="color:#000000;">{row.get('Removal Date','N/A')}</span></p>
                                <p><b style="color:#5C246E;">📌 Ex-Aircraft:</b> <span style="color:#000000;">{row.get('Ex-Aircraft','N/A')}</span></p>
                                <p><b style="color:#5C246E;">🔧 AJL No:</b> <span style="color:#000000;">{row.get('AJL No','N/A')}</span></p>
                                <p><b style="color:#5C246E;">🔄 Cycles Since Installed:</b> <span style="color:#000000;">{row.get('Cycles Since Installed','0')}</span></p>
                                <p><b style="color:#5C246E;">📊 Usage:</b> <span style="color:#000000;">{usage:.1f}% of {max_cycles} cycles</span></p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        # --- Animated donut via embedded Plotly.js ---
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
                    st.error("⚠️ Selected record index is out of range.")
            else:
                st.error("⚠️ No saved search results available to display details. Please perform a search and then click a row to view details.")

    # --- ABOUT PAGE ---
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
