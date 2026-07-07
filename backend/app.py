import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from model import NewsClassifier

app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')),
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')))

# Initialize model
classifier = NewsClassifier()

# Helper: Scrape URL text
def scrape_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Add a short timeout to prevent blocking
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code != 200:
            return None
            
        html = response.text
        # Remove head, scripts, styles
        html = re.sub(r'<head.*?>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Find paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean paragraph text
        cleaned_paragraphs = []
        for p in paragraphs:
            # Remove inline tags e.g., <a>, <strong>
            p_clean = re.sub(r'<[^>]+>', '', p)
            p_clean = re.sub(r'\s+', ' ', p_clean).strip()
            if len(p_clean) > 20: # skip empty or tiny lines
                cleaned_paragraphs.append(p_clean)
                
        text = " ".join(cleaned_paragraphs)
        return text if len(text) > 100 else None
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json() or {}
    text = data.get('text', '')
    url = data.get('url', '')
    
    if url:
        print(f"Fetching content from URL: {url}")
        scraped_text = scrape_url(url)
        if not scraped_text:
            return jsonify({
                "success": False,
                "error": "Could not extract sufficient text from the provided URL. Please copy and paste the article text directly."
            }), 400
        text = scraped_text
        
    if not text or len(text.strip()) < 50:
        return jsonify({
            "success": False,
            "error": "Please provide a longer text (at least 50 characters) or a valid article URL."
        }), 400
        
    try:
        result = classifier.predict(text)
        # If text was scraped from URL, return first 500 chars to show the user what was parsed
        result["scraped_preview"] = text[:500] + "..." if url else None
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error running classification: {str(e)}"
        }), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    try:
        info = classifier.get_model_info()
        return jsonify({
            "success": True,
            "data": info
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    try:
        # Train model synchronously for simplicity, but let's make it quick
        metrics = classifier.train()
        info = classifier.get_model_info()
        return jsonify({
            "success": True,
            "metrics": metrics,
            "info": info
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Make sure model is trained at startup
    classifier.load_model()
    app.run(debug=True, port=5000)
