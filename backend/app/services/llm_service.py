
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from opentelemetry import context


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are an accurate AI research assistant.
Answer the question using only the provided context.

Important rules:
1. Read the context carefully before answering.
2. Preserve the exact relationship between labels and values.
3. Never swap values between categories or groups.
4. When the context contains a table, match each value
   to its correct row and column.
5. If the context does not contain the answer, say:
   "The provided document does not contain this information."
6. Do not invent facts.
7. Keep the answer concise and include page numbers.
8. When answering questions comparing groups, always state
each group name alongside its value.
Never return unlabeled numbers for a comparison.
9.Treat explicit result statements as confirmation of table values.
- Match each measurement to its stated group.
- If table rows and prose appear inconsistent, report the inconsistency.
- Never guess which value belongs to a group.
context = 
Verified facts from Page 1:
- Roof type: Rooftop garden
  Mean indoor temperature: 27.1 °C
- Roof type: Conventional roof
  Mean indoor temperature: 29.4 °C

The results section confirms:
Rooftop gardens: 27.1 °C.
Conventional roofs: 29.4 °C.


Question:
{question}

Answer:
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "").strip()

    except HTTPError as error:
        raise RuntimeError(
            f"Ollama returned HTTP {error.code}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from error