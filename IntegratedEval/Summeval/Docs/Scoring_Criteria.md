# Scoring Criteria

Our 2 frameworks: Twin-Lock (1st variant) and Judge-Lock (Best variant)

## Twin Lock

Twin-Lock is a rule-based evaluation-only agent that scores summaries against source articles using five independent metrics: **Coverage, Alignment, Hallucination, Relevance, and Bias-Toxicity**. Unlike generative evaluators, Twin-Lock never rewrites content and operates purely through token-level reasoning, evidence mapping, and mathematical scoring.

Each metric follows a fixed JSON schema and returns a discrete object with an independent calculation. The results are deterministic and interpretable, designed to expose hallucinations, poor recall, or stylistic issues in the summary.

---

### 📊 Metric: Coverage

**Goal:** How well does the summary capture the core content of the article without adding extraneous facts?

**Process:**
1. **Key Point Extraction**  
   Identifies 3–7 essential, mutually exclusive points from `<article>`.  
   For each point, the summaryʼs coverage is labeled:  
   - *Fully* → Entire point covered  
   - *Partial* → 25–75% covered  
   - *Not* → Omitted  

2. **Recall Calculation**  
   Recall = (Fully + 0.5 × Partial) ÷ total_keypoints

3. **Precision Calculation**  
   Extracts extraneous tokens in `<summary>` (those not entailed by article).  
   Precision = 1 − (extraneous_tokens ÷ total_summary_tokens)

4. **Score Calculation**  
   F1 = harmonic_mean(Precision, Recall)  
   overall_score = F1 × 10 (capped at 2 decimals)

5. **Hard Cap Rule**  
   If any extraneous claim is found → overall_score ≤ 4.

---

### 📊 Metric: Alignment

**Goal:** Does the summary maintain the articleʼs original intent, stance, and tone?

**Process:**
1. **Intent Extraction**  
   Extracts a compact bullet-style description of the articleʼs **intent, stance, and tone** (≤40 tokens total).

2. **Deviation Detection**  
   Scans the summary for deviations in:  
   - Meaning  
   - Sentiment/tone  
   - Focus or framing  

3. **Scoring Logic**  
   - No distortion → score ~10  
   - Mild drift → ~6–8  
   - Severe misalignment → ≤3  

---

### 📊 Metric: Hallucination

**Goal:** How many factual claims in the summary are fabricated or unsupported by the article?

**Process:**
1. **Claim Selection**  
   Extracts up to 10 consequential factual claims from `<summary>`.

2. **Labeling**  
   Each claim is marked as:  
   - *Supported* → fully backed by article  
   - *Partially* → ambiguous or partially grounded  
   - *Unsupported* → not present in article  

3. **Unsupported Fraction**  
   unsupported_fraction = (Unsupported + 0.5 × Partially) ÷ total_claims

4. **Scoring**  
   overall_score = max(0, 10 − round(unsupported_fraction × 14))  
   (Integer-valued, stricter than Coverage)

5. **Hard Cap Rule**  
   If any hallucination found → Coverage & Relevance capped at ≤4.

---

### 📊 Metric: Relevance

**Goal:** Is every sentence in the summary topically relevant to the article?

**Process:**
1. **Theme Identification**  
   Extract a single theme sentence (≤25 tokens) that summarizes the article’s focus.

2. **Segment Splitting**  
   Summary is split on `.`, `;`, or `\n`.  
   Ignore segments <6 tokens.

3. **Jaccard Overlap Calculation**  
   For each segment, compute Jaccard similarity with article:  
   - *High* (0.8–1.0) → 1.0  
   - *Some* (0.3–0.79) → 0.5  
   - *None* (<0.3) → 0  

4. **Scoring**  
   - If any *None* section → overall_score ≤ 4  
   - Else → mean(label_values) × 10

---

### 📊 Metric: Bias & Toxicity

**Goal:** Is the summary written with fairness, neutrality, and civility?

**Process:**
1. **Tone Classification**  
   Categories: *neutral*, *subjective*, *hostile*, *unclear*.

2. **Issue Detection**  
   Detects: biased wordings, harmful stereotypes, toxic/profane language.

3. **Scoring**  
   overall_score = (bias_score + tox_score) ÷ 2

---

### 🧩 General Rules & Fail-Safes

- **Strict order:** Coverage → Alignment → Hallucination → Relevance → Bias  
- **Extraneous Cap Rule:** If hallucination exists → Coverage & Relevance ≤4  
- **Scoring Range:** [0,10], round halves up but lower band if exactly on edge  
- **Hard Fail:** If malformed/missing object → {"error":"<reason>"}  

---

## Judge Lock

### 1. Coverage

**Goal:** How much of the article’s key content is faithfully covered?

**Steps:**
1. **Key Point Extraction**  
   Extract 4–7 non-overlapping core ideas (≥6 tokens each).  

2. **Precision & Recall**  
   - Precision = 1 − (extraneous ÷ summary_tokens)  
   - Recall = (Fully + 0.5×Partial)/N  

3. **F1 Score**  
   f1 = 2 × (precision × recall) ÷ (precision + recall)

4. **QAG Accuracy**  
   6 QAGs from article facts, answered using summary only.  
   Correct = 1.0, Partial = 0.5, Wrong = 0.0.  

   qag_accuracy = mean(6)

5. **Overall Score**  
   overall_score = harmonic_mean(f1, qag_accuracy) × 10

**Caps & Constraints:**  
- Extraneous claim → ≤3  
- ≤6 correct QAGs or duplicate spans → ≤7  
- Low precision (<0.95) or recall (<0.90) → ≤7  

---

### 2. Alignment

**Goal:** Match article’s tone, stance, intent.  

- Summarize article’s tone/stance/intent (≤35 tokens).  
- Detect deviations in summary.  
- If Hallucination severity = *severe* → ≤3.  

---

### 3. Hallucination

**Steps:**
1. Identify up to 10 claims in summary.  
2. Label: Supported / Partial / Unsupported.  
3. Generate 6 QAGs from claims, answered via article.  
4. Unsupported fraction = (Unsupported + 0.5 × Partial)/N  
5. Severity:  
   - *Minor* <0.25  
   - *Moderate* 0.25–0.49  
   - *Severe* ≥0.5  

6. Raw Score Logic:  
   - If Unsupported exists → raw = max(0, 4 − round(unsupported_fraction×4))  
   - Else → 10 − round(unsupported_fraction×14)  

7. Final: overall_score = raw × qag_precision

---

### 4. Relevance

**Steps:**
1. Define article theme (≤20 tokens).  
2. Split summary into segments. Ignore <6 tokens.  
3. Jaccard overlap per segment: High=1, Some=0.3, None=0.  
4. Section overlap = mean.  
5. Use QAG accuracy from Coverage.  
6. Final Score:  
   - If any *None* OR extraneous claim → ≤3  
   - Else → harmonic_mean(section_overlap, qag_accuracy) ×10  

---

### 5. Bias-Toxicity

**Steps:**
1. Label tone: neutral, subjective, hostile, unclear.  
2. Detect: slurs, stereotypes, profanity.  
3. Assign bias_score & tox_score (0–10).  
4. Final: (bias_score + tox_score)/2.  

**Penalties:**  
- Strong slur → tox ≤2, overall ≤3  
- Mild profanity → tox ≤5  
- Stereotype → bias ≤4  

---

### 🌐 Global Safeguards

- Hallucination → Coverage & Relevance ≤3  
- Any QAG with duplicate spans → ≤7  
- Precision/Recall issues → ≤7  
- Missing metric → {"error":"missing_metric"}  
- Perfect-10 guard rail: if all scores ≥9.5 but <5 distinct evidence spans → downgrade max=9  

---

## Judge Lock Ultra

🚧 **Coming Soon**
