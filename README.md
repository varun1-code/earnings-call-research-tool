---
title: Earnings Call Research Tool
emoji: 📈
colorFrom: blue
colorTo: green
sdk: streamlit
app_file:app.py
pinned: false
---
# Earnings Call Research Tool 

This project implements a structured research tool for analyzing earnings call transcripts and management discussion sections.  
The system is designed as a fixed research tool (not a chatbot) and produces analyst-ready structured outputs.

It supports PDF, TXT and DOCX files and includes OCR fallback for scanned documents.

---

## Supported Input

- Earnings call transcripts
- Management discussion / commentary sections
- File formats:
  - PDF
  - TXT
  - DOCX

Scanned PDFs are supported using OCR.

---

## Research Tool Implemented 

### Earnings Call / Management Commentary Summary

The tool produces the following structured outputs:

- Management tone (optimistic, cautious, neutral, pessimistic)
- Confidence level (high, medium, low)
- Key positives mentioned (with supporting quotes)
- Key concerns / challenges (with supporting quotes)
- Forward guidance:
  - revenue outlook
  - margin outlook
  - capex outlook
- Capacity utilization trends
- New growth initiatives described

Each extracted point is backed by a direct quote from the transcript.

---

## Hallucination Control

To avoid hallucinations:

- The model is restricted to use only the provided transcript.
- Every positive, concern and growth initiative must include a supporting quote.
- If a section is not present in the transcript, the tool returns `null` instead of generating content.

---

## Handling Missing and Vague Information

- When guidance is vague, short descriptive phrases are returned (for example: “stable” or “moderate growth”), along with the supporting quote.
- If a data section is not mentioned in the transcript, it is returned as `null`.

---

## System Overview

High-level pipeline:

1. Document upload
2. Text extraction
3. OCR fallback for scanned PDFs
4. Structured analysis using an LLM
5. Analyst-ready output
6. JSON and PDF export

---

## Technology Stack

- Streamlit (UI)
- Python
- PyMuPDF, python-docx (text extraction)
- Tesseract + Poppler (OCR fallback)
- NVIDIA hosted LLM endpoint (OpenAI-compatible API)
- ReportLab (PDF export)

---

## Deployment

The application is deployed as a Docker service and can be accessed via a public URL.

OCR dependencies (Tesseract and Poppler) are installed inside the container.

---

## Limitations (Free Hosting)

- OCR on scanned PDFs may take longer to process.
- To remain within LLM context limits and improve reliability, only the first 8,000 characters of extracted text are analysed.
- Large files may result in higher latency.

---

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
