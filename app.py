import streamlit as st
import tempfile
import os
import json
import io

from tools.option_b_tool import run_management_summary
from utils.text_extractor import extract_text

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


# ---------------- PDF builder ----------------

def build_pdf(result: dict) -> bytes:

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    story = []

    def add(title, value):
        story.append(Paragraph(f"<b>{title}</b>", styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(str(value), styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

    add("Management tone", result.get("management_tone"))
    add("Confidence level", result.get("confidence_level"))

    story.append(Paragraph("<b>Key positives</b>", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    for p in result.get("key_positives", []):
        story.append(Paragraph(
            f"- {p.get('point')}<br/><i>{p.get('supporting_quote')}</i>",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("<b>Key concerns</b>", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    for c in result.get("key_concerns", []):
        story.append(Paragraph(
            f"- {c.get('point')}<br/><i>{c.get('supporting_quote')}</i>",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.2 * inch))

    fg = result.get("forward_guidance", {})
    add("Forward guidance – Revenue", fg.get("revenue"))
    add("Forward guidance – Margin", fg.get("margin"))
    add("Forward guidance – Capex", fg.get("capex"))

    add("Capacity utilization trend",
        result.get("capacity_utilization_trend"))

    story.append(Paragraph("<b>New growth initiatives</b>", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    for g in result.get("new_growth_initiatives", []):
        story.append(Paragraph(
            f"- {g.get('initiative')}<br/><i>{g.get('supporting_quote')}</i>",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)

    buffer.seek(0)
    return buffer.read()


# ---------------- Streamlit UI ----------------

st.set_page_config(
    page_title="Earnings Call Analyzer",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
# 📊 Earnings Call Analysis Tool  
**Option B – Management Commentary Summary**
""")

st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload earnings call transcript  
2. Click Analyze  
3. View structured analysis  

Supported formats:
PDF, TXT, DOCX
""")

uploaded_file = st.file_uploader(
    "Upload Earnings Call Transcript",
    type=["pdf", "txt", "docx"]
)

if uploaded_file is not None:

    file_size = len(uploaded_file.getvalue()) / 1024
    st.info(f"File: {uploaded_file.name} ({file_size:.1f} KB)")

    if st.checkbox("Preview file"):
        preview = uploaded_file.getvalue().decode("utf-8", errors="ignore")[:500]
        st.text_area("Preview", preview, height=200)

    if st.button("🚀 Analyze Transcript", type="primary", use_container_width=True):

        with st.spinner("Processing document..."):

            suffix = os.path.splitext(uploaded_file.name)[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            try:
                text = extract_text(temp_path)

                # safety cut for very long transcripts
                text = text[:8000]

                if not text.strip():
                    st.error("Could not extract any text from the file.")
                else:
                    result = run_management_summary(text)

                    if "error" in result:
                        st.error(result["error"])
                        st.text(result.get("raw_output", ""))
                    else:
                        st.success("Analysis completed")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Management tone",
                                result.get("management_tone")
                            )

                        with col2:
                            st.metric(
                                "Confidence level",
                                result.get("confidence_level")
                            )

                        st.subheader("📈 Key Positives")
                        for item in result.get("key_positives", []):
                            st.markdown(f"**• {item.get('point')}**")
                            st.markdown(f"> {item.get('supporting_quote')}")

                        st.subheader("⚠️ Key Concerns")
                        for item in result.get("key_concerns", []):
                            st.markdown(f"**• {item.get('point')}**")
                            st.markdown(f"> {item.get('supporting_quote')}")

                        st.subheader("🔮 Forward Guidance")
                        fg = result.get("forward_guidance", {})

                        def show(v):
                            return v if v is not None else "Not mentioned"

                        st.write("Revenue:", show(fg.get("revenue")))
                        st.write("Margin:", show(fg.get("margin")))
                        st.write("Capex:", show(fg.get("capex")))

                        if fg.get("supporting_quotes"):
                            st.write("Supporting quotes:")
                            for q in fg["supporting_quotes"]:
                                st.markdown(f"> {q}")

                        st.subheader("🏭 Capacity Utilization Trend")
                        st.write(show(result.get("capacity_utilization_trend")))

                        st.subheader("🚀 New Growth Initiatives")
                        for item in result.get("new_growth_initiatives", []):
                            st.markdown(f"**• {item.get('initiative')}**")
                            st.markdown(f"> {item.get('supporting_quote')}")

                        with st.expander("Raw JSON"):
                            st.json(result)

                        # -------- Downloads --------

                        json_str = json.dumps(result, indent=2)

                        st.download_button(
                            "Download JSON",
                            json_str,
                            file_name="management_summary.json",
                            mime="application/json"
                        )

                        pdf_bytes = build_pdf(result)

                        st.download_button(
                            "Download PDF",
                            pdf_bytes,
                            file_name="management_summary.pdf",
                            mime="application/pdf"
                        )

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

else:
    st.info("Upload a transcript file to begin.")

st.divider()
st.caption("""
This tool only extracts information explicitly stated in the transcript.
Every analytical point is supported by direct quotes.
Missing information is returned as null.
""")
