# Importing libraries
import streamlit as st
import spacy

import html

# from detectors import redact_text, scan_text

from detectors import redact_selected_findings, scan_text

@st.cache_resource
def load_model():
    """
    Load the spaCy model once and reuse it across Streamlit reruns.
    """
    return spacy.load("en_core_web_sm")


nlp = load_model()

st.set_page_config(
    page_title="Shadow AI Privacy Auditor",
    page_icon="🛡️",
    layout="wide",
)

st.title("Shadow AI Privacy Auditor")

st.write(
    "Review text for sensitive information before sharing it with "
    "a public generative-AI tool."
)

st.info(
    "Use only fictional or synthetic examples. "
    "The application does not intentionally store submitted text."
)

user_text = st.text_area(
    "Text to review",
    height=220,
    placeholder=(
        "Enter a fictional example, such as: "
        "Thomas Nandan, employee ID EMP-0793, can be contacted at "
        "thomas.nandan@example.com."
    ),
)


def highlight_findings(text, findings):
    """
    Highlight detected sensitive spans while preserving the safe text.

    Findings are inserted from left to right. HTML escaping prevents
    user-submitted text from being treated as executable HTML.
    """

    highlighted_parts = []
    current_position = 0

    for finding in findings:
        start = finding["start"]
        end = finding["end"]

        # Add and escape the safe text before the detected span.
        highlighted_parts.append(
            html.escape(text[current_position:start])
        )

        detected_text = html.escape(text[start:end])
        explanation = html.escape(finding["explanation"])
        subtype = html.escape(finding["subtype"])

        highlighted_parts.append(
            f'<mark title="{subtype}: {explanation}">'
            f"{detected_text}"
            "</mark>"
        )

        current_position = end

    # Add any remaining safe text after the last finding.
    highlighted_parts.append(
        html.escape(text[current_position:])
    )

    return "".join(highlighted_parts)



# Keep scan results available when Streamlit reruns the script.
if "findings" not in st.session_state:
    st.session_state.findings = None

if "scanned_text" not in st.session_state:
    st.session_state.scanned_text = ""


scan_clicked = st.button("Scan text", type="primary")

if scan_clicked:
    if not user_text.strip():
        st.warning("Please enter some text before scanning.")
        st.session_state.findings = None
        st.session_state.scanned_text = ""
    else:
        st.session_state.findings = scan_text(user_text, nlp)
        st.session_state.scanned_text = user_text

findings = st.session_state.findings
scanned_text = st.session_state.scanned_text

if findings is not None:
    if findings:
        st.warning(
            f"{len(findings)} sensitive item(s) detected. "
            "Review the findings before using the redacted text."
        )

        st.subheader("Highlighted text")

        highlighted_text = highlight_findings(
            scanned_text,
            findings,
        )

        st.markdown(
            f"""
            <div style="
                padding: 1rem;
                border: 1px solid #d9d9d9;
                border-radius: 0.5rem;
                line-height: 1.8;
                white-space: pre-wrap;
            ">
                {highlighted_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Highlighted text indicates information that may require privacy review."
        )



        st.subheader("Detected findings")

        table_rows = []

        for finding in findings:
            table_rows.append(
                {
                    "Detected text": finding["text"],
                    "Category": finding["category"],
                    "Type": finding["subtype"],
                    "Risk": finding["risk"],
                    "Explanation": finding["explanation"],
                    "Replacement": finding["replacement"],
                }
            )

        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Review suggested redactions")

        selected_findings = []

        for index, finding in enumerate(findings):
            redact_this_finding = st.checkbox(
                (
                    f"Redact `{finding['text']}` "
                    f"— {finding['subtype']} — {finding['risk']} risk"
                ),
                value=True,
                key=f"redact_finding_{index}",
                help=finding["explanation"],
            )

            if redact_this_finding:
                selected_findings.append(finding)

        redacted_output = redact_selected_findings(
            scanned_text,
            selected_findings,
        )

        st.subheader("Safer reviewed version")

        st.caption(
            f"{len(selected_findings)} of {len(findings)} detected "
            "finding(s) selected for redaction."
        )

        st.text_area(
            "Reviewed and redacted text",
            value=redacted_output,
            height=220,
        )

    else:
        st.success(
            "No sensitive information was detected. "
            "The text remains unchanged."
        )

        st.subheader("Reviewed text")

        st.text_area(
            "Safe text",
            value=scanned_text,
            height=220,
        )


