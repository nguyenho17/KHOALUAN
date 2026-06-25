import os, re, json
from openai import OpenAI
from dotenv import dotenv_values

cfg = dotenv_values('.env')
keys = [(k,v) for k,v in cfg.items() if k.startswith('OPENROUTER_API_KEY_') and v and not v.strip().startswith('#')]
key = keys[0][1].strip()

client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=key)

system_msg = (
    "You are a strict JSON scoring bot. "
    "You MUST respond with ONLY a JSON object, no explanation, no markdown. "
    'Format: {"factuality":N,"completeness":N,"coherence":N,"clarity":N,"relevance":N} '
    "where N is an integer 1-10."
)
user_msg = (
    "Score this AI legal answer on 5 criteria (1-10):\n"
    "Q: Vo chong co the ly hon khi nao?\n"
    "Ground truth: Theo Dieu 51 Luat Hon nhan va Gia dinh, vo chong co quyen yeu cau Toa an giai quyet ly hon.\n"
    "AI answer: Vo chong co the ly hon khi co mau thuan nghiem trong, khong the hoa giai.\n"
    'Return ONLY JSON: {"factuality":N,"completeness":N,"coherence":N,"clarity":N,"relevance":N}'
)

resp = client.chat.completions.create(
    model='meta-llama/llama-3.3-70b-instruct',
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg}
    ],
    temperature=0.0, max_tokens=80
)
result = resp.choices[0].message.content
print("RAW OUTPUT:", repr(result))

# Test parsing
try:
    m = re.search(r'\{[^{}]+\}', result, re.DOTALL)
    if m:
        s = json.loads(m.group(0))
        vals = [float(s.get(k, 0)) for k in ["factuality","completeness","coherence","clarity","relevance"]]
        print("JSON PARSE OK - Score:", round(sum(vals)/5.0, 2))
    else:
        # Fallback
        criteria_patterns = {
            "factuality":   r'factualit[y\w]*[^0-9]*?(\d+)',
            "completeness": r'completeness[^0-9]*?(\d+)',
            "coherence":    r'coherence[^0-9]*?(\d+)',
            "clarity":      r'clarity[^0-9]*?(\d+)',
            "relevance":    r'relevance[^0-9]*?(\d+)',
        }
        scores = {}
        for crit, pattern in criteria_patterns.items():
            m2 = re.search(pattern, result.lower())
            if m2:
                val = float(m2.group(1))
                if 1 <= val <= 10:
                    scores[crit] = val
        print("FALLBACK PARSE:", scores)
        if scores:
            print("Score:", round(sum(scores.values())/len(scores), 2))
except Exception as e:
    print("Parse error:", e)
