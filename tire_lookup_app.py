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
.result-table { background-color: white; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); }
.table-header { background-color: #5C246E; color: white; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
.table-row { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; margin: 8px 0; padding: 12px; cursor: pointer; transition: all 0.3s ease; }
.table-row:hover { background-color: #e9ecef; transform: translateY(-2px); box-shadow: 0px 4px 8px rgba(0,0,0,0.1); }
.table-row.expanded { background-color: #fff3cd; border-color: #ffc107; }
.expanded-content { background-color: white; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 8px 8px; padding: 20px; margin-top: -8px; }
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
                    
                    # Initialize expanded state for each row
                    if "expanded_rows" not in st.session_state:
                        st.session_state.expanded_rows = {}
                    
                    # Create table view
                    st.markdown("""
                        <div class="result-table">
                            <div class="table-header">
                                <h4 style="margin:0; color:white;">📋 Search Results - Click any row to view details</h4>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, row in result.iterrows():
                        # Create unique key for each row
                        row_key = f"row_{idx}_{row.get('SN', '')}_{row.get('P/No', '')}"
                        
                        # Check if this row is expanded
                        is_expanded = st.session_state.expanded_rows.get(row_key, False)
                        
                        # Create row HTML
                        row_html = f"""
                        <div class="table-row {'expanded' if is_expanded else ''}" onclick="toggleRow('{row_key}')">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="flex: 1;">
                                    <strong>📅 Date In:</strong> {row.get('Date In','N/A')} | 
                                    <strong>📅 Date Out:</strong> {row.get('DATE OUT','N/A')} | 
                                    <strong>✈️ Ex-Aircraft:</strong> {row.get('Ex-Aircraft','N/A')}
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <strong>📋 Description:</strong> {row.get('Description','N/A')}
                                </div>
                                <div style="flex: 1; text-align: right;">
                                    <strong>📄 W/O No:</strong> {row.get('W/O No','N/A')} | 
                                    <strong>🧩 P/No:</strong> {row.get('P/No','N/A')} | 
                                    <strong>🔧 SN:</strong> {row.get('SN','N/A')}
                                </div>
                            </div>
                        </div>
                        """
                        
                        if is_expanded:
                            # Calculate usage for expanded content
                            max_cycles = 300
                            usage = (
                                min((row.get('Cycles Since Installed', 0) / max_cycles) * 100, 100)
                                if pd.notna(row.get('Cycles Since Installed'))
                                else 0
                            )
                            
                            # Color logic
                            if usage >= 90:
                                donut_color = "#FF0000"
                            elif usage >= 70:
                                donut_color = "#F5D104"
                            else:
                                donut_color = "#28A745"
                            
                            # Expanded content with chart
                            expanded_html = f"""
                            <div class="expanded-content" id="content_{row_key}">
                                <div style="display: flex; gap: 20px;">
                                    <div style="flex: 2;">
                                        <h4 style="color:#5C246E; margin-top:0;">📊 Detailed Information</h4>
                                        <p><b style="color:#5C246E;">🛠️ TC Remark:</b> {row.get('TC Remark','N/A')}</p>
                                        <p><b style="color:#5C246E;">📅 Removal Date:</b> {row.get('Removal Date','N/A')}</p>
                                        <p><b style="color:#5C246E;">🔢 AJL No:</b> {row.get('AJL No','N/A')}</p>
                                        <p><b style="color:#5C246E;">🔄 Cycles Since Installed:</b> {row.get('Cycles Since Installed','0')}</p>
                                        <p><b style="color:#5C246E;">📊 Usage:</b> {usage:.1f}% of {max_cycles} cycles</p>
                                    </div>
                                    <div style="flex: 1; text-align: center;">
                                        <div id="chart_{row_key}" style="width:100%;height:250px;"></div>
                                    </div>
                                </div>
                            </div>
                            """
                            
                            # Add chart JavaScript
                            chart_js = f"""
                            <script>
                            (function() {{
                                var usage = {json.dumps(usage)};
                                var donutColor = {json.dumps(donut_color)};
                                var chartDiv = document.getElementById('chart_{row_key}');
                                
                                if (chartDiv) {{
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
                                        annotations: [{{ text: '0%', x:0.5, y:0.5, font:{{size:16, color:'white'}}, showarrow:false }}],
                                        margin: {{t:0,b:0,l:0,r:0}},
                                        height: 200,
                                        width: 200,
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
                                                    annotations: [{{ text: i + '%', x:0.5, y:0.5, font:{{size:16, color:'white'}}, showarrow:false }}]
                                                }}
                                            }});
                                        }}
                                        
                                        var totalDuration = 600;
                                        var frameDuration = Math.max(6, Math.floor(totalDuration / Math.max(1, frames.length)));
                                        
                                        Plotly.animate(chartDiv, frames, {{
                                            transition: {{ duration: frameDuration, easing: 'cubic-in-out' }},
                                            frame: {{ duration: frameDuration, redraw: true }},
                                            mode: 'immediate'
                                        }});
                                    }});
                                }}
                            }})();
                            </script>
                            """
                            
                            row_html += expanded_html + chart_js
                        
                        st.markdown(row_html, unsafe_allow_html=True)
                    
                    # Add JavaScript for row toggling
                    st.markdown("""
                    <script>
                    function toggleRow(rowKey) {
                        // This will trigger a Streamlit rerun with the row key
                        // We'll use Streamlit's session state to handle this
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            key: 'toggle_row',
                            value: rowKey
                        }, '*');
                    }
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # Handle row toggling
                    if st.button("🔄 Refresh View", key="refresh_view"):
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
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
