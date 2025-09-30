import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="My App", page_icon="🟣")

# --- Helper to load logo as base64 ---
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Logo file '{img_path}' not found.")
        return ""

logo_base64 = get_base64_image("batik_logo_transparent.png")

# ✅ NEW: load two app icons for PWA
icon192 = get_base64_image("icons/icon-192x192.png")
icon512 = get_base64_image("icons/icon-512x512.png")

# ✅ Inject manifest.json dynamically (so Streamlit can serve it)
manifest = f"""
{{
  "name": "Tire Usage Monitoring System",
  "short_name": "TUMS",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#5C246E",
  "icons": [
    {{
      "src": "data:image/png;base64,{icon192}",
      "sizes": "192x192",
      "type": "image/png"
    }},
    {{
      "src": "data:image/png;base64,{icon512}",
      "sizes": "512x512",
      "type": "image/png"
    }}
  ]
}}
"""

st.markdown(
    f"""
    <link rel="manifest" id="manifest-placeholder">
    <script>
    const manifest = {manifest};
    const blob = new Blob([JSON.stringify(manifest)], {{type: 'application/json'}});
    const manifestURL = URL.createObjectURL(blob);
    document.getElementById('manifest-placeholder').setAttribute('href', manifestURL);
    </script>
    """,
    unsafe_allow_html=True
)
