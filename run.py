import os
import sys
import time
import webbrowser
from threading import Thread

# Ensure directory is in Python path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from model import NewsClassifier

def open_browser():
    # Wait for the Flask server to start up
    time.sleep(1.5)
    url = "http://127.0.0.1:5000"
    print(f"Opening browser to {url}...")
    webbrowser.open(url)

if __name__ == "__main__":
    print("====================================================")
    print("            VeritasAI News Detector                 ")
    print("====================================================")
    
    # 1. Initialize classifier & ensure it downloads dataset / runs training if empty
    print("Checking model status and datasets...")
    classifier = NewsClassifier()
    
    model_info = classifier.get_model_info()
    if not model_info.get("trained", False):
        print("Model not trained yet. Starting training cycle...")
        print("This will download the corpus (~30MB) or generate a fallback.")
        metrics = classifier.train()
        print(f"Training completed successfully. Model Accuracy: {metrics['accuracy']:.2%}")
    else:
        print(f"Loaded existing model. Current Accuracy: {model_info['metrics']['accuracy']:.2%}")
    
    # 2. Launch browser opening thread
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 3. Start Flask app
    print("Starting Flask web server...")
    from app import app
    app.run(host="127.0.0.1", port=5000, debug=False)
