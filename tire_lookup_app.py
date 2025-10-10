
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

                if not result.empty:
                    st.success(f"✅ Found {len(result)} matching record(s).")
                    
                    # Create table data
                    table_data = []
                    for idx, row in result.iterrows():
                        # Format dates properly
                        date_in = str(row.get('Date In', 'N/A'))
                        if 'T' in date_in:
                            date_in = date_in.split('T')[0]
                        elif ' ' in date_in:
                            date_in = date_in.split(' ')[0]
                        
                        date_out = str(row.get('DATE OUT', 'N/A'))
                        if 'T' in date_out:
                            date_out = date_out.split('T')[0]
                        elif ' ' in date_out:
                            date_out = date_out.split(' ')[0]
                        
                        table_data.append({
                            'Seq. No': row.get('Seq. No', idx + 1),
                            'Date In': date_in,
                            'DATE OUT': date_out,
                            'W/O No': row.get('W/O No', 'N/A'),
                            'Description': row.get('Description', 'N/A'),
                            'P/No': row.get('P/No', 'N/A'),
                            'SN': row.get('SN', 'N/A'),
                            'Ex-Aircraft': row.get('Ex-Aircraft', 'N/A')
                        })
                    
                    # Display the table using Streamlit's native dataframe
                    table_df = pd.DataFrame(table_data)
                    st.dataframe(table_df, use_container_width=True, hide_index=True)
                    
                    # Add "open" buttons for each row below the table
                    st.markdown("**Click to view details:**")
                    
                    # Create buttons in a grid layout
                    num_buttons_per_row = 5
                    for i in range(0, len(table_data), num_buttons_per_row):
                        cols = st.columns(num_buttons_per_row)
                        for j, col in enumerate(cols):
                            if i + j < len(table_data):
                                with col:
                                    aircraft = table_data[i + j]['Ex-Aircraft']
                                    if st.button(f"open {aircraft}", key=f"open_{i + j}"):
                                        # Get the original row data
                                        original_row = result.iloc[i + j]
                                        
                                        # Calculate usage
                                        max_cycles = 300
                                        usage = (
                                            min((original_row.get('Cycles Since Installed', 0) / max_cycles) * 100, 100)
                                            if pd.notna(original_row.get('Cycles Since Installed'))
                                            else 0
                                        )
                                        
                                        # Color logic
                                        if usage >= 90:
                                            donut_color = "#FF0000"
                                        elif usage >= 70:
                                            donut_color = "#F5D104"
                                        else:
                                            donut_color = "#28A745"
                                        
                                        # Display full details
                                        st.markdown("---")
                                        st.markdown("### 📊 Detailed Information")
                                        
                                        col1, col2 = st.columns([2, 1])
                                        with col1:
                                            st.markdown(f"""
                                                <div class="result-card">
                                                    <h3 style="color:#5C246E;">{original_row.get('Description','N/A')}</h3>
                                                    <p><b style="color:#5C246E;">Date In:</b> {original_row.get('Date In','N/A')}</p>
                                                    <p><b style="color:#5C246E;">Date Out:</b> {original_row.get('DATE OUT','N/A')}</p>
                                                    <p><b style="color:#5C246E;">W/O No:</b> {original_row.get('W/O No','N/A')}</p>
                                                    <p><b style="color:#5C246E;">Part No:</b> {original_row.get('P/No','N/A')}</p>
                                                    <p><b style="color:#5C246E;">Serial No:</b> {original_row.get('SN','N/A')}</p>
                                                    <p><b style="color:#5C246E;">TC Remark:</b> {original_row.get('TC Remark','N/A')}</p>
                                                    <p><b style="color:#5C246E;">Removal Date:</b> {original_row.get('Removal Date','N/A')}</p>
                                                    <p><b style="color:#5C246E;">Ex-Aircraft:</b> {original_row.get('Ex-Aircraft','N/A')}</p>
                                                    <p><b style="color:#5C246E;">AJL No:</b> {original_row.get('AJL No','N/A')}</p>
                                                    <p><b style="color:#5C246E;">Cycles Since Installed:</b> {original_row.get('Cycles Since Installed','0')}</p>
                                                    <p><b style="color:#5C246E;">Usage:</b> {usage:.1f}% of {max_cycles} cycles</p>
                                                </div>
                                            """, unsafe_allow_html=True)
                                        
                                        with col2:
                                            chart_id = f"chart_{i + j}_{id(original_row)}"
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
                    st.error("❌ No matching records found.")
        else:
            st.info("ℹ️ Enter one or more search fields above to find tire details.")

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
The table will now display correctly as a proper table with black text on white background, and the "open" buttons below will work to show the detailed information with the usage chart.
