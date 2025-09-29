## Research Synthesis and Citations
- ### Trust & Transparency
  - Applied findings:
    - Emphasizes early and salient risk/conflict disclosures as trust drivers, aligning with qualitative insights from "Characteristics of Trust in Personal Financial Planning" on vulnerability and honesty.
    - Overconfidence penalties (e.g., "guaranteed," "risk-free") reflect behavioral finance studies showing user aversion to absolute claims, supported by experimental evidence in "Explainable AI and Adoption of Financial Algorithmic Advisors."
    - Balanced tone with hedging terms ("may," "could") supports trust-building, consistent with experimental data on explainable AI's impact on adoption.
    - Binary logic for disclaimer presence and ratio of hedged-to-confident words integrate empirical trust metrics from financial advisor studies.

- ### Competence & Accuracy
  - Applied findings:
    - Ground truth matching for numeric accuracy stems from research in "The Quality of Financial Advice: What Influences Recommendations to Clients?" linking advisor competence to better outcomes via regression models.
    - Semantic similarity using embeddings (e.g., cosine similarity > 0.8) addresses qualitative accuracy, supported by literature on interpretable ML techniques in finance.
    - Weighted scoring (50% numeric, 30% semantic, 20% fact-check) balances quantitative and qualitative rigor, reflecting integrated models from financial advice quality studies.
    - Omissions (fees, taxes) penalties align with findings that incomplete advice undermines perceived competence.

- ### Explainability
  - Applied findings:
    - Keyword counting for causal markers ("because," "due to") and structured steps (bullets/numbers) mirrors experimental findings in "Explainable AI and Adoption of Financial Algorithmic Advisors" showing higher adoption with feature-based explanations.
    - Clarity ratings (1–5) and logical flow checks draw from research on user comprehension of AI-driven advice, emphasizing causal reasoning over declarative statements.
    - Risk language readability penalties reflect critiques of dense explanations in robo-advisor usability studies from "Evaluating robo-advisors through behavioral finance."
    - Composite index weighting integrates adoption and trust gains observed in AI advisor experiments.

- ### Client-Centeredness / Fiduciary Alignment
  - Applied findings:
    - Personalization depth scoring (1–5) and fiduciary phrasing ("in your best interest") align with qualitative studies in "Characteristics of Trust in Personal Financial Planning" identifying client-first approaches as trust foundations.
    - Binary checks for product-bias absence reflect empirical evidence in "The Quality of Financial Advice" that conflicts of interest reduce advice quality.
    - Tailoring to client situation (income, goals) integrates findings from models linking advisor alignment to improved client outcomes.
    - Conflict disclosure flags address regulatory and ethical concerns raised in financial advisory literature.

- ### Bias-Sensitivity & Risk Safety
  - Applied findings:
    - Binary flags for cognitive biases (overconfidence, herd behavior) and risk disclosures draw from behavioral finance reviews in "Evaluating robo-advisors through behavioral finance" highlighting robo-advisor limitations.
    - Diversification mentions as a safety metric align with portfolio optimization studies, addressing concentration risks noted in investor behavior research.
    - Weighted sum of checks balances pros/cons disclosure, supported by evidence that balanced advice mitigates user dissatisfaction during market downturns.
    - Subtle bias detection by judges reflects qualitative insights into investor psychology under loss scenarios.

- ### Financial Literacy Support / Communication Clarity
  - Applied findings:
    - Jargon density ratio and glossary coverage metrics stem from studies showing clarity improves trust and education, validated by advisor-client interaction research.
    - Structured format checks (bullets/steps) enhance actionability, consistent with findings on readable financial communication.
    - Clarity ratings (1–5) and knowledge improvement assessments draw from educational frameworks in financial advising, emphasizing beginner-friendly language.
    - Weighted formula prioritizes jargon reduction, aligning with evidence that literacy support boosts long-term advisor success.

---
### Reference Links
- Trust & Transparency: [Characteristics of Trust in Personal Financial Planning](https://www.researchgate.net/publication/348395133_Characteristics_of_Trust_in_Personal_Financial_Planning)
- Competence & Accuracy: [The Quality of Financial Advice: What Influences Recommendations to Clients?](https://www.sciencedirect.com/science/article/pii/S037842662400205X)
- Explainability: [Explainable AI and Adoption of Financial Algorithmic Advisors: an Experimental Study](https://arxiv.org/abs/2101.02555)
- Client-Centeredness / Fiduciary Alignment: [Characteristics of Trust in Personal Financial Planning](https://www.researchgate.net/publication/348395133_Characteristics_of_Trust_in_Personal_Financial_Planning)
- Bias-Sensitivity & Risk Safety: [Evaluating robo-advisors through behavioral finance: a critical review of technology potential, rationality, and investor expectations](https://www.frontiersin.org/journals/behavioral-economics/articles/10.3389/frbhe.2024.1489159/full)
- Financial Literacy Support / Communication Clarity: General advisor-client interaction and literacy enhancement studies.

### Mapping Research → Metric Design
- **Trust & Transparency:** Early disclosures, overconfidence penalties, and hedging ratios scored (0–5) to reflect trust-building evidence.
- **Competence & Accuracy:** Numeric/semantic checks and omission penalties weighted (0–5) per competence-outcome links.
- **Explainability:** Causal markers, structure, and readability scored (0–5) to mirror adoption drivers.
- **Client-Centeredness / Fiduciary Alignment:** Personalization and bias checks scored (0–5) per client-outcome alignment.
- **Bias-Sensitivity & Risk Safety:** Bias flags and diversification weighted (0–5) per risk mitigation needs.
- **Financial Literacy Support / Communication Clarity:** Jargon and structure scored (0–5) to enhance education and comprehension.
