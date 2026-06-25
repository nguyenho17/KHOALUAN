---
title: ChatBot AI Luật Hôn Nhân và Gia Đình
emoji: ⚖️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
license: other
short_description: Hệ thống tư vấn pháp lý Luật Hôn Nhân VN với RAG++ (FAISS + BM25 + LLM)
---

# ⚖️ ChatBot AI – Luật Hôn Nhân và Gia Đình Việt Nam

> **LexRAG++** — Hệ thống RAG 4 giai đoạn: FAISS + BM25 + Cross-Encoder + Llama-3.3-70B

## Cách sử dụng

Truy cập giao diện web tại URL của Space này. Trang chủ sẽ tự động hiển thị.

## Cấu hình Secrets cần thiết

Vào **Settings → Variables and secrets** của Space và thêm:

| Secret Name | Ví dụ | Mô tả |
|---|---|---|
| `DATABASE_URL` | `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require` | PostgreSQL (Neon.tech) |
| `JWT_SECRET_KEY` | `your-secret-key-here` | Khóa ký JWT |
| `OPENROUTER_API_KEY_28` | `sk-or-v1-...` | OpenRouter API Key |
| `OPENROUTER_API_KEY_29` | `sk-or-v1-...` | Dự phòng |
| `OPENROUTER_API_KEY_30` | `sk-or-v1-...` | Dự phòng |

## Công nghệ

- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL (Neon.tech)
- **RAG**: FAISS Dense + BM25 Sparse + Cross-Encoder Reranking
- **LLM**: Llama-3.3-70B via OpenRouter
- **Frontend**: HTML + TailwindCSS
