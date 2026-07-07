// VeritasAI Frontend JavaScript

// Global state
let currentTab = 'detector';
let inputMode = 'text'; // 'text' or 'url'

// Sample articles database
const sampleArticles = {
    1: {
        title: "Global Climate Research Study",
        text: "Scientists have successfully deployed advanced marine sensors to monitor global ocean current velocities. The newly compiled data, gathered over a seven-year collaborative project across five international oceanographic institutes, indicates a steady and measurable shift in deep-sea thermal regulation. According to the official report published in the Journal of Earth Sciences, researchers observed temperature fluctuations that correlate closely with atmospheric models. The study emphasizes the critical role of systematic oceanic data collection to support municipal climate adaptation planning. Local authorities have already begun incorporating these findings into coastal development programs to prepare for rising sea levels and shifting weather patterns."
    },
    2: {
        title: "Central Bank Interest Rate Adjustments",
        text: "The Federal Reserve has officially voted to maintain baseline interest rates following an intensive review of national labor market indicators. In a public statement delivered by the chairman this morning, the monetary policy committee confirmed that employment rates have stabilized alongside moderate economic growth. Economists report that the decision to hold interest rates steady reflects a cautious approach to balancing price stability and sustainable job creation. Financial analysts expect minor adjustments in the coming quarters depending on future consumer price index statistics. The official treasury statement reiterates the bank's long-term commitment to keeping inflation near its target rate of two percent."
    },
    3: {
        title: "SHOCKING SECRET: Weather Control Towers exposed!",
        text: "UNBELIEVABLE! Secret government documents leaked from deep underground command bunkers confirm they are controlling storms using massive energy rays! Insider whistleblowers have revealed that recent massive hurricanes were actually created in a lab and directed at major cities by greedy elites to control the population. The media is totally silent about this shocking global weather control conspiracy. Share this article immediately before it gets deleted by the authorities! We must expose the truth! Mysterious towers are being built in every neighborhood to manipulate the climate and force citizens to submit to their control. Wake up, they are lying to us!"
    },
    4: {
        title: "Doctors Furious! Simple Remedy Cures All Diseases",
        text: "BIG PHARMA IS PANICKING! An anonymous medical researcher has discovered a rare, secret herbal liquid that completely cures cancer, diabetes, and heart disease overnight. Doctors are absolutely furious because this simple, cheap trick will destroy their multi-billion dollar business! This magic potion is being covered up by the medical establishment to keep you sick. Click this link immediately to buy your supply of the miracle cure before it is banned forever! Thousands of patients have been completely cured in secret trials, but the government is trying to silence the truth. Do not trust your physician, they are hiding this from you!"
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Get initial model info
    fetchModelInfo();
    
    // Setup text-area word counter
    const textarea = document.getElementById('text-input');
    textarea.addEventListener('input', updateWordCount);
    
    // Theme toggle setup
    const themeBtn = document.getElementById('theme-toggle-btn');
    themeBtn.addEventListener('click', toggleTheme);
    
    // Check saved theme
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-mode');
        themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }
});

// Theme Management
function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('theme-toggle-btn');
    
    if (body.classList.contains('light-mode')) {
        body.classList.remove('light-mode');
        themeBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
        localStorage.setItem('theme', 'dark');
    } else {
        body.classList.add('light-mode');
        themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
        localStorage.setItem('theme', 'light');
    }
}

// Tab Switch Management
function switchTab(tabId) {
    // Deactivate previous tab
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    // Activate new tab
    document.getElementById(`tab-${tabId}`).classList.remove('hidden');
    document.getElementById(`nav-btn-${tabId}`).classList.add('active');
    
    currentTab = tabId;
    
    // Update headers based on active tab
    const title = document.getElementById('page-title');
    const subtitle = document.getElementById('page-subtitle');
    
    if (tabId === 'detector') {
        title.innerText = 'Credential Analyzer';
        subtitle.innerText = 'Scan articles for misinformation using NLP & Machine Learning';
    } else if (tabId === 'insights') {
        title.innerText = 'Model Insights';
        subtitle.innerText = 'Explore the classifier parameters and predictive keywords';
        // Refresh metrics whenever they click on Insights
        fetchModelInfo();
    } else if (tabId === 'samples') {
        title.innerText = 'Quick-Test Library';
        subtitle.innerText = 'Preloaded articles to verify classifier responses';
    }
}

// Input Mode Toggles (Text vs. URL)
function setInputMode(mode) {
    inputMode = mode;
    
    const textToggle = document.getElementById('mode-text-btn');
    const urlToggle = document.getElementById('mode-url-btn');
    const textContainer = document.getElementById('container-text');
    const urlContainer = document.getElementById('container-url');
    
    if (mode === 'text') {
        textToggle.classList.add('active');
        urlToggle.classList.remove('active');
        textContainer.classList.remove('hidden');
        urlContainer.classList.add('hidden');
    } else {
        textToggle.classList.remove('active');
        urlToggle.classList.add('active');
        textContainer.classList.add('hidden');
        urlContainer.classList.remove('hidden');
    }
}

// Word Counter
function updateWordCount() {
    const text = document.getElementById('text-input').value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    document.getElementById('word-count').innerText = `${words} word${words !== 1 ? 's' : ''}`;
}

// Clear Inputs
function clearInput() {
    document.getElementById('text-input').value = '';
    document.getElementById('url-input').value = '';
    updateWordCount();
    
    // Reset results panel back to empty state
    const resultsPanel = document.getElementById('panel-results');
    resultsPanel.classList.add('empty');
    document.getElementById('results-empty').classList.remove('hidden');
    document.getElementById('results-active').classList.add('hidden');
}

// Run Analysis Request
async function runAnalysis() {
    const textInput = document.getElementById('text-input').value.trim();
    const urlInput = document.getElementById('url-input').value.trim();
    
    let payload = {};
    if (inputMode === 'text') {
        if (!textInput || textInput.length < 50) {
            showToast('Please provide a news article text of at least 50 characters.', 'error');
            return;
        }
        payload = { text: textInput };
    } else {
        if (!urlInput || !urlInput.startsWith('http')) {
            showToast('Please enter a valid URL (starting with http:// or https://).', 'error');
            return;
        }
        payload = { url: urlInput };
    }
    
    // Show Loading
    setLoadingState(true);
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.success) {
            renderResults(result.data);
            showToast('Analysis completed successfully!', 'success');
        } else {
            showToast(result.error || 'Failed to analyze content.', 'error');
        }
    } catch (err) {
        showToast('Error connecting to the server.', 'error');
        console.error(err);
    } finally {
        setLoadingState(false);
    }
}

// Set UI Loading State
function setLoadingState(isLoading) {
    const analyzeBtn = document.getElementById('analyze-btn');
    const loader = document.getElementById('analyze-loader');
    const icon = document.getElementById('analyze-icon');
    const textarea = document.getElementById('text-input');
    const urlInput = document.getElementById('url-input');
    
    if (isLoading) {
        analyzeBtn.disabled = true;
        loader.classList.remove('hidden');
        icon.classList.add('hidden');
        textarea.disabled = true;
        urlInput.disabled = true;
    } else {
        analyzeBtn.disabled = false;
        loader.classList.add('hidden');
        icon.classList.remove('hidden');
        textarea.disabled = false;
        urlInput.disabled = false;
    }
}

// Render Results to UI
function renderResults(data) {
    const resultsPanel = document.getElementById('panel-results');
    const emptyState = document.getElementById('results-empty');
    const activeState = document.getElementById('results-active');
    
    // Switch states
    resultsPanel.classList.remove('empty');
    emptyState.classList.add('hidden');
    activeState.classList.remove('hidden');
    
    // 1. Verdict card classes and labels
    const verdictCard = document.getElementById('verdict-card');
    const verdictBadge = document.getElementById('verdict-badge');
    const verdictConfidence = document.getElementById('verdict-confidence');
    const verdictIconContainer = document.getElementById('verdict-icon-container');
    
    verdictCard.className = 'verdict-banner'; // reset
    if (data.prediction === 'REAL') {
        verdictCard.classList.add('real');
        verdictBadge.innerText = 'Verified Credible';
        verdictConfidence.innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        verdictIconContainer.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
    } else {
        verdictCard.classList.add('fake');
        verdictBadge.innerText = 'Suspected Sensational/Fake';
        verdictConfidence.innerText = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        verdictIconContainer.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
    }
    
    // 2. Circular Gauge
    const gaugeValue = document.getElementById('gauge-value');
    const gaugeRating = document.getElementById('gauge-rating');
    const gaugeRing = document.getElementById('gauge-fill-ring');
    
    const percentage = Math.round(data.credibility_score * 100);
    gaugeValue.innerText = `${percentage}%`;
    
    // Set text rating and coloring
    if (percentage >= 70) {
        gaugeRating.innerText = 'HIGHLY CREDIBLE';
        gaugeRating.style.color = 'var(--real-color)';
        gaugeRing.style.stroke = 'var(--real-color)';
    } else if (percentage >= 40) {
        gaugeRating.innerText = 'MIXED CONTENT';
        gaugeRating.style.color = 'var(--warning-color)';
        gaugeRing.style.stroke = 'var(--warning-color)';
    } else {
        gaugeRating.innerText = 'LOW CREDIBILITY';
        gaugeRating.style.color = 'var(--fake-color)';
        gaugeRing.style.stroke = 'var(--fake-color)';
    }
    
    // Circle offset animation
    // circumference = 2 * pi * 40 = 251.3
    const circumference = 251;
    const offset = circumference - (circumference * data.credibility_score);
    gaugeRing.style.strokeDashoffset = offset;
    
    // 3. Explanation Text
    document.getElementById('explanation-text').innerText = data.explanation;
    
    // 4. Token Highlighter
    const highlighter = document.getElementById('highlighted-content');
    highlighter.innerHTML = ''; // reset
    
    data.highlights.forEach(item => {
        if (item.category !== 'neutral') {
            const span = document.createElement('span');
            span.className = `word-hl ${item.category}`;
            span.innerText = item.word;
            
            // Format coefficient label for tooltips
            const sign = item.weight > 0 ? '+' : '';
            span.setAttribute('data-weight-label', `Influence: ${sign}${item.weight.toFixed(2)}`);
            highlighter.appendChild(span);
        } else {
            const textNode = document.createTextNode(item.word);
            highlighter.appendChild(textNode);
        }
    });
}

// Fetch model configuration and insights
async function fetchModelInfo() {
    try {
        const response = await fetch('/api/model-info');
        const result = await response.json();
        
        if (result.success && result.data.trained) {
            updateModelInfoUI(result.data);
        } else {
            // Model not trained yet
            document.getElementById('status-model-name').innerText = 'Untrained';
        }
    } catch (err) {
        console.error('Error loading model info:', err);
    }
}

// Update model stats page elements
function updateModelInfoUI(data) {
    // Sidebar Status
    document.getElementById('status-model-name').innerText = `Logistic Regression (${data.metrics.accuracy * 100 === 100 ? 'Offline Synthetic' : 'Active Model'})`;
    
    // Accuracy progress ring
    const accFill = document.getElementById('ring-accuracy');
    const accVal = document.getElementById('metric-accuracy-val');
    accVal.innerText = `${(data.metrics.accuracy * 100).toFixed(1)}%`;
    accFill.style.strokeDasharray = `${data.metrics.accuracy * 100}, 100`;
    
    // Precision progress ring
    const precFill = document.getElementById('ring-precision');
    const precVal = document.getElementById('metric-precision-val');
    precVal.innerText = `${(data.metrics.precision * 100).toFixed(1)}%`;
    precFill.style.strokeDasharray = `${data.metrics.precision * 100}, 100`;
    
    // Recall progress ring
    const recFill = document.getElementById('ring-recall');
    const recVal = document.getElementById('metric-recall-val');
    recVal.innerText = `${(data.metrics.recall * 100).toFixed(1)}%`;
    recFill.style.strokeDasharray = `${data.metrics.recall * 100}, 100`;
    
    // Metadata stats
    document.getElementById('info-vocab-size').innerText = `${data.vocab_size.toLocaleString()} features`;
    document.getElementById('info-train-samples').innerText = `${data.metrics.samples_trained.toLocaleString()} articles`;
    
    // Render top predictive words
    const realList = document.getElementById('real-word-list');
    const fakeList = document.getElementById('fake-word-list');
    
    realList.innerHTML = '';
    data.real_words.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="feature-word">${item.word}</span> <span class="feature-weight">+${item.weight.toFixed(2)}</span>`;
        realList.appendChild(li);
    });
    
    fakeList.innerHTML = '';
    data.fake_words.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="feature-word">${item.word}</span> <span class="feature-weight">${item.weight.toFixed(2)}</span>`;
        fakeList.appendChild(li);
    });
}

// Trigger asynchronous/retraining sequence
async function triggerRetrain() {
    const retrainBtn = document.getElementById('retrain-btn');
    const loader = document.getElementById('retrain-loader');
    
    retrainBtn.disabled = true;
    loader.classList.remove('hidden');
    
    showToast('Retraining model... This may take a moment.', 'success');
    
    try {
        const response = await fetch('/api/train', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            updateModelInfoUI(result.info);
            showToast('Model successfully retrained!', 'success');
        } else {
            showToast(result.error || 'Failed to retrain model.', 'error');
        }
    } catch (err) {
        showToast('Error retrying model compilation.', 'error');
        console.error(err);
    } finally {
        retrainBtn.disabled = false;
        loader.classList.add('hidden');
    }
}

// Load preloaded sample news articles
function loadSample(id) {
    const sample = sampleArticles[id];
    if (!sample) return;
    
    // Insert text
    document.getElementById('text-input').value = sample.text;
    updateWordCount();
    
    // Transition views
    setInputMode('text');
    switchTab('detector');
    
    showToast(`Loaded article: "${sample.title}"`, 'success');
}

// Toast Notifications helper
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-message');
    const icon = document.getElementById('toast-icon');
    
    msgEl.innerText = message;
    
    // Set types
    toast.className = 'toast'; // reset
    if (type === 'error') {
        toast.classList.add('error');
        icon.className = 'fa-solid fa-circle-xmark toast-icon';
    } else {
        toast.classList.add('success');
        icon.className = 'fa-solid fa-circle-check toast-icon';
    }
    
    // Reveal toast
    toast.classList.remove('hidden');
    
    // Auto hide after 4 seconds
    if (window.toastTimeout) {
        clearTimeout(window.toastTimeout);
    }
    
    window.toastTimeout = setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}
