


# Model Card

## Model

The machine-learning model used in this project is spaCy `en_core_web_sm`.

It is a pretrained English NLP model. I use its named-entity recognition capability to identify person names in user-provided text.

The complete privacy auditor is a hybrid system. spaCy provides the ML/NLP component, while regular expressions and validation rules detect structured sensitive information.

---

## Intended Use

The model is used to help identify person names that may require privacy review before text is shared with a public generative-AI platform.

The model output is treated as a suggestion rather than an automatic privacy decision.

The user can review every finding and decide whether the detected information should be redacted.

This prototype should not be used as the only security or privacy control for real sensitive information.

---

## Why This Model Was Chosen

I selected spaCy `en_core_web_sm` because it is:

- pretrained
- lightweight
- easy to integrate with Python
- suitable for local NLP processing
- fast enough for an interactive Streamlit application

It also allows the application to perform person-name detection without sending the text to an external generative-AI API.

---

## How the Model Is Used

The complete user text is passed to the spaCy model.

spaCy may return several entity types, including:

- people
- dates
- organizations
- locations

For this application, only entities labelled `PERSON` are retained.

For example, spaCy may detect `Monday` as a date, but the application does not treat that as sensitive information.

Each accepted person-name detection is converted into the same result format used by the structured detectors.

The result contains:

- detected text
- start character position
- end character position
- category
- subtype
- risk level
- explanation
- replacement label
- detection method

---

## Hybrid Detection System

spaCy is only one part of the complete detection system.

Other information is detected with transparent structured methods:

- emails — regex
- phone numbers — regex
- SSNs — regex
- credit-card-like numbers — regex plus Luhn validation
- passwords and credentials — keyword-aware regex
- employee, client, and volunteer IDs — structured regex

This hybrid approach uses ML where semantic entity detection is useful and rules where the sensitive information has a predictable format.

---

## Evaluation

The complete hybrid system was evaluated using synthetic risky, safe, mixed, and challenge cases.

Final results:

| Metric | Result |
|---|---:|
| Precision | 1.000 |
| Recall | 0.850 |
| F1 score | 0.919 |
| True positives | 17 |
| False positives | 0 |
| False negatives | 3 |

The results are specific to the current synthetic evaluation set and do not represent guaranteed performance on real-world data.

---

## Known Limitations

The spaCy model may miss uncommon person names.

It may also identify a public or non-sensitive name as a person even when that name does not create a meaningful privacy risk.

The broader hybrid system also has limitations and may miss:

- obfuscated email formats
- passwords without nearby labels
- unusual organizational IDs
- international phone-number formats
- sensitive information expressed in unexpected ways

The application therefore includes a review step where the user makes the final redaction decision.

---

## Privacy and Responsible Use

The application does not require an external generative-AI API.

Submitted text is not forwarded to ChatGPT, Gemini, Claude, Copilot, or another public generative-AI service for detection.

The application is designed not to intentionally store submitted text.

Only fictional or synthetic examples were used for development and evaluation.

This project should be considered an assistive privacy-review prototype, not a replacement for enterprise data-loss-prevention systems, organizational security policies, or professional privacy review.

.
