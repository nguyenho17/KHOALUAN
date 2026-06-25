"""
LEXRAG++ BENCHMARK - GROQ VERSION
Chay tren Groq API (mien phi, khong can OpenRouter credit)
Models: llama-3.3-70b-versatile, llama-3.1-8b-instant
"""

import os, sys, re, json, time
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# =============================================================
# CONFIG
# =============================================================
GROQ_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_KEY)

MODELS = {
    "Llama-3.3-70B": "llama-3.3-70b-versatile",
    "Llama-3.1-8B":  "llama-3.1-8b-instant",
}

MAX_QUESTIONS     = 35   # 7 phien x 5-turn (gon de chay nhanh)
TURNS_PER_SESSION = 5
JUDGE_MODEL       = "llama-3.3-70b-versatile"

# =============================================================
# GOI GROQ LLM
# =============================================================
def call_groq(model_id, messages, max_tokens=600):
    for attempt in range(3):
        try:
            r = groq_client.chat.completions.create(
                model=model_id, messages=messages,
                temperature=0.0, max_tokens=max_tokens
            )
            return r.choices[0].message.content or ""
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                wait = 60 if attempt == 0 else 120
                print(f"    [Rate limit] Cho {wait}s...")
                time.sleep(wait)
            else:
                print(f"    [Groq error] {err[:80]}")
                return ""
    return ""

# =============================================================
# LOAD RETRIEVAL SERVICE
# =============================================================
print("[INFO] Khoi tai RetrievalService...")
try:
    from app.services.retrieval import RetrievalService
    retrieval_svc = RetrievalService()
    print("[OK] RetrievalService san sang.\n")
except Exception as e:
    print(f"[WARN] Khong tai duoc RetrievalService: {e}")
    retrieval_svc = None

# =============================================================
# PROMPTS
# =============================================================
SYS_ZERO = "Ban la Luat su AI chuyen Luat Hon nhan va Gia dinh Viet Nam. Tra loi bang tieng Viet, ngan gon, chinh xac."
SYS_RAG  = "Ban la Luat su AI chuyen Luat Hon nhan va Gia dinh Viet Nam. Dua tren can cu phap ly duoi day, tra loi bang tieng Viet, ngan gon, trich dan so dieu luat."

def build_context(docs, law_content_fallback=""):
    if docs:
        parts = []
        for doc in docs:
            art  = doc.get("metadata", {}).get("article", "")
            name = doc.get("metadata", {}).get("law_name", "")[:50]
            cont = doc.get("content", "")[:500]
            parts.append(f"[{art} - {name}]: {cont}")
        return "\n\n".join(parts)
    return str(law_content_fallback)[:800]

def gen_answer(model_id, mode, question, history, context=""):
    msgs = []
    if mode == "zero":
        msgs = [{"role":"system","content":SYS_ZERO}]
        for t in history[-3:]:
            msgs += [{"role":"user","content":t["q"]},{"role":"assistant","content":t["a"][:300]}]
        msgs.append({"role":"user","content":question})

    elif mode == "retriever":
        content = f"Can cu phap luat:\n{context}\n\nCau hoi: {question}" if context else question
        msgs = [{"role":"system","content":SYS_RAG}]
        for t in history[-3:]:
            msgs += [{"role":"user","content":t["q"]},{"role":"assistant","content":t["a"][:300]}]
        msgs.append({"role":"user","content":content})

    elif mode == "reference":
        hist = "".join(f"Nguoi dung: {t['q']}\nAI: {t['a'][:150]}...\n" for t in history[-3:])
        prompt = f"""PHAN I: Xac nhan van de cua nguoi hoi.
PHAN II: Can cu phap ly - Trich dan chinh xac so dieu luat.
PHAN III: Phan tich chi tiet.
PHAN IV: Ket luan va loi khuyen.
{("Lich su: " + hist) if hist else ""}
--- Can cu phap ly ---
{context}
--- Cau hoi ---
{question}"""
        msgs = [{"role":"system","content":SYS_RAG},{"role":"user","content":prompt}]

    return call_groq(model_id, msgs, max_tokens=600).strip()

# =============================================================
# METRICS
# =============================================================
def keyword_acc(prediction, ground_truth):
    if not prediction or not ground_truth:
        return 0.0
    pred = re.sub(r'[^\w\s]', '', prediction.lower())
    gt   = re.sub(r'[^\w\s]', '', ground_truth.lower())
    gt_w = set(w for w in gt.split() if len(w) > 2)
    if not gt_w:
        return 1.0
    return round(len(gt_w & set(pred.split())) / len(gt_w), 4)

def judge_score(question, prediction, ground_truth):
    if not prediction:
        return 0.0
    prompt = f"""Cham diem cau tra loi AI (thang 1-10) theo 5 tieu chi:
Q: {question[:250]}
GT: {ground_truth[:300]}
AI: {prediction[:400]}
Tra ve JSON (chi JSON): {{"factuality":X,"completeness":X,"coherence":X,"clarity":X,"relevance":X}}"""
    res = call_groq(JUDGE_MODEL, [{"role":"user","content":prompt}], max_tokens=80)
    try:
        m = re.search(r'\{[^{}]+\}', res)
        if m:
            s = json.loads(m.group(0))
            vals = [float(s.get(k, 0)) for k in ["factuality","completeness","coherence","clarity","relevance"]]
            return round(sum(vals)/5.0, 2)
    except Exception:
        pass
    nums = re.findall(r':\s*(\d+(?:\.\d+)?)', res)
    if len(nums) >= 5:
        return round(sum(float(n) for n in nums[:5])/5.0, 2)
    return 0.0

# =============================================================
# BENCHMARK CHINH
# =============================================================
def run():
    print("="*60)
    print("  LEXRAG++ GROQ BENCHMARK")
    print("="*60)

    df = pd.read_excel("benchmark_hngd.xlsx").head(MAX_QUESTIONS)
    questions     = df["question"].tolist()
    law_conts     = df.get("law_content", pd.Series([""] * len(df))).tolist()
    ground_truths = [str(c) for c in law_conts]
    turn_indices  = [(i % TURNS_PER_SESSION) + 1 for i in range(len(questions))]

    # acc_data[model][mode][turn] = list of acc values
    acc_data = {m: {mode: {t: [] for t in range(1,6)} for mode in ["zero","retriever","reference"]} for m in MODELS}
    llm_data = {m: {mode: {t: [] for t in range(1,6)} for mode in ["zero","retriever","reference"]} for m in MODELS}

    for model_name, model_id in MODELS.items():
        print(f"\n{'='*60}")
        print(f"[MODEL] {model_name} ({model_id})")
        print("="*60)

        for mode in ["zero", "retriever", "reference"]:
            print(f"\n  [MODE] {mode.upper()}")
            history = []

            for i, (question, turn_idx, gt) in enumerate(
                    tqdm(zip(questions, turn_indices, ground_truths),
                         total=len(questions), desc=f"    {mode}")):

                if turn_idx == 1:
                    history = []

                context = ""
                if mode in ["retriever","reference"]:
                    if retrieval_svc:
                        try:
                            docs = retrieval_svc.hybrid_search(question, top_k=5)
                            context = build_context(docs)
                        except Exception:
                            context = str(law_conts[i])[:800]
                    else:
                        context = str(law_conts[i])[:800]

                answer = gen_answer(model_id, mode, question, history, context)
                history.append({"q": question, "a": answer})

                acc = keyword_acc(answer, gt)
                llm = judge_score(question, answer, gt)

                acc_data[model_name][mode][turn_idx].append(acc)
                llm_data[model_name][mode][turn_idx].append(llm)

                time.sleep(0.5)  # Groq rate limit

    # ==========================================================
    # TONG HOP
    # ==========================================================
    rows = []
    for model_name in MODELS:
        for mode in ["zero","retriever","reference"]:
            row = {"Model": model_name, "Type": mode.capitalize()}
            all_acc, all_llm = [], []
            for t in range(1,6):
                al = acc_data[model_name][mode][t]
                ll = llm_data[model_name][mode][t]
                avg_acc = round(sum(al)/len(al), 4) if al else 0.0
                avg_llm = round(sum(ll)/len(ll), 2) if ll else 0.0
                row[f"{t}-turn Acc"] = avg_acc
                row[f"{t}-turn LLM"] = avg_llm
                all_acc.append(avg_acc)
                all_llm.append(avg_llm)
            row["ALL Acc"] = round(sum(all_acc)/5, 4)
            row["ALL LLM"] = round(sum(all_llm)/5, 2)
            rows.append(row)

    result_df = pd.DataFrame(rows)
    result_df.to_excel("groq_benchmark_results.xlsx", index=False)
    print("\n[DONE] Da luu: groq_benchmark_results.xlsx")
    print("\n" + result_df.to_string(index=False))
    return result_df

if __name__ == "__main__":
    run()
