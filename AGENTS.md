# AGENTS.md - FinBot-AI

## Project Overview
AI-powered Telegram bot for business financial recording. Users send natural language messages (e.g., "jual kaos hitam 3 pcs dapet 250rb") and the bot extracts transaction data, stores it in Supabase, and confirms.

## Tech Stack
- **Backend:** Python (FastAPI/Flask)
- **Database:** Supabase (PostgreSQL)
- **Hosting:** Render (Web Service)
- **AI:** LLM API (Google Gemini/OpenAI)
- **Interface:** Telegram Bot API

## Critical Requirements
- **Webhook-only architecture** (no long polling) for Render Free Tier efficiency
- **Environment variables** for all secrets: `TELEGRAM_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, `AI_API_KEY`
- **sender_id validation** on every webhook request (only authorized user can use bot)
- **JSON structured output** from AI engine with fields: `nominal`, `jenis`, `kategori`, `keterangan`

## Database Schema
```sql
CREATE TABLE cash_flow (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    jenis VARCHAR(20) NOT NULL, -- 'Pemasukan' or 'Pengeluaran'
    kategori VARCHAR(50) NOT NULL, -- 'Fashion', 'Makanan', 'Minuman', 'Operasional'
    nominal NUMERIC NOT NULL,
    keterangan TEXT,
    raw_text TEXT -- Original Telegram text for audit
);
```

## Key Testing Scenarios
1. Number format variations: "100 ribu", "50k", "Rp 25.000", "seratus lima puluh ribu rupiah"
2. Auto-categorization without explicit category mention
3. Access protection for unauthorized sender_id
4. Error handling for invalid AI responses
5. Data deduplication on retry after failure

## Deployment Notes
- Cold start mitigation needed for Render Free Tier (15min sleep)
- Health checks for Supabase and LLM API connections
- Logging: webhook requests, AI responses, DB status, errors

## Current Status
Early stage - PRD defined, no implementation yet.