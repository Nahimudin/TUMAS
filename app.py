from flask import Flask, send_from_directory, redirect
import subprocess
import threading

app = Flask(__name__)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/icons/<filename>')
def icons(filename):
    return send_from_directory('icons', filename)

@app.route('/')
def index():
    return redirect("http://localhost:8501")  # Redirect to Streamlit

def run_streamlit():
    subprocess.Popen(["streamlit", "run", "streamlit_app.py", "--server.port", "8501"])

if __name__ == '__main__':
    threading.Thread(target=run_streamlit).start()
    app.run(host="0.0.0.0", port=10000)