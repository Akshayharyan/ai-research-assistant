
from app.services.llm_service import generate_answer

question = "What were the mean indoor temperatures?"

context = """
Page 1:
The simulated study compared rooftop gardens with
conventional roofs across 12 fictional buildings.

The mean indoor temperature was:
- Rooftop garden: 27.1°C
- Conventional roof: 29.4°C

These are simulated results, not real measurements.
"""

answer = generate_answer(question, context)

print("\nQuestion:")
print(question)

print("\nAI Answer:")
print(answer)