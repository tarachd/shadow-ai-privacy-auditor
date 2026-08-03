# Importinglibraries

import re
import spacy

nlp = spacy.load("en_core_web_sm")


def detect_person_names(text, nlp_model):
    """
    Detect person names using spaCy's pretrained NER model.

    Only entities labelled PERSON are included. Other spaCy entities,
    such as dates and organizations, are ignored in this first version.
    """
    findings = []

    doc = nlp_model(text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            finding = {
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "category": "Names and contact information",
                "subtype": "PERSON_NAME",
                "replacement": "[NAME]",
                "risk": "Medium",
                "explanation": "A person's name may identify an individual.",
                "method": "spaCy NER",
            }

            findings.append(finding)

    return findings

def detect_emails(text):
    """
    Detect email addresses using a regular-expression pattern.

    This detector supports common email formats and returns the text
    and character positions of each match.
    """

    findings = []

    # Basic email pattern:
    # - allows letters, numbers, periods, underscores, percent signs,
    #   plus signs, and hyphens before the @ symbol
    # - requires a domain name and a final extension such as .com or .org
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"


    # re.finditer() returns every match and includes its character positions.
    for match in re.finditer(email_pattern, text):
        finding = {
            "text": match.group(),
            "start": match.start(),
            "end": match.end(),
            "category": "Names and contact information",
            "subtype": "EMAIL",
            "replacement": "[EMAIL]",
            "risk": "Medium",
            "explanation": (
                "An email address can identify or provide contact information "
                "for a person or organization."
            ),
            "method": "Regex",
        }


        findings.append(finding)

    return findings


def detect_phone_numbers(text):
    """
    Detect common US phone-number formats using regex.

    The first version supports formats with an optional +1 country code.
    International phone formats are outside the current project scope.
    """
    findings = []

    # Supports common US phone formats with an optional +1 country code.
    phone_pattern = (
        r"(?<!\d)"
        r"(?:\+1[\s.-]?)?"
        r"(?:\(\d{3}\)|\d{3})"
        r"[\s.-]?"
        r"\d{3}"
        r"[\s.-]?"
        r"\d{4}"
        r"(?!\d)"
    )



    for match in re.finditer(phone_pattern, text):
        finding = {
            "text": match.group(),
            "start": match.start(),
            "end": match.end(),
            "category": "Names and contact information",
            "subtype": "PHONE_NUMBER",
            "replacement": "[PHONE]",
            "risk": "Medium",
            "explanation": (
                "A phone number can identify or provide direct contact "
                "information for a person."
            ),
            "method": "Regex",
        }


        findings.append(finding)

    return findings

def detect_ssns(text):
    """
    Detect Social Security numbers written in the XXX-XX-XXXX format.

    The detector uses a strict structured pattern to reduce matches
    with ordinary numbers.
    """
    findings = []

    ssn_pattern = r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"


    for match in re.finditer(ssn_pattern, text):
        finding = {
            "text": match.group(),
            "start": match.start(),
            "end": match.end(),
            "category": "Government or financial identifiers",
            "subtype": "SSN",
            "replacement": "[SSN]",
            "risk": "Critical",
            "explanation": (
                "A Social Security number is a highly sensitive government "
                "identifier that could be misused for identity theft."
            ),

            "method": "Regex",
        }


        findings.append(finding)


    return findings


def passes_luhn_check(number):
    """
    Check whether a card-like number passes the Luhn algorithm.

    This validation helps reject random 16-digit numbers that match
    the card-number pattern but are not plausible payment-card numbers.
    """
    digits = [int(digit) for digit in number if digit.isdigit()]

    total = 0
    reverse_digits = digits[::-1]

    for index, digit in enumerate(reverse_digits):
        if index % 2 == 1:
            digit *= 2

            if digit > 9:
                digit -= 9

        total += digit

    return total % 10 == 0


def detect_credit_cards(text):
    """
    Detect credit-card-like numbers using regex and Luhn validation.

    A possible number is returned only when its digits pass the
    validation check.
    """
    findings = []

    card_pattern = r"(?<!\d)(?:\d[ -]?){15}\d(?!\d)"

    for match in re.finditer(card_pattern, text):
        detected_text = match.group()

        if passes_luhn_check(detected_text):
            finding = {
                "text": detected_text,
                "start": match.start(),
                "end": match.end(),
                "category": "Government or financial identifiers",
                "subtype": "CREDIT_CARD",
                "replacement": "[CREDIT CARD]",
                "risk": "Critical",
                "explanation": (
                    "A payment card number is sensitive financial information "
                    "and could be misused for fraud."
                ),

                "method": "Regex with Luhn validation",
            }


            findings.append(finding)

    return findings


def detect_passwords(text):
    """
    Detect plaintext password values next to labels such as password,
    passwd, or pwd.

    Requiring both a label and a value helps avoid flagging general
    discussions about password policies.
    
    Examples detected:
        password = SummerDemo123!
        password: "DemoPass456!"
        pwd = sample_password_789

    A sentence that only discusses passwords should not be detected.
    """

    findings = []

    password_pattern = re.compile(
        r"""(?ix)
        \b(?:password|passwd|pwd)\b
        \s*[:=]\s*
        ["']?
        (?P<value>[^\s"'`,;}{\]\[]+)
        ["']?
        """
    )

    for match in password_pattern.finditer(text):
        finding = {
            "text": match.group("value"),
            "start": match.start("value"),
            "end": match.end("value"),
            "category": "Passwords, API keys or credentials",
            "subtype": "PASSWORD",
            "replacement": "[PASSWORD]",
            "risk": "Critical",
            "explanation": (
                "A plaintext password could allow unauthorized access "
                "to an account or system."
            ),
            "method": "Keyword-aware regex",
        }

        findings.append(finding)

    return findings


def detect_api_keys(text):
    """
    Detect labelled API keys, access tokens, and secret keys.
 
    Examples detected:
        api_key = sk_test_example123456
        access_token: fictional_token_123456
        secret_key = example_secret_987654

    This Tier 1 version focuses on labelled credentials rather than
    attempting to recognize every provider-specific key format.
    """

    findings = []

    api_key_pattern = re.compile(
        r"""(?ix)
        \b(?:
            api[_-]?key
            |
            access[_-]?token
            |
            auth[_-]?token
            |
            api[_-]?token
            |
            secret[_-]?key
        )\b
        \s*[:=]\s*
        ["']?
        (?P<value>[A-Za-z0-9_-]{12,})
        ["']?
        """
    )

    for match in api_key_pattern.finditer(text):
        finding = {
            "text": match.group("value"),
            "start": match.start("value"),
            "end": match.end("value"),
            "category": "Passwords, API keys or credentials",
            "subtype": "API_KEY_OR_TOKEN",
            "replacement": "[API KEY]",
            "risk": "Critical",
            "explanation": (
                "An exposed API key or access token could allow unauthorized "
                "access to services, data, or paid resources."
            ),
            "method": "Keyword-aware regex",
        }

        findings.append(finding)

    return findings


def detect_personnel_ids(text):
    """
    Detect employee, client, and volunteer identifiers.
    
    Supported Tier 1 formats:
        EMP-1234
        CLIENT-2098
        VOL-4821
    """

    findings = []

    personnel_id_pattern = re.compile(
        r"\b(?:EMP|CLIENT|VOL)-\d{4,8}\b",
        re.IGNORECASE,
    )

    for match in personnel_id_pattern.finditer(text):
        detected_text = match.group()

        prefix = detected_text.split("-")[0].upper()

        replacement_map = {
            "EMP": "[EMPLOYEE ID]",
            "CLIENT": "[CLIENT ID]",
            "VOL": "[VOLUNTEER ID]",
        }

        subtype_map = {
            "EMP": "EMPLOYEE_ID",
            "CLIENT": "CLIENT_ID",
            "VOL": "VOLUNTEER_ID",
        }

        finding = {
            "text": detected_text,
            "start": match.start(),
            "end": match.end(),
            "category": "Employee, client or volunteer information",
            "subtype": subtype_map[prefix],
            "replacement": replacement_map[prefix],
            "risk": "High",
            "explanation": (
                "An internal employee, client, or volunteer identifier "
                "could expose confidential organizational records."
            ),
            "method": "Structured regex",
        }

        findings.append(finding)

    return findings

# To prevent two detectors from replacing the same characters

def remove_overlapping_findings(findings):
    """
    Remove duplicate or overlapping detections.

    Findings are considered from left to right. When two findings
    overlap, the longer and more specific span is kept.
    """

    if not findings:
        return []

    # Prefer earlier findings, and prefer longer spans when they start
    # at the same character position.
    sorted_findings = sorted(
        findings,
        key=lambda finding: (
            finding["start"],
            -(finding["end"] - finding["start"]),
        ),
    )

    filtered_findings = []

    for finding in sorted_findings:
        overlaps_existing = any(
            finding["start"] < existing["end"]
            and finding["end"] > existing["start"]
            for existing in filtered_findings
        )

        if not overlaps_existing:
            filtered_findings.append(finding)

    return sorted(
        filtered_findings,
        key=lambda finding: (finding["start"], finding["end"]),
    )




# Now all detector in one scanner

def scan_text(text, nlp_model):
    """
    Run all Tier 1 detectors on the same input text.

    The findings are combined and sorted by their character positions
    so they can later be highlighted and redacted in the correct order.
    """

    findings = []

    # ML/NLP detector
    findings.extend(detect_person_names(text, nlp_model))

    # Names and contact-information detectors
    findings.extend(detect_emails(text))
    findings.extend(detect_phone_numbers(text))

    # Government and financial detectors
    findings.extend(detect_ssns(text))
    findings.extend(detect_credit_cards(text))

    # Credential detectors
    findings.extend(detect_passwords(text))
    findings.extend(detect_api_keys(text))

    # Employee, client, and volunteer detector
    findings.extend(detect_personnel_ids(text))

    # Sort findings from left to right in the original text.
    #findings.sort(key=lambda finding: (finding["start"], finding["end"]))

    findings = remove_overlapping_findings(findings)

    return findings



# Now lets build the redaction function

def redact_text(text, findings):
    """
    Replace detected sensitive spans with their planned redaction labels.

    Findings are processed from right to left so earlier replacements
    do not change the character positions of later findings.
    """

    redacted_text = text

    # Sort from the end of the text toward the beginning.
    findings_right_to_left = sorted(
        findings,
        key=lambda finding: (finding["start"], finding["end"]),
        reverse=True,
    )

    for finding in findings_right_to_left:
        start = finding["start"]
        end = finding["end"]
        replacement = finding["replacement"]

        redacted_text = (
            redacted_text[:start]
            + replacement
            + redacted_text[end:]
        )

    return redacted_text


# this is for user to review 

def redact_selected_findings(text, findings):
    """
    Redact only the findings selected by the user.

    The selected findings are processed from right to left so that
    replacing one span does not change the positions of earlier spans.
    """

    redacted_text = text

    findings_right_to_left = sorted(
        findings,
        key=lambda finding: (finding["start"], finding["end"]),
        reverse=True,
    )


    for finding in findings_right_to_left:
        start = finding["start"]
        end = finding["end"]
        replacement = finding["replacement"]

        redacted_text = (
            redacted_text[:start]
            + replacement
            + redacted_text[end:]
        )

    return redacted_text




if __name__ == "__main__":
    test_sentences = [
        "Bibhuti Bhushan presented novel bioengineering research findings at Monday's group meeting.",
        "Our drug development team lead, Thomas Nandan, employee ID EMP-0793, requested Bibhuti Bhushan's research report be sent to drugteam@example.com.",
        "The targeted drug research presentation motivated the entire team.",
    ]

    for sentence in test_sentences:
        results = detect_person_names(sentence, nlp)

        print("\nSentence:")
        print(sentence)

        print("Detected names:")
        if results:
            for result in results:
                print(result)
        else:
            print("No person names detected.")


    # ----------------------------------
    # email detection tests
    # ---------------------------------

    print("\nEmail detection test:")

    email_test_text = (
        "Send the report to drugteam@example.com and copy analyst@example.org."
    )

    email_results = detect_emails(email_test_text)

    print(email_test_text)

    if email_results:
        for result in email_results:
            print(result)
    else:
        print("No email addresses detected.")


    # ----------------------------------
    # Phone number detection tests
    # ---------------------------------

    print("\nPhone detection test:")

    phone_test_text = (
        "Call the our imaginary coordinator at (610) 555-0123 "
        "or the office at +1 484-555-0198."
    )

    phone_results = detect_phone_numbers(phone_test_text)

    print(phone_test_text)

    if phone_results:
        for result in phone_results:
            print(result)
    else:
        print("No phone numbers detected.")


    # ----------------------------------
    # SSN detection tests
    # ---------------------------------

    print("\nSSNs detection test:")

    ssns_test_text = (
        "The imaginary applicant entered SSN 123-45-6789 on the sample form. "
        "The report contains 123 pages and 45 figures from 6789 records."
    )

    ssns_results = detect_ssns(ssns_test_text)

    print(ssns_test_text)

    if ssns_results:
        for result in ssns_results:
            print(result)
    else:
        print("No SSNs detected.")


    # ----------------------------------
    # Credit card number detection tests
    # ---------------------------------

    print("\nCard detection test:")

    card_test_text = (
    "The fictional payment card is 4111 1111 1111 1111. "
    "The reference number is 1234 5678 9012 3456."
)

    card_results = detect_credit_cards(card_test_text)

    print(card_test_text)

    if card_results:
        for result in card_results:
            print(result)
    else:
        print("No Credit card number detected.")


    # --------------------------
    # Password detector tests
    # ----------------------------

    risky_password_text = (
        "For this fictional test account, password = SummerDemo123!"
    )

    safe_password_text = (
        "The password policy requires at least 12 characters."
    )

    print("\nRisky password test:")
    print(risky_password_text)

    risky_password_results = detect_passwords(risky_password_text)

    if risky_password_results:
        for result in risky_password_results:
            print(result)
    else:
        print("No passwords detected.")

    print("\nSafe password test:")
    print(safe_password_text)

    safe_password_results = detect_passwords(safe_password_text)

    if safe_password_results:
        for result in safe_password_results:
            print(result)
    else:
        print("No passwords detected.")


    # ----------------------------------
    # API key and token detector tests
    # ---------------------------------

    risky_api_key_text = (
        "The fictional test configuration uses "
        "api_key = sk_test_example123456."
    )

    safe_api_key_text = (
        "The development team discussed how API keys should be protected."
    )

    print("\nRisky API key test:")
    print(risky_api_key_text)

    risky_api_key_results = detect_api_keys(risky_api_key_text)

    if risky_api_key_results:
        for result in risky_api_key_results:
            print(result)
    else:
        print("No API keys or tokens detected.")

    print("\nSafe API key test:")
    print(safe_api_key_text)

    safe_api_key_results = detect_api_keys(safe_api_key_text)

    if safe_api_key_results:
        for result in safe_api_key_results:
            print(result)
    else:
        print("No API keys or tokens detected.")

    # ----------------------------------
    # Employee id detector tests
    # ---------------------------------



    risky_personnel_text = (
        "Employee ID EMP-0793 prepared the report for client CLIENT-2098, "
        "with assistance from volunteer VOL-4821."
    )

    safe_personnel_text = (
        "The organization supports employees, clients, and volunteers."
    )

    print("\nRisky personnel ID test:")
    print(risky_personnel_text)

    risky_personnel_results = detect_personnel_ids(risky_personnel_text)

    if risky_personnel_results:
        for result in risky_personnel_results:
            print(result)
    else:
        print("No employee, client, or volunteer IDs detected.")

    print("\nSafe personnel ID test:")
    print(safe_personnel_text)

    safe_personnel_results = detect_personnel_ids(safe_personnel_text)

    if safe_personnel_results:
        for result in safe_personnel_results:
            print(result)
    else:
        print("No employee, client, or volunteer IDs detected.")


    # Combined test

    combined_test_text = (
        "Thomas Nandan, employee ID EMP-0793, can be contacted at "
        "thomas.nandan@example.com or (610) 555-0123. "
        "The fictional account uses password = SummerDemo123! "
        "and api_key = sk_test_example123456. "
        "The sample SSN is 123-45-6789."
    )

    # Redaction test

    print("\nCombined detection test:")
    print(combined_test_text)

    combined_results = scan_text(combined_test_text, nlp)

    if combined_results:
        for result in combined_results:
            print(result)
    else:
        print("No sensitive information detected.")

    print("\nRedacted combined text:")

    redacted_output = redact_text(
        combined_test_text,
        combined_results,
    )

    print(redacted_output)





