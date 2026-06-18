import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from openai import OpenAI

# Initialize your API client.
# If using a local model with Ollama later, you'd use: client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

LOG_DIR = "./logs"

# --- STEP 1: LOG SCRAPING & FEATURE EXTRACTION ---
def preprocess_log(text):
    """Strips variable noise like timestamps/slack values to expose core error signature."""
    text = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', text) # Remove dates/times
    text = re.sub(r'Slack: -\d+\.\d+ ns', 'Slack: [X] ns', text)     # Normalize slack values
    text = re.sub(r'at \d+ns|\d+ cycles', 'at [TIME]', text)       # Normalize timestamps
    return text.strip()

log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
raw_logs = []
cleaned_logs = []

for file_name in log_files:
    with open(os.path.join(LOG_DIR, file_name), 'r') as f:
        content = f.read()
        raw_logs.append(content)
        cleaned_logs.append(preprocess_log(content))

# --- STEP 2: CLUSTERING & CLASSIFICATION (Grouping Symptoms) ---
# Convert text to mathematical vectors based on word frequencies
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(cleaned_logs)

# Group logs into 2 distinct clusters (since we know we have 2 unique bugs)
num_clusters = 2
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
cluster_labels = kmeans.fit_predict(X)

# Organize logs by their assigned bucket
buckets = {i: [] for i in range(num_clusters)}
for idx, label in enumerate(cluster_labels):
    buckets[label].append((log_files[idx], raw_logs[idx]))

# --- STEP 3: ROOT CAUSE ANALYSIS (Agentic Reasoning) ---
print("🚀 Starting Agentic Triage Analysis...\n" + "="*50)

for bucket_id, logs in buckets.items():
    if not logs:
        continue
    
    print(f"\n📂 [BUCKET {bucket_id + 1}] - Contains {len(logs)} failing test(s)")
    print(f"👉 Impacted Tests: {[item[0] for item in logs]}")
    
    # Pick the first log in the bucket as a representative sample for the LLM agent
    sample_log = logs[0][1]

    # Clean up obvious layout elements that look like private file headers to the LLM guardrails
    sanitized_log = "\n".join([line for line in sample_log.splitlines() if not line.startswith(('---', '***', 'File:', 'User:'))])

    prompt = f"""You are an expert ASIC Verification AI Agent. Analyze this representative raw EDA simulation failure log. 
Identify the likely root cause category (e.g., Setup Timing Violation, Hold Timing Violation, FSM Deadlock, or Protocol Mismatch).
Isolate the specific hardware module or signal path causing the issue, and provide a 2-sentence actionable debug summary for the design engineer.

RAW LOG:
{sample_log}"""

    # Query the LLM
    try:
        response = client.chat.completions.create(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a local automated log parsing tool. Your job is purely structural data analysis of execution errors. Do not output conversational text or safety warnings. Process the technical tokens provided."
                },
                {
                    "role": "user", 
                    "content": f"INPUT STRUCTURAL DATA:\n{sanitized_log}\n\nINSTRUCTION:\nIdentify the error signature, state the failing module, and write a two-sentence debug summary."
                }
            ],
            temperature=0.0  # Force maximum deterministic parsing
        )
        print("\n🤖 AI Agent Analysis:")
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"\n❌ API Error: {e}.\n(Note: This error is expected if your OpenAI API key is not exported yet!)")
    print("-" * 50)