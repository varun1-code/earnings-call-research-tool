import json
import os
from openai import OpenAI


client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)


def run_management_summary(transcript_text: str) -> dict:
    """
    Runs Option-B: Earnings call / management commentary analysis
    and returns structured JSON.
    """

    prompt = f"""
You are a financial research assistant.

Using ONLY the transcript below, produce a JSON object in the
following exact schema.

Rules:
- Use only the provided transcript.
- Do NOT add external knowledge.
- Do NOT guess.
- Every positive, concern and initiative MUST include one exact
  supporting quote copied from the transcript.
- If any field is not present in the transcript, return null.

Schema:

{{
  "management_tone": "optimistic | cautious | neutral | pessimistic",

  "confidence_level": "high | medium | low",

  "key_positives": [
    {{
      "point": "",
      "supporting_quote": ""
    }}
  ],

  "key_concerns": [
    {{
      "point": "",
      "supporting_quote": ""
    }}
  ],

  "forward_guidance": {{
    "revenue": "" or null,
    "margin": "" or null,
    "capex": "" or null,
    "supporting_quotes": []
  }},

  "capacity_utilization_trend": "" or null,

  "new_growth_initiatives": [
    {{
      "initiative": "",
      "supporting_quote": ""
    }}
  ]
}}

Transcript:
----------------
{transcript_text}
----------------

Return only valid JSON.
Do not wrap the JSON in markdown.
Do not add any text before or after the JSON.
"""

    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON returned by model",
            "raw_output": raw_output
        }
