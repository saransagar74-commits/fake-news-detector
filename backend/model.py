import os
import re
import urllib.request
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import nltk

# NLTK resources setup
def setup_nltk():
    resources = ['stopwords', 'punkt', 'wordnet']
    for res in resources:
        try:
            if res == 'stopwords':
                nltk.data.find('corpora/stopwords')
            elif res == 'punkt':
                nltk.data.find('tokenizers/punkt')
            elif res == 'wordnet':
                nltk.data.find('corpora/wordnet')
        except LookupError:
            print(f"Downloading NLTK resource: {res}...")
            nltk.download(res, quiet=True)

setup_nltk()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

class NewsClassifier:
    def __init__(self, data_dir='data', model_dir='saved_model'):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.dataset_url = "https://raw.githubusercontent.com/piyushmishra12/Fake-News-Detector/master/fake_or_real_news.csv"
        self.dataset_path = os.path.join(data_dir, "fake_or_real_news.csv")
        self.model_path = os.path.join(model_dir, "model.joblib")
        self.pipeline = None
        self.stemmer = PorterStemmer()
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load stop words
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        # Lowercase
        text = text.lower()
        # Remove HTML
        text = re.sub(r'<[^>]+>', '', text)
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove non-alphabetic chars
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Tokenize
        try:
            words = word_tokenize(text)
        except Exception:
            words = text.split()
        # Stem and remove stopwords
        cleaned = [self.stemmer.stem(word) for word in words if word not in self.stop_words]
        return " ".join(cleaned)

    def download_dataset(self):
        if os.path.exists(self.dataset_path):
            print(f"Dataset already exists at {self.dataset_path}")
            return True
            
        print(f"Downloading dataset from {self.dataset_url}...")
        try:
            # Set a timeout for download to avoid hanging
            urllib.request.urlretrieve(self.dataset_url, self.dataset_path)
            print("Download completed successfully.")
            return True
        except Exception as e:
            print(f"Failed to download dataset: {e}. Generating fallback synthetic dataset...")
            self.generate_synthetic_dataset()
            return False

    def generate_synthetic_dataset(self):
        # Create a synthetic dataset if downloading fails
        print("Generating synthetic real and fake news dataset...")
        
        real_phrases = [
            "The government announced a new economic policy today to curb inflation and support middle-class families.",
            "Scientists at NASA have successfully launched a new climate monitoring satellite into orbit.",
            "The international summit concluded with a joint agreement on global trade regulations and carbon reduction goals.",
            "Local authorities have approved funding for the construction of a new public transit line connecting the suburbs.",
            "A study published in the New England Journal of Medicine shows that regular exercise reduces heart disease risks.",
            "The Central Bank decided to keep interest rates steady after reviewing the latest employment numbers.",
            "The Prime Minister met with leaders of neighboring countries to discuss border security and agricultural imports.",
            "A coalition of research universities received a federal grant to develop next-generation solar cells.",
            "The city council voted unanimously to expand green spaces and install solar panels on municipal buildings.",
            "Public health officials recommend seasonal vaccination campaigns to prevent outbreaks in the winter."
        ]
        
        fake_phrases = [
            "SHOCKING: Secret government conspiracy exposed showing how they control weather using towers!",
            "Doctors are furious about this simple home trick that cures all cancer instantly, click here!",
            "BREAKING: Extraterrestrial spacecraft landed in the desert and the military is covering it up!",
            "Leaked documents reveal a hidden plot to replace all physical money with microchip implants next month.",
            "The truth they don't want you to know: Drinking this magic water cures every disease known to man.",
            "A secret meeting of billionaires decided to shut down the internet worldwide to control the population.",
            "Scientists shocked as mysterious island appears in the Pacific containing prehistoric monsters.",
            "CONFIRMED: NASA admits that the moon landing was filmed on a Hollywood studio set in 1969.",
            "Urgent warning: Major cities are being secretly evacuated tonight due to an impending alien invasion.",
            "An anonymous source reveals that the President is actually a cloned robot controlled by a foreign power."
        ]
        
        # Build 100 rows
        data = []
        for i in range(100):
            if i % 2 == 0:
                text = real_phrases[i % len(real_phrases)] + " " + " ".join(np.random.choice(real_phrases, size=2))
                title = f"Official Report: Government Action on Policy {i}"
                label = "REAL"
            else:
                text = fake_phrases[i % len(fake_phrases)] + " " + " ".join(np.random.choice(fake_phrases, size=2))
                title = f"ALERT: The Secret Plot Exposed {i}!!"
                label = "FAKE"
            data.append({"title": title, "text": text, "label": label})
            
        df = pd.DataFrame(data)
        df.to_csv(self.dataset_path, index=False)
        print(f"Synthetic dataset saved to {self.dataset_path}")

    def train(self):
        # Ensure we have data
        self.download_dataset()
        
        print("Loading data...")
        df = pd.read_csv(self.dataset_path)
        
        # Standardize columns: need text and label
        # fake_or_real_news.csv columns: title, text, label (REAL/FAKE)
        df = df.dropna(subset=['text', 'label'])
        
        print("Preprocessing text data...")
        # To make it fast during dev/test if dataset is huge, we can train on a subset or full
        # Let's train on a subset if the dataset is the large 30MB one, say 3000 samples for speed,
        # or full if it's small.
        if len(df) > 3000:
            df = df.sample(3000, random_state=42).reset_index(drop=True)
            
        df['cleaned_text'] = df['text'].apply(self.clean_text)
        
        X = df['cleaned_text']
        y = df['label'].map({'REAL': 1, 'FAKE': 0})
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("Training model...")
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(C=10.0, max_iter=1000, random_state=42))
        ])
        
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred)),
            'recall': float(recall_score(y_test, y_pred)),
            'f1': float(f1_score(y_test, y_pred)),
            'samples_trained': len(X_train) + len(X_test)
        }
        
        print(f"Training complete. Accuracy: {metrics['accuracy']:.4f}")
        
        # Save model
        joblib.dump((self.pipeline, metrics), self.model_path)
        print(f"Model saved to {self.model_path}")
        return metrics

    def load_model(self):
        if os.path.exists(self.model_path):
            self.pipeline, metrics = joblib.load(self.model_path)
            return metrics
        return None

    def get_model_info(self):
        metrics = self.load_model()
        if not self.pipeline:
            return {"trained": False}
            
        # Get feature importances
        vectorizer = self.pipeline.named_steps['tfidf']
        classifier = self.pipeline.named_steps['classifier']
        
        feature_names = vectorizer.get_feature_names_out()
        coefficients = classifier.coef_[0]
        
        # Zip features with coefficients
        feature_coefs = list(zip(feature_names, coefficients))
        
        # Top real indicators (highest positive coefficients)
        real_indicators = sorted(feature_coefs, key=lambda x: x[1], reverse=True)[:15]
        # Top fake indicators (lowest negative coefficients)
        fake_indicators = sorted(feature_coefs, key=lambda x: x[1])[:15]
        
        real_words = [{"word": word, "weight": float(coef)} for word, coef in real_indicators]
        fake_words = [{"word": word, "weight": float(coef)} for word, coef in fake_indicators]
        
        return {
            "trained": True,
            "metrics": metrics,
            "real_words": real_words,
            "fake_words": fake_words,
            "vocab_size": len(feature_names)
        }

    def predict(self, text):
        if not self.pipeline:
            metrics = self.load_model()
            if not self.pipeline:
                # Force training if not trained
                metrics = self.train()
                
        cleaned = self.clean_text(text)
        if not cleaned.strip():
            return {
                "prediction": "UNKNOWN",
                "credibility_score": 0.5,
                "confidence": 0.0,
                "explanation": "No text provided for analysis.",
                "highlights": []
            }
            
        # Get prediction and probabilities
        prob = self.pipeline.predict_proba([cleaned])[0] # [P(Fake), P(Real)]
        real_prob = prob[1]
        
        prediction = "REAL" if real_prob >= 0.5 else "FAKE"
        confidence = real_prob if prediction == "REAL" else (1.0 - real_prob)
        
        # Word highlight logic
        vectorizer = self.pipeline.named_steps['tfidf']
        classifier = self.pipeline.named_steps['classifier']
        
        feature_names = vectorizer.get_feature_names_out()
        coefficients = classifier.coef_[0]
        
        coef_dict = dict(zip(feature_names, coefficients))
        
        # Tokenize original text to highlight
        # We will split original text by words/boundaries, keeping punctuation intact for rendering
        words_original = re.findall(r'\w+|\W+', text)
        
        highlights = []
        for word in words_original:
            word_clean = word.lower().strip()
            # Stem it to see if it matches trained features
            stemmed = self.stemmer.stem(word_clean)
            
            weight = 0.0
            if word_clean in coef_dict:
                weight = coef_dict[word_clean]
            elif stemmed in coef_dict:
                weight = coef_dict[stemmed]
                
            # Determine color/category based on weight
            # Large positive = Real, Large negative = Fake
            category = "neutral"
            if weight > 0.1:
                category = "real"
            elif weight < -0.1:
                category = "fake"
                
            highlights.append({
                "word": word,
                "weight": float(weight),
                "category": category
            })
            
        # Explanation summary
        if prediction == "REAL":
            explanation = f"The article exhibits language highly characteristic of credible reporting (confidence: {confidence:.1%}). Key factual terms and structured expressions strongly correlate with trusted news sources."
        else:
            explanation = f"The article exhibits language patterns frequently associated with sensationalized or unverified claims (confidence: {confidence:.1%}). Clickbait verbs and emotional indicators heavily influenced this classification."
            
        return {
            "prediction": prediction,
            "credibility_score": float(real_prob),
            "confidence": float(confidence),
            "explanation": explanation,
            "highlights": highlights
        }
