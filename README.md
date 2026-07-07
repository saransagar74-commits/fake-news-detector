# VeritasAI - Fake News Detection System

VeritasAI is a machine learning-powered web application designed to detect fake news, scan article credibility, and highlight sensationalized language using NLP.

## Core Features
- **Real-Time Classification**: Machine Learning-powered rating (TF-IDF + Logistic Regression) trained on standard corpora.
- **Credibility Index Dial**: Visual percentage representations showing the likelihood of article credibility.
- **Keyword-Impact Highlighter**: Marks language indicators color-coded by statistical significance (Green for Credible, Red for Sensational).
- **Interactive Model dashboard**: Model metrics (Accuracy, Precision, Recall) and top text feature weights displayed on demand.
- **URL Scraper**: Extracts article text directly from a URL.
- **Customizable theme**: Seamlessly togglable dark and light modes.

## Directory Structure
- `run.py`: Root runner script.
- `requirements.txt`: Project dependencies list.
- `backend/`: Flask routes and the machine learning model architecture.
- `frontend/`: Custom templates, CSS layout, and visual interactions.

## Installation & Execution

1. Clone or download this project, then open your terminal inside the root folder.
2. Initialize and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install package dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   python run.py
   ```
5. Navigate to `http://127.0.0.1:5000` in your web browser.
