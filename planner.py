import json
import re


def extract_orders(text):
    try:
        import ollama

        response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "system",
                    "content":
                    (
                        "You are a production planner.\n"
                        "Extract ONLY production quantities.\n"
                        "Return ONLY valid JSON.\n"
                        "Example: {\"type1\":1,\"type2\":1}\n"
                        "Do not explain anything."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        content = response["message"]["content"]

        print("\nLLM RAW RESPONSE:")
        print(content)

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if match:
            return json.loads(match.group())

    except Exception as e:
        print(f"[Planner] Ollama not used: {e}")
        print("[Planner] Using regex fallback")

    type1 = 0
    type2 = 0

    match1 = re.search(r"(\d+)\s*type\s*1|(\d+)\s*type1", text.lower())
    match2 = re.search(r"(\d+)\s*type\s*2|(\d+)\s*type2", text.lower())

    if match1:
        type1 = int(match1.group(1) or match1.group(2))

    if match2:
        type2 = int(match2.group(1) or match2.group(2))

    return {
        "type1": type1,
        "type2": type2
    }