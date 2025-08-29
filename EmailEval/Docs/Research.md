## Research Synthesis and Citations

- ### Clarity
- Source: “A Simple Approach to Improving Email Communication” (CACM, 2006) — [CACM (2006)](https://cacm.acm.org/opinion/a-simple-approach-to-improving-email-communication/#:~:text=%2A%2046,messages%20are%20easy%20to%20read)
- Applied findings:
  - Measure presence of explicit asks and deadlines, reflecting low baseline for actionable clarity (46%).
  - Subject usefulness scoring responds to prioritization/readability improvements reported post‑training.
  - Intro clarity checks align with reported lifts in ease of reading and faster comprehension (−10s).
  - Additional baselines tracked contextually: unnecessary CC/BCC (~16%), irrelevant (~13%), information‑only (~41%), email overuse (56%), readability (45%).

### Length
- Sources: “When Writing for Busy Readers, Less Is More” — [Behavioral Scientist](https://behavioralscientist.org/when-writing-for-busy-readers-less-is-more/#:~:text=Image); “The Ideal Email Length, According to Studies” (2025) — [EmailAnalytics](https://emailanalytics.com/ideal-email-length/#:~:text=,yielded%20a%2049%20percent%20response)
- Applied findings:
  - Class‑aware ideal/good bands reflect 50–125 (response) and 100–200 (CTR) ranges, with balanced ~100.
  - Follow‑up/internal classes skew concise; promo/outreach allow longer copy within good bounds.
  - Subject length peak 30–60 chars to aid prioritization and clarity.

### Spam Score
- Sources: IEEE Access (2024) review — [ResearchGate](https://www.researchgate.net/publication/384330009_Email_Spam_A_Comprehensive_Review_of_Optimize_Detection_Methods_Challenges_and_Open_Research_Problems); Mailchimp triggers — [Mailchimp](https://mailchimp.com/resources/most-common-spam-filter-triggers/?ds_c=DEPT_BAU_GOOGLE_SEARCH_APAC_EN_NB_ACQUIRE_BROAD_DSA-50OFF_APACOTH&ds_kids=p82448132187&ds_a_lid=dsa-2227026702184&ds_cid=71700000123022287&ds_agid=58700008937753817&gad_source=1&gad_campaignid=22775832945&gbraid=0AAAAADh1Fp3UQ8MyooeXyEoFHsQjRdJa4&gclid=CjwKCAjw2brFBhBOEiwAVJX5GBfDBxT1mszEgDcoqUk1maVzfiTBbAKRDdhy4DY07iH6WbTqtyB9VhoCLp0QAvD_BwE&gclsrc=aw.ds); Postmark deliverability (2024) — [Postmark](https://postmarkapp.com/blog/why-are-my-emails-going-to-spam)
- Applied findings:
  - Score‑based accumulation of minor infractions (caps, exclamations, triggers) reflects filter scoring.
  - Marketing/urgency/reward/clickbait regex markers model common triggers; HTML/text ratio supported optionally.
  - LLM lexicon counts are weighted tiers (A/B/C) to mimic content‑scoring without profane lists.
  - Deliverability hygiene (opt‑in, list cleaning, no‑reply avoidance) documented as operational guidance.

### Personalization
- Sources: Bloomreach benchmarks — [Bloomreach](https://www.bloomreach.com/en/blog/email-personalization-your-guide-to-better-email-marketing-campaigns); two‑experiment study — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666954423000066)
- Applied findings:
  - Medium‑is‑best curve (0→3, 1→5/6, 2→7/9, 3+→6/5 if intrusive) encodes the personalization paradox.
  - Relevance tracking of cues (name/company/role/location/context) determines scoring within degree curve.
  - Documentation includes benchmarks: +26% opens (subject), +202% conversions (CTA), up to 6× transactions.

- ### Tone
- Sources: Grammarly tone guidance — [Grammarly](https://www.grammarly.com/blog/emailing/email-tone/)
- Applied findings:
  - Greeting/sign‑off bonuses reflect positive politeness norms; polite markers add small bonus.
  - Penalties for ALL CAPS, excess exclamations, and emoji abundance align with professional tone guidance.
  - Passive‑aggressive and hostile phrasing detected via regex and LLM flags to maintain workplace decorum.

### Grammatical Hygiene
- Source: Reader reactions to typos vs. homophone errors — [University of Michigan (PDF)](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://public.websites.umich.edu/%7Ejeboland/BolandQueen2016_plosOne.pdf#:~:text=In%20this%20paper%2C%20we%20ask,mechanical%20errors%20linked%20to%20keyboarding)
- Applied findings:
  - Hygiene score highlights typos and grammar issues; surfaced lists support correction.
  - Emphasizes user perception impacts across personalities; communicates why hygiene matters.

---

### Reference Links
- Clarity (CACM 2006): [CACM (2006)](https://cacm.acm.org/opinion/a-simple-approach-to-improving-email-communication/#:~:text=%2A%2046,messages%20are%20easy%20to%20read)
- Length — Less Is More: [Behavioral Scientist](https://behavioralscientist.org/when-writing-for-busy-readers-less-is-more/#:~:text=Image)
- Length — Ideal Email Length (2025): [EmailAnalytics](https://emailanalytics.com/ideal-email-length/#:~:text=,yielded%20a%2049%20percent%20response)
- Spam — IEEE Access 2024 Review: [ResearchGate](https://www.researchgate.net/publication/384330009_Email_Spam_A_Comprehensive_Review_of_Optimize_Detection_Methods_Challenges_and_Open_Research_Problems)
- Spam — Mailchimp Triggers: [Mailchimp](https://mailchimp.com/resources/most-common-spam-filter-triggers/?ds_c=DEPT_BAU_GOOGLE_SEARCH_APAC_EN_NB_ACQUIRE_BROAD_DSA-50OFF_APACOTH&ds_kids=p82448132187&ds_a_lid=dsa-2227026702184&ds_cid=71700000123022287&ds_agid=58700008937753817&gad_source=1&gad_campaignid=22775832945&gbraid=0AAAAADh1Fp3UQ8MyooeXyEoFHsQjRdJa4&gclid=CjwKCAjw2brFBhBOEiwAVJX5GBfDBxT1mszEgDcoqUk1maVzfiTBbAKRDdhy4DY07iH6WbTqtyB9VhoCLp0QAvD_BwE&gclsrc=aw.ds)
- Spam — Postmark Deliverability (2024): [Postmark](https://postmarkapp.com/blog/why-are-my-emails-going-to-spam)
- Personalization — Bloomreach Benchmarks: [Bloomreach](https://www.bloomreach.com/en/blog/email-personalization-your-guide-to-better-email-marketing-campaigns)
- Personalization — Field Experiments: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666954423000066)
- Tone — Grammarly Tone Guidance: [Grammarly](https://www.grammarly.com/blog/emailing/email-tone/)
- Grammatical Hygiene — Typos vs Grammos: [University of Michigan (PDF)](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://public.websites.umich.edu/%7Ejeboland/BolandQueen2016_plosOne.pdf#:~:text=In%20this%20paper%2C%20we%20ask,mechanical%20errors%20linked%20to%20keyboarding)

### Mapping Research → Metric Design
- Clarity: explicit ask, subject usefulness, concise intro scored to sum 0–10.
- Length: class‑aware bands target concise ranges by email type.
- Spam: deterministic triggers + safe lexicon counts + cumulative penalties reflect industry guidance and score‑based filters.
- Personalization: medium‑best curve avoids over‑personalization; relevance and intrusiveness considered.
- Tone: professional norms (greeting/sign‑off), discipline on caps/exclamations/emoji, and markers of hostility/passive‑aggressiveness; modest bonus for polite markers.
- Grammar: a direct hygiene score with surfaced errors/typos improves perceived quality.


