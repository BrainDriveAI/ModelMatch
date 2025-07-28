# Summary Evaluator (Summeval) 📊

## What is Summeval? 🤔

Summeval is a tool designed to evaluate and rank the quality of article summaries using the BrainDrive Model-Match Evaluator. Its primary aim is to assess and compare how well different AI models perform in summary evaluation, scoring summaries against source articles based on five core metrics: **Coverage**, **Alignment**, **Hallucination**, **Relevance**, and **Bias/Toxicity**. It’s perfect for benchmarking AI models while also serving researchers, developers, and content creators.

## What Does It Do? 🚀

Summeval compares a summary to its source article, providing scores (0-1 or 0-10 depending on the variant) for each metric to measure how well the summary captures key content, aligns with the article’s intent, avoids fabricated information, stays relevant, and maintains neutrality. It ranks model performance and provides detailed feedback for improvement.

## How It Works (In Short) ⚙️

1. **Input**: Paste the full article and its summary.
2. **Select Variant**: Choose Twin-Lock (fast, structured) or Judge-Lock (deeper, hallucination-aware).
3. **Choose Model**: Select an evaluator model (e.g., GPT-4.1 mini, Claude 3.5 Sonnet, DeepSeek Chat).
4. **Adjust Metrics**: Customize weights for each metric or use defaults.
5. **Run Evaluation**: Get per-metric scores, average score, JSON feedback, and token usage.
6. **Output**: Download results as CSV or JSON for analysis and model ranking.

## Scoring Criteria 📈

| Metric            | Goal                                                                 | Twin-Lock                              | Judge-Lock                                      |
|-------------------|----------------------------------------------------------------------|----------------------------------------|------------------------------------------------|
| **Coverage**      | Captures article’s key points without extraneous facts                | Rule-based F1 score                    | Precision, recall, and QAG accuracy             |
| **Alignment**     | Matches article’s intent, stance, and tone                            | Structured JSON scoring                | Deeper intent and tone deviation detection      |
| **Hallucination** | Detects fabricated or unsupported claims                              | Token-level claim verification         | QAG-based claim analysis, stricter scoring      |
| **Relevance**     | Ensures summary content is thematically tied to the article           | Jaccard similarity on segments         | Enhanced with QAG accuracy                     |
| **Bias/Toxicity** | Evaluates neutrality and absence of offensive content                 | Rule-based tone and bias detection     | Detailed tone, slur, and stereotype analysis    |

- **Twin-Lock**: Fast, deterministic, rule-based scoring with JSON outputs.
- **Judge-Lock**: Advanced scoring with precision, recall, F1, and QAG accuracy, focusing on hallucination detection.

## Who Is It For? 👥

- **Researchers**: Evaluate and rank AI models for summarization tasks.
- **Developers**: Benchmark model performance in generating accurate summaries.
- **Content Creators**: Ensure summaries are accurate, relevant, and neutral.
- **Organizations**: Need consistent, unbiased summary evaluations for quality control.

## Features ✨

- **Variants**: Twin-Lock (fast) and Judge-Lock (accurate) evaluation modes.
- **Customizable Metrics**: Adjust weights for tailored evaluations.
- **Model Backends**: Supports GPT-4.1 mini, Claude 3.5 Sonnet, DeepSeek Chat.
- **Output Formats**: JSON, CSV, or raw JSON zip for easy analysis.
- **Evidence Spans**: Highlights referenced article parts for transparency.
- **Temperature Control**: Adjust randomness of evaluation (0 to 1, default 0.6).

## How to Use 🛠️

1. Paste the article and summary into the input fields.
2. Select a variant: Twin-Lock for speed, Judge-Lock for depth.
3. Choose a model backend (e.g., GPT-4.1 mini, DeepSeek Chat).
4. Adjust metric weights or use presets (Twin Defaults or Judge Defaults).
5. Set advanced options (e.g., temperature, evidence spans).
6. Click "Run Evaluation" to generate scores, feedback, and model rankings.
7. Download results as CSV or JSON for analysis.

**Skip Installation**: Try Summeval on Hugging Face Spaces: [https://huggingface.co/spaces/BrainDrive/Summary-Evaluator](https://huggingface.co/spaces/BrainDrive/Summary-Evaluator) 🌐

## Installation 🔧

1. Clone the repository:
   ```bash
   git clone https://github.com/BrainDriveAI/ModelMatch
   ```
2. Navigate to the Summeval directory:
   ```bash
   cd ModelMatch
   cd Summeval
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables for API keys:
   ```bash
   export ANTHROPIC_API_KEY="add your API key here"
   export OPENAI_API_KEY="add your API key here"
   export OPENROUTER_API_KEY="add your API key here"
   export DEEPSEEK_API_KEY="add your API key here"
   ```
5. Run the application:
   ```bash
   python3 app.py
   ```
6. Access the app on your local host at port 7860 via a browser (e.g., http://localhost:7860).

## Conclusion 🎉

Summeval is a robust tool for ranking AI models on summary evaluation while delivering transparent, actionable insights. Whether you're a researcher benchmarking models, a developer optimizing summarization, or a content creator ensuring quality, Summeval offers precision and flexibility. Get started locally or use the Hugging Face Space for a seamless experience.