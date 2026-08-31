# Architecture

## Overview

Shadow AI Privacy Auditor is a Streamlit application that reviews text for sensitive information before the text is shared with a public generative-AI platform.

The application uses a hybrid detection approach. A pretrained spaCy named-entity recognition model provides the ML/NLP component for person-name detection, while regular expressions and validation rules are used for structured sensitive information.

The goal is not to automatically block user text. Instead, the application detects possible privacy risks, explains them, and allows the user to decide which findings should be redacted.

---

## Technology Stack

- **Language:** Python 3.11
- **Web application:** Streamlit
- **ML/NLP:** spaCy `en_core_web_sm`
- **Structured detection:** Python regular expressions
- **Validation:** Luhn algorithm and format checks
- **Evaluation:** pandas and custom Python evaluation logic
- **Deployment:** Streamlit Community Cloud
- **External generative-AI API:** None

---

## Repository Structure

```text
shadow-ai-privacy-auditor/
├── README.md
├── requirements.txt
├── environment.yml
├── src/
│   ├── app.py
│   ├── detectors.py
│   └── evaluate.py
├── tests/
│   ├── test_cases.csv
│   └── evaluation_results.csv
├── docs/
│   ├── architecture.md
│   └── model_card.md
└── assets/
    └── Shadow_AI_Privacy_Auditor.png


---

## Main Files

* `src/app.py` contains the Streamlit user interface.
* `src/detectors.py` contains the sensitive-information detectors, validation logic, overlap handling, and redaction functions.
* `src/evaluate.py` runs the labelled synthetic test cases and calculates evaluation metrics.
* `tests/test_cases.csv` contains risky, safe, mixed, and challenge examples.
* `tests/evaluation_results.csv` contains the case-level evaluation results.

---

## Detection Pipeline

The user enters text in the Streamlit interface and starts a scan.

The text then passes through several detection functions.

### 1. ML/NLP Detection

spaCy `en_core_web_sm` is used to detect named entities.

For the current version, only entities labelled `PERSON` are retained for privacy review. Other spaCy entity types, such as dates and organizations, are ignored.

### 2. Structured Detection

Regular expressions detect information with predictable formats, including:

* Email addresses
* Common US phone numbers
* Social Security numbers
* Credit-card-like numbers
* Labelled passwords
* API keys and access tokens
* Employee, client, and volunteer IDs

### 3. Validation

Some detections receive additional validation.

For example, credit-card-like numbers must pass the **Luhn algorithm** before they are treated as a finding.

Credential detectors also require labels such as `password`, `api_key`, or `access_token` to reduce unnecessary matches.

### 4. Overlap Handling

All detector outputs use the same result structure containing:

* Detected text
* Start and end character position
* Category
* Subtype
* Risk level
* Explanation
* Replacement label
* Detection method

Overlapping findings are removed before the results are displayed so that the same text span is not highlighted or redacted more than once.

### 5. Explainable Review

Detected spans are highlighted in the original text.

Each finding is also shown with its:

* Category
* Subtype
* Risk level
* Explanation
* Suggested replacement

The user can decide whether each finding should be redacted.

### 6. Redaction

Only findings selected by the user are replaced.

Redaction is performed from **right to left** so that replacing one sensitive span does not change the stored character positions of earlier findings.

---

## Detection Categories

The current application supports four main categories.

### Names and Contact Information

* Person names — spaCy NER
* Email addresses — regex
* Common US phone numbers — regex

### Government or Financial Identifiers

* Social Security numbers — regex
* Credit-card-like numbers — regex plus Luhn validation

### Passwords, API Keys, or Credentials

Supported credential types include:

* Labelled passwords
* API keys
* Access tokens
* Secret keys

These are detected using keyword-aware structured patterns.

### Employee, Client, or Volunteer Information

Supported identifier formats include examples such as:

* `EMP-0793`
* `CLIENT-2098`
* `VOL-4821`

---

## Privacy Design

The application does not require an external generative-AI API.

User text is processed by the deployed Python application and is not forwarded to ChatGPT, Gemini, Claude, Copilot, or another external generative-AI service.

The application is also designed not to intentionally store submitted text.

Only fictional or synthetic examples were used during development and evaluation.

---

## Evaluation

The hybrid system was evaluated using synthetic risky, safe, mixed, and challenge cases.

### Final Evaluation Results

| Metric          |  Result |
| --------------- | ------: |
| Precision       | `1.000` |
| Recall          | `0.850` |
| F1 score        | `0.919` |
| True positives  |    `17` |
| False positives |     `0` |
| False negatives |     `3` |

The challenge cases were intentionally added after the basic detectors were working. These cases helped identify limitations such as uncommon names, obfuscated email formats, and passwords without clear labels.

These results describe performance on the current synthetic evaluation set and should not be interpreted as guaranteed real-world performance.

---

## Known Limitations

The current version may miss:

* Uncommon person names
* Obfuscated emails such as `name[at]example[dot]com`
* Passwords without a nearby credential label
* Unusual employee or client ID formats
* International phone-number formats
* Sensitive information written in unexpected formats or contexts

A general-purpose NER model may also identify a public or non-sensitive person name even when that name does not represent a privacy risk.

For this reason, the application presents findings for user review rather than automatically blocking or removing all detected text.

---

## Possible Future Improvements

Future improvements could include:

* Larger or specialized NER models
* Physical-address detection
* Additional government and organizational identifiers
* Medical or health-related sensitive information
* Confidential project-information detection
* Multilingual detection
* Configurable organization-specific rules
* Broader credential detection
* Browser-extension integration
* Larger and more diverse evaluation datasets


