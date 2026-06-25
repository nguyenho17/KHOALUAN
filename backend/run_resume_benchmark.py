"""
LEXRAG++ RESUME BENCHMARK - Chi chay 3 model con thieu
- Gemini-2.5-Flash  (google/gemini-2.5-flash)
- GPT-4o-mini       (openai/gpt-4o-mini)
- Gemma-3-27B-it    (google/gemma-3-27b-it)
Features:
- Tu dong xoay key va comment key het credit vao .env
- Checkpoint luu sau moi session (khong mat du lieu neu bi ngat)
- Resume tu checkpoint neu chay lai
"""

import os, sys, re, json, time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# =============================================================
# 1. ENV LOADER & KEY ROTATOR CO CHECKPOINT
# =============================================================
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

def reload_env():
    """Load lai .env moi nhat vao os.environ."""
    cfg = dotenv_values(ENV_PATH)
    for k, v in cfg.items():
        if v:
            os.environ[k] = v

reload_env()

class SmartKeyRotator:
    """Tu dong xoay key, comment key het credit vao file .env."""

    def __init__(self):
        self._load_keys()

    def _load_keys(self):
        reload_env()
        self.keys = []
        for i in range(1, 60):
            val = os.environ.get(f"OPENROUTER_API_KEY_{i}")
            if val and val.strip():
                self.keys.append((f"OPENROUTER_API_KEY_{i}", val.strip()))
        self.idx = 0
        print(f"[KEY] Da nap {len(self.keys)} key OpenRouter kha dung.")

    def get(self):
        if not self.keys:
            return None
        return self.keys[self.idx % len(self.keys)][1]

    def get_name(self):
        if not self.keys:
            return "NONE"
        return self.keys[self.idx % len(self.keys)][0]

    def expire_current(self):
        """Comment key hien tai trong .env va chuyen sang key tiep theo."""
        if not self.keys:
            return False
        name, val = self.keys[self.idx % len(self.keys)]
        print(f"\n[EXPIRE] Key {name} het credit. Dang comment lai trong .env...")
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{name}="):
                    lines[i] = f"# {line.strip()} # HET CREDIT\n"
                    break
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"[OK] Da comment {name} trong .env")
        except Exception as e:
            print(f"[WARN] Khong the comment .env: {e}")
        self.keys.pop(self.idx % len(self.keys))
        if not self.keys:
            print("[CRITICAL] Tat ca key da het! Vui long nap them key.")
            return False
        self.idx = self.idx % len(self.keys)
        print(f"[SWITCH] Chuyen sang key moi: {self.get_name()}")
        return True

rotator = SmartKeyRotator()

def call_llm(model_id, messages, max_tokens=700):
    """Goi LLM qua OpenRouter voi tu dong xoay key khi het credit."""
    for _ in range(len(rotator.keys) + 1):
        key = rotator.get()
        if not key:
            return ""
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
            resp = client.chat.completions.create(
                model=model_id, messages=messages,
                temperature=0.0, max_tokens=max_tokens
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ["402","401","credit","payment","insufficient"]):
                if not rotator.expire_current():
                    return ""
                time.sleep(1.0)
            elif "429" in err or "rate" in err:
                time.sleep(3.0)
            else:
                print(f"    [LLM error] {str(e)[:100]}")
                return ""
    return ""

# =============================================================
# 2. MODELS
# =============================================================
MODELS = {
    "Gemini-2.5-Flash": "google/gemini-2.5-flash",
    "GPT-4o-mini":      "openai/gpt-4o-mini",
    "Gemma-3-27B-it":  "google/gemma-3-27b-it",
}

MAX_QUESTIONS     = 70
TURNS_PER_SESSION = 5
CHECKPOINT_FILE   = "resume_benchmark_checkpoint.json"
JUDGE_MODEL       = "meta-llama/llama-3.3-70b-instruct"

# =============================================================
# 3. LOAD RETRIEVAL SERVICE
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
# 4. PROMPTS
# =============================================================
SYS_ZERO = "Ban la Luat su AI chuyen Luat Hon nhan va Gia dinh Viet Nam. Tra loi bang tieng Viet, ngan gon, chinh xac."
SYS_RAG  = "Ban la Luat su AI chuyen Luat Hon nhan va Gia dinh Viet Nam. Dua tren can cu phap ly, tra loi bang tieng Viet, trich dan so dieu luat."

def build_context(docs, fallback=""):
    if docs:
        parts = []
        for doc in docs:
            art  = doc.get("metadata", {}).get("article", "")
            name = doc.get("metadata", {}).get("law_name", "")[:50]
            cont = doc.get("content", "")[:500]
            parts.append(f"[{art} - {name}]: {cont}")
        return "\n\n".join(parts)
    return str(fallback)[:800]

def gen_answer(model_id, mode, question, history, context=""):
    msgs = []
    if mode == "zero":
        msgs = [{"role": "system", "content": SYS_ZERO}]
        for t in history[-3:]:
            msgs += [{"role":"user","content":t["q"]}, {"role":"assistant","content":t["a"][:300]}]
        msgs.append({"role": "user", "content": question})

    elif mode == "retriever":
        uc = f"Can cu phap luat:\n{context}\n\nCau hoi: {question}" if context else question
        msgs = [{"role": "system", "content": SYS_RAG}]
        for t in history[-3:]:
            msgs += [{"role":"user","content":t["q"]}, {"role":"assistant","content":t["a"][:300]}]
        msgs.append({"role": "user", "content": uc})

    elif mode == "reference":
        hist = "".join(f"ND: {t['q']}\nAI: {t['a'][:150]}...\n" for t in history[-3:])
        prompt = f"""PHAN I: Xac nhan van de.
PHAN II: Can cu phap ly (trich dan chinh xac so dieu luat).
PHAN III: Phan tich chi tiet.
PHAN IV: Ket luan va loi khuyen.
{("Lich su: " + hist) if hist else ""}
--- Can cu phap ly ---
{context}
--- Cau hoi ---
{question}"""
        msgs = [{"role":"system","content":SYS_RAG}, {"role":"user","content":prompt}]

    return call_llm(model_id, msgs, max_tokens=700).strip()

# =============================================================
# 5. METRICS
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
    """
    Cham diem 5 tieu chi, xu ly ca 2 dinh dang:
      - JSON: {"factuality":8, ...}
      - Markdown: **Factuality**: 8 hoac - factuality: 8
    """
    if not prediction:
        return 0.0

    # Prompt manh buoc model phai tra JSON thuan tuy
    system_msg = (
        "You are a strict JSON scoring bot. "
        "You MUST respond with ONLY a JSON object, no explanation, no markdown. "
        "Format: {\"factuality\":N,\"completeness\":N,\"coherence\":N,\"clarity\":N,\"relevance\":N} "
        "where N is an integer 1-10."
    )
    user_msg = (
        f"Score this AI legal answer on 5 criteria (1-10):\n"
        f"Q: {question[:200]}\n"
        f"Ground truth: {ground_truth[:250]}\n"
        f"AI answer: {prediction[:350]}\n"
        f"Return ONLY JSON: {{\"factuality\":N,\"completeness\":N,\"coherence\":N,\"clarity\":N,\"relevance\":N}}"
    )
    res = call_llm(JUDGE_MODEL, [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg}
    ], max_tokens=80)

    if not res:
        return 0.0

    # Phuong phap 1: Parse JSON truc tiep
    try:
        m = re.search(r'\{[^{}]+\}', res, re.DOTALL)
        if m:
            s = json.loads(m.group(0))
            vals = [float(s.get(k, 0)) for k in ["factuality","completeness","coherence","clarity","relevance"]]
            if all(0 < v <= 10 for v in vals):
                return round(sum(vals)/5.0, 2)
    except Exception:
        pass

    # Phuong phap 2: Parse theo ten tieu chi (xu ly format markdown/text)
    # Vi du: "**Factuality (...)**: 6" hoac "- factuality: 8" hoac "factuality: 8/10"
    criteria_patterns = {
        "factuality":   r'factualit[y\w]*[^0-9]*?(\d+)',
        "completeness": r'completeness[^0-9]*?(\d+)',
        "coherence":    r'coherence[^0-9]*?(\d+)',
        "clarity":      r'clarity[^0-9]*?(\d+)',
        "relevance":    r'relevance[^0-9]*?(\d+)',
    }
    res_lower = res.lower()
    scores = {}
    for crit, pattern in criteria_patterns.items():
        m2 = re.search(pattern, res_lower)
        if m2:
            val = float(m2.group(1))
            if 1 <= val <= 10:
                scores[crit] = val

    if len(scores) >= 3:  # Neu parse duoc it nhat 3/5 tieu chi
        vals = list(scores.values())
        return round(sum(vals)/len(vals), 2)

    # Phuong phap 3: Lay 5 so dau tien trong khoang 1-10
    nums = [float(n) for n in re.findall(r'\b([1-9]|10)\b', res)]
    if len(nums) >= 5:
        return round(sum(nums[:5])/5.0, 2)

    return 0.0


# =============================================================
# 6. CHECKPOINT HELPERS
# =============================================================
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[RESUME] Tim thay checkpoint: {CHECKPOINT_FILE}")
            return data
        except Exception:
            pass
    return {}

def save_checkpoint(data):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =============================================================
# 7. BENCHMARK CHINH
# =============================================================
def run():
    print("="*60)
    print("  LEXRAG++ RESUME BENCHMARK (3 models con thieu)")
    print("="*60)

    df = pd.read_excel("benchmark_hngd.xlsx").head(MAX_QUESTIONS)
    questions     = df["question"].tolist()
    law_conts     = df["law_content"].tolist() if "law_content" in df.columns else [""] * len(df)
    ground_truths = [str(c) for c in law_conts]
    turn_indices  = [(i % TURNS_PER_SESSION) + 1 for i in range(len(questions))]

    # Load checkpoint neu co
    ckpt = load_checkpoint()

    # Cau truc luu: ckpt[model][mode][turn] = {acc_list, llm_list}
    for model_name in MODELS:
        if model_name not in ckpt:
            ckpt[model_name] = {}
        for mode in ["zero", "retriever", "reference"]:
            if mode not in ckpt[model_name]:
                ckpt[model_name][mode] = {str(t): {"acc": [], "llm": []} for t in range(1,6)}

    for model_name, model_id in MODELS.items():
        print(f"\n{'='*60}")
        print(f"[MODEL] {model_name}  ({model_id})")
        print("="*60)

        for mode in ["zero", "retriever", "reference"]:
            # Kiem tra xem da co du lieu chua (resume logic)
            total_done = sum(len(ckpt[model_name][mode][str(t)]["acc"]) for t in range(1,6))
            if total_done >= MAX_QUESTIONS:
                print(f"  [SKIP] {mode.upper()} - Da co du lieu ({total_done} mau). Bo qua.")
                continue

            print(f"\n  [MODE] {mode.upper()} (Da co: {total_done}/{MAX_QUESTIONS})")
            history = []

            # Tinh session da chay xong de skip
            done_per_turn = {t: len(ckpt[model_name][mode][str(t)]["acc"]) for t in range(1,6)}
            min_done = min(done_per_turn.values())  # So session hoan chinh
            sessions_done = min_done  # Moi session co 1 sample/turn

            pbar = tqdm(enumerate(zip(questions, turn_indices, ground_truths)),
                        total=len(questions), desc=f"    {mode}")

            session_count = -1
            for i, (question, turn_idx, gt) in pbar:
                if turn_idx == 1:
                    session_count += 1
                    history = []

                # Skip session da lam xong
                if session_count < sessions_done:
                    pbar.set_postfix({"status": f"skip_session_{session_count}"})
                    continue

                # Lay context
                context = ""
                if mode in ["retriever", "reference"]:
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

                ckpt[model_name][mode][str(turn_idx)]["acc"].append(acc)
                ckpt[model_name][mode][str(turn_idx)]["llm"].append(llm)

                pbar.set_postfix({"t": turn_idx, "acc": f"{acc:.3f}", "llm": f"{llm:.2f}", "key": rotator.get_name()[-6:]})

                # Luu checkpoint sau moi 5 cau
                if (i + 1) % 5 == 0:
                    save_checkpoint(ckpt)

                time.sleep(0.3)

            # Luu checkpoint sau moi mode
            save_checkpoint(ckpt)
            print(f"  [SAVED] Checkpoint da luu sau mode {mode.upper()}")

    # ==========================================================
    # TONG HOP KET QUA
    # ==========================================================
    print("\n\n" + "="*60)
    print("  TONG HOP KET QUA 3 MODELS")
    print("="*60)

    rows = []
    for model_name in MODELS:
        for mode in ["zero", "retriever", "reference"]:
            row = {"Model": model_name, "Type": mode.capitalize()}
            all_acc, all_llm = [], []
            for t in range(1, 6):
                al = ckpt[model_name][mode][str(t)]["acc"]
                ll = ckpt[model_name][mode][str(t)]["llm"]
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
    result_df.to_excel("resume_benchmark_results.xlsx", index=False)
    print(f"\n[DONE] Da luu: resume_benchmark_results.xlsx")
    print("\n" + result_df.to_string(index=False))

    # Xoa checkpoint khi hoan thanh
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print("[CLEAN] Da xoa checkpoint file.")

    return result_df


if __name__ == "__main__":
    run()
