# 🧠 BrainDrive Summeval Documentation

## 🔹 How Input Works

1. **Article Input**  
   - Field: *Paste full article…*  
   - Purpose: The original source text from which the summary was generated.  
   - Required: ✅ for all evaluations  

2. **Summary Input**  
   - Field: *Paste summary…*  
   - Purpose: Candidate summary (AI-generated or human-written).  
   - Judged **only against the provided article**.  

---

## 🔹 Our Frameworks

### **Twin-Lock**
- A **carefully engineered evaluation prompt** fed to a model in a **controlled manner**.  
- The prompt instructs the base LLM how to **score summaries on 5 fixed metrics**:  
  **Coverage, Alignment, Hallucination, Relevance, Bias/Toxicity.**  
- **Lightweight variant** → Faster, interpretable, JSON-structured outputs.  
- Has strict caps for hallucinations and extraneous claims.  

### **Judge-Lock**
- Also a **carefully written evaluation prompt**, but with **deeper reasoning and safeguards**.  
- Extends Twin-Lock by adding:  
  - **Hallucination-aware scoring**  
  - **QAG (Question-Answer Generation) checks**  
  - **Caps & penalties for low precision/recall or unsupported claims**  
- Designed for **factuality-heavy use cases** where reliability matters more than speed.  

> ⚠ **Judge-Lock Ultra**: *Coming Soon*  

---

## 🔹 How It’s Used (by Models)

- Both **Twin-Lock** and **Judge-Lock** are **not separate models**, but **structured evaluation prompts** that run **on top of base LLMs**.  
- The prompts **tell the underlying models exactly how to evaluate a summary** against the article across the 5 metrics.  
- Usage flow:  
  1. Paste article & summary.  
  2. Select **Twin-Lock** (fast) or **Judge-Lock** (strict).  
  3. Choose model backend.  
  4. Run → Outputs per-metric scores (JSON), plus CSV & feedback.  

---

## 🔹 Model Backends

Available evaluator models:  
- **GPT-4.1 mini** (OpenAI)  
- **Claude 3.5 Sonnet** (Anthropic)  
- **DeepSeek Chat** (DeepSeek)  

👉 These base models execute the **Twin-Lock** or **Judge-Lock** prompts to produce deterministic scoring results.  

---

## 🔹 Scoring Criteria (math and logic behind)

For detailed metric definitions, scoring formulas, and evaluation safeguards for both Twin-Lock and Judge-Lock:  

Refer: 📑 [GitHub: Scoring_Criteria.md](https://github.com/BrainDriveAI/ModelMatch/blob/main/Summeval/Docs/Scoring_Criteria.md)  

---

## 🔹 Usage Reference

For implementation and running evaluations with the provided frameworks:  

Refer: ⚙ [GitHub: ModelMatch / Summeval](https://github.com/BrainDriveAI/ModelMatch/tree/main/Summeval)  

---
