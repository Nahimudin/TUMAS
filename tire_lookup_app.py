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
# New state for storing search results and selected item
if "search_results" not in st.session_state:
    st.session_state.search_results = pd.DataFrame()
if "selected_sn_wo" not in st.session_state:
    st.session_state.selected_sn_wo = None # Stores (SN, W/O No, index) to uniquely identify a record


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

/* Custom style for the summary table background and font */
.stDataFrame {
    background-color: white !important;
}
.stDataFrame table {
    color: black !important;
    background-color: white !important;
}
.stDataFrame th {
    color: white !important;
    background-color: #5C246E !important; /* Header background color */
}
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
        # Reset search state on logout
        st.session_state.search_results = pd.DataFrame()
        st.session_state.selected_sn_wo = None
        
        st.warning("⚠️ Are you sure you want to log out?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Yes, Log Out"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.rerun() # Use rerun instead of stop to force full page reload to login
        with col2:
            if st.button("❌ Cancel"):
                # Just re-display the search page
                st.session_state.page = "Search"
                st.rerun()
    # --- SEARCH PAGE ---
    elif page == "Search":
        st.session_state.selected_sn_wo = None # Ensure nothing is selected when returning to search form
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
            # Clear previous selected record and results
            st.session_state.selected_sn_wo = None
            st.session_state.search_results = pd.DataFrame()

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
                st.session_state.search_results = result # Store full result set in session state

                if st.session_state.search_results.empty:
                    st.error("❌ No matching records found.")
                else:
                    st.success(f"✅ Found {len(st.session_state.search_results)} matching record(s).")

                    # --- Display Summary Table ---
                    st.markdown("---")
                    st.subheader("Results Summary")

                    # Define columns to display in the summary table
                    display_cols = ['Date In', 'DATE OUT', 'Ex-Aircraft', 'Description', 'W/O No', 'P/No', 'SN']
                    summary_df = st.session_state.search_results[display_cols].copy()
                    
                    # Convert date columns for cleaner display if they are datetime objects
                    for col in ['Date In', 'DATE OUT']:
                        if col in summary_df.columns:
                            try:
                                summary_df[col] = pd.to_datetime(summary_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                            except:
                                pass # Keep as is if conversion fails

                    st.dataframe(
                        summary_df, 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.markdown("---")

                    # Add 'Open' buttons for each row
                    st.subheader("Select Record for Detail")
                    
                    # Create a unique key for the button using SN and W/O No (and index for safety)
                    for i, row in st.session_state.search_results.iterrows():
                        key = f"open_btn_{i}"
                        
                        col_sn, col_wo, col_desc, col_btn = st.columns([1, 1, 3, 0.5])
                        
                        # Display the key identifier for context
                        with col_sn:
                            st.markdown(f"**SN:** `{row.get('SN', 'N/A')}`", help="Serial Number")
                        with col_wo:
                            st.markdown(f"**W/O No:** `{row.get('W/O No', 'N/A')}`", help="Work Order Number")
                        with col_desc:
                            st.markdown(f"**Desc:** `{row.get('Description', 'N/A')}`", help="Description")

                        with col_btn:
                            if st.button("Open ➡️", key=key):
                                # Store a tuple to uniquely identify the selected record: (SN, W/O No, index)
                                st.session_state.selected_sn_wo = (row.get('SN'), row.get('W/O No'), i)
                                st.rerun()

        # --- Display Detailed Card if a record is selected ---
        if st.session_state.selected_sn_wo:
            # Re-read the stored results
            result = st.session_state.search_results
            
            # Use the stored index to find the row
            selected_index = st.session_state.selected_sn_wo[2]
            
            # Check if index is valid (important for re-runs)
            if 0 <= selected_index < len(result):
                row = result.iloc[selected_index]
                
                # --- Detailed Card Logic (unchanged from original) ---
                max_cycles = 300
                usage = (
                    min((row.get('Cycles Since Installed', 0) / max_cycles) * 100, 100)
                    if pd.notna(row.get('Cycles Since Installed'))
                    else 0
                )

                # --- Color logic ---
                if usage >= 90:
                    donut_color = "#FF0000"
                elif usage >= 70:
                    donut_color = "#F5D104"
                else:
                    donut_color = "#28A745"

                st.markdown("---")
                st.subheader("Detailed Record View")

                col1, col2 = st.columns([2, 1])
                with col1:
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

                with col2:
                    chart_id = f"chart_{selected_index}"
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
                st.error("❌ Error retrieving selected record details.")
        
        elif not submitted: # Show info only if not submitted and no selection
            st.info("ℹ️ Enter one or more search fields above to find tire details.")

    # --- ABOUT PAGE ---
    elif page == "About":
        # Clear search state when navigating away
        st.session_state.search_results = pd.DataFrame()
        st.session_state.selected_sn_wo = None
        
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
