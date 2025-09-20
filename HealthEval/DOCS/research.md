# Research Foundations for HealthEval

HealthEval’s metrics and logic are grounded in leading research on medical AI, patient-clinician interaction, and trustworthy system design. Below are the key papers and findings that shaped the framework, with notes on their influence.

---

## CONSORT-AI & SPIRIT-AI (Nature Medicine, 2020)
- **Context:** These are international reporting standards for clinical trials involving AI. They emphasize transparency, reproducibility, and clear communication of intended use, limitations, and deployment context.
- **Key findings:** Trials must spell out intended use, input requirements, human–AI interaction, error analysis, and deployment context so claims are interpretable and reproducible.
- **Influence:** Directly underpins the “Evidence & Transparency” metric. HealthEval’s scoring anchors map to these checklist items, ensuring models disclose their purpose, limitations, and evidence base.
- **Metrics:** Evidence & Transparency, Clinical Safety
- [Nature+1](https://www.nature.com/articles/s41591-020-1034-x)

## Ayers et al., JAMA Internal Medicine (2023)
- **Context:** Compared physician and chatbot responses to real patient questions in a blinded study.
- **Key findings:** Clinicians preferred chatbot answers 4:1 for quality and empathy, largely due to more thorough and empathic replies. The study highlights the importance of separating “medical correctness” from “empathic delivery.”
- **Influence:** Motivates separate scoring for “Clinical Safety” (correctness/escalation) and “Empathy” (tone, validation).
- **Metrics:** Clinical Safety & Escalation, Empathy & Relationship Quality
- [JAMA Network](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2804309)

## Kelley et al., PLoS ONE (2014)
- **Context:** Meta-analysis of randomized controlled trials on the patient-clinician relationship.
- **Key findings:** The relationship itself yields small but significant improvements in clinical and subjective outcomes. Empathy, tone, and partnership matter for patient satisfaction and adherence.
- **Influence:** Supports “Empathy & Relationship Quality” as a core metric, rewarding validating and collaborative language.
- **Metrics:** Empathy & Relationship Quality
- [PLOS](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0086041)

## Batbaatar et al., Systematic Review (2017)
- **Context:** Systematic review of determinants of patient satisfaction across healthcare settings.
- **Key findings:** Service-quality indicators (interpersonal care, communication, provider technical skill) dominate patient satisfaction. Demographics have inconsistent effects.
- **Influence:** Informs “Clarity & Comprehension” (plain language, structure) and “Empathy” (interpersonal care) metrics.
- **Metrics:** Clarity & Comprehension, Empathy & Relationship Quality
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/28676093/)

## Derksen et al., Br J Gen Pract (2012)
- **Context:** Review of empathy’s impact in general practice.
- **Key findings:** Empathy correlates with higher satisfaction, adherence, lower anxiety, and better outcomes. Empathic communication is a clinical skill with measurable impact.
- **Influence:** Validates “Empathy & Relationship Quality” as a metric, rewarding specific validation and partnership language.
- **Metrics:** Empathy & Relationship Quality
- [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3529296/)

## Robertson et al., PLOS Digital Health (2023)
- **Context:** Surveyed diverse patients’ attitudes toward AI in healthcare.
- **Key findings:** Patients appreciate AI’s accuracy but are reluctant to trust automation. Acceptance improves with careful framing, information, and physician-led decisions with AI assist.
- **Influence:** Supports “Trust, Explainability & User Agency” (user control, transparency) and “Clinical Safety” (escalation to human care).
- **Metrics:** Trust, Explainability & User Agency, Clinical Safety & Escalation
- [PLOS](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000286)

## Shevtsova et al., JMIR Human Factors (2024)
- **Context:** Systematic review of trust and acceptance factors for medical AI.
- **Key findings:** Transparency, perceived reliability, usability, and user education are central to trust and acceptance. Clear limitations, uncertainty statements, and reasoning are essential.
- **Influence:** Informs “Evidence & Transparency” (disclosure, uncertainty) and “Trust” (user agency, explainability) metrics.
- **Metrics:** Evidence & Transparency, Trust, Explainability & User Agency
- [JMIR Human Factors](https://humanfactors.jmir.org/2024/1/e50000/)

## Singh et al., npj Digital Medicine (2023)
- **Context:** Meta-analysis of chatbot interventions for health behaviors (activity, diet, sleep).
- **Key findings:** Chatbots can improve health behaviors, but quality and design vary. Plan specificity and adherence support are critical for effectiveness.
- **Influence:** Directly shapes “Plan Quality & Behavior Support,” rewarding concrete, feasible, and supported plans.
- **Metrics:** Plan Quality & Behavior Support
- [Nature](https://www.nature.com/articles/s41746-023-00938-2)

---

## Metric-to-Research Mapping
- **Evidence & Transparency:** CONSORT-AI, Shevtsova et al.
- **Clinical Safety & Escalation:** CONSORT-AI, Ayers et al., Robertson et al.
- **Empathy & Relationship Quality:** Ayers et al., Kelley et al., Derksen et al., Batbaatar et al.
- **Clarity & Comprehension:** Batbaatar et al.
- **Plan Quality & Behavior Support:** Singh et al.
- **Trust, Explainability & User Agency:** Shevtsova et al., Robertson et al.

---

*HealthEval’s design is directly traceable to these foundational works, ensuring that each metric is evidence-based and aligned with best practices in health AI evaluation.*
