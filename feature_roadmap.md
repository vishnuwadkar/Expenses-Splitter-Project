# 🚀 SplitWise AI — Advanced Feature Roadmap

> Features organized by ML/DS skill area. Pick features that align with the roles you're targeting.

---

## 1. 🔍 Computer Vision & OCR (shows CV skills)

### a) Custom OCR Post-Processing Pipeline
- **What:** Instead of raw EasyOCR → Gemini, build a preprocessing pipeline: deskew, denoise, binarize, contrast enhancement using OpenCV before OCR
- **Skills shown:** Image processing, OpenCV, data cleaning
- **Difficulty:** ⭐⭐
- **Resume impact:** ⭐⭐⭐

### b) Receipt Layout Detection (Object Detection)
- **What:** Train/use a model (YOLOv8 or Detectron2) to detect regions: header, items, totals, tax, footer — then OCR only the relevant zones
- **Skills shown:** Object detection, transfer learning, annotation (LabelImg)
- **Difficulty:** ⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐

### c) Handwritten Receipt Support
- **What:** Fine-tune a TrOCR or CRNN model on handwritten bill data
- **Skills shown:** Sequence models, fine-tuning transformers, custom datasets
- **Difficulty:** ⭐⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐

### d) Multi-Language Receipt Support
- **What:** Detect receipt language automatically and use appropriate OCR models (Hindi, Tamil, etc.)
- **Skills shown:** Multilingual NLP, language detection
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐

---

## 2. 🧠 NLP & LLM Engineering (shows NLP/GenAI skills)

### a) Confidence Scoring & Human-in-the-Loop
- **What:** Show Gemini's confidence for each parsed item, let users correct mistakes, and log corrections as training data
- **Skills shown:** Active learning, HITL systems, feedback loops
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐

### b) Prompt Engineering Benchmark
- **What:** Test multiple prompt variations, measure accuracy (precision/recall on item extraction) across 50+ receipts, and auto-select the best prompt
- **Skills shown:** Prompt engineering, evaluation metrics, A/B testing
- **Difficulty:** ⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### c) Fine-Tuned Small Model (Replace Gemini)
- **What:** Collect 500+ receipts, label them, and fine-tune a small local model (Phi-3, Llama 3.2, or even a BERT-based NER model) to replace Gemini entirely
- **Skills shown:** Fine-tuning LLMs, NER, dataset creation, model evaluation
- **Difficulty:** ⭐⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐ (this alone is interview-worthy)

### d) Named Entity Recognition (NER) for Receipts
- **What:** Train a spaCy/HuggingFace NER model to tag: ITEM_NAME, PRICE, QTY, TAX, TOTAL, DISCOUNT
- **Skills shown:** NER, sequence labeling, custom entity training
- **Difficulty:** ⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐

### e) Smart Categorization
- **What:** Auto-categorize items (Appetizer, Main Course, Drinks, Dessert) using text classification
- **Skills shown:** Text classification, embeddings, clustering
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐

---

## 3. 📊 Data Engineering & Analytics (shows DE/Analytics skills)

### a) Receipt History Database
- **What:** Store all parsed receipts in SQLite/PostgreSQL with user accounts. Track spending over time.
- **Skills shown:** Database design, SQL, data modeling
- **Difficulty:** ⭐⭐
- **Resume impact:** ⭐⭐⭐

### b) Spending Analytics Dashboard
- **What:** Build charts showing:
  - Spending trends over time (line chart)
  - Category breakdown (pie chart)
  - Most frequent items (bar chart)
  - Per-person spending history
  - Restaurant-wise comparison
- **Skills shown:** Data visualization, Plotly/Altair, analytics
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### c) Receipt Data Pipeline (ETL)
- **What:** Build an automated pipeline: Ingest → Clean → Parse → Store → Aggregate using Airflow or Prefect
- **Skills shown:** ETL, pipeline orchestration, data engineering
- **Difficulty:** ⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### d) Export & Reports
- **What:** Generate PDF/Excel reports of splits, email them to participants
- **Skills shown:** Automation, reporting, practical engineering
- **Difficulty:** ⭐⭐
- **Resume impact:** ⭐⭐

---

## 4. 🤖 ML Models (shows core ML skills)

### a) Price Anomaly Detection
- **What:** Train a model to flag unusually priced items (e.g., "Naan ₹500" is likely an OCR error). Use Isolation Forest or statistical methods.
- **Skills shown:** Anomaly detection, unsupervised learning, feature engineering
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### b) Smart Split Recommendations
- **What:** Based on past splits, predict who likely ordered what using collaborative filtering (like a recommendation system)
- **Skills shown:** RecSys, collaborative filtering, user modeling
- **Difficulty:** ⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### c) Receipt Quality Scorer
- **What:** Train a CNN classifier to predict OCR accuracy from the image quality (blurry, dark, skewed) and warn users before processing
- **Skills shown:** Image classification, CNN, transfer learning
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### d) Tip & Discount Predictor
- **What:** Predict suggested tip based on restaurant type, location, bill amount using regression
- **Skills shown:** Regression, feature engineering, model deployment
- **Difficulty:** ⭐⭐
- **Resume impact:** ⭐⭐

---

## 5. ⚙️ MLOps & Production (shows engineering maturity)

### a) Model Monitoring & Logging
- **What:** Log every prediction (OCR text, parsed items, user corrections) to track model drift and accuracy over time
- **Skills shown:** MLOps, monitoring, drift detection
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### b) Evaluation Suite
- **What:** Create a test set of 100+ annotated receipts. Auto-evaluate OCR accuracy (CER/WER) and parsing accuracy (F1 on item extraction) on every code change
- **Skills shown:** ML evaluation, CI/CD for ML, test-driven ML
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐

### c) Dockerize & Deploy
- **What:** Containerize with Docker, deploy on AWS/GCP with a CI/CD pipeline
- **Skills shown:** Docker, cloud deployment, DevOps
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### d) API Backend
- **What:** Build a FastAPI backend separating the ML logic from the Streamlit frontend. Add rate limiting, auth, and API docs.
- **Skills shown:** API design, system architecture, backend engineering
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

---

## 6. 🎯 Full-Stack Data Science (the "wow" features)

### a) Multi-Receipt Group Expenses
- **What:** Upload multiple receipts for a trip/event, track running balances, calculate "who owes whom" (like Splitwise's debt simplification algorithm)
- **Skills shown:** Graph algorithms (min-cost flow), full-stack DS
- **Difficulty:** ⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐⭐

### b) WhatsApp/Telegram Bot
- **What:** Send a photo of a receipt via WhatsApp → bot returns the split. Uses Twilio API.
- **Skills shown:** Bot development, API integration, product thinking
- **Difficulty:** ⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

### c) Real-Time Collaborative Splitting
- **What:** Share a link, everyone joins a room, assigns their own items in real-time using WebSockets
- **Skills shown:** Real-time systems, WebSockets, collaborative UX
- **Difficulty:** ⭐⭐⭐⭐
- **Resume impact:** ⭐⭐⭐⭐

---

## 🏆 Recommended Priority (Best ROI for Interviews)

> [!IMPORTANT]
> These 5 features will have the MOST impact on your resume for ML/DS roles:

| Priority | Feature | Why |
|----------|---------|-----|
| 1️⃣ | **Evaluation Suite** (5b) | Shows you think like a data scientist — measuring, not guessing |
| 2️⃣ | **Confidence Scoring + HITL** (2a) | Active learning is a hot topic; shows production ML thinking |
| 3️⃣ | **Spending Analytics Dashboard** (3b) | Visual proof of your analytics skills — very demo-able |
| 4️⃣ | **Receipt Layout Detection** (1b) | Real CV project with transfer learning — stands out |
| 5️⃣ | **Fine-Tuned NER Model** (2d) | Replace the API with YOUR model — shows you can build, not just call APIs |

> [!TIP]
> The key differentiator for ML/DS roles is showing you can **evaluate** and **improve** models, not just use them.
> Build the evaluation suite first — it makes every other feature measurable and therefore more impressive.
